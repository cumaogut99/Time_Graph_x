@echo off
REM ============================================
REM Time Graph X - Gelismis Manual Builder
REM Kapak sayfasi, header/footer ile PDF olusturur
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo Time Graph X - Advanced Manual Builder
echo ==========================================
echo.

REM 1. Gerekli araçları kontrol et
echo [1/7] Gerekli araclari kontrol ediliyor...
where pandoc >nul 2>nul
if %errorlevel% neq 0 (
    echo HATA: Pandoc bulunamadi!
    echo Indirin: https://pandoc.org/installing.html
    pause
    exit /b 1
)
echo OK - Pandoc mevcut

REM 2. Klasörleri oluştur
echo [2/7] Klasorler hazirlaniyor...
if not exist "screenshots\" mkdir screenshots
if not exist "dist\" mkdir dist
if not exist "temp\" mkdir temp
echo OK - Klasorler hazir

REM 3. Kapak sayfası oluştur
echo [3/7] Kapak sayfasi olusturuluyor...

(
echo ---
echo title: "Time Graph X"
echo subtitle: "Kullanım Kılavuzu"
echo author: "Time Graph X Development Team"
echo date: "Ekim 2025"
echo version: "v1.0.0"
echo ---
echo.
echo \newpage
) > temp\cover.md

echo OK - Kapak sayfasi hazir

REM 4. Pandoc ayar dosyası oluştur
echo [4/7] PDF ayarlari hazirlaniyor...

(
echo geometry:
echo   - margin=2.5cm
echo   - paper=a4paper
echo fontsize: 11pt
echo linestretch: 1.2
echo toc: true
echo toc-depth: 2
echo number-sections: true
echo lang: tr-TR
echo colorlinks: true
echo linkcolor: blue
echo urlcolor: blue
echo toccolor: black
echo header-includes: ^|
echo   \usepackage{fancyhdr}
echo   \pagestyle{fancy}
echo   \fancyhead[L]{Time Graph X}
echo   \fancyhead[R]{Kullanım Kılavuzu v1.0}
echo   \fancyfoot[C]{\thepage}
echo   \usepackage{graphicx}
echo   \usepackage{float}
) > temp\pandoc-settings.yaml

echo OK - PDF ayarlari hazir

REM 5. Markdown dosyalarını birleştir
echo [5/7] Markdown dosyalari birlestiriliyor...
copy /Y temp\cover.md + KULLANIM_KLAVUZU_TR.md temp\full_manual.md >nul
echo OK - Dosyalar birlestirildi

REM 6. PDF oluştur
echo [6/7] PDF olusturuluyor...
echo Bu islem 1-2 dakika surebilir...
echo.

pandoc temp\full_manual.md ^
  -o dist\KULLANIM_KLAVUZU_TR.pdf ^
  --defaults=temp\pandoc-settings.yaml ^
  --pdf-engine=xelatex ^
  --highlight-style=tango ^
  -V documentclass=report

if %errorlevel% neq 0 (
    echo HATA: PDF olusturulamadi!
    echo.
    echo LaTeX yuklu oldugundan emin olun:
    echo - Windows: MiKTeX (https://miktex.org/download)
    echo - Alternatif: TeX Live (https://www.tug.org/texlive/)
    echo.
    pause
    exit /b 1
)
echo OK - PDF olusturuldu!

REM 7. Dağıtım paketi oluştur
echo [7/7] Dagitim paketi hazirlaniyor...

REM Markdown ve PDF'i kopyala
copy /Y KULLANIM_KLAVUZU_TR.md dist\ >nul
copy /Y KULLANIM_KLAVUZU_TR.md KULLANIM_KLAVUZU_TR_backup.md >nul

REM Screenshots kopyala
if exist "screenshots\" (
    xcopy /E /I /Y screenshots dist\screenshots\ >nul
)

REM README oluştur
(
echo TIME GRAPH X - KULLANIM KILAVUZU
echo ================================
echo.
echo Bu klasor Time Graph X v1.0.0 kullanim kilavuzunu icerir.
echo.
echo DOSYALAR:
echo ---------
echo KULLANIM_KLAVUZU_TR.pdf  - Turkce kullanim kilavuzu ^(PDF^)
echo KULLANIM_KLAVUZU_TR.md   - Kaynak markdown dosyasi
echo screenshots/             - Kilavuzda kullanilan gorseller
echo.
echo OKUMA:
echo ------
echo KULLANIM_KLAVUZU_TR.pdf dosyasini herhangi bir PDF okuyucu ile acabilirsiniz.
echo.
echo TELIF HAKKI:
echo -----------
echo Copyright (c) 2025 Time Graph X. Tum haklari saklidir.
echo.
echo VERSIYON: v1.0.0
echo TARIH: %date%
) > dist\README.txt

echo OK - Dagitim paketi hazir!

REM Temp dosyalarını temizle
echo.
echo Gecici dosyalar temizleniyor...
rmdir /S /Q temp >nul 2>nul

REM Dosya bilgileri
echo.
echo ==========================================
echo BASARILI! Manual hazir.
echo ==========================================
echo.
echo Olusturulan dosyalar:
echo.
for %%A in (dist\KULLANIM_KLAVUZU_TR.pdf) do (
    echo   PDF Dosyasi: %%~nxA
    echo   Boyut: %%~zA bytes
    echo   Konum: %CD%\dist\
)
echo.
echo   + Kaynak markdown
echo   + Screenshot klasoru
echo   + README.txt
echo.
echo Tum dosyalar 'dist' klasorunde.
echo.

REM ZIP oluştur (opsiyonel)
choice /C YN /M "Dagitim paketi ZIP olusturulsun mu"
if %errorlevel% equ 1 (
    echo ZIP olusturuluyor...
    powershell -Command "Compress-Archive -Path dist\* -DestinationPath TimeGraphX_Manual_v1.0.zip -Force"
    echo ZIP olusturuldu: TimeGraphX_Manual_v1.0.zip
)

REM PDF'i aç
echo.
choice /C YN /M "PDF dosyasini simdi acmak ister misiniz"
if %errorlevel% equ 1 (
    start dist\KULLANIM_KLAVUZU_TR.pdf
)

pause

