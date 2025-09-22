# type: ignore
"""
Time Analysis Dialog

Integrates the TimeAnalysisWidget with MachinePulseAI's dialog system.
Provides the main interface for advanced time-series analysis.
"""

import logging
from typing import TYPE_CHECKING
import vaex
import numpy as np
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal as Signal
from PyQt5.QtGui import QColor

from .time_graph_widget import TimeGraphWidget

if TYPE_CHECKING:
    from .widget import TimeGraphCanvasWidget

logger = logging.getLogger(__name__)

class TimeGraphDialog(QDialog):
    """
    Dialog window for the Time Graph Widget.
    
    Contains both the advanced time-series analysis interface and
    configuration controls.
    """
    
    def __init__(self, widget: "TimeGraphCanvasWidget"):
        super().__init__()
        self.widget = widget
        self.original_settings = widget.settings.copy()

        print("🔍 DEBUG: TimeGraphDialog.__init__ başladı")
        
        # Dialog setup
        self.setWindowTitle("📊 Time Graph Analysis")
        self.setMinimumSize(1000, 700)
        self.resize(1400, 900)
        self.setStyleSheet("QDialog { background-color: #f8f9fa; }")
        
        # Window flags - native title bar with minimize/maximize/close buttons
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                          Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # UI creation
        self._ui_created = False
        self._pending_data = widget.input_df  # Store initial data
        print("🔍 DEBUG: TimeAnalysisDialog constructor tamamlandı")

    def showEvent(self, event):
        """Dialog gösterildiğinde UI'ı oluştur."""
        super().showEvent(event)
        if not self._ui_created:
            print("🔍 DEBUG: showEvent - UI yaratılıyor")
            try:
                self._create_dialog_ui()
                self._ui_created = True
                # Now that UI is created, process any pending data
                self.update_data(self._pending_data)
                print("🔍 DEBUG: showEvent - UI başarıyla yaratıldı")
            except Exception as e:
                print(f"🔍 DEBUG: showEvent - UI yaratırken hata: {e}")
                import traceback
                traceback.print_exc()
                raise

    def _create_dialog_ui(self):
        """Create the complete dialog UI."""
        print("🔍 DEBUG: _create_dialog_ui başladı")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Main content: Time Graph Widget (full width)
        self.time_graph_widget = TimeGraphWidget()
        main_layout.addWidget(self.time_graph_widget)
        
        # Button box
        self._create_button_box()
        main_layout.addWidget(self.button_box)
        
        # Connect signals
        self._connect_signals()
        
        print("🔍 DEBUG: _create_dialog_ui tamamlandı")

    def _create_button_box(self):
        """Create the bottom button bar."""
        self.button_box = QDialogButtonBox()
        
        # Analysis button
        self.analyze_button = self.button_box.addButton("🔬 Analyze", QDialogButtonBox.ActionRole)
        self.analyze_button.setToolTip("Refresh analysis with current settings")
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745; color: white; border: none;
                padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        
        # Export button
        self.export_button = self.button_box.addButton("💾 Export", QDialogButtonBox.ActionRole)
        self.export_button.setToolTip("Export analysis results")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8; color: white; border: none;
                padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #138496; }
        """)
        
        # Standard buttons
        self.button_box.addButton(QDialogButtonBox.Ok)
        self.button_box.addButton(QDialogButtonBox.Cancel)
        
        # Style standard buttons
        for button in self.button_box.buttons():
            if self.button_box.buttonRole(button) in [QDialogButtonBox.AcceptRole, QDialogButtonBox.RejectRole]:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #007bff; color: white; border: none;
                        padding: 8px 16px; border-radius: 4px; font-weight: bold;
                    }
                    QPushButton:hover { background-color: #0056b3; }
                """)

    def _connect_signals(self):
        """Connect dialog signals."""
        # Time graph widget signals
        if hasattr(self.time_graph_widget, 'data_changed'):
            self.time_graph_widget.data_changed.connect(self._on_analysis_data_changed)
        
        # Dialog buttons
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.rejected.connect(self._restore_settings)
        
        # Time analysis widget signals
        self.time_graph_widget.data_changed.connect(self._on_analysis_data_changed)
        self.time_graph_widget.cursor_moved.connect(self._on_cursor_moved)
        self.time_graph_widget.range_selected.connect(self._on_range_selected)

    def update_data(self, df: vaex.DataFrame | None):
        """Update the dialog with new data."""
        print(f"🔍 DEBUG: TimeAnalysisDialog.update_data çağrıldı, df: {df}")
        self._pending_data = df
        
        if not self._ui_created:
            print("🔍 DEBUG: UI henüz yaratılmadı, veri beklemeye alındı.")
            return
        
        # Update the time analysis widget
        if hasattr(self, 'time_graph_widget'):
            self.time_graph_widget.update_data(df)
        
        print("🔍 DEBUG: TimeAnalysisDialog data update tamamlandı")

    def update_analysis(self):
        """Update the analysis based on current settings."""
        print("🔍 DEBUG: Updating time-series analysis")
        
        if not hasattr(self, 'time_graph_widget'):
            return
        
        # Apply current settings to the analysis widget
        settings = self.widget.settings
        
        # Update normalization state
        normalize = settings.get('normalize_data', False)
        if hasattr(self.time_graph_widget, 'normalize_btn'):
            self.time_graph_widget.normalize_btn.setChecked(normalize)
            if normalize != self.time_graph_widget.is_normalized:
                self.time_graph_widget._toggle_normalization()
        
        # Update cursor mode
        cursor_mode = settings.get('cursor_mode', 'none')
        if hasattr(self.time_graph_widget, 'cursor_manager'):
            self.time_graph_widget.cursor_manager.set_mode(cursor_mode)
        
        print("🔍 DEBUG: Analysis update completed")

    def export_results(self):
        """Export analysis results."""
        print("🔍 DEBUG: Exporting analysis results")
        # TODO: Implement export functionality
        # This could include:
        # - Statistics tables
        # - Plot images
        # - Raw data in selected ranges
        # - Analysis reports

    def _on_analysis_data_changed(self, data_manager):
        """Handle changes in analysis data."""
        print("🔍 DEBUG: Analysis data changed")
        # Update widget settings if needed
        
    def _on_cursor_moved(self, cursor_type: str, position: float):
        """Handle cursor movement events."""
        print(f"🔍 DEBUG: Cursor moved - {cursor_type}: {position:.3f}")
        # Could update status information or trigger additional analysis
        
    def _on_range_selected(self, range_tuple):
        """Handle range selection events."""
        start, end = range_tuple
        print(f"🔍 DEBUG: Range selected - {start:.3f} to {end:.3f}")
        # Could trigger range-specific analysis or updates

    def _restore_settings(self):
        """Restore original settings when dialog is cancelled."""
        self.widget.settings = self.original_settings
        logger.info("Time Analysis configuration cancelled, settings restored.")

    def closeEvent(self, event):
        """Handle the dialog closing."""
        self._restore_settings()
        super().closeEvent(event)