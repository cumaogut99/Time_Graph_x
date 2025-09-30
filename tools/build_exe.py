#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXE Build Script - Time Graph Uygulaması
========================================

Bu script Time Graph uygulamasını EXE formatına çevirir.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Gerekli paketlerin yüklü olup olmadığını kontrol et."""
    required_packages = ['pyinstaller', 'pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            if package == 'pillow':
                try:
                    __import__('PIL')
                except ImportError:
                    missing_packages.append(package)
            else:
                missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Eksik paketler: {', '.join(missing_packages)}")
        print(f"📦 Yüklemek için: pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ Tüm gerekli paketler yüklü")
    return True

def clean_build_dirs():
    """Önceki build dosyalarını temizle."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Temizleniyor: {dir_name}")
            shutil.rmtree(dir_name)

def convert_icon():
    """PNG ikonunu ICO formatına çevir."""
    if os.path.exists('ikon.png') and not os.path.exists('ikon.ico'):
        print("🎨 İkon dönüştürülüyor...")
        try:
            subprocess.run([sys.executable, 'convert_icon.py'], check=True)
            print("✅ İkon dönüştürüldü")
        except subprocess.CalledProcessError:
            print("❌ İkon dönüştürme başarısız")
            return False
    elif os.path.exists('ikon.ico'):
        print("✅ İkon zaten mevcut")
    else:
        print("⚠️  İkon dosyası bulunamadı")
    
    return True

def build_exe():
    """EXE dosyasını oluştur."""
    print("🔨 EXE oluşturuluyor...")
    
    try:
        # PyInstaller ile build
        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            'time_graph_app.spec'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ EXE başarıyla oluşturuldu!")
            
            # Dosya boyutunu kontrol et
            exe_path = Path('dist/TimeGraphApp.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📁 EXE dosyası: {exe_path} ({size_mb:.1f} MB)")
            
            return True
        else:
            print("❌ EXE oluşturma başarısız!")
            print("Hata çıktısı:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build hatası: {e}")
        return False

def main():
    """Ana build fonksiyonu."""
    print("🚀 Time Graph EXE Build Başlıyor...")
    print("=" * 50)
    
    # Gerekli paketleri kontrol et
    if not check_requirements():
        return False
    
    # Önceki build'leri temizle
    clean_build_dirs()
    
    # İkonu dönüştür
    if not convert_icon():
        return False
    
    # EXE oluştur
    if not build_exe():
        return False
    
    print("=" * 50)
    print("🎉 Build tamamlandı!")
    print("📁 EXE dosyası: dist/TimeGraphApp.exe")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
