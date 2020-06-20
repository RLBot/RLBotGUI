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


# If any version of Python 3.8 is not installed, install Python 3.8

parsedVersion=$(echo "${version//./}")
if [[ "$parsedVersion" -gt "380" ]]
then
    echo "Invalid Python install. Installing Python 3.8..."
    sudo apt-get install python3.8
else
    echo "Detected valid Python install"
fi

# Check if the virtual environment exists

if [ ! -e "$HOME/.RLBotGUI/env/bin/activate" ]
then

    # Check if the user has python3.8-venv installed. If they don't, then install it
    
    python3.8 -c "import venv"

    if [ $? -gt 0 ]
    then
        echo "Installing the Python 3.8 Virtual Environment"
        sudo apt-get install python3.8-venv
    fi

    # Create the virutal environment
    # There's currently a bug in Ubuntu, so we must create the venv without pip and then manually install it

    echo "Creating the Python 3.8 Virtual Environment"

    python3.8 -m venv --without-pip env

    # Enter the virtual environment
    source ./env/bin/activate

    # Check if curl is installed and install it if needed
    curl -V

    if [ $? -gt 0 ]
    then
        echo "Installing cURL"
        sudo apt-get install curl
    fi

    # Install pip, wheel and setuptools
    sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

    python get-pip.py
    if [ $? -gt 0 ]
    then
        echo "Installing distutils"
        sudo apt-get install python3-distutils
        python get-pip.py
    fi

    # Pip is now installed, so we can remove get-pip.py as it's no longer needed
    sudo rm get-pip.py

    # Install packages
    pip install eel rlbot_gui rlbot
    if [ $? -gt 0 ]
    then
        echo "Install Python-dev"
        sudo apt-get install python3.8-dev
        pip install rlbot
    fi

else
    # Enter the virtual environment and upgrade all packages
    echo "Activating virtual environment"
    source ./env/bin/activate
    echo "Updating packages"
    pip install --upgrade pip wheel setuptools eel rlbot_gui rlbot
fi

# Launch the GUI

python -c "from rlbot_gui import gui; gui.start()"
