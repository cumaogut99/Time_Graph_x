"""
Parameters Panel - Signal selection and visibility management
OPTIMIZED: Virtual scrolling for large datasets (300-400+ items)
"""

import logging
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListView,
    QPushButton, QCheckBox, QGroupBox, QLineEdit, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, pyqtSignal, QAbstractListModel, QModelIndex, QVariant
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)


class SignalListModel(QAbstractListModel):
    """
    PERFORMANCE: Virtual scrolling model for large signal lists.
    Only visible items are rendered, dramatically improving performance with 300-400+ signals.
    """
    
    def __init__(self, signals: List[str], checked_signals: set, parent=None):
        super().__init__(parent)
        self._signals = signals
        self._checked = checked_signals
        self._filter_text = ""
        self._filtered_signals = signals.copy()
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of items."""
        return len(self._filtered_signals)
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data for the item."""
        if not index.isValid() or index.row() >= len(self._filtered_signals):
            return QVariant()
        
        signal_name = self._filtered_signals[index.row()]
        
        if role == Qt.DisplayRole:
            return signal_name
        elif role == Qt.CheckStateRole:
            return Qt.Checked if signal_name in self._checked else Qt.Unchecked
        
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        """Set data for the item."""
        if not index.isValid() or index.row() >= len(self._filtered_signals):
            return False
        
        if role == Qt.CheckStateRole:
            signal_name = self._filtered_signals[index.row()]
            if value == Qt.Checked:
                self._checked.add(signal_name)
            else:
                self._checked.discard(signal_name)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        
        return False
    
    def flags(self, index):
        """Return item flags."""
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
    
    def get_checked_signals(self) -> List[str]:
        """Return list of checked signals."""
        return list(self._checked)
    
    def set_filter(self, text: str):
        """Filter signals by text."""
        self.beginResetModel()
        self._filter_text = text.lower()
        if self._filter_text:
            self._filtered_signals = [s for s in self._signals if self._filter_text in s.lower()]
        else:
            self._filtered_signals = self._signals.copy()
        self.endResetModel()
    
    def select_all(self):
        """Select all filtered signals."""
        self.beginResetModel()
        self._checked.update(self._filtered_signals)
        self.endResetModel()
    
    def deselect_all(self):
        """Deselect all filtered signals."""
        self.beginResetModel()
        for signal in self._filtered_signals:
            self._checked.discard(signal)
        self.endResetModel()
    
    def invert_selection(self):
        """Invert selection of filtered signals."""
        self.beginResetModel()
        for signal in self._filtered_signals:
            if signal in self._checked:
                self._checked.discard(signal)
            else:
                self._checked.add(signal)
        self.endResetModel()


class ParametersPanel(QWidget):
    """Panel for parameter/signal selection and visibility management with virtual scrolling."""
    
    signals_changed = pyqtSignal(list)  # Emits list of selected signals

    def __init__(self, all_signals: List[str], visible_signals: List[str] = None, parent=None):
        super().__init__(parent)
        self.all_signals = all_signals if all_signals else []
        self.visible_signals = visible_signals if visible_signals else []
        
        # PERFORMANCE: Virtual scrolling model
        self._checked_set = set(self.visible_signals)
        self._model = SignalListModel(self.all_signals, self._checked_set, self)
        
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
                color: #ffffff;
                font-size: 12px;
                margin-bottom: 10px;
                padding: 8px;
            }
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Search bar
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
        layout.addWidget(self.search_bar)
        
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
        
        # PERFORMANCE: Signal list with virtual scrolling (QListView + Model)
        self.signal_list = QListView()
        self.signal_list.setModel(self._model)
        self.signal_list.setUniformItemSizes(True)  # PERFORMANCE: All items same height
        self.signal_list.setStyleSheet("""
            QListView {
                background: rgba(74, 144, 226, 0.1);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 4px;
                color: #e6f3ff;
                selection-background-color: rgba(74, 144, 226, 0.5);
            }
            QListView::item {
                padding: 8px;
                border-bottom: 1px solid rgba(74, 144, 226, 0.2);
            }
            QListView::item:hover {
                background: rgba(74, 144, 226, 0.2);
            }
        """)
        
        layout.addWidget(self.signal_list)
        
        # Statistics
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 11px;
                padding: 5px;
            }
        """)
        self._update_stats()
        layout.addWidget(self.stats_label)
        
    # REMOVED: _populate_signal_list() - Not needed with virtual scrolling model
            
    def _setup_connections(self):
        """Setup signal connections."""
        self.select_all_btn.clicked.connect(self._select_all)
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        self.invert_selection_btn.clicked.connect(self._invert_selection)
        self._model.dataChanged.connect(self._on_model_changed)
        self.search_bar.textChanged.connect(self._filter_signals)
        
    def _select_all(self):
        """Select all signals."""
        self._model.select_all()
        self._update_stats()
        self._emit_selection_changed()
        
    def _deselect_all(self):
        """Deselect all signals."""
        self._model.deselect_all()
        self._update_stats()
        self._emit_selection_changed()
        
    def _invert_selection(self):
        """Invert signal selection."""
        self._model.invert_selection()
        self._update_stats()
        self._emit_selection_changed()
        
    def _on_model_changed(self):
        """Handle model data change."""
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
            self.stats_label.setText(f"Showing {visible_count} of {len(self.all_signals)} signals (filtered)")
        else:
            self._update_stats()
        
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
