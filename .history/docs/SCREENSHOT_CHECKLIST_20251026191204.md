# ✅ Screenshot Çekim Kontrol Listesi

Her görsel için bu listeyi kullanarak screenshot alın ve işaretleyin.

---

## Genel Ayarlar

### Uygulama Hazırlık
- [ ] Uygulama tam ekran veya 1920x1080 boyutunda
- [ ] Örnek veri yüklendi (motor test verisi önerilen)
- [ ] Tema: Light (varsayılan) - PDF için daha uygun
- [ ] Windows görev çubuğu gizli (Auto-hide)

### Screenshot Kalite Ayarları
- [ ] Çözünürlük: 1920x1080 minimum
- [ ] Format: PNG (JPG değil!)
- [ ] Temiz arka plan (gereksiz pencereler kapalı)

---

## Görsel Çekim Listesi

### Bölüm 1: Başlangıç (2 görsel)

#### ✅ Görsel 1: Uygulama Başlangıç Ekranı
- [ ] Uygulamayı aç
- [ ] Splash screen göründüğünde PrintScreen
- [ ] Ardından ana pencere açılışını çek
- [ ] İki görseli yan yana birleştir
- **Dosya:** `screenshots/01_splash_screen.png`

#### ✅ Görsel 2: Ana Pencere Bölümleri
- [ ] Ana pencere tam görünür
- [ ] Paint/Snagit ile bölgeleri işaretle:
  - Toolbar (üst)
  - Sol sidebar
  - Grafik alanı (ortada)
  - Sağ sidebar
  - Status bar (alt)
- [ ] Her bölgeye etiket ekle
- **Dosya:** `screenshots/02_main_window_layout.png`

---

### Bölüm 2: Dosya İşlemleri (6 görsel)

#### ✅ Görsel 3: File Menüsü
- [ ] Toolbar → File butonuna tıkla
- [ ] Dropdown menü açıkken screenshot
- **Dosya:** `screenshots/03_file_menu.png`

#### ✅ Görsel 4: Import Dialog Penceresi
- [ ] File → Open → Bir CSV seç
- [ ] Import dialog tam görünsün
- [ ] Tüm bölümler görünür olmalı
- **Dosya:** `screenshots/04_import_dialog.png`

#### ✅ Görsel 5: Import Ayarları Bölümü
- [ ] Import dialog → Üst bölüm (Settings)
- [ ] Delimiter dropdown'u göster
- [ ] Encoding dropdown'u göster
- [ ] Header/Start row inputları göster
- **Dosya:** `screenshots/05_import_settings.png`

#### ✅ Görsel 6: Zaman Kolonu Ayarları
- [ ] Import dialog → Time Settings bölümü
- [ ] İki seçenek de görünsün:
  - Use Existing Time Column
  - Create Custom Time Column
- [ ] Sampling Frequency inputları göster
- **Dosya:** `screenshots/06_time_column_settings.png`

#### ✅ Görsel 7: Veri Önizleme Tablosu
- [ ] Import dialog → Alt bölüm (Preview)
- [ ] İlk 10 satır tablo halinde
- [ ] Kolon isimleri net görünsün
- **Dosya:** `screenshots/07_data_preview.png`

#### ✅ Görsel 8: Yükleme Animasyonu
- [ ] Load Data butonuna bas
- [ ] Loading overlay görünürken screenshot
- [ ] Animasyon ve "Loading..." yazısı görünsün
- **Dosya:** `screenshots/08_loading_overlay.png`

---

### Bölüm 3: Grafik Yönetimi (6 görsel)

#### ✅ Görsel 9: Graph Settings Dialog
- [ ] Toolbar → Graph Settings butonu
- [ ] Dialog penceresi tam açık
- [ ] Graph count slider göster
- [ ] Layout önizleme göster
- **Dosya:** `screenshots/09_graph_settings.png`

#### ✅ Görsel 10: Zoom İşlemleri
- [ ] Grafik üzerinde zoom dikdörtgeni çiz
- [ ] Sol tık + sürükle işaretli göster
- [ ] Ok ve açıklama ekle (Paint ile)
- **Dosya:** `screenshots/10_zoom_operations.png`

#### ✅ Görsel 11: Sağ Tık Menüsü
- [ ] Grafik üzerinde sağ tık
- [ ] Context menu açıkken screenshot
- [ ] Auto Range, View All, Export Image seçenekleri görünsün
- **Dosya:** `screenshots/11_context_menu.png`

