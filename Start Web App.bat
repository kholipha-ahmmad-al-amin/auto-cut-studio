@echo off
setlocal EnableExtensions

title Auto Cut Studio Web App

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"

echo.
echo Auto Cut Studio Web App
echo =======================
echo.

if not exist "%PYTHON_EXE%" (
    echo Local environment was not found.
    echo Run setup.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting at http://127.0.0.1:7860
echo Press Ctrl+C to stop.
echo.

"%PYTHON_EXE%" "%SCRIPT_DIR%app.py"

endlocal
