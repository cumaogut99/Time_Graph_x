# type: ignore
"""
Data Manager for Time Analysis Widget

Handles time-series data storage, processing, and management:
- Original data preservation for normalization
- Efficient data access and filtering
- Signal metadata management
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal as Signal

logger = logging.getLogger(__name__)

class TimeSeriesDataManager(QObject):
    """
    Manages time-series data for the analysis widget.
    
    Features:
    - Store original and processed data separately
    - Efficient data filtering by range
    - Signal metadata management
    - Data validation and preprocessing
    """
    
    # Signals
    data_changed = Signal()  # Emitted when data is modified
    signal_added = Signal(str)  # Emitted when new signal is added
    signal_removed = Signal(str)  # Emitted when signal is removed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data storage
        self.signals = {}  # signal_name -> SignalData
        self.raw_data = None  # Store the original DataFrame
        
        logger.info("TimeSeriesDataManager initialized")

    def set_data(self, df, time_column: Optional[str] = None):
        """
        Set data from a Vaex DataFrame.
        
        Args:
            df: Vaex DataFrame containing time-series data
            time_column: The name of the column to be used as the time axis.
                         If None, it will be auto-detected.
        """
        if df is None or df.length() == 0:
            logger.warning("set_data called with empty or None DataFrame")
            return
            
        # Store the raw data
        self.raw_data = df
        
        # Clear existing signals
        self.clear_all()
        
        # Get column names
        columns = df.get_column_names()
        
        # Find time column (usually first column or contains 'time')
        if not time_column or time_column not in columns:
            logger.debug(f"Time column '{time_column}' not provided or not found. Auto-detecting.")
            time_column_detected = None
            for col in columns:
                if 'time' in col.lower() or col == columns[0]:
                    time_column_detected = col
                    break
            time_column = time_column_detected
                
        if not time_column:
            logger.error("No time column found in data")
            return
            
        # Convert time data to numpy array
        time_data = df[time_column].to_numpy()
        
        # Add all other columns as signals
        for col in columns:
            if col != time_column:
                try:
                    y_data = df[col].to_numpy()
                    self.add_signal(col, time_data, y_data)
                except Exception as e:
                    logger.warning(f"Failed to add signal '{col}': {e}")
                    
        logger.info(f"Loaded {len(self.signals)} signals from DataFrame")

    def get_data(self):
        """Get the original DataFrame."""
        return self.raw_data

    def add_signal(self, name: str, x_data: np.ndarray, y_data: np.ndarray, 
                   metadata: Optional[Dict[str, Any]] = None):
        """
        Add a new signal to the data manager.
        
        Args:
            name: Signal name
            x_data: Time or X-axis data
            y_data: Signal values
            metadata: Optional metadata dictionary
        """
        # Validate input data
        if not isinstance(x_data, np.ndarray) or not isinstance(y_data, np.ndarray):
            raise ValueError("Data must be NumPy arrays")
            
        if len(x_data) != len(y_data):
            raise ValueError("X and Y data must have the same length")
            
        if len(x_data) == 0:
            raise ValueError("Data arrays cannot be empty")
        
        # Create signal data object
        signal_data = SignalData(
            name=name,
            x_data=x_data.copy(),
            y_data=y_data.copy(),
            metadata=metadata or {}
        )
        
        # Store signal
        self.signals[name] = signal_data
        
        logger.info(f"Added signal '{name}' with {len(y_data)} data points")
        
        # Emit signals
        self.signal_added.emit(name)
        self.data_changed.emit()

    def remove_signal(self, name: str):
        """
        Remove a signal from the data manager.
        
        Args:
            name: Signal name to remove
        """
        if name in self.signals:
            del self.signals[name]
            logger.info(f"Removed signal: {name}")
            
            # Emit signals
            self.signal_removed.emit(name)
            self.data_changed.emit()

    def get_signal(self, name: str) -> Optional['SignalData']:
        """
        Get signal data by name.
        
        Args:
            name: Signal name
            
        Returns:
            SignalData object or None if not found
        """
        return self.signals.get(name)

    def get_signal_names(self) -> List[str]:
        """Get list of all signal names."""
        return list(self.signals.keys())

    def get_filtered_data(self, name: str, x_range: Optional[Tuple[float, float]] = None) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Get filtered signal data within specified range.
        
        Args:
            name: Signal name
            x_range: Optional (start, end) range for filtering
            
        Returns:
            Tuple of (x_data, y_data) or None if signal not found
        """
        signal = self.get_signal(name)
        if not signal:
            return None
            
        x_data = signal.x_data
        y_data = signal.get_current_y_data()
        
        if x_range:
            start, end = x_range
            mask = (x_data >= start) & (x_data <= end)
            return x_data[mask], y_data[mask]
        
        return x_data, y_data

    def apply_normalization_to_signal(self, name: str, method: str = "peak"):
        """
        Apply normalization to a specific signal.
        
        Args:
            name: Signal name
            method: Normalization method ('peak', 'rms', 'zscore')
        """
        signal = self.get_signal(name)
        if not signal:
            return
            
        signal.apply_normalization(method)
        logger.info(f"Applied {method} normalization to signal: {name}")
        
        self.data_changed.emit()

    def remove_normalization_from_signal(self, name: str):
        """
        Remove normalization from a specific signal.
        
        Args:
            name: Signal name
        """
        signal = self.get_signal(name)
        if not signal:
            return
            
        signal.remove_normalization()
        logger.info(f"Removed normalization from signal: {name}")
        
        self.data_changed.emit()

    def apply_normalization_to_all(self, method: str = "peak"):
        """
        Apply normalization to all signals.
        
        Args:
            method: Normalization method
        """
        for signal in self.signals.values():
            signal.apply_normalization(method)
            
        logger.info(f"Applied {method} normalization to all signals")
        self.data_changed.emit()

    def remove_normalization_from_all(self):
        """Remove normalization from all signals."""
        for signal in self.signals.values():
            signal.remove_normalization()
            
        logger.info("Removed normalization from all signals")
        self.data_changed.emit()

    def clear_all(self):
        """Remove all signals."""
        signal_names = list(self.signals.keys())
        for name in signal_names:
            self.remove_signal(name)
            
        logger.info("Cleared all signals")

    def get_statistics(self, name: str, x_range: Optional[Tuple[float, float]] = None) -> Optional[Dict[str, float]]:
        """
        Calculate statistics for a signal within optional range.
        
        Args:
            name: Signal name
            x_range: Optional (start, end) range
            
        Returns:
            Statistics dictionary or None if signal not found
        """
        filtered_data = self.get_filtered_data(name, x_range)
        if not filtered_data:
            return None
            
        x_data, y_data = filtered_data
        
        if len(y_data) == 0:
            return None
            
        return {
            'mean': float(np.mean(y_data)),
            'max': float(np.max(y_data)),
            'min': float(np.min(y_data)),
            'rms': float(np.sqrt(np.mean(y_data**2))),
            'std': float(np.std(y_data)),
            'count': len(y_data)
        }

    def get_value_at_time(self, signal_name: str, time_pos: float) -> Optional[float]:
        """Get signal value at a specific time position using interpolation."""
        signal = self.get_signal(signal_name)
        if not signal:
            return None

        x_data = signal.x_data
        y_data = signal.get_current_y_data()

        if len(x_data) == 0:
            return None
        
        # Use numpy interpolation for efficiency
        try:
            # np.interp handles cases where time_pos is outside the x_data range
            # by returning the first or last value.
            y_value = np.interp(time_pos, x_data, y_data)
            return float(y_value)
        except Exception:
            return None


