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
import json
from typing import Optional
from datetime import datetime
import numpy as np
import polars as pl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, 
    QFileDialog, QStatusBar, QMenuBar, QAction, QSplashScreen, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal as Signal, QObject, QThread
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont

# Import our time graph widget and dialog
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # ORİJİNAL VERSİYON - Kararlı ve test edilmiş
    from time_graph_widget import TimeGraphWidget  # Orijinal stabil versiyon
    from src.data.data_import_dialog import DataImportDialog
    from src.managers.status_bar_manager import StatusBarManager
    from src.graphics.loading_overlay import LoadingManager
    # Multi-file support
    from src.managers.multi_file_manager import MultiFileManager
    from src.data.data_loader import DataLoader
    from src.managers.widget_container_manager import WidgetContainerManager
    # Project file support (.mpai)
    from src.managers.project_file_manager import ProjectFileManager
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


# DataLoader is now imported from src.data.data_loader for better modularity

class OldDataLoader(QObject):
    """Veri yükleme işlemlerini ayrı bir thread'de yürüten worker."""
    finished = Signal(object, str)  # DataFrame ve zaman kolonu adını gönderir
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, settings: dict):
        super().__init__()
        self.settings = settings
        self._datetime_converted = False
        
        # PERFORMANCE: Parquet cache manager
        from src.data.data_cache_manager import DataCacheManager
        self.cache_manager = DataCacheManager()

    def run(self):
        """Veri yükleme işlemini başlatır."""
        try:
            df = self._load_data()
            time_column = self.settings.get('time_column')
            self.finished.emit(df, time_column)
        except FileNotFoundError as e:
            self.error.emit(f"Dosya bulunamadı: {e.filename}")
        except ValueError as e:
            self.error.emit(f"Veri formatı hatası: {e}")
        except Exception as e:
            self.error.emit(f"Beklenmedik bir hata oluştu: {e}")

    def _load_data(self):
        """Asıl veri yükleme mantığı."""
        file_path = self.settings['file_path']
        
        # Dosya uzantısına göre yükleme yöntemi seç
        file_ext = os.path.splitext(file_path)[1].lower()

        # Polars okuma ayarlarını hazırla
        header_row = self.settings.get('header_row')
        start_row = self.settings.get('start_row', 0)
        
        has_header = header_row is not None
        skip_rows = start_row if not has_header else start_row - (header_row + 1)
        
        # CSV okuma seçenekleri - ROBUST MODE
        csv_opts = {
            'encoding': self.settings.get('encoding', 'latin-1'),
            'separator': self.settings.get('delimiter', ','),
            'has_header': has_header,
            'skip_rows': skip_rows,
            'ignore_errors': True,  # Hatalı satırları atla
            'try_parse_dates': False,  # Manuel kontrol için kapalı
            'null_values': ['', 'NULL', 'null', 'None', 'NA', 'N/A', 'nan', 'NaN', '-'],  # Tüm null varyasyonları
            'infer_schema_length': 10000  # Daha fazla satır analiz et
        }
        
        # Excel okuma seçenekleri
        excel_opts = {
            'has_header': has_header,
            'skip_rows': skip_rows
        }

        if file_ext == '.csv':
            try:
                # PERFORMANCE: Parquet cache kullan - 8-27x daha hızlı!
                self.progress.emit("CSV yükleniyor (cache kontrolü)...")
                
                # İlk önce cache'i dene
                df = self.cache_manager.load_with_cache(
                    file_path,
                    infer_schema_length=10000
                )
                
                if df is None:
                    # Cache başarısız, normal CSV okuma
                    logger.warning("Cache failed, falling back to direct CSV read")
                    df = pl.read_csv(file_path, **csv_opts)
                    
            except Exception as e:
                raise ValueError(f"CSV dosyası okunamadı. Ayarları kontrol edin. Hata: {e}")
        elif file_ext in ['.xlsx', '.xls']:
            try:
                # Polars'ın read_excel'i header'ı satır indeksi olarak almaz,
                # bu yüzden veriyi okuduktan sonra ayarlamamız gerekebilir.
                # Şimdilik basit skip_rows kullanıyoruz.
                df = pl.read_excel(file_path, **excel_opts)
            except Exception as e:
                raise ValueError(f"Excel dosyası okunamadı. Dosya bozuk olabilir. Hata: {e}")
        else:
            # Desteklenmeyen format için CSV olarak deneme
            try:
                df = pl.read_csv(file_path, **csv_opts)
            except Exception as e:
                raise ValueError(f"Desteklenmeyen dosya formatı: {file_ext}. Sadece CSV ve Excel dosyaları desteklenmektedir.")
        
        if df is None or df.height == 0:
            raise ValueError("Dosya boş veya okunamadı")
        
        # ROBUST: Veri temizleme ve standardizasyon
        df = self._sanitize_dataframe(df)
        
        # Zaman kolonu işleme
        if self.settings.get('create_custom_time', False):
            # Yeni zaman kolonu oluştur
            df = self._create_custom_time_column(df, self.settings)
        else:
            # Mevcut zaman kolonu kullan
            df = self._use_existing_time_column(df, self.settings)

        # Update time column in settings if it was auto-generated
        time_col_setting = self.settings.get('time_column')
        if not time_col_setting and self.settings.get('create_custom_time', False):
             self.settings['time_column'] = self.settings.get('new_time_column_name', 'time_generated')
        elif not time_col_setting:
             self.settings['time_column'] = 'time' # Fallback for auto-detection case

        return df
    
    def _sanitize_dataframe(self, df):
        """
        Veri frame'i temizle ve robust hale getir.
        ATI Vision benzeri profesyonel veri temizleme.
        """
        try:
            logger.info("[DATA CLEANING] Veri temizleme baslatiliyor...")
            
            # 1. Kolon isimlerini temizle
            df = self._clean_column_names(df)
            
            # 2. Karışık tip kolonları düzelt
            df = self._fix_mixed_type_columns(df)
            
            # 3. Sayısal kolonlardaki NULL değerleri handle et
            df = self._handle_null_values(df)
            
            # 4. Infinite değerleri temizle
            df = self._clean_infinite_values(df)
            
            logger.info(f"[DATA CLEANING] Veri temizleme tamamlandi: {df.height} satir, {len(df.columns)} kolon")
            
            return df
            
        except Exception as e:
            logger.warning(f"Veri temizleme sırasında hata: {e}")
            return df  # Hata olsa bile orijinal df'i döndür
    
    def _clean_column_names(self, df):
        """Kolon isimlerini temizle ve standardize et."""
        try:
            new_names = {}
            for col in df.columns:
                # Boşlukları alt çizgiye çevir, özel karakterleri temizle
                clean_name = str(col).strip()
                # Duplicate isimleri önle
                if clean_name in new_names.values():
                    counter = 1
                    while f"{clean_name}_{counter}" in new_names.values():
                        counter += 1
                    clean_name = f"{clean_name}_{counter}"
                new_names[col] = clean_name
            
            if new_names != {col: col for col in df.columns}:
                df = df.rename(new_names)
                logger.debug(f"Kolon isimleri temizlendi: {len(new_names)} kolon")
            
            return df
        except Exception as e:
            logger.warning(f"Kolon ismi temizleme hatası: {e}")
            return df
    
    def _fix_mixed_type_columns(self, df):
        """
        Karışık tip kolonları düzelt.
        String + Number karışımı kolonları sayısal hale getir.
        """
        try:
            for col in df.columns:
                dtype = df[col].dtype
                
                # String kolonları kontrol et - sayısal olabilir mi?
                if dtype == pl.Utf8:
                    # Sayısala dönüştürmeyi dene
                    try:
                        # ROBUST: strict=False - başarısız olanları NULL yap
                        numeric_col = df[col].cast(pl.Float64, strict=False)
                        
                        # Kaç tane başarılı dönüştü?
                        null_count_before = df[col].null_count()
                        null_count_after = numeric_col.null_count()
                        
                        # Eğer %80'den fazlası sayısal ise, dönüştür
                        success_rate = 1 - ((null_count_after - null_count_before) / df.height)
                        if success_rate > 0.8:
                            df = df.with_columns(numeric_col.alias(col))
                            logger.debug(f"'{col}' kolonu sayısal hale getirildi (%{success_rate*100:.1f} başarı)")
                        else:
                            logger.debug(f"'{col}' kolonu string olarak kalıyor (sadece %{success_rate*100:.1f} sayısal)")
                            
                    except:
                        # Dönüştürülemez, string olarak kal
                        pass
                        
            return df
            
        except Exception as e:
            logger.warning(f"Mixed type fix hatası: {e}")
            return df
    
    def _handle_null_values(self, df):
        """
        NULL değerleri akıllıca handle et.
        Sayısal kolonlar için forward-fill veya 0 kullan.
        """
        try:
            for col in df.columns:
                dtype = df[col].dtype
                null_count = df[col].null_count()
                
                if null_count > 0 and dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]:
                    null_pct = (null_count / df.height) * 100
                    
                    if null_pct < 50:  # Eğer yarısından azı null ise düzelt
                        # Forward fill dene
                        try:
                            df = df.with_columns(
                                df[col].fill_null(strategy="forward").fill_null(0.0).alias(col)
                            )
                            logger.debug(f"'{col}' kolonundaki {null_count} NULL değer düzeltildi")
                        except:
                            # Forward fill başarısız, 0 kullan
                            df = df.with_columns(df[col].fill_null(0.0).alias(col))
                    else:
                        logger.warning(f"'{col}' kolonunda çok fazla NULL var (%{null_pct:.1f}), olduğu gibi bırakıldı")
            
            return df
            
        except Exception as e:
            logger.warning(f"NULL handling hatası: {e}")
            return df
    
    def _clean_infinite_values(self, df):
        """Infinite değerleri temizle (±inf)."""
        try:
            for col in df.columns:
                dtype = df[col].dtype
                
                if dtype in [pl.Float32, pl.Float64]:
                    # Infinite değerleri NULL yap sonra forward fill
                    df = df.with_columns(
                        pl.when(df[col].is_infinite())
                        .then(None)
                        .otherwise(df[col])
                        .fill_null(strategy="forward")
                        .fill_null(0.0)
                        .alias(col)
                    )
            
            return df
            
        except Exception as e:
            logger.warning(f"Infinite cleaning hatası: {e}")
            return df

    def _create_custom_time_column(self, df, settings):
        """Yeni zaman kolonu oluştur."""
        try:
            sampling_freq = settings.get('sampling_frequency', 1000)  # Hz
            start_time_mode = settings.get('start_time_mode', '0 (Sıfırdan Başla)')
            custom_start_time = settings.get('custom_start_time')
            time_unit = settings.get('time_unit', 'saniye')
            column_name = settings.get('new_time_column_name', 'time_generated')
            
            # Veri uzunluğu
            data_length = df.height
            
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
            
            # DataFrame'e ekle
            df = df.with_columns(pl.Series(column_name, time_array))
            
            logger.info(f"Yeni zaman kolonu oluşturuldu: '{column_name}' "
                       f"(Frekans: {sampling_freq} Hz, Birim: {time_unit}, "
                       f"Başlangıç: {start_timestamp}, Uzunluk: {data_length})")
                       
        except Exception as e:
            logger.error(f"Yeni zaman kolonu oluşturulurken hata: {e}")
            # Hata durumunda varsayılan index oluştur
            column_name = settings.get('new_time_column_name', 'time_generated')
            df = df.with_columns(pl.Series(column_name, np.arange(df.height) / 1000.0))
        return df
            
    def _use_existing_time_column(self, df, settings):
        """Mevcut zaman kolonu kullan."""
        time_column_name = settings.get('time_column')

        try:
            # Case 1: A valid time column is provided.
            if time_column_name and time_column_name in df.columns:
                logger.info(f"Zaman kolonu olarak '{time_column_name}' kullanılıyor.")
                time_format = settings.get('time_format', 'Otomatik')
                
                original_series = df.get_column(time_column_name)

                logger.debug(f"Zaman kolonu '{time_column_name}' veri tipi: {original_series.dtype}")
                logger.debug(f"Zaman kolonu '{time_column_name}' ilk 5 değer: {original_series.head().to_list()}")
                logger.debug(f"Seçilen zaman formatı: {time_format}")

                converted_series = None

                if time_format == 'Unix Timestamp':
                    # Unix timestamp'i datetime'a çevir (Polars saniye cinsinden bekler)
                    converted_series = original_series.cast(pl.Datetime)
                elif time_format == 'Saniyelik Index':
                    time_unit = settings.get('time_unit', 'saniye')
                    multiplier = {'saniye': 1.0, 'milisaniye': 1000.0, 'mikrosaniye': 1e6, 'nanosaniye': 1e9}.get(time_unit, 1.0)
                    converted_series = original_series.cast(pl.Float64) / multiplier
                else: # Otomatik veya özel format
                    if original_series.dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]:
                        logger.info(f"Zaman kolonu '{time_column_name}' zaten sayısal, olduğu gibi kullanılıyor.")
                        converted_series = original_series
                    else:
                        # String ise datetime'a çevirmeyi dene
                        try:
                            logger.info(f"Zaman kolonu '{time_column_name}' zaman formatına dönüştürülüyor.")
                            # `cast` ile direkt deneme, olmazsa `strptime`
                            converted_series = original_series.str.to_datetime(errors='coerce')
                        except Exception:
                            logger.warning(f"'{time_column_name}' kolonu zaman formatına dönüştürülemedi. Sayısal olarak deneniyor.")
                            converted_series = original_series.cast(pl.Float64, strict=False)
                
                # Değişiklikleri uygula
                if converted_series is not None:
                    # Datetime ise float'a (Unix timestamp) çevir
                    if converted_series.dtype == pl.Datetime:
                        logger.info(f"Datetime verisi Unix timestamp'e dönüştürülüyor...")
                        # saniye cinsinden timestamp'e çevir
                        converted_series = converted_series.dt.timestamp('ms') / 1000.0
                        self._datetime_converted = True
                    
                    # ROBUST: Eğer sayısal ama çok büyük değerlerse (milisaniye timestamp olabilir)
                    elif converted_series.dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]:
                        # İlk değeri kontrol et - eğer 1e12'den büyükse milisaniye olabilir
                        first_value = converted_series[0]
                        if first_value is not None and abs(first_value) > 1e12:
                            logger.info(f"Zaman kolonu milisaniye timestamp olarak tespit edildi, saniyeye çevriliyor...")
                            converted_series = converted_series / 1000.0
                            self._datetime_converted = True
                            logger.info(f"Örnek değer: {first_value} → {converted_series[0]}")
                    
                    df = df.with_columns(converted_series.alias(time_column_name))
            
            # Case 2: No time column provided, or provided one is invalid. Create a new one.
            else:
                if time_column_name:
                    logger.warning(f"Belirtilen zaman kolonu '{time_column_name}' bulunamadı, 'time' adında otomatik index oluşturuluyor.")
                else:
                    logger.info("Zaman kolonu belirtilmemiş, 'time' adında otomatik index oluşturuluyor.")
                
                df = df.with_columns(pl.Series('time', np.arange(df.height) / 1000.0))
        
        # Case 3: An unexpected error occurred during processing.
        except Exception as e:
            logger.error(f"Mevcut zaman kolonu işlenirken hata: {e}")
            df = df.with_columns(pl.Series('time', np.arange(df.height) / 1000.0))
        
        return df

