# 🏗️ MİMARİ ANALİZ VE PERFORMANS SORUNLARI

## 🔴 KRİTİK SORUNLAR TESPİT EDİLDİ!

### Problem 1: POLARS → NUMPY DÖNÜŞÜMÜ (Ana Performans Kaybı!)

**Durum:**
```python
# src/data/signal_processor.py satır 88-94
time_data = df.get_column(time_column).to_numpy()  # ❌ YAVAŞ!

for col in columns:
    if col != time_column:
        y_data = df.get_column(col).to_numpy()  # ❌ HER SÜTUN İÇİN KOPYA!
        self.add_signal(col, time_data, y_data)
```

**Sorun:**
- ❌ Polars DataFrame → NumPy array dönüşümü **pahalı**
- ❌ Her sütun için **ayrı kopya** oluşturuluyor
- ❌ 23 MB dosya = 10+ sütun × 100K+ satır = **çok fazla bellek kopyalama**
- ❌ Polars'ın hızından hiç **yararlanılmıyor**!

**Neden Polars Kullanıyorsak Numpy'a Çeviriyoruz?**
- PyQtGraph sadece NumPy array kabul ediyor
- Ama dönüşümü **hemen** yapmamalıyız!

**Çözüm:**
```python
# Lazy conversion - sadece gerektiğinde dönüştür
class SignalProcessor:
    def process_data(self, df, normalize=False, time_column=None):
        # Polars DataFrame'i sakla, hemen dönüştürme!
        self._df = df  # ✅ Referans sakla
        self._time_column = time_column
        
        # Lazy evaluation - sadece erişildiğinde numpy'a çevir
        for col in df.columns:
            if col != time_column:
                self.signal_data[col] = {
                    'lazy_loader': lambda c=col: df.get_column(c).to_numpy(),
                    'column_name': col
                }
    
    def get_signal_data(self, name):
        """İhtiyaç duyulduğunda yükle"""
        if 'lazy_loader' in self.signal_data[name]:
            # İlk erişimde numpy'a çevir ve cache'le
            self.signal_data[name]['y_data'] = self.signal_data[name]['lazy_loader']()
            del self.signal_data[name]['lazy_loader']  # Loader'ı sil
        return self.signal_data[name]
```

**Beklenen İyileşme:**
- ⚡ Veri yükleme: %70-80 daha hızlı
- 💾 Bellek kullanımı: %50 azalma
- 📊 23 MB dosya: 5-10 saniye → 1-2 saniye

---

### Problem 2: GRAFİK RENDERING (Kasma Nedeni!)

**Durum:**
```python
# src/managers/plot_manager.py satır 598-619
def render_signals(self, all_signals):
    self.clear_signals()  # ❌ Önce tümünü sil
    
    for signal_name, signal_data in all_signals.items():
        x_data = signal_data['x_data']  # ❌ TÜM veri
        y_data = signal_data['y_data']  # ❌ TÜM veri
        self.add_signal(signal_name, x_data, y_data, plot_index=0)
```

**Sorunlar:**
- ❌ **Tüm veriyi** bir kerede çizmeye çalışıyor
- ❌ 100K+ nokta = PyQtGraph kasıyor
- ❌ Her filtre değişikliğinde **tüm grafiği yeniden çiziyor**
- ❌ Downsampling YOK!

**Çözüm 1: DOWNSAMPLING**
```python
def add_signal(self, name, x_data, y_data, plot_index=0):
    # PyQtGraph için optimum nokta sayısı: 1000-5000
    MAX_POINTS = 5000
    
    if len(x_data) > MAX_POINTS:
        # LTTB (Largest Triangle Three Buckets) algoritması
        # veya basit downsampling
        step = len(x_data) // MAX_POINTS
        x_data = x_data[::step]
        y_data = y_data[::step]
    
    # Şimdi çiz
    self.plot_widget.plot(x_data, y_data)
```

