# Time Graph Uygulaması - EXE Build Kılavuzu

Bu kılavuz Time Graph uygulamasını EXE formatına çevirmek için gerekli adımları açıklar.

## 🎯 Gereksinimler

### Gerekli Python Paketleri
```bash
pip install pyinstaller pillow
```

### Dosya Yapısı
```
time_graph_x/
├── app.py                 # Ana uygulama
├── ikon.png             # Uygulama ikonu (PNG format)
├── ikon.ico             # Dönüştürülmüş ikon (ICO format)
├── time_graph_app.spec  # PyInstaller spec dosyası
├── build_exe.py         # Otomatik build script
├── convert_icon.py      # İkon dönüştürücü
└── ... (diğer dosyalar)
```

## 🚀 EXE Oluşturma

### Yöntem 1: Otomatik Build (Önerilen)
```bash
python build_exe.py
```

Bu script:
- Gerekli paketleri kontrol eder
- Önceki build dosyalarını temizler  
- PNG ikonunu ICO formatına çevirir
- EXE dosyasını oluşturur

### Yöntem 2: Manuel Build
```bash
# 1. İkonu dönüştür
python convert_icon.py

# 2. EXE oluştur
pyinstaller --clean --noconfirm time_graph_app.spec
```

## 📁 Çıktı

Başarılı build sonrası:
```
dist/
└── TimeGraphApp.exe    # Çalıştırılabilir dosya
```

## 🎨 İkon Ayarları

### PNG İkon Gereksinimleri
- **Dosya adı:** `ikon.png`
- **Format:** PNG (şeffaflık destekli)
- **Önerilen boyut:** 256x256 piksel veya daha büyük
- **Kalite:** Yüksek çözünürlük

### ICO Dönüşümü
Script otomatik olarak PNG'yi ICO formatına çevirir ve şu boyutları oluşturur:
- 16x16, 32x32, 48x48, 64x64, 128x128, 256x256

## ⚙️ Spec Dosyası Özellikleri

`time_graph_app.spec` dosyası şu özellikleri içerir:

### İkon Ayarları
- **EXE ikonu:** `ikon.ico`
- **Pencere ikonu:** Çalışma zamanında `ikon.png`

### Paketlenen Dosyalar
- Tüm Python modülleri
- İkon dosyaları (`icons/` klasörü)
- Gerekli kütüphane dosyaları

### Optimizasyonlar
- UPX sıkıştırma aktif
- Konsol penceresi gizli (GUI modu)
- Gereksiz modüller hariç tutulmuş

## 🔧 Sorun Giderme

### İkon Görünmüyor
1. `ikon.png` dosyasının mevcut olduğunu kontrol edin
2. `convert_icon.py` scriptini çalıştırın
3. `ikon.ico` dosyasının oluştuğunu doğrulayın

### Build Hatası
1. Gerekli paketlerin yüklü olduğunu kontrol edin:
   ```bash
   pip list | findstr -i "pyinstaller pillow"
   ```
2. Python sürümünün uyumlu olduğunu kontrol edin (3.7+)
3. Antivirus yazılımının build'i engellemediğini kontrol edin

### EXE Çalışmıyor
1. Geliştirme ortamında uygulamanın çalıştığını doğrulayın:
   ```bash
   python app.py
   ```
2. Eksik DLL'leri kontrol edin
3. Windows Defender'ın dosyayı karantinaya almadığını kontrol edin

## 📊 Dosya Boyutu

Tipik EXE boyutu: **50-100 MB**

Boyutu azaltmak için:
- Gereksiz kütüphaneleri spec dosyasından çıkarın
- UPX sıkıştırmayı aktif tutun
- `--onefile` yerine `--onedir` kullanın (daha hızlı başlatma)

## 🎉 Başarılı Build Sonrası

EXE dosyası oluşturulduktan sonra:

1. **Test edin:** `dist/TimeGraphApp.exe` dosyasını çalıştırın
2. **İkonu kontrol edin:** Dosya özelliklerinde ikon görünüyor mu?
3. **Dağıtım:** EXE dosyasını hedef bilgisayarlara kopyalayın

## 💡 İpuçları

- **Geliştirme:** Her değişiklikten sonra yeniden build yapın
- **Test:** Farklı Windows sürümlerinde test edin
- **Boyut:** Büyük dosyalar için sıkıştırma kullanın
- **Güvenlik:** Dijital imza ekleyerek güvenilirlik artırın

---

**Not:** Bu kılavuz Windows için hazırlanmıştır. Linux/Mac için farklı adımlar gerekebilir.
