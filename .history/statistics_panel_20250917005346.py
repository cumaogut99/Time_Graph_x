# type: ignore
"""
Statistics Panel for Time Analysis Widget

Displays real-time statistics for each signal:
- Signal Name
- Mean
- Max  
- Min
- RMS (Root Mean Square)
- Standard Deviation

Updates dynamically based on cursor/range selection.
"""

import logging
from typing import Dict, Any, Optional
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, 
    QLabel, QScrollArea, QFrame, QColorDialog, QSizePolicy, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QMouseEvent

logger = logging.getLogger(__name__)

class ClickableColorLabel(QLabel):
    """A QLabel that shows a color and opens a QColorDialog when clicked."""
    color_changed = pyqtSignal(str)  # Emits the new color hex string

    def __init__(self, initial_color: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.set_color(initial_color)

    def set_color(self, color_hex: str):
        self._color = QColor(color_hex)
        self.setToolTip(f"Click to change color ({color_hex})")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color_hex};
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 6px;
            }}
            QLabel:hover {{
                border: 2px solid rgba(255, 255, 255, 1);
            }}
        """)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            new_color = QColorDialog.getColor(self._color, self, "Select Signal Color")
            if new_color.isValid():
                new_color_hex = new_color.name()
                self.set_color(new_color_hex)
                self.color_changed.emit(new_color_hex)
        super().mousePressEvent(event)

class ClickableGroupBox(QGroupBox):
    """QGroupBox that emits a signal when clicked."""
    
    clicked = pyqtSignal(int)  # graph_index
    
    def __init__(self, title: str, graph_index: int, parent=None):
        super().__init__(title, parent)
        self.graph_index = graph_index
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event: QMouseEvent):
        # Only emit the signal if the click is within the title bar area (approx. 30px height)
        if event.button() == Qt.LeftButton and event.pos().y() < 30:
            self.clicked.emit(self.graph_index)
        
        # We don't call super().mousePressEvent(event) if we handle the click,
        # but in this case, we want default behaviors for other parts of the groupbox.
        # Let's let the event propagate.
        super().mousePressEvent(event)

class StatisticsPanel(QWidget):
    """
    Panel for displaying real-time signal statistics organized by graphs.
    
    Features:
    - Separate section for each graph
    - Horizontal layout for efficient space usage
    - Color-coded signal identification
    - Scrollable layout for multiple graphs
    - Coordinated with statistics settings panel
    - Clickable graph titles to open individual graph settings
    """
    
    # Signal emitted when a graph title is clicked
    graph_settings_requested = pyqtSignal(int)  # graph_index
    signal_color_changed = pyqtSignal(str, str) # Emits signal_name and new_color_hex

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data storage
        self.graph_sections = {}  # graph_index -> QGroupBox
        self.signal_data = {}  # full_signal_name -> {graph_index, signal_name, labels_dict}
        self.visible_stats = {'mean', 'max', 'min', 'rms', 'std'}  # Default visible stats
        self.cursor_mode = "none"  # Track cursor mode for dynamic headers
        
        # Cursor position tracking
        self.cursor_positions = {}  # Store current cursor positions
        
        # Datetime formatting
        self.is_datetime_axis = False  # Track if we should format cursor values as datetime
        
        # Column width management
        self.column_widths = {
            'signal': 180,  # Signal name column
            'c1': 80,       # Cursor 1 column
            'c2': 80,       # Cursor 2 column
            'min': 80,      # Min column
            'mean': 80,     # Mean column
            'max': 80,      # Max column
            'rms': 80,      # RMS column
            'std': 80       # Standard deviation column
        }
        
        # Setup UI
        self._setup_ui()
        self._setup_styling()
        
        logger.debug("StatisticsPanel initialized with graph-based organization")

    def _create_cursor_info_panel(self) -> QWidget:
        """Create the compact cursor information panel at the bottom."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        panel.setFixedHeight(45)  # Increased height for better readability
        panel.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.3);
                border: 2px solid rgba(74, 144, 226, 0.5);
                border-radius: 8px;
                margin: 1px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(8, 4, 8, 4)  # Reduced padding
        layout.setSpacing(12)  # Slightly reduced spacing
        
        # T1 (Cursor 1)
        self.cursor1_time_label = QLabel("T1: --")
        self.cursor1_time_label.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(74, 144, 226, 0.15);
                min-height: 20px;
            }
        """)
        layout.addWidget(self.cursor1_time_label)
        
        # T2 (Cursor 2)
        self.cursor2_time_label = QLabel("T2: --")
        self.cursor2_time_label.setStyleSheet("""
            QLabel {
                color: #e24a90;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(226, 74, 144, 0.15);
                min-height: 20px;
            }
        """)
        layout.addWidget(self.cursor2_time_label)
        
        # ΔT (Delta time)
        self.delta_time_label = QLabel("ΔT: --")
        self.delta_time_label.setStyleSheet("""
            QLabel {
                color: #90e24a;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(144, 226, 74, 0.15);
                min-height: 20px;
            }
        """)
        layout.addWidget(self.delta_time_label)
        
        # Freq (Frequency)
        self.frequency_label = QLabel("Freq: --")
        self.frequency_label.setStyleSheet("""
            QLabel {
                color: #e2904a;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(226, 144, 74, 0.15);
                min-height: 20px;
            }
        """)
        layout.addWidget(self.frequency_label)
        
        layout.addStretch()
        
        return panel

    def _create_statistics_header(self) -> QWidget:
        """Create the statistics header with resizable columns using QSplitter."""
        header_widget = QWidget()
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 3, 5, 3)
        header_layout.setSpacing(0)
        
        # Create splitter for resizable columns
        self.header_splitter = QSplitter(Qt.Horizontal)
        self.header_splitter.setChildrenCollapsible(False)
        
        # Signal name column
        name_header = QLabel("Signal")
        name_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_header.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 8px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                border-right: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        name_header.setMinimumWidth(self.column_widths['signal'])
        self.header_splitter.addWidget(name_header)
        
        # Statistics headers - dynamic based on cursor mode
        stats_info = self._get_stats_info_for_mode()
        
        column_keys = ['signal']
        
        for stat_key, icon, display_name in stats_info:
            is_cursor_stat = stat_key in ['c1', 'c2']
            if is_cursor_stat or stat_key in self.visible_stats:
                stat_header = QLabel(f"{icon} {display_name}")
                stat_header.setAlignment(Qt.AlignCenter)
                stat_header.setStyleSheet("""
                    QLabel {
                        color: #cccccc;
                        font-size: 12px;
                        font-weight: bold;
                        padding: 5px 8px;
                        background-color: rgba(255, 255, 255, 0.15);
                        border-radius: 6px;
                        border-right: 1px solid rgba(255, 255, 255, 0.3);
                    }
                """)
                stat_header.setMinimumWidth(self.column_widths.get(stat_key, 80))
                self.header_splitter.addWidget(stat_header)
                column_keys.append(stat_key)

        # Set initial sizes for the splitter
        initial_sizes = [self.column_widths.get(key, 80) for key in column_keys]
        self.header_splitter.setSizes(initial_sizes)
        
        # Connect splitter signals to update column widths
        self.header_splitter.splitterMoved.connect(self._on_column_resized)
        
        header_layout.addWidget(self.header_splitter)
        
        header_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                margin: 2px 0px;
            }
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.3);
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: rgba(74, 144, 226, 0.8);
            }
        """)
        
        return header_widget

    def _on_column_resized(self, pos: int, index: int):
        """Handle column resize events from the header splitter."""
        if not hasattr(self, 'header_splitter'):
            return
            
        # Get current sizes from splitter
        sizes = self.header_splitter.sizes()
        
        # Update column widths dictionary
        stats_info = self._get_stats_info_for_mode()
        column_keys = ['signal'] + [stat_key for stat_key, _, _ in stats_info 
                                   if stat_key in ['c1', 'c2'] or stat_key in self.visible_stats]
        
        for i, size in enumerate(sizes):
            if i < len(column_keys):
                self.column_widths[column_keys[i]] = size
        
        # Update all signal rows to match new column widths
        self._update_all_signal_row_widths()
        
        logger.debug(f"Column resized: {self.column_widths}")

    def _update_all_signal_row_widths(self):
        """Update all signal rows to match current column widths."""
        for signal_name, signal_info in self.signal_data.items():
            row_widget = signal_info.get('row_widget')
            if row_widget and hasattr(row_widget, 'row_splitter'):
                # Update splitter sizes to match header
                if hasattr(self, 'header_splitter'):
                    header_sizes = self.header_splitter.sizes()
                    row_widget.row_splitter.setSizes(header_sizes)

    def _get_stats_info_for_mode(self):
        """Get statistics info based on current cursor mode."""
        if self.cursor_mode == 'dual':
            return [
                ('c1', '🎯', 'C1'),
                ('c2', '🎯', 'C2'),
                ('min', '📉', 'Min'),
                ('mean', '📊', 'Mean'),
                ('max', '📈', 'Max'),
                ('rms', '⚡', 'RMS (C1)'),
                ('std', '📏', 'Std')
            ]
        else:
            # When no cursors, maintain a logical order
            return [
                ('min', '📉', 'Min'),
                ('mean', '📊', 'Mean'),
                ('max', '📈', 'Max'),
                ('std', '📏', 'Std')
            ]

    def set_cursor_mode(self, mode: str):
        """Update cursor mode and refresh headers."""
        if self.cursor_mode != mode:
            self.cursor_mode = mode
            # Recreate header with new mode
            self._recreate_header()
            # Recreate all signal rows to match new structure
            self._recreate_all_signal_rows()
            
        # Clear cursor values if mode is none
        if mode == 'none':
            self._clear_cursor_values()
    
    def set_datetime_axis(self, is_datetime: bool):
        """Enable or disable datetime formatting for cursor values."""
        self.is_datetime_axis = is_datetime
        # Update cursor positions with new formatting
        if self.cursor_positions:
            self.update_cursor_positions(self.cursor_positions)
            self.clear_cursor_info()
            
        # Show/hide cursor info panel based on mode
        if hasattr(self, 'cursor_info_panel'):
            if mode == 'dual':
                self.cursor_info_panel.show()
            else:
                self.cursor_info_panel.hide()

    def _recreate_header(self):
        """Recreate the statistics header."""
        # Remove old header
        if hasattr(self, 'header_widget') and self.header_widget:
            self.main_layout.removeWidget(self.header_widget)
            self.header_widget.deleteLater()
        
        # Create new header
        self.header_widget = self._create_statistics_header()
        self.main_layout.insertWidget(1, self.header_widget)  # Insert after title

    def _recreate_all_signal_rows(self):
        """Recreate all signal rows to match new cursor mode structure."""
        # Store current signal data
        current_data = self.signal_data.copy()
        
        # Clear all graph sections
        for graph_section in self.graph_sections.values():
            graph_section.deleteLater()
        self.graph_sections.clear()
        self.signal_data.clear()
        
        # Recreate all signals with new structure
        for full_signal_name, data in current_data.items():
            graph_index = data['graph_index']
            signal_name = data['signal_name']
            
            # Ensure graph section exists
            if graph_index not in self.graph_sections:
                self._create_graph_section(graph_index)
            
            # Add signal back
            self.add_signal(full_signal_name, graph_index, signal_name, data.get('color', '#ffffff'))

    def _setup_ui(self):
        """Setup the statistics panel UI."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        
        # Title
        self.title_label = QLabel("📊 Signal Statistics")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        # Title styling will be applied in _apply_theme_styling
        self.main_layout.addWidget(self.title_label)
        
        # Statistics header
        self.header_widget = self._create_statistics_header()
        self.main_layout.addWidget(self.header_widget)
        
        # Scroll area for statistics boxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for scroll area
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(1)
        
        # No stretch needed - graph sections will fill the space with fixed heights
        
        scroll_area.setWidget(self.container_widget)
        self.main_layout.addWidget(scroll_area)
        
        # Cursor info panel at the bottom (fixed)
        self.cursor_info_panel = self._create_cursor_info_panel()
        self.cursor_info_panel.hide()  # Initially hidden, shown when dual cursor mode is active
        self.main_layout.addWidget(self.cursor_info_panel)

    def _setup_styling(self):
        """Setup the panel styling with theme support."""
        self._apply_theme_styling()

    def _apply_theme_styling(self, theme_colors=None):
        """Apply theme-based styling to the statistics panel."""
        # Get theme colors from parent or use fallback
        if theme_colors is None and hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        if theme_colors is None:
            # Fallback colors for space theme
            theme_colors = {
                'text_primary': '#ffffff',
                'text_secondary': '#e6f3ff',
                'surface': '#1a2332',
                'surface_variant': '#2d4a66',
                'border': '#4a90e2'
            }
        
        logger.debug(f"Statistics panel applying theme with text_primary: {theme_colors.get('text_primary')}")
        
        # Determine if this is a light theme
        is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
        
        # Adjust colors for light theme
        if is_light_theme:
            text_color = '#212121'
            secondary_text_color = '#757575'
            border_color_base = '0, 0, 0'  # Black for light theme
            bg_color_base = '0, 0, 0'      # Black for light theme
            border_opacity = '0.2'
            bg_opacity = '0.05'
            scrollbar_bg = 'rgba(0, 0, 0, 0.1)'
            scrollbar_handle = 'rgba(0, 0, 0, 0.3)'
            scrollbar_handle_hover = 'rgba(0, 0, 0, 0.5)'
            title_bg_opacity = '0.05'
        else:
            text_color = theme_colors.get('text_primary', '#ffffff')
            secondary_text_color = theme_colors.get('text_secondary', '#e0e0e0')
            border_color_base = '255, 255, 255' # White for dark themes
            bg_color_base = '255, 255, 255'     # White for dark themes
            border_opacity = '0.2'
            bg_opacity = '0.05'
            scrollbar_bg = 'rgba(255, 255, 255, 0.1)'
            scrollbar_handle = 'rgba(255, 255, 255, 0.3)'
            scrollbar_handle_hover = 'rgba(255, 255, 255, 0.5)'
            title_bg_opacity = '0.1'
        
        # Update title label styling
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: 18px;
                    font-weight: bold;
                    padding: 2px;
                    background-color: rgba({bg_color_base}, {title_bg_opacity});
                    border-radius: 8px;
                    margin-bottom: 2px;
                }}
            """)
        
        self.setStyleSheet(f"""
            StatisticsPanel {{
                background-color: transparent;
                border: none;
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba({border_color_base}, {border_opacity});
                border-radius: 12px;
                margin-top: 1px;
                padding: 3px;
                background-color: rgba({bg_color_base}, {bg_opacity});
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                color: {theme_colors.get('primary', '#4a90e2')};
            }}
            
            QLabel {{
                color: {text_color};
                font-size: 16px;
                font-weight: 500;
                padding: 3px 0px;
            }}

            QFormLayout QLabel {{
                font-weight: bold;
                color: {secondary_text_color};
                font-size: 14px;
                min-width: 80px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollArea QScrollBar:vertical {{
                background-color: {scrollbar_bg};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollArea QScrollBar::handle:vertical {{
                background-color: {scrollbar_handle};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollArea QScrollBar::handle:vertical:hover {{
                background-color: {scrollbar_handle_hover};
            }}
            
            /* Graph section scroll bars */
            QGroupBox QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QGroupBox QScrollArea QScrollBar:vertical {{
                background-color: {scrollbar_bg};
                width: 8px;
                border-radius: 4px;
            }}
            
            QGroupBox QScrollArea QScrollBar::handle:vertical {{
                background-color: {scrollbar_handle};
                border-radius: 4px;
                min-height: 15px;
            }}
            
            QGroupBox QScrollArea QScrollBar::handle:vertical:hover {{
                background-color: {scrollbar_handle_hover};
            }}
        """)

    def update_theme(self, theme_colors=None):
        """Update the panel styling when theme changes."""
        self._apply_theme_styling(theme_colors)

    def add_signal(self, full_signal_name: str, graph_index: int, signal_name: str, color: str):
        """
        Add a new signal to the appropriate graph section.
        
        Args:
            full_signal_name: Full signal name with graph suffix (e.g., "RPM (G1)")
            graph_index: Index of the graph this signal belongs to
            signal_name: Base signal name (e.g., "RPM")
            color: Color for visual identification
        """
        # Ensure graph section exists
        if graph_index not in self.graph_sections:
            self._create_graph_section(graph_index)
        
        # Create signal row in horizontal layout
        signal_row = self._create_signal_row(signal_name, color)
        
        # Add to the graph section's signals container
        graph_section = self.graph_sections[graph_index]
        scroll_area = graph_section.findChild(QScrollArea)
        signals_container = scroll_area.widget()
        signals_layout = signals_container.layout()
        
        # Insert before the stretch (last item)
        signals_layout.insertWidget(signals_layout.count() - 1, signal_row)
        
        # Store signal data
        self.signal_data[full_signal_name] = {
            'graph_index': graph_index,
            'signal_name': signal_name,
            'color': color,
            'row_widget': signal_row,
            'labels': self._extract_labels_from_row(signal_row)
        }
        
        #logger.debug(f"Added signal '{signal_name}' to graph {graph_index+1} section")

    def _create_graph_section(self, graph_index: int):
        """Create a new graph section."""
        section_title = f"⚙️ Graph {graph_index + 1} Settings"
        graph_section = ClickableGroupBox(section_title, graph_index)
        
        # Set graph section styling with hover effect
        graph_section.setStyleSheet(f"""
            ClickableGroupBox {{
                font-weight: bold;
                font-size: 15px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                margin-top: 1px;
                padding: 3px;
                background-color: rgba(255, 255, 255, 0.05);
            }}
            ClickableGroupBox:hover {{
                border: 2px solid rgba(93, 156, 236, 0.8);
                background-color: rgba(93, 156, 236, 0.15);
            }}
            ClickableGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: rgba(0, 0, 0, 0.4);
                border-radius: 6px;
                color: #5d9cec;
            }}
            ClickableGroupBox:hover::title {{
                color: #ffffff;
                background-color: rgba(93, 156, 236, 0.5);
                font-weight: bold;
            }}
        """)
        
        # Create scroll area for this graph section
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create container widget for signals
        signals_container = QWidget()
        signals_layout = QVBoxLayout(signals_container)
        signals_layout.setSpacing(2)
        signals_layout.setContentsMargins(1, 1, 1, 1)
        signals_layout.addStretch()  # Push signals to top
        
        scroll_area.setWidget(signals_container)
        
        # Main layout for the graph section
        section_layout = QVBoxLayout(graph_section)
        section_layout.setContentsMargins(2, 25, 2, 2)
        section_layout.addWidget(scroll_area)
        
        # Connect click signal
        graph_section.clicked.connect(self.graph_settings_requested.emit)
        
        # Store and add to main layout
        self.graph_sections[graph_index] = graph_section
        self.container_layout.insertWidget(
            self.container_layout.count() - 1, 
            graph_section
        )
        
        logger.debug(f"Created graph section for Graph {graph_index + 1}")

    def _create_signal_row(self, signal_name: str, color: str) -> QWidget:
        """Create a horizontal row for a signal with all its statistics using QSplitter."""
        row_widget = QWidget()
        row_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 3, 5, 3)
        row_layout.setSpacing(0)
        
        # Create splitter for resizable columns that matches header
        row_splitter = QSplitter(Qt.Horizontal)
        row_splitter.setChildrenCollapsible(False)
        row_widget.row_splitter = row_splitter  # Store reference for width updates
        
        # Signal name widget with color indicator
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_layout.setContentsMargins(5, 0, 5, 0)
        name_layout.setSpacing(5)
        
        # Color indicator
        color_indicator = ClickableColorLabel(color)
        color_indicator.setFixedSize(12, 12)

        # Connect the color change signal to the panel's signal
        color_indicator.color_changed.connect(
            lambda new_color, s_name=signal_name: self.signal_color_changed.emit(s_name, new_color)
        )
        
        name_layout.addWidget(color_indicator)
        
        # Signal name (full name, no truncation)
        name_label = QLabel(signal_name)
        name_label.setWordWrap(False)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        name_label.setToolTip(signal_name)  # Show full name in tooltip
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        
        name_widget.setMinimumWidth(self.column_widths['signal'])
        row_splitter.addWidget(name_widget)
        
        # Statistics values in separate widgets that match header columns
        stats_info = self._get_stats_info_for_mode()
        
        labels_dict = {}
        for stat_key, icon, display_name in stats_info:
            is_cursor_stat = stat_key in ['c1', 'c2']
            if is_cursor_stat or stat_key in self.visible_stats:
                value_widget = QWidget()
                value_layout = QHBoxLayout(value_widget)
                value_layout.setContentsMargins(5, 0, 5, 0)
                
                value_label = self._create_value_label("--")
                value_label.setObjectName(f"value_{stat_key}")
                value_layout.addWidget(value_label)
                
                value_widget.setMinimumWidth(self.column_widths.get(stat_key, 80))
                row_splitter.addWidget(value_widget)
                labels_dict[stat_key] = value_label
        
        # Sync splitter sizes with header if it exists
        if hasattr(self, 'header_splitter'):
            row_splitter.setSizes(self.header_splitter.sizes())
        
        row_layout.addWidget(row_splitter)
        
        row_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 2px;
            }
            QSplitter::handle {
                background-color: transparent;
                width: 2px;
            }
        """)
        
        # Store labels in the widget for easy access
        row_widget.labels_dict = labels_dict
        
        return row_widget

    def _create_value_label(self, value: str) -> QLabel:
        """Create a responsive value label for statistics."""
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
                background-color: rgba(255, 255, 255, 0.1);
                padding: 5px 8px;
                border-radius: 4px;
                min-width: 60px;
                max-width: 150px;
            }
        """)
        return value_label

    def _create_stat_widget(self, icon: str, name: str, value: str) -> QWidget:
        """Create a compact statistic widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # Header with icon and name
        header_label = QLabel(f"{icon} {name}")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        layout.addWidget(header_label)
        
        # Value label
        value_label = QLabel(value)
        value_label.setObjectName(f"value_{name.lower()}")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
                background-color: rgba(255, 255, 255, 0.1);
                padding: 3px;
                border-radius: 4px;
                min-width: 60px;
            }
        """)
        layout.addWidget(value_label)
        
        widget.setMinimumWidth(80)
        return widget

    def _extract_labels_from_row(self, row_widget: QWidget) -> Dict[str, QLabel]:
        """Extract value labels from a signal row widget."""
        return getattr(row_widget, 'labels_dict', {})

    def update_statistics(self, signal_name: str, stats: Dict[str, float]):
        """
        Update statistics for a specific signal.
        
        Args:
            signal_name: Name of the signal (with graph suffix)
            stats: Dictionary with statistic values
        """
        if signal_name not in self.signal_data:
            logger.warning(f"Signal {signal_name} not found in statistics panel")
            return
        
        signal_info = self.signal_data[signal_name]
        labels = signal_info['labels']
        
        # Update each statistic with proper formatting
        for stat_name, value in stats.items():
            # Skip cursor-related stats if cursor mode is not dual
            if stat_name in ['c1', 'c2', 'rms'] and self.cursor_mode != 'dual':
                continue
                
            is_cursor_stat = stat_name in ['c1', 'c2']
            if stat_name in labels and (is_cursor_stat or stat_name in self.visible_stats):
                label = labels[stat_name]
                if label is not None:
                    if isinstance(value, (int, float)):
                        # Improved number formatting - avoid scientific notation when possible
                        if is_cursor_stat:
                            # Cursor values with higher precision
                            if abs(value) >= 1000000:
                                formatted_value = f"{value/1000000:.2f}M"
                            elif abs(value) >= 1000:
                                formatted_value = f"{value/1000:.1f}K"
                            elif abs(value) >= 1:
                                formatted_value = f"{value:.3f}"
                            elif abs(value) >= 0.001:
                                formatted_value = f"{value:.5f}"
                            else:
                                formatted_value = f"{value:.2e}"
                        else:
                            # Standard statistics formatting
                            if abs(value) >= 1000000:
                                formatted_value = f"{value/1000000:.2f}M"
                            elif abs(value) >= 1000:
                                formatted_value = f"{value/1000:.1f}K"
                            elif abs(value) >= 1:
                                formatted_value = f"{value:.2f}"
                            elif abs(value) >= 0.001:
                                formatted_value = f"{value:.4f}"
                            else:
                                formatted_value = f"{value:.2e}"
                    else:
                        formatted_value = str(value)
                    
                    label.setText(formatted_value)
                    
                    # Add visual feedback for cursor values
                    if is_cursor_stat:
                        label.setStyleSheet("""
                            QLabel {
                                color: #ffffff;
                                font-size: 14px;
                                font-weight: 600;
                                background-color: rgba(74, 144, 226, 0.2);
                                padding: 3px;
                                border-radius: 4px;
                                min-width: 80px;
                                border: 1px solid rgba(74, 144, 226, 0.5);
                            }
                        """)

    def _clear_cursor_values(self):
        """Clear all cursor values from statistics display."""
        for signal_name, signal_info in self.signal_data.items():
            labels = signal_info['labels']
            
            # Clear cursor values (C1, C2)
            for cursor_key in ['c1', 'c2']:
                if cursor_key in labels and labels[cursor_key]:
                    labels[cursor_key].setText("--")
                    # Reset styling for cursor labels
                    labels[cursor_key].setStyleSheet("""
                        QLabel {
                            color: #cccccc;
                            font-size: 13px;
                            font-weight: normal;
                            background-color: transparent;
                            padding: 2px;
                            border: none;
                            min-width: 80px;
                        }
                    """)

    def update_cursor_positions(self, cursor_positions: Dict[str, float]):
        """Update cursor position information and calculate delta values."""
        self.cursor_positions = cursor_positions.copy()
        
        # Update cursor 1 position
        if 'c1' in cursor_positions:
            c1_time = cursor_positions['c1']
            self.cursor1_time_label.setText(f"T1: {c1_time:.4f}s")
        else:
            self.cursor1_time_label.setText("T1: --")
            
        # Update cursor 2 position
        if 'c2' in cursor_positions:
            c2_time = cursor_positions['c2']
            self.cursor2_time_label.setText(f"T2: {c2_time:.4f}s")
        else:
            self.cursor2_time_label.setText("T2: --")
            
        # Calculate and display delta time and frequency
        if 'c1' in cursor_positions and 'c2' in cursor_positions:
            c1_time = cursor_positions['c1']
            c2_time = cursor_positions['c2']
            delta_time = abs(c2_time - c1_time)
            
            # Display delta time
            if delta_time > 0:
                if delta_time >= 1.0:
                    self.delta_time_label.setText(f"ΔT: {delta_time:.4f}s")
                elif delta_time >= 0.001:
                    self.delta_time_label.setText(f"ΔT: {delta_time*1000:.2f}ms")
                else:
                    self.delta_time_label.setText(f"ΔT: {delta_time*1000000:.1f}μs")
                
                # Calculate and display frequency
                frequency = 1.0 / delta_time
                if frequency >= 1000000:
                    self.frequency_label.setText(f"Freq: {frequency/1000000:.2f}MHz")
                elif frequency >= 1000:
                    self.frequency_label.setText(f"Freq: {frequency/1000:.2f}kHz")
                else:
                    self.frequency_label.setText(f"Freq: {frequency:.2f}Hz")
            else:
                self.delta_time_label.setText("ΔT: 0s")
                self.frequency_label.setText("Freq: ∞Hz")
        else:
            self.delta_time_label.setText("ΔT: --")
            self.frequency_label.setText("Freq: --")
            
        logger.debug(f"Updated cursor positions: {cursor_positions}")

    def clear_cursor_info(self):
        """Clear all cursor information."""
        self.cursor_positions = {}
        self.cursor1_time_label.setText("T1: --")
        self.cursor2_time_label.setText("T2: --")
        self.delta_time_label.setText("ΔT: --")
        self.frequency_label.setText("Freq: --")

    def remove_signal(self, signal_name: str):
        """
        Remove a signal from its graph section.
        
        Args:
            signal_name: Name of the signal to remove (with graph suffix)
        """
        if signal_name in self.signal_data:
            signal_info = self.signal_data[signal_name]
            graph_index = signal_info['graph_index']
            row_widget = signal_info['row_widget']
            
            # Remove from graph section's signals container
            if graph_index in self.graph_sections:
                graph_section = self.graph_sections[graph_index]
                scroll_area = graph_section.findChild(QScrollArea)
                signals_container = scroll_area.widget()
                signals_layout = signals_container.layout()
                signals_layout.removeWidget(row_widget)
                row_widget.deleteLater()
            
            # Clean up references
            del self.signal_data[signal_name]
            
            logger.debug(f"Removed signal: {signal_name}")

    def clear_all(self):
        """Remove all signals and graph sections."""
        # Clear all signal data
        for signal_name in list(self.signal_data.keys()):
            self.remove_signal(signal_name)
        
        # Clear all graph sections
        for graph_index in list(self.graph_sections.keys()):
            graph_section = self.graph_sections[graph_index]
            self.container_layout.removeWidget(graph_section)
            graph_section.deleteLater()
        
        self.graph_sections.clear()
        self.signal_data.clear()
        
        logger.debug("Cleared all statistics")

    def save_column_widths(self) -> Dict[str, int]:
        """Save current column widths to a dictionary."""
        return self.column_widths.copy()

    def restore_column_widths(self, widths: Dict[str, int]):
        """Restore column widths from a dictionary."""
        self.column_widths.update(widths)
        
        # Update header splitter if it exists
        if hasattr(self, 'header_splitter'):
            stats_info = self._get_stats_info_for_mode()
            column_keys = ['signal'] + [stat_key for stat_key, _, _ in stats_info 
                                       if stat_key in ['c1', 'c2'] or stat_key in self.visible_stats]
            
            sizes = [self.column_widths.get(key, 80) for key in column_keys]
            self.header_splitter.setSizes(sizes)
            
            # Update all signal rows
            self._update_all_signal_row_widths()
        
        logger.debug(f"Restored column widths: {widths}")

    def get_signal_count(self) -> int:
        """Get the number of signals currently displayed."""
        return len(self.signal_data)

    def has_signal(self, signal_name: str) -> bool:
        """Check if a signal is currently displayed."""
        return signal_name in self.signal_data
    
    def set_visible_stats(self, visible_stats: set):
        """Update which statistics are visible."""
        self.visible_stats = visible_stats
        logger.debug(f"Updated visible statistics: {visible_stats}")
        
        # Update the header to reflect new visible stats
        if hasattr(self, 'header_widget'):
            # Remove old header
            self.header_widget.setParent(None)
            self.header_widget.deleteLater()
            
            # Create new header
            self.header_widget = self._create_statistics_header()
            
            # Insert new header after title (at index 1)
            main_layout = self.layout()
            main_layout.insertWidget(1, self.header_widget)

    def ensure_graph_sections(self, max_graph_index: int):
        """Ensure graph sections exist up to the specified index in correct order."""
        total_graphs = max_graph_index + 1
        
        # Create missing graph sections in order
        for graph_idx in range(total_graphs):
            if graph_idx not in self.graph_sections:
                self._create_graph_section(graph_idx)
                logger.debug(f"Auto-created graph section for Graph {graph_idx + 1}")
        
        # Ensure sections are in correct order in the layout
        self._reorder_graph_sections()
        
        # Update all graph sections to have equal heights
        self._equalize_graph_heights(total_graphs)

    def _reorder_graph_sections(self):
        """Reorder graph sections in the layout to match their indices."""
        # Remove all graph sections from layout
        for graph_section in self.graph_sections.values():
            self.container_layout.removeWidget(graph_section)
        
        # Add them back in correct order
        for graph_idx in sorted(self.graph_sections.keys()):
            graph_section = self.graph_sections[graph_idx]
            self.container_layout.addWidget(graph_section)
        
        logger.debug(f"Reordered {len(self.graph_sections)} graph sections")

    def _equalize_graph_heights(self, total_graphs: int):
        """Set equal heights for all graph sections to fill the panel completely."""
        if total_graphs == 0:
            return
            
        # Get the actual scroll area height dynamically
        scroll_area = self.parent().findChild(QScrollArea) if self.parent() else None
        if scroll_area:
            available_height = scroll_area.height()
        else:
            available_height = 700  # Fallback height
            
        header_height = 80  # Header + title height
        spacing = 1 * (total_graphs - 1)  # Spacing between sections
        
        # Calculate height per graph section to fill the entire panel
        section_height = max(200, (available_height - header_height - spacing) // total_graphs)
        
        # Apply equal height to all graph sections
        for graph_section in self.graph_sections.values():
            graph_section.setMinimumHeight(section_height)
            graph_section.setMaximumHeight(section_height)
            
        logger.debug(f"Equalized {total_graphs} graph sections to {section_height}px each (total: {available_height}px)")

    def set_no_data_message(self):
        """Display a message when no data is available."""
        if not self.signal_data:
            # Create temporary message box
            message_box = QGroupBox("ℹ️ No Data")
            message_layout = QVBoxLayout(message_box)
            
            message_label = QLabel("Connect a data source to view statistics")
            message_label.setAlignment(Qt.AlignCenter)
            message_label.setStyleSheet("color: #6c757d; font-style: italic; font-size: 14px;")
            message_layout.addWidget(message_label)
            
            # Add to layout temporarily
            self.container_layout.insertWidget(0, message_box)
            
            # Store reference for removal when data is added
            self._no_data_box = message_box

    def _remove_no_data_message(self):
        """Remove the no data message if it exists."""
        if hasattr(self, '_no_data_box'):
            self.container_layout.removeWidget(self._no_data_box)
            self._no_data_box.deleteLater()
            delattr(self, '_no_data_box')