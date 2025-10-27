# Time Graph Widget - Ürün Gereksinim Dökümanı (PRD)

## 1. Genel Bakış

**Ürün Adı:** Time Graph Widget  
**Versiyon:** 1.0.0  
**Tip:** Masaüstü Veri Analiz Uygulaması  
**Platform:** Windows, Linux, macOS (PyQt5 tabanlı)  
**Hedef Kullanıcı:** Mühendisler, Veri Analistleri, Araştırmacılar

## 2. Ana Özellikler

### 2.1 Veri Yönetimi
- ✅ CSV, Excel (.xlsx, .xls) formatlarında veri yükleme
- ✅ Gelişmiş import dialog (header seçimi, delimiter, encoding)
- ✅ Çoklu dosya desteği (3 dosyaya kadar eş zamanlı)
- ✅ Dosya sekmeleri ile hızlı geçiş
- ✅ Parquet cache sistemi (8-27x hızlı yükleme)
- ✅ 25 MB dosya boyutu limiti
- ✅ Otomatik veri temizleme (NULL değerler, karışık tipler)

### 2.2 Görselleştirme
- ✅ 1-6 arası özelleştirilebilir grafik sayısı
- ✅ Gerçek zamanlı grafik güncelleme
- ✅ Normalizasyon seçenekleri (0-1, -1 to 1, Mean Center)
- ✅ Grid görünürlüğü kontrolü
- ✅ Datetime axis formatlama
- ✅ Çoklu sinyal çizimi
- ✅ Renk özelleştirme

