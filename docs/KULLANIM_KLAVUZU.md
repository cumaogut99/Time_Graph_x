# 📖 Time Graph X - Kapsamlı Kullanım Klavuzu

**Versiyon:** 1.0.0  
**Son Güncelleme:** Ekim 2025  
**Hedef Kullanıcı:** Mühendisler, Veri Analistleri, Test Mühendisleri

---

## 📋 İçindekiler

1. [Giriş ve Genel Bakış](#1-giriş-ve-genel-bakış)
2. [Kurulum ve Başlangıç](#2-kurulum-ve-başlangıç)
3. [Dosya İşlemleri](#3-dosya-işlemleri)
4. [Grafik Yönetimi](#4-grafik-yönetimi)
5. [Cursor Araçları](#5-cursor-araçları)
6. [İstatistiksel Analiz](#6-istatistiksel-analiz)
7. [Filtreleme Sistemi](#7-filtreleme-sistemi)
8. [Bitmask Analizi](#8-bitmask-analizi)
9. [Korelasyon Analizi](#9-korelasyon-analizi)
10. [Sapma (Deviation) Analizi](#10-sapma-deviation-analizi)
11. [Proje Yönetimi (.mpai)](#11-proje-yönetimi-mpai)
12. [Tema ve Görünüm Ayarları](#12-tema-ve-görünüm-ayarları)
13. [Performans İpuçları](#13-performans-ipuçları)
14. [Klavye Kısayolları](#14-klavye-kısayolları)
15. [Sorun Giderme](#15-sorun-giderme)
16. [SSS (Sıkça Sorulan Sorular)](#16-sss-sıkça-sorulan-sorular)

---

## 1. Giriş ve Genel Bakış

### 1.1 Uygulama Hakkında

**Time Graph X**, profesyonel zaman serisi veri analizi ve görselleştirme için geliştirilmiş, yüksek performanslı bir masaüstü uygulamasıdır. Motor test verileri, sensör kayıtları, endüstriyel ölçümler ve bilimsel zaman serisi verilerini analiz etmek için tasarlanmıştır.

### 1.2 Ana Özellikler

#### 🎯 Veri Yönetimi
- ✅ CSV, Excel (.xlsx, .xls) formatlarında veri yükleme
- ✅ **Çoklu dosya desteği** - 3 dosyaya kadar eş zamanlı çalışma
- ✅ **Gelişmiş Import Dialog** - Esnek veri yükleme ayarları
- ✅ **Parquet Cache** - 8-27x daha hızlı yeniden yükleme
- ✅ **Otomatik veri temizleme** - NULL, infinite, karışık tip düzeltme
- ✅ **25 MB boyut limiti** - Performans garantisi

#### 📊 Görselleştirme
- ✅ **1-6 grafik** - Esnek çoklu grafik desteği
- ✅ **Normalizasyon** - 0-1, -1 to 1, Mean Center
- ✅ **Datetime Axis** - Zaman damgası formatlama
- ✅ **Grid kontrolü** - Her grafik için ayrı grid ayarları
- ✅ **Renk özelleştirme** - Her sinyal için özel renkler
- ✅ **Senkronize zoom** - Tüm grafiklerde eş zamanlı zoom

#### 🎯 Cursor Araçları
- ✅ **Single Cursor** - Tek nokta ölçümü
- ✅ **Dual Cursor** - İki nokta arası delta hesaplama
- ✅ **Gerçek zamanlı değerler** - Anlık veri okuma
- ✅ **Tüm grafiklerde senkronizasyon**

#### 📈 Analiz Araçları
- ✅ **İstatistik Paneli** - Min, Max, Ortalama, RMS, Std Dev
- ✅ **Korelasyon Analizi** - Sinyal çiftleri arası ilişki
- ✅ **Bitmask Analizi** - Dijital sinyal inceleme
- ✅ **Duty Cycle** - Dijital sinyal duty cycle hesaplama
- ✅ **Sapma (Deviation)** - Referans sinyale göre sapma analizi
- ✅ **Filtreleme** - Gelişmiş koşullu filtreleme

#### 💾 Proje Yönetimi
- ✅ **.mpai format** - Veri + Layout + Ayarlar tek dosyada
- ✅ **Hızlı kaydetme** - Parquet tabanlı yüksek performans
- ✅ **Layout kaydetme** - Grafik düzenini sakla

---

## 2. Kurulum ve Başlangıç

### 2.1 Sistem Gereksinimleri

**Minimum Gereksinimler:**
- **İşletim Sistemi:** Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **RAM:** 4 GB
- **Disk Alanı:** 500 MB
- **Python:** 3.8 veya üzeri

**Önerilen Gereksinimler:**
- **RAM:** 8 GB veya üzeri
- **CPU:** 4 çekirdek veya üzeri
- **Ekran Çözünürlüğü:** 1920x1080 veya üzeri

### 2.2 Kurulum Adımları

#### Yöntem 1: Python ile Çalıştırma

```bash
# 1. Gerekli paketleri yükle
pip install -r requirements.txt

# 2. Uygulamayı çalıştır
python app.py
```

#### Yöntem 2: EXE Dosyası (Windows)

```bash
# Standalone EXE oluştur
python tools/build_exe.py

# Oluşan dist/time_graph_app.exe dosyasını çalıştır
```

### 2.3 İlk Çalıştırma

1. **Splash Screen:** Uygulama yüklenirken başlangıç ekranı görünür
2. **Ana Pencere:** Boş bir çalışma alanı ile açılır
3. **İlk Veri Yükleme:** File → Open ile veri dosyanızı yükleyin

---

## 3. Dosya İşlemleri

### 3.1 Veri Dosyası Yükleme

#### A. Temel Veri Yükleme

1. **Menü:** `File → Open` veya `Ctrl+O`
2. **Dosya Seç:** CSV veya Excel dosyanızı seçin
3. **Import Dialog:** Gelişmiş ayarlar penceresi açılır

#### B. Import Dialog Ayarları

**📄 Dosya Bilgileri**
- Dosya yolu, boyutu ve satır sayısı görüntülenir
- 25 MB üzeri dosyalar için uyarı alırsınız

**⚙️ Import Ayarları**

1. **Delimiter (Ayırıcı)**
   - Virgül (,) - Varsayılan CSV
   - Noktalı virgül (;)
   - Tab (\t)
   - Pipe (|)
   - Boşluk ( )

2. **Encoding (Karakter Kodlaması)**
   - UTF-8 - Modern standart
   - Latin-1 - Türkçe karakterler için önerilen
   - ASCII
   - CP1252 (Windows)

3. **Header Row (Başlık Satırı)**
   - Kolon isimlerinin bulunduğu satır numarası
   - Genellikle 0 (ilk satır)

4. **Start Row (Başlangıç Satırı)**
   - Verinin başladığı satır
   - Header'dan sonraki satır

**🕐 Zaman Kolonu Ayarları**

**Seçenek 1: Mevcut Zaman Kolonu Kullan**
- Dosyada zaten zaman kolonu varsa bu seçeneği kullanın
- Zaman formatı seçenekleri:
  - **Otomatik:** Sistem otomatik algılar
  - **Unix Timestamp:** 1693526400 gibi
  - **ISO Format:** 2023-09-01 12:00:00
  - **Saniyelik Index:** 0, 1, 2, 3...

**Seçenek 2: Yeni Zaman Kolonu Oluştur**
- **Sampling Frequency (Hz):** Örnekleme frekansı (örn: 1000 Hz)
- **Start Time Mode:**
  - 0 (Sıfırdan Başla)
  - Şimdiki Zaman
  - Özel Zaman (YYYY-MM-DD HH:MM:SS)
- **Time Unit:** saniye, milisaniye, mikrosaniye, nanosaniye

**Örnek Kullanım:**
```
Motor test verileri - 1000 Hz örnekleme
- Sampling Frequency: 1000 Hz
- Time Unit: milisaniye
- Start Time: 0 (Sıfırdan Başla)
```

#### C. Veri Önizleme

- **İlk 10 Satır:** Import dialog'da otomatik önizleme
- **Kolon Tipleri:** Otomatik algılanan veri tipleri
- **NULL Değerler:** Eksik veri uyarıları

### 3.2 Çoklu Dosya Yönetimi

#### Dosya Sekmeleri

**Maksimum Dosya:** 3 dosya eş zamanlı açık olabilir

**Dosya Sekmeleri (Status Bar'da)**
- Her dosya için ayrı sekme
- Aktif dosya vurgulanır
- **Kapat butonu (✕)** - Dosyayı kapat

**Dosyalar Arası Geçiş:**
- **Sekmeye tıklama** - Diğer dosyaya geç
- Her dosya **kendi ayarlarını korur:**
  - Grafik sayısı ve düzeni
  - Seçili sinyaller
  - Cursor pozisyonları
  - Tema ayarları
  - Filtreler

**Dosya Kapatma:**
1. Sekme üzerindeki **✕** butonuna tıklayın
2. Kaydedilmemiş değişiklikler varsa uyarı alırsınız
3. Dosya kapatılır, diğer dosyalar açık kalır

### 3.3 Veri Kaydetme

#### A. CSV/Excel Export

1. **Menü:** `File → Save` veya `Ctrl+S`
2. **Format Seç:**
   - CSV (*.csv) - Hızlı, evrensel
   - Excel (*.xlsx) - Microsoft Excel uyumlu
3. **Dosya Adı:** İstediğiniz ismi verin
4. **Kaydet:** Mevcut veri ve sinyaller kaydedilir

**Kaydedilen İçerik:**
- Zaman kolonu
- Seçili tüm sinyaller
- Filtrelenmiş veri (eğer filtre aktifse)

#### B. Layout Kaydetme

**Layout Nedir?**
- Grafik düzeni
- Seçili sinyaller
- Renk ayarları
- Panel konumları

**Kaydetme:**
1. `File → Export Layout`
2. JSON dosyası olarak kaydedin (örn: `motor_layout.json`)

**Yükleme:**
1. `File → Import Layout`
2. Daha önce kaydedilen layout'u seçin
3. Grafik düzeni otomatik yüklenir

---

## 4. Grafik Yönetimi

### 4.1 Grafik Oluşturma

#### Grafik Sayısı Ayarlama

1. **📊 Graph Settings** butonuna tıklayın (Toolbar)
2. **Graph Count:** 1-6 arası seçin
3. **Apply** ile uygulayın

**Layout Düzeni:**
- 1 Grafik: Tam ekran
- 2 Grafik: Üst-alt
- 3 Grafik: Üst-alt sıralı
- 4 Grafik: 2x2 grid
- 5-6 Grafik: 3x2 grid

### 4.2 Sinyal Ekleme/Çıkarma

#### Parameters Paneli (Sol Sidebar)

**Sinyal Listesi:**
- Tüm kolonlar görüntülenir
- Zaman kolonu otomatik hariç tutulur

**Checkbox'lar:**
- ☑️ **Üst checkbox:** Sinyalin aktif/pasif durumu
- 🎨 **Renk butonu:** Sinyal rengini değiştir
- 📊 **Grafik dropdown:** Hangi grafikte gösterileceğini seç (Graph 1, 2, 3...)

**Toplu İşlemler:**
- **Select All:** Tüm sinyalleri seç
- **Deselect All:** Tüm sinyalleri kaldır
- **Group Operations:** Benzer isimdeki sinyalleri grupla

### 4.3 Grafik Özellikleri

#### Her Grafik İçin Ayrı Ayarlar

**📊 Graph Advanced Settings** (Her grafik için)

1. **Normalization (Normalizasyon)**
   - **None:** Orijinal değerler
   - **0 to 1:** 0-1 arasına sıkıştır
   - **-1 to 1:** -1 ile 1 arası
   - **Mean Center:** Ortalamayı 0 yap
   - **Z-Score:** Standart sapma normalizasyonu

2. **Grid Settings**
   - ☑️ Show X Grid - Yatay grid çizgileri
   - ☑️ Show Y Grid - Dikey grid çizgileri
   - Grid Alpha (Saydamlık): 0-100%

3. **Axis Settings**
   - Auto Range: Otomatik ölçekleme
   - Fixed Range: Sabit Y ekseni aralığı
   - Log Scale: Logaritmik eksen

### 4.4 Grafik Etkileşimi

#### Zoom ve Pan

**Mouse ile:**
- **Sol tık + sürükle:** Dikdörtgen zoom
- **Sağ tık + sürükle:** Pan (kaydır)
- **Mouse tekerleği:** Zoom in/out
- **Çift tık:** Reset zoom (otomatik ölçekleme)

**Senkronize Zoom:**
- Bir grafikte zoom yaptığınızda tüm grafikler senkronize olur
- X ekseni her zaman senkron
- Y ekseni grafik bazlı (normalizasyon nedeniyle)

#### Context Menu (Sağ Tık)

- **Auto Range:** Otomatik ölçekleme
- **View All:** Tüm veriyi göster
- **Export Image:** Grafik görüntüsünü kaydet

---

## 5. Cursor Araçları

### 5.1 Cursor Modları

#### 🎯 Cursor Mode Button

**3 Mod Mevcuttur:**

1. **None (Kapalı)**
   - Cursor gösterilmez
   - Sadece zoom/pan aktif

2. **Single Cursor**
   - Tek dikey çizgi
   - Mouse pozisyonunda değer okur
   - Tüm grafiklerde senkronize

3. **Dual Cursor**
   - İki dikey çizgi (Cursor 1, Cursor 2)
   - İki nokta arası delta hesaplar
   - Zaman farkı, değer farkı

### 5.2 Single Cursor Kullanımı

#### Özellikler

- **Mouse hareketini takip eder**
- **Tüm grafiklerde senkronize dikey çizgi**
- **İstatistik panelinde değerler güncellenir**

#### Değer Okuma

**Statistics Panel'de:**
```
=== Cursor Values ===
Cursor Position: 2.345 s
Signal1: 123.45
Signal2: 67.89
Signal3: -45.23
```

### 5.3 Dual Cursor Kullanımı

#### Cursor Yerleştirme

1. **Cursor 1 (Mavi):**
   - İlk grafikte istediğiniz noktaya tıklayın
   - Dikey mavi çizgi belirir

2. **Cursor 2 (Kırmızı):**
   - İkinci noktaya tıklayın
   - Dikey kırmızı çizgi belirir

#### Delta Hesaplama

**Statistics Panel'de:**
```
=== Cursor 1 Values ===
Time: 2.345 s
Signal1: 123.45

=== Cursor 2 Values ===
Time: 3.890 s
Signal2: 145.67

=== Delta (Cursor2 - Cursor1) ===
ΔTime: 1.545 s
ΔSignal1: 22.22
ΔSignal2: 18.91
```

#### Kullanım Senaryoları

**1. Rise Time Ölçümü:**
- Motor startta voltaj yükselişini ölçün
- Cursor 1: %10 noktası
- Cursor 2: %90 noktası
- ΔTime = Rise Time

**2. Frekans Hesaplama:**
- Periyodik sinyalde iki tepe arası süreyi ölçün
- Frekans = 1 / ΔTime

**3. Değer Karşılaştırma:**
- İki farklı çalışma noktasını karşılaştırın

---

## 6. İstatistiksel Analiz

### 6.1 Statistics Panel

#### Panel Konumu

**Sağ sidebar'da** - "📊 Statistics" sekmesi

#### Gösterilen İstatistikler

**Temel İstatistikler:**
- **Minimum:** En düşük değer
- **Maximum:** En yüksek değer
- **Mean (Ortalama):** Aritmetik ortalama
- **RMS:** Root Mean Square (Etkin değer)
- **Std Dev:** Standart sapma
- **Variance:** Varyans

**Cursor Değerleri:**
- Single Cursor: O anki değerler
- Dual Cursor: İki nokta + Delta

### 6.2 Statistics Settings

#### ⚙️ Statistics Settings Butonu

**Hangi İstatistiklerin Gösterileceğini Seçin:**

```
☑️ Minimum
☑️ Maximum
☑️ Mean (Average)
☑️ RMS
☑️ Standard Deviation
☐ Variance
☐ Peak-to-Peak
☐ Median
```

**Performans İpucu:**
- Gereksiz istatistikleri kapatın
- Büyük veri setlerinde hesaplama hızlanır

### 6.3 İstatistik Hesaplama Kapsamı

#### Otomatik Güncelleme

**İstatistikler şu durumlarda güncellenir:**
1. Yeni veri yüklendiğinde
2. Sinyal ekleme/çıkarma
3. Filtreleme uygulandığında
4. Cursor hareket ettiğinde
5. Zoom değiştiğinde (görünür alan için)

#### Hesaplama Modları

**Full Data Mode:**
- Tüm veri seti üzerinde hesaplama
- Filtrelenmemiş tüm noktalar

**Visible Range Mode:**
- Sadece ekranda görünen alan
- Zoom yapıldığında değişir

**Selected Range Mode:**
- Cursor'lar arası bölge (Dual Cursor'da)

---

## 7. Filtreleme Sistemi

### 7.1 Filtre Paneli

#### Panel Konumu

**Sağ sidebar'da** - "🔍 Filters" sekmesi

### 7.2 Basit Filtreleme

#### Filtre Ekleme

1. **Add Filter** butonuna tıklayın
2. **Parameter:** Filtrelemek istediğin kolonu seç
3. **Operator:** Karşılaştırma operatörü seç
   - `>=` Büyük eşit
   - `>` Büyük
   - `<=` Küçük eşit
   - `<` Küçük
   - `==` Eşit
   - `!=` Eşit değil
4. **Value:** Eşik değerini gir
5. **Add** - Filtreyi ekle

**Örnek:**
```
Motor_Speed >= 1000
Motor_Temp < 85
```

### 7.3 Çoklu Filtre

#### AND Mantığı

**Tüm filtreler AND ile birleştirilir:**

```
Motor_Speed >= 1000  AND
Motor_Temp < 85      AND
Voltage > 10
```

Sonuç: Üç koşulu da sağlayan satırlar gösterilir

#### Filtre Yönetimi

- **Remove:** Belirli bir filtreyi kaldır
- **Clear All:** Tüm filtreleri temizle
- **Disable:** Filtreyi geçici olarak devre dışı bırak

### 7.4 Gelişmiş Filtre Modları

#### Segmented Mode (Bölütlenmiş)

**Aktifleştirme:** ☑️ "Segmented Mode"

**Ne Yapar?**
- Filtreyi geçen bölgeleri **ayrı ayrı** gösterir
- Koşulu sağlamayan veriler **görünmez**
- Zaman ekseninde **boşluklar** oluşur

**Kullanım Senaryosu:**
```
Motor çalıştığı zamanları göster:
Motor_Speed > 0

Sonuç: Motor durduğunda grafik kesilir
```

#### Concatenated Mode (Birleştirilmiş)

**Aktifleştirme:** ☐ "Segmented Mode" kapalı

**Ne Yapar?**
- Filtreyi geçen bölgeleri **birleştirir**
- Zaman ekseni **yeniden oluşturulur**
- Sürekli bir grafik gösterir

**Kullanım Senaryosu:**
```
Sadece yüksek hız anlarını analiz et:
Motor_Speed > 3000

Sonuç: Düşük hız anları atılır, 
       yüksek hız bölgeleri birleştirilir
```

### 7.5 Filtre Performansı

#### Optimizasyon

- **Debouncing:** 100ms gecikme ile gereksiz hesaplamalar önlenir
- **Thread-safe:** Arka planda hesaplanır, UI donmaz
- **Cache:** Aynı filtre tekrar uygulandığında cache kullanılır

#### Büyük Veri Setleri

**25 MB'a kadar veri için:**
- Filtre uygulama: < 1 saniye
- Gerçek zamanlı güncelleme

---

## 8. Bitmask Analizi

### 8.1 Bitmask Nedir?

**Dijital sinyallerin bit düzeyinde analizi**

**Kullanım Alanları:**
- CAN bus verileri
- Durum bayrakları (status flags)
- Hata kodları
- Digital I/O sinyalleri

### 8.2 Bitmask Paneli

#### Panel Konumu

**Sağ sidebar'da** - "🔢 Bitmask" sekmesi

### 8.3 Bitmask Sinyali Seçme

#### Adımlar

1. **Parameter Dropdown:** Bitmask kolonunu seçin
2. **Bit Count:** Kaç bit analiz edilecek (1-32)
3. **Start Bit:** Başlangıç bit pozisyonu (LSB = 0)

**Örnek:**
```
8-bit Status Register:
Bit 0: Motor Running
Bit 1: Temperature Warning
Bit 2: Overspeed
Bit 3: Fault
Bit 4-7: Reserved
```

### 8.4 Bit Görselleştirme

#### Bit Grafikleri

**Her bit için ayrı sinyal:**
- `Status_Bit0` - Motor Running
- `Status_Bit1` - Temperature Warning
- `Status_Bit2` - Overspeed
- ...

**Görselleştirme:**
- **1:** Yüksek (ON)
- **0:** Düşük (OFF)

**Dijital dalga formları:**
- Kare dalga şeklinde gösterilir
- Rise/fall edge'ler net görünür

### 8.5 Duty Cycle Hesaplama

#### Duty Cycle Nedir?

**Sinyalin HIGH olduğu sürenin yüzdesi:**

```
Duty Cycle = (HIGH time / Total time) × 100%
```

#### Panel'de Gösterim

```
=== Bitmask: Status_Register ===
Bit 0 (Motor_Running):
  Duty Cycle: 85.3%
  Total transitions: 456
  
Bit 1 (Temp_Warning):
  Duty Cycle: 12.7%
  Total transitions: 89
```

#### Threshold Ayarları

**Manual Threshold:**
- Varsayılan: Otomatik (veri ortalaması)
- Manuel: Belirli bir değer (örn: 2.5V)

**Ayarlama:**
1. ⚙️ **Duty Cycle Settings**
2. ☑️ Manual Threshold
3. Değer girin (örn: 2.5)

---

## 9. Korelasyon Analizi

### 9.1 Correlations Panel

#### Panel Konumu

**Sağ sidebar'da** - "📈 Correlations" sekmesi

### 9.2 Korelasyon Nedir?

**İki sinyal arasındaki doğrusal ilişkiyi ölçer**

**Pearson Korelasyon Katsayısı (r):**
- **r = 1:** Mükemmel pozitif korelasyon
- **r = 0:** İlişki yok
- **r = -1:** Mükemmel negatif korelasyon

### 9.3 Korelasyon Hesaplama

#### Otomatik Hesaplama

**Panel açıldığında:**
- Tüm sinyal çiftleri için korelasyon hesaplanır
- Sonuçlar tabloda gösterilir

#### Korelasyon Tablosu

```
Signal Pair                  | Correlation | Strength
---------------------------------------------------------
Motor_Speed ↔ Motor_Torque  |   0.92      | Very Strong
Motor_Speed ↔ Vibration     |   0.67      | Moderate
Motor_Temp ↔ Ambient_Temp   |   0.45      | Weak
Voltage ↔ Current           |  -0.15      | Very Weak
```

### 9.4 Korelasyon Yorumlama

#### Strength Levels

- **Very Strong:** |r| > 0.8
- **Strong:** 0.6 < |r| ≤ 0.8
- **Moderate:** 0.4 < |r| ≤ 0.6
- **Weak:** 0.2 < |r| ≤ 0.4
- **Very Weak:** |r| ≤ 0.2

#### Pozitif vs Negatif

**Pozitif Korelasyon (r > 0):**
- Bir sinyal arttığında diğeri de artar
- Örnek: Hız ↔ Güç

**Negatif Korelasyon (r < 0):**
- Bir sinyal arttığında diğeri azalır
- Örnek: Hız ↔ Efficiency (bazı durumlarda)

### 9.5 Scatter Plot

#### Görselleştirme

1. **Sinyal çiftine çift tıklayın**
2. **Scatter plot** penceresi açılır
3. **X eksen:** İlk sinyal
4. **Y eksen:** İkinci sinyal

**Görsel İpuçları:**
- Düz çizgi: Güçlü korelasyon
- Dağılmış noktalar: Zayıf korelasyon
- Pozitif eğim: Pozitif korelasyon
- Negatif eğim: Negatif korelasyon

---

## 10. Sapma (Deviation) Analizi

### 10.1 Deviation Nedir?

**Bir sinyalin referans sinyalden sapmasını ölçer**

**Kullanım Alanları:**
- **Test vs. Referans** karşılaştırması
- **Before/After** analizi
- **Tolerans kontrolü**
- **Kalite kontrol**

### 10.2 Deviation Panel

#### Panel Konumu

**Sağ sidebar'da** - "📉 Deviation" sekmesi

### 10.3 Basic Deviation

#### Adımlar

1. **Test Signal:** Test edilecek sinyali seçin
2. **Reference Signal:** Referans sinyali seçin
3. **Calculate:** Sapma hesapla

#### Sapma Metrikleri

```
=== Deviation Analysis ===

Max Deviation: +15.3 units
Min Deviation: -8.7 units
Mean Absolute Deviation: 5.2 units
RMS Deviation: 6.8 units
```

### 10.4 Advanced Deviation

#### Static Limits (Sabit Limitler)

**Excel Dosyası ile Limit Tanımlama:**

1. **Load Limits:** Excel dosyası yükleyin
2. **Format:**
   ```
   Time | Upper_Limit | Lower_Limit
   0    | 100        | 90
   1    | 105        | 95
   2    | 110        | 100
   ```
3. **Tolerance Zones:** Grafikte limit çizgileri gösterilir

#### Deviation Visualization

**Grafik Overlay:**
- **Yeşil alan:** Tolerans içi
- **Kırmızı alan:** Tolerans dışı
- **Sapma sinyali:** Ayrı bir sinyal olarak gösterilir

#### Örnek Kullanım

**Motor Test Senaryosu:**
```
Reference: Beklenen hız profili
Test Signal: Gerçek ölçülen hız

Deviation Analysis:
- Max sapma: +50 RPM (t=5.3s)
- Min sapma: -30 RPM (t=8.1s)
- Tolerans aşımı: 3 nokta
```

---

## 11. Proje Yönetimi (.mpai)

### 11.1 MPAI Format Nedir?

**Motor Performance Analysis Information (MPAI)**

**Tek dosyada şunları saklar:**
- ✅ Tüm veri (Parquet formatında)
- ✅ Grafik düzeni (Layout)
- ✅ Seçili sinyaller
- ✅ Renk ayarları
- ✅ Filtreler
- ✅ Cursor pozisyonları
- ✅ Tema ayarları

**Avantajlar:**
- 🚀 **Hızlı kaydetme** - Parquet tabanlı
- 🚀 **Hızlı yükleme** - CSV'den 8-27x daha hızlı
- 💾 **Tek dosya** - Kolay taşıma ve paylaşım
- 🔒 **Sıkıştırılmış** - Küçük dosya boyutu

### 11.2 Proje Kaydetme

#### Adımlar

1. **Menü:** `File → Save Project (.mpai)`
2. **Dosya Adı:** Örn: `motor_test_20231025.mpai`
3. **Kaydet:** Tüm durum kaydedilir

**Kaydedilen Metadata:**
```json
{
  "original_file": "test_data.csv",
  "saved_date": "2023-10-25T14:30:00",
  "time_column": "Time",
  "row_count": 50000,
  "column_count": 25
}
```

### 11.3 Proje Yükleme

#### Adımlar

1. **Menü:** `File → Open Project (.mpai)`
2. **Dosya Seç:** .mpai dosyanızı seçin
3. **Otomatik Yükleme:**
   - Veri yüklenir
   - Layout uygulanır
   - Tüm ayarlar geri gelir

**Yükleme Süresi:**
- CSV: 5-15 saniye
- MPAI: < 1 saniye

**Status Bar Mesajı:**
```
✅ Proje başarıyla yüklendi: motor_test_20231025.mpai (Parquet - Hızlı!)
```

### 11.4 Proje Paylaşımı

#### İş Arkadaşları ile Paylaşım

**Tek .mpai dosyasını paylaşın:**
- Tüm analiz dahil
- Aynı görünüm
- Tekrar üretilebilir sonuçlar

---

## 12. Tema ve Görünüm Ayarları

### 12.1 Theme Manager

#### ⚙️ General Settings Butonu

**Tema Seçenekleri:**
1. **Light:** Açık tema (varsayılan)
2. **Dark:** Koyu tema
3. **High Contrast:** Yüksek kontrast
4. **Custom:** Özel tema

### 12.2 Özel Tema Oluşturma

#### Renk Ayarları

**Özelleştirilebilir Renkler:**
- Background (Arka plan)
- Foreground (Yazı)
- Grid Color
- Cursor Color
- Selection Color

**Kaydetme:**
```json
{
  "theme_name": "My Custom Theme",
  "background": "#1E1E1E",
  "foreground": "#FFFFFF",
  "grid_color": "#404040",
  "cursor_color": "#00FF00"
}
```

### 12.3 Panel Düzeni

#### Esnek Panel Sistemi

**Sol Sidebar:**
- Parameters (Sinyaller)
- Control Panel

**Sağ Sidebar:**
- Statistics
- Filters
- Bitmask
- Correlations
- Deviation

**Panel Boyutlandırma:**
- Splitter'ları sürükleyerek boyutlandırın
- Minimize/Maximize butonları
- Tam ekran grafik modu

---

## 13. Performans İpuçları

### 13.1 Büyük Veri Setleri

#### Optimizasyon Stratejileri

**1. Parquet Cache Kullan**
```
İlk yükleme: 12 saniye (CSV)
İkinci yükleme: 1.5 saniye (Parquet Cache)
```

**2. Gereksiz Sinyalleri Kaldır**
- Sadece gerekli kolonları seçin
- 50 kolon yerine 10 kolon: 5x daha hızlı

**3. Filtre Kullan**
- Gereksiz veriyi filtreleyin
- Analiz süresini kısaltın

**4. Grafik Sayısını Azaltın**
- 6 grafik yerine 2-3 grafik
- Render süresi azalır

### 13.2 Memory Yönetimi

#### Çoklu Dosya Limiti

**Neden 3 dosya?**
- Her dosya 25 MB'a kadar
- Toplam: ~75 MB RAM kullanımı
- Sistem stabilitesi

**Büyük dosyalarla çalışma:**
1. Dosyayı filtreleyerek küçültün
2. Sadece ilgili bölümü yükleyin
3. MPAI formatında kaydedin

### 13.3 Render Performansı

#### Grafik Optimizasyonu

**Anti-aliasing:**
- Kapalı: Daha hızlı
- Açık: Daha güzel

**Downsampling:**
- Otomatik aktif
- Ekranda 1000 pikselden fazla nokta varsa örnekleme yapar

---

## 14. Klavye Kısayolları

### 14.1 Dosya İşlemleri

| Kısayol | İşlev |
|---------|-------|
| `Ctrl+O` | Dosya Aç |
| `Ctrl+S` | Dosya Kaydet |
| `Ctrl+Shift+S` | Proje Kaydet (.mpai) |
| `Ctrl+Q` | Uygulamadan Çık |

### 14.2 Görünüm

| Kısayol | İşlev |
|---------|-------|
| `Ctrl++` | Zoom In |
| `Ctrl+-` | Zoom Out |
| `Ctrl+0` | Reset Zoom |
| `F11` | Tam Ekran |

### 14.3 Analiz

| Kısayol | İşlev |
|---------|-------|
| `Ctrl+C` | Cursor Mode Toggle |
| `Ctrl+F` | Filtre Ekle |
| `Ctrl+R` | Filtreleri Sıfırla |
| `Ctrl+T` | Statistics Panel Toggle |

---

## 15. Sorun Giderme

### 15.1 Yaygın Hatalar

#### 1. Dosya Yüklenmiyor

**Hata:** "Dosya okunamadı"

**Çözümler:**
- Dosya formatını kontrol edin (CSV veya Excel)
- Delimiter ayarını kontrol edin (virgül/noktalı virgül)
- Encoding'i değiştirin (UTF-8 → Latin-1)
- Dosya bozuk olabilir, başka bir dosya deneyin

#### 2. Grafik Görünmüyor

**Hata:** Boş grafik ekranı

**Çözümler:**
- Parameters panelinden sinyal seçin (checkbox'ları işaretleyin)
- Grafik ataması yapın (Graph 1, 2, etc.)
- Veri tipi sayısal olmalı (string kolonlar grafik yapılamaz)
- Auto Range yapın (grafik üzerinde sağ tık → Auto Range)

#### 3. Uygulama Yavaş

**Semptom:** Donma, gecikme

**Çözümler:**
- Dosya boyutunu kontrol edin (max 25 MB)
- Gereksiz sinyalleri kaldırın
- Grafik sayısını azaltın
- Filtreleme ile veri miktarını azaltın
- Daha az istatistik hesaplayın

#### 4. Cursor Çalışmıyor

**Hata:** Cursor görünmüyor veya değer göstermiyor

**Çözümler:**
- Cursor Mode'un açık olduğunu kontrol edin
- Grafiğin içine tıklayın
- Sinyal seçili olmalı
- Statistics panelini açın

### 15.2 Log Dosyası

#### Hata Tespiti

**Log Konumu:**
```
time_graph_app.log
```

**Log İçeriği:**
- Tüm işlemler
- Hata mesajları
- Performans metrikleri
- Thread durumu

**Log Okuma:**
```
[2023-10-25 14:30:00] INFO - Dosya yüklendi: test_data.csv
[2023-10-25 14:30:05] ERROR - Kolon 'Speed' bulunamadı
[2023-10-25 14:30:10] WARNING - Yüksek NULL oranı: Temperature (%35)
```

### 15.3 Reset ve Temizleme

#### Uygulama Sıfırlama

**1. Cache Temizleme:**
```bash
# Parquet cache'i sil
rm -rf .cache/
```

**2. Ayar Sıfırlama:**
```bash
# Config dosyalarını sil
rm -rf config/
```

**3. Tam Sıfırlama:**
- Uygulamayı kapat
- Log ve cache dosyalarını sil
- Yeniden başlat

---

## 16. SSS (Sıkça Sorulan Sorular)

### Veri İşleme

**S: Maksimum dosya boyutu nedir?**
> A: 25 MB. Daha büyük dosyalar için filtreleme yaparak küçültün.

**S: Hangi dosya formatları destekleniyor?**
> A: CSV (.csv), Excel (.xlsx, .xls), MPAI (.mpai)

**S: Türkçe karakter sorunu nasıl çözülür?**
> A: Import dialog'da Encoding'i "Latin-1" olarak seçin.

**S: Virgül yerine noktalı virgül ayırıcı nasıl kullanılır?**
> A: Import dialog'da Delimiter'ı "Semicolon (;)" seçin.

### Grafik ve Görselleştirme

**S: Kaç grafik oluşturabilirim?**
> A: 1-6 arası.

**S: Farklı birimlerdeki sinyalleri aynı grafikte gösterebilir miyim?**
> A: Evet, normalizasyon kullanın (0 to 1 veya -1 to 1).

**S: Grafikleri nasıl yakınlaştırırım?**
> A: Sol tık + sürükle ile dikdörtgen zoom yapın.

### Analiz

**S: Korelasyon analizi ne zaman kullanılır?**
> A: İki sinyal arasında ilişki olup olmadığını görmek için (örn: Hız ve Güç).

**S: Duty Cycle nedir?**
> A: Dijital sinyalin "HIGH" olduğu sürenin yüzdesidir.

**S: Filtreleme sonrası orijinal veriye nasıl dönerim?**
> A: "Clear All Filters" butonuna tıklayın.

### Performans

**S: Neden Parquet cache kullanmalıyım?**
> A: İkinci yüklemede 8-27x daha hızlı olur.

**S: Çoklu dosya desteği neden 3 ile sınırlı?**
> A: Performans ve stabilite için. Her dosya 25 MB'a kadar olabilir.

**S: Uygulamayı nasıl hızlandırabilirim?**
> A: Gereksiz sinyalleri kaldırın, daha az grafik kullanın, filtreleme yapın.

### Proje Yönetimi

**S: MPAI formatı nedir?**
> A: Motor Performance Analysis Information - Veri + Layout tek dosyada.

**S: MPAI dosyalarını başkalarıyla paylaşabilir miyim?**
> A: Evet, tüm analiz tek dosyada olduğu için kolayca paylaşılabilir.

**S: Layout'u nasıl kaydederim?**
> A: File → Export Layout → JSON dosyası kaydedin.

---

## 📞 Destek ve İletişim

### Teknik Destek

**E-posta:** support@timegraphx.com  
**Web:** www.timegraphx.com/support  
**Dokümantasyon:** www.timegraphx.com/docs

### Geri Bildirim

Önerileriniz ve hata raporlarınız için lütfen iletişime geçin.

---

## 📄 Lisans

Bu yazılım ticari lisans altındadır. Kullanım koşulları için lisans sözleşmesine bakınız.

**Copyright © 2025 Time Graph X. Tüm hakları saklıdır.**

---

## 🔄 Versiyon Geçmişi

### v1.0.0 (Ekim 2025)
- ✅ İlk kararlı sürüm
- ✅ Çoklu dosya desteği
- ✅ MPAI proje formatı
- ✅ Gelişmiş filtreleme
- ✅ Deviation analizi
- ✅ Parquet cache

---

## 📚 Ek Kaynaklar

### Video Eğitimler
- Temel kullanım (15 dk)
- Gelişmiş analiz teknikleri (30 dk)
- Filtreleme ve deviation (20 dk)

### Örnek Projeler
- Motor test analizi
- Sensör veri işleme
- Kalite kontrol uygulaması

---

**Son Güncelleme:** Ekim 2025
**Doküman Versiyonu:** 1.0

