#!/bin/bash -e

echo "Hello World";

cd /usr/bin

# First do apt-get update
sudo apt-get update

# Then the upgrade
sudo apt-get -y upgrade

# Then rpi-update
sudo rpi-update

# Python Installation
sudo apt install python3 idle3

# Bluepy library install
sudo apt-get install python3-pip libglib2.0-dev
sudo pip install bluepy

# Install Paho client for MQTT communication
sudo pip install paho-mqtt