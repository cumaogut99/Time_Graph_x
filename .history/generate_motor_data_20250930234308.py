"""
350 kolonlu gerçekçi pistonlu motor test verisi oluşturucu
25 MB'dan küçük CSV dosyası
"""

import numpy as np
import polars as pl
from pathlib import Path

# Veri boyutunu hesapla
target_size_mb = 11  # 25 MB'dan küçük kalması için
bytes_per_row = 350 * 8  # 350 float, her biri ~8 byte
target_rows = int((target_size_mb * 1024 * 1024) / bytes_per_row)

print("350 Kolonlu Motor Test Verisi Olusturuluyor...")
print(f"Hedef satır sayısı: {target_rows:,}")

# Zaman verisi (saniye cinsinden)
sampling_rate = 1000  # Hz
duration = target_rows / sampling_rate
time = np.linspace(0, duration, target_rows)

# Motor parametreleri
rpm = 3000  # Devir/dakika
frequency = rpm / 60  # Hz
omega = 2 * np.pi * frequency

# Veri sözlüğü
data = {'Time': time}

# 1. SILINDIR BASINCI (16 silindir × 4 ölçüm noktası = 64 sütun)
print("  - Silindir basınçları oluşturuluyor...")
for cyl in range(1, 17):  # 16 silindir
    phase_offset = (cyl - 1) * (2 * np.pi / 16)  # Her silindir faz farkı
    
    for point in range(1, 5):  # Her silindirde 4 ölçüm noktası
        base_pressure = 20 + np.random.uniform(-2, 2)  # bar
        pressure = base_pressure + 30 * np.sin(omega * time + phase_offset) + \
                   5 * np.sin(2 * omega * time + phase_offset) + \
                   np.random.normal(0, 1, target_rows)
        pressure = np.maximum(pressure, 0)  # Negatif basınç olmasın
        
        data[f'Cyl{cyl}_P{point}'] = pressure

# 2. SICAKLIK SENSÖRLERİ (80 sütun)
print("  - Sıcaklık sensörleri oluşturuluyor...")
# Egzoz sıcaklıkları (16 silindir)
for cyl in range(1, 17):
    phase_offset = (cyl - 1) * (2 * np.pi / 16)
    base_temp = 450 + np.random.uniform(-20, 20)
    temp = base_temp + 50 * np.sin(omega * time + phase_offset) + \
           10 * np.random.normal(0, 1, target_rows)
    data[f'Cyl{cyl}_ExhaustTemp'] = temp

# Soğutma suyu sıcaklıkları (16 silindir)
for cyl in range(1, 17):
    base_temp = 85 + np.random.uniform(-3, 3)
    temp = base_temp + 2 * np.sin(0.1 * time) + np.random.normal(0, 0.5, target_rows)
    data[f'Cyl{cyl}_CoolantTemp'] = temp

# Yağ sıcaklıkları (16 silindir)
for cyl in range(1, 17):
    base_temp = 95 + np.random.uniform(-5, 5)
    temp = base_temp + 3 * np.sin(0.05 * time) + np.random.normal(0, 0.8, target_rows)
    data[f'Cyl{cyl}_OilTemp'] = temp

# Piston sıcaklıkları (16 silindir)
for cyl in range(1, 17):
    phase_offset = (cyl - 1) * (2 * np.pi / 16)
    base_temp = 320 + np.random.uniform(-15, 15)
    temp = base_temp + 30 * np.sin(omega * time + phase_offset) + \
           8 * np.random.normal(0, 1, target_rows)
    data[f'Cyl{cyl}_PistonTemp'] = temp

# Silindir kafası sıcaklıkları (16 silindir)
for cyl in range(1, 17):
    base_temp = 280 + np.random.uniform(-10, 10)
    temp = base_temp + 15 * np.sin(0.2 * time) + np.random.normal(0, 2, target_rows)
    data[f'Cyl{cyl}_HeadTemp'] = temp

