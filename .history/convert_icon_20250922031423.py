#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İkon Dönüştürücü
================

PNG formatındaki ikonu ICO formatına çevirir.
"""

from PIL import Image
import os

def convert_png_to_ico(png_path, ico_path):
    """PNG dosyasını ICO formatına çevir."""
    try:
        # PNG dosyasını aç
        img = Image.open(png_path)
        
        # RGBA moduna çevir (şeffaflık için)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Farklı boyutlarda ikonlar oluştur (Windows standartları)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Her boyut için resmi yeniden boyutlandır
        icons = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # ICO dosyası olarak kaydet
        icons[0].save(ico_path, format='ICO', sizes=[icon.size for icon in icons])
        
        print(f"✅ İkon başarıyla dönüştürüldü: {ico_path}")
        return True
        
    except Exception as e:
        print(f"❌ İkon dönüştürme hatası: {e}")
        return False

if __name__ == "__main__":
    png_file = "ikon.png"
    ico_file = "ikon.ico"
    
    if os.path.exists(png_file):
        success = convert_png_to_ico(png_file, ico_file)
        if success:
            print(f"📁 ICO dosyası oluşturuldu: {ico_file}")
        else:
            print("❌ Dönüştürme başarısız!")
    else:
        print(f"❌ PNG dosyası bulunamadı: {png_file}")
