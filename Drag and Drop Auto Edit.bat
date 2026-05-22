@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Drag and Drop Auto Edit

set "SCRIPT_DIR=%~dp0"
set "AUTO_EDITOR=%SCRIPT_DIR%.venv\Scripts\auto-editor.exe"
set "PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "AUDIO_HELPER=%SCRIPT_DIR%audio_cleanup.py"

echo.
echo Drag and Drop Auto Edit
echo =======================
echo.

if not exist "%AUTO_EDITOR%" (
    echo Could not find auto-editor here:
    echo "%AUTO_EDITOR%"
    echo.
    echo Keep this .bat file in the AUTO EDIT folder with the .venv folder.
    echo Run setup.bat first if the .venv folder is missing.
    echo.
    goto end
)

if "%~1"=="" (
    echo Drag one or more video files onto this .bat file.
    echo.
    echo You will be asked to choose an edit mode first.
    echo Output files will be saved next to each video.
    echo.
    goto end
)

call :choose_mode

:next_file
if "%~1"=="" goto done
call :process_one "%~1"
shift
goto next_file

:choose_mode
echo Choose an edit mode:
echo.
echo   1. Normal           - default smart silence cut
echo   2. Safe             - gentler cut, keeps more around speech
echo   3. Podcast          - cuts silence, slightly speeds speech, normalizes voice
echo   4. Soft             - keeps silent parts but fast-forwards them
echo   5. Motion-aware     - keeps sections with audio OR visible movement
echo   6. Light denoise    - smart cut, then light audio denoise if FFmpeg is available
echo   7. Voice consistent - smart cut with EBU voice volume normalization
echo   8. Clean voice      - light denoise plus volume consistency if FFmpeg is available
echo.

if not "%AUTO_EDITOR_MODE%"=="" (
    set "MODE_CHOICE=%AUTO_EDITOR_MODE%"
) else (
    choice /C 12345678 /N /M "Mode [1-8]: "
    set "MODE_CHOICE=!ERRORLEVEL!"
)

set "MODE_NAME=Normal"
set "MODE_SUFFIX=_normal-cut"
set "AUTO_ARGS="
set "NEEDS_POST=0"
set "POST_ARGS="

if "%MODE_CHOICE%"=="2" goto mode_safe
if "%MODE_CHOICE%"=="3" goto mode_podcast
if "%MODE_CHOICE%"=="4" goto mode_soft
if "%MODE_CHOICE%"=="5" goto mode_motion
if "%MODE_CHOICE%"=="6" goto mode_denoise
if "%MODE_CHOICE%"=="7" goto mode_voice
if "%MODE_CHOICE%"=="8" goto mode_clean
goto mode_selected

:mode_safe
set "MODE_NAME=Safe"
set "MODE_SUFFIX=_safe-cut"
set "AUTO_ARGS=--margin 0.5s"
goto mode_selected

:mode_podcast
set "MODE_NAME=Podcast"
set "MODE_SUFFIX=_podcast-cut"
set "AUTO_ARGS=--margin 0.25s --video-speed 1.08 --audio-normalize ebu"
goto mode_selected

:mode_soft
set "MODE_NAME=Soft"
set "MODE_SUFFIX=_soft-cut"
set "AUTO_ARGS=--margin 0.2s --silent-speed 8"
goto mode_selected

:mode_motion
set AUTO_ARGS=--edit "(or (audio 0.04) (motion 0.02))"
set "MODE_NAME=Motion-aware"
set "MODE_SUFFIX=_motion-cut"
goto mode_selected

:mode_denoise
set "MODE_NAME=Light denoise"
set "MODE_SUFFIX=_denoise-cut"
set "NEEDS_POST=1"
set "POST_ARGS=--denoise"
goto mode_selected

:mode_voice
set "MODE_NAME=Voice consistent"
set "MODE_SUFFIX=_voice-cut"
set "AUTO_ARGS=--audio-normalize ebu"
goto mode_selected

:mode_clean
set "MODE_NAME=Clean voice"
set "MODE_SUFFIX=_clean-cut"
set "NEEDS_POST=1"
set "POST_ARGS=--denoise --normalize"
goto mode_selected

:mode_selected
echo.
echo Selected mode: !MODE_NAME!
echo.
exit /b 0

:process_one
set "INPUT=%~1"

if not exist "!INPUT!" (
    echo Skipping missing file:
    echo "!INPUT!"
    echo.
    exit /b 0
)

set "BASE=%~dp1%~n1!MODE_SUFFIX!"
set "EXT=%~x1"
set "OUTPUT=!BASE!!EXT!"
set /a COPY_NUM=1

:choose_output
if not exist "!OUTPUT!" goto run_editor
set /a COPY_NUM+=1
set "OUTPUT=!BASE!_!COPY_NUM!!EXT!"
goto choose_output

:run_editor
set "WORK_OUTPUT=!OUTPUT!"

if "!NEEDS_POST!"=="1" (
    set "WORK_OUTPUT=%TEMP%\auto-editor-!RANDOM!-!RANDOM!!EXT!"
)

echo Input:
echo "!INPUT!"
echo.
echo Output:
echo "!OUTPUT!"
echo.

"%AUTO_EDITOR%" "!INPUT!" !AUTO_ARGS! --output "!WORK_OUTPUT!"

if errorlevel 1 (
    echo.
    echo Failed:
    echo "!INPUT!"
    if exist "!WORK_OUTPUT!" del /f /q "!WORK_OUTPUT!" >nul 2>nul
    echo.
    exit /b 0
)

if "!NEEDS_POST!"=="1" (
    echo.
    echo Running audio cleanup...
    "%PYTHON%" "%AUDIO_HELPER%" "!WORK_OUTPUT!" "!OUTPUT!" !POST_ARGS!

    if errorlevel 1 (
        echo.
        echo Audio cleanup was skipped or failed.
        echo Keeping the smart-cut file without extra cleanup.
        move /Y "!WORK_OUTPUT!" "!OUTPUT!" >nul
    ) else (
        del /f /q "!WORK_OUTPUT!" >nul 2>nul
    )
)

echo.
echo Finished:
echo "!OUTPUT!"
echo.
exit /b 0

:done
echo All done.
echo.

:end
if /i not "%AUTO_EDITOR_NO_PAUSE%"=="1" pause
endlocal
