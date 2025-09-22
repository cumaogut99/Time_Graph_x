# type: ignore
"""
Plot Manager for Time Graph Widget

Manages the plotting interface including:
- Multiple stacked subplots
- Signal visualization
- Plot synchronization
- View management
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QAction, QMenu
from PyQt5.QtCore import Qt, pyqtSignal as Signal, QObject
from PyQt5.QtGui import QColor
import datetime

if TYPE_CHECKING:
    from .time_graph_widget import TimeGraphWidget

logger = logging.getLogger(__name__)

class DateTimeAxisItem(pg.AxisItem):
    """Custom axis item for displaying Unix timestamps as readable datetime."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_datetime_axis = False
        
    def enable_datetime_mode(self, enable=True):
        """Enable or disable datetime formatting."""
        self.is_datetime_axis = enable
        
    def tickStrings(self, values, scale, spacing):
        """Override to format Unix timestamps as datetime strings."""
        if not self.is_datetime_axis:
            return super().tickStrings(values, scale, spacing)
            
        strings = []
        for v in values:
            try:
                # Convert Unix timestamp to datetime (UTC)
                dt = datetime.datetime.utcfromtimestamp(v)
                
                # Choose format based on time range
                if spacing < 1:  # Less than 1 second - show milliseconds
                    time_str = dt.strftime('%H:%M:%S.%f')[:-3]
                elif spacing < 60:  # Less than 1 minute - show seconds
                    time_str = dt.strftime('%H:%M:%S')
                elif spacing < 3600:  # Less than 1 hour - show minutes
                    time_str = dt.strftime('%H:%M')
                elif spacing < 86400:  # Less than 1 day - show hours
                    time_str = dt.strftime('%m/%d %H:%M')
                else:  # More than 1 day - show date
                    time_str = dt.strftime('%m/%d/%Y')
                    
                strings.append(time_str)
            except (ValueError, OSError, OverflowError):
                # Fallback to original formatting if timestamp is invalid
                strings.append(f'{v:.2f}')
                
        return strings

