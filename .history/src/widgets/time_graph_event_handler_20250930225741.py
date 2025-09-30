# type: ignore
"""
TimeGraph Event Handler Module

Bu modül TimeGraphWidget'ın tüm event handler metodlarını yönetir.
Ana sınıftan event handling kodlarını ayırarak daha yönetilebilir hale getirir.
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .time_graph_widget_v2 import TimeGraphWidget

logger = logging.getLogger(__name__)


class TimeGraphEventHandler:
    """TimeGraphWidget için event handler işlemlerini yöneten sınıf."""
    
    def __init__(self, widget: 'TimeGraphWidget'):
        self.widget = widget
        
    # Graph ve Tab Event Handlers
    def on_graph_count_changed(self, count: int):
        """Graph sayısı değişikliğini işle."""
        active_container = self.widget.get_active_graph_container()
        if active_container:
            active_container.set_graph_count(count)
            # Gecikmeli başlatma
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self._delayed_post_graph_change)
            # Graph ayarları panelini yeniden oluştur
            self.widget.graph_settings_panel_manager.rebuild_controls(count)
    
    def _delayed_post_graph_change(self):
        """Graph sayısı değişikliği sonrası gecikmeli işlemler."""
        active_container = self.widget.get_active_graph_container()
        if not active_container:
            return
        count = active_container.plot_manager.get_subplot_count()
        
        # Mevcut cursor modunu sakla
        current_mode = getattr(self.widget, 'current_cursor_mode', 'dual')
        
        # Cursor manager'ı yeniden başlat
        self.widget._initialize_cursor_manager()
        
        # Cursor modunu geri yükle
        self.widget.current_cursor_mode = current_mode
        if self.widget.cursor_manager:
            self.widget.cursor_manager.set_cursor_mode(current_mode)
        
        # İstatistik panelini güncelle
        if hasattr(self.widget, 'statistics_panel'):
            self.widget.statistics_panel.update_graph_count(count)
            self.widget.statistics_panel.set_cursor_mode(current_mode)
        
        logger.debug(f"Post-graph-change setup completed for {count} graphs")
    
    def on_tab_changed(self, index: int):
        """Tab değişikliğini işle."""
        # Tab değişikliği işlemleri burada
        pass
    
    # Processing Event Handlers
    def on_processing_finished(self, all_signals: Dict):
        """Sinyal işleme tamamlandığında çağrılır."""
        self.widget.loading_manager.finish_operation("processing")
        
        try:
            # Aktif container'ı al
            active_container = self.widget.get_active_graph_container()
            if not active_container:
                logger.error("No active graph container found during processing completion")
                return
            
            active_tab_index = self.widget.tab_widget.currentIndex()
            
            # Aktif container'a sinyalleri gönder
            active_container = self.widget.get_active_graph_container()
            if active_container and hasattr(active_container, 'plot_manager'):
                plot_manager = active_container.plot_manager
                if hasattr(plot_manager, 'render_signals'):
                    plot_manager.render_signals(all_signals)
                elif hasattr(plot_manager, 'update_plots'):
                    plot_manager.update_plots(all_signals)
                else:
                    logger.warning("PlotManager doesn't have render_signals or update_plots method")
            
            # Statistics panel'i yeniden oluştur
            self._recreate_statistics_panel()
            
            # İstatistikleri güncelle
            self._update_statistics_from_signals(all_signals)
            
            # Cursor manager'ı yeniden başlat (veri yüklendikten sonra)
            self.widget._initialize_cursor_manager()
            
            # Mevcut cursor modunu uygula
            if hasattr(self.widget, 'current_cursor_mode') and self.widget.cursor_manager:
                self.widget.cursor_manager.set_mode(self.widget.current_cursor_mode)
            
            # Veri değişikliği sinyali gönder
            self.widget.data_changed.emit(all_signals)
            
            logger.info(f"Successfully processed {len(all_signals)} signals")
            
        except Exception as e:
            logger.error(f"Error in processing completion: {e}", exc_info=True)
    
    def on_processing_error(self, error_msg: str):
        """İşleme hatası durumunda çağrılır."""
        self.widget.loading_manager.finish_operation("processing")
        logger.error(f"Processing error: {error_msg}")
    
    # Graph Settings Event Handlers
    def on_graph_settings_requested(self, graph_index: int):
        """Graph ayarları dialog'unu aç."""
        active_tab_index = self.widget.tab_widget.currentIndex()
        
        try:
            from src.ui.graph_advanced_settings_dialog import GraphAdvancedSettingsDialog
            
            # Mevcut ayarları al
            current_settings = self.widget._get_graph_setting(graph_index, {})
            
            dialog = GraphAdvancedSettingsDialog(
                graph_index=graph_index,
                current_settings=current_settings,
                parent=self.widget
            )
            
            if dialog.exec_() == dialog.Accepted:
                settings = dialog.get_settings()
                self._apply_graph_settings(graph_index, settings)
                
        except Exception as e:
            logger.error(f"Error opening graph settings dialog: {e}")
    
    def on_basic_deviation_applied(self, graph_index: int, deviation_settings: Dict[str, Any]):
        """Temel sapma ayarlarını uygula."""
        active_tab_index = self.widget.tab_widget.currentIndex()
        logger.info(f"Applying basic deviation settings to graph {graph_index} on tab {active_tab_index}: {deviation_settings}")

        try:
            if hasattr(self.widget, 'graph_renderer') and self.widget.graph_renderer:
                self.widget.graph_renderer.set_basic_deviation_settings(active_tab_index, graph_index, deviation_settings)
                logger.info(f"Basic deviation settings applied successfully to graph {graph_index}")
            else:
                logger.warning("Graph renderer not available for basic deviation application")

        except Exception as e:
            logger.error(f"Error applying basic deviation settings to graph {graph_index}: {e}", exc_info=True)
    
    # Plot Event Handlers
    def on_plot_clicked(self, plot_index: int, x: float, y: float):
        """Plot tıklamasını işle."""
        self.widget.current_cursor_position = x
        self.widget._update_legend_values()
        self.widget.cursor_moved.emit("click", (x, y))
    
    def on_range_selected(self, start: float, end: float):
        """Aralık seçimini işle."""
        self.widget.selected_range = (start, end)
        self.widget._update_statistics_for_range(start, end)
        self.widget.range_selected.emit((start, end))
    
    # Signal Event Handlers
    def on_signal_visibility_changed(self, signal_name: str, visible: bool):
        """Sinyal görünürlük değişikliğini işle."""
        pass  # Gereksinime göre implement edilecek
    
    def on_signal_selected(self, signal_name: str):
        """Sinyal seçimini işle."""
        pass
    
    def on_signal_color_changed(self, signal_name: str, new_color: str):
        """Sinyal renk değişikliğini işle."""
        logger.info(f"Color change requested for signal '{signal_name}' to {new_color}")
        
        try:
            active_container = self.widget.get_active_graph_container()
            if active_container and hasattr(active_container, 'plot_manager'):
                active_container.plot_manager.update_signal_color(signal_name, new_color)
                logger.info(f"Signal color updated successfully for '{signal_name}'")
            else:
                logger.warning("No active container or plot manager available for color update")
                
        except Exception as e:
            logger.error(f"Error updating signal color for '{signal_name}': {e}")
    
    # Theme Event Handlers
    def on_theme_changed(self, theme_name: str):
        """Tema değişikliğini işle."""
        self.widget._apply_theme()
    
    # Cursor Event Handlers
    def on_cursor_mode_changed(self, mode: str):
        """Cursor modu değişikliğini işle."""
        logger.info(f"Cursor mode change requested: {mode}")
        
        self.widget.current_cursor_mode = mode
        
        # Cursor manager'ı güncelle
        if self.widget.cursor_manager:
            self.widget.cursor_manager.set_mode(mode)
        
        # İstatistik panelini güncelle
        if hasattr(self.widget, 'statistics_panel'):
            self.widget.statistics_panel.set_cursor_mode(mode)
        
        logger.debug(f"Cursor mode changed to: {mode}")
    
    def on_cursor_moved(self, cursor_positions: Dict[str, float]):
        """Cursor hareketi ve gerçek zamanlı istatistik güncellemesi."""
        logger.debug(f"Cursor moved: {cursor_positions}")
        
        # İstatistik panelini güncelle
        if hasattr(self.widget, 'statistics_panel'):
            self.widget.statistics_panel.update_cursor_positions(cursor_positions)
        
        # Cursor pozisyonlarını sakla
        self.widget.current_cursor_position = cursor_positions.get('c1')
        
        # Sinyal gönder
        self.widget.cursor_moved.emit("cursor", cursor_positions)
    
    # Panel Toggle Event Handlers
    def on_panel_toggled(self):
        """İstatistik paneli görünürlük toggle."""
        if hasattr(self.widget, 'channel_stats_panel'):
            self.widget.channel_stats_panel.setVisible(not self.widget.channel_stats_panel.isVisible())
    
    def on_settings_toggled(self):
        """Ayarlar paneli toggle."""
        try:
            if hasattr(self.widget, 'settings_panel'):
                self.widget._toggle_left_panel(self.widget.settings_panel)
        except Exception as e:
            logger.error(f"Error toggling settings panel: {e}")
    
    def on_graph_settings_toggled(self):
        """Graph ayarları paneli toggle."""
        try:
            if hasattr(self.widget, 'graph_settings_panel'):
                self.widget._toggle_left_panel(self.widget.graph_settings_panel)
        except Exception as e:
            logger.error(f"Error toggling graph settings panel: {e}")
    
    def on_statistics_settings_toggled(self):
        """İstatistik ayarları paneli toggle."""
        try:
            if hasattr(self.widget, 'statistics_settings_panel'):
                self.widget._toggle_left_panel(self.widget.statistics_settings_panel)
        except Exception as e:
            logger.error(f"Error toggling statistics settings panel: {e}")
    
    def on_correlations_toggled(self):
        """Korelasyon paneli toggle."""
        try:
            if hasattr(self.widget, 'correlations_panel'):
                self.widget._toggle_left_panel(self.widget.correlations_panel)
        except Exception as e:
            logger.error(f"Error toggling correlations panel: {e}")
    
    def on_bitmask_toggled(self):
        """Bitmask paneli toggle."""
        try:
            if hasattr(self.widget, 'bitmask_panel'):
                self.widget._toggle_left_panel(self.widget.bitmask_panel)
        except Exception as e:
            logger.error(f"Error toggling bitmask panel: {e}")
    
    # Settings Event Handlers
    def on_visible_columns_changed(self, visible_columns: set):
        """Görünür sütun değişikliklerini işle."""
        self.widget.visible_stats_columns = visible_columns
        if hasattr(self.widget, 'statistics_panel'):
            self.widget.statistics_panel.set_visible_stats(visible_columns)
    
    def on_duty_cycle_threshold_changed(self, threshold_mode: str, threshold_value: float):
        """Duty cycle threshold değişikliklerini işle."""
        self.widget.duty_cycle_threshold_mode = threshold_mode
        self.widget.duty_cycle_threshold_value = threshold_value
        
        # Aktif sinyalleri yeniden işle
        if hasattr(self.widget, 'data_manager') and self.widget.data_manager.has_data():
            self.widget._reprocess_current_data()
    
    # Helper Methods
    def _update_statistics_from_signals(self, all_signals: Dict):
        """Sinyallerden istatistikleri güncelle."""
        try:
            if not hasattr(self.widget, 'statistics_panel') or not self.widget.statistics_panel:
                return
            
            # Her sinyal için istatistikleri hesapla ve güncelle
            for signal_name, signal_data in all_signals.items():
                if 'y_data' in signal_data and len(signal_data['y_data']) > 0:
                    stats = self.widget._calculate_signal_statistics(signal_data['y_data'])
                    self.widget.statistics_panel.update_statistics(signal_name, stats)
                    
        except Exception as e:
            logger.error(f"Error updating statistics from signals: {e}")
    
    def _apply_graph_settings(self, graph_index: int, settings: Dict[str, Any]):
        """Graph ayarlarını uygula."""
        try:
            # Ayarları sakla
            self.widget._save_graph_setting(graph_index, 'advanced_settings', settings)
            
            # Aktif container'a uygula
            active_container = self.widget.get_active_graph_container()
            if active_container:
                active_container.apply_graph_settings(graph_index, settings)
                
            logger.info(f"Graph settings applied successfully to graph {graph_index}")
            
        except Exception as e:
            logger.error(f"Error applying graph settings to graph {graph_index}: {e}")
    
    def on_signal_color_changed(self, signal_name: str, color: str):
        """Sinyal rengi değişikliğini işle."""
        try:
            # Aktif container'daki plot manager'a renk değişikliğini bildir
            active_container = self.widget.get_active_graph_container()
            if active_container and hasattr(active_container, 'plot_manager'):
                plot_manager = active_container.plot_manager
                if hasattr(plot_manager, 'update_signal_color'):
                    plot_manager.update_signal_color(signal_name, color)
                    logger.debug(f"Signal color updated: {signal_name} -> {color}")
                
        except Exception as e:
            logger.error(f"Error updating signal color: {e}")
    
    def on_cursor_moved(self, position):
        """Cursor hareket ettiğinde çağrılır."""
        try:
            if hasattr(self.widget, 'statistics_panel') and self.widget.statistics_panel:
                # Statistics panel'e cursor pozisyonunu bildir
                if hasattr(self.widget.statistics_panel, 'update_cursor_position'):
                    self.widget.statistics_panel.update_cursor_position(position)
                    
        except Exception as e:
            logger.error(f"Error handling cursor movement: {e}")
    
    def on_graph_settings_requested(self, graph_index: int):
        """Graph ayarları istendiğinde çağrılır."""
        try:
            if hasattr(self.widget, 'graph_settings_panel_manager'):
                # Graph settings panel'i aç/kapat
                self.widget.graph_settings_panel_manager.toggle_panel()
                
        except Exception as e:
            logger.error(f"Error handling graph settings request: {e}")
    
    def on_theme_changed(self, theme_name: str):
        """Tema değişikliğini işle."""
        try:
            logger.info(f"Theme change requested: {theme_name}")
            
            # Aktif container'a tema uygula
            active_container = self.widget.get_active_graph_container()
            if active_container and hasattr(active_container, 'apply_theme'):
                active_container.apply_theme()
                logger.debug("Theme applied to active container")
            
            # Tüm container'lara tema uygula
            for container in self.widget.graph_containers:
                if container and hasattr(container, 'apply_theme'):
                    container.apply_theme()
            
            # Statistics panel'e tema uygula
            if hasattr(self.widget, 'statistics_panel') and self.widget.statistics_panel:
                theme_colors = self.widget.theme_manager.get_theme_colors()
                if hasattr(self.widget.statistics_panel, 'update_theme'):
                    self.widget.statistics_panel.update_theme(theme_colors)
            
            # Tab widget styling'i güncelle
            if hasattr(self.widget, '_apply_tab_stylesheet'):
                self.widget._apply_tab_stylesheet()
            
            logger.info(f"Theme change completed: {theme_name}")
            
        except Exception as e:
            logger.error(f"Error handling theme change: {e}")
    
    def _recreate_statistics_panel(self):
        """Statistics panel'i yeniden oluştur."""
        try:
            if not hasattr(self.widget, 'statistics_panel') or not self.widget.statistics_panel:
                return
            
            # Aktif tab ve container'ı al
            active_tab_index = self.widget.tab_widget.currentIndex()
            active_container = self.widget.get_active_graph_container()
            
            if not active_container:
                return
            
            # Graph sayısını al
            num_graphs = active_container.plot_manager.get_subplot_count()
            
            # Graph section'larını oluştur
            if num_graphs > 0:
                for graph_idx in range(num_graphs):
                    self.widget.statistics_panel.ensure_graph_sections(graph_idx)
            
            # Sinyalleri statistics panel'e ekle
            all_signals = self.widget.signal_processor.get_all_signals()
            
            for graph_idx in range(num_graphs):
                for signal_name in all_signals.keys():
                    # Sinyal rengini al
                    color = active_container.plot_manager.get_signal_color(graph_idx, signal_name)
                    if not color:
                        # Fallback renk
                        signal_index = list(all_signals.keys()).index(signal_name)
                        color = self.widget.theme_manager.get_signal_color(signal_index)
                    
                    # Sinyali statistics panel'e ekle
                    full_signal_name = f"{signal_name} (G{graph_idx+1})"
                    self.widget.statistics_panel.add_signal(full_signal_name, graph_idx, signal_name, color)
            
            logger.debug(f"Statistics panel recreated with {len(all_signals)} signals")
            
        except Exception as e:
            logger.error(f"Error recreating statistics panel: {e}")
