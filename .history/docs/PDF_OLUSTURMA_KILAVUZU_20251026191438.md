# 📄 PDF Oluşturma Kılavuzu

Time Graph X kullanım kılavuzunu PDF'e dönüştürmek için bu rehberi takip edin.

---

## Hızlı Başlangıç

### Windows Kullanıcıları

**En Kolay Yol:**
```cmd
build_manual.bat
```

Bu script:
1. ✅ Gerekli araçları kontrol eder
2. ✅ PDF oluşturur
3. ✅ Otomatik açar

---

## Detaylı Kurulum

### Adım 1: Pandoc Kurulumu

**Pandoc Nedir?**
- Markdown'dan PDF'e dönüştürme aracı
- Açık kaynak ve ücretsiz

**Windows İçin:**
1. İndirin: https://pandoc.org/installing.html
2. Windows MSI installer'ı seçin
3. Kurulum sihirbazını takip edin
4. Varsayılan ayarlarla yükleyin

**Kurulum Kontrolü:**
```cmd
pandoc --version
```

Çıktı:
```
pandoc 3.1.9
...
```

### Adım 2: LaTeX Kurulumu (PDF için gerekli)

**MiKTeX (Önerilen):**
1. İndirin: https://miktex.org/download
2. Basic MiKTeX Installer'ı seçin (270 MB)
3. Yükleyin (varsayılan ayarlar yeterli)
4. İlk kullanımda eksik paketleri otomatik indirecek

**Kurulum Kontrolü:**
```cmd
xelatex --version
```

**Alternatif: TeX Live**
- Daha kapsamlı (4 GB)
- İndirin: https://www.tug.org/texlive/
- Tüm paketler dahil

---

## PDF Oluşturma Yöntemleri

### Yöntem 1: Basit Script (Önerilen)

**Kullanım:**
```cmd
build_manual.bat
```

**Ne Yapar?**
- Gerekli kontrolleri yapar
- PDF oluşturur
- Hata durumunda bilgi verir

**Çıktı:**
- `KULLANIM_KLAVUZU_TR.pdf` (ana klasörde)

---

### Yöntem 2: Gelişmiş Script

**Kullanım:**
```cmd
build_manual_advanced.bat
```

**Ekstra Özellikler:**
- ✅ Kapak sayfası
- ✅ Header/Footer (sayfa numaraları)
- ✅ Dağıtım paketi (dist/ klasörü)
- ✅ ZIP oluşturma
- ✅ README dosyası

**Çıktı:**
```
dist/
├── KULLANIM_KLAVUZU_TR.pdf
├── KULLANIM_KLAVUZU_TR.md
├── screenshots/
│   └── *.png
└── README.txt
```

---

### Yöntem 3: Manuel Komut

**Temel PDF:**
```cmd
pandoc KULLANIM_KLAVUZU_TR.md -o KULLANIM_KLAVUZU_TR.pdf --pdf-engine=xelatex
```

**İçindekiler ve Bölüm Numaraları:**
```cmd
pandoc KULLANIM_KLAVUZU_TR.md -o KULLANIM_KLAVUZU_TR.pdf ^
  --pdf-engine=xelatex ^
  --toc ^
  --toc-depth=2 ^
  --number-sections
```

**Gelişmiş (Tüm ayarlar):**
```cmd
pandoc KULLANIM_KLAVUZU_TR.md -o KULLANIM_KLAVUZU_TR.pdf ^
  --pdf-engine=xelatex ^
  --toc ^
  --toc-depth=2 ^
  --number-sections ^
  -V geometry:margin=2cm ^
  -V fontsize=11pt ^
  -V documentclass=report ^
  -V lang=tr-TR ^
  -V papersize=a4 ^
  -V linestretch=1.15 ^
  --highlight-style=tango
```

---

## Özelleştirme

### Sayfa Ayarları

**Margin (Kenar Boşluğu):**
```cmd
-V geometry:margin=2.5cm
```

**Kağıt Boyutu:**
```cmd
-V papersize=a4       # A4 (Avrupa)
-V papersize=letter   # Letter (ABD)
```

**Font Boyutu:**
```cmd
-V fontsize=10pt    # Küçük
-V fontsize=11pt    # Orta (önerilen)
-V fontsize=12pt    # Büyük
```

### İçindekiler (Table of Contents)

**İçindekiler ekle:**
```cmd
--toc
```

**Derinlik ayarı:**
```cmd
--toc-depth=2    # Sadece başlık ve alt başlık (H1, H2)
--toc-depth=3    # H3'e kadar
```

### Bölüm Numaralandırma

