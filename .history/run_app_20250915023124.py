#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Graph Widget Launcher
==========================

Bu script, time graph widget uygulamasını başlatır.
Relative import sorunlarını çözmek için özel launcher.
"""

import sys
import os
import subprocess

def main():
    """Ana launcher fonksiyonu."""
    print("Time Graph Widget Uygulaması Başlatılıyor...")
    
    # Mevcut dizini Python path'ine ekle
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Python modül olarak çalıştır
    try:
        # app.py'yi modül olarak çalıştır
        cmd = [sys.executable, "-m", "app"]
        
        # Çalışma dizinini ayarla
        env = os.environ.copy()
        env['PYTHONPATH'] = current_dir + os.pathsep + env.get('PYTHONPATH', '')
        
        # Uygulamayı başlat
        result = subprocess.run(cmd, cwd=current_dir, env=env)
        return result.returncode
        
    except Exception as e:
        print(f"Uygulama başlatılamadı: {e}")
        
        # Alternatif yöntem: doğrudan Python script olarak çalıştır
        try:
            print("Alternatif yöntem deneniyor...")
            cmd = [sys.executable, "app.py"]
            result = subprocess.run(cmd, cwd=current_dir, env=env)
            return result.returncode
        except Exception as e2:
            print(f"Alternatif yöntem de başarısız: {e2}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
