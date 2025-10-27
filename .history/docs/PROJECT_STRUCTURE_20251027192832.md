# Time Graph X - Proje Yapısı

**Son Güncelleme:** 2025-01-27  
**Versiyon:** 1.0

---

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Klasör Yapısı Ağacı](#klasör-yapısı-ağacı)
3. [Dosya Organizasyonu](#dosya-organizasyonu)
4. [Modül Açıklamaları](#modül-açıklamaları)
5. [Yeni Dosya Ekleme Rehberi](#yeni-dosya-ekleme-rehberi)
6. [Temizlik Önerileri](#temizlik-önerileri)

---

## 🎯 Genel Bakış

### Proje Durumu
- **Ana Widget:** `time_graph_widget.py` (1671 satır) - Monolitik
- **Toplam Modül:** ~50+ dosya
- **Organizasyon:** Orta düzeyde modüler

### Organizasyon Prensibi

```
📦 Kod Tabanı
├── 🎯 Ana Uygulama (app.py, time_graph_widget.py)
├── 📁 src/ - Modüler kodlar
│   ├── data/ - Veri işleme
│   ├── graphics/ - Görselleştirme
│   ├── managers/ - İş mantığı
│   ├── ui/ - Kullanıcı arayüzü
│   └── utils/ - Yardımcı araçlar
├── 📚 docs/ - Dokümantasyon
├── 🧪 tests/ - Test dosyaları
└── 🛠️ tools/ - Yardımcı araçlar
```

---

## 📂 Klasör Yapısı Ağacı

### Tam Proje Ağacı

```
time_graph_x/
│
├── 📄 app.py                          # Ana uygulama giriş noktası (1671 satır)
├── 📄 time_graph_widget.py            # Ana widget - MONOLİTİK (1671 satır) ⚠️
├── 📄 requirements.txt                 # Python bağımlılıkları
├── 📄 time_graph_app.spec             # PyInstaller config
├── 📄 __init__.py
│
├── 📁 src/                            # 🎯 MODÜLER KOD TABANI
│   ├── 📄 __init__.py
│   │
│   ├── 📁 data/                       # Veri İşleme Modülleri
│   │   ├── 📄 __init__.py
│   │   ├── 📄 data_cache_manager.py   # Parquet cache yönetimi
│   │   ├── 📄 data_import_dialog.py   # Import UI dialog
│   │   ├── 📄 data_loader.py          # Veri yükleme
│   │   ├── 📄 data_validator.py       # Veri doğrulama
│   │   └── 📄 signal_processor.py     # Sinyal işleme
│   │
│   ├── 📁 graphics/                   # Görselleştirme Modülleri
│   │   ├── 📄 __init__.py
│   │   ├── 📄 graph_container.py      # Grafik container yönetimi
│   │   ├── 📄 graph_renderer.py       # Grafik çizim
│   │   ├── 📄 loading_overlay.py      # Yükleme animasyonu
│   │   └── 📄 Engine Animation.json   # Animasyon config
│   │
│   ├── 📁 managers/                   # İş Mantığı Yöneticileri (17 dosya)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 bitmask_panel_manager.py         # Bitmask analizi
│   │   ├── 📄 control_panel_manager.py         # Kontrol paneli
│   │   ├── 📄 correlations_panel_manager.py    # Korelasyon analizi
│   │   ├── 📄 cursor_manager.py                # Cursor yönetimi
│   │   ├── 📄 data_manager.py                  # Veri yönetimi
│   │   ├── 📄 filter_manager.py                # Filtreleme yönetimi ⭐
│   │   ├── 📄 graph_settings_panel_manager.py  # Grafik ayarları
│   │   ├── 📄 legend_manager.py                # Legend yönetimi
│   │   ├── 📄 multi_file_manager.py            # Çoklu dosya yönetimi ⭐
│   │   ├── 📄 plot_manager.py                  # Plot yönetimi
│   │   ├── 📄 project_file_manager.py          # .mpai dosya yönetimi
│   │   ├── 📄 settings_panel_manager.py        # Ayarlar paneli
│   │   ├── 📄 statistics_settings_panel_manager.py  # İstatistik ayarları
│   │   ├── 📄 status_bar_manager.py            # Durum çubuğu
│   │   ├── 📄 theme_manager.py                 # Tema yönetimi
│   │   ├── 📄 toolbar_manager.py               # Araç çubuğu
│   │   └── 📄 widget_container_manager.py      # Widget container
│   │
│   ├── 📁 ui/                         # UI Bileşenleri (8 dosya)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 basic_deviation_panel.py         # Temel sapma paneli
│   │   ├── 📄 deviation_panel.py               # Gelişmiş sapma paneli
│   │   ├── 📄 graph_advanced_settings_dialog.py # Grafik ayarları dialog ⭐
│   │   ├── 📄 graph_settings_dialog.py         # Grafik ayarları
│   │   ├── 📄 parameter_filters_panel.py       # Parametre filtreleri
│   │   ├── 📄 parameters_panel.py              # Parametreler paneli
│   │   ├── 📄 static_limits_panel.py           # Statik limitler
│   │   └── 📄 statistics_panel.py              # İstatistik paneli
│   │
│   └── 📁 utils/                      # Yardımcı Araçlar (7 dosya)
│       ├── 📄 __init__.py
│       ├── 📄 advanced_logger.py               # Gelişmiş loglama
│       ├── 📄 error_handler.py                 # Hata yönetimi
│       ├── 📄 error_reporter.py                # Hata raporlama
│       ├── 📄 feature_stability_tracker.py     # Özellik stabilite takibi
│       ├── 📄 license_manager.py               # Lisans yönetimi (hazır)
│       ├── 📄 production_logger.py             # Production logging
│       └── 📄 pyqtgraph_patch.py               # PyQtGraph düzeltmeleri
│
├── 📁 docs/                           # 📚 DOKÜMANTASYON
│   ├── 📄 ROADMAP.md                  # ⭐ YOL HARİTASI (Ana doküman)
│   ├── 📄 FEATURE_DEFINITIONS.md      # ⭐ ÖZELLİK TANIMLARI
│   ├── 📄 README_DOCS.md              # ⭐ DOKÜMAN REHBERİ
│   ├── 📄 README.md                   # Ana README
│   ├── 📄 README_USER.md              # Kullanıcı README
│   ├── 📄 KULLANIM_KLAVUZU.md         # Kullanım kılavuzu
│   │
│   ├── 📄 BUILD_SYSTEM_REHBERI.md     # Build sistemi
│   ├── 📄 PDF_OLUSTURMA_KILAVUZU.md   # PDF oluşturma
│   ├── 📄 SCREENSHOT_CHECKLIST.md     # Ekran görüntüleri
│   ├── 📄 GORSEL_EKLEME_REHBERI.md    # Görsel ekleme
│   │
│   ├── 📄 CRITICAL_BUG_FIXES_REPORT.md      # 📦 Arşiv
│   ├── 📄 FILTER_LIMIT_BUG_FIXES.md         # 📦 Arşiv
│   ├── 📄 DEBUG_FILTER_ISSUE.md             # 📦 Arşiv
│   ├── 📄 DEBUG_CLEANUP_REPORT.md           # 📦 Arşiv
│   ├── 📄 PROFESSIONAL_IMPROVEMENTS_SUMMARY.md  # 📦 Arşiv
│   ├── 📄 QTHREAD_FIX_SUMMARY.md            # 📦 Arşiv
│   ├── 📄 PERFORMANCE_LOG_CLEANUP.md        # 📦 Arşiv
│   ├── 📄 DPI_SOLUTION_EXPLANATION.md       # Referans
│   │
│   └── 📄 manual_style.css            # HTML stil dosyası
│
├── 📁 tests/                          # 🧪 TEST DOSYALARI
│   ├── 📄 offline_diagnostics.py      # Offline test
│   ├── 📄 offline_test_tools.py       # Test araçları
│   ├── 📄 performance_test.py         # Performans testleri
│   ├── 📄 quick_health_check.py       # Hızlı sağlık kontrolü
│   ├── 📄 regression_tester.py        # Regresyon testleri
│   ├── 📄 test_data.py                # Test veri oluşturucu
│   ├── 📄 test_dpi_pyqt5.py          # DPI testleri
│   ├── 📄 test_dpi_pyside6.py        # DPI testleri
│   ├── 📄 test_dpi_scaling.py        # DPI testleri
│   ├── 📄 test_features_simple.py    # Özellik testleri
│   ├── 📄 test_filters_diagnostic.py # Filtre testleri
│   ├── 📄 test_framework.py          # Test framework
│   ├── 📄 test_performance_improvements.py
│   └── 📄 README_DPI_TESTS.md        # Test dokümantasyonu
│
├── 📁 Test_Files/                     # 📊 TEST VERİ DOSYALARI
│   ├── 📄 README_TEST_FILES.md        # Test dosyaları açıklaması
│   ├── 📄 test_data.csv               # Temel test verisi
│   ├── 📄 test_1_mixed_types.csv      # Karışık tipler
│   ├── 📄 test_2_null_heavy.csv       # Yoğun NULL
│   ├── 📄 test_3_millisecond_timestamp.csv
│   ├── 📄 test_4_datetime_strings.csv
│   ├── 📄 test_5_inconsistent_columns.csv
│   ├── 📄 test_6_special_characters.csv
│   ├── 📄 test_7_extreme_values.csv
│   ├── 📄 test_8_all_null_column.csv
│   ├── 📄 test_9_semicolon_delimiter.csv
│   ├── 📄 test_10_constant_values.csv
│   ├── 📄 test_date_only.csv
│   ├── 📄 test_datetime_custom.csv
│   ├── 📄 test_datetime_custom_fixed.csv
│   ├── 📄 test_datetime_iso.csv
│   ├── 📄 sample_limits.xlsx          # Örnek limitler
│   └── 📄 sample_limits_try.xlsx
│
├── 📁 tools/                          # 🛠️ YARDIMCI ARAÇLAR
│   ├── 📄 build_exe.py                # EXE oluşturucu
│   ├── 📄 convert_icon.py             # İkon dönüştürücü
│   ├── 📄 create_release.py           # Release oluşturucu
│   ├── 📄 create_sample_limits.py     # Örnek limit oluşturucu
│   ├── 📄 integration_guide.py        # Entegrasyon rehberi
│   └── 📄 quick_integration.py        # Hızlı entegrasyon
│
├── 📁 hazir/                          # 🎨 ÖRNEK DOSYALAR
│   ├── 📄 test_data.csv               # Test verisi
│   ├── 📄 test_data.mpai              # MPAI proje
│   ├── 📄 test_data2.mpai
│   ├── 📄 motor_test_data_350col.csv  # Büyük test
│   ├── 📄 motor_test_data_350col.mpai
│   ├── 📄 sensor_data_with_bitmask.csv # Bitmask örneği
│   ├── 📄 bitmask.xlsx                # Bitmask Excel
│   ├── 📄 deneme.csv
│   ├── 📄 deneme2.csv
│   ├── 📄 layout.json                 # Layout örnekleri
│   ├── 📄 layout2.json
│   └── 📄 generate_motor_data.py      # Veri oluşturucu
│
├── 📁 icons/                          # 🎨 İKONLAR
│   ├── 📄 arrow-down.svg
│   ├── 📄 arrow-up.svg
│   ├── 📄 ikon.ico                    # Uygulama ikonu
│   └── 📄 ikon.png
│
├── 📁 Screenshot/                     # 📸 EKRAN GÖRÜNTÜLERİ
│   ├── 📄 tga_1.png
│   ├── 📄 tga_2.png
│   ├── ... (15 ekran görüntüsü)
│   └── 📄 tga14_2.png
│
├── 📁 health_data/                    # 💊 SAĞLIK KONTROL DOSYALARI
│   ├── 📄 health_issues.json
│   └── 📄 health_metrics.json
│
├── 📁 testsprite_tests/               # 🧪 TESTSPRITE TESTLERI
│   └── 📁 tmp/
│       ├── 📄 code_summary.json
│       └── 📁 prd_files/
│           └── 📄 time_graph_requirements.md  # PRD dokümanı
│
├── 📁 _archive/                       # 📦 ARŞİV (eski dosyalar)
│
├── 📁 __pycache__/                    # Python cache (ignore)
│
├── 📄 KULLANIM_KLAVUZU_TR.md          # Türkçe kullanım kılavuzu
├── 📄 KULLANIM_KLAVUZU_TR.html        # HTML kullanım kılavuzu
├── 📄 markdown_to_html.py             # MD → HTML dönüştürücü
├── 📄 app.py.broken_backup            # Backup dosyası ⚠️
└── 📄 time_graph_app.log              # Log dosyası (runtime)
```

---

## 📊 Dosya Organizasyonu

### Ana Dosyalar

| Dosya | Satır | Durum | Açıklama |
|-------|-------|-------|----------|
| `app.py` | ~1671 | ✅ Aktif | Ana uygulama entry point |
| `time_graph_widget.py` | ~1671 | ⚠️ Monolitik | Ana widget - GENİŞLETİLMEMELİ |
| `requirements.txt` | ~20 | ✅ Güncel | Python bağımlılıkları |

### src/ Modül Sayıları

| Klasör | Dosya Sayısı | Durum | Açıklama |
|--------|--------------|-------|----------|
| `data/` | 5 | ✅ İyi | Veri işleme modülleri |
| `graphics/` | 3 | ✅ İyi | Görselleştirme |
| `managers/` | 17 | ⚠️ Çok | İş mantığı yöneticileri |
| `ui/` | 8 | ✅ İyi | UI bileşenleri |
| `utils/` | 7 | ✅ İyi | Yardımcı araçlar |

**Toplam:** ~40 modül dosyası

### docs/ Doküman Durumu

| Doküman | Durum | Kullanım |
|---------|-------|----------|
| `ROADMAP.md` | ✅ Aktif | Ana yol haritası |
| `FEATURE_DEFINITIONS.md` | ✅ Aktif | Özellik tanımları |
| `README_DOCS.md` | ✅ Aktif | Doküman rehberi |
| `KULLANIM_KLAVUZU.md` | ✅ Aktif | Kullanıcı kılavuzu |
| `*_BUG_FIXES_*.md` | 📦 Arşiv | Referans için |
| `*_SUMMARY.md` | 📦 Arşiv | Referans için |

---

## 🎯 Modül Açıklamaları

### src/data/ - Veri İşleme

```python
data/
├── data_cache_manager.py      # Parquet cache yönetimi
│   └── ParquetCacheManager    # 8-27x hızlı yükleme
│
├── data_import_dialog.py      # Import UI
│   └── DataImportDialog       # CSV/Excel import dialog
│
├── data_loader.py             # Veri yükleme
│   └── DataLoader             # Thread-safe veri yükleme
│
├── data_validator.py          # Veri doğrulama
│   └── DataValidator          # NULL, type validation
│
└── signal_processor.py        # Sinyal işleme
    └── SignalProcessor        # Filtreleme, normalizasyon
```

**Kullanım:**
- Veri yükleme: `DataLoader`
- Veri doğrulama: `DataValidator`
- Cache yönetimi: `ParquetCacheManager`

### src/graphics/ - Görselleştirme

```python
graphics/
├── graph_container.py         # Grafik container
│   └── GraphContainer         # Multi-graph layout yönetimi
│
├── graph_renderer.py          # Grafik çizimi
│   └── GraphRenderer          # PyQtGraph rendering
│
└── loading_overlay.py         # Yükleme animasyonu
    └── LoadingManager         # Splash screen, overlay
```

**Kullanım:**
- Grafik oluşturma: `GraphContainer`
- Grafik çizimi: `GraphRenderer`
- Yükleme animasyonu: `LoadingManager`

### src/managers/ - İş Mantığı Yöneticileri

```python
managers/
├── 🔥 filter_manager.py              # Filtreleme mantığı
│   └── FilterManager                 # Range, segment filtreleme
│
├── 🔥 multi_file_manager.py          # Çoklu dosya
│   └── MultiFileManager              # 3 dosya yönetimi
│
├── cursor_manager.py                 # Cursor mantığı
│   └── CursorManager                 # Single, dual cursor
│
├── theme_manager.py                  # Tema
│   └── ThemeManager                  # Light, dark tema
│
├── legend_manager.py                 # Legend
│   └── LegendManager                 # Legend gösterimi
│
├── toolbar_manager.py                # Toolbar
│   └── ToolbarManager                # Araç çubuğu butonları
│
├── status_bar_manager.py             # Status bar
│   └── StatusBarManager              # Durum çubuğu, dosya sekmeleri
│
├── project_file_manager.py           # .mpai dosya
│   └── ProjectFileManager            # MPAI load/save
│
├── data_manager.py                   # Veri yönetimi
│   └── DataManager                   # Veri state yönetimi
│
├── plot_manager.py                   # Plot yönetimi
│   └── PlotManager                   # Plot işlemleri
│
├── bitmask_panel_manager.py          # Bitmask
│   └── BitmaskPanelManager           # Bitmask analizi
│
├── correlations_panel_manager.py     # Korelasyon
│   └── CorrelationsPanelManager      # Korelasyon hesaplama
│
├── control_panel_manager.py          # Kontrol paneli
│   └── ControlPanelManager           # Sol panel yönetimi
│
├── graph_settings_panel_manager.py   # Grafik ayarları
│   └── GraphSettingsPanelManager     # Grafik count, layout
│
├── settings_panel_manager.py         # Ayarlar
│   └── SettingsPanelManager          # Genel ayarlar
│
├── statistics_settings_panel_manager.py  # İstatistik ayarları
│   └── StatisticsSettingsPanelManager    # İstatistik seçenekleri
│
└── widget_container_manager.py       # Widget container
    └── WidgetContainerManager        # Container yönetimi
```

### src/ui/ - UI Bileşenleri

```python
ui/
├── 🔥 graph_advanced_settings_dialog.py  # Gelişmiş grafik ayarları
│   └── GraphAdvancedSettingsDialog       # Range filter, limits, deviation
│
├── graph_settings_dialog.py             # Grafik ayarları
│   └── GraphSettingsDialog               # Grafik sayısı, layout
│
├── parameters_panel.py                   # Parametreler paneli
│   └── ParametersPanel                   # Sinyal seçimi, renk
│
├── statistics_panel.py                   # İstatistik paneli
│   └── StatisticsPanel                   # Min, max, mean, RMS
│
├── parameter_filters_panel.py           # Filtre paneli
│   └── ParameterFiltersPanel             # Filtre UI
│
├── static_limits_panel.py               # Limit paneli
│   └── StaticLimitsPanel                 # Limit çizgileri
│
├── deviation_panel.py                    # Sapma paneli
│   └── DeviationPanel                    # Deviation analizi
│
└── basic_deviation_panel.py             # Basit sapma
    └── BasicDeviationPanel               # Temel deviation
```

### src/utils/ - Yardımcı Araçlar

```python
utils/
├── production_logger.py          # Production logging
│   └── ProductionLogger          # Rotating file handler
│
├── error_handler.py              # Hata yönetimi
│   └── ErrorHandler              # Exception handling
│
├── error_reporter.py             # Hata raporlama
│   └── ErrorReporter             # Crash report oluşturma
│
├── advanced_logger.py            # Gelişmiş logging
│   └── AdvancedLogger            # Debug, info, warning
│
├── license_manager.py            # Lisans yönetimi (hazır)
│   └── LicenseManager            # Trial, activation
│
├── feature_stability_tracker.py  # Stabilite takibi
│   └── FeatureStabilityTracker   # Özellik kararlılık ölçümü
│
└── pyqtgraph_patch.py            # PyQtGraph düzeltmeleri
    └── apply_pyqtgraph_patch()   # autoRangeEnabled fix
```

---

## 🆕 Yeni Dosya Ekleme Rehberi

### Yeni Özellik Eklerken

#### 1. Yeni Modül Oluşturma

**KURAL:** Mevcut dosyaları büyütme, yeni modül oluştur!

```bash
# Kötü ❌
time_graph_widget.py'ye 200 satır eklemek

# İyi ✅
src/features/export/export_manager.py (yeni dosya)
```

#### 2. Klasör Yapısı

```python
# Yeni özellik için klasör yapısı
src/
└── features/              # YENİ: Özellik modülleri
    ├── __init__.py
    │
    ├── streaming/         # Real-time streaming
    │   ├── __init__.py
    │   ├── socket_manager.py
    │   ├── buffer_manager.py
    │   └── streaming_ui.py
    │
    ├── export/            # Export geliştirmeleri
    │   ├── __init__.py
    │   ├── export_manager.py
    │   ├── png_exporter.py
    │   ├── pdf_exporter.py
    │   └── excel_reporter.py
    │
    └── plugins/           # Plugin sistemi
        ├── __init__.py
        ├── plugin_manager.py
        ├── plugin_loader.py
        └── plugin_api.py
```

#### 3. Dosya Boyutu Limitleri

| Dosya Tipi | Max Satır | Aksyon |
|-----------|-----------|--------|
| Widget/UI | 300 | Yeni modül oluştur |
| Manager | 500 | Yeni modül oluştur |
| Utility | 200 | Yeni modül oluştur |
| Ana dosya | Mevcut | YENİ KOD EKLEME! |

#### 4. Import Yapısı

```python
# time_graph_widget.py'de
from src.features.export.export_manager import ExportManager

class TimeGraphWidget:
    def __init__(self):
        # Yeni manager instance
        self.export_manager = ExportManager()
    
    def export_graph(self, format, filepath):
        # Sadece method call
        self.export_manager.export(format, filepath)
```

### Yeni Özellik Örnekleri

#### Örnek 1: Real-time Streaming Eklemek

```bash
# 1. Yeni klasör oluştur
mkdir -p src/features/streaming

# 2. Dosyalar oluştur
touch src/features/streaming/__init__.py
touch src/features/streaming/socket_manager.py
touch src/features/streaming/buffer_manager.py
touch src/features/streaming/streaming_ui.py

# 3. time_graph_widget.py'de sadece import ve method call
# ❌ time_graph_widget.py'ye 200 satır ekleme!
# ✅ src/features/streaming/socket_manager.py'ye kod yaz
```

#### Örnek 2: Export Manager Eklemek

```python
# src/features/export/export_manager.py
class ExportManager:
    """Export işlemlerini yönetir"""
    
    def __init__(self, widget):
        self.widget = widget
        self.png_exporter = PNGExporter()
        self.pdf_exporter = PDFExporter()
    
    def export(self, format, filepath):
        if format == 'png':
            self.png_exporter.export(self.widget, filepath)
        elif format == 'pdf':
            self.pdf_exporter.export(self.widget, filepath)
```

---

## 🧹 Temizlik Önerileri

### Silinebilir/Arşivlenebilir Dosyalar

#### 1. Root Klasörde

```bash
# ❌ Silinebilir
app.py.broken_backup          # Backup dosyası

# 📦 Arşivlenebilir
_archive/                      # Zaten arşiv klasöründe
```

#### 2. docs/ Klasöründe

```bash
# 📦 Arşive taşınabilir (bilgi referansı için)
docs/CRITICAL_BUG_FIXES_REPORT.md
docs/FILTER_LIMIT_BUG_FIXES.md
docs/DEBUG_FILTER_ISSUE.md
docs/DEBUG_CLEANUP_REPORT.md
docs/PROFESSIONAL_IMPROVEMENTS_SUMMARY.md
docs/QTHREAD_FIX_SUMMARY.md
docs/PERFORMANCE_LOG_CLEANUP.md

# Tavsiye: docs/_archive/ klasörüne taşı
mkdir -p docs/_archive/bug_reports/
mv docs/*BUG*.md docs/_archive/bug_reports/
mv docs/*DEBUG*.md docs/_archive/bug_reports/
mv docs/*SUMMARY.md docs/_archive/bug_reports/
```

#### 3. Test Dosyaları

```bash
# ✅ Tutulmalı (aktif testler)
tests/                         # Tüm test dosyaları
Test_Files/                    # Test veri dosyaları

# 🤔 Değerlendirilmeli
testsprite_tests/              # TestSprite çıktıları - gerekli mi?
health_data/                   # Sağlık kontrol - gerekli mi?
```

### Önerilen Klasör Yapısı (Temizlenmiş)

```
time_graph_x/
├── app.py
├── time_graph_widget.py
├── requirements.txt
├── time_graph_app.spec
│
├── src/                       # Modüler kodlar
│   ├── data/
│   ├── graphics/
│   ├── managers/
│   ├── ui/
│   ├── utils/
│   └── features/              # YENİ: Gelecek özellikler
│
├── docs/                      # Dokümantasyon
│   ├── ROADMAP.md             # ⭐ Ana doküman
│   ├── FEATURE_DEFINITIONS.md
│   ├── README_DOCS.md
│   ├── KULLANIM_KLAVUZU.md
│   ├── README.md
│   │
│   ├── guides/                # YENİ: Rehberler
│   │   ├── BUILD_SYSTEM_REHBERI.md
│   │   ├── PDF_OLUSTURMA_KILAVUZU.md
│   │   └── GORSEL_EKLEME_REHBERI.md
│   │
│   └── _archive/              # YENİ: Eski dokümanlar
│       ├── bug_reports/
│       └── old_docs/
│
├── tests/                     # Test dosyaları
├── Test_Files/                # Test veri dosyaları
├── tools/                     # Yardımcı araçlar
├── hazir/                     # Örnek dosyalar
├── icons/                     # İkonlar
└── Screenshot/                # Ekran görüntüleri
```

---

## 📝 Hızlı Referans

### Dosya Arama Kılavuzu

**"X özelliğini nerede bulabilirim?"**

| Özellik | Dosya/Klasör |
|---------|--------------|
| Veri yükleme | `src/data/data_loader.py` |
| CSV import dialog | `src/data/data_import_dialog.py` |
| Grafik çizimi | `src/graphics/graph_renderer.py` |
| Filtreleme mantığı | `src/managers/filter_manager.py` |
| Cursor işlemleri | `src/managers/cursor_manager.py` |
| Çoklu dosya yönetimi | `src/managers/multi_file_manager.py` |
| Grafik ayarları UI | `src/ui/graph_advanced_settings_dialog.py` |
| İstatistik paneli | `src/ui/statistics_panel.py` |
| Hata yönetimi | `src/utils/error_handler.py` |
| Logging | `src/utils/production_logger.py` |

### Yeni Özellik Nereye?

| Özellik Tipi | Klasör | Örnek |
|-------------|--------|-------|
| Veri işleme | `src/data/` | `data_transformer.py` |
| Görselleştirme | `src/graphics/` | `animation_manager.py` |
| İş mantığı | `src/managers/` | `calculation_manager.py` |
| UI bileşeni | `src/ui/` | `new_dialog.py` |
| Yardımcı | `src/utils/` | `math_utils.py` |
| Büyük özellik | `src/features/` | `streaming/` |

---

## 🎯 Sonuç

### Mevcut Durum
- ✅ Modüler yapı oluşturulmuş
- ⚠️ `time_graph_widget.py` çok büyük (1671 satır)
- ✅ Dokümantasyon organize
- ⚠️ Bazı eski dokümanlar temizlenmeli

### Öneriler
1. ✅ `src/features/` klasörü oluştur (yeni özellikler için)
2. ✅ Eski dokümanları `docs/_archive/` taşı
3. ✅ `time_graph_widget.py` GENİŞLETME, yeni modüller oluştur
4. ✅ Her yeni özellik için ROADMAP.md'yi güncelle

---

**Son Güncelleme:** 2025-01-27  
**Doküman Sahibi:** Development Team  
**İlgili Dokümanlar:** ROADMAP.md, FEATURE_DEFINITIONS.md, README_DOCS.md

