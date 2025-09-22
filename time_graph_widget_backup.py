# type: ignore
"""
Advanced Time-Series Analysis Widget

This is the main analysis interface that provides:
- Interactive cursor modes (Single, Dual, Range Selection)
- Real-time statistics calculation
- Data normalization features
- Professional toolbar interface
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QToolButton, 
    QButtonGroup, QLabel, QGroupBox, QFormLayout, QSplitter,
    QPushButton, QFrame, QScrollArea, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal as Signal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

from .cursor_manager import CursorManager
from .statistics_panel import StatisticsPanel
from .data_manager import TimeSeriesDataManager

logger = logging.getLogger(__name__)

class TimeGraphWidget(QWidget):
    """
    Advanced Time Graph Widget
    
    Features:
    - Interactive cursor modes (None, Single, Dual, Range Selection)
    - Real-time statistics calculation and display
    - Data normalization with visual feedback
    - Professional toolbar interface
    - High-performance PyQtGraph plotting
    """
    
    # Signals
    data_changed = Signal(object)  # Emitted when data is updated
    cursor_moved = Signal(str, object)  # Emitted when cursor position changes
    range_selected = Signal(tuple)  # Emitted when range is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data management
        self.data_manager = TimeSeriesDataManager()
        
        # UI Components
        self.plot_widgets = []
        self.toolbar = None
        self.cursor_manager = None
        
        # Panel components
        self.statistics_panel = None
        self.panel_visible = True
        
        # Graph management
        self.subplot_count = 3
        self.max_subplots = 10
        self.min_subplots = 1
        
        # State variables
        self.current_signals = {}  # Dict of signal_name -> plot_data_item
        self.is_normalized = False
        
        # Setup UI
        self._setup_ui()
        self._setup_toolbar()
        
        # Initialize with sample data
        self._create_sample_data()
        
        logger.info("TimeAnalysisWidget initialized successfully")

    def _setup_ui(self):
        """Setup the main UI layout with left statistics panel."""
        # Main layout - no margins for maximum plot area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)
        
        # Compact toolbar at top
        self.toolbar = QToolBar("Analysis Tools")
        self.toolbar.setMovable(False)
        self.toolbar.setMaximumHeight(32)  # Compact height
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2b2b2b;
                border: none;
                spacing: 2px;
            }
            QToolButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 8px;
                margin: 1px;
                color: white;
                font-size: 10px;
                min-width: 60px;
            }
            QToolButton:checked {
                background-color: #0078d4;
                border-color: #106ebe;
            }
            QToolButton:hover {
                background-color: #505050;
            }
            QSpinBox {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                color: white;
                padding: 2px;
                max-width: 50px;
            }
        """)
        main_layout.addWidget(self.toolbar)
        
        # Content area with two panels
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #555555;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #777777;
            }
        """)
        
        # Left panel: Statistics and settings panel (collapsible)
        self.statistics_panel = self._create_statistics_panel()
        self.statistics_panel.setMinimumWidth(200)
        self.statistics_panel.setMaximumWidth(350)
        content_splitter.addWidget(self.statistics_panel)
        
        # Right panel: Plot area with graph controls
        plot_panel = self._create_plot_panel()
        content_splitter.addWidget(plot_panel)
        
        # Set splitter proportions: 20% - 80%
        content_splitter.setSizes([250, 1000])
        content_splitter.setCollapsible(0, True)  # Statistics panel can be collapsed
        content_splitter.setCollapsible(1, False)  # Plot panel cannot be collapsed
        
        main_layout.addWidget(content_splitter)
        
        # Create stacked plots after all panels are initialized
        self._setup_stacked_plots()
        
        # Initialize cursor manager after plots are created
        self.cursor_manager = CursorManager(self.plot_widgets)
        
        # Setup signal-slot connections after all components are ready
        self._setup_connections()
        
        # Update graph settings buttons now that all panels exist
        self._update_graph_settings_buttons()
        
        # Apply dark theme
        self._apply_dark_theme()
    
    def _create_plot_panel(self):
        """Create the main plot panel with graph controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Graph controls header
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(4, 2, 4, 2)
        
        # Graph count controls
        graph_count_label = QLabel("📈 Graphs:")
        graph_count_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
        
        self.decrease_graphs_btn = QPushButton("-")
        self.decrease_graphs_btn.setMaximumSize(25, 25)
        self.decrease_graphs_btn.setToolTip("Decrease number of graphs")
        self.decrease_graphs_btn.clicked.connect(self._decrease_graph_count)
        
        self.graph_count_spin = QSpinBox()
        self.graph_count_spin.setRange(self.min_subplots, self.max_subplots)
        self.graph_count_spin.setValue(self.subplot_count)
        self.graph_count_spin.setToolTip("Number of graphs")
        self.graph_count_spin.valueChanged.connect(self._update_graph_count)
        
        self.increase_graphs_btn = QPushButton("+")
        self.increase_graphs_btn.setMaximumSize(25, 25)
        self.increase_graphs_btn.setToolTip("Increase number of graphs")
        self.increase_graphs_btn.clicked.connect(self._increase_graph_count)
        
        controls_layout.addWidget(graph_count_label)
        controls_layout.addWidget(self.decrease_graphs_btn)
        controls_layout.addWidget(self.graph_count_spin)
        controls_layout.addWidget(self.increase_graphs_btn)
        controls_layout.addStretch()
        
        # Apply button styling
        button_style = """
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #0078d4;
            }
        """
        self.decrease_graphs_btn.setStyleSheet(button_style)
        self.increase_graphs_btn.setStyleSheet(button_style)
        
        layout.addLayout(controls_layout)
        
        # Plot container
        self.plot_container = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_container)
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.setSpacing(1)
        
        # Stacked plots will be created after all panels are initialized
        
        layout.addWidget(self.plot_container)
        
        return panel
    
    def _create_statistics_panel(self):
        """Create statistics and settings panel on the left with show/hide toggle."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #404040;
            }
            QLabel {
                color: white;
                font-size: 10px;
                padding: 2px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 3px;
                margin-top: 8px;
                padding-top: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px 6px;
                color: white;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Panel header with hide/show button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("📊 Analysis Panel")
        title.setStyleSheet("font-weight: bold; font-size: 11px; color: #ffffff;")
        
        self.panel_toggle_btn = QPushButton("▶")
        self.panel_toggle_btn.setMaximumSize(20, 20)
        self.panel_toggle_btn.setToolTip("Hide/Show Analysis Panel")
        self.panel_toggle_btn.clicked.connect(self._toggle_statistics_panel)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.panel_toggle_btn)
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #555555;")
        layout.addWidget(separator)
        
        # Signal Legend Section
        legend_group = QGroupBox("📊 Signal Legend")
        legend_layout = QVBoxLayout(legend_group)
        legend_layout.setContentsMargins(4, 8, 4, 4)
        legend_layout.setSpacing(2)
        
        # Legend scroll area
        legend_scroll = QScrollArea()
        legend_scroll.setWidgetResizable(True)
        legend_scroll.setMaximumHeight(150)
        legend_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 10px;
            }
        """)
        
        # Legend content container
        self.legend_container = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_container)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setSpacing(1)
        
        legend_scroll.setWidget(self.legend_container)
        legend_layout.addWidget(legend_scroll)
        
        layout.addWidget(legend_group)
        
        # Statistics scroll area
        stats_group = QGroupBox("📊 Statistics")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setContentsMargins(4, 8, 4, 4)
        stats_layout.setSpacing(2)
        
        stats_scroll = QScrollArea()
        stats_scroll.setWidgetResizable(True)
        stats_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 10px;
            }
        """)
        
        # Statistics content
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setSpacing(2)
        
        stats_scroll.setWidget(self.stats_container)
        stats_layout.addWidget(stats_scroll)
        
        layout.addWidget(stats_group)
        
        # Graph settings section
        settings_group = QGroupBox("⚙️ Graph Settings")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(4, 8, 4, 4)
        settings_layout.setSpacing(2)
        
        # Create settings buttons for each graph (will be populated dynamically)
        self.graph_settings_container = QWidget()
        self.graph_settings_layout = QVBoxLayout(self.graph_settings_container)
        self.graph_settings_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_settings_layout.setSpacing(2)
        
        settings_layout.addWidget(self.graph_settings_container)
        layout.addWidget(settings_group)
        
        layout.addStretch()
        
        # Initialize components
        self.legend_items = {}  # signal_name -> QWidget
        self.panel_visible = True
        
        return panel
    def _setup_stacked_plots(self):
        """Create stacked subplots with shared time axis."""
        # Clear existing plots
        for plot_widget in self.plot_widgets:
            plot_widget.setParent(None)
        self.plot_widgets.clear()
        
        # Clear layout
        while self.plot_layout.count():
            child = self.plot_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Create new plot widgets
        for i in range(self.subplot_count):
            plot_widget = pg.PlotWidget()
            
            # Styling
            plot_widget.setBackground('#1e1e1e')
            plot_widget.showGrid(True, True, alpha=0.3)
            plot_widget.getAxis('left').setPen(color='#ffffff')
            plot_widget.getAxis('bottom').setPen(color='#ffffff')
            plot_widget.getAxis('left').setTextPen(color='#ffffff')
            plot_widget.getAxis('bottom').setTextPen(color='#ffffff')
            
            # Configure axes
            if i == self.subplot_count - 1:  # Only bottom plot shows time labels
                plot_widget.setLabel('bottom', 'Time', color='white', size='10pt')
            else:
                plot_widget.getAxis('bottom').setStyle(showValues=False)
            
            plot_widget.setLabel('left', f'Graph {i+1}', color='white', size='9pt')
            
            # Store reference
            self.plot_widgets.append(plot_widget)
            self.plot_layout.addWidget(plot_widget)
            
            # Link X-axes for synchronized zooming
            if i > 0:
                plot_widget.setXLink(self.plot_widgets[0])
        
        # Equal height distribution
        for i, plot_widget in enumerate(self.plot_widgets):
            self.plot_layout.setStretch(i, 1)
        
        # Update cursor manager
        if hasattr(self, 'cursor_manager') and self.cursor_manager:
            self.cursor_manager.plot_widgets = self.plot_widgets
            self.cursor_manager.clear_all()
        
        # Update graph settings buttons if the layout exists
        if hasattr(self, 'graph_settings_layout'):
            self._update_graph_settings_buttons()
    
    def _create_ati_vision_legend(self):
        """Create ATI Vision-style compact legend panel with signal values."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #404040;
            }
            QLabel {
                color: white;
                font-size: 10px;
                padding: 2px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 3px;
                margin-top: 8px;
                padding-top: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Legend title
        title = QLabel("Legend")
        title.setStyleSheet("font-weight: bold; font-size: 11px; color: #ffffff;")
        layout.addWidget(title)
        
        # Signal legend container
        self.legend_container = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_container)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setSpacing(1)
        
        layout.addWidget(self.legend_container)
        layout.addStretch()
        
        # Signal legend items will be added dynamically
        self.legend_items = {}  # signal_name -> QWidget
        
        return panel
    
    def _apply_dark_theme(self):
        """Apply dark theme to the entire widget."""
        self.setStyleSheet("""
            TimeAnalysisWidget {
                background-color: #1e1e1e;
                color: white;
            }
        """)

    def _setup_toolbar(self):
        """Setup the toolbar with cursor controls and panel toggles."""
        
        # Statistics panel toggle
        panel_toggle_btn = QToolButton()
        panel_toggle_btn.setText("📊 Panel")
        panel_toggle_btn.setToolTip("Toggle statistics panel visibility")
        panel_toggle_btn.setCheckable(True)
        panel_toggle_btn.setChecked(True)
        panel_toggle_btn.clicked.connect(self._toggle_statistics_panel)
        self.toolbar.addWidget(panel_toggle_btn)
        
        self.toolbar.addSeparator()
        
        # Cursor Controls Group
        cursor_group = QButtonGroup(self)
        
        # No Cursor button
        no_cursor_btn = QToolButton()
        no_cursor_btn.setText("No Cursor")
        no_cursor_btn.setToolTip("Disable all cursors")
        no_cursor_btn.setCheckable(True)
        no_cursor_btn.setChecked(True)  # Default mode
        no_cursor_btn.clicked.connect(lambda: self._set_cursor_mode("none"))
        cursor_group.addButton(no_cursor_btn)
        self.toolbar.addWidget(no_cursor_btn)
        
        # Single Cursor button
        single_cursor_btn = QToolButton()
        single_cursor_btn.setText("Single")
        single_cursor_btn.setToolTip("Enable single movable cursor")
        single_cursor_btn.setCheckable(True)
        single_cursor_btn.clicked.connect(lambda: self._set_cursor_mode("single"))
        cursor_group.addButton(single_cursor_btn)
        self.toolbar.addWidget(single_cursor_btn)
        
        # Two Cursors button
        dual_cursor_btn = QToolButton()
        dual_cursor_btn.setText("Dual")
        dual_cursor_btn.setToolTip("Enable two independent cursors")
        dual_cursor_btn.setCheckable(True)
        dual_cursor_btn.clicked.connect(lambda: self._set_cursor_mode("dual"))
        cursor_group.addButton(dual_cursor_btn)
        self.toolbar.addWidget(dual_cursor_btn)
        
        # Range Selector button
        range_selector_btn = QToolButton()
        range_selector_btn.setText("Range")
        range_selector_btn.setToolTip("Enable range selection for statistics")
        range_selector_btn.setCheckable(True)
        range_selector_btn.clicked.connect(lambda: self._set_cursor_mode("range"))
        cursor_group.addButton(range_selector_btn)
        self.toolbar.addWidget(range_selector_btn)
        
        self.toolbar.addSeparator()
        
        # View Controls
        reset_view_btn = QToolButton()
        reset_view_btn.setText("Reset View")
        reset_view_btn.setToolTip("Reset plot view to show all data")
        reset_view_btn.clicked.connect(self._reset_view)
        self.toolbar.addWidget(reset_view_btn)
        
        self.toolbar.addSeparator()
        
        # Data Processing
        self.normalize_btn = QToolButton()
        self.normalize_btn.setText("Normalize")
        self.normalize_btn.setToolTip("Apply peak normalization to all signals")
        self.normalize_btn.setCheckable(True)
        self.normalize_btn.clicked.connect(self._toggle_normalization)
        self.toolbar.addWidget(self.normalize_btn)

    def _setup_connections(self):
        """Setup signal-slot connections."""
        # Connect cursor manager signals
        self.cursor_manager.cursor_moved.connect(self._on_cursor_moved)
        self.cursor_manager.range_changed.connect(self._on_range_changed)
        
        # Connect data manager signals
        self.data_manager.data_changed.connect(self._on_data_updated)

    def _create_sample_data(self):
        """Create sample sine wave data for demonstration."""
        # Generate sample time-series data
        t = np.linspace(0, 10, 1000)
        signal1 = np.sin(2 * np.pi * 1 * t) + 0.1 * np.sin(2 * np.pi * 10 * t)
        signal2 = np.cos(2 * np.pi * 0.5 * t) + 0.2 * np.random.normal(0, 1, len(t))
        
        # Add signals to the plot
        self.setData(t, signal1, "Sine Wave")
        self.setData(t, signal2, "Cosine + Noise")

    def setData(self, x_data: np.ndarray, y_data: np.ndarray, name: str = "Signal"):
        """
        Add a new signal to the plot - ATI Vision style.
        
        Args:
            x_data: Time or X-axis data
            y_data: Signal values
            name: Signal name for display
        """
        # Store original data
        self.data_manager.add_signal(name, x_data, y_data)
        
        # Get signal index and assign to subplot
        signal_index = len(self.current_signals)
        subplot_index = signal_index % len(self.plot_widgets)
        plot_widget = self.plot_widgets[subplot_index]
        
        # ATI Vision colors (cyan, green, red, blue, yellow, etc.)
        ati_colors = ['#00FFFF', '#00FF00', '#FF0000', '#0080FF', '#FFFF00', '#FF8000', '#FF00FF', '#FFFFFF']
        color = ati_colors[signal_index % len(ati_colors)]
        
        # Create plot item with ATI Vision styling
        pen = pg.mkPen(color=color, width=1.5)  # Thinner lines like ATI Vision
        plot_item = plot_widget.plot(x_data, y_data, pen=pen, name=name)
        
        # Store signal data
        self.current_signals[name] = {
            'plot_item': plot_item,
            'plot_widget': plot_widget,
            'subplot_index': subplot_index,
            'color': color,
            'x_data': x_data,
            'y_data': y_data,
            'original_y': y_data.copy()  # Store original for normalization
        }
        
        # Add to ATI Vision legend
        self._add_legend_item(name, color, y_data[-1] if len(y_data) > 0 else 0.0)
        
        # Update plot label
        if len([s for s in self.current_signals.values() if s['subplot_index'] == subplot_index]) == 1:
            # First signal in this subplot
            plot_widget.setLabel('left', name, color='white', size='9pt')
        
        logger.info(f"Added signal '{name}' to subplot {subplot_index} with {len(y_data)} data points")

    def _toggle_statistics_panel(self):
        """Toggle visibility of the statistics panel."""
        self.panel_visible = not self.panel_visible
        self.statistics_panel.setVisible(self.panel_visible)
        
        # Update button text
        if self.panel_visible:
            self.panel_toggle_btn.setText("▶")  # Right arrow (hide)
            self.panel_toggle_btn.setToolTip("Hide Analysis Panel")
        else:
            self.panel_toggle_btn.setText("◀")  # Left arrow (show)
            self.panel_toggle_btn.setToolTip("Show Analysis Panel")
        
        logger.info(f"Statistics panel {'shown' if self.panel_visible else 'hidden'}")
    
    def _increase_graph_count(self):
        """Increase the number of graphs."""
        if self.subplot_count < self.max_subplots:
            self.subplot_count += 1
            self.graph_count_spin.setValue(self.subplot_count)
            self._rebuild_plots()
            logger.info(f"Increased graph count to {self.subplot_count}")
    
    def _decrease_graph_count(self):
        """Decrease the number of graphs."""
        if self.subplot_count > self.min_subplots:
            self.subplot_count -= 1
            self.graph_count_spin.setValue(self.subplot_count)
            self._rebuild_plots()
            logger.info(f"Decreased graph count to {self.subplot_count}")
    
    def _update_graph_count(self, value):
        """Update graph count from spinbox."""
        if value != self.subplot_count:
            self.subplot_count = value
            self._rebuild_plots()
            logger.info(f"Graph count updated to {self.subplot_count}")
    
    def _rebuild_plots(self):
        """Rebuild all plots with new count and redistribute signals."""
        # Store current signal data
        signals_backup = {}
        for name, signal_data in self.current_signals.items():
            signals_backup[name] = {
                'x_data': signal_data['x_data'].copy(),
                'y_data': signal_data['original_y'].copy(),  # Use original data
                'color': signal_data['color']
            }
        
        # Clear current signals
        self.current_signals.clear()
        
        # Rebuild plots
        self._setup_stacked_plots()
        
        # Restore signals
        for name, signal_data in signals_backup.items():
            self.setData(signal_data['x_data'], signal_data['y_data'], name)
        
        # Apply normalization if it was enabled
        if self.is_normalized:
            self._apply_normalization()
    
    def _update_graph_settings_buttons(self):
        """Update graph settings buttons based on current graph count."""
        # Safety check - ensure the layout exists
        if not hasattr(self, 'graph_settings_layout') or self.graph_settings_layout is None:
            return
            
        # Clear existing buttons
        while self.graph_settings_layout.count():
            child = self.graph_settings_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Create settings button for each graph
        for i in range(self.subplot_count):
            btn = QPushButton(f"⚙️ Graph {i+1} Settings")
            btn.setToolTip(f"Open settings for Graph {i+1}")
            btn.clicked.connect(lambda checked, idx=i: self._open_graph_settings(idx))
            self.graph_settings_layout.addWidget(btn)
    
    def _open_graph_settings(self, graph_index):
        """Open settings dialog for a specific graph."""
        # Placeholder for future implementation
        logger.info(f"Opening settings for Graph {graph_index + 1}")
        # TODO: Implement graph settings dialog
        print(f"TODO: Open Graph {graph_index + 1} Settings Dialog")

    def _add_legend_item(self, name: str, color: str, current_value: float):
        """Add a signal to the ATI Vision style legend panel."""
        # Create legend item widget
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(2, 1, 2, 1)
        item_layout.setSpacing(4)
        
        # Color indicator
        color_label = QLabel("●")
        color_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
        color_label.setFixedWidth(12)
        
        # Signal name
        name_label = QLabel(name)
        name_label.setStyleSheet("color: white; font-size: 10px;")
        name_label.setMinimumWidth(80)
        
        # Current value
        value_label = QLabel(f"{current_value:.3f}")
        value_label.setStyleSheet("color: #cccccc; font-size: 9px; font-family: monospace;")
        value_label.setAlignment(Qt.AlignRight)
        value_label.setMinimumWidth(50)
        
        item_layout.addWidget(color_label)
        item_layout.addWidget(name_label)
        item_layout.addStretch()
        item_layout.addWidget(value_label)
        
        # Store reference for updates
        self.legend_items[name] = {
            'widget': item_widget,
            'value_label': value_label,
            'color': color
        }
        
        # Add to legend layout
        self.legend_layout.addWidget(item_widget)

    def _get_next_color(self, index: int) -> str:
        """Get the next color for a new signal."""
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        return colors[index % len(colors)]

    def _set_cursor_mode(self, mode: str):
        """Set the cursor interaction mode."""
        self.cursor_manager.set_mode(mode)
        logger.info(f"Cursor mode set to: {mode}")

    def _reset_view(self):
        """Reset the plot view to show all data."""
        for plot_widget in self.plot_widgets:
            plot_widget.autoRange()
        logger.info("Plot view reset to auto-range")

    def _toggle_normalization(self):
        """Toggle data normalization on/off."""
        self.is_normalized = self.normalize_btn.isChecked()
        
        if self.is_normalized:
            self._apply_normalization()
            for plot_widget in self.plot_widgets:
                plot_widget.setLabel('left', 'Normalized Amplitude', color='white', size='9pt')
        else:
            self._remove_normalization()
            for plot_widget in self.plot_widgets:
                plot_widget.setLabel('left', 'Values', color='white', size='9pt')
        
        # Update statistics after normalization change
        self._update_statistics()
        
        logger.info(f"Data normalization {'enabled' if self.is_normalized else 'disabled'}")

    def _apply_normalization(self):
        """Apply peak normalization to all signals."""
        for name, signal_data in self.current_signals.items():
            original_y = signal_data['original_y']
            max_abs = np.max(np.abs(original_y))
            
            if max_abs > 0:
                normalized_y = original_y / max_abs
                signal_data['plot_item'].setData(signal_data['x_data'], normalized_y)
                signal_data['y_data'] = normalized_y

    def _remove_normalization(self):
        """Remove normalization and restore original data."""
        for name, signal_data in self.current_signals.items():
            original_y = signal_data['original_y']
            signal_data['plot_item'].setData(signal_data['x_data'], original_y)
            signal_data['y_data'] = original_y

    def _on_cursor_moved(self, cursor_type: str, position: float):
        """Handle cursor movement events."""
        # Update statistics based on cursor position
        self._update_statistics()
        
        # Emit signal for external listeners
        self.cursor_moved.emit(cursor_type, position)

    def _on_range_changed(self, start: float, end: float):
        """Handle range selection changes."""
        # Update statistics for the selected range
        self._update_statistics()
        
        # Emit signal for external listeners
        self.range_selected.emit((start, end))

    def _on_data_updated(self):
        """Handle data manager updates."""
        self._update_statistics()
        self.data_changed.emit(self.data_manager)

    def _update_statistics(self):
        """Update the legend values based on current data and cursor position."""
        if not self.current_signals:
            return
        
        # Get cursor position for current value display
        cursor_pos = None
        if hasattr(self.cursor_manager, 'get_cursor_position'):
            cursor_pos = self.cursor_manager.get_cursor_position()
        
        for name, signal_data in self.current_signals.items():
            x_data = signal_data['x_data']
            y_data = signal_data['y_data']
            
            # Get current value at cursor position or last value
            if cursor_pos is not None and len(x_data) > 0:
                # Find closest data point to cursor
                idx = np.argmin(np.abs(x_data - cursor_pos))
                current_value = y_data[idx]
            else:
                # Use last value
                current_value = y_data[-1] if len(y_data) > 0 else 0.0
            
            # Update legend item value
            if name in self.legend_items:
                self.legend_items[name]['value_label'].setText(f"{current_value:.3f}")

    def _get_statistics_range(self) -> Optional[Tuple[float, float]]:
        """Get the current range for statistics calculation."""
        if self.cursor_manager.current_mode == "range":
            return self.cursor_manager.get_range()
        else:
            # Use visible range of first plot widget if no specific range is selected
            if self.plot_widgets:
                view_range = self.plot_widgets[0].getViewBox().viewRange()
                return view_range[0]  # x-axis range
            return None

    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """
        Calculate statistics for the given data.
        
        Args:
            data: NumPy array of signal values
            
        Returns:
            Dictionary with calculated statistics
        """
        return {
            'mean': float(np.mean(data)),
            'max': float(np.max(data)),
            'min': float(np.min(data)),
            'rms': float(np.sqrt(np.mean(data**2))),
            'std': float(np.std(data))
        }

    def update_data(self, df=None):
        """Update the widget with new data (for integration with dialog system)."""
        if df is None:
            return
        
        # Clear existing data
        self.clear_all_data()
        
        # Extract columns and add as signals
        if hasattr(df, 'get_column_names'):
            # Vaex DataFrame
            columns = df.get_column_names()
            if len(columns) >= 2:
                x_col = columns[0]  # Assume first column is time
                x_data = df[x_col].to_numpy()
                
                for col in columns[1:4]:  # Add up to 3 signals
                    try:
                        y_data = df[col].to_numpy()
                        self.setData(x_data, y_data, col)
                    except Exception as e:
                        logger.warning(f"Could not add signal {col}: {e}")

    def clear_all_data(self):
        """Clear all signals and reset the widget."""
        # Clear all plot widgets
        for plot_widget in self.plot_widgets:
            plot_widget.clear()
        
        # Clear data structures
        self.current_signals.clear()
        
        # Clear legend items
        for item_data in self.legend_items.values():
            item_data['widget'].setParent(None)
        self.legend_items.clear()
        
        # Clear cursor manager
        self.cursor_manager.clear_all()
        
        # Reset normalization
        self.is_normalized = False
        self.normalize_btn.setChecked(False)
        for plot_widget in self.plot_widgets:
            plot_widget.setLabel('left', 'Values', color='white', size='9pt')