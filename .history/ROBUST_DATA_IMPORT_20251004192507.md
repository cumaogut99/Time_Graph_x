# 🛡️ Robust Data Import System - Teknik Dokümantasyon

## 📋 Genel Bakış

Time Graph X uygulaması artık **ATI Vision benzeri endüstriyel seviyede robust bir veri işleme sistemi**ne sahiptir. Bu sistem, farklı kaynaklardan gelen CSV dosyalarındaki problemleri otomatik olarak tespit edip düzeltir.

## 🎯 Çözülen Problemler

### Problem 1: NULL/None Değerler
**Önceki durum:** `float() argument must be a string or a real number, not 'NoneType'`
**Çözüm:**
- NULL değerleri otomatik tespit (`null_values` listesi)
- Forward-fill stratejisi ile doldurma
- Başarısız olursa 0 ile doldurma

### Problem 2: Karışık Veri Tipleri (Mixed Types)
**Önceki durum:** `could not convert string to float: '9/20/2025'`
**Çözüm:**
- String kolonları sayısal olabilir mi analiz et
- %80+ başarı oranı ile dönüştür
- Başarısız kolonları string olarak bırak
- Tarih formatlarını yanlış yerde kullanmayı önle

### Problem 3: Infinite Değerler (±inf)
**Çözüm:**
- Tüm float kolonlarda ±inf kontrolü
- Inf değerleri NULL'a çevir, sonra forward-fill

### Problem 4: Korelasyon Hesaplama Hataları
**Çözüm:**
- NaN/None/Inf filtreleme
- Minimum 2 valid değer kontrolü
- Sabit değer (zero variance) kontrolü
- Her parametre için try-except koruması

## 🏗️ Sistem Mimarisi

### 3 Katmanlı Koruma Sistemi

```
┌─────────────────────────────────────────────────────┐
│ LAYER 1: Pre-Import Validation                     │
│ - DataValidator ile önizleme                        │
│ - Sorunlu kolonları tespit et ve göster            │
│ - Kullanıcıya bilgi ver                            │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 2: Robust Parsing & Cleaning                 │
│ - Polars robust options (null_values, ignore_errors)│
│ - _sanitize_dataframe() - 4 aşamalı temizlik       │
│   1. Kolon isimleri temizle                         │
│   2. Mixed-type kolonları düzelt                    │
│   3. NULL değerleri handle et                       │
│   4. Infinite değerleri temizle                     │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 3: Safe Mathematical Operations               │
│ - SignalProcessor: Robust numpy conversion          │
│ - Correlation: NaN/Inf filtering, variance check    │
│ - Fallback mechanisms (zero arrays)                 │
└─────────────────────────────────────────────────────┘
```

## 📁 Değiştirilen Dosyalar

### 1. `src/data/data_import_dialog.py`
**Eklenen:** `_validate_data_quality(df)` metodu
- Import öncesi veri kalite kontrolü
- Kullanıcıya sorunları göster
- Otomatik düzeltme bilgisi ver

### 2. `app.py` - DataLoader Sınıfı
**Eklenen Metodlar:**
- `_sanitize_dataframe(df)` - Ana temizlik metodu
- `_clean_column_names(df)` - Kolon ismi standardizasyonu
- `_fix_mixed_type_columns(df)` - Tip dönüşümleri
- `_handle_null_values(df)` - NULL temizleme
- `_clean_infinite_values(df)` - Infinity temizleme
- `_show_data_quality_summary(df, filename)` - Raporlama

**Güncellenen:**
- CSV okuma seçenekleri (`csv_opts`)
  - `ignore_errors: True`
  - `try_parse_dates: False` (manuel kontrol için)
  - `null_values: [liste]` - Tüm NULL varyasyonları
  - `infer_schema_length: 10000`

### 3. `src/managers/correlations_panel_manager.py`
**Güncellenen:** `_calculate_correlations()` metodu
- NaN/None/Inf mask ile filtreleme
- Minimum 2 valid değer kontrolü
- Zero variance kontrolü
- Try-except per parameter
- Detaylı debug logging

### 4. `src/data/signal_processor.py`
**Güncellenen:** `_get_numpy_column()` metodu
- Object type handling (mixed columns)
- pandas.to_numeric ile güvenli dönüşüm
- None → NaN → forward-fill → 0
- Fallback: zero array

## 🔍 Veri Temizleme Stratejileri

