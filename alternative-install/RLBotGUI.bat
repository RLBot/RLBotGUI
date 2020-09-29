@echo off

echo Installing RLBotGUI if necessary, then launching!

rem Find if the key exists, and put the output into a temporary file so it isn't printed to the console
reg query "HKEY_CURRENT_USER\SOFTWARE\rlbotgui\preferences" /v "AppDataPath" > tmp_out_file
if %ERRORLEVEL% GTR 0 (
  rem If the key isn't in the registry, then add the default path to the registry - the key is 'AppDataPath'
  echo Adding the installation path to the registry...
  reg add "HKEY_CURRENT_USER\SOFTWARE\rlbotgui\preferences" /v AppDataPath /t REG_SZ /d "%LocalAppData%"

  rem Set the AppDataPath manually because, in this case, it's a constant
  set AppDataPath="%LocalAppData%"
) else (
  rem Get AppDataPath's value from the registry and put it in a variable called 'AppDataPath'
  FOR /f "tokens=3 skip=2" %%a IN ('reg query "HKEY_CURRENT_USER\SOFTWARE\rlbotgui\preferences" /v "AppDataPath"') DO set "AppDataPath=%%a"
)

rem Delete the temporary file
del tmp_out_file

if not exist "%AppDataPath%\RLBotGUIX" mkdir "%AppDataPath%\RLBotGUIX"
pushd "%AppDataPath%\RLBotGUIX"

if not exist "%AppDataPath%\RLBotGUIX\Python37" (
  echo Looks like we're missing RLBot's Python ^(3.7.9^), installing...

  powershell Expand-Archive "%~dp0\python-3.7.9-custom-amd64.zip" "%AppDataPath%\RLBotGUIX\Python37"

  if exist "%AppDataPath%\RLBotGUIX\venv\pyvenv.cfg" (
    echo Old venv detected, updating Python location so we don't have to reinstall...
    rem This is a custom python script that updates the Python location in the venv
    "%AppDataPath%\RLBotGUIX\Python37\python.exe" "%~dp0\update_venv.py"
  )
)

rem Create a virtual environment which will isolate our package installations from any
rem existing python installation that the user may have.

if not exist .\venv\Scripts\activate.bat (
  echo Creating Python virtual environment just for RLBot...
  "%AppDataPath%\RLBotGUIX\Python37\python.exe" -m venv .\venv
  if %ERRORLEVEL% GTR 0 (
    echo Something went wrong with creating Python virtual environment, aborting.
    pause
    exit
  )
)

rem Activate the virtual environment
call .\venv\Scripts\activate.bat

echo Installing / upgrading RLBot components...

python -m pip install -U pip
pip install -U wheel
pip install -U eel
pip install -U rlbot_gui rlbot

echo Launching RLBotGUI...

python -c "from rlbot_gui import gui; gui.start()"

if %ERRORLEVEL% GTR 0 (
  pause
)

