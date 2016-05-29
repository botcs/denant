#!/bin/bash

#MULTIPLE PACKAGES ARE REQUIRED
sudo apt-get install python-pip
sudo pip install numpy matplotlib pandas

#MAKE SYMLINK FOR EASIER CALL OF DENANT
sudo ln -s $(pwd)/denant.py /usr/bin/denant
