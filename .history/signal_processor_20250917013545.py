# type: ignore
"""
Signal Processor for Time Graph Widget

Handles signal processing operations including:
- Data normalization and scaling
- Statistical calculations
- Signal filtering and conditioning
- Performance-optimized data operations
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread, QMutex, QMutexLocker

logger = logging.getLogger(__name__)

class SignalProcessor(QObject):
    """
    High-performance signal processor for time-series data.
    
    Features:
    - Memory-efficient operations using numpy views
    - Threaded processing for large datasets
    - Caching for repeated calculations
    - Optimized statistical computations
    """
    
    # Signals
    processing_started = Signal()
    processing_finished = Signal()
    statistics_updated = Signal(dict)  # Updated statistics
    
    def __init__(self):
        super().__init__()
        self.signal_data = {}  # Dict of signal_name -> data_dict
        self.normalized_data = {}  # Cache for normalized data
        self.statistics_cache = {}  # Cache for statistics
        self.mutex = QMutex()  # Thread safety
        
        # Processing parameters
        self.normalization_method = "peak"  # peak, rms, minmax
        self.statistics_window_size = 1000  # Rolling statistics window
        
    def process_data(self, df, normalize: bool = False, time_column: Optional[str] = None) -> Dict[str, Dict]:
        """
        Process Vaex DataFrame and extract all signals.
        
        Args:
            df: Vaex DataFrame containing time-series data
            normalize: Whether to apply normalization
            time_column: The name of the column to be used as the time axis.
                         If None, it will be auto-detected.
            
        Returns:
            Dict of signal_name -> signal_data_dict
        """
        if df is None or df.length() == 0:
            logger.warning("process_data called with empty or None DataFrame")
            return {}
            
        self.processing_started.emit()
        
        try:
            # Clear existing data
            self.clear_all_data()
            
            # Get column names
            columns = df.get_column_names()
            
            # Find time column (usually first column or contains 'time')
            if not time_column or time_column not in columns:
                logger.debug(f"SignalProcessor: Time column '{time_column}' not provided or not found. Auto-detecting.")
                time_column_detected = None
                for col in columns:
                    if 'time' in col.lower() or col == columns[0]:
                        time_column_detected = col
                        break
                time_column = time_column_detected
                    
            if not time_column:
                logger.error("No time column found in data")
                return {}
                
            # Convert time data to numpy array
            time_data = df[time_column].to_numpy()
            
            # Process all other columns as signals
            for col in columns:
                if col != time_column:
                    try:
                        y_data = df[col].to_numpy()
                        self.add_signal(col, time_data, y_data)
                    except Exception as e:
                        logger.warning(f"Failed to process signal '{col}': {e}")
            
            # Apply normalization if requested
            if normalize:
                self.apply_normalization(method=self.normalization_method)
                
            logger.info(f"Processed {len(self.signal_data)} signals from DataFrame")
            
            return self.get_all_signals()
            
        finally:
            self.processing_finished.emit()

    def add_signal(self, name: str, x_data: np.ndarray, y_data: np.ndarray, 
                   metadata: Optional[Dict] = None):
        """
        Add or update signal data with memory-efficient storage.
        
        Args:
            name: Signal identifier
            x_data: Time/X-axis data (shared reference when possible)
            y_data: Signal values
            metadata: Additional signal information
        """
        with QMutexLocker(self.mutex):
            # Use memory views for efficiency
            if not isinstance(x_data, np.ndarray):
                x_data = np.asarray(x_data, dtype=np.float64)
            if not isinstance(y_data, np.ndarray):
                y_data = np.asarray(y_data, dtype=np.float64)
            
            # Store signal data
            self.signal_data[name] = {
                'x_data': x_data,
                'y_data': y_data,
                'original_y': y_data.copy(),  # Keep original for normalization
                'metadata': metadata or {},
                'last_modified': np.datetime64('now')
            }
            
            # Clear related caches
            self._clear_cache(name)
            
            logger.debug(f"Added signal '{name}' with {len(y_data)} points")
    
    def remove_signal(self, name: str):
        """Remove signal and clear associated caches."""
        with QMutexLocker(self.mutex):
            if name in self.signal_data:
                del self.signal_data[name]
            if name in self.normalized_data:
                del self.normalized_data[name]
            if name in self.statistics_cache:
                del self.statistics_cache[name]
            
            logger.debug(f"Removed signal '{name}'")
    
    def get_signal_data(self, name: str) -> Optional[Dict]:
        """Get signal data safely."""
        with QMutexLocker(self.mutex):
            return self.signal_data.get(name, {}).copy()
    
    def get_all_signals(self) -> Dict[str, Dict]:
        """Get all signal data safely."""
        with QMutexLocker(self.mutex):
            return {name: data.copy() for name, data in self.signal_data.items()}
    
    def apply_normalization(self, signal_names: Optional[List[str]] = None, 
                          method: str = "peak") -> Dict[str, np.ndarray]:
        """
        Apply normalization to specified signals or all signals.
        
        Args:
            signal_names: List of signals to normalize (None for all)
            method: Normalization method ('peak', 'rms', 'minmax', 'zscore')
            
        Returns:
            Dict of signal_name -> normalized_y_data
        """
        self.processing_started.emit()
        
        try:
            with QMutexLocker(self.mutex):
                if signal_names is None:
                    signal_names = list(self.signal_data.keys())
                
                normalized_results = {}
                
                for name in signal_names:
                    if name not in self.signal_data:
                        continue
                    
                    y_data = self.signal_data[name]['y_data']
                    
                    # Check cache first
                    cache_key = f"{name}_{method}_{hash(y_data.tobytes())}"
                    if cache_key in self.normalized_data:
                        normalized_y = self.normalized_data[cache_key]
                    else:
                        # Perform normalization
                        normalized_y = self._normalize_array(y_data, method)
                        self.normalized_data[cache_key] = normalized_y
                    
                    # Update signal data
                    self.signal_data[name]['y_data'] = normalized_y
                    self.signal_data[name]['normalized'] = True
                    self.signal_data[name]['normalization_method'] = method
                    
                    normalized_results[name] = normalized_y
                    
                    logger.debug(f"Normalized signal '{name}' using {method} method")
                
                return normalized_results
                
        finally:
            self.processing_finished.emit()
    
    def remove_normalization(self, signal_names: Optional[List[str]] = None) -> Dict[str, np.ndarray]:
        """
        Remove normalization and restore original data.
        
        Args:
            signal_names: List of signals to denormalize (None for all)
            
        Returns:
            Dict of signal_name -> original_y_data
        """
        with QMutexLocker(self.mutex):
            if signal_names is None:
                signal_names = list(self.signal_data.keys())
            
            restored_results = {}
            
            for name in signal_names:
                if name not in self.signal_data:
                    continue
                
                # Restore original data
                original_y = self.signal_data[name]['original_y']
                self.signal_data[name]['y_data'] = original_y.copy()
                self.signal_data[name]['normalized'] = False
                
                restored_results[name] = original_y
                
                logger.debug(f"Restored original data for signal '{name}'")
            
            return restored_results
    
    def _normalize_array(self, data: np.ndarray, method: str) -> np.ndarray:
        """
        Normalize array using specified method with optimized algorithms.
        
        Args:
            data: Input array
            method: Normalization method
            
        Returns:
            Normalized array
        """
        if len(data) == 0:
            return data.copy()
        
        if method == "peak":
            # Peak normalization (divide by absolute maximum)
            peak_val = np.max(np.abs(data))
            return data / peak_val if peak_val != 0 else data.copy()
            
        elif method == "rms":
            # RMS normalization
            rms_val = np.sqrt(np.mean(data**2))
            return data / rms_val if rms_val != 0 else data.copy()
            
        elif method == "minmax":
            # Min-Max normalization to [0, 1]
            min_val, max_val = np.min(data), np.max(data)
            range_val = max_val - min_val
            return (data - min_val) / range_val if range_val != 0 else data.copy()
            
        elif method == "zscore":
            # Z-score normalization (mean=0, std=1)
            mean_val, std_val = np.mean(data), np.std(data)
            return (data - mean_val) / std_val if std_val != 0 else data.copy()
            
        else:
            logger.warning(f"Unknown normalization method: {method}")
            return data.copy()
    
    def calculate_statistics(self, signal_names: Optional[List[str]] = None, 
                           time_range: Optional[Tuple[float, float]] = None,
                           duty_cycle_threshold_mode: str = "auto",
                           duty_cycle_threshold_value: float = 0.0) -> Dict[str, Dict]:
        """
        Calculate comprehensive statistics for signals.
        
        Args:
            signal_names: Signals to analyze (None for all)
            time_range: Time range for analysis (start, end)
            duty_cycle_threshold_mode: "auto" (use mean) or "manual" (use custom value)
            duty_cycle_threshold_value: Custom threshold value for manual mode
            
        Returns:
            Dict of signal_name -> statistics_dict
        """
        with QMutexLocker(self.mutex):
            if signal_names is None:
                signal_names = list(self.signal_data.keys())
            
            results = {}
            
            for name in signal_names:
                if name not in self.signal_data:
                    continue
                
                signal_info = self.signal_data[name]
                x_data = signal_info['x_data']
                y_data = signal_info['y_data']
                
                # Apply time range filter if specified
                if time_range is not None:
                    start_time, end_time = time_range
                    mask = (x_data >= start_time) & (x_data <= end_time)
                    if np.any(mask):
                        y_subset = y_data[mask]
                        x_subset = x_data[mask]
                    else:
                        continue
                else:
                    y_subset = y_data
                    x_subset = x_data
                
                # Calculate statistics efficiently
                stats = self._calculate_signal_statistics(y_subset, x_subset, duty_cycle_threshold_mode, duty_cycle_threshold_value)
                results[name] = stats
            
            return results
    
    def get_statistics(self, signal_name: str, time_range: Optional[Tuple[float, float]] = None,
                      duty_cycle_threshold_mode: str = "auto", duty_cycle_threshold_value: float = 0.0) -> Optional[Dict[str, float]]:
        """
        Get statistics for a specific signal.
        
        Args:
            signal_name: Signal identifier
            time_range: Optional time range (start, end)
            duty_cycle_threshold_mode: "auto" (use mean) or "manual" (use custom value)
            duty_cycle_threshold_value: Custom threshold value for manual mode
            
        Returns:
            Statistics dictionary or None if signal not found
        """
        stats_dict = self.calculate_statistics([signal_name], time_range, duty_cycle_threshold_mode, duty_cycle_threshold_value)
        return stats_dict.get(signal_name)
    
    def _calculate_signal_statistics(self, y_data: np.ndarray, x_data: np.ndarray) -> Dict[str, float]:
        """
        Calculate comprehensive statistics for a single signal.
        
        Optimized for performance with vectorized operations.
        """
        if len(y_data) == 0:
            return {}
        
        # Basic statistics (vectorized)
        stats = {
            'count': len(y_data),
            'mean': np.mean(y_data),
            'std': np.std(y_data),
            'min': np.min(y_data),
            'max': np.max(y_data),
            'median': np.median(y_data),
            'rms': np.sqrt(np.mean(y_data**2)),
            'peak_to_peak': np.ptp(y_data),
        }
        
        # Percentiles
        if len(y_data) > 1:
            percentiles = np.percentile(y_data, [25, 75])
            stats['q25'] = percentiles[0]
            stats['q75'] = percentiles[1]
            stats['iqr'] = percentiles[1] - percentiles[0]
        
        # Duty Cycle Calculation (based on mean as threshold)
        if stats['mean'] is not None and len(y_data) > 1:
            try:
                threshold = stats['mean']
                # Find indices where the signal crosses the threshold
                crossings = np.where(np.diff(y_data > threshold))[0]
                
                # Calculate time spent above threshold
                high_time = 0
                is_high = y_data[0] > threshold
                last_cross_time = x_data[0]

                for cross_idx in crossings:
                    cross_time = x_data[cross_idx]
                    if is_high:
                        high_time += cross_time - last_cross_time
                    is_high = not is_high
                    last_cross_time = cross_time
                
                # Add time for the last segment
                if is_high:
                    high_time += x_data[-1] - last_cross_time

                total_duration = x_data[-1] - x_data[0]
                stats['duty_cycle'] = (high_time / total_duration) * 100 if total_duration > 0 else 0
            except Exception as e:
                logger.warning(f"Could not calculate duty cycle: {e}")
                stats['duty_cycle'] = 0
        else:
            stats['duty_cycle'] = 0

        # Time-based statistics
        if len(x_data) > 1:
            dt = np.diff(x_data)
            stats['sample_rate'] = 1.0 / np.mean(dt) if np.mean(dt) > 0 else 0
            stats['duration'] = x_data[-1] - x_data[0]
        
        # Advanced statistics (if enough data points)
        if len(y_data) > 10:
            # Skewness and kurtosis approximation
            centered = y_data - stats['mean']
            if stats['std'] > 0:
                normalized = centered / stats['std']
                stats['skewness'] = np.mean(normalized**3)
                stats['kurtosis'] = np.mean(normalized**4) - 3
        
        return stats
    
    def get_signal_at_time(self, signal_name: str, time_point: float) -> Optional[float]:
        """
        Get signal value at specific time point using interpolation.
        
        Args:
            signal_name: Signal identifier
            time_point: Time point to query
            
        Returns:
            Interpolated signal value or None if not found
        """
        with QMutexLocker(self.mutex):
            if signal_name not in self.signal_data:
                return None
            
            signal_info = self.signal_data[signal_name]
            x_data = signal_info['x_data']
            y_data = signal_info['y_data']
            
            if len(x_data) == 0 or len(y_data) == 0:
                return None
            
            # Check bounds
            if time_point < x_data[0] or time_point > x_data[-1]:
                return None
            
            # Linear interpolation
            return float(np.interp(time_point, x_data, y_data))
    
    def get_signal_range(self, signal_name: str, start_time: float, end_time: float) -> Optional[Dict]:
        """
        Get signal data within time range.
        
        Args:
            signal_name: Signal identifier
            start_time: Range start time
            end_time: Range end time
            
        Returns:
            Dict with x_data, y_data, and statistics for the range
        """
        with QMutexLocker(self.mutex):
            if signal_name not in self.signal_data:
                return None
            
            signal_info = self.signal_data[signal_name]
            x_data = signal_info['x_data']
            y_data = signal_info['y_data']
            
            # Find indices within range
            mask = (x_data >= start_time) & (x_data <= end_time)
            
            if not np.any(mask):
                return None
            
            x_range = x_data[mask]
            y_range = y_data[mask]
            
            # Calculate statistics for range
            stats = self._calculate_signal_statistics(y_range, x_range)
            
            return {
                'x_data': x_range,
                'y_data': y_range,
                'statistics': stats
            }
    
    def _clear_cache(self, signal_name: Optional[str] = None):
        """Clear caches for specific signal or all signals."""
        if signal_name:
            # Clear caches for specific signal
            keys_to_remove = [key for key in self.normalized_data.keys() if key.startswith(f"{signal_name}_")]
            for key in keys_to_remove:
                del self.normalized_data[key]
            
            if signal_name in self.statistics_cache:
                del self.statistics_cache[signal_name]
        else:
            # Clear all caches
            self.normalized_data.clear()
            self.statistics_cache.clear()
    
    def clear_all_data(self):
        """Clear all signal data and caches."""
        with QMutexLocker(self.mutex):
            self.signal_data.clear()
            self.normalized_data.clear()
            self.statistics_cache.clear()
            
            logger.info("Cleared all signal data and caches")
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics."""
        with QMutexLocker(self.mutex):
            signal_memory = sum(
                data['x_data'].nbytes + data['y_data'].nbytes + data['original_y'].nbytes
                for data in self.signal_data.values()
            )
            
            cache_memory = sum(
                arr.nbytes for arr in self.normalized_data.values()
            )
            
            return {
                'signal_data_bytes': signal_memory,
                'cache_bytes': cache_memory,
                'total_bytes': signal_memory + cache_memory,
                'signal_count': len(self.signal_data)
            }
