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
        
        # Y ekseni hizalama için sabit genişlik ayarı
        self.y_axis_width = 80  # Piksel cinsinden sabit genişlik
        
        # Snap to data points feature
        self.snap_to_data_enabled = False
        
        # Tooltips feature
        self.tooltips_enabled = False  # Default disabled - user can enable if needed
        self.tooltip_items = {}  # Store tooltip items per plot widget
        
        self._setup_plot_panel()
        self._rebuild_ui()  # Initial UI creation
    
    def _get_global_settings(self) -> dict:
        """Get global settings from parent GraphContainer."""
        if hasattr(self.parent, 'get_global_settings'):
            return self.parent.get_global_settings()

        logger.warning(f"PlotManager: Parent {type(self.parent).__name__} does not have get_global_settings method. Critical error.")
        # This fallback should ideally not be reached now.
        return {
            'normalize': False,
            'show_grid': True,
            'autoscale': True,
            'show_legend': True,
            'show_tooltips': False,
            'snap_to_data': False,
            'line_width': 1,
            'x_axis_mouse': True,
            'y_axis_mouse': True
        }
    
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
        
        # Get global settings from parent
        global_settings = self._get_global_settings()
        
        for i in range(self.subplot_count):
            # Create custom datetime axis for bottom axis
            datetime_axis = DateTimeAxisItem(orientation='bottom')
            plot_widget = pg.PlotWidget(axisItems={'bottom': datetime_axis})
            legend = plot_widget.addLegend() # Add legend to each plot

            # Apply global legend setting
            show_legend = global_settings.get('show_legend', True)
            if legend:
                legend.setVisible(show_legend)

            # Link X-axes and manage visibility
            if i > 0 and self.plot_widgets: # Link current plot to the first one
                plot_widget.setXLink(self.plot_widgets[0])
                # CRITICAL FIX: After linking, sync the X range with the first plot
                # This ensures all linked plots start with the same X range
                try:
                    first_plot_x_range = self.plot_widgets[0].getViewBox().viewRange()[0]
                    plot_widget.setXRange(*first_plot_x_range, padding=0)
                    logger.debug(f"[FIX] Synced plot {i} X range with first plot: {first_plot_x_range}")
                except Exception as e:
                    logger.debug(f"Could not sync X range for plot {i}: {e}")
            
            # Hide X-axis for all but the last plot
            if i < self.subplot_count - 1:
                plot_widget.getAxis('bottom').setStyle(showValues=False)
            
            plot_widget.setLabel('left', f'Channel {i+1}')
            
            # Y ekseni hizalama sorunu için sabit genişlik ayarla
            left_axis = plot_widget.getAxis('left')
            left_axis.setWidth(self.y_axis_width)  # Y ekseni için sabit genişlik (piksel)
            
            # Apply global grid setting instead of hardcoded True
            show_grid = global_settings.get('show_grid', True)
            self.grid_visible = show_grid  # Update internal state
            plot_widget.showGrid(x=show_grid, y=show_grid, alpha=self.theme_colors['grid_alpha'] if show_grid else 0.0)
            plot_widget.setBackground(self.theme_colors['background'])
            
            # PERFORMANCE OPTIMIZATIONS for PyQtGraph
            plot_widget.setDownsampling(auto=True, mode='peak')  # Auto downsampling
            plot_widget.setClipToView(True)  # Only render visible data
            plot_widget.setAntialiasing(False)  # Disable antialiasing for speed
            
            axis_pen = pg.mkPen(color=self.theme_colors['axis_pen'])
            plot_widget.getAxis('left').setPen(axis_pen)
            plot_widget.getAxis('bottom').setPen(axis_pen)
            
            # Apply global autoscale setting for Y axis
            autoscale = global_settings.get('autoscale', True)
            plot_widget.enableAutoRange(axis='y', enable=autoscale)
            
            # CRITICAL FIX: Disable X-axis auto-range by default
            # This prevents unwanted X-axis zoom changes when data is added
            # We'll manually trigger autoRange() when needed (e.g., on data load)
            plot_widget.enableAutoRange(axis='x', enable=False)
            
            # Context menu setup removed - zoom functionality moved to Graph Settings panel
            
            # Setup tooltips for this plot widget using global setting
            tooltips_enabled = global_settings.get('show_tooltips', False)
            self.tooltips_enabled = tooltips_enabled  # Update internal state
            self._setup_tooltip_for_plot(plot_widget, tooltips_enabled)
            
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
        
        # Only restore signals that have explicit mapping - don't auto-distribute to new graphs
        signal_names = list(signal_data.keys())
        restored_count = 0
        
        for name in signal_names:
            data = signal_data[name]
            
            # Only restore signals that have explicit mapping
            if name in signal_mapping:
                # Use saved mapping
                plot_index = signal_mapping[name]
                # Ensure plot index is valid for current subplot count
                if plot_index >= self.subplot_count:
                    plot_index = plot_index % self.subplot_count
                
                try:
                    self.add_signal(name, data['x'], data['y'], plot_index, pen=data['pen'])
                    restored_count += 1
                    logger.debug(f"Restored signal '{name}' to plot {plot_index}")
                except Exception as e:
                    logger.error(f"Failed to restore signal '{name}' to plot {plot_index}: {e}")
            else:
                # No mapping found - don't auto-distribute to new graphs
                # New graphs should start empty until user explicitly assigns signals
                logger.debug(f"Signal '{name}' has no mapping - not restoring to new graphs")
        
        logger.info(f"Successfully restored {restored_count}/{len(signal_names)} signals (unmapped signals not auto-distributed)")
        
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
    
    def _downsample_data(self, x_data: np.ndarray, y_data: np.ndarray, max_points: int = 5000):
        """
        Downsample data for faster rendering.
        Uses intelligent downsampling to preserve visual appearance.
        
        Args:
            x_data: X-axis data
            y_data: Y-axis data
            max_points: Maximum number of points to display
            
        Returns:
            Tuple of (downsampled_x, downsampled_y)
        """
        data_len = len(x_data)
        
        # No downsampling needed
        if data_len <= max_points:
            return x_data, y_data
        
        # Calculate step size
        step = max(1, data_len // max_points)
        
        # Simple downsampling - take every Nth point
        # This preserves peaks better than just slicing
        downsampled_x = x_data[::step]
        downsampled_y = y_data[::step]
        
        logger.debug(f"Downsampled {data_len} points to {len(downsampled_x)} points (step={step})")
        return downsampled_x, downsampled_y
    
    def add_signal(self, name: str, x_data: np.ndarray, y_data: np.ndarray, 
                   plot_index: int = 0, pen=None, **kwargs):
        """Add a signal to a specific plot with automatic downsampling."""
        if not (0 <= plot_index < len(self.plot_widgets)):
            logger.warning(f"Invalid plot index: {plot_index}")
            return None
        
        plot_widget = self.plot_widgets[plot_index]
        
        # PERFORMANCE OPTIMIZATION: Downsample data if too many points
        original_len = len(x_data)
        if original_len > 5000:
            x_data, y_data = self._downsample_data(x_data, y_data, max_points=5000)
            logger.info(f"Signal '{name}' downsampled from {original_len} to {len(x_data)} points")
        
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
        """Clear all signals from all plots while preserving tooltips and deviation lines."""
        # Store tooltip items before clearing
        tooltip_backup = {}
        deviation_backup = {}
        
        for i, plot_widget in enumerate(self.plot_widgets):
            # Backup tooltips
            if plot_widget in self.tooltip_items:
                tooltip_backup[plot_widget] = self.tooltip_items[plot_widget]
                # Temporarily remove tooltip from plot to prevent it being cleared
                try:
                    plot_widget.removeItem(tooltip_backup[plot_widget])
                except:
                    pass
            
            # Backup deviation lines and other non-signal items
            deviation_backup[plot_widget] = []
            for item in plot_widget.listDataItems():
                # Check if this is a deviation line by looking at its pen color and width
                if hasattr(item, 'opts') and 'pen' in item.opts:
                    pen = item.opts['pen']
                    if hasattr(pen, 'color') and hasattr(pen, 'width'):
                        # Red lines with width >= 3 are likely deviation lines
                        if (pen.color().name() in ['#ff0000', '#FF0000'] and pen.width() >= 3) or \
                           (hasattr(item, 'name') and item.name() and 'deviation' in item.name().lower()):
                            deviation_backup[plot_widget].append(item)
                            try:
                                plot_widget.removeItem(item)
                            except:
                                pass
        
        # Clear all plot content
        for plot_widget in self.plot_widgets:
            plot_widget.clear()
        
        # Restore tooltips
        for plot_widget, tooltip_item in tooltip_backup.items():
            try:
                plot_widget.addItem(tooltip_item)
                tooltip_item.hide()  # Keep hidden until mouse moves
            except Exception as e:
                logger.debug(f"Failed to restore tooltip: {e}")
                # Re-create tooltip if restoration failed
                self._setup_tooltip_for_plot(plot_widget, self.tooltips_enabled)
        
        # Restore deviation lines
        for plot_widget, deviation_items in deviation_backup.items():
            for item in deviation_items:
                try:
                    plot_widget.addItem(item)
                    logger.debug(f"Restored deviation line: {getattr(item, 'name', 'unnamed')}")
                except Exception as e:
                    logger.debug(f"Failed to restore deviation line: {e}")
        
        self.current_signals.clear()
        self.signal_colors.clear()  # Clear color info as well
        
        logger.debug("Cleared all signals while preserving tooltips and deviation lines")
    
    def reset_view(self):
        """Reset the plot view to show all data including limit lines."""
        if len(self.plot_widgets) == 0:
            return
        
        # CRITICAL FIX: X-axis is linked across all plots, so handle it globally
        # Step 1: Enable X auto-range for ALL plots
        for plot_widget in self.plot_widgets:
            plot_widget.enableAutoRange(axis='x', enable=True)
        
        # Step 2: Trigger X auto-range on the first plot (affects all due to linking)
        self.plot_widgets[0].autoRange(padding=0)
        
        # Step 3: Disable X auto-range for all plots
        for plot_widget in self.plot_widgets:
            plot_widget.enableAutoRange(axis='x', enable=False)
        
        logger.info(f"[RESET VIEW] X-axis auto-ranged globally for all {len(self.plot_widgets)} linked plots")
        
        # Step 4: Now handle Y-axis individually for each plot
        for plot_widget in self.plot_widgets:
            plot_widget.enableAutoRange(axis='y', enable=True)
            plot_widget.autoRange()
            plot_widget.enableAutoRange(axis='y', enable=False)
    
    def redraw_all_plots(self):
        """Redraw all plots to reflect updated data."""
        for plot_widget in self.plot_widgets:
            # Force a repaint/redraw of the plot widget
            plot_widget.update()
            plot_widget.repaint()
        
        logger.debug("Redrawn all plots")
    
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
    
    def clear_signals(self):
        """Tüm sinyalleri temizle."""
        try:
            # Plot widget'larındaki tüm sinyalleri temizle
            for plot_widget in self.plot_widgets:
                plot_widget.clear()
            
            # Sinyal referanslarını temizle
            self.current_signals.clear()
            self.signal_colors.clear()
            
            logger.debug("All signals cleared from plots")
            
        except Exception as e:
            logger.error(f"Error clearing signals: {e}")

    def render_signals(self, all_signals: Dict[str, Any]):
        """Tüm sinyalleri plot'lara render et."""
        try:
            # Mevcut sinyalleri temizle
            self.clear_signals()
            
            # Her sinyali uygun plot'a ekle
            for signal_name, signal_data in all_signals.items():
                if 'x_data' in signal_data and 'y_data' in signal_data:
                    x_data = signal_data['x_data']
                    y_data = signal_data['y_data']
                    
                    # Plot indeksini belirle (şimdilik tüm sinyaller plot 0'a)
                    plot_index = 0
                    
                    # Sinyali ekle
                    self.add_signal(signal_name, x_data, y_data, plot_index)
            
            logger.info(f"Rendered {len(all_signals)} signals to plots")
            
        except Exception as e:
            logger.error(f"Error rendering signals: {e}")
    
    def update_plots(self, all_signals: Dict[str, Any]):
        """Alias for render_signals for backward compatibility."""
        self.render_signals(all_signals)

    def get_subplot_count(self) -> int:
        """Subplot sayısını döndür."""
        return self.subplot_count

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
    
    def update_global_settings(self):
        """Update plot widgets with current global settings."""
        global_settings = self._get_global_settings()
        
        # Update grid visibility
        show_grid = global_settings.get('show_grid', True)
        self.set_grid_visibility(show_grid)
        
        # Update autoscale
        autoscale = global_settings.get('autoscale', True)
        for plot_widget in self.plot_widgets:
            plot_widget.enableAutoRange(axis='y', enable=autoscale)
        
        # Update legend visibility
        show_legend = global_settings.get('show_legend', True)
        self.set_legend_visibility(show_legend)
        
        # Update tooltips
        tooltips_enabled = global_settings.get('show_tooltips', False)
        self.tooltips_enabled = tooltips_enabled
        for plot_widget in self.plot_widgets:
            self._setup_tooltip_for_plot(plot_widget, tooltips_enabled)
        
        logger.debug("Plot widgets updated with current global settings")
    
    def set_tooltips_enabled(self, enabled: bool):
        """Set tooltips enabled/disabled for all plots."""
        self.tooltips_enabled = enabled
        for plot_widget in self.plot_widgets:
            self._setup_tooltip_for_plot(plot_widget, enabled)

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
                        fill=pg.mkBrush(0, 0, 0, 255),  # Completely opaque black background
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
        if not self.tooltips_enabled:
            return
            
        if plot_widget not in self.tooltip_items:
            logger.warning(f"Tooltip item not found for plot_widget, creating it now")
            self._setup_tooltip_for_plot(plot_widget, True)
            if plot_widget not in self.tooltip_items:
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
            
            # Generate tooltip text
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
                logger.debug(f"Tooltip shown at ({tooltip_x:.2f}, {tooltip_y:.2f}): {tooltip_text[:30]}")
            else:
                tooltip_item.hide()
                logger.debug(f"Tooltip hidden: empty text")
                
        except Exception as e:
            logger.error(f"Error updating tooltip: {e}", exc_info=True)
            # Hide tooltip on error to prevent stuck tooltips
            if plot_widget in self.tooltip_items:
                self.tooltip_items[plot_widget].hide()

    def _on_mouse_left(self, plot_widget):
        """Handle mouse leaving the plot widget."""
        if plot_widget in self.tooltip_items:
            tooltip_item = self.tooltip_items[plot_widget]
            tooltip_item.hide()

    def _find_closest_signal_to_cursor(self, x_pos: float, y_pos: float, plot_widget):
        """Find the signal closest to the mouse cursor position in Y-axis."""
        try:
            import numpy as np
            closest_signal = None
            min_y_distance = float('inf')
            
            # Get the plot index for this widget
            try:
                plot_index = self.plot_widgets.index(plot_widget)
            except (ValueError, AttributeError):
                plot_index = 0
            
            # Get signal processor - try parent (GraphContainer) first, then main_widget
            signal_processor = None
            if hasattr(self.parent, 'signal_processor') and self.parent.signal_processor:
                signal_processor = self.parent.signal_processor
            elif hasattr(self.parent, 'main_widget') and hasattr(self.parent.main_widget, 'signal_processor'):
                signal_processor = self.parent.main_widget.signal_processor
            
            if not signal_processor:
                logger.debug("No signal_processor found on parent or main_widget")
                return None
            
            # Get signal names from signal_data keys
            if not hasattr(signal_processor, 'signal_data'):
                logger.debug("signal_processor has no signal_data attribute")
                return None
                
            signal_names = list(signal_processor.signal_data.keys())
            
            if not signal_names:
                logger.debug("No signal names found in signal_data")
                return None
            
            logger.debug(f"Finding closest signal - Available signals: {signal_names[:3]}..., current_signals keys: {list(self.current_signals.keys())[:3]}..., plot_index: {plot_index}")
            
            for signal_name in signal_names:
                try:
                    # Check if this signal is displayed on this plot
                    signal_key = f"{signal_name}_{plot_index}"
                    if signal_key not in self.current_signals:
                        logger.debug(f"Signal key '{signal_key}' not in current_signals")
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
                    
                    # Find the Y value at the current mouse X position (interpolated)
                    try:
                        interpolated_y = np.interp(x_pos, x_data, y_data)
                        
                        # Calculate Y-axis distance only
                        y_distance = abs(y_pos - interpolated_y)
                        
                        if y_distance < min_y_distance:
                            min_y_distance = y_distance
                            
                            # Find closest actual X data point for reference
                            idx = np.argmin(np.abs(x_array - x_pos))
                            
                            closest_signal = {
                                'name': signal_name,
                                'x_value': x_pos,  # Use mouse X position
                                'y_value': interpolated_y,  # Use interpolated Y value at mouse X
                                'closest_data_x': x_array[idx],  # Closest actual data point X
                                'closest_data_y': y_array[idx],  # Closest actual data point Y
                                'y_distance': y_distance
                            }
                            logger.debug(f"Found closer signal: {signal_name}, y_distance: {y_distance:.3f}, interpolated_y: {interpolated_y:.3f}")
                    except Exception as e:
                        logger.debug(f"Error interpolating for signal {signal_name}: {e}")
                        continue
                            
                except Exception as e:
                    logger.debug(f"Error processing signal {signal_name}: {e}")
                    continue
            
            if closest_signal:
                logger.debug(f"Returning closest signal: {closest_signal['name']} with y_value: {closest_signal['y_value']:.3f}")
            else:
                logger.debug(f"No closest signal found")
            
            return closest_signal
            
        except Exception as e:
            logger.error(f"Error finding closest signal: {e}", exc_info=True)
            return None

    def _generate_enhanced_tooltip_text(self, x_pos: float, y_pos: float, closest_signal_info: dict) -> str:
        """Generate tooltip text showing parameter name and values at cursor position."""
        try:
            tooltip_lines = []
            
            if closest_signal_info:
                # Parameter name as title - no emoji to avoid Unicode issues
                signal_name = closest_signal_info['name']
                display_name = signal_name
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."
                
                # Show parameter name and its value only
                tooltip_lines.append(display_name)
                tooltip_lines.append(f"Deger: {closest_signal_info['y_value']:.6f}")
                
            else:
                # Fallback if no signal found - show position
                tooltip_lines.append(f"Pozisyon")
                tooltip_lines.append(f"Y: {y_pos:.6f}")
            
            result = "\n".join(tooltip_lines)
            logger.debug(f"Generated tooltip: '{result}' (has_signal: {closest_signal_info is not None})")
            return result
            
        except Exception as e:
            logger.error(f"Error generating enhanced tooltip text: {e}")
            return f"Y: {y_pos:.6f}"

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

    def get_visible_signals(self) -> List[str]:
        """Get a list of unique signal names currently visible on the plots."""
        signal_names = set()
        for signal_key in self.current_signals.keys():
            # signal_key is in format "signal_name_plot_index"
            # We want to extract just "signal_name"
            base_name = '_'.join(signal_key.split('_')[:-1])
            if base_name:
                signal_names.add(base_name)
        return list(signal_names)

    # Context menu methods removed - zoom functionality moved to Graph Settings panel

    def set_legend_visibility(self, visible: bool):
        """Set legend visibility for all plots."""
        for plot_widget in self.plot_widgets:
            # PyQtGraph'ta legend'e erişim için plotItem üzerinden gitmek gerekiyor
            legend = plot_widget.plotItem.legend
            if legend:
                legend.setVisible(visible)
    
    def set_y_axis_width(self, width: int):
        """Y ekseni genişliğini ayarla (grafik hizalama için)."""
        self.y_axis_width = width
        for plot_widget in self.plot_widgets:
            left_axis = plot_widget.getAxis('left')
            left_axis.setWidth(width)
        logger.info(f"Y ekseni genişliği {width} piksel olarak ayarlandı")
    
    def get_y_axis_width(self) -> int:
        """Mevcut Y ekseni genişliğini döndür."""
        return self.y_axis_width
