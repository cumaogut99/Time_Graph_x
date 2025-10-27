# 📖 Time Graph X - Kullanım Kılavuzu

**Versiyon:** 1.0.0  
**Platform:** Windows 10/11  
**Son Güncelleme:** Ekim 2025

---

## 📋 İçindekiler

1. [Başlangıç](#1-başlangıç)
2. [İlk Adımlar](#2-ilk-adımlar)
3. [Veri Yükleme](#3-veri-yükleme)
4. [Grafik Yönetimi](#4-grafik-yönetimi)
5. [Sinyal Seçimi ve Ayarları](#5-sinyal-seçimi-ve-ayarları)
6. [Cursor Araçları](#6-cursor-araçları)
7. [İstatistiksel Analiz](#7-istatistiksel-analiz)
8. [Filtreleme](#8-filtreleme)
9. [Bitmask (Dijital Sinyal) Analizi](#9-bitmask-dijital-sinyal-analizi)
10. [Korelasyon Analizi](#10-korelasyon-analizi)
11. [Sapma Analizi](#11-sapma-analizi)
12. [Çoklu Dosya Yönetimi](#12-çoklu-dosya-yönetimi)
13. [Proje Kaydetme ve Yükleme](#13-proje-kaydetme-ve-yükleme)
14. [Klavye Kısayolları](#14-klavye-kısayolları)
15. [İpuçları ve Püf Noktaları](#15-ipuçları-ve-püf-noktaları)
16. [Sorun Giderme](#16-sorun-giderme)

---

## 1. Başlangıç

### 1.1 Time Graph X Nedir?

**Time Graph X**, profesyonel zaman serisi veri analizi için geliştirilmiş, güçlü ve kullanıcı dostu bir masaüstü uygulamasıdır.

**Kullanım Alanları:**
- 🏭 Motor ve makine test verileri analizi
- 📊 Sensör verilerinin görselleştirilmesi
- 🔬 Bilimsel ölçüm verilerinin incelenmesi
- ⚙️ Kalite kontrol ve test raporlama
- 📈 Endüstriyel veri analizi

**Ana Özellikler:**
- ✅ Kolay veri yükleme (CSV, Excel)
- ✅ Çoklu grafik desteği (6 grafiğe kadar)
- ✅ Gelişmiş ölçüm araçları (Dual Cursor)
- ✅ Otomatik istatistik hesaplama
- ✅ Güçlü filtreleme sistemi
- ✅ Hızlı proje kaydetme (.mpai format)

### 1.2 Sistem Gereksinimleri

**Minimum:**
- Windows 10 veya Windows 11
- 4 GB RAM
- 500 MB boş disk alanı
- 1366x768 ekran çözünürlüğü

**Önerilen:**
- Windows 11
- 8 GB veya üzeri RAM
- 4 çekirdekli işlemci
- 1920x1080 veya daha yüksek çözünürlük

### 1.3 Uygulama İkonları Rehberi

| İkon | Açıklama |
|------|----------|
| 📁 **File** | Dosya işlemleri menüsü |
| 📊 **Graph Settings** | Grafik sayısı ve düzeni ayarları |
| ⚙️ **General** | Genel ayarlar ve tema |
| 🎯 **Cursor Mode** | Cursor modunu değiştir |
| ⚙️ **Statistics Settings** | İstatistik ayarları |

---

## 2. İlk Adımlar

### 2.1 Uygulamayı Başlatma

1. **Time Graph X.exe** dosyasına çift tıklayın
2. Başlangıç ekranı görünür ve uygulama yüklenir
3. Ana pencere açılır

> 📸 **[Görsel 1: Uygulama Başlangıç Ekranı]**  
> _Splash screen ve ana pencere açılış görüntüsü_

### 2.2 Ana Pencere Düzeni

Ana pencere 4 ana bölümden oluşur:

```
┌─────────────────────────────────────────────────────────┐
│  ⚙️ TOOLBAR (Üst Menü)                                  │
├───────────┬─────────────────────────────┬───────────────┤
│           │                             │               │
│  SOL      │     GRAFIK ALANI            │    SAĞ       │
│  SIDEBAR  │     (Grafikler)             │  SIDEBAR     │
│           │                             │               │
│ Parameters│                             │ Statistics    │
│           │                             │ Filters       │
│           │                             │ Correlations  │
├───────────┴─────────────────────────────┴───────────────┤
│  📊 STATUS BAR (Durum Çubuğu)                           │
└─────────────────────────────────────────────────────────┘
```

> 📸 **[Görsel 2: Ana Pencere Bölümleri]**  
> _Tüm bölümlerin işaretlenmiş hali_

**Bölüm Açıklamaları:**

1. **Toolbar (Üst Menü)**
   - Dosya işlemleri
   - Grafik ayarları
   - Cursor modu seçimi
   - Tema değiştirme

2. **Sol Sidebar (Parameters)**
   - Yüklenmiş veri kolonları
   - Sinyal seçme checkbox'ları
   - Renk ve grafik atamaları

3. **Grafik Alanı (Ortada)**
   - Zaman serisi grafikleri
   - 1-6 arası grafik gösterimi
   - Zoom ve pan işlemleri

4. **Sağ Sidebar (Analiz Panelleri)**
   - Statistics: İstatistikler
   - Filters: Filtreleme
   - Bitmask: Dijital sinyal analizi
   - Correlations: Korelasyon
   - Deviation: Sapma analizi

5. **Status Bar (Alt)**
   - Dosya sekmeleri
   - Sistem durumu
   - İşlem bilgileri

---

## 3. Veri Yükleme

### 3.1 Desteklenen Dosya Formatları

- **CSV Dosyaları** (.csv) - Virgül veya noktalı virgül ile ayrılmış
- **Excel Dosyaları** (.xlsx, .xls) - Microsoft Excel
- **Proje Dosyaları** (.mpai) - Time Graph X özel formatı

**Maksimum Dosya Boyutu:** 25 MB

### 3.2 Temel Veri Yükleme

**Adımlar:**

1. **Dosya menüsünü açın**
   - Üst menüde **📁 File** butonuna tıklayın
   - **"Open Data File"** seçeneğini seçin
   - _Veya klavyede **Ctrl+O** tuşlarına basın_

> 📸 **[Görsel 3: File Menüsü]**  
> _File menüsü ve seçenekleri_

2. **Dosya seçin**
   - Bilgisayarınızdan CSV veya Excel dosyanızı seçin
   - **"Aç"** butonuna tıklayın

3. **Import Dialog açılır**
   - Veri önizleme ekranı gelir
   - İlk 10 satır gösterilir

> 📸 **[Görsel 4: Import Dialog Penceresi]**  
> _Import dialog ve önizleme ekranı_

### 3.3 Import Dialog Ayarları

Import Dialog, verinin doğru şekilde yüklenmesi için gelişmiş ayarlar sunar.

#### A. Temel Ayarlar

**1. Delimiter (Ayırıcı Karakter)**

Verinizdeki kolonların nasıl ayrıldığını belirtir:

- **Comma (,)** - Varsayılan CSV formatı
- **Semicolon (;)** - Türkçe Excel dosyaları için
- **Tab** - Tab ile ayrılmış dosyalar
- **Pipe (|)** - Özel formatlar
- **Space** - Boşlukla ayrılmış

> ⚠️ **Önemli:** Türkçe Excel'den kaydedilen CSV dosyaları genellikle noktalı virgül (;) kullanır.

**2. Encoding (Karakter Kodlaması)**

Türkçe karakter sorunu yaşıyorsanız:

- **Latin-1** - Türkçe karakterler için ÖNERİLEN
- **UTF-8** - Modern standart
- **CP1252** - Windows varsayılanı
- **ASCII** - Sadece İngilizce karakterler

**3. Header Row (Başlık Satırı)**

Kolon isimlerinin hangi satırda olduğunu belirtin:
- Genellikle **0** (ilk satır)
- Bazı dosyalarda **1** veya **2** olabilir

**4. Start Row (Veri Başlangıç Satırı)**

Gerçek verinin hangi satırdan başladığını belirtin:
- Header'dan hemen sonraki satır
- Genellikle **1** (ikinci satır)

> 📸 **[Görsel 5: Import Ayarları Bölümü]**  
> _Delimiter, encoding ve satır ayarları_

#### B. Zaman Kolonu Ayarları

Time Graph X, zaman eksenini oluşturmak için bir zaman kolonu gerektirir.

**İki seçenek vardır:**

##### Seçenek 1: Mevcut Zaman Kolonu Kullan

Dosyanızda zaten bir zaman kolonu varsa bu seçeneği kullanın.

**Adımlar:**
1. **"Use Existing Time Column"** seçeneğini işaretleyin
2. **Time Column** dropdown'dan zaman kolonunu seçin
3. **Time Format** seçin:
   - **Automatic** - Otomatik algılama (önerilen)
   - **Unix Timestamp** - 1693526400 gibi sayılar
   - **ISO DateTime** - 2023-09-01 12:00:00 formatı
   - **Numeric Index** - 0, 1, 2, 3... şeklinde sayılar

**Örnek Zaman Formatları:**
```
Unix Timestamp:    1693526400
ISO DateTime:      2023-09-01 12:00:00
Numeric Index:     0, 0.001, 0.002, 0.003, ...
```

##### Seçenek 2: Yeni Zaman Kolonu Oluştur

Dosyanızda zaman kolonu yoksa veya yeni bir zaman serisi oluşturmak istiyorsanız:

**Adımlar:**
1. **"Create Custom Time Column"** seçeneğini işaretleyin
2. Ayarları yapın:

**Sampling Frequency (Örnekleme Frekansı):**
- Verinizin saniyedeki örnek sayısı (Hz)
- Örnek: Motor 1000 Hz'de ölçülmüşse → **1000**

**Start Time Mode:**
- **0 (Sıfırdan Başla)** - Zaman 0'dan başlar
- **Current Time** - Şu anki zaman
- **Custom Time** - Özel bir zaman belirtin (YYYY-MM-DD HH:MM:SS)

**Time Unit (Zaman Birimi):**
- **Seconds** - Saniye
- **Milliseconds** - Milisaniye
- **Microseconds** - Mikrosaniye
- **Nanoseconds** - Nanosaniye

**Örnek Ayar:**
```
Motor test verisi - 1000 Hz örnekleme:
├─ Sampling Frequency: 1000 Hz
├─ Start Time Mode: 0 (Sıfırdan Başla)
├─ Time Unit: Milliseconds
└─ Oluşan zaman: 0, 1, 2, 3, ... (ms cinsinden)
```

> 📸 **[Görsel 6: Zaman Kolonu Ayarları]**  
> _Mevcut zaman kolonu ve yeni oluşturma seçenekleri_

#### C. Veri Önizleme

Import Dialog'un alt kısmında verinin önizlemesi gösterilir:

- **İlk 10 satır** tablo halinde
- **Kolon isimleri** başlıkta
- **Veri tipleri** otomatik algılanmış

**Kontrol edin:**
- ✅ Kolonlar doğru ayrılmış mı?
- ✅ Türkçe karakterler düzgün mü?
- ✅ Sayısal değerler doğru mu?

> 📸 **[Görsel 7: Veri Önizleme Tablosu]**  
> _İlk 10 satırın tablo görünümü_

### 3.4 Veri Yükleme

Tüm ayarları yaptıktan sonra:

1. **"Load Data"** butonuna tıklayın
2. Loading (yükleniyor) animasyonu görünür
3. Veri yüklendikten sonra grafikler açılır

**Yükleme Süreleri:**
- Küçük dosyalar (< 5 MB): 1-3 saniye
- Orta dosyalar (5-15 MB): 3-8 saniye
- Büyük dosyalar (15-25 MB): 8-15 saniye

> 📸 **[Görsel 8: Yükleme Animasyonu]**  
> _Loading overlay ve ilerleme göstergesi_

**Başarılı yüklemede:**
- Status bar'da dosya bilgisi gösterilir
- Örnek: `"Dosya yüklendi: motor_data.csv (50,000 satır, 24 sütun)"`
- Sol sidebar'da tüm kolonlar listelenir
- Grafikler boş olarak hazırlanır

---

## 4. Grafik Yönetimi

### 4.1 Grafik Sayısını Ayarlama

Time Graph X, 1 ile 6 arası grafik gösterimi destekler.

**Adımlar:**

1. **Toolbar'da 📊 "Graph Settings" butonuna tıklayın**

2. **Graph Settings Dialog açılır**

3. **"Number of Graphs" slider'ını kaydırın**
   - Minimum: 1 grafik
   - Maksimum: 6 grafik

4. **"Apply" butonuna tıklayın**

> 📸 **[Görsel 9: Graph Settings Dialog]**  
> _Grafik sayısı ayarlama ve layout önizleme_

**Grafik Düzenleri:**

```
1 Grafik:  ┌─────────┐
           │ Graph 1 │
           └─────────┘

2 Grafik:  ┌─────────┐
           │ Graph 1 │
           ├─────────┤
           │ Graph 2 │
           └─────────┘

3 Grafik:  ┌─────────┐
           │ Graph 1 │
           ├─────────┤
           │ Graph 2 │
           ├─────────┤
           │ Graph 3 │
           └─────────┘

4 Grafik:  ┌────┬────┐
           │ G1 │ G2 │
           ├────┼────┤
           │ G3 │ G4 │
           └────┴────┘

6 Grafik:  ┌────┬────┬────┐
           │ G1 │ G2 │ G3 │
           ├────┼────┼────┤
           │ G4 │ G5 │ G6 │
           └────┴────┴────┘
```

### 4.2 Grafik İle Etkileşim

#### Zoom ve Pan İşlemleri

**Mouse ile:**

| İşlem | Nasıl Yapılır |
|-------|---------------|
| **Zoom In (Yakınlaştır)** | Sol fare tuşu ile dikdörtgen çizin |
| **Pan (Kaydır)** | Sağ fare tuşu ile sürükleyin |
| **Zoom (Tekerlek ile)** | Mouse tekerleğini yukarı/aşağı kaydırın |
| **Reset Zoom** | Grafiğe çift tıklayın |

> 📸 **[Görsel 10: Zoom İşlemleri]**  
> _Sol tık dikdörtgen zoom, sağ tık pan gösterimi_

**Senkronize Zoom:**
- Bir grafikte zoom yaptığınızda **tüm grafikler** aynı zaman aralığını gösterir
- Bu sayede farklı sinyalleri aynı zamanda karşılaştırabilirsiniz

#### Sağ Tık Menüsü

Grafik üzerinde sağ tıkladığınızda:

```
┌─────────────────────┐
│ Auto Range          │ ← Otomatik ölçeklendirme
│ View All            │ ← Tüm veriyi göster
│ Export Image...     │ ← Grafik görselini kaydet
│ Reset to Default    │ ← Varsayılana dön
└─────────────────────┘
```

> 📸 **[Görsel 11: Sağ Tık Menüsü]**  
> _Context menu seçenekleri_

### 4.3 Grafik Özellikleri (Advanced Settings)

Her grafik için ayrı ayrı gelişmiş ayarlar yapabilirsiniz.

**Erişim:**
1. Grafik üzerinde **"⚙️"** ikonuna tıklayın
2. Veya grafik başlığına sağ tıklayıp **"Advanced Settings"** seçin

> 📸 **[Görsel 12: Advanced Settings İkonu]**  
> _Her grafiğin başlığındaki ayarlar ikonu_

#### Normalizasyon (Normalization)

Farklı ölçekteki sinyalleri aynı grafikte göstermek için normalizasyon kullanın.

**Normalizasyon Tipleri:**

1. **None (Yok)**
   - Orijinal değerler gösterilir
   - Aynı birimden sinyaller için

2. **0 to 1**
   - Minimum değer → 0
   - Maksimum değer → 1
   - En yaygın kullanılan

3. **-1 to 1**
   - Minimum değer → -1
   - Maksimum değer → 1
   - Simetrik sinyaller için

4. **Mean Center**
   - Ortalama → 0
   - Değerler ortalamanın etrafında
   - Sapmaları görmek için

5. **Z-Score**
   - Standart sapma normalizasyonu
   - İstatistiksel karşılaştırma için

**Örnek Kullanım:**
```
Grafik 1: Motor Hızı (0-5000 RPM) ve Güç (0-100 kW)
Normalization: 0 to 1
Sonuç: İkisi de 0-1 arasında gösterilir, karşılaştırma kolay
```

> 📸 **[Görsel 13: Normalizasyon Seçenekleri]**  
> _Normalizasyon dropdown menüsü ve etkisi_

#### Grid Ayarları

Grid çizgileri, grafiği okumayı kolaylaştırır.

**Ayarlar:**
- ☑️ **Show X Grid** - Yatay çizgiler (zaman ekseni)
- ☑️ **Show Y Grid** - Dikey çizgiler (değer ekseni)
- **Grid Opacity** - Şeffaflık (0-100%)

**Öneri:** %30-50 opacity değerleri grafiği karıştırmaz.

> 📸 **[Görsel 14: Grid Ayarları]**  
> _Grid açık/kapalı karşılaştırması_

---

## 5. Sinyal Seçimi ve Ayarları

### 5.1 Parameters Paneli

Sol sidebar'daki **Parameters** sekmesi, yüklenen tüm veri kolonlarını gösterir.

> 📸 **[Görsel 15: Parameters Paneli]**  
> _Sol sidebar parameters sekmesi_

**Panel Yapısı:**

Her sinyal için 3 kontrol bulunur:

```
☑️ Signal_Name         🎨 [Renk]  📊 [Graph 1 ▼]
│                       │           │
└─ Aktif/Pasif        └─ Renk     └─ Hangi grafikte
```

### 5.2 Sinyal Seçme

**Bir sinyali grafiğe eklemek için:**

1. **Checkbox'ı işaretleyin (☑️)**
   - Sinyal aktif hale gelir

2. **Grafik seçin (📊 dropdown)**
   - "Graph 1", "Graph 2", vb. seçin
   - Sinyal o grafikte görünür

3. **Renk değiştir (🎨 opsiyonel)**
   - Renk butonuna tıklayın
   - Renk seçici açılır
   - İstediğiniz rengi seçin

> 📸 **[Görsel 16: Sinyal Seçme İşlemi]**  
> _Checkbox işaretleme ve grafik atama adımları_

**Örnek:**
```
Motor test dosyası yüklendi, şu sinyalleri gösterelim:

Graph 1:
  ☑️ Motor_Speed     🔵 Mavi     → Graph 1
  ☑️ Motor_Torque    🔴 Kırmızı  → Graph 1

Graph 2:
  ☑️ Motor_Temp      🟠 Turuncu  → Graph 2
  ☑️ Coolant_Temp    🟢 Yeşil    → Graph 2
```

### 5.3 Toplu İşlemler

Panel üstündeki butonlarla toplu işlem yapabilirsiniz:

**"Select All" (Tümünü Seç)**
- Tüm sinyalleri aktif eder
- Hepsini Graph 1'e atar

**"Deselect All" (Tümünün Seçimini Kaldır)**
- Tüm sinyalleri pasif eder
- Grafikler temizlenir

**"Collapse/Expand All" (Tümünü Topla/Aç)**
- Uzun listelerde paneli temiz tutar

> ⚠️ **Performans İpucu:** Çok fazla sinyal seçmek uygulamayı yavaşlatabilir. Gerekli olanları seçin.

### 5.4 Sinyal Renkleri

**Varsayılan Renkler:**
Time Graph X, sinyallere otomatik renkler atar:
- Mavi, Kırmızı, Yeşil, Turuncu, Mor, Sarı, ...

**Özel Renk Seçme:**
1. Sinyal yanındaki **🎨 renk butonuna** tıklayın
2. Renk seçici açılır
3. Renk paletinden seçim yapın veya RGB/HEX kodu girin
4. **"OK"** ile onayla

> 📸 **[Görsel 17: Renk Seçici Dialog]**  
> _Renk paleti ve RGB/HEX kod girişi_

**Renk İpuçları:**
- 🔴 Kırmızı: Hata, limit aşımı, kritik değerler
- 🟢 Yeşil: Normal çalışma, referans değerler
- 🔵 Mavi: Birincil ölçüm
- 🟠 Turuncu: Sıcaklık değerleri
- 🟣 Mor: Hesaplanan değerler

---

## 6. Cursor Araçları

Cursor araçları, grafikte hassas ölçüm yapmanızı sağlar.

### 6.1 Cursor Modları

Toolbar'da **🎯 "Cursor Mode"** butonu ile 3 mod arasında geçiş yapabilirsiniz:

```
┌─────────────────┐
│ ⊗ None          │ ← Cursor kapalı
│ ┃ Single Cursor │ ← Tek nokta ölçümü
│ ┃┃ Dual Cursor  │ ← İki nokta arası ölçüm
└─────────────────┘
```

> 📸 **[Görsel 18: Cursor Mode Butonu]**  
> _Cursor modu dropdown menüsü_

### 6.2 None Modu (Cursor Kapalı)

**Özellikler:**
- Cursor gösterilmez
- Sadece zoom ve pan kullanılabilir
- Performans maksimum

**Ne Zaman Kullanılır:**
- Genel görünüm için
- Hızlı veri tarama
- Çok sayıda grafikle çalışırken

### 6.3 Single Cursor Modu

**Özellikleri:**
- Tek dikey çizgi
- Mouse'u takip eder
- Tüm grafiklerde senkronize
- O anki değerleri gösterir

> 📸 **[Görsel 19: Single Cursor]**  
> _Tek cursor çizgisi ve değer okuma_

**Kullanım:**
1. **"Single Cursor"** modunu seçin
2. Mouse'u grafik üzerinde hareket ettirin
3. Dikey mavi çizgi mouse'u takip eder
4. Sağ sidebar'da **Statistics** sekmesine bakın
5. "Cursor Values" bölümünde o anki değerler gösterilir

**Statistics Panel'de Görünüm:**
```
═══ Cursor Values ═══
Cursor Position: 2.345 s

Motor_Speed:     2450 RPM
Motor_Torque:    85.3 Nm
Motor_Temp:      72.1 °C
Coolant_Temp:    65.8 °C
```

**Kullanım Senaryoları:**
- Belirli bir zamandaki değerleri okuma
- Anomali noktalarını inceleme
- Hızlı değer kontrolleri

### 6.4 Dual Cursor Modu

**Özellikleri:**
- İki dikey çizgi (Cursor 1, Cursor 2)
- İki nokta arasındaki farkları hesaplar
- Delta (Δ) değerleri gösterir
- Zaman farkı ve değer farkı

> 📸 **[Görsel 20: Dual Cursor]**  
> _İki cursor çizgisi ve delta hesaplaması_

**Kullanım:**
1. **"Dual Cursor"** modunu seçin
2. İlk ölçüm noktasına **sol tıklayın** → **Cursor 1** (Mavi)
3. İkinci ölçüm noktasına **sol tıklayın** → **Cursor 2** (Kırmızı)
4. Statistics panel'de delta değerlerini görün

**Statistics Panel'de Görünüm:**
```
═══ Cursor 1 ═══
Time: 2.345 s
Motor_Speed:     2450 RPM
Motor_Torque:    85.3 Nm

═══ Cursor 2 ═══
Time: 5.890 s
Motor_Speed:     3120 RPM
Motor_Torque:    102.7 Nm

═══ Delta (Δ) ═══
ΔTime:           3.545 s
ΔMotor_Speed:    +670 RPM
ΔMotor_Torque:   +17.4 Nm
```

**Kullanım Senaryoları:**

**1. Yükselme Süresi (Rise Time) Ölçümü:**
```
Motor başlangıç:
Cursor 1: Motor start (0 RPM, t=0s)
Cursor 2: Hedef hız (3000 RPM, t=2.5s)
ΔTime = 2.5s → Rise Time
```

**2. Frekans Hesaplama:**
```
Periyodik sinyalde:
Cursor 1: İlk tepe noktası (t=0.0s)
Cursor 2: İkinci tepe noktası (t=0.02s)
ΔTime = 0.02s → Frekans = 1/0.02 = 50 Hz
```

**3. Efficiency Analizi:**
```
Farklı çalışma noktalarını karşılaştır:
Cursor 1: Düşük hız noktası
Cursor 2: Yüksek hız noktası
ΔTorque / ΔSpeed = Verimlilik değişimi
```

> 📸 **[Görsel 21: Dual Cursor Kullanım Örnekleri]**  
> _Rise time, frekans ve efficiency ölçüm örnekleri_

### 6.5 Cursor İpuçları

**Hassas Yerleştirme:**
- Zoom yaparak cursor'ları daha hassas yerleştirin
- Tepe noktalarını bulmak için max değere zoom yapın

**Cursor Taşıma:**
- Cursor çizgisine tıklayıp sürükleyerek taşıyabilirsiniz

**Senkronizasyon:**
- Cursor'lar tüm grafiklerde aynı zaman noktasını gösterir
- Farklı sinyalleri aynı anda karşılaştırabilirsiniz

---

## 7. İstatistiksel Analiz

### 7.1 Statistics Panel

**Konum:** Sağ sidebar → **"📊 Statistics"** sekmesi

Statistics panel, seçili sinyallerin otomatik hesaplanan istatistiklerini gösterir.

> 📸 **[Görsel 22: Statistics Paneli]**  
> _Statistics panel tam görünüm_

### 7.2 Gösterilen İstatistikler

**Her sinyal için hesaplanan değerler:**

| İstatistik | Açıklama | Formül |
|-----------|----------|--------|
| **Minimum** | En düşük değer | min(x) |
| **Maximum** | En yüksek değer | max(x) |
| **Mean** | Aritmetik ortalama | Σx / n |
| **RMS** | Etkin değer | √(Σx² / n) |
| **Std Dev** | Standart sapma | √(Σ(x-μ)² / n) |
| **Variance** | Varyans | Σ(x-μ)² / n |
| **Peak-to-Peak** | Tepe-tepe değer | max - min |

**Örnek Gösterim:**
```
═══ Motor_Speed ═══
✓ Minimum:        0 RPM
✓ Maximum:     5000 RPM
✓ Mean:        2450 RPM
✓ RMS:         2520 RPM
✓ Std Dev:      620 RPM
✓ Peak-to-Peak: 5000 RPM

═══ Motor_Torque ═══
✓ Minimum:      0.0 Nm
✓ Maximum:    120.5 Nm
✓ Mean:        85.3 Nm
✓ RMS:         87.2 Nm
✓ Std Dev:     18.4 Nm
```

> 📸 **[Görsel 23: İstatistik Değerleri]**  
> _Sinyal bazlı istatistik kartları_

### 7.3 İstatistik Ayarları

**Hangi istatistiklerin gösterileceğini seçebilirsiniz:**

1. Toolbar'da **"⚙️ Statistics Settings"** butonuna tıklayın

2. Statistics Settings Dialog açılır

3. İstediğiniz istatistikleri işaretleyin:
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

4. **"Apply"** butonuna tıklayın

> 📸 **[Görsel 24: Statistics Settings Dialog]**  
> _İstatistik seçim checkbox'ları_

**Performans İpucu:**
- Gereksiz istatistikleri kapatın
- Büyük veri setlerinde hesaplama hızlanır

### 7.4 Cursor ile İstatistik

**Single Cursor:** O anki değerler gösterilir
**Dual Cursor:** İki nokta arası değerler ve delta gösterilir

**Dual Cursor ile Segment İstatistikleri:**
```
═══ Segment Statistics (Cursor 1 → 2) ═══
Time Range: 2.345s - 5.890s (Δ 3.545s)

Motor_Speed (bu aralıkta):
✓ Minimum:     2250 RPM
✓ Maximum:     3120 RPM
✓ Mean:        2685 RPM
```

> 📸 **[Görsel 25: Cursor ile Segment İstatistikleri]**  
> _İki cursor arası bölgenin istatistikleri_

### 7.5 İstatistik Yorumlama

**RMS vs Mean:**
- **Mean:** Basit ortalama
- **RMS:** AC sinyallerde daha anlamlı (elektrik, titreşim)

**Standard Deviation:**
- Düşük: Sinyal stabil
- Yüksek: Sinyal dalgalı, değişken

**Peak-to-Peak:**
- Sinyalin toplam salınım genişliği
- Titreşim analizi için önemli

---

## 8. Filtreleme

Filtreleme, belirli koşulları sağlayan verileri göstermenizi sağlar.

### 8.1 Filters Paneli

**Konum:** Sağ sidebar → **"🔍 Filters"** sekmesi

> 📸 **[Görsel 26: Filters Paneli]**  
> _Filters panel boş hali_

### 8.2 Basit Filtre Ekleme

**Adımlar:**

1. **"Add Filter" butonuna tıklayın**

2. **Filtre ayarlarını yapın:**
   - **Parameter:** Filtrelemek istediğiniz kolonu seçin
   - **Operator:** Karşılaştırma operatörünü seçin
   - **Value:** Eşik değerini girin

3. **"Add" butonuna tıklayın**

**Operatörler:**

| Operator | Anlamı | Örnek |
|----------|--------|-------|
| `>=` | Büyük eşit | Speed >= 1000 |
| `>` | Büyük | Temp > 80 |
| `<=` | Küçük eşit | Pressure <= 5 |
| `<` | Küçük | Voltage < 10 |
| `==` | Eşit | Status == 1 |
| `!=` | Eşit değil | Error != 0 |

**Örnek Filtre:**
```
Motor hızı 1000 RPM'in üzerinde olsun:
Parameter: Motor_Speed
Operator:  >=
Value:     1000
```

> 📸 **[Görsel 27: Filtre Ekleme Dialog]**  
> _Parameter, operator ve value seçimi_

### 8.3 Çoklu Filtre (AND Mantığı)

**Birden fazla filtre ekleyebilirsiniz** - Hepsi aynı anda sağlanmalıdır (AND)

**Örnek:**
```
Filtre 1: Motor_Speed >= 1000
Filtre 2: Motor_Temp < 85
Filtre 3: Voltage > 10

Sonuç: Üç koşulu DA sağlayan satırlar gösterilir
```

> 📸 **[Görsel 28: Çoklu Filtre Listesi]**  
> _Eklenen filtrelerin listesi_

**Filtre Yönetimi:**
- **✕ (Remove):** Belirli bir filtreyi kaldır
- **"Clear All Filters":** Tüm filtreleri temizle
- **☐ Disable:** Filtreyi geçici olarak devre dışı bırak

### 8.4 Filtre Modları

Filtreleme sonuçlarının nasıl gösterileceğini belirler.

#### Segmented Mode (Bölütlenmiş Mod)

**Aktif:** ☑️ "Segmented Mode" işaretli

**Ne yapar?**
- Koşulu **sağlayan bölgeler** gösterilir
- Sağlamayan bölgeler **boşluk olarak** kalır
- Zaman ekseni **orijinal** kalır

**Kullanım:** Hangi zaman aralıklarında koşul sağlanıyor görmek için

**Örnek:**
```
Filtre: Motor_Speed > 2000

Grafik:
  │ ████       ████     ████  │
  └─────────────────────────────┘
    0s   2s   4s   6s   8s   10s

Boşluklar: Motor 2000 RPM altında olduğu anlar
```

> 📸 **[Görsel 29: Segmented Mode Örneği]**  
> _Bölütlenmiş gösterim, boşluklarla_

#### Concatenated Mode (Birleştirilmiş Mod)

**Aktif:** ☐ "Segmented Mode" kapalı

**Ne yapar?**
- Koşulu **sağlayan bölgeler birleştirilir**
- Sağlamayan bölgeler **silinir**
- Zaman ekseni **yeniden oluşturulur**

**Kullanım:** Sadece ilgili verileri analiz etmek için

**Örnek:**
```
Filtre: Motor_Speed > 2000

Grafik:
  │ ██████████████████████████  │
  └─────────────────────────────┘
    Sürekli grafik, düşük hız anları çıkarılmış

Zaman: Yeniden 0'dan başlar
```

> 📸 **[Görsel 30: Concatenated Mode Örneği]**  
> _Birleştirilmiş gösterim, sürekli grafik_

**Hangi Modu Kullanmalı?**

| Amaç | Mod | Nedeni |
|------|-----|--------|
| Zaman bazlı analiz | Segmented | Boşluklar anlamlı |
| Koşul sağlayan verileri analiz | Concatenated | Sürekli grafik |
| Test geçti/kaldı gösterimi | Segmented | Fail noktaları görünür |
| Sadece geçerli veri istatistiği | Concatenated | Hatalı veri hariç |

### 8.5 Filtreleme Örnekleri

**Örnek 1: Motor Çalışma Anları**
```
Filtre: Motor_Speed > 0
Mod: Segmented
Sonuç: Motor durduğunda grafik kesilir
```

**Örnek 2: Kritik Sıcaklık Analizi**
```
Filtre 1: Motor_Temp >= 80
Filtre 2: Motor_Temp <= 95
Mod: Concatenated
Sonuç: Sadece 80-95°C arası veriler analiz edilir
```

**Örnek 3: Hata Durumları**
```
Filtre: Error_Code != 0
Mod: Segmented
Sonuç: Hataların ne zaman oluştuğu görünür
```

---

## 9. Bitmask (Dijital Sinyal) Analizi

Bitmask, dijital sinyalleri bit bit incelemenizi sağlar.

### 9.1 Bitmask Nedir?

**Dijital verilerin bit düzeyinde analizi**

**Ne zaman kullanılır?**
- CAN bus verileri
- Durum bayrakları (status flags)
- Hata kodları
- Digital I/O sinyalleri
- Modbus/Profibus verileri

**Örnek:**
```
Status Register = 0b10110101 (8-bit)

Bit 0 (LSB): Motor Running     → 1 (Açık)
Bit 1:       Temperature Alarm → 0 (Kapalı)
Bit 2:       Overspeed         → 1 (Açık)
Bit 3:       Fault             → 0 (Kapalı)
Bit 4:       Emergency Stop    → 1 (Açık)
Bit 5:       Door Open         → 1 (Açık)
Bit 6:       Reserved          → 0
Bit 7 (MSB): System Ready      → 1 (Açık)
```

### 9.2 Bitmask Paneli

**Konum:** Sağ sidebar → **"🔢 Bitmask"** sekmesi

> 📸 **[Görsel 31: Bitmask Paneli]**  
> _Bitmask panel ve ayarlar_

### 9.3 Bitmask Analizi Yapma

**Adımlar:**

1. **Parameter seçin**
   - Dropdown'dan bitmask içeren kolonu seçin
   - Örnek: "Status_Register", "Error_Code", "Digital_IO"

2. **Bit ayarlarını yapın:**
   - **Bit Count:** Kaç bit analiz edilecek (1-32)
   - **Start Bit:** Başlangıç bit pozisyonu (0 = LSB)

3. **"Analyze" butonuna tıklayın**

**Örnek Ayar:**
```
8-bit Status Register analizi:
Parameter:  Status_Register
Bit Count:  8
Start Bit:  0 (LSB'den başla)
```

> 📸 **[Görsel 32: Bitmask Ayarları]**  
> _Parameter, bit count ve start bit seçimi_

### 9.4 Bit Görselleştirme

**Her bit ayrı bir sinyal olarak gösterilir:**

```
Status_Register_Bit0  (Motor Running)
Status_Register_Bit1  (Temp Alarm)
Status_Register_Bit2  (Overspeed)
...
Status_Register_Bit7  (System Ready)
```

**Grafik Gösterimi:**
- **1 (HIGH):** Yukarıda
- **0 (LOW):** Aşağıda
- Dijital kare dalga şeklinde

> 📸 **[Görsel 33: Bit Grafikleri]**  
> _Her bit için ayrı dijital dalga formu_

### 9.5 Duty Cycle Hesaplama

**Duty Cycle Nedir?**
```
Duty Cycle = (HIGH olduğu süre / Toplam süre) × 100%
```

**Panel'de Gösterim:**
```
═══ Bitmask Analysis ═══
Parameter: Status_Register

Bit 0 (Motor_Running):
  ✓ Duty Cycle:     85.3%
  ✓ Total HIGH:     8.53 s
  ✓ Total LOW:      1.47 s
  ✓ Transitions:    156

Bit 1 (Temp_Alarm):
  ✓ Duty Cycle:     12.7%
  ✓ Total HIGH:     1.27 s
  ✓ Total LOW:      8.73 s
  ✓ Transitions:    24
```

> 📸 **[Görsel 34: Duty Cycle Sonuçları]**  
> _Her bit için duty cycle ve geçiş sayısı_

**Yorumlama:**
- **Yüksek Duty Cycle (>80%):** Genellikle açık
- **Düşük Duty Cycle (<20%):** Genellikle kapalı
- **Orta Duty Cycle (40-60%):** PWM sinyali olabilir
- **Çok geçiş:** Titreşimli sinyal

### 9.6 Threshold Ayarı

**Manual Threshold** ile sinyalin HIGH/LOW sınırını belirleyebilirsiniz.

**Varsayılan:** Otomatik (veri ortalaması)

**Manuel Ayar:**
1. ⚙️ **"Duty Cycle Settings"** butonuna tıklayın
2. ☑️ **"Manual Threshold"** işaretleyin
3. Threshold değerini girin (örn: 2.5V)
4. **"Apply"**

**Örnek:**
```
Analog sinyal: 0-5V
Threshold: 2.5V
> 2.5V → HIGH (1)
< 2.5V → LOW (0)
```

---

## 10. Korelasyon Analizi

İki sinyal arasındaki ilişkiyi ölçer.

### 10.1 Correlations Paneli

**Konum:** Sağ sidebar → **"📈 Correlations"** sekmesi

> 📸 **[Görsel 35: Correlations Paneli]**  
> _Korelasyon tablosu_

### 10.2 Korelasyon Nedir?

**Pearson Korelasyon Katsayısı (r):**
- İki sinyal arasındaki **doğrusal ilişki** gücünü ölçer
- Değer aralığı: **-1 ile +1** arası

**Yorumlama:**

| r Değeri | Anlamı | Örnek |
|----------|--------|-------|
| **r = +1** | Mükemmel pozitif | Hız artarsa güç de artar |
| **r = +0.8** | Güçlü pozitif | Motor yükü artarsa sıcaklık artar |
| **r = +0.5** | Orta pozitif | Hava sıcaklığı artarsa motor sıcaklığı artar |
| **r = 0** | İlişki yok | Hız ile gün ışığı |
| **r = -0.5** | Orta negatif | Hız artarsa verim azalır |
| **r = -1** | Mükemmel negatif | Tam ters ilişki |

### 10.3 Korelasyon Hesaplama

**Otomatik:**
- Panel açıldığında tüm sinyal çiftleri için otomatik hesaplanır

**Manuel:**
- **"Calculate Correlations"** butonuna tıklayın

> 📸 **[Görsel 36: Korelasyon Tablosu]**  
> _Tüm sinyal çiftleri ve korelasyon değerleri_

**Tablo Yapısı:**
```
Signal Pair                    Correlation  Strength
─────────────────────────────────────────────────────
Motor_Speed ↔ Motor_Power        +0.92     Very Strong
Motor_Speed ↔ Vibration          +0.67     Moderate
Motor_Temp ↔ Ambient_Temp        +0.45     Weak
Motor_Speed ↔ Efficiency         -0.35     Weak (Negative)
Voltage ↔ Temperature            +0.12     Very Weak
```

**Strength Levels (Güç Seviyeleri):**

| Seviye | |r| Aralığı | Renk Kodu |
|--------|-----------|-----------|
| **Very Strong** | > 0.8 | 🟢 Yeşil |
| **Strong** | 0.6 - 0.8 | 🟡 Sarı |
| **Moderate** | 0.4 - 0.6 | 🟠 Turuncu |
| **Weak** | 0.2 - 0.4 | 🔴 Kırmızı açık |
| **Very Weak** | < 0.2 | ⚪ Gri |

### 10.4 Scatter Plot Görselleştirme

**İki sinyal arasındaki ilişkiyi görsel olarak görmek için:**

1. Korelasyon tablosunda sinyal çiftine **çift tıklayın**
2. **Scatter Plot** penceresi açılır
3. **X ekseni:** İlk sinyal
4. **Y ekseni:** İkinci sinyal

> 📸 **[Görsel 37: Scatter Plot]**  
> _İki sinyal arası scatter plot grafiği_

**Scatter Plot Yorumlama:**

```
Pozitif Korelasyon:     Negatif Korelasyon:    İlişki Yok:
    ╱╱╱                      ╲╲╲                  ∴∵∴
   ╱╱╱                        ╲╲╲                 ∵∴∵
  ╱╱╱                          ╲╲╲                ∴∵∴
 ╱╱╱                            ╲╲╲               ∵∴∵
```

- **Düz çizgi:** Güçlü korelasyon
- **Dağılmış noktalar:** Zayıf korelasyon
- **Yukarı eğim:** Pozitif
- **Aşağı eğim:** Negatif

### 10.5 Korelasyon Kullanım Örnekleri

**Örnek 1: Motor Performans Analizi**
```
Hız ↔ Güç: r = +0.92 (Very Strong)
Yorum: Hız arttıkça güç de doğrusal olarak artıyor.
       Motor beklenen performansı gösteriyor.
```

**Örnek 2: Soğutma Sistemi Kontrolü**
```
Sıcaklık ↔ Fan Hızı: r = +0.78 (Strong)
Yorum: Sıcaklık arttıkça fan hızı artıyor.
       Soğutma sistemi doğru çalışıyor.
```

**Örnek 3: Anomali Tespiti**
```
Titreşim ↔ Hız: r = +0.15 (Very Weak)
Beklenen: r > 0.6
Yorum: Titreşim hızdan bağımsız artıyor.
       Rulman sorunu olabilir!
```

---

## 11. Sapma Analizi

Bir sinyalin referans sinyalden sapmasını ölçer.

### 11.1 Deviation Paneli

**Konum:** Sağ sidebar → **"📉 Deviation"** sekmesi

> 📸 **[Görsel 38: Deviation Paneli]**  
> _Deviation panel ve ayarlar_

### 11.2 Sapma Analizi Nedir?

**İki sinyal karşılaştırması:**
- **Test Signal:** Test edilen sinyal
- **Reference Signal:** Referans (beklenen) sinyal
- **Deviation:** Test - Reference farkı

**Kullanım Alanları:**
- **Test vs. Referans:** Yeni motor vs. standart profil
- **Before/After:** Bakım öncesi vs. sonrası
- **Tolerans Kontrolü:** Limit değerleri içinde mi?
- **Kalite Kontrol:** Üretim hattı test

### 11.3 Basic Deviation

**Adımlar:**

1. **Test Signal seçin**
   - Test edilecek sinyali dropdown'dan seçin

2. **Reference Signal seçin**
   - Referans sinyali seçin

3. **"Calculate Deviation" butonuna tıklayın**

> 📸 **[Görsel 39: Deviation Ayarları]**  
> _Test ve reference signal seçimi_

**Sonuçlar:**
```
═══ Deviation Analysis ═══

Test:      Motor_Speed_Test
Reference: Motor_Speed_Reference

Max Positive Deviation:  +120 RPM  (t=5.3s)
Max Negative Deviation:  -85 RPM   (t=8.1s)
Mean Absolute Deviation: 35 RPM
RMS Deviation:           42 RPM

Tolerance Check:
  Within ±50 RPM:  92.5% ✓
  Outside limits:  7.5%  ⚠️
```

> 📸 **[Görsel 40: Deviation Sonuçları]**  
> _Sapma metrikleri ve tolerans kontrolü_

### 11.4 Advanced Deviation - Static Limits

**Excel dosyası ile zaman bazlı limit tanımlama:**

**Excel Format:**
```
Time  | Upper_Limit | Lower_Limit
------|-------------|------------
0.0   | 100        | 90
0.5   | 150        | 140
1.0   | 200        | 180
1.5   | 250        | 220
...
```

**Kullanım:**
1. **"Load Limits from Excel"** butonuna tıklayın
2. Excel dosyanızı seçin
3. Limit çizgileri grafikte gösterilir

> 📸 **[Görsel 41: Static Limits Grafiği]**  
> _Üst/alt limit çizgileri ve sapma bölgeleri_

**Grafik Gösterimi:**
- **Yeşil alan:** Tolerans içi (Within limits)
- **Kırmızı alan:** Tolerans dışı (Out of limits)
- **Sapma sinyali:** Deviation değerleri ayrı sinyal olarak

### 11.5 Deviation Kullanım Örnekleri

**Örnek 1: Motor Test Onayı**
```
Test:      Yeni motor hız profili
Reference: Standart hız profili
Limit:     ±50 RPM

Sonuç:
  Max sapma: +45 RPM ✓
  Test PASSED
```

**Örnek 2: Bakım Etkisi**
```
Before: Bakım öncesi titreşim
After:  Bakım sonrası titreşim

Sonuç:
  Mean Deviation: -35% ✓
  Titreşim azalmış, bakım başarılı
```

**Örnek 3: Kalite Kontrol**
```
Test:      Üretilen parça sıcaklık profili
Reference: Standart pişirme profili
Limit:     Excel'den yüklenen zaman bazlı limitler

Sonuç:
  Within limits: 98.5% ✓
  Out of limits: 1.5% (t=45-47s) ⚠️
  Karar: Kabul edilebilir
```

---

## 12. Çoklu Dosya Yönetimi

Time Graph X, aynı anda **3 dosyaya** kadar çalışmanızı destekler.

### 12.1 Çoklu Dosya Nedir?

**Her dosya için ayrı:**
- Grafik düzeni
- Seçili sinyaller
- Cursor pozisyonları
- Filtreler
- Tema ayarları

**Avantajlar:**
- Farklı testleri karşılaştırma
- Before/After analizi
- Çoklu motor testi

> 📸 **[Görsel 42: Dosya Sekmeleri]**  
> _Status bar'da 3 dosya sekmesi_

### 12.2 İkinci Dosya Yükleme

1. **File → Open** ile yeni dosya yükleyin
2. Import dialog'u tamamlayın
3. **Yeni sekme** status bar'da oluşur
4. Otomatik olarak yeni dosyaya geçilir

**Status Bar'da:**
```
┌────────┬────────┬────────┬─────────────┐
│ File 1 │ File 2 │ File 3 │  [Sistem]   │
└────────┴────────┴────────┴─────────────┘
   Aktif  Pasif    Boş      Durum göstergesi
```

### 12.3 Dosyalar Arası Geçiş

**Dosya sekmesine tıklayın:**
- Grafik düzeni otomatik yüklenir
- O dosyanın tüm ayarları geri gelir
- Pencere başlığı değişir

**Performans:**
- Geçiş anında (< 100ms)
- Her dosya hafızada tutulur

### 12.4 Dosya Kapatma

**Sekme üzerindeki ✕ butonuna tıklayın:**

1. Kaydedilmemiş değişiklik varsa **uyarı** verilir
2. Dosya kapatılır
3. Diğer dosyalar açık kalır
4. Tüm dosyalar kapanırsa boş ekran gelir

> ⚠️ **Dikkat:** Dosya kapatıldığında ayarlar kaybolur. Proje olarak kaydetmeyi unutmayın!

### 12.5 Çoklu Dosya Kullanım Örnekleri

**Örnek 1: Before/After Karşılaştırma**
```
File 1: Motor_Before_Maintenance.csv
File 2: Motor_After_Maintenance.csv

Karşılaştırma:
- File 1'e geç → Titreşim değerlerini not et
- File 2'ye geç → Titreşim değerlerini karşılaştır
```

**Örnek 2: Farklı Test Koşulları**
```
File 1: Motor_20C_Ambient.csv
File 2: Motor_40C_Ambient.csv
File 3: Motor_60C_Ambient.csv

Analiz: Ortam sıcaklığının motor performansına etkisi
```

**Örnek 3: Çoklu Motor Test**
```
File 1: Motor_Serial_001.csv
File 2: Motor_Serial_002.csv
File 3: Motor_Serial_003.csv

Kalite Kontrol: Üç motorun performans karşılaştırması
```

---

## 13. Proje Kaydetme ve Yükleme

### 13.1 MPAI Format Nedir?

**Motor Performance Analysis Information (.mpai)**

**Tek dosyada şunları saklar:**
- ✅ Tüm veri (sıkıştırılmış Parquet formatında)
- ✅ Grafik düzeni ve sayısı
- ✅ Seçili sinyaller ve renkleri
- ✅ Cursor pozisyonları
- ✅ Filtreler
- ✅ Tema ayarları
- ✅ Metadata (tarih, orijinal dosya adı, vb.)

**Avantajlar:**

| Özellik | CSV | MPAI |
|---------|-----|------|
| **Yükleme Hızı** | 10-15 saniye | < 1 saniye |
| **Dosya Boyutu** | 25 MB | 8-12 MB |
| **Layout Koruması** | ❌ Hayır | ✅ Evet |
| **Ayar Koruması** | ❌ Hayır | ✅ Evet |
| **Paylaşım** | Zor | ✅ Kolay |

> 📸 **[Görsel 43: MPAI Dosya İkonu]**  
> _.mpai dosya türü ve özellikleri_

### 13.2 Proje Kaydetme

**Adımlar:**

1. **File → Save Project (.mpai)** seçin

2. **Dosya adı girin:**
   - Örnek: `motor_test_20231025.mpai`
   - Açıklayıcı isim kullanın (tarih, test numarası, vb.)

3. **Kaydet** butonuna tıklayın

4. Loading animasyonu gösterilir (1-2 saniye)

5. **Başarılı mesajı:**
   ```
   ✅ Proje başarıyla kaydedildi: motor_test_20231025.mpai
   ```

> 📸 **[Görsel 44: Proje Kaydetme Dialog]**  
> _Save Project dialog ve dosya adı girişi_

**Kaydedilen Metadata:**
```json
{
  "original_file": "motor_data.csv",
  "saved_date": "2023-10-25T14:30:00",
  "time_column": "Time",
  "row_count": 50000,
  "column_count": 24,
  "app_version": "1.0.0"
}
```

### 13.3 Proje Yükleme

**Adımlar:**

1. **File → Open Project (.mpai)** seçin

2. **.mpai dosyanızı seçin**

3. **Otomatik yükleme başlar:**
   - Veri yüklenir (Parquet - çok hızlı!)
   - Grafik düzeni uygulanır
   - Sinyaller seçilir ve renklendirilir
   - Cursor pozisyonları geri gelir
   - Filtreler aktif olur

4. **< 1 saniyede hazır!**

**Status Bar Mesajı:**
```
✅ Proje başarıyla yüklendi: motor_test_20231025.mpai (Parquet - Hızlı!)
```

> 📸 **[Görsel 45: Proje Yükleme]**  
> _Hızlı proje yükleme ve otomatik layout uygulama_

### 13.4 Proje Paylaşımı

**Tek .mpai dosyası paylaşın:**

**Senaryo:**
```
Mühendis A:
- Analizi yapar
- motor_analysis.mpai olarak kaydeder
- Dosyayı e-posta ile gönderir

Mühendis B:
- .mpai dosyasını açar
- Aynı grafik düzeni
- Aynı ayarlar
- Anında çalışmaya başlar
```

**Avantajlar:**
- ✅ Tek dosya - kolay
- ✅ Tekrar üretilebilir sonuçlar
- ✅ Ayar şaşması yok
- ✅ Hızlı paylaşım

### 13.5 Proje Yönetimi İpuçları

**İsimlendirme Önerileri:**
```
✅ İyi:
motor_test_serial123_20231025.mpai
engine_performance_before_maintenance_v1.mpai
quality_check_batch_456_passed.mpai

❌ Kötü:
test.mpai
data1.mpai
son_versiyon_final_son.mpai
```

**Proje Arşivleme:**
```
project_archive/
├── 2023-10/
│   ├── motor_test_20231001.mpai
│   ├── motor_test_20231015.mpai
│   └── motor_test_20231025.mpai
└── 2023-11/
    └── motor_test_20231105.mpai
```

---

## 14. Klavye Kısayolları

Hızlı çalışma için klavye kısayolları:

### 14.1 Dosya İşlemleri

| Kısayol | İşlev |
|---------|-------|
| **Ctrl + O** | Veri Dosyası Aç |
| **Ctrl + S** | Veri Kaydet (CSV/Excel) |
| **Ctrl + Shift + S** | Proje Kaydet (.mpai) |
| **Ctrl + P** | Proje Aç (.mpai) |
| **Ctrl + Q** | Uygulamadan Çık |

### 14.2 Görünüm

| Kısayol | İşlev |
|---------|-------|
| **Ctrl + +** | Zoom In (Yakınlaştır) |
| **Ctrl + -** | Zoom Out (Uzaklaştır) |
| **Ctrl + 0** | Reset Zoom (Otomatik ölçek) |
| **F11** | Tam Ekran Modu |
| **Esc** | Tam Ekrandan Çık |

### 14.3 Analiz Araçları

| Kısayol | İşlev |
|---------|-------|
| **Ctrl + C** | Cursor Mode Değiştir |
| **Ctrl + D** | Dual Cursor Aktif/Pasif |
| **Ctrl + F** | Filtre Ekle |
| **Ctrl + R** | Filtreleri Sıfırla |
| **Ctrl + T** | Statistics Panel Aç/Kapat |
| **Ctrl + B** | Bitmask Panel Aç/Kapat |

### 14.4 Grafik İşlemleri

| Kısayol | İşlev |
|---------|-------|
| **Ctrl + G** | Graph Settings Dialog |
| **Ctrl + 1-6** | Grafik 1-6'yı odakla |
| **Space** | Pan Modu Aktif (basılı tutun) |
| **Çift Tık** | Reset Zoom (fare ile) |

---

## 15. İpuçları ve Püf Noktaları

### 15.1 Performans İpuçları

**Hızlı Yükleme:**
```
✅ İlk yükleme: CSV'den yükleyin
✅ İkinci yükleme: Otomatik Parquet cache kullanılır (8-27x hızlı)
✅ Sık kullanılan veri: .mpai olarak kaydedin
```

**Düzgün Çalışma:**
```
✅ Gereksiz sinyalleri kaldırın (sadece gerekli olanları seçin)
✅ Grafik sayısını sınırlayın (2-3 grafik yeterli çoğunlukla)
✅ Kullanmadığınız istatistikleri kapatın
✅ Dosya boyutunu 15 MB altında tutmaya çalışın
```

**Bellek Yönetimi:**
```
✅ 3 dosya limiti: Her dosya 25 MB → Toplam ~75 MB RAM
✅ Kullanmadığınız dosyaları kapatın
✅ Çok büyük dosyalar: Filtreleme ile küçültün
```

### 15.2 Analiz İpuçları

**Anomali Tespiti:**
```
1. Önce genel görünümü inceleyin (zoom out)
2. İstatistiklere bakın (min, max, std dev)
3. Std dev yüksekse → dalgalanma var
4. Dual cursor ile anomali bölgesini ölçün
```

**Karşılaştırma Analizi:**
```
1. İki dosya açın (Before/After)
2. Aynı grafik düzenini kullanın
3. Aynı normalizasyonu uygulayın (0 to 1)
4. Dosyalar arası geçiş yaparak karşılaştırın
5. Korelasyon analizi ile ilişkileri görün
```

**Test Raporu Hazırlama:**
```
1. Veriyi yükleyin ve analizleri yapın
2. Önemli cursor pozisyonlarını not edin
3. Proje olarak kaydedin (.mpai)
4. Screenshot'lar alın (grafiklerin)
5. İstatistik sonuçlarını kopyalayın
```

### 15.3 Grafik İpuçları

**Renk Seçimi:**
```
🔴 Kırmızı:    Kritik değerler, limitler, hatalar
🟢 Yeşil:      Normal çalışma, referans
🔵 Mavi:       Birincil ölçüm
🟠 Turuncu:    Sıcaklık, uyarı seviyeleri
🟣 Mor:        Hesaplanan değerler, türev
```

**Grafik Düzeni:**
```
✅ İyi Düzen:
Graph 1: Ana performans parametreleri (Hız, Güç)
Graph 2: Sıcaklıklar
Graph 3: Yardımcı parametreler (Akım, Voltaj)

❌ Kötü Düzen:
Tüm sinyaller Graph 1'de (karmaşık)
```

**Normalizasyon Kullanımı:**
```
Aynı birim:   Normalizasyon YOK
Farklı birim: 0 to 1 (en yaygın)
Karşılaştırma: Mean Center veya Z-Score
```

### 15.4 Veri Kalitesi

**Yükleme Öncesi Kontrol:**
```
✅ Dosya boyutu < 25 MB
✅ Türkçe karakter varsa: Encoding = Latin-1
✅ Excel'den kaydedilmişse: Delimiter = Semicolon (;)
✅ Kolon isimleri temiz (boşluk yok, özel karakter yok)
```

**Veri Temizleme:**
```
Time Graph X otomatik temizlik yapar:
✅ NULL değerleri düzeltir
✅ Infinite değerleri temizler
✅ Karışık tipleri çözer
✅ Duplicate isimleri düzenler

Yine de önce Excel'de kontrol etmek iyi olur.
```

### 15.5 Workflow Önerileri

**Günlük Test Rutini:**
```
1. Test verisini yükle
2. Hızlı görsel kontrol (zoom out)
3. Kritik parametreleri seçili tut (template kullan)
4. Otomatik istatistikleri kontrol et
5. Limitlerin dışına çıkma var mı? (Deviation analizi)
6. Proje olarak kaydet (.mpai)
7. Gerekirse rapor oluştur
```

**Sorun Analizi:**
```
1. Problem olan dosyayı yükle
2. Filtreleme ile problem bölgesini izole et
3. Dual cursor ile hassas ölçüm yap
4. Korelasyon analizi ile ilişkileri bul
5. Bitmask ile dijital durumları kontrol et
6. Screenshot al ve dokümante et
```

---

## 16. Sorun Giderme

### 16.1 Yaygın Sorunlar ve Çözümleri

#### Sorun 1: Dosya Yüklenmiyor

**Hata:** "Dosya okunamadı" veya "Import failed"

**Çözümler:**

**Adım 1: Dosya formatını kontrol edin**
```
✅ Desteklenen: .csv, .xlsx, .xls, .mpai
❌ Desteklenmeyen: .txt, .dat, .bin
```

**Adım 2: Delimiter ayarını kontrol edin**
```
Virgül (,):        İngilizce CSV
Noktalı virgül (;): Türkçe Excel CSV
Tab:               Tab-separated
```

**Adım 3: Encoding'i değiştirin**
```
Türkçe karakter hatası → Latin-1 seçin
Garip karakterler → UTF-8 deneyin
```

**Adım 4: Dosya boyutunu kontrol edin**
```
Maksimum: 25 MB
Dosya properties'e sağ tıklayıp kontrol edin
Çok büyükse → Excel'de gereksiz satırları silin
```

> 📸 **[Görsel 46: Import Hata Mesajı]**  
> _Yaygın import hataları ve çözümleri_

#### Sorun 2: Grafik Görünmüyor

**Hata:** Boş grafik ekranı

**Çözümler:**

**Adım 1: Sinyal seçili mi kontrol edin**
```
Sol sidebar → Parameters
Checkbox'lar işaretli mi? ☑️
```

**Adım 2: Grafik ataması yapın**
```
Her sinyal için dropdown'dan grafik seçin:
📊 Graph 1, Graph 2, vb.
```

**Adım 3: Auto Range yapın**
```
Grafik üzerinde:
- Sağ tık → "Auto Range"
- Veya çift tık
```

**Adım 4: Veri tipi kontrolü**
```
String kolonlar grafik yapılamaz!
Sadece sayısal kolonlar gösterilir.
```

#### Sorun 3: Uygulama Yavaş veya Donuyor

**Belirti:** Gecikmeli grafik, donma

**Çözümler:**

**Adım 1: Dosya boyutunu kontrol edin**
```
Mevcut dosya < 25 MB olmalı
Status bar'da satır sayısına bakın
> 100,000 satır → Yavaş olabilir
```

**Adım 2: Gereksiz sinyalleri kaldırın**
```
20 sinyal yerine 5-10 sinyal seçin
Her sinyal hesaplama ve render yükü ekler
```

**Adım 3: Grafik sayısını azaltın**
```
6 grafik → 2-3 grafik
Daha az grafik = Daha hızlı render
```

**Adım 4: İstatistikleri sınırlayın**
```
⚙️ Statistics Settings
Gereksiz istatistikleri kapatın
```

**Adım 5: Filtreleme kullanın**
```
İlgili veri bölgesini filtreleyin
Veri miktarı azalır → Hız artar
```

#### Sorun 4: Cursor Çalışmıyor

**Hata:** Cursor görünmüyor veya değer göstermiyor

**Çözümler:**

**Adım 1: Cursor Mode açık mı?**
```
🎯 Cursor Mode butonu
None değil, Single veya Dual olmalı
```

**Adım 2: Grafiğin içine tıklayın**
```
Grafik alanı içinde mouse hareket ettirin
Dışarıda cursor görünmez
```

**Adım 3: Sinyal seçili olmalı**
```
Cursor değerleri için en az 1 sinyal aktif olmalı
Parameters'dan sinyal seçin
```

**Adım 4: Statistics panel'i açın**
```
Sağ sidebar → Statistics sekmesi
Cursor değerleri orada görünür
```

#### Sorun 5: Türkçe Karakterler Bozuk

**Hata:** ş→?, ğ→?, ı→? gibi görünüyor

**Çözüm:**

**Import Dialog'da:**
```
Encoding: Latin-1 seçin (Türkçe için en iyi)
```

**Alternatif:**
```
CSV'yi Excel'de açın
Farklı kaydet → CSV UTF-8
Time Graph X'te UTF-8 encoding ile açın
```

#### Sorun 6: Proje (.mpai) Açılmıyor

**Hata:** "Invalid project file" veya "Cannot load project"

**Çözümler:**

**Adım 1: Dosya bozulmuş olabilir**
```
Dosya boyutu 0 KB mi?
Yeniden kaydetmeyi deneyin (orijinal CSV'den)
```

**Adım 2: Versiyon uyumsuzluğu**
```
Dosya çok eski bir versiyonla mı kaydedilmiş?
Orijinal CSV'yi yükleyin, yeniden .mpai kaydedin
```

**Adım 3: Dosya yolu çok uzun**
```
Windows'ta 260 karakter limiti var
Dosyayı kısa bir yola taşıyın (örn: C:\Data\)
```

### 16.2 Hata Mesajları ve Anlamları

| Hata Mesajı | Anlamı | Çözüm |
|------------|--------|-------|
| **"File too large"** | > 25 MB | Dosyayı küçültün veya filtreleyin |
| **"Invalid encoding"** | Karakter kodlaması yanlış | Latin-1 veya UTF-8 deneyin |
| **"No numeric columns"** | Sayısal kolon yok | Tüm kolonlar string, veri kontrol edin |
| **"Time column not found"** | Zaman kolonu bulunamadı | Import dialog'da doğru kolon seçin |
| **"Out of memory"** | RAM yetersiz | Daha küçük dosya veya daha az dosya açın |

### 16.3 Log Dosyası

**Detaylı hata bilgisi için log dosyasına bakın:**

**Log Konumu:**
```
Uygulama klasöründe:
time_graph_app.log
```

**Log Açma:**
```
1. Uygulama klasörüne gidin (time_graph_x.exe'nin yanında)
2. time_graph_app.log dosyasını Not Defteri ile açın
3. En altta son hatalar var
```

**Log Örneği:**
```
[2023-10-25 14:30:00] INFO - Uygulama başlatıldı
[2023-10-25 14:30:15] INFO - Dosya yüklendi: motor_data.csv (50000 satır)
[2023-10-25 14:30:20] ERROR - Kolon 'Speed' bulunamadı
[2023-10-25 14:30:25] WARNING - Yüksek NULL oranı: Temperature (%35)
```

> 📸 **[Görsel 47: Log Dosyası]**  
> _Log dosyası içeriği ve hata mesajları_

### 16.4 Uygulamayı Sıfırlama

**Tüm sorunlar devam ediyorsa:**

**Tam Sıfırlama:**
```
1. Uygulamayı kapatın
2. Uygulama klasöründe şunları silin:
   - .cache/ klasörü (Parquet cache)
   - config/ klasörü (Ayarlar)
   - time_graph_app.log (Log)
3. Uygulamayı yeniden başlatın
```

**Sadece Cache Temizleme:**
```
1. Uygulamayı kapatın
2. .cache/ klasörünü silin
3. Yeniden başlatın
(Sadece yükleme hızı ilk seferde yavaş olur)
```

### 16.5 Teknik Destek

**Sorun çözülmediyse:**

📧 **E-posta:** support@timegraphx.com  
🌐 **Web:** www.timegraphx.com/support  
📖 **Döküman:** www.timegraphx.com/docs

**Destek talep ederken şunları ekleyin:**
- Log dosyası (time_graph_app.log)
- Hata mesajının screenshot'u
- Kullandığınız dosya örneği (mümkünse)
- İşletim sistemi ve versiyonu

---

## 📚 Ek Bilgiler

### Versiyon Notları

**v1.0.0 (Ekim 2025)** - İlk Kararlı Sürüm
- ✅ Çoklu dosya desteği (3 dosya)
- ✅ MPAI proje formatı
- ✅ Gelişmiş filtreleme sistemi
- ✅ Deviation analizi
- ✅ Parquet cache (8-27x hızlı)
- ✅ Otomatik veri temizleme
- ✅ Dual cursor ölçüm
- ✅ Korelasyon analizi
- ✅ Bitmask (dijital sinyal) analizi
- ✅ Tema desteği

### Sistem Bilgileri

**Desteklenen Dosya Boyutu:** 25 MB  
**Maksimum Satır Sayısı:** ~1,000,000 satır  
**Maksimum Kolon Sayısı:** Sınırsız (önerilen: < 100)  
**Maksimum Grafik Sayısı:** 6  
**Maksimum Eşzamanlı Dosya:** 3

### Lisans ve Telif Hakkı

**Copyright © 2025 Time Graph X**  
**Tüm hakları saklıdır.**

Bu yazılım ticari lisans altındadır. Kullanım koşulları için lisans sözleşmesine bakınız.

---

## 🎯 Hızlı Başlangıç Özeti

**5 Dakikada Time Graph X:**

```
1. 📁 Dosya yükle        → File → Open → CSV/Excel seç
2. ⚙️ Import ayarları    → Delimiter, Encoding, Zaman kolonu
3. 📊 Grafik düzenle     → Graph Settings → 2-3 grafik seç
4. 🎨 Sinyal seç         → Sol sidebar → Checkbox işaretle
5. 🎯 Ölçüm yap          → Dual Cursor → İki nokta seç
6. 📈 Analiz et          → Statistics, Filters, Correlations
7. 💾 Proje kaydet       → File → Save Project (.mpai)
```

**İyi çalışmalar! 🚀**

---

**Doküman Sonu**

_Bu kılavuz Time Graph X v1.0.0 için hazırlanmıştır._  
_Son Güncelleme: Ekim 2025_

