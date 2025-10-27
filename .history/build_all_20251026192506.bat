@echo off
REM ============================================
REM Time Graph X - Complete Build System
REM HTML + PDF tek seferde olustur
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo Time Graph X - Complete Build System
echo ==========================================
echo.
echo Bu script su dosyalari olusturacak:
echo   1. KULLANIM_KLAVUZU_TR.html
echo   2. KULLANIM_KLAVUZU_TR.pdf
echo   3. dist/ klasorunde dagitim paketi
echo.

pause

REM 1. HTML olustur
echo.
echo ==========================================
echo [1/3] HTML Olusturuluyor...
echo ==========================================
call build_html.bat
if %errorlevel% neq 0 (
    echo HTML olusturulamadi!
    pause
    exit /b 1
)

REM 2. PDF olustur
echo.
echo ==========================================
echo [2/3] PDF Olusturuluyor...
echo ==========================================

REM Once WeasyPrint dene (en iyi)
where weasyprint >nul 2>nul
if %errorlevel% equ 0 (
    echo WeasyPrint bulundu, HTML'den PDF olusturuluyor...
    call build_pdf_from_html.bat
    set PDF_SOURCE=HTML
) else (
    echo WeasyPrint yok, Markdown'dan PDF olusturuluyor...
    call build_manual_advanced.bat
    set PDF_SOURCE=Markdown
)

REM 3. Dagitim paketi olustur
echo.
echo ==========================================
echo [3/3] Dagitim Paketi Olusturuluyor...
echo ==========================================

if not exist "dist\" mkdir dist
if not exist "dist\screenshots\" mkdir dist\screenshots

echo Dosyalar kopyalaniyor...

REM Ana dosyalar
copy /Y KULLANIM_KLAVUZU_TR.html dist\ >nul 2>nul
copy /Y KULLANIM_KLAVUZU_TR.pdf dist\ >nul 2>nul
copy /Y KULLANIM_KLAVUZU_TR.md dist\ >nul 2>nul

REM CSS
if not exist "dist\docs\" mkdir dist\docs
copy /Y docs\manual_style.css dist\docs\ >nul 2>nul

REM Screenshots
if exist "screenshots\" (
    xcopy /E /I /Y screenshots dist\screenshots\ >nul 2>nul
)

REM README olustur
(
echo TIME GRAPH X - KULLANIM KILAVUZU
echo ================================
echo.
echo DOSYALAR:
echo ---------
echo KULLANIM_KLAVUZU_TR.html - Web tarayicida goruntulenebilir HTML
echo KULLANIM_KLAVUZU_TR.pdf  - Yazdirilabilir PDF dosyasi
echo KULLANIM_KLAVUZU_TR.md   - Kaynak Markdown dosyasi
echo docs/manual_style.css    - HTML stil dosyasi
echo screenshots/             - Gorsel dosyalari
echo.
echo KULLANIM:
echo ---------
echo HTML: Herhangi bir web tarayicida acin
echo PDF:  Adobe Reader veya baska bir PDF okuyucu ile acin
echo.
echo PDF KAYNAK: %PDF_SOURCE%
echo OLUSTURMA TARIHI: %date% %time%
echo.
echo TELIF HAKKI:
echo -----------
echo Copyright (c) 2025 Time Graph X. Tum haklari saklidir.
echo.
echo VERSIYON: v1.0.0
) > dist\README.txt

echo OK - Dosyalar kopyalandi

REM Ozet
echo.
echo ==========================================
echo TAMAMLANDI!
echo ==========================================
echo.
echo Olusturulan dosyalar:
echo.

if exist "dist\KULLANIM_KLAVUZU_TR.html" (
    for %%A in (dist\KULLANIM_KLAVUZU_TR.html) do (
        echo   [HTML] %%~nxA - %%~zA bytes
    )
)

if exist "dist\KULLANIM_KLAVUZU_TR.pdf" (
    for %%A in (dist\KULLANIM_KLAVUZU_TR.pdf) do (
        echo   [PDF]  %%~nxA - %%~zA bytes
    )
)

echo   [MD]   KULLANIM_KLAVUZU_TR.md
echo   [CSS]  docs/manual_style.css
echo   [TXT]  README.txt

if exist "dist\screenshots\" (
    set screenshot_count=0
    for %%F in (dist\screenshots\*.png) do set /a screenshot_count+=1
    echo   [IMG]  !screenshot_count! adet gorsel
)

echo.
echo Tum dosyalar 'dist' klasorunde.
echo.

REM ZIP olustur
choice /C YN /M "ZIP arsivi olusturulsun mu"
if %errorlevel% equ 1 (
    echo.
    echo ZIP olusturuluyor...
    
    set ZIP_NAME=TimeGraphX_Manual_v1.0_%date:~-4%%date:~-7,2%%date:~-10,2%.zip
    
    powershell -Command "Compress-Archive -Path dist\* -DestinationPath '!ZIP_NAME!' -Force"
    
    if exist "!ZIP_NAME!" (
        echo.
        echo ZIP olusturuldu: !ZIP_NAME!
        for %%A in (!ZIP_NAME!) do (
            echo Boyut: %%~zA bytes
        )
    )
)

echo.
echo ==========================================
echo Kullanilabilir Dosyalar:
echo ==========================================
echo.
echo 1. HTML Preview: dist\KULLANIM_KLAVUZU_TR.html
echo 2. PDF Manual:   dist\KULLANIM_KLAVUZU_TR.pdf
echo 3. ZIP Package:  TimeGraphX_Manual_v1.0_*.zip
echo.

REM Dosyalari ac
choice /C YN /M "Olusturulan dosyalari acmak ister misiniz"
if %errorlevel% equ 1 (
    if exist "dist\KULLANIM_KLAVUZU_TR.html" start dist\KULLANIM_KLAVUZU_TR.html
    timeout /t 1 >nul
    if exist "dist\KULLANIM_KLAVUZU_TR.pdf" start dist\KULLANIM_KLAVUZU_TR.pdf
)

echo.
pause