#### ✅ Görsel 12: Advanced Settings İkonu
- [ ] Grafik başlığına zoom yap
- [ ] ⚙️ ikonu net görünsün
- [ ] Mouse hover olabilir (vurgulu)
- **Dosya:** `screenshots/12_advanced_settings_icon.png`

#### ✅ Görsel 13: Normalizasyon Seçenekleri
- [ ] Advanced Settings dialog aç
- [ ] Normalization dropdown'u genişlet
- [ ] Tüm seçenekler görünsün:
  - None, 0 to 1, -1 to 1, Mean Center, Z-Score
- **Dosya:** `screenshots/13_normalization_options.png`

#### ✅ Görsel 14: Grid Ayarları
- [ ] İki grafik yan yana:
  - Sol: Grid kapalı
  - Sağ: Grid açık
- [ ] Fark net belli olmalı
- **Dosya:** `screenshots/14_grid_settings.png`

---

### Bölüm 4: Sinyal İşlemleri (3 görsel)

#### ✅ Görsel 15: Parameters Paneli
- [ ] Sol sidebar → Parameters sekmesi
- [ ] En az 5-10 sinyal listesi
- [ ] Checkbox, renk, dropdown görünsün
- **Dosya:** `screenshots/15_parameters_panel.png`

#### ✅ Görsel 16: Sinyal Seçme İşlemi
- [ ] Bir sinyalin seçim adımlarını göster:
  1. Checkbox işaretle (kırmızı ok)
  2. Renk seç (kırmızı ok)
  3. Grafik ata (kırmızı ok)
- [ ] Numaraları ekle (Paint ile)
- **Dosya:** `screenshots/16_signal_selection.png`

#### ✅ Görsel 17: Renk Seçici Dialog
- [ ] Renk butonuna tıkla
- [ ] Color picker dialog açık
- [ ] Renk paleti görünsün
- **Dosya:** `screenshots/17_color_picker.png`

---

### Bölüm 5: Cursor Araçları (4 görsel)

#### ✅ Görsel 18: Cursor Mode Butonu
- [ ] Toolbar → Cursor Mode dropdown
- [ ] Üç seçenek görünsün:
  - None
  - Single Cursor
  - Dual Cursor
- **Dosya:** `screenshots/18_cursor_mode_button.png`

#### ✅ Görsel 19: Single Cursor
- [ ] Single Cursor modu aktif
- [ ] Grafikte mavi dikey çizgi
- [ ] Sağ sidebar → Statistics → Cursor Values bölümü
- [ ] İki bölümü aynı screenshot'ta göster
- **Dosya:** `screenshots/19_single_cursor.png`

#### ✅ Görsel 20: Dual Cursor
- [ ] Dual Cursor modu aktif
- [ ] Grafikte iki çizgi (mavi ve kırmızı)
- [ ] Statistics panel → Delta değerleri
- [ ] Tam görünüm
- **Dosya:** `screenshots/20_dual_cursor.png`

#### ✅ Görsel 21: Dual Cursor Kullanım Örnekleri
- [ ] 3 farklı örnek collage yap:
  1. Rise Time ölçümü (motor start)
  2. Frekans ölçümü (periyodik sinyal)
  3. Efficiency analizi (iki nokta karşılaştırma)
- [ ] Her birinde cursor'lar ve sonuç göster
- **Dosya:** `screenshots/21_dual_cursor_examples.png`

---

### Bölüm 6: İstatistik (4 görsel)

#### ✅ Görsel 22: Statistics Paneli
- [ ] Sağ sidebar → Statistics sekmesi
- [ ] En az 2-3 sinyal için istatistikler
- [ ] Tam panel görünümü
- **Dosya:** `screenshots/22_statistics_panel.png`

#### ✅ Görsel 23: İstatistik Değerleri
- [ ] Statistics panel yakın çekim
- [ ] Bir sinyalin tüm istatistikleri net:
  - Min, Max, Mean, RMS, Std Dev
- **Dosya:** `screenshots/23_statistics_values.png`

#### ✅ Görsel 24: Statistics Settings Dialog
- [ ] Toolbar → Statistics Settings butonu
- [ ] Dialog açık
- [ ] Checkbox listesi görünsün
- **Dosya:** `screenshots/24_statistics_settings.png`

