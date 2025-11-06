# type: ignore
"""
Parameters Panel Manager

Manages the parameters panel with drag-and-drop functionality.
Parameters can be dragged onto graphs to visualize them.
"""

import logging
from typing import TYPE_CHECKING, List, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import QObject, pyqtSignal as Signal
import numpy as np

from src.ui.parameter_list import ParameterList
from src.ui.parameter_calculator_dialog import ParameterCalculatorDialog
from src.ui.parameter_item import ParameterItem

if TYPE_CHECKING:
    from ..widgets.time_graph_widget_refactored import TimeGraphWidget

logger = logging.getLogger(__name__)


class ParametersPanelManager(QObject):
    """
    Manages the parameters panel with drag-drop functionality.
    
    Features:
    - List of available parameters
    - Drag parameters onto graphs to plot them
    - Search and filter parameters
    - Custom parameter support
    """
    
    # Signals
    parameter_drag_started = Signal(str)  # parameter_name
    parameter_dropped = Signal(int, str)  # graph_index, parameter_name
    
    def __init__(self, parent_widget: "TimeGraphWidget"):
        super().__init__()
        self.parent = parent_widget
        self.panel = None
        self.parameter_list = None
        
        self._setup_panel()
    
    def _setup_panel(self):
        """Setup the parameters panel UI with drag-drop functionality."""
        # Create main panel widget
        self.panel = QWidget()
        self.panel.setObjectName("parametersPanel")
        
        # Create main layout
        main_layout = QVBoxLayout(self.panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title section
        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d4a66, stop:1 #1a2332);
                border-bottom: 2px solid rgba(74, 144, 226, 0.5);
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("🔧 Parameters")
        title_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #e6f3ff;
            padding: 5px;
        """)
        title_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Drag parameters onto graphs to plot them")
        desc_label.setStyleSheet("""
            font-size: 9pt;
            color: #a0c0e0;
            padding: 2px 5px;
        """)
        title_layout.addWidget(desc_label)
        
        # Add New Parameter button
        self.add_param_btn = QPushButton("➕ Add New Parameter")
        self.add_param_btn.setStyleSheet("""
            QPushButton {
                background: rgba(74, 144, 226, 0.3);
                border: 1px solid rgba(74, 144, 226, 0.5);
                border-radius: 4px;
                padding: 8px;
                color: #e6f3ff;
                font-size: 10pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(74, 144, 226, 0.5);
            }
            QPushButton:pressed {
                background: rgba(74, 144, 226, 0.7);
            }
        """)
        self.add_param_btn.clicked.connect(self._on_add_parameter_clicked)
        title_layout.addWidget(self.add_param_btn)
        
        main_layout.addWidget(title_container)
        
        # Parameter list
        self.parameter_list = ParameterList(self.panel)
        self.parameter_list.parameter_drag_started.connect(self._on_parameter_drag_started)
        main_layout.addWidget(self.parameter_list, 1)
        
        logger.debug("Parameters panel initialized with drag-drop support")
    
    def _on_parameter_drag_started(self, parameter_name: str):
        """Handle when a parameter drag starts."""
        logger.info(f"Parameter drag started: {parameter_name}")
        self.parameter_drag_started.emit(parameter_name)
    
    def get_panel(self) -> QWidget:
        """Get the parameters panel widget."""
        return self.panel
    
    def update_columns(self, column_names: list, time_column: str = None):
        """
        Update the parameter list with columns from loaded data.
        
        Args:
            column_names: List of column names from the dataframe
            time_column: Name of the time column (will be excluded)
        """
        if self.parameter_list:
            self.parameter_list.update_columns(column_names, time_column)
            logger.info(f"Parameters panel updated with {len(column_names)} columns")
    
    def update_theme(self):
        """Update panel styling when theme changes."""
        # Theme update logic can be added here if needed
        pass
    
    def _on_add_parameter_clicked(self):
        """Handle Add New Parameter button click."""
        # Get available parameters
        if not self.parameter_list:
            return
        
        available_params = list(self.parameter_list.parameter_items.keys())
        if not available_params:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self.panel,
                "No Parameters",
                "Please load data first to see available parameters."
            )
            return
        
        # Get signal data getter function
        def get_signal_data(param_name: str):
            """Get signal data for a parameter."""
            if not hasattr(self.parent, 'signal_processor'):
                raise ValueError("Signal processor not available")
            
            signal_data = self.parent.signal_processor.get_signal_data(param_name)
            if signal_data:
                return signal_data['x_data'], signal_data['y_data']
            else:
                raise ValueError(f"Signal '{param_name}' not found")
        
        # Create and show dialog
        dialog = ParameterCalculatorDialog(available_params, get_signal_data, self.panel)
        dialog.parameter_created.connect(self._on_parameter_created)
        
        # Center dialog on parent window
        if self.parent and hasattr(self.parent, 'parent') and self.parent.parent():
            parent_geometry = self.parent.parent().geometry()
            dialog.move(
                parent_geometry.center().x() - dialog.width() // 2,
                parent_geometry.center().y() - dialog.height() // 2
            )
        
        dialog.exec_()
    
    def _on_parameter_created(self, param_name: str, x_data: np.ndarray, y_data: np.ndarray):
        """Handle new parameter creation."""
        logger.info(f"New parameter created: {param_name}")
        
        # Add to signal processor
        if hasattr(self.parent, 'signal_processor'):
            self.parent.signal_processor.add_signal(param_name, x_data, y_data)
            logger.info(f"Added '{param_name}' to signal processor")
        
        # Add to parameter list
        if self.parameter_list:
            self.parameter_list.add_parameter(param_name)
            logger.info(f"Added '{param_name}' to parameter list")
        
        # Update parent widget if needed
        if hasattr(self.parent, '_on_processing_finished'):
            # Trigger a refresh
            self.parent._on_processing_finished()

