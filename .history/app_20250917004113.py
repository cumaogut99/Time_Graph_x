#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Graph Widget - Bağımsız Uygulama
=====================================

Bu uygulama, time graph widget'ını bağımsız bir masaüstü uygulaması olarak çalıştırır.
Veri analizi ve görselleştirme için gelişmiş araçlar sunar.

Özellikler:
- Çoklu grafik desteği
- Gerçek zamanlı istatistikler
- Tema desteği
- Veri dışa/içe aktarma
- Gelişmiş cursor araçları
"""

import sys
import os
import logging
from typing import Optional
import numpy as np
import pandas as pd
import vaex
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, 
    QFileDialog, QStatusBar, QMenuBar, QAction, QSplashScreen, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal as Signal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont

# Import our time graph widget and dialog
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from time_graph_widget import TimeGraphWidget
    from data_import_dialog import DataImportDialog
except ImportError as e:
    print(f"Import hatası: {e}")
    print("Lütfen tüm gerekli modüllerin mevcut olduğundan emin olun.")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('time_graph_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TimeGraphApp(QMainWindow):
    """Ana uygulama penceresi."""
    
    def __init__(self):
        super().__init__()
        self.time_graph_widget = None
        self.current_file_path = None
        self.is_data_modified = False
        
        self._setup_ui()
        self._setup_connections()
        self._setup_status_bar()
        
        # Uygulama başlangıç mesajı
        logger.info("Time Graph Widget Uygulaması başlatıldı")
        self.status_bar.showMessage("Hazır - Veri dosyası açmak için File > Open kullanın", 5000)
        
    def _setup_ui(self):
        """Kullanıcı arayüzünü kurulum."""
        self.setWindowTitle("Time Graph Widget - Veri Analizi ve Görselleştirme")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # Ana widget'ı oluştur
        self.time_graph_widget = TimeGraphWidget()
        self.setCentralWidget(self.time_graph_widget)
        
        # Pencere ikonunu ayarla (eğer varsa)
        try:
            self.setWindowIcon(QIcon("icons/app_icon.png"))
        except:
            pass  # İkon yoksa devam et
            
        # Pencereyi ekranın ortasına yerleştir
        self._center_window()
        
    def _center_window(self):
        """Pencereyi ekranın ortasına yerleştir."""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def _setup_connections(self):
        """Sinyal-slot bağlantılarını kur."""
        if self.time_graph_widget and hasattr(self.time_graph_widget, 'toolbar_manager'):
            toolbar = self.time_graph_widget.toolbar_manager
            
            # File menü bağlantıları
            if hasattr(toolbar, 'file_open_requested'):
                toolbar.file_open_requested.connect(self._on_file_open)
            if hasattr(toolbar, 'file_save_requested'):
                toolbar.file_save_requested.connect(self._on_file_save)
            if hasattr(toolbar, 'file_exit_requested'):
                toolbar.file_exit_requested.connect(self._on_file_exit)
                
        # Veri değişikliği sinyali
        if self.time_graph_widget:
            self.time_graph_widget.data_changed.connect(self._on_data_changed)
            
    def _setup_status_bar(self):
        """Durum çubuğunu kur."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Durum çubuğuna bilgi ekle
        self.status_bar.showMessage("Hazır")
        
    def _on_file_open(self):
        """Dosya açma işlemi - Gelişmiş import dialog ile."""
        logger.info("Dosya açma işlemi başlatıldı")
        
        # Desteklenen dosya formatları
        file_filter = (
            "Veri Dosyaları (*.csv *.xlsx *.xls *.parquet *.hdf5 *.h5);;",
            "CSV Dosyaları (*.csv);;",
            "Excel Dosyaları (*.xlsx *.xls);;",
            "Parquet Dosyaları (*.parquet);;",
            "HDF5 Dosyaları (*.hdf5 *.h5);;",
            "Tüm Dosyalar (*.*)"
        )
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Veri Dosyası Seç",
            "",
            "".join(file_filter)
        )
        
        if file_path:
            # Gelişmiş import dialog'unu aç
            import_dialog = DataImportDialog(file_path, self)
            if import_dialog.exec_() == QDialog.Accepted:
                # Import ayarlarını al
                settings = import_dialog.get_import_settings()
                self._load_data_with_settings(settings)
            else:
                logger.info("Dosya import işlemi iptal edildi")
                
    def _load_data_with_settings(self, settings: dict):
        """Ayarlarla veri dosyasını yükle."""
        try:
            file_path = settings['file_path']
            filename = os.path.basename(file_path)
            self.status_bar.showMessage(f"📂 Dosya yükleniyor: {filename}...")
            
            # Dosya boyutunu kontrol et
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 50:
                self.status_bar.showMessage(f"⚠️ Büyük dosya yükleniyor: {filename} ({file_size_mb:.1f} MB) - Lütfen bekleyin...")
            
            # Dosya uzantısına göre yükleme yöntemi seç
            file_ext = os.path.splitext(file_path)[1].lower()

            # Pandas okuma ayarlarını hazırla
            header = settings.get('header_row')
            start_row = settings.get('start_row', 0)
            
            skip_rows = None
            if header is not None:
                # Header ile veri başlangıcı arasındaki satırları atla
                if start_row > (header + 1):
                    skip_rows = list(range(header + 1, start_row))
            elif start_row > 0:
                # Header yoksa, baştan itibaren atla
                skip_rows = list(range(start_row))

            read_opts = {
                'header': header,
                'skiprows': skip_rows
            }
            csv_opts = {
                'encoding': settings['encoding'],
                'delimiter': settings['delimiter'],
                **read_opts
            }

            if file_ext == '.csv':
                df_pandas = pd.read_csv(file_path, **csv_opts)
            elif file_ext in ['.xlsx', '.xls']:
                df_pandas = pd.read_excel(file_path, **read_opts)
            elif file_ext == '.parquet':
                df_pandas = pd.read_parquet(file_path)
                if start_row > 0:
                    df_pandas = df_pandas.iloc[start_row:]
            elif file_ext in ['.hdf5', '.h5']:
                df_pandas = pd.read_hdf(file_path)
                if start_row > 0:
                    df_pandas = df_pandas.iloc[start_row:]
            else:
                df_pandas = pd.read_csv(file_path, **csv_opts)
            
            # Pandas'tan Vaex'e çevir
            df = vaex.from_pandas(df_pandas)
            
            if df is None or df.length() == 0:
                raise ValueError("Dosya boş veya okunamadı")
            
            # Zaman kolonu işleme
            if settings.get('create_custom_time', False):
                # Yeni zaman kolonu oluştur
                df = self._create_custom_time_column(df, settings)
            else:
                # Mevcut zaman kolonu kullan
                df = self._use_existing_time_column(df, settings)
            
            # Performans için veri optimizasyonu
            df_optimized = self._optimize_data_for_performance(df)
            
            # Veriyi widget'a yükle
            time_col_setting = settings.get('time_column')
            if not time_col_setting and settings.get('create_custom_time', False):
                 time_col_setting = settings.get('new_time_column_name', 'time_generated')
            elif not time_col_setting:
                 time_col_setting = 'time' # Fallback for auto-detection case
            
            logger.debug(f"Widget'a gönderilen zaman kolonu: '{time_col_setting}'")
            logger.debug(f"DataFrame kolonları: {df_optimized.get_column_names()}")
            if time_col_setting in df_optimized.get_column_names():
                time_data_sample = df_optimized[time_col_setting].to_numpy()[:5]
                logger.debug(f"Zaman kolonu '{time_col_setting}' ilk 5 değer: {time_data_sample}")
            
            self.time_graph_widget.update_data(df_optimized, time_column=time_col_setting)
            
            # Başarılı yükleme
            self.current_file_path = file_path
            self.is_data_modified = False
            
            # Pencere başlığını güncelle
            filename = os.path.basename(file_path)
            self.setWindowTitle(f"Time Graph Widget - {filename}")
            
            # Durum mesajı
            row_count = df.length()
            col_count = len(df.get_column_names())
            self.status_bar.showMessage(
                f"Dosya yüklendi: {filename} ({row_count:,} satır, {col_count} sütun)", 
                10000
            )
            
            logger.info(f"Dosya başarıyla yüklendi: {file_path} ({row_count} satır, {col_count} sütun)")
            
        except Exception as e:
            error_msg = f"Dosya yüklenirken hata oluştu: {str(e)}"
            logger.error(error_msg)
            
            QMessageBox.critical(
                self,
                "Dosya Yükleme Hatası",
                f"Dosya yüklenemedi:\n\n{error_msg}\n\nLütfen import ayarlarını kontrol edin."
            )
            
            self.status_bar.showMessage("Dosya yükleme başarısız", 5000)
            
    def _create_custom_time_column(self, df, settings):
        """Yeni zaman kolonu oluştur."""
        try:
            sampling_freq = settings.get('sampling_frequency', 1000)  # Hz
            start_time_mode = settings.get('start_time_mode', '0 (Sıfırdan Başla)')
            custom_start_time = settings.get('custom_start_time')
            time_unit = settings.get('time_unit', 'saniye')
            column_name = settings.get('new_time_column_name', 'time_generated')
            
            # Veri uzunluğu
            data_length = df.length()
            
            # Zaman aralığını hesapla (saniye cinsinden)
            time_step = 1.0 / sampling_freq
            
            # Zaman birimi dönüşümü
            if time_unit == 'milisaniye':
                time_step *= 1000
            elif time_unit == 'mikrosaniye':
                time_step *= 1000000
            elif time_unit == 'nanosaniye':
                time_step *= 1000000000
            # 'saniye' için dönüşüm gerekmiyor
            
            # Başlangıç zamanını belirle
            if start_time_mode == "Şimdiki Zaman":
                import datetime
                start_timestamp = datetime.datetime.now().timestamp()
                if time_unit != 'saniye':
                    # Saniye dışındaki birimler için timestamp'i dönüştür
                    if time_unit == 'milisaniye':
                        start_timestamp *= 1000
                    elif time_unit == 'mikrosaniye':
                        start_timestamp *= 1000000
                    elif time_unit == 'nanosaniye':
                        start_timestamp *= 1000000000
            elif start_time_mode == "Özel Zaman" and custom_start_time:
                try:
                    import datetime
                    dt = datetime.datetime.strptime(custom_start_time, '%Y-%m-%d %H:%M:%S')
                    start_timestamp = dt.timestamp()
                    if time_unit != 'saniye':
                        if time_unit == 'milisaniye':
                            start_timestamp *= 1000
                        elif time_unit == 'mikrosaniye':
                            start_timestamp *= 1000000
                        elif time_unit == 'nanosaniye':
                            start_timestamp *= 1000000000
                except:
                    logger.warning(f"Özel başlangıç zamanı parse edilemedi: {custom_start_time}, sıfır kullanılıyor")
                    start_timestamp = 0.0
            else:
                # "0 (Sıfırdan Başla)" veya varsayılan
                start_timestamp = 0.0
            
            # Zaman dizisini oluştur
            time_array = np.arange(data_length) * time_step + start_timestamp
            
            # DataFrame'e ekle (numpy array'i pandas'a çevirip vaex'e ekle)
            df = df.copy()  # Değişiklik için kopya oluştur
            df[column_name] = time_array
            
            logger.info(f"Yeni zaman kolonu oluşturuldu: '{column_name}' "
                       f"(Frekans: {sampling_freq} Hz, Birim: {time_unit}, "
                       f"Başlangıç: {start_timestamp}, Uzunluk: {data_length})")
                       
        except Exception as e:
            logger.error(f"Yeni zaman kolonu oluşturulurken hata: {e}")
            # Hata durumunda varsayılan index oluştur
            df = df.copy()
            column_name = settings.get('new_time_column_name', 'time_generated')
            df[column_name] = np.arange(df.length()) / 1000.0
        return df
            
    def _use_existing_time_column(self, df, settings):
        """Mevcut zaman kolonu kullan."""
        df = df.copy() # Start with a copy to avoid side effects
        time_column_name = settings.get('time_column')

        try:
            # Case 1: A valid time column is provided.
            if time_column_name and time_column_name in df.get_column_names():
                logger.info(f"Zaman kolonu olarak '{time_column_name}' kullanılıyor.")
                time_format = settings.get('time_format', 'Otomatik')
                
                original_series_pd = df[time_column_name].to_pandas_series()
                converted_values = None

                logger.debug(f"Zaman kolonu '{time_column_name}' veri tipi: {original_series_pd.dtype}")
                logger.debug(f"Zaman kolonu '{time_column_name}' ilk 5 değer: {original_series_pd.head().tolist()}")
                logger.debug(f"Seçilen zaman formatı: {time_format}")

                if time_format == 'Unix Timestamp':
                    converted_values = pd.to_datetime(original_series_pd, unit='s', errors='coerce').values
                elif time_format == 'Saniyelik Index':
                    time_unit = settings.get('time_unit', 'saniye')
                    multiplier = {'saniye': 1.0, 'milisaniye': 1000.0, 'mikrosaniye': 1e6, 'nanosaniye': 1e9}.get(time_unit, 1.0)
                    converted_values = pd.to_numeric(original_series_pd, errors='coerce').values / multiplier
                else: # Otomatik veya özel format
                    # If the column is already numeric, don't try to convert it to datetime
                    # unless a specific format is provided.
                    if np.issubdtype(original_series_pd.dtype, np.number):
                        logger.info(f"Zaman kolonu '{time_column_name}' zaten sayısal, olduğu gibi kullanılıyor.")
                        converted_values = original_series_pd.values
                    else:
                        # It's not numeric, so it's likely a datetime string. Try to convert.
                        try:
                            # Try to convert to datetime
                            logger.info(f"Zaman kolonu '{time_column_name}' zaman formatına dönüştürülüyor.")
                            converted_values = pd.to_datetime(original_series_pd, errors='coerce').values
                        except Exception:
                            # If conversion fails, keep original values
                            logger.warning(f"'{time_column_name}' kolonu zaman formatına dönüştürülemedi. Orijinal veri kullanılıyor.")
                            # As a last resort, try converting to a number
                            converted_values = pd.to_numeric(original_series_pd, errors='coerce').values
                
                # Overwrite column with converted values if conversion happened
                if converted_values is not None:
                    logger.debug(f"Dönüştürülmüş zaman verisi ilk 5 değer: {converted_values[:5]}")
                    
                    # Convert datetime64 to float (Unix timestamp) for compatibility
                    if 'datetime64' in str(converted_values.dtype):
                        logger.info(f"Datetime64 verisi Unix timestamp'e dönüştürülüyor...")
                        # Convert to Unix timestamp (seconds since epoch)
                        converted_values = converted_values.astype('datetime64[ns]').astype(np.float64) / 1e9
                        logger.debug(f"Unix timestamp ilk 5 değer: {converted_values[:5]}")
                    
                    df[time_column_name] = converted_values
            
            # Case 2: No time column provided, or provided one is invalid. Create a new one.
            else:
                if time_column_name:
                    logger.warning(f"Belirtilen zaman kolonu '{time_column_name}' bulunamadı, 'time' adında otomatik index oluşturuluyor.")
                else:
                    logger.info("Zaman kolonu belirtilmemiş, 'time' adında otomatik index oluşturuluyor.")
                
                df['time'] = np.arange(df.length()) / 1000.0  # Saniye cinsinden
        
        # Case 3: An unexpected error occurred during processing.
        except Exception as e:
            logger.error(f"Mevcut zaman kolonu işlenirken hata: {e}")
            df['time'] = np.arange(df.length()) / 1000.0 # Fallback to index
        
        return df
            
    def _optimize_data_for_performance(self, df):
        """Büyük veriler için performans optimizasyonu."""
        try:
            data_length = df.length()
            logger.info(f"Veri optimizasyonu başlıyor: {data_length:,} satır")
            
            # Performans eşikleri
            MAX_POINTS_DISPLAY = 10000  # Ekranda max gösterilecek nokta
            MAX_POINTS_MEMORY = 50000   # Bellekte tutulacak max nokta
            
            if data_length <= MAX_POINTS_DISPLAY:
                # Küçük veri, optimizasyon gereksiz
                logger.info("Küçük veri seti, optimizasyon atlanıyor")
                return df
                
            elif data_length <= MAX_POINTS_MEMORY:
                # Orta boyut: Sadece görüntü için downsample
                downsample_ratio = max(1, data_length // MAX_POINTS_DISPLAY)
                logger.info(f"Orta boyut veri: {downsample_ratio}x downsampling")
                
                # Her N'inci noktayı al
                indices = np.arange(0, data_length, downsample_ratio)
                df_optimized = df.take(indices)
                
            else:
                # Büyük veri: Agresif downsampling
                downsample_ratio = max(1, data_length // MAX_POINTS_DISPLAY)
                logger.info(f"Büyük veri: {downsample_ratio}x agresif downsampling")
                
                # Chunked processing ile bellek dostu downsampling
                chunk_size = 100000
                sampled_indices = []
                
                for start in range(0, data_length, chunk_size):
                    end = min(start + chunk_size, data_length)
                    chunk_indices = np.arange(start, end, downsample_ratio)
                    sampled_indices.extend(chunk_indices)
                
                # İlk ve son noktaları her zaman dahil et
                if 0 not in sampled_indices:
                    sampled_indices.insert(0, 0)
                if (data_length - 1) not in sampled_indices:
                    sampled_indices.append(data_length - 1)
                    
                df_optimized = df.take(sampled_indices)
            
            optimized_length = df_optimized.length()
            reduction_ratio = data_length / optimized_length
            
            logger.info(f"Optimizasyon tamamlandı: {data_length:,} → {optimized_length:,} "
                       f"({reduction_ratio:.1f}x azaltma)")
            
            # Optimizasyon bilgisini kullanıcıya göster
            if reduction_ratio > 2:
                self.status_bar.showMessage(
                    f"🚀 Performans optimizasyonu: {data_length:,} → {optimized_length:,} nokta "
                    f"({reduction_ratio:.1f}x hızlandırma)", 
                    10000
                )
            else:
                self.status_bar.showMessage(
                    f"✅ Veri yüklendi: {optimized_length:,} nokta", 
                    5000
                )
            
            return df_optimized
            
        except Exception as e:
            logger.error(f"Veri optimizasyonu hatası: {e}")
            # Hata durumunda orijinal veriyi döndür
            return df
            
    def _load_data_file(self, file_path: str):
        """Veri dosyasını yükle."""
        try:
            self.status_bar.showMessage(f"Dosya yükleniyor: {os.path.basename(file_path)}...")
            
            # Dosya uzantısına göre yükleme yöntemi seç
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = vaex.from_csv(file_path)
            elif file_ext == '.parquet':
                df = vaex.from_parquet(file_path)
            elif file_ext in ['.hdf5', '.h5']:
                df = vaex.open(file_path)
            else:
                # Varsayılan olarak vaex'in otomatik algılamasını dene
                df = vaex.open(file_path)
                
            if df is None or df.length() == 0:
                raise ValueError("Dosya boş veya okunamadı")
                
            # Veriyi widget'a yükle
            self.time_graph_widget.update_data(df)
            
            # Başarılı yükleme
            self.current_file_path = file_path
            self.is_data_modified = False
            
            # Pencere başlığını güncelle
            filename = os.path.basename(file_path)
            self.setWindowTitle(f"Time Graph Widget - {filename}")
            
            # Durum mesajı
            row_count = df.length()
            col_count = len(df.get_column_names())
            self.status_bar.showMessage(
                f"Dosya yüklendi: {filename} ({row_count:,} satır, {col_count} sütun)", 
                10000
            )
            
            logger.info(f"Dosya başarıyla yüklendi: {file_path} ({row_count} satır, {col_count} sütun)")
            
        except Exception as e:
            error_msg = f"Dosya yüklenirken hata oluştu: {str(e)}"
            logger.error(error_msg)
            
            QMessageBox.critical(
                self,
                "Dosya Yükleme Hatası",
                f"Dosya yüklenemedi:\n\n{error_msg}\n\nLütfen geçerli bir veri dosyası seçin."
            )
            
            self.status_bar.showMessage("Dosya yükleme başarısız", 5000)
            
    def _on_file_save(self):
        """Dosya kaydetme işlemi."""
        if not self.time_graph_widget:
            return
            
        logger.info("Dosya kaydetme işlemi başlatıldı")
        
        # Kaydetme formatı seç
        file_filter = (
            "CSV Dosyası (*.csv);;",
            "Parquet Dosyası (*.parquet);;",
            "HDF5 Dosyası (*.hdf5)"
        )
        
        default_name = "time_graph_data.csv"
        if self.current_file_path:
            default_name = os.path.splitext(os.path.basename(self.current_file_path))[0] + "_exported.csv"
            
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Veriyi Kaydet",
            default_name,
            "".join(file_filter)
        )
        
        if file_path:
            self._save_data_file(file_path, selected_filter)
            
    def _save_data_file(self, file_path: str, file_filter: str):
        """Veri dosyasını kaydet."""
        try:
            self.status_bar.showMessage(f"Dosya kaydediliyor: {os.path.basename(file_path)}...")
            
            # Mevcut veriyi al
            export_data = self.time_graph_widget.export_data()
            
            if not export_data or 'signals' not in export_data:
                raise ValueError("Kaydedilecek veri bulunamadı")
                
            signals = export_data['signals']
            
            # İlk sinyalden zaman eksenini al
            if not signals:
                raise ValueError("Kaydedilecek sinyal bulunamadı")
                
            first_signal = next(iter(signals.values()))
            time_data = first_signal.get('x_data', [])
            
            # DataFrame oluştur
            data_dict = {'time': time_data}
            for signal_name, signal_data in signals.items():
                data_dict[signal_name] = signal_data.get('y_data', [])
                
            df = vaex.from_arrays(**data_dict)
            
            # Dosya formatına göre kaydet
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv' or 'CSV' in file_filter:
                df.export_csv(file_path)
            elif file_ext == '.parquet' or 'Parquet' in file_filter:
                df.export_parquet(file_path)
            elif file_ext in ['.hdf5', '.h5'] or 'HDF5' in file_filter:
                df.export_hdf5(file_path)
            else:
                # Varsayılan CSV
                df.export_csv(file_path)
                
            # Başarılı kaydetme
            self.is_data_modified = False
            
            self.status_bar.showMessage(
                f"Dosya kaydedildi: {os.path.basename(file_path)}", 
                5000
            )
            
            logger.info(f"Dosya başarıyla kaydedildi: {file_path}")
            
        except Exception as e:
            error_msg = f"Dosya kaydedilirken hata oluştu: {str(e)}"
            logger.error(error_msg)
            
            QMessageBox.critical(
                self,
                "Dosya Kaydetme Hatası",
                f"Dosya kaydedilemedi:\n\n{error_msg}"
            )
            
            self.status_bar.showMessage("Dosya kaydetme başarısız", 5000)
            
    def _on_file_exit(self):
        """Uygulamadan çıkış."""
        self.close()
        
    def _on_data_changed(self, data):
        """Veri değişikliği işlemi."""
        self.is_data_modified = True
        
        # Pencere başlığına * ekle
        current_title = self.windowTitle()
        if not current_title.endswith('*'):
            self.setWindowTitle(current_title + '*')
            
    def closeEvent(self, event):
        """Pencere kapatma olayı."""
        if self.is_data_modified:
            reply = QMessageBox.question(
                self,
                "Kaydedilmemiş Değişiklikler",
                "Kaydedilmemiş değişiklikler var. Çıkmak istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
                
        # Temizlik işlemleri
        if self.time_graph_widget:
            self.time_graph_widget.cleanup()
            
        logger.info("Uygulama kapatılıyor")
        event.accept()

def create_splash_screen():
    """Başlangıç ekranı oluştur."""
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.darkBlue)
    
    painter = QPainter(splash_pix)
    painter.setPen(Qt.white)
    
    # Başlık
    font = QFont("Arial", 16, QFont.Bold)
    painter.setFont(font)
    painter.drawText(splash_pix.rect(), Qt.AlignCenter, 
                    "Time Graph Widget\n\nVeri Analizi ve Görselleştirme\n\nYükleniyor...")
    
    painter.end()
    
    splash = QSplashScreen(splash_pix)
    splash.setMask(splash_pix.mask())
    return splash

def main():
    """Ana uygulama fonksiyonu."""
    # QApplication oluştur
    app = QApplication(sys.argv)
    app.setApplicationName("Time Graph Widget")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Data Analysis Tools")
    
    # Başlangıç ekranı göster
    splash = create_splash_screen()
    splash.show()
    app.processEvents()
    
    try:
        # Ana pencereyi oluştur
        splash.showMessage("Ana pencere oluşturuluyor...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        app.processEvents()
        
        main_window = TimeGraphApp()
        
        splash.showMessage("Arayüz hazırlanıyor...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        app.processEvents()
        
        # Pencereyi göster
        main_window.show()
        
        # Başlangıç ekranını kapat
        splash.finish(main_window)
        
        # Uygulama döngüsünü başlat
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Uygulama başlatılırken hata oluştu: {e}")
        
        # Hata mesajı göster
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Başlatma Hatası")
        error_msg.setText(f"Uygulama başlatılamadı:\n\n{str(e)}")
        error_msg.exec_()
        
        sys.exit(1)

if __name__ == "__main__":
    main()
