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

parsedVersion=$(echo "${version//./}")
if [[ "$parsedVersion" -gt "370" && "$parsedVersion" -lt "380" ]]
then
    echo "Detected valid Python install"
else
    echo "Invalid Python install. Installing Python 3.7..."
    sudo apt-get install python3.7
fi

# Check if the virtual environment exists

if [ ! -e "$HOME/.RLBotGUI/env/bin/activate" ]
then

    # Check if the user has python3.7-venv installed. If they don't, then install it
    
    python3.7 -c "import venv"

    if [ $? -gt 0 ]
    then
        echo "Installing the Python 3.7 Virtual Environment"
        sudo apt-get install python3.7-venv
    fi

    # Create the virutal environment
    # There's currently a bug in Ubuntu, so we must create the venv without pip and then manually install it

    echo "Creating the Python 3.7 Virtual Environment"

    python3.7 -m venv --without-pip env

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
        echo "Installing build-essential and python3.7-dev"
		sudo apt-get install build-essential
        sudo apt-get install python3.7-dev
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
