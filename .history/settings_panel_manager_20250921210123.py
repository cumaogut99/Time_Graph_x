"""
Settings Panel Manager for Time Graph Widget

Manages the settings panel interface including:
- Graph display settings
- Analysis parameters
- Export options
- Theme settings
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGroupBox, QComboBox, QListWidget, QLineEdit, QCheckBox, QRadioButton,
    QButtonGroup, QPushButton, QListWidgetItem, QSpinBox, QSlider, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal as Signal, QObject
from PyQt5.QtGui import QFont

if TYPE_CHECKING:
    from .time_graph_widget import TimeGraphWidget

logger = logging.getLogger(__name__)

class SettingsPanelManager(QObject):
    """Manages the settings panel interface for the Time Graph Widget."""
    
    # Signals
    theme_changed = Signal(str)
    export_format_changed = Signal(str)
    
    def __init__(self, parent_widget: "TimeGraphWidget"):
        super().__init__()
        self.parent = parent_widget
        self.settings_panel = None
        
        self._setup_settings_panel()
    
    def _setup_settings_panel(self):
        """Create the main settings panel."""
        self.settings_panel = QFrame()
        self.settings_panel.setMinimumWidth(280)
        self.settings_panel.setMaximumWidth(350)
        # Apply theme-based styling - will be updated dynamically
        self._apply_theme_styling()
        
        # Main layout in a scroll area for scalability
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        container_widget = QWidget()
        main_layout = QVBoxLayout(container_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create settings sections
        self._create_display_settings(main_layout)
        self._create_export_settings(main_layout)
        
        main_layout.addStretch()
        
        scroll_area.setWidget(container_widget)
        
        # Set the scroll area as the main layout for the panel
        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(0,0,0,0)
        panel_layout.addWidget(scroll_area)
    
    def _create_display_settings(self, parent_layout):
        """Create display settings section."""
        group = QGroupBox("📊 Display")
        layout = QFormLayout(group)
        layout.setSpacing(8)
        layout.setLabelAlignment(Qt.AlignLeft)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Space"])
        self.theme_combo.setCurrentText("Space")  # Space is default
        self.theme_combo.currentTextChanged.connect(self.theme_changed.emit)
        layout.addRow("Theme:", self.theme_combo)

        parent_layout.addWidget(group)

    # Cursor and Performance settings removed - functionality moved to Graph Settings panel
    
    def _create_export_settings(self, parent_layout):
        """Create export settings section."""
        # Plot Export Section
        plot_group = QGroupBox("📈 Plot Export")
        plot_layout = QFormLayout(plot_group)
        plot_layout.setSpacing(8)
        
        self.plot_format_combo = QComboBox()
        self.plot_format_combo.addItems(["PNG", "PDF"])  # SVG removed
        self.plot_format_combo.setCurrentText("PNG")
        self.plot_format_combo.currentTextChanged.connect(self.export_format_changed.emit)
        plot_layout.addRow("Format:", self.plot_format_combo)
        
        export_plot_btn = QPushButton("Export Plot")
        export_plot_btn.clicked.connect(self._export_plot)
        plot_layout.addRow(export_plot_btn)
        
        parent_layout.addWidget(plot_group)
        
        # Data Export Section
        data_group = QGroupBox("📊 Data Export")
        data_layout = QFormLayout(data_group)
        data_layout.setSpacing(8)
        
        # Info label for cursor range
        cursor_info_label = QLabel("Exports data between two cursors")
        cursor_info_label.setStyleSheet("font-style: italic; color: #888888;")
        data_layout.addRow(cursor_info_label)
        
        export_data_btn = QPushButton("Export CSV Data")
        export_data_btn.clicked.connect(self._export_data)
        data_layout.addRow(export_data_btn)
        
        parent_layout.addWidget(data_group)
    
    def _export_plot(self):
        """Export plot to file."""
        logger.info("Export plot requested")
        # TODO: Implement plot export
    
    def _export_data(self):
        """Export data to file."""
        logger.info("Export data requested")
        # TODO: Implement data export
    
    def get_settings_panel(self) -> QWidget:
        """Get the settings panel widget."""
        return self.settings_panel
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update settings from external source."""
        if 'theme' in settings:
            self.theme_combo.setCurrentText(settings['theme'])
        
        if 'export_format' in settings:
            self.export_format_combo.setCurrentText(settings['export_format'])
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings values."""
        return {
            'theme': self.theme_combo.currentText(),
            'export_format': self.export_format_combo.currentText()
        }
    
    def _apply_theme_styling(self):
        """Apply current theme styling to the settings panel."""
        # Get theme colors from parent's theme manager
        if hasattr(self.parent, 'theme_manager'):
            theme_colors = self.parent.theme_manager.get_theme_colors()
        else:
            # Fallback to space theme colors
            theme_colors = {
                'background': '#1a2332',
                'surface': '#2d4a66',
                'surface_variant': '#3a5f7a',
                'primary': '#4a90e2',
                'text_primary': '#e6f3ff',
                'text_secondary': '#ffffff',
                'border': '#4a90e2'
            }
        
        self.settings_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_colors['surface']};
                border: 1px solid {theme_colors['border']};
                border-radius: 8px;
            }}
            QGroupBox {{
                color: {theme_colors['text_primary']};
                font-weight: bold;
                font-size: 11px;
                border: 1px solid {theme_colors['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
                background-color: {theme_colors['surface_variant']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme_colors['primary']};
            }}
            QLabel {{
                color: {theme_colors['text_secondary']};
                font-size: 10px;
            }}
            QCheckBox, QRadioButton {{
                color: {theme_colors['text_secondary']};
                font-size: 10px;
                spacing: 5px;
            }}
            QComboBox, QSpinBox, QLineEdit {{
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 4px;
                background-color: {theme_colors['background']};
                color: {theme_colors['text_primary']};
                font-size: 10px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QPushButton {{
                background-color: {theme_colors['primary']};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme_colors.get('hover', theme_colors['primary'])};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors.get('selected', theme_colors['primary'])};
            }}
        """)
    
    def update_theme(self):
        """Update the panel styling when theme changes."""
        self._apply_theme_styling()
