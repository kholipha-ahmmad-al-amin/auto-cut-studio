@echo off
setlocal EnableExtensions

title Auto Cut Studio Setup

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

echo.
echo Auto Cut Studio Setup
echo =====================
echo.

if not exist "%PYTHON_EXE%" (
    echo Creating local Python environment...
    python -m venv "%VENV_DIR%"

    if errorlevel 1 (
        echo.
        echo Python was not found. Install Python 3.11 or newer and enable Add python.exe to PATH.
        goto end
    )
)

echo Installing requirements...
"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements.txt"

if errorlevel 1 (
    echo.
    echo Setup failed. Check the messages above.
) else (
    echo.
    echo Setup complete.
)

:end
pause
endlocal
