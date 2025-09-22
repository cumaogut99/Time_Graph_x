"""
Parameters Panel - Signal selection and visibility management
"""

import logging
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
    QListWidgetItem, QPushButton, QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)


class ParametersPanel(QWidget):
    """Panel for parameter/signal selection and visibility management."""
    
    signals_changed = pyqtSignal(list)  # Emits list of selected signals

    def __init__(self, all_signals: List[str], visible_signals: List[str] = None, parent=None):
        super().__init__(parent)
        self.all_signals = all_signals if all_signals else []
        self.visible_signals = visible_signals if visible_signals else []
        
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self):
        """Setup the parameters panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Parameters")
        title.setStyleSheet("""
            QLabel {
                color: #e6f3ff;
                font-size: 18px;
                font-weight: 700;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(74, 144, 226, 0.3), stop:1 rgba(74, 144, 226, 0.1));
                border-radius: 6px;
                border: 1px solid rgba(74, 144, 226, 0.3);
            }
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Select which parameters/signals to display in the graph. Use the search bar to quickly find specific signals.")
        desc.setStyleSheet("""
            QLabel {
                color: rgba(230, 243, 255, 0.8);
                font-size: 12px;
                margin-bottom: 10px;
                padding: 8px;
            }
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search signals...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.1), stop:1 transparent);
                color: #e6f3ff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 rgba(74, 144, 226, 0.05));
            }
        """)
        search_layout.addWidget(self.search_bar)
        layout.addWidget(search_layout)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.deselect_all_btn = QPushButton("Deselect All")
        self.invert_selection_btn = QPushButton("Invert Selection")
        
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
        
        for btn in [self.select_all_btn, self.deselect_all_btn, self.invert_selection_btn]:
            btn.setStyleSheet(button_style)
        
        controls_layout.addWidget(self.select_all_btn)
        controls_layout.addWidget(self.deselect_all_btn)
        controls_layout.addWidget(self.invert_selection_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Signal list
        self.signal_list = QListWidget()
        self.signal_list.setStyleSheet("""
            QListWidget {
                background: rgba(74, 144, 226, 0.1);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 4px;
                color: #e6f3ff;
                selection-background-color: rgba(74, 144, 226, 0.5);
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(74, 144, 226, 0.2);
            }
            QListWidget::item:hover {
                background: rgba(74, 144, 226, 0.2);
            }
        """)
        
        # Populate signal list
        self._populate_signal_list()
        
        layout.addWidget(self.signal_list)
        
        # Statistics
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                color: rgba(230, 243, 255, 0.7);
                font-size: 11px;
                padding: 5px;
            }
        """)
        self._update_stats()
        layout.addWidget(self.stats_label)
        
    def _populate_signal_list(self):
        """Populate the signal list with checkable items."""
        self.signal_list.clear()
        
        for signal in self.all_signals:
            item = QListWidgetItem(signal)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if signal in self.visible_signals else Qt.Unchecked)
            self.signal_list.addItem(item)
            
    def _setup_connections(self):
        """Setup signal connections."""
        self.select_all_btn.clicked.connect(self._select_all)
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        self.invert_selection_btn.clicked.connect(self._invert_selection)
        self.signal_list.itemChanged.connect(self._on_item_changed)
        
    def _select_all(self):
        """Select all signals."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            item.setCheckState(Qt.Checked)
        self._update_stats()
        self._emit_selection_changed()
        
    def _deselect_all(self):
        """Deselect all signals."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            item.setCheckState(Qt.Unchecked)
        self._update_stats()
        self._emit_selection_changed()
        
    def _invert_selection(self):
        """Invert signal selection."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            current_state = item.checkState()
            new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
            item.setCheckState(new_state)
        self._update_stats()
        self._emit_selection_changed()
        
    def _on_item_changed(self, item):
        """Handle item check state change."""
        self._update_stats()
        self._emit_selection_changed()
        
    def _update_stats(self):
        """Update selection statistics."""
        total = self.signal_list.count()
        selected = len(self.get_selected_signals())
        self.stats_label.setText(f"Selected: {selected} / {total} signals")
        
    def _emit_selection_changed(self):
        """Emit signal when selection changes."""
        selected = self.get_selected_signals()
        self.signals_changed.emit(selected)
        
    def get_selected_signals(self) -> List[str]:
        """Get list of selected signals."""
        selected = []
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected
        
    def set_selected_signals(self, signals: List[str]):
        """Set which signals are selected."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            item.setCheckState(Qt.Checked if item.text() in signals else Qt.Unchecked)
        self._update_stats()
        
    def update_available_signals(self, signals: List[str]):
        """Update the list of available signals."""
        self.all_signals = signals
        selected = self.get_selected_signals()  # Preserve current selection
        self._populate_signal_list()
        self.set_selected_signals(selected)  # Restore selection where possible
