#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Graph Widget - Performans Testi
=====================================

Bu script uygulamanın performansını ölçer:
- Başlatma süresi
- Veri yükleme süresi
- Memory kullanımı
- UI responsiveness
"""

import sys
import os
import time
import psutil
import json
from datetime import datetime
import tracemalloc

# Test başlat
print("=" * 60)
print("TIME GRAPH WIDGET - PERFORMANS TESTİ")
print("=" * 60)
print(f"Test Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Bellek takibi başlat
tracemalloc.start()
process = psutil.Process(os.getpid())

# Başlangıç metrikleri
start_time = time.time()
start_memory = process.memory_info().rss / 1024 / 1024  # MB

print(f"Başlangıç Bellek Kullanımı: {start_memory:.2f} MB")
print()

# PyQt5 import
print("1. PyQt5 modülleri yükleniyor...")
import_start = time.time()
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import_time = time.time() - import_start
print(f"   [OK] PyQt5 yuklendi: {import_time:.3f} saniye")

# Uygulama oluştur
print("\n2. QApplication oluşturuluyor...")
app_start = time.time()
app = QApplication(sys.argv)
app_time = time.time() - app_start
print(f"   [OK] QApplication oluşturuldu: {app_time:.3f} saniye")

# TimeGraphWidget import ve başlatma
print("\n3. TimeGraphWidget yükleniyor...")
widget_import_start = time.time()
from time_graph_widget import TimeGraphWidget
from src.graphics.loading_overlay import LoadingManager
widget_import_time = time.time() - widget_import_start
print(f"   [OK] TimeGraphWidget import edildi: {widget_import_time:.3f} saniye")

print("\n4. Widget başlatılıyor...")
widget_init_start = time.time()
loading_manager = LoadingManager(None)
widget = TimeGraphWidget(loading_manager=loading_manager)
widget_init_time = time.time() - widget_init_start
print(f"   [OK] Widget başlatıldı: {widget_init_time:.3f} saniye")

# Widget göster
print("\n5. Widget gösteriliyor...")
show_start = time.time()
widget.show()
app.processEvents()  # UI update
show_time = time.time() - show_start
print(f"   [OK] Widget gösterildi: {show_time:.3f} saniye")

# Veri yükleme testi
print("\n6. Test verisi yükleniyor...")
data_load_start = time.time()

try:
    import polars as pl
    
    # test_data.csv varsa onu kullan
    if os.path.exists('test_data.csv'):
        df = pl.read_csv('test_data.csv')
        print(f"   [OK] Test verisi okundu: {df.height} satır, {len(df.columns)} sütun")
        
        # Veri yükleme
        data_update_start = time.time()
        widget.update_data(df, time_column='time')
        
        # İşlemin bitmesini bekle (maksimum 10 saniye)
        max_wait = 10
        waited = 0
        while waited < max_wait:
            app.processEvents()
            if not hasattr(widget, 'processing_thread') or not widget.processing_thread or not widget.processing_thread.isRunning():
                break
            time.sleep(0.1)
            waited += 0.1
        
        data_update_time = time.time() - data_update_start
        print(f"   [OK] Veri yüklendi ve işlendi: {data_update_time:.3f} saniye")
    else:
        print("   [WARN] test_data.csv bulunamadı, veri yükleme testi atlandı")
        
except Exception as e:
    print(f"   [ERROR] Veri yükleme hatası: {e}")

data_load_time = time.time() - data_load_start

# Son bellek ölçümü
current_memory = process.memory_info().rss / 1024 / 1024  # MB
memory_increase = current_memory - start_memory

# Toplam süre
total_time = time.time() - start_time

# Tracemalloc istatistikleri
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print("\n" + "=" * 60)
print("PERFORMANS SONUÇLARI")
print("=" * 60)

results = {
    "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "timings": {
        "pyqt5_import": f"{import_time:.3f}s",
        "qapplication_init": f"{app_time:.3f}s",
        "widget_import": f"{widget_import_time:.3f}s",
        "widget_init": f"{widget_init_time:.3f}s",
        "widget_show": f"{show_time:.3f}s",
        "data_load": f"{data_load_time:.3f}s",
        "total": f"{total_time:.3f}s"
    },
    "memory": {
        "start_mb": f"{start_memory:.2f}",
        "end_mb": f"{current_memory:.2f}",
        "increase_mb": f"{memory_increase:.2f}",
        "peak_mb": f"{peak / 1024 / 1024:.2f}"
    },
    "system": {
        "cpu_count": psutil.cpu_count(),
        "total_ram_gb": f"{psutil.virtual_memory().total / 1024 / 1024 / 1024:.2f}"
    }
}

# Sonuçları yazdır
print("\n[ZAMANLAMA]:")
print(f"  - PyQt5 Import     : {import_time:.3f} saniye")
print(f"  - QApplication     : {app_time:.3f} saniye")
print(f"  - Widget Import    : {widget_import_time:.3f} saniye")
print(f"  - Widget Init      : {widget_init_time:.3f} saniye")
print(f"  - Widget Show      : {show_time:.3f} saniye")
print(f"  - Data Load        : {data_load_time:.3f} saniye")
print(f"  - TOPLAM           : {total_time:.3f} saniye")

print("\n[BELLEK]:")
print(f"  - Başlangıç        : {start_memory:.2f} MB")
print(f"  - Son              : {current_memory:.2f} MB")
print(f"  - Artış            : {memory_increase:.2f} MB")
print(f"  - Peak (tracemalloc): {peak / 1024 / 1024:.2f} MB")

print("\n[SISTEM]:")
print(f"  - CPU Çekirdek     : {psutil.cpu_count()}")
print(f"  - Toplam RAM       : {psutil.virtual_memory().total / 1024 / 1024 / 1024:.2f} GB")

# Değerlendirme
print("\n[DEGERLENDIRME]:")
if total_time < 3:
    print("  [MUKEMMEL] - Cok hizli baslatma!")
elif total_time < 5:
    print("  [IYI] - Kabul edilebilir baslatma suresi")
elif total_time < 8:
    print("  [ORTA] - Iyilestirilebilir")
else:
    print("  ❌ Yavaş - Optimizasyon gerekli")

if memory_increase < 100:
    print("  ✅ Bellek kullanımı iyi")
elif memory_increase < 200:
    print("  ⚠️  Bellek kullanımı orta")
else:
    print("  ❌ Yüksek bellek kullanımı - Optimizasyon gerekli")

# Sonuçları JSON'a kaydet
output_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n💾 Detaylı rapor kaydedildi: {output_file}")

print("\n" + "=" * 60)
print("Test tamamlandı. Pencereyi kapatabilirsiniz.")
print("=" * 60)

# Cleanup
try:
    widget.cleanup()
except:
    pass

sys.exit(0)

