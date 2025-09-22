"""
Basic Deviation Panel - Simple and functional deviation analysis
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout,
    QDoubleSpinBox, QComboBox, QCheckBox, QSlider, QSpinBox, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)


class BasicDeviationPanel(QWidget):
    """Panel for basic deviation analysis with real backend functionality."""
    
    deviation_settings_changed = pyqtSignal(dict)  # Emits deviation configuration
    
    def __init__(self, all_signals: List[str] = None, parent=None):
        super().__init__(parent)
        self.all_signals = all_signals if all_signals else []
        
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self):
        """Setup the basic deviation analysis panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Basic Deviation Analysis")
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
        desc = QLabel("Simple deviation analysis for trend following and short-term fluctuation detection.")
        desc.setStyleSheet("""
            QLabel {
                color: rgba(230, 243, 255, 0.8);
                font-size: 12px;
                margin-bottom: 10px;
                padding: 8px;
                background: rgba(74, 144, 226, 0.1);
                border-radius: 6px;
                border: 1px solid rgba(74, 144, 226, 0.2);
            }
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Trend Analysis Group
        trend_group = QGroupBox("🎯 Trend Analysis")
        trend_group.setStyleSheet(self._get_group_style())
        trend_layout = QFormLayout(trend_group)
        
        # Enable trend following
        self.enable_trend = QCheckBox("Enable Trend Following")
        self.enable_trend.setStyleSheet("color: #e6f3ff;")
        self.enable_trend.setChecked(True)
        trend_layout.addRow(self.enable_trend)
        
        # Trend sensitivity
        self.trend_sensitivity = QSlider(Qt.Horizontal)
        self.trend_sensitivity.setRange(1, 5)
        self.trend_sensitivity.setValue(3)
        self.trend_label = QLabel("Medium (3)")
        self.trend_label.setStyleSheet("color: #e6f3ff; font-size: 11px;")
        
        trend_sens_layout = QHBoxLayout()
        trend_sens_layout.addWidget(self.trend_sensitivity)
        trend_sens_layout.addWidget(self.trend_label)
        trend_layout.addRow("Trend Sensitivity:", trend_sens_layout)
        
        layout.addWidget(trend_group)
        
        # Parameter Selection Group
        parameter_group = QGroupBox("📊 Parameter Selection")
        parameter_group.setStyleSheet(self._get_group_style())
        parameter_layout = QFormLayout(parameter_group)
        
        # Parameter selection
        self.parameter_combo = QComboBox()
        self.parameter_combo.addItem("All Parameters")
        for signal in self.all_signals:
            self.parameter_combo.addItem(signal)
        self.parameter_combo.setStyleSheet(self._get_combo_style())
        parameter_layout.addRow("Select Parameter:", self.parameter_combo)
        
        layout.addWidget(parameter_group)
        
        # Short-term Fluctuation Group
        fluctuation_group = QGroupBox("⚡ Short-term Fluctuation Detection")
        fluctuation_group.setStyleSheet(self._get_group_style())
        fluctuation_layout = QFormLayout(fluctuation_group)
        
        # Enable detection
        self.enable_fluctuation = QCheckBox("Enable Fluctuation Detection")
        self.enable_fluctuation.setStyleSheet("color: #e6f3ff;")
        self.enable_fluctuation.setChecked(True)
        fluctuation_layout.addRow(self.enable_fluctuation)
        
        # Sample window (Son X parametre)
        self.sample_window = QSpinBox()
        self.sample_window.setRange(5, 100)
        self.sample_window.setValue(20)
        self.sample_window.setSuffix(" samples")
        self.sample_window.setStyleSheet(self._get_spinbox_style())
        fluctuation_layout.addRow("Sample Window:", self.sample_window)
        
        # Deviation threshold (%Y sapma)
        self.deviation_threshold = QDoubleSpinBox()
        self.deviation_threshold.setRange(1.0, 50.0)
        self.deviation_threshold.setValue(10.0)
        self.deviation_threshold.setSuffix("%")
        self.deviation_threshold.setDecimals(1)
        self.deviation_threshold.setStyleSheet(self._get_spinbox_style())
        fluctuation_layout.addRow("Deviation Threshold:", self.deviation_threshold)
        
        # Highlight on graph
        self.highlight_deviations = QCheckBox("Highlight Deviations on Graph")
        self.highlight_deviations.setStyleSheet("color: #e6f3ff;")
        self.highlight_deviations.setChecked(True)
        fluctuation_layout.addRow(self.highlight_deviations)
        
        # Red highlighting for threshold exceedance
        self.red_highlighting = QCheckBox("Red Highlighting for Threshold Exceedance")
        self.red_highlighting.setStyleSheet("color: #e6f3ff;")
        self.red_highlighting.setChecked(True)
        fluctuation_layout.addRow(self.red_highlighting)
        
        layout.addWidget(fluctuation_group)
        
        # Visual Settings Group
        visual_group = QGroupBox("📈 Visual Settings")
        visual_group.setStyleSheet(self._get_group_style())
        visual_layout = QFormLayout(visual_group)
        
        # Show deviation bands
        self.show_bands = QCheckBox("Show Deviation Bands")
        self.show_bands.setStyleSheet("color: #e6f3ff;")
        self.show_bands.setChecked(True)
        visual_layout.addRow(self.show_bands)
        
        # Band transparency
        self.band_transparency = QSlider(Qt.Horizontal)
        self.band_transparency.setRange(10, 80)
        self.band_transparency.setValue(30)
        self.transparency_label = QLabel("30%")
        self.transparency_label.setStyleSheet("color: #e6f3ff; font-size: 11px;")
        
        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(self.band_transparency)
        transparency_layout.addWidget(self.transparency_label)
        visual_layout.addRow("Band Transparency:", transparency_layout)
        
        layout.addWidget(visual_group)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Settings")
        self.reset_btn = QPushButton("Reset to Defaults")
        
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
        """
        
        self.apply_btn.setStyleSheet(button_style)
        self.reset_btn.setStyleSheet(button_style)
        
        controls_layout.addWidget(self.apply_btn)
        controls_layout.addWidget(self.reset_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addStretch()
        
    def _setup_connections(self):
        """Setup signal connections."""
        # Trend settings
        self.enable_trend.toggled.connect(self._on_settings_changed)
        self.trend_sensitivity.valueChanged.connect(self._on_trend_sensitivity_changed)
        
        # Parameter settings
        self.parameter_combo.currentTextChanged.connect(self._on_settings_changed)
        
        # Fluctuation settings
        self.enable_fluctuation.toggled.connect(self._on_settings_changed)
        self.sample_window.valueChanged.connect(self._on_settings_changed)
        self.deviation_threshold.valueChanged.connect(self._on_settings_changed)
        self.highlight_deviations.toggled.connect(self._on_settings_changed)
        self.red_highlighting.toggled.connect(self._on_settings_changed)
        
        # Visual settings
        self.show_bands.toggled.connect(self._on_settings_changed)
        self.band_transparency.valueChanged.connect(self._on_transparency_changed)
        
        # Control buttons
        self.apply_btn.clicked.connect(self._apply_settings)
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        
    def _on_trend_sensitivity_changed(self, value):
        """Handle trend sensitivity slider change."""
        sensitivity_labels = {
            1: "Very Low (1)", 2: "Low (2)", 3: "Medium (3)", 
            4: "High (4)", 5: "Very High (5)"
        }
        self.trend_label.setText(sensitivity_labels.get(value, f"({value})"))
        self._on_settings_changed()
        
    def _on_transparency_changed(self, value):
        """Handle transparency slider change."""
        self.transparency_label.setText(f"{value}%")
        self._on_settings_changed()
        
    def _on_settings_changed(self):
        """Handle any setting change."""
        settings = self.get_deviation_settings()
        self.deviation_settings_changed.emit(settings)
        
    def _apply_settings(self):
        """Apply current settings."""
        settings = self.get_deviation_settings()
        logger.info(f"Applied basic deviation settings: {settings}")
        self.deviation_settings_changed.emit(settings)
        
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.enable_trend.setChecked(True)
        self.trend_sensitivity.setValue(3)
        self.enable_fluctuation.setChecked(True)
        self.sample_window.setValue(20)
        self.deviation_threshold.setValue(10.0)
        self.highlight_deviations.setChecked(True)
        self.show_bands.setChecked(True)
        self.band_transparency.setValue(30)
        
    def get_deviation_settings(self) -> Dict[str, Any]:
        """Get current basic deviation settings."""
        return {
            'type': 'basic',
            'selected_parameter': self.parameter_combo.currentText(),
            'trend_analysis': {
                'enabled': self.enable_trend.isChecked(),
                'sensitivity': self.trend_sensitivity.value()
            },
            'fluctuation_detection': {
                'enabled': self.enable_fluctuation.isChecked(),
                'sample_window': self.sample_window.value(),
                'threshold_percent': self.deviation_threshold.value(),
                'highlight_on_graph': self.highlight_deviations.isChecked(),
                'red_highlighting': self.red_highlighting.isChecked()
            },
            'visual_settings': {
                'show_bands': self.show_bands.isChecked(),
                'band_transparency': self.band_transparency.value()
            }
        }
        
    def calculate_deviation_for_signal(self, signal_data: np.ndarray, signal_name: str) -> Dict[str, Any]:
        """
        Calculate deviation for a signal based on current settings.
        This is the real backend functionality.
        """
        if len(signal_data) == 0:
            return {'deviations': [], 'bands': [], 'alerts': []}
            
        settings = self.get_deviation_settings()
        results = {
            'deviations': [],
            'bands': [],
            'alerts': [],
            'trend_line': []
        }
        
        # Trend Analysis
        if settings['trend_analysis']['enabled']:
            trend_line = self._calculate_trend_line(signal_data, settings['trend_analysis']['sensitivity'])
            results['trend_line'] = trend_line
            
        # Fluctuation Detection
        if settings['fluctuation_detection']['enabled']:
            window_size = settings['fluctuation_detection']['sample_window']
            threshold_percent = settings['fluctuation_detection']['threshold_percent']
            
            deviations, alerts = self._detect_fluctuations(
                signal_data, window_size, threshold_percent
            )
            results['deviations'] = deviations
            results['alerts'] = alerts
            
        # Deviation Bands
        if settings['visual_settings']['show_bands']:
            bands = self._calculate_deviation_bands(signal_data, settings)
            results['bands'] = bands
            
        return results
        
    def _calculate_trend_line(self, data: np.ndarray, sensitivity: int) -> List[float]:
        """Calculate trend line based on sensitivity."""
        if len(data) < 2:
            return data.tolist()
            
        # Simple linear regression for trend
        x = np.arange(len(data))
        coeffs = np.polyfit(x, data, 1)
        trend_line = np.polyval(coeffs, x)
        
        # Apply sensitivity smoothing
        if sensitivity <= 2:  # Low sensitivity - more smoothing
            window = min(len(data) // 4, 20)
        elif sensitivity >= 4:  # High sensitivity - less smoothing
            window = min(len(data) // 10, 5)
        else:  # Medium sensitivity
            window = min(len(data) // 8, 10)
            
        if window > 1:
            # Apply moving average smoothing
            trend_smoothed = np.convolve(trend_line, np.ones(window)/window, mode='same')
            return trend_smoothed.tolist()
        
        return trend_line.tolist()
        
    def _detect_fluctuations(self, data: np.ndarray, window_size: int, threshold_percent: float) -> tuple:
        """Detect short-term fluctuations."""
        deviations = []
        alerts = []
        
        if len(data) < window_size:
            return deviations, alerts
            
        for i in range(window_size, len(data)):
            # Get last window_size samples
            window_data = data[i-window_size:i]
            window_mean = np.mean(window_data)
            current_value = data[i]
            
            # Calculate percentage deviation
            if window_mean != 0:
                deviation_percent = abs((current_value - window_mean) / window_mean) * 100
                deviations.append(deviation_percent)
                
                # Check if it exceeds threshold
                if deviation_percent > threshold_percent:
                    alerts.append({
                        'index': i,
                        'value': current_value,
                        'expected': window_mean,
                        'deviation_percent': deviation_percent
                    })
            else:
                deviations.append(0.0)
                
        return deviations, alerts
        
    def _calculate_deviation_bands(self, data: np.ndarray, settings: Dict) -> Dict[str, List[float]]:
        """Calculate deviation bands for visualization."""
        if len(data) < 10:
            return {'upper': [], 'lower': []}
            
        window_size = settings['fluctuation_detection']['sample_window']
        threshold_percent = settings['fluctuation_detection']['threshold_percent']
        
        upper_band = []
        lower_band = []
        
        for i in range(len(data)):
            start_idx = max(0, i - window_size + 1)
            window_data = data[start_idx:i+1]
            
            if len(window_data) > 0:
                mean_val = np.mean(window_data)
                threshold_val = mean_val * (threshold_percent / 100)
                
                upper_band.append(mean_val + threshold_val)
                lower_band.append(mean_val - threshold_val)
            else:
                upper_band.append(data[i])
                lower_band.append(data[i])
                
        return {'upper': upper_band, 'lower': lower_band}
        
    def update_available_signals(self, signals: List[str]):
        """Update the list of available signals."""
        self.all_signals = signals
        
        # Update parameter combo box
        current_selection = self.parameter_combo.currentText()
        self.parameter_combo.clear()
        self.parameter_combo.addItem("All Parameters")
        for signal in signals:
            self.parameter_combo.addItem(signal)
            
        # Restore selection if it still exists
        index = self.parameter_combo.findText(current_selection)
        if index >= 0:
            self.parameter_combo.setCurrentIndex(index)
        
    def _get_group_style(self) -> str:
        """Get consistent group box styling."""
        return """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #e6f3ff;
                border: 2px solid rgba(74, 144, 226, 0.3);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.05), stop:1 transparent);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #4a90e2;
                font-weight: 700;
            }
        """
        
    def _get_spinbox_style(self) -> str:
        """Get spinbox styling."""
        return """
            QSpinBox, QDoubleSpinBox {
                background: rgba(74, 144, 226, 0.1);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 4px;
                padding: 4px 8px;
                color: #e6f3ff;
                font-size: 12px;
            }
            QSpinBox:hover, QDoubleSpinBox:hover {
                border-color: #4a90e2;
                background: rgba(74, 144, 226, 0.2);
            }
        """
