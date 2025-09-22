#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Release Oluşturucu
=========================

Bu script yeni bir GitHub release oluşturur ve EXE dosyasını yükler.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def get_version():
    """Sürüm numarasını al veya oluştur."""
    # Git tag'lerinden son sürümü al
    try:
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            last_tag = result.stdout.strip()
            print(f"📋 Son tag: {last_tag}")
            
            # Yeni sürüm öner
            if last_tag.startswith('v'):
                version_parts = last_tag[1:].split('.')
                if len(version_parts) >= 3:
                    major, minor, patch = map(int, version_parts[:3])
                    new_version = f"v{major}.{minor}.{patch + 1}"
                    print(f"💡 Önerilen yeni sürüm: {new_version}")
                    return new_version
    except:
        pass
    
    # Varsayılan sürüm
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"v1.0.{timestamp}"

def create_tag(version):
    """Git tag oluştur."""
    try:
        # Tag oluştur
        subprocess.run(['git', 'tag', '-a', version, '-m', f'Release {version}'], check=True)
        print(f"✅ Tag oluşturuldu: {version}")
        
        # Tag'i push et
        subprocess.run(['git', 'push', 'origin', version], check=True)
        print(f"📤 Tag push edildi: {version}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tag oluşturma hatası: {e}")
        return False

def build_exe():
    """EXE dosyasını oluştur."""
    print("🔨 EXE oluşturuluyor...")
    
    try:
        # Build script'ini çalıştır
        result = subprocess.run([sys.executable, 'build_exe.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ EXE başarıyla oluşturuldu!")
            return True
        else:
            print("❌ EXE oluşturma başarısız!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build hatası: {e}")
        return False

def check_git_status():
    """Git durumunu kontrol et."""
    try:
        # Uncommitted değişiklikler var mı?
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  Commit edilmemiş değişiklikler var!")
            print("Lütfen önce tüm değişiklikleri commit edin.")
            return False
        
        # Remote repository var mı?
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("⚠️  Git remote repository bulunamadı!")
            print("Lütfen önce GitHub'a repository oluşturun ve bağlayın.")
            return False
        
        print("✅ Git durumu uygun")
        return True
        
    except Exception as e:
        print(f"❌ Git kontrol hatası: {e}")
        return False

def main():
    """Ana release fonksiyonu."""
    print("🚀 GitHub Release Oluşturucu")
    print("=" * 40)
    
    # Git durumunu kontrol et
    if not check_git_status():
        return False
    
    # Sürüm numarasını al
    version = get_version()
    
    # Kullanıcıdan onay al
    user_version = input(f"Sürüm numarası ({version}): ").strip()
    if user_version:
        version = user_version
    
    if not version.startswith('v'):
        version = f"v{version}"
    
    print(f"📦 Release sürümü: {version}")
    
    # Onay al
    confirm = input("Devam etmek istiyor musunuz? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', 'evet', 'e']:
        print("❌ İşlem iptal edildi")
        return False
    
    # EXE oluştur
    if not build_exe():
        return False
    
    # Git tag oluştur ve push et
    if not create_tag(version):
        return False
    
    print("=" * 40)
    print("🎉 Release başarıyla oluşturuldu!")
    print(f"📋 Sürüm: {version}")
    print("🔄 GitHub Actions otomatik olarak EXE'yi build edecek")
    print("📥 Birkaç dakika sonra Releases sayfasından indirilebilir olacak")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
