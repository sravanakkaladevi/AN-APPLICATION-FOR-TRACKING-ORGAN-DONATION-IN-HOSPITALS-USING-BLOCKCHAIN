@echo off

title Organ Donation Blockchain System

echo ======================================
echo STARTING BLOCKCHAIN PROJECT
echo ======================================

call venv\Scripts\activate

echo.
echo Please ensure Ganache is already running...
timeout /t 5

echo.
echo Deploying Smart Contract...

python blockchain\scripts\deploy_contract.py

echo.
echo Starting Django Server...

start http://127.0.0.1:8000

python manage.py runserver

pause