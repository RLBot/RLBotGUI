# RLBotGUI via LISS

This stands for the Rocket League Bot Graphical User Interface via the Linux Installation Shell Script.

## First-time installation with LISS

1. Download `RLBotGUI.sh` (Or save [this file](https://raw.githubusercontent.com/RLBot/RLBotGUI/master/linux-install/RLBotGUI.sh))
2. `chmod +x path/to/RLBotGUI.sh`
3. `path/to/RLBotGUI` (`./RLBotGUI` if it's in the current folder)
4. Do not run the script with sudo - you will be asked to provide your sudo password after it starts, _if needed_. LISS requires sudo in order to run:

   - `sudo apt install software-properties-common` (If needed)
   - `sudo add-apt-repository ppa:deadsnakes/ppa` (If needed; this is the Linux Python archive - https://github.com/deadsnakes)
   - `sudo apt update`
   - `sudo apt install build-essential python3.11-dev python3.11-venv python3.11-distutils` (If needed)

   We won't do anything else with the sudo permission you give us, and is only required for installation.

5. Once LISS does its thing, RLBotGUI will open! You can now take `RLBotGUI.sh` and put it wherever in your system you want.
The RLBotGUI has been installed, and you can just keep running it every time you want to use RLBotGUI and it will update itself if needed.

## Opening RLBotGUI after installation

1. Where ever you've put `RLBotGUI.sh`, run it using `path/to/RLBotGUI.sh`
2. LISS will now update all dependencies, if you have internet access. (`pip`, `setuptools`, `wheel`, `eel`, `rlbot_gui` and `rlbot`)
3. RLBotGUI will then launch in Chrome, or your default system browser if Chrome isn't installed.
