# 🔍 DEBUG: Range Filter Sorunu

## 🐛 **SORUN**
Range filter uygulandığında hiçbir log gözükmüyor ve filter çalışmıyor.

## 🔧 **DEBUG LOGLARI EKLENDİ**

### **src/ui/graph_advanced_settings_dialog.py**

**1. OK Butonu:**
```python
def accept(self):
    logger.info("[DIALOG] ==================== OK BUTTON CLICKED ====================")
    logger.info(f"[DIALOG] Graph index: {self.graph_index}")
    logger.info("[DIALOG] Starting _apply_settings()...")
    self._apply_settings()
    logger.info("[DIALOG] _apply_settings() completed")
```

**2. Range Filter Emit:**
```python
filter_conditions = self.parameter_filters_panel.get_range_filter_conditions()
logger.info(f"[DIALOG] Emitting Range Filter signal: {num_conditions} conditions, mode: {filter_conditions.get('mode', 'N/A')}")
logger.info(f"[DIALOG] Filter data: {filter_conditions}")
self.range_filter_applied.emit(filter_conditions)
logger.info(f"[DIALOG] Range filter signal EMITTED successfully")
```

### **time_graph_widget.py**

**3. Filter Alındı:**
```python
def _apply_range_filter(self, filter_data: dict):
    logger.info("=" * 80)
    logger.info("[FILTER] _apply_range_filter() CALLED!")
    logger.info(f"[FILTER] Received filter_data: {filter_data}")
    logger.info(f"[FILTER] target_tab_index: {target_tab_index}")
```

---

## 🧪 **TEST ADIMLARI**

### **1. Uygulamayı Başlat**
```bash
python app.py
```

### **2. Filter Test**
1. Dosya yükle (CSV/Excel)
2. Advanced Settings aç
3. **Range Filter** ekle:
   - Parameter: (herhangi bir parametre)
   - Operator: > (Greater than)
   - Value: 100
   - Mode: Segmented veya Concatenated
4. **OK tuşuna bas**

### **3. Terminal Loglarını Kontrol Et**

**BEKLENİLEN LOGLAR:**
```
[DIALOG] ==================== OK BUTTON CLICKED ====================
[DIALOG] Graph index: 0
[DIALOG] Starting _apply_settings()...
[DIALOG] Applying ALL settings for graph 0...
[DIALOG] Emitting Range Filter signal: 1 conditions, mode: segmented
[DIALOG] Filter data: {'conditions': [...], 'mode': 'segmented', 'graph_index': 0}
[DIALOG] Range filter signal EMITTED successfully
[DIALOG] _apply_settings() completed
[DIALOG] Calling super().accept() to close dialog
================================================================================
[FILTER] _apply_range_filter() CALLED!
[FILTER] Received filter_data: {'conditions': [...], 'mode': 'segmented', 'graph_index': 0}
[FILTER] target_tab_index: 0
[FILTER] graph_containers count: 1
[FILTER] Applying filter to target_tab_index: 0 (dialog opened for this tab)
```

---

## 🔍 **SORUN TESPİTİ**

### **Durum 1: Hiçbir Log Gözükmüyor**
❌ **Problem:** OK butonu çalışmıyor veya dialog accept() çağrılmıyor
- Dialog hatalı kapanıyor olabilir
- Exception oluşuyor olabilir

### **Durum 2: [DIALOG] Logları Var, [FILTER] Logları Yok**
❌ **Problem:** Signal bağlantısı kopuk!
```python
# time_graph_widget.py satır 883
dialog.range_filter_applied.connect(self._apply_range_filter)
```
Bu satır çalışmıyor veya signal emit edilemiyor.

**MUHTEMEL NEDENLER:**
1. `parameter_filters_panel` yüklenmemiş (deferred creation)
2. `get_range_filter_conditions()` exception fırlatıyor
3. Signal emit edilirken exception oluşuyor

### **Durum 3: Her İki Log da Var Ama Filter Uygulanmıyor**
❌ **Problem:** Filter logic hatası
- `can_apply` check başarısız
- `conditions` boş
- `target_tab_index` hatalı

### **Durum 4: Exception Görünüyor**
❌ **Problem:** Kod hatası
- Exception mesajını inceleyin
- Stack trace'e bakın

---

## 🛠️ **OLASI ÇÖZÜMLER**

### **1. Deferred Panel Creation Sorunu**
Eğer `parameter_filters_panel` henüz oluşturulmamışsa:

```python
# Dialog açıldığında panel henüz yüklenmemiş olabilir
# _create_deferred_panels() çağrıldığından emin olun
```

**Çözüm:** Dialog açıldıktan sonra panellerin yüklenmesini bekleyin.

### **2. Signal Connection Sorunu**
Signal bağlantısı dialog oluşturulmadan önce yapılıyor olabilir:

```python
# time_graph_widget.py
dialog = GraphAdvancedSettingsDialog(...)
# Panel henüz oluşturulmadı!
dialog.range_filter_applied.connect(self._apply_range_filter)  # ❌
```

### **3. Exception Swallow**
Exception yakalanıp log edilmiyor olabilir:

```python
try:
    self.range_filter_applied.emit(filter_conditions)
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)  # ✅ exc_info eklendi
```

---

## 📋 **RAPOR İSTENENLER**

Lütfen şu bilgileri paylaşın:

1. **Terminal çıktısı:**
   - Hangi loglar gözüküyor?
   - Hangi loglar gözükmüyor?
   - Exception var mı?

2. **Filter ayarları:**
   - Hangi parametreyi seçtiniz?
   - Hangi operatör? (>, <, ==, !=, >=, <=)
   - Hangi değer?
   - Hangi mode? (segmented / concatenated)

3. **Ek bilgiler:**
   - Kaç sekme var?
   - Hangi sekmedesiniz?
   - Kaç grafik var?

---

## ✅ **BAŞARILI TEST ÇIKTISI ÖRNEĞİ**

```
[DIALOG] ==================== OK BUTTON CLICKED ====================
[DIALOG] Graph index: 0
[DIALOG] Starting _apply_settings()...
[DIALOG] Applying ALL settings for graph 0...
[DIALOG] Emitting Range Filter signal: 1 conditions, mode: segmented
[DIALOG] Filter data: {'conditions': [{'parameter': 'RPM', 'operator': '>', 'value': 1000.0}], 'mode': 'segmented', 'graph_index': 0}
[DIALOG] Range filter signal EMITTED successfully
[DIALOG] Finished applying all settings for graph 0
[DIALOG] _apply_settings() completed
[DIALOG] Calling super().accept() to close dialog
[DIALOG] Dialog closed
[DIALOG] Updated signals for Tab 0, Graph 0: ['RPM', 'Torque']
================================================================================
[FILTER] _apply_range_filter() CALLED!
[FILTER] Received filter_data: {'conditions': [{'parameter': 'RPM', 'operator': '>', 'value': 1000.0}], 'mode': 'segmented', 'graph_index': 0}
[FILTER] target_tab_index: 0
[FILTER] graph_containers count: 1
[FILTER] Applying filter to target_tab_index: 0 (dialog opened for this tab)
[FILTER MODE] Concatenated mode: False, Active filters count: 0
[SEGMENTED DEBUG] Starting segmented filter application
[SEGMENTED DEBUG] Graph index: 0, Tab index: 0
[SEGMENTED DEBUG] Time segments: 5 segments
...
```

Bu çıktı gözüküyorsa **filter çalışıyor demektir!** ✅

---

**Test sonuçlarını paylaşın!**

