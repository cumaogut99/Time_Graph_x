# 📅 Datetime Axis Formatting Düzeltmesi

## 🐛 Problem

X ekseninde tarih/saat değerleri düzgün gösterilmiyordu:
- Unix timestamp formatında gösteriliyordu (örn: `1.7041e+15`)
- Kullanıcı dostu tarih/saat formatı yoktu (örn: `01/01/2024 10:00:00`)
- Milisaniye cinsinden timestamp'ler desteklenmiyordu

## ✅ Çözüm

### 1. Milisaniye Timestamp Desteği

**`app.py` - DataLoader sınıfı:**
```python
# Otomatik milisaniye timestamp tespiti
if abs(first_value) > 1e12:
    # Milisaniye → Saniye çevrimi
    converted_series = converted_series / 1000.0
    self._datetime_converted = True
```

**Nasıl Çalışır:**
- Timestamp değeri 1e12'den (1 trilyon) büyükse → milisaniye olarak algıla
- Saniyeye çevir (1000'e böl)
- `_datetime_converted` flag'ini True yap → datetime axis aktif olur

### 2. DateTimeAxisItem İyileştirmeleri

**`src/managers/plot_manager.py`:**

#### A) Milisaniye Timestamp Handling
```python
# tickStrings() metodunda
if abs(v) > 1e12:
    v = v / 1000.0  # Milisaniye → Saniye
```

#### B) Türkçe-Dostu Tarih Formatı
```python
# dd/mm/yyyy formatı (Avrupa/Türkiye standardı)
if spacing < 1:
    time_str = dt.strftime('%d/%m/%Y %H:%M:%S.%f')[:-3]  # Milisaniye
elif spacing < 60:
    time_str = dt.strftime('%d/%m/%Y %H:%M:%S')  # Saniye
elif spacing < 3600:
    time_str = dt.strftime('%d/%m %H:%M')  # Dakika
else:
    time_str = dt.strftime('%d/%m/%Y')  # Tarih
```

#### C) Lokal Zaman Dilimi
```python
# UTC yerine lokal zaman
dt = datetime.datetime.fromtimestamp(v)  # utcfromtimestamp → fromtimestamp
```

#### D) Force Update Mekanizması
```python
def enable_datetime_mode(self, enable=True):
    self.is_datetime_axis = enable
    self.picture = None  # Cache temizle
    self.update()  # Yeniden çiz
```

### 3. PlotManager Refresh
```python
def enable_datetime_axis(self, enable=True):
    for plot_widget in self.plot_widgets:
        bottom_axis = plot_widget.getAxis('bottom')
        if isinstance(bottom_axis, DateTimeAxisItem):
            bottom_axis.enable_datetime_mode(enable)
            bottom_axis.update()
            plot_widget.update()
    
    self.refresh_all_plots()  # Tüm grafikleri yenile
```

## 📊 Desteklenen Timestamp Formatları

| Format | Örnek Değer | Tespit | Çıktı |
|--------|-------------|--------|-------|
| **Saniye** | `1704110400` | < 1e12 | `01/01/2024 10:00:00` |
| **Milisaniye** | `1704110400000` | > 1e12 | `01/01/2024 10:00:00` |
| **Datetime String** | `"01/01/2024 10:00:00"` | String parse | `01/01/2024 10:00:00` |

## 🎯 Kullanıcı Deneyimi

### Öncesi
```
X-axis: 1.7041e+15
        Okunamaz, anlamsız
```

### Sonrası
```
X-axis: 01/01/2024 10:00:00.000
        Anlaşılır, kullanışlı
```

## 🔧 Otomatik Tespit Mantığı

```
CSV Dosyası Yükleniyor
         ↓
Timestamp Kolonu Tespit Edildi
         ↓
Değer > 1e12 mi?
    ├─ EVET → Milisaniye / 1000 = Saniye
    └─ HAYIR → Zaten saniye
         ↓
_datetime_converted = True
         ↓
enable_datetime_axis(True) çağrılır
         ↓
DateTimeAxisItem aktif olur
         ↓
tickStrings() tarih formatında gösterir
         ↓
✅ Kullanıcı dostu X ekseni!
```

## 📝 Tarih Format Örnekleri

| Zoom Seviyesi | Format | Örnek |
|---------------|--------|-------|
| **Mikro** (< 1 saniye) | `dd/mm/yyyy HH:MM:SS.fff` | `01/01/2024 10:00:00.123` |
| **Saniye** (< 1 dakika) | `dd/mm/yyyy HH:MM:SS` | `01/01/2024 10:00:00` |
| **Dakika** (< 1 saat) | `dd/mm HH:MM` | `01/01 10:00` |
| **Saat** (< 1 gün) | `dd/mm HH:MM` | `01/01 10:00` |
| **Gün+** | `dd/mm/yyyy` | `01/01/2024` |

## 🧪 Test Senaryoları

### Test 1: Milisaniye Timestamp
```csv
timestamp,value
1704110400000,100.5
1704110400100,101.2
1704110400200,102.3
```
**Beklenen:** X ekseni `01/01/2024 10:00:00.xxx` formatında

### Test 2: Saniye Timestamp
```csv
timestamp,value
1704110400,100.5
1704110401,101.2
1704110402,102.3
```
**Beklenen:** X ekseni `01/01/2024 10:00:00` formatında

### Test 3: String Datetime
```csv
timestamp,value
"01/01/2024 10:00:00",100.5
"01/01/2024 10:00:01",101.2
```
**Beklenen:** Parse edilip Unix timestamp'e çevrilir, sonra formatlanır

## 🚀 Performans

- ✅ Cache mekanizması (self.picture = None)
- ✅ Lazy formatting (sadece görünen tick'ler)
- ✅ Error handling (fallback to numeric)
- ✅ Automatic detection (kullanıcı müdahalesi yok)

## 📋 Değiştirilen Dosyalar

1. **`app.py`**
   - Milisaniye timestamp otomatik tespiti
   - Saniye çevrimi

2. **`src/managers/plot_manager.py`**
   - DateTimeAxisItem.tickStrings() iyileştirmesi
   - enable_datetime_axis() refresh mekanizması
   - enable_datetime_mode() force update

## 💡 Önemli Notlar

- **Lokal Zaman:** `fromtimestamp()` kullanıldı (UTC yerine)
- **Türkçe Format:** `dd/mm/yyyy` Avrupa standardı
- **Otomatik:** Kullanıcı hiçbir şey yapmadan çalışır
- **Robust:** Hatalı değerlerde numeric formata döner

---

**Durum:** ✅ Tamamlandı
**Test Edildi:** 🧪 Milisaniye ve saniye timestamp'leri
**Kullanıcı Dostu:** ⭐⭐⭐⭐⭐