### 2.3 Cursor Araçları
- ✅ Single Cursor modu
- ✅ Dual Cursor modu (iki nokta arası ölçüm)
- ✅ Gerçek zamanlı değer okuma
- ✅ Delta hesaplama (Dual Cursor'da)
- ✅ Tüm grafiklerde senkronize cursor

### 2.4 İstatistiksel Analiz
- ✅ Temel istatistikler (Min, Max, Ortalama)
- ✅ RMS (Root Mean Square) hesaplama
- ✅ Standart sapma
- ✅ Varyans
- ✅ Korelasyon analizi (sinyal çiftleri arası)
- ✅ Cursor pozisyonlarında değer gösterimi

### 2.5 Filtreleme Sistemi
- ✅ Range-based filtreleme (>=, >, <=, <)
- ✅ Çoklu koşul desteği (AND mantığı)
- ✅ Segmented mode (bölütlenmiş gösterim)
- ✅ Concatenated mode (birleştirilmiş gösterim)
- ✅ Thread-safe arka plan hesaplama
- ✅ Debouncing (100ms) ile performans optimizasyonu
- ✅ Filtre geçmişi ve geri alma

### 2.6 Bitmask Analizi
- ✅ Dijital sinyal analizi
- ✅ Bit seviyesi inceleme
- ✅ Bitmask uygulaması
- ✅ Sonuç görselleştirme

### 2.7 Tema Sistemi
- ✅ Light tema
- ✅ Dark tema
- ✅ Custom tema desteği
- ✅ Gerçek zamanlı tema değiştirme

### 2.8 Proje Yönetimi
- ✅ .mpai proje dosyası formatı
- ✅ Veri + Layout tek dosyada kaydetme
- ✅ Hızlı proje yükleme (Parquet tabanlı)
- ✅ Layout import/export (JSON)

### 2.9 Performans İzleme
- ✅ CPU kullanım göstergesi
- ✅ RAM kullanım göstergesi
- ✅ Gerçek zamanlı sistem monitörü
- ✅ Durum çubuğunda bilgi gösterimi

## 3. Kullanıcı Akışları

### 3.1 Temel Veri Analizi Akışı
1. Uygulama başlatma
2. File > Open ile veri dosyası seçme
3. Import dialog'da ayarları yapılandırma
4. Veri yükleme ve otomatik grafik oluşturma
5. Parametreleri seçme ve grafiklere atama
6. Cursor ile değer okuma
7. İstatistikleri inceleme

### 3.2 Gelişmiş Filtreleme Akışı
1. Veri yükleme
2. Parameter Filters panelini açma
3. Filtre koşulları ekleme
4. Segmented veya Concatenated mod seçimi
5. Apply Filter ile uygulama
6. Sonuçları inceleme
7. Reset Filter ile temizleme

### 3.3 Çoklu Dosya Karşılaştırma Akışı
1. İlk dosyayı yükleme
2. File > Open ile ikinci dosyayı yükleme
3. Dosya sekmeleri arasında geçiş
4. Her dosya için bağımsız analiz
5. Sonuçları karşılaştırma

### 3.4 Proje Kaydetme/Yükleme Akışı
1. Veri analizi tamamlama
2. Layout ayarlama (grafik sayısı, parametreler)
3. File > Save Project (.mpai)
4. Daha sonra File > Open Project ile hızlı yükleme

## 4. Teknik Gereksinimler

### 4.1 Performans
- ✅ CSV yükleme: <3 saniye (10MB dosya için)
- ✅ Parquet cache ile: <0.5 saniye
- ✅ Grafik güncelleme: <100ms
- ✅ Filtre hesaplama: Thread-based, UI bloke etmez
- ✅ Bellek kullanımı: <500MB (normal kullanımda)

### 4.2 Güvenilirlik
- ✅ Thread-safe veri işleme
- ✅ Graceful error handling
- ✅ Otomatik crash report oluşturma
- ✅ QThread proper cleanup
- ✅ Memory leak prevention

### 4.3 Kullanılabilirlik
- ✅ Responsive UI (High DPI desteği)
- ✅ Sezgisel panel düzeni
- ✅ Tooltip'ler ve açıklayıcı etiketler
- ✅ Hata mesajlarında kullanıcı dostu dil
- ✅ Splash screen ile başlatma bilgisi

### 4.4 Uyumluluk
- ✅ Windows 10/11
- ✅ Python 3.8+
- ✅ PyQt5 5.15+
- ✅ High DPI ekranlar
- ✅ Çoklu monitör desteği

## 5. Veri Formatları

### 5.1 Desteklenen Girdi Formatları
```
CSV:
- Delimiter: virgül, noktalı virgül, tab, custom
- Encoding: UTF-8, Latin-1, custom
- Header: Opsiyonel, satır numarası seçilebilir
- Null values: Otomatik algılama ve temizleme

Excel:
- .xlsx, .xls formatları
- İlk sayfa veya belirli sayfa seçimi
- Header satırı yapılandırması

MPAI (Project):
- Özel format (Parquet + JSON metadata)
- Hızlı yükleme
- Layout bilgisi dahil
```

### 5.2 Zaman Kolonu Formatları
- Unix timestamp (saniye/milisaniye)
- ISO 8601 datetime string
- Özel datetime formatları
- Otomatik index oluşturma (frekans bazlı)

## 6. Kısıtlamalar ve Sınırlar

### 6.1 Dosya Boyutu
- Maksimum: 25 MB (kullanıcı dostu)
- Önerilen: <10 MB (optimal performans)

### 6.2 Eş Zamanlı Dosya
- Maksimum: 3 dosya
- Her dosya için bağımsız widget instance

### 6.3 Grafik Sayısı
- Minimum: 1
- Maksimum: 6
- Her grafikte çoklu sinyal çizilebilir

### 6.4 Parametre Sayısı
- Teorik limit yok
- Pratik: 350+ kolon test edildi
- UI performansı için ~50 parametre önerilir

## 7. Hata Durumları ve İşlenmesi

### 7.1 Dosya Yükleme Hataları
- Dosya bulunamadı → Kullanıcıya bildir
- Format hatası → Import dialog ile yeniden dene
- Encoding hatası → Otomatik Latin-1 fallback
- Çok büyük dosya → Boyut limiti uyarısı

### 7.2 Veri İşleme Hataları
- NULL değerler → Otomatik forward-fill
- Karışık tipler → Akıllı tip dönüşümü
- Eksik zaman kolonu → Otomatik index oluşturma
- Infinite değerler → Temizleme ve düzeltme

### 7.3 Thread Hataları
- Thread cleanup → Otomatik deleteLater
- RuntimeError → Sessizce yakala
- Memory leak → Proper reference management

### 7.4 Kullanıcı Hataları
- Geçersiz filtre → Uyarı mesajı
- Grafik limitlerini aşma → Maksimum bilgisi
- Boş veri seçimi → Bilgilendirme

## 8. Test Senaryoları

### 8.1 Fonksiyonel Testler
1. ✅ Veri yükleme (CSV, Excel)
2. ✅ Çoklu dosya yükleme ve geçiş
3. ✅ Grafik oluşturma (1-6 arası)
4. ✅ Parametre seçimi ve grafiklere atama
5. ✅ Cursor kullanımı (Single, Dual)
6. ✅ İstatistik hesaplama
7. ✅ Filtreleme (Segmented, Concatenated)
8. ✅ Proje kaydetme/yükleme
9. ✅ Tema değiştirme
10. ✅ Layout import/export

### 8.2 Performans Testleri
1. Büyük dosya yükleme (25MB)
2. Çoklu grafik performansı (6 grafik)
3. Filtre hesaplama süresi
4. Bellek kullanımı (uzun süreli kullanım)
5. Thread cleanup (çoklu yükleme/kapatma)

### 8.3 Stres Testleri
1. Maksimum dosya boyutu (25MB)
2. Maksimum kolon sayısı (350+)
3. Hızlı dosya değiştirme
4. Çoklu filtre uygulama
5. Ekstrem NULL oranları (%80+)

### 8.4 Edge Case Testleri
1. Boş dosya
2. Tek satırlık veri
3. Tek kolonlu veri
4. Sadece NULL değerler
5. Karışık tip kolonlar
6. Özel karakterler içeren veriler
7. Çok büyük timestamp değerleri

## 9. Başarı Kriterleri

### 9.1 Fonksiyonel
- ✅ Tüm ana özellikler çalışıyor
- ✅ Hata durumlarında graceful degradation
- ✅ Kullanıcı akışları sorunsuz tamamlanıyor

### 9.2 Performans
- ✅ 10MB dosya <3 saniye yükleniyor
- ✅ Cache ile <0.5 saniye
- ✅ UI responsive (thread-based işlemler)
- ✅ Bellek sızıntısı yok

### 9.3 Kullanılabilirlik
- ✅ Sezgisel arayüz
- ✅ Açık hata mesajları
- ✅ Tooltip'ler mevcut
- ✅ High DPI desteği

### 9.4 Güvenilirlik
- ✅ Crash durumunda rapor oluşturma
- ✅ Thread güvenliği
- ✅ Veri bütünlüğü korunuyor

## 10. Bilinen Sınırlamalar (Kabul Edilebilir)

1. **Dosya Boyutu:** 25MB limit (RAM yönetimi için)
2. **Eş Zamanlı Dosya:** 3 dosya (performans için)
3. **Desktop Only:** Web versiyonu yok
4. **Single User:** Çoklu kullanıcı desteği yok
5. **Offline:** Network özellikleri yok

## 11. Gelecek Geliştirmeler (Roadmap)

### v1.1 (Planlanan)
- [ ] Real-time data streaming
- [ ] Export to PDF/Image
- [ ] Custom formül/hesaplama motoru
- [ ] Plugin sistemi

### v1.2 (Gelecek)
- [ ] Cloud sync
- [ ] Collaborative editing
- [ ] Web versiyonu
- [ ] Mobile app (viewer)

## 12. Güvenlik ve Lisans

### 12.1 Veri Güvenliği
- Tüm veriler local'de işlenir
- Network bağlantısı gerektirmez
- Kullanıcı verisi dışarı gönderilmez

### 12.2 Lisans (Hazır, şimdilik kullanılmıyor)
- Trial mode: 30 gün
- Full license: Tek kullanıcı, tek makine
- Subscription: Yıllık yenileme

---

**Doküman Versiyonu:** 1.0  
**Son Güncelleme:** 2025-01-21  
**Hazırlayan:** TimeGraph Development Team

