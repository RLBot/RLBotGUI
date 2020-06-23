@echo off

echo Installing RLBotGUI if necessary, then launching!


if not exist "%LocalAppData%\RLBotGUIX" mkdir "%LocalAppData%\RLBotGUIX"
pushd "%LocalAppData%\RLBotGUIX"

py -3.7 --version

rem If python 3.7 is not installed, then the above py command will cause a non-zero error level.

if %ERRORLEVEL% GTR 0 (

  echo Looks like we don't have python 3.7, will download and install from python.org...

  if not exist python-install.exe (
    powershell -Command "Invoke-WebRequest https://www.python.org/ftp/python/3.7.7/python-3.7.7-amd64.exe -OutFile .\python-installer.exe"
  )

  rem Go ahead and install the specific version of python we want.
  rem We have selected options which will not modify the user's PATH
  rem If the user already has 3.7 installed but the py command was not available or could not find it,
  rem the installation will be modified, which will probably not cause trouble for anyone.

  .\python-installer.exe /passive InstallAllUsers=0 Shortcuts=0 Include_doc=0 Include_dev=0 Include_launcher=1 InstallLauncherAllUsers=0 PrependPath=0
)

rem Create a virtual environment which will isolate our package installations from any
rem existing python installation that the user may have.

if not exist .\venv\Scripts\python.exe (
  rem if we just installed python for the first time then py is probably still not on PATH.
  rem Make sure the environment variables are up-to-date.
  call %~dp0\RefreshEnv.cmd

  echo Creating python virtual environment just for RLBot...
  py -3.7 -m venv .\venv
)

set rlbotpy=.\venv\Scripts\python.exe

echo Installing / upgrading RLBot components...

%rlbotpy% -m pip install --upgrade pip
%rlbotpy% -m pip install wheel
%rlbotpy% -m pip install eel
%rlbotpy% -m pip install --upgrade rlbot_gui rlbot

echo Launching RLBotGUI...

%rlbotpy% -c "from rlbot_gui import gui; gui.start()"

if %ERRORLEVEL% GTR 0 (
  pause
)
