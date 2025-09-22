# Time Graph Widget - Kullanım Kılavuzu

## 🚀 Uygulamayı Başlatma

```bash
python simple_app.py
```

## 📁 Dosya Açma İşlemi

### 1. File Menüsünü Kullanma
- Toolbar'daki **📁 File** butonuna tıklayın
- **📂 Open** seçeneğini seçin
- Dosya seçim dialog'u açılacak

### 2. Dosya Seçimi
Desteklenen formatlar:
- **CSV** (*.csv)
- **Excel** (*.xlsx, *.xls) 
- **Parquet** (*.parquet)
- **HDF5** (*.hdf5, *.h5)

### 3. Gelişmiş Import Dialog'u

Dosya seçtikten sonra **Gelişmiş Import Dialog'u** açılır:

#### Sol Panel - Veri Önizlemesi 📋
- **İlk 100 satır** otomatik görüntülenir
- Sütunlara tıklayarak **zaman kolonu** seçebilirsiniz
- Verinin nasıl görüneceğini anlık olarak görebilirsiniz

#### Sağ Panel - Ayarlar ⚙️

##### 🔧 Dosya Format Ayarları
- **Encoding**: utf-8, latin-1, cp1252, vb.
- **Ayırıcı**: Virgül, noktalı virgül, tab, pipe, boşluk
- **🔍 Otomatik Algıla**: Formatı otomatik belirler

##### 📊 Sütun Ayarları  
- **Header Satırı**: Hangi satırda sütun başlıkları var
- **Header Var mı**: Dosyada header olup olmadığını belirtir

##### 📝 Satır Ayarları
- **Veri Başlangıç Satırı**: Verinin hangi satırdan başladığı
- **Atlanacak Satır**: Baştan kaç satır atlanacak

##### ⏰ Zaman Kolonu Ayarları

**Zaman Kolonu Modu**: İki seçenek
- **Mevcut Kolonu Kullan**: Dosyadaki bir sütunu zaman ekseni olarak kullan
- **Yeni Zaman Kolonu Oluştur**: Örnekleme frekansına göre yeni zaman ekseni oluştur

**Mevcut Kolonu Kullan Modu**:
- **Zaman Kolonu**: X ekseni için kullanılacak sütun
- **Zaman Formatı**: Otomatik, tarih formatları, Unix timestamp
- **Zaman Birimi**: Saniye, milisaniye, mikrosaniye, nanosaniye

**🕒 Yeni Zaman Kolonu Oluştur Modu**:
- **Örnekleme Frekansı**: 1 Hz - 1 MHz arası (örn: 1000 Hz = 1 kHz)
- **Başlangıç Zamanı**: 
  - 0 (Sıfırdan Başla)
  - Şimdiki Zaman (gerçek zaman damgası)
  - Özel Zaman (YYYY-MM-DD HH:MM:SS formatında)
- **Zaman Birimi**: Saniye, milisaniye, mikrosaniye, nanosaniye
- **Yeni Kolon Adı**: Oluşturulacak zaman kolonunun adı

### 4. Import İşlemi
- Ayarları yaptıktan sonra **🔄 Önizlemeyi Yenile** ile kontrol edin
- **✅ Import Et** butonu ile veriyi yükleyin
- **❌ İptal** ile işlemi iptal edebilirsiniz

## 📊 Veri Analizi Araçları

### Cursor Modları 🎯
- **❌ None**: Cursor yok
- **⚡ Dual Cursors**: İki cursor ile ölçüm

### Panel Yönetimi
- **📊 Statistics**: İstatistik paneli
- **⚙️ General**: Genel ayarlar
- **📊 Graph Settings**: Grafik ayarları
- **⚙️ Statistics Settings**: İstatistik ayarları
- **📈 Correlations**: Korelasyon analizi
- **🔢 Bitmask**: Bitmask analizi

### Grafik Kontrolü
- **📊 Graphs**: Grafik sayısını ayarlayın (1-10)
- Her grafik için ayrı normalizasyon
- Grid ve autoscale ayarları

## 🎨 Kullanım İpuçları

### Hızlı Başlangıç
1. `python test_data.py` ile test verisi oluşturun
2. `python simple_app.py` ile uygulamayı başlatın  
3. **File > Open** ile `test_data.csv` dosyasını açın
4. Import dialog'unda **time** sütununu zaman kolonu olarak seçin
5. **Import Et** ile veriyi yükleyin