class PlotManager(QObject):
    """Manages the plotting interface for the Time Graph Widget."""
    
    # Signals
    plot_clicked = Signal(int, float, float)  # plot_index, x, y
    range_selected = Signal(float, float)  # start, end
    settings_requested = Signal(int)
    
    def __init__(self, parent_widget: "TimeGraphWidget"):
        super().__init__()
        self.parent = parent_widget
        self.plot_widgets = []
        self.current_signals = {}  # Dict of signal_name -> plot_data_item
        self.signal_colors = {}  # Store original colors for each signal
        self.subplot_count = 1
        self.max_subplots = 10
        self.min_subplots = 1
        
        # UI components that will be managed
        self.plot_panel = None
        self.main_layout = None
        self.plot_container = None
        self.settings_container = None
        
        # Grid visibility state
        self.grid_visible = True
        
        # Theme settings that will be updated by apply_theme
        self.theme_colors = {
            'background': '#1e1e1e',
            'axis_pen': '#ffffff',
            'grid_alpha': 0.3
        }
        
        # Snap to data points feature
        self.snap_to_data_enabled = False
        
        # Tooltips feature
        self.tooltips_enabled = True  # Default enabled
        self.tooltip_items = {}  # Store tooltip items per plot widget
        
        self._setup_plot_panel()
        self._rebuild_ui()  # Initial UI creation
    
    def _setup_plot_panel(self):
        """Create the main plot panel and its permanent layout."""
        self.plot_panel = QWidget()
        self.main_layout = QVBoxLayout(self.plot_panel)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)

    def set_subplot_count(self, count: int):
        """Set the number of subplots with safe error handling."""
        if not (self.min_subplots <= count <= self.max_subplots):
            logger.warning(f"Invalid subplot count: {count}. Must be between {self.min_subplots} and {self.max_subplots}")
            return False
        
        if count == self.subplot_count:
            logger.info(f"Subplot count is already {count}, skipping rebuild")
            return True
        
        logger.info(f"Changing subplot count from {self.subplot_count} to {count}")
        
        try:
            # Store signal data before rebuilding UI
            signal_data_to_restore = self._get_signal_data_for_restore()
            
            # Update count and rebuild the entire UI safely
            self.subplot_count = count
            self._rebuild_ui()
            
            # Restore signals to the new plots
            self._restore_signals(signal_data_to_restore)
            
            logger.info(f"Successfully changed subplot count to {count}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change subplot count: {e}", exc_info=True)
            # Attempt to rollback is complex, better to revert to a stable state
            self.subplot_count = 1
            self._rebuild_ui()
            return False
            
    def _rebuild_ui(self):
        """
        Safely rebuilds the entire plot and settings UI from scratch.
        This is the core of the stable UI update mechanism.
        """
        # 1. Clean up existing UI components safely
        if self.plot_container is not None:
            self.plot_container.deleteLater()
            self.plot_container = None
        
        if self.settings_container is not None:
            self.settings_container.deleteLater()
            self.settings_container = None
            
        self._clear_plots()  # Clear internal lists

        # 2. Re-create the plot widgets and their layout container
        self.plot_container = QWidget()
        plot_layout = QVBoxLayout(self.plot_container)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(1)
        
        for i in range(self.subplot_count):
            # Create custom datetime axis for bottom axis
            datetime_axis = DateTimeAxisItem(orientation='bottom')
            plot_widget = pg.PlotWidget(axisItems={'bottom': datetime_axis})
            plot_widget.addLegend() # Add legend to each plot

            # Link X-axes and manage visibility
            if i > 0 and self.plot_widgets: # Link current plot to the first one
                plot_widget.setXLink(self.plot_widgets[0])
            
            # Hide X-axis for all but the last plot
            if i < self.subplot_count - 1:
                plot_widget.getAxis('bottom').setStyle(showValues=False)
            
            plot_widget.setLabel('left', f'Channel {i+1}')
            plot_widget.showGrid(x=True, y=True, alpha=self.theme_colors['grid_alpha'])
            plot_widget.setBackground(self.theme_colors['background'])
            
            axis_pen = pg.mkPen(color=self.theme_colors['axis_pen'])
            plot_widget.getAxis('left').setPen(axis_pen)
            plot_widget.getAxis('bottom').setPen(axis_pen)
            
            # Customize context menu for cursor zoom
            self._setup_context_menu(plot_widget)
            
            # Setup tooltips for this plot widget
            self._setup_tooltip_for_plot(plot_widget, self.tooltips_enabled)
            
            self.plot_widgets.append(plot_widget)
            plot_layout.addWidget(plot_widget)

        # 3. Re-create the settings buttons and their layout container
        self.settings_container = QWidget()
        self.graph_settings_layout = QHBoxLayout(self.settings_container)
        self.graph_settings_layout.setContentsMargins(5, 2, 5, 2)
        self._update_graph_settings_buttons()

        # 4. Add the new containers to the main, permanent layout
        self.main_layout.addWidget(self.plot_container)
        self.main_layout.addWidget(self.settings_container)
        
        logger.info(f"UI rebuilt with {self.subplot_count} subplots.")

    def get_subplot_count(self) -> int:
        """Returns the current number of subplots."""
        return self.subplot_count
    
    def enable_datetime_axis(self, enable=True):
        """Enable datetime formatting for all plot x-axes."""
        for plot_widget in self.plot_widgets:
            bottom_axis = plot_widget.getAxis('bottom')
            if isinstance(bottom_axis, DateTimeAxisItem):
                bottom_axis.enable_datetime_mode(enable)
                # Force axis update by triggering a repaint
                plot_widget.update()
        logger.info(f"Datetime axis formatting {'enabled' if enable else 'disabled'}")

    def _get_signal_data_for_restore(self) -> Dict[str, Dict]:
        """Extracts data from current plot items for later restoration."""
        signal_data = {}
        for name, plot_item in self.current_signals.items():
            try:
                original_name = name.rsplit('_', 1)[0]
                if hasattr(plot_item, 'xData') and plot_item.xData is not None and \
                   hasattr(plot_item, 'yData') and plot_item.yData is not None:
                    signal_data[original_name] = {
                        'x': plot_item.xData.copy(),
                        'y': plot_item.yData.copy(),
                        'pen': plot_item.opts.get('pen', 'white')
                    }
            except Exception as e:
                logger.warning(f"Could not store data for signal '{name}': {e}")
        return signal_data

    def _restore_signals(self, signal_data: Dict[str, Dict]):
        """Restores signals to the newly created plots."""
        if not signal_data:
            logger.debug("No signal data to restore")
            return

        logger.info(f"Restoring {len(signal_data)} signals to {self.subplot_count} plots")
        
        # Clear any existing signals first
        self.current_signals.clear()
        
        # Get the signal mapping from parent to determine which signals go to which plots
        signal_mapping = {}
        if hasattr(self.parent, 'graph_signal_mapping'):
            # Get current tab index
            current_tab = 0
            if hasattr(self.parent, 'get_active_tab_index'):
                current_tab = self.parent.get_active_tab_index()
            
            # Get signal mapping for current tab
            tab_mapping = self.parent.graph_signal_mapping.get(current_tab, {})
            
            # Build reverse mapping: signal_name -> plot_index
            for plot_index, signals in tab_mapping.items():
                for signal_name in signals:
                    signal_mapping[signal_name] = plot_index
        
        # Restore signals according to their previous mapping, or distribute evenly if no mapping exists
        signal_names = list(signal_data.keys())
        restored_count = 0
        
        for name in signal_names:
            data = signal_data[name]
            
            # Determine target plot index
            if name in signal_mapping:
                # Use saved mapping
                plot_index = signal_mapping[name]
                # Ensure plot index is valid for current subplot count
                if plot_index >= self.subplot_count:
                    plot_index = plot_index % self.subplot_count
            else:
                # No mapping found, distribute evenly
                plot_index = restored_count % self.subplot_count
            
            try:
                self.add_signal(name, data['x'], data['y'], plot_index, pen=data['pen'])
                restored_count += 1
                logger.debug(f"Restored signal '{name}' to plot {plot_index}")
            except Exception as e:
                logger.error(f"Failed to restore signal '{name}' to plot {plot_index}: {e}")
        
        logger.info(f"Successfully restored {restored_count}/{len(signal_names)} signals")
        
        # Re-setup tooltips for all plots after signal restoration
        self._ensure_tooltips_after_rebuild()

    def _ensure_tooltips_after_rebuild(self):
        """Ensure tooltips are properly setup after plot rebuild."""
        try:
            # Clear old tooltip items that may reference deleted plot widgets
            old_tooltip_items = list(self.tooltip_items.keys())
            for old_plot_widget in old_tooltip_items:
                if old_plot_widget not in self.plot_widgets:
                    # Remove tooltip items for deleted plot widgets
                    del self.tooltip_items[old_plot_widget]
            
            # Setup tooltips for all current plot widgets
            for plot_widget in self.plot_widgets:
                if plot_widget not in self.tooltip_items:
                    self._setup_tooltip_for_plot(plot_widget, self.tooltips_enabled)
            
            logger.debug(f"Tooltips ensured for {len(self.plot_widgets)} plot widgets")
            
        except Exception as e:
            logger.warning(f"Failed to ensure tooltips after rebuild: {e}")

    def _clear_plots(self):
        """Clear all internal references to plot widgets and data items."""
        # Clear tooltip items before clearing plot widgets
        for plot_widget in list(self.tooltip_items.keys()):
            if plot_widget in self.tooltip_items:
                tooltip_item = self.tooltip_items[plot_widget]
                try:
                    tooltip_item.hide()
                    if hasattr(plot_widget, 'removeItem'):
                        plot_widget.removeItem(tooltip_item)
                except Exception as e:
                    logger.debug(f"Error removing tooltip item: {e}")
        
        self.tooltip_items.clear()
        self.plot_widgets.clear()
        self.current_signals.clear()
    
    def _update_graph_settings_buttons(self):
        """Update graph settings buttons based on current graph count."""
        # Clear existing buttons
        while self.graph_settings_layout.count():
            child = self.graph_settings_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Buttons removed - graph settings now accessible via statistics panel titles
    
    def _open_graph_settings(self, index: int):
        """Open settings dialog for a specific graph."""
        logger.info(f"Requesting settings for graph {index}")
        self.settings_requested.emit(index)
    
    def get_plot_panel(self) -> QWidget:
        """Get the plot panel widget."""
        return self.plot_panel
    
    def add_signal(self, name: str, x_data: np.ndarray, y_data: np.ndarray, 
                   plot_index: int = 0, pen=None, **kwargs):
        """Add a signal to a specific plot."""
        if not (0 <= plot_index < len(self.plot_widgets)):
            logger.warning(f"Invalid plot index: {plot_index}")
            return None
        
        plot_widget = self.plot_widgets[plot_index]
        
        # Create plot item
        if pen is None:
            pen = self._get_next_color(len(self.current_signals))
        
        plot_item = plot_widget.plot(x_data, y_data, pen=pen, name=name, **kwargs)
        
        # Store signal reference with a unique key
        signal_key = f"{name}_{plot_index}"
        self.current_signals[signal_key] = plot_item
        
        # Store the original color for this signal
        if isinstance(pen, str):
            self.signal_colors[signal_key] = pen
        elif hasattr(pen, 'color'):
            try:
                color = pen.color()
                if hasattr(color, 'name'):
                    self.signal_colors[signal_key] = color.name()
                else:
                    self.signal_colors[signal_key] = str(pen)
            except:
                self.signal_colors[signal_key] = str(pen)
        else:
            self.signal_colors[signal_key] = str(pen)
        
        logger.info(f"Added signal '{name}' to plot {plot_index} with color: {self.signal_colors[signal_key]}")
        return plot_item
    
    def remove_signal(self, name: str, plot_index: int = None):
        """Remove a signal from plots."""
        if plot_index is not None:
            # Remove from specific plot
            signal_key = f"{name}_{plot_index}"
            if signal_key in self.current_signals:
                plot_item = self.current_signals[signal_key]
                if hasattr(plot_item, 'getViewBox'):
                    plot_item.getViewBox().removeItem(plot_item)
                del self.current_signals[signal_key]
                # Remove color info as well
                if signal_key in self.signal_colors:
                    del self.signal_colors[signal_key]
        else:
            # Remove from all plots
            keys_to_remove = [key for key in self.current_signals.keys() if key.startswith(f"{name}_")]
            for key in keys_to_remove:
                plot_item = self.current_signals[key]
                if hasattr(plot_item, 'getViewBox'):
                    plot_item.getViewBox().removeItem(plot_item)
                del self.current_signals[key]
                # Remove color info as well
                if key in self.signal_colors:
                    del self.signal_colors[key]
    
    def clear_all_signals(self):
        """Clear all signals from all plots."""
        for plot_widget in self.plot_widgets:
            plot_widget.clear()
        self.current_signals.clear()
        self.signal_colors.clear()  # Clear color info as well
    
    def reset_view(self):
        """Reset the plot view to show all data."""
        for plot_widget in self.plot_widgets:
            plot_widget.autoRange()
    
    def _get_next_color(self, index: int) -> str:
        """Get the next color for a new signal."""
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        return colors[index % len(colors)]
    
    def get_signal_color(self, plot_index: int, signal_name: str) -> Optional[str]:
        """Get the color of a specific signal in a plot."""
        signal_key = f"{signal_name}_{plot_index}"
        if signal_key in self.current_signals:
            plot_item = self.current_signals[signal_key]
            if hasattr(plot_item, 'opts') and 'pen' in plot_item.opts:
                pen = plot_item.opts['pen']
                if hasattr(pen, 'color'):
                    return pen.color().name()
                elif isinstance(pen, str):
                    return pen
        return None
    
    def get_plot_widgets(self) -> List[pg.PlotWidget]:
        """Get all plot widgets."""
        return self.plot_widgets.copy()
    
    def get_current_signals(self) -> Dict[str, Any]:
        """Get current signals dictionary."""
        return self.current_signals.copy()
    
    def apply_normalization(self, signal_data: Dict[str, Dict]):
        """Apply normalization to signals."""
        for signal_key, plot_item in self.current_signals.items():
            if signal_key in signal_data:
                data = signal_data[signal_key]
                if 'normalized_y' in data:
                    plot_item.setData(data['x'], data['normalized_y'])
    
    def remove_normalization(self, signal_data: Dict[str, Dict]):
        """Remove normalization from signals."""
        for signal_key, plot_item in self.current_signals.items():
            if signal_key in signal_data:
                data = signal_data[signal_key]
                if 'original_y' in data:
                    plot_item.setData(data['x'], data['original_y'])
    
    def update_signal_data(self, name: str, x_data: np.ndarray, y_data: np.ndarray, plot_index: int = 0):
        """Update existing signal data."""
        signal_key = f"{name}_{plot_index}"
        if signal_key in self.current_signals:
            plot_item = self.current_signals[signal_key]
            plot_item.setData(x_data, y_data)
        else:
            # Signal doesn't exist, add it
            self.add_signal(name, x_data, y_data, plot_index)
    
    def set_grid_visibility(self, show_grid: bool):
        """Set grid visibility for all plots."""
        self.grid_visible = show_grid
        for plot_widget in self.plot_widgets:
            plot_widget.showGrid(x=show_grid, y=show_grid, alpha=self.theme_colors['grid_alpha'] if show_grid else 0.0)

    def apply_theme(self, colors: Dict[str, str]):
        """Apply a new theme to all plots."""
        self.theme_colors = {
            'background': colors.get('background', '#1e1e1e'),
            'axis_pen': colors.get('axis', '#ffffff'),
            'grid_alpha': 0.3
        }
        
        axis_pen = pg.mkPen(color=self.theme_colors['axis_pen'])
        
        for plot_widget in self.plot_widgets:
            plot_widget.setBackground(self.theme_colors['background'])
            plot_widget.getAxis('left').setPen(axis_pen)
            plot_widget.getAxis('bottom').setPen(axis_pen)
            
            plot_widget.showGrid(x=self.grid_visible, y=self.grid_visible, alpha=self.theme_colors['grid_alpha'] if self.grid_visible else 0.0)
            
    def set_line_width(self, width: int):
        """Set line width for all signals in all plots."""
        updated_count = 0
        
        for signal_key, plot_item in self.current_signals.items():
            try:
                # Önce saklanan orijinal rengi kullanmaya çalış
                pen_color = self.signal_colors.get(signal_key, None)
                pen_style = None
                
                # Eğer saklanan renk yoksa, mevcut pen'den almaya çalış
                if pen_color is None:
                    current_pen = None
                    
                    # opts dictionary'den pen al
                    if hasattr(plot_item, 'opts') and 'pen' in plot_item.opts:
                        current_pen = plot_item.opts['pen']
                    
                    # Mevcut pen'den renk ve stil bilgilerini al
                    if current_pen is not None:
                        try:
                            # Renk bilgisini al
                            if hasattr(current_pen, 'color'):
                                existing_color = current_pen.color()
                                # QColor'dan string'e çevir
                                if hasattr(existing_color, 'name'):
                                    pen_color = existing_color.name()
                                elif hasattr(existing_color, 'getRgb'):
                                    r, g, b, a = existing_color.getRgb()
                                    pen_color = f"#{r:02x}{g:02x}{b:02x}"
                            
                            # Stil bilgisini al
                            if hasattr(current_pen, 'style'):
                                pen_style = current_pen.style()
                                
                        except Exception as e:
                            logger.debug(f"Could not extract pen properties for {signal_key}: {e}")
                
                # Hala renk yoksa, signal index'e göre renk ata
                if pen_color is None:
                    # Signal key'den index çıkar ve renk ata
                    try:
                        # signal_key format: "signal_name_plot_index"
                        parts = signal_key.split('_')
                        if len(parts) >= 2:
                            # Son kısmı plot index olarak al
                            plot_index = int(parts[-1])
                            # Signal adından index hesapla
                            signal_name = '_'.join(parts[:-1])
                            signal_index = len([k for k in self.current_signals.keys() if k.startswith(signal_name)])
                            pen_color = self._get_next_color(signal_index)
                        else:
                            pen_color = self._get_next_color(updated_count)
                    except:
                        pen_color = self._get_next_color(updated_count)
                
                # Yeni pen oluştur - sadece width değişecek
                if pen_style is not None:
                    new_pen = pg.mkPen(color=pen_color, width=width, style=pen_style)
                else:
                    new_pen = pg.mkPen(color=pen_color, width=width)
                
                # Pen'i uygula
                if hasattr(plot_item, 'setPen'):
                    plot_item.setPen(new_pen)
                    updated_count += 1
                    logger.info(f"Updated line width to {width} for signal: {signal_key} (color: {pen_color})")
                        
            except Exception as e:
                logger.error(f"Failed to update line width for signal {signal_key}: {e}")
        
        logger.info(f"Set line width to {width} for {updated_count}/{len(self.current_signals)} signals")

    def set_snap_to_data(self, enabled: bool):
        """Enable or disable snap to data points functionality."""
        self.snap_to_data_enabled = enabled
        logger.info(f"PlotManager: Snap to data points {'enabled' if enabled else 'disabled'}")
        
        # Notify cursor manager if it exists
        if hasattr(self.parent, 'cursor_manager') and self.parent.cursor_manager:
            self.parent.cursor_manager.set_snap_to_data(enabled)

    def set_tooltips_enabled(self, enabled: bool):
        """Enable or disable tooltips functionality."""
        self.tooltips_enabled = enabled
        logger.info(f"PlotManager: Tooltips {'enabled' if enabled else 'disabled'}")
        
        # Update all plot widgets
        for plot_widget in self.plot_widgets:
            self._setup_tooltip_for_plot(plot_widget, enabled)

    def _setup_tooltip_for_plot(self, plot_widget, enabled: bool):
        """Setup or remove tooltip functionality for a specific plot widget."""
        try:
            if enabled:
                # Enable mouse tracking for hover events
                plot_widget.setMouseTracking(True)
                plot_widget.plotItem.vb.setMouseEnabled(x=True, y=True)  # Ensure mouse is enabled
                
                # Create tooltip item if it doesn't exist
                if plot_widget not in self.tooltip_items:
                    tooltip_item = pg.TextItem(
                        text="",
                        color=(255, 255, 255),
                        fill=pg.mkBrush(0, 0, 0, 150),  # More opaque background
                        border=pg.mkPen(255, 255, 255, width=1),
                        anchor=(0, 1)  # Bottom-left anchor
                    )
                    plot_widget.addItem(tooltip_item)
                    self.tooltip_items[plot_widget] = tooltip_item
                    tooltip_item.hide()  # Initially hidden
                    
                    # Store original leaveEvent to restore later
                    if not hasattr(plot_widget, '_original_leaveEvent'):
                        plot_widget._original_leaveEvent = plot_widget.leaveEvent
                
                # Disconnect any existing connections to avoid duplicates
                try:
                    plot_widget.scene().sigMouseMoved.disconnect()
                except:
                    pass
                
                # Connect mouse move events with unique connection
                plot_widget.scene().sigMouseMoved.connect(
                    lambda pos, pw=plot_widget: self._on_mouse_moved(pos, pw)
                )
                
                # Override leaveEvent to hide tooltip
                def custom_leave_event(event, pw=plot_widget):
                    self._on_mouse_left(pw)
                    # Call original leaveEvent if it exists
                    if hasattr(pw, '_original_leaveEvent') and pw._original_leaveEvent:
                        pw._original_leaveEvent(event)
                
                plot_widget.leaveEvent = custom_leave_event
                
            else:
                # Disable tooltips
                if plot_widget in self.tooltip_items:
                    tooltip_item = self.tooltip_items[plot_widget]
                    tooltip_item.hide()
                
                # Disconnect mouse events
                try:
                    plot_widget.scene().sigMouseMoved.disconnect()
                except:
                    pass
                
                # Restore original leaveEvent
                if hasattr(plot_widget, '_original_leaveEvent'):
                    plot_widget.leaveEvent = plot_widget._original_leaveEvent
                    
        except Exception as e:
            logger.warning(f"Failed to setup tooltip for plot widget: {e}")

    def _on_mouse_moved(self, pos, plot_widget):
        """Handle mouse movement over plot widget for tooltip display."""
        if not self.tooltips_enabled or plot_widget not in self.tooltip_items:
            return
            
        try:
            # Check if the position is valid
            if pos is None:
                return
                
            # Convert scene position to view coordinates
            view_pos = plot_widget.plotItem.vb.mapSceneToView(pos)
            x_pos = view_pos.x()
            y_pos = view_pos.y()
            
            # Check if coordinates are valid (not NaN or infinite)
            if not (isinstance(x_pos, (int, float)) and isinstance(y_pos, (int, float))):
                return
            if abs(x_pos) == float('inf') or abs(y_pos) == float('inf'):
                return
            
            # Get tooltip item
            tooltip_item = self.tooltip_items[plot_widget]
            
            # Find the closest signal to mouse cursor
            closest_signal_info = self._find_closest_signal_to_cursor(x_pos, y_pos, plot_widget)
            
            if closest_signal_info:
                tooltip_text = self._generate_enhanced_tooltip_text(x_pos, y_pos, closest_signal_info)
                
                if tooltip_text and len(tooltip_text.strip()) > 0:
                    # Position tooltip with slight offset to avoid cursor overlap
                    view_range = plot_widget.plotItem.vb.viewRange()
                    x_range = view_range[0]
                    y_range = view_range[1]
                    
                    # Calculate offset (5% of visible range)
                    x_offset = (x_range[1] - x_range[0]) * 0.05
                    y_offset = (y_range[1] - y_range[0]) * 0.05
                    
                    tooltip_x = x_pos + x_offset
                    tooltip_y = y_pos + y_offset
                    
                    tooltip_item.setPos(tooltip_x, tooltip_y)
                    tooltip_item.setText(tooltip_text)
                    tooltip_item.show()
                else:
                    tooltip_item.hide()
            else:
                # Show basic position info even if no signal found
                basic_text = f"📍 Position:\n   X: {x_pos:.6f}\n   Y: {y_pos:.6f}"
                tooltip_item.setPos(x_pos, y_pos)
                tooltip_item.setText(basic_text)
                tooltip_item.show()
                
        except Exception as e:
            logger.debug(f"Error updating tooltip: {e}")
            # Hide tooltip on error to prevent stuck tooltips
            if plot_widget in self.tooltip_items:
                self.tooltip_items[plot_widget].hide()

    def _on_mouse_left(self, plot_widget):
        """Handle mouse leaving the plot widget."""
        if plot_widget in self.tooltip_items:
            tooltip_item = self.tooltip_items[plot_widget]
            tooltip_item.hide()

    def _find_closest_signal_to_cursor(self, x_pos: float, y_pos: float, plot_widget):
        """Find the signal closest to the mouse cursor position."""
        try:
            import numpy as np
            closest_signal = None
            min_distance = float('inf')
            
            # Get the plot index for this widget
            try:
                plot_index = self.plot_widgets.index(plot_widget)
            except (ValueError, AttributeError):
                plot_index = 0
            
            if not hasattr(self.parent, 'signal_processor'):
                return None
                
            signal_processor = self.parent.signal_processor
            signal_names = signal_processor.get_signal_names()
            
            if not signal_names:
                return None
            
            for signal_name in signal_names:
                try:
                    # Check if this signal is displayed on this plot
                    signal_key = f"{signal_name}_{plot_index}"
                    if signal_key not in self.current_signals:
                        continue
                    
                    signal_data = signal_processor.get_signal_data(signal_name)
                    if not signal_data or 'x_data' not in signal_data or 'y_data' not in signal_data:
                        continue
                        
                    x_data = signal_data['x_data']
                    y_data = signal_data['y_data']
                    
                    if len(x_data) == 0 or len(y_data) == 0:
                        continue
                        
                    x_array = np.array(x_data)
                    y_array = np.array(y_data)
                    
                    # Check for valid arrays
                    if x_array.size == 0 or y_array.size == 0:
                        continue
                    
                    # Check if position is within reasonable data range
                    x_min, x_max = np.min(x_array), np.max(x_array)
                    if x_pos < x_min or x_pos > x_max:
                        continue
                    
                    # Find the closest data point to the cursor
                    # Use a tolerance to avoid excessive computation for large datasets
                    if len(x_array) > 10000:
                        # For large datasets, use interpolation approach
                        try:
                            interpolated_y = np.interp(x_pos, x_data, y_data)
                            distance = abs(y_pos - interpolated_y)
                            
                            if distance < min_distance:
                                min_distance = distance
                                # Find closest actual data point for display
                                idx = np.argmin(np.abs(x_array - x_pos))
                                closest_signal = {
                                    'name': signal_name,
                                    'x_value': x_array[idx],
                                    'y_value': y_array[idx],
                                    'distance': distance,
                                    'interpolated_y': interpolated_y
                                }
                        except Exception:
                            continue
                    else:
                        # For smaller datasets, use exact distance calculation
                        distances = np.sqrt((x_array - x_pos)**2 + (y_array - y_pos)**2)
                        min_idx = np.argmin(distances)
                        distance = distances[min_idx]
                        
                        if distance < min_distance:
                            min_distance = distance
                            try:
                                interpolated_y = np.interp(x_pos, x_data, y_data)
                            except Exception:
                                interpolated_y = y_array[min_idx]
                                
                            closest_signal = {
                                'name': signal_name,
                                'x_value': x_array[min_idx],
                                'y_value': y_array[min_idx],
                                'distance': distance,
                                'interpolated_y': interpolated_y
                            }
                            
                except Exception as e:
                    logger.debug(f"Error processing signal {signal_name}: {e}")
                    continue
            
            return closest_signal
            
        except Exception as e:
            logger.debug(f"Error finding closest signal: {e}")
            return None

    def _generate_enhanced_tooltip_text(self, x_pos: float, y_pos: float, closest_signal_info: dict) -> str:
        """Generate enhanced tooltip text showing the closest signal information."""
        try:
            tooltip_lines = []
            
            if closest_signal_info:
                # Signal name
                signal_name = closest_signal_info['name']
                display_name = signal_name
                if len(display_name) > 25:
                    display_name = display_name[:22] + "..."
                
                tooltip_lines.append(f"📊 Signal: {display_name}")
                tooltip_lines.append("")  # Empty line for separation
                
                # Coordinates
                tooltip_lines.append(f"📍 Mouse Position:")
                tooltip_lines.append(f"   X: {x_pos:.6f}")
                tooltip_lines.append(f"   Y: {y_pos:.6f}")
                tooltip_lines.append("")
                
                # Closest data point
                tooltip_lines.append(f"🎯 Closest Data Point:")
                tooltip_lines.append(f"   X: {closest_signal_info['x_value']:.6f}")
                tooltip_lines.append(f"   Y: {closest_signal_info['y_value']:.6f}")
                tooltip_lines.append("")
                
                # Interpolated value at mouse X position
                tooltip_lines.append(f"📈 Value at Mouse X:")
                tooltip_lines.append(f"   Y: {closest_signal_info['interpolated_y']:.6f}")
                
            else:
                # Fallback if no signal found
                tooltip_lines.append(f"📍 Position:")
                tooltip_lines.append(f"   X: {x_pos:.6f}")
                tooltip_lines.append(f"   Y: {y_pos:.6f}")
                tooltip_lines.append("")
                tooltip_lines.append("No signals found at this position")
            
            return "\n".join(tooltip_lines)
            
        except Exception as e:
            logger.debug(f"Error generating enhanced tooltip text: {e}")
            return f"X: {x_pos:.6f}\nY: {y_pos:.6f}"

    def _generate_tooltip_text(self, x_pos: float, y_pos: float) -> str:
        """Generate tooltip text showing signal values at the given position."""
        try:
            tooltip_lines = [f"X: {x_pos:.6f}"]
            
            # Get signal values at this X position
            if hasattr(self.parent, 'signal_processor'):
                signal_processor = self.parent.signal_processor
                signal_names = signal_processor.get_signal_names()
                
                values_found = 0
                for signal_name in signal_names[:5]:  # Limit to first 5 signals to avoid clutter
                    signal_data = signal_processor.get_signal_data(signal_name)
                    if signal_data and 'x_data' in signal_data and 'y_data' in signal_data:
                        x_data = signal_data['x_data']
                        y_data = signal_data['y_data']
                        
                        if len(x_data) > 0 and len(y_data) > 0:
                            # Find closest data point
                            import numpy as np
                            x_array = np.array(x_data)
                            
                            # Check if position is within data range
                            if x_pos >= x_array[0] and x_pos <= x_array[-1]:
                                # Interpolate value at x_pos
                                y_value = np.interp(x_pos, x_data, y_data)
                                
                                # Shorten signal name if too long
                                display_name = signal_name
                                if len(display_name) > 20:
                                    display_name = display_name[:17] + "..."
                                
                                tooltip_lines.append(f"{display_name}: {y_value:.6f}")
                                values_found += 1
                
                if values_found == 0:
                    tooltip_lines.append("No signals at this position")
                elif len(signal_names) > 5:
                    tooltip_lines.append(f"... and {len(signal_names) - 5} more signals")
            
            return "\n".join(tooltip_lines)
            
        except Exception as e:
            logger.debug(f"Error generating tooltip text: {e}")
            return f"X: {x_pos:.6f}\nY: {y_pos:.6f}"

    def _setup_context_menu(self, plot_widget):
        """Setup custom context menu for plot widget."""
        # Get the original context menu
        original_menu = plot_widget.plotItem.ctrlMenu
        
        # Add separator before our custom actions
        original_menu.addSeparator()
        
        # Add cursor zoom action
        zoom_action = QAction("🎯 Zoom to Cursors", self)
        zoom_action.setToolTip("Zoom to the range between dual cursors")
        zoom_action.triggered.connect(self._on_zoom_to_cursors)
        original_menu.addAction(zoom_action)
        
        # Store reference to update enabled state
        plot_widget._cursor_zoom_action = zoom_action
        
        # Connect to menu about to show to update action state
        original_menu.aboutToShow.connect(lambda: self._update_context_menu_state(plot_widget))
        
    def _update_context_menu_state(self, plot_widget):
        """Update context menu action states based on current cursor state."""
        if hasattr(plot_widget, '_cursor_zoom_action'):
            # Check if cursor manager exists and can zoom
            cursor_manager = getattr(self.parent, 'cursor_manager', None)
            can_zoom = False
            if cursor_manager and hasattr(cursor_manager, 'can_zoom_to_cursors'):
                try:
                    can_zoom = cursor_manager.can_zoom_to_cursors()
                    # Ensure it's a boolean
                    can_zoom = bool(can_zoom) if can_zoom is not None else False
                except Exception as e:
                    logger.warning(f"Error checking cursor zoom state: {e}")
                    can_zoom = False
            plot_widget._cursor_zoom_action.setEnabled(can_zoom)
            
    def _on_zoom_to_cursors(self):
        """Handle zoom to cursors action from context menu."""
        cursor_manager = getattr(self.parent, 'cursor_manager', None)
        if cursor_manager:
            success = cursor_manager.zoom_to_cursors()
            if success:
                logger.info("Zoomed to cursor range from context menu")
            else:
                logger.warning("Failed to zoom to cursors - check cursor positions")
