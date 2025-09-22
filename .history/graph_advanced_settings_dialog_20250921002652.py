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
from basic_deviation_panel import BasicDeviationPanel
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
    
    def __init__(self, graph_index: int, all_signals: List[str], visible_signals: List[str] = None, 
                 saved_filter_data: dict = None, saved_limits_data: dict = None, parent=None):
        super().__init__(parent)
        
        self.graph_index = graph_index
        self.all_signals = all_signals if all_signals else []
        self.visible_signals = visible_signals if visible_signals else []
        self.saved_filter_data = saved_filter_data  # Store saved filter data
        self.saved_limits_data = saved_limits_data  # Store saved limits data
        
        # Debug logging
        logger.debug(f"GraphAdvancedSettingsDialog constructor:")
        logger.debug(f"  - graph_index: {graph_index}")
        logger.debug(f"  - all_signals count: {len(all_signals) if all_signals else 0}")
        logger.debug(f"  - visible_signals count: {len(visible_signals) if visible_signals else 0}")
        logger.debug(f"  - saved_filter_data: {saved_filter_data is not None}")
        
        self._setup_dialog()
        self._setup_ui()
        self._setup_connections()
        
        # Load saved filter data if available
        self._load_saved_filter_data()
        
        # Load saved limits data if available
        self._load_saved_limits_data()
        
        logger.debug(f"GraphAdvancedSettingsDialog initialized for graph {graph_index}")
        
    def _setup_dialog(self):
        """Setup dialog properties."""
        self.setWindowTitle(f"Graph {self.graph_index + 1} - Advanced Settings")
        self.setMinimumSize(900, 600)
        self.resize(1200, 650)  # Sağ panel için genişlik artırıldı
        
        # Window flags - taskbar'da görünmesi ve minimize/maximize butonları için
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                          Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint |
                          Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        
        # Taskbar'da görünmesi için
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setWindowModality(Qt.NonModal)  # Non-modal dialog
        
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
        
        # Middle content area
        self._create_main_content(splitter)
        
        # Right summary panel
        self._create_summary_panel(splitter)
        
        # Set splitter proportions: sidebar(220) + content(650) + summary(330)
        splitter.setSizes([220, 650, 330])
        splitter.setCollapsible(0, False)  # Sidebar
        splitter.setCollapsible(1, False)  # Main content
        splitter.setCollapsible(2, True)   # Summary panel (collapsible)
        
        main_layout.addWidget(splitter)
        
        # Bottom buttons
        self._create_bottom_buttons(main_layout)
        
    def _create_sidebar(self, parent):
        """Create the left sidebar with navigation buttons."""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget {
                background: #2d4a66;
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
        self.basic_deviation_btn = ModernSidebarButton("Basic Deviation", "📊")
        self.advanced_deviation_btn = ModernSidebarButton("Advanced Deviation", "📈")
        
        buttons = [self.parameters_btn, self.filters_btn, self.limits_btn, self.basic_deviation_btn, self.advanced_deviation_btn]
        
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
        self.basic_deviation_panel = BasicDeviationPanel(self.all_signals, self)
        self.advanced_deviation_panel = DeviationPanel(self.all_signals, self)
        
        self.stacked_widget.addWidget(self.parameters_panel)
        self.stacked_widget.addWidget(self.parameter_filters_panel)
        self.stacked_widget.addWidget(self.static_limits_panel)
        self.stacked_widget.addWidget(self.basic_deviation_panel)
        self.stacked_widget.addWidget(self.advanced_deviation_panel)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Set default selection
        self.parameters_btn.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)
        
        parent.addWidget(content_widget)
        
    def _create_summary_panel(self, parent):
        """Create the right summary panel."""
        summary_widget = QWidget()
        summary_widget.setFixedWidth(330)
        summary_widget.setStyleSheet("""
            QWidget {
                background: #2d4a66;
                border-left: 2px solid rgba(74, 144, 226, 0.5);
            }
        """)
        
        layout = QVBoxLayout(summary_widget)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📋 Current Settings")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #e6f3ff;
                padding: 8px 0;
                border-bottom: 2px solid rgba(74, 144, 226, 0.5);
                margin-bottom: 12px;
            }
        """)
        layout.addWidget(title)
        
        # Scroll area for summary content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        
        # Summary content widget
        self.summary_content = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_content)
        self.summary_layout.setContentsMargins(5, 5, 5, 5)
        self.summary_layout.setSpacing(10)
        
        # Initial empty state
        self._update_summary_content()
        
        scroll_area.setWidget(self.summary_content)
        layout.addWidget(scroll_area)
        
        parent.addWidget(summary_widget)
        
    def _update_summary_content(self):
        """Update the summary panel content based on current tab."""
        # Clear existing content
        for i in reversed(range(self.summary_layout.count())):
            child = self.summary_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 0:  # Parameters
            self._show_parameters_summary()
        elif current_index == 1:  # Range Filters
            self._show_filters_summary()
        elif current_index == 2:  # Static Limits
            self._show_limits_summary()
        elif current_index == 3:  # Basic Deviation
            self._show_basic_deviation_summary()
        elif current_index == 4:  # Advanced Deviation
            self._show_advanced_deviation_summary()
        
        # Add stretch at the end
        self.summary_layout.addStretch()
        
    def _show_parameters_summary(self):
        """Show parameters summary."""
        group = QGroupBox("📊 Selected Parameters")
        group.setStyleSheet(self._get_summary_group_style())
        layout = QVBoxLayout(group)
        
        selected_signals = self.parameters_panel.get_selected_signals()
        
        if selected_signals:
            for signal in selected_signals:
                label = QLabel(f"• {signal}")
                label.setStyleSheet("color: #e6f3ff; font-size: 13px; padding: 2px;")
                label.setWordWrap(True)
                layout.addWidget(label)
        else:
            label = QLabel("No parameters selected")
            label.setStyleSheet("color: #888; font-style: italic; font-size: 13px;")
            layout.addWidget(label)
        
        self.summary_layout.addWidget(group)
        
    def _show_filters_summary(self):
        """Show range filters summary."""
        group = QGroupBox("🔍 Active Filters")
        group.setStyleSheet(self._get_summary_group_style())
        layout = QVBoxLayout(group)
        
        try:
            filter_conditions = self.parameter_filters_panel.get_range_filter_conditions()
            conditions = filter_conditions.get('conditions', [])
            
            if conditions:
                for i, condition in enumerate(conditions):
                    param_name = condition.get('parameter', 'Unknown')
                    ranges = condition.get('ranges', [])
                    
                    # Parameter name
                    param_label = QLabel(f"📋 {param_name}")
                    param_label.setStyleSheet("color: #4a90e2; font-weight: bold; font-size: 13px; margin-top: 5px;")
                    layout.addWidget(param_label)
                    
                    # Ranges
                    for range_info in ranges:
                        range_text = f"  {range_info.get('operator', '')} {range_info.get('value', '')}"
                        range_label = QLabel(range_text)
                        range_label.setStyleSheet("color: #e6f3ff; font-size: 12px; padding-left: 10px;")
                        layout.addWidget(range_label)
                        
                # Mode info
                mode = filter_conditions.get('mode', 'segmented')
                mode_label = QLabel(f"Mode: {mode.title()}")
                mode_label.setStyleSheet("color: #888; font-size: 12px; margin-top: 8px; font-style: italic;")
                layout.addWidget(mode_label)
            else:
                label = QLabel("No filters applied")
                label.setStyleSheet("color: #888; font-style: italic; font-size: 13px;")
                layout.addWidget(label)
        except:
            label = QLabel("Filter info unavailable")
            label.setStyleSheet("color: #888; font-style: italic; font-size: 13px;")
            layout.addWidget(label)
        
        self.summary_layout.addWidget(group)
        
    def _show_limits_summary(self):
        """Show static limits summary."""
        group = QGroupBox("⚠️ Static Limits")
        group.setStyleSheet(self._get_summary_group_style())
        layout = QVBoxLayout(group)
        
        try:
            limits_config = self.static_limits_panel.get_limits_configuration()
            
            if limits_config:
                for signal_name, limits in limits_config.items():
                    # Signal name
                    signal_label = QLabel(f"📋 {signal_name}")
                    signal_label.setStyleSheet("color: #4a90e2; font-weight: bold; font-size: 13px; margin-top: 5px;")
                    layout.addWidget(signal_label)
                    
                    # Warning limits
                    if limits.get('warning_min') != 0 or limits.get('warning_max') != 0:
                        warning_text = f"  ⚠️ Warning: {limits.get('warning_min', 0):.2f} - {limits.get('warning_max', 0):.2f}"
                        warning_label = QLabel(warning_text)
                        warning_label.setStyleSheet("color: #ffa500; font-size: 12px; padding-left: 10px;")
                        layout.addWidget(warning_label)
            else:
                label = QLabel("No limits configured")
                label.setStyleSheet("color: #888; font-style: italic; font-size: 13px;")
                layout.addWidget(label)
        except Exception as e:
            label = QLabel("Limits info unavailable")
            label.setStyleSheet("color: #888; font-style: italic; font-size: 13px;")
            layout.addWidget(label)
        
        self.summary_layout.addWidget(group)
        
    def _show_deviation_summary(self):
        """Show deviation summary."""
        group = QGroupBox("📈 Deviation Settings")
        group.setStyleSheet(self._get_summary_group_style())
        layout = QVBoxLayout(group)
        
        try:
            deviation_settings = self.deviation_panel.get_deviation_settings()
            
            # Global settings
            global_settings = deviation_settings.get('global', {})
            if global_settings:
                # Analysis method
                method_label = QLabel(f"Method: {global_settings.get('analysis_method', 'N/A')}")
                method_label.setStyleSheet("color: #e6f3ff; font-size: 13px; font-weight: bold;")
                layout.addWidget(method_label)
                
                # Window size and sensitivity
                window_label = QLabel(f"Window: {global_settings.get('window_size', 0)} samples")
                window_label.setStyleSheet("color: #e6f3ff; font-size: 12px;")
                layout.addWidget(window_label)
                
                sensitivity_label = QLabel(f"Sensitivity: {global_settings.get('sensitivity', 0)}%")
                sensitivity_label.setStyleSheet("color: #e6f3ff; font-size: 12px;")
                layout.addWidget(sensitivity_label)
                
                # Outlier detection
                if global_settings.get('outlier_detection', False):
                    outlier_label = QLabel(f"Outlier Detection: Z-score > {global_settings.get('zscore_threshold', 0):.1f}")
                    outlier_label.setStyleSheet("color: #ffa500; font-size: 12px;")
                    layout.addWidget(outlier_label)
            
            # Signal-specific settings
            signal_settings = deviation_settings.get('signals', {})
            if signal_settings:
                signals_label = QLabel(f"Active Signals: {len(signal_settings)}")
                signals_label.setStyleSheet("color: #4a90e2; font-weight: bold; font-size: 13px; margin-top: 8px;")
                layout.addWidget(signals_label)
                
                for signal_name, settings in list(signal_settings.items())[:3]:  # Show max 3 signals
                    signal_text = f"• {signal_name}: {settings.get('baseline_method', 'N/A')}"
                    signal_label = QLabel(signal_text)
                    signal_label.setStyleSheet("color: #e6f3ff; font-size: 12px; padding-left: 10px;")
                    signal_label.setWordWrap(True)
                    layout.addWidget(signal_label)
                
                if len(signal_settings) > 3:
                    more_label = QLabel(f"... and {len(signal_settings) - 3} more")
                    more_label.setStyleSheet("color: #888; font-size: 12px; font-style: italic; padding-left: 10px;")
                    layout.addWidget(more_label)
            else:
                label = QLabel("No deviation analysis configured")
                label.setStyleSheet("color: #888; font-style: italic; font-size: 13px;")
                layout.addWidget(label)
        except Exception as e:
            label = QLabel("Deviation info unavailable")
            label.setStyleSheet("color: #888; font-style: italic; font-size: 13px;")
            layout.addWidget(label)
        
        self.summary_layout.addWidget(group)
        
    def _get_summary_group_style(self):
        """Get styling for summary group boxes."""
        return """
            QGroupBox {
                font-weight: 600;
                font-size: 12px;
                color: #e6f3ff;
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.1), stop:1 transparent);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                color: #4a90e2;
                font-weight: 700;
            }
        """
        
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
        
        # Connect panel change signals to update summary
        self.parameters_panel.signals_changed.connect(self._on_parameters_changed)
        
        # Connect other panel signals if they exist
        if hasattr(self.static_limits_panel, 'limits_changed'):
            self.static_limits_panel.limits_changed.connect(self._on_limits_changed)
        if hasattr(self.deviation_panel, 'deviation_settings_changed'):
            self.deviation_panel.deviation_settings_changed.connect(self._on_deviation_changed)
        
    def _on_nav_button_clicked(self, button):
        """Handle navigation button clicks."""
        button_id = self.nav_buttons.id(button)
        self.stacked_widget.setCurrentIndex(button_id)
        
        # Update summary panel
        self._update_summary_content()
        
        # Log navigation for debugging
        panel_names = ["Parameters", "Range Filters", "Static Limits", "Deviation"]
        print(f"[DEBUG] Switched to {panel_names[button_id]} panel")
        
    def _on_parameters_changed(self, selected_signals):
        """Handle parameters panel changes."""
        # Update summary if parameters panel is active
        if self.stacked_widget.currentIndex() == 0:
            self._update_summary_content()
            
    def _on_limits_changed(self, limits_data):
        """Handle static limits panel changes."""
        # Update summary if limits panel is active
        if self.stacked_widget.currentIndex() == 2:
            self._update_summary_content()
            
    def _on_deviation_changed(self, deviation_data):
        """Handle deviation panel changes."""
        # Update summary if deviation panel is active
        if self.stacked_widget.currentIndex() == 3:
            self._update_summary_content()
            
    def _load_saved_filter_data(self):
        """Load saved filter data into the panels."""
        if self.saved_filter_data:
            try:
                # Load range filter data
                if 'conditions' in self.saved_filter_data or 'mode' in self.saved_filter_data:
                    self.parameter_filters_panel.set_range_filter_conditions(self.saved_filter_data)
                    logger.info(f"Loaded saved filter data for graph {self.graph_index}")
                    
                    # Update summary panel to reflect loaded data
                    self._update_summary_content()
                    
            except Exception as e:
                logger.error(f"Error loading saved filter data: {e}")
    
    def _load_saved_limits_data(self):
        """Load saved limits data into the static limits panel."""
        if self.saved_limits_data:
            try:
                self.static_limits_panel.set_limits_configuration(self.saved_limits_data)
                logger.info(f"Loaded saved limits data for graph {self.graph_index}")
                
                # Update summary panel to reflect loaded data
                self._update_summary_content()
                
            except Exception as e:
                logger.error(f"Error loading saved limits data: {e}")
        
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