class SignalData:
    """
    Container for individual signal data and metadata.
    """
    
    def __init__(self, name: str, x_data: np.ndarray, y_data: np.ndarray, 
                 metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.x_data = x_data.copy()
        self.original_y_data = y_data.copy()  # Store original for normalization
        self.processed_y_data = y_data.copy()  # Current processed data
        self.metadata = metadata or {}
        
        # Processing state
        self.is_normalized = False
        self.normalization_method = None
        self.processing_history = []

    def get_current_y_data(self) -> np.ndarray:
        """Get the currently active Y data (original or processed)."""
        return self.processed_y_data

    def apply_normalization(self, method: str = "peak"):
        """
        Apply normalization to the signal.
        
        Args:
            method: Normalization method ('peak', 'rms', 'zscore')
        """
        if method == "peak":
            # Peak normalization: divide by maximum absolute value
            max_abs = np.max(np.abs(self.original_y_data))
            if max_abs > 0:
                self.processed_y_data = self.original_y_data / max_abs
                
        elif method == "rms":
            # RMS normalization: divide by RMS value
            rms_value = np.sqrt(np.mean(self.original_y_data**2))
            if rms_value > 0:
                self.processed_y_data = self.original_y_data / rms_value
                
        elif method == "zscore":
            # Z-score normalization: (x - mean) / std
            mean_val = np.mean(self.original_y_data)
            std_val = np.std(self.original_y_data)
            if std_val > 0:
                self.processed_y_data = (self.original_y_data - mean_val) / std_val
                
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
        self.is_normalized = True
        self.normalization_method = method
        self.processing_history.append(f"Applied {method} normalization")

    def remove_normalization(self):
        """Remove normalization and restore original data."""
        self.processed_y_data = self.original_y_data.copy()
        self.is_normalized = False
        self.normalization_method = None
        self.processing_history.append("Removed normalization")

    def get_data_range(self) -> Tuple[float, float, float, float]:
        """
        Get the data range for both axes.
        
        Returns:
            Tuple of (x_min, x_max, y_min, y_max)
        """
        return (
            float(np.min(self.x_data)),
            float(np.max(self.x_data)),
            float(np.min(self.get_current_y_data())),
            float(np.max(self.get_current_y_data()))
        )

    def get_info(self) -> Dict[str, Any]:
        """Get signal information summary."""
        x_min, x_max, y_min, y_max = self.get_data_range()
        
        return {
            'name': self.name,
            'length': len(self.x_data),
            'x_range': (x_min, x_max),
            'y_range': (y_min, y_max),
            'is_normalized': self.is_normalized,
            'normalization_method': self.normalization_method,
            'metadata': self.metadata.copy(),
            'processing_history': self.processing_history.copy()
        }