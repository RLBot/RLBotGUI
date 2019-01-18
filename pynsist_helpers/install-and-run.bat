@echo off

@rem Change the working directory to the location of this file so that relative paths will work
cd /D "%~dp0"


.\Python\python.exe upgrade.py || goto :error
.\Python\python.exe run.py || goto :error
exit


:error
@rem echo Failed with error #%errorlevel%.
pause
@rem This exit is required to close the cmd that's created in the shortcut.
exit
