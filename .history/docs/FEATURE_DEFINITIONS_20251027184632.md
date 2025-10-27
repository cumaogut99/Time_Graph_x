# Time Graph X - Özellik Tanımları

**Son Güncelleme:** 2025-01-21  
**Kullanım:** Her özellik için geliştirme prompt'u ve gereksinimler

---

## 📋 İçindekiler

1. [Filter Dialog State Management](#filter-dialog-state-management)
2. [Limit Lines Management](#limit-lines-management)
3. [Multi-Tab İzolasyonu](#multi-tab-izolasyonu)
4. [Real-time Data Streaming](#real-time-data-streaming)
5. [Export Geliştirmeleri](#export-geliştirmeleri)

---

## 1. Filter Dialog State Management

### Özet
Filter dialog'u açıldığında mevcut filtre state'ini yükle, kapatıldığında kaydet.

### Mevcut Durum
❌ **Çalışmıyor** - Dialog açıldığında boş geliyor

### Problem
- Range filter ekliyoruz → Dialog'u kapatıyoruz → Dialog tekrar açınca filtre gösterilmiyor
- Filtre grafikte aktif ama dialog'da görünmüyor
- Kullanıcı hangi filtrenin aktif olduğunu göremez

### Teknik Gereksinimler

#### 1. Dialog Açılışında State Yükleme

**Dosya:** `src/ui/graph_advanced_settings_dialog.py`

```python
def __init__(self, parent, data, columns, time_column, current_graph_index, **kwargs):
    # Mevcut state'i al
    self.current_filter = kwargs.get('current_filter', None)
    self.current_limits = kwargs.get('current_limits', {})
    
    # UI'ı doldur
    if self.current_filter:
        self._load_filter_into_ui(self.current_filter)
    
    if self.current_limits:
        self._load_limits_into_ui(self.current_limits)
```

**Method:** `_load_filter_into_ui()`
```python
def _load_filter_into_ui(self, filter_data):
    """Mevcut filtreyi UI'a yükle"""
    # Range filter varsa
    if 'range_filter' in filter_data:
        conditions = filter_data['range_filter'].get('conditions', [])
        for condition in conditions:
            self.parameter_filters_panel.add_condition(
                parameter=condition['parameter'],
                operator=condition['operator'],
                value=condition['value']
            )
    
    # Segmented mode
    mode = filter_data.get('mode', 'concatenated')
    if mode == 'segmented':
        self.parameter_filters_panel.segmented_checkbox.setChecked(True)
```

#### 2. Widget'tan Dialog'a State Gönderme

**Dosya:** `time_graph_widget.py`

```python
def _on_graph_settings_requested(self, graph_index):
    # Mevcut state'i al
    active_tab_index = self.tab_widget.currentIndex()
    current_filter = self.filter_manager.get_filter_state(active_tab_index)
    current_limits = self._get_current_limits(active_tab_index, graph_index)
    
    # Dialog'u başlat
    dialog = GraphAdvancedSettingsDialog(
        parent=self,
        data=self.data,
        columns=self.columns,
        time_column=self.time_column,
        current_graph_index=graph_index,
        # State'i gönder
        current_filter=current_filter,
        current_limits=current_limits,
        target_tab_index=active_tab_index  # Tab context
    )
```

#### 3. Limit State Yükleme

**Method:** `_get_current_limits()`
```python
def _get_current_limits(self, tab_index, graph_index):
    """Mevcut limit durumunu al"""
    limits_config = {}
    
    # Static limits panel'den al
    if hasattr(self, 'static_limits_panel'):
        limits_data = self.static_limits_panel.get_current_limits()
        if limits_data:
            limits_config[graph_index] = limits_data
    
    return limits_config
```

### Test Senaryoları

#### Test 1: Filter Ekleme
```python
1. Grafik oluştur
2. Advanced Settings aç
3. Range filter ekle (Motor_Speed > 1000)
4. OK'a bas
5. Dialog tekrar aç
6. ✅ Filter gösterilmeli
```

#### Test 2: Filter Değiştirme
```python
1. Filter ekle (Motor_Speed > 1000)
2. Dialog kapat
3. Dialog tekrar aç
4. Filter'ı değiştir (Motor_Speed > 2000)
5. OK'a bas
6. ✅ Yeni filter uygulanmalı
```

#### Test 3: Filter Kaldırma
```python
1. Filter ekle
2. Dialog kapat
3. Dialog tekrar aç
4. Filter'ı sil
5. OK'a bas
6. ✅ Filter kaldırılmalı
```

### Beklenen Süre
4-6 saat

---

## 2. Limit Lines Management

### Özet
Limit çizgilerini ekleme, kaldırma ve temizleme yönetimi.

### Mevcut Durum
⚠️ **Kısmen Çalışıyor** - Ekleme çalışıyor, kaldırma çalışmıyor

### Problem
- Static limit eklendiğinde çizgi görünüyor ✅
- Limit kaldırıldığında çizgi grafikten kalkmıyor ❌
- Çift çizgi problemi (eski + yeni çizgiler üst üste)

### Teknik Gereksinimler

#### 1. Limit Line Referans Yönetimi

**Dosya:** `time_graph_widget.py`

```python
def __init__(self):
    # Limit line referansları
    self.limit_lines = {}  # {graph_index: [Line1, Line2, ...]}
```

#### 2. Limit Lines Temizleme

**Method:** `_clear_limit_lines()`
```python
def _clear_limit_lines(self, plot_widget, graph_index):
    """Belirli bir grafikteki tüm limit çizgilerini temizle"""
    if graph_index not in self.limit_lines:
        return
    
    for line in self.limit_lines[graph_index]:
        # PyQtGraph'ten kaldır
        if line in plot_widget.items:
            plot_widget.removeItem(line)
    
    # Referansları temizle
    self.limit_lines[graph_index] = []
```

#### 3. Limit Lines Uygulama

**Method:** `_apply_limit_lines()`
```python
def _apply_limit_lines(self, plot_widget, graph_index, signals):
    """Limit çizgilerini uygula"""
    # ÖNCE temizle
    self._clear_limit_lines(plot_widget, graph_index)
    
    # Eğer limit yoksa çık
    if not hasattr(self, 'static_limits_panel'):
        return
    
    limits_data = self.static_limits_panel.get_current_limits()
    if not limits_data:
        return
    
    # Her sinyal için limit çizgileri ekle
    for signal_name in signals:
        if signal_name in limits_data:
            limits = limits_data[signal_name]
            
            # Upper limit
            if 'upper' in limits:
                upper_line = pg.InfiniteLine(
                    pos=limits['upper'],
                    angle=0,
                    pen=pg.mkPen('r', width=2, style=Qt.DashLine)
                )
                plot_widget.addItem(upper_line)
                self.limit_lines[graph_index].append(upper_line)
            
            # Lower limit
            if 'lower' in limits:
                lower_line = pg.InfiniteLine(
                    pos=limits['lower'],
                    angle=0,
                    pen=pg.mkPen('r', width=2, style=Qt.DashLine)
                )
                plot_widget.addItem(lower_line)
                self.limit_lines[graph_index].append(lower_line)
```

#### 4. Dialog'dan Limit Uygulama

**Dosya:** `time_graph_widget.py` → `_on_limits_applied_from_dialog()`

```python
def _on_limits_applied_from_dialog(self, limits_config):
    """Dialog'dan gelen limitleri uygula"""
    target_tab_index = getattr(self, '_dialog_target_tab', None)
    if target_tab_index is None:
        target_tab_index = self.tab_widget.currentIndex()
    
    # Tab ve grafik context
    graph_index = getattr(self, '_dialog_target_graph', 0)
    
    # Container al
    container = self.graph_containers[target_tab_index]
    plot_widget = container.plot_widgets[graph_index]
    
    # Mevcut sinyalleri al
    tab_mapping = self.graph_signal_mapping.get(target_tab_index, {})
    visible_signals = tab_mapping.get(graph_index, [])
    
    # Eğer limit yoksa temizle
    if not limits_config:
        self._clear_limit_lines(plot_widget, graph_index)
        return
    
    # Limit çizgilerini uygula
    self._apply_limit_lines(plot_widget, graph_index, visible_signals)
    
    # State'i kaydet
    self.filter_manager.save_limits_state(target_tab_index, graph_index, limits_config)
```

### Test Senaryoları

#### Test 1: Limit Ekleme
```python
1. Grafik oluştur, sinyal ekle
2. Advanced Settings aç
3. Static Limits ekle (Upper: 100, Lower: 0)
4. OK'a bas
5. ✅ Kırmızı çizgiler görünmeli
```

#### Test 2: Limit Kaldırma
```python
1. Limit ekle
2. Dialog aç
3. Limit'i sil
4. OK'a bas
5. ✅ Çizgiler kaybolmalı
```

#### Test 3: Limit Değiştirme
```python
1. Limit ekle (Upper: 100)
2. Dialog aç
3. Limit'i değiştir (Upper: 200)
4. OK'a bas
5. ✅ Yeni çizgi görünmeli (eski kalkmalı)
```

### Beklenen Süre
3-4 saat

---

## 3. Multi-Tab İzolasyonu

### Özet
Dialog açıkken tab değiştirme durumunda işlemleri doğru tab'a uygula.

### Mevcut Durum
⚠️ **Kısmen Çalışıyor** - Bazı fonksiyonlarda çalışmıyor

### Problem
- Tab 1'de dialog açıyoruz
- Dialog açıkken Tab 2'ye geçiyoruz
- OK'a basınca işlem Tab 2'ye uygulanıyor ❌

### Teknik Gereksinimler

#### 1. Target Tab Kaydetme

**Dosya:** `time_graph_widget.py`

```python
def _on_graph_settings_requested(self, graph_index):
    # Dialog açılırken target tab'ı kaydet
    active_tab_index = self.tab_widget.currentIndex()
    self._dialog_target_tab = active_tab_index
    self._dialog_target_graph = graph_index
    
    # Dialog'u başlat
    dialog = GraphAdvancedSettingsDialog(...)
```

#### 2. Tüm İşlemlerde Target Tab Kullanma

**Örnek:** `_apply_calculated_segments()`
```python
def _apply_calculated_segments(self, segments):
    """Hesaplanmış segmentleri uygula"""
    # Target tab kullan!
    target_tab_index = getattr(self, '_dialog_target_tab', None)
    if target_tab_index is None:
        target_tab_index = self.tab_widget.currentIndex()
    
    # DOĞRU container'ı al
    container = self.graph_containers[target_tab_index]
    
    # Tab mapping'i al
    tab_mapping = self.graph_signal_mapping.get(target_tab_index, {})
    
    # İşlemi uygula
    ...
```

**Uygulanacak Fonksiyonlar:**
- `_apply_calculated_segments()` ✅ Düzeltildi
- `_on_basic_deviation_applied()` ⚠️ Düzeltilmeli
- `_apply_range_filter()` ✅ Düzeltildi

#### 3. Basic Deviation Düzeltmesi

**Dosya:** `time_graph_widget.py` → `_on_basic_deviation_applied()`

```python
def _on_basic_deviation_applied(self, deviation_data):
    """Basic deviation analizini uygula"""
    # Target tab kullan!
    target_tab_index = getattr(self, '_dialog_target_tab', None)
    if target_tab_index is None:
        target_tab_index = self.tab_widget.currentIndex()
    
    # Container al
    container = self.graph_containers[target_tab_index]
    
    # İşlemi uygula
    # ...
```

### Test Senaryoları

#### Test 1: Tab Değişimi
```python
1. Tab 1'de dialog aç
2. Filter ekle (Motor_Speed > 1000)
3. Dialog açıkken Tab 2'ye geç
4. OK'a bas
5. ✅ Filter Tab 1'e uygulanmalı
6. ✅ Tab 2 etkilenmemeli
```

#### Test 2: Çoklu Tab
```python
1. Tab 1'e filter ekle
2. Tab 2'e farklı filter ekle
3. Her iki tab'ı kontrol et
4. ✅ Filtreler izole olmalı
```

### Beklenen Süre
2-3 saat

---

## 4. Real-time Data Streaming

### Özet
Dış kaynaklardan canlı veri akışı desteği.

### Mevcut Durum
❌ **Yok**

### Gereksinimler

#### 1. Socket Manager

**Dosya:** `src/managers/socket_manager.py` (Yeni)

```python
class SocketManager(QObject):
    """Veri akışı yönetimi"""
    
    data_received = Signal(dict)  # {timestamp: value, ...}
    connection_status = Signal(bool)  # Connected/Disconnected
    
    def __init__(self):
        super().__init__()
        self.socket = None
        self.buffer = deque(maxlen=10000)  # Ring buffer
        self.thread = None
    
    def connect(self, host, port):
        """Socket bağlantısı kur"""
        # TCP socket
        pass
    
    def disconnect(self):
        """Bağlantıyı kes"""
        pass
    
    def start_streaming(self):
        """Veri akışını başlat"""
        pass
```

#### 2. Data Handler

```python
class StreamingDataHandler:
    """Veri akışı işleme"""
    
    def __init__(self, buffer_size=10000):
        self.buffer = deque(maxlen=buffer_size)
        self.time_window = 60  # 60 saniye
    
    def add_data(self, timestamp, values):
        """Yeni veri ekle"""
        # Eski verileri sil (time window dışında)
        # Yeni veriyi ekle
        pass
```

#### 3. UI Integration

**Dosya:** `time_graph_widget.py`

```python
def _setup_streaming(self):
    """Streaming UI'ı kur"""
    # Toolbar'a streaming butonu
    streaming_action = QAction("Start Streaming", self)
    streaming_action.triggered.connect(self._on_streaming_toggled)
    
    # Status bar'da connection indicator
    self.streaming_indicator = QLabel("●")
    self.status_bar.addPermanentWidget(self.streaming_indicator)

def _on_streaming_toggled(self):
    """Streaming toggle"""
    if not hasattr(self, 'socket_manager'):
        # İlk kez açılıyor
        self._show_streaming_dialog()
    else:
        # Streaming'i kapat
        self.socket_manager.disconnect()
```

### Test Senaryoları

#### Test 1: Basic Streaming
```python
1. "Start Streaming" butonuna bas
2. Socket adresini gir (localhost:8080)
3. Veri akışı başlamalı
4. Grafik gerçek zamanlı güncellenmeli
```

### Beklenen Süre
1 hafta

---

## 5. Export Geliştirmeleri

### Özet
Yüksek kaliteli görsel export özellikleri.

### Mevcut Durum
⚠️ **Temel Export Var** - Kalite düşük

### Gereksinimler

#### 1. PNG Export (Yüksek Çözünürlük)

**Dosya:** `time_graph_widget.py`

```python
def export_graph_as_png(self, filepath, dpi=300, width=10, height=8):
    """Grafiği yüksek çözünürlüklü PNG olarak kaydet"""
    # Pencere boyutunu kaydet
    original_size = self.size()
    
    # Yeni boyutu ayarla
    target_size = QSize(int(width * dpi), int(height * dpi))
    self.resize(target_size)
    
    # Render et
    pixmap = self.grab()
    
    # PNG olarak kaydet
    pixmap.save(filepath, "PNG", quality=100)
    
    # Orijinal boyutu geri yükle
    self.resize(original_size)
```

#### 2. PDF Export

**Kütüphane:** reportlab

```python
def export_as_pdf(self, filepath):
    """Grafikleri PDF olarak kaydet"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(filepath, pagesize=letter)
    
    # Her grafik için sayfa
    for i, plot_widget in enumerate(self.plot_widgets):
        # PNG'e çevir
        pixmap = plot_widget.grab()
        temp_path = f"/tmp/graph_{i}.png"
        pixmap.save(temp_path)
        
        # PDF'e ekle
        c.drawImage(temp_path, 50, 650, width=500, height=350)
        c.showPage()
    
    c.save()
```

#### 3. Excel Report

```python
def export_statistics_to_excel(self, filepath):
    """İstatistikleri Excel'e aktar"""
    import pandas as pd
    
    # İstatistikleri topla
    stats_data = []
    for signal in self.visible_signals:
        stats_data.append({
            'Signal': signal,
            'Min': self.stats_panel.get_min(signal),
            'Max': self.stats_panel.get_max(signal),
            'Mean': self.stats_panel.get_mean(signal),
            'Std': self.stats_panel.get_std(signal)
        })
    
    # DataFrame oluştur
    df = pd.DataFrame(stats_data)
    
    # Excel'e kaydet
    df.to_excel(filepath, index=False, engine='openpyxl')
```

### Test Senaryoları

#### Test 1: PNG Export
```python
1. Grafik oluştur
2. File > Export > PNG
3. DPI seç (300)
4. Kaydet
5. ✅ Yüksek kaliteli PNG oluşturulmalı
```

### Beklenen Süre
3-4 gün

---

## 📝 Kullanım Notları

### Geliştirme Workflow

1. **ROADMAP.md'den öğeyi seç**
   - Bug mı, özellik mi?
   - Öncelik nedir?
   - Tahmini süre?

2. **FEATURE_DEFINITIONS.md'den detayları oku**
   - Teknik gereksinimler
   - Dosyalar
   - Test senaryoları

3. **Kod geliştir**
   - Feature branch oluştur
   - Kod yaz
   - Test et

4. **ROADMAP.md'i güncelle**
   - Tamamlandı olarak işaretle
   - Not ekle

### Prompt Örneği

```
ROADMAP.md'deki "Filter Dialog State Management" 
özelliğini implement et. FEATURE_DEFINITIONS.md'deki
detaylı gereksinimleri kullan. Test senaryolarını 
kontrol et ve sonucu bildir.
```

---

**Son Güncelleme:** 2025-01-21  
**Doküman Sahibi:** Development Team
