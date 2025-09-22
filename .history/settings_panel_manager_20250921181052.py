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
        self.settings_panel.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 8px;
            }
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                font-size: 11px;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
                background-color: #383838;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #5d9cec;
            }
            QLabel {
                color: #d0d0d0;
                font-size: 10px;
            }
            QCheckBox, QRadioButton {
                color: #d0d0d0;
                font-size: 10px;
                spacing: 5px;
            }
            QComboBox, QSpinBox, QLineEdit {
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                background-color: #2c2c2c;
                color: #e0e0e0;
                font-size: 10px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QPushButton {
                background-color: #5d9cec;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a8cdb;
            }
            QPushButton:pressed {
                background-color: #3a7acb;
            }
        """)
        
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
        self._create_cursor_settings(main_layout)
        self._create_performance_settings(main_layout)
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

    def _create_cursor_settings(self, parent_layout):
        """Create placeholder for cursor settings."""
        group = QGroupBox("🖱️ Cursors")
        layout = QFormLayout(group)
        layout.setSpacing(8)

        snap_checkbox = QCheckBox("Snap to data points")
        snap_checkbox.setEnabled(False)
        layout.addRow(snap_checkbox)

        tooltip_checkbox = QCheckBox("Show tooltips")
        tooltip_checkbox.setEnabled(False)
        layout.addRow(tooltip_checkbox)
        
        parent_layout.addWidget(group)

    def _create_performance_settings(self, parent_layout):
        """Create placeholder for performance settings."""
        group = QGroupBox("🚀 Performance")
        layout = QFormLayout(group)
        layout.setSpacing(8)

        decimation_checkbox = QCheckBox("Enable Data Decimation")
        decimation_checkbox.setEnabled(False)
        decimation_checkbox.setChecked(True)
        layout.addRow(decimation_checkbox)
        
        max_points_spinbox = QSpinBox()
        max_points_spinbox.setRange(1000, 1000000)
        max_points_spinbox.setValue(50000)
        max_points_spinbox.setSingleStep(1000)
        max_points_spinbox.setEnabled(False)
        layout.addRow("Max Points to Display:", max_points_spinbox)
        
        parent_layout.addWidget(group)
    
    def _create_export_settings(self, parent_layout):
        """Create export settings section."""
        group = QGroupBox("📤 Export")
        layout = QFormLayout(group)
        layout.setSpacing(8)
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["PNG", "PDF", "SVG", "CSV"])
        self.export_format_combo.setCurrentText("PNG")
        self.export_format_combo.currentTextChanged.connect(self.export_format_changed.emit)
        layout.addRow("Format:", self.export_format_combo)
        
        button_layout = QHBoxLayout()
        export_plot_btn = QPushButton("Export Plot")
        export_plot_btn.clicked.connect(self._export_plot)
        button_layout.addWidget(export_plot_btn)
        
        export_data_btn = QPushButton("Export Data")
        export_data_btn.clicked.connect(self._export_data)
        button_layout.addWidget(export_data_btn)
        
        layout.addRow(button_layout)
        
        parent_layout.addWidget(group)
    
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
