"""
Filter Manager - Range filter logic and calculations
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class FilterManager:
    """Manages range filter calculations and operations."""
    
    def __init__(self):
        self.active_filters = {}
        self.filter_applied = False
    
    def calculate_filter_segments(self, all_signals: dict, conditions: list) -> list:
        """Calculate time segments that satisfy all filter conditions."""
        logger.info(f"[FILTER DEBUG] Calculating segments for {len(conditions)} conditions")
        
        if not conditions or not all_signals:
            return []
        
        # Start with all time points
        time_data = None
        for signal_name, signal_data in all_signals.items():
            if 'x_data' in signal_data and len(signal_data['x_data']) > 0:
                time_data = np.array(signal_data['x_data'])
                break
        
        if time_data is None:
            logger.warning("[FILTER DEBUG] No time data found")
            return []
        
        # Create a boolean mask for all time points
        combined_mask = np.ones(len(time_data), dtype=bool)
        
        # Apply each condition
        for condition in conditions:
            param_name = condition['parameter']
            ranges = condition['ranges']
            
            if param_name not in all_signals:
                logger.warning(f"[FILTER DEBUG] Parameter {param_name} not found in signals")
                continue
            
            param_data = np.array(all_signals[param_name]['y_data'])
            condition_mask = np.zeros(len(param_data), dtype=bool)
            
            # Apply all ranges for this parameter (OR logic within parameter)
            for range_filter in ranges:
                range_type = range_filter['type']
                operator = range_filter['operator']
                value = range_filter['value']
                
                if range_type == 'lower':
                    if operator == '>=':
                        range_mask = param_data >= value
                    elif operator == '>':
                        range_mask = param_data > value
                    else:
                        continue
                elif range_type == 'upper':
                    if operator == '<=':
                        range_mask = param_data <= value
                    elif operator == '<':
                        range_mask = param_data < value
                    else:
                        continue
                else:
                    continue
                
                condition_mask |= range_mask
            
            # Combine with overall mask (AND logic between parameters)
            combined_mask &= condition_mask
        
        # Find continuous segments
        segments = self._find_continuous_segments(time_data, combined_mask)
        logger.info(f"[FILTER DEBUG] Found {len(segments)} segments")
        
        return segments
    
    def _find_continuous_segments(self, time_data: np.ndarray, mask: np.ndarray) -> List[Tuple[float, float]]:
        """Find continuous time segments where mask is True."""
        if not np.any(mask):
            return []
        
        # Find indices where mask is True
        true_indices = np.where(mask)[0]
        
        if len(true_indices) == 0:
            return []
        
        segments = []
        start_idx = true_indices[0]
        
        for i in range(1, len(true_indices)):
            # If there's a gap, end current segment and start new one
            if true_indices[i] - true_indices[i-1] > 1:
                end_idx = true_indices[i-1]
                segments.append((float(time_data[start_idx]), float(time_data[end_idx])))
                start_idx = true_indices[i]
        
        # Add the last segment
        end_idx = true_indices[-1]
        segments.append((float(time_data[start_idx]), float(time_data[end_idx])))
        
        return segments
    
    def clear_filters(self):
        """Clear all active filters."""
        logger.info("[FILTER DEBUG] Clearing all active filters")
        self.active_filters.clear()
        self.filter_applied = False
    
    def save_filter_state(self, tab_index: int, filter_data: dict):
        """Save filter state for a specific tab."""
        self.active_filters[tab_index] = filter_data.copy()
        self.filter_applied = True
        logger.info(f"[FILTER DEBUG] Saved filter state for tab {tab_index}")
    
    def get_active_filters(self) -> dict:
        """Get all active filters."""
        return self.active_filters.copy()
    
    def has_active_filters(self) -> bool:
        """Check if there are any active filters."""
        return self.filter_applied and bool(self.active_filters)
    
    def remove_filter(self, tab_index: int):
        """Remove filter for a specific tab."""
        if tab_index in self.active_filters:
            del self.active_filters[tab_index]
            if not self.active_filters:
                self.filter_applied = False
            logger.info(f"[FILTER DEBUG] Removed filter for tab {tab_index}")
