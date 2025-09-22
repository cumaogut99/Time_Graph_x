# 🔒 GitHub Private Repository Kurulum Kılavuzu

Bu kılavuz Time Graph uygulamasını GitHub'da private repository olarak nasıl kuracağınızı ve kullanıcılara sadece EXE dosyasını nasıl dağıtacağınızı açıklar.

## 🎯 Hedef

- ✅ Kaynak kod korumalı (private repository)
- ✅ Kullanıcılar sadece EXE indirebilir
- ✅ Otomatik build ve release sistemi
- ✅ Profesyonel dağıtım

## 📋 Adım Adım Kurulum

### 1. GitHub Repository Oluşturma

1. **GitHub'a giriş yapın**
2. **New Repository** butonuna tıklayın
3. **Repository ayarları:**
   - **Name:** `time-graph-app` (veya istediğiniz isim)
   - **Description:** "Professional data analysis and visualization application"
   - **Visibility:** ⚠️ **Private** (ÖNEMLİ!)
   - **Initialize:** README, .gitignore ve license eklemeyin (zaten var)

### 2. Local Repository Bağlama

```bash
# Git repository'yi başlat (eğer henüz başlatmadıysanız)
git init

# Dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: Time Graph Application"

# GitHub repository'yi remote olarak ekle
git remote add origin https://github.com/KULLANICI_ADINIZ/time-graph-app.git

# Ana branch'i push et
git branch -M main
git push -u origin main
```

### 3. GitHub Actions Ayarları

Repository oluşturulduktan sonra:

1. **Settings** sekmesine gidin
2. **Actions** > **General** bölümüne gidin
3. **Actions permissions:** "Allow all actions and reusable workflows" seçin
4. **Workflow permissions:** "Read and write permissions" seçin
5. **Save** butonuna tıklayın

### 4. İlk Release Oluşturma

```bash
# Release script'ini çalıştır
python create_release.py
```

Bu script:
- Sürüm numarası önerir
- EXE dosyasını build eder
- Git tag oluşturur
- GitHub Actions'ı tetikler

### 5. Repository Ayarları

#### Private Repository Avantajları:
- ✅ Kaynak kod gizli
- ✅ Seçili kişilere erişim
- ✅ Ticari kullanım uygun
- ✅ Unlimited private repositories (GitHub Pro)

#### Public Releases:
- ✅ EXE dosyaları herkese açık
- ✅ Kaynak kod gizli kalır
- ✅ Professional görünüm

## 🚀 Otomatik Build Sistemi

### GitHub Actions Workflow

`.github/workflows/build-release.yml` dosyası:

- **Tetikleyici:** Git tag push edildiğinde
- **Platform:** Windows Server (latest)
- **Çıktı:** `TimeGraphApp-Windows.zip`
- **Hedef:** GitHub Releases

### Build Süreci

1. **Kod checkout**
2. **Python kurulumu**
3. **Dependency yükleme**
4. **İkon dönüştürme**
5. **EXE oluşturma**
6. **ZIP paketleme**
7. **Release yayınlama**

## 📥 Kullanıcı Deneyimi

### İndirme Süreci (Kullanıcı Perspektifi)

1. **GitHub repository sayfasına git**
2. **Releases** sekmesine tıkla
3. **Latest release** bölümünden `TimeGraphApp-Windows.zip` indir
4. **ZIP'i aç** ve `TimeGraphApp.exe` çalıştır

### Kullanıcılar Göremez:
- ❌ Kaynak kod dosyaları
- ❌ Python script'leri
- ❌ Geliştirme araçları
- ❌ Build process detayları

### Kullanıcılar Görebilir:
- ✅ Release notları
- ✅ EXE dosyası
- ✅ Kullanım kılavuzu (README_USER.md)
- ✅ Sürüm geçmişi

## 🔧 Yönetim

### Yeni Sürüm Yayınlama

```bash
# 1. Değişiklikleri commit et
git add .
git commit -m "Feature: New awesome feature"
git push

# 2. Release oluştur
python create_release.py

# 3. GitHub Actions otomatik build yapar
# 4. Birkaç dakika sonra Releases'da görünür
```

### Sürüm Numaralandırma

- **Major:** `v2.0.0` (büyük değişiklikler)
- **Minor:** `v1.1.0` (yeni özellikler)
- **Patch:** `v1.0.1` (hata düzeltmeleri)

### Erişim Kontrolü

Private repository'de:

1. **Settings** > **Manage access**
2. **Invite a collaborator** (gerekirse)
3. **Role:** Read, Write, Admin

## 📊 İstatistikler ve İzleme

### GitHub Insights

- **Traffic:** İndirme sayıları
- **Releases:** Sürüm istatistikleri
- **Issues:** Kullanıcı geri bildirimleri

### Release Metrikleri

- İndirme sayıları
- Platform dağılımı
- Sürüm adoption oranları

## 🛡️ Güvenlik

### Private Repository Güvenliği

- ✅ Kaynak kod korumalı
- ✅ Seçili erişim
- ✅ Audit log
- ✅ Branch protection

### EXE Güvenliği

- ⚠️ Windows Defender uyarısı normal
- 💡 Code signing sertifikası önerilir
- 🔒 Antivirus whitelist gerekebilir

## 💰 Maliyet

### GitHub Pricing

- **Free:** Public repositories unlimited
- **Pro ($4/ay):** Private repositories unlimited
- **Team ($4/user/ay):** Team features
- **Enterprise:** Advanced features

### Önerilen Plan

**GitHub Pro** - Şirket kullanımı için ideal:
- ✅ Unlimited private repositories
- ✅ Advanced tools
- ✅ Professional appearance
- ✅ Priority support

## 🎉 Sonuç

Bu kurulum ile:

1. **Kaynak kodunuz güvende** (private repository)
2. **Kullanıcılar sadece EXE indirebilir**
3. **Otomatik build sistemi** çalışır
4. **Profesyonel dağıtım** sağlanır
5. **Ticari kullanım** için uygun

---

**Sonraki Adım:** Repository oluşturduktan sonra `python create_release.py` komutunu çalıştırarak ilk release'inizi yayınlayın! 🚀
