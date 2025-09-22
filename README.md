# Time Graph Widget - Bağımsız Uygulama

Bu uygulama, gelişmiş veri analizi ve görselleştirme için tasarlanmış bağımsız bir masaüstü uygulamasıdır.

## Özellikler

### 🎯 Ana Özellikler
- **Çoklu Grafik Desteği**: Aynı anda birden fazla grafik görüntüleme
- **Gerçek Zamanlı İstatistikler**: Anlık veri analizi ve istatistikler
- **Gelişmiş Cursor Araçları**: Dual cursor ile hassas ölçümler
- **Tema Desteği**: Farklı görsel temalar
- **Veri Dışa/İçe Aktarma**: CSV, Parquet, HDF5 formatları

### 📊 Analiz Araçları
- **İstatistik Paneli**: Min, Max, Ortalama, RMS, Standart sapma
- **Korelasyon Analizi**: Sinyaller arası korelasyon hesaplama
- **Bitmask Analizi**: Dijital sinyal analizi
- **Filtreleme**: Gelişmiş veri filtreleme seçenekleri

### 🎨 Kullanıcı Arayüzü
- **Modern Tasarım**: Profesyonel ve kullanıcı dostu arayüz
- **Özelleştirilebilir Paneller**: Esnek panel düzeni
- **Klavye Kısayolları**: Hızlı erişim için kısayollar
- **Durum Çubuğu**: Anlık bilgi ve durum gösterimi

## Kurulum

### Gereksinimler
```bash
pip install PyQt5 numpy pandas vaex matplotlib pyqtgraph
```

### Çalıştırma
```bash
python app.py
```

## Kullanım

### 1. Veri Yükleme
- **File > Open** menüsünden veri dosyası seçin
- Desteklenen formatlar: CSV, Parquet, HDF5
- Örnek veri için: `python test_data.py` çalıştırın

### 2. Grafik Ayarları
- **📊 Graph Settings** butonu ile grafik sayısını ayarlayın
- Her grafik için ayrı normalizasyon ve grid ayarları
- **⚙️ General** butonu ile genel tema ayarları

### 3. Cursor Kullanımı
- **🎯 Cursor Mode** ile cursor modunu seçin
- Dual cursor ile iki nokta arası ölçüm
- Gerçek zamanlı değer okuma

### 4. İstatistik Analizi
- **📊 Statistics** paneli ile anlık istatistikler
- **⚙️ Statistics Settings** ile görüntülenecek istatistikleri seçin
- Cursor pozisyonlarında otomatik değer hesaplama

### 5. Gelişmiş Analiz
- **📈 Correlations** ile korelasyon analizi
- **🔢 Bitmask** ile dijital sinyal analizi
- Filtreleme ve segmentasyon araçları

## Dosya Formatları

### Desteklenen Giriş Formatları
- **CSV**: Virgülle ayrılmış değerler
- **Parquet**: Yüksek performanslı sütunlu format
- **HDF5**: Bilimsel veri formatı

### Çıkış Formatları
- Tüm giriş formatları desteklenir
- **File > Save** ile mevcut veriyi dışa aktarın

## Klavye Kısayolları

- **Ctrl+O**: Dosya aç
- **Ctrl+S**: Dosya kaydet
- **Ctrl+Q**: Uygulamadan çık

## Test Verisi

Uygulama ile test etmek için örnek veri oluşturun:

```bash
python test_data.py
```

Bu komut şu sinyalleri içeren test verisi oluşturur:
- Sinüs dalgaları (1Hz, 5Hz, 10Hz)
- Kosinüs dalgası (2Hz)
- Gürültülü sinyal
- Kare dalga
- Üçgen dalga
- Exponential decay
- Chirp sinyali
- Random walk

## Sorun Giderme

### Yaygın Sorunlar

1. **Uygulama açılmıyor**
   - Python ve gerekli kütüphanelerin yüklü olduğundan emin olun
   - `time_graph_app.log` dosyasını kontrol edin

2. **Veri yüklenmiyor**
   - Dosya formatının desteklendiğinden emin olun
   - Dosya yolunda Türkçe karakter olmamasına dikkat edin

3. **Grafik görünmüyor**
   - Veri sütunlarının sayısal olduğundan emin olun
   - Graph Settings panelinden grafik sayısını kontrol edin

## Geliştirici Notları

### Mimari
- **time_graph_widget.py**: Ana widget sınıfı
- **toolbar_manager.py**: Araç çubuğu yönetimi
- **app.py**: Bağımsız uygulama wrapper'ı

### Genişletme
- Yeni analiz araçları eklemek için panel manager'ları kullanın
- Tema sistemi `theme_manager.py` üzerinden özelleştirilebilir
- Veri işleme `signal_processor.py` ile yapılır

## Lisans

Bu proje özel lisans altındadır. Ticari kullanım için lisans gereklidir.

## İletişim

Sorularınız için lütfen geliştirici ekibi ile iletişime geçin.
