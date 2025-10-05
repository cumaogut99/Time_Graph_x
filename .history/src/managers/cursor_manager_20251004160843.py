# type: ignore
"""
Cursor Manager for Time Analysis Widget

Handles different cursor interaction modes:
- Single Cursor: One movable vertical line
- Dual Cursors: Two independent movable lines  
- Range Selector: Shaded region with two boundaries
"""

import logging
from typing import Optional, Tuple, Dict, Any
import pyqtgraph as pg
from PyQt5.QtCore import QObject, pyqtSignal as Signal
from PyQt5.QtGui import QColor

logger = logging.getLogger(__name__)

class CursorManager(QObject):
    """
    Manages cursor interactions for the time analysis plot.
    
    Modes:
    - none: No cursors active
    - single: Single movable cursor line
    - dual: Two independent cursor lines
    - range: Range selection with shaded region
    """
    
    # Signals
    cursor_moved = Signal(dict)  # Emits cursor positions when they change
    range_changed = Signal(float, float)  # start, end
    
    def __init__(self, plot_widgets):
        super().__init__()
        
        self.plot_widgets = plot_widgets  # List of plot widgets for stacked plots
        self.plots = plot_widgets  # Alias for compatibility
        self.current_mode = "none"
        
        # Cursor objects (will be applied to all plots)
        self.dual_cursors_1 = []  # First dual cursor per plot
        self.dual_cursors_2 = []  # Second dual cursor per plot
        
        # State tracking
        self.dual_cursor_count = 0  # For dual mode click tracking
        
        # Snap to data points feature
        self.snap_to_data_enabled = False
        self.signal_data_cache = {}  # Cache for signal data for snapping
        
        # Viewport-locked cursor positions (relative positions: 0.0 to 1.0)
        # Cursors stay at fixed screen positions during pan/zoom
        # Viewport lock feature removed - cursors now stay at fixed data coordinates
        
        # Cursor boundary constraint feature - keep cursors inside view range
        self.constrain_to_view = True  # Keep cursors inside visible area during pan/zoom
        
        # Connect plot click events for all plot widgets
        for plot_widget in self.plot_widgets:
            # Connect to the plot item's scene mouse click signal
            plot_widget.plotItem.scene().sigMouseClicked.connect(self._on_plot_clicked)
            
            # Connect to view range changes to constrain cursors when panning/zooming
            try:
                plot_widget.getViewBox().sigRangeChanged.connect(self._on_view_range_changed)
            except Exception as e:
                logger.warning(f"Failed to connect view range signal: {e}")
        
        logger.debug(f"CursorManager initialized with {len(plot_widgets)} plot widgets")

    def set_mode(self, mode: str):
        """
        Set the cursor interaction mode.
        
        Args:
            mode: One of 'none', 'dual'
        """
        logger.info(f"Setting cursor mode to: {mode}")
        
        # Clear existing cursors first
        self.clear_all()
        
        self.current_mode = mode
        self.dual_cursor_count = 0  # Reset dual cursor counter
        
        logger.info(f"Cursor mode changed to: {mode}")
        logger.info(f"Cursor lists after mode change - Cursor1: {len(self.dual_cursors_1) if self.dual_cursors_1 else 0}, Cursor2: {len(self.dual_cursors_2) if self.dual_cursors_2 else 0}")

        # --- New logic to auto-create cursors ---
        if mode == "dual":
            self._auto_create_dual_cursors()
        elif mode == "none":
            # Ensure all cursors are completely removed
            self._ensure_cursors_removed()
            logger.debug("All cursors removed for 'none' mode")

    def _auto_create_dual_cursors(self):
        """Creates two cursors at 1/3 and 2/3 of the current view."""
        if not self.plot_widgets:
            logger.warning("No plot widgets available for auto-creating cursors")
            return
            
        # Prevent duplicate cursor creation
        if self.dual_cursors_1 or self.dual_cursors_2:
            logger.debug("Cursors already exist, skipping creation")
            return
            
        try:
            # Find the first valid plot widget
            valid_plot = None
            for plot_widget in self.plot_widgets:
                if (hasattr(plot_widget, 'getViewBox') and 
                    plot_widget.getViewBox() is not None and
                    plot_widget.isVisible()):
                    valid_plot = plot_widget
                    break
            
            if not valid_plot:
                logger.warning("No valid plot widget found for cursor creation")
                return
                
            # Don't force autorange - use current view range instead
            # This prevents unwanted zoom when activating cursors
            # valid_plot.autoRange()  # REMOVED: This was causing X-axis zoom issues
            
            # Wait a moment to ensure plot is ready
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self._delayed_cursor_creation)
            
        except Exception as e:
            logger.error(f"Failed to auto-create dual cursors: {e}")
            import traceback
            traceback.print_exc()
    
    def _delayed_cursor_creation(self):
        """Delayed cursor creation after autorange."""
        try:
            # Double-check that we don't already have cursors
            if self.dual_cursors_1 or self.dual_cursors_2:
                logger.debug("Cursors already exist during delayed creation, aborting")
                return
                
            # Find the first valid plot widget again
            valid_plot = None
            for plot_widget in self.plot_widgets:
                if (hasattr(plot_widget, 'getViewBox') and 
                    plot_widget.getViewBox() is not None):
                    valid_plot = plot_widget
                    break
            
            if not valid_plot:
                logger.warning("No valid plot widget found for delayed cursor creation")
                return
                
            view_range = valid_plot.getViewBox().viewRange()[0]
            
            # Check if view range is valid
            if view_range[0] >= view_range[1]:
                logger.warning(f"Invalid view range for cursor creation: {view_range}")
                return
                
            one_third_pos = view_range[0] + (view_range[1] - view_range[0]) / 3
            two_thirds_pos = view_range[0] + 2 * (view_range[1] - view_range[0]) / 3
            
            # Create first cursor
            self.dual_cursors_1 = []
            self._create_dual_cursor_set(self.dual_cursors_1, one_third_pos, '#ff4444', self._sync_dual_cursors_1)
            
            # Create second cursor
            self.dual_cursors_2 = []
            self._create_dual_cursor_set(self.dual_cursors_2, two_thirds_pos, '#4444ff', self._sync_dual_cursors_2)
            
            logger.info(f"Successfully created dual cursors at positions: {one_third_pos:.2f}, {two_thirds_pos:.2f}")
            
            # Emit cursor positions immediately
            self._emit_cursor_positions()
            
        except Exception as e:
            logger.error(f"Failed to create delayed cursors: {e}")
            import traceback
            traceback.print_exc()

    def clear_all(self):
        """Remove all cursor objects from all plots."""
        # Clear dual cursors
        for cursor in self.dual_cursors_1:
            for plot_widget in self.plot_widgets:
                try:
                    plot_widget.removeItem(cursor)
                except:
                    pass
        self.dual_cursors_1.clear()
        
        for cursor in self.dual_cursors_2:
            for plot_widget in self.plot_widgets:
                try:
                    plot_widget.removeItem(cursor)
                except:
                    pass
        self.dual_cursors_2.clear()
        
    def _ensure_cursors_removed(self):
        """Ensure all cursors are completely removed from all plots."""
        logger.debug("Ensuring all cursors are removed")
        
        # Force remove any remaining cursor items
        for plot_widget in self.plot_widgets:
            try:
                # Get all items in the plot
                items = plot_widget.plotItem.items[:]
                for item in items:
                    # Check if item is a cursor (InfiniteLine)
                    if hasattr(item, '__class__') and 'InfiniteLine' in str(item.__class__):
                        try:
                            plot_widget.removeItem(item)
                            logger.debug(f"Removed cursor item: {item}")
                        except Exception as e:
                            logger.warning(f"Failed to remove cursor item: {e}")
            except Exception as e:
                logger.warning(f"Failed to check plot items: {e}")
        
        # Clear cursor lists
        self.dual_cursors_1.clear()
        self.dual_cursors_2.clear()
        self.dual_cursor_count = 0
        
    def _on_plot_clicked(self, event):
        """Handle mouse clicks on any plot."""
        if event.button() != 1:  # Only handle left clicks
            return
            
        if self.current_mode == "none":
            return
            
        # Get the scene that sent the event
        event_scene = event.widget()
        
        # Find which plot widget was clicked by matching scenes
        clicked_plot = None
        for plot_widget in self.plot_widgets:
            if plot_widget.plotItem.scene() == event_scene:
                clicked_plot = plot_widget
                break
        
        if clicked_plot is None:
            # Fallback to first plot widget
            clicked_plot = self.plot_widgets[0] if self.plot_widgets else None
            
        if clicked_plot is None:
            return
            
        # Get click position in data coordinates
        scene_pos = event.scenePos()
        try:
            view_pos = clicked_plot.plotItem.vb.mapSceneToView(scene_pos)
            x_pos = view_pos.x()
        except Exception as e:
            logger.warning(f"Failed to get click position: {e}")
            return
        
        # Handle based on current mode
        if self.current_mode == "dual":
            self._handle_dual_cursor_click(x_pos)

    def _handle_dual_cursor_click(self, x_pos: float):
        """Handle dual cursor mode clicks."""
        logger.info(f"Dual cursor click at position: {x_pos:.3f}")
        
        # Apply snap to data if enabled
        snapped_x_pos = self._find_nearest_data_point(x_pos)
        
        # If no cursors, create the first one
        if not self.dual_cursors_1:
            self.dual_cursors_1 = []
            self._create_dual_cursor_set(self.dual_cursors_1, snapped_x_pos, 'red', self._sync_dual_cursors_1)
            logger.info(f"First dual cursors created at position: {snapped_x_pos:.3f}")
            self._emit_cursor_positions()
            return

        # If first cursor exists but not the second, create the second one
        if not self.dual_cursors_2:
            self.dual_cursors_2 = []
            self._create_dual_cursor_set(self.dual_cursors_2, snapped_x_pos, 'blue', self._sync_dual_cursors_2)
            logger.info(f"Second dual cursors created at position: {snapped_x_pos:.3f}")
            logger.info(f"Both cursors now exist - can zoom: {self.can_zoom_to_cursors()}")
            self._emit_cursor_positions()
            return

        # If both exist, move the closest one
        pos1 = self.dual_cursors_1[0].value()
        pos2 = self.dual_cursors_2[0].value()
        
        if abs(x_pos - pos1) <= abs(x_pos - pos2):
            for cursor in self.dual_cursors_1:
                cursor.setPos(snapped_x_pos)
            self._sync_dual_cursors_1(self.dual_cursors_1[0]) # Manually call sync to emit signal
        else:
            for cursor in self.dual_cursors_2:
                cursor.setPos(snapped_x_pos)
            self._sync_dual_cursors_2(self.dual_cursors_2[0]) # Manually call sync to emit signal

    def _create_dual_cursor_set(self, cursor_list, x_pos, color, sync_slot):
        """Helper to create a set of synchronized cursors for dual mode."""
        for plot_widget in self.plot_widgets:
            cursor = pg.InfiniteLine(
                pos=x_pos,
                angle=90,
                pen=pg.mkPen(color=color, width=2),
                hoverPen=pg.mkPen(color=color, alpha=100, width=10), # Wider, semi-transparent hover area
                movable=True
            )
            plot_widget.addItem(cursor)
            cursor_list.append(cursor)
            
            # Connect movement signal for EACH cursor
            # The sync_slot will be one of _sync_dual_cursors_1 or _sync_dual_cursors_2
            cursor.sigPositionChanged.connect(
                lambda c=cursor, s=sync_slot: s(c)
            )
    
    def _sync_dual_cursors_1(self, moved_cursor):
        """Synchronize position of all first dual cursors."""
        if not self.dual_cursors_1:
            return
            
        pos = moved_cursor.value()
        
        # Apply snap to data if enabled
        snapped_pos = self._find_nearest_data_point(pos)
        
        # Update all cursors to the snapped position
        for cursor in self.dual_cursors_1:
            cursor.blockSignals(True)
            cursor.setPos(snapped_pos)
            cursor.blockSignals(False)
        
        self._emit_cursor_positions()
    
    def _sync_dual_cursors_2(self, moved_cursor):
        """Synchronize position of all second dual cursors."""
        if not self.dual_cursors_2:
            return
            
        pos = moved_cursor.value()
        
        # Apply snap to data if enabled
        snapped_pos = self._find_nearest_data_point(pos)
        
        # Update all cursors to the snapped position
        for cursor in self.dual_cursors_2:
            cursor.blockSignals(True)
            cursor.setPos(snapped_pos)
            cursor.blockSignals(False)
        
        self._emit_cursor_positions()

    def get_cursor_positions(self) -> Dict[str, float]:
        """Get current cursor positions."""
        positions = {}
        
        if self.dual_cursors_1:
            positions['cursor1'] = self.dual_cursors_1[0].value()
            
        if self.dual_cursors_2:
            positions['cursor2'] = self.dual_cursors_2[0].value()
            
        return positions

    def get_range(self) -> Optional[Tuple[float, float]]:
        """Get current range selection."""
        return None
    
    def get_cursor_position(self) -> Optional[float]:
        """Get current cursor position for value display."""
        if self.dual_cursors_1:
            return self.dual_cursors_1[0].value()
        return None

    def get_cursor_positions(self) -> Dict[str, float]:
        """Get all cursor positions for statistics."""
        positions = {}
        if self.current_mode == "dual":
            if self.dual_cursors_1:
                positions['c1'] = self.dual_cursors_1[0].value()
            if self.dual_cursors_2:
                positions['c2'] = self.dual_cursors_2[0].value()
        return positions

    def _emit_cursor_positions(self):
        """Emit current cursor positions."""
        positions = self.get_cursor_positions()
        if positions:
            self.cursor_moved.emit(positions)

    def set_cursor_position(self, cursor_type: str, position: float):
        """Programmatically set cursor position."""
        if cursor_type == "dual_1" and self.dual_cursors_1:
            for cursor in self.dual_cursors_1:
                cursor.setPos(position)
        elif cursor_type == "dual_2" and self.dual_cursors_2:
            for cursor in self.dual_cursors_2:
                cursor.setPos(position)

    def set_range(self, start: float, end: float):
        """Programmatically set range selection."""
        pass
        
    def zoom_to_cursors(self):
        """Zoom to the range between dual cursors."""
        if self.current_mode != "dual" or not self.dual_cursors_1 or not self.dual_cursors_2:
            logger.warning("Zoom to cursors requires dual cursor mode with both cursors active")
            return False
            
        try:
            # Get cursor positions
            pos1 = self.dual_cursors_1[0].value()
            pos2 = self.dual_cursors_2[0].value()
            
            # Ensure proper order (min, max)
            start_pos = min(pos1, pos2)
            end_pos = max(pos1, pos2)
            
            # Add small margin (5% on each side)
            range_width = end_pos - start_pos
            margin = range_width * 0.05
            zoom_start = start_pos - margin
            zoom_end = end_pos + margin
            
            logger.info(f"Zooming to cursor range: {zoom_start:.3f} to {zoom_end:.3f}")
            
            # Apply zoom to all plot widgets
            for plot_widget in self.plot_widgets:
                plot_widget.setXRange(zoom_start, zoom_end, padding=0)
                
            return True
            
        except Exception as e:
            logger.error(f"Error zooming to cursors: {e}")
            return False
            
    def can_zoom_to_cursors(self) -> bool:
        """Check if zoom to cursors is possible."""
        result = (self.current_mode == "dual" and 
                 self.dual_cursors_1 and 
                 self.dual_cursors_2 and
                 len(self.dual_cursors_1) > 0 and 
                 len(self.dual_cursors_2) > 0)
        
        # Debug logging
        logger.debug(f"Zoom check - Mode: {self.current_mode}, "
                    f"Cursor1: {len(self.dual_cursors_1) if self.dual_cursors_1 else 0}, "
                    f"Cursor2: {len(self.dual_cursors_2) if self.dual_cursors_2 else 0}, "
                    f"Can zoom: {result}")
        
        return result

    def set_snap_to_data(self, enabled: bool):
        """Enable or disable snap to data points functionality."""
        self.snap_to_data_enabled = enabled
        logger.info(f"Snap to data points {'enabled' if enabled else 'disabled'}")
        
        # Update signal data cache when enabling
        if enabled:
            self._update_signal_data_cache()

    def _update_signal_data_cache(self):
        """Update the cache of signal data for snapping."""
        self.signal_data_cache.clear()
        
        # Get signal data from parent widget
        try:
            # Try to get signal processor from parent
            parent_widget = None
            for plot_widget in self.plot_widgets:
                if hasattr(plot_widget, 'parent') and plot_widget.parent():
                    parent_widget = plot_widget.parent()
                    while parent_widget and not hasattr(parent_widget, 'signal_processor'):
                        parent_widget = parent_widget.parent()
                    if parent_widget and hasattr(parent_widget, 'signal_processor'):
                        break
            
            if parent_widget and hasattr(parent_widget, 'signal_processor'):
                signal_processor = parent_widget.signal_processor
                
                # Get all signal names
                signal_names = signal_processor.get_signal_names()
                
                for signal_name in signal_names:
                    signal_data = signal_processor.get_signal_data(signal_name)
                    if signal_data and 'x_data' in signal_data and 'y_data' in signal_data:
                        x_data = signal_data['x_data']
                        y_data = signal_data['y_data']
                        
                        if len(x_data) > 0 and len(y_data) > 0:
                            self.signal_data_cache[signal_name] = {
                                'x_data': x_data,
                                'y_data': y_data
                            }
                
                logger.debug(f"Updated signal data cache with {len(self.signal_data_cache)} signals")
                
        except Exception as e:
            logger.warning(f"Failed to update signal data cache: {e}")

    def _find_nearest_data_point(self, x_pos: float) -> float:
        """Find the nearest data point X coordinate to the given position."""
        if not self.snap_to_data_enabled or not self.signal_data_cache:
            return x_pos
        
        nearest_x = x_pos
        min_distance = float('inf')
        
        try:
            # Check all cached signals for nearest point
            for signal_name, data in self.signal_data_cache.items():
                x_data = data['x_data']
                
                if len(x_data) == 0:
                    continue
                
                # Use numpy for efficient nearest point finding
                import numpy as np
                x_array = np.array(x_data)
                
                # Find the index of the closest point
                idx = np.argmin(np.abs(x_array - x_pos))
                closest_x = x_array[idx]
                distance = abs(closest_x - x_pos)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_x = closest_x
            
            logger.debug(f"Snapped cursor from {x_pos:.6f} to {nearest_x:.6f} (distance: {min_distance:.6f})")
            
        except Exception as e:
            logger.warning(f"Error finding nearest data point: {e}")
            return x_pos
        
        return nearest_x

    # Viewport lock feature removed - cursors now stay at fixed data coordinates during pan/zoom