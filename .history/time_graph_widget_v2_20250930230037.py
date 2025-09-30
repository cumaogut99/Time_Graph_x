# type: ignore
"""
Refactored TimeGraph Widget V2 - Ana Koordinasyon Sınıfı

Bu sınıf sadece koordinasyon yapar, ağır işlemler ayrı modüllerde yapılır.
QThread desteği ile performans optimizasyonu sağlanır.

2653 satırlık orijinal dosya şimdi ~730 satıra düşürüldü!
"""

import logging
from typing import Dict, Any, Optional
import numpy as np
from PyQt5.QtWidgets import QWidget, QMessageBox, QInputDialog
from PyQt5.QtCore import pyqtSignal as Signal

# Refactor edilmiş modüller
from src.widgets.time_graph_ui_setup import TimeGraphUISetup
from src.widgets.time_graph_event_handler import TimeGraphEventHandler
from src.widgets.time_graph_data_handler import TimeGraphDataHandler

# Mevcut manager'lar
from src.managers.filter_manager import FilterManager
from src.graphics.graph_renderer import GraphRenderer
from src.managers.toolbar_manager import ToolbarManager
from src.managers.legend_manager import LegendManager
from src.data.signal_processor import SignalProcessor
from src.managers.theme_manager import ThemeManager
from src.managers.cursor_manager import CursorManager
from src.ui.statistics_panel import StatisticsPanel
from src.managers.data_manager import TimeSeriesDataManager
from src.managers.settings_panel_manager import SettingsPanelManager
from src.managers.statistics_settings_panel_manager import StatisticsSettingsPanelManager
from src.managers.graph_settings_panel_manager import GraphSettingsPanelManager
from src.managers.bitmask_panel_manager import BitmaskPanelManager
from src.graphics.graph_container import GraphContainer
from src.managers.correlations_panel_manager import CorrelationsPanelManager

logger = logging.getLogger(__name__)


