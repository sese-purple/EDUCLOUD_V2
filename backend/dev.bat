@echo off
REM Activate venv and run Django dev server
call "%~dp0venv\Scripts\activate.bat"
python "%~dp0manage.py" runserver
