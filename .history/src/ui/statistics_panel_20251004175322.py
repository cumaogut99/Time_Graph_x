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
    QLabel, QScrollArea, QFrame, QColorDialog, QSizePolicy, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
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
        self.visible_stats = {'mean', 'max', 'min', 'rms', 'std', 'duty_cycle'}  # Default visible stats
        self.cursor_mode = "none"  # Track cursor mode for dynamic headers
        
        # Cursor position tracking
        self.cursor_positions = {}  # Store current cursor positions
        
        # Datetime formatting
        self.is_datetime_axis = False  # Track if we should format cursor values as datetime
        
        # Column width management
        self.column_widths = {
            'signal': 180,      # Signal name column
            'c1': 80,           # Cursor 1 column
            'c2': 80,           # Cursor 2 column
            'min': 80,          # Min column
            'mean': 80,         # Mean column
            'max': 80,          # Max column
            'rms': 80,          # RMS column
            'std': 80,          # Standard deviation column
            'duty_cycle': 90    # Duty cycle column
        }
        
        # Setup UI
        self._setup_ui()
        self._setup_styling()
        
        # Apply initial theme styling
        self._apply_initial_theme_styling()
        
        logger.debug("StatisticsPanel initialized with graph-based organization")

    def _apply_initial_theme_styling(self):
        """Apply initial theme styling when panel is created."""
        # Get theme colors
        theme_colors = {}
        if hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        # Apply theme styling to ensure proper initial appearance
        self._apply_theme_styling(theme_colors)

    def _create_cursor_info_panel(self) -> QWidget:
        """Create the compact cursor information panel at the bottom."""
        # Get theme colors
        theme_colors = {}
        if hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        # Determine if this is a light theme
        is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
        text_color = '#ffffff' if not is_light_theme else '#212121'
        
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
        self.cursor1_time_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(74, 144, 226, 0.15);
                min-height: 20px;
            }}
        """)
        layout.addWidget(self.cursor1_time_label)
        
        # T2 (Cursor 2)
        self.cursor2_time_label = QLabel("T2: --")
        self.cursor2_time_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(226, 74, 144, 0.15);
                min-height: 20px;
            }}
        """)
        layout.addWidget(self.cursor2_time_label)
        
        # ΔT (Delta time)
        self.delta_time_label = QLabel("ΔT: --")
        self.delta_time_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(144, 226, 74, 0.15);
                min-height: 20px;
            }}
        """)
        layout.addWidget(self.delta_time_label)
        
        # Freq (Frequency)
        self.frequency_label = QLabel("Freq: --")
        self.frequency_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 13px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 4px;
                background-color: rgba(226, 144, 74, 0.15);
                min-height: 20px;
            }}
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
        # Use theme-appropriate styling for header
        name_header.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                padding: 5px 8px;
                background-color: rgba(128, 128, 128, 0.1);
                border-radius: 6px;
                border-right: 1px solid rgba(128, 128, 128, 0.3);
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
                # Use theme-appropriate styling for stat headers
                stat_header.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: bold;
                        padding: 5px 8px;
                        background-color: rgba(128, 128, 128, 0.15);
                        border-radius: 6px;
                        border-right: 1px solid rgba(128, 128, 128, 0.3);
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
        
        # Use theme-appropriate styling for header widget
        header_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(128, 128, 128, 0.05);
                border: 1px solid rgba(128, 128, 128, 0.2);
                border-radius: 8px;
                margin: 2px 0px;
            }
            QSplitter::handle {
                background-color: rgba(128, 128, 128, 0.3);
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
        if not hasattr(self, 'header_splitter'):
            return
            
        header_sizes = self.header_splitter.sizes()
        
        for signal_name, signal_info in self.signal_data.items():
            row_widget = signal_info.get('row_widget')
            if row_widget and hasattr(row_widget, 'row_splitter'):
                # Temporarily disconnect signals to avoid recursion
                try:
                    row_widget.row_splitter.splitterMoved.disconnect()
                except:
                    pass
                
                # Update splitter sizes to match header
                row_widget.row_splitter.setSizes(header_sizes)
                
                # Reconnect signals
                row_widget.row_splitter.splitterMoved.connect(
                    lambda pos, idx, splitter=row_widget.row_splitter: self._on_row_splitter_moved(pos, idx, splitter)
                )

    def _on_row_splitter_moved(self, pos: int, index: int, source_splitter):
        """Handle row splitter movement and sync with header."""
        if not hasattr(self, 'header_splitter'):
            return
            
        # Get sizes from the moved splitter
        new_sizes = source_splitter.sizes()
        
        # Update header splitter to match
        try:
            self.header_splitter.splitterMoved.disconnect()
        except:
            pass
            
        self.header_splitter.setSizes(new_sizes)
        self.header_splitter.splitterMoved.connect(self._on_column_resized)
        
        # Update column widths
        stats_info = self._get_stats_info_for_mode()
        column_keys = ['signal'] + [stat_key for stat_key, _, _ in stats_info 
                                   if stat_key in ['c1', 'c2'] or stat_key in self.visible_stats]
        
        for i, size in enumerate(new_sizes):
            if i < len(column_keys):
                self.column_widths[column_keys[i]] = size
        
        # Sync all other row splitters
        for signal_name, signal_info in self.signal_data.items():
            row_widget = signal_info.get('row_widget')
            if row_widget and hasattr(row_widget, 'row_splitter') and row_widget.row_splitter != source_splitter:
                try:
                    row_widget.row_splitter.splitterMoved.disconnect()
                except:
                    pass
                    
                row_widget.row_splitter.setSizes(new_sizes)
                
                row_widget.row_splitter.splitterMoved.connect(
                    lambda pos, idx, splitter=row_widget.row_splitter: self._on_row_splitter_moved(pos, idx, splitter)
                )

    def _get_stats_info_for_mode(self):
        """Get statistics info based on current cursor mode."""
        if self.cursor_mode == 'dual':
            return [
                ('c1', '🎯', 'C1'),
                ('c2', '🎯', 'C2'),
                ('min', '📉', 'Min'),
                ('mean', '📊', 'Mean'),
                ('max', '📈', 'Max'),
                ('rms', '⚡', 'RMS'),
                ('std', '📏', 'Std'),
                ('duty_cycle', '⏱️', 'Duty %')
            ]
        else:
            # When no cursors, maintain a logical order
            return [
                ('min', '📉', 'Min'),
                ('mean', '📊', 'Mean'),
                ('max', '📈', 'Max'),
                ('std', '📏', 'Std'),
                ('duty_cycle', '⏱️', 'Duty %')
            ]

    def set_cursor_mode(self, mode: str):
        """Update cursor mode and refresh table headers."""
        if self.cursor_mode != mode:
            self.cursor_mode = mode
            # Update common header
            self._update_common_header()
            # Recreate table headers with new mode
            self._setup_table_headers()
            # Recreate all signal rows to match new structure
            self._recreate_all_signal_rows()
            
        # Clear cursor values if mode is none
        if mode == 'none':
            self._clear_cursor_values()
        
        # Show/hide cursor info panel based on mode
        if hasattr(self, 'cursor_info_panel'):
            if mode == 'dual':
                self.cursor_info_panel.show()
            else:
                self.cursor_info_panel.hide()
    
    def set_datetime_axis(self, is_datetime: bool):
        """Enable or disable datetime formatting for cursor values."""
        self.is_datetime_axis = is_datetime
        # Update cursor positions with new formatting
        if self.cursor_positions:
            self.update_cursor_positions(self.cursor_positions)

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
        
        # Clear all tables
        for table in self.graph_tables.values():
            table.setRowCount(0)
        self.signal_data.clear()
        
        # Update headers for all tables
        for table in self.graph_tables.values():
            self._setup_table_headers_for_graph(table)
        
        # Recreate all signals with new structure
        for full_signal_name, data in current_data.items():
            graph_index = data['graph_index']
            signal_name = data['signal_name']
            color = data.get('color', '#ffffff')
            
            # Add signal back to appropriate table
            self.add_signal(full_signal_name, graph_index, signal_name, color)

    def _setup_ui(self):
        """Setup the statistics panel UI with separate tables for each graph."""
        # Main layout - optimized for space efficiency
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        self.main_layout.setSpacing(1)  # Minimal spacing
        
        # Common header for all graphs
        self.common_header = self._create_common_header()
        self.main_layout.addWidget(self.common_header)
        
        # Scroll area for graph sections
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for scroll area - minimal spacing for efficiency
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(1)  # Reduced spacing between graph sections
        
        scroll_area.setWidget(self.container_widget)
        self.main_layout.addWidget(scroll_area)
        
        # Dictionary to store tables for each graph
        self.graph_tables = {}
        self.graph_sections = {}
        
        # Cursor info panel at the bottom (fixed)
        self.cursor_info_panel = self._create_cursor_info_panel()
        self.cursor_info_panel.hide()  # Initially hidden, shown when dual cursor mode is active
        self.main_layout.addWidget(self.cursor_info_panel)

    def _create_common_header(self):
        """Create common header table that syncs with all graph tables."""
        # Get theme colors for styling
        theme_colors = {}
        if hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        if theme_colors is None:
            # Fallback colors for space theme
            theme_colors = {
                'text_primary': '#e6f3ff',
                'text_secondary': '#ffffff',
                'surface': '#2d4a66',
                'surface_variant': '#3a5f7a',
                'border': '#4a90e2'
            }
        
        # Determine if this is a light theme
        is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
        
        # Adjust colors for light theme
        if is_light_theme:
            text_color = '#212121'
            border_color_base = '0, 0, 0'  # Black for light theme
            bg_color_base = '0, 0, 0'      # Black for light theme
            border_opacity = '0.2'
            bg_opacity = '0.05'
        else:
            text_color = theme_colors.get('text_primary', '#ffffff')
            border_color_base = '255, 255, 255' # White for dark themes
            bg_color_base = '255, 255, 255'     # White for dark themes
            border_opacity = '0.2'
            bg_opacity = '0.05'
        
        # Create header table
        self.header_table = QTableWidget()
        self.header_table.setRowCount(1)
        self.header_table.setFixedHeight(40)  # Fixed height for header
        
        # Disable horizontal scrollbar and enable column resizing
        self.header_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.header_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Setup headers based on current mode and visible stats
        headers = ['📊 Signal', '🎨']
        stats_info = self._get_stats_info_for_mode()
        
        for stat_key, icon, display_name in stats_info:
            is_cursor_stat = stat_key in ['c1', 'c2']
            if is_cursor_stat or stat_key in self.visible_stats:
                headers.append(f"{icon} {display_name}")
        
        self.header_table.setColumnCount(len(headers))
        self.header_table.setHorizontalHeaderLabels(headers)
        
        # Hide vertical header and make it non-interactive
        self.header_table.verticalHeader().setVisible(False)
        self.header_table.setSelectionMode(QTableWidget.NoSelection)
        self.header_table.setFocusPolicy(Qt.NoFocus)
        
        # Fill with empty items to show headers only
        for col in range(len(headers)):
            item = QTableWidgetItem("")
            item.setFlags(Qt.NoItemFlags)  # Make non-interactive
            self.header_table.setItem(0, col, item)
        
        # Set initial column widths with minimum sizes (only if no previous widths exist)
        # Check if we have saved column widths to restore
        has_saved_widths = hasattr(self, '_temp_saved_widths') and self._temp_saved_widths
        
        if not has_saved_widths:
            # Use default widths only for first time initialization
            logger.debug("Using default column widths for header table")
            self.header_table.setColumnWidth(0, 120)  # Signal name
            self.header_table.setColumnWidth(1, 30)   # Color - further reduced from 40 to 30
            for i in range(2, len(headers)):
                self.header_table.setColumnWidth(i, 80)  # Statistics
        else:
            # Restore saved widths
            logger.debug(f"Restoring saved widths in header creation: {self._temp_saved_widths}")
            for col, width in self._temp_saved_widths.items():
                if col < len(headers):
                    self.header_table.setColumnWidth(col, width)
                    logger.debug(f"Set header column {col} to width {width}")
            # Clear temporary saved widths
            delattr(self, '_temp_saved_widths')
        
        # Set minimum column widths to prevent columns from becoming too small
        header = self.header_table.horizontalHeader()
        header.setMinimumSectionSize(50)  # Minimum width for any column
        
        # Style the header table with theme-appropriate colors
        header_table_style = f"""
            QTableWidget {{
                background-color: rgba({bg_color_base}, {bg_opacity});
                border: 1px solid rgba({border_color_base}, {border_opacity});
                border-radius: 8px;
                gridline-color: rgba({border_color_base}, 0.3);
                color: {text_color};
            }}
            QHeaderView::section {{
                background-color: rgba({bg_color_base}, 0.15);
                border: 1px solid rgba({border_color_base}, 0.3);
                padding: 5px 8px;
                font-weight: bold;
                font-size: 12px;
                color: {text_color};
            }}
            QHeaderView::section:first {{
                font-size: 13px;
                color: {text_color};
            }}
            QTableWidget::item {{
                color: {text_color};
                background-color: transparent;
            }}
        """
        self.header_table.setStyleSheet(header_table_style)
        
        # Connect header resize signal to sync all tables
        header = self.header_table.horizontalHeader()
        header.sectionResized.connect(self._sync_column_widths)
        
        return self.header_table

    def _sync_column_widths(self, logical_index: int, old_size: int, new_size: int):
        """Sync column widths across all tables when header table is resized."""
        # Ensure minimum width is respected
        min_width = 50 if logical_index > 1 else (120 if logical_index == 0 else 30)
        new_size = max(new_size, min_width)
        
        # Update all graph tables to match header table column width
        for table in self.graph_tables.values():
            if logical_index < table.columnCount():
                # Temporarily disconnect signals to avoid recursion
                header = table.horizontalHeader()
                try:
                    header.sectionResized.disconnect()
                except:
                    pass  # Ignore if no connections exist
                
                # Set the new width
                table.setColumnWidth(logical_index, new_size)
                
                # Reconnect signals
                header.sectionResized.connect(lambda idx, old, new, t=table: self._on_graph_table_resized(t, idx, old, new))

    def _on_graph_table_resized(self, source_table: QTableWidget, logical_index: int, old_size: int, new_size: int):
        """Handle column resize from any graph table and sync to header and other tables."""
        # Ensure minimum width is respected
        min_width = 50 if logical_index > 1 else (120 if logical_index == 0 else 30)
        new_size = max(new_size, min_width)
        
        # Update header table
        if hasattr(self, 'header_table') and logical_index < self.header_table.columnCount():
            header = self.header_table.horizontalHeader()
            try:
                header.sectionResized.disconnect()
            except:
                pass
            self.header_table.setColumnWidth(logical_index, new_size)
            header.sectionResized.connect(self._sync_column_widths)
        
        # Update all other graph tables
        for table in self.graph_tables.values():
            if table != source_table and logical_index < table.columnCount():
                header = table.horizontalHeader()
                try:
                    header.sectionResized.disconnect()
                except:
                    pass
                table.setColumnWidth(logical_index, new_size)
                header.sectionResized.connect(lambda idx, old, new, t=table: self._on_graph_table_resized(t, idx, old, new))

    def _update_common_header(self):
        """Update the common header when cursor mode or visible stats change."""
        if hasattr(self, 'common_header') and self.common_header:
            # Save current column widths before recreating header
            saved_widths = self._save_current_column_widths()
            
            # Store saved widths temporarily for _create_common_header to use
            if saved_widths:
                self._temp_saved_widths = saved_widths
            
            # Remove old header
            self.main_layout.removeWidget(self.common_header)
            self.common_header.deleteLater()
            
            # Create new header (will use _temp_saved_widths if available)
            self.common_header = self._create_common_header()
            self.main_layout.insertWidget(0, self.common_header)

    def _setup_table_headers(self):
        """Setup table headers for all graph tables based on cursor mode and visible statistics."""
        # Save current column widths before updating headers
        saved_widths = self._save_current_column_widths()
        
        # Update headers for all existing graph tables
        for table in self.graph_tables.values():
            self._setup_table_headers_for_graph(table)
        
        # Restore column widths after header updates
        if saved_widths:
            self._restore_column_widths_to_all_tables(saved_widths)

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
                'text_primary': '#e6f3ff',
                'text_secondary': '#ffffff',
                'surface': '#2d4a66',
                'surface_variant': '#3a5f7a',
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
            border_opacity = '0.3'
            bg_opacity = '0.1'
            scrollbar_bg = 'rgba(0, 0, 0, 0.15)'
            scrollbar_handle = 'rgba(0, 0, 0, 0.4)'
            scrollbar_handle_hover = 'rgba(0, 0, 0, 0.6)'
            title_bg_opacity = '0.1'
            title_bg_color = 'rgba(255, 255, 255, 0.9)'  # Light background for title
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
            title_bg_color = 'rgba(0, 0, 0, 0.3)'  # Dark background for title
        
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
                border-radius: 8px;
                margin-top: 0px;
                margin-bottom: 1px;
                padding: 1px;
                background-color: rgba({bg_color_base}, {bg_opacity});
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: {title_bg_color};
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
        
        # Apply table styling to all graph tables
        table_style = f"""
                QTableWidget {{
                    background-color: rgba({bg_color_base}, {bg_opacity});
                    border: 1px solid rgba({border_color_base}, {border_opacity});
                    border-radius: 8px;
                    color: {text_color};
                    gridline-color: rgba({border_color_base}, 0.1);
                    selection-background-color: rgba(74, 144, 226, 0.3);
                    alternate-background-color: rgba({bg_color_base}, 0.08);
                }}
                
                QTableWidget::item {{
                    padding: 8px;
                    border: none;
                    color: {text_color};
                    background-color: transparent;
                }}
                
                QTableWidget::item:alternate {{
                    background-color: rgba({bg_color_base}, 0.08);
                    color: {text_color};
                }}
                
                QTableWidget::item:selected {{
                    background-color: rgba(74, 144, 226, 0.3);
                    color: {text_color};
                }}
                
                QTableWidget::item:hover {{
                    background-color: rgba({border_color_base}, 0.15);
                    color: {text_color};
                }}
                
                QHeaderView::section {{
                    background-color: rgba({bg_color_base}, 0.2);
                    color: {text_color};
                    padding: 8px;
                    border: 1px solid rgba({border_color_base}, 0.2);
                    font-weight: bold;
                }}
                
                QHeaderView::section:hover {{
                    background-color: rgba(74, 144, 226, 0.2);
                    color: {text_color};
                }}
            """
        
        # Apply styling to all graph tables
        for table in self.graph_tables.values():
            table.setStyleSheet(table_style)

    def update_theme(self, theme_colors=None):
        """Update the panel styling when theme changes."""
        # Apply theme styling to main panel
        self._apply_theme_styling(theme_colors)
        
        # Update all graph tables with new theme
        for table in self.graph_tables.values():
            self._apply_table_styling_to_single_table(table)
        
        # Update header table styling with new theme
        if hasattr(self, 'header_table') and self.header_table:
            self._update_header_table_theme(theme_colors)
        
        # Update cursor info panel if it exists
        if hasattr(self, 'cursor_info_panel') and self.cursor_info_panel:
            self._update_cursor_info_panel_theme(theme_colors)
        
        # Update all graph sections styling
        for graph_section in self.graph_sections.values():
            if graph_section:
                self._apply_graph_section_styling(graph_section)
        
        logger.debug("Theme updated for all statistics panel components")

    def _update_header_table_theme(self, theme_colors=None):
        """Update header table theme styling."""
        # Get theme colors
        if theme_colors is None and hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        if theme_colors is None:
            # Fallback colors for space theme
            theme_colors = {
                'text_primary': '#e6f3ff',
                'text_secondary': '#ffffff',
                'surface': '#2d4a66',
                'surface_variant': '#3a5f7a',
                'border': '#4a90e2'
            }
        
        # Determine if this is a light theme
        is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
        
        # Adjust colors for light theme
        if is_light_theme:
            text_color = '#212121'
            border_color_base = '0, 0, 0'  # Black for light theme
            bg_color_base = '0, 0, 0'      # Black for light theme
            border_opacity = '0.3'
            bg_opacity = '0.1'
        else:
            text_color = theme_colors.get('text_primary', '#ffffff')
            border_color_base = '255, 255, 255' # White for dark themes
            bg_color_base = '255, 255, 255'     # White for dark themes
            border_opacity = '0.2'
            bg_opacity = '0.05'
        
        # Update header table style
        header_table_style = f"""
            QTableWidget {{
                background-color: rgba({bg_color_base}, {bg_opacity});
                border: 1px solid rgba({border_color_base}, {border_opacity});
                border-radius: 8px;
                gridline-color: rgba({border_color_base}, 0.3);
                color: {text_color};
            }}
            QHeaderView::section {{
                background-color: rgba({bg_color_base}, 0.15);
                border: 1px solid rgba({border_color_base}, 0.3);
                padding: 5px 8px;
                font-weight: bold;
                font-size: 12px;
                color: {text_color};
            }}
            QHeaderView::section:first {{
                font-size: 13px;
                color: {text_color};
            }}
            QTableWidget::item {{
                color: {text_color};
                background-color: transparent;
            }}
        """
        self.header_table.setStyleSheet(header_table_style)

    def _update_cursor_info_panel_theme(self, theme_colors=None):
        """Update cursor info panel theme styling."""
        # Get theme colors
        if theme_colors is None and hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        # Determine if this is a light theme
        is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
        text_color = '#212121' if is_light_theme else '#ffffff'
        
        # Update all cursor labels
        for label in [self.cursor1_time_label, self.cursor2_time_label, 
                     self.delta_time_label, self.frequency_label]:
            if hasattr(self, label.objectName()) or label:
                current_style = label.styleSheet()
                # Extract background color from current style
                if 'background-color: rgba(74, 144, 226' in current_style:
                    bg_color = 'rgba(74, 144, 226, 0.15)'
                elif 'background-color: rgba(226, 74, 144' in current_style:
                    bg_color = 'rgba(226, 74, 144, 0.15)'
                elif 'background-color: rgba(144, 226, 74' in current_style:
                    bg_color = 'rgba(144, 226, 74, 0.15)'
                elif 'background-color: rgba(226, 144, 74' in current_style:
                    bg_color = 'rgba(226, 144, 74, 0.15)'
                else:
                    bg_color = 'rgba(74, 144, 226, 0.15)'
                
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-size: 13px;
                        font-weight: 600;
                        padding: 6px 10px;
                        border-radius: 4px;
                        background-color: {bg_color};
                        min-height: 20px;
                    }}
                """)

    def add_signal(self, full_signal_name: str, graph_index: int, signal_name: str, color: str):
        """
        Add a new signal to the appropriate graph table.
        
        Args:
            full_signal_name: Full signal name with graph suffix (e.g., "RPM (G1)")
            graph_index: Index of the graph this signal belongs to
            signal_name: Base signal name (e.g., "RPM")
            color: Color for visual identification
        """
        # Ensure graph section exists
        if graph_index not in self.graph_sections:
            self._create_graph_section(graph_index)
        
        # Get the table for this graph
        table = self.graph_tables[graph_index]
        
        # Add new row to table
        row_count = table.rowCount()
        table.insertRow(row_count)
        
        # Signal name
        name_item = QTableWidgetItem(signal_name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
        table.setItem(row_count, 0, name_item)
        
        # Color indicator button - smaller size for space efficiency
        color_btn = QPushButton()
        color_btn.setFixedSize(20, 16)  # Reduced from 30x20 to 20x16
        color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid rgba(255, 255, 255, 0.8);
            }}
        """)
        color_btn.clicked.connect(lambda: self._change_signal_color(full_signal_name))
        table.setCellWidget(row_count, 1, color_btn)
        
        # Statistics columns - initialize with empty values
        col_index = 2
        stats_info = self._get_stats_info_for_mode()
        for stat_key, icon, display_name in stats_info:
            is_cursor_stat = stat_key in ['c1', 'c2']
            if is_cursor_stat or stat_key in self.visible_stats:
                stat_item = QTableWidgetItem("-")
                stat_item.setFlags(stat_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                stat_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_count, col_index, stat_item)
                col_index += 1
        
        # Store signal data
        self.signal_data[full_signal_name] = {
            'graph_index': graph_index,
            'signal_name': signal_name,
            'color': color,
            'row_index': row_count,
            'color_button': color_btn,
            'table': table
        }
        
        logger.debug(f"Added signal {full_signal_name} to Graph {graph_index + 1} table at row {row_count}")
        
        # Auto-resize columns to content but respect minimum widths
        table.resizeColumnsToContents()
        
        # Ensure minimum column widths are maintained
        for col in range(table.columnCount()):
            current_width = table.columnWidth(col)
            min_width = 50 if col > 1 else (120 if col == 0 else 30)  # Different minimums for different columns
            if current_width < min_width:
                table.setColumnWidth(col, min_width)

    def _change_signal_color(self, full_signal_name: str):
        """Open color dialog to change signal color."""
        if full_signal_name not in self.signal_data:
            return
            
        current_color = QColor(self.signal_data[full_signal_name]['color'])
        new_color = QColorDialog.getColor(current_color, self, f"Select color for {self.signal_data[full_signal_name]['signal_name']}")
        
        if new_color.isValid():
            new_color_hex = new_color.name()
            # Update stored color
            self.signal_data[full_signal_name]['color'] = new_color_hex
            # Update button color
            color_btn = self.signal_data[full_signal_name]['color_button']
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {new_color_hex};
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border: 2px solid rgba(255, 255, 255, 0.8);
                }}
            """)
            # Emit signal for color change - use base signal name without graph suffix
            base_signal_name = self.signal_data[full_signal_name]['signal_name']
            self.signal_color_changed.emit(base_signal_name, new_color_hex)
            logger.debug(f"Emitted color change signal for '{base_signal_name}' to {new_color_hex}")

    def _create_graph_section(self, graph_index: int):
        """Create a new graph section with its own table and controls."""
        # Create group box for this graph
        section_title = f"⚙️ Graph {graph_index + 1}"
        graph_section = ClickableGroupBox(section_title, graph_index)
        
        # Main layout for the section - minimal padding for space efficiency
        section_layout = QVBoxLayout(graph_section)
        section_layout.setContentsMargins(2, 20, 2, 2)  # Reduced padding: left, top, right, bottom
        section_layout.setSpacing(2)  # Reduced spacing between elements
        
        # Control buttons removed - cleaner interface
        
        # Create table for this graph
        graph_table = QTableWidget()
        graph_table.setAlternatingRowColors(True)
        graph_table.setSelectionBehavior(QTableWidget.SelectRows)
        graph_table.setSelectionMode(QTableWidget.SingleSelection)
        graph_table.verticalHeader().setVisible(False)
        graph_table.horizontalHeader().setStretchLastSection(False)  # Disable auto-stretch for manual resize
        graph_table.setSortingEnabled(False)
        graph_table.setMaximumHeight(200)  # Limit height
        
        # Disable horizontal scrollbar and enable column resizing
        graph_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graph_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # Allow manual column resize
        
        # Set up table headers
        self._setup_table_headers_for_graph(graph_table)
        
        section_layout.addWidget(graph_table)
        
        # Store references
        self.graph_sections[graph_index] = graph_section
        self.graph_tables[graph_index] = graph_table
        
        # Add to container layout
        self.container_layout.addWidget(graph_section)
        
        # Apply styling
        self._apply_graph_section_styling(graph_section)
        
        # Apply table styling immediately
        self._apply_table_styling_to_single_table(graph_table)
        
        # Apply current column widths from header table if available
        self._sync_new_table_widths(graph_table)
        
        # Connect click signal
        graph_section.clicked.connect(self.graph_settings_requested.emit)
        
        logger.debug(f"Created graph section for Graph {graph_index + 1}")

    def _sync_new_table_widths(self, table: QTableWidget):
        """Sync new table column widths with current header table widths."""
        if hasattr(self, 'header_table') and self.header_table:
            for col in range(min(table.columnCount(), self.header_table.columnCount())):
                current_width = self.header_table.columnWidth(col)
                table.setColumnWidth(col, current_width)

    def _apply_table_styling_to_single_table(self, table: QTableWidget):
        """Apply current theme styling to a single table."""
        # Get theme colors
        theme_colors = {}
        if hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        if theme_colors is None:
            # Fallback colors for space theme
            theme_colors = {
                'text_primary': '#e6f3ff',
                'text_secondary': '#ffffff',
                'surface': '#2d4a66',
                'surface_variant': '#3a5f7a',
                'border': '#4a90e2'
            }
        
        # Determine if this is a light theme
        is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
        
        # Adjust colors for light theme
        if is_light_theme:
            text_color = '#212121'
            border_color_base = '0, 0, 0'  # Black for light theme
            bg_color_base = '0, 0, 0'      # Black for light theme
            border_opacity = '0.3'
            bg_opacity = '0.1'
        else:
            text_color = theme_colors.get('text_primary', '#ffffff')
            border_color_base = '255, 255, 255' # White for dark themes
            bg_color_base = '255, 255, 255'     # White for dark themes
            border_opacity = '0.2'
            bg_opacity = '0.05'
        
        # Apply table styling
        table_style = f"""
                QTableWidget {{
                    background-color: rgba({bg_color_base}, {bg_opacity});
                    border: 1px solid rgba({border_color_base}, {border_opacity});
                    border-radius: 8px;
                    color: {text_color};
                    gridline-color: rgba({border_color_base}, 0.1);
                    selection-background-color: rgba(74, 144, 226, 0.3);
                    alternate-background-color: rgba({bg_color_base}, 0.08);
                }}
                
                QTableWidget::item {{
                    padding: 8px;
                    border: none;
                    color: {text_color};
                    background-color: transparent;
                }}
                
                QTableWidget::item:alternate {{
                    background-color: rgba({bg_color_base}, 0.08);
                    color: {text_color};
                }}
                
                QTableWidget::item:selected {{
                    background-color: rgba(74, 144, 226, 0.3);
                    color: {text_color};
                }}
                
                QTableWidget::item:hover {{
                    background-color: rgba({border_color_base}, 0.15);
                    color: {text_color};
                }}
                
                QHeaderView::section {{
                    background-color: rgba({bg_color_base}, 0.2);
                    color: {text_color};
                    padding: 8px;
                    border: 1px solid rgba({border_color_base}, 0.2);
                    font-weight: bold;
                }}
                
                QHeaderView::section:hover {{
                    background-color: rgba(74, 144, 226, 0.2);
                    color: {text_color};
                }}
            """
        table.setStyleSheet(table_style)

    def _setup_table_headers_for_graph(self, table: QTableWidget):
        """Setup table headers for a specific graph table."""
        headers = ['Signal', '🎨']
        
        # Add statistics columns based on visible stats
        stats_info = self._get_stats_info_for_mode()
        for stat_key, icon, display_name in stats_info:
            is_cursor_stat = stat_key in ['c1', 'c2']
            if is_cursor_stat or stat_key in self.visible_stats:
                headers.append(f"{icon} {display_name}")
        
        table.setColumnCount(len(headers))
        
        # Hide table headers since we have common header
        table.horizontalHeader().setVisible(False)
        
        # Set column widths to match header table if it exists
        if hasattr(self, 'header_table') and self.header_table:
            for i in range(min(len(headers), self.header_table.columnCount())):
                width = self.header_table.columnWidth(i)
                table.setColumnWidth(i, width)
        else:
            # Fallback to default widths
            table.setColumnWidth(0, 120)  # Signal name column
            table.setColumnWidth(1, 30)   # Color column - further reduced from 40 to 30
            for i in range(2, len(headers)):
                table.setColumnWidth(i, 80)  # Statistics columns
        
        # Set minimum column widths to prevent columns from becoming too small
        table_header = table.horizontalHeader()
        table_header.setMinimumSectionSize(50)  # Minimum width for any column
        
        # Connect resize signal for syncing
        header = table.horizontalHeader()
        # Disconnect any existing connections first
        try:
            header.sectionResized.disconnect()
        except:
            pass
        # Connect to sync function
        header.sectionResized.connect(lambda idx, old, new, t=table: self._on_graph_table_resized(t, idx, old, new))

    def _apply_graph_section_styling(self, graph_section):
        """Apply styling to a graph section."""
        # Get theme colors
        theme_colors = {}
        if hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager.get_theme_colors()
        
        if not theme_colors:
            theme_colors = {
                'text_primary': '#e6f3ff',
                'surface': '#2d4a66',
                'surface_variant': '#3a5f7a',
                'border': '#4a90e2',
                'primary': '#4a90e2'
            }
        
        # Apply styling
        graph_section.setStyleSheet(f"""
            ClickableGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {theme_colors.get('border', '#4a90e2')};
                border-radius: 8px;
                margin-top: 0px;
                margin-bottom: 1px;
                padding: 1px;
                background-color: {theme_colors.get('surface', '#2d4a66')};
            }}
            ClickableGroupBox:hover {{
                border: 2px solid {theme_colors.get('primary', '#4a90e2')};
                background-color: {theme_colors.get('surface_variant', '#3a5f7a')};
            }}
            ClickableGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
                color: {theme_colors.get('primary', '#4a90e2')};
            }}
            /* Button styles removed - no buttons in sections */
        """)

    # Button-related methods removed for cleaner interface

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
        # Use theme-appropriate color for signal name
        name_label.setStyleSheet("")  # Will inherit from parent styling
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
        
        # Connect row splitter to sync with header
        row_splitter.splitterMoved.connect(
            lambda pos, idx, splitter=row_splitter: self._on_row_splitter_moved(pos, idx, splitter)
        )
        
        row_layout.addWidget(row_splitter)
        
        # Use theme-appropriate styling for row widget
        row_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(128, 128, 128, 0.08);
                border: 1px solid rgba(128, 128, 128, 0.2);
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
        # Use theme-appropriate styling - will inherit from parent
        value_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                background-color: rgba(128, 128, 128, 0.1);
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
        # Use theme-appropriate color for header
        header_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
            }
        """)
        layout.addWidget(header_label)
        
        # Value label
        value_label = QLabel(value)
        value_label.setObjectName(f"value_{name.lower()}")
        value_label.setAlignment(Qt.AlignCenter)
        # Use theme-appropriate styling
        value_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                background-color: rgba(128, 128, 128, 0.1);
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
        Update statistics for a specific signal in its graph table.
        
        Args:
            signal_name: Name of the signal (with graph suffix)
            stats: Dictionary with statistic values
        """
        if signal_name not in self.signal_data:
            logger.warning(f"Signal {signal_name} not found in statistics panel")
            return
        
        signal_info = self.signal_data[signal_name]
        row_index = signal_info['row_index']
        table = signal_info['table']
        
        # Update each statistic with proper formatting
        col_index = 2  # Start after Signal and Color columns
        stats_info = self._get_stats_info_for_mode()
        
        for stat_key, icon, display_name in stats_info:
            is_cursor_stat = stat_key in ['c1', 'c2']
            if is_cursor_stat or stat_key in self.visible_stats:
                if stat_key in stats:
                    value = stats[stat_key]
                    
                    if isinstance(value, (int, float)):
                        # Special formatting for duty cycle
                        if stat_key == 'duty_cycle':
                            formatted_value = f"{value:.1f}%"
                        # Full number formatting - no abbreviations
                        else:
                            # Format numbers without K, M abbreviations or scientific notation
                            if abs(value) >= 1:
                                # For larger numbers, show 2 decimal places
                                formatted_value = f"{value:.2f}"
                            elif abs(value) >= 0.0001:
                                # For small numbers, show more precision
                                formatted_value = f"{value:.6f}"
                            else:
                                # For very small numbers, use scientific notation as last resort
                                formatted_value = f"{value:.2e}"
                    else:
                        formatted_value = str(value)
                    
                    # Update table cell
                    if col_index < table.columnCount():
                        item = table.item(row_index, col_index)
                        if item:
                            item.setText(formatted_value)
                            # Add visual feedback for cursor values
                            if is_cursor_stat:
                                item.setBackground(QColor(74, 144, 226, 50))  # Light blue background
                
                col_index += 1

    def _clear_cursor_values(self):
        """Clear all cursor values from statistics display."""
        for signal_name, signal_info in self.signal_data.items():
            labels = signal_info['labels']
            
            # Clear cursor values (C1, C2)
            for cursor_key in ['c1', 'c2']:
                if cursor_key in labels and labels[cursor_key]:
                    labels[cursor_key].setText("--")
                    # Reset styling for cursor labels
                    # Use theme-appropriate styling
                    labels[cursor_key].setStyleSheet("""
                        QLabel {
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
            if self.is_datetime_axis:
                try:
                    dt = datetime.datetime.utcfromtimestamp(c1_time)
                    time_str = dt.strftime('%H:%M:%S.%f')[:-3]  # Show milliseconds
                    self.cursor1_time_label.setText(f"T1: {time_str}")
                except (ValueError, OSError, OverflowError):
                    self.cursor1_time_label.setText(f"T1: {c1_time:.4f}s")
            else:
                self.cursor1_time_label.setText(f"T1: {c1_time:.4f}s")
        else:
            self.cursor1_time_label.setText("T1: --")
            
        # Update cursor 2 position
        if 'c2' in cursor_positions:
            c2_time = cursor_positions['c2']
            if self.is_datetime_axis:
                try:
                    dt = datetime.datetime.utcfromtimestamp(c2_time)
                    time_str = dt.strftime('%H:%M:%S.%f')[:-3]  # Show milliseconds
                    self.cursor2_time_label.setText(f"T2: {time_str}")
                except (ValueError, OSError, OverflowError):
                    self.cursor2_time_label.setText(f"T2: {c2_time:.4f}s")
            else:
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
        Remove a signal from its graph table.
        
        Args:
            signal_name: Name of the signal to remove (with graph suffix)
        """
        if signal_name in self.signal_data:
            signal_info = self.signal_data[signal_name]
            row_index = signal_info['row_index']
            table = signal_info['table']
            graph_index = signal_info['graph_index']
            
            # Remove row from table
            table.removeRow(row_index)
            
            # Update row indices for remaining signals in the same graph
            for other_signal, other_info in self.signal_data.items():
                if (other_info['graph_index'] == graph_index and 
                    other_info['row_index'] > row_index):
                    other_info['row_index'] -= 1
            
            # Clean up references
            del self.signal_data[signal_name]
            
            logger.debug(f"Removed signal: {signal_name}")
            
            # Auto-resize columns to content but respect minimum widths
            table.resizeColumnsToContents()
            
            # Ensure minimum column widths are maintained
            for col in range(table.columnCount()):
                current_width = table.columnWidth(col)
                min_width = 50 if col > 1 else (120 if col == 0 else 40)
                if current_width < min_width:
                    table.setColumnWidth(col, min_width)

    def clear_all(self):
        """Remove all signals from all graph tables."""
        # Clear all graph tables
        for table in self.graph_tables.values():
            table.setRowCount(0)
        
        # Clear signal data
        self.signal_data.clear()
        
        logger.debug("Cleared all statistics")

    def remove_graph_section(self, graph_index: int):
        """Remove a graph section and all its signals."""
        if graph_index in self.graph_sections:
            # Remove all signals from this graph
            signals_to_remove = []
            for signal_name, signal_info in self.signal_data.items():
                if signal_info['graph_index'] == graph_index:
                    signals_to_remove.append(signal_name)
            
            for signal_name in signals_to_remove:
                del self.signal_data[signal_name]
            
            # Remove the graph section widget
            graph_section = self.graph_sections[graph_index]
            if graph_section:
                self.container_layout.removeWidget(graph_section)
                graph_section.deleteLater()
            
            # Remove from dictionaries
            del self.graph_sections[graph_index]
            if graph_index in self.graph_tables:
                del self.graph_tables[graph_index]
            
            logger.debug(f"Removed graph section for Graph {graph_index + 1}")

    def update_graph_count(self, new_graph_count: int):
        """Update the statistics panel when graph count changes."""
        # Save current column widths before making changes
        saved_widths = self._save_current_column_widths()
        
        current_graph_indices = list(self.graph_sections.keys())
        max_current_index = max(current_graph_indices) if current_graph_indices else -1
        
        # Remove graphs that are no longer needed
        for graph_index in current_graph_indices:
            if graph_index >= new_graph_count:
                self.remove_graph_section(graph_index)
        
        # Ensure we have sections for all needed graphs
        self.ensure_graph_sections(new_graph_count - 1)
        
        # Restore column widths after creating new sections
        if saved_widths:
            self._restore_column_widths_to_all_tables(saved_widths)
        
        logger.debug(f"Updated statistics panel for {new_graph_count} graphs with preserved column widths")

    def _save_current_column_widths(self) -> Dict[int, int]:
        """Save current column widths from header table."""
        saved_widths = {}
        if hasattr(self, 'header_table') and self.header_table:
            for col in range(self.header_table.columnCount()):
                saved_widths[col] = self.header_table.columnWidth(col)
            logger.debug(f"Saved column widths: {saved_widths}")
        return saved_widths

    def _restore_column_widths_to_all_tables(self, saved_widths: Dict[int, int]):
        """Restore column widths to header table and all graph tables."""
        logger.debug(f"Restoring column widths: {saved_widths}")
        
        # Restore to header table
        if hasattr(self, 'header_table') and self.header_table and saved_widths:
            for col, width in saved_widths.items():
                if col < self.header_table.columnCount():
                    self.header_table.setColumnWidth(col, width)
                    logger.debug(f"Restored header column {col} to width {width}")
        
        # Restore to all graph tables
        for table in self.graph_tables.values():
            if table and saved_widths:
                for col, width in saved_widths.items():
                    if col < table.columnCount():
                        table.setColumnWidth(col, width)

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
        
        # Save current column widths before making changes
        saved_widths = self._save_current_column_widths()
        
        # Update common header
        self._update_common_header()
        
        # Update table headers for all graphs
        self._setup_table_headers()
        
        # Recreate all signal rows to match new headers
        self._recreate_all_signal_rows()
        
        # Restore column widths after all changes
        if saved_widths:
            self._restore_column_widths_to_all_tables(saved_widths)
            logger.debug(f"Restored column widths after visible stats change: {saved_widths}")

    def ensure_graph_sections(self, max_graph_index: int):
        """Ensure graph sections exist for all graphs up to max_graph_index."""
        total_graphs = max_graph_index + 1
        
        # Save current column widths before creating new sections
        saved_widths = self._save_current_column_widths()
        
        # Create missing graph sections in order
        for graph_idx in range(total_graphs):
            if graph_idx not in self.graph_sections:
                self._create_graph_section(graph_idx)
                logger.debug(f"Auto-created graph section for Graph {graph_idx + 1}")
        
        # Apply saved widths to any newly created tables
        if saved_widths:
            for graph_idx in range(total_graphs):
                if graph_idx in self.graph_tables:
                    table = self.graph_tables[graph_idx]
                    for col, width in saved_widths.items():
                        if col < table.columnCount():
                            table.setColumnWidth(col, width)
        
        logger.debug(f"Ensured {total_graphs} graph sections exist with preserved column widths")

    def _reorder_graph_sections(self):
        """Reorder graph sections in the layout to match their indices."""
        # Remove all graph sections from layout
        for graph_section in self.graph_sections.values():
            if graph_section is not None:  # Skip placeholder entries
                self.container_layout.removeWidget(graph_section)
        
        # Add them back in correct order
        for graph_idx in sorted(self.graph_sections.keys()):
            graph_section = self.graph_sections[graph_idx]
            if graph_section is not None:  # Skip placeholder entries
                self.container_layout.addWidget(graph_section)
        
        logger.debug(f"Reordered {len([s for s in self.graph_sections.values() if s is not None])} graph sections")

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
            # Use theme-appropriate color
            message_label.setStyleSheet("font-style: italic; font-size: 14px;")
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