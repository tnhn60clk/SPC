#!/bin/bash

# Update package list and install python3-venv if not installed
sudo apt-get update
sudo apt-get install -y python3-venv

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required Python packages
pip install requests fake_useragent colorama paramiko pysftp

echo "Setup complete. To activate the virtual environment, run 'source venv/bin/activate'."
