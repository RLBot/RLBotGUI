#!/bin/bash

set +v

echo "Installing/upgrading RLBotGUI if necessary, then launching!"
echo ""

if [ ! -d "$HOME/.RLBotGUI" ]
then
    mkdir "$HOME/.RLBotGUI"
fi

pushd "$HOME/.RLBotGUI"

# If any version of Python 3.11 is not installed, then install it

python3.11 -V
if [ $? -gt 0 ]
then
    echo
    echo "Invalid Python install. Installing Python 3.11, and possibly not present dependencies..."
    echo
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.11

    # Instead of waiting to see if these aren't installed, just install them. If they're already installed, then nothing will happen.
    echo
    echo "Installing build-essential, python3.11-dev, python3.11-venv, python3.11-distutils..."
    echo
    sudo apt install build-essential python3.11-dev python3.11-venv, python3.11-distutils
fi

# Check if the virtual environment exists

if [ ! -e "$HOME/.RLBotGUI/env/bin/activate" ]
then
    echo
    echo "Creating the Python 3.11 Virtual Environment"
    python3.11 -m venv env
fi

# Enter the virtual environment
source ./env/bin/activate

# Check for an internet connection
ping -c 1 pypi.org >/dev/null 2>&1
if [ $? -eq 0 ]
then
    echo
    echo "Checking for updates..."
    echo
    python -m pip install -U pip
    pip install -U setuptools wheel
    pip install -U eel rlbot_gui rlbot
else
    echo
    echo "No internet connection, skipping update check"
    echo "NOTE - INTERNET IS REQURIED FOR FIRST TIME LAUNCHES"
fi

# Launch the GUI

echo
echo "Launching RLBotGUI"
echo
python -c "from rlbot_gui import gui; gui.start()"
