"""
Advanced Graph Settings Dialog for Time Graph Widget
Modern, professional interface with comprehensive configuration options
"""

import logging
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QDialogButtonBox,
    QListWidgetItem, QLabel, QFrame, QLineEdit, QWidget, QSplitter,
    QPushButton, QScrollArea, QGroupBox, QFormLayout, QSpinBox,
    QDoubleSpinBox, QCheckBox, QComboBox, QSlider,
    QColorDialog, QSizePolicy, QStackedWidget, QButtonGroup, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QPixmap

logger = logging.getLogger(__name__)

class ModernSidebarButton(QPushButton):
    """Modern sidebar navigation button with hover effects and selection state."""
    
    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setText(f"{icon} {text}" if icon else text)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(38)
        self.setMaximumHeight(38)
        
        # Modern space theme styling
        self.setStyleSheet("""
            ModernSidebarButton {
                text-align: left;
                padding: 10px 16px;
                border: 1px solid rgba(74, 144, 226, 0.2);
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.1), stop:1 transparent);
                color: #e6f3ff;
                font-size: 13px;
                font-weight: 500;
            }
            ModernSidebarButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.3), stop:1 rgba(74, 144, 226, 0.1));
                color: #ffffff;
                border-color: rgba(74, 144, 226, 0.5);
            }
            ModernSidebarButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #5ba0f2);
                color: #ffffff;
                font-weight: 600;
                border-color: #4a90e2;
            }
            ModernSidebarButton:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #6bb0ff);
            }
        """)

class ParametersPanel(QWidget):
    """Parameters selection panel - enhanced version of existing signal selection."""
    
    signals_changed = pyqtSignal(list)  # List of selected signals
    
    def __init__(self, all_signals: List[str], visible_signals: List[str], parent=None):
        super().__init__(parent)
        self.all_signals = sorted(all_signals)
        self.visible_signals = set(visible_signals)
        
        self._setup_ui()
        self._populate_signals()
        
    def _setup_ui(self):
        """Setup the parameters panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Signal Parameters")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #e6f3ff;
                margin-bottom: 8px;
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 transparent);
                border-radius: 6px;
                border: 1px solid rgba(74, 144, 226, 0.3);
            }
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Select which signals to display on this graph. Use the search bar to quickly find specific signals.")
        desc.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 12px;
                margin-bottom: 15px;
            }
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Search and controls section
        controls_layout = QHBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search signals...")
        self.search_bar.textChanged.connect(self._filter_signals)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #3a3a3a;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                background-color: #404040;
            }
        """)
        controls_layout.addWidget(self.search_bar, 3)
        
        # Quick action buttons
        self.select_all_btn = QPushButton("Select All")
        self.select_none_btn = QPushButton("Select None")
        
        for btn in [self.select_all_btn, self.select_none_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 15px;
                    border: 1px solid #4a90e2;
                    border-radius: 6px;
                    background-color: transparent;
                    color: #4a90e2;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #4a90e2;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #3a7bc8;
                }
            """)
        
        self.select_all_btn.clicked.connect(self._select_all)
        self.select_none_btn.clicked.connect(self._select_none)
        
        controls_layout.addWidget(self.select_all_btn)
        controls_layout.addWidget(self.select_none_btn)
        
        layout.addLayout(controls_layout)
        
        # Signal list
        self.signal_list = QListWidget()
        self.signal_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
                color: #e0e0e0;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QListWidget::item:selected:hover {
                background-color: #5ba0f2;
            }
        """)
        layout.addWidget(self.signal_list)
        
        # Statistics
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.stats_label)
        
    def _populate_signals(self):
        """Populate the signal list with checkboxes."""
        # Get real signals from parent if available
        parent_dialog = self.parent()
        logger.debug(f"ParametersPanel parent: {parent_dialog}")
        
        if parent_dialog and hasattr(parent_dialog, 'parent') and parent_dialog.parent():
            parent_widget = parent_dialog.parent()
            logger.debug(f"ParametersPanel grandparent (TimeGraphWidget): {parent_widget}")
            logger.debug(f"Grandparent has signal_processor: {hasattr(parent_widget, 'signal_processor')}")
            
            if hasattr(parent_widget, 'signal_processor') and parent_widget.signal_processor:
                try:
                    all_signals_data = parent_widget.signal_processor.get_all_signals()
                    self.all_signals = sorted(list(all_signals_data.keys()))
                    logger.info(f"ParametersPanel: Loaded {len(self.all_signals)} real signals from signal_processor")
                except Exception as e:
                    logger.warning(f"ParametersPanel: Error accessing signal_processor: {e}")
        
        for signal_name in self.all_signals:
            item = QListWidgetItem(signal_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if signal_name in self.visible_signals else Qt.Unchecked)
            self.signal_list.addItem(item)
            
        self._update_stats()
        
        # Connect change signal
        self.signal_list.itemChanged.connect(self._on_item_changed)
        
    def _filter_signals(self, text: str):
        """Filter signals based on search text."""
        visible_count = 0
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            matches = text.lower() in item.text().lower()
            item.setHidden(not matches)
            if matches:
                visible_count += 1
                
        # Update stats for filtered view
        if text:
            self.stats_label.setText(f"Showing {visible_count} of {len(self.all_signals)} signals")
        else:
            self._update_stats()
            
    def _select_all(self):
        """Select all visible signals."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.Checked)
                
    def _select_none(self):
        """Deselect all visible signals."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.Unchecked)
                
    def _on_item_changed(self, item):
        """Handle item check state change."""
        self._update_stats()
        self.signals_changed.emit(self.get_selected_signals())
        
    def _update_stats(self):
        """Update statistics label."""
        selected_count = len(self.get_selected_signals())
        total_count = len(self.all_signals)
        self.stats_label.setText(f"Selected: {selected_count} / {total_count} signals")
        
    def get_selected_signals(self) -> List[str]:
        """Get list of selected signal names."""
        selected = []
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected

