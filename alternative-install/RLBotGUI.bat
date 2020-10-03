@echo off

echo Installing RLBotGUI if necessary, then launching!

if not exist "%LocalAppData%\RLBotGUIX" mkdir "%LocalAppData%\RLBotGUIX"
pushd "%LocalAppData%\RLBotGUIX"

if not exist "%LocalAppData%\RLBotGUIX\Python37" (
  echo Looks like we're missing RLBot's Python ^(3.7.9^), installing...

  powershell Expand-Archive "%~dp0\python-3.7.9-custom-amd64.zip" "%LocalAppData%\RLBotGUIX\Python37"

  if exist "%LocalAppData%\RLBotGUIX\venv\pyvenv.cfg" (
    echo Old venv detected, updating Python location so we don't have to reinstall...
    rem This is a custom python script that updates the Python location in the venv
    "%LocalAppData%\RLBotGUIX\Python37\python.exe" "%~dp0\update_venv.py"
  )
)

rem Create a virtual environment which will isolate our package installations from any
rem existing python installation that the user may have.

if not exist .\venv\Scripts\activate.bat (
  echo Creating Python virtual environment just for RLBot...
  "%LocalAppData%\RLBotGUIX\Python37\python.exe" -m venv .\venv
  if %ERRORLEVEL% GTR 0 (
    echo Something went wrong with creating Python virtual environment, aborting.
    pause
    exit
  )
)

rem Activate the virtual environment
call .\venv\Scripts\activate.bat

echo Installing / upgrading RLBot components...

pip install --upgrade pip
pip install wheel
pip install eel
pip install --upgrade rlbot_gui rlbot

echo Launching RLBotGUI...

python -c "from rlbot_gui import gui; gui.start()"

if %ERRORLEVEL% GTR 0 (
  pause
)

