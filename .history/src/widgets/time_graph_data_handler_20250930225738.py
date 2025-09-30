# type: ignore
"""
TimeGraph Data Handler Module

Bu modül TimeGraphWidget'ın veri işleme işlemlerini QThread ile yönetir.
Performans odaklı tasarım ile UI donmasını önler.
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal as Signal, QTimer
from PyQt5.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from .time_graph_widget_v2 import TimeGraphWidget

logger = logging.getLogger(__name__)


class DataProcessingWorker(QObject):
    """Veri işleme için QThread worker sınıfı."""
    
    # Sinyaller
    finished = Signal(dict)  # İşlem tamamlandığında
    error = Signal(str)      # Hata durumunda
    progress = Signal(str)   # İlerleme güncellemesi
    
    def __init__(self, df, is_normalized, time_column, signal_processor):
        super().__init__()
        self.df = df
        self.is_normalized = is_normalized
        self.time_column = time_column
        self.signal_processor = signal_processor
        self._is_cancelled = False
    
    def run(self):
        """Ana veri işleme fonksiyonu."""
        try:
            if self._is_cancelled:
                return
                
            self.progress.emit("Veri işleme başlatılıyor...")
            
            # Veri işleme
            all_signals = self.signal_processor.process_data(
                self.df, 
                self.is_normalized, 
                self.time_column
            )
            
            if self._is_cancelled:
                return
                
            self.progress.emit("Veri işleme tamamlandı")
            self.finished.emit(all_signals)
            
        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Data processing error: {e}")
                self.error.emit(str(e))
    
    def cancel(self):
        """İşlemi iptal et."""
        self._is_cancelled = True


class StatisticsCalculationWorker(QObject):
    """İstatistik hesaplama için QThread worker sınıfı."""
    
    # Sinyaller
    finished = Signal(dict)  # {signal_name: stats_dict}
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, signals_data, cursor_positions=None, selected_range=None):
        super().__init__()
        self.signals_data = signals_data
        self.cursor_positions = cursor_positions
        self.selected_range = selected_range
        self._is_cancelled = False
    
    def run(self):
        """İstatistik hesaplama işlemi."""
        try:
            if self._is_cancelled:
                return
                
            self.progress.emit("İstatistikler hesaplanıyor...")
            
            all_stats = {}
            total_signals = len(self.signals_data)
            
            for i, (signal_name, signal_data) in enumerate(self.signals_data.items()):
                if self._is_cancelled:
                    return
                
                # İlerleme güncelle
                progress_pct = int((i / total_signals) * 100)
                self.progress.emit(f"İstatistik hesaplanıyor: {signal_name} ({progress_pct}%)")
                
                # İstatistikleri hesapla
                stats = self._calculate_signal_statistics(signal_data)
                all_stats[signal_name] = stats
            
            if not self._is_cancelled:
                self.progress.emit("İstatistik hesaplama tamamlandı")
                self.finished.emit(all_stats)
                
        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Statistics calculation error: {e}")
                self.error.emit(str(e))
    
    def _calculate_signal_statistics(self, signal_data):
        """Tek bir sinyal için istatistikleri hesapla."""
        try:
            y_data = signal_data.get('y_data', [])
            if y_data is None or len(y_data) == 0:
                return {}
            
            y_array = np.array(y_data)
            
            # Temel istatistikler
            stats = {
                'mean': float(np.mean(y_array)),
                'max': float(np.max(y_array)),
                'min': float(np.min(y_array)),
                'std': float(np.std(y_array)),
                'rms': float(np.sqrt(np.mean(y_array**2)))
            }
            
            # Cursor değerleri
            if self.cursor_positions:
                x_data = signal_data.get('x_data', [])
                if x_data is not None and len(x_data) == len(y_data):
                    x_array = np.array(x_data)
                    
                    for cursor_name, cursor_pos in self.cursor_positions.items():
                        # En yakın indeksi bul
                        idx = np.argmin(np.abs(x_array - cursor_pos))
                        stats[cursor_name] = float(y_array[idx])
            
            # Duty cycle hesaplama
            if len(y_array) > 1:
                # Otomatik threshold (ortalama değer)
                threshold = np.mean(y_array)
                high_samples = np.sum(y_array > threshold)
                duty_cycle = (high_samples / len(y_array)) * 100
                stats['duty_cycle'] = float(duty_cycle)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def cancel(self):
        """İşlemi iptal et."""
        self._is_cancelled = True


class TimeGraphDataHandler:
    """TimeGraphWidget için veri işleme yöneticisi."""
    
    def __init__(self, widget: 'TimeGraphWidget'):
        self.widget = widget
        
        # Thread yönetimi
        self.processing_thread = None
        self.processing_worker = None
        self.statistics_thread = None
        self.statistics_worker = None
        
        # Performans optimizasyonu için cache
        self._statistics_cache = {}
        self._last_cursor_positions = {}
        
        # Throttling için timer
        self._statistics_update_timer = QTimer()
        self._statistics_update_timer.setSingleShot(True)
        self._statistics_update_timer.timeout.connect(self._delayed_statistics_update)
        
    def update_data(self, df, time_column: str = None, is_normalized: bool = False):
        """Veri güncelleme işlemini thread'de başlat."""
        try:
            # Önceki işlemi iptal et
            self._cancel_processing()
            
            # Loading göster
            if self.widget.loading_manager:
                self.widget.loading_manager.start_operation("processing", "Veri işleniyor...")
            
            # Worker thread oluştur
            self.processing_thread = QThread()
            self.processing_worker = DataProcessingWorker(
                df, is_normalized, time_column, self.widget.signal_processor
            )
            self.processing_worker.moveToThread(self.processing_thread)
            
            # Sinyalleri bağla
            self.processing_thread.started.connect(self.processing_worker.run)
            self.processing_worker.finished.connect(self._on_processing_finished)
            self.processing_worker.error.connect(self._on_processing_error)
            self.processing_worker.progress.connect(self._on_processing_progress)
            
            # Cleanup
            self.processing_worker.finished.connect(self.processing_thread.quit)
            self.processing_worker.finished.connect(self.processing_worker.deleteLater)
            self.processing_thread.finished.connect(self.processing_thread.deleteLater)
            
            # Thread'i başlat
            self.processing_thread.start()
            
            logger.info("Data processing started in background thread")
            
        except Exception as e:
            logger.error(f"Error starting data processing: {e}")
            if self.widget.loading_manager:
                self.widget.loading_manager.finish_operation("processing")
    
    def update_statistics_async(self, signals_data: Dict, cursor_positions: Dict = None, 
                               selected_range: tuple = None, force_update: bool = False):
        """İstatistikleri asenkron olarak güncelle."""
        try:
            # Cache kontrolü (performans optimizasyonu)
            cache_key = self._generate_cache_key(signals_data, cursor_positions, selected_range)
            if not force_update and cache_key in self._statistics_cache:
                cached_stats = self._statistics_cache[cache_key]
                self._apply_statistics_to_ui(cached_stats)
                return
            
            # Throttling - çok sık güncelleme yapılmasını önle
            if cursor_positions and cursor_positions == self._last_cursor_positions:
                return
            
            self._last_cursor_positions = cursor_positions.copy() if cursor_positions else {}
            
            # Önceki istatistik işlemini iptal et
            self._cancel_statistics_calculation()
            
            # Worker thread oluştur
            self.statistics_thread = QThread()
            self.statistics_worker = StatisticsCalculationWorker(
                signals_data, cursor_positions, selected_range
            )
            self.statistics_worker.moveToThread(self.statistics_thread)
            
            # Sinyalleri bağla
            self.statistics_thread.started.connect(self.statistics_worker.run)
            self.statistics_worker.finished.connect(self._on_statistics_finished)
            self.statistics_worker.error.connect(self._on_statistics_error)
            self.statistics_worker.progress.connect(self._on_statistics_progress)
            
            # Cleanup
            self.statistics_worker.finished.connect(self.statistics_thread.quit)
            self.statistics_worker.finished.connect(self.statistics_worker.deleteLater)
            self.statistics_thread.finished.connect(self.statistics_thread.deleteLater)
            
            # Thread'i başlat
            self.statistics_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting statistics calculation: {e}")
    
    def update_statistics_throttled(self, signals_data: Dict, cursor_positions: Dict = None):
        """Throttled istatistik güncelleme (UI responsiveness için)."""
        # Mevcut parametreleri sakla
        self._pending_signals_data = signals_data
        self._pending_cursor_positions = cursor_positions
        
        # Timer'ı yeniden başlat (debouncing)
        self._statistics_update_timer.stop()
        self._statistics_update_timer.start(100)  # 100ms gecikme
    
    def _delayed_statistics_update(self):
        """Gecikmeli istatistik güncelleme."""
        if hasattr(self, '_pending_signals_data'):
            self.update_statistics_async(
                self._pending_signals_data,
                self._pending_cursor_positions
            )
    
    def _on_processing_finished(self, all_signals: Dict):
        """Veri işleme tamamlandığında."""
        try:
            if self.widget.loading_manager:
                self.widget.loading_manager.finish_operation("processing")
            
            # Event handler'a yönlendir
            if hasattr(self.widget, 'event_handler'):
                self.widget.event_handler.on_processing_finished(all_signals)
            
            # İstatistikleri güncelle
            self.update_statistics_async(all_signals, force_update=True)
            
        except Exception as e:
            logger.error(f"Error in processing finished handler: {e}")
    
    def _on_processing_error(self, error_msg: str):
        """Veri işleme hatası."""
        if self.widget.loading_manager:
            self.widget.loading_manager.finish_operation("processing")
        
        logger.error(f"Data processing error: {error_msg}")
        
        # Kullanıcıya hata göster
        QMessageBox.critical(
            self.widget,
            "Veri İşleme Hatası",
            f"Veri işlenirken hata oluştu:\n\n{error_msg}"
        )
    
    def _on_processing_progress(self, message: str):
        """Veri işleme ilerlemesi."""
        if self.widget.loading_manager:
            self.widget.loading_manager.update_operation("processing", message)
    
    def _on_statistics_finished(self, all_stats: Dict):
        """İstatistik hesaplama tamamlandığında."""
        try:
            # Cache'e kaydet
            cache_key = self._generate_cache_key(
                self._pending_signals_data if hasattr(self, '_pending_signals_data') else {},
                self._pending_cursor_positions if hasattr(self, '_pending_cursor_positions') else {}
            )
            self._statistics_cache[cache_key] = all_stats
            
            # UI'ya uygula
            self._apply_statistics_to_ui(all_stats)
            
        except Exception as e:
            logger.error(f"Error in statistics finished handler: {e}")
    
    def _on_statistics_error(self, error_msg: str):
        """İstatistik hesaplama hatası."""
        logger.error(f"Statistics calculation error: {error_msg}")
    
    def _on_statistics_progress(self, message: str):
        """İstatistik hesaplama ilerlemesi."""
        # Progress bar veya status message güncellenebilir
        pass
    
    def _apply_statistics_to_ui(self, all_stats: Dict):
        """İstatistikleri UI'ya uygula."""
        try:
            if hasattr(self.widget, 'statistics_panel') and self.widget.statistics_panel:
                for signal_name, stats in all_stats.items():
                    self.widget.statistics_panel.update_statistics(signal_name, stats)
            
            # Statistics updated sinyali gönder
            self.widget.statistics_updated.emit(all_stats)
            
        except Exception as e:
            logger.error(f"Error applying statistics to UI: {e}")
    
    def _generate_cache_key(self, signals_data: Dict, cursor_positions: Dict = None, 
                           selected_range: tuple = None) -> str:
        """Cache key oluştur."""
        try:
            # Basit hash tabanlı key
            key_parts = []
            
            # Sinyal sayısı ve isimler
            if signals_data:
                signal_names = sorted(signals_data.keys())
                key_parts.append(f"signals_{len(signal_names)}_{hash(tuple(signal_names))}")
            
            # Cursor pozisyonları
            if cursor_positions:
                cursor_str = "_".join([f"{k}:{v:.6f}" for k, v in sorted(cursor_positions.items())])
                key_parts.append(f"cursors_{hash(cursor_str)}")
            
            # Seçili aralık
            if selected_range:
                key_parts.append(f"range_{hash(selected_range)}")
            
            return "_".join(key_parts)
            
        except Exception:
            # Fallback - her zaman yeni hesapla
            return f"fallback_{hash(str(signals_data))}"
    
    def _cancel_processing(self):
        """Aktif veri işleme işlemini iptal et."""
        if self.processing_worker:
            self.processing_worker.cancel()
        
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.quit()
            if not self.processing_thread.wait(3000):  # 3 saniye bekle
                logger.warning("Processing thread did not finish, terminating...")
                self.processing_thread.terminate()
                self.processing_thread.wait(1000)
    
    def _cancel_statistics_calculation(self):
        """Aktif istatistik hesaplama işlemini iptal et."""
        if self.statistics_worker:
            self.statistics_worker.cancel()
        
        if self.statistics_thread and self.statistics_thread.isRunning():
            self.statistics_thread.quit()
            if not self.statistics_thread.wait(1000):  # 1 saniye bekle
                self.statistics_thread.terminate()
                self.statistics_thread.wait(500)
    
    def cleanup(self):
        """Temizlik işlemleri."""
        try:
            # Timer'ı durdur
            if self._statistics_update_timer:
                self._statistics_update_timer.stop()
            
            # Thread'leri iptal et
            self._cancel_processing()
            self._cancel_statistics_calculation()
            
            # Cache'i temizle
            self._statistics_cache.clear()
            
            logger.debug("Data handler cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during data handler cleanup: {e}")
    
    def get_active_signals(self) -> Dict:
        """Aktif sinyalleri döndür."""
        try:
            if hasattr(self.widget, 'data_manager') and self.widget.data_manager:
                return self.widget.data_manager.get_all_signals()
            return {}
        except Exception as e:
            logger.error(f"Error getting active signals: {e}")
            return {}
    
    def is_processing(self) -> bool:
        """Veri işleme devam ediyor mu?"""
        return (self.processing_thread and self.processing_thread.isRunning()) or \
               (self.statistics_thread and self.statistics_thread.isRunning())
