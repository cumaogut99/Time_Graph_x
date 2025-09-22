"""
Status Bar Manager for Time Graph Widget
Displays CPU, RAM, GPU usage and progress indicators
"""

import logging
import psutil
import time
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QProgressBar, 
    QFrame, QVBoxLayout, QSizePolicy, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal as Signal
from PyQt5.QtGui import QFont, QPalette

logger = logging.getLogger(__name__)

class SystemMonitorThread(QThread):
    """Background thread for monitoring system resources."""
    
    # Signals for resource updates
    cpu_usage_updated = Signal(float)  # CPU percentage
    ram_usage_updated = Signal(float, float, float)  # used_gb, total_gb, percentage
    gpu_usage_updated = Signal(float)  # GPU percentage (if available)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.update_interval = 1.0  # Update every 1 second
        
    def run(self):
        """Main monitoring loop."""
        self.running = True
        logger.info("System monitor thread started")
        
        while self.running:
            try:
                # CPU Usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.cpu_usage_updated.emit(cpu_percent)
                
                # RAM Usage
                memory = psutil.virtual_memory()
                used_gb = memory.used / (1024**3)  # Convert to GB
                total_gb = memory.total / (1024**3)
                ram_percent = memory.percent
                self.ram_usage_updated.emit(used_gb, total_gb, ram_percent)
                
                # GPU Usage (try to get if available)
                try:
                    import GPUtil
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu_percent = gpus[0].load * 100
                        self.gpu_usage_updated.emit(gpu_percent)
                    else:
                        self.gpu_usage_updated.emit(0.0)
                except ImportError:
                    # GPUtil not available, emit 0
                    self.gpu_usage_updated.emit(0.0)
                except Exception as e:
                    logger.debug(f"GPU monitoring error: {e}")
                    self.gpu_usage_updated.emit(0.0)
                
                # Sleep for update interval
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        logger.info("System monitor thread stopped")

