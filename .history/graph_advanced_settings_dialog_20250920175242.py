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
from parameter_filters_panel import ParameterFiltersPanel
from parameters_panel import ParametersPanel
from static_limits_panel import StaticLimitsPanel
from deviation_panel import DeviationPanel
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


class GraphAdvancedSettingsDialog(QDialog):
    """
    Advanced Graph Settings Dialog - Modern, Professional Interface
    
    Provides comprehensive configuration options for graph display and filtering.
    """
    
    # Signals for filter application
    range_filter_applied = pyqtSignal(dict)  # Emits filter conditions
    
    def __init__(self, graph_index: int, all_signals: List[str], visible_signals: List[str] = None, parent=None):
        super().__init__(parent)
        
        self.graph_index = graph_index
        self.all_signals = all_signals if all_signals else []
        self.visible_signals = visible_signals if visible_signals else []
        
        # Debug logging
        logger.debug(f"GraphAdvancedSettingsDialog constructor:")
        logger.debug(f"  - graph_index: {graph_index}")
        logger.debug(f"  - all_signals count: {len(all_signals) if all_signals else 0}")
        logger.debug(f"  - visible_signals count: {len(visible_signals) if visible_signals else 0}")
        
        self._setup_dialog()
        self._setup_ui()
        self._setup_connections()
        
        logger.debug(f"GraphAdvancedSettingsDialog initialized for graph {graph_index}")
        
    def _setup_dialog(self):
        """Setup dialog properties."""
        self.setWindowTitle(f"Graph {self.graph_index + 1} - Advanced Settings")
        self.setMinimumSize(900, 600)
        self.resize(1200, 650)  # Sağ panel için genişlik artırıldı
        
        # Window flags - minimize/maximize butonları için
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                          Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Modern space theme
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a2332, stop:0.5 #2d4a66, stop:1 #1a2332);
                color: #e6f3ff;
            }
        """)
        
    def _setup_ui(self):
        """Setup the main UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left sidebar
        self._create_sidebar(splitter)
        
        # Right content area
        self._create_main_content(splitter)
        
        # Set splitter proportions
        splitter.setSizes([220, 780])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        main_layout.addWidget(splitter)
        
        # Bottom buttons
        self._create_bottom_buttons(main_layout)
        
    def _create_sidebar(self, parent):
        """Create the left sidebar with navigation buttons."""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
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
        
    def _create_main_content(self, parent):
        """Create the main content area with stacked panels."""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Stacked widget for different panels
        self.stacked_widget = QStackedWidget()
        
        # Create and add panels
        self.parameters_panel = ParametersPanel(self.all_signals, self.visible_signals, self)
        self.parameter_filters_panel = ParameterFiltersPanel(self.graph_index, self.all_signals, self)
        self.static_limits_panel = StaticLimitsPanel(self.all_signals, self)
        self.deviation_panel = DeviationPanel(self.all_signals, self)
        
        self.stacked_widget.addWidget(self.parameters_panel)
        self.stacked_widget.addWidget(self.parameter_filters_panel)
        self.stacked_widget.addWidget(self.static_limits_panel)
        self.stacked_widget.addWidget(self.deviation_panel)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Set default selection
        self.parameters_btn.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)
        
        parent.addWidget(content_widget)
        
    def _create_bottom_buttons(self, parent_layout):
        """Create bottom dialog buttons."""
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        
        button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
                padding: 8px 16px;
                border: 1px solid rgba(74, 144, 226, 0.5);
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.2), stop:1 transparent);
                color: #e6f3ff;
                font-size: 12px;
                font-weight: 500;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.4), stop:1 rgba(74, 144, 226, 0.1));
                border-color: #4a90e2;
            }
        """)
        
        parent_layout.addWidget(button_box)
        
        # Store references
        self.ok_btn = button_box.button(QDialogButtonBox.Ok)
        self.cancel_btn = button_box.button(QDialogButtonBox.Cancel)
        self.apply_btn = button_box.button(QDialogButtonBox.Apply)
        
    def _setup_connections(self):
        """Setup signal connections."""
        # Navigation
        self.nav_buttons.buttonClicked.connect(self._on_nav_button_clicked)
        
        # Dialog buttons
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self._apply_settings)
        
        # Connect filter panel signals
        self.parameter_filters_panel.range_filter_applied.connect(self.range_filter_applied.emit)
        
    def _on_nav_button_clicked(self, button):
        """Handle navigation button clicks."""
        button_id = self.nav_buttons.id(button)
        self.stacked_widget.setCurrentIndex(button_id)
        
        # Log navigation for debugging
        panel_names = ["Parameters", "Range Filters", "Static Limits", "Deviation"]
        print(f"[DEBUG] Switched to {panel_names[button_id]} panel")
        
    def get_selected_signals(self):
        """Get list of selected signals from parameters panel."""
        return self.parameters_panel.get_selected_signals()
        
    def _apply_settings(self):
        """Apply current settings without closing dialog."""
        logger.info(f"Applied settings for graph {self.graph_index}")
        
    def get_all_settings(self):
        """Get all settings from all panels."""
        settings = {
            'graph_index': self.graph_index,
            'selected_signals': self.get_selected_signals(),
            'filters': self._get_filter_settings(),
            'limits': self._get_limit_settings(),
            'deviation': self._get_deviation_settings()
        }
        return settings
        
    def _get_filter_settings(self):
        """Get filter settings from the filters panel."""
        try:
            return self.parameter_filters_panel.get_range_filter_conditions()
        except:
            return {}
            
    def _get_limit_settings(self):
        """Get limit settings from the limits panel."""
        try:
            return self.static_limits_panel.get_limits_configuration()
        except:
            return {}
            
    def _get_deviation_settings(self):
        """Get deviation settings from the deviation panel."""
        try:
            return self.deviation_panel.get_deviation_settings()
        except:
            return {}