### Etkili Veri Analizi
- **Dual Cursors** ile iki nokta arası ölçüm yapın
- **Statistics Panel** ile anlık değerleri takip edin
- **Correlations** ile sinyaller arası ilişkiyi analiz edin
- **Graph Settings** ile her grafiği özelleştirin

### Performans İpuçları
- Büyük dosyalar için **Parquet** formatını tercih edin
- Gereksiz sütunları import etmeyin
- **Vaex** backend sayesinde milyonlarca satır desteklenir

## 🔧 Sorun Giderme

### Import Sorunları
- **Encoding hatası**: Farklı encoding deneyin (cp1254, latin-1)
- **Delimiter hatası**: Otomatik algıla kullanın
- **Header hatası**: Header satırı ayarını kontrol edin

### Performans Sorunları  
- Çok fazla sütun varsa sadece gerekli olanları seçin
- Büyük dosyalar için HDF5 veya Parquet kullanın
- RAM kullanımını Task Manager'dan takip edin

### Görüntü Sorunları
- **Grafik görünmüyor**: Graph Settings'ten grafik sayısını kontrol edin
- **Cursor çalışmıyor**: Cursor Mode'u kontrol edin
- **İstatistik yok**: Statistics Settings'ten görünür sütunları seçin

## 📋 Klavye Kısayolları

- **Ctrl+O**: Dosya aç
- **Ctrl+S**: Dosya kaydet  
- **Ctrl+Q**: Uygulamadan çık

## 🎯 Örnek Kullanım Senaryoları

### Sensör Verisi Analizi
1. CSV formatında sensör verisi import edin
2. Timestamp sütununu zaman kolonu olarak seçin
3. Dual cursor ile belirli zaman aralığını seçin
4. Statistics panel'den min/max/ortalama değerleri okuyun

### Sinyal İşleme
1. Çoklu sinyal dosyası açın
2. Her sinyali farklı grafikte görüntüleyin
3. Correlations panel ile sinyaller arası korelasyonu hesaplayın
4. Bitmask panel ile dijital sinyalleri analiz edin

### Zaman Serisi Analizi
1. Zaman serisi verisi import edin
2. Normalizasyon uygulayın
3. Cursor ile trend analizi yapın
4. İstatistiksel özellikleri inceleyin

### 🕒 Yeni Zaman Kolonu Kullanım Örnekleri

#### Sensör Verisi (Zaman Kolonu Yok)
1. CSV dosyasında sadece sensör değerleri var
2. **Yeni Zaman Kolonu Oluştur** seçin
3. **Örnekleme Frekansı**: 100 Hz (sensör 100 Hz'de örnekleme yapıyor)
4. **Başlangıç Zamanı**: "Şimdiki Zaman" (gerçek zaman damgası)
5. **Zaman Birimi**: saniye
6. Import edin → Otomatik zaman ekseni oluşturulur

#### Laboratuvar Ölçümü
1. Excel dosyasında ölçüm değerleri var
2. **Yeni Zaman Kolonu Oluştur** seçin  
3. **Örnekleme Frekansı**: 1000 Hz (1 kHz)
4. **Başlangıç Zamanı**: "Özel Zaman" → "2024-01-15 14:30:00"
5. **Zaman Birimi**: milisaniye
6. **Yeni Kolon Adı**: "measurement_time"

#### Yüksek Hızlı Veri Toplama
1. Parquet dosyasında ham veri
2. **Yeni Zaman Kolonu Oluştur** seçin
3. **Örnekleme Frekansı**: 50000 Hz (50 kHz)
4. **Başlangıç Zamanı**: "0 (Sıfırdan Başla)"
5. **Zaman Birimi**: mikrosaniye
6. Import edin → Mikrosaniye hassasiyetinde zaman ekseni

## 📞 Destek

Sorunlarınız için:
- Log dosyasını kontrol edin: `time_graph_app.log`
- Hata mesajlarını kaydedin
- Kullandığınız veri formatını belirtin

---

**Time Graph Widget v1.0** - Gelişmiş Veri Analizi ve Görselleştirme Aracı