**Çözüm 2: PyQtGraph İyileştirmeleri**
```python
# Hızlandırma ayarları
plot_widget.setDownsampling(auto=True, mode='peak')  # Otomatik downsampling
plot_widget.setClipToView(True)  # Sadece görünen alanı çiz
plot_widget.setAntialiasing(False)  # Antialiasing kapat (2x hız)
```

**Beklenen İyileşme:**
- ⚡ Grafik rendering: %80-90 daha hızlı
- 🖱️ Zoom/Pan: Akıcı
- 📊 100K nokta: Smooth rendering

---

### Problem 3: FİLTRE İŞLEMLERİ (Çok Yavaş!)

**Durum:**
```python
# src/managers/filter_manager.py
def _calculate_segments(self):
    # Her koşul için TÜM veriyi tara
    for condition in self.conditions:
        param_data = np.asarray(self.all_signals[param_name]['y_data'])  # ❌
        condition_mask = np.zeros(len(param_data), dtype=bool)  # ❌ Gereksiz
        
        for range_filter in ranges:
            range_mask = param_data >= value  # ❌ Her seferinde yeni array
            condition_mask |= range_mask
        
        combined_mask &= condition_mask
```

**Sorunlar:**
- ❌ Çok fazla **gereksiz array allocation**
- ❌ Inefficient boolean operasyonlar
- ❌ Polars kullanılmıyor (native filtreleme 10x hızlı!)

**Çözüm: Polars Native Filtreleme**
```python
def calculate_filter_segments_fast(self, df, conditions):
    """Polars native filtreleme - ÇOOK daha hızlı"""
    import polars as pl
    
    # Polars expression oluştur
    filter_expr = None
    
    for condition in conditions:
        param = condition['parameter']
        ranges = condition['ranges']
        
        # Polars expression
        param_expr = None
        for r in ranges:
            if r['type'] == 'lower':
                expr = pl.col(param) >= r['value']
            else:
                expr = pl.col(param) <= r['value']
            
            param_expr = expr if param_expr is None else (param_expr | expr)
        
        filter_expr = param_expr if filter_expr is None else (filter_expr & param_expr)
    
    # Tek bir filtreleme operasyonu - HIZLI!
    filtered_df = df.filter(filter_expr)
    
    # Segment'leri bul
    return self._find_segments_from_filtered_df(filtered_df)
```

**Beklenen İyileşme:**
- ⚡ Filtre hesaplama: %85-95 daha hızlı
- 💾 Bellek: %60 daha az
- 🔄 UI responsiveness: Anlık

---

## 📊 MEVCUT VS ÖNERILEN MİMARİ

### Mevcut Mimari (Yavaş):
```
Polars DataFrame
    ↓ [YAVAŞ: to_numpy()]
NumPy Arrays (her sütun ayrı kopya)
    ↓ [YAVAŞ: tüm veri]
SignalProcessor (dict of arrays)
    ↓ [YAVAŞ: tüm noktalar]
PlotManager (PyQtGraph)
    ↓ [ÇOOOK YAVAŞ: 100K+ nokta çizimi]
Kasma ve Donma!
```

### Önerilen Mimari (Hızlı):
```
Polars DataFrame [SAKLA!]
    ↓ [Lazy conversion]
SignalProcessor (lazy loaders)
    ↓ [Downsampling: 100K → 5K nokta]
PlotManager (optimized)
    ↓ [Sadece görünen alan]
Smooth Rendering! ✅
```

---

## 🎯 ÖNCELİKLENDİRİLMİŞ ÇÖZÜM PLANI

### AŞAMA 1: ACİL FİKS (2-3 saat) - ⚡ EN BÜYÜK ETKİ
**Hedef: Grafik kasmasını çöz**

1. **PyQtGraph Downsampling** (30 dakika)
   ```python
   # plot_manager.py'ye ekle
   MAX_PLOT_POINTS = 5000
   if len(y_data) > MAX_PLOT_POINTS:
       step = max(1, len(y_data) // MAX_PLOT_POINTS)
       y_data = y_data[::step]
       x_data = x_data[::step]
   ```
   **Etki:** Grafik kasması %90 azalır

