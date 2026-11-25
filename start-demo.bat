@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Legal CRM Demo

pushd "%~dp0" || goto :directory_error
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONUTF8=1"
set "PYTHON_MANAGER_AUTOMATIC_INSTALL=0"
set "VENV_PYTHON=.venv-demo\Scripts\python.exe"
set "SUPPORTED_VERSION=(3, 12) <= sys.version_info[:2] <= (3, 14)"

if not exist "%VENV_PYTHON%" (
    set "STEP=Creating the virtual environment"
    echo Creating the virtual environment...
    call :create_environment || goto :failed
)

set "STEP=Checking the virtual environment"
"%VENV_PYTHON%" -I -c "import sys; sys.exit(not (%SUPPORTED_VERSION% and sys.prefix != sys.base_prefix))" >nul 2>&1 || (
    echo The demo virtual environment is not usable.
    echo Delete .venv-demo in the project folder and run this script again.
    goto :failed
)

set "STEP=Installing demo dependencies"
echo Installing demo dependencies...
"%VENV_PYTHON%" -m pip install --require-virtualenv --disable-pip-version-check -r "requirements-demo.txt" || goto :failed

set "STEP=Applying database migrations"
echo Applying database migrations...
"%VENV_PYTHON%" "manage.py" migrate --settings=config.settings_demo --noinput || goto :failed

set "STEP=Loading demo data"
echo Loading demo data...
"%VENV_PYTHON%" "manage.py" seed_demo --settings=config.settings_demo --with-demo-user || goto :failed

set "STEP=Running Legal CRM"
echo(
echo Open http://127.0.0.1:8765/ in your browser after Django starts.
echo Press Ctrl+C to stop the demo.
"%VENV_PYTHON%" "manage.py" runserver 127.0.0.1:8765 --settings=config.settings_demo --noreload || goto :failed
popd
exit /b 0

:create_environment
for %%P in (py.exe) do set "PY_LAUNCHER=%%~$PATH:P"
if defined PY_LAUNCHER (
    for %%V in (3.12 3.13 3.14) do (
        "%PY_LAUNCHER%" -%%V -I -c "import sys; sys.exit(not (%SUPPORTED_VERSION%))" >nul 2>&1 && (
            "%PY_LAUNCHER%" -%%V -I -m venv ".venv-demo"
            exit /b
        )
    )
)

for %%P in (python.exe) do set "PATH_PYTHON=%%~$PATH:P"
if defined PATH_PYTHON if /i not "%PATH_PYTHON%"=="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    "%PATH_PYTHON%" -I -c "import sys; sys.exit(not (%SUPPORTED_VERSION%))" >nul 2>&1 && (
        "%PATH_PYTHON%" -I -m venv ".venv-demo"
        exit /b
    )
)

echo Python 3.12, 3.13 or 3.14 is required.
echo Install Python from https://www.python.org/downloads/windows/ and enable the launcher or Add Python to PATH.
exit /b 1

:failed
echo(
echo Legal CRM demo could not start. Failed step: %STEP%.
popd
pause
exit /b 1

:directory_error
echo The project directory could not be opened.
pause
exit /b 1
