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
import vaex
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, 
    QFileDialog, QStatusBar, QMenuBar, QAction, QSplashScreen
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
            self.status_bar.showMessage(f"Dosya yükleniyor: {os.path.basename(file_path)}...")
            
            # Dosya uzantısına göre yükleme yöntemi seç
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                # CSV dosyası - ayarları kullan
                df_pandas = pd.read_csv(
                    file_path,
                    encoding=settings['encoding'],
                    delimiter=settings['delimiter'],
                    header=settings['header_row'],
                    skiprows=settings['skip_rows'] if settings['skip_rows'] > 0 else None
                )
            elif file_ext in ['.xlsx', '.xls']:
                # Excel dosyası
                df_pandas = pd.read_excel(
                    file_path,
                    header=settings['header_row'],
                    skiprows=settings['skip_rows'] if settings['skip_rows'] > 0 else None
                )
            elif file_ext == '.parquet':
                # Parquet dosyası
                df_pandas = pd.read_parquet(file_path)
            elif file_ext in ['.hdf5', '.h5']:
                # HDF5 dosyası
                df_pandas = pd.read_hdf(file_path)
            else:
                # Varsayılan CSV okuma
                df_pandas = pd.read_csv(
                    file_path,
                    encoding=settings['encoding'],
                    delimiter=settings['delimiter'],
                    header=settings['header_row'],
                    skiprows=settings['skip_rows'] if settings['skip_rows'] > 0 else None
                )
            
            # Pandas'tan Vaex'e çevir
            df = vaex.from_pandas(df_pandas)
            
            if df is None or df.length() == 0:
                raise ValueError("Dosya boş veya okunamadı")
            
            # Zaman kolonu işleme
            time_column = settings.get('time_column')
            if time_column and time_column in df.get_column_names():
                # Zaman kolonu varsa, onu x ekseni olarak ayarla
                logger.info(f"Zaman kolonu olarak '{time_column}' kullanılıyor")
                
                # Zaman formatı dönüşümü
                time_format = settings.get('time_format', 'Otomatik')
                if time_format == 'Unix Timestamp':
                    # Unix timestamp'i datetime'a çevir
                    df['time_converted'] = vaex.from_pandas(pd.to_datetime(df[time_column].to_pandas_df(), unit='s'))
                elif time_format == 'Saniyelik Index':
                    # Index'i saniye cinsinden zaman olarak kullan
                    time_unit = settings.get('time_unit', 'saniye')
                    if time_unit == 'milisaniye':
                        df['time_converted'] = df[time_column] / 1000.0
                    elif time_unit == 'mikrosaniye':
                        df['time_converted'] = df[time_column] / 1000000.0
                    elif time_unit == 'nanosaniye':
                        df['time_converted'] = df[time_column] / 1000000000.0
                    else:
                        df['time_converted'] = df[time_column]
                else:
                    # Otomatik veya özel format
                    try:
                        df['time_converted'] = vaex.from_pandas(pd.to_datetime(df[time_column].to_pandas_df()))
                    except:
                        # Dönüşüm başarısız, orijinal kolonu kullan
                        df['time_converted'] = df[time_column]
            else:
                # Zaman kolonu yoksa, index oluştur
                df['time_converted'] = vaex.arange(0, df.length()) / 1000.0  # Saniye cinsinden
                logger.info("Zaman kolonu bulunamadı, otomatik index oluşturuldu")
            
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
                f"Dosya yüklenemedi:\n\n{error_msg}\n\nLütfen import ayarlarını kontrol edin."
            )
            
            self.status_bar.showMessage("Dosya yükleme başarısız", 5000)
            
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