class ParameterFiltersPanel(QWidget):
    """Panel for configuring range filters."""
    
    range_filter_applied = pyqtSignal(dict)

    def __init__(self, graph_index: int, all_signals: List[str], parent=None):
        super().__init__(parent)
        self.graph_index = graph_index
        self.all_signals = all_signals if all_signals else []
        self.conditions = []
        self.condition_widgets = []
        
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self):
        """Setup the range filters panel UI with tabs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔍 Range Filters")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #e6f3ff;
                margin-bottom: 8px;
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 transparent);
                border-radius: 6px;
                border: 1px solid rgba(74, 144, 226, 0.3);
            }
        """)
        layout.addWidget(title)
        
        # Create range filter content directly
        self._create_range_filter_content(layout)
        
        # Apply/Reset buttons
        button_layout = QHBoxLayout()
        
        self.apply_filters_btn = QPushButton("Apply Filters")
        self.reset_filters_btn = QPushButton("Reset All")
        
        button_style = """
            QPushButton {
                padding: 8px 16px;
                border: 1px solid rgba(74, 144, 226, 0.5);
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 transparent);
                color: #e6f3ff;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.4), stop:1 rgba(74, 144, 226, 0.1));
                border-color: #4a90e2;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 rgba(74, 144, 226, 0.3));
            }
        """
        
        for btn in [self.apply_filters_btn, self.reset_filters_btn]:
            btn.setStyleSheet(button_style)
            
        # Connect button signals
        self.apply_filters_btn.clicked.connect(self._apply_range_filters)
        self.reset_filters_btn.clicked.connect(self._reset_range_filters)
            
        button_layout.addWidget(self.apply_filters_btn)
        button_layout.addWidget(self.reset_filters_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def _setup_connections(self):
        """Setup signal connections for the filters panel."""
        # Connect range filter applied signal to parent
        self.range_filter_applied.connect(self._handle_range_filter_applied)
        
    def _handle_range_filter_applied(self, filter_data: dict):
        """Handle the signal emitted by ParameterFiltersPanel when range filters are applied."""
        # This signal is emitted by ParameterFiltersPanel, which is a child of GraphAdvancedSettingsDialog.
        # The GraphAdvancedSettingsDialog will then emit this signal to its parent (TimeGraphWidget).
        # For now, we just log it.
        logger.debug(f"ParameterFiltersPanel range filters applied: {filter_data}")
        # You might want to update the parent widget's filter state here
        # self.parent().update_graph_filters(filter_data)
        
    def _get_message_box_style(self) -> str:
        """Gets a consistent stylesheet for QMessageBox to match the space theme."""
        return """
            QMessageBox {
                background-color: #2d344a; /* Dark blue background from theme */
                font-size: 14px;
            }
            QMessageBox QLabel { /* General label styling */
                color: #e0e0e0;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a536b, stop:1 #3a4258);
                color: #ffffff;
                border: 1px solid #5a647d;
                padding: 8px 16px;
                border-radius: 5px;
                min-width: 90px;
            }
            QMessageBox QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a647d, stop:1 #4a536b);
                border: 1px solid #7a849d;
            }
            QMessageBox QPushButton:pressed {
                background-color: #3a4258;
            }
        """

    def _apply_range_filters(self):
        """Gathers the filter conditions and emits a signal."""
        filter_data = self.get_range_filter_conditions()
        
        if not filter_data['conditions']:
            msg = QMessageBox(self)
            msg.setStyleSheet(self._get_message_box_style())
            msg.setIcon(QMessageBox.Warning)
            msg.setText("No filter conditions have been set.")
            msg.setWindowTitle("No Conditions")
            msg.exec_()
            return

        # Add graph index to filter data
        filter_data['graph_index'] = self.graph_index
        
        # Emit signal to parent widget for filter application
        self.range_filter_applied.emit(filter_data)
        
        print(f"[DEBUG] Applying range filters: {filter_data}")
        
        # Show a success message
        msg = QMessageBox(self)
        msg.setStyleSheet(self._get_message_box_style())
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Applied {len(filter_data['conditions'])} range condition(s) in {filter_data['mode']} mode to Graph {self.graph_index + 1}.")
        msg.setWindowTitle("Filters Applied")
        msg.exec_()
        
    def _reset_range_filters(self):
        """Resets all range filter conditions to their default state."""
        # Confirmation dialog
        msg = QMessageBox(self)
        msg.setStyleSheet(self._get_message_box_style())
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to reset all range conditions?")
        msg.setInformativeText("This action cannot be undone.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            # Clear all conditions except the first one
            while len(self.range_conditions) > 1:
                self._remove_range_condition()
                
            # Reset the first condition
            if self.range_conditions:
                condition = self.range_conditions[0]
                condition['param_search'].clear()
                condition['param_list'].clearSelection()
                condition['selected_param_label'].setText("Selected: None")
                condition['lower_enabled'].setChecked(True)
                condition['lower_operator'].setCurrentIndex(0)
                condition['lower_value'].setValue(0.0)
                condition['upper_enabled'].setChecked(True)
                condition['upper_operator'].setCurrentIndex(0)
                condition['upper_value'].setValue(100.0)
                
                # Show all parameters
                for i in range(condition['param_list'].count()):
                    condition['param_list'].item(i).setHidden(False)
                
            # Reset mode to segmented
            self.segmented_mode_rb.setChecked(True)
            print(f"[DEBUG] Range filters reset for graph {self.graph_index + 1}")
            msg = QMessageBox(self)
            msg.setStyleSheet(self._get_message_box_style())
            msg.setIcon(QMessageBox.Information)
            msg.setText("All range conditions reset for Graph {self.graph_index + 1}.")
            msg.setWindowTitle("Filters Reset")
            msg.exec_()
        else:
            print(f"[DEBUG] Range filters reset cancelled for graph {self.graph_index + 1}")

    def _create_range_filter_content(self, parent_layout):
        """Create the advanced value range filter content with integrated parameter and range selection."""
        
        
        # Scroll area for conditions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        # Container for dynamic range conditions
        self.conditions_container = QWidget()
        self.conditions_layout = QVBoxLayout(self.conditions_container)
        self.conditions_layout.setSpacing(8)
        
        self.range_conditions = []
        self._add_range_condition()  # Add first condition
        
        scroll.setWidget(self.conditions_container)
        parent_layout.addWidget(scroll)
        
        # Add/Remove buttons
        buttons_layout = QHBoxLayout()
        
        self.add_condition_btn = QPushButton("➕ Add Parameter Condition")
        self.remove_condition_btn = QPushButton("➖ Remove Last Condition")
        
        button_style = """
            QPushButton {
                padding: 8px 16px;
                border: 1px solid rgba(74, 144, 226, 0.5);
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 transparent);
                color: #e6f3ff;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.4), stop:1 rgba(74, 144, 226, 0.1));
                border-color: #4a90e2;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 rgba(74, 144, 226, 0.3));
            }
        """
        
        self.add_condition_btn.setStyleSheet(button_style)
        self.remove_condition_btn.setStyleSheet(button_style)
        
        self.add_condition_btn.clicked.connect(self._add_range_condition)
        self.remove_condition_btn.clicked.connect(self._remove_range_condition)
        
        buttons_layout.addWidget(self.add_condition_btn)
        buttons_layout.addWidget(self.remove_condition_btn)
        buttons_layout.addStretch()
        
        parent_layout.addLayout(buttons_layout)
        
        # Filter mode selection
        mode_group = QGroupBox("🔗 Display Mode")
        mode_group.setStyleSheet(self._get_group_style())
        mode_layout = QVBoxLayout(mode_group)
        
        self.segmented_mode_rb = QCheckBox("Segmented Display (Show matching time segments with gaps)")
        self.concatenated_mode_rb = QCheckBox("Concatenated Display (Apply global time filter to all graphs)")
        self.segmented_mode_rb.setChecked(True)  # Default to segmented
        
        # Make them mutually exclusive
        self.segmented_mode_rb.toggled.connect(lambda checked: self.concatenated_mode_rb.setChecked(not checked) if checked else None)
        self.concatenated_mode_rb.toggled.connect(lambda checked: self.segmented_mode_rb.setChecked(not checked) if checked else None)
        
        mode_layout.addWidget(self.segmented_mode_rb)
        mode_layout.addWidget(self.concatenated_mode_rb)
        
        parent_layout.addWidget(mode_group)
        
    def _add_range_condition(self):
        """Adds a new parameter condition box to the layout."""
        condition_index = len(self.range_conditions)
        
        # Create main condition group box
        condition_group = QGroupBox(f"📊 Condition {condition_index + 1}")
        condition_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid rgba(74, 144, 226, 0.4);
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                color: #e6f3ff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.08), stop:1 transparent);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: rgba(45, 74, 102, 0.8);
                color: #e6f3ff;
                border-radius: 4px;
            }
        """)
        
        condition_layout = QHBoxLayout(condition_group)  # Changed to horizontal layout
        condition_layout.setSpacing(15)
        
        # Left side - Parameter selection
        param_section = QVBoxLayout()
        param_section.setSpacing(8)
        
        param_title = QLabel("📋 Parameter")
        param_title.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-weight: bold;
                font-size: 12px;
                margin-bottom: 5px;
            }
        """)
        param_section.addWidget(param_title)
        
        # Parameter search
        param_search = QLineEdit()
        param_search.setPlaceholderText("🔍 Search parameters...")
        param_search.setMinimumWidth(180)
        param_search.setMaximumWidth(200)
        param_search.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.05), stop:1 transparent);
                color: #e6f3ff;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.1), stop:1 transparent);
            }
        """)
        param_section.addWidget(param_search)
        
        # Parameter list
        param_list = QListWidget()
        param_list.setMaximumHeight(100)
        param_list.setMinimumWidth(180)
        param_list.setMaximumWidth(200)
        param_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.05), stop:1 transparent);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 4px;
                color: #e6f3ff;
                padding: 2px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 3px 6px;
                border-radius: 2px;
                margin: 1px;
            }
            QListWidget::item:hover {
                background: rgba(74, 144, 226, 0.2);
            }
            QListWidget::item:selected {
                background: rgba(74, 144, 226, 0.4);
                color: #ffffff;
            }
        """)
        
        # Populate with real parameters from parent widget
        if self.all_signals:
            logger.info(f"Populating new condition with {len(self.all_signals)} signals.")
            for param in self.all_signals:
                param_list.addItem(param)
        else:
            # Fallback to sample parameters if no real data available
            logger.warning("No real signals available for new condition, using fallback sample parameters.")
            sample_params = ["Temperature_1", "Temperature_2", "Pressure_1", "Pressure_2", "Voltage_A", "Voltage_B", "Current_A", "Current_B", "Speed_Motor1", "Speed_Motor2", "Torque_Motor1", "Torque_Motor2", "Flow_Rate_1", "Flow_Rate_2"]
            for param in sample_params:
                param_list.addItem(param)
            
        param_section.addWidget(param_list)
        
        # Selected parameter display
        selected_param_label = QLabel("Selected: None")
        selected_param_label.setStyleSheet("""
            QLabel {
                color: rgba(230, 243, 255, 0.7);
                font-size: 10px;
                font-style: italic;
                padding: 2px;
            }
        """)
        param_section.addWidget(selected_param_label)
        
        condition_layout.addLayout(param_section)
        
        # Vertical separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("QFrame { color: rgba(74, 144, 226, 0.3); }")
        condition_layout.addWidget(separator)
        
        # Right side - Range conditions
        range_section = QVBoxLayout()
        range_section.setSpacing(8)
        
        range_title = QLabel("📊 Range Conditions")
        range_title.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-weight: bold;
                font-size: 12px;
                margin-bottom: 5px;
            }
        """)
        range_section.addWidget(range_title)
        
        # Lower bound row
        lower_row = QHBoxLayout()
        lower_row.setSpacing(6)
        
        lower_enabled = QCheckBox("Lower:")
        lower_enabled.setChecked(True)
        lower_enabled.setMinimumWidth(60)
        lower_enabled.setStyleSheet("font-size: 11px; font-weight: 500;")
        
        lower_operator = QComboBox()
        lower_operator.addItems([">", ">="])
        lower_operator.setMinimumWidth(45)
        lower_operator.setMaximumWidth(50)
        
        lower_value = QDoubleSpinBox()
        lower_value.setRange(-999999, 999999)
        lower_value.setDecimals(3)
        lower_value.setMinimumWidth(80)
        lower_value.setMaximumWidth(100)
        lower_value.setValue(0.0)
        
        lower_row.addWidget(lower_enabled)
        lower_row.addWidget(lower_operator)
        lower_row.addWidget(lower_value)
        lower_row.addStretch()
        
        range_section.addLayout(lower_row)
        
        # Upper bound row
        upper_row = QHBoxLayout()
        upper_row.setSpacing(6)
        
        upper_enabled = QCheckBox("Upper:")
        upper_enabled.setChecked(True)
        upper_enabled.setMinimumWidth(60)
        upper_enabled.setStyleSheet("font-size: 11px; font-weight: 500;")
        
        upper_operator = QComboBox()
        upper_operator.addItems(["<", "<="])
        upper_operator.setMinimumWidth(45)
        upper_operator.setMaximumWidth(50)
        
        upper_value = QDoubleSpinBox()
        upper_value.setRange(-999999, 999999)
        upper_value.setDecimals(3)
        upper_value.setMinimumWidth(80)
        upper_value.setMaximumWidth(100)
        upper_value.setValue(100.0)
        
        upper_row.addWidget(upper_enabled)
        upper_row.addWidget(upper_operator)
        upper_row.addWidget(upper_value)
        upper_row.addStretch()
        
        range_section.addLayout(upper_row)
        
        # Logic display
        logic_label = QLabel("Logic: Lower AND Upper")
        logic_label.setStyleSheet("""
            QLabel {
                color: rgba(230, 243, 255, 0.6);
                font-size: 10px;
                font-style: italic;
                margin-top: 5px;
            }
        """)
        range_section.addWidget(logic_label)
        
        condition_layout.addLayout(range_section)
        
        # Connect search functionality
        param_search.textChanged.connect(lambda text: self._filter_condition_parameters(param_list, text))
        
        # Connect parameter selection
        param_list.itemSelectionChanged.connect(lambda: self._update_selected_parameter(param_list, selected_param_label))
        
        # Connect enable/disable functionality
        lower_enabled.toggled.connect(lambda checked: self._toggle_range_controls(lower_operator, lower_value, checked))
        upper_enabled.toggled.connect(lambda checked: self._toggle_range_controls(upper_operator, upper_value, checked))
        
        # Store references
        condition_data = {
            'widget': condition_group,
            'param_search': param_search,
            'param_list': param_list,
            'selected_param_label': selected_param_label,
            'lower_enabled': lower_enabled,
            'lower_operator': lower_operator,
            'lower_value': lower_value,
            'upper_enabled': upper_enabled,
            'upper_operator': upper_operator,
            'upper_value': upper_value
        }
        
        self.range_conditions.append(condition_data)
        self.conditions_layout.addWidget(condition_group)
        
    def _toggle_range_controls(self, operator_combo, value_spin, enabled):
        """Enable/disable range controls based on checkbox state."""
        operator_combo.setEnabled(enabled)
        value_spin.setEnabled(enabled)
        
    def _filter_condition_parameters(self, param_list, text):
        """Filter parameter list based on search text."""
        for i in range(param_list.count()):
            item = param_list.item(i)
            matches = text.lower() in item.text().lower()
            item.setHidden(not matches)
            
    def _update_selected_parameter(self, param_list, selected_label):
        """Update selected parameter label when selection changes."""
        selected_items = param_list.selectedItems()
        if selected_items:
            selected_param = selected_items[0].text()
            selected_label.setText(f"Selected: {selected_param}")
            selected_label.setStyleSheet("""
                QLabel {
                    color: #4a90e2;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 2px;
                }
            """)
        else:
            selected_label.setText("Selected: None")
            selected_label.setStyleSheet("""
                QLabel {
                    color: rgba(230, 243, 255, 0.7);
                    font-size: 10px;
                    font-style: italic;
                    padding: 2px;
                }
            """)
        
    def _remove_range_condition(self):
        """Remove the last range condition."""
        if len(self.range_conditions) > 1:  # Keep at least one condition
            condition_data = self.range_conditions.pop()
            condition_data['widget'].deleteLater()
            
            # Update condition numbers
            self._update_condition_titles()
            
    def _update_condition_titles(self):
        """Update condition group box titles after adding/removing conditions."""
        for i, condition_data in enumerate(self.range_conditions):
            condition_data['widget'].setTitle(f"📊 Condition {i + 1}")
            
    def get_range_filter_conditions(self):
        """Get all range filter conditions in the new format."""
        conditions = []
        
        for i, condition_data in enumerate(self.range_conditions):
            # Get selected parameter from list
            selected_items = condition_data['param_list'].selectedItems()
            if not selected_items:
                continue
                
            param_name = selected_items[0].text()
            
            condition = {
                'parameter': param_name,
                'ranges': []
            }
            
            # Add lower bound if enabled
            if condition_data['lower_enabled'].isChecked():
                condition['ranges'].append({
                    'type': 'lower',
                    'operator': condition_data['lower_operator'].currentText(),
                    'value': condition_data['lower_value'].value()
                })
                
            # Add upper bound if enabled
            if condition_data['upper_enabled'].isChecked():
                condition['ranges'].append({
                    'type': 'upper',
                    'operator': condition_data['upper_operator'].currentText(),
                    'value': condition_data['upper_value'].value()
                })
                
            if condition['ranges']:  # Only add if at least one range is enabled
                conditions.append(condition)
                
        return {
            'conditions': conditions,
            'mode': 'segmented' if self.segmented_mode_rb.isChecked() else 'concatenated'
        }
        
        
    def _get_group_style(self) -> str:
        """Get consistent group box styling."""
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: #2d2d2d;
                color: #4a90e2;
            }
        """