#### ✅ Görsel 25: Cursor ile Segment İstatistikleri
- [ ] Dual cursor aktif
- [ ] Statistics panel → Segment statistics bölümü
- [ ] İki cursor arası istatistikler gösteriliyor
- **Dosya:** `screenshots/25_segment_statistics.png`

---

### Bölüm 7: Filtreleme (5 görsel)

#### ✅ Görsel 26: Filters Paneli
- [ ] Sağ sidebar → Filters sekmesi
- [ ] Boş panel (henüz filtre yok)
- [ ] "Add Filter" butonu görünsün
- **Dosya:** `screenshots/26_filters_panel.png`

#### ✅ Görsel 27: Filtre Ekleme Dialog
- [ ] Add Filter → Form açık
- [ ] Parameter dropdown
- [ ] Operator dropdown
- [ ] Value input
- [ ] Hepsi görünsün
- **Dosya:** `screenshots/27_add_filter.png`

#### ✅ Görsel 28: Çoklu Filtre Listesi
- [ ] 2-3 filtre eklenmiş
- [ ] Liste görünümü
- [ ] Remove (X) butonları görünsün
- **Dosya:** `screenshots/28_multiple_filters.png`

#### ✅ Görsel 29: Segmented Mode Örneği
- [ ] Filtre ekle (örn: Speed > 2000)
- [ ] Segmented Mode ☑️ işaretli
- [ ] Grafikte boşluklar görünsün
- [ ] Filtreyi geçmeyen bölgeler boş
- **Dosya:** `screenshots/29_segmented_mode.png`

#### ✅ Görsel 30: Concatenated Mode Örneği
- [ ] Aynı filtre
- [ ] Segmented Mode ☐ kapalı
- [ ] Grafik sürekli (birleştirilmiş)
- [ ] Boşluk yok
- **Dosya:** `screenshots/30_concatenated_mode.png`

---

### Bölüm 8: Bitmask (4 görsel)

#### ✅ Görsel 31: Bitmask Paneli
- [ ] Sağ sidebar → Bitmask sekmesi
- [ ] Boş panel
- [ ] Parameter seçimi görünsün
- **Dosya:** `screenshots/31_bitmask_panel.png`

#### ✅ Görsel 32: Bitmask Ayarları
- [ ] Parameter seçilmiş
- [ ] Bit Count input
- [ ] Start Bit input
- [ ] Analyze butonu
- **Dosya:** `screenshots/32_bitmask_settings.png`

#### ✅ Görsel 33: Bit Grafikleri
- [ ] Bitmask analizi yapılmış
- [ ] Her bit için dijital dalga formu
- [ ] En az 4-8 bit görünsün
- [ ] Grafikte kare dalga şekilleri net
- **Dosya:** `screenshots/33_bit_graphs.png`

#### ✅ Görsel 34: Duty Cycle Sonuçları
- [ ] Bitmask panel → Results bölümü
- [ ] Her bit için:
  - Duty Cycle %
  - Total HIGH/LOW
  - Transitions
- **Dosya:** `screenshots/34_duty_cycle.png`

---

### Bölüm 9: Korelasyon (3 görsel)

#### ✅ Görsel 35: Correlations Paneli
- [ ] Sağ sidebar → Correlations sekmesi
- [ ] Boş veya hesaplanmış tablo
- **Dosya:** `screenshots/35_correlations_panel.png`

#### ✅ Görsel 36: Korelasyon Tablosu
- [ ] Calculate Correlations yapılmış
- [ ] Tablo dolu:
  - Signal Pair
  - Correlation
  - Strength
- [ ] En az 5-10 sinyal çifti
- **Dosya:** `screenshots/36_correlation_table.png`

#### ✅ Görsel 37: Scatter Plot
- [ ] Bir sinyal çiftine çift tık
- [ ] Scatter plot penceresi açık
- [ ] X-Y grafiği net görünsün
- [ ] Korelasyon trendi belli olmalı
- **Dosya:** `screenshots/37_scatter_plot.png`

---

### Bölüm 10: Deviation (4 görsel)

#### ✅ Görsel 38: Deviation Paneli
- [ ] Sağ sidebar → Deviation sekmesi
- [ ] Boş panel
- [ ] Signal seçim dropdown'ları
- **Dosya:** `screenshots/38_deviation_panel.png`

#### ✅ Görsel 39: Deviation Ayarları
- [ ] Test Signal seçilmiş
- [ ] Reference Signal seçilmiş
- [ ] Calculate Deviation butonu
- **Dosya:** `screenshots/39_deviation_settings.png`

