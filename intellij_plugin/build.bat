@echo off
REM Build script for IA Local Vargas IntelliJ Plugin (Windows)

echo Building IA Local Vargas IntelliJ Plugin...

REM Check if gradlew exists
if not exist "gradlew.bat" (
    echo Gradle wrapper not found. Using system Gradle...
    gradle buildPlugin
) else (
    echo Using Gradle wrapper...
    gradlew.bat buildPlugin
)

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b 1
)

echo.
echo Build completed successfully!
echo The plugin JAR should be in build/distributions/
echo.
echo To install:
echo 1. Open IntelliJ IDEA
echo 2. Go to Settings > Plugins
echo 3. Click the gear icon > Install Plugin from Disk
echo 4. Select the JAR from build/distributions/

