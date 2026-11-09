@echo off
title NexusCore Mission Control v2.0
echo =======================================================
echo   NEXUSCORE // Autonomous DevSecOps Mission Control
echo =======================================================
echo.
echo [1/2] Installing requirements...
python -m pip install -r backend\requirements.txt
echo.
echo [2/2] Launching Mission Control at http://localhost:8000 ...
start http://localhost:8000
python backend\main.py
pause