class StatusBarManager(QStatusBar):
    """Manages the status bar at the bottom of the main window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # System monitoring
        self.monitor_thread = SystemMonitorThread()
        
        # Progress tracking
        self.current_operation = ""
        self.operation_progress = 0
        
        self._setup_ui()
        self._setup_connections()
        self._start_monitoring()
        
    def _setup_ui(self):
        """Setup the status bar UI."""
        # Create main widget to hold all components
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Left side - System resources
        self._create_resource_indicators(layout)
        
        # Spacer
        layout.addStretch()
        
        # Right side - Operation progress
        self._create_progress_indicator(layout)
        
        # Add the main widget to status bar
        self.addPermanentWidget(main_widget, 1)
        
        # Apply styling
        self._apply_styling()
        
    def _create_resource_indicators(self, layout):
        """Create CPU, RAM, GPU usage indicators."""
        
        # CPU Indicator
        cpu_frame = self._create_resource_frame("CPU", "🖥️")
        self.cpu_label = cpu_frame.findChild(QLabel, "value_label")
        self.cpu_bar = cpu_frame.findChild(QProgressBar, "progress_bar")
        layout.addWidget(cpu_frame)
        
        # RAM Indicator  
        ram_frame = self._create_resource_frame("RAM", "🧠")
        self.ram_label = ram_frame.findChild(QLabel, "value_label")
        self.ram_bar = ram_frame.findChild(QProgressBar, "progress_bar")
        layout.addWidget(ram_frame)
        
        # GPU Indicator
        gpu_frame = self._create_resource_frame("GPU", "🎮")
        self.gpu_label = gpu_frame.findChild(QLabel, "value_label")
        self.gpu_bar = gpu_frame.findChild(QProgressBar, "progress_bar")
        layout.addWidget(gpu_frame)
        
    def _create_resource_frame(self, name: str, icon: str) -> QFrame:
        """Create a frame for a single resource indicator."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        frame.setLineWidth(1)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(5)
        
        # Icon and name
        icon_label = QLabel(f"{icon} {name}:")
        icon_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(icon_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setObjectName("progress_bar")
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setFixedSize(60, 16)
        progress_bar.setTextVisible(False)
        layout.addWidget(progress_bar)
        
        # Value label
        value_label = QLabel("0%")
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("Arial", 8))
        value_label.setMinimumWidth(35)
        layout.addWidget(value_label)
        
        return frame
        
    def _create_progress_indicator(self, layout):
        """Create operation progress indicator."""
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        progress_frame.setLineWidth(1)
        
        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(8, 4, 8, 4)
        progress_layout.setSpacing(8)
        
        # Operation label
        self.operation_label = QLabel("⚡ Ready")
        self.operation_label.setFont(QFont("Arial", 9, QFont.Bold))
        progress_layout.addWidget(self.operation_label)
        
        # Progress bar
        self.operation_progress_bar = QProgressBar()
        self.operation_progress_bar.setRange(0, 100)
        self.operation_progress_bar.setValue(0)
        self.operation_progress_bar.setFixedSize(120, 16)
        self.operation_progress_bar.setVisible(False)
        progress_layout.addWidget(self.operation_progress_bar)
        
        layout.addWidget(progress_frame)
        
    def _apply_styling(self):
        """Apply styling to the status bar."""
        self.setStyleSheet("""
            StatusBarManager {
                background-color: #2b2b2b;
                border-top: 1px solid #555;
                color: white;
            }
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
                border: none;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 2px;
                background-color: #2b2b2b;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 2px;
            }
            QProgressBar[value="0"] {
                background-color: #2b2b2b;
            }
        """)
        
    def _setup_connections(self):
        """Setup signal connections."""
        self.monitor_thread.cpu_usage_updated.connect(self._update_cpu_usage)
        self.monitor_thread.ram_usage_updated.connect(self._update_ram_usage)
        self.monitor_thread.gpu_usage_updated.connect(self._update_gpu_usage)
        
    def _start_monitoring(self):
        """Start system monitoring."""
        try:
            self.monitor_thread.start()
            logger.info("System monitoring started")
        except Exception as e:
            logger.error(f"Failed to start system monitoring: {e}")
            
    def _update_cpu_usage(self, cpu_percent: float):
        """Update CPU usage display."""
        try:
            self.cpu_bar.setValue(int(cpu_percent))
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            
            # Color coding based on usage
            if cpu_percent > 80:
                color = "#ff4444"  # Red
            elif cpu_percent > 60:
                color = "#ffaa00"  # Orange
            else:
                color = "#4a90e2"  # Blue
                
            self.cpu_bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
        except Exception as e:
            logger.debug(f"Error updating CPU usage: {e}")
            
    def _update_ram_usage(self, used_gb: float, total_gb: float, ram_percent: float):
        """Update RAM usage display."""
        try:
            self.ram_bar.setValue(int(ram_percent))
            self.ram_label.setText(f"{used_gb:.1f}/{total_gb:.1f}GB")
            
            # Color coding based on usage
            if ram_percent > 85:
                color = "#ff4444"  # Red
            elif ram_percent > 70:
                color = "#ffaa00"  # Orange
            else:
                color = "#4a90e2"  # Blue
                
            self.ram_bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
        except Exception as e:
            logger.debug(f"Error updating RAM usage: {e}")
            
    def _update_gpu_usage(self, gpu_percent: float):
        """Update GPU usage display."""
        try:
            self.gpu_bar.setValue(int(gpu_percent))
            if gpu_percent > 0:
                self.gpu_label.setText(f"{gpu_percent:.1f}%")
            else:
                self.gpu_label.setText("N/A")
                
            # Color coding based on usage
            if gpu_percent > 80:
                color = "#ff4444"  # Red
            elif gpu_percent > 60:
                color = "#ffaa00"  # Orange
            else:
                color = "#4a90e2"  # Blue
                
            self.gpu_bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
        except Exception as e:
            logger.debug(f"Error updating GPU usage: {e}")
    
    def set_operation(self, operation_name: str, progress: int = 0):
        """Set current operation and progress."""
        try:
            self.current_operation = operation_name
            self.operation_progress = progress
            
            if operation_name and operation_name.lower() != "ready":
                self.operation_label.setText(f"⚙️ {operation_name}")
                self.operation_progress_bar.setValue(progress)
                self.operation_progress_bar.setVisible(True)
            else:
                self.operation_label.setText("⚡ Ready")
                self.operation_progress_bar.setVisible(False)
                
            logger.debug(f"Operation set: {operation_name} ({progress}%)")
        except Exception as e:
            logger.error(f"Error setting operation: {e}")
    
    def update_progress(self, progress: int):
        """Update current operation progress."""
        try:
            self.operation_progress = progress
            self.operation_progress_bar.setValue(progress)
            
            if progress >= 100:
                # Operation completed
                QTimer.singleShot(1000, lambda: self.set_operation("Ready"))
                
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if self.monitor_thread.isRunning():
                self.monitor_thread.stop()
                self.monitor_thread.wait(3000)  # Wait up to 3 seconds
                if self.monitor_thread.isRunning():
                    self.monitor_thread.terminate()
            logger.info("Status bar cleanup completed")
        except Exception as e:
            logger.error(f"Error during status bar cleanup: {e}")
