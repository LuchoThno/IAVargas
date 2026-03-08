@echo off
echo ========================================
echo IA Vargas - Reset y Ejecucion
echo ========================================
echo.

echo [1] Cerrando procesos que usan la base de datos...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2] Eliminando base de datos antigua...
if exist "data\memory.db" (
    del /f "data\memory.db"
    echo    - memory.db eliminada
) else (
    echo    - No habia base de datos para eliminar
)

echo.
echo [3] Ejecutando app.py...
echo.
python app.py
pause
