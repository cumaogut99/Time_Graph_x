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
            logger.info(f"[LIMITS DEBUG] Applying limit lines to graph {graph_index}")
            logger.info(f"[LIMITS DEBUG] Visible signals: {visible_signals}")
            
            # Get limit configuration from parent widget if available
            limits_config = self._get_limits_configuration(graph_index)
            logger.info(f"[LIMITS DEBUG] Limits config: {limits_config}")
            
            if not limits_config:
                logger.info(f"[LIMITS DEBUG] No limits config found for graph {graph_index}")
                return
            
            # Clear existing limit lines for this plot
            self._clear_limit_lines(plot_widget, graph_index)
            logger.info(f"[LIMITS DEBUG] Cleared existing limit lines for graph {graph_index}")
            
            # Get plot view range for drawing lines across the full width
            view_box = plot_widget.getViewBox()
            if view_box is None:
                logger.warning(f"[LIMITS DEBUG] No view box found for plot widget")
                return
                
            # Get current view range
            x_range, _ = view_box.viewRange()
            x_min, x_max = x_range
            logger.info(f"[LIMITS DEBUG] Plot view range: x_min={x_min}, x_max={x_max}")
            
            # Draw limit lines for each signal that has limits
            # Check both visible signals and all signals with limits
            signals_to_check = set(visible_signals) | set(limits_config.keys())
            logger.info(f"[LIMITS DEBUG] Signals to check for limits: {signals_to_check}")
            
            for signal_name in signals_to_check:
                if signal_name in limits_config:
                    limits = limits_config[signal_name]
                    logger.info(f"[LIMITS DEBUG] Found limits for signal {signal_name}: {limits}")
                    
                    # Check if signal has data (exists in signal processor)
                    all_signals = self.signal_processor.get_all_signals()
                    if signal_name in all_signals:
                        logger.info(f"[LIMITS DEBUG] Signal {signal_name} has data, drawing limit lines")
                        self._draw_signal_limit_lines(plot_widget, graph_index, signal_name, limits, x_min, x_max)
                    else:
                        logger.warning(f"[LIMITS DEBUG] Signal {signal_name} has limits but no data available")
                else:
                    logger.info(f"[LIMITS DEBUG] No limits found for signal {signal_name}")
                    
        except Exception as e:
            logger.error(f"Error applying limit lines: {e}")
    
    def _draw_signal_limit_lines(self, plot_widget, graph_index: int, signal_name: str, limits: Dict[str, float], x_min: float, x_max: float):
        """Draw warning limit lines for a specific signal."""
        try:
            logger.info(f"[LIMITS DEBUG] Drawing limit lines for signal {signal_name}")
            warning_min = limits.get('warning_min', 0.0)
            warning_max = limits.get('warning_max', 0.0)
            logger.info(f"[LIMITS DEBUG] Warning limits: min={warning_min}, max={warning_max}")
            
            # Create dashed pen for limit lines
            limit_pen = pg.mkPen(color='#FFA500', width=2, style=pg.QtCore.Qt.DashLine)
            logger.info(f"[LIMITS DEBUG] Created limit pen: color=#FFA500, width=2, dashed")
            
            # Store limit lines for later removal
            limit_key = f"{graph_index}_{signal_name}"
            if limit_key not in self.limit_lines:
                self.limit_lines[limit_key] = []
            logger.info(f"[LIMITS DEBUG] Using limit key: {limit_key}")
            
            # Draw warning min line if not zero
            if warning_min != 0.0:
                logger.info(f"[LIMITS DEBUG] Drawing min warning line at {warning_min}")
                min_line = pg.InfiniteLine(pos=warning_min, angle=0, pen=limit_pen, 
                                         label=f'{signal_name} Min Warning: {warning_min:.2f}',
                                         labelOpts={'position': 0.1, 'color': '#FFA500'})
                plot_widget.addItem(min_line)
                self.limit_lines[limit_key].append(min_line)
                logger.info(f"[LIMITS DEBUG] Added min warning line to plot")
                
            # Draw warning max line if not zero
            if warning_max != 0.0:
                logger.info(f"[LIMITS DEBUG] Drawing max warning line at {warning_max}")
                max_line = pg.InfiniteLine(pos=warning_max, angle=0, pen=limit_pen,
                                         label=f'{signal_name} Max Warning: {warning_max:.2f}',
                                         labelOpts={'position': 0.9, 'color': '#FFA500'})
                plot_widget.addItem(max_line)
                self.limit_lines[limit_key].append(max_line)
                logger.info(f"[LIMITS DEBUG] Added max warning line to plot")
                
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
            if warning_min != 0.0:
                violations.extend(np.where(y_data < warning_min)[0])
            if warning_max != 0.0:
                violations.extend(np.where(y_data > warning_max)[0])
                
            if not violations:
                return
                
            # Create violation highlight pen - use same color as signal but dashed
            signal_color = self._get_signal_color(signal_name)
            violation_pen = pg.mkPen(color=signal_color, width=3, style=pg.QtCore.Qt.DashLine)
            
            # Group consecutive violations into segments
            violation_segments = self._group_consecutive_indices(violations)
            
            limit_key = f"{graph_index}_{signal_name}"
            if limit_key not in self.limit_lines:
                self.limit_lines[limit_key] = []
            
            # Draw violation segments
            for segment in violation_segments:
                start_idx, end_idx = segment[0], segment[-1]
                if end_idx < len(x_data) and start_idx >= 0:
                    violation_x = x_data[start_idx:end_idx+1]
                    violation_y = y_data[start_idx:end_idx+1]
                    
                    # Create violation line with dashed style
                    violation_line = plot_widget.plot(violation_x, violation_y, pen=violation_pen, 
                                                     name=f'{signal_name}_violation')
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
