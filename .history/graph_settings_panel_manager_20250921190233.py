"""
Graph Settings Panel Manager for Time Graph Widget
"""

import logging
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QScrollArea,
    QGroupBox, QFormLayout, QLabel, QPushButton, QCheckBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal as Signal

if TYPE_CHECKING:
    from .time_graph_widget import TimeGraphWidget

logger = logging.getLogger(__name__)

class GraphSettingsPanelManager(QObject):
    """Manages the graph settings panel interface."""
    
    # Per-graph signals (for right-click context menu)
    normalization_toggled = Signal(int, bool) # graph_index, is_checked
    view_reset_requested = Signal(int) # graph_index
    grid_visibility_changed = Signal(int, bool) # graph_index, is_visible
    autoscale_changed = Signal(int, bool) # graph_index, is_enabled
    
    # Global signals (for panel settings applied to all graphs)
    global_normalization_toggled = Signal(bool) # is_checked
    global_view_reset_requested = Signal() # no args
    global_grid_visibility_changed = Signal(bool) # is_visible
    global_autoscale_changed = Signal(bool) # is_enabled

    def __init__(self, parent_widget: "TimeGraphWidget"):
        super().__init__()
        self.parent = parent_widget
        self.settings_panel = None
        
        # Store global settings state
        self.global_settings = {
            'normalize': False,
            'show_grid': True,
            'autoscale': True
        }
        
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
        """)
        
        # Create main container layout
        container_widget = QWidget()
        main_layout = QVBoxLayout(container_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create global settings group
        self._create_global_settings_group(main_layout)
        
        main_layout.addStretch()
        
        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(container_widget)

    def _create_global_settings_group(self, parent_layout):
        """Create global settings group that applies to all graphs."""
        group = QGroupBox("🌐 Global Graph Settings")
        
        # Apply theme-appropriate styling
        self._apply_group_styling(group)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)
        
        # Normalization and Reset row
        control_row1 = QHBoxLayout()
        
        self.global_normalize_check = QCheckBox("Normalize All Graphs")
        self.global_normalize_check.setChecked(self.global_settings['normalize'])
        self.global_normalize_check.toggled.connect(self._on_global_normalize_toggled)
        
        self.global_reset_button = QPushButton("Reset All Views")
        self.global_reset_button.clicked.connect(self._on_global_reset_clicked)
        
        control_row1.addWidget(self.global_normalize_check)
        control_row1.addWidget(self.global_reset_button)
        layout.addLayout(control_row1)
        
        # Grid and Autoscale row
        control_row2 = QHBoxLayout()
        
        self.global_grid_check = QCheckBox("Show Grid (All)")
        self.global_grid_check.setChecked(self.global_settings['show_grid'])
        self.global_grid_check.toggled.connect(self._on_global_grid_toggled)
        
        self.global_autoscale_check = QCheckBox("Auto-scale Y-Axis (All)")
        self.global_autoscale_check.setChecked(self.global_settings['autoscale'])
        self.global_autoscale_check.toggled.connect(self._on_global_autoscale_toggled)
        
        control_row2.addWidget(self.global_grid_check)
        control_row2.addWidget(self.global_autoscale_check)
        layout.addLayout(control_row2)
        
        # Info label
        info_label = QLabel("💡 These settings apply to all graphs simultaneously")
        info_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-style: italic;
                font-size: 9px;
                padding: 5px;
            }
        """)
        layout.addWidget(info_label)
        
        parent_layout.addWidget(group)

    def _apply_group_styling(self, group):
        """Apply theme-appropriate styling to a group box."""
        # Get theme colors from parent or use fallback
        if hasattr(self.parent, 'theme_manager'):
            theme_colors = self.parent.theme_manager.get_theme_colors()
        else:
            # Fallback to space theme colors
            theme_colors = {
                'text_primary': '#e6f3ff',
                'text_secondary': '#ffffff',
                'surface': '#2d4a66',
                'surface_variant': '#3a5f7a',
                'border': '#4a90e2',
                'primary': '#4a90e2'
            }
        
        # Determine if this is a light theme
        is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
        
        if is_light_theme:
            title_bg_color = 'rgba(255, 255, 255, 0.8)'
        else:
            title_bg_color = 'rgba(0, 0, 0, 0.3)'
        
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {theme_colors.get('border', '#4a90e2')};
                border-radius: 12px;
                margin-top: 10px;
                padding: 10px;
                background-color: {theme_colors.get('surface', '#2d4a66')};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: {title_bg_color};
                border-radius: 6px;
                color: {theme_colors.get('primary', '#4a90e2')};
            }}
            QCheckBox {{
                color: {theme_colors.get('text_primary', '#e6f3ff')};
                font-size: 12px;
                font-weight: 500;
                spacing: 8px;
            }}
            QPushButton {{
                background-color: {theme_colors.get('primary', '#4a90e2')};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme_colors.get('hover', theme_colors.get('primary', '#4a90e2'))};
            }}
        """)

    def _on_global_normalize_toggled(self, checked):
        """Handle global normalization toggle."""
        self.global_settings['normalize'] = checked
        self.global_normalization_toggled.emit(checked)
        logger.info(f"Global normalization {'enabled' if checked else 'disabled'}")

    def _on_global_reset_clicked(self):
        """Handle global reset button click."""
        self.global_view_reset_requested.emit()
        logger.info("Global view reset requested")

    def _on_global_grid_toggled(self, checked):
        """Handle global grid visibility toggle."""
        self.global_settings['show_grid'] = checked
        self.global_grid_visibility_changed.emit(checked)
        logger.info(f"Global grid {'shown' if checked else 'hidden'}")

    def _on_global_autoscale_toggled(self, checked):
        """Handle global autoscale toggle."""
        self.global_settings['autoscale'] = checked
        self.global_autoscale_changed.emit(checked)
        logger.info(f"Global autoscale {'enabled' if checked else 'disabled'}")

    def rebuild_controls(self, graph_count: int):
        """No longer needed - using global controls only."""
        # Global controls don't need rebuilding based on graph count
        logger.info(f"Graph count changed to {graph_count}, but using global controls")

    def update_theme(self):
        """Update the panel styling when theme changes."""
        # Re-apply styling to the global settings group
        if hasattr(self, 'global_normalize_check'):
            # Find the parent group box and re-apply styling
            group = self.global_normalize_check.parent()
            while group and not isinstance(group, QGroupBox):
                group = group.parent()
            if group:
                self._apply_group_styling(group)

    def get_settings_panel(self) -> QWidget:
        """Get the settings panel widget."""
        return self.settings_panel

    def sync_with_current_settings(self, graph_settings: dict, active_tab_index: int):
        """Synchronize checkbox states with current graph settings."""
        if active_tab_index < 0 or active_tab_index not in graph_settings:
            return
            
        tab_settings = graph_settings[active_tab_index]
        
        # Iterate through all graph control groups
        for i in range(self.dynamic_controls_layout.count()):
            item = self.dynamic_controls_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QGroupBox):
                group = item.widget()
                graph_index = i  # Graph index matches the layout position
                
                if graph_index in tab_settings:
                    settings = tab_settings[graph_index]
                    
                    # Find and update checkboxes in this group
                    self._update_checkboxes_in_group(group, settings)

    def _update_checkboxes_in_group(self, group: QGroupBox, settings: dict):
        """Update checkbox states in a specific graph group."""
        # Find all checkboxes in the group
        checkboxes = group.findChildren(QCheckBox)
        
        for checkbox in checkboxes:
            text = checkbox.text()
            
            # Update checkbox states based on saved settings
            if "Show Grid" in text:
                show_grid = settings.get('show_grid', True)
                checkbox.blockSignals(True)  # Prevent triggering signals during sync
                checkbox.setChecked(show_grid)
                checkbox.blockSignals(False)
                
            elif "Auto-scale Y-Axis" in text:
                autoscale = settings.get('autoscale', True)
                checkbox.blockSignals(True)
                checkbox.setChecked(autoscale)
                checkbox.blockSignals(False)
                
            elif "Normalize" in text:
                normalize = settings.get('normalize', False)
                checkbox.blockSignals(True)
                checkbox.setChecked(normalize)
                checkbox.blockSignals(False)