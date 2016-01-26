Crosstag: A sensible gym solution for sensible people
=========================

I really wish I had written more here. Maybe by Christmas?

Features
--------

- Designed to run on a Raspberry Pi (http://www.raspberrypi.org/products/)
- COTS RFID-reader compatible (https://www.sparkfun.com/products/retired/9875, https://www.sparkfun.com/products/13198)
- Stand alone server
- Stand alone reader
- Stand alone viewer
- Not much more

Installation
------------

To install Crosstag, simply clone and run.

# to start the server
sudo python crosstag_server.py

# to start the reader
python crosstag_reader.py

# to start the terminal based viewer
python crosstag_viewer.py


Avoid screen blanking
---------------------
sudo nano /etc/kbd/config

BLANK_TIME=0

POWERDOWN_TIME=0

sudo /etc/init.d/kbd restart

sudo nano /etc/lightdm/lightdm.conf

xserver-command=X -s 0 dpms

Setup for remote access
-----------------------

sudo apt-get update

sudo apt-get install weavedconnectd

sudo weavedinstaller
