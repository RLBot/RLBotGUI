#!/bin/bash

set +v

echo "Installing RLBotGUI if necessary, then launching!"
echo ""

if [ ! -d "$HOME/.RLBotGUI" ]
then
    sudo apt-get update
    mkdir "$HOME/.RLBotGUI"
fi

pushd "$HOME/.RLBotGUI"

# If any version of Python 3.7 is not installed, then install it

python3.7 -V
if [ $? -gt 0 ]
then
    echo ""
    echo "Invalid Python install. Installing Python 3.7, and possibly not present dependencies..."
    echo ""
    sudo apt-get install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install python3.7
fi

# Check if the virtual environment exists

if [ ! -e "$HOME/.RLBotGUI/env/bin/activate" ]
then
    # Instead of waiting to see if these aren't installed, just install them. If they're already installed, then nothing will happen.
    echo ""
    echo "Installing build-essential, python3.7-venv, python3.7-dev, python3-distutils, and curl if they're needed"
    echo ""
    sudo apt-get install build-essential
    sudo apt-get install python3.7-venv
    sudo apt-get install python3.7-dev
    sudo apt-get install python3-distutils
    sudo apt-get install curl
    sudo apt autoremove
	
    # Create the virutal environment
    # There's currently a bug in Ubuntu, so we must create the venv without pip and then manually install it

    echo ""
    echo "Creating the Python 3.7 Virtual Environment"
    echo ""

    python3.7 -m venv --without-pip env

    # Enter the virtual environment
    source ./env/bin/activate

    # Install pip, wheel and setuptools
    sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

    python get-pip.py
	
    # Pip is now installed, so we can remove get-pip.py as it's no longer needed
    sudo rm get-pip.py

    # Install packages
	
    pip install eel rlbot_gui rlbot

else
    # Enter the virtual environment and upgrade all packages
    echo ""
    echo "Activating virtual environment"
    echo ""
    source ./env/bin/activate
	
    echo ""
    echo "Updating packages"
    echo ""
    pip install --upgrade pip wheel setuptools eel rlbot_gui rlbot
fi

# Launch the GUI

echo ""
echo "Launching RLBotGUI"
echo ""
python -c "from rlbot_gui import gui; gui.start()"