class StaticLimitsPanel(QWidget):
    """Static limits panel for setting warning and alarm thresholds."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the static limits panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚠️ Static Limits")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4a90e2;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Configure static warning and alarm limits for parameters. These limits will be displayed as horizontal lines on the graph.")
        desc.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 12px;
                margin-bottom: 15px;
            }
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Scroll area for limits
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        limits_widget = QWidget()
        limits_layout = QVBoxLayout(limits_widget)
        
        # High Alarm Limits
        high_alarm_group = QGroupBox("🔴 High Alarm Limits")
        high_alarm_group.setStyleSheet(self._get_group_style("#e74c3c"))
        high_alarm_layout = QFormLayout(high_alarm_group)
        
        self.high_alarm_enabled = QCheckBox("Enable High Alarm")
        self.high_alarm_value = QDoubleSpinBox()
        self.high_alarm_value.setRange(-999999, 999999)
        self.high_alarm_value.setDecimals(3)
        
        high_alarm_layout.addRow(self.high_alarm_enabled)
        high_alarm_layout.addRow("Alarm Value:", self.high_alarm_value)
        
        limits_layout.addWidget(high_alarm_group)
        
        # High Warning Limits
        high_warn_group = QGroupBox("🟡 High Warning Limits")
        high_warn_group.setStyleSheet(self._get_group_style("#f39c12"))
        high_warn_layout = QFormLayout(high_warn_group)
        
        self.high_warn_enabled = QCheckBox("Enable High Warning")
        self.high_warn_value = QDoubleSpinBox()
        self.high_warn_value.setRange(-999999, 999999)
        self.high_warn_value.setDecimals(3)
        
        high_warn_layout.addRow(self.high_warn_enabled)
        high_warn_layout.addRow("Warning Value:", self.high_warn_value)
        
        limits_layout.addWidget(high_warn_group)
        
        # Low Warning Limits
        low_warn_group = QGroupBox("🟡 Low Warning Limits")
        low_warn_group.setStyleSheet(self._get_group_style("#f39c12"))
        low_warn_layout = QFormLayout(low_warn_group)
        
        self.low_warn_enabled = QCheckBox("Enable Low Warning")
        self.low_warn_value = QDoubleSpinBox()
        self.low_warn_value.setRange(-999999, 999999)
        self.low_warn_value.setDecimals(3)
        
        low_warn_layout.addRow(self.low_warn_enabled)
        low_warn_layout.addRow("Warning Value:", self.low_warn_value)
        
        limits_layout.addWidget(low_warn_group)
        
        # Low Alarm Limits
        low_alarm_group = QGroupBox("🔴 Low Alarm Limits")
        low_alarm_group.setStyleSheet(self._get_group_style("#e74c3c"))
        low_alarm_layout = QFormLayout(low_alarm_group)
        
        self.low_alarm_enabled = QCheckBox("Enable Low Alarm")
        self.low_alarm_value = QDoubleSpinBox()
        self.low_alarm_value.setRange(-999999, 999999)
        self.low_alarm_value.setDecimals(3)
        
        low_alarm_layout.addRow(self.low_alarm_enabled)
        low_alarm_layout.addRow("Alarm Value:", self.low_alarm_value)
        
        limits_layout.addWidget(low_alarm_group)
        
        # Visualization Options
        viz_group = QGroupBox("🎨 Visualization Options")
        viz_group.setStyleSheet(self._get_group_style("#4a90e2"))
        viz_layout = QFormLayout(viz_group)
        
        self.show_limit_lines = QCheckBox("Show Limit Lines")
        self.show_limit_labels = QCheckBox("Show Limit Labels")
        self.limit_line_style = QComboBox()
        self.limit_line_style.addItems(["Solid", "Dashed", "Dotted", "Dash-Dot"])
        
        self.show_limit_lines.setChecked(True)
        self.show_limit_labels.setChecked(True)
        
        viz_layout.addRow(self.show_limit_lines)
        viz_layout.addRow(self.show_limit_labels)
        viz_layout.addRow("Line Style:", self.limit_line_style)
        
        limits_layout.addWidget(viz_group)
        
        limits_layout.addStretch()
        scroll.setWidget(limits_widget)
        layout.addWidget(scroll)
        
    def _get_group_style(self, color: str = "#4a90e2") -> str:
        """Get consistent group box styling with custom color."""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #e0e0e0;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: #2d2d2d;
                color: {color};
            }}
        """

