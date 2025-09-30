"""
Graph Renderer - Handles segmented and concatenated graph rendering
"""

import logging
import numpy as np
import pyqtgraph as pg
from typing import List, Dict, Any, Tuple, Optional
from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread

logger = logging.getLogger(__name__)


class DeviationCalculator(QObject):
    """
    Performs deviation calculations in a separate thread.
    Emits results when calculations are complete.
    """
    result_ready = Signal(dict)

    def __init__(self, signal_data: np.ndarray, settings: Dict[str, Any]):
        super().__init__()
        self.signal_data = signal_data
        self.settings = settings
        self.should_stop = False

    def run(self):
        """Starts the calculation."""
        if self.should_stop:
            return
        results = self._calculate_basic_deviation(self.signal_data, self.settings)
        if not self.should_stop:
            self.result_ready.emit(results)
    
    def stop(self):
        """Stop the calculation."""
        self.should_stop = True
        
    def _calculate_basic_deviation(self, signal_data: np.ndarray, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform vectorized calculation of basic deviation analysis.
        This optimized version avoids loops for performance.
        """
        if len(signal_data) < 2:
            return {'deviations': [], 'bands': [], 'alerts': [], 'trend_line': [], 'red_segments': []}

        results = {
            'deviations': [], 'bands': [], 'alerts': [], 'trend_line': [], 'red_segments': []
        }

        # Trend Analysis (already reasonably performant)
        if settings.get('trend_analysis', {}).get('enabled', False):
            sensitivity = settings['trend_analysis'].get('sensitivity', 3)
            results['trend_line'] = self._calculate_trend_line(signal_data, sensitivity)
        
        # --- Optimized Fluctuation, Bands, and Red Segments Calculation ---
        fluctuation_settings = settings.get('fluctuation_detection', {})
        if fluctuation_settings.get('enabled', False):
            window_size = fluctuation_settings.get('sample_window', 20)
            threshold_percent = fluctuation_settings.get('threshold_percent', 10.0)
            
            if len(signal_data) < window_size:
                return results

            # Use a single rolling mean calculation for all features
            # Pad the data at the beginning to handle edges correctly
            padded_data = np.pad(signal_data, (window_size - 1, 0), mode='edge')
            
            # Create a rolling window view
            shape = (len(signal_data), window_size)
            strides = (signal_data.strides[0], signal_data.strides[0])
            rolling_view = np.lib.stride_tricks.as_strided(padded_data, shape=shape, strides=strides)
            
            # Calculate rolling mean vectorized
            rolling_mean = np.mean(rolling_view, axis=1)

            # --- 1. Fluctuation Detection ---
            # Calculate deviation percentage, handle division by zero
            epsilon = 1e-9
            deviation_percent = np.abs((signal_data - rolling_mean) / (rolling_mean + epsilon)) * 100
            results['deviations'] = deviation_percent.tolist()

            # Find alerts
            alert_indices = np.where(deviation_percent > threshold_percent)[0]
            results['alerts'] = [{
                'index': int(i),
                'value': signal_data[i],
                'expected': rolling_mean[i],
                'deviation_percent': deviation_percent[i]
            } for i in alert_indices]

            # --- 2. Deviation Bands ---
            if settings.get('visual_settings', {}).get('show_bands', False):
                threshold_val = rolling_mean * (threshold_percent / 100.0)
                upper_band = rolling_mean + threshold_val
                lower_band = rolling_mean - threshold_val
                results['bands'] = {'upper': upper_band.tolist(), 'lower': lower_band.tolist()}

            # --- 3. Red Segments ---
            if fluctuation_settings.get('red_highlighting', False):
                exceeds_threshold = deviation_percent > threshold_percent
                
                # Find start and end of consecutive True blocks
                diff = np.diff(np.concatenate(([False], exceeds_threshold, [False])).astype(int))
                starts = np.where(diff == 1)[0]
                ends = np.where(diff == -1)[0] - 1
                
                red_segments = []
                for start, end in zip(starts, ends):
                    if end >= start:
                        segment_slice = slice(start, end + 1)
                        red_segments.append({
                            'start_index': int(start),
                            'end_index': int(end),
                            'values': signal_data[segment_slice].tolist(),
                            'deviation_percent': np.max(deviation_percent[segment_slice])
                        })
                results['red_segments'] = red_segments

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
        
    # --- The old, slow methods below are now replaced by the vectorized _calculate_basic_deviation ---
    # We can remove them or keep them for reference, but they are no longer called.

    def _detect_fluctuations(self, data: np.ndarray, window_size: int, threshold_percent: float) -> tuple:
        """
        [DEPRECATED] Detect short-term fluctuations. 
        Replaced by vectorized version in _calculate_basic_deviation.
        """
        deviations = []
        alerts = []
        
        if len(data) < window_size:
            return deviations, alerts

        # Vectorized calculation
        # Create a rolling window view of the data without copying data
        shape = (data.shape[0] - window_size + 1, window_size)
        strides = (data.strides[0], data.strides[0])
        rolling_data = np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)
        
        # Calculate rolling mean
        rolling_mean = np.mean(rolling_data, axis=1)
        
        # Current values are the ones after each window
        current_values = data[window_size:]
        
        # Calculate deviation percentage, handle division by zero
        # Add a small epsilon to avoid division by zero
        epsilon = 1e-9
        deviation_percent = np.abs((current_values - rolling_mean[:-1]) / (rolling_mean[:-1] + epsilon)) * 100
        
        deviations = deviation_percent.tolist()
        
        # Find alerts where deviation exceeds threshold
        alert_indices = np.where(deviation_percent > threshold_percent)[0] + window_size
        
        alerts = [{
            'index': int(i),
            'value': data[i],
            'expected': rolling_mean[i - window_size],
            'deviation_percent': deviation_percent[i - window_size]
        } for i in alert_indices]
        
        return deviations, alerts

    def _calculate_deviation_bands(self, data: np.ndarray, settings: Dict) -> Dict[str, List[float]]:
        """
        [DEPRECATED] Calculate deviation bands for visualization.
        Replaced by vectorized version in _calculate_basic_deviation.
        """
        if len(data) < 2:
            return {'upper': [], 'lower': []}
            
        window_size = settings.get('fluctuation_detection', {}).get('sample_window', 20)
        threshold_percent = settings.get('fluctuation_detection', {}).get('threshold_percent', 10.0)

        # Use pandas for efficient rolling window calculations
        try:
            import pandas as pd
            s = pd.Series(data)
            rolling_mean = s.rolling(window=window_size, min_periods=1).mean().to_numpy()
            
            threshold_val = rolling_mean * (threshold_percent / 100.0)
            
            upper_band = rolling_mean + threshold_val
            lower_band = rolling_mean - threshold_val
            
            return {'upper': upper_band.tolist(), 'lower': lower_band.tolist()}
            
        except ImportError:
            logger.warning("Pandas not found, falling back to slower deviation band calculation.")
            # Fallback to slower method if pandas is not available
            upper_band, lower_band = [], []
            for i in range(len(data)):
                start_idx = max(0, i - window_size + 1)
                window_data = data[start_idx:i+1]
                mean_val = np.mean(window_data)
                threshold_val = mean_val * (threshold_percent / 100)
                upper_band.append(mean_val + threshold_val)
                lower_band.append(mean_val - threshold_val)
            return {'upper': upper_band, 'lower': lower_band}

    def _calculate_red_segments(self, data: np.ndarray, settings: Dict) -> List[Dict[str, Any]]:
        """
        [DEPRECATED] Calculate red segments where signal exceeds threshold.
        Replaced by vectorized version in _calculate_basic_deviation.
        """
        if len(data) < 2:
            return []
            
        window_size = settings.get('fluctuation_detection', {}).get('sample_window', 20)
        threshold_percent = settings.get('fluctuation_detection', {}).get('threshold_percent', 10.0)

        # Use pandas for efficient rolling window calculations
        try:
            import pandas as pd
            s = pd.Series(data)
            rolling_mean = s.rolling(window=window_size, min_periods=1).mean().to_numpy()
            
            # Add a small epsilon to avoid division by zero
            epsilon = 1e-9
            deviation_percent = np.abs((data - rolling_mean) / (rolling_mean + epsilon)) * 100
            
            # Find indices where deviation exceeds threshold
            exceeds_threshold = deviation_percent > threshold_percent
            
            # Find start and end of consecutive True blocks
            diff = np.diff(exceeds_threshold.astype(int))
            starts = np.where(diff == 1)[0] + 1
            ends = np.where(diff == -1)[0]
            
            # Handle cases where the series starts or ends with an exceedance
            if exceeds_threshold[0]:
                starts = np.insert(starts, 0, 0)
            if exceeds_threshold[-1]:
                ends = np.append(ends, len(data) - 1)
                
            red_segments = []
            for start, end in zip(starts, ends):
                if end > start:
                    red_segments.append({
                        'start_index': int(start),
                        'end_index': int(end),
                        'values': data[start:end+1].tolist(),
                        'deviation_percent': np.max(deviation_percent[start:end+1])
                    })
            return red_segments
            
        except ImportError:
            logger.warning("Pandas not found, falling back to slower red segment calculation.")
            # Fallback to the original slower method
            return self._calculate_red_segments_slow(data, settings)

    def _calculate_red_segments_slow(self, data: np.ndarray, settings: Dict) -> List[Dict[str, Any]]:
        """[DEPRECATED] Original, slower implementation for calculating red segments."""
        window_size = settings.get('fluctuation_detection', {}).get('sample_window', 20)
        threshold_percent = settings.get('fluctuation_detection', {}).get('threshold_percent', 10.0)
        
        red_segments = []
        current_segment = None
        
        for i in range(window_size, len(data)):
            window_data = data[i-window_size:i]
            window_mean = np.mean(window_data)
            current_value = data[i]
            
            if window_mean != 0:
                deviation_percent = abs((current_value - window_mean) / window_mean) * 100
                if deviation_percent > threshold_percent:
                    if current_segment is None:
                        current_segment = {'start_index': i, 'end_index': i, 'values': [current_value], 'deviation_percent': deviation_percent}
                    else:
                        current_segment['end_index'] = i
                        current_segment['values'].append(current_value)
                        current_segment['deviation_percent'] = max(current_segment['deviation_percent'], deviation_percent)
                else:
                    if current_segment is not None:
                        red_segments.append(current_segment)
                        current_segment = None
            else:
                if current_segment is not None:
                    red_segments.append(current_segment)
                    current_segment = None
                    
        if current_segment is not None:
            red_segments.append(current_segment)
            
        return red_segments

class GraphRenderer:
    """Handles different graph rendering modes for filtered data."""
    
    def __init__(self, signal_processor, graph_signal_mapping, parent_widget=None):
        self.signal_processor = signal_processor
        self.graph_signal_mapping = graph_signal_mapping
        self.parent_widget = parent_widget  # Reference to TimeGraphWidget
        self.deviation_threads = {} # Store active threads
        self.deviation_workers = {} # Store active workers
        self.limit_lines = {}  # Store limit line references for removal
        self.limits_config = {}  # Store limits configuration
        self.deviation_lines = {}  # Store deviation visualization references
        self.basic_deviation_settings = {}  # Store basic deviation settings per graph
        self._is_destroyed = False
        
        # TODO: Gelecekte performans optimizasyonu için cache eklenecek
        # self._violation_cache = {}  # Violation hesaplamalarını cache'ler
        # self._limits_cache = {}  # Limit konfigürasyonlarını cache'ler
    
    def set_static_limits(self, graph_index: int, limits: Dict[str, Any]):
        """Store static limits for a specific graph."""
        if not self.limits_config:
            self.limits_config = {}
        self.limits_config[graph_index] = limits
        logger.info(f"Updated static limits for graph {graph_index}: {limits}")

    def __del__(self):
        """Destructor - ensure all threads are cleaned up."""
        if not self._is_destroyed:
            logger.warning("GraphRenderer being destroyed without proper cleanup!")
            self.cleanup()
    
    def cleanup(self):
        """Cleanup all resources and threads."""
        if self._is_destroyed:
            return
        self._is_destroyed = True
        logger.info("GraphRenderer cleanup started")
        self.clear_all_deviation_lines()
        logger.info("GraphRenderer cleanup completed")
    
    def apply_segmented_filter(self, container, graph_index: int, time_segments: List[Tuple[float, float]]):
        """Apply segmented display filter - show matching segments with gaps."""
        logger.info(f"[SEGMENTED DEBUG] Starting segmented filter application")
        logger.info(f"[SEGMENTED DEBUG] Graph index: {graph_index}")
        logger.info(f"[SEGMENTED DEBUG] Time segments: {len(time_segments)} segments")
        
        # Get active tab and visible signals
        active_tab_index = 0  # This should be passed from parent
        visible_signals = self._get_visible_signals_for_graph(active_tab_index, graph_index)
        
        # If no visible signals found, try to get all signals for this graph
        if not visible_signals:
            all_signals = self.signal_processor.get_all_signals()
            visible_signals = list(all_signals.keys())
        
        logger.info(f"[SEGMENTED DEBUG] Active tab: {active_tab_index}")
        logger.info(f"[SEGMENTED DEBUG] Visible signals: {visible_signals}")
        
        if not visible_signals:
            logger.warning(f"[SEGMENTED DEBUG] No visible signals for graph {graph_index}")
            return
        
        # Get plot widget and clear it
        plot_widgets = container.plot_manager.get_plot_widgets()
        logger.info(f"[SEGMENTED DEBUG] Available plot widgets: {len(plot_widgets)}")
        
        if graph_index < len(plot_widgets):
            plot_widget = plot_widgets[graph_index]
            logger.info(f"[SEGMENTED DEBUG] Clearing plot widget {graph_index}")
            plot_widget.clear()
        else:
            logger.warning(f"[SEGMENTED DEBUG] Graph index {graph_index} out of range, available plots: {len(plot_widgets)}")
            return
        
        # Get all signals data
        all_signals = self.signal_processor.get_all_signals()
        
        # Process each visible signal
        for signal_name in visible_signals:
            logger.info(f"[SEGMENTED DEBUG] Processing signal: {signal_name}")
            
            if signal_name not in all_signals:
                logger.warning(f"[SEGMENTED DEBUG] Signal {signal_name} not found in all_signals")
                continue
            
            full_x_data = np.array(all_signals[signal_name]['x_data'])
            full_y_data = np.array(all_signals[signal_name]['y_data'])
            
            logger.info(f"[SEGMENTED DEBUG] Signal data length: {len(full_x_data)}")
            
            # Create optimized segmented data with proper NaN handling
            segmented_x = []
            segmented_y = []
            segments_found = 0
            
            # Sort segments by start time to ensure proper ordering
            sorted_segments = sorted(time_segments, key=lambda x: x[0])
            
            for i, (segment_start, segment_end) in enumerate(sorted_segments):
                # Find indices for this segment
                mask = (full_x_data >= segment_start) & (full_x_data <= segment_end)
                segment_indices = np.where(mask)[0]
                
                if len(segment_indices) > 0:
                    # Get segment data
                    segment_x = full_x_data[segment_indices]
                    segment_y = full_y_data[segment_indices]
                    
                    # Add NaN separator before segment (except for first segment)
                    if segments_found > 0:
                        segmented_x.append(np.nan)
                        segmented_y.append(np.nan)
                    
                    # Add segment data
                    segmented_x.extend(segment_x)
                    segmented_y.extend(segment_y)
                    
                    segments_found += 1
            
            # Plot all segments as a single line with NaN breaks
            if segmented_x:
                color = self._get_signal_color(signal_name)
                
                # Convert to numpy arrays for better performance
                x_array = np.array(segmented_x)
                y_array = np.array(segmented_y)
                
                # Use PyQtGraph's PlotDataItem for better control
                from pyqtgraph import PlotDataItem
                plot_item = PlotDataItem(
                    x=x_array,
                    y=y_array,
                    pen=color,
                    name=signal_name,
                    connect='finite',  # Only connect finite values, skip NaN
                    skipFiniteCheck=False  # Ensure NaN handling works properly
                )
                plot_widget.addItem(plot_item)
                
                logger.info(f"[SEGMENTED DEBUG] Signal {signal_name}: plotted {segments_found} segments as optimized PlotDataItem")
            else:
                logger.warning(f"[SEGMENTED DEBUG] No valid segments found for signal {signal_name}")
                    
        logger.info(f"Segmented filter applied successfully to graph {graph_index}")
        
        # Apply limit lines if available
        self._apply_limit_lines(plot_widget, graph_index, visible_signals)
    
    def apply_concatenated_filter(self, container, time_segments: List[Tuple[float, float]]):
        """Apply concatenated display filter - create continuous timeline from filtered segments."""
        logger.info(f"[CONCATENATED DEBUG] Starting concatenated filter application")
        logger.info(f"[CONCATENATED DEBUG] Time segments: {len(time_segments)} segments")
        
        # Get all signals data
        all_signals = self.signal_processor.get_all_signals()
        
        # Create concatenated time and value arrays with continuous timeline
        concatenated_data = {}
        
        for signal_name, signal_data in all_signals.items():
            full_x_data = np.array(signal_data['x_data'])
            full_y_data = np.array(signal_data['y_data'])
            
            concat_x = []
            concat_y = []
            current_time_offset = 0.0
            
            for i, (segment_start, segment_end) in enumerate(time_segments):
                mask = (full_x_data >= segment_start) & (full_x_data <= segment_end)
                segment_x = full_x_data[mask]
                segment_y = full_y_data[mask]
                
                if len(segment_x) > 0:
                    # Create continuous timeline by adjusting time values
                    if i == 0:
                        # First segment starts at 0
                        adjusted_x = segment_x - segment_x[0]
                        current_time_offset = adjusted_x[-1] if len(adjusted_x) > 0 else 0
                    else:
                        # Subsequent segments continue from where previous ended
                        segment_duration = segment_x[-1] - segment_x[0] if len(segment_x) > 1 else 0
                        adjusted_x = np.linspace(current_time_offset, 
                                               current_time_offset + segment_duration, 
                                               len(segment_x))
                        current_time_offset = adjusted_x[-1] if len(adjusted_x) > 0 else current_time_offset
                    
                    concat_x.extend(adjusted_x)
                    concat_y.extend(segment_y)
            
            if concat_x:
                concatenated_data[signal_name] = {
                    'time': np.array(concat_x),
                    'values': np.array(concat_y)
                }
                logger.debug(f"[CONCATENATED DEBUG] Signal '{signal_name}': {len(concat_x)} points, "
                           f"time range: {concat_x[0]:.3f} - {concat_x[-1]:.3f}")
        
        # Update signal processor with concatenated data
        self.signal_processor.set_filtered_data(concatenated_data)
        logger.info(f"[CONCATENATED DEBUG] Updated signal processor with concatenated data")
        
        # NOT: Grafik redraw'ı TimeGraphWidget._redraw_all_signals() tarafından yapılacak
        # container.plot_manager.redraw_all_plots() yeterli değil - sadece repaint yapıyor
        
        logger.info(f"Concatenated filter applied successfully - continuous timeline created")
    
    def clear_filters(self, container, graph_index: int):
        """Clear all filters and restore original data display."""
        logger.info(f"[CLEAR DEBUG] Clearing filters for graph {graph_index}")
        
        try:
            # Restore original data in signal processor (important for concatenated display)
            self.signal_processor.restore_original_data()
            logger.info(f"[CLEAR DEBUG] Restored original data in signal processor")
            
            # Clear all plots and redraw with original data
            container.plot_manager.clear_all_signals()
            
            # Trigger redraw of all graphs with original data
            container.plot_manager.redraw_all_plots()
            
            # Apply limit lines to all plots
            self._apply_limit_lines_to_all_plots(container)
            
            logger.info(f"[CLEAR DEBUG] Successfully cleared filters and restored original data")
                
        except Exception as e:
            logger.error(f"Error clearing filters: {e}")
    
    def _get_visible_signals_for_graph(self, tab_index: int, graph_index: int) -> List[str]:
        """Get visible signals for a specific graph."""
        if tab_index in self.graph_signal_mapping and graph_index in self.graph_signal_mapping[tab_index]:
            return self.graph_signal_mapping[tab_index][graph_index]
        return []
    
    def _get_signal_color(self, signal_name: str) -> str:
        """Get color for a signal."""
        # This should be implemented based on your color scheme
        # For now, return a default color
        colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
        hash_value = hash(signal_name) % len(colors)
        return colors[hash_value]
    
    def _apply_limit_lines(self, plot_widget, graph_index: int, visible_signals: List[str]):
        """Apply warning limit lines to the plot."""
        try:
            # Get limit configuration from parent widget if available
            limits_config = self._get_limits_configuration(graph_index)
            if not limits_config:
                return
            
            # Clear existing limit lines for this plot
            self._clear_limit_lines(plot_widget, graph_index)
            
            # Get plot view range for drawing lines across the full width
            view_box = plot_widget.getViewBox()
            if view_box is None:
                return
                
            # Get current view range
            x_range, _ = view_box.viewRange()
            x_min, x_max = x_range
            
            # Draw limit lines for each signal that has limits and is visible
            for signal_name in visible_signals:
                if signal_name in limits_config:
                    limits = limits_config[signal_name]
                    self._draw_signal_limit_lines(plot_widget, graph_index, signal_name, limits, x_min, x_max)
                    
        except Exception as e:
            logger.error(f"Error applying limit lines: {e}")
    
    def _draw_signal_limit_lines(self, plot_widget, graph_index: int, signal_name: str, limits: Dict[str, float], x_min: float, x_max: float):
        """Draw warning limit lines for a specific signal."""
        try:
            warning_min = limits.get('warning_min', 0.0)
            warning_max = limits.get('warning_max', 0.0)
            
            # Create dashed pen for limit lines - more visible with custom dash pattern
            limit_pen = pg.mkPen(color='#FFA500', width=3, style=pg.QtCore.Qt.CustomDashLine)
            limit_pen.setDashPattern([8, 4])  # 8 pixels dash, 4 pixels gap
            
            # Store limit lines for later removal
            limit_key = f"{graph_index}_{signal_name}"
            if limit_key not in self.limit_lines:
                self.limit_lines[limit_key] = []
            
            # Draw warning min line (always draw if limit is configured)
            min_line = pg.InfiniteLine(pos=warning_min, angle=0, pen=limit_pen, 
                                     label=f'{signal_name} Min Warning: {warning_min:.2f}',
                                     labelOpts={'position': 0.1, 'color': '#FFA500'})
            plot_widget.addItem(min_line)
            self.limit_lines[limit_key].append(min_line)
            
            # Draw warning max line (always draw if limit is configured)
            max_line = pg.InfiniteLine(pos=warning_max, angle=0, pen=limit_pen,
                                     label=f'{signal_name} Max Warning: {warning_max:.2f}',
                                     labelOpts={'position': 0.9, 'color': '#FFA500'})
            plot_widget.addItem(max_line)
            self.limit_lines[limit_key].append(max_line)
                
            # Highlight violations if signal data is available
            self._highlight_limit_violations(plot_widget, graph_index, signal_name, limits)
            
        except Exception as e:
            logger.error(f"Error drawing limit lines for {signal_name}: {e}")
    
    def _highlight_limit_violations(self, plot_widget, graph_index: int, signal_name: str, limits: Dict[str, float]):
        """Highlight areas where signal violates limits with dashed lines."""
        try:
            # Get signal data
            all_signals = self.signal_processor.get_all_signals()
            if signal_name not in all_signals:
                return
                
            signal_data = all_signals[signal_name]
            x_data = np.array(signal_data['x_data'])
            y_data = np.array(signal_data['y_data'])
            
            warning_min = limits.get('warning_min', 0.0)
            warning_max = limits.get('warning_max', 0.0)
            
            # Find violation points
            violations = []
            # Check min violations (always check since 0 is a valid limit)
            violations.extend(np.where(y_data < warning_min)[0])
            # Check max violations (always check since 0 is a valid limit)
            violations.extend(np.where(y_data > warning_max)[0])
                
            if not violations:
                return
                
            # Create violation highlight pen - always red for limit violations
            violation_pen = pg.mkPen(color='#FF0000', width=4, style=pg.QtCore.Qt.CustomDashLine)
            violation_pen.setDashPattern([6, 3])  # 6 pixels dash, 3 pixels gap
            
            # Group consecutive violations into segments
            violation_segments = self._group_consecutive_indices(violations)
            
            limit_key = f"{graph_index}_{signal_name}"
            if limit_key not in self.limit_lines:
                self.limit_lines[limit_key] = []
            
            # Draw violation segments
            for i, segment in enumerate(violation_segments):
                start_idx, end_idx = segment[0], segment[-1]
                if end_idx < len(x_data) and start_idx >= 0:
                    violation_x = x_data[start_idx:end_idx+1]
                    violation_y = y_data[start_idx:end_idx+1]
                    
                    # Create violation line with dashed style
                    # Only show legend name for the first violation segment
                    legend_name = f'{signal_name}_violation' if i == 0 else None
                    violation_line = plot_widget.plot(violation_x, violation_y, pen=violation_pen, 
                                                     name=legend_name)
                    # Make sure the violation line is drawn on top
                    violation_line.setZValue(10)
                    self.limit_lines[limit_key].append(violation_line)
                    
        except Exception as e:
            logger.error(f"Error highlighting violations for {signal_name}: {e}")
    
    def _group_consecutive_indices(self, indices: List[int]) -> List[List[int]]:
        """Group consecutive indices into segments."""
        if not indices:
            return []
            
        indices = sorted(set(indices))
        segments = []
        current_segment = [indices[0]]
        
        for i in range(1, len(indices)):
            if indices[i] == indices[i-1] + 1:
                current_segment.append(indices[i])
            else:
                segments.append(current_segment)
                current_segment = [indices[i]]
                
        segments.append(current_segment)
        return segments
    
    def _clear_limit_lines(self, plot_widget, graph_index: int):
        """Clear existing limit lines for a specific graph."""
        try:
            keys_to_remove = [key for key in self.limit_lines.keys() if key.startswith(f"{graph_index}_")]
            
            for key in keys_to_remove:
                for line_item in self.limit_lines[key]:
                    try:
                        plot_widget.removeItem(line_item)
                    except:
                        pass  # Item might already be removed
                del self.limit_lines[key]
                
        except Exception as e:
            logger.error(f"Error clearing limit lines: {e}")

    def _get_limits_configuration(self, graph_index: int) -> Dict[str, Any]:
        """Get limits configuration for the specified graph from the stored config."""
        return self.limits_config.get(graph_index, {})

    def set_limits_configuration(self, limits_config: Dict[str, Any]):
        """Set the limits configuration for rendering."""
        self.limits_config = limits_config
        logger.info(f"Limits configuration updated: {len(limits_config)} signals with limits")
    
    def clear_all_limit_lines(self):
        """Clear all limit lines from all plots."""
        self.limit_lines.clear()
    
    def _apply_limit_lines_to_all_plots(self, container):
        """Apply limit lines to all plots in concatenated mode."""
        try:
            plot_widgets = container.plot_manager.get_plot_widgets()
            
            for graph_index, plot_widget in enumerate(plot_widgets):
                # Get visible signals for this graph
                visible_signals = self._get_visible_signals_for_graph(0, graph_index)
                if not visible_signals:
                    # Fallback: use all signals
                    all_signals = self.signal_processor.get_all_signals()
                    visible_signals = list(all_signals.keys())
                    
                self._apply_limit_lines(plot_widget, graph_index, visible_signals)
                
        except Exception as e:
            logger.error(f"Error applying limit lines to all plots: {e}")
            
    def set_basic_deviation_settings(self, tab_index: int, graph_index: int, deviation_settings: Dict[str, Any]):
        """Set basic deviation analysis settings for a specific graph."""
        # Önce mevcut ayarları kontrol et - gereksiz yeniden hesaplama yapma
        current_settings = self.basic_deviation_settings.get(graph_index, {})
        if current_settings == deviation_settings:
            logger.info(f"[DEVIATION_PERFORMANCE] Settings unchanged for graph {graph_index}, skipping update")
            return
            
        self.basic_deviation_settings[graph_index] = deviation_settings
        logger.info(f"[DEVIATION DEBUG] Stored basic deviation settings for graph {graph_index}: {deviation_settings}")
        logger.info(f"[DEVIATION DEBUG] Selected parameters: {deviation_settings.get('selected_parameters', [])}")
        logger.info(f"[DEVIATION DEBUG] Trend enabled: {deviation_settings.get('trend_analysis', {}).get('enabled', False)}")
        logger.info(f"[DEVIATION DEBUG] Fluctuation enabled: {deviation_settings.get('fluctuation_detection', {}).get('enabled', False)}")

        # Apply deviation analysis to the graph - sadece değişiklik varsa
        self._apply_basic_deviation_to_graph(tab_index, graph_index, deviation_settings)

    def _apply_basic_deviation_to_graph(self, tab_index: int, graph_index: int, deviation_settings: Dict[str, Any]):
        """Apply basic deviation analysis visualization to a specific graph."""
        logger.info(f"[DEVIATION DEBUG] Starting deviation application for graph {graph_index} on tab {tab_index}")
        logger.info(f"[DEVIATION DEBUG] Settings: {deviation_settings}")

        try:
            if not self.parent_widget:
                logger.warning("No parent widget available for deviation visualization")
                return
                
            # Get plot widgets from the active container
            active_container = self.parent_widget.get_active_graph_container()
            if not active_container:
                logger.warning("No active graph container available")
                return
                
            plot_widgets = active_container.get_plot_widgets()
            if graph_index >= len(plot_widgets):
                logger.warning(f"Graph index {graph_index} out of range")
                return
                
            plot_widget = plot_widgets[graph_index]

            # Clear existing deviation visualizations for this graph
            self._clear_deviation_lines(graph_index)

            # Get all available signals data
            all_signals_data = self.signal_processor.get_all_signals()
            
            # Determine which signals to process
            selected_parameters = deviation_settings.get('selected_parameters', [])
            
            signals_to_process = []
            if selected_parameters:
                logger.info(f"[DEVIATION DEBUG] Applying to selected parameters: {selected_parameters}")
                signals_to_process = selected_parameters
            else:
                logger.info(f"[DEVIATION DEBUG] No parameters selected, applying to all visible signals on graph.")
                visible_signals = self._get_visible_signals_for_graph(tab_index, graph_index)
                if visible_signals:
                    signals_to_process = visible_signals
                else:
                    # Fallback if no signals are visible for some reason
                    logger.warning(f"No visible signals found for graph {graph_index}, falling back to all signals.")
                    signals_to_process = list(all_signals_data.keys())

            logger.info(f"[DEVIATION DEBUG] Signals to process: {signals_to_process}")

            # Apply deviation analysis to each signal
            for signal_name in signals_to_process:
                if signal_name in all_signals_data:
                    signal_data = all_signals_data[signal_name]
                    x_data = np.array(signal_data['x_data'])
                    y_data = np.array(signal_data['y_data'])

                    # --- Threaded Calculation ---
                    thread = QThread(self.parent_widget)  # Set parent for proper cleanup
                    worker = DeviationCalculator(y_data, deviation_settings)
                    worker.moveToThread(thread)

                    # Connect signals and slots
                    thread.started.connect(worker.run)
                    
                    # Create a proper callback without circular reference
                    def create_callback(signal_name, x_data, y_data, graph_index, plot_widget, thread):
                        return lambda results: self.on_deviation_calculation_finished(
                            signal_name, x_data, y_data, results, graph_index, plot_widget, thread
                        )
                    
                    worker.result_ready.connect(create_callback(signal_name, x_data, y_data, graph_index, plot_widget, thread))
                    
                    # Cleanup connections
                    worker.result_ready.connect(thread.quit)
                    worker.result_ready.connect(worker.deleteLater)
                    thread.finished.connect(thread.deleteLater)
                    
                    # Store both thread and worker for cleanup
                    thread_key = f"{graph_index}_{signal_name}"
                    self.deviation_threads[thread_key] = thread
                    self.deviation_workers[thread_key] = worker
                    
                    # Start the thread
                    thread.start()
                    
                else:
                    logger.warning(f"[DEVIATION DEBUG] Signal '{signal_name}' not found in available data.")

        except Exception as e:
            logger.error(f"Error applying basic deviation to graph {graph_index}: {e}", exc_info=True)
            
    def on_deviation_calculation_finished(self, signal_name, x_data, y_data, deviation_results, graph_index, plot_widget, thread):
        """Handle the results from the deviation calculator thread."""
        logger.info(f"[DEVIATION DEBUG] Calculation finished for {signal_name}. Visualizing results.")
        
        # Remove the thread and worker from the tracking dictionaries
        thread_key = f"{graph_index}_{signal_name}"
        if thread_key in self.deviation_threads:
            del self.deviation_threads[thread_key]
        if thread_key in self.deviation_workers:
            del self.deviation_workers[thread_key]

        self._visualize_deviation_results(plot_widget, graph_index, signal_name,
                                          x_data, y_data, deviation_results, 
                                          self.basic_deviation_settings.get(graph_index, {}))

    def _visualize_deviation_results(self, plot_widget, graph_index: int, signal_name: str, 
                                   x_data: np.ndarray, y_data: np.ndarray, 
                                   deviation_results: Dict[str, Any], settings: Dict[str, Any]):
        """Visualize deviation analysis results on the plot."""
        try:
            # Initialize deviation lines storage for this graph if needed
            if graph_index not in self.deviation_lines:
                self.deviation_lines[graph_index] = {}
                
            # Trend Line - Make it more visible
            if deviation_results['trend_line'] and settings.get('trend_analysis', {}).get('enabled', False):
                trend_line = plot_widget.plot(x_data, deviation_results['trend_line'], 
                                            pen=pg.mkPen(color='#FFD700', width=4, style=pg.QtCore.Qt.DashLine),
                                            name=f"{signal_name} Trend Line")
                self.deviation_lines[graph_index][f"{signal_name}_trend"] = trend_line
                logger.debug(f"Added trend line for {signal_name} with {len(deviation_results['trend_line'])} points")
                
            # Deviation Bands
            if deviation_results['bands'] and settings.get('visual_settings', {}).get('show_bands', False):
                upper_band = deviation_results['bands']['upper']
                lower_band = deviation_results['bands']['lower']
                
                if len(upper_band) == len(x_data) and len(lower_band) == len(x_data):
                    transparency = settings.get('visual_settings', {}).get('band_transparency', 30)
                    alpha = int(255 * (transparency / 100))
                    
                    # Upper band - Make more visible
                    upper_line = plot_widget.plot(x_data, upper_band, 
                                                pen=pg.mkPen(color='orange', width=2, style=pg.QtCore.Qt.DotLine),
                                                name=f"{signal_name} Upper Band")
                    self.deviation_lines[graph_index][f"{signal_name}_upper"] = upper_line
                    
                    # Lower band - Make more visible
                    lower_line = plot_widget.plot(x_data, lower_band, 
                                                pen=pg.mkPen(color='orange', width=2, style=pg.QtCore.Qt.DotLine),
                                                name=f"{signal_name} Lower Band")
                    self.deviation_lines[graph_index][f"{signal_name}_lower"] = lower_line
                    
                    logger.debug(f"Added deviation bands for {signal_name}")
                    
            # Alert Points
            if (deviation_results['alerts'] and 
                settings.get('fluctuation_detection', {}).get('highlight_on_graph', False)):
                
                alert_x = []
                alert_y = []
                
                for alert in deviation_results['alerts']:
                    if alert['index'] < len(x_data):
                        alert_x.append(x_data[alert['index']])
                        alert_y.append(alert['value'])
                        
                if alert_x and alert_y:
                    alert_scatter = plot_widget.plot(alert_x, alert_y, 
                                                   pen=None, 
                                                   symbol='o', 
                                                   symbolBrush=pg.mkBrush(color='red'),
                                                   symbolSize=12,
                                                   name=f"{signal_name} Alerts")
                    self.deviation_lines[graph_index][f"{signal_name}_alerts"] = alert_scatter
                    logger.debug(f"Added {len(alert_x)} alert points for {signal_name}")
                    
            # Red Segments for threshold exceedance
            if (deviation_results['red_segments'] and 
                settings.get('fluctuation_detection', {}).get('red_highlighting', False)):
                
                red_segments = deviation_results['red_segments']
                logger.info(f"Adding {len(red_segments)} red segments for {signal_name}")
                
                for i, segment in enumerate(red_segments):
                    start_idx = segment['start_index']
                    end_idx = segment['end_index']
                    
                    if start_idx < len(x_data) and end_idx < len(x_data):
                        # Extract segment data
                        segment_x = x_data[start_idx:end_idx+1]
                        segment_y = y_data[start_idx:end_idx+1]
                        
                        if len(segment_x) > 0 and len(segment_y) > 0:
                            # Create red line for this segment - Make it very visible
                            # Only show legend for the first segment to avoid clutter
                            legend_name = f"{signal_name} Threshold Exceedance" if i == 0 else None
                            red_line = plot_widget.plot(segment_x, segment_y, 
                                                       pen=pg.mkPen(color='#FF0000', width=5),
                                                       name=legend_name)
                            self.deviation_lines[graph_index][f"{signal_name}_red_segment_{i}"] = red_line
                            logger.debug(f"Added red segment {i+1} for {signal_name} from index {start_idx} to {end_idx}")
                    
        except Exception as e:
            logger.error(f"Error visualizing deviation results for {signal_name}: {e}")
            
    def _clear_deviation_lines(self, graph_index: int):
        """Clear deviation visualization lines for a specific graph."""
        if graph_index in self.deviation_lines:
            lines_to_remove = list(self.deviation_lines[graph_index].values())
            logger.info(f"[DEVIATION_PERFORMANCE] Clearing {len(lines_to_remove)} deviation lines for graph {graph_index}")
            
            # Batch remove items to avoid continuous removeItem calls
            for line in lines_to_remove:
                try:
                    if hasattr(line, 'scene') and line.scene():
                        scene = line.scene()
                        if scene:
                            scene.removeItem(line)
                except Exception as e:
                    logger.debug(f"[DEVIATION_PERFORMANCE] Error removing line: {e}")
                    
            # Clear the dictionary once
            self.deviation_lines[graph_index].clear()
            logger.info(f"[DEVIATION_PERFORMANCE] Cleared deviation lines for graph {graph_index}")
            
    def clear_all_deviation_lines(self):
        """Clear all deviation lines from all graphs."""
        # Stop any running threads before clearing lines
        for thread_key, thread in list(self.deviation_threads.items()):
            if thread.isRunning():
                logger.info(f"Stopping deviation thread: {thread_key}")
                
                # Try to stop the worker gracefully first
                if thread_key in self.deviation_workers:
                    try:
                        worker = self.deviation_workers[thread_key]
                        worker.stop()
                        logger.debug(f"Stopped worker for thread {thread_key}")
                    except Exception as e:
                        logger.debug(f"Could not stop worker gracefully: {e}")
                
                thread.quit()
                if not thread.wait(3000):  # Wait up to 3 seconds
                    logger.warning(f"Deviation thread {thread_key} did not finish, terminating...")
                    thread.terminate()
                    thread.wait(1000)  # Wait for termination
                else:
                    logger.info(f"Deviation thread {thread_key} stopped successfully")
        self.deviation_threads.clear()
        self.deviation_workers.clear()

        for graph_index in list(self.deviation_lines.keys()):
            self._clear_deviation_lines(graph_index)
        self.deviation_lines.clear()
        self.clear_all_limit_lines()