**Otomatik numaralandırma:**
```cmd
--number-sections
```

Sonuç:
```
1. Başlangıç
   1.1 Time Graph X Nedir?
   1.2 Ana Özellikler
2. İlk Adımlar
   2.1 Uygulama Başlatma
   ...
```

### Syntax Highlighting (Kod Blokları)

**Tema seçimi:**
```cmd
--highlight-style=tango        # Renkli, okunabilir (önerilen)
--highlight-style=kate         # Koyu arka plan
--highlight-style=espresso     # Kahverengi tonlar
--highlight-style=zenburn      # Gri tonlar
```

### Türkçe Karakter Desteği

**Mutlaka ekleyin:**
```cmd
-V lang=tr-TR
--pdf-engine=xelatex    # Unicode desteği için gerekli
```

---

## Kapak Sayfası Ekleme

### cover.md Dosyası

**Oluştur:**
```markdown
---
title: "Time Graph X"
subtitle: "Kullanım Kılavuzu"
author: "Time Graph X Development Team"
date: "Ekim 2025"
version: "v1.0.0"
---

\newpage
```

**Kullan:**
```cmd
pandoc cover.md KULLANIM_KLAVUZU_TR.md -o output.pdf --pdf-engine=xelatex
```

---

## Header ve Footer

### Pandoc YAML Ayarları

**header-footer.yaml:**
```yaml
header-includes: |
  \usepackage{fancyhdr}
  \pagestyle{fancy}
  \fancyhead[L]{Time Graph X}
  \fancyhead[R]{Kullanım Kılavuzu v1.0}
  \fancyfoot[C]{\thepage}
  \fancyfoot[L]{Copyright © 2025}
  \fancyfoot[R]{Sayfa \thepage}
```

**Kullanım:**
```cmd
pandoc KULLANIM_KLAVUZU_TR.md -o output.pdf ^
  --metadata-file=header-footer.yaml ^
  --pdf-engine=xelatex
```

---

## Görsel Ayarları

### Görsel Boyutu

**Markdown'da:**
```markdown
![Açıklama](path/to/image.png){width=80%}
```

**veya:**
```markdown
![Açıklama](path/to/image.png){height=400px}
```

### Görsel Pozisyonu

**LaTeX komutu:**
```markdown
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{screenshots/01_splash_screen.png}
\caption{Uygulama Başlangıç Ekranı}
\end{figure}
```

---

## Sorun Giderme

### Hata 1: "pandoc: command not found"

**Çözüm:**
1. Pandoc yüklü mü kontrol et: `pandoc --version`
2. Yüklü değilse: https://pandoc.org/installing.html
3. Yükledikten sonra yeni terminal aç

### Hata 2: "xelatex not found"

**Çözüm:**
1. MiKTeX veya TeX Live yükle
2. Yükleme sonrası terminal'i yeniden başlat
3. Kontrol: `xelatex --version`

### Hata 3: "Missing LaTeX packages"

**Çözüm (MiKTeX):**
```
MiKTeX Console → Settings → General
"Install missing packages on-the-fly" → Yes
```

**Manuel paket yükleme:**
```cmd
miktex packages install fancyhdr
miktex packages install graphicx
```

### Hata 4: "Image not found"

**Çözüm:**
1. Screenshot klasörü var mı? `screenshots/`
2. Dosya adları doğru mu? (01_*.png)
3. Markdown'da path doğru mu?

**Test:**
```cmd
dir screenshots
```

Görseller listesi görünmeli.

### Hata 5: "Türkçe karakterler bozuk"

**Çözüm:**
1. Markdown dosyası UTF-8 ile kaydedilmiş mi?
2. Pandoc komutunda `-V lang=tr-TR` var mı?
3. `--pdf-engine=xelatex` kullanılıyor mu?

**Not Defteri'nde UTF-8 kaydetme:**
```
Farklı Kaydet → Kodlama: UTF-8
```

### Hata 6: "PDF çok büyük"

**Çözüm:**
1. Görselleri sıkıştır:
   ```cmd
   # PNG optimize
   pngquant --quality=65-80 screenshots/*.png
   ```

2. Veya görselleri küçült:
   ```markdown
   ![](image.png){width=50%}
   ```

3. DPI azalt (150 DPI yeterli)

---

## Alternatif Araçlar

### 1. Typora (Kolay - WYSIWYG)

**Artıları:**
- ✅ Görsel arayüz
- ✅ Canlı önizleme
- ✅ Tek tıkla PDF

**Eksileri:**
- ❌ Ücretli ($14.99)

**Kullanım:**
1. Typora indir: https://typora.io/
2. KULLANIM_KLAVUZU_TR.md aç
3. File → Export → PDF

