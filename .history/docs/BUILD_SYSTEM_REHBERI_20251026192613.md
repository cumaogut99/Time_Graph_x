# 🔧 Gelişmiş Build Sistemi Rehberi

## HTML → PDF Workflow

Artık daha esnek ve hızlı bir build sisteminiz var!

---

## 📊 Workflow Karşılaştırması

### ❌ Eski Yöntem (Direkt PDF)
```
Markdown → PDF (Pandoc + LaTeX)
- Yavaş (30-60 saniye)
- Hata yapma olasılığı yüksek
- Düzenleme zor
- LaTeX hatası = başa dön
```

### ✅ Yeni Yöntem (HTML → PDF)
```
Markdown → HTML → PDF
- Hızlı HTML (3-5 saniye)
- Tarayıcıda önizleme
- Düzenleme kolay
- Çoklu PDF motoru desteği
- Hata ayıklama kolay
```

---

## 🚀 Build Script'leri

### 1. `build_html.bat` - HTML Oluşturma

**Ne Yapar:**
- Markdown'ı HTML'e dönüştürür
- CSS stil dosyası uygular
- İçindekiler oluşturur
- Tarayıcıda görüntülenebilir

**Kullanım:**
```cmd
build_html.bat
```

**Çıktı:**
- `KULLANIM_KLAVUZU_TR.html` (ana klasörde)
- Tarayıcıda açılabilir

**Ne Zaman Kullanmalı:**
- ✅ Hızlı önizleme istediğinizde
- ✅ Düzenleme yaparken kontrol için
- ✅ Web'de paylaşmak istediğinizde
- ✅ PDF'e geçmeden önce kontrol

---

### 2. `build_pdf_from_html.bat` - HTML'den PDF

**Ne Yapar:**
- Mevcut HTML'i PDF'e dönüştürür
- 3 farklı PDF motoru destekler
- En iyisini otomatik seçer

**PDF Motorları (Öncelik Sırasıyla):**

#### 1. WeasyPrint (En İyi - Önerilen)
```bash
# Kurulum
pip install weasyprint

# Özellikler
✅ En iyi HTML/CSS desteği
✅ Yüksek kalite
✅ Hızlı
✅ CSS print media desteği
✅ Sayfa kesme kontrolü
```

#### 2. wkhtmltopdf (İyi)
```bash
# Kurulum
# İndirin: https://wkhtmltopdf.org/downloads.html
# Windows installer çalıştırın

# Özellikler
✅ Kolay kurulum
✅ İyi kalite
✅ Hızlı
⚠️ Bazı CSS özelliklerinde sınırlı
```

#### 3. Pandoc + LaTeX (Fallback)
```bash
# Zaten kurulu (build_manual.bat)

# Özellikler
✅ Her zaman çalışır
⚠️ Yavaş
⚠️ HTML avantajlarını kaybeder
```

**Kullanım:**
```cmd
# Once HTML oluştur
build_html.bat

# Sonra PDF'e çevir
build_pdf_from_html.bat
```

---

### 3. `build_all.bat` - Tek Seferde Her Şey

**Ne Yapar:**
- HTML oluşturur
- PDF oluşturur
- Dağıtım paketi hazırlar
- ZIP arşivi oluşturur (opsiyonel)

**Kullanım:**
```cmd
build_all.bat
```

**Çıktı Klasör Yapısı:**
```
dist/
├── KULLANIM_KLAVUZU_TR.html     # Web versiyonu
├── KULLANIM_KLAVUZU_TR.pdf      # PDF versiyonu
├── KULLANIM_KLAVUZU_TR.md       # Kaynak
├── docs/
│   └── manual_style.css         # Stil dosyası
├── screenshots/                  # Görseller
│   ├── 01_splash_screen.png
│   ├── 02_main_window.png
│   └── ...
└── README.txt                    # Bilgi dosyası

+ TimeGraphX_Manual_v1.0_YYYYMMDD.zip  (Opsiyonel)
```

---

## 🎨 CSS Özelleştirme

### Style Dosyası: `docs/manual_style.css`

