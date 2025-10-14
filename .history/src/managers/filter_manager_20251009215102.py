"""
Filter Manager - Range filter logic and calculations
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread

logger = logging.getLogger(__name__)


class FilterCalculationWorker(QObject):
    """Worker for calculating filter segments in background thread."""
    
    finished = Signal(list)  # Emits calculated segments
    error = Signal(str)
    progress = Signal(int)  # Progress percentage
    
    def __init__(self, all_signals: dict, conditions: list):
        super().__init__()
        # Deep copy to avoid data race conditions
        self.all_signals = {k: {'x_data': v['x_data'], 'y_data': v['y_data']} 
                           for k, v in all_signals.items()}
        self.conditions = [c.copy() for c in conditions]
        self.should_stop = False
        self._is_running = False
    
    def run(self):
        """Calculate filter segments."""
        try:
            self._is_running = True
            
            if self.should_stop:
                return
                
            segments = self._calculate_segments()
            
            if not self.should_stop:
                self.finished.emit(segments)
        except Exception as e:
            logger.error(f"Error in filter calculation: {e}")
            if not self.should_stop:
                self.error.emit(str(e))
        finally:
            self._is_running = False
    
    def stop(self):
        """Stop the calculation."""
        self.should_stop = True
        logger.debug("Worker stop requested")
    
    def is_running(self) -> bool:
        """Check if worker is currently running."""
        return self._is_running
    
    def _calculate_segments(self) -> list:
        """Calculate time segments that satisfy all filter conditions."""
        logger.info(f"[FILTER DEBUG] Calculating segments for {len(self.conditions)} conditions")
        
        if not self.conditions or not self.all_signals:
            return []
        
        # Get time data from first available signal
        time_data = None
        for signal_data in self.all_signals.values():
            if 'x_data' in signal_data and len(signal_data['x_data']) > 0:
                time_data = np.array(signal_data['x_data'])
                break
        
        if time_data is None:
            return []
        
        # Create a boolean mask for all time points
        combined_mask = np.ones(len(time_data), dtype=bool)
        
        # Apply each condition with progress reporting
        total_conditions = len(self.conditions)
        for idx, condition in enumerate(self.conditions):
            if self.should_stop:
                return []
            
            # Report progress
            progress = int((idx / total_conditions) * 100)
            self.progress.emit(progress)
                
            param_name = condition['parameter']
            ranges = condition['ranges']
            
            if param_name not in self.all_signals:
                logger.warning(f"[FILTER DEBUG] Parameter {param_name} not found in signals")
                continue
            
            # Use view instead of copy for better performance
            param_data = np.asarray(self.all_signals[param_name]['y_data'])
            condition_mask = np.zeros(len(param_data), dtype=bool)
            
            # Apply all ranges for this parameter (OR logic within parameter)
            for range_filter in ranges:
                if self.should_stop:
                    return []
                    
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
            if self.should_stop:
                return segments
                
            # Check if there's a gap
            if true_indices[i] - true_indices[i-1] > 1:
                # End current segment
                end_idx = true_indices[i-1]
                segments.append((time_data[start_idx], time_data[end_idx]))
                start_idx = true_indices[i]
        
        # Add the last segment
        segments.append((time_data[start_idx], time_data[true_indices[-1]]))
        
        return segments


class FilterManager:
    """Manages range filter calculations and operations."""
    
    def __init__(self, parent_widget=None):
        self.active_filters = {}
        self.filter_applied = False
        self.parent_widget = parent_widget
        self.calculation_thread = None
        self.calculation_worker = None
        self._cleanup_in_progress = False
        self._pending_callback = None
    
    def calculate_filter_segments_threaded(self, all_signals: dict, conditions: list, callback=None):
        """Calculate time segments that satisfy all filter conditions in background thread."""
        logger.info(f"[FILTER DEBUG] Starting threaded calculation for {len(conditions)} conditions")
        
        if not conditions or not all_signals:
            if callback:
                callback([])
            return
        
        # Stop any existing calculation
        self._stop_calculation()
        
        # Create new thread and worker with proper parent
        self.calculation_thread = QThread()
        self.calculation_worker = FilterCalculationWorker(all_signals, conditions)
        self.calculation_worker.moveToThread(self.calculation_thread)
        
        # Store callback reference
        self._pending_callback = callback
        
        # Connect signals with proper order and error handling
        self.calculation_thread.started.connect(self.calculation_worker.run)
        
        # Use a safe callback wrapper
        if callback:
            self.calculation_worker.finished.connect(
                lambda segments: self._safe_callback_execution(callback, segments)
            )
        
        self.calculation_worker.error.connect(self._on_calculation_error)
        
        # Cleanup connections - Critical: Must disconnect before deleteLater
        def safe_cleanup():
            try:
                # Disconnect all signals before deletion
                if self.calculation_worker:
                    self.calculation_worker.finished.disconnect()
                    self.calculation_worker.error.disconnect()
                    self.calculation_worker.progress.disconnect()
                if self.calculation_thread:
                    self.calculation_thread.started.disconnect()
            except (RuntimeError, TypeError) as e:
                logger.debug(f"Signal already disconnected: {e}")
        
        self.calculation_worker.finished.connect(safe_cleanup)
        self.calculation_worker.finished.connect(self.calculation_thread.quit)
        self.calculation_worker.finished.connect(self.calculation_worker.deleteLater)
        self.calculation_thread.finished.connect(self.calculation_thread.deleteLater)
        
        # Reset references after cleanup
        self.calculation_thread.finished.connect(self._reset_thread_references)
        
        # Start the thread
        self.calculation_thread.start()
        logger.info("[FILTER DEBUG] Started filter calculation thread")
    
    def _safe_callback_execution(self, callback, segments):
        """Safely execute callback with error handling."""
        try:
            if not self._cleanup_in_progress and callback:
                callback(segments)
        except RuntimeError as e:
            logger.warning(f"Callback execution failed (object may be deleted): {e}")
        except Exception as e:
            logger.error(f"Error in filter callback: {e}")
    
    def _reset_thread_references(self):
        """Reset thread references after cleanup."""
        try:
            # Only reset if not currently cleaning up
            if not self._cleanup_in_progress:
                self.calculation_thread = None
                self.calculation_worker = None
                self._pending_callback = None
                logger.debug("Thread references reset")
        except Exception as e:
            logger.debug(f"Error resetting thread references: {e}")
    
    def _stop_calculation(self):
        """Stop any running calculation."""
        try:
            if self.calculation_worker:
                self.calculation_worker.stop()
                
            if self.calculation_thread:
                try:
                    # Check if thread object is still valid
                    if self.calculation_thread.isRunning():
                        logger.info("Stopping running filter calculation thread...")
                        self.calculation_thread.quit()
                        
                        # Wait for thread to finish
                        if not self.calculation_thread.wait(3000):
                            logger.warning("Filter calculation thread did not finish, terminating...")
                            self.calculation_thread.terminate()
                            self.calculation_thread.wait(1000)
                        
                        logger.info("Filter calculation thread stopped")
                except RuntimeError as e:
                    # Thread nesnesi zaten silinmiş, sorun değil
                    logger.debug(f"Thread already deleted during stop: {e}")
        except Exception as e:
            logger.debug(f"Error stopping calculation (may already be stopped): {e}")
    
    def _on_calculation_error(self, error_msg: str):
        """Handle calculation error."""
        logger.error(f"Filter calculation error: {error_msg}")
    
    def cleanup(self):
        """Cleanup filter manager resources."""
        try:
            logger.debug("FilterManager cleanup started")
            self._cleanup_in_progress = True
            
            # Stop any running calculation
            self._stop_calculation()
            
            # Reset references
            self._reset_thread_references()
            
            logger.debug("FilterManager cleanup completed")
        except Exception as e:
            logger.error(f"Error during FilterManager cleanup: {e}")
        finally:
            self._cleanup_in_progress = False
    
    def calculate_filter_segments(self, all_signals: dict, conditions: list) -> list:
        
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
    
    def get_filter_state(self, tab_index: int) -> dict:
        """Get filter state for a specific tab."""
        return self.active_filters.get(tab_index, {})
    
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
    
    def cleanup(self):
        """Cleanup resources and stop any running calculations."""
        logger.info("FilterManager cleanup started")
        self._cleanup_in_progress = True
        
        try:
            # Clear callback reference first
            self._pending_callback = None
            
            # Stop calculation
            self._stop_calculation()
            
            # Wait a bit for cleanup to complete
            import time
            time.sleep(0.1)
            
            # Clear all references
            self.calculation_thread = None
            self.calculation_worker = None
            self.active_filters.clear()
            
        except Exception as e:
            logger.error(f"Error during FilterManager cleanup: {e}")
        finally:
            self._cleanup_in_progress = False
            logger.info("FilterManager cleanup completed")
