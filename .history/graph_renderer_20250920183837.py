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
    
    def __init__(self, signal_processor, graph_signal_mapping):
        self.signal_processor = signal_processor
        self.graph_signal_mapping = graph_signal_mapping
        self.limit_lines = {}  # Store limit line references for removal
    
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
