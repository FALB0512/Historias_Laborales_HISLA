@echo off
REM Genera dist\HISLA.exe. Ejecutar en la carpeta del proyecto con el venv activo.
pip install pyinstaller
pyinstaller --noconfirm --onefile --console --name HISLA ^
  --add-data "app\templates;app\templates" ^
  --add-data "app\static;app\static" ^
  lanzador.py
echo.
echo Listo: dist\HISLA.exe
pause
