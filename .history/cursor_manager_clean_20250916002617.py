# Sadece zoom fonksiyonlarını ekleyeceğim
def zoom_to_cursors(self):
    """Zoom to the range between dual cursors."""
    if self.current_mode != "dual" or not self.dual_cursors_1 or not self.dual_cursors_2:
        logger.warning("Zoom to cursors requires dual cursor mode with both cursors active")
        return False
        
    try:
        # Get cursor positions
        pos1 = self.dual_cursors_1[0].value()
        pos2 = self.dual_cursors_2[0].value()
        
        # Ensure proper order (min, max)
        start_pos = min(pos1, pos2)
        end_pos = max(pos1, pos2)
        
        # Add small margin (5% on each side)
        range_width = end_pos - start_pos
        margin = range_width * 0.05
        zoom_start = start_pos - margin
        zoom_end = end_pos + margin
        
        logger.info(f"Zooming to cursor range: {zoom_start:.3f} to {zoom_end:.3f}")
        
        # Apply zoom to all plot widgets
        for plot_widget in self.plot_widgets:
            plot_widget.setXRange(zoom_start, zoom_end, padding=0)
            plot_widget.enableAutoRange(axis='y')  # Keep Y auto-scaled
            
        return True
        
    except Exception as e:
        logger.error(f"Error zooming to cursors: {e}")
        return False
        
def can_zoom_to_cursors(self) -> bool:
    """Check if zoom to cursors is possible."""
    return (self.current_mode == "dual" and 
            self.dual_cursors_1 and 
            self.dual_cursors_2 and
            len(self.dual_cursors_1) > 0 and 
            len(self.dual_cursors_2) > 0)
