# RLBotGUI Ubuntu (Linux) Install

## First-time installation

There are a few steps to install this on Linux.

1. Download `RLBotGUI.sh` (Or save [this file](https://raw.githubusercontent.com/RLBot/RLBotGUI/master/linux-install/RLBotGUI.sh))
2. `chmod +x /path/to/RLBotGUI.sh`
3. `path/to/RLBotGUI`
4. You will be asked to provide your password. The RLBotGUI requires sudo in order to run:

   - `sudo apt-get update`
   - `sudo apt-get install python3.8` NOTE: If you're using Ubuntu 20.04, This won't be run as you'll already have Python 3.8 installed.
   - `sudo apt-get install python3.8-venv`
   - `sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
   - `sudo rm get-pip.py`

   We won't do anything else with the sudo permission you give us.

5. Once the shell script does it's thing, the RLBotGUI will open! You can now take `RLBotGUI.sh` and put it where every in your system you want. The RLBotGUI has been installed, and you won't need to do it again. (Or at least for a while.)

## Opening RLBotGUI after installation

1. Where ever you've put `RLBotGUI.sh`, run it using `path/to/RLBotGUI.sh`
2. Unlike the first time you ran the script, you won't be prompted for you password. This is because it isn't needed.
3. The shell script will now update all dependicies if needed (`pip`, `wheel`, `setuptools`, `eel`, `rlbot_gui` and `rlbot`)
4. The RLBotGUI will then launch.
