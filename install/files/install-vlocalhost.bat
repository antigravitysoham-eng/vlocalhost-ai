@echo off
setlocal EnableExtensions
title Vlocalhost.AI installer
color 0E

set "VERSION=1.0.5"
set "ZIPURL=https://github.com/antigravitysoham-eng/vlocalhost-core/archive/refs/tags/v%VERSION%.zip"
set "ROOT=%LOCALAPPDATA%\Vlocalhost"
set "APP=%ROOT%\vlocalhost-core-%VERSION%"
set "ZIP=%TEMP%\vlocalhost-%VERSION%.zip"
set "LOG=%ROOT%\install-log.txt"

echo.
echo    Vlocalhost.AI
echo    Meeting notes that never leave your machine
echo    ==========================================
echo.
echo    This installs everything into your own user folder.
echo    No administrator rights are needed.
if not exist "%ROOT%" mkdir "%ROOT%" >nul 2>&1
echo Vlocalhost installer %VERSION% - %DATE% %TIME% > "%LOG%"
echo.

REM --------------------------------------------------------------- Python
set "PY="
for %%C in (py python python3) do (
  if not defined PY (
    %%C -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1 && set "PY=%%C"
  )
)
if not defined PY (
  echo    [X] Python 3.9 or newer was not found.
  echo.
  echo        1. Install it from  https://www.python.org/downloads/
  echo        2. On the first screen, TICK "Add python.exe to PATH"
  echo        3. Run this installer again
  echo.
  echo.
  echo        Details:  %LOG%
  echo        Get help: https://antigravitysoham-eng.github.io/vlocalhost-ai/support/
  echo.
  pause
  exit /b 1
)
echo    [1/5] Python found.

REM ------------------------------------------------------------- Download
echo    [2/5] Downloading Vlocalhost %VERSION% ...
if exist "%APP%" rmdir /s /q "%APP%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri '%ZIPURL%' -OutFile '%ZIP%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 (
  echo    [X] Download failed. Check your internet connection and try again.
  echo.
  echo        Details:  %LOG%
  echo        Get help: https://antigravitysoham-eng.github.io/vlocalhost-ai/support/
  echo.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Expand-Archive -Path '%ZIP%' -DestinationPath '%ROOT%' -Force } catch { exit 1 }"
if errorlevel 1 (
  echo    [X] Could not unpack the download.
  echo.
  echo        Details:  %LOG%
  echo        Get help: https://antigravitysoham-eng.github.io/vlocalhost-ai/support/
  echo.
  pause
  exit /b 1
)
del "%ZIP%" >nul 2>&1
if not exist "%APP%\vlocalhost.py" (
  echo    [X] The download did not contain what we expected.
  echo.
  echo        Details:  %LOG%
  echo        Get help: https://antigravitysoham-eng.github.io/vlocalhost-ai/support/
  echo.
  pause
  exit /b 1
)

REM ------------------------------------------------------- Environment
echo    [3/5] Setting up a private Python environment ...
%PY% -m venv "%APP%\.venv" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo    [X] Could not create the Python environment.
  echo.
  echo        Details:  %LOG%
  echo        Get help: https://antigravitysoham-eng.github.io/vlocalhost-ai/support/
  echo.
  pause
  exit /b 1
)
set "VPY=%APP%\.venv\Scripts\python.exe"
"%VPY%" -m pip install --upgrade pip --disable-pip-version-check >> "%LOG%" 2>&1
"%VPY%" -m pip install -r "%APP%\requirements.txt" --disable-pip-version-check >> "%LOG%" 2>&1
if errorlevel 1 (
  echo    [X] Could not install the dependencies.
  echo.
  echo        Details:  %LOG%
  echo        Get help: https://antigravitysoham-eng.github.io/vlocalhost-ai/support/
  echo.
  pause
  exit /b 1
)

REM ------------------------------------------------------------- Ollama
where ollama >nul 2>&1
if errorlevel 1 (
  echo    [4/5] Ollama is not installed - recording and transcription will
  echo          work, but written summaries need it.
  echo          Get it from  https://ollama.com/download
  echo          then run:    ollama pull llama3.2
) else (
  echo    [4/5] Fetching the local summary model ^(this can take a few minutes^) ...
  ollama pull llama3.2
)

REM ----------------------------------------------------------- Shortcut
echo    [5/5] Creating your desktop icon ...
pushd "%APP%"
"%VPY%" vlocalhost.py --install-shortcut
popd

echo.
echo    ==========================================
echo    Done. Look for the Vlocalhost.AI icon on
echo    your desktop and double-click it any time.
echo    ==========================================
echo.
choice /C YN /N /M "   Open Vlocalhost now? [Y/N] "
if errorlevel 2 goto done
start "" "%APP%\.venv\Scripts\pythonw.exe" "%APP%\vlocalhost.py"
:done
echo.
timeout /t 3 >nul
exit /b 0
