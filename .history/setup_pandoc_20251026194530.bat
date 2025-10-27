@echo off
REM ============================================
REM Pandoc Kurulum Yardimcisi
REM ============================================

echo.
echo ==========================================
echo Pandoc Kurulum Yardimcisi
echo ==========================================
echo.

REM Mevcut Pandoc kontrolu
where pandoc >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Pandoc zaten kurulu!
    pandoc --version
    echo.
    echo Kurulum gerekli degil.
    pause
    exit /b 0
)

echo Pandoc bulunamadi. Kurulum gerekli.
echo.
echo ==========================================
echo SECENEKLER:
echo ==========================================
echo.
echo 1. OTOMATIK KURULUM (Winget - Kolay)
echo    - Windows Package Manager kullanir
echo    - Otomatik indirir ve kurar
echo    - Sistem genelinde kullanilabilir
echo.
echo 2. PORTABLE VERSIYON (ZIP - Hizli)
echo    - Kurulum gerektirmez
echo    - Sadece bu proje icin
echo    - PATH'e eklenmez (script'lerle kullanilir)
echo.
echo 3. MANUEL KURULUM (MSI - Geleneksel)
echo    - Installer indirilecek
echo    - Siz yukleyeceksiniz
echo    - Sistem genelinde kullanilabilir
echo.

choice /C 123Q /M "Seciminiz (1, 2, 3 veya Q-cikis)"
set CHOICE=%errorlevel%

if %CHOICE% equ 4 (
    echo Iptal edildi.
    pause
    exit /b 0
)

if %CHOICE% equ 1 goto :winget_install
if %CHOICE% equ 2 goto :portable_install
if %CHOICE% equ 3 goto :manual_install

:winget_install
echo.
echo ==========================================
echo WINGET ile KURULUM
echo ==========================================
echo.
echo Pandoc indiriliyor ve kuruluyor...

winget install --id JohnMacFarlane.Pandoc -e

if %errorlevel% neq 0 (
    echo.
    echo HATA: Winget kurulum basarisiz!
    echo.
    echo Olasi sebepler:
    echo - Winget yuklu degil (Windows 10/11 gerekli)
    echo - Internet baglantisi yok
    echo.
    echo Lutfen Secenek 2 veya 3'u deneyin.
    pause
    exit /b 1
)

echo.
echo [OK] Kurulum tamamlandi!
echo.
echo Lutfen bu terminal'i kapatip yenisini acin.
echo Sonra: pandoc --version
pause
exit /b 0

:portable_install
echo.
echo ==========================================
echo PORTABLE VERSIYON
echo ==========================================
echo.

REM Portable klasor olustur
if not exist "tools\pandoc" mkdir tools\pandoc

echo Pandoc portable indiriliyor...
echo.
echo Indirme baglantisi tarayicida aciliyor...
echo Lutfen pandoc-3.8.2.1-windows-x86_64.zip dosyasini indirin.
echo.

start https://github.com/jgm/pandoc/releases/download/3.8.2.1/pandoc-3.8.2.1-windows-x86_64.zip

echo.
echo ==========================================
echo ADIMLAR:
echo ==========================================
echo.
echo 1. Tarayicidan ZIP dosyasini indirin
echo 2. ZIP'i acin
echo 3. Icindeki 'pandoc.exe' dosyasini buraya kopyalin:
echo    %CD%\tools\pandoc\
echo.
echo 4. Bu script'i tekrar calistirin
echo.

pause

REM Kontrol et
if exist "tools\pandoc\pandoc.exe" (
    echo.
    echo [OK] pandoc.exe bulundu!
    echo Portable versiyon hazir.
    echo.
    echo Script'ler otomatik olarak kullanacak.
) else (
    echo.
    echo [!] pandoc.exe bulunamadi.
    echo Lutfen tools\pandoc\ klasorune kopyalayin.
)

pause
exit /b 0

:manual_install
echo.
echo ==========================================
echo MANUEL KURULUM
echo ==========================================
echo.
echo Installer tarayicida aciliyor...
echo Lutfen pandoc-3.8.2.1-windows-x86_64.msi dosyasini indirin ve calistirin.
echo.

start https://github.com/jgm/pandoc/releases/download/3.8.2.1/pandoc-3.8.2.1-windows-x86_64.msi

echo.
echo ==========================================
echo ADIMLAR:
echo ==========================================
echo.
echo 1. MSI dosyasini indirin
echo 2. Cift tiklayarak calistirin
echo 3. Installer'i takip edin (Next, Next, Install)
echo 4. Kurulum bitince bu terminal'i kapatin
echo 5. Yeni terminal acin
echo 6. Komut: pandoc --version
echo.

pause
exit /b 0

