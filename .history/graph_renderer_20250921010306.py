"""
Graph Renderer - Handles segmented and concatenated graph rendering
"""

import logging
import numpy as np
import pyqtgraph as pg
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class GraphRenderer:
    """Handles different graph rendering modes for filtered data."""
    
    def __init__(self, signal_processor, graph_signal_mapping, parent_widget=None):
        self.signal_processor = signal_processor
        self.graph_signal_mapping = graph_signal_mapping
        self.parent_widget = parent_widget  # Reference to TimeGraphWidget
        self.limit_lines = {}  # Store limit line references for removal
        self.limits_config = {}  # Store limits configuration
        self.deviation_lines = {}  # Store deviation visualization references
        self.basic_deviation_settings = {}  # Store basic deviation settings per graph
    
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
            
            # Create segmented data
            segments_plotted = 0
            for i, (segment_start, segment_end) in enumerate(time_segments):
                # Find indices for this segment
                mask = (full_x_data >= segment_start) & (full_x_data <= segment_end)
                segment_x = full_x_data[mask]
                segment_y = full_y_data[mask]
                
                if len(segment_x) > 0:
                    # Plot this segment
                    color = self._get_signal_color(signal_name)
                    # Only show legend for the first segment of each signal
                    legend_name = signal_name if segments_plotted == 0 else None
                    plot_widget.plot(segment_x, segment_y, pen=color, name=legend_name)
                    segments_plotted += 1
                    
            logger.info(f"[SEGMENTED DEBUG] Signal {signal_name}: plotted {segments_plotted} segments")
                    
        logger.info(f"Segmented filter applied successfully to graph {graph_index}")
        
        # Apply limit lines if available
        self._apply_limit_lines(plot_widget, graph_index, visible_signals)
    
    def apply_concatenated_filter(self, container, time_segments: List[Tuple[float, float]]):
        """Apply concatenated display filter - apply global time filter to all graphs."""
        logger.info(f"[CONCATENATED DEBUG] Starting concatenated filter application")
        logger.info(f"[CONCATENATED DEBUG] Time segments: {len(time_segments)} segments")
        
        # Get all signals data
        all_signals = self.signal_processor.get_all_signals()
        
        # Create concatenated time and value arrays
        concatenated_data = {}
        
        for signal_name, signal_data in all_signals.items():
            full_x_data = np.array(signal_data['x_data'])
            full_y_data = np.array(signal_data['y_data'])
            
            concat_x = []
            concat_y = []
            
            for segment_start, segment_end in time_segments:
                mask = (full_x_data >= segment_start) & (full_x_data <= segment_end)
                segment_x = full_x_data[mask]
                segment_y = full_y_data[mask]
                
                if len(segment_x) > 0:
                    concat_x.extend(segment_x)
                    concat_y.extend(segment_y)
            
            if concat_x:
                concatenated_data[signal_name] = {
                    'time': np.array(concat_x),
                    'values': np.array(concat_y)
                }
        
        # Update signal processor with concatenated data
        self.signal_processor.set_filtered_data(concatenated_data)
        
        # Trigger redraw of all graphs
        container.plot_manager.redraw_all_plots()
        
        # Apply limit lines to all plots
        self._apply_limit_lines_to_all_plots(container)
        
        logger.info(f"Concatenated filter applied successfully")
    
    def clear_filters(self, container, graph_index: int):
        """Clear all filters and restore original data display."""
        logger.info(f"[CLEAR DEBUG] Clearing filters for graph {graph_index}")
        
        try:
            # Get plot widgets
            plot_widgets = container.plot_manager.get_plot_widgets()
            
            if graph_index < len(plot_widgets):
                plot_widget = plot_widgets[graph_index]
                
                # Clear the specific plot
                plot_widget.clear()
                logger.info(f"[CLEAR DEBUG] Cleared plot widget {graph_index}")
                
                # Get original signal data and redraw
                all_signals = self.signal_processor.get_all_signals()
                
                # Find visible signals for this graph
                visible_signals = []
                for tab_index, tab_mapping in self.graph_signal_mapping.items():
                    if graph_index in tab_mapping:
                        visible_signals = tab_mapping[graph_index]
                        break
                
                if not visible_signals:
                    # Fallback: use all signals
                    visible_signals = list(all_signals.keys())
                
                logger.info(f"[CLEAR DEBUG] Restoring {len(visible_signals)} signals")
                
                # Redraw original signals
                for signal_name in visible_signals:
                    if signal_name in all_signals:
                        signal_data = all_signals[signal_name]
                        color = self._get_signal_color(signal_name)
                        
                        plot_widget.plot(
                            signal_data['x_data'], 
                            signal_data['y_data'], 
                            pen=color, 
                            name=signal_name
                        )
                
                # Apply limit lines after restoring data
                self._apply_limit_lines(plot_widget, graph_index, visible_signals)
                
                logger.info(f"[CLEAR DEBUG] Successfully restored original data for graph {graph_index}")
            else:
                logger.warning(f"[CLEAR DEBUG] Graph index {graph_index} out of range")
                
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
        """Get limits configuration for the specified graph."""
        # Try to get limits from parent widget first
        if self.parent_widget and hasattr(self.parent_widget, '_get_graph_setting'):
            try:
                limits_config = self.parent_widget._get_graph_setting(graph_index, 'limits', {})
                logger.debug(f"Retrieved limits config for graph {graph_index}: {limits_config}")
                return limits_config
            except Exception as e:
                logger.error(f"Error getting limits from parent widget: {e}")
        
        # Fallback to stored limits configuration
        return getattr(self, 'limits_config', {})
    
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
            
    def set_basic_deviation_settings(self, graph_index: int, deviation_settings: Dict[str, Any]):
        """Set basic deviation analysis settings for a specific graph."""
        self.basic_deviation_settings[graph_index] = deviation_settings
        logger.info(f"Basic deviation settings updated for graph {graph_index}: {deviation_settings}")
        
        # Apply deviation analysis to the graph
        self._apply_basic_deviation_to_graph(graph_index, deviation_settings)
        
    def _apply_basic_deviation_to_graph(self, graph_index: int, deviation_settings: Dict[str, Any]):
        """Apply basic deviation analysis visualization to a specific graph."""
        try:
            if not self.parent_widget:
                logger.warning("No parent widget available for deviation visualization")
                return
                
            # Get plot widgets from parent
            plot_widgets = self.parent_widget.plot_manager.get_plot_widgets()
            if graph_index >= len(plot_widgets):
                logger.warning(f"Graph index {graph_index} out of range")
                return
                
            plot_widget = plot_widgets[graph_index]
            
            # Clear existing deviation visualizations for this graph
            self._clear_deviation_lines(graph_index)
            
            # Get visible signals for this graph
            visible_signals = self._get_visible_signals_for_graph(0, graph_index)
            if not visible_signals:
                all_signals = self.signal_processor.get_all_signals()
                visible_signals = list(all_signals.keys())
                
            # Apply deviation analysis to each visible signal
            all_signals_data = self.signal_processor.get_all_signals()
            
            # Check if specific parameters are selected
            selected_parameters = deviation_settings.get('selected_parameters', [])
            
            if selected_parameters:
                # Apply only to selected parameters
                for selected_parameter in selected_parameters:
                    if selected_parameter in all_signals_data:
                        signal_data = all_signals_data[selected_parameter]
                        x_data = np.array(signal_data['x_data'])
                        y_data = np.array(signal_data['y_data'])
                        
                        # Calculate deviation analysis
                        deviation_results = self._calculate_basic_deviation(y_data, deviation_settings)
                        
                        # Visualize results
                        self._visualize_deviation_results(plot_widget, graph_index, selected_parameter, 
                                                        x_data, y_data, deviation_results, deviation_settings)
            else:
                # Apply to all visible signals if no specific selection
                for signal_name in visible_signals:
                    if signal_name not in all_signals_data:
                        continue
                        
                    signal_data = all_signals_data[signal_name]
                    x_data = np.array(signal_data['x_data'])
                    y_data = np.array(signal_data['y_data'])
                    
                    # Calculate deviation analysis
                    deviation_results = self._calculate_basic_deviation(y_data, deviation_settings)
                    
                    # Visualize results
                    self._visualize_deviation_results(plot_widget, graph_index, signal_name, 
                                                    x_data, y_data, deviation_results, deviation_settings)
                
        except Exception as e:
            logger.error(f"Error applying basic deviation to graph {graph_index}: {e}")
            
    def _calculate_basic_deviation(self, signal_data: np.ndarray, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic deviation analysis for signal data."""
        if len(signal_data) == 0:
            return {'deviations': [], 'bands': [], 'alerts': [], 'trend_line': []}
            
        results = {
            'deviations': [],
            'bands': [],
            'alerts': [],
            'trend_line': [],
            'red_segments': []  # For red highlighting of threshold exceedance
        }
        
        # Trend Analysis
        if settings.get('trend_analysis', {}).get('enabled', False):
            sensitivity = settings['trend_analysis'].get('sensitivity', 3)
            trend_line = self._calculate_trend_line(signal_data, sensitivity)
            results['trend_line'] = trend_line
            
        # Fluctuation Detection
        if settings.get('fluctuation_detection', {}).get('enabled', False):
            window_size = settings['fluctuation_detection'].get('sample_window', 20)
            threshold_percent = settings['fluctuation_detection'].get('threshold_percent', 10.0)
            
            deviations, alerts = self._detect_fluctuations(signal_data, window_size, threshold_percent)
            results['deviations'] = deviations
            results['alerts'] = alerts
            
        # Deviation Bands
        if settings.get('visual_settings', {}).get('show_bands', False):
            bands = self._calculate_deviation_bands(signal_data, settings)
            results['bands'] = bands
            
        # Red Segments for threshold exceedance
        if settings.get('fluctuation_detection', {}).get('red_highlighting', False):
            red_segments = self._calculate_red_segments(signal_data, settings)
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
            
        window_size = settings.get('fluctuation_detection', {}).get('sample_window', 20)
        threshold_percent = settings.get('fluctuation_detection', {}).get('threshold_percent', 10.0)
        
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
        
    def _calculate_red_segments(self, data: np.ndarray, settings: Dict) -> List[Dict[str, Any]]:
        """Calculate red segments where signal exceeds threshold."""
        if len(data) < 10:
            return []
            
        window_size = settings.get('fluctuation_detection', {}).get('sample_window', 20)
        threshold_percent = settings.get('fluctuation_detection', {}).get('threshold_percent', 10.0)
        
        red_segments = []
        current_segment = None
        
        for i in range(window_size, len(data)):
            # Get last window_size samples
            window_data = data[i-window_size:i]
            window_mean = np.mean(window_data)
            current_value = data[i]
            
            # Calculate percentage deviation
            if window_mean != 0:
                deviation_percent = abs((current_value - window_mean) / window_mean) * 100
                
                # Check if it exceeds threshold
                if deviation_percent > threshold_percent:
                    if current_segment is None:
                        # Start new segment
                        current_segment = {
                            'start_index': i,
                            'end_index': i,
                            'values': [current_value],
                            'deviation_percent': deviation_percent
                        }
                    else:
                        # Continue current segment
                        current_segment['end_index'] = i
                        current_segment['values'].append(current_value)
                        current_segment['deviation_percent'] = max(current_segment['deviation_percent'], deviation_percent)
                else:
                    # End current segment if exists
                    if current_segment is not None:
                        red_segments.append(current_segment)
                        current_segment = None
            else:
                # End current segment if exists
                if current_segment is not None:
                    red_segments.append(current_segment)
                    current_segment = None
                    
        # Don't forget the last segment
        if current_segment is not None:
            red_segments.append(current_segment)
            
        return red_segments
        
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
                logger.info(f"Added trend line for {signal_name} with {len(deviation_results['trend_line'])} points")
                
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
                    
                    logger.info(f"Added deviation bands for {signal_name}")
                    
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
                                                   symbolSize=8,
                                                   name=f"{signal_name} Alerts")
                    self.deviation_lines[graph_index][f"{signal_name}_alerts"] = alert_scatter
                    
            # Red Segments for threshold exceedance
            if (deviation_results['red_segments'] and 
                settings.get('fluctuation_detection', {}).get('red_highlighting', False)):
                
                for i, segment in enumerate(deviation_results['red_segments']):
                    start_idx = segment['start_index']
                    end_idx = segment['end_index']
                    
                    if start_idx < len(x_data) and end_idx < len(x_data):
                        # Extract segment data
                        segment_x = x_data[start_idx:end_idx+1]
                        segment_y = y_data[start_idx:end_idx+1]
                        
                        if len(segment_x) > 0 and len(segment_y) > 0:
                            # Create red line for this segment
                            red_line = plot_widget.plot(segment_x, segment_y, 
                                                       pen=pg.mkPen(color='red', width=3),
                                                       name=f"{signal_name} Threshold Exceedance {i+1}")
                            self.deviation_lines[graph_index][f"{signal_name}_red_segment_{i}"] = red_line
                    
        except Exception as e:
            logger.error(f"Error visualizing deviation results for {signal_name}: {e}")
            
    def _clear_deviation_lines(self, graph_index: int):
        """Clear deviation visualization lines for a specific graph."""
        if graph_index in self.deviation_lines:
            for line in self.deviation_lines[graph_index].values():
                try:
                    if hasattr(line, 'scene') and line.scene():
                        line.scene().removeItem(line)
                except:
                    pass
            self.deviation_lines[graph_index].clear()
            
    def clear_all_deviation_lines(self):
        """Clear all deviation lines from all graphs."""
        for graph_index in list(self.deviation_lines.keys()):
            self._clear_deviation_lines(graph_index)
        self.deviation_lines.clear()
