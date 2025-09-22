# type: ignore
"""
UI Components for Time Analysis Widget Configuration

Provides configuration controls for the time analysis widget:
- Column selection (same as line chart widget)
- Cursor mode controls
- Analysis settings
- Export options
"""

import logging
from typing import TYPE_CHECKING, List
import vaex
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
    QComboBox, QPushButton, QCheckBox, QSpinBox,
    QLineEdit, QListWidget, QListWidgetItem, QAbstractItemView,
    QButtonGroup, QRadioButton, QHBoxLayout, QLabel
)
from PyQt5.QtCore import pyqtSignal as Signal

if TYPE_CHECKING:
    from .widget import TimeAnalysisCanvasWidget

logger = logging.getLogger(__name__)

class TimeAnalysisUIComponents(QWidget):
    """
    Configuration UI components for the Time Analysis widget.
    
    Provides the same data selection interface as the line chart widget
    plus additional analysis-specific controls.
    """
    settings_changed = Signal()

    def __init__(self, widget: "TimeAnalysisCanvasWidget"):
        print("🔍 DEBUG: TimeAnalysisUIComponents.__init__ başladı")
        super().__init__()
        print("🔍 DEBUG: TimeAnalysisUIComponents super().__init__() tamamlandı")
        self.widget = widget
        
        # UI components - will be created lazily
        self.x_column_combo = None
        self.y_columns_list = None
        self.title_edit = None
        self.cursor_mode_group = None
        self.normalize_check = None
        self.statistics_check = None
        self._ui_created = False
        
        print("🔍 DEBUG: TimeAnalysisUIComponents.__init__ tamamlandı")

    def _create_ui(self):
        """Create all UI components."""
        if self._ui_created:
            return
            
        self._setup_modern_styling()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        self._create_column_selection_group(layout)
        self._create_analysis_settings_group(layout)
        self._create_cursor_controls_group(layout)
        self._create_export_controls_group(layout)
        layout.addStretch()
        
        self._connect_signals()
        self.update_data(self.widget.input_df)
        
        self._ui_created = True

    def _setup_modern_styling(self):
        """Setup modern styling for the UI components."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600; border: 2px solid #007bff;
                border-radius: 8px; margin-top: 10px;
                padding: 10px; background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 10px; padding: 0 5px;
            }
            QListWidget { 
                border: 1px solid #ced4da; border-radius: 4px; 
                background-color: white;
            }
            QComboBox {
                border: 1px solid #ced4da; border-radius: 4px;
                padding: 5px; background-color: white;
            }
            QLineEdit {
                border: 1px solid #ced4da; border-radius: 4px;
                padding: 5px; background-color: white;
            }
            QCheckBox {
                spacing: 5px;
            }
            QRadioButton {
                spacing: 5px;
            }
        """)

    def _create_column_selection_group(self, layout: QVBoxLayout):
        """Create column selection controls (same as line chart widget)."""
        group = QGroupBox("📊 Data Selection")
        form_layout = QFormLayout(group)
        
        # X-axis column selection
        self.x_column_combo = QComboBox()
        self.x_column_combo.setToolTip("Select the time/X-axis column")
        form_layout.addRow("Time Column:", self.x_column_combo)
        
        # Y-axis columns selection
        self.y_columns_list = QListWidget()
        self.y_columns_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.y_columns_list.setMaximumHeight(120)
        self.y_columns_list.setToolTip("Select signal columns to analyze")
        form_layout.addRow("Signal Columns:", self.y_columns_list)
        
        layout.addWidget(group)

    def _create_analysis_settings_group(self, layout: QVBoxLayout):
        """Create analysis-specific settings."""
        group = QGroupBox("🔬 Analysis Settings")
        form_layout = QFormLayout(group)
        
        # Analysis title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter analysis title...")
        form_layout.addRow("Title:", self.title_edit)
        
        # Data normalization
        self.normalize_check = QCheckBox("Apply Peak Normalization")
        self.normalize_check.setToolTip("Normalize all signals to [-1, 1] range")
        form_layout.addRow(self.normalize_check)
        
        # Statistics display
        self.statistics_check = QCheckBox("Show Real-time Statistics")
        self.statistics_check.setChecked(True)
        self.statistics_check.setToolTip("Display real-time statistics panel")
        form_layout.addRow(self.statistics_check)
        
        # Grid display
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        self.grid_check.setToolTip("Display grid lines on plot")
        form_layout.addRow(self.grid_check)
        
        layout.addWidget(group)

    def _create_cursor_controls_group(self, layout: QVBoxLayout):
        """Create cursor mode controls."""
        group = QGroupBox("🎯 Cursor Controls")
        cursor_layout = QVBoxLayout(group)
        
        # Create button group for mutually exclusive cursor modes
        self.cursor_mode_group = QButtonGroup(self)
        
        # No cursor (default)
        no_cursor_radio = QRadioButton("No Cursor")
        no_cursor_radio.setChecked(True)
        no_cursor_radio.setToolTip("Disable all cursors")
        self.cursor_mode_group.addButton(no_cursor_radio, 0)
        cursor_layout.addWidget(no_cursor_radio)
        
        # Single cursor
        single_cursor_radio = QRadioButton("Single Cursor")
        single_cursor_radio.setToolTip("Enable single movable cursor line")
        self.cursor_mode_group.addButton(single_cursor_radio, 1)
        cursor_layout.addWidget(single_cursor_radio)
        
        # Dual cursors
        dual_cursor_radio = QRadioButton("Two Cursors")
        dual_cursor_radio.setToolTip("Enable two independent cursor lines")
        self.cursor_mode_group.addButton(dual_cursor_radio, 2)
        cursor_layout.addWidget(dual_cursor_radio)
        
        # Range selector
        range_selector_radio = QRadioButton("Range Selector")
        range_selector_radio.setToolTip("Enable range selection for detailed analysis")
        self.cursor_mode_group.addButton(range_selector_radio, 3)
        cursor_layout.addWidget(range_selector_radio)
        
        layout.addWidget(group)

    def _create_export_controls_group(self, layout: QVBoxLayout):
        """Create export and action controls."""
        group = QGroupBox("💾 Export & Actions")
        export_layout = QVBoxLayout(group)
        
        # Reset analysis button
        reset_button = QPushButton("🔄 Reset Analysis")
        reset_button.setToolTip("Reset all cursors and zoom to fit all data")
        reset_button.clicked.connect(self._reset_analysis)
        export_layout.addWidget(reset_button)
        
        # Export statistics button
        export_stats_button = QPushButton("📊 Export Statistics")
        export_stats_button.setToolTip("Export current statistics to CSV")
        export_stats_button.clicked.connect(self._export_statistics)
        export_layout.addWidget(export_stats_button)
        
        # Export plot button
        export_plot_button = QPushButton("🖼️ Export Plot")
        export_plot_button.setToolTip("Export current plot as image")
        export_plot_button.clicked.connect(self._export_plot)
        export_layout.addWidget(export_plot_button)
        
        layout.addWidget(group)

    def _connect_signals(self):
        """Connect UI component signals."""
        # Column selection signals
        self.x_column_combo.currentTextChanged.connect(self._on_settings_changed)
        self.y_columns_list.itemSelectionChanged.connect(self._on_settings_changed)
        
        # Analysis settings signals
        self.title_edit.textChanged.connect(self._on_settings_changed)
        self.normalize_check.toggled.connect(self._on_settings_changed)
        self.statistics_check.toggled.connect(self._on_settings_changed)
        self.grid_check.toggled.connect(self._on_settings_changed)
        
        # Cursor mode signals
        self.cursor_mode_group.buttonClicked.connect(self._on_cursor_mode_changed)

    def _on_settings_changed(self):
        """Handle settings changes."""
        if getattr(self, '_updating_ui', False):
            return
        
        # Update widget settings
        self.widget.settings['x_column'] = self.x_column_combo.currentText()
        self.widget.settings['title'] = self.title_edit.text()
        self.widget.settings['normalize_data'] = self.normalize_check.isChecked()
        self.widget.settings['statistics_enabled'] = self.statistics_check.isChecked()
        self.widget.settings['show_grid'] = self.grid_check.isChecked()
        
        # Update Y columns
        selected_items = self.y_columns_list.selectedItems()
        self.widget.settings['y_columns'] = [item.text() for item in selected_items]
        
        # Emit settings changed signal
        self.settings_changed.emit()

    def _on_cursor_mode_changed(self, button):
        """Handle cursor mode changes."""
        mode_map = {0: "none", 1: "single", 2: "dual", 3: "range"}
        button_id = self.cursor_mode_group.id(button)
        cursor_mode = mode_map.get(button_id, "none")
        
        self.widget.settings['cursor_mode'] = cursor_mode
        self.settings_changed.emit()

    def _reset_analysis(self):
        """Reset the analysis to initial state."""
        # This will be connected to the dialog's analysis widget
        print("🔍 DEBUG: Reset analysis requested")
        
    def _export_statistics(self):
        """Export current statistics."""
        # TODO: Implement statistics export
        print("🔍 DEBUG: Export statistics requested")
        
    def _export_plot(self):
        """Export current plot as image."""
        # TODO: Implement plot export
        print("🔍 DEBUG: Export plot requested")

    def update_data(self, df: vaex.DataFrame | None):
        """Update UI components when new data arrives."""
        print(f"🔍 DEBUG: TimeAnalysisUIComponents.update_data çağrıldı, df: {df}")
        
        if not self._ui_created or self.x_column_combo is None:
            print("🔍 DEBUG: UI henüz oluşturulmadı, update_data skip edildi")
            return
        
        # Clear existing items
        self.x_column_combo.clear()
        self.y_columns_list.clear()

        if df is not None:
            try:
                columns = df.get_column_names()
                print(f"🔍 DEBUG: Columns: {columns}")
                
                # Add columns to X-axis combo
                self.x_column_combo.addItems(columns)
                
                # Add columns to Y-axis list
                for col in columns:
                    item = QListWidgetItem(col)
                    self.y_columns_list.addItem(item)
                
                print(f"🔍 DEBUG: UI güncellendi - {len(columns)} kolon eklendi")
                
                # Auto-select columns
                self.widget._auto_select_columns()
                
                # Update UI with current settings
                self._update_ui_from_settings()
                
            except Exception as e:
                print(f"🔍 DEBUG: UI güncelleme hatası: {e}")
                logger.error(f"Failed to update UI components: {e}")
        else:
            print("🔍 DEBUG: df None, UI temizlendi")

    def _update_ui_from_settings(self):
        """Update UI controls with current widget settings."""
        print(f"🔍 DEBUG: _update_ui_from_settings çağrıldı")
        
        # Block signals to prevent loops
        controls = [
            self.x_column_combo, self.y_columns_list, self.title_edit,
            self.normalize_check, self.statistics_check, self.grid_check
        ]
        for control in controls:
            if control:
                control.blockSignals(True)

        # Update X column
        x_col = self.widget.settings.get('x_column')
        if x_col and self.x_column_combo.count() > 0:
            index = self.x_column_combo.findText(x_col)
            if index >= 0:
                self.x_column_combo.setCurrentIndex(index)
        
        # Update Y columns
        y_cols = self.widget.settings.get('y_columns', [])
        for i in range(self.y_columns_list.count()):
            item = self.y_columns_list.item(i)
            should_select = item.text() in y_cols
            item.setSelected(should_select)
        
        # Update other settings
        self.title_edit.setText(self.widget.settings.get('title', 'Time Analysis'))
        self.normalize_check.setChecked(self.widget.settings.get('normalize_data', False))
        self.statistics_check.setChecked(self.widget.settings.get('statistics_enabled', True))
        self.grid_check.setChecked(self.widget.settings.get('show_grid', True))
        
        # Update cursor mode
        cursor_mode = self.widget.settings.get('cursor_mode', 'none')
        mode_map = {"none": 0, "single": 1, "dual": 2, "range": 3}
        button_id = mode_map.get(cursor_mode, 0)
        if button_id < len(self.cursor_mode_group.buttons()):
            self.cursor_mode_group.button(button_id).setChecked(True)
        
        # Restore signals
        for control in controls:
            if control:
                control.blockSignals(False)
        
        print("🔍 DEBUG: UI ayarları tamamlandı")