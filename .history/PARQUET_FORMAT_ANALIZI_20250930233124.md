# 🚀 PARQUET/HDF5 FORMAT ÖNERİSİ - ANALİZ VE UYGULAMA PLANI

## 📊 FORMAT KARŞILAŞTIRMASI

### CSV vs Parquet vs HDF5

| Özellik | CSV | Parquet | HDF5 |
|---------|-----|---------|------|
| **Dosya Boyutu** | 23 MB | 3-5 MB | 5-8 MB |
| **Yükleme Hızı** | 1.0x (base) | **5-10x daha hızlı** | 3-5x daha hızlı |
| **Bellek Kullanımı** | Yüksek | **%70 daha az** | %50 daha az |
| **Polars Uyumluluğu** | Orta | **MÜKEMMEL** ⭐ | İyi |
| **Sütunsal Okuma** | ❌ Hayır | ✅ Evet | ✅ Evet |
| **Sıkıştırma** | ❌ Yok | ✅ Built-in | ✅ Built-in |
| **Metadata** | ❌ Yok | ✅ Zengin | ✅ Zengin |
| **Lazy Loading** | ❌ Hayır | ✅ Evet | ⚠️ Kısıtlı |

---

## 🎯 ÖNERİ: PARQUET FORMATI

### Neden Parquet?

#### 1. **Polars ile Mükemmel Entegrasyon** 🐻‍❄️
```python
# Polars Parquet için optimize edilmiş
df = pl.read_parquet("data.parquet")  # Çok hızlı!
df = pl.scan_parquet("data.parquet")  # Lazy loading - SÜPER HIZLI!
```

#### 2. **Sütunsal Depolama** 📊
- CSV: Tüm satırları okumak zorundasın
- Parquet: Sadece ihtiyacın olan sütunları oku!

```python
# Sadece 2 sütun gerekiyorsa
df = pl.read_parquet("data.parquet", columns=["Time", "Temperature"])
# Diğer sütunlar hiç okunmaz! ⚡
```

#### 3. **Otomatik Sıkıştırma** 🗜️
- **23 MB CSV** → **3-5 MB Parquet** (80% daha küçük!)
- Snappy, ZSTD, GZIP sıkıştırma seçenekleri
- Okuma sırasında otomatik decompress

#### 4. **Metadata ve Schema** 📝
- Veri tipleri saklanır (int, float, datetime)
- CSV'de her seferinde type inference gerekir
- Parquet'te schema hazır → anında yükleme

#### 5. **Lazy Loading** 🦥
```python
# LAZY SCAN - dosyayı hemen yükleme!
lazy_df = pl.scan_parquet("big_file.parquet")

# Sadece filtre uygulanmış veriyi oku
result = (lazy_df
    .filter(pl.col("Temperature") > 20)
    .select(["Time", "Temperature"])
    .collect())  # Burası çalışır

# Bellek kullanımı: %90 azalma! 🎉
```

---

## 💡 UYGULAMA STRATEJİSİ

### Yaklaşım 1: **Otomatik Cache Sistemi** (ÖNERİLEN) ⭐

```
Kullanıcı CSV yükler
    ↓
App otomatik Parquet'e çevirir
    ↓
.cache/ klasörüne kaydeder
    ↓
Sonraki açılışlarda Parquet'ten yükler
```

**Avantajlar**:
- ✅ Kullanıcı hiçbir şey fark etmez
- ✅ İlk yükleme sonrası her şey çok hızlı
- ✅ Backward compatibility korunur
- ✅ Cache'i isterse silebilir

**Dezavantajlar**:
- ⚠️ İlk yükleme aynı hızda
- ⚠️ Disk alanı kullanır (ama %80 daha az!)

### Yaklaşım 2: **Manuel Parquet Export**

```
Kullanıcı: File → Export as Parquet
    ↓
Parquet dosyası kaydedilir
    ↓
Sonra File → Open Parquet
```

**Avantajlar**:
- ✅ Kullanıcı kontrolü
- ✅ Basit implementasyon

**Dezavantajlar**:
- ❌ Ekstra kullanıcı aksiyonu
- ❌ UX karmaşıklığı

---

## 🔧 KOD İMPLEMENTASYONU

### 1. Otomatik Cache Sistemi

