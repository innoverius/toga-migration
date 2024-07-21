#!/bin/bash
# ----------------------------
# Title: Set up Python script
# Author(s): Joren Coulier
# ----------------------------

sudo apt-get update

# Install git
sudo apt install -y git

# Install python and pip
sudo apt install -y python3 python3-pip

# Install packages required for pyodbc
sudo apt-get install -y g++ unixodbc-dev

# Clone repository
git clone https://github.com/innoverius/toga-migration.git

cd toga-migration/ || exit

sudo pip install -r requirements.txt --break-system-packages