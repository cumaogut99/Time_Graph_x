@echo off
REM ============================================
REM Time Graph X - HTML Builder
REM Markdown'dan HTML olustur
REM ============================================

echo.
echo ==========================================
echo Time Graph X - HTML Builder
echo ==========================================
echo.

REM Pandoc kontrolu
echo [1/3] Pandoc kontrolu...
where pandoc >nul 2>nul
if %errorlevel% neq 0 (
    echo HATA: Pandoc bulunamadi!
    echo Indirin: https://pandoc.org/installing.html
    pause
    exit /b 1
)
echo OK - Pandoc bulundu

REM CSS dosyasi kontrolu
echo [2/3] CSS dosyasi kontrolu...
if not exist "docs\manual_style.css" (
    echo UYARI: CSS dosyasi bulunamadi!
    echo HTML varsayilan stil ile olusturulacak.
)

REM HTML olustur
echo [3/3] HTML olusturuluyor...

pandoc KULLANIM_KLAVUZU_TR.md -o KULLANIM_KLAVUZU_TR.html ^
  --standalone ^
  --toc ^
  --toc-depth=2 ^
  --css=docs/manual_style.css ^
  --metadata title="Time Graph X - Kullanım Kılavuzu" ^
  --metadata lang=tr-TR ^
  --metadata charset=UTF-8 ^
  --highlight-style=tango ^
  --template=docs/manual_template.html

if %errorlevel% neq 0 (
    echo Template bulunamadi, basit HTML olusturuluyor...
    
    pandoc KULLANIM_KLAVUZU_TR.md -o KULLANIM_KLAVUZU_TR.html ^
      --standalone ^
      --toc ^
      --toc-depth=2 ^
      --css=docs/manual_style.css ^
      --metadata title="Time Graph X - Kullanım Kılavuzu" ^
      --metadata lang=tr-TR ^
      --highlight-style=tango
)

if %errorlevel% neq 0 (
    echo HATA: HTML olusturulamadi!
    pause
    exit /b 1
)

echo OK - HTML basariyla olusturuldu!
echo.
echo Dosya: KULLANIM_KLAVUZU_TR.html
echo.

REM HTML'i acmak ister misiniz?
choice /C YN /M "HTML dosyasini tarayicida acmak ister misiniz"
if %errorlevel% equ 1 (
    start KULLANIM_KLAVUZU_TR.html
)

echo.
echo ==========================================
echo BASARILI!
echo ==========================================
echo.
echo Simdi HTML'den PDF olusturabilirsiniz:
echo   build_pdf_from_html.bat
echo.
pause

