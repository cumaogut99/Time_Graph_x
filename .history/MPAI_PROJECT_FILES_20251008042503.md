# 📦 MPAI Proje Dosyaları Sistemi

## 🎯 Genel Bakış

**.mpai** (Motor Performance Analysis Interface) dosya formatı, Time Graph uygulamasında tüm analiz çalışmanızı **tek bir dosyada** saklamanızı sağlar.

### ✨ Özellikler

- ✅ **Tek Dosya**: Veri + Layout + Ayarlar birlikte
- ✅ **Hızlı Yükleme**: Parquet formatı sayesinde 8-27x daha hızlı
- ✅ **Kompakt**: ZSTD sıkıştırma ile küçük dosya boyutu
- ✅ **Taşınabilir**: Kopyalama, e-posta gönderme, yedekleme kolay
- ✅ **Güvenli**: ZIP tabanlı, kolayca doğrulanabilir

---

## 📁 Dosya İçeriği

Bir `.mpai` dosyası şunları içerir:

```
my_analysis.mpai
│
├── data.parquet          # Verileriniz (hızlı yükleme için)
├── layout.json           # Sekmeler, grafikler, parametreler
└── metadata.json         # Dosya bilgileri, tarih, sürüm
```

---

## 🚀 Nasıl Kullanılır?

### 💾 Proje Kaydetme

1. Verilerinizi yükleyin (CSV, Excel, vb.)
2. İstediğiniz gibi düzenleyin:
   - Sekmeleri oluşturun
   - Grafikleri ekleyin
   - Parametreleri seçin
   - Layout'u ayarlayın
3. **File** menüsünden **"Save Project (.mpai)"** seçin
4. Dosya adını belirleyin ve kaydedin

**Kısayol**: `Ctrl+Shift+S`

### 📂 Proje Açma

1. **File** menüsünden **"Open Project (.mpai)"** seçin
2. `.mpai` dosyasını seçin
3. Proje otomatik olarak yüklenir:
   - ✅ Veri hızlıca yüklenir (Parquet)
   - ✅ Layout otomatik uygulanır
   - ✅ Tüm ayarlar geri gelir

**Kısayol**: `Ctrl+Shift+O`

---

## ⚡ Performans Karşılaştırması

| İşlem | Geleneksel (CSV) | MPAI Projesi | Kazanç |
|-------|------------------|--------------|--------|
| Dosya açma | 8-15 saniye | 0.3-1 saniye | **8-27x hızlı** ✨ |
| Layout uygulama | Manuel | Otomatik | ⏱️ Zaman tasarrufu |
| Dosya sayısı | 2 (CSV + JSON) | 1 (MPAI) | 🎯 Basitlik |

---

## 💡 Kullanım Senaryoları

### 🔄 Günlük Analiz Rutini
```
1. motor_test_monday.mpai aç
2. Analiz yap
3. Sonuçları not al
4. Dosyayı kapat
```

### 📊 Karşılaştırmalı Analiz
```
1. test_before.mpai aç (Tab 1)
2. test_after.mpai aç (Tab 2)
3. İki dosyayı yan yana karşılaştır
```

### 💼 Raporlama
```
1. Analizi tamamla
2. .mpai olarak kaydet
3. Raporda kullan veya ekibinle paylaş
4. İsteyenler aynı layout'la açabilir
```

---

## 🔧 Teknik Detaylar

### Dosya Formatı
- **Container**: ZIP arşivi
- **Veri Format**: Apache Parquet
- **Sıkıştırma**: ZSTD (yüksek performans)
- **Layout Format**: JSON
- **Versiyon**: 1.0

### Uyumluluk
- ✅ Windows, Linux, macOS
- ✅ Geri uyumlu (eski CSV/Layout sistemle çalışır)
- ✅ Multi-file desteği (3 dosyaya kadar)

### Güvenlik
- ZIP formatı kolayca doğrulanabilir
- İçerik açıkça görülebilir
- Kötü amaçlı kod çalıştıramaz

---

## 📝 Önemli Notlar

### ✅ Yapın
- ✅ Düzenli olarak `.mpai` formatında kaydedin
- ✅ Önemli analizleri yedekleyin
- ✅ Anlamlı dosya isimleri kullanın
  - ✅ İyi: `motor_vibration_analysis_2024_10.mpai`
  - ❌ Kötü: `project1.mpai`

### ⚠️ Dikkat Edin
- ⚠️ Çok büyük veri setleri (~1GB+) için yükleme süresi artabilir
- ⚠️ `.mpai` dosyaları binary format'tır (text editor'de açılamaz)
- ⚠️ Eski versiyon uygulamalar yeni `.mpai` formatını desteklemeyebilir

---

## 🆚 Geleneksel vs. MPAI

### Geleneksel Yöntem
```
📂 Proje Klasörü/
  ├── 📄 data.csv              (15 MB)
  ├── 📄 layout.json           (10 KB)
  └── 📄 settings.json         (2 KB)
```
- ❌ 3 ayrı dosya yönetimi
- ❌ Her açılışta CSV parse
- ❌ Layout manuel import

### MPAI Yöntemi
```
📦 analysis.mpai               (5 MB - sıkıştırılmış)
```
- ✅ Tek dosya
- ✅ Hızlı Parquet yükleme
- ✅ Otomatik layout

---

## 🔍 Sık Sorulan Sorular

**S: Eski CSV dosyalarımı nasıl `.mpai`'ye çevirebilirim?**
> CSV'yi açın, istediğiniz layout'u oluşturun, "Save Project" deyin.

**S: `.mpai` dosyasını başkasıyla paylaşabilir miyim?**
> Evet! Tek dosya olduğu için e-posta, USB, cloud üzerinden kolayca paylaşılır.

**S: Dosya bozulursa ne olur?**
> ZIP tabanlı olduğu için arşiv onarım araçlarıyla kurtarılabilir.

**S: Veriyi tekrar CSV'ye dönüştürebilir miyim?**
> Evet! Projeyi açın, "Save Data" seçeneğiyle CSV'ye export edin.

**S: Hangi sürümlerde çalışır?**
> v1.0+ tüm sürümler `.mpai` destekler.

---

## 📞 Destek

Sorun yaşarsanız:
1. Log dosyasını kontrol edin: `time_graph_app.log`
2. Proje dosyasını doğrulayın (otomatik doğrulama var)
3. Gerekirse CSV + JSON export edin (yedek)

---

## 🎉 Sonuç

`.mpai` formatı, analiz iş akışınızı basitleştirir ve hızlandırır. Tek tıkla kaydet, tek tıkla aç!

**Mutlu analizler! 🚀📊**