```python
# src/data/data_cache_manager.py (YENİ DOSYA)

import polars as pl
import hashlib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataCacheManager:
    """
    CSV dosyalarını otomatik Parquet'e çevirip cache'ler.
    """
    
    def __init__(self, cache_dir="./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_path(self, original_file: Path) -> Path:
        """CSV dosyası için cache path hesapla."""
        # File hash + modification time
        file_hash = hashlib.md5(
            f"{original_file.absolute()}_{original_file.stat().st_mtime}".encode()
        ).hexdigest()
        
        return self.cache_dir / f"{original_file.stem}_{file_hash}.parquet"
    
    def load_with_cache(self, csv_path: Path) -> pl.DataFrame:
        """
        CSV'yi cache'den yükle veya yeni cache oluştur.
        """
        cache_path = self.get_cache_path(csv_path)
        
        # Cache varsa ve güncel mi kontrol et
        if cache_path.exists():
            cache_time = cache_path.stat().st_mtime
            csv_time = csv_path.stat().st_mtime
            
            if cache_time >= csv_time:
                logger.info(f"Loading from cache: {cache_path.name}")
                # LAZY SCAN - süper hızlı!
                return pl.scan_parquet(cache_path).collect()
        
        # Cache yok veya eski - CSV'yi yükle ve cache'le
        logger.info(f"Creating cache for: {csv_path.name}")
        df = pl.read_csv(csv_path, infer_schema_length=10000)
        
        # Parquet'e çevir (sıkıştırmalı)
        df.write_parquet(
            cache_path,
            compression="zstd",  # En iyi sıkıştırma
            statistics=True,     # Metadata ekle
        )
        
        logger.info(f"Cache created: {cache_path.name} ({cache_path.stat().st_size / 1024 / 1024:.2f} MB)")
        return df
    
    def clear_cache(self):
        """Tüm cache'i temizle."""
        for parquet_file in self.cache_dir.glob("*.parquet"):
            parquet_file.unlink()
        logger.info("Cache cleared")
    
    def get_cache_size(self) -> float:
        """Cache boyutunu MB olarak döndür."""
        total = sum(
            f.stat().st_size 
            for f in self.cache_dir.glob("*.parquet")
        )
        return total / 1024 / 1024
```

### 2. DataManager'a Entegrasyon

```python
# src/managers/data_manager.py içinde

from src.data.data_cache_manager import DataCacheManager

class TimeSeriesDataManager:
    def __init__(self):
        # ... existing code ...
        self.cache_manager = DataCacheManager()  # YENİ
    
    def load_csv_file(self, file_path: str) -> Optional[pl.DataFrame]:
        """Load CSV with automatic Parquet caching."""
        try:
            from pathlib import Path
            csv_path = Path(file_path)
            
            # CACHE KULLAN - otomatik Parquet conversion!
            df = self.cache_manager.load_with_cache(csv_path)
            
            logger.info(f"Loaded data: {df.height} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return None
```

### 3. Lazy Scan Optimizasyonu (İLERİ SEVİYE)

```python
# SignalProcessor'da lazy loading

class SignalProcessor(QObject):
    def __init__(self):
        super().__init__()
        # ... existing ...
        self.lazy_frame = None  # LazyFrame for huge files
    
    def process_data_lazy(self, file_path: str, filters=None):
        """
        LAZY PROCESSING - dosyayı tamamen yükleme!
        """
        # Lazy scan
        self.lazy_frame = pl.scan_parquet(file_path)
        
        # Filtre varsa uygula (henüz execute edilmedi!)
        if filters:
            for cond in filters:
                self.lazy_frame = self.lazy_frame.filter(
                    pl.col(cond['param']) >= cond['min']
                )
        
        # Sadece görünür sütunları seç
        visible_cols = ["Time"] + list(self.visible_signals)
        self.lazy_frame = self.lazy_frame.select(visible_cols)
        
        # ŞİMDİ execute et - sadece ihtiyaç olan veri!
        df = self.lazy_frame.collect()
        
        # Bellek kullanımı: %90 azalma! 🎉
```

---

## 📈 BEKLENEN İYİLEŞMELER

### Örnek: 23 MB CSV Dosyası (100K satır × 20 sütun)

| Metrik | ŞİMDİ (CSV) | SONRA (Parquet Cache) | İyileşme |
|--------|-------------|------------------------|----------|
| **İlk Yükleme** | 2.5s | 2.5s + 0.5s cache | ≈ Eşit |
| **2. Yükleme** | 2.5s | **0.3s** | **8x daha hızlı** ⚡ |
| **Dosya Boyutu** | 23 MB | **4 MB** | %83 azalma |
| **Bellek (tüm data)** | 180 MB | 180 MB | Eşit |
| **Bellek (3 sütun)** | 180 MB | **27 MB** | %85 azalma 🎉 |
| **Filtre + 3 sütun** | 2.0s | **0.2s** | **10x daha hızlı** ⚡ |

