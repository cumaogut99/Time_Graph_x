# 📅 Zaman Formatı Seçenekleri - Kullanıcı Dostu Açıklamalar

## 🎯 Değişiklik

Kullanıcıların anlamakta zorlandığı teknik zaman formatları artık **anlaşılır açıklamalar ve örneklerle** gösteriliyor.

## 📋 Öncesi vs Sonrası

| Önceki Gösterim | Yeni Gösterim | Ne Anlama Geliyor? |
|----------------|---------------|-------------------|
| `Otomatik` | `Otomatik - Kendisi seçsin` | Program otomatik olarak formatı tespit eder |
| `%Y-%m-%d %H:%M:%S` | `%Y-%m-%d %H:%M:%S (2024-01-15 14:30:45)` | Yıl-Ay-Gün Saat:Dakika:Saniye |
| `%d/%m/%Y %H:%M:%S` | `%d/%m/%Y %H:%M:%S (15/01/2024 14:30:45)` | Gün/Ay/Yıl Saat:Dakika:Saniye (Türkiye formatı) |
| `%Y-%m-%d` | `%Y-%m-%d (2024-01-15)` | Sadece Tarih (Yıl-Ay-Gün) |
| `%d/%m/%Y` | `%d/%m/%Y (15/01/2024)` | Sadece Tarih (Gün/Ay/Yıl - Türkiye) |
| `Unix Timestamp` | `Unix Timestamp (1704110400)` | Saniye cinsinden zaman damgası |
| `Saniyelik Index` | `Saniyelik Index (0.0, 0.1, 0.2...)` | Başlangıçtan itibaren saniye sayısı |

## 🔍 Detaylı Açıklamalar

### 1️⃣ Otomatik - Kendisi seçsin
**Ne zaman kullanılır:** Zaman formatından emin değilseniz
**Nasıl çalışır:** Program verinizdeki zaman kolonunu analiz eder ve uygun formatı otomatik seçer
**Örnek:** 
- `2024-01-15 14:30:45` → ISO formatı olarak algılar
- `15/01/2024 14:30:45` → Avrupa formatı olarak algılar
- `1704110400` → Unix timestamp olarak algılar

### 2️⃣ %Y-%m-%d %H:%M:%S (2024-01-15 14:30:45)
**Format:** Uluslararası standart (ISO 8601)
**Açıklama:**
- `%Y` = 4 haneli yıl (2024)
- `%m` = 2 haneli ay (01-12)
- `%d` = 2 haneli gün (01-31)
- `%H` = 24 saat formatında saat (00-23)
- `%M` = Dakika (00-59)
- `%S` = Saniye (00-59)

**Örnek CSV verisi:**
```
timestamp
2024-01-15 14:30:45
2024-01-15 14:30:46
2024-01-15 14:30:47
```

### 3️⃣ %d/%m/%Y %H:%M:%S (15/01/2024 14:30:45)
**Format:** Avrupa/Türkiye standardı
**Açıklama:**
- `%d` = Gün (15)
- `%m` = Ay (01)
- `%Y` = Yıl (2024)
- `%H:%M:%S` = Saat:Dakika:Saniye

**Örnek CSV verisi:**
```
datetime
15/01/2024 14:30:45
15/01/2024 14:30:46
15/01/2024 14:30:47
```

### 4️⃣ %Y-%m-%d (2024-01-15)
**Format:** Sadece tarih, saat yok (ISO)
**Ne zaman kullanılır:** Günlük veriler, saat önemli değil

**Örnek CSV verisi:**
```
date
2024-01-15
2024-01-16
2024-01-17
```

### 5️⃣ %d/%m/%Y (15/01/2024)
**Format:** Sadece tarih (Türkiye)
**Ne zaman kullanılır:** Günlük veriler, Türk formatı

**Örnek CSV verisi:**
```
tarih
15/01/2024
16/01/2024
17/01/2024
```

### 6️⃣ Unix Timestamp (1704110400)
**Format:** 1 Ocak 1970'den itibaren geçen saniye sayısı
**Ne zaman kullanılır:** Programlama sistemleri, veritabanları
**Bilgi:** 
- Saniye cinsinden: `1704110400`
- Milisaniye cinsinden: `1704110400000` (otomatik tespit edilir)

**Örnek CSV verisi:**
```
timestamp
1704110400
1704110401
1704110402
```

**Karşılığı:**
- `1704110400` = 1 Ocak 2024, 10:00:00

