# RLBotGUI

[<img src="https://img.shields.io/pypi/v/rlbot-gui.svg">](https://pypi.org/project/rlbot-gui/)

## About

RLBotGUI is a streamlined user interface that helps you run custom
Rocket League bots for offline entertainment. It relies on the RLBot
project to work its magic: https://github.com/RLBot/RLBot

It works on Windows only and requires Google Chrome to run.

## Installation

If you just want to use this GUI, you can go download the installer from
https://drive.google.com/drive/folders/1LZdTVPQeqO0ZGtelQE3yPyBlvC_pqsGT?usp=sharing

It will put "RLBotGUI" in your Windows start menu.

## Dev Environment Setup

### Prerequisites

- Python 3.7

### Setup

1. In a command prompt, run `pip install -r requirements.txt`
2. Run `python run.py`

### Deployment to PyPI

For normal changes, e.g. things happening inside the rlbot_gui folder,
you should be publishing an update to PyPI. All users will get this change
automatically without needing to reinstall!

To deploy:
1. Create a .pypirc file like the one described here:
https://github.com/RLBot/RLBot/wiki/Deploying-Changes#first-time-setup
1. Look in setup.py and increment the version number.
1. Run `publish-to-pypi-prod.bat`

### Building the Installer

You can build an installer executable for users to download. You will rarely need
to do this, because normal updates should be pushed to users by deploying to PyPI.

You really only need a new installer if you changed something in the pynsist_helpers
folder, run.py, or anything else that gets referenced in installer.cfg. **AVOID THIS**
because you don't want to run around bugging users to reinstall.

1. Follow https://pynsist.readthedocs.io/en/latest/index.html to get NSIS installed.
2. Run `pip install pynsist`
3. Run `pynsist installer.cfg`

Find the resulting executable in build\nsis.
