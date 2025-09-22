# type: ignore
"""
Toolbar Manager for Time Graph Widget

Manages the toolbar interface including:
- Cursor mode controls
- Panel toggles
- Graph and Tab count controls
- Normalization controls
"""

import logging
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import (
    QToolBar, QToolButton, QButtonGroup, QLabel, QSpinBox, QPushButton, QFrame, QHBoxLayout, QComboBox, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal as Signal, QObject
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

if TYPE_CHECKING:
    from .time_graph_widget import TimeGraphWidget

logger = logging.getLogger(__name__)

class ToolbarManager(QObject):
    """Manages the toolbar and its controls for the Time Graph Widget."""
    
    # Signals
    cursor_mode_changed = Signal(str)
    panel_toggled = Signal()
    settings_toggled = Signal()
    graph_settings_toggled = Signal()
    statistics_settings_toggled = Signal()
    correlations_toggled = Signal()
    bitmask_toggled = Signal()
    graph_count_changed = Signal(int)
    tab_count_changed = Signal(int)
    
    def __init__(self, parent_widget: "TimeGraphWidget"):
        super().__init__()
        self.parent = parent_widget
        self.toolbar = None
        self.cursor_group = None
        self.normalize_btn = None
        
        self.current_tab_count = 1
        self.current_graph_count = 1
        
        self._setup_toolbar()
        self._setup_connections()
    
    def _setup_toolbar(self):
        """Setup the toolbar with cursor controls and panel toggles."""
        self.toolbar = QToolBar("Analysis Tools")
        self.toolbar.setMovable(False)
        self.toolbar.setMinimumHeight(48)
        self.toolbar.setMaximumHeight(48)
        
        # Apply theme-based styling
        self._apply_theme_styling()
        
        # Settings button on the far left
        self._create_settings_control()
        self.toolbar.addSeparator()
        
        # Cursor mode controls
        self._create_cursor_controls()
        self.toolbar.addSeparator()

        # Graph count controls
        graph_count_label = QLabel("📊 Graphs:")
        graph_count_label.setObjectName("groupLabel")
        self.toolbar.addWidget(graph_count_label)
        self.graph_count_spinbox = QSpinBox()
        self.graph_count_spinbox.setRange(1, 10)
        self.graph_count_spinbox.setValue(1)
        self.graph_count_spinbox.setToolTip("Number of graphs to display in the current tab")
        self.toolbar.addWidget(self.graph_count_spinbox)
        
        self.toolbar.addSeparator()
        
        # Statistics panel toggle
        self.panel_toggle_btn = QToolButton()
        self.panel_toggle_btn.setObjectName("textButton")
        self.panel_toggle_btn.setText("📊 Statistics")
        self.panel_toggle_btn.setCheckable(True)
        self.panel_toggle_btn.setChecked(True)
        self.panel_toggle_btn.setToolTip("Toggle signal statistics panel")
        self.panel_toggle_btn.clicked.connect(self.panel_toggled.emit)
        self.toolbar.addWidget(self.panel_toggle_btn)

        # Statistics settings button
        self.statistics_settings_btn = QToolButton()
        self.statistics_settings_btn.setObjectName("textButton")
        self.statistics_settings_btn.setText("⚙️ Statistics Settings")
        self.statistics_settings_btn.setCheckable(True)
        self.statistics_settings_btn.setChecked(False)
        self.statistics_settings_btn.setToolTip("Configure which statistics to display")
        self.statistics_settings_btn.clicked.connect(self.statistics_settings_toggled.emit)
        self.toolbar.addWidget(self.statistics_settings_btn)
        
        self.toolbar.addSeparator()
        
        # Correlations button
        self.correlations_btn = QToolButton()
        self.correlations_btn.setObjectName("textButton")
        self.correlations_btn.setText("📈 Correlations")
        self.correlations_btn.setCheckable(True)
        self.correlations_btn.setChecked(False)
        self.correlations_btn.setToolTip("Open correlations analysis panel")
        self.correlations_btn.clicked.connect(self.correlations_toggled.emit)
        self.toolbar.addWidget(self.correlations_btn)
        
        # Bitmask button
        self.bitmask_btn = QToolButton()
        self.bitmask_btn.setObjectName("textButton")
        self.bitmask_btn.setText("🔢 Bitmask")
        self.bitmask_btn.setCheckable(True)
        self.bitmask_btn.setChecked(False)
        self.bitmask_btn.setToolTip("Open bitmask analysis panel")
        self.bitmask_btn.clicked.connect(self.bitmask_toggled.emit)
        self.toolbar.addWidget(self.bitmask_btn)

    def _apply_theme_styling(self):
        """Apply theme-based styling to the toolbar."""
        # Get theme colors from parent's theme manager
        if hasattr(self.parent, 'theme_manager'):
            colors = self.parent.theme_manager.get_theme_colors()
        else:
            # Fallback colors for space theme
            colors = {
                'surface': '#1a2332',
                'surface_variant': '#2d4a66',
                'primary': '#4a90e2',
                'primary_variant': '#6bb6ff',
                'text_primary': '#ffffff',
                'text_secondary': '#e6f3ff',
                'border': '#4a90e2',
                'hover': '#3a5f7a'
            }
        
        self.toolbar.setStyleSheet(f"""
            QToolBar {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface']}, stop: 1 {colors['surface_variant']});
                border: none;
                border-bottom: 2px solid {colors['primary']};
                spacing: 4px;
                padding: 4px 8px;
            }}
            QFrame#controlGroup {{
                border: 1px solid {colors['border']};
                border-radius: 6px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface_variant']}, stop: 1 {colors['surface']});
                padding: 2px;
                margin: 1px;
            }}
            QToolButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface_variant']}, stop: 1 {colors['surface']});
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                margin: 1px;
                color: {colors['text_primary']};
                font-size: 14px;
                font-weight: 600;
                min-width: 70px;
                min-height: 28px;
            }}
            QToolButton#textButton {{
                min-width: 90px;
                padding: 4px 10px;
                font-size: 15px;
                font-weight: 700;
            }}
            QToolButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['hover']}, stop: 1 {colors['surface_variant']});
                border-color: {colors['primary']};
                color: {colors['text_primary']};
            }}
            QToolButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface']}, stop: 1 {colors['surface_variant']});
                border-color: {colors['primary']};
            }}
            QToolButton:checked {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['primary_variant']}, stop: 1 {colors['primary']});
                border-color: {colors['primary_variant']};
                font-weight: bold;
                color: {colors['text_primary']};
            }}
            QLabel#countLabel {{
                color: {colors['text_primary']};
                font-size: 14px;
                font-weight: bold;
                min-width: 30px;
                text-align: center;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface']}, stop: 1 {colors['surface_variant']});
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QLabel#groupLabel {{
                color: {colors['text_secondary']};
                font-size: 14px;
                font-weight: 700;
                margin: 0px 4px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }}
            QComboBox {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface_variant']}, stop: 1 {colors['surface']});
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text_primary']};
                font-size: 14px;
                font-weight: 700;
                min-width: 100px;
                min-height: 28px;
            }}
            QComboBox:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['hover']}, stop: 1 {colors['surface_variant']});
                border-color: {colors['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-left: 1px solid {colors['border']};
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['text_primary']};
                margin-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                selection-background-color: {colors['primary']};
                selection-color: {colors['text_primary']};
                color: {colors['text_primary']};
                font-size: 16px;
                font-weight: 600;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
                padding: 8px 12px;
                border: none;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {colors['primary']};
                color: {colors['text_primary']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {colors['primary']};
                color: {colors['text_primary']};
            }}
            QSpinBox {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface_variant']}, stop: 1 {colors['surface']});
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 6px;
                color: {colors['text_primary']};
                font-size: 14px;
                font-weight: 700;
                min-width: 50px;
                min-height: 28px;
            }}
            QSpinBox:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['hover']}, stop: 1 {colors['surface_variant']});
                border-color: {colors['primary']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface_variant']}, stop: 1 {colors['surface']});
                border: 1px solid {colors['border']};
                width: 20px;
                height: 14px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: {colors['primary']};
            }}
            QSpinBox::up-arrow {{
                image: url(icons/arrow-up.svg);
                width: 12px;
                height: 12px;
            }}
            QSpinBox::down-arrow {{
                image: url(icons/arrow-down.svg);
                width: 12px;
                height: 12px;
            }}
        """)

    def _create_settings_control(self):
        """Create the settings panel toggle button."""
        self.settings_btn = QToolButton()
        self.settings_btn.setObjectName("textButton")
        self.settings_btn.setText("⚙️ General")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setChecked(False)
        self.settings_btn.setToolTip("Toggle general settings panel")
        self.settings_btn.clicked.connect(self.settings_toggled.emit)
        self.toolbar.addWidget(self.settings_btn)

        # Add the new Graph Settings button
        self.graph_settings_btn = QToolButton()
        self.graph_settings_btn.setObjectName("textButton")
        self.graph_settings_btn.setText("📊 Graph Settings")
        self.graph_settings_btn.setCheckable(True)
        self.graph_settings_btn.setChecked(False)
        self.graph_settings_btn.setToolTip("Toggle graph settings panel")
        self.graph_settings_btn.clicked.connect(self.graph_settings_toggled.emit)
        self.toolbar.addWidget(self.graph_settings_btn)

    def _create_cursor_controls(self):
        """Create a combo box for cursor mode selection."""
        cursor_label = QLabel("🎯 Cursor Mode:")
        cursor_label.setObjectName("groupLabel")
        self.toolbar.addWidget(cursor_label)

        self.cursor_combo = QComboBox()
        self.cursor_combo.addItems(["❌ None", "⚡ Dual Cursors"])
        self.cursor_combo.setCurrentText("⚡ Dual Cursors")
        self.cursor_combo.setToolTip("Select cursor mode for precise data analysis and measurements")
        self.toolbar.addWidget(self.cursor_combo)


    def _add_control_group(self, label: str):
        """Helper to create a styled group for +/- controls."""
        frame = QFrame()
        frame.setObjectName("controlGroup")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)
        
        group_label = QLabel(label)
        group_label.setObjectName("groupLabel")
        layout.addWidget(group_label)
        
        count_label = QLabel("1")
        count_label.setObjectName("countLabel")
        layout.addWidget(count_label)
        
        decrease_btn = QToolButton()
        decrease_btn.setText("➖")
        decrease_btn.setToolTip(f"Decrease {label.lower()}")
        layout.addWidget(decrease_btn)
        
        increase_btn = QToolButton()
        increase_btn.setText("➕")
        increase_btn.setToolTip(f"Increase {label.lower()}")
        layout.addWidget(increase_btn)
        
        self.toolbar.addWidget(frame)
        return count_label, decrease_btn, increase_btn

    def _create_tab_controls(self):
        """Create tab count controls."""
        self.tab_count_label, self.tab_decrease_btn, self.tab_increase_btn = self._add_control_group("📑 Tabs:")
        self.tab_decrease_btn.setToolTip("Remove last tab")
        self.tab_increase_btn.setToolTip("Add new tab")

    def _create_graph_controls(self):
        """Create graph count controls for the active tab."""
        self.graph_count_label, self.graph_decrease_btn, self.graph_increase_btn = self._add_control_group("📈 Graphs:")
        self.graph_decrease_btn.setToolTip("Decrease graph count in active tab")
        self.graph_increase_btn.setToolTip("Increase graph count in active tab")



    def _setup_connections(self):
        """Connect signals and slots for toolbar widgets."""
        # Connect cursor mode combo box
        self.cursor_combo.currentTextChanged.connect(self._on_cursor_mode_changed)
        
        # Connect graph controls
        self.graph_count_spinbox.valueChanged.connect(self.graph_count_changed.emit)

    def _on_cursor_mode_changed(self, mode_text: str):
        """Handle cursor mode changes from the combo box."""
        # Parse the mode text to extract the actual mode
        if "none" in mode_text.lower():
            mode = "none"
        elif "dual" in mode_text.lower():
            mode = "dual"
        else:
            mode = "none"  # fallback
            
        logger.debug(f"Cursor mode changed from '{mode_text}' to '{mode}'")
        self.cursor_mode_changed.emit(mode)
        
    def get_toolbar(self) -> QToolBar:
        """Get the configured toolbar."""
        return self.toolbar

    def set_graph_count(self, count: int):
        self.graph_count_spinbox.setValue(count)

    def set_tab_count(self, count: int):
        """Set the value of the tab count spinbox."""
        pass # This is now deprecated

    def update_theme(self):
        """Update toolbar styling when theme changes."""
        self._apply_theme_styling()
