@echo off
echo ========================================
echo Installing Required Libraries
echo ========================================
echo.

REM Try different Python commands
if exist "%LOCALAPPDATA%\Programs\Python\Python*" (
    echo Found Python in Local AppData
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        set "PYTHON_PATH=%%i\python.exe"
        goto :found
    )
)

where python >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=python"
    goto :install
)

where py >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=py"
    goto :install
)

where python3 >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=python3"
    goto :install
)

echo ERROR: Python not found!
echo Please install Python from https://www.python.org/
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b 1

:found
echo Using Python at: %PYTHON_PATH%
"%PYTHON_PATH%" -m pip install -r requirements.txt
goto :end

:install
echo Using Python command: %PYTHON_CMD%
%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo Installation successful!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Installation failed!
    echo ========================================
    echo Please check the error messages above.
)

:end
echo.
pause

