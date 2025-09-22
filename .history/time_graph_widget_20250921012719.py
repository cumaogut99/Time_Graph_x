# type: ignore
"""
Advanced Time Graph Widget - Refactored Main Class

Professional architecture with separation of concerns for maintainability and performance.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import vaex
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QLabel, QDialog, QGroupBox, 
    QHBoxLayout, QTabWidget, QGridLayout, QStackedWidget, QToolButton,
    QTabBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal as Signal
from PyQt5.QtGui import QIcon

# Import our modular components - Always use absolute imports for standalone app
from filter_manager import FilterManager
from graph_renderer import GraphRenderer
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from toolbar_manager import ToolbarManager
from plot_manager import PlotManager
from legend_manager import LegendManager
from signal_processor import SignalProcessor
from theme_manager import ThemeManager
from cursor_manager import CursorManager
from statistics_panel import StatisticsPanel
from data_manager import TimeSeriesDataManager
from settings_panel_manager import SettingsPanelManager
from statistics_settings_panel_manager import StatisticsSettingsPanelManager
from graph_settings_panel_manager import GraphSettingsPanelManager
from bitmask_panel_manager import BitmaskPanelManager
from graph_settings_dialog import GraphSettingsDialog
from graph_advanced_settings_dialog import GraphAdvancedSettingsDialog
from graph_container import GraphContainer


logger = logging.getLogger(__name__)

class TimeGraphWidget(QWidget):
    """
    Advanced Time Graph Widget - Professional Architecture
    
    Modular components:
    - ToolbarManager: Handles all toolbar controls
    - PlotManager: Manages synchronized plots
    - LegendManager: Real-time signal legend
    - SignalProcessor: High-performance signal processing
    - ThemeManager: Professional theming
    """
    
    # Signals for external communication
    data_changed = Signal(object)
    cursor_moved = Signal(str, object)
    range_selected = Signal(tuple)
    statistics_updated = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_containers = []  # Initialize the list here
        
        # Duty cycle threshold settings
        self.duty_cycle_threshold_mode = "auto"  # "auto" or "manual"
        self.duty_cycle_threshold_value = 0.0
        
        # Initialize modular components
        self.filter_manager = FilterManager()
        self.graph_renderer = None  # Will be initialized after signal_processor
        
        # Initialize managers and components
        self._initialize_managers()
        
        # Setup UI architecture
        self._setup_ui()
        
        # Connect signals between components
        self._setup_connections()
        
        # Apply initial theme
        self._apply_theme()
        
        logger.debug("TimeGraphWidget initialized successfully")
    
    def _initialize_managers(self):
        """Initialize all manager components."""
        # Note: PlotManager is no longer a central manager.
        # Each GraphContainer will have its own.
        self.data_manager = TimeSeriesDataManager()
        self.signal_processor = SignalProcessor()
        
        # Initialize graph renderer after signal processor
        self.graph_renderer = GraphRenderer(self.signal_processor, {}, self)
        
        self.toolbar_manager = ToolbarManager(self)
        self.legend_manager = LegendManager(self)
        self.settings_panel_manager = SettingsPanelManager(self)
        self.statistics_settings_panel_manager = StatisticsSettingsPanelManager(self)
        self.graph_settings_panel_manager = GraphSettingsPanelManager(self)
        self.theme_manager = ThemeManager()
        self.bitmask_panel_manager = BitmaskPanelManager(self.data_manager, self.theme_manager, self)
        
        self.cursor_manager = None
        self.statistics_panel = StatisticsPanel()
        self.channel_stats_widgets = {} # Initialize here to prevent race condition
        
        self.is_normalized = False
        self.current_cursor_position = None
        self.selected_range = None
        self.current_cursor_mode = "dual"  # Default cursor mode
        self._last_graph_count = 1
        
        # State for dynamic statistics panel
        self.visible_stats_columns = self.statistics_settings_panel_manager.get_visible_columns()

        # Signal mapping now needs to be aware of tabs
        self.graph_signal_mapping = {} # This will become a dict of dicts: {tab_index: {graph_index: [signals]}}
        
        # Per-graph settings storage
        self.graph_settings = {}  # {tab_index: {graph_index: {setting_name: value}}}

    def _setup_ui(self):
        """Setup the main UI layout with a QTabWidget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toolbar_manager.get_toolbar())
        
        self.content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.content_splitter)
        
        # --- Left Panel Management using QStackedWidget ---
        self.left_panel_stack = QStackedWidget()
        self.left_panel_stack.setMinimumWidth(280)
        self.left_panel_stack.setMaximumWidth(350)
        
        self.settings_panel = self.settings_panel_manager.get_settings_panel()
        self.statistics_settings_panel = self.statistics_settings_panel_manager.get_settings_panel()
        self.graph_settings_panel = self.graph_settings_panel_manager.get_settings_panel()
        
        # Create new analysis panels
        self.correlations_panel = self._create_correlations_panel()
        self.bitmask_panel = self._create_bitmask_panel()
        
        self.left_panel_stack.addWidget(self.settings_panel)
        self.left_panel_stack.addWidget(self.statistics_settings_panel)
        self.left_panel_stack.addWidget(self.graph_settings_panel)
        self.left_panel_stack.addWidget(self.correlations_panel)
        self.left_panel_stack.addWidget(self.bitmask_panel)
        
        self.left_panel_stack.setVisible(False) # Hide the stack initially
        self.content_splitter.addWidget(self.left_panel_stack)
        # --- End of Left Panel Management ---

        # Create all UI elements first before connecting signals that might use them
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._remove_tab_at_index)

        # Add a '+' button to the tab bar for adding new tabs
        self.add_tab_button = QToolButton(self)
        self.add_tab_button.setText("+")
        self.add_tab_button.setCursor(Qt.PointingHandCursor)
        self.add_tab_button.clicked.connect(self._add_tab)
        self.tab_widget.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)
        
        # Apply modern styling
        self._apply_tab_stylesheet()

        self.content_splitter.addWidget(self.tab_widget)
        
        self.channel_stats_panel = self._create_channel_statistics_panel()
        self.content_splitter.addWidget(self.channel_stats_panel)
        
        self.content_splitter.setSizes([280, 660, 300])
        self.content_splitter.setCollapsible(0, True)
        self.content_splitter.setCollapsible(1, False)
        self.content_splitter.setCollapsible(2, False)

        # Now that UI elements exist, connect the tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Add the first tab. This will trigger _on_tab_changed, which requires
        # ati_stats_panel and its layout to exist.
        self._add_tab()
        
        # Initialize cursor manager after UI is fully set up
        QTimer.singleShot(200, self._delayed_initial_setup)
        
    def _create_channel_statistics_panel(self):
        """Creates the main container widget for the statistics panel."""
        # Use our modern StatisticsPanel class
        self.statistics_panel = StatisticsPanel(self)
        self.statistics_panel.setMinimumWidth(300)
        
        # Connect graph settings signal
        self.statistics_panel.graph_settings_requested.connect(self._on_graph_settings_requested)
        self.statistics_panel.signal_color_changed.connect(self._on_signal_color_changed)
        
        # Connect theme change signal
        self.theme_manager.theme_changed.connect(lambda: self.statistics_panel.update_theme(self.theme_manager.get_theme_colors()))
        
        return self.statistics_panel

    def _create_correlations_panel(self):
        """Create the correlations analysis panel using the dedicated manager."""
        from correlations_panel_manager import CorrelationsPanelManager
        self.correlations_panel_manager = CorrelationsPanelManager(self)
        return self.correlations_panel_manager.get_panel()

    def _create_bitmask_panel(self):
        """Create the bitmask analysis panel."""
        return self.bitmask_panel_manager.get_widget()

    def _delayed_initial_setup(self):
        """Delayed setup after UI is fully initialized."""
        logger.debug("Starting delayed initial setup")
        
        # Initialize cursor manager for the first time
        self._initialize_cursor_manager()
        
        # Ensure cursor mode matches toolbar default
        self._force_cursor_mode_sync()

        # Manually trigger the cursor mode change logic to update all panels on startup
        initial_mode = "dual"  # Default mode
        if self.toolbar_manager and hasattr(self.toolbar_manager, 'cursor_combo'):
            toolbar_text = self.toolbar_manager.cursor_combo.currentText().lower()
            if "none" in toolbar_text:
                initial_mode = "none"
        
        # This call ensures that the statistics panel and other components
        # are correctly configured with the initial cursor mode.
        self._on_cursor_mode_changed(initial_mode)
        
        logger.debug("Delayed initial setup completed")

    def _on_graph_count_changed(self, count: int):
        """Delegates graph count change to the active tab's container."""
        active_container = self.get_active_graph_container()
        if active_container:
            active_container.set_graph_count(count)
            # Use delayed initialization to ensure plots are fully ready
            QTimer.singleShot(100, self._delayed_post_graph_change)
            # Rebuild the graph settings panel immediately
            self.graph_settings_panel_manager.rebuild_controls(count)
    
    def _delayed_post_graph_change(self):
        """Delayed initialization after graph count change to ensure plots are ready."""
        active_container = self.get_active_graph_container()
        if not active_container:
            return
        count = active_container.plot_manager.get_subplot_count()
        
        # Store current cursor mode before reinitializing
        current_mode = getattr(self, 'current_cursor_mode', 'dual')
        
        # Re-initialize cursors after plots are fully ready
        self._initialize_cursor_manager()
        
        # Ensure cursor mode is preserved and applied
        if self.cursor_manager and current_mode:
            self.cursor_manager.set_mode(current_mode)
            logger.info(f"Restored cursor mode to '{current_mode}' after graph count change")
        
        # Force cursor mode to match toolbar selection
        self._force_cursor_mode_sync()
        
        # Apply saved graph settings after graph count change
        self._apply_saved_graph_settings()
        
        # Rebuild the bitmask panel
        self.bitmask_panel_manager.update_graph_sections(count)
        
        # Recreate the stats panel to match the new number of graphs
        self._recreate_statistics_panel()
        # Update statistics with current data
        self._update_statistics()

    def _apply_tab_stylesheet(self):
        """Apply a modern stylesheet to the tab widget."""
        colors = self.theme_manager.get_theme_colors()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border-top: 2px solid {colors.get('primary', '#4a90e2')};
                background: {colors.get('surface', '#2d2d2d')};
            }}
            QTabBar::tab {{
                background: {colors.get('surface_variant', '#3c3c3c')};
                color: {colors.get('text_secondary', '#e0e0e0')};
                border: 1px solid {colors.get('surface', '#2d2d2d')};
                border-bottom-color: {colors.get('primary', '#4a90e2')}; 
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 100px;
                padding: 8px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: {colors.get('surface', '#2d2d2d')};
                color: {colors.get('text_primary', '#ffffff')};
                font-weight: bold;
            }}
            QTabBar::close-button {{
                image: url(icons/x.svg); /* Make sure you have a close icon */
                subcontrol-position: right;
                subcontrol-origin: padding;
                border: none;
                background: transparent;
                padding: 4px;
            }}
            QTabBar::close-button:hover {{
                background-color: #e81123;
            }}
            QTabBar::close-button:pressed {{
                background-color: #f1707a;
            }}
            QToolButton {{
                background-color: {colors.get('surface_variant', '#3c3c3c')};
                color: {colors.get('text_primary', '#ffffff')};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {colors.get('surface', '#2d2d2d')};
            }}
            QToolButton:hover {{
                background-color: {colors.get('primary', '#4a90e2')};
            }}
        """)

    def _on_tab_count_changed(self, count: int):
        """Handle tab count changes from toolbar."""
        # This method is now deprecated and should not be used.
        pass

    def _on_tab_changed(self, index: int):
        """Handle tab switching."""
        #logger.debug(f"Switched to tab {index}")
        # Update graph count on toolbar to reflect the new active tab
        active_container = self.get_active_graph_container()
        if active_container:
            graph_count = active_container.plot_manager.get_subplot_count()
            self.toolbar_manager.set_graph_count(graph_count)
            # Rebuild graph settings panel when tab changes
            self.graph_settings_panel_manager.rebuild_controls(graph_count)

        # Use delayed initialization for tab changes too
        QTimer.singleShot(50, self._delayed_post_tab_change)
    
    def _delayed_post_tab_change(self):
        """Delayed initialization after tab change to ensure plots are ready."""
        # Store current cursor mode before reinitializing
        current_mode = getattr(self, 'current_cursor_mode', 'dual')
        
        # Cursors are initialized when tabs change to handle different plot widgets
        self._initialize_cursor_manager()
        
        # Ensure cursor mode is preserved and applied
        if self.cursor_manager and current_mode:
            self.cursor_manager.set_mode(current_mode)
            logger.info(f"Restored cursor mode to '{current_mode}' after tab change")
        
        # Force cursor mode to match toolbar selection
        self._force_cursor_mode_sync()
        
        # Apply saved graph settings for the new tab
        self._apply_saved_graph_settings()
        
        # Update statistics for the new tab
        self._recreate_statistics_panel()

    def _initialize_cursor_manager(self):
        """Initialize or re-initialize cursor manager for the active tab."""
        active_container = self.get_active_graph_container()
        if not active_container:
            if self.cursor_manager:
                self.cursor_manager.deleteLater()
                self.cursor_manager = None
            return

        plot_widgets = active_container.get_plot_widgets()
        
        # Check if plot widgets are properly initialized
        if not plot_widgets:
            logger.warning("No plot widgets available for cursor initialization")
            return
            
        # For initial setup, don't require all widgets to be visible yet
        # Just check if they exist and have valid view boxes
        try:
            for widget in plot_widgets:
                if not hasattr(widget, 'getViewBox') or widget.getViewBox() is None:
                    logger.warning("Plot widget doesn't have valid ViewBox")
                    return
        except Exception as e:
            logger.warning(f"Plot widgets not ready for cursor initialization: {e}")
            return
        
        # This check was causing the initial load bug. Cursors must be re-initialized
        # even if the plot widgets are the same, because their view range might have changed.
        # if self.cursor_manager and self.cursor_manager.plots == plot_widgets:
        #     return

        if self.cursor_manager:
            try:
                self.cursor_manager.cursor_moved.disconnect()
                self.cursor_manager.range_changed.disconnect()
            except TypeError: pass
            self.cursor_manager.deleteLater()
            self.cursor_manager = None
        
        if plot_widgets:
            # Force an update of the view range before creating cursors.
            # This is critical to prevent a race condition where cursors are
            # created before the plot's autorange has been calculated.
            for pw in plot_widgets:
                pw.autoRange()

            self.cursor_manager = CursorManager(plot_widgets)
            self.cursor_manager.cursor_moved.connect(self._on_cursor_moved)
            self.cursor_manager.range_changed.connect(self._on_range_changed)
            
            # Connect bitmask panel to cursor movement
            self.cursor_manager.cursor_moved.connect(self.bitmask_panel_manager.on_cursor_position_changed)
            
            # Use stored mode if available, otherwise sync with toolbar
            if hasattr(self, 'current_cursor_mode') and self.current_cursor_mode:
                self.cursor_manager.set_mode(self.current_cursor_mode)
                logger.debug(f"Applied stored cursor mode: {self.current_cursor_mode}")
            else:
                # Fallback to toolbar selection
                toolbar_mode = self.toolbar_manager.cursor_combo.currentText().lower()
                if "dual" in toolbar_mode:
                    toolbar_mode = "dual"
                elif "none" in toolbar_mode:
                    toolbar_mode = "none"
                else:
                    toolbar_mode = "dual"  # Default to dual
                
                self.cursor_manager.set_mode(toolbar_mode)
                self.current_cursor_mode = toolbar_mode
                logger.debug(f"Applied toolbar cursor mode: {toolbar_mode}")
            
            #logger.debug(f"Cursor manager re-initialized for tab {self.tab_widget.currentIndex()} with mode: {toolbar_mode}")

    def _force_cursor_mode_sync(self):
        """Force cursor mode to match toolbar selection, ensuring consistency."""
        if not self.cursor_manager:
            return
            
        # Get current mode from toolbar and parse it properly
        toolbar_text = self.toolbar_manager.cursor_combo.currentText().lower()
        if "dual" in toolbar_text:
            toolbar_mode = "dual"
        elif "none" in toolbar_text:
            toolbar_mode = "none"
        else:
            toolbar_mode = "dual"  # Default to dual
        
        # Only sync if there's a mismatch or if cursor manager doesn't have the right mode
        current_manager_mode = getattr(self.cursor_manager, 'current_mode', None)
        if current_manager_mode != toolbar_mode:
            # Ensure cursor manager matches toolbar selection
            if hasattr(self.cursor_manager, 'set_mode'):
                self.cursor_manager.set_mode(toolbar_mode)
                self.current_cursor_mode = toolbar_mode
                logger.debug(f"Synced cursor mode to toolbar selection: {toolbar_mode}")
        else:
            logger.debug(f"Cursor mode already in sync: {toolbar_mode}")

    def _initialize_signal_mapping(self, signal_names: list[str]):
        """
        Initializes or updates the signal-to-graph mapping for the new tabbed structure.
        By default, it distributes signals across the graphs of the first tab.
        """
        self.graph_signal_mapping = {}
        for i in range(self.tab_widget.count()):
            self.graph_signal_mapping[i] = {}

        if not signal_names:
            return

        # Default: Distribute signals across graphs in the first tab
        first_tab_container = self.graph_containers[0]
        num_graphs_in_first_tab = first_tab_container.plot_manager.get_subplot_count()
        if num_graphs_in_first_tab == 0:
            return

        for i, signal_name in enumerate(signal_names):
            target_graph_index = i % num_graphs_in_first_tab
            if target_graph_index not in self.graph_signal_mapping[0]:
                self.graph_signal_mapping[0][target_graph_index] = []
            self.graph_signal_mapping[0][target_graph_index].append(signal_name)
        
        logger.debug("Signal mapping initialized for the first tab.")
            
    def _redraw_all_signals(self):
        """Redraws all signals across all tabs based on the current mapping."""
        all_signals = self.signal_processor.get_all_signals()
        all_signal_names = sorted(list(all_signals.keys()))

        # Store current cursor mode before redrawing
        current_mode = getattr(self, 'current_cursor_mode', 'dual')
        cursor_positions = {}
        
        # Save cursor positions if they exist
        if self.cursor_manager and hasattr(self.cursor_manager, 'get_cursor_positions'):
            cursor_positions = self.cursor_manager.get_cursor_positions()
            logger.debug(f"Saved cursor positions: {cursor_positions}")

        self.legend_manager.clear_all_items()

        for tab_index, container in enumerate(self.graph_containers):
            container.plot_manager.clear_all_signals()
            
            tab_mapping = self.graph_signal_mapping.get(tab_index, {})
            for graph_index, signal_names in tab_mapping.items():
                if graph_index < container.plot_manager.get_subplot_count():
                    for name in signal_names:
                        if name in all_signals:
                            signal_data = all_signals[name]
                            signal_index = all_signal_names.index(name)
                            color = self.theme_manager.get_signal_color(signal_index)
                            
                            container.plot_manager.add_signal(
                                name, 
                                signal_data['x_data'], 
                                signal_data['y_data'], 
                                plot_index=graph_index, 
                                pen=color
                            )
                            
                            # Add to legend only once
                            if not self.legend_manager.has_item(name):
                                last_value = float(signal_data['y_data'][-1]) if signal_data['y_data'].size > 0 else 0.0
                            self.legend_manager.add_legend_item(name, color, last_value)
        
        # Restore cursors after redrawing signals
        if current_mode and current_mode != "none":
            # Use a timer to ensure plots are fully ready before restoring cursors
            QTimer.singleShot(50, lambda: self._restore_cursors_after_redraw(current_mode, cursor_positions))
        
        # Apply saved graph settings after redrawing signals
        self._apply_saved_graph_settings()
        
        # Apply limit lines after redrawing signals
        self._apply_limit_lines_to_all_graphs()
        
        # Update statistics panel after redrawing signals
        self._recreate_statistics_panel()
        self._update_statistics()
        
        # Update correlations panel with new parameters
        if hasattr(self, 'correlations_panel_manager') and self.correlations_panel_manager:
            self.correlations_panel_manager.update_available_parameters(all_signal_names)
            self.correlations_panel_manager.on_data_changed()
        
        # Reapply active filters if any exist
        if self.filter_manager.has_active_filters():
            logger.info(f"[FILTER DEBUG] Reapplying filters after redraw")
            # Use a timer to ensure plots are fully ready before reapplying filters
            QTimer.singleShot(100, self._reapply_active_filters)
        
        logger.debug("Redrew all signals across all tabs.")
    
    def _apply_limit_lines_to_all_graphs(self):
        """Apply limit lines to all graphs based on saved settings."""
        try:
            active_tab_index = self.tab_widget.currentIndex()
            if active_tab_index < 0 or active_tab_index >= len(self.graph_containers):
                return
                
            container = self.graph_containers[active_tab_index]
            plot_widgets = container.plot_manager.get_plot_widgets()
            
            for graph_index, plot_widget in enumerate(plot_widgets):
                # Get saved limit settings for this graph
                limits_settings = self._get_graph_setting(graph_index, 'limits', {})
                
                if limits_settings and self.graph_renderer:
                    # Get visible signals for this graph
                    visible_signals = self.graph_signal_mapping.get(active_tab_index, {}).get(graph_index, [])
                    
                    # Apply limit lines
                    self.graph_renderer._apply_limit_lines(plot_widget, graph_index, visible_signals)
                    logger.debug(f"Applied limit lines to graph {graph_index} with {len(limits_settings)} limit configs")
                    
        except Exception as e:
            logger.error(f"Error applying limit lines to all graphs: {e}")

    def _reapply_active_filters(self):
        """Reapply active filters after signal redraw."""
        try:
            active_filters = self.filter_manager.get_active_filters()
            logger.info(f"[FILTER DEBUG] Reapplying {len(active_filters)} active filters")
            for tab_index, filter_data in active_filters.items():
                if tab_index < len(self.graph_containers):
                    logger.info(f"[FILTER DEBUG] Reapplying filter for tab {tab_index}: {filter_data}")
                    self._apply_range_filter(filter_data)
                else:
                    logger.warning(f"[FILTER DEBUG] Tab {tab_index} no longer exists, removing filter")
                    self.filter_manager.remove_filter(tab_index)
        except Exception as e:
            logger.error(f"[FILTER DEBUG] Error reapplying filters: {e}")

    def clear_active_filters(self):
        """Clear all active filters and redraw signals using filter manager."""
        logger.info(f"[FILTER DEBUG] Clearing all active filters")
        self.filter_manager.clear_filters()
        self._redraw_all_signals()

    def _restore_cursors_after_redraw(self, cursor_mode: str, saved_positions: dict):
        """Restore cursors after signal redraw operation."""
        try:
            logger.info(f"Restoring cursors after redraw: mode={cursor_mode}, positions={saved_positions}")
            
            # Reinitialize cursor manager to ensure it's working with current plot widgets
            self._initialize_cursor_manager()
            
            if self.cursor_manager and cursor_mode != "none":
                # Set the cursor mode
                self.cursor_manager.set_mode(cursor_mode)
                
                # If we have saved positions, try to restore them
                if saved_positions and cursor_mode == "dual":
                    # Give cursors a moment to be created, then restore positions
                    QTimer.singleShot(100, lambda: self._restore_cursor_positions(saved_positions))
                
                logger.info(f"Successfully restored cursors with mode: {cursor_mode}")
            
        except Exception as e:
            logger.error(f"Failed to restore cursors after redraw: {e}")
            import traceback
            traceback.print_exc()

    def _restore_cursor_positions(self, positions: dict):
        """Restore specific cursor positions."""
        try:
            if not self.cursor_manager or not positions:
                return
                
            # Restore cursor positions if available
            if 'cursor1' in positions and hasattr(self.cursor_manager, 'set_cursor_position'):
                self.cursor_manager.set_cursor_position("dual_1", positions['cursor1'])
                
            if 'cursor2' in positions and hasattr(self.cursor_manager, 'set_cursor_position'):
                self.cursor_manager.set_cursor_position("dual_2", positions['cursor2'])
                
            logger.debug(f"Restored cursor positions: {positions}")
            
        except Exception as e:
            logger.warning(f"Could not restore cursor positions: {e}")

    def update_data(self, df, time_column: Optional[str] = None):
        """Main entry point to update the widget with new data."""
        if df is None or df.length() == 0:
            logger.warning("Update_data called with empty or None DataFrame.")
            return

        #logger.debug(f"Received new data with {df.length()} rows and columns: {df.get_column_names()}")
        
        self.data_manager.set_data(df, time_column=time_column)
        all_signals = self.signal_processor.process_data(df, self.is_normalized, time_column=time_column)
        
        self._initialize_signal_mapping(list(all_signals.keys()))
        self._redraw_all_signals()
        # Initialize cursors AFTER data is loaded and plots are drawn
        self._initialize_cursor_manager()
        self._recreate_statistics_panel()
        # Also initialize the graph settings panel for the first time
        if self.get_active_graph_container():
            count = self.get_active_graph_container().plot_manager.get_subplot_count()
            self.graph_settings_panel_manager.rebuild_controls(count)
            self.bitmask_panel_manager.update_graph_sections(count)

    def _on_graph_settings_requested(self, graph_index: int):
        """Open the advanced graph settings dialog for comprehensive configuration."""
        active_tab_index = self.tab_widget.currentIndex()
        if active_tab_index < 0:
            return

        logger.debug(f"Advanced settings requested for graph {graph_index} in tab {active_tab_index}")
        
        # Debug signal processor access
        logger.debug(f"Signal processor: {self.signal_processor}")
        logger.debug(f"Signal processor type: {type(self.signal_processor)}")
        
        all_signals_data = self.signal_processor.get_all_signals()
        logger.debug(f"All signals data: {all_signals_data}")
        logger.debug(f"All signals data type: {type(all_signals_data)}")
        logger.debug(f"All signals count: {len(all_signals_data) if all_signals_data else 0}")
        
        all_signals = list(all_signals_data.keys()) if all_signals_data else []
        logger.debug(f"All signals keys: {all_signals}")
        
        # Get signals currently visible in the specific graph of the active tab
        visible_signals = self.graph_signal_mapping.get(active_tab_index, {}).get(graph_index, [])
        
        # Get saved filter data for this graph if available
        saved_filter_data = None
        if hasattr(self, 'filter_manager') and self.filter_manager:
            active_filters = self.filter_manager.get_active_filters()
            saved_filter_data = active_filters.get(active_tab_index, None)
            logger.debug(f"Retrieved saved filter data for tab {active_tab_index}: {saved_filter_data}")
        
        # Get saved limits data for this graph if available
        saved_limits_data = self._get_graph_setting(graph_index, 'limits', {})
        logger.debug(f"Retrieved saved limits data for graph {graph_index}: {saved_limits_data}")
        
        # Get saved basic deviation data for this graph if available
        saved_basic_deviation_data = self._get_graph_setting(graph_index, 'basic_deviation', {})
        logger.debug(f"Retrieved saved basic deviation data for graph {graph_index}: {saved_basic_deviation_data}")
        
        # Use the new advanced settings dialog - parent=None for taskbar visibility
        dialog = GraphAdvancedSettingsDialog(graph_index, all_signals, visible_signals, 
                                           saved_filter_data, saved_limits_data, 
                                           saved_basic_deviation_data, None)
        
        # Set proper window icon and title for taskbar
        dialog.setWindowIcon(self.windowIcon() if self.windowIcon() else QIcon())
        
        # Center dialog on parent window
        if self.parent():
            parent_geometry = self.parent().geometry()
            dialog.move(
                parent_geometry.center().x() - dialog.width() // 2,
                parent_geometry.center().y() - dialog.height() // 2
            )
        
        # Connect filter signal
        dialog.range_filter_applied.connect(self._apply_range_filter)
        # Connect basic deviation signal
        dialog.basic_deviation_applied.connect(self._on_basic_deviation_applied)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_signals = dialog.get_selected_signals()
            
            # Ensure the mapping for the tab exists
            if active_tab_index not in self.graph_signal_mapping:
                self.graph_signal_mapping[active_tab_index] = {}
                
            self.graph_signal_mapping[active_tab_index][graph_index] = selected_signals
            logger.info(f"Updated signals for Tab {active_tab_index}, Graph {graph_index}: {selected_signals}")
            
            # Get all advanced settings
            all_settings = dialog.get_all_settings()
            logger.debug(f"Advanced settings applied: {all_settings}")
            
            # graph redraw
            self._redraw_all_signals()

            # Apply limit settings to graph renderer
            limits_settings = all_settings.get('limits', {})
            if limits_settings and self.graph_renderer:
                self.graph_renderer.set_limits_configuration(limits_settings)
                logger.info(f"Applied limit settings: {len(limits_settings)} signals with limits")

            # Apply basic deviation settings
            deviation_settings = all_settings.get('deviation', {})
            basic_deviation_settings = deviation_settings.get('basic', {})
            if basic_deviation_settings:
                logger.info(f"Applying basic deviation settings from dialog: {basic_deviation_settings}")
                self._on_basic_deviation_applied(graph_index, basic_deviation_settings)
                # Save basic deviation settings
                self._save_graph_setting(graph_index, 'basic_deviation', basic_deviation_settings)

            # Save graph settings including limits
            self._save_graph_setting(graph_index, 'limits', limits_settings)
            
    def _on_basic_deviation_applied(self, graph_index: int, deviation_settings: Dict[str, Any]):
        """Handle basic deviation settings application."""
        active_tab_index = self.tab_widget.currentIndex()
        logger.info(f"Applying basic deviation settings to graph {graph_index} on tab {active_tab_index}: {deviation_settings}")

        try:
            # Apply deviation settings to graph renderer
            if hasattr(self, 'graph_renderer') and self.graph_renderer:
                self.graph_renderer.set_basic_deviation_settings(active_tab_index, graph_index, deviation_settings)
                logger.info(f"Basic deviation settings applied successfully to graph {graph_index}")
            else:
                logger.warning("Graph renderer not available for basic deviation application")

        except Exception as e:
            logger.error(f"Error applying basic deviation settings to graph {graph_index}: {e}", exc_info=True)

    def _on_plot_clicked(self, plot_index: int, x: float, y: float):
        """Handle plot clicks."""
        self.current_cursor_position = x
        self._update_legend_values()
        self.cursor_moved.emit("click", (x, y))
    
    def _on_range_selected(self, start: float, end: float):
        """Handle range selection."""
        self.selected_range = (start, end)
        self._update_statistics_for_range(start, end)
        self.range_selected.emit((start, end))
    
    def _on_signal_visibility_changed(self, signal_name: str, visible: bool):
        """Handle signal visibility changes."""
        pass  # Implementation depends on requirements
    
    def _on_signal_selected(self, signal_name: str):
        """Handle signal selection."""
        pass
    
    def _on_processing_started(self):
        """Handle processing start."""
        pass
    
    def _on_processing_finished(self):
        """Handle processing completion."""
        self._update_statistics()
        
    def _on_statistics_updated(self, stats: dict):
        """Handle statistics updates."""
        self.statistics_updated.emit(stats)
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes broadcast from the theme manager."""
        self._apply_theme()
    
    def _on_cursor_mode_changed(self, mode: str):
        """Handle cursor mode changes."""
        logger.info(f"Cursor mode change requested: {mode}")
        
        # Update stored mode immediately
        self.current_cursor_mode = mode
        
        # Ensure cursor manager is properly initialized before applying mode
        if not self.cursor_manager:
            logger.info("Cursor manager not initialized, initializing now...")
            self._initialize_cursor_manager()
        
        # Apply to cursor manager if it exists
        if self.cursor_manager and hasattr(self.cursor_manager, 'set_mode'):
            try:
                self.cursor_manager.set_mode(mode)
                logger.info(f"Successfully applied cursor mode: {mode}")
            except Exception as e:
                logger.error(f"Failed to set cursor mode: {e}")
                # Try to reinitialize cursor manager
                self._initialize_cursor_manager()
                if self.cursor_manager:
                    self.cursor_manager.set_mode(mode)
        else:
            logger.warning("Cursor manager not available for mode change, reinitializing...")
            self._initialize_cursor_manager()
            if self.cursor_manager:
                self.cursor_manager.set_mode(mode)
            
        # Update statistics panel with new cursor mode
        if hasattr(self, 'statistics_panel') and self.statistics_panel:
            self.statistics_panel.set_cursor_mode(mode)
            
        # Update statistics settings panel with new cursor mode
        if hasattr(self, 'statistics_settings_panel_manager') and self.statistics_settings_panel_manager:
            self.statistics_settings_panel_manager.set_cursor_mode(mode)
            
        # Redraw panel for new columns
        self._recreate_statistics_panel()
    
    def _on_panel_toggled(self):
        """Handle statistics panel visibility toggle."""
        if hasattr(self, 'channel_stats_panel'):
            self.channel_stats_panel.setVisible(not self.channel_stats_panel.isVisible())
    
    def _on_settings_toggled(self):
        """Handle settings panel visibility toggle."""
        self._toggle_left_panel(self.settings_panel)
        #logger.info(f"Settings panel visibility: {self.left_panel_stack.isVisible() and self.left_panel_stack.currentWidget() == self.settings_panel}")

    def _on_graph_settings_toggled(self):
        """Handle graph settings panel visibility toggle."""
        self._toggle_left_panel(self.graph_settings_panel)
        #logger.info(f"Graph settings panel visibility: {self.left_panel_stack.isVisible() and self.left_panel_stack.currentWidget() == self.graph_settings_panel}")

    def _on_statistics_settings_toggled(self):
        """Handle statistics settings panel visibility toggle."""
        self._toggle_left_panel(self.statistics_settings_panel)
            
        #logger.info(f"Statistics settings panel visibility: {self.left_panel_stack.isVisible() and self.left_panel_stack.currentWidget() == self.statistics_settings_panel}")
    
    def _on_correlations_toggled(self):
        """Handle correlations panel visibility toggle."""
        self._toggle_left_panel(self.correlations_panel)
        
    def _on_bitmask_toggled(self):
        """Handle bitmask panel visibility toggle."""
        self._toggle_left_panel(self.bitmask_panel)

    def _toggle_left_panel(self, panel_to_show):
        """Generic function to toggle visibility of a panel in the left stack."""
        if self.left_panel_stack.currentWidget() == panel_to_show and self.left_panel_stack.isVisible():
            self.left_panel_stack.setVisible(False)
        else:
            self.left_panel_stack.setCurrentWidget(panel_to_show)
            self.left_panel_stack.setVisible(True)

    def _on_per_graph_normalization_toggled(self, graph_index: int, normalize: bool):
        """Handle normalization for a specific graph."""
        active_tab_index = self.tab_widget.currentIndex()
        if active_tab_index < 0:
            return

        signals_in_graph = self.graph_signal_mapping.get(active_tab_index, {}).get(graph_index, [])
        
        if not signals_in_graph:
            return

        if normalize:
            self.signal_processor.apply_normalization(signal_names=signals_in_graph)
        else:
            self.signal_processor.remove_normalization(signal_names=signals_in_graph)
        
        # Save normalization setting for this graph
        self._save_graph_setting(graph_index, 'normalize', normalize)
        
        # Redraw all signals to reflect the change
        self._redraw_all_signals()
        logger.info(f"Normalization toggled to {normalize} for signals in graph {graph_index}: {signals_in_graph}")

    def _on_per_graph_view_reset(self, graph_index: int):
        """Handle view reset for a specific graph."""
        active_container = self.get_active_graph_container()
        if active_container:
            plot_widgets = active_container.get_plot_widgets()
            if 0 <= graph_index < len(plot_widgets):
                plot_widgets[graph_index].autoRange()
                #logger.info(f"View reset for graph {graph_index}")

    def _on_per_graph_grid_changed(self, graph_index: int, show_grid: bool):
        """Handle grid visibility for a specific graph."""
        active_container = self.get_active_graph_container()
        if active_container:
            plot_widgets = active_container.get_plot_widgets()
            if 0 <= graph_index < len(plot_widgets):
                plot_widgets[graph_index].showGrid(x=show_grid, y=show_grid)
                
                # Save grid setting for this graph
                self._save_graph_setting(graph_index, 'show_grid', show_grid)
                
                logger.info(f"Grid visibility for graph {graph_index} set to {show_grid}")

    def _on_per_graph_autoscale_changed(self, graph_index: int, autoscale: bool):
        """Handle Y-axis autoscale for a specific graph."""
        active_container = self.get_active_graph_container()
        if active_container:
            plot_widgets = active_container.get_plot_widgets()
            if 0 <= graph_index < len(plot_widgets):
                plot_widgets[graph_index].enableAutoRange(axis='y', enable=autoscale)
                
                # Save autoscale setting for this graph
                self._save_graph_setting(graph_index, 'autoscale', autoscale)
                
                logger.info(f"Autoscale for graph {graph_index} set to {autoscale}")

    def _add_tab(self):
        """Adds a new tab with a GraphContainer."""
        tab_index = self.tab_widget.count()
        container = GraphContainer(self.theme_manager)
        
        # Connect the settings button signal from the new container's plot manager
        container.plot_manager.settings_requested.connect(self._on_graph_settings_requested)
        
        self.graph_containers.append(container)
        self.tab_widget.addTab(container, f"Tab {self.tab_widget.count() + 1}")
        # Apply the current theme to the new container's plots
        container.apply_theme()

    def _remove_tab(self):
        """Removes the last tab."""
        # This is now deprecated in favor of _remove_tab_at_index
        if self.tab_widget.count() > 1:
            index_to_remove = self.tab_widget.count() - 1
            self._remove_tab_at_index(index_to_remove)

    def _remove_tab_at_index(self, index: int):
        """Removes the tab at the given index."""
        if self.tab_widget.count() > 1:
            widget_to_remove = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            
            if widget_to_remove in self.graph_containers:
                self.graph_containers.remove(widget_to_remove)
            
            # Clean up the removed widget
            widget_to_remove.deleteLater()

            # Update remaining tab titles
            for i in range(self.tab_widget.count()):
                self.tab_widget.setTabText(i, f"Tab {i + 1}")

    def get_active_graph_container(self) -> Optional['GraphContainer']:
        """Gets the GraphContainer from the currently active tab."""
        if not hasattr(self, 'tab_widget') or not self.tab_widget:
            return None
        current_index = self.tab_widget.currentIndex()
        if 0 <= current_index < len(self.graph_containers):
            return self.graph_containers[current_index]
        return None

    def _on_cursor_moved_old(self, cursor_type: str, position: float):
        """Handle cursor movement events (old signature - deprecated)."""
        self.current_cursor_position = position
        self._update_legend_values()
        self.cursor_moved.emit(cursor_type, position)

    def _on_range_changed(self, start: float, end: float):
        """Handle range changes from cursor manager."""
        self.selected_range = (start, end)
        self._update_statistics_for_range(start, end)
    
    # Data processing methods
    def _apply_normalization(self):
        """Apply normalization to all signals."""
        signal_names = list(self.signal_processor.get_all_signals().keys())
        normalized_data = self.signal_processor.apply_normalization(signal_names)
        
        for signal_name, y_data in normalized_data.items():
            signal_data = self.signal_processor.get_signal_data(signal_name)
            if signal_data and 'x_data' in signal_data:
                self.plot_manager.update_signal_data(signal_name, signal_data['x_data'], y_data, 0)
        
        self._update_legend_values()
    
    def _remove_normalization(self):
        """Remove normalization from all signals."""
        signal_names = list(self.signal_processor.get_all_signals().keys())
        original_data = self.signal_processor.remove_normalization(signal_names)
        
        for signal_name, y_data in original_data.items():
            signal_data = self.signal_processor.get_signal_data(signal_name)
            if signal_data and 'x_data' in signal_data:
                self.plot_manager.update_signal_data(signal_name, signal_data['x_data'], y_data, 0)
        
        self._update_legend_values()

    def _update_statistics(self, cursor_pos=None, selected_range=None):
        """Updates all statistics based on the active tab and cursors."""
        active_container = self.get_active_graph_container()
        tab_index = self.tab_widget.currentIndex()

        if not active_container or tab_index < 0:
            return

        tab_mapping = self.graph_signal_mapping.get(tab_index, {})

        # Get cursor positions if available
        cursor_positions = {}
        if self.cursor_manager and self.current_cursor_mode == 'dual':
            cursor_positions = self.cursor_manager.get_cursor_positions()
            logger.debug(f"Using cursor positions for statistics: {cursor_positions}")

        # Update stats for each signal in the modern statistics panel
        for graph_index, signal_names in tab_mapping.items():
            for signal_name in signal_names:
                # Determine the range for statistics calculation
                stats_range = selected_range
                
                # If cursors are active, use cursor range for statistics
                if cursor_positions and 'c1' in cursor_positions and 'c2' in cursor_positions:
                    c1_pos = cursor_positions['c1']
                    c2_pos = cursor_positions['c2']
                    # Use the range between cursors (min to max)
                    cursor_range = (min(c1_pos, c2_pos), max(c1_pos, c2_pos))
                    stats_range = cursor_range
                    logger.debug(f"Using cursor range for {signal_name}: {cursor_range}")
                
                stats = self.signal_processor.get_statistics(
                    signal_name, 
                    stats_range, 
                    self.duty_cycle_threshold_mode, 
                    self.duty_cycle_threshold_value
                )
                if stats:
                    # Add cursor values to stats if available
                    if cursor_positions:
                        cursor_values = self._get_cursor_values_for_signal(signal_name, cursor_positions)
                        stats.update(cursor_values)
                        
                        # Calculate RMS from start to C1 cursor position if C1 is available
                        if 'c1' in cursor_positions:
                            c1_rms = self._calculate_rms_to_cursor(signal_name, cursor_positions['c1'])
                            if c1_rms is not None:
                                stats['rms'] = c1_rms
                    
                    # Update the modern statistics panel
                    full_signal_name = f"{signal_name} (G{graph_index+1})"
                    self.statistics_panel.update_statistics(full_signal_name, stats)

    def _get_cursor_values_for_signal(self, signal_name: str, cursor_positions: Dict[str, float]) -> Dict[str, float]:
        """Get signal values at cursor positions with improved interpolation."""
        cursor_values = {}
        
        # Get signal data
        signal_data = self.signal_processor.get_signal_data(signal_name)
        if not signal_data:
            logger.debug(f"No signal data found for {signal_name}")
            return cursor_values
            
        x_data = signal_data.get('x_data', [])
        y_data = signal_data.get('y_data', [])
        
        if len(x_data) == 0 or len(y_data) == 0:
            logger.debug(f"Empty data arrays for {signal_name}")
            return cursor_values
            
        # Find values at cursor positions using interpolation
        import numpy as np
        
        for cursor_key, x_pos in cursor_positions.items():
            try:
                # Check if cursor position is within data range
                if x_pos < x_data[0] or x_pos > x_data[-1]:
                    logger.debug(f"Cursor position {x_pos} outside data range for {signal_name}")
                    # Use extrapolation for positions outside range
                    if x_pos < x_data[0]:
                        y_value = y_data[0]
                    else:
                        y_value = y_data[-1]
                else:
                    # Interpolate to find y value at cursor x position
                    y_value = np.interp(x_pos, x_data, y_data)
                
                cursor_values[cursor_key] = float(y_value)
                logger.debug(f"Cursor {cursor_key} at {x_pos:.3f} -> {signal_name} = {y_value:.6f}")
                
            except Exception as e:
                logger.warning(f"Failed to get cursor value for {signal_name} at {cursor_key}: {e}")
                cursor_values[cursor_key] = 0.0
                
        return cursor_values

    def _calculate_rms_to_cursor(self, signal_name: str, cursor_x: float) -> Optional[float]:
        """Calculate RMS from signal start to cursor position."""
        signal_data = self.signal_processor.get_signal_data(signal_name)
        if not signal_data:
            return None
            
        x_data = signal_data.get('x_data', [])
        y_data = signal_data.get('y_data', [])
        
        if len(x_data) == 0 or len(y_data) == 0:
            return None
            
        import numpy as np
        
        try:
            # Find indices where x <= cursor_x
            mask = np.array(x_data) <= cursor_x
            if not np.any(mask):
                return None
                
            # Get y values up to cursor position
            y_subset = np.array(y_data)[mask]
            
            if len(y_subset) == 0:
                return None
                
            # Calculate RMS
            rms_value = np.sqrt(np.mean(y_subset**2))
            return float(rms_value)
            
        except Exception as e:
            logger.warning(f"Failed to calculate RMS to cursor for {signal_name}: {e}")
            return None

    def _on_cursor_moved(self, cursor_positions: Dict[str, float]):
        """Handle cursor movement and update statistics in real-time."""
        logger.debug(f"Cursor moved: {cursor_positions}")
        
        # Store cursor positions for other components
        if cursor_positions:
            # Update current cursor position for legacy compatibility
            if 'c1' in cursor_positions:
                self.current_cursor_position = cursor_positions['c1']
            elif 'cursor1' in cursor_positions:
                self.current_cursor_position = cursor_positions['cursor1']
        
        # Update statistics with new cursor positions immediately
        self._update_statistics()
        
        # Update cursor information in statistics panel
        if hasattr(self, 'statistics_panel') and self.statistics_panel:
            self.statistics_panel.update_cursor_positions(cursor_positions)
        
        # Update legend values
        self._update_legend_values()
        
        # Update correlations panel if it exists
        if hasattr(self, 'correlations_panel_manager') and self.correlations_panel_manager:
            self.correlations_panel_manager.on_cursor_moved(cursor_positions)
        
        # Update bitmask panel if it exists
        if hasattr(self, 'bitmask_panel_manager') and self.bitmask_panel_manager:
            self.bitmask_panel_manager.on_cursor_position_changed(cursor_positions)
        
        # Emit signal for external listeners
        if cursor_positions:
            # Convert to old format for backward compatibility
            if 'c1' in cursor_positions:
                self.cursor_moved.emit("cursor1", cursor_positions['c1'])
            elif 'cursor1' in cursor_positions:
                self.cursor_moved.emit("cursor1", cursor_positions['cursor1'])

    def _update_statistics_for_range(self, start: float, end: float):
        """Update statistics for time range."""
        stats = self.signal_processor.calculate_statistics(time_range=(start, end))
        self.statistics_updated.emit(stats)
        
    def _apply_range_filter(self, filter_data: dict):
        """Apply range filter to the specified graph using modular components."""
        print(f"[SIGNAL DEBUG] _apply_range_filter called with: {filter_data}")
        logger.info(f"[FILTER DEBUG] Starting range filter application")
        logger.info(f"[FILTER DEBUG] Filter data: {filter_data}")
        
        try:
            # Get active tab and container
            active_tab_index = self.tab_widget.currentIndex()
            logger.info(f"[FILTER DEBUG] Active tab index: {active_tab_index}")
            logger.info(f"[FILTER DEBUG] Available containers: {len(self.graph_containers)}")
            
            if active_tab_index < 0 or active_tab_index >= len(self.graph_containers):
                logger.warning("[FILTER DEBUG] No active tab for filter application")
                return
                
            container = self.graph_containers[active_tab_index]
            logger.info(f"[FILTER DEBUG] Container: {container}")
            
            graph_index = filter_data['graph_index']
            conditions = filter_data['conditions']
            mode = filter_data['mode']
            
            logger.info(f"[FILTER DEBUG] Graph index: {graph_index}")
            logger.info(f"[FILTER DEBUG] Conditions: {conditions}")
            logger.info(f"[FILTER DEBUG] Mode: {mode}")
            
            # Get all signals data
            all_signals = self.signal_processor.get_all_signals()
            logger.info(f"[FILTER DEBUG] Available signals: {list(all_signals.keys())}")
            logger.info(f"[FILTER DEBUG] Signal count: {len(all_signals)}")
            
            # Check if this is a reset operation (empty conditions)
            if not conditions:
                logger.info("[FILTER DEBUG] Reset operation detected - clearing all filters")
                
                # Clear filter state
                self.filter_manager.remove_filter(active_tab_index)
                
                # Reset graph to show all data
                if hasattr(self.graph_renderer, 'clear_filters'):
                    self.graph_renderer.clear_filters(container, graph_index)
                else:
                    # Fallback: refresh the graph to show all data
                    self._refresh_graph_display(container)
                
                logger.info("[FILTER DEBUG] Filters cleared successfully")
                return
            
            # Use filter manager to calculate segments
            logger.info(f"[FILTER DEBUG] Calculating filter segments...")
            time_segments = self.filter_manager.calculate_filter_segments(all_signals, conditions)
            logger.info(f"[FILTER DEBUG] Calculated {len(time_segments)} segments")
            
            if not time_segments:
                logger.warning("[FILTER DEBUG] No time segments match the filter conditions")
                from PyQt5.QtWidgets import QMessageBox
                msg = QMessageBox(self)
                msg.setStyleSheet(self._get_message_box_style())
                msg.setIcon(QMessageBox.Warning)
                msg.setText("No time segments match the specified filter conditions.")
                msg.setWindowTitle("No Matches")
                msg.exec_()
                return
                
            logger.info(f"[FILTER DEBUG] Found {len(time_segments)} time segments matching filter conditions")
            
            # Save filter state using filter manager
            self.filter_manager.save_filter_state(active_tab_index, filter_data)
            
            # Update graph renderer with current signal mapping
            self.graph_renderer.graph_signal_mapping = self.graph_signal_mapping
            
            # Apply filtering based on mode using graph renderer
            if mode == 'segmented':
                self.graph_renderer.apply_segmented_filter(container, graph_index, time_segments)
            else:  # concatenated
                self.graph_renderer.apply_concatenated_filter(container, time_segments)
                
        except Exception as e:
            logger.error(f"Error applying range filter: {e}")
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setStyleSheet(self._get_message_box_style())
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Error applying filter: {str(e)}")
            msg.setWindowTitle("Filter Error")
            msg.exec_()
    
    def _refresh_graph_display(self, container):
        """Refresh graph display to show all data (remove filters)."""
        try:
            logger.info("[REFRESH DEBUG] Refreshing graph display to show all data")
            
            # Clear any existing filters on the container
            container.plot_manager.clear_all_signals()
            
            # Get current tab index and redraw signals for this container
            active_tab_index = self.tab_widget.currentIndex()
            if active_tab_index >= 0:
                # Get signal mapping for this tab
                tab_mapping = self.graph_signal_mapping.get(active_tab_index, {})
                all_signals = self.signal_processor.get_all_signals()
                all_signal_names = list(all_signals.keys())
                
                # Redraw all signals for this container
                for graph_index, signal_names in tab_mapping.items():
                    if graph_index < container.plot_manager.get_subplot_count():
                        for name in signal_names:
                            if name in all_signals:
                                signal_data = all_signals[name]
                                signal_index = all_signal_names.index(name)
                                color = self.theme_manager.get_signal_color(signal_index)
                                
                                container.plot_manager.add_signal(
                                    name, 
                                    signal_data['x_data'], 
                                    signal_data['y_data'], 
                                    plot_index=graph_index, 
                                    pen=color
                                )
                
                logger.info("[REFRESH DEBUG] Graph display refreshed successfully")
                
        except Exception as e:
            logger.error(f"Error refreshing graph display: {e}")
    
    def _get_message_box_style(self) -> str:
        """Gets a consistent stylesheet for QMessageBox to match the space theme."""
        return """
            QMessageBox {
                background-color: #2d344a;
                font-size: 14px;
                color: #ffffff !important;
            }
            QMessageBox QLabel {
                color: #ffffff !important;
                padding: 10px;
                font-size: 14px;
                font-weight: normal;
                background: transparent;
            }
            QMessageBox * {
                color: #ffffff !important;
                background: transparent;
            }
            QMessageBox QTextEdit {
                color: #ffffff !important;
                background-color: rgba(74, 144, 226, 0.1);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 4px;
            }
            QMessageBox QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a536b, stop:1 #3a4258);
                color: #ffffff !important;
                border: 1px solid #5a647d;
                padding: 8px 16px;
                border-radius: 5px;
                min-width: 90px;
                font-weight: 600;
            }
            QMessageBox QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a647d, stop:1 #4a536b);
                border: 1px solid #7a849d;
                color: #ffffff !important;
            }
            QMessageBox QPushButton:pressed {
                background-color: #3a4258;
                color: #ffffff !important;
            }
        """
                               
    def _calculate_filter_segments(self, all_signals: dict, conditions: list) -> list:
        """Calculate time segments where all conditions are satisfied."""
        logger.info(f"🔍 [SEGMENT DEBUG] Starting segment calculation")
        logger.info(f"🔍 [SEGMENT DEBUG] Conditions count: {len(conditions)}")
        
        if not conditions:
            logger.warning(f"🔍 [SEGMENT DEBUG] No conditions provided")
            return []
            
        # Get time axis from first signal
        first_signal_name = next(iter(all_signals.keys()))
        first_signal = all_signals[first_signal_name]
        time_data = first_signal.get('x_data', [])
        
        logger.info(f"🔍 [SEGMENT DEBUG] First signal: {first_signal_name}")
        logger.info(f"🔍 [SEGMENT DEBUG] Time data length: {len(time_data)}")
        
        if len(time_data) == 0:
            logger.warning(f"🔍 [SEGMENT DEBUG] Empty time data")
            return []
            
        import numpy as np
        time_array = np.array(time_data)
        logger.info(f"🔍 [SEGMENT DEBUG] Time range: {time_array[0]} to {time_array[-1]}")
        
        # Initialize mask with all True values
        combined_mask = np.ones(len(time_array), dtype=bool)
        
        # Apply each condition (AND logic between conditions)
        for i, condition in enumerate(conditions):
            param_name = condition['parameter']
            ranges = condition['ranges']
            
            logger.info(f"🔍 [SEGMENT DEBUG] Processing condition {i+1}: {param_name}")
            logger.info(f"🔍 [SEGMENT DEBUG] Ranges: {ranges}")
            
            if param_name not in all_signals:
                logger.warning(f"🔍 [SEGMENT DEBUG] Parameter {param_name} not found in signals")
                logger.warning(f"🔍 [SEGMENT DEBUG] Available signals: {list(all_signals.keys())}")
                continue
                
            signal_data = all_signals[param_name]
            y_data = np.array(signal_data.get('y_data', []))
            
            logger.info(f"🔍 [SEGMENT DEBUG] Signal data length: {len(y_data)}")
            logger.info(f"🔍 [SEGMENT DEBUG] Signal value range: {np.min(y_data)} to {np.max(y_data)}")
            
            if len(y_data) != len(time_array):
                logger.warning(f"🔍 [SEGMENT DEBUG] Data length mismatch for {param_name}: {len(y_data)} vs {len(time_array)}")
                continue
                
            # Create mask for this parameter's conditions
            param_mask = np.ones(len(time_array), dtype=bool)
            
            # Apply range conditions (AND logic within parameter)
            for j, range_condition in enumerate(ranges):
                operator = range_condition['operator']
                value = range_condition['value']
                
                logger.info(f"🔍 [SEGMENT DEBUG] Range {j+1}: {operator} {value}")
                
                if operator == '>':
                    range_mask = y_data > value
                elif operator == '>=':
                    range_mask = y_data >= value
                elif operator == '<':
                    range_mask = y_data < value
                elif operator == '<=':
                    range_mask = y_data <= value
                else:
                    logger.warning(f"🔍 [SEGMENT DEBUG] Unknown operator: {operator}")
                    continue
                
                matching_points = np.sum(range_mask)
                logger.info(f"🔍 [SEGMENT DEBUG] Matching points for {operator} {value}: {matching_points}/{len(range_mask)}")
                    
                param_mask = param_mask & range_mask
                
            # Combine with overall mask (AND logic between parameters)
            param_matching = np.sum(param_mask)
            logger.info(f"🔍 [SEGMENT DEBUG] Parameter {param_name} matching points: {param_matching}/{len(param_mask)}")
            combined_mask = combined_mask & param_mask
            
        # Find continuous segments where mask is True
        total_matching = np.sum(combined_mask)
        logger.info(f"🔍 [SEGMENT DEBUG] Total matching points after all conditions: {total_matching}/{len(combined_mask)}")
        
        segments = []
        in_segment = False
        segment_start = None
        
        for i, mask_value in enumerate(combined_mask):
            if mask_value and not in_segment:
                # Start of new segment
                segment_start = time_array[i]
                in_segment = True
                logger.info(f"🔍 [SEGMENT DEBUG] Segment start at time {segment_start}")
            elif not mask_value and in_segment:
                # End of current segment
                segment_end = time_array[i-1]
                segments.append((segment_start, segment_end))
                logger.info(f"🔍 [SEGMENT DEBUG] Segment end at time {segment_end}, duration: {segment_end - segment_start}")
                in_segment = False
                
        # Handle case where segment extends to end of data
        if in_segment:
            segment_end = time_array[-1]
            segments.append((segment_start, segment_end))
            logger.info(f"🔍 [SEGMENT DEBUG] Final segment end at time {segment_end}, duration: {segment_end - segment_start}")
            
        logger.info(f"🔍 [SEGMENT DEBUG] Found {len(segments)} segments: {segments}")
        return segments
        
    def _apply_segmented_filter(self, container, graph_index: int, time_segments: list):
        """Apply segmented display filter - show matching segments with gaps."""
        logger.info(f"[SEGMENTED DEBUG] Starting segmented filter application")
        logger.info(f"[SEGMENTED DEBUG] Graph index: {graph_index}")
        logger.info(f"[SEGMENTED DEBUG] Time segments: {time_segments}")
        
        # Get signals for this graph
        active_tab_index = self.tab_widget.currentIndex()
        visible_signals = self.graph_signal_mapping.get(active_tab_index, {}).get(graph_index, [])
        
        logger.info(f"[SEGMENTED DEBUG] Active tab: {active_tab_index}")
        logger.info(f"[SEGMENTED DEBUG] Visible signals: {visible_signals}")
        logger.info(f"[SEGMENTED DEBUG] Graph signal mapping: {self.graph_signal_mapping}")
        
        if not visible_signals:
            logger.warning(f"[SEGMENTED DEBUG] No visible signals for graph {graph_index}")
            return
            
        # Clear existing plots for this graph
        plot_widgets = container.plot_manager.get_plot_widgets()
        logger.info(f"[SEGMENTED DEBUG] Available plot widgets: {len(plot_widgets)}")
        
        if graph_index < len(plot_widgets):
            plot_widget = plot_widgets[graph_index]
            logger.info(f"[SEGMENTED DEBUG] Clearing plot widget {graph_index}")
            plot_widget.clear()
        else:
            logger.warning(f"[SEGMENTED DEBUG] Graph index {graph_index} out of range, available plots: {len(plot_widgets)}")
            return
            
        # Plot each signal with segmented data
        all_signals = self.signal_processor.get_all_signals()
        
        for signal_name in visible_signals:
            logger.info(f"[SEGMENTED DEBUG] Processing signal: {signal_name}")
            
            if signal_name not in all_signals:
                logger.warning(f"[SEGMENTED DEBUG] Signal {signal_name} not found in all_signals")
                continue
                
            signal_data = all_signals[signal_name]
            full_x_data = np.array(signal_data.get('x_data', []))
            full_y_data = np.array(signal_data.get('y_data', []))
            
            logger.info(f"[SEGMENTED DEBUG] Signal data length: {len(full_x_data)}")
            
            # Create segmented data
            segments_plotted = 0
            for i, (segment_start, segment_end) in enumerate(time_segments):
                # Find indices for this segment
                mask = (full_x_data >= segment_start) & (full_x_data <= segment_end)
                segment_x = full_x_data[mask]
                segment_y = full_y_data[mask]
                
                if len(segment_x) > 0:
                    # Plot this segment
                    color = self._get_signal_color(signal_name)
                    # Only show legend for the first segment of each signal
                    legend_name = signal_name if segments_plotted == 0 else None
                    plot_widget.plot(segment_x, segment_y, pen=color, name=legend_name)
                    segments_plotted += 1
                    
            logger.info(f"[SEGMENTED DEBUG] Signal {signal_name}: plotted {segments_plotted} segments")
                    
        logger.info(f"Segmented filter applied successfully to graph {graph_index}")
        
        # Show success message
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setStyleSheet(self._get_message_box_style())
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Segmented filter applied to Graph {graph_index + 1}.\n\n"
            f"Showing {len(time_segments)} time segments with gaps.\n\n"
            "Time synchronization with other graphs is maintained.")
        msg.setWindowTitle("Filter Applied")
        msg.exec_()
        
    def _apply_concatenated_filter(self, container, graph_index: int, time_segments: list):
        """Apply concatenated display filter - join matching segments continuously."""
        logger.info(f"Applying concatenated filter to graph {graph_index} with {len(time_segments)} segments")
        
        # Get signals for this graph
        active_tab_index = self.tab_widget.currentIndex()
        visible_signals = self.graph_signal_mapping.get(active_tab_index, {}).get(graph_index, [])
        
        if not visible_signals:
            logger.warning(f"No visible signals for graph {graph_index}")
            return
            
        # Clear existing plots for this graph
        plot_widgets = container.plot_manager.get_plot_widgets()
        if graph_index < len(plot_widgets):
            plot_widget = plot_widgets[graph_index]
            plot_widget.clear()
        else:
            logger.warning(f"Graph index {graph_index} out of range, available plots: {len(plot_widgets)}")
            return
            
        # Plot each signal with concatenated data
        all_signals = self.signal_processor.get_all_signals()
        
        for signal_name in visible_signals:
            if signal_name not in all_signals:
                continue
                
            signal_data = all_signals[signal_name]
            full_x_data = np.array(signal_data.get('x_data', []))
            full_y_data = np.array(signal_data.get('y_data', []))
            
            # Concatenate all segments
            concatenated_x = []
            concatenated_y = []
            new_time_offset = 0.0
            
            for i, (segment_start, segment_end) in enumerate(time_segments):
                # Find indices for this segment
                mask = (full_x_data >= segment_start) & (full_x_data <= segment_end)
                segment_x = full_x_data[mask]
                segment_y = full_y_data[mask]
                
                if len(segment_x) > 0:
                    # Adjust time axis for concatenation
                    if i == 0:
                        adjusted_x = segment_x - segment_x[0]  # Start from 0
                    else:
                        adjusted_x = segment_x - segment_x[0] + new_time_offset
                        
                    concatenated_x.extend(adjusted_x)
                    concatenated_y.extend(segment_y)
                    
                    # Update offset for next segment
                    if len(adjusted_x) > 0:
                        new_time_offset = adjusted_x[-1] + (adjusted_x[-1] - adjusted_x[0]) * 0.01  # Small gap
                        
            if concatenated_x:
                # Plot concatenated data
                color = self._get_signal_color(signal_name)
                plot_widget.plot(concatenated_x, concatenated_y, pen=color, name=signal_name)
                
        logger.info(f"Concatenated filter applied successfully to graph {graph_index}")

    def _apply_global_concatenated_filter(self, container, time_segments: list):
        """Apply concatenated display filter globally to all graphs in the tab."""
        logger.info(f"Applying global concatenated filter with {len(time_segments)} segments to all graphs")
        
        # Get all signals from signal processor
        all_signals = self.signal_processor.get_all_signals()
        
        if not all_signals:
            logger.warning("No signals available for global filter")
            return
            
        # Create concatenated time axis and signal data for all signals
        concatenated_signals = self._create_concatenated_signals(all_signals, time_segments)
        
        if not concatenated_signals:
            logger.warning("Failed to create concatenated signals")
            return
            
        # Clear all plots in the container
        plot_widgets = container.plot_manager.get_plot_widgets()
        for plot_widget in plot_widgets:
            plot_widget.clear()
            
        # Get current tab's graph signal mapping
        active_tab_index = self.tab_widget.currentIndex()
        tab_mapping = self.graph_signal_mapping.get(active_tab_index, {})
        
        # Apply concatenated data to all graphs
        for graph_index, signal_names in tab_mapping.items():
            if graph_index < len(plot_widgets):
                plot_widget = plot_widgets[graph_index]
                
                for signal_name in signal_names:
                    if signal_name in concatenated_signals:
                        concat_data = concatenated_signals[signal_name]
                        color = self._get_signal_color(signal_name)
                        plot_widget.plot(
                            concat_data['x_data'], 
                            concat_data['y_data'], 
                            pen=color, 
                            name=signal_name
                        )
        
        # Update signal processor with concatenated data (for statistics etc.)
        self._update_signal_processor_with_concatenated_data(concatenated_signals)
        
        # Show success message
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setStyleSheet(self._get_message_box_style())
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Concatenated filter applied to all graphs in this tab.\n\n"
            f"Time axis shows {len(time_segments)} segments continuously.\n\n"
            f"All {len(concatenated_signals)} signals are now synchronized to the filtered time domain.")
        msg.setWindowTitle("Global Filter Applied")
        msg.exec_()
        
        logger.info(f"Global concatenated filter applied successfully to {len(concatenated_signals)} signals")

    def _create_concatenated_signals(self, all_signals: dict, time_segments: list) -> dict:
        """Create concatenated signal data for all signals."""
        concatenated_signals = {}
        
        for signal_name, signal_data in all_signals.items():
            full_x_data = np.array(signal_data.get('x_data', []))
            full_y_data = np.array(signal_data.get('y_data', []))
            
            # Concatenate all segments for this signal
            concatenated_x = []
            concatenated_y = []
            new_time_offset = 0.0
            
            for i, (segment_start, segment_end) in enumerate(time_segments):
                # Find indices for this segment
                mask = (full_x_data >= segment_start) & (full_x_data <= segment_end)
                segment_x = full_x_data[mask]
                segment_y = full_y_data[mask]
                
                if len(segment_x) > 0:
                    # Adjust time axis for concatenation
                    if i == 0:
                        adjusted_x = segment_x - segment_x[0]  # Start from 0
                    else:
                        adjusted_x = segment_x - segment_x[0] + new_time_offset
                        
                    concatenated_x.extend(adjusted_x)
                    concatenated_y.extend(segment_y)
                    
                    # Update offset for next segment
                    if len(adjusted_x) > 0:
                        new_time_offset = adjusted_x[-1] + (adjusted_x[-1] - adjusted_x[0]) * 0.01  # Small gap
                        
            if concatenated_x:
                concatenated_signals[signal_name] = {
                    'x_data': np.array(concatenated_x),
                    'y_data': np.array(concatenated_y),
                    'original_x': full_x_data,
                    'original_y': full_y_data,
                    'metadata': signal_data.get('metadata', {})
                }
                
        logger.info(f"Created concatenated data for {len(concatenated_signals)} signals")
        return concatenated_signals

    def _update_signal_processor_with_concatenated_data(self, concatenated_signals: dict):
        """Update signal processor with concatenated data for statistics calculations."""
        try:
            # Clear existing data
            self.signal_processor.clear_all_data()
            
            # Add concatenated signals
            for signal_name, concat_data in concatenated_signals.items():
                self.signal_processor.add_signal(
                    signal_name,
                    concat_data['x_data'],
                    concat_data['y_data'],
                    concat_data.get('metadata', {})
                )
                
            logger.info(f"Updated signal processor with {len(concatenated_signals)} concatenated signals")
            
            # Update statistics panel
            self._update_statistics()
            
        except Exception as e:
            logger.error(f"Error updating signal processor with concatenated data: {e}")
        
    def _get_signal_color(self, signal_name: str) -> str:
        """Get color for a signal (simplified version)."""
        # Simple color cycling - in real implementation, use proper color management
        colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
        hash_value = hash(signal_name) % len(colors)
        return colors[hash_value]
    
    def _update_legend_values(self):
        """Update legend with current values."""
        if self.current_cursor_position is not None:
            signal_data = {}
            for signal_name in self.signal_processor.get_all_signals().keys():
                value = self.signal_processor.get_signal_at_time(signal_name, self.current_cursor_position)
                if value is not None:
                    signal_data[signal_name] = {'y_data': [value]}
            self.legend_manager.update_values_from_data(signal_data)
        else:
            all_signals = self.signal_processor.get_all_signals()
            signal_data = {}
            for signal_name, data in all_signals.items():
                if 'y_data' in data and len(data['y_data']) > 0:
                    signal_data[signal_name] = {'y_data': data['y_data']}
            self.legend_manager.update_values_from_data(signal_data)
        
        # Update statistics panel with new cursor values
        self._update_statistics()
    
    # Public API methods
    def set_theme(self, theme_name: str):
        """Set the visual theme."""
        self.theme_manager.set_theme(theme_name)
    
    def _apply_theme(self):
        """Apply the current theme to all components."""
        theme_name = self.theme_manager.get_current_theme()
        
        # Apply to main widget background and panels
        self.setStyleSheet(f"background-color: {self.theme_manager.get_color('background')};")
        
        # Update toolbar with theme colors
        if hasattr(self.toolbar_manager, 'update_theme'):
            self.toolbar_manager.update_theme()
        else:
            self.toolbar_manager.get_toolbar().setStyleSheet(
                self.theme_manager.get_widget_stylesheet('toolbar', theme_name)
            )
        self.settings_panel_manager.get_settings_panel().setStyleSheet(
            self.theme_manager.get_widget_stylesheet('panel', theme_name)
        )
        self.statistics_settings_panel_manager.get_settings_panel().setStyleSheet(
            self.theme_manager.get_widget_stylesheet('panel', theme_name)
        )
        self.graph_settings_panel_manager.get_settings_panel().setStyleSheet(
            self.theme_manager.get_widget_stylesheet('panel', theme_name)
        )
        if hasattr(self, 'channel_stats_panel'):
            self.channel_stats_panel.setStyleSheet(
                self.theme_manager.get_widget_stylesheet('panel', theme_name)
            )
        
        # Update statistics panel with theme colors
        if hasattr(self, 'statistics_panel') and hasattr(self.statistics_panel, 'update_theme'):
            self.statistics_panel.update_theme(self.theme_manager.get_theme_colors())
        
        # Apply to all graph containers
        for container in self.graph_containers:
            container.apply_theme()
        
        # Redraw signals with new theme colors
        self._redraw_all_signals()
    
    def _setup_connections(self):
        """Setup signal-slot connections for the widget."""
        # Toolbar connections
        self.toolbar_manager.cursor_mode_changed.connect(self._on_cursor_mode_changed)
        self.toolbar_manager.panel_toggled.connect(self._on_panel_toggled)
        self.toolbar_manager.settings_toggled.connect(self._on_settings_toggled)
        self.toolbar_manager.graph_count_changed.connect(self._on_graph_count_changed)
        
        # Connect the new statistics settings toggle signal
        if hasattr(self.toolbar_manager, 'statistics_settings_toggled'):
            self.toolbar_manager.statistics_settings_toggled.connect(self._on_statistics_settings_toggled)
            
        if hasattr(self.toolbar_manager, 'graph_settings_toggled'):
            self.toolbar_manager.graph_settings_toggled.connect(self._on_graph_settings_toggled)
            
        # Connect new analysis panel signals
        if hasattr(self.toolbar_manager, 'correlations_toggled'):
            self.toolbar_manager.correlations_toggled.connect(self._on_correlations_toggled)
            
        if hasattr(self.toolbar_manager, 'bitmask_toggled'):
            self.toolbar_manager.bitmask_toggled.connect(self._on_bitmask_toggled)

        # Settings panel connections
        self.settings_panel_manager.theme_changed.connect(self.set_theme)

        # Statistics settings panel connections
        self.statistics_settings_panel_manager.visible_columns_changed.connect(self._on_visible_columns_changed)
        self.statistics_settings_panel_manager.duty_cycle_threshold_changed.connect(self._on_duty_cycle_threshold_changed)
        
        # Graph settings panel connections
        self.graph_settings_panel_manager.normalization_toggled.connect(self._on_per_graph_normalization_toggled)
        self.graph_settings_panel_manager.view_reset_requested.connect(self._on_per_graph_view_reset)
        self.graph_settings_panel_manager.grid_visibility_changed.connect(self._on_per_graph_grid_changed)
        self.graph_settings_panel_manager.autoscale_changed.connect(self._on_per_graph_autoscale_changed)

        # Theme manager connections
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Settings panel connections
        self.settings_panel_manager.theme_changed.connect(self.theme_manager.set_theme)
        
        # Connect bitmask panel to theme changes
        self.theme_manager.theme_changed.connect(self.bitmask_panel_manager.update_theme)
        
        # Legend manager connections
        self.legend_manager.signal_visibility_changed.connect(self._on_signal_visibility_changed)
        self.legend_manager.signal_selected.connect(self._on_signal_selected)
        
        # Signal processor connections
        self.signal_processor.processing_started.connect(self._on_processing_started)
        self.signal_processor.processing_finished.connect(self._on_processing_finished)
        self.signal_processor.statistics_updated.connect(self._on_statistics_updated)
    
    def _on_signal_color_changed(self, signal_name: str, new_color: str):
        """Handle color changes for a specific signal from the statistics panel."""
        logger.debug(f"Color change requested for signal '{signal_name}' to {new_color}")
        
        all_signals = self.signal_processor.get_all_signals()
        all_signal_names = sorted(list(all_signals.keys()))
        
        if signal_name in all_signal_names:
            signal_index = all_signal_names.index(signal_name)
            
            # Update theme manager with the color override
            self.theme_manager.set_signal_color_override(signal_index, new_color)
            
            # Redraw all signals to apply the new color
            self._redraw_all_signals()
        else:
            logger.warning(f"Could not find signal '{signal_name}' to change its color.")

    def _on_visible_columns_changed(self, visible_columns: set):
        """Handle changes to visible statistics columns."""
        self.visible_stats_columns = visible_columns
        # Update the statistics panel with new visible columns
        self.statistics_panel.set_visible_stats(visible_columns)
        self._recreate_statistics_panel() # Redraw panel with new columns

    def _on_duty_cycle_threshold_changed(self, threshold_mode: str, threshold_value: float):
        """Handle changes to duty cycle threshold settings."""
        self.duty_cycle_threshold_mode = threshold_mode
        self.duty_cycle_threshold_value = threshold_value
        
        # Update statistics with new threshold settings
        self._update_statistics()
        
        logger.info(f"Duty cycle threshold updated: mode={threshold_mode}, value={threshold_value}")
    
    def get_current_statistics(self) -> Dict[str, Dict]:
        """Get current statistics for all signals."""
        return self.signal_processor.calculate_statistics()
    
    def export_data(self) -> Dict[str, Any]:
        """Export current data and settings."""
        return {
            'signals': self.signal_processor.get_all_signals(),
            'theme': self.theme_manager.get_current_theme(),
            'normalized': self.is_normalized,
            'cursor_position': self.current_cursor_position,
            'selected_range': self.selected_range
        }
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics."""
        return self.signal_processor.get_memory_usage()
    
    def cleanup(self):
        """Cleanup resources."""
        if self.cursor_manager:
            self.cursor_manager.deleteLater()
        self.legend_manager.stop_updates()
        self.signal_processor.clear_all_data()
        for container in self.graph_containers:
            container.plot_manager.clear_all_signals()
        self.legend_manager.clear_all_items()
        logger.info("TimeGraphWidget cleanup completed")

    def _save_graph_setting(self, graph_index: int, setting_name: str, value):
        """Save a setting for a specific graph in the active tab."""
        active_tab_index = self.tab_widget.currentIndex()
        if active_tab_index < 0:
            return
            
        # Initialize tab settings if not exists
        if active_tab_index not in self.graph_settings:
            self.graph_settings[active_tab_index] = {}
            
        # Initialize graph settings if not exists
        if graph_index not in self.graph_settings[active_tab_index]:
            self.graph_settings[active_tab_index][graph_index] = {}
            
        # Save the setting
        self.graph_settings[active_tab_index][graph_index][setting_name] = value
        logger.debug(f"Saved setting: Tab {active_tab_index}, Graph {graph_index}, {setting_name} = {value}")

    def _get_graph_setting(self, graph_index: int, setting_name: str, default_value=None):
        """Get a setting for a specific graph in the active tab."""
        active_tab_index = self.tab_widget.currentIndex()
        if active_tab_index < 0:
            return default_value
            
        return (self.graph_settings
                .get(active_tab_index, {})
                .get(graph_index, {})
                .get(setting_name, default_value))

    def _apply_saved_graph_settings(self):
        """Apply saved settings to all graphs in the active tab."""
        active_container = self.get_active_graph_container()
        if not active_container:
            return
            
        active_tab_index = self.tab_widget.currentIndex()
        if active_tab_index < 0:
            return
            
        plot_widgets = active_container.get_plot_widgets()
        tab_settings = self.graph_settings.get(active_tab_index, {})
        
        for graph_index, graph_settings in tab_settings.items():
            if 0 <= graph_index < len(plot_widgets):
                plot_widget = plot_widgets[graph_index]
                
                # Apply grid setting
                show_grid = graph_settings.get('show_grid', True)  # Default to True
                plot_widget.showGrid(x=show_grid, y=show_grid)
                
                # Apply autoscale setting
                autoscale = graph_settings.get('autoscale', True)  # Default to True
                plot_widget.enableAutoRange(axis='y', enable=autoscale)
                
                logger.debug(f"Applied settings to Graph {graph_index}: grid={show_grid}, autoscale={autoscale}")
        
        # Update graph settings panel to reflect current settings
        self._sync_graph_settings_panel()

    def _sync_graph_settings_panel(self):
        """Synchronize the graph settings panel checkboxes with actual settings."""
        if hasattr(self, 'graph_settings_panel_manager'):
            self.graph_settings_panel_manager.sync_with_current_settings(self.graph_settings, self.tab_widget.currentIndex())

    def _recreate_statistics_panel(self):
        """Recreates the channel statistics groups in the ATI panel based on the active tab."""
        # Clear all existing signals from the modern statistics panel
        self.statistics_panel.clear_all()
        
        # Reset the storage for signal tracking
        self.channel_stats_widgets = {}

        # Get active container and add signals to the modern panel
        active_container = self.get_active_graph_container()
        if not active_container:
            return
            
        # Add signals from all graphs to the statistics panel
        num_graphs = active_container.plot_manager.get_subplot_count()
        tab_index = self.tab_widget.currentIndex()
        
        # Ensure statistics panel has sections for all graphs
        if num_graphs > 0:
            self.statistics_panel.ensure_graph_sections(num_graphs - 1)
        
        for graph_idx in range(num_graphs):
            # Get signals for this graph
            tab_mapping = self.graph_signal_mapping.get(tab_index, {})
            if graph_idx in tab_mapping:
                signals = tab_mapping[graph_idx]
                
                for signal_name in signals:
                    # Try to get signal color from plot manager, fallback to theme manager
                    color = active_container.plot_manager.get_signal_color(graph_idx, signal_name)
                    if not color:
                        # Fallback: use theme manager to get color by signal index
                        all_signals = list(self.signal_processor.get_all_signals().keys())
                        if signal_name in all_signals:
                            signal_index = all_signals.index(signal_name)
                            color = self.theme_manager.get_signal_color(signal_index)
                        else:
                            color = "#ffffff"  # Default white
                    
                    # Add signal to modern statistics panel
                    full_signal_name = f"{signal_name} (G{graph_idx+1})"
                    self.statistics_panel.add_signal(full_signal_name, graph_idx, signal_name, color)
                    #logger.debug(f"Added signal '{signal_name}' to graph {graph_idx+1} statistics panel with color {color}")
        
        self._update_statistics()


