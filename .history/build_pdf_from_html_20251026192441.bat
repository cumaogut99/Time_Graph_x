@echo off
REM ============================================
REM Time Graph X - PDF from HTML Builder
REM HTML'den PDF olustur (daha hizli ve guvenilir)
REM ============================================

echo.
echo ==========================================
echo Time Graph X - HTML to PDF Builder
echo ==========================================
echo.

REM HTML varligini kontrol et
echo [1/4] HTML dosyasi kontrolu...
if not exist "KULLANIM_KLAVUZU_TR.html" (
    echo HTML dosyasi bulunamadi!
    echo Once HTML olusturun: build_html.bat
    pause
    exit /b 1
)
echo OK - HTML mevcut

REM Pandoc kontrolu
echo [2/4] Pandoc kontrolu...
where pandoc >nul 2>nul
if %errorlevel% neq 0 (
    echo HATA: Pandoc bulunamadi!
    pause
    exit /b 1
)
echo OK - Pandoc bulundu

REM WeasyPrint kontrolu (HTML to PDF icin en iyi)
echo [3/4] WeasyPrint kontrolu...
where weasyprint >nul 2>nul
if %errorlevel% equ 0 (
    echo OK - WeasyPrint bulundu (en iyi kalite)
    set PDF_ENGINE=weasyprint
    goto :build_pdf
)

REM wkhtmltopdf kontrolu
where wkhtmltopdf >nul 2>nul
if %errorlevel% equ 0 (
    echo OK - wkhtmltopdf bulundu
    set PDF_ENGINE=wkhtmltopdf
    goto :build_pdf
)

REM Pandoc + XeLaTeX fallback
where xelatex >nul 2>nul
if %errorlevel% equ 0 (
    echo OK - XeLaTeX bulundu (Pandoc kullanilacak)
    set PDF_ENGINE=pandoc
    goto :build_pdf
)

echo.
echo UYARI: HTML to PDF motoru bulunamadi!
echo.
echo Onerileler (en iyiden en kotüye):
echo 1. WeasyPrint (pip install weasyprint)
echo 2. wkhtmltopdf (https://wkhtmltopdf.org/)
echo 3. Pandoc + MiKTeX (build_manual.bat)
echo.
pause
exit /b 1

:build_pdf
echo [4/4] PDF olusturuluyor (%PDF_ENGINE%)...

if "%PDF_ENGINE%"=="weasyprint" (
    REM WeasyPrint - En iyi HTML to PDF
    weasyprint KULLANIM_KLAVUZU_TR.html KULLANIM_KLAVUZU_TR.pdf
    
    if %errorlevel% neq 0 (
        echo HATA: PDF olusturulamadi!
        pause
        exit /b 1
    )
    
    echo.
    echo ==========================================
    echo BASARILI! (WeasyPrint - En Iyi Kalite)
    echo ==========================================
    
) else if "%PDF_ENGINE%"=="wkhtmltopdf" (
    REM wkhtmltopdf
    wkhtmltopdf ^
      --encoding UTF-8 ^
      --page-size A4 ^
      --margin-top 20mm ^
      --margin-bottom 20mm ^
      --margin-left 20mm ^
      --margin-right 20mm ^
      --enable-local-file-access ^
      KULLANIM_KLAVUZU_TR.html KULLANIM_KLAVUZU_TR.pdf
    
    if %errorlevel% neq 0 (
        echo HATA: PDF olusturulamadi!
        pause
        exit /b 1
    )
    
    echo.
    echo ==========================================
    echo BASARILI! (wkhtmltopdf)
    echo ==========================================
    
) else (
    REM Pandoc fallback (Markdown'dan direkt)
    echo HTML to PDF motoru yok, Markdown'dan PDF olusturuluyor...
    call build_manual.bat
    exit /b
)

echo.
for %%A in (KULLANIM_KLAVUZU_TR.pdf) do (
    echo Dosya: %%~nxA
    echo Boyut: %%~zA bytes
)
echo.

REM PDF'i ac
choice /C YN /M "PDF dosyasini acmak ister misiniz"
if %errorlevel% equ 1 (
    start KULLANIM_KLAVUZU_TR.pdf
)

pause

