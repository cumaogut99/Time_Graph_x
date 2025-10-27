@echo off
REM ============================================
REM HTML Builder - Python (Pandoc gerektirmez!)
REM ============================================

echo.
echo ==========================================
echo Time Graph X - HTML Builder (Python)
echo ==========================================
echo.
echo Pandoc gerektirmez - Aninda calisir!
echo.

REM Python kontrolu
echo [1/3] Python kontrolu...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi!
    echo Python yuklu degil veya PATH'de yok.
    pause
    exit /b 1
)
echo [OK] Python bulundu

REM Dosya kontrolu
echo [2/3] Markdown dosyasi kontrolu...
if not exist "KULLANIM_KLAVUZU_TR.md" (
    echo [HATA] KULLANIM_KLAVUZU_TR.md bulunamadi!
    pause
    exit /b 1
)
echo [OK] Markdown dosyasi mevcut

REM HTML olustur
echo [3/3] HTML olusturuluyor...
echo.

python markdown_to_html.py KULLANIM_KLAVUZU_TR.md KULLANIM_KLAVUZU_TR.html docs/manual_style.css

if %errorlevel% neq 0 (
    echo.
    echo [HATA] HTML olusturulamadi!
    pause
    exit /b 1
)

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

echo.
echo Not: Pandoc gerekmedi! Python ile olusturduk.
echo.
pause

