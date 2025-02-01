#!/bin/bash

apt update
apt install git -y
apt install task-spooler -y
apt install vim
git config --global core.editor "vim"

pip install -r requirements.txt

echo "Setup completed."

