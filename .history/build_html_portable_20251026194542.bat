@echo off
REM ============================================
REM HTML Builder - Portable Pandoc Destegi
REM ============================================

echo.
echo ==========================================
echo Time Graph X - HTML Builder
echo ==========================================
echo.

REM Pandoc PATH'ini belirle
set PANDOC_EXE=pandoc

REM 1. Sistem PATH'inde kontrol et
where pandoc >nul 2>nul
if %errorlevel% equ 0 (
    echo [1/4] Pandoc bulundu (sistem)
    set PANDOC_EXE=pandoc
    goto :build_html
)

REM 2. Portable versiyonu kontrol et
if exist "tools\pandoc\pandoc.exe" (
    echo [1/4] Pandoc bulundu (portable)
    set PANDOC_EXE=tools\pandoc\pandoc.exe
    goto :build_html
)

REM 3. Ana klasorde kontrol et
if exist "pandoc.exe" (
    echo [1/4] Pandoc bulundu (ana klasor)
    set PANDOC_EXE=pandoc.exe
    goto :build_html
)

REM Pandoc bulunamadi
echo [HATA] Pandoc bulunamadi!
echo.
echo Lutfen once Pandoc kurun:
echo   setup_pandoc.bat
echo.
pause
exit /b 1

:build_html
echo [2/4] CSS dosyasi kontrol ediliyor...
if not exist "docs\manual_style.css" (
    echo [UYARI] CSS dosyasi yok, varsayilan stil kullanilacak
)

echo [3/4] HTML olusturuluyor...
echo.

REM HTML olustur
"%PANDOC_EXE%" KULLANIM_KLAVUZU_TR.md -o KULLANIM_KLAVUZU_TR.html ^
  --standalone ^
  --toc ^
  --toc-depth=2 ^
  --css=docs/manual_style.css ^
  --metadata title="Time Graph X - Kullanım Kılavuzu" ^
  --metadata lang=tr-TR ^
  --highlight-style=tango

if %errorlevel% neq 0 (
    echo [HATA] HTML olusturulamadi!
    pause
    exit /b 1
)

echo [4/4] Tamamlandi!
echo.
echo ==========================================
echo BASARILI!
echo ==========================================
echo.
echo Dosya: KULLANIM_KLAVUZU_TR.html
echo.

REM Dosya boyutu
for %%A in (KULLANIM_KLAVUZU_TR.html) do (
    echo Boyut: %%~zA bytes
)
echo.

REM HTML'i ac
choice /C YN /M "HTML dosyasini tarayicida acmak ister misiniz"
if %errorlevel% equ 1 (
    start KULLANIM_KLAVUZU_TR.html
)

pause