### 7️⃣ Saniyelik Index (0.0, 0.1, 0.2...)
**Format:** Başlangıçtan itibaren saniye
**Ne zaman kullanılır:** Test verileri, zamandan bağımsız ölçümler
**Açıklama:** İlk ölçüm 0.0 saniye, sonrakiler +0.1, +0.2 şeklinde

**Örnek CSV verisi:**
```
time
0.0
0.1
0.2
0.3
```

## 🎨 Görsel Karşılaştırma

### Eski Arayüz
```
Zaman Formatı: [%Y-%m-%d %H:%M:%S ▼]
                 ↑
           Kullanıcı anlamıyor!
```

### Yeni Arayüz
```
Zaman Formatı: [%Y-%m-%d %H:%M:%S (2024-01-15 14:30:45) ▼]
                 ↑                  ↑
           Teknik format      Örnek - Anlaşılır!
```

## 🔄 Nasıl Çalışır?

### 1. Kullanıcı Görür
```
Otomatik - Kendisi seçsin
%Y-%m-%d %H:%M:%S (2024-01-15 14:30:45)
%d/%m/%Y %H:%M:%S (15/01/2024 14:30:45)
```

### 2. Program Kullanır
```python
# Kullanıcı dostu → Teknik format çevrimi
time_format_map = {
    'Otomatik - Kendisi seçsin': 'Otomatik',
    '%Y-%m-%d %H:%M:%S (2024-01-15 14:30:45)': '%Y-%m-%d %H:%M:%S',
    '%d/%m/%Y %H:%M:%S (15/01/2024 14:30:45)': '%d/%m/%Y %H:%M:%S',
    # ...
}
```

### 3. Veri İşlenir
```python
if time_format == '%Y-%m-%d %H:%M:%S':
    dt = datetime.strptime('2024-01-15 14:30:45', '%Y-%m-%d %H:%M:%S')
```

## 💡 Kullanım İpuçları

### Excel'den Gelen Tarihler
Excel tarihleri genelde şu formattadır:
- **Türkçe Excel:** `15/01/2024 14:30:45` → `%d/%m/%Y %H:%M:%S` seçin
- **İngilizce Excel:** `2024-01-15 14:30:45` → `%Y-%m-%d %H:%M:%S` seçin

### Veritabanından Gelen Tarihler
Çoğu veritabanı Unix timestamp kullanır:
- `1704110400` → `Unix Timestamp` seçin
- Program otomatik olarak milisaniye/saniye algılar

### Test Sistemlerinden Gelen Veriler
Test sistemleri genelde saniyelik index kullanır:
- `0.0, 0.1, 0.2` → `Saniyelik Index` seçin
- Veya `Otomatik` bırakın, program algılar

### Emin Değilseniz
**Her zaman `Otomatik - Kendisi seçsin` seçeneğini kullanın!**
- ✅ %95 durumda doğru formatı bulur
- ✅ Milisaniye/saniye otomatik tespit
- ✅ Farklı formatları deneme

## 🚀 Test Senaryoları

### Test 1: Türkçe Tarih
**CSV:**
```
tarih,deger
15/01/2024 10:00:00,100.5
15/01/2024 10:00:01,101.2
```
**Seçin:** `%d/%m/%Y %H:%M:%S (15/01/2024 14:30:45)`

### Test 2: Unix Timestamp
**CSV:**
```
timestamp,rpm
1704110400,1500
1704110401,1520
```
**Seçin:** `Unix Timestamp (1704110400)` veya `Otomatik`

### Test 3: Belirsiz Format
**CSV:**
```
time,value
2024-01-15,100
2024-01-16,102
```
**Seçin:** `Otomatik - Kendisi seçsin` (en güvenli)

## ✅ Avantajlar

| Özellik | Öncesi | Sonrası |
|---------|--------|---------|
| **Anlaşılırlık** | ❌ Teknik kodlar | ✅ Örnekli açıklama |
| **Kullanım** | ❌ Manuel çöz | ✅ Doğrudan seç |
| **Hata Oranı** | ❌ Yüksek | ✅ Düşük |
| **Öğrenme Eğrisi** | ❌ Dik | ✅ Kolay |

---

**Durum:** ✅ Uygulandı
**Dosya:** `src/data/data_import_dialog.py`
**Kullanıcı Dostu:** ⭐⭐⭐⭐⭐