class TimeGraphWidget(QWidget):
    """
    Refactored TimeGraph Widget - Performans Odaklı Tasarım
    
    Bu sınıf sadece koordinasyon yapar:
    - UI Setup: TimeGraphUISetup (src/widgets/time_graph_ui_setup.py)
    - Event Handling: TimeGraphEventHandler (src/widgets/time_graph_event_handler.py)
    - Data Processing: TimeGraphDataHandler (src/widgets/time_graph_data_handler.py)
    - Manager koordinasyonu
    
    Performans İyileştirmeleri:
    - QThread ile arka plan veri işleme
    - İstatistik hesaplamalarında throttling ve caching
    - Modüler yapı ile daha kolay bakım
    """
    
    # Sinyaller
    data_changed = Signal(object)
    cursor_moved = Signal(str, object)
    range_selected = Signal(tuple)
    statistics_updated = Signal(dict)
    
    def __init__(self, parent=None, loading_manager=None):
        super().__init__(parent)
        
        # Temel özellikler
        self.graph_containers = []
        self.loading_manager = loading_manager
        
        # Duty cycle ayarları
        self.duty_cycle_threshold_mode = "auto"
        self.duty_cycle_threshold_value = 0.0
        
        # Manager referansları
        self.filter_manager = None
        self.graph_renderer = None
        self.status_bar = None
        self.cursor_manager = None
        
        # Refactored handler'lar
        self.ui_setup = None
        self.event_handler = None
        self.data_handler = None
        
        # State variables
        self.is_normalized = False
        self.current_cursor_position = None
        self.selected_range = None
        self.current_cursor_mode = "dual"
        self._last_graph_count = 1
        
        # Başlatma
        self._initialize_components()
        
        logger.debug("Refactored TimeGraphWidget V2 initialized successfully")
    
    def _initialize_components(self):
        """Tüm bileşenleri başlat."""
        try:
            # 1. Manager'ları başlat
            self._initialize_managers()
            
            # 2. Refactored handler'ları başlat
            self._initialize_handlers()
            
            # 3. UI'ı kur
            self.ui_setup.setup_ui()
            
            # 4. Bağlantıları kur
            self._setup_connections()
            
            # 5. Tema uygula
            self._apply_theme()
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    def _initialize_managers(self):
        """Manager'ları başlat."""
        # Veri yönetimi
        self.data_manager = TimeSeriesDataManager()
        self.signal_processor = SignalProcessor()
        
        # Grafik renderer
        self.graph_renderer = GraphRenderer(self.signal_processor, {}, self)
        
        # Filter manager
        self.filter_manager = FilterManager(self)
        
        # UI Manager'ları
        self.toolbar_manager = ToolbarManager(self)
        self.legend_manager = LegendManager(self)
        self.settings_panel_manager = SettingsPanelManager(self)
        self.statistics_settings_panel_manager = StatisticsSettingsPanelManager(self)
        self.graph_settings_panel_manager = GraphSettingsPanelManager(self)
        self.theme_manager = ThemeManager()
        self.bitmask_panel_manager = BitmaskPanelManager(self.data_manager, self.theme_manager, self)
        
        # İstatistik paneli
        self.statistics_panel = StatisticsPanel()
        self.channel_stats_widgets = {}
        
        # State
        self.visible_stats_columns = self.statistics_settings_panel_manager.get_visible_columns()
        self.graph_signal_mapping = {}
        self.graph_settings = {}
        
        logger.debug("Managers initialized")
    
    def _initialize_handlers(self):
        """Refactored handler'ları başlat."""
        self.ui_setup = TimeGraphUISetup(self)
        self.event_handler = TimeGraphEventHandler(self)
        self.data_handler = TimeGraphDataHandler(self)
        
        logger.debug("Handlers initialized")
    
    def _setup_connections(self):
        """Sinyal-slot bağlantılarını kur."""
        try:
            # Toolbar bağlantıları
            if self.toolbar_manager:
                # File operations (app.py'de handle edilir)
                if hasattr(self.toolbar_manager, 'file_open_requested'):
                    self.toolbar_manager.file_open_requested.connect(
                        lambda: logger.info("File open requested from toolbar")
                    )
                
                if hasattr(self.toolbar_manager, 'file_save_requested'):
                    self.toolbar_manager.file_save_requested.connect(
                        lambda: logger.info("File save requested from toolbar")
                    )
                
                # Graph count
                if hasattr(self.toolbar_manager, 'graph_count_changed'):
                    self.toolbar_manager.graph_count_changed.connect(
                        self.event_handler.on_graph_count_changed
                    )
                
                # Cursor mode
                if hasattr(self.toolbar_manager, 'cursor_mode_changed'):
                    self.toolbar_manager.cursor_mode_changed.connect(
                        self.event_handler.on_cursor_mode_changed
                    )
                
                # Panel toggles
                if hasattr(self.toolbar_manager, 'panel_toggled'):
                    self.toolbar_manager.panel_toggled.connect(
                        self.event_handler.on_panel_toggled
                    )
                
                if hasattr(self.toolbar_manager, 'settings_toggled'):
                    self.toolbar_manager.settings_toggled.connect(
                        self.event_handler.on_settings_toggled
                    )
                
                if hasattr(self.toolbar_manager, 'graph_settings_toggled'):
                    self.toolbar_manager.graph_settings_toggled.connect(
                        self.event_handler.on_graph_settings_toggled
                    )
                
                if hasattr(self.toolbar_manager, 'statistics_settings_toggled'):
                    self.toolbar_manager.statistics_settings_toggled.connect(
                        self.event_handler.on_statistics_settings_toggled
                    )
                
                if hasattr(self.toolbar_manager, 'correlations_toggled'):
                    self.toolbar_manager.correlations_toggled.connect(
                        self.event_handler.on_correlations_toggled
                    )
                
                if hasattr(self.toolbar_manager, 'bitmask_toggled'):
                    self.toolbar_manager.bitmask_toggled.connect(
                        self.event_handler.on_bitmask_toggled
                    )
            
            # Statistics panel bağlantıları
            if self.statistics_panel:
                self.statistics_panel.graph_settings_requested.connect(
                    self.event_handler.on_graph_settings_requested
                )
                self.statistics_panel.signal_color_changed.connect(
                    self.event_handler.on_signal_color_changed
                )
            
            # Theme manager bağlantıları
            if self.theme_manager:
                self.theme_manager.theme_changed.connect(
                    self.event_handler.on_theme_changed
                )
                self.theme_manager.theme_changed.connect(
                    lambda: self.statistics_panel.update_theme(self.theme_manager.get_theme_colors())
                )
            
            # Settings panel bağlantıları
            if self.settings_panel_manager:
                if hasattr(self.settings_panel_manager, 'theme_changed'):
                    self.settings_panel_manager.theme_changed.connect(
                        self.theme_manager.set_theme
                    )
            
            if self.statistics_settings_panel_manager:
                if hasattr(self.statistics_settings_panel_manager, 'visible_columns_changed'):
                    self.statistics_settings_panel_manager.visible_columns_changed.connect(
                        self.event_handler.on_visible_columns_changed
                    )
                
                if hasattr(self.statistics_settings_panel_manager, 'duty_cycle_threshold_changed'):
                    self.statistics_settings_panel_manager.duty_cycle_threshold_changed.connect(
                        self.event_handler.on_duty_cycle_threshold_changed
                    )
            
            logger.debug("Connections established")
            
        except Exception as e:
            logger.error(f"Error setting up connections: {e}")
    
    def _apply_theme(self):
        """Tema uygula."""
        try:
            if self.theme_manager:
                # Tema döngüsünü önlemek için sadece bir kez ayarla
                if not hasattr(self, '_theme_applied'):
                    if hasattr(self.theme_manager, 'set_theme'):
                        self.theme_manager.set_theme("space")
                    else:
                        theme_colors = self.theme_manager.get_theme_colors()
                        if theme_colors:
                            logger.debug("Theme colors applied successfully")
                    
                    self._theme_applied = True
                
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
    
    # ========== PUBLIC API METHODS ==========
    
    def update_data(self, df, time_column: str = None, is_normalized: bool = False):
        """Veri güncelle (QThread ile arka planda işlenir)."""
        try:
            self.data_handler.update_data(df, time_column, is_normalized)
        except Exception as e:
            logger.error(f"Error updating data: {e}")
            QMessageBox.critical(
                self,
                "Veri Güncelleme Hatası",
                f"Veri güncellenirken hata oluştu:\n\n{str(e)}"
            )
    
    def export_data(self) -> Dict[str, Any]:
        """Mevcut veriyi dışa aktar."""
        try:
            return self.data_handler.get_active_signals()
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return {'signals': {}}
    
    def get_layout_config(self) -> Dict[str, Any]:
        """Layout konfigürasyonunu al."""
        try:
            config = {
                'theme': self.theme_manager.current_theme if self.theme_manager else 'space',
                'cursor_mode': self.current_cursor_mode,
                'graph_count': self._last_graph_count,
                'visible_stats': list(self.visible_stats_columns),
                'duty_cycle_settings': {
                    'mode': self.duty_cycle_threshold_mode,
                    'value': self.duty_cycle_threshold_value
                }
            }
            
            if self.graph_settings:
                config['graph_settings'] = self.graph_settings
                
            return config
            
        except Exception as e:
            logger.error(f"Error getting layout config: {e}")
            return {}
    
    def set_layout_config(self, config: Dict[str, Any]):
        """Layout konfigürasyonunu uygula."""
        try:
            if 'theme' in config and self.theme_manager:
                self.theme_manager.apply_theme(config['theme'])
            
            if 'cursor_mode' in config:
                self.current_cursor_mode = config['cursor_mode']
                if self.cursor_manager:
                    self.cursor_manager.set_cursor_mode(config['cursor_mode'])
            
            if 'graph_count' in config:
                self._last_graph_count = config['graph_count']
                if self.toolbar_manager:
                    self.toolbar_manager.set_graph_count(config['graph_count'])
            
            if 'visible_stats' in config:
                self.visible_stats_columns = set(config['visible_stats'])
                if self.statistics_panel:
                    self.statistics_panel.set_visible_stats(self.visible_stats_columns)
            
            if 'duty_cycle_settings' in config:
                duty_settings = config['duty_cycle_settings']
                self.duty_cycle_threshold_mode = duty_settings.get('mode', 'auto')
                self.duty_cycle_threshold_value = duty_settings.get('value', 0.0)
            
            if 'graph_settings' in config:
                self.graph_settings = config['graph_settings']
            
            logger.info("Layout configuration applied successfully")
            
        except Exception as e:
            logger.error(f"Error setting layout config: {e}")
    
    def get_active_graph_container(self) -> Optional[GraphContainer]:
        """Aktif graph container'ı al."""
        try:
            if hasattr(self, 'tab_widget') and self.tab_widget:
                current_index = self.tab_widget.currentIndex()
                if 0 <= current_index < len(self.graph_containers):
                    return self.graph_containers[current_index]
            return None
        except Exception as e:
            logger.error(f"Error getting active graph container: {e}")
            return None
    
    # ========== HELPER METHODS ==========
    
    def _create_correlations_panel(self):
        """Korelasyon paneli oluştur."""
        self.correlations_panel_manager = CorrelationsPanelManager(self)
        return self.correlations_panel_manager.get_panel()
    
    def _create_bitmask_panel(self):
        """Bitmask paneli oluştur."""
        return self.bitmask_panel_manager.get_widget()
    
    def _create_channel_statistics_panel(self):
        """İstatistik paneli oluştur."""
        self.statistics_panel = StatisticsPanel(self)
        self.statistics_panel.setMinimumWidth(300)
        
        # Bağlantıları kur
        self.statistics_panel.graph_settings_requested.connect(
            self.event_handler.on_graph_settings_requested
        )
        self.statistics_panel.signal_color_changed.connect(
            self.event_handler.on_signal_color_changed
        )
        
        return self.statistics_panel
    
    def _delayed_initial_setup(self):
        """Gecikmeli başlangıç kurulumu."""
        logger.debug("Starting delayed initial setup")
        
        self._initialize_cursor_manager()
        self._force_cursor_mode_sync()
        
        # İlk cursor mode ayarı
        initial_mode = "dual"
        if self.toolbar_manager and hasattr(self.toolbar_manager, 'cursor_combo'):
            toolbar_text = self.toolbar_manager.cursor_combo.currentText().lower()
            if "none" in toolbar_text:
                initial_mode = "none"
        
        if self.event_handler:
            self.event_handler.on_cursor_mode_changed(initial_mode)
        
        logger.debug("Delayed initial setup completed")
    
    def _rename_tab(self, index: int):
        """Tab'ı yeniden adlandır."""
        try:
            current_name = self.tab_widget.tabText(index)
            new_name, ok = QInputDialog.getText(
                self, 
                "Tab Adını Değiştir", 
                "Yeni tab adı:", 
                text=current_name
            )
            
            if ok and new_name:
                self.tab_widget.setTabText(index, new_name)
                logger.debug(f"Tab {index} renamed to: {new_name}")
                
        except Exception as e:
            logger.error(f"Error renaming tab: {e}")
    
    def _initialize_cursor_manager(self):
        """Cursor manager'ı başlat."""
        try:
            active_container = self.get_active_graph_container()
            if active_container and hasattr(active_container, 'plot_manager'):
                plot_manager = active_container.plot_manager
                
                if hasattr(plot_manager, 'get_plot_widgets'):
                    plot_widgets = plot_manager.get_plot_widgets()
                    if plot_widgets:
                        self.cursor_manager = CursorManager(plot_widgets)
                        logger.debug(f"Cursor manager initialized with {len(plot_widgets)} plot widgets")
                    else:
                        logger.warning("No plot widgets available for cursor manager")
                        return
                else:
                    logger.warning("PlotManager doesn't have get_plot_widgets method")
                    return
                
                if hasattr(self.cursor_manager, 'cursor_moved'):
                    self.cursor_manager.cursor_moved.connect(
                        self.event_handler.on_cursor_moved
                    )
                
                logger.debug("Cursor manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing cursor manager: {e}")
    
    def _force_cursor_mode_sync(self):
        """Cursor mode senkronizasyonunu zorla."""
        if self.cursor_manager and hasattr(self, 'current_cursor_mode'):
            self.cursor_manager.set_cursor_mode(self.current_cursor_mode)
    
    def _apply_tab_stylesheet(self):
        """Tab stil uygula."""
        try:
            if self.theme_manager:
                theme_colors = self.theme_manager.get_theme_colors()
                
                if theme_colors:
                    is_light_theme = theme_colors.get('text_primary', '#ffffff') == '#212121'
                    
                    if is_light_theme:
                        tab_style = """
                            QTabWidget::pane {
                                border: 1px solid #c0c0c0;
                                background-color: #f0f0f0;
                            }
                            QTabBar::tab {
                                background-color: #e0e0e0;
                                color: #212121;
                                padding: 8px 16px;
                                margin-right: 2px;
                                border-top-left-radius: 4px;
                                border-top-right-radius: 4px;
                            }
                            QTabBar::tab:selected {
                                background-color: #ffffff;
                                color: #212121;
                            }
                            QTabBar::tab:hover {
                                background-color: #d0d0d0;
                            }
                        """
                    else:
                        tab_style = """
                            QTabWidget::pane {
                                border: 1px solid #4a90e2;
                                background-color: #2d4a66;
                            }
                            QTabBar::tab {
                                background-color: #3a5f7a;
                                color: #e6f3ff;
                                padding: 8px 16px;
                                margin-right: 2px;
                                border-top-left-radius: 4px;
                                border-top-right-radius: 4px;
                            }
                            QTabBar::tab:selected {
                                background-color: #4a90e2;
                                color: #ffffff;
                            }
                            QTabBar::tab:hover {
                                background-color: #5a7f9a;
                            }
                        """
                    
                    if hasattr(self, 'tab_widget') and self.tab_widget:
                        self.tab_widget.setStyleSheet(tab_style)
                        
        except Exception as e:
            logger.error(f"Error applying tab stylesheet: {e}")
    
    def _on_tab_changed(self, index: int):
        """Tab değişikliği işle."""
        try:
            if self.event_handler:
                self.event_handler.on_tab_changed(index)
            logger.debug(f"Tab changed to: {index}")
        except Exception as e:
            logger.error(f"Error handling tab change: {e}")
    
    def _add_tab(self):
        """Yeni tab ekle."""
        try:
            container = GraphContainer(self)
            self.graph_containers.append(container)
            
            tab_index = self.tab_widget.addTab(container, f"Graph {len(self.graph_containers)}")
            self.tab_widget.setCurrentIndex(tab_index)
            
            logger.debug(f"Added new tab: {tab_index}")
        except Exception as e:
            logger.error(f"Error adding tab: {e}")
    
    def _remove_tab(self, index: int = None):
        """Tab kaldır."""
        try:
            if index is None:
                index = self.tab_widget.currentIndex()
            
            if 0 <= index < len(self.graph_containers):
                container = self.graph_containers.pop(index)
                container.cleanup()
                self.tab_widget.removeTab(index)
                logger.debug(f"Removed tab: {index}")
        except Exception as e:
            logger.error(f"Error removing tab: {e}")
    
    def _toggle_left_panel(self, panel):
        """Sol paneli toggle et."""
        try:
            if hasattr(self, 'left_panel_stack'):
                if self.left_panel_stack.isVisible() and self.left_panel_stack.currentWidget() == panel:
                    self.left_panel_stack.setVisible(False)
                else:
                    self.left_panel_stack.setCurrentWidget(panel)
                    self.left_panel_stack.setVisible(True)
        except Exception as e:
            logger.error(f"Error toggling left panel: {e}")
    
    def cleanup(self):
        """Temizlik işlemleri."""
        try:
            if self.data_handler:
                self.data_handler.cleanup()
            
            for container in self.graph_containers:
                if container and hasattr(container, 'cleanup'):
                    container.cleanup()
            
            if self.graph_renderer and hasattr(self.graph_renderer, 'cleanup'):
                self.graph_renderer.cleanup()
            
            self.ui_setup = None
            self.event_handler = None
            self.data_handler = None
            
            logger.debug("TimeGraphWidget cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    # ========== BACKWARD COMPATIBILITY METHODS ==========
    
    def _get_graph_setting(self, graph_index: int, default_value=None):
        """Graph ayarını al."""
        active_tab = self.tab_widget.currentIndex() if hasattr(self, 'tab_widget') else 0
        return self.graph_settings.get(active_tab, {}).get(graph_index, default_value)
    
    def _save_graph_setting(self, graph_index: int, setting_name: str, value: Any):
        """Graph ayarını kaydet."""
        active_tab = self.tab_widget.currentIndex() if hasattr(self, 'tab_widget') else 0
        if active_tab not in self.graph_settings:
            self.graph_settings[active_tab] = {}
        if graph_index not in self.graph_settings[active_tab]:
            self.graph_settings[active_tab][graph_index] = {}
        self.graph_settings[active_tab][graph_index][setting_name] = value
    
    def _update_legend_values(self):
        """Legend değerlerini güncelle."""
        try:
            if self.legend_manager and self.current_cursor_position is not None:
                self.legend_manager.update_cursor_values(self.current_cursor_position)
        except Exception as e:
            logger.error(f"Error updating legend values: {e}")
    
    def _update_statistics_for_range(self, start: float, end: float):
        """Aralık için istatistikleri güncelle."""
        try:
            if self.data_handler:
                active_signals = self.data_handler.get_active_signals()
                logger.debug(f"Statistics update requested for range: {start} - {end}")
        except Exception as e:
            logger.error(f"Error updating statistics for range: {e}")
    
    def _reprocess_current_data(self):
        """Mevcut veriyi yeniden işle."""
        try:
            if self.data_manager and self.data_manager.has_data():
                current_df = self.data_manager.get_dataframe()
                time_column = self.data_manager.get_time_column()
                
                if current_df is not None and self.data_handler:
                    self.data_handler.update_data(current_df, time_column, self.is_normalized)
        except Exception as e:
            logger.error(f"Error reprocessing current data: {e}")
    
    def _calculate_signal_statistics(self, y_data):
        """Sinyal istatistiklerini hesapla."""
        try:
            if not y_data or len(y_data) == 0:
                return {}
            
            y_array = np.array(y_data)
            
            stats = {
                'mean': float(np.mean(y_array)),
                'max': float(np.max(y_array)),
                'min': float(np.min(y_array)),
                'std': float(np.std(y_array)),
                'rms': float(np.sqrt(np.mean(y_array**2)))
            }
            
            # Duty cycle hesaplama
            if len(y_array) > 1:
                if self.duty_cycle_threshold_mode == "auto":
                    threshold = np.mean(y_array)
                else:
                    threshold = self.duty_cycle_threshold_value
                
                high_samples = np.sum(y_array > threshold)
                duty_cycle = (high_samples / len(y_array)) * 100
                stats['duty_cycle'] = float(duty_cycle)
            
            return stats
        except Exception as e:
            logger.error(f"Error calculating signal statistics: {e}")
            return {}

