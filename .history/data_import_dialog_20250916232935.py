#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Veri Import Dialog'u
=============================

Bu dialog, veri dosyalarını açmak için gelişmiş seçenekler sunar:
- Veri önizlemesi (ilk 100 satır)
- Zaman kolonu seçimi
- Header satırı belirleme
- Başlangıç satırı seçimi
- Encoding (Unicode) seçimi
- Delimiter seçimi
- Dosya formatı otomatik algılama
"""

import os
import sys
import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QGroupBox, QLabel, QComboBox, QSpinBox, QPushButton, QTextEdit, QCheckBox,
    QProgressBar, QMessageBox, QFrame, QScrollArea, QGridLayout, QLineEdit, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal as Signal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

logger = logging.getLogger(__name__)

class DataPreviewThread(QThread):
    """Veri önizlemesi için background thread."""
    
    preview_ready = Signal(object, dict)  # DataFrame ve metadata
    error_occurred = Signal(str)
    
    def __init__(self, file_path: str, encoding: str = 'utf-8', delimiter: str = ',', 
                 header_row: int = 0):
        super().__init__()
        self.file_path = file_path
        self.encoding = encoding
        self.delimiter = delimiter
        self.header_row = header_row
        
    def run(self):
        """Veri önizlemesi yükle."""
        try:
            # Dosya uzantısına göre okuma yöntemi belirle
            file_ext = os.path.splitext(self.file_path)[1].lower()
            
            if file_ext == '.csv':
                # CSV dosyası için pandas kullan
                # Basit mantık: sadece header ve veri başlangıcı
                df = pd.read_csv(
                    self.file_path,
                    encoding=self.encoding,
                    delimiter=self.delimiter,
                    header=self.header_row if self.header_row >= 0 else None,
                    nrows=100,  # Sadece ilk 100 satır
                    low_memory=False
                )
            elif file_ext in ['.xlsx', '.xls']:
                # Excel dosyası
                # Basit mantık: sadece header
                df = pd.read_excel(
                    self.file_path,
                    header=self.header_row if self.header_row >= 0 else None,
                    nrows=100
                )
            elif file_ext == '.parquet':
                # Parquet dosyası
                df = pd.read_parquet(self.file_path)
                df = df.head(100)  # İlk 100 satır
            else:
                # Genel okuma denemesi
                df = pd.read_csv(
                    self.file_path,
                    encoding=self.encoding,
                    delimiter=self.delimiter,
                    header=self.header_row if self.header_row >= 0 else None,
                    skiprows=self.start_row,
                    nrows=100,
                    low_memory=False
                )
            
            # Metadata oluştur
            metadata = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'file_size': os.path.getsize(self.file_path),
                'encoding': self.encoding,
                'delimiter': self.delimiter
            }
            
            self.preview_ready.emit(df, metadata)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class DataImportDialog(QDialog):
    """Gelişmiş veri import dialog'u."""
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.preview_df = None
        self.metadata = None
        self.preview_thread = None
        
        self.selected_time_column = None
        self.selected_encoding = 'utf-8'
        self.selected_delimiter = ','
        self.selected_header_row = 0
        self.selected_start_row = 0
        
        self._setup_ui()
        self._setup_connections()
        self._load_initial_preview()
        
    def _setup_ui(self):
        """Kullanıcı arayüzünü kur."""
        self.setWindowTitle(f"Veri Import - {os.path.basename(self.file_path)}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Üst bilgi paneli - kompakt
        info_frame = self._create_info_panel()
        main_layout.addWidget(info_frame)
        
        # Ana splitter (sol: önizleme, sağ: ayarlar) - ana alanı kaplar
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter, 1)  # Stretch factor = 1
        
        # Sol panel: Veri önizlemesi
        preview_panel = self._create_preview_panel()
        main_splitter.addWidget(preview_panel)
        
        # Sağ panel: Ayarlar
        settings_panel = self._create_settings_panel()
        main_splitter.addWidget(settings_panel)
        
        # Splitter oranları - sol panel daha geniş
        main_splitter.setSizes([650, 350])
        
        # Alt butonlar - kompakt
        button_layout = self._create_button_panel()
        main_layout.addLayout(button_layout)
        
        # Progress bar with status
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        main_layout.addWidget(progress_frame)
        
        # Tema uygula
        self._apply_theme()
        
    def _create_info_panel(self):
        """Üst bilgi paneli oluştur - kompakt."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMaximumHeight(40)  # Maksimum yükseklik sınırla
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)  # Kompakt margin
        
        # Dosya bilgisi
        self.file_info_label = QLabel(f"📁 {os.path.basename(self.file_path)}")
        self.file_info_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(self.file_info_label)
        
        layout.addStretch()
        
        # Dosya boyutu - kompakt
        try:
            file_size = os.path.getsize(self.file_path)
            size_mb = file_size / (1024 * 1024)
            self.size_label = QLabel(f"📊 {size_mb:.1f} MB")
            self.size_label.setFont(QFont("Arial", 8))
            layout.addWidget(self.size_label)
        except:
            pass
            
        return frame
    def _create_preview_panel(self):
        """Veri önizleme paneli oluştur."""
        group = QGroupBox("📋 Veri Önizlemesi (İlk 100 Satır)")
        layout = QVBoxLayout(group)
        
        # Önizleme tablosu
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectColumns)
        layout.addWidget(self.preview_table)
        
        return group
        
    def _create_settings_panel(self):
        """Ayarlar paneli oluştur."""
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)  # Gruplar arası boşluk
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        
        # Dosya format ayarları
        format_group = self._create_format_settings()
        scroll_layout.addWidget(format_group)
        
        # Sütun ayarları
        column_group = self._create_column_settings()
        scroll_layout.addWidget(column_group)
        
        # Satır ayarları
        row_group = self._create_row_settings()
        scroll_layout.addWidget(row_group)
        
        # Zaman kolonu ayarları
        time_group = self._create_time_column_settings()
        scroll_layout.addWidget(time_group)
        
        # Büyük stretch ekle - kalan alanı doldur
        scroll_layout.addStretch(1)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(350)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        return scroll_area
        
    def _create_format_settings(self):
        """Dosya format ayarları grubu."""
        group = QGroupBox("🔧 Dosya Format Ayarları")
        group.setMaximumHeight(120)  # Kompakt yükseklik
        layout = QGridLayout(group)
        layout.setSpacing(4)  # Kompakt spacing
        
        # Encoding seçimi
        layout.addWidget(QLabel("Encoding:"), 0, 0)
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems([
            'utf-8', 'utf-16', 'latin-1', 'cp1252', 'ascii', 'iso-8859-1', 'cp1254'
        ])
        self.encoding_combo.setCurrentText('utf-8')
        layout.addWidget(self.encoding_combo, 0, 1)
        
        # Delimiter seçimi
        layout.addWidget(QLabel("Ayırıcı:"), 1, 0)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([
            ', (Virgül)', '; (Noktalı virgül)', '\\t (Tab)', '| (Pipe)', ' (Boşluk)'
        ])
        self.delimiter_combo.setEditable(True)
        layout.addWidget(self.delimiter_combo, 1, 1)
        
        # Otomatik algıla butonu
        self.auto_detect_btn = QPushButton("🔍 Otomatik Algıla")
        self.auto_detect_btn.setToolTip("Dosya formatını otomatik olarak algıla")
        layout.addWidget(self.auto_detect_btn, 2, 0, 1, 2)
        
        return group
        
    def _create_column_settings(self):
        """Sütun ayarları grubu."""
        group = QGroupBox("📊 Header Ayarları")
        group.setMaximumHeight(120)  # Biraz daha yüksek
        layout = QGridLayout(group)
        layout.setSpacing(4)  # Kompakt spacing
        
        # Header satırı
        layout.addWidget(QLabel("Header Satır Numarası:"), 0, 0)
        self.header_spinbox = QSpinBox()
        self.header_spinbox.setRange(-1, 100)
        self.header_spinbox.setValue(0)
        self.header_spinbox.setSpecialValueText("Header Yok")
        self.header_spinbox.setToolTip("Kolon isimlerinin bulunduğu satır numarası (0=ilk satır)")
        layout.addWidget(self.header_spinbox, 0, 1)
        
        # Header var mı checkbox
        self.has_header_checkbox = QCheckBox("Dosyada header var")
        self.has_header_checkbox.setChecked(True)
        layout.addWidget(self.has_header_checkbox, 1, 0, 1, 2)
        
        # Açıklama
        info_label = QLabel("💡 0=İlk satır header, -1=Header yok")
        info_label.setStyleSheet("color: #7fb3d3; font-size: 9px;")
        layout.addWidget(info_label, 2, 0, 1, 2)
        
        return group
        
    def _create_row_settings(self):
        """Satır ayarları grubu."""
        group = QGroupBox("📝 Satır Ayarları")
        group.setMaximumHeight(100)  # Kompakt yükseklik
        layout = QGridLayout(group)
        layout.setSpacing(4)  # Kompakt spacing
        
        # Veri başlangıç satırı (header'dan sonra)
        layout.addWidget(QLabel("Veri Başlangıç Satırı:"), 0, 0)
        self.start_row_spinbox = QSpinBox()
        self.start_row_spinbox.setRange(0, 1000)
        self.start_row_spinbox.setValue(1)  # Header'dan sonra
        self.start_row_spinbox.setToolTip("Header satırından sonra veri hangi satırda başlıyor")
        layout.addWidget(self.start_row_spinbox, 0, 1)
        
        # Açıklama
        info_label = QLabel("💡 Header=0, Veri=1 → Normal CSV")
        info_label.setStyleSheet("color: #7fb3d3; font-size: 9px;")
        layout.addWidget(info_label, 1, 0, 1, 2)
        
        return group
        
    def _create_time_column_settings(self):
        """Zaman kolonu ayarları grubu."""
        group = QGroupBox("⏰ Zaman Kolonu Ayarları")
        # Time column settings daha büyük olabilir ama yine de sınırla
        group.setMaximumHeight(280)  # Biraz daha büyük ama sınırlı
        layout = QGridLayout(group)
        layout.setSpacing(4)  # Kompakt spacing
        
        # Zaman kolonu modu seçimi
        layout.addWidget(QLabel("Zaman Kolonu Modu:"), 0, 0)
        self.time_mode_combo = QComboBox()
        self.time_mode_combo.addItems([
            "Mevcut Kolonu Kullan", 
            "Yeni Zaman Kolonu Oluştur"
        ])
        layout.addWidget(self.time_mode_combo, 0, 1)
        
        # Mevcut zaman kolonu seçimi
        layout.addWidget(QLabel("Mevcut Zaman Kolonu:"), 1, 0)
        self.time_column_combo = QComboBox()
        self.time_column_combo.addItem("Otomatik Algıla")
        layout.addWidget(self.time_column_combo, 1, 1)
        
        # Zaman formatı
        layout.addWidget(QLabel("Zaman Formatı:"), 2, 0)
        self.time_format_combo = QComboBox()
        self.time_format_combo.addItems([
            'Otomatik', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', 
            '%Y-%m-%d', '%d/%m/%Y', 'Unix Timestamp', 'Saniyelik Index'
        ])
        layout.addWidget(self.time_format_combo, 2, 1)
        
        # Ayırıcı çizgi
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator, 3, 0, 1, 2)
        
        # Yeni zaman kolonu ayarları
        layout.addWidget(QLabel("🕒 Yeni Zaman Kolonu Ayarları"), 4, 0, 1, 2)
        
        # Örnekleme frekansı
        layout.addWidget(QLabel("Örnekleme Frekansı (Hz):"), 5, 0)
        self.sampling_freq_spinbox = QSpinBox()
        self.sampling_freq_spinbox.setRange(1, 1000000)  # 1 Hz - 1 MHz
        self.sampling_freq_spinbox.setValue(1)  # Varsayılan 1 Hz
        self.sampling_freq_spinbox.setSuffix(" Hz")
        layout.addWidget(self.sampling_freq_spinbox, 5, 1)
        
        # Başlangıç zamanı
        layout.addWidget(QLabel("Başlangıç Zamanı:"), 6, 0)
        self.start_time_combo = QComboBox()
        self.start_time_combo.addItems([
            "0 (Sıfırdan Başla)",
            "Şimdiki Zaman", 
            "Özel Zaman"
        ])
        layout.addWidget(self.start_time_combo, 6, 1)
        
        # Özel başlangıç zamanı
        layout.addWidget(QLabel("Özel Başlangıç:"), 7, 0)
        self.custom_start_time = QLineEdit()
        self.custom_start_time.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        self.custom_start_time.setEnabled(False)
        layout.addWidget(self.custom_start_time, 7, 1)
        
        # Zaman birimi
        layout.addWidget(QLabel("Zaman Birimi:"), 8, 0)
        self.time_unit_combo = QComboBox()
        self.time_unit_combo.addItems(['saniye', 'milisaniye', 'mikrosaniye', 'nanosaniye'])
        layout.addWidget(self.time_unit_combo, 8, 1)
        
        # Zaman kolonu adı
        layout.addWidget(QLabel("Yeni Kolon Adı:"), 9, 0)
        self.new_time_column_name = QLineEdit()
        self.new_time_column_name.setText("time_generated")
        layout.addWidget(self.new_time_column_name, 9, 1)
        
        return group
        
    def _create_button_panel(self):
        """Alt buton paneli oluştur - kompakt."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 4)  # Kompakt margin
        
        # Önizleme yenile butonu
        self.refresh_btn = QPushButton("🔄 Yenile")
        self.refresh_btn.setToolTip("Ayarları uygulayarak önizlemeyi yenile")
        self.refresh_btn.setMaximumHeight(32)  # Kompakt yükseklik
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
        
        # İptal butonu
        self.cancel_btn = QPushButton("❌ İptal")
        self.cancel_btn.setMaximumHeight(32)
        layout.addWidget(self.cancel_btn)
        
        # Import butonu
        self.import_btn = QPushButton("✅ Import Et")
        self.import_btn.setDefault(True)
        self.import_btn.setMaximumHeight(32)
        layout.addWidget(self.import_btn)
        
        return layout
        
    def _setup_connections(self):
        """Sinyal-slot bağlantılarını kur."""
        # Buton bağlantıları
        self.cancel_btn.clicked.connect(self.reject)
        self.import_btn.clicked.connect(self.accept)
        self.refresh_btn.clicked.connect(self._refresh_preview)
        self.auto_detect_btn.clicked.connect(self._auto_detect_format)
        
        # Ayar değişikliklerinde otomatik yenileme
        self.encoding_combo.currentTextChanged.connect(self._on_settings_changed)
        self.delimiter_combo.currentTextChanged.connect(self._on_settings_changed)
        self.header_spinbox.valueChanged.connect(self._on_settings_changed)
        self.skip_rows_spinbox.valueChanged.connect(self._on_settings_changed)  # skip_rows
        self.start_row_spinbox.valueChanged.connect(self._on_settings_changed)  # start_row
        self.has_header_checkbox.toggled.connect(self._on_header_checkbox_changed)
        
        # Zaman kolonu ayarları
        self.time_mode_combo.currentTextChanged.connect(self._on_time_mode_changed)
        self.start_time_combo.currentTextChanged.connect(self._on_start_time_changed)
        self.sampling_freq_spinbox.valueChanged.connect(self._on_sampling_freq_changed)
        
        # Tablo seçimi
        self.preview_table.itemSelectionChanged.connect(self._on_column_selected)
        
    def _load_initial_preview(self):
        """İlk önizlemeyi yükle."""
        self._refresh_preview()
        
    def _refresh_preview(self):
        """Önizlemeyi yenile."""
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.quit()
            self.preview_thread.wait()
            
        # Ayarları al
        encoding = self.encoding_combo.currentText()
        delimiter_text = self.delimiter_combo.currentText()
        
        # Delimiter'ı parse et
        if delimiter_text.startswith(','):
            delimiter = ','
        elif delimiter_text.startswith(';'):
            delimiter = ';'
        elif delimiter_text.startswith('\\t'):
            delimiter = '\t'
        elif delimiter_text.startswith('|'):
            delimiter = '|'
        elif delimiter_text.startswith(' '):
            delimiter = ' '
        else:
            delimiter = delimiter_text  # Kullanıcı girişi
            
        header_row = self.header_spinbox.value() if self.has_header_checkbox.isChecked() else -1
        skip_rows = self.skip_rows_spinbox.value()  # Dosya başından atlanacak
        
        # Progress bar göster
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_label.setText("Veri önizlemesi yükleniyor...")
        
        # Thread başlat
        self.preview_thread = DataPreviewThread(
            self.file_path, encoding, delimiter, header_row, skip_rows
        )
        self.preview_thread.preview_ready.connect(self._on_preview_ready)
        self.preview_thread.error_occurred.connect(self._on_preview_error)
        self.preview_thread.start()
        
    def _on_preview_ready(self, df, metadata):
        """Önizleme hazır olduğunda çağrılır."""
        self.preview_df = df
        self.metadata = metadata
        
        # Progress bar gizle
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Tabloyu güncelle
        self._update_preview_table(df)
        
        # Zaman kolonu seçeneklerini güncelle
        self._update_time_column_options(df.columns)
        
    def _on_preview_error(self, error_msg):
        """Önizleme hatası olduğunda çağrılır."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        QMessageBox.warning(
            self, 
            "Önizleme Hatası", 
            f"Veri önizlemesi yüklenirken hata oluştu:\n\n{error_msg}\n\nLütfen format ayarlarını kontrol edin."
        )
        
    def _update_preview_table(self, df):
        """Önizleme tablosunu güncelle."""
        self.preview_table.setRowCount(len(df))
        self.preview_table.setColumnCount(len(df.columns))
        
        # Sütun başlıkları
        self.preview_table.setHorizontalHeaderLabels([str(col) for col in df.columns])
        
        # Veriyi doldur
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                value = df.iloc[i, j]
                if pd.isna(value):
                    item = QTableWidgetItem("NaN")
                    item.setForeground(QColor(128, 128, 128))
                else:
                    item = QTableWidgetItem(str(value))
                    
                self.preview_table.setItem(i, j, item)
                
        # Sütun genişliklerini ayarla
        self.preview_table.resizeColumnsToContents()
        
    def _update_time_column_options(self, columns):
        """Zaman kolonu seçeneklerini güncelle."""
        self.time_column_combo.clear()
        self.time_column_combo.addItem("Otomatik Algıla")
        
        for col in columns:
            self.time_column_combo.addItem(str(col))
            
        # Otomatik zaman kolonu algılama
        time_keywords = ['time', 'timestamp', 'date', 'zaman', 'tarih', 't']
        for col in columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in time_keywords):
                self.time_column_combo.setCurrentText(str(col))
                break
                
    def _on_settings_changed(self):
        """Ayarlar değiştiğinde otomatik yenileme."""
        # Kısa bir gecikme ile yenile (kullanıcı yazmayı bitirsin diye)
        if hasattr(self, '_refresh_timer'):
            self._refresh_timer.stop()
        
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._refresh_preview)
        self._refresh_timer.start(1000)  # 1 saniye gecikme
        
    def _on_header_checkbox_changed(self, checked):
        """Header checkbox değiştiğinde."""
        self.header_spinbox.setEnabled(checked)
        if not checked:
            self.header_spinbox.setValue(-1)
        else:
            self.header_spinbox.setValue(0)
        self._on_settings_changed()
        
    def _on_column_selected(self):
        """Sütun seçildiğinde."""
        selected_columns = []
        for item in self.preview_table.selectedItems():
            col_index = item.column()
            if col_index not in selected_columns:
                selected_columns.append(col_index)
                
        if selected_columns and self.preview_df is not None:
            col_name = self.preview_df.columns[selected_columns[0]]
            # Sadece mevcut kolonu kullan modundayken sütun seçimini güncelle
            if self.time_mode_combo.currentText() == "Mevcut Kolonu Kullan":
                self.time_column_combo.setCurrentText(str(col_name))
                
    def _on_time_mode_changed(self, mode_text: str):
        """Zaman kolonu modu değiştiğinde."""
        is_existing_mode = (mode_text == "Mevcut Kolonu Kullan")
        
        # Mevcut zaman kolonu ayarlarını etkinleştir/devre dışı bırak
        self.time_column_combo.setEnabled(is_existing_mode)
        self.time_format_combo.setEnabled(is_existing_mode)
        
        # Yeni zaman kolonu ayarlarını etkinleştir/devre dışı bırak
        self.sampling_freq_spinbox.setEnabled(not is_existing_mode)
        self.start_time_combo.setEnabled(not is_existing_mode)
        self.custom_start_time.setEnabled(not is_existing_mode and 
                                         self.start_time_combo.currentText() == "Özel Zaman")
        self.time_unit_combo.setEnabled(not is_existing_mode)
        self.new_time_column_name.setEnabled(not is_existing_mode)
        
        logger.debug(f"Zaman kolonu modu değişti: {mode_text}")
        
    def _on_start_time_changed(self, start_time_text: str):
        """Başlangıç zamanı seçimi değiştiğinde."""
        is_custom = (start_time_text == "Özel Zaman")
        self.custom_start_time.setEnabled(is_custom)
        
        if not is_custom:
            self.custom_start_time.clear()
            
    def _on_sampling_freq_changed(self, freq: int):
        """Örnekleme frekansı değiştiğinde."""
        # Frekans bilgisini göster
        period = 1.0 / freq if freq > 0 else 0
        if hasattr(self, 'sampling_freq_spinbox'):
            tooltip = f"Örnekleme periyodu: {period:.6f} saniye"
            self.sampling_freq_spinbox.setToolTip(tooltip)
            
    def _auto_detect_format(self):
        """Dosya formatını otomatik algıla."""
        try:
            # Dosyanın ilk birkaç satırını oku
            with open(self.file_path, 'rb') as f:
                sample = f.read(1024).decode('utf-8', errors='ignore')
                
            # Delimiter algılama
            delimiters = [',', ';', '\t', '|', ' ']
            delimiter_counts = {}
            
            for delim in delimiters:
                count = sample.count(delim)
                delimiter_counts[delim] = count
                
            # En çok bulunan delimiter'ı seç
            best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
            
            # Delimiter combo'yu güncelle
            delimiter_map = {
                ',': ', (Virgül)',
                ';': '; (Noktalı virgül)',
                '\t': '\\t (Tab)',
                '|': '| (Pipe)',
                ' ': ' (Boşluk)'
            }
            
            if best_delimiter in delimiter_map:
                self.delimiter_combo.setCurrentText(delimiter_map[best_delimiter])
                
            QMessageBox.information(
                self,
                "Otomatik Algılama",
                f"Algılanan ayırıcı: '{best_delimiter}'\nÖnizleme otomatik olarak güncellenecek."
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Algılama Hatası",
                f"Otomatik format algılama başarısız:\n{str(e)}"
            )
            
    def _apply_theme(self):
        """Yumuşak uzay teması - göze rahat."""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2a3441, stop: 1 #1e2832);
                color: #e8eaed;
            }
            QGroupBox {
                font-weight: 600;
                border: 1px solid #5f7c8a;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 4px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3a4a5c, stop: 1 #2a3441);
                color: #e8eaed;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #7fb3d3;
                font-weight: 600;
                font-size: 11px;
            }
            QLabel {
                color: #e8eaed;
                font-weight: normal;
                font-size: 11px;
                padding: 1px 2px;
            }
            QTableWidget {
                background-color: #2a3441;
                alternate-background-color: #3a4a5c;
                gridline-color: #5f7c8a;
                selection-background-color: #5f7c8a;
                color: #e8eaed;
                border: 1px solid #5f7c8a;
                border-radius: 4px;
            }
            QTableWidget::item {
                color: #e8eaed;
                padding: 3px 4px;
                font-size: 10px;
            }
            QTableWidget::item:selected {
                background-color: #5f7c8a;
                color: #ffffff;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5f7c8a, stop: 1 #4a6270);
                color: #ffffff;
                padding: 4px 6px;
                border: 1px solid #7fb3d3;
                font-weight: 600;
                font-size: 10px;
            }
            QComboBox, QSpinBox, QLineEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3a4a5c, stop: 1 #2a3441);
                border: 1px solid #5f7c8a;
                border-radius: 4px;
                padding: 2px 4px;
                color: #e8eaed;
                font-weight: normal;
                font-size: 11px;
                min-height: 18px;
                max-height: 24px;
            }
            QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
                border-color: #7fb3d3;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4a6270, stop: 1 #3a4a5c);
            }
            QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
                border-color: #9fc5e8;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4a6270, stop: 1 #3a4a5c);
            }
            QComboBox::drop-down {
                border: none;
                width: 16px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-left: 1px solid #5f7c8a;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #e8eaed;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a3441;
                border: 1px solid #5f7c8a;
                border-radius: 4px;
                selection-background-color: #5f7c8a;
                selection-color: #ffffff;
                color: #e8eaed;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5f7c8a, stop: 1 #4a6270);
                border: 1px solid #7fb3d3;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-weight: 600;
                font-size: 11px;
                min-width: 60px;
                min-height: 20px;
                max-height: 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #7fb3d3, stop: 1 #5f7c8a);
                border-color: #9fc5e8;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4a6270, stop: 1 #3a4a5c);
            }
            QPushButton:default {
                border: 2px solid #7fb3d3;
            }
            QCheckBox {
                color: #e8eaed;
                font-weight: normal;
                font-size: 11px;
                spacing: 4px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #5f7c8a;
                border-radius: 2px;
                background-color: #2a3441;
            }
            QCheckBox::indicator:hover {
                border-color: #7fb3d3;
            }
            QCheckBox::indicator:checked {
                background-color: #5f7c8a;
                border: 1px solid #7fb3d3;
            }
            QScrollArea {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2a3441, stop: 1 #1e2832);
                border: 1px solid #5f7c8a;
                border-radius: 4px;
            }
            QFrame[frameShape="4"] {
                color: #5f7c8a;
                background-color: #5f7c8a;
            }
            QProgressBar {
                border: 1px solid #5f7c8a;
                border-radius: 4px;
                background-color: #2a3441;
                color: #e8eaed;
                text-align: center;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #5f7c8a, stop: 1 #7fb3d3);
                border-radius: 3px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4a6270, stop: 1 #3a4a5c);
                border: 1px solid #5f7c8a;
                width: 14px;
                height: 10px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #5f7c8a;
            }
        """)
        
    def get_import_settings(self) -> Dict[str, Any]:
        """Import ayarlarını döndür."""
        delimiter_text = self.delimiter_combo.currentText()
        
        # Delimiter'ı parse et
        if delimiter_text.startswith(','):
            delimiter = ','
        elif delimiter_text.startswith(';'):
            delimiter = ';'
        elif delimiter_text.startswith('\\t'):
            delimiter = '\t'
        elif delimiter_text.startswith('|'):
            delimiter = '|'
        elif delimiter_text.startswith(' '):
            delimiter = ' '
        else:
            delimiter = delimiter_text
            
        # Zaman kolonu ayarları
        time_mode = self.time_mode_combo.currentText()
        is_custom_time = (time_mode == "Yeni Zaman Kolonu Oluştur")
        
        settings = {
            'file_path': self.file_path,
            'encoding': self.encoding_combo.currentText(),
            'delimiter': delimiter,
            'header_row': self.header_spinbox.value() if self.has_header_checkbox.isChecked() else None,
            'start_row': self.start_row_spinbox.value(),
            'skip_rows': self.skip_rows_spinbox.value(),
            'time_mode': time_mode,
            'create_custom_time': is_custom_time
        }
        
        if is_custom_time:
            # Yeni zaman kolonu ayarları
            settings.update({
                'sampling_frequency': self.sampling_freq_spinbox.value(),
                'start_time_mode': self.start_time_combo.currentText(),
                'custom_start_time': self.custom_start_time.text() if self.custom_start_time.isEnabled() else None,
                'time_unit': self.time_unit_combo.currentText(),
                'new_time_column_name': self.new_time_column_name.text()
            })
        else:
            # Mevcut zaman kolonu ayarları
            settings.update({
                'time_column': self.time_column_combo.currentText() if self.time_column_combo.currentText() != "Otomatik Algıla" else None,
                'time_format': self.time_format_combo.currentText(),
                'time_unit': self.time_unit_combo.currentText()
            })
            
        return settings

def test_dialog():
    """Test fonksiyonu."""
    from PyQt5.QtWidgets import QApplication, QFileDialog
    import sys
    
    app = QApplication(sys.argv)
    
    # Test dosyası seç
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Test için dosya seç",
        "",
        "CSV Dosyaları (*.csv);;Tüm Dosyalar (*.*)"
    )
    
    if file_path:
        dialog = DataImportDialog(file_path)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_import_settings()
            print("Import ayarları:", settings)
        else:
            print("İptal edildi")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_dialog()