### 2. VSCode Extension

**Markdown PDF Extension:**
1. VSCode → Extensions
2. Ara: "Markdown PDF"
3. Yükle: yzane.markdown-pdf
4. Markdown dosyasını aç
5. Sağ tık → "Markdown PDF: Export (pdf)"

**Artıları:**
- ✅ VSCode'dan çıkmadan
- ✅ Ücretsiz

**Eksileri:**
- ❌ Sınırlı özelleştirme

### 3. Online Dönüştürücüler

**Web Siteleri:**
- https://www.markdowntopdf.com/
- https://md2pdf.netlify.app/
- https://dillinger.io/

**Kullanım:**
1. Markdown içeriğini kopyala
2. Web sitesine yapıştır
3. Convert → Download

**Artıları:**
- ✅ Kurulum yok
- ✅ Hızlı test için iyi

**Eksileri:**
- ❌ Görseller sorun olabilir
- ❌ Özelleştirme yok
- ❌ Büyük dosyalarda yavaş

---

## Best Practices

### PDF Kalitesi

**Önerilen Ayarlar:**
```cmd
pandoc KULLANIM_KLAVUZU_TR.md -o output.pdf ^
  --pdf-engine=xelatex ^
  --toc ^
  --toc-depth=2 ^
  --number-sections ^
  -V geometry:margin=2.5cm ^
  -V fontsize=11pt ^
  -V documentclass=report ^
  -V lang=tr-TR ^
  -V linestretch=1.2 ^
  --highlight-style=tango
```

**Sonuç:**
- Okunabilir kenar boşlukları (2.5cm)
- Uygun font boyutu (11pt)
- Rahat satır aralığı (1.2)
- Renkli kod blokları
- Türkçe karakter desteği

### Görsel Kalite

**Öneriler:**
- Format: PNG (JPG değil)
- DPI: 150 (print için)
- Genişlik: 1920px (Full HD)
- Boyutlandırma: {width=80%} (Markdown'da)

### Dosya Boyutu

**Hedef:** < 20 MB

**Büyükse:**
1. Görselleri optimize et (pngquant)
2. Gereksiz görselleri çıkar
3. Görselleri küçült (%50-80)

---

## Kontrol Listesi

### PDF Oluşturmadan Önce

- [ ] Pandoc yüklü (`pandoc --version`)
- [ ] LaTeX yüklü (`xelatex --version`)
- [ ] Screenshot klasörü mevcut
- [ ] 47 görsel eksiksiz
- [ ] Markdown dosyası UTF-8
- [ ] Görsel path'leri doğru

### PDF Oluşturduktan Sonra

- [ ] PDF açılıyor mu?
- [ ] İçindekiler çalışıyor mu?
- [ ] Tüm görseller görünüyor mu?
- [ ] Türkçe karakterler doğru mu?
- [ ] Sayfa numaraları var mı?
- [ ] Kod blokları renkli mi?
- [ ] Dosya boyutu makul mü? (< 50 MB)

### Dağıtımdan Önce

- [ ] PDF versiyonu doğru (v1.0.0)
- [ ] Tarih güncel (Ekim 2025)
- [ ] Copyright bilgisi var
- [ ] README.txt hazır
- [ ] Klasör yapısı düzenli
- [ ] ZIP oluşturuldu

---

## Örnek Workflow

**Tam Süreç:**

```cmd
REM 1. Screenshot'ları çek (4-6 saat)
REM    docs/SCREENSHOT_CHECKLIST.md kullan

REM 2. Görselleri düzenle (1-2 saat)
REM    İşaretleme, numaralandırma, collage

REM 3. Markdown'a ekle (30 dakika)
REM    Find & Replace ile placeholder değiştir

REM 4. Önizle (10 dakika)
REM    VSCode veya Typora ile kontrol et

REM 5. PDF oluştur (5 dakika)
build_manual_advanced.bat

REM 6. PDF kontrolü (15 dakika)
REM    Tüm sayfalara göz at, hata ara

REM 7. Dağıtım paketi (5 dakika)
REM    ZIP oluştur, test et

REM Toplam: 6-9 saat
```

---

## Yardım ve Destek

**Dokümantasyon:**
- Pandoc: https://pandoc.org/MANUAL.html
- MiKTeX: https://docs.miktex.org/

**Topluluk:**
- Pandoc GitHub: https://github.com/jgm/pandoc
- Stack Overflow: [pandoc] tag

**İletişim:**
- E-posta: support@timegraphx.com
- Web: www.timegraphx.com/docs

---

**Başarılar! 📄**

