@echo off
cd /d d:\Proyectos\IAVargas
call .venv\Scripts\activate.bat
python test_fix.py > test_output2.txt 2>&1
echo Done
pause

