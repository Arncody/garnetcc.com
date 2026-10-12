@echo off
chcp 65001 >nul
echo Applying database migrations...
python manage.py migrate
if errorlevel 1 (echo Migration failed. Is the virtualenv active? & pause & exit /b 1)
python manage.py runserver 8005
