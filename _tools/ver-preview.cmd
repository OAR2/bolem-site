@echo off
REM Abre el preview de BOLEM navegable (rutas sin .html incluidas)
cd /d "%~dp0.."
python "_tools\servidor_preview.py"
pause
