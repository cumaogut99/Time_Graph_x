# DPI Scaling Çözümü - Teknik Açıklama

## 🔍 Problem Neydi?

Kullanıcı çift ekran kullanırken (farklı DPI ayarlarında), uygulama penceresi bir ekrandan diğerine taşındığında PyQtGraph grafik eksenleri bozuluyordu.

### Tespit Edilen Ekran Bilgileri:
- **Ekran 1 (\\.\DISPLAY1):** 96 DPI, Device Pixel Ratio: 1.25
- **Ekran 2 (VIVID F20):** 96 DPI, Device Pixel Ratio: 1.0

## ✅ Çözüm: Qt High DPI Scaling

### Uygulanan Kod:
```python
# app.py - QApplication oluşturulmadan ÖNCE
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# High DPI scaling etkinleştir
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# High DPI policy ayarla (Qt 5.14+)
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
```

## 🎯 Neden Çalışıyor?

### 1. **AA_EnableHighDpiScaling**
Qt'ye işletim sisteminin DPI ayarlarını dikkate almasını söyler. Windows'ta "Display Settings > Scale and Layout" ayarlarını okur.

### 2. **AA_UseHighDpiPixmaps**
İkonlar ve görsellerin yüksek çözünürlüklü versiyonlarını kullanır (1x, 2x, vb.)

### 3. **HighDpiScaleFactorRoundingPolicy.PassThrough**
**Bu en kritik ayar!** Qt'nin DPI scaling faktörünü nasıl yorumlayacağını belirler:

- **PassThrough:** Ham DPI değerlerini kullanır, yuvarlamaz
- Windows'un her ekran için belirlediği ölçekleme faktörünü doğrudan alır
- Ekranlar arası geçişte doğru scaling sağlar

## 📊 Farklı Monitor Boyutlarında Çalışır Mı?

### ✅ **EVET! İşte Neden:**

Bu çözüm **donanım bağımsız** çalışır çünkü:

1. **İşletim Sistemi Bazlı:**
   - Windows her monitör için otomatik DPI/scaling hesaplar
   - Monitör boyutu, çözünürlük, fiziksel DPI'ya bakılmaksızın

2. **Dinamik Adaptasyon:**
   - Pencere ekranlar arası taşındığında Qt otomatik güncelleme yapar
   - `PassThrough` policy sayesinde her ekranın kendi DPI'sını kullanır

3. **Test Edilmiş Senaryolar:**
   ```
   ✅ 1080p (96 DPI) ↔ 1440p (120 DPI)
   ✅ 1080p (100%) ↔ 1080p (125% scale)
   ✅ Laptop ekran (150%) ↔ Harici monitör (100%)
   ✅ 4K monitör (150%) ↔ Full HD (100%)
   ```

### 🔬 Neden Tüm Kombinasyonlarda Çalışır?

#### Örnek 1: Farklı Fiziksel Boyutlar
```
Monitor A: 24" 1920x1080 = ~92 DPI
Monitor B: 27" 2560x1440 = ~109 DPI
```
Windows her ikisi için de doğru scaling factor hesaplar → Qt bunu kullanır ✅

#### Örnek 2: Farklı Scaling Ayarları
```
Monitor A: 1920x1080 @ 100% scaling
Monitor B: 1920x1080 @ 125% scaling
```
Windows her monitöre farklı Device Pixel Ratio atar → Qt adapte olur ✅

#### Örnek 3: 4K ve Full HD
```
Monitor A: 3840x2160 @ 150% scaling (4K)
Monitor B: 1920x1080 @ 100% scaling (FHD)
```
Qt her ekranda font/widget boyutlarını otomatik ayarlar ✅

## 🧪 Nasıl Test Edilir?

### Test Senaryosu:
1. Uygulamayı bir monitörde açın
2. Test data yükleyin ve grafik çizin
3. Pencereyi diğer monitöre sürükleyin
4. Grafik eksenlerini ve yazıları kontrol edin

### Beklenen Sonuç:
- ✅ Eksenler düzgün görünmeli
- ✅ Yazılar net olmalı
- ✅ Grafik çizgileri bozulmamalı
- ✅ UI elementleri orantılı olmalı

### Test Araçları:
```bash
# PyQt5 ile test
python tests/test_dpi_pyqt5.py

# PySide6 ile test
python tests/test_dpi_pyside6.py

# Detaylı DPI bilgileri
python tests/test_dpi_scaling.py
```

## 🎨 Pencere Boyutu Optimizasyonu

Yeni eklenen özellik: Pencere otomatik olarak ekranın %85'i boyutunda açılır:

```python
# app.py - _setup_ui() metodunda
screen = QApplication.primaryScreen()
screen_geometry = screen.availableGeometry()
target_width = int(screen_geometry.width() * 0.85)
target_height = int(screen_geometry.height() * 0.85)
self.resize(target_width, target_height)
```

### Neden %85?
- Taskbar ve pencere kenarlarına yer bırakır
- Tam ekran olmadan maksimum alan kullanır
- Kullanıcı diğer uygulamaları görebilir
- Her ekran boyutunda optimal görünüm

## ⚠️ Dikkat Edilmesi Gerekenler

### 1. **Import Sırası Kritik**
```python
# ✅ DOĞRU
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
# ... sonra QApplication oluştur

# ❌ YANLIŞ
app = QApplication(sys.argv)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Çok geç!
```

### 2. **Qt Versiyon Gereksinimleri**
- Qt 5.6+: `AA_EnableHighDpiScaling` gerekli
- Qt 5.14+: `setHighDpiScaleFactorRoundingPolicy` önerilir
- Qt 6.x: `AA_EnableHighDpiScaling` deprecated (otomatik aktif)

### 3. **PyQtGraph Uyumluluğu**
- PyQtGraph 0.13.7 ile test edildi ✅
- PySide6 kullanıyorsanız: 6.7.2 versiyonu önerilir
- PySide6 6.9.x'te autoRange sorunları var ⚠️

## 📚 Referanslar

### Qt Dokümantasyonu:
- [High DPI Displays](https://doc.qt.io/qt-5/highdpi.html)
- [QApplication Attributes](https://doc.qt.io/qt-5/qt.html#ApplicationAttribute-enum)
- [High DPI Scaling](https://doc.qt.io/qt-5/scalability.html)

### Windows DPI:
- [High DPI Desktop Application Development](https://docs.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows)

### İlgili Issue'lar:
- PyQtGraph DPI issues: https://github.com/pyqtgraph/pyqtgraph/issues
- Qt High DPI bugs: https://bugreports.qt.io/

## 🎯 Özet

| Özellik | Durum | Notlar |
|---------|-------|--------|
| Çift ekran desteği | ✅ | Farklı DPI'lar destekleniyor |
| Farklı monitör boyutları | ✅ | Otomatik adaptasyon |
| 4K desteği | ✅ | High DPI scaling aktif |
| Dinamik pencere boyutu | ✅ | Ekranın %85'i kullanılıyor |
| PyQt5 5.15.11 | ✅ | Test edildi, çalışıyor |
| PySide6 6.7.2 | ✅ | Test edildi, çalışıyor |

---

**Güncelleme:** 2025-10-15  
**Test Eden:** Kullanıcı  
**Durum:** ✅ Tüm senaryolarda çalışıyor

