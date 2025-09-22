# type: ignore
from typing import Dict, Any, Optional, TYPE_CHECKING
import logging
import vaex
from PyQt5.QtGui import QPainter, QColor

from src.widgets.base_widget import BaseWidget, WidgetMetadata, PortDescriptor, DataType
from src.widgets.widget_factory import register_widget

if TYPE_CHECKING:
    from .dialog import TimeGraphDialog

logger = logging.getLogger(__name__)

@register_widget("time_graph", "Visualization")
class TimeGraphCanvasWidget(BaseWidget):
    """
    Canvas widget for advanced time-series analysis.
    Shows a placeholder on the canvas. The actual analysis interface is in a separate dialog.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.metadata = WidgetMetadata(
            name="Time Graph",
            description="Advanced time-series analysis with interactive cursors and real-time statistics.",
            category="Visualization",
            icon="icons/trending-up.svg",
            input_ports=[
                PortDescriptor(
                    name="data", 
                    data_type=DataType.VAEX_DATAFRAME,
                    description="Vaex DataFrame with time-series data to analyze.",
                )
            ],
            output_ports=[]
        )
        self.widget_name = self.metadata.name
        
        # Setup complete visual appearance with correct metadata
        self._setup_visual_appearance()

        self.input_df: Optional[vaex.DataFrame] = None
        self._dialog: Optional['TimeGraphDialog'] = None
        self._initialize_default_settings()
        self.set_size(120, 80)
        self.update()

    def set_size(self, width: int, height: int) -> None:
        """Set the canvas placeholder size for this widget."""
        self.setRect(0, 0, width, height)
        self.update()

    def _initialize_default_settings(self):
        """Set up the default configuration for the widget."""
        self.settings = {
            "x_column": None,
            "y_columns": [],
            "title": "Time Graph",
            "cursor_mode": "none",  # none, single, dual, range
            "normalize_data": False,
            "statistics_enabled": True,
            "show_grid": True,
            "line_width": 2,
            "color_scheme": "Default Colors",
        }

    def process_data(self, input_data: Dict[str, Any]) -> bool:
        """
        Process the input Vaex DataFrame (triggered by workflow engine).
        """
        print(f"🔍 DEBUG: Time Analysis process_data called with: {input_data}")
        self.input_df = input_data.get("data")
        print(f"🔍 DEBUG: Time Analysis extracted input_df: {self.input_df}")
        
        if self.input_df is None:
            self.set_info("No data")
            if self._dialog:
                self._dialog.update_data(None)
            return False

        self._auto_select_columns()
        
        # Properties paneli için detaylı bilgi
        rows, cols = self.input_df.shape
        selected_y_cols = len(self.settings.get('y_columns', []))
        self.set_info(f"{rows:,} rows, {cols} cols, {selected_y_cols} selected")

        # If dialog is open, update it with new data
        if self._dialog and self._dialog.isVisible():
            print(f"🔍 DEBUG: Dialog is open, updating with new data")
            self._dialog.update_data(self.input_df)
        
        return True

    def _auto_select_columns(self):
        """Automatically select the first suitable columns for plotting."""
        if self.input_df is None:
            return
        
        current_x = self.settings.get("x_column")
        current_y = self.settings.get("y_columns")

        # Only auto-select if columns are not already set
        if current_x and current_y:
            return
            
        columns = self.input_df.get_column_names()
        
        time_candidates = [c for c in columns if 'time' in c.lower()]
        if time_candidates:
            self.settings['x_column'] = time_candidates[0]
        else:
            self.settings['x_column'] = columns[0]
            
        # Vaex DataFrame için numeric kolon kontrolü
        numeric_cols = []
        for col in columns:
            if col != self.settings['x_column']:
                try:
                    # Vaex'te numeric kontrolü için dtype kullan
                    dtype = str(self.input_df[col].dtype)
                    if any(t in dtype.lower() for t in ['int', 'float', 'double', 'number']):
                        numeric_cols.append(col)
                except:
                    # Eğer dtype kontrolü başarısızsa, tüm kolonları ekle
                    numeric_cols.append(col)
        self.settings['y_columns'] = numeric_cols[:3]  # Limit to 3 for performance

    def open_widget_dialog(self):
        """Opens the advanced time-series analysis dialog."""
        if self._dialog is None:
            from .dialog import TimeGraphDialog  # Lazy import
            self._dialog = TimeGraphDialog(self)
        
        print(f"🔍 DEBUG: Time Graph dialog açılıyor, input_df: {self.input_df}")
        
        # Pass the current data to the dialog
        self._dialog.update_data(self.input_df)

        # Dialog'u göster
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()