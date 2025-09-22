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
            
            logger.info(f"✅ Successfully changed subplot count to {count}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to change subplot count: {e}", exc_info=True)
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
            return

        signal_names = list(signal_data.keys())
        for i, name in enumerate(signal_names):
            data = signal_data[name]
            # Distribute signals across the new plots
            plot_index = i % self.subplot_count
            try:
                self.add_signal(name, data['x'], data['y'], plot_index, pen=data['pen'])
            except Exception as e:
                logger.error(f"Failed to restore signal '{name}' to plot {plot_index}: {e}")

    def _clear_plots(self):
        """Clear all internal references to plot widgets and data items."""
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
        else:
            # Remove from all plots
            keys_to_remove = [key for key in self.current_signals.keys() if key.startswith(f"{name}_")]
            for key in keys_to_remove:
                plot_item = self.current_signals[key]
                if hasattr(plot_item, 'getViewBox'):
                    plot_item.getViewBox().removeItem(plot_item)
                del self.current_signals[key]
    
    def clear_all_signals(self):
        """Clear all signals from all plots."""
        for plot_widget in self.plot_widgets:
            plot_widget.clear()
        self.current_signals.clear()
    
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
                # PyQtGraph PlotDataItem için doğru yöntem:
                # Mevcut pen'den renk ve stili al, sadece width'i değiştir
                
                current_pen = None
                pen_color = None
                pen_style = None
                
                # Method 1: opts dictionary'den pen al (en güvenilir)
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
                
                # Eğer renk alınamazsa, mevcut görsel rengi korumaya çalış
                if pen_color is None:
                    # Son çare: plot_item'dan rengi almaya çalış
                    try:
                        if hasattr(plot_item, 'curve') and hasattr(plot_item.curve, 'pen'):
                            curve_pen = plot_item.curve.pen()
                            if hasattr(curve_pen, 'color'):
                                curve_color = curve_pen.color()
                                if hasattr(curve_color, 'name'):
                                    pen_color = curve_color.name()
                    except:
                        pass
                
                # Hala renk yoksa varsayılan renk kullan
                if pen_color is None:
                    pen_color = '#ffffff'  # Beyaz fallback
                
                # Yeni pen oluştur - sadece width değişecek
                if pen_style is not None:
                    new_pen = pg.mkPen(color=pen_color, width=width, style=pen_style)
                else:
                    new_pen = pg.mkPen(color=pen_color, width=width)
                
                # Pen'i uygula
                if hasattr(plot_item, 'setPen'):
                    plot_item.setPen(new_pen)
                    updated_count += 1
                    logger.info(f"Updated line width to {width} for signal: {signal_key} (preserved color: {pen_color})")
                        
            except Exception as e:
                logger.error(f"Failed to update line width for signal {signal_key}: {e}")
        
        logger.info(f"Set line width to {width} for {updated_count}/{len(self.current_signals)} signals")

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