class DeviationPanel(QWidget):
    """Deviation analysis panel for statistical deviation detection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the deviation panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Deviation Analysis")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4a90e2;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Configure statistical deviation analysis to automatically detect anomalies and outliers in your data.")
        desc.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 12px;
                margin-bottom: 15px;
            }
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Scroll area for deviation settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        deviation_widget = QWidget()
        deviation_layout = QVBoxLayout(deviation_widget)
        
        # Standard Deviation Analysis
        std_group = QGroupBox("📈 Standard Deviation Analysis")
        std_group.setStyleSheet(self._get_group_style())
        std_layout = QFormLayout(std_group)
        
        self.std_enabled = QCheckBox("Enable Standard Deviation Analysis")
        self.std_threshold = QDoubleSpinBox()
        self.std_threshold.setRange(0.1, 10.0)
        self.std_threshold.setValue(2.0)
        self.std_threshold.setSingleStep(0.1)
        self.std_threshold.setSuffix(" σ")
        
        self.std_window_size = QSpinBox()
        self.std_window_size.setRange(10, 10000)
        self.std_window_size.setValue(100)
        self.std_window_size.setSuffix(" samples")
        
        std_layout.addRow(self.std_enabled)
        std_layout.addRow("Threshold:", self.std_threshold)
        std_layout.addRow("Window Size:", self.std_window_size)
        
        deviation_layout.addWidget(std_group)
        
        # Moving Average Deviation
        ma_group = QGroupBox("📊 Moving Average Deviation")
        ma_group.setStyleSheet(self._get_group_style())
        ma_layout = QFormLayout(ma_group)
        
        self.ma_enabled = QCheckBox("Enable Moving Average Deviation")
        self.ma_window = QSpinBox()
        self.ma_window.setRange(5, 1000)
        self.ma_window.setValue(50)
        self.ma_window.setSuffix(" samples")
        
        self.ma_threshold = QDoubleSpinBox()
        self.ma_threshold.setRange(0.1, 100.0)
        self.ma_threshold.setValue(5.0)
        self.ma_threshold.setSuffix(" %")
        
        ma_layout.addRow(self.ma_enabled)
        ma_layout.addRow("Window Size:", self.ma_window)
        ma_layout.addRow("Deviation Threshold:", self.ma_threshold)
        
        deviation_layout.addWidget(ma_group)
        
        # Trend Analysis
        trend_group = QGroupBox("📈 Trend Analysis")
        trend_group.setStyleSheet(self._get_group_style())
        trend_layout = QFormLayout(trend_group)
        
        self.trend_enabled = QCheckBox("Enable Trend Analysis")
        self.trend_sensitivity = QSlider(Qt.Horizontal)
        self.trend_sensitivity.setRange(1, 10)
        self.trend_sensitivity.setValue(5)
        
        self.trend_min_duration = QSpinBox()
        self.trend_min_duration.setRange(10, 1000)
        self.trend_min_duration.setValue(50)
        self.trend_min_duration.setSuffix(" samples")
        
        trend_layout.addRow(self.trend_enabled)
        trend_layout.addRow("Sensitivity:", self.trend_sensitivity)
        trend_layout.addRow("Min Duration:", self.trend_min_duration)
        
        deviation_layout.addWidget(trend_group)
        
        # Visualization Options
        viz_group = QGroupBox("🎨 Visualization Options")
        viz_group.setStyleSheet(self._get_group_style())
        viz_layout = QFormLayout(viz_group)
        
        self.highlight_deviations = QCheckBox("Highlight Deviations")
        self.show_deviation_bands = QCheckBox("Show Deviation Bands")
        self.deviation_color = QPushButton("Deviation Color")
        self.deviation_color.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
        """)
        
        self.highlight_deviations.setChecked(True)
        self.show_deviation_bands.setChecked(True)
        
        viz_layout.addRow(self.highlight_deviations)
        viz_layout.addRow(self.show_deviation_bands)
        viz_layout.addRow("Color:", self.deviation_color)
        
        deviation_layout.addWidget(viz_group)
        
        deviation_layout.addStretch()
        scroll.setWidget(deviation_widget)
        layout.addWidget(scroll)
        
        # Analysis buttons
        button_layout = QHBoxLayout()
        
        self.run_analysis_btn = QPushButton("🔍 Run Analysis")
        self.clear_results_btn = QPushButton("🗑️ Clear Results")
        
        for btn in [self.run_analysis_btn, self.clear_results_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 20px;
                    border: 2px solid #4a90e2;
                    border-radius: 8px;
                    background-color: transparent;
                    color: #4a90e2;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #4a90e2;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #3a7bc8;
                }
            """)
            
        button_layout.addWidget(self.run_analysis_btn)
        button_layout.addWidget(self.clear_results_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def _get_group_style(self) -> str:
        """Get consistent group box styling."""
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: #2d2d2d;
                color: #4a90e2;
            }
        """

