"""
Statistics Settings Panel Manager for Time Graph Widget

Manages the settings panel for statistical calculations and display.
"""

import logging
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QScrollArea,
    QGroupBox, QFormLayout, QLabel, QCheckBox,
    QRadioButton, QDoubleSpinBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal as Signal, QObject

if TYPE_CHECKING:
    from .time_graph_widget import TimeGraphWidget

logger = logging.getLogger(__name__)

class StatisticsSettingsPanelManager(QObject):
    """Manages the statistics settings panel interface."""
    
    # Emits a set of the names of the visible columns
    visible_columns_changed = Signal(set)
    # Emits duty cycle threshold settings (threshold_mode: str, threshold_value: float)
    duty_cycle_threshold_changed = Signal(str, float)
    
    def __init__(self, parent_widget: "TimeGraphWidget"):
        super().__init__()
        self.parent = parent_widget
        self.settings_panel = None
        self.column_checkboxes = {}
        self.current_cursor_mode = "none"  # Track cursor mode
        
        self._setup_settings_panel()
        self._connect_signals()
    
    def _setup_settings_panel(self):
        """Create the main settings panel."""
        self.settings_panel = QFrame()
        self.settings_panel.setMinimumWidth(280)
        self.settings_panel.setMaximumWidth(350)
        # Apply similar styling to the general settings panel
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
        """)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        container_widget = QWidget()
        main_layout = QVBoxLayout(container_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create the settings sections
        self._create_visibility_settings(main_layout)
        
        main_layout.addStretch()
        
        scroll_area.setWidget(container_widget)
        
        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(0,0,0,0)
        panel_layout.addWidget(scroll_area)

    def _create_visibility_settings(self, parent_layout):
        """Create a group for toggling statistic column visibility."""
        group = QGroupBox("📊 Visible Columns")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Define the available statistic columns (display_name, key_name)
        stats_options = [
            ("Min", "min"),
            ("Mean", "mean"),
            ("Max", "max"),
            ("RMS (C1)", "rms"),
            ("Std Dev", "std"),
            ("Duty Cycle", "duty_cycle")
        ]
        
        for display_name, key in stats_options:
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(True) # Default to visible
            layout.addWidget(checkbox)
            self.column_checkboxes[key] = checkbox

        parent_layout.addWidget(group)

    def _connect_signals(self):
        """Connect checkbox signals to the handler."""
        for checkbox in self.column_checkboxes.values():
            checkbox.stateChanged.connect(self._on_visibility_changed)

    def _on_visibility_changed(self):
        """Emit the set of currently visible columns."""
        visible_set = {key for key, cb in self.column_checkboxes.items() if cb.isChecked()}
        self.visible_columns_changed.emit(visible_set)
        logger.info(f"Visible statistics columns changed: {visible_set}")

    def get_settings_panel(self) -> QWidget:
        """Get the settings panel widget."""
        return self.settings_panel

    def get_visible_columns(self) -> set:
        """Return the set of currently visible columns."""
        visible_set = {key for key, cb in self.column_checkboxes.items() if cb.isChecked()}
        
        # Remove RMS if cursor mode is not dual
        if self.current_cursor_mode != 'dual':
            visible_set.discard('rms')
            
        return visible_set
    
    def set_cursor_mode(self, mode: str):
        """Update cursor mode and enable/disable RMS checkbox accordingly."""
        self.current_cursor_mode = mode
        
        # Enable/disable RMS checkbox based on cursor mode
        if 'rms' in self.column_checkboxes:
            rms_checkbox = self.column_checkboxes['rms']
            if mode == 'dual':
                rms_checkbox.setEnabled(True)
                rms_checkbox.setText("RMS (C1)")
            else:
                rms_checkbox.setEnabled(False)
                rms_checkbox.setChecked(False)  # Uncheck when disabled
                rms_checkbox.setText("RMS (requires cursors)")
        
        # Emit updated visible columns
        self._on_visibility_changed()
