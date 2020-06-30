# RLBotGUI Ubuntu (Linux) Install

## First-time installation

There are a few steps to install this on Linux.

1. Download `RLBotGUI.sh` (Or save [this file](https://raw.githubusercontent.com/RLBot/RLBotGUI/master/linux-install/RLBotGUI.sh))
2. `chmod +x /path/to/RLBotGUI.sh`
3. `path/to/RLBotGUI`
4. You will be asked to provide your password. The RLBotGUI requires sudo in order to run:

   - `sudo apt-get update`
   - `sudo apt-get install software-properties-common` (If needed)
   - `sudo add-apt-repository ppa:deadsnakes/ppa` (If needed)
   - `sudo apt-get install build-essential` (If needed)
   - `sudo apt-get install python3.7` (If needed)
   - `sudo apt-get install python3.7-venv` (If needed)
   - `sudo apt-get install curl` (If needed)
   - `sudo apt-get install python3-distutils` (If needed)
   - `sudo apt-get install python3.7-dev` (If needed)
   - `sudo apt autoremove` (For garbage collection of recently installed packages)
   - `sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
   - `sudo rm get-pip.py`

   We won't do anything else with the sudo permission you give us.

5. Once the shell script does its thing, the RLBotGUI will open! You can now take `RLBotGUI.sh` and put it wherever in your system you want. The RLBotGUI has been installed, and you won't need to do it again. (Or at least for a while.)

## Opening RLBotGUI after installation

1. Where ever you've put `RLBotGUI.sh`, run it using `path/to/RLBotGUI.sh`
2. Unlike the first time you ran the script, you won't be prompted for you password. This is because it isn't needed.
3. The shell script will now update all dependicies if needed (`pip`, `wheel`, `setuptools`, `eel`, `rlbot_gui` and `rlbot`)
4. The RLBotGUI will then launch in Chrome, or your defaut system browser if Chrome isn't installed.