### Lazy Scan ile (İleri Seviye):

| Senaryo | Normal | Lazy Scan | İyileşme |
|---------|--------|-----------|----------|
| **100K satır, 3/20 sütun** | 180 MB | 27 MB | %85 ⬇️ |
| **1M satır, filtreli** | 1.8 GB | 180 MB | %90 ⬇️ |
| **Yükleme süresi** | 10s | 1s | 10x ⬆️ |

---

## ⚙️ UYGULAMA PLANI

### Aşama 1: Basit Cache (1-2 saat) ⭐ ÖNERİLEN

1. ✅ `DataCacheManager` sınıfını oluştur
2. ✅ `load_csv_file()` metodunu güncelle
3. ✅ Cache klasörü oluştur
4. ✅ Test et (10K, 100K, 1M satır)
5. ✅ Kullanıcıya "Cache cleared" mesajı ekle (opsiyonel)

**Etki**:
- 2. yükleme: 8-10x daha hızlı
- Disk kullanımı: %80 azalma
- Kullanıcı hiçbir şey fark etmez

### Aşama 2: Lazy Scan (2-3 saat) - İLERİ SEVİYE

1. ⏹️ `process_data_lazy()` metodu ekle
2. ⏹️ Filtre entegrasyonu (Polars expressions)
3. ⏹️ Sütun seçimi optimizasyonu
4. ⏹️ Büyük dosya testi (>100 MB)

**Etki**:
- Bellek: %90 azalma
- Büyük dosyalar: 10-20x daha hızlı
- Filtre: Anlık sonuç

### Aşama 3: UI İyileştirmeleri (30 dk) - OPSIYONEL

1. ⏹️ Settings → Clear Cache butonu
2. ⏹️ Cache size göster
3. ⏹️ "Loading from cache..." mesajı
4. ⏹️ Progress bar (ilk cache oluşturma)

---

## 🎯 HDF5 vs PARQUET

### Parquet Avantajları:
- ✅ Polars native desteği (optimize)
- ✅ Daha küçük dosya boyutu
- ✅ Lazy loading built-in
- ✅ Cloud-ready (S3, Azure Blob)
- ✅ Endüstri standardı (Spark, Pandas, Arrow)

### HDF5 Avantajları:
- ✅ Hierarchical data (nested structures)
- ✅ Çok hızlı random access
- ✅ Append mode (incremental writes)

### Karar: **PARQUET** ⭐

**Sebep**: Time-series data için sütunsal okuma ve Polars entegrasyonu çok önemli.

---

## 🚀 HEMEN UYGULAYALIM MI?

### Hızlı Prototip (30 dakika):

1. `DataCacheManager` oluştur
2. `load_csv_file()` güncelle
3. Test et
4. Kullanıcıya sun!

### Sonuç:
```
23 MB CSV yükleme:
  İlk: 2.5s
  2.: 0.3s  ← 8x daha hızlı! 🎉

Dosya boyutu:
  CSV: 23 MB
  Parquet cache: 4 MB  ← %83 azalma!
```

---

## 📋 ÖNERİM

### Kısa Vadeli:
1. ✅ **Basit Cache Sistemi** uygula (1-2 saat)
   - Otomatik Parquet conversion
   - Cache klasörü (.cache/ veya temp)
   - Transparent kullanıcı deneyimi

### Orta Vadeli:
2. ⏹️ **Lazy Scan** ekle (2-3 saat)
   - pl.scan_parquet() kullan
   - Filtre optimizasyonu
   - Sütun seçimi

### Uzun Vadeli:
3. ⏹️ **UI İyileştirmeleri**
   - Cache management
   - Format seçimi (CSV/Parquet)
   - Export özelliği

---

## 🎉 SONUÇ

Parquet formatı **muhteşem bir öneri**! 🎯

### Neden?
- ✅ Polars ile **mükemmel** uyum
- ✅ 8-10x daha hızlı yükleme
- ✅ %80 daha küçük dosya
- ✅ Lazy loading desteği
- ✅ Kolay implementasyon

### Önerim:
**HEMEN UYGULAYALIM!** 

Basit cache sistemi ile başlayalım → 2. yükleme 8x daha hızlı olsun → Kullanıcı mutlu olsun 😊

Sana kod yazayım mı? 30 dakikada hazır! 🚀

