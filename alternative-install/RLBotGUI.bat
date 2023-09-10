@echo off

echo Installing RLBotGUI if necessary, then launching!

if not exist "%LocalAppData%\RLBotGUIX" mkdir "%LocalAppData%\RLBotGUIX"
pushd "%LocalAppData%\RLBotGUIX"

if not exist "%LocalAppData%\RLBotGUIX\Python37" (
  echo Looks like we're missing RLBot's Python ^(3.7.9^), installing...

  powershell -command "Expand-Archive '%~dp0python-3.7.9-custom-amd64.zip' '%LocalAppData%\RLBotGUIX\Python37'"

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

rem We ping google.com to see if we have an internet connection
rem We then store the output of the command to nul which prevents the command from printing to the console
ping -n 1 google.com > nul
if %errorlevel% == 0 (
  echo Installing / upgrading RLBot components...
  python -m pip install --upgrade pip
  pip install wheel
  pip install gevent^<22
  pip install eel
  pip install --upgrade rlbot_gui rlbot
) else (
  echo It looks like you're offline, skipping package upgrades.
  echo Please note that if this is your first time running RLBotGUI, an internet connection is required to properly install.
)

echo Launching RLBotGUI...

python -c "from rlbot_gui import gui; gui.start()"

if %ERRORLEVEL% GTR 0 (
  pause
)