### Forward Fill Stratejisi
```python
# Önce forward fill ile boşlukları doldur
df.fill_null(strategy="forward")
# Hala kalan NULL'ları 0 yap
.fill_null(0.0)
```

**Neden forward-fill?**
- Test sistemlerinde önceki değer genelde geçerlidir
- Motor sensörleri kısa süre sabit kalabilir
- 0 yerine gerçekçi bir değer

### Mixed Type Detection
```python
# String kolonunu sayısal olarak dene
numeric_col = df[col].cast(pl.Float64, strict=False)

# Başarı oranını hesapla
success_rate = 1 - ((null_after - null_before) / total_rows)

# %80'den fazlası başarılı ise dönüştür
if success_rate > 0.8:
    df = df.with_columns(numeric_col.alias(col))
```

### Korelasyon Güvenliği
```python
# Geçerli değerler için mask oluştur
mask = (
    ~np.isnan(target) & 
    ~np.isnan(other) & 
    ~np.isinf(target) & 
    ~np.isinf(other) &
    (target != None) &
    (other != None)
)

valid_target = target[mask]
valid_other = other[mask]

# Zero variance kontrolü
if np.std(valid_target) == 0 or np.std(valid_other) == 0:
    skip_column()
```

## 📊 Veri Kalite Raporlama

### Import Dialog'da
- Önizleme sırasında otomatik validasyon
- Sorunlu kolonlar için uyarı mesajı
- "Otomatik düzeltme" bilgisi

### Yükleme Sonrası
- Logger'a detaylı rapor
- NULL oranları ve temizlenen değer sayıları
- Kullanıcıya başarı mesajı

Örnek Log Çıktısı:
```
📊 Veri Kalite Raporu - motor_data.csv
   ✅ Toplam: 10000 satır, 350 kolon
   ⚠️ Yüksek NULL oranı olan kolonlar: 5
      • 'Temperature_3': 2500 NULL (%25.0) - otomatik düzeltildi
      • 'Pressure_12': 1800 NULL (%18.0) - otomatik düzeltildi
   📈 Veri kullanıma hazır!
```

## 🚀 Performans İyileştirmeleri

### 1. Lazy Validation
- Import dialog: İlk 100 satır validasyonu
- Ana yükleme: Tam veri temizleme

### 2. Caching
- DataCacheManager Parquet cache (8-27x hızlı)
- SignalProcessor numpy cache

### 3. Polars Optimization
- `infer_schema_length=10000` - Daha iyi tip tespiti
- `ignore_errors=True` - Hatalı satırları atla
- Zero-copy numpy conversion

## ✅ Test Önerileri

### Test Case 1: NULL Değerler
```csv
Time,Speed,Temperature
0.0,100.5,50.2
0.1,,51.3
0.2,NULL,
0.3,102.3,N/A
```
**Beklenen:** Tüm NULL'lar forward-fill ile doldurulur

### Test Case 2: Mixed Types
```csv
Time,Value,Status
0.0,100.5,OK
0.1,9/20/2025,ERROR
0.2,102.3,OK
```
**Beklenen:** Value kolonu %66 sayısal → String kalır

### Test Case 3: Infinite Values
```csv
Time,Speed
0.0,100.5
0.1,inf
0.2,-inf
0.3,102.3
```
**Beklenen:** inf değerleri forward-fill ile 100.5 ve 102.3 olur

## 🔧 Bakım ve Geliştirme

### Log Seviyeleri
- `logger.info()` - Kullanıcı bilgilendirme
- `logger.debug()` - Detaylı işlem adımları
- `logger.warning()` - Başarısız düzeltmeler
- `logger.error()` - Kritik hatalar

### Yeni Veri Tipi Ekleme
1. `DataValidator` regex pattern ekle
2. `_fix_mixed_type_columns()` özel dönüşüm ekle
3. Test case oluştur

### Performans İzleme
```python
# Temizleme istatistikleri
logger.debug(f"Cleaned {num_cleaned} invalid values")
logger.debug(f"Success rate: %{success_rate*100:.1f}")
```

## 📝 Sürüm Notları

### v1.0 - Robust Import System
- ✅ 3 katmanlı koruma sistemi
- ✅ ATI Vision benzeri robust parsing
- ✅ Otomatik veri temizleme
- ✅ Kullanıcı dostu raporlama
- ✅ Korelasyon güvenliği
- ✅ Performance optimization

---

**Son Güncelleme:** 2025-10-04
**Durum:** Production Ready ✅

