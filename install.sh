#!/bin/bash

# install dependies
pip3 install -r requirements.txt

# build package and install it 
python3 setup.py bdist_wheel
python3 -m pip install -e .

# create json config 
mkdir ~/.discord_bot_chatter/
touch ~/.discord_bot_chatter/config.json