@echo off
setlocal

echo Voice2Text - Setup
echo ===================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
if not exist ".venv" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
) else (
    echo [1/5] Virtual environment already exists, skipping...
)

REM Upgrade pip
echo [2/5] Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

REM Install dependencies
echo [3/5] Installing dependencies...
.venv\Scripts\python.exe -m pip install -e .
if errorlevel 1 (
    echo.
    echo ERROR: pip install failed. Please check the error messages above.
    pause
    exit /b 1
)

REM Create data directories
echo [4/5] Creating data directories...
if not exist "data" mkdir data
if not exist "data\recordings" mkdir data\recordings
if not exist "models" mkdir models

REM Copy .env if not exists
if not exist ".env" (
    echo [5/5] Creating .env file...
    copy .env.example .env >nul
) else (
    echo [5/5] .env already exists, skipping...
)

echo.
echo ===================
echo Setup complete!
echo.
echo Starting Voice2Text GUI...
echo.

REM Check PySide6
.venv\Scripts\python.exe -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PySide6 is not installed. Please re-run setup (start.bat).
    pause
    exit /b 1
)

REM Set HuggingFace cache to project directory
set HF_HOME=%CD%\models\.hf_cache
set TRANSFORMERS_CACHE=%CD%\models\.transformers_cache
set PYTHONPATH=%CD%

REM Launch GUI
.venv\Scripts\python.exe -m app.gui

echo.
echo GUI closed. Press any key to exit...
pause >nul