**Renk Değişkenleri:**
```css
:root {
  --primary-color: #2563eb;      /* Ana renk */
  --secondary-color: #1e40af;    /* İkincil renk */
  --success-color: #16a34a;      /* Başarı mesajları */
  --warning-color: #f59e0b;      /* Uyarılar */
  --danger-color: #dc2626;       /* Hatalar */
}
```

**Özelleştirme Örneği:**
```css
/* Koyu tema için */
:root {
  --bg-color: #1f2937;
  --text-color: #f9fafb;
  --primary-color: #3b82f6;
}
```

---

## 📝 HTML Avantajları

### 1. Hızlı Önizleme
```cmd
build_html.bat
start KULLANIM_KLAVUZU_TR.html
# 5 saniyede tarayıcıda görüntüle
```

### 2. Canlı Düzenleme
```
1. Markdown'da değişiklik yap
2. build_html.bat çalıştır
3. Tarayıcıda F5 (yenile)
4. Değişikliği gör
```

### 3. Web'de Paylaşım
```
HTML dosyasını web sunucusuna yükle
Doğrudan tarayıcıda görüntülenebilir
PDF indirme gereği yok
```

### 4. Responsive (Mobil Uyumlu)
```css
/* CSS'de zaten var */
@media (max-width: 768px) {
  /* Mobil düzeni */
}
```

### 5. Arama Yapılabilir
```
Ctrl+F ile kelime ara
PDF'den daha hızlı
```

### 6. Linkler Çalışır
```html
<!-- İçindekiler linkleri -->
<a href="#section-3">Bölüm 3'e git</a>
<!-- Anında atlama -->
```

---

## 🔄 Önerilen Workflow

### Geliştirme Aşaması

```cmd
# 1. Değişiklikleri yap
notepad KULLANIM_KLAVUZU_TR.md

# 2. HTML'e çevir (hızlı önizleme)
build_html.bat

# 3. Tarayıcıda kontrol et
start KULLANIM_KLAVUZU_TR.html

# 4. Düzeltmeler yap, tekrar et
# Döngü: 2-3 saniye
```

### Final Aşaması

```cmd
# 1. Son kontroller
build_html.bat
# Tarayıcıda son kontrol

# 2. PDF oluştur
build_pdf_from_html.bat

# 3. Dağıtım paketi
build_all.bat

# 4. Test et
start dist\KULLANIM_KLAVUZU_TR.pdf
```

---

## 🛠️ WeasyPrint Kurulumu (Önerilen)

### Windows

```bash
# 1. Python yüklü mü kontrol et
python --version

# 2. WeasyPrint kur
pip install weasyprint

# 3. Test et
weasyprint --version
```

**Olası Sorunlar:**

**GTK3 Runtime eksik:**
```bash
# Hata mesajı
"GTK3 runtime not found"

# Çözüm
# İndirin: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
# gtk3-runtime-x.x.x-x-x-x-ts-win64.exe yükleyin
```

**Cairo eksik:**
```bash
# WeasyPrint kurulumu zaten dahil eder
# Sorun devam ederse:
pip install --upgrade weasyprint
```

---

## 📊 Performans Karşılaştırması

### Markdown → PDF (Eski)
```
Zaman: 30-60 saniye
CPU: Yüksek (LaTeX)
Hata Olasılığı: Orta
Düzenleme Döngüsü: Yavaş
```

### Markdown → HTML (Yeni)
```
Zaman: 3-5 saniye
CPU: Düşük
Hata Olasılığı: Çok düşük
Düzenleme Döngüsü: Çok hızlı
```

### HTML → PDF (WeasyPrint)
```
Zaman: 5-10 saniye
CPU: Orta
Hata Olasılığı: Düşük
Kalite: Yüksek
```

**Toplam:**
- Eski yöntem: 30-60 saniye
- Yeni yöntem: 8-15 saniye
- **İyileştirme: 4-6x daha hızlı**

---

## 🐛 Sorun Giderme

### HTML oluşturulamıyor

**Hata:** "pandoc: command not found"
```bash
# Çözüm
# Pandoc yükle: https://pandoc.org/
# Terminal'i yeniden başlat
```