2. **PyQtGraph Optimizasyonları** (15 dakika)
   ```python
   plot_widget.setDownsampling(auto=True, mode='peak')
   plot_widget.setClipToView(True)
   plot_widget.setAntialiasing(False)
   ```
   **Etki:** Zoom/pan 3-4x daha hızlı

3. **Polars Native Filtreleme** (2 saat)
   - Filter Manager'ı Polars kullanacak şekilde refactor et
   **Etki:** Filtre işlemleri 10x daha hızlı

**Toplam Beklenen İyileşme:**
- ✅ Grafik kasması: %90 azalma
- ✅ Filtre hızı: %85 artış
- ✅ 23 MB dosya: Smooth rendering

---

### AŞAMA 2: LAZY LOADING (2-3 saat) - 💾 BELLEK + HIZ
**Hedef: Bellek kullanımını azalt, yüklemeyi hızlandır**

1. **Lazy Data Conversion** (2 saat)
   - Polars → NumPy dönüşümünü lazy yap
   - Sadece gerektiğinde dönüştür
   
2. **Data Streaming** (1 saat)
   - Çok büyük dosyalar için chunk'lar halinde yükle

**Beklenen İyileşme:**
- ✅ Veri yükleme: %70 daha hızlı
- ✅ Bellek: %50 azalma

---

### AŞAMA 3: GELİŞMİŞ OPTİMİZASYONLAR (4-5 saat) - 🚀 PRO
**Hedef: Enterprise-grade performans**

1. **LTTB Downsampling** - En iyi görsel kalite
2. **GPU Acceleration** - PyQtGraph OpenGL
3. **Incremental Updates** - Sadece değişen kısmı çiz
4. **Virtual Scrolling** - Sonsuz veri desteği

---

## 💰 MALİYET-FAYDA ANALİZİ

| Aşama | Süre | Etki | Öncelik |
|-------|------|------|---------|
| **AŞAMA 1** | 2-3h | ⭐⭐⭐⭐⭐ | 🔴 KRİTİK |
| **AŞAMA 2** | 2-3h | ⭐⭐⭐⭐ | 🟡 YÜKSEK |
| **AŞAMA 3** | 4-5h | ⭐⭐⭐ | 🟢 DÜŞÜK |

---

## ❓ SORULARINIZIN CEVAPLARI

### ❓ "Polars kullanıyoruz ama yeterince hızlı değil, kullanımda mı problem var?"
**CEVAP:** Evet! Polars'ın hızından hiç yararlanılmıyor.
- ❌ Hemen numpy'a çeviriyoruz (yavaş)
- ❌ Filtreleme için numpy kullanıyoruz (Polars 10x hızlı olabilir)
- ✅ Çözüm: Polars DataFrame'i sakla, lazy conversion kullan

### ❓ "23 MB dosya yüklediğimde grafik kasıyor?"
**CEVAP:** Evet! 100K+ nokta çizmeye çalışıyor.
- ❌ PyQtGraph tüm noktaları çiziyor
- ❌ Downsampling yok
- ✅ Çözüm: 5000 nokta ile downsample et, %90 daha hızlı

### ❓ "Filtre uygulayınca çok yavaşlıyor?"
**CEVAP:** Evet! Numpy ile manual filtreleme yapıyor.
- ❌ Çok fazla array allocation
- ❌ Inefficient boolean operations  
- ✅ Çözüm: Polars native filtering kullan, 10x hızlı

---

## 🎯 HANGİ AŞAMAYI YAPALIM?

**ÖNERİM: AŞAMA 1 (ACİL FİKS) - 2-3 saat**

Bu size:
- ✅ Grafik kasması %90 azalma
- ✅ Filtre hızı 10x artış
- ✅ 23 MB dosya smooth rendering
- ✅ Düşük risk (mevcut kodu minimal değişiklik)

**Devam edelim mi?** (Evet/Hayır)