class GraphAdvancedSettingsDialog(QDialog):
    """
    Advanced Graph Settings Dialog - Modern, Professional Interface
    
    Features:
    - Modern sidebar navigation
    - Comprehensive parameter configuration
    - Advanced filtering options
    - Static limit configuration
    - Deviation analysis tools
    - Professional dark theme
    """
    
    # Signals for filter application
    range_filter_applied = pyqtSignal(dict)  # Emits filter conditions
    
    def __init__(self, graph_index: int, all_signals: List[str], visible_signals: List[str], parent=None):
        super().__init__(parent)
        
        self.graph_index = graph_index
        self.all_signals = all_signals
        self.visible_signals = visible_signals
        
        # Debug logging
        logger.debug(f"GraphAdvancedSettingsDialog constructor:")
        logger.debug(f"  - graph_index: {graph_index}")
        logger.debug(f"  - all_signals count: {len(all_signals) if all_signals else 0}")
        logger.debug(f"  - all_signals sample: {all_signals[:3] if all_signals else 'None'}")
        logger.debug(f"  - visible_signals count: {len(visible_signals) if visible_signals else 0}")
        logger.debug(f"  - parent: {parent}")
        logger.debug(f"  - parent has signal_processor: {hasattr(parent, 'signal_processor') if parent else False}")
        
        self._setup_dialog()
        self._setup_ui()
        self._setup_connections()
        
        logger.debug(f"GraphAdvancedSettingsDialog initialized for graph {graph_index}")
        print(f"[DEBUG] GraphAdvancedSettingsDialog v2.0 - Space Theme initialized for graph {graph_index}")
        
    def _setup_dialog(self):
        """Setup dialog properties."""
        self.setWindowTitle(f"Graph {self.graph_index + 1} - Advanced Settings (Space Theme)")
        self.setMinimumSize(900, 600)
        self.resize(1000, 650)
        
        # Modern space theme
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a2332, stop:0.5 #2d4a66, stop:1 #1a2332);
                color: #e6f3ff;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d4a66, stop:1 #4a90e2);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a90e2, stop:1 #5ba0f2);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5ba0f2, stop:1 #6bb0ff);
            }
            QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 6px 10px;
                border: 2px solid rgba(74, 144, 226, 0.3);
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d4a66, stop:1 #1a2332);
                color: #e6f3ff;
                font-size: 12px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #4a90e2;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #2d4a66);
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #e6f3ff;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d4a66, stop:1 #1a2332);
                border: 2px solid rgba(74, 144, 226, 0.5);
                border-radius: 6px;
                color: #e6f3ff;
                selection-background-color: rgba(74, 144, 226, 0.3);
                selection-color: #ffffff;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                border-radius: 3px;
                color: #e6f3ff;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(74, 144, 226, 0.2);
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background: rgba(74, 144, 226, 0.4);
                color: #ffffff;
            }
            QCheckBox {
                color: #e6f3ff;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid rgba(74, 144, 226, 0.3);
                border-radius: 3px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d4a66, stop:1 #1a2332);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #5ba0f2);
                border-color: #4a90e2;
            }
            QSlider::groove:horizontal {
                border: 1px solid rgba(74, 144, 226, 0.3);
                height: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d4a66, stop:1 #1a2332);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #5ba0f2);
                border: 2px solid #4a90e2;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
        """)
        
    def _setup_ui(self):
        """Setup the main UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main content area
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left sidebar
        self._create_sidebar(splitter)
        
        # Right content area with embedded buttons
        self._create_content_area(splitter)
        
        # Set splitter proportions (more space for content)
        splitter.setSizes([220, 780])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        content_layout.addWidget(splitter)
        main_layout.addLayout(content_layout)
        
    def _create_sidebar(self, parent):
        """Create the left sidebar with navigation buttons."""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)  # Reduced width
        sidebar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a2332, stop:0.7 #2d4a66, stop:1 #4a90e2);
                border-right: 2px solid rgba(74, 144, 226, 0.5);
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        # Title
        title = QLabel(f"Graph {self.graph_index + 1}")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #e6f3ff;
                padding: 8px 0;
                border-bottom: 2px solid rgba(74, 144, 226, 0.5);
                margin-bottom: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 transparent);
                border-radius: 4px;
            }
        """)
        layout.addWidget(title)
        
        # Navigation buttons
        self.nav_buttons = QButtonGroup(self)
        
        self.parameters_btn = ModernSidebarButton("Parameters", "📊")
        self.filters_btn = ModernSidebarButton("Range Filters", "🔍")
        self.limits_btn = ModernSidebarButton("Static Limits", "⚠️")
        self.deviation_btn = ModernSidebarButton("Deviation", "📈")
        
        buttons = [self.parameters_btn, self.filters_btn, self.limits_btn, self.deviation_btn]
        
        for i, btn in enumerate(buttons):
            self.nav_buttons.addButton(btn, i)
            layout.addWidget(btn)
            
        # Set default selection
        self.parameters_btn.setChecked(True)
        
        layout.addStretch()
        
        parent.addWidget(sidebar)
        
    def _create_content_area(self, splitter):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        
        self.stacked_widget = QStackedWidget()
        
        # Create and add panels
        self.parameters_panel = ParametersPanel(self.all_signals, self.visible_signals, self)
        self.parameter_filters_panel = ParameterFiltersPanel(self.graph_index, self.all_signals, self)
        self.static_limits_panel = StaticLimitsPanel(self)
        self.deviation_panel = DeviationPanel(self)
        
        self.stacked_widget.addWidget(self.parameters_panel)
        self.stacked_widget.addWidget(self.parameter_filters_panel)
        self.stacked_widget.addWidget(self.static_limits_panel)
        self.stacked_widget.addWidget(self.deviation_panel)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Add buttons at the bottom right
        self._create_embedded_buttons(content_layout)
        
        splitter.addWidget(content_widget)
        
    def _create_embedded_buttons(self, parent_layout):
        """Create compact buttons embedded in the content area."""
        # Button container with space theme
        button_container = QWidget()
        button_container.setFixedHeight(50)
        button_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.1), stop:1 transparent);
                border-top: 1px solid rgba(74, 144, 226, 0.3);
                margin: 0px;
            }
        """)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(15, 8, 15, 8)
        button_layout.setSpacing(8)
        
        # Info label
        info_label = QLabel(f"Graph {self.graph_index + 1} Settings")
        info_label.setStyleSheet("""
            QLabel {
                color: rgba(230, 243, 255, 0.7);
                font-size: 11px;
                font-weight: 500;
            }
        """)
        button_layout.addWidget(info_label)
        
        button_layout.addStretch()
        
        # Compact action buttons
        self.apply_btn = QPushButton("Apply")
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        
        # Compact button styling
        button_style = """
            QPushButton {
                padding: 6px 16px;
                border: 1px solid rgba(74, 144, 226, 0.5);
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 transparent);
                color: #e6f3ff;
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.4), stop:1 rgba(74, 144, 226, 0.1));
                border-color: #4a90e2;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 rgba(74, 144, 226, 0.3));
            }
        """
        
        for btn in [self.apply_btn, self.cancel_btn]:
            btn.setStyleSheet(button_style)
            
        # OK button special styling (primary action)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border: 1px solid #4a90e2;
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #5ba0f2);
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                min-width: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #6bb0ff);
                border-color: #5ba0f2;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a7bc8, stop:1 #4a90e2);
            }
        """)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        parent_layout.addWidget(button_container)
        
        
    def _setup_connections(self):
        """Setup signal connections."""
        # Navigation
        self.nav_buttons.buttonClicked.connect(self._on_nav_button_clicked)
        
        # Dialog buttons
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self._apply_settings)
        
        # Connect filter panel signals to dialog signals
        self.filters_panel.range_filter_applied.connect(self.range_filter_applied.emit)
        
    def _on_nav_button_clicked(self, button):
        """Handle navigation button clicks."""
        button_id = self.nav_buttons.id(button)
        self.stacked_widget.setCurrentIndex(button_id)
        
        # Log navigation for debugging
        panel_names = ["Parameters", "Range Filters", "Static Limits", "Deviation"]
        logger.debug(f"Switched to {panel_names[button_id]} panel")
        
    def _apply_settings(self):
        """Apply current settings without closing dialog."""
        # This would typically save settings and update the graph
        logger.info(f"Applied settings for graph {self.graph_index}")
        
        # You could emit a signal here to update the parent widget
        # self.settings_applied.emit(self.get_all_settings())
        
    def get_selected_signals(self) -> List[str]:
        """Get the selected signals from the parameters panel."""
        return self.parameters_panel.get_selected_signals()
        
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings from all panels."""
        settings = {
            'graph_index': self.graph_index,
            'selected_signals': self.get_selected_signals(),
            # Add other settings as needed
            'filters': self._get_filter_settings(),
            'limits': self._get_limit_settings(),
            'deviation': self._get_deviation_settings()
        }
        return settings
        
    def _get_filter_settings(self) -> Dict[str, Any]:
        """Get filter settings from the filters panel."""
        # Implementation would extract all filter settings
        return {}
        
    def _get_limit_settings(self) -> Dict[str, Any]:
        """Get limit settings from the limits panel."""
        # Implementation would extract all limit settings
        return {}
        
    def _get_deviation_settings(self) -> Dict[str, Any]:
        """Get deviation settings from the deviation panel."""
        # Implementation would extract all deviation settings
        return {}
