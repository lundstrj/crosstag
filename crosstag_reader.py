# -*- coding: utf-8 -*-
import serial
import time
from datetime import datetime
from datetime import date, timedelta
import sys
import select
import os
import requests
import json
from pyfiglet import Figlet
import glob
from random import randint
from optparse import OptionParser
import subprocess

"""
sudo pip install requests
"""

def heardEnter():
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            return True
    return False

class CrosstagReader(object):
    def main(self, server, reader):
        try:
            """ 
                ls /dev/serial/by-id/ to get all connected devices. Use that to determine this 
                /dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AD026CI5-if00-port0 
            """
            usb_devices = glob.glob("/dev/serial/by-id/*")
            ser = serial.Serial(usb_devices[0], 9600, timeout=0)
            print "Crosstag reader is up and running."
            sys.stdout.flush()
        except:
            now = datetime.now()
            print '%s reader ERROR unable to setup the RFID reade, is it plugged in?' % (now)
        answer = raw_input("Running in simulation mode. Without the actual reader? yes/no ")
        while True:
            if reader == 'no':
                if heardEnter():
                    try:
                        now = datetime.now()
                        tag_nbr = 888888444444
                        print '%s reader tagging [%s]' % (now, tag_nbr)
                        res = requests.get("http://localhost:80/crosstag/v1.0/tagevent/%s" % tag_nbr, timeout=3)
                        now = datetime.now()
                        print "%s reader tagging result: [%s]" % (now, res.text)
                    except:
                        e = sys.exc_info()[0]
                        print "unable to send tagevent.", e
            else:
                if ser.inWaiting() > 0:
                    data = ser.readline()
                    if len(data) < 12:
                        continue
                    now = datetime.datetime.now()
                    ser.flushOutput()
                    data = data.strip()
                    tag_nbr = data[1:]
                    if len(tag_nbr) != 12:
                        print '%s reader ERROR [%s] is too long. len(tag_nbr): %d' % (now, tag_nbr, len(tag_nbr))
                        # TODO, PiFace code to ask the person to tag again.
                        # audio signal and visual signal.
                        continue
                    try:
                        print '%s reader tagging [%s]' % (now, tag_nbr)
                        res = requests.get("http://localhost:80/crosstag/v1.0/tagevent/%s" % tag_nbr, timeout=3)
                        now = datetime.now()
                        print "%s reader tagging result: [%s]" % (now, res.text)
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        print '%s reader failed (timeout?) to tag %s error: %s' % (now, tag_nbr, e)
                else:
                    time.sleep(1)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] arg \nTry this: python crosstag_reader.py", version="%prog 1.0")
    parser.add_option("--reader",
                  action="store", type="choice", dest="reader", default="no", choices=['yes','no'], help="do you have a reader connected?")
    parser.add_option("-s", "--server",
                  action="store", type="string", dest="server", default="", help="What is the URL to the crosstag server?")
    (options, args) = parser.parse_args()
    r = CrosstagReader()
    r.main(options.server, options.reader)
