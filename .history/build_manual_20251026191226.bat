@echo off
REM ============================================
REM Time Graph X - Kullanım Kılavuzu Builder
REM ============================================
REM Bu script Markdown dosyasını PDF'e dönüştürür

echo.
echo ==========================================
echo Time Graph X - Manual Builder
echo ==========================================
echo.

REM Renk kodları için
set GREEN=[92m
set RED=[91m
set YELLOW=[93m
set RESET=[0m

REM 1. Pandoc kontrolü
echo [1/5] Pandoc kontrolu...
where pandoc >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%HATA: Pandoc bulunamadi!%RESET%
    echo.
    echo Pandoc yuklemeniz gerekiyor:
    echo https://pandoc.org/installing.html
    echo.
    pause
    exit /b 1
)
echo %GREEN%OK - Pandoc bulundu%RESET%

REM 2. Screenshot klasörü kontrolü
echo [2/5] Screenshot klasoru kontrolu...
if not exist "screenshots\" (
    echo %YELLOW%UYARI: screenshots klasoru bulunamadi!%RESET%
    echo Gorseller olmadan PDF olusturulacak.
    echo.
    mkdir screenshots
)
echo %GREEN%OK - Screenshots klasoru mevcut%RESET%

REM 3. Kaynak dosya kontrolü
echo [3/5] Kaynak dosya kontrolu...
if not exist "KULLANIM_KLAVUZU_TR.md" (
    echo %RED%HATA: KULLANIM_KLAVUZU_TR.md bulunamadi!%RESET%
    pause
    exit /b 1
)
echo %GREEN%OK - Kaynak dosya mevcut%RESET%

REM 4. PDF oluştur
echo [4/5] PDF olusturuluyor...
echo Bu islem 30-60 saniye surebilir...
echo.

pandoc KULLANIM_KLAVUZU_TR.md -o KULLANIM_KLAVUZU_TR.pdf ^
  --pdf-engine=xelatex ^
  --toc ^
  --toc-depth=2 ^
  --number-sections ^
  -V geometry:margin=2cm ^
  -V fontsize=11pt ^
  -V documentclass=report ^
  -V lang=tr-TR ^
  -V papersize=a4 ^
  -V linestretch=1.15 ^
  --highlight-style=tango

if %errorlevel% neq 0 (
    echo %RED%HATA: PDF olusturulamadi!%RESET%
    echo.
    echo Olasi sebepler:
    echo - LaTeX yuklu degil (MiKTeX veya TeX Live gerekli)
    echo - Markdown syntax hatasi
    echo - Eksik gorsel dosyasi
    echo.
    pause
    exit /b 1
)
echo %GREEN%OK - PDF basariyla olusturuldu!%RESET%

REM 5. Dosya bilgisi
echo [5/5] Dosya bilgileri...
for %%A in (KULLANIM_KLAVUZU_TR.pdf) do (
    echo Dosya adi: %%~nxA
    echo Boyut: %%~zA bytes
    echo Konum: %CD%\%%~nxA
)
echo.

echo %GREEN%==========================================
echo BASARILI! PDF hazir.
echo ==========================================%RESET%
echo.
echo KULLANIM_KLAVUZU_TR.pdf dosyasini acabilirsiniz.
echo.

REM PDF'i otomatik aç (opsiyonel)
choice /C YN /M "PDF dosyasini simdi acmak ister misiniz"
if %errorlevel% equ 1 (
    start KULLANIM_KLAVUZU_TR.pdf
)

pause

