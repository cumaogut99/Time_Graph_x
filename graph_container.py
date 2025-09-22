# type: ignore
"""
Graph Container for Time Graph Widget

A self-contained widget that manages a vertical stack of plots for a single tab.
"""

import logging
from typing import Dict, Any
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# Import necessary components - use absolute imports for standalone app
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from plot_manager import PlotManager
from theme_manager import ThemeManager

logger = logging.getLogger(__name__)

class GraphContainer(QWidget):
    """
    Manages a collection of vertically stacked plots within a single tab.
    Each GraphContainer has its own PlotManager.
    """
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.cursor_manager = None  # Initialize cursor manager attribute
        self.signal_processor = None # Initialize signal processor attribute
        
        # Each container has its own plot manager to handle its own plots
        self.plot_manager = PlotManager(self)
        
        # Main layout for this container
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.plot_manager.get_plot_panel())
        
        logger.info("GraphContainer initialized")

    def set_graph_count(self, count: int):
        """Sets the number of vertically stacked graphs (subplots)."""
        logger.info(f"Setting graph count in container to: {count}")
        self.plot_manager.set_subplot_count(count)

    def add_signal(self, name: str, x_data, y_data, plot_index: int, **kwargs):
        """Adds a signal to a specific subplot within this container."""
        self.plot_manager.add_signal(name, x_data, y_data, plot_index, **kwargs)

    def get_plot_widgets(self):
        """Returns the plot widgets managed by this container."""
        return self.plot_manager.get_plot_widgets()

    def apply_theme(self):
        """Applies the current theme to the plots in this container."""
        plot_colors = self.theme_manager.get_plot_colors()
        self.plot_manager.apply_theme(plot_colors)

    # ... other methods to delegate calls to plot_manager can be added here ...
    # (e.g., clear_signals, reset_view, etc.)
