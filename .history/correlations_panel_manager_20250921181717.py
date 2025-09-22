# type: ignore
"""
Correlations Panel Manager for Time Graph Widget

Manages correlation analysis between signals with real-time updates.
Features:
- Target parameter selection with search
- Pearson correlation calculation
- Real-time cursor-based updates
- Color-coded results
- Configurable result count
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QPushButton, QSpinBox, QListWidget, 
    QListWidgetItem, QCheckBox, QProgressBar, QDialog, QDialogButtonBox, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal as Signal
from PyQt5.QtGui import QFont, QColor

logger = logging.getLogger(__name__)

class ParameterSelectionDialog(QDialog):
    """A dialog for searching and selecting a parameter."""
    def __init__(self, parameters: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Target Parameter")
        self.setMinimumWidth(300)
        self.setStyleSheet(parent.styleSheet())

        self.all_parameters = parameters
        self.selected_parameter = None

        layout = QVBoxLayout(self)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self._filter_list)
        layout.addWidget(self.search_box)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.all_parameters)
        self.list_widget.itemDoubleClicked.connect(self._on_item_selected)
        layout.addWidget(self.list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _filter_list(self, text: str):
        self.list_widget.clear()
        if not text:
            self.list_widget.addItems(self.all_parameters)
        else:
            filtered_items = [p for p in self.all_parameters if text.lower() in p.lower()]
            self.list_widget.addItems(filtered_items)

    def _on_item_selected(self, item: QListWidgetItem):
        self.accept()

    def accept(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            self.selected_parameter = selected_item.text()
        super().accept()

    @staticmethod
    def get_parameter(parameters: List[str], parent=None) -> Optional[str]:
        dialog = ParameterSelectionDialog(parameters, parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.selected_parameter
        return None

class CorrelationsPanelManager:
    """Manages the correlations analysis panel."""
    
    # Signals
    correlation_calculated = Signal(dict)  # Emits correlation results
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.panel = None
        
        # Analysis settings
        self.is_analysis_active = False
        self.target_parameter = None
        self.max_results = 5
        self.current_correlations = {}
        
        # UI components
        self.active_checkbox = None
        self.target_button = None
        self.results_spinbox = None
        self.results_list = None
        self.progress_bar = None
        self.available_parameters = []
        
        # Timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._calculate_correlations)
        self.update_timer.setSingleShot(True)  # Only fire once per trigger
        
        self._create_panel()
        
    def get_panel(self) -> QWidget:
        """Get the correlations panel widget."""
        return self.panel
        
    def _create_panel(self):
        """Create the main correlations panel."""
        self.panel = QWidget()
        # Apply theme-based styling
        self._apply_theme_styling()
        
        layout = QVBoxLayout(self.panel)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("📈 Correlations Analysis")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a90e2; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Analysis Control Group
        self._create_analysis_controls(layout)
        
        # Target Selection Group
        self._create_target_selection(layout)
        
        # Results Configuration Group
        self._create_results_config(layout)
        
        # Results Display Group
        self._create_results_display(layout)
        
        layout.addStretch()
        
    def _create_analysis_controls(self, parent_layout):
        """Create analysis control section."""
        control_group = QGroupBox("Analysis Control")
        control_layout = QVBoxLayout(control_group)
        
        # Active/Inactive toggle
        self.active_checkbox = QCheckBox("🔄 Enable Real-time Analysis")
        self.active_checkbox.setToolTip("Enable/disable automatic correlation calculation")
        self.active_checkbox.toggled.connect(self._on_analysis_toggled)
        control_layout.addWidget(self.active_checkbox)
        
        # Progress bar for calculations
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Calculation Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        control_layout.addLayout(progress_layout)
        
        parent_layout.addWidget(control_group)
        
    def _create_target_selection(self, parent_layout):
        """Create target parameter selection section."""
        target_group = QGroupBox("Target Parameter Selection")
        target_layout = QVBoxLayout(target_group)
        
        # Target parameter button
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("🎯 Target:"))
        self.target_button = QPushButton("Select Parameter...")
        self.target_button.setStyleSheet("text-align: left; padding: 4px 8px;")
        self.target_button.clicked.connect(self._show_parameter_dialog)
        combo_layout.addWidget(self.target_button)
        target_layout.addLayout(combo_layout)
        
        parent_layout.addWidget(target_group)
        
    def _show_parameter_dialog(self):
        """Show the parameter selection dialog."""
        selected = ParameterSelectionDialog.get_parameter(self.available_parameters, self.panel)
        if selected:
            self._on_target_changed(selected)

    def _create_results_config(self, parent_layout):
        """Create results configuration section."""
        config_group = QGroupBox("Results Configuration")
        config_layout = QHBoxLayout(config_group)
        
        config_layout.addWidget(QLabel("📊 Show Top:"))
        self.results_spinbox = QSpinBox()
        self.results_spinbox.setRange(1, 50)
        self.results_spinbox.setValue(5)
        self.results_spinbox.setSuffix(" results")
        self.results_spinbox.valueChanged.connect(self._on_max_results_changed)
        config_layout.addWidget(self.results_spinbox)
        
        config_layout.addStretch()
        
        # Manual calculate button
        calc_btn = QPushButton("Calculate")
        calc_btn.setStyleSheet("padding: 4px 12px; font-size: 12px;")
        calc_btn.clicked.connect(self._calculate_correlations)
        config_layout.addWidget(calc_btn)
        
        parent_layout.addWidget(config_group)
        
    def _create_results_display(self, parent_layout):
        """Create results display section."""
        results_group = QGroupBox("Correlation Results")
        results_layout = QVBoxLayout(results_group)
        
        # Info label
        info_label = QLabel("💡 Results show correlation with target parameter (-1 to +1)")
        info_label.setStyleSheet("font-size: 12px; color: #888888; font-style: italic;")
        results_layout.addWidget(info_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        results_layout.addWidget(self.results_list)
        
        parent_layout.addWidget(results_group)
        
    def _on_analysis_toggled(self, checked: bool):
        """Handle analysis active/inactive toggle."""
        self.is_analysis_active = checked
        logger.info(f"Correlation analysis {'enabled' if checked else 'disabled'}")
        
        if checked:
            self._trigger_calculation()
        else:
            self.update_timer.stop()
            
    def _on_target_changed(self, target_name: str):
        """Handle target parameter selection change."""
        if target_name and target_name != self.target_parameter:
            self.target_parameter = target_name
            self.target_button.setText(target_name)
            logger.info(f"Target parameter changed to: {target_name}")
            if self.is_analysis_active:
                self._trigger_calculation()
                
    def _on_max_results_changed(self, value: int):
        """Handle max results count change."""
        self.max_results = value
        self._update_results_display()
        
    def _filter_target_combo(self, search_text: str):
        """Filter target combo based on search text."""
        # TODO: Implement parameter filtering
        pass
        
    def _trigger_calculation(self):
        """Trigger correlation calculation with a small delay."""
        if self.is_analysis_active and self.target_parameter:
            self.update_timer.stop()
            self.update_timer.start(500)  # 500ms delay to avoid too frequent updates
            
    def _calculate_correlations(self):
        """Calculate correlations between target and other parameters."""
        if not self.is_analysis_active or not self.target_parameter:
            return
            
        logger.debug(f"Calculating correlations for target: {self.target_parameter}")
        
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(10)

            if not hasattr(self.parent, 'signal_processor') or not hasattr(self.parent.signal_processor, 'get_all_signals'):
                logger.warning("Signal processor not found on parent widget.")
                self.current_correlations = {}
                self._update_results_display()
                return

            all_signals = self.parent.signal_processor.get_all_signals()
            if not all_signals or self.target_parameter not in all_signals:
                logger.warning(f"Target parameter '{self.target_parameter}' not found in signals.")
                self.current_correlations = {}
                self._update_results_display()
                return

            target_data = all_signals[self.target_parameter]['y_data']
            correlations = {}
            
            # Ensure target data is a 1D numpy array
            if not isinstance(target_data, np.ndarray):
                target_data = np.array(target_data)

            total_signals = len(all_signals) - 1
            processed_signals = 0

            for name, signal_data in all_signals.items():
                if name == self.target_parameter:
                    continue
                
                other_data = signal_data['y_data']
                if not isinstance(other_data, np.ndarray):
                    other_data = np.array(other_data)

                # Ensure data lengths are equal for correlation calculation
                min_len = min(len(target_data), len(other_data))
                if min_len > 1: # Correlation requires at least 2 points
                    corr_matrix = np.corrcoef(target_data[:min_len], other_data[:min_len])
                    # corrcoef returns a 2x2 matrix, the value is at [0, 1]
                    correlation = corr_matrix[0, 1]
                    if not np.isnan(correlation):
                        correlations[name] = correlation
                
                processed_signals += 1
                self.progress_bar.setValue(10 + int(90 * (processed_signals / total_signals)))

            self.current_correlations = correlations
            self._update_results_display()
            
            # Hide progress bar after a short delay
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}", exc_info=True)
            self.progress_bar.setVisible(False)
            
    def _update_results_display(self):
        """Update the results list display."""
        self.results_list.clear()
        
        if not self.current_correlations:
            item = QListWidgetItem("No correlations calculated yet")
            item.setForeground(QColor("#888888"))
            self.results_list.addItem(item)
            return
            
        # Sort by absolute correlation value (strongest correlations first)
        sorted_correlations = sorted(
            self.current_correlations.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Show only top N results
        for i, (param_name, correlation) in enumerate(sorted_correlations[:self.max_results]):
            self._add_correlation_item(i + 1, param_name, correlation)
            
    def _add_correlation_item(self, rank: int, param_name: str, correlation: float):
        """Add a correlation result item to the list."""
        # Format correlation value
        corr_percent = abs(correlation) * 100
        corr_sign = "+" if correlation >= 0 else "-"
        
        # Create item text
        item_text = f"{rank}. {param_name:<20} {corr_sign}{corr_percent:.1f}% ({correlation:.3f})"
        
        item = QListWidgetItem(item_text)
        
        # Color coding based on correlation strength
        if abs(correlation) >= 0.8:
            # Strong correlation - bright color
            color = QColor("#4CAF50") if correlation > 0 else QColor("#F44336")  # Green/Red
        elif abs(correlation) >= 0.5:
            # Moderate correlation - medium color
            color = QColor("#8BC34A") if correlation > 0 else QColor("#FF7043")  # Light Green/Orange
        else:
            # Weak correlation - muted color
            color = QColor("#9E9E9E")  # Gray
            
        item.setForeground(color)
        
        # Set font weight for strong correlations
        if abs(correlation) >= 0.8:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            
        self.results_list.addItem(item)
        
    def update_available_parameters(self, parameters: List[str]):
        """Update the list of available parameters for target selection."""
        self.available_parameters = parameters
        # Set initial or restore previous target
        if self.target_parameter and self.target_parameter in self.available_parameters:
            self.target_button.setText(self.target_parameter)
        elif self.available_parameters:
            # Set a default target if none is selected
            self._on_target_changed(self.available_parameters[0])
        else:
            self.target_button.setText("No parameters available")
            
    def on_cursor_moved(self, cursor_positions: Dict[str, float]):
        """Handle cursor movement for real-time updates."""
        if self.is_analysis_active:
            self._trigger_calculation()
            
    def on_data_changed(self):
        """Handle data changes that might affect correlations."""
        if self.is_analysis_active:
            self._trigger_calculation()
