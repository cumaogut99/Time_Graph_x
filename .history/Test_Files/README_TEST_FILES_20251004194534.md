# 🧪 Test Files - Robustness Testing

Bu klasör, Time Graph X uygulamasının veri import robustness'ini test etmek için özel olarak hazırlanmış problematik CSV dosyalarını içerir.

## 📋 Test Dosyaları

### 1️⃣ test_1_mixed_types.csv
**Problem:** Karışık veri tipleri
- String ve sayı karışımı
- Tarih formatı yanlış yerde (9/20/2025)
- ERROR, INVALID gibi metinler sayısal kolonlarda
- NULL, NaN, inf, -inf değerleri

**Beklenen Davranış:**
- ✅ String kolonlar tespit edilip string olarak kalmalı
- ✅ %80+ sayısal kolonlar float'a çevrilmeli
- ✅ NULL/NaN değerleri forward-fill ile doldurulmalı
- ✅ inf/-inf değerleri temizlenmeli

### 2️⃣ test_2_null_heavy.csv
**Problem:** Yoğun NULL değerler (%50+)
- Farklı NULL formatları: "", NULL, NA, NaN, None, N/A, -
- Bazı satırlarda çoklu boş değerler
- Tutarsız boşluk kullanımı

**Beklenen Davranış:**
- ✅ Tüm NULL varyasyonları tespit edilmeli
- ✅ Forward-fill stratejisi uygulanmalı
- ✅ %50+ NULL kolonlar için warning
- ✅ Korelasyon hesaplamalarında bu kolonlar atlanmalı

### 3️⃣ test_3_millisecond_timestamp.csv
**Problem:** Milisaniye cinsinden timestamp
- Değerler 1.7e15 civarında (çok büyük)
- Normal timestamp'in 1000 katı

**Beklenen Davranış:**
- ✅ Otomatik milisaniye tespiti (> 1e12)
- ✅ Saniyeye çevirme (/1000)
- ✅ Datetime axis aktif olmalı
- ✅ X-axis: "01/01/2024 10:00:00" formatında

### 4️⃣ test_4_datetime_strings.csv
**Problem:** String datetime formatı + karışık sorunlar
- "01/01/2024 10:00:00.000" formatı
- FAIL, NULL gibi invalid değerler
- Boş hücreler
- inf değerleri

**Beklenen Davranış:**
- ✅ Datetime parse edilmeli
- ✅ Unix timestamp'e çevrilmeli
- ✅ Invalid değerler temizlenmeli
- ✅ X-axis datetime formatında

### 5️⃣ test_5_inconsistent_columns.csv
**Problem:** Tutarsız kolon sayıları
- Bazı satırlarda eksik kolonlar
- Bazı satırlarda fazla kolonlar
- Extra değerler

**Beklenen Davranış:**
- ✅ Polars `ignore_errors=True` ile atlamalı
- ✅ Eksik değerler NULL olarak doldurulmalı
- ✅ Fazla kolonlar görmezden gelinmeli
- ⚠️ Warning mesajı gösterilmeli

### 6️⃣ test_6_special_characters.csv
**Problem:** Türkçe karakterler ve karışık tipler
- İ, ş, ğ, ü, ö, ç karakterleri
- Şehir isimleri + sayısal değerler karışımı
- UTF-8 encoding testi

**Beklenen Davranış:**
- ✅ UTF-8 encoding düzgün çalışmalı
- ✅ Türkçe kolon isimleri sorun çıkarmamalı
- ✅ Mixed-type detection çalışmalı
- ✅ String kolonlar string olarak kalmalı

### 7️⃣ test_7_extreme_values.csv
**Problem:** Aşırı büyük/küçük değerler
- Çok küçük: 1.2e-10
- Çok büyük: 1.5e15
- inf ve -inf değerleri
- Normal ve negatif değerler

**Beklenen Davranış:**
- ✅ Extreme değerler handle edilmeli
- ✅ inf/-inf temizlenmeli
- ✅ Grafik zoom yapıldığında düzgün görünmeli
- ✅ Korelasyon hesaplarında sorun çıkarmamalı

### 8️⃣ test_8_all_null_column.csv
**Problem:** Tamamen NULL olan kolon
- "all_null_signal" kolonu %100 NULL
- Farklı NULL formatları

**Beklenen Davranış:**
- ✅ Kolon yüklenmeli ama warning verilmeli
- ✅ Korelasyon hesaplamalarında zero variance nedeniyle atlanmalı
- ✅ Grafik çizilmemeli (veya sıfır çizgisi)
- ⚠️ Kullanıcıya bilgi verilmeli

### 9️⃣ test_9_semicolon_delimiter.csv
**Problem:** Noktalı virgül (;) delimiter
- Virgül (,) yerine noktalı virgül
- ERROR, NULL, NA değerleri
- Boş hücreler

**Beklenen Davranış:**
- ✅ Import dialog'da otomatik algılama
- ✅ Delimiter selection çalışmalı
- ✅ Tüm diğer robustness özellikleri çalışmalı