# 3. TİTREŞİM SENSÖRLERİ (48 sütun)
print("  - Titreşim sensörleri oluşturuluyor...")
for cyl in range(1, 17):  # 16 silindir
    phase_offset = (cyl - 1) * (2 * np.pi / 16)
    
    # X, Y, Z ekseni titreşimleri
    for axis in ['X', 'Y', 'Z']:
        vibration = 0.5 * np.sin(omega * time + phase_offset) + \
                    0.3 * np.sin(2 * omega * time) + \
                    0.1 * np.sin(4 * omega * time) + \
                    np.random.normal(0, 0.05, target_rows)
        data[f'Cyl{cyl}_Vib_{axis}'] = vibration

# 4. YAKIT SİSTEMİ (32 sütun)
print("  - Yakıt sistemi verileri oluşturuluyor...")
for cyl in range(1, 17):
    # Enjektör basıncı
    base_pressure = 800 + np.random.uniform(-50, 50)  # bar
    pressure = base_pressure + 100 * np.sin(omega * time) + \
               np.random.normal(0, 10, target_rows)
    data[f'Cyl{cyl}_FuelPressure'] = pressure
    
    # Yakıt debisi
    base_flow = 15 + np.random.uniform(-1, 1)  # g/s
    flow = base_flow + 3 * np.sin(omega * time) + \
           np.random.normal(0, 0.5, target_rows)
    data[f'Cyl{cyl}_FuelFlow'] = flow

# 5. HAVA SİSTEMİ (32 sütun)
print("  - Hava sistemi verileri oluşturuluyor...")
for cyl in range(1, 17):
    # Emme manifold basıncı
    base_pressure = 2.5 + np.random.uniform(-0.1, 0.1)  # bar
    pressure = base_pressure + 0.3 * np.sin(omega * time) + \
               np.random.normal(0, 0.05, target_rows)
    data[f'Cyl{cyl}_IntakePress'] = pressure
    
    # Hava debisi
    base_flow = 200 + np.random.uniform(-10, 10)  # kg/h
    flow = base_flow + 30 * np.sin(omega * time) + \
           np.random.normal(0, 5, target_rows)
    data[f'Cyl{cyl}_AirFlow'] = flow

# 6. TORK VE GÜÇ (16 sütun)
print("  - Tork ve güç verileri oluşturuluyor...")
for cyl in range(1, 17):
    phase_offset = (cyl - 1) * (2 * np.pi / 16)
    
    # Her silindir torku
    base_torque = 500 / 16 + np.random.uniform(-2, 2)  # Nm
    torque = base_torque + 5 * np.sin(omega * time + phase_offset) + \
             np.random.normal(0, 0.5, target_rows)
    data[f'Cyl{cyl}_Torque'] = torque

# 7. EGR VE EMİSYON (16 sütun)
print("  - Emisyon sensörleri oluşturuluyor...")
for cyl in range(1, 17):
    # NOx seviyesi
    base_nox = 450 + np.random.uniform(-50, 50)  # ppm
    nox = base_nox + 100 * np.sin(0.3 * time) + \
          np.random.normal(0, 20, target_rows)
    data[f'Cyl{cyl}_NOx'] = nox

# 8. TURBO (16 sütun)
print("  - Turbo verileri oluşturuluyor...")
for turbo in range(1, 5):  # 4 turbo (her 4 silindir için 1)
    # Turbo hızı
    base_speed = 100000 + np.random.uniform(-5000, 5000)  # rpm
    speed = base_speed + 20000 * np.sin(0.5 * time) + \
            np.random.normal(0, 2000, target_rows)
    data[f'Turbo{turbo}_Speed'] = speed
    
    # Turbo basıncı
    base_pressure = 2.8 + np.random.uniform(-0.2, 0.2)  # bar
    pressure = base_pressure + 0.5 * np.sin(0.5 * time) + \
               np.random.normal(0, 0.1, target_rows)
    data[f'Turbo{turbo}_Pressure'] = pressure
    
    # Turbo sıcaklığı
    base_temp = 650 + np.random.uniform(-30, 30)  # °C
    temp = base_temp + 80 * np.sin(0.3 * time) + \
           np.random.normal(0, 10, target_rows)
    data[f'Turbo{turbo}_Temp'] = temp
    
    # Turbo debisi
    base_flow = 800 + np.random.uniform(-40, 40)  # kg/h
    flow = base_flow + 150 * np.sin(0.5 * time) + \
           np.random.normal(0, 20, target_rows)
    data[f'Turbo{turbo}_Flow'] = flow