**Hata:** "CSS dosyası bulunamadı"
```bash
# Sorun değil, varsayılan stil kullanılır
# İsterseniz:
# docs/manual_style.css oluşturun
```

### PDF oluşturulamıyor

**Hata:** "WeasyPrint not found"
```bash
# Çözüm
pip install weasyprint
# veya
# wkhtmltopdf yükle
```

**Hata:** "Görseller görünmüyor"
```bash
# Sebep: Görseller screenshots/ klasöründe yok
# Çözüm:
# 1. Screenshot'ları çek
# 2. docs/SCREENSHOT_CHECKLIST.md kullan
```

### HTML'de Türkçe karakterler bozuk

**Sebep:** Markdown UTF-8 değil
```bash
# Çözüm
# Markdown'ı UTF-8 ile kaydet
# VSCode/Notepad: Encoding → UTF-8
```

---

## 🎯 En İyi Pratikler

### 1. Her Zaman HTML ile Başla
```cmd
# ❌ Kötü
build_manual.bat  # Direkt PDF (yavaş)

# ✅ İyi
build_html.bat    # Önce HTML (hızlı önizleme)
# Kontrol et
build_pdf_from_html.bat  # Sonra PDF
```

### 2. Incremental Development
```cmd
# Küçük değişiklikler yap
# Her seferinde HTML oluştur
# Hata varsa hemen gör
# PDF'i en son yap
```

### 3. Version Control
```bash
# Git'e commit yapmadan önce
build_all.bat
# Son versiyonu test et
# Her şey OK ise commit
```

### 4. Dağıtım Öncesi
```cmd
# 1. HTML oluştur, tarayıcıda kontrol et
build_html.bat

# 2. PDF oluştur, Adobe Reader'da kontrol et
build_pdf_from_html.bat

# 3. Her ikisi de OK ise dağıtım paketi
build_all.bat

# 4. ZIP oluştur, test et
```

---

## 📦 Dağıtım Senaryoları

### Senaryo 1: Sadece PDF
```cmd
build_pdf_from_html.bat
# KULLANIM_KLAVUZU_TR.pdf paylaş
```

### Senaryo 2: Web ve PDF
```cmd
build_all.bat
# dist/ klasörünü web'e yükle
# HTML: Online görüntüleme
# PDF: İndirme linki
```

### Senaryo 3: Offline Paket
```cmd
build_all.bat
# ZIP oluştur
# TimeGraphX_Manual_v1.0.zip paylaş
# İçinde hem HTML hem PDF
```

### Senaryo 4: Kullanıcı Dökümantasyonu
```
dist/
├── KULLANIM_KLAVUZU_TR.pdf   # Ana klavuz
├── QUICK_START.pdf            # Hızlı başlangıç (ayrı belge)
└── FAQ.pdf                    # SSS (ayrı belge)
```

---

## 🔮 Gelecek İyileştirmeler

### 1. Canlı Reload
```bash
# Markdown değiştiğinde otomatik HTML oluştur
# Browser-sync ile canlı önizleme
npm install -g browser-sync
browser-sync start --server --files "KULLANIM_KLAVUZU_TR.html"
```

### 2. Çoklu Dil
```
build_all.bat --lang=en  # İngilizce
build_all.bat --lang=tr  # Türkçe
build_all.bat --lang=de  # Almanca
```

### 3. Interaktif HTML
```html
<!-- Tıklanabilir demo'lar -->
<button onclick="showDemo()">Demo Göster</button>
```

### 4. Video Embed
```html
<!-- YouTube entegrasyonu -->
<iframe src="tutorial_video"></iframe>
```

---

## 📞 Yardım

**Build sistemi sorunu:**
- Script'leri kontrol et
- Log dosyalarına bak
- Pandoc versiyonu: `pandoc --version`

**PDF kalite sorunu:**
- WeasyPrint kullandığınızdan emin olun
- CSS'i optimize edin
- Görselleri yüksek çözünürlükte tutun

---

**Başarılar! 🚀**

HTML → PDF workflow ile çok daha hızlı ve esnek bir sistem kazandınız.