class DataSaver(QObject):
    """Veri kaydetme işlemlerini ayrı bir thread'de yürüten worker."""
    finished = Signal(str)  # Kaydedilen dosya yolunu gönderir
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, df, file_path, file_filter):
        super().__init__()
        self.df = df
        self.file_path = file_path
        self.file_filter = file_filter

    def run(self):
        """Veri kaydetme işlemini başlatır."""
        try:
            self._save_data()
            self.finished.emit(self.file_path)
        except Exception as e:
            self.error.emit(str(e))

    def _save_data(self):
        """Asıl veri kaydetme mantığı."""
        # Dosya formatına göre kaydet
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        if file_ext == '.csv' or 'CSV' in self.file_filter:
            self.df.write_csv(self.file_path)
        elif file_ext == '.xlsx' or 'Excel' in self.file_filter:
            self.df.write_excel(self.file_path)
        else:
            # Varsayılan CSV
            self.df.write_csv(self.file_path)


class TimeGraphApp(QMainWindow):
    """Ana uygulama penceresi."""
    
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.is_data_modified = False
        
        # Threading members
        self.load_threads = []  # Track all threads for proper cleanup
        self.load_worker = None
        self.save_thread = None
        self.save_worker = None

        # Initialize managers
        self.status_bar_manager = None
        self.loading_manager = None
        
        # Multi-file manager
        self.file_manager = MultiFileManager(self, max_files=3)
        
        # Widget container manager - HER DOSYA İÇİN AYRI WİDGET
        self.widget_container_manager = None
        
        # Project file manager (.mpai)
        self.project_manager = ProjectFileManager(self)
        
        self._setup_loading_manager()
        self._setup_ui()
        self._setup_connections()
        self._setup_status_bar()
        
        # Multi-file manager connections
        self._setup_file_manager_connections()
        
        # Uygulama başlangıç mesajı
        logger.info("Time Graph Uygulaması başlatıldı")
        
    def _setup_ui(self):
        """Kullanıcı arayüzünü kurulum."""
        self.setWindowTitle("Time Graph - Veri Analizi ve Görselleştirme")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # Widget container manager'ı oluştur - HER DOSYA İÇİN AYRI WİDGET
        self.widget_container_manager = WidgetContainerManager(self, self.loading_manager)
        
        # Stacked widget'ı ana widget olarak ayarla
        self.setCentralWidget(self.widget_container_manager.get_stacked_widget())
        
        # Initial widget için sinyal bağlantılarını kur
        if hasattr(self.widget_container_manager, 'initial_widget') and self.widget_container_manager.initial_widget:
            self._connect_widget_signals(self.widget_container_manager.initial_widget)
        
        # Pencere ikonunu ayarla (eğer varsa)
        try:
            # EXE için resource path'i kontrol et
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller ile paketlenmiş durumda
                icon_path = os.path.join(sys._MEIPASS, 'ikon.png')
            else:
                # Geliştirme ortamında
                icon_path = 'ikon.png'
            
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # Fallback ikon yolu
                fallback_path = "icons/app_icon.png"
                if os.path.exists(fallback_path):
                    self.setWindowIcon(QIcon(fallback_path))
        except Exception as e:
            logger.debug(f"İkon yüklenemedi: {e}")
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
        # Widget container manager'dan widget oluşturulduğunda bağlantıları yapacağız
        # İlk widget oluşturulduğunda _connect_widget_signals çağrılacak
        pass
    
    def _connect_widget_signals(self, widget):
        """Bir widget için sinyal-slot bağlantılarını kur."""
        if widget and hasattr(widget, 'toolbar_manager'):
            toolbar = widget.toolbar_manager
            
            # File menü bağlantıları
            if hasattr(toolbar, 'file_open_requested'):
                toolbar.file_open_requested.connect(self._on_file_open)
            if hasattr(toolbar, 'file_save_requested'):
                toolbar.file_save_requested.connect(self._on_file_save)
            if hasattr(toolbar, 'file_exit_requested'):
                toolbar.file_exit_requested.connect(self._on_file_exit)
            if hasattr(toolbar, 'layout_import_requested'):
                toolbar.layout_import_requested.connect(self._on_layout_import)
            if hasattr(toolbar, 'layout_export_requested'):
                toolbar.layout_export_requested.connect(self._on_layout_export)
            # Project file operations (.mpai)
            if hasattr(toolbar, 'project_save_requested'):
                toolbar.project_save_requested.connect(self._on_project_save)
            if hasattr(toolbar, 'project_open_requested'):
                toolbar.project_open_requested.connect(self._on_project_open)
                
        # Veri değişikliği sinyali
        if widget:
            widget.data_changed.connect(self._on_data_changed)
            
            # Tema değişikliği sinyali - status bar'ı güncelle
            if hasattr(widget, 'theme_manager'):
                widget.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        logger.debug("Widget signals connected")
    
    def _setup_file_manager_connections(self):
        """Multi-file manager sinyal bağlantılarını kur."""
        self.file_manager.file_switched.connect(self._on_file_switched)
        self.file_manager.file_closed.connect(self._on_file_closed)
        self.file_manager.all_files_closed.connect(self._on_all_files_closed)
            
    def _setup_status_bar(self):
        """Durum çubuğunu kur."""
        # Create custom status bar with system monitoring
        self.status_bar_manager = StatusBarManager(self)
        self.setStatusBar(self.status_bar_manager)
        
        # Store reference for compatibility
        self.status_bar = self.status_bar_manager
        
        # === DOSYA SEKMELERİNİ STATUS BAR'A EKLE ===
        # Dosya sekmelerini oluştur
        file_tab_widget = self.file_manager.create_file_tab_widget()
        
        # Status bar'ın başına (soluna) ekle
        self.status_bar_manager.insertPermanentWidget(0, file_tab_widget)
        
        logger.debug("File tabs added to status bar")
    
    def _setup_loading_manager(self):
        """Loading manager'ı kur."""
        self.loading_manager = LoadingManager(self)
        
        # Başlangıçta tema renklerini ayarla
        self._update_status_bar_theme()
    
    def _update_status_bar_theme(self):
        """Status bar tema renklerini güncelle."""
        try:
            active_widget = self.widget_container_manager.get_active_widget()
            if self.status_bar_manager and active_widget and hasattr(active_widget, 'theme_manager'):
                theme_colors = active_widget.theme_manager.get_theme_colors()
                self.status_bar_manager.update_theme(theme_colors)
        except Exception as e:
            logger.debug(f"Could not update status bar theme at startup: {e}")
        
    def _on_file_open(self):
        """Dosya açma işlemi - Gelişmiş import dialog ile."""
        logger.info("Dosya açma işlemi başlatıldı")
        
        # Desteklenen dosya formatları
        file_filter = (
            "Veri Dosyaları (*.csv *.xlsx *.xls);;",
            "CSV Dosyaları (*.csv);;",
            "Excel Dosyaları (*.xlsx *.xls);;",
            "Tüm Dosyalar (*.*)"
        )
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Veri Dosyası Seç",
            "",
            "".join(file_filter)
        )
        
        if file_path:
            # Dosya boyutunu kontrol et (25 MB sınırı)
            try:
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb > 25:
                    QMessageBox.warning(
                        self,
                        "Dosya Çok Büyük",
                        f"Seçilen dosya çok büyük ({file_size_mb:.1f} MB).\n\n"
                        f"Maksimum dosya boyutu: 25 MB\n"
                        f"Lütfen daha küçük bir dosya seçin."
                    )
                    return
            except Exception as e:
                logger.error(f"Dosya boyutu kontrol edilirken hata: {e}")
                QMessageBox.critical(
                    self,
                    "Dosya Hatası",
                    f"Dosya bilgileri alınamadı:\n{str(e)}"
                )
                return
            
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
        # Reset datetime conversion flag
        self._datetime_converted = False
        
        try:
            file_path = settings['file_path']
            filename = os.path.basename(file_path)
            
            # Start loading operation
            self.loading_manager.start_operation("file_loading", f"Loading {filename}...")
            self.status_bar.set_operation("File Loading", 0)
            
            # === MULTI-FILE CHECK ===
            # Check if file already open
            existing_index = self.file_manager.is_file_already_open(file_path)
            if existing_index >= 0:
                self.file_manager.file_tab_widget.setCurrentIndex(existing_index)
                QMessageBox.information(
                    self,
                    "Dosya Zaten Açık",
                    f"'{filename}' dosyası zaten açık.\nİlgili sekmeye geçildi."
                )
                return
            
            # Check file limit
            if not self.file_manager.can_add_file():
                QMessageBox.warning(
                    self,
                    "Maksimum Dosya Sayısı",
                    f"Maksimum {self.file_manager.max_files} dosya açık olabilir.\n"
                    f"Yeni dosya yüklemek için önce bir dosyayı kapatın."
                )
                return
            
            # Dosya boyutunu kontrol et
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 25:
                # Bu duruma gelmemeli çünkü dosya seçiminde kontrol ediliyor
                raise ValueError(f"Dosya çok büyük ({file_size_mb:.1f} MB). Maksimum boyut: 25 MB")
            elif file_size_mb > 10:
                self.loading_manager.update_operation("file_loading", f"Large file: {filename} ({file_size_mb:.1f} MB)")
            else:
                self.loading_manager.update_operation("file_loading", f"Loading: {filename}")
            
            # === FİX: DÜZGÜN THREAD YÖNETİMİ ===
            # Yeni thread oluştur
            load_thread = QThread()
            load_worker = DataLoader(settings)
            load_worker.moveToThread(load_thread)

            # Connect signals
            load_thread.started.connect(load_worker.run)
            load_worker.finished.connect(self.on_loading_finished)
            load_worker.error.connect(self.on_loading_error)
            load_worker.progress.connect(lambda msg: self.loading_manager.update_operation("file_loading", msg))
            
            # Cleanup - BU KRİTİK!
            load_worker.finished.connect(load_thread.quit)
            load_worker.error.connect(load_thread.quit)  # Error durumunda da quit et
            load_worker.finished.connect(load_worker.deleteLater)
            load_thread.finished.connect(load_thread.deleteLater)
            
            # Thread'i listede tut (temizlik için)
            self.load_threads.append((load_thread, load_worker))
            self.load_worker = load_worker  # Current worker reference

            # Start the thread
            load_thread.start()
            logger.debug(f"Started loading thread for {filename}")

        except Exception as e:
             # This will now only catch errors from the pre-flight checks, not the loading itself
            error_msg = f"Dosya yükleme başlatılırken hata oluştu: {str(e)}"
            logger.error(error_msg)
            self.loading_manager.finish_operation("file_loading")
            QMessageBox.critical(self, "Dosya Yükleme Hatası", error_msg)
            self.status_bar.showMessage("Dosya yükleme başarısız", 5000)

    def on_loading_finished(self, df, time_column):
        """Worker thread'den veri yükleme bittiğinde çağrılır."""
        try:
            file_path = self.load_worker.settings.get('file_path', self.current_file_path)
            filename = os.path.basename(file_path)

            logger.debug(f"Widget'a gönderilen zaman kolonu: '{time_column}'")
            logger.debug(f"DataFrame kolonları: {df.columns}")
            if time_column in df.columns:
                time_data_sample = df.get_column(time_column).head(5).to_numpy()
                logger.debug(f"Zaman kolonu '{time_column}' ilk 5 değer: {time_data_sample}")
            
            # ROBUST: Veri kalite özeti göster
            self._show_data_quality_summary(df, filename)
            
            # === MULTI-FILE: Dosyayı file manager'a ekle ===
            file_metadata = {
                'file_path': file_path,
                'filename': filename,
                'df': df,
                'time_column': time_column,
                'settings': self.load_worker.settings.copy(),
                'datetime_converted': getattr(self.load_worker, '_datetime_converted', False),
                'is_data_modified': False
            }
            
            # Dosyayı ekle ve index al
            file_index = self.file_manager.add_file(file_metadata)
            
            if file_index < 0:
                logger.error("File could not be added to manager")
                return
            
            # Bu dosya için yeni bir widget oluştur
            logger.info(f"[WIDGET CREATE] Creating new widget for file {file_index}")
            widget = self.widget_container_manager.create_widget_for_file(file_index)
            
            # Widget sinyallerini bağla
            self._connect_widget_signals(widget)
            
            # Widget'a geç
            self.widget_container_manager.switch_to_file_widget(file_index)
            
            # Veriyi widget'a yükle
            logger.info(f"[WIDGET CREATE] Loading data to widget for file {file_index}")
            widget.update_data(df, time_column=time_column)
            
            # Datetime axis ayarını yap
            active_container = widget.get_active_graph_container()
            if active_container and hasattr(active_container.plot_manager, 'enable_datetime_axis'):
                if file_metadata['datetime_converted']:
                    active_container.plot_manager.enable_datetime_axis(True)
                    logger.info("Datetime axis formatting enabled for better readability")
                    if hasattr(widget, 'statistics_panel'):
                        widget.statistics_panel.set_datetime_axis(True)
                else:
                    active_container.plot_manager.enable_datetime_axis(False)
                    logger.info("Datetime axis formatting disabled for numeric data")
                    if hasattr(widget, 'statistics_panel'):
                        widget.statistics_panel.set_datetime_axis(False)
            
            # Başarılı yükleme
            self.current_file_path = file_path
            self.is_data_modified = False
            
            self.setWindowTitle(f"Time Graph Widget - {filename}")
            
            row_count = df.height
            col_count = len(df.columns)
            self.status_bar.showMessage(
                f"Dosya yüklendi: {filename} ({row_count:,} satır, {col_count} sütun)", 
                10000
            )
            
            logger.info(f"Dosya başarıyla yüklendi: {file_path} ({row_count} satır, {col_count} sütun)")
            logger.info(f"Toplam açık dosya: {self.file_manager.get_file_count()}/{self.file_manager.max_files}")
            
        except Exception as e:
            error_msg = f"Veri widget'a yüklenirken hata oluştu: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Veri İşleme Hatası", error_msg)

        finally:
            self.loading_manager.finish_operation("file_loading")

    def on_loading_error(self, error_msg):
        """Worker thread'de bir hata oluştuğunda çağrılır."""
        logger.error(f"Dosya yüklenirken hata oluştu (worker'dan): {error_msg}")
        self.loading_manager.finish_operation("file_loading")
        QMessageBox.critical(
            self,
            "Dosya Yükleme Hatası",
            f"Dosya yüklenemedi:\n\n{error_msg}\n\nLütfen import ayarlarını kontrol edin."
        )
    
    def _show_data_quality_summary(self, df, filename=""):
        """Yüklenen verinin kalite özetini logla."""
        try:
            # Hızlı kalite kontrolü
            total_cols = len(df.columns)
            total_rows = df.height
            
            # NULL oranlarını hesapla
            high_null_cols = []
            for col in df.columns:
                null_count = df[col].null_count()
                if null_count > 0:
                    null_pct = (null_count / total_rows) * 100
                    if null_pct > 20:
                        high_null_cols.append((str(col), null_pct, null_count))
            
            # Log raporu
            logger.info(f"[QUALITY REPORT] Veri Kalite Raporu - {filename}")
            logger.info(f"[QUALITY REPORT] Toplam: {total_rows} satir, {total_cols} kolon")
            
            if high_null_cols:
                logger.info(f"[QUALITY REPORT] Yuksek NULL orani olan kolonlar: {len(high_null_cols)}")
                for col, pct, count in high_null_cols[:5]:
                    logger.info(f"[QUALITY REPORT] - '{col}': {count} NULL (%{pct:.1f}) - otomatik duzeltildi")
            else:
                logger.info(f"[QUALITY REPORT] Tum kolonlar temiz (dusuk NULL orani)")
                
            logger.info(f"[QUALITY REPORT] Veri kullanima hazir!")
            
        except Exception as e:
            logger.debug(f"Data quality summary failed: {e}")
            
    def _on_file_save(self):
        """Dosya kaydetme işlemi."""
        active_widget = self.widget_container_manager.get_active_widget()
        if not active_widget:
            return
            
        logger.info("Dosya kaydetme işlemi başlatıldı")
        
        # Kaydetme formatı seç
        file_filter = (
            "CSV Dosyası (*.csv);;",
            "Excel Dosyası (*.xlsx)"
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
            try:
                self.status_bar.showMessage(f"Dosya kaydediliyor: {os.path.basename(file_path)}...")
                
                # Mevcut veriyi al
                export_data = active_widget.export_data()
                
                if not export_data or 'signals' not in export_data:
                    raise ValueError("Kaydedilecek veri bulunamadı")
                    
                signals = export_data['signals']
                
                if not signals:
                    raise ValueError("Kaydedilecek sinyal bulunamadı")
                    
                first_signal = next(iter(signals.values()))
                time_data = first_signal.get('x_data', [])
                
                data_dict = {'time': time_data}
                for signal_name, signal_data in signals.items():
                    data_dict[signal_name] = signal_data.get('y_data', [])
                    
                df_to_save = pl.DataFrame(data_dict)

                # --- Threaded Data Saving ---
                self.save_thread = QThread()
                self.save_worker = DataSaver(df_to_save, file_path, selected_filter)
                self.save_worker.moveToThread(self.save_thread)

                # Connect signals
                self.save_thread.started.connect(self.save_worker.run)
                self.save_worker.finished.connect(self.on_saving_finished)
                self.save_worker.error.connect(self.on_saving_error)
                
                # Cleanup
                self.save_worker.finished.connect(self.save_thread.quit)
                self.save_worker.finished.connect(self.save_worker.deleteLater)
                self.save_thread.finished.connect(self.save_thread.deleteLater)

                # Start the thread
                self.save_thread.start()

            except (ValueError, KeyError) as e:
                error_msg = f"Kaydedilecek veri hazırlanırken hata oluştu: {str(e)}"
                logger.error(error_msg)
                QMessageBox.warning(self, "Veri Kaydetme Hatası", error_msg)
                self.status_bar.showMessage("Veri kaydetme başarısız", 5000)
            except Exception as e:
                error_msg = f"Dosya kaydetme işlemi başlatılamadı: {str(e)}"
                logger.error(error_msg)
                QMessageBox.critical(self, "Dosya Kaydetme Hatası", error_msg)

    def on_saving_finished(self, saved_path):
        """Worker thread'den dosya kaydetme bittiğinde çağrılır."""
        self.is_data_modified = False
        self.status_bar.showMessage(
            f"Dosya kaydedildi: {os.path.basename(saved_path)}", 
            5000
        )
        logger.info(f"Dosya başarıyla kaydedildi: {saved_path}")

    def on_saving_error(self, error_msg):
        """Worker thread'de kaydetme hatası oluştuğunda çağrılır."""
        logger.error(f"Dosya kaydedilirken hata oluştu (worker'dan): {error_msg}")
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
        
        # Aktif dosyanın modified flag'ini güncelle
        active_file = self.file_manager.get_active_file_data()
        if active_file:
            active_file['is_data_modified'] = True
        
        # Pencere başlığına * ekle
        current_title = self.windowTitle()
        if not current_title.endswith('*'):
            self.setWindowTitle(current_title + '*')
    
    # Widget state save/restore artık gerekli değil - her dosyanın kendi widget instance'ı var
    
    def _on_file_switched(self, new_index: int, old_index: int):
        """Dosya sekmesi değiştiğinde çağrılır - sadece widget'lar arası geçiş yap."""
        file_data = self.file_manager.get_file_data(new_index)
        if not file_data:
            return
        
        logger.info(f"[FILE SWITCH] Switching from file {old_index} to file {new_index}: {file_data['filename']}")
        
        try:
            # Sadece widget'a geç - her dosyanın kendi widget'ı var!
            self.widget_container_manager.switch_to_file_widget(new_index)
            
            # UI güncellemeleri
            self.current_file_path = file_data['file_path']
            self.is_data_modified = file_data['is_data_modified']
            self.setWindowTitle(f"Time Graph Widget - {file_data['filename']}")
            
            row_count = file_data['df'].height
            col_count = len(file_data['df'].columns)
            self.status_bar.showMessage(
                f"Aktif dosya: {file_data['filename']} ({row_count:,} satır, {col_count} sütun)",
                5000
            )
            
            logger.info(f"Successfully switched to file: {file_data['filename']}")
            
        except Exception as e:
            error_msg = f"Dosya değiştirme sırasında hata: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Dosya Değiştirme Hatası", error_msg)
    
    def _on_file_closed(self, file_index: int):
        """Bir dosya kapatıldığında çağrılır."""
        logger.info(f"[FILE CLOSE] Closing file {file_index}")
        
        # Bu dosyanın widget'ını kaldır
        self.widget_container_manager.remove_widget_for_file(file_index)
        
        logger.info(f"[FILE CLOSE] Widget removed for file {file_index}")
    
    def _on_all_files_closed(self):
        """Tüm dosyalar kapatıldığında çağrılır."""
        self.setWindowTitle("Time Graph - Veri Analizi ve Görselleştirme")
        self.status_bar.showMessage("Tüm dosyalar kapatıldı", 3000)
        self.current_file_path = None
        self.is_data_modified = False
        
        # Tüm widget'ları temizle
        self.widget_container_manager.cleanup_all()
    
    def _on_theme_changed(self, theme_name: str):
        """Tema değişikliği olayı - status bar'ı güncelle."""
        try:
            active_widget = self.widget_container_manager.get_active_widget()
            if self.status_bar_manager and active_widget and hasattr(active_widget, 'theme_manager'):
                # Tema renklerini al ve status bar'ı güncelle
                theme_colors = active_widget.theme_manager.get_theme_colors()
                self.status_bar_manager.update_theme(theme_colors)
                logger.debug(f"Status bar theme updated to: {theme_name}")
        except Exception as e:
            logger.error(f"Error updating status bar theme: {e}")
            
    def _on_layout_import(self):
        """Layout'u bir dosyadan içe aktar."""
        active_widget = self.widget_container_manager.get_active_widget()
        if not active_widget:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Layout",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    layout_config = json.load(f)
                
                active_widget.set_layout_config(layout_config)
                
                self.status_bar.showMessage(f"Layout başarıyla içe aktarıldı: {os.path.basename(file_path)}", 5000)
                logger.info(f"Layout başarıyla içe aktarıldı: {file_path}")

            except Exception as e:
                error_msg = f"Layout içe aktarılırken hata oluştu: {str(e)}"
                logger.error(error_msg)
                QMessageBox.critical(
                    self,
                    "Layout Import Hatası",
                    error_msg
                )

    def _on_layout_export(self):
        """Mevcut layout'u bir dosyaya aktar."""
        active_widget = self.widget_container_manager.get_active_widget()
        if not active_widget:
            return

        try:
            layout_config = active_widget.get_layout_config()

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Layout",
                "layout.json",
                "JSON Files (*.json)"
            )

            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(layout_config, f, indent=4)
                
                self.status_bar.showMessage(f"Layout başarıyla dışa aktarıldı: {os.path.basename(file_path)}", 5000)
                logger.info(f"Layout başarıyla dışa aktarıldı: {file_path}")

        except Exception as e:
            error_msg = f"Layout dışa aktarılırken hata oluştu: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(
                self,
                "Layout Export Hatası",
                error_msg
            )
    
    def _on_project_save(self):
        """Projeyi kaydet (.mpai format) - Veri + Layout + Metadata tek dosyada."""
        active_widget = self.widget_container_manager.get_active_widget()
        if not active_widget:
            QMessageBox.warning(
                self,
                "Proje Kaydedilemedi",
                "Kaydedilecek bir veri yok. Önce bir dosya yükleyin."
            )
            return
        
        # Check if data exists
        if not hasattr(active_widget, 'data_manager'):
            QMessageBox.warning(
                self,
                "Proje Kaydedilemedi",
                "Veri yöneticisi bulunamadı."
            )
            return
        
        # Get dataframe from data manager
        dataframe = active_widget.data_manager.get_data()
        if dataframe is None or (hasattr(dataframe, 'height') and dataframe.height == 0):
            QMessageBox.warning(
                self,
                "Proje Kaydedilemedi",
                "Kaydedilecek veri bulunamadı."
            )
            return
        
        try:
            # Get current file info
            active_file_index = self.file_manager.get_active_file_index()
            file_data = self.file_manager.get_file_data(active_file_index)
            
            # Suggest filename based on original file
            suggested_name = "project.mpai"
            if file_data:
                original_name = file_data.get('filename', 'project')
                # Remove extension and add .mpai
                base_name = os.path.splitext(original_name)[0]
                suggested_name = f"{base_name}.mpai"
            
            # File dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Proje Kaydet (.mpai)",
                suggested_name,
                "MPAI Project Files (*.mpai)"
            )
            
            if not file_path:
                return
            
            # Show loading overlay
            if self.loading_manager:
                self.loading_manager.show_loading("Proje kaydediliyor...")
            
            # Get dataframe and layout
            dataframe = active_widget.data_manager.df
            layout_config = active_widget.get_layout_config()
            
            # Prepare metadata
            metadata = {
                'original_file': file_data.get('filename', 'unknown') if file_data else 'unknown',
                'original_file_path': file_data.get('file_path', '') if file_data else '',
                'time_column': file_data.get('time_column', '') if file_data else '',
                'saved_date': datetime.now().isoformat(),
            }
            
            # Save project
            success = self.project_manager.save_project(
                file_path,
                dataframe,
                layout_config,
                metadata
            )
            
            # Hide loading overlay
            if self.loading_manager:
                self.loading_manager.hide_loading()
            
            if success:
                self.status_bar.showMessage(
                    f"✅ Proje başarıyla kaydedildi: {os.path.basename(file_path)}", 
                    5000
                )
                logger.info(f"Project saved: {file_path}")
                
                # Mark as not modified
                if file_data:
                    file_data['is_data_modified'] = False
                    
            else:
                QMessageBox.critical(
                    self,
                    "Proje Kaydetme Hatası",
                    "Proje kaydedilemedi. Lütfen log dosyasını kontrol edin."
                )
                
        except Exception as e:
            error_msg = f"Proje kaydedilemedi: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if self.loading_manager:
                self.loading_manager.hide_loading()
            
            QMessageBox.critical(
                self,
                "Proje Kaydetme Hatası",
                error_msg
            )
    
    def _on_project_open(self):
        """Proje aç (.mpai format) - Veri + Layout tek dosyadan hızlı yükleme."""
        # File dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Proje Aç (.mpai)",
            "",
            "MPAI Project Files (*.mpai)"
        )
        
        if not file_path:
            return
        
        try:
            # Validate project file
            is_valid, message = self.project_manager.validate_project(file_path)
            if not is_valid:
                QMessageBox.warning(
                    self,
                    "Geçersiz Proje Dosyası",
                    f"Proje dosyası geçerli değil:\n\n{message}"
                )
                return
            
            # Show loading overlay
            if self.loading_manager:
                self.loading_manager.show_loading("Proje yükleniyor...")
            
            # Load project
            project_data = self.project_manager.load_project(file_path)
            
            if project_data is None:
                if self.loading_manager:
                    self.loading_manager.hide_loading()
                QMessageBox.critical(
                    self,
                    "Proje Yükleme Hatası",
                    "Proje yüklenemedi. Lütfen log dosyasını kontrol edin."
                )
                return
            
            # Extract data
            dataframe = project_data['dataframe']
            layout_config = project_data['layout_config']
            metadata = project_data['metadata']
            
            # Get filename from metadata or file path
            original_filename = metadata.get('custom', {}).get('original_file', os.path.basename(file_path))
            time_column = metadata.get('custom', {}).get('time_column', 'time')
            
            # Check if file is already open
            existing_index = self.file_manager.is_file_already_open(file_path)
            if existing_index >= 0:
                # Switch to existing file
                self.file_manager.switch_to_file(existing_index)
                if self.loading_manager:
                    self.loading_manager.hide_loading()
                self.status_bar.showMessage(f"Proje zaten açık: {original_filename}", 3000)
                return
            
            # Check if we can add more files
            if not self.file_manager.can_add_file():
                if self.loading_manager:
                    self.loading_manager.hide_loading()
                QMessageBox.warning(
                    self,
                    "Dosya Limiti",
                    f"Maksimum {self.file_manager.max_files} dosya aynı anda açık olabilir.\nBir dosyayı kapatıp tekrar deneyin."
                )
                return
            
            # Convert polars to pandas for compatibility
            df_pandas = dataframe.to_pandas()
            
            # Create new widget for this project
            new_widget = self.widget_container_manager.create_widget()
            
            # Load data into widget
            new_widget.load_data(df_pandas, time_column)
            
            # Apply layout configuration
            QTimer.singleShot(500, lambda: new_widget.set_layout_config(layout_config))
            
            # Add to file manager
            file_metadata = {
                'file_path': file_path,
                'filename': original_filename,
                'df': dataframe,
                'time_column': time_column,
                'widget': new_widget,
                'is_data_modified': False,
                'is_project_file': True  # Mark as project file
            }
            
            file_index = self.file_manager.add_file(file_metadata)
            
            # Hide loading overlay
            if self.loading_manager:
                self.loading_manager.hide_loading()
            
            if file_index >= 0:
                self.status_bar.showMessage(
                    f"✅ Proje başarıyla yüklendi: {original_filename} (Parquet - Hızlı!)", 
                    5000
                )
                logger.info(f"Project loaded: {file_path}")
            else:
                QMessageBox.warning(
                    self,
                    "Dosya Eklenemedi",
                    "Dosya yüklendi ancak listeye eklenemedi."
                )
                
        except Exception as e:
            error_msg = f"Proje yüklenemedi: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if self.loading_manager:
                self.loading_manager.hide_loading()
            
            QMessageBox.critical(
                self,
                "Proje Yükleme Hatası",
                error_msg
            )

    def closeEvent(self, event):
        """Pencere kapatma olayı."""
        # Check for unsaved changes in ANY file
        has_unsaved = False
        for file_data in self.file_manager.loaded_files:
            if file_data.get('is_data_modified', False):
                has_unsaved = True
                break
        
        if has_unsaved:
            reply = QMessageBox.question(
                self,
                "Kaydedilmemiş Değişiklikler",
                "Bir veya daha fazla dosyada kaydedilmemiş değişiklikler var.\nÇıkmak istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
                
        # Temizlik işlemleri - tüm widget'ları temizle
        if self.widget_container_manager:
            self.widget_container_manager.cleanup_all()
        
        # Cleanup status bar and loading manager
        if self.status_bar_manager:
            self.status_bar_manager.cleanup()
        
        # Cleanup project manager temp files
        if hasattr(self, 'project_manager') and self.project_manager:
            self.project_manager.cleanup()
            logger.debug("Project manager cleaned up")
        
        # === FİX: TÜM LOAD THREAD'LERİNİ TEMİZLE ===
        logger.info("Cleaning up load threads...")
        for thread, worker in self.load_threads:
            try:
                if thread.isRunning():
                    thread.quit()
                    if not thread.wait(2000):
                        logger.warning(f"Thread did not finish, terminating...")
                        thread.terminate()
                        thread.wait(1000)
            except RuntimeError as e:
                logger.debug(f"Thread already deleted: {e}")
            
        try:
            if self.save_thread and self.save_thread.isRunning():
                self.save_thread.quit()
                if not self.save_thread.wait(3000):  # Wait up to 3 seconds
                    logger.warning("Save thread did not finish, terminating...")
                    self.save_thread.terminate()
                    self.save_thread.wait(1000)
        except RuntimeError as e:
            logger.debug(f"Save thread already deleted: {e}")

        if self.loading_manager:
            # Finish any active operations
            for operation in self.loading_manager.get_active_operations():
                self.loading_manager.finish_operation(operation)
            
        # Debug: Thread sayısını logla
        self._log_active_threads()
        
        logger.info("Uygulama kapatılıyor")
        event.accept()
    
    def _log_active_threads(self):
        """Aktif thread'leri logla."""
        import threading
        active_threads = threading.active_count()
        logger.info(f"Aktif thread sayısı: {active_threads}")
        
        # QThread'leri kontrol et
        qthread_count = 0
        try:
            if hasattr(self, 'load_thread') and self.load_thread and self.load_thread.isRunning():
                qthread_count += 1
                logger.info("- Load thread hala çalışıyor")
        except RuntimeError:
            pass  # Thread already deleted
            
        try:
            if hasattr(self, 'save_thread') and self.save_thread and self.save_thread.isRunning():
                qthread_count += 1
                logger.info("- Save thread hala çalışıyor")
        except RuntimeError:
            pass  # Thread already deleted
            
        # Check all widgets for threads
        if hasattr(self, 'widget_container_manager') and self.widget_container_manager:
            for file_index, widget in self.widget_container_manager.widgets.items():
                if widget:
                    try:
                        if hasattr(widget, 'processing_thread') and widget.processing_thread and widget.processing_thread.isRunning():
                            qthread_count += 1
                            logger.info(f"- Processing thread for file {file_index} hala çalışıyor")
                    except RuntimeError:
                        pass  # Thread already deleted
                        
                    if hasattr(widget, 'graph_renderer') and widget.graph_renderer:
                        try:
                            deviation_threads = [t for t in widget.graph_renderer.deviation_threads.values() if t.isRunning()]
                        except RuntimeError:
                            deviation_threads = []
                        qthread_count += len(deviation_threads)
                        if deviation_threads:
                            logger.info(f"- {len(deviation_threads)} deviation thread for file {file_index} hala çalışıyor")
        if hasattr(self, 'status_bar_manager') and self.status_bar_manager:
            if hasattr(self.status_bar_manager, 'monitor_thread') and self.status_bar_manager.monitor_thread.isRunning():
                qthread_count += 1
                logger.info("- Monitor thread hala çalışıyor")
        
        logger.info(f"Toplam QThread sayısı: {qthread_count}")

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
        import traceback
        full_error = traceback.format_exc()
        logger.error(f"Uygulama başlatılırken hata oluştu: {e}")
        logger.error(f"Full traceback: {full_error}")
        print(f"FULL ERROR TRACEBACK:\n{full_error}")
        
        # Hata mesajı göster
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Başlatma Hatası")
        error_msg.setText(f"Uygulama başlatılamadı:\n\n{str(e)}")
        error_msg.exec_()
        
        sys.exit(1)

if __name__ == "__main__":
    main()