### 🔟 test_10_constant_values.csv
**Problem:** Sabit değerli kolonlar
- constant_100: Her satırda 100.0
- constant_0: Her satırda 0.0
- constant_null: Her satırda NULL

**Beklenen Davranış:**
- ✅ Korelasyon hesaplamalarında zero variance kontrolü
- ✅ Bu kolonlar korelasyon listesinde görünmemeli
- ⚠️ "Zero variance - constant values" uyarısı
- ✅ Grafik çizilmeli ama düz çizgi

## 🎯 Test Stratejisi

### Öncelik 1: Kritik Testler
1. ✅ test_1_mixed_types.csv - En yaygın problem
2. ✅ test_2_null_heavy.csv - Endüstriyel dosyalarda sık
3. ✅ test_3_millisecond_timestamp.csv - Tarih görüntüleme

### Öncelik 2: Önemli Testler
4. ✅ test_4_datetime_strings.csv - String datetime
5. ✅ test_7_extreme_values.csv - Matematiksel sorunlar
6. ✅ test_8_all_null_column.csv - Edge case

### Öncelik 3: Ek Testler
7. ✅ test_5_inconsistent_columns.csv - Format sorunları
8. ✅ test_6_special_characters.csv - Encoding
9. ✅ test_9_semicolon_delimiter.csv - Delimiter
10. ✅ test_10_constant_values.csv - İstatistiksel sorunlar

## 📊 Beklenen Sonuçlar

### Tüm Testlerde Ortak Beklentiler:
- ✅ Uygulama crash etmemeli
- ✅ Veri yüklenebilmeli
- ✅ Sorunlu değerler otomatik düzeltilmeli
- ✅ Kullanıcıya anlamlı mesajlar gösterilmeli
- ✅ Log'da detaylı bilgi olmalı

### Veri Kalite Raporu:
```
📊 Veri Kalite Raporu - test_X.csv
   ✅ Toplam: N satır, M kolon
   ⚠️ Yüksek NULL oranı olan kolonlar: K
      • 'kolon_adi': X NULL (%Y) - otomatik düzeltildi
   📈 Veri kullanıma hazır!
```

## 🔍 Orange Data Mining Yaklaşımı

Orange uygulaması şu stratejileri kullanır:

### 1. Esnek Dosya Okuma
- **Otomatik Delimiter Detection:** Virgül, noktalı virgül, tab, pipe
- **Encoding Detection:** UTF-8, Latin-1, cp1252, vb.
- **Header Detection:** İlk satırın header olup olmadığını analiz

### 2. Veri Doğrulama
- **Type Inference:** Her kolon için optimal veri tipini tespit
- **Missing Value Detection:** Farklı NULL formatlarını tanıma
- **Outlier Detection:** Aşırı değerleri tespit

### 3. Kullanıcı Etkileşimi
- **Import Preview:** Veri önizlemesi ve sorun gösterimi
- **Interactive Fixing:** Kullanıcının sorunları düzeltmesi için seçenekler
- **Detailed Reports:** Hangi satır/kolonlarda ne sorunlar var

### 4. Otomatik Düzeltme
- **Type Coercion:** String'i sayıya çevirme (errors='coerce')
- **Missing Value Imputation:** Forward-fill, mean, median
- **Normalization:** Aşırı değerleri normalize etme

### Time Graph X'te Uygulanan Özellikler:
- ✅ Otomatik delimiter detection (import dialog)
- ✅ Encoding selection (UTF-8, Latin-1, vb.)
- ✅ Type inference ve mixed-type handling
- ✅ NULL value detection (10+ format)
- ✅ Otomatik forward-fill stratejisi
- ✅ Import preview ile veri kalite kontrolü
- ✅ Detaylı log ve kullanıcı bilgilendirme
- ✅ Robust correlation calculation
- ✅ Fallback mechanisms

## 🚀 Test Nasıl Yapılır?

1. Uygulamayı başlat
2. Dosya > Aç
3. Test_Files klasöründen bir dosya seç
4. Import dialog'da önizlemeyi kontrol et
5. Import et
6. Log'da "Veri Kalite Raporu" kontrol et
7. Grafiklerin düzgün çizildiğini doğrula
8. Korelasyon hesaplamalarını test et
9. Zoom in/out yap, datetime axis kontrol et

## ✅ Başarı Kriterleri

- [ ] Tüm 10 test dosyası yüklenebiliyor
- [ ] Hiçbir dosyada crash olmuyor
- [ ] Veri kalite raporları görünüyor
- [ ] Datetime axis düzgün çalışıyor
- [ ] Korelasyonlar hesaplanabiliyor
- [ ] Grafik zoom/pan sorunsuz
- [ ] Log'da anlamlı mesajlar var
- [ ] Kullanıcı uyarıları açıklayıcı

---

**Hazırlayan:** AI Assistant
**Tarih:** 2025-10-04
**Amaç:** Endüstriyel seviyede robustness testi

