@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  Instagram Reels Scraper Launcher
echo ==========================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Check if main_gui.py exists
if not exist "main_gui.py" (
    echo ERROR: main_gui.py not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

:: Initialize variables
set "PYTHON_CMD="
set "PYTHON_FOUND=0"

echo [1/3] Looking for Python installations...
echo.

:: Method 1: Try Anaconda Python (highest priority)
set "ANACONDA_PYTHON=%USERPROFILE%\AppData\Local\anaconda3\python.exe"
echo Checking Anaconda Python: !ANACONDA_PYTHON!
if exist "!ANACONDA_PYTHON!" (
    echo [OK] Found Anaconda Python
    set "PYTHON_CMD=!ANACONDA_PYTHON!"
    set "PYTHON_FOUND=1"
    set "PYTHON_TYPE=Anaconda"
    goto :check_requirements
)
echo [FAIL] Anaconda Python not found

:: Method 2: Try standard Python commands
echo.
echo Checking standard Python commands...

:: Try 'python' command
echo Checking 'python' command...
python --version >nul 2>&1
if !errorlevel!==0 (
    echo [OK] Found 'python' command
    set "PYTHON_CMD=python"
    set "PYTHON_FOUND=1"
    set "PYTHON_TYPE=System Python"
    goto :check_requirements
)
echo [FAIL] 'python' command not available

:: Try 'py' launcher
echo Checking 'py' launcher...
py --version >nul 2>&1
if !errorlevel!==0 (
    echo [OK] Found 'py' launcher
    set "PYTHON_CMD=py"
    set "PYTHON_FOUND=1"
    set "PYTHON_TYPE=Python Launcher"
    goto :check_requirements
)
echo [FAIL] 'py' launcher not available

:: Try 'python3' command
echo Checking 'python3' command...
python3 --version >nul 2>&1
if !errorlevel!==0 (
    echo [OK] Found 'python3' command
    set "PYTHON_CMD=python3"
    set "PYTHON_FOUND=1"
    set "PYTHON_TYPE=Python3"
    goto :check_requirements
)
echo [FAIL] 'python3' command not available

:: Method 3: Search common installation paths
echo.
echo Searching common Python installation paths...
for %%p in (
    "C:\Python39\python.exe"
    "C:\Python310\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
) do (
    if exist %%p (
        echo [OK] Found Python at: %%p
        set "PYTHON_CMD=%%p"
        set "PYTHON_FOUND=1"
        set "PYTHON_TYPE=Direct Path"
        goto :check_requirements
    )
)

:: No Python found
echo.
echo ERROR: No Python installation found!
echo.
echo Please install one of the following:
echo   1. Anaconda (Recommended): https://www.anaconda.com/download
echo   2. Python: https://www.python.org/downloads/
echo.
echo Make sure to add Python to your PATH during installation.
pause
exit /b 1

:check_requirements
echo.
echo ==========================================
echo [2/3] Python Configuration
echo ==========================================
echo Found Python: !PYTHON_TYPE!
echo Command: !PYTHON_CMD!

:: Get Python version
echo.
echo Python version:
"!PYTHON_CMD!" --version

echo.
echo ==========================================
echo [3/3] Requirements Check
echo ==========================================

:: Check if requirements.txt exists
if exist "requirements.txt" (
    echo [OK] Found requirements.txt
    echo.
    echo Checking installed packages...
    
    :: Check each requirement
    call :check_package "selenium"
    call :check_package "webdriver-manager" 
    call :check_package "pandas"
    call :check_package "openpyxl"
    call :check_package "python-dateutil"
    
    echo.
    set /p "install_req=Do you want to install/update requirements? (y/n): "
    if /i "!install_req!"=="y" (
        echo.
        echo Installing requirements...
        "!PYTHON_CMD!" -m pip install -r requirements.txt
        if !errorlevel!==0 (
            echo [OK] Requirements installed successfully!
        ) else (
            echo [WARNING] Some packages may have failed to install
            echo Check the error messages above
        )
        echo.
    )
) else (
    echo [WARNING] requirements.txt not found
    echo.
    set /p "install_manual=Do you want to install essential packages manually? (y/n): "
    if /i "!install_manual!"=="y" (
        echo.
        echo Installing essential packages...
        "!PYTHON_CMD!" -m pip install selenium webdriver-manager pandas openpyxl python-dateutil
        if !errorlevel!==0 (
            echo [OK] Essential packages installed successfully!
        ) else (
            echo [WARNING] Some packages may have failed to install
        )
        echo.
    )
)

:: Final confirmation before running
echo.
echo ==========================================
echo Ready to Launch
echo ==========================================
echo Python: !PYTHON_TYPE!
echo Command: !PYTHON_CMD!
echo Script: main_gui.py
echo.
set /p "run_now=Start Instagram Reels Scraper now? (y/n): "
if /i "!run_now!"=="n" (
    echo Cancelled by user.
    pause
    exit /b 0
)

:: Run the application
echo.
echo ==========================================
echo Starting Instagram Reels Scraper...
echo ==========================================
echo.

"!PYTHON_CMD!" main_gui.py

echo.
echo ==========================================
echo Application finished.
echo ==========================================
pause
goto :EOF

:: Function to check if a package is installed
:check_package
set "package=%~1"
"!PYTHON_CMD!" -c "import %package%" >nul 2>&1
if !errorlevel!==0 (
    echo [OK] %package% - installed
) else (
    echo [MISSING] %package% - not installed
)
goto :EOF