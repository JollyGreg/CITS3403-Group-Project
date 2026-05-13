@echo off
setlocal enabledelayedexpansion

echo Installing dependencies...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Error upgrading pip
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing requirements
    exit /b 1
)

echo Initializing database...
python db.py
if errorlevel 1 (
    echo Error initializing database
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo To run the application:
echo   python app.py
echo.
pause
