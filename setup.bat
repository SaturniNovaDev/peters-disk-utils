@echo off
setlocal enabledelayedexpansion

echo --- Peter's Disk Utils - Windows Setup ---

:: 1. Choose Setup Mode
set /p choice="Use recommended defaults? (y/n): "

if /i "%choice%"=="y" (
    echo Creating config.ini with Windows defaults...
    copy config.template config.ini
    goto VENV
)

echo --- Custom Configuration ---

set /p VERBOSE="Verbose Mode (True/False) [False]: "
if "!VERBOSE!"=="" set VERBOSE=False

set /p ELIMIT="Error Limit [20]: "
if "!ELIMIT!"=="" set ELIMIT=20

set /p SUMMARY="Show Summary at end of scan? (True/False) [True]: "
if "!SUMMARY!"=="" set SUMMARY=True

set /p TARGET="Default Windows Scan Target [C:/Users]: "
if "!TARGET!"=="" set TARGET=C:/Users

set /p JSON_OUT="Output JSON Name [disk-index.json]: "
if "!JSON_OUT!"=="" set JSON_OUT=disk-index.json

set /p CHART_OUT="Output Chart Name [analysis.pdf]: "
if "!CHART_OUT!"=="" set CHART_OUT=analysis.pdf

set /p LOG_FILE="Output Error Log [nls-errors.log]: "
if "!LOG_FILE!"=="" set LOG_FILE=nls-errors.log

set /p WIN_DIRS="Ignore which directories? [C:/System Volume Information, C:/$Recycle.Bin]: "
if "!WIN_DIRS!"=="" set WIN_DIRS=C:/System Volume Information, C:/$Recycle.Bin

:: Build the config file
echo [GENERAL] > config.ini
echo Verbose = !VERBOSE! >> config.ini
echo ErrorLimit = !ELIMIT! >> config.ini
echo ShowSummary = !SUMMARY! >> config.ini
echo. >> config.ini
echo [PATHS] >> config.ini
echo JsonOutput = !JSON_OUT! >> config.ini
echo ChartOutput = !CHART_OUT! >> config.ini
echo LogFile = !LOG_FILE! >> config.ini
echo. >> config.ini
echo [DEFAULT_TARGETS] >> config.ini
echo Windows = !TARGET! >> config.ini
echo Linux = /home >> config.ini
echo. >> config.ini
echo [EXCLUDE] >> config.ini
echo LinuxDirs = /proc, /sys, /dev, /run, /snap >> config.ini
echo WindowsDirs = !WIN_DIRS! >> config.ini

:VENV
echo.
echo Setting up Virtual Environment...
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 2. Create Global Commands
echo.
set /p global_choice="Register 'disk-nls' and 'disk-nav' as global commands? (y/n): "
if /i "%global_choice%"=="y" (
    set "INSTALL_DIR=%CD%"
    set "VENV_PY=%CD%\.venv\Scripts\python.exe"

    :: Create disk-nls.bat shim
    echo @echo off > disk-nls.bat
    echo "!VENV_PY!" "!INSTALL_DIR!\disk-nls.py" %%* >> disk-nls.bat

    :: Create disk-nav.bat shim
    echo @echo off > disk-nav.bat
    echo "!VENV_PY!" "!INSTALL_DIR!\disk-nav.py" %%* >> disk-nav.bat

    echo.
    echo To use these commands from any folder, you must add this directory to your PATH:
    echo !INSTALL_DIR!
    echo.
    echo Would you like me to try adding it to your User PATH automatically?
    set /p path_choice="(y/n): "
    if /i "!path_choice!"=="y" (
        :: Add to path using setx (takes effect in NEW terminal windows)
        for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path') do set "oldpath=%%B"
        echo !oldpath! | findstr /i "!INSTALL_DIR!" >nul
        if errorlevel 1 (
            setx PATH "!oldpath!;!INSTALL_DIR!"
            echo Success! Please restart your terminal for global commands to work.
        ) else (
            echo Directory already in PATH.
        )
    )
)

echo.
echo Setup Complete!
pause