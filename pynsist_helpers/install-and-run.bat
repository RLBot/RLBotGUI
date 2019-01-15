@echo off

@rem Change the working directory to the location of this file so that relative paths will work
cd /D "%~dp0"


.\Python\python.exe upgrade.py

.\Python\python.exe run.py

pause
