@echo off

title Organ Donation Blockchain System

echo ======================================
echo STARTING BLOCKCHAIN PROJECT
echo ======================================

REM Activate virtual environment
call venv\Scripts\activate

echo.
echo Starting Ganache...

REM Open Ganache
start "" "C:\Users\srava\AppData\Local\Programs\Ganache\Ganache.exe"

REM Wait for Ganache startup
timeout /t 10

echo.
echo Deploying Smart Contract...

python blockchain\scripts\deploy_contract.py

echo.
echo Starting Django Server...

start http://127.0.0.1:8000

python manage.py runserver

pause