#### ✅ Görsel 40: Deviation Sonuçları
- [ ] Deviation hesaplanmış
- [ ] Results bölümü:
  - Max Positive/Negative Deviation
  - Mean Absolute Deviation
  - RMS Deviation
  - Tolerance Check
- **Dosya:** `screenshots/40_deviation_results.png`

#### ✅ Görsel 41: Static Limits Grafiği
- [ ] Excel limits yüklenmiş
- [ ] Grafikte üst/alt limit çizgileri
- [ ] Yeşil (tolerans içi) ve kırmızı (dışı) alanlar
- [ ] Test sinyali gösteriliyor
- **Dosya:** `screenshots/41_static_limits.png`

---

### Bölüm 11: Çoklu Dosya (1 görsel)

#### ✅ Görsel 42: Dosya Sekmeleri
- [ ] 2-3 dosya yüklenmiş
- [ ] Status bar → Dosya sekmeleri
- [ ] Aktif sekme vurgulu
- [ ] Close (X) butonları görünsün
- **Dosya:** `screenshots/42_file_tabs.png`

---

### Bölüm 12: Proje (3 görsel)

#### ✅ Görsel 43: MPAI Dosya İkonu
- [ ] .mpai dosyası oluştur
- [ ] Windows Explorer'da göster
- [ ] Dosya ikonu ve properties (sağ tık → Properties)
- [ ] Boyut ve oluşturma tarihi görünsün
- **Dosya:** `screenshots/43_mpai_icon.png`

#### ✅ Görsel 44: Proje Kaydetme Dialog
- [ ] File → Save Project (.mpai)
- [ ] Save dialog açık
- [ ] Dosya adı girişi göster
- **Dosya:** `screenshots/44_save_project.png`

#### ✅ Görsel 45: Proje Yükleme
- [ ] File → Open Project (.mpai)
- [ ] Loading animasyonu göster
- [ ] Ardından yüklenmiş hali göster
- [ ] İki screenshot birleştir
- **Dosya:** `screenshots/45_load_project.png`

---

### Bölüm 13: Sorun Giderme (2 görsel)

#### ✅ Görsel 46: Import Hata Mesajı
- [ ] Kasıtlı olarak hatalı dosya yükle:
  - Bozuk CSV
  - Yanlış delimiter
  - Çok büyük dosya
- [ ] Hata mesajı dialog'u
- **Dosya:** `screenshots/46_import_error.png`

#### ✅ Görsel 47: Log Dosyası
- [ ] time_graph_app.log dosyasını aç (Not Defteri)
- [ ] Hata ve warning satırları görünsün
- [ ] Timestamp'ler okunabilir
- **Dosya:** `screenshots/47_log_file.png`

---

## Screenshot Sonrası

### Kontrol Listesi
- [ ] Toplam 47 görsel çekildi
- [ ] Hepsi `screenshots/` klasöründe
- [ ] Dosya isimleri doğru (01_*.png formatında)
- [ ] PNG formatında (JPG değil)
- [ ] En az 1920px genişlikte
- [ ] Okunabilir ve net

### Düzenleme İhtiyacı Olan Görseller
- [ ] Görsel 2: Bölüm işaretlemeleri ekle
- [ ] Görsel 10: Zoom işlemleri açıklaması ekle
- [ ] Görsel 16: Adımları numaralandır
- [ ] Görsel 21: 3 örneği collage yap

### Markdown'a Ekleme
- [ ] Find & Replace ile placeholder'ları değiştir
- [ ] Tüm görsellerin göründüğünü kontrol et
- [ ] Markdown önizlemede test et

---

## Notlar

**İpuçları:**
- Tutarlı tema kullan (hep light veya hep dark)
- Aynı test verisini kullan (motor_test_data.csv önerilen)
- Gerçekçi veri olsun (random sayılar değil)
- Mouse cursor'u görsellerde sakla (Snagit/ShareX ayarı)

**Zaman Tahmini:**
- Hazırlık: 30 dakika
- Screenshot çekimi: 2-3 saat
- Düzenleme: 1-2 saat
- **Toplam: 4-6 saat**

**Öncelik Sırası:**
1. Önce temel görseller (1-20)
2. Sonra analiz görselleri (21-41)
3. Son olarak ekstra görseller (42-47)

---

✅ **Başarılar! Bu listeyi takip ederek profesyonel bir kılavuz hazırlayabilirsiniz.**

