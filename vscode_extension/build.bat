@echo off
REM Build script for IA Local Vargas VSCode Extension (Windows)

echo Building IA Local Vargas VSCode Extension...

REM Check if npm is available
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm not found. Please install Node.js
    exit /b 1
)

REM Install dependencies
echo.
echo Installing dependencies...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies!
    exit /b 1
)

REM Compile TypeScript
echo.
echo Compiling TypeScript...
call npm run compile

if %ERRORLEVEL% NEQ 0 (
    echo Failed to compile!
    exit /b 1
)

REM Package the extension
echo.
echo Packaging extension...
call npm run package

if %ERRORLEVEL% NEQ 0 (
    echo Failed to package!
    exit /b 1
)

echo.
echo Build completed successfully!
echo The VSIX file should be in the current directory
echo.
echo To install:
echo 1. Open VSCode
echo 2. Go to Extensions (Ctrl+Shift+X)
echo 3. Click the three dots ^ > Install from VSIX
echo 4. Select the .vsix file