# 9. GENEL MOTOR PARAMETRELERİ (kalan sütunları doldur)
print("  - Genel motor parametreleri oluşturuluyor...")

# Motor devri
rpm_signal = rpm + 100 * np.sin(0.1 * time) + np.random.normal(0, 20, target_rows)
data['Engine_RPM'] = rpm_signal

# Toplam tork
total_torque = 500 + 50 * np.sin(omega * time) + np.random.normal(0, 10, target_rows)
data['Engine_Torque_Total'] = total_torque

# Toplam güç
power = (total_torque * rpm_signal * 2 * np.pi) / 60000  # kW
data['Engine_Power_Total'] = power

# Yağ basıncı
oil_pressure = 6.5 + 0.5 * np.sin(0.05 * time) + np.random.normal(0, 0.1, target_rows)
data['Engine_OilPressure'] = oil_pressure

# Soğutma suyu basıncı
coolant_pressure = 1.8 + 0.2 * np.sin(0.1 * time) + np.random.normal(0, 0.05, target_rows)
data['Engine_CoolantPressure'] = coolant_pressure

# Lambda (hava/yakıt oranı)
lambda_val = 1.0 + 0.05 * np.sin(0.2 * time) + np.random.normal(0, 0.02, target_rows)
data['Engine_Lambda'] = lambda_val

# Ateşleme avansı
ignition = 15 + 5 * np.sin(0.3 * time) + np.random.normal(0, 1, target_rows)
data['Engine_IgnitionAdvance'] = ignition

# Gaz kelebeği pozisyonu
throttle = 75 + 10 * np.sin(0.15 * time) + np.random.normal(0, 2, target_rows)
throttle = np.clip(throttle, 0, 100)
data['Engine_ThrottlePos'] = throttle

# Turbo wastegate pozisyonu
wastegate = 30 + 15 * np.sin(0.4 * time) + np.random.normal(0, 3, target_rows)
wastegate = np.clip(wastegate, 0, 100)
data['Engine_WastegatePos'] = wastegate

# Eksik kolonları tamamla (350'ye ulaşmak için)
current_cols = len(data)
remaining_cols = 350 - current_cols
if remaining_cols > 0:
    for i in range(remaining_cols):
        # Rastgele sensör verileri ekle
        sensor_data = 50 + 10 * np.sin((i+1) * 0.1 * time) + np.random.normal(0, 2, target_rows)
        data[f'Sensor_Extra_{i+1:03d}'] = sensor_data

# DataFrame oluştur
print("  - DataFrame oluşturuluyor...")
df = pl.DataFrame(data)

# Kolon sayısını kontrol et
actual_columns = len(df.columns)
print(f"[OK] Toplam kolon sayisi: {actual_columns}")

# Dosya boyutunu tahmin et
print("  - CSV dosyası yazılıyor...")
output_file = "motor_test_data_350col.csv"
df.write_csv(output_file)

# Dosya boyutunu kontrol et
file_size_mb = Path(output_file).stat().st_size / (1024 * 1024)

print(f"\n{'='*60}")
print(f"[OK] BASARIYLA OLUSTURULDU!")
print(f"{'='*60}")
print(f"Dosya: {output_file}")
print(f"Satir sayisi: {target_rows:,}")
print(f"Kolon sayisi: {actual_columns}")
print(f"Dosya boyutu: {file_size_mb:.2f} MB")
print(f"Sure: {duration:.1f} saniye motor verisi")
print(f"Ornekleme hizi: {sampling_rate} Hz")
print(f"Motor tipi: 16 silindirli pistonlu motor")
print(f"{'='*60}")
print("\nTest icin hazir! Uygulamada yukleyebilirsin.")

