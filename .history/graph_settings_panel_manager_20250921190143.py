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

    def rebuild_controls(self, graph_count: int):
        """Clears and rebuilds the controls for the given number of graphs."""
        # Clear existing widgets from the layout
        while self.dynamic_controls_layout.count():
            child = self.dynamic_controls_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Create a new group for each graph
        for i in range(graph_count):
            group = QGroupBox(f"⚙️ Graph {i+1} Controls")
            
            # Apply modern styling similar to statistics panel
            group.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 10px;
                    margin-top: 1px;
                    padding: 3px;
                    background-color: rgba(255, 255, 255, 0.05);
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 4px 8px;
                    background-color: rgba(0, 0, 0, 0.4);
                    border-radius: 5px;
                    color: #5d9cec;
                }}
            """)
            
            # Create scroll area for this graph section
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setFrameShape(QFrame.NoFrame)
            
            # Create container widget for controls
            controls_container = QWidget()
            controls_layout = QVBoxLayout(controls_container)
            controls_layout.setContentsMargins(5, 5, 5, 5)
            controls_layout.setSpacing(8)
            
            # --- Normalization and Reset ---
            control_layout = QHBoxLayout()
            normalize_check = QCheckBox("Normalize")
            reset_button = QPushButton("Reset View")
            control_layout.addWidget(normalize_check)
            control_layout.addWidget(reset_button)
            controls_layout.addLayout(control_layout)

            # --- Grid and Autoscale ---
            axis_layout = QHBoxLayout()
            grid_check = QCheckBox("Show Grid")
            grid_check.setChecked(True) # Default to on
            autoscale_check = QCheckBox("Auto-scale Y-Axis")
            autoscale_check.setChecked(True) # Default to on
            axis_layout.addWidget(grid_check)
            axis_layout.addWidget(autoscale_check)
            controls_layout.addLayout(axis_layout)
            
            # Add stretch to push controls to top
            controls_layout.addStretch()
            
            scroll_area.setWidget(controls_container)
            
            # Main layout for the graph section
            section_layout = QVBoxLayout(group)
            section_layout.setContentsMargins(2, 15, 2, 2)
            section_layout.addWidget(scroll_area)

            # Connect signals with the graph index
            normalize_check.toggled.connect(
                lambda checked, index=i: self.normalization_toggled.emit(index, checked)
            )
            reset_button.clicked.connect(
                lambda _, index=i: self.view_reset_requested.emit(index)
            )
            grid_check.toggled.connect(
                lambda checked, index=i: self.grid_visibility_changed.emit(index, checked)
            )
            autoscale_check.toggled.connect(
                lambda checked, index=i: self.autoscale_changed.emit(index, checked)
            )

            self.dynamic_controls_layout.addWidget(group)
        
        # Apply equal height distribution after all groups are created
        self._equalize_graph_heights(graph_count)
        
        self.dynamic_controls_layout.addStretch()

    def _equalize_graph_heights(self, graph_count: int):
        """Apply equal height to all graph control groups."""
        if graph_count <= 0:
            return
            
        # Get the main panel height to calculate available height
        if hasattr(self.settings_panel, 'height'):
            available_height = self.settings_panel.height()
        else:
            available_height = 600  # Fallback height
            
        # Account for margins and spacing
        margins_and_spacing = 20 + (3 * (graph_count - 1))  # margins + spacing between sections
        usable_height = available_height - margins_and_spacing
        
        # Calculate height per graph section to fill the entire panel
        section_height = max(120, usable_height // graph_count)
        
        # Apply equal height to all graph control groups
        for i in range(self.dynamic_controls_layout.count()):
            item = self.dynamic_controls_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QGroupBox):
                group = item.widget()
                group.setMinimumHeight(section_height)
                group.setMaximumHeight(section_height)
                
        logger.info(f"Applied equal heights ({section_height}px) to {graph_count} graph control groups")

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