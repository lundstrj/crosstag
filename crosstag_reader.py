import serial
import time
import datetime
import sys
import requests
import glob
from random import randint
from optparse import OptionParser

"""
sudo pip install requests
"""

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
            now = datetime.datetime.now()
            print '%s reader ERROR unable to setup the RFID reade, is it plugged in?' % (now)

        while True:
            if reader == 'no':
                answer = raw_input("Running in simulation mode. Without the actual reader? yes/no")
                if 'y' in answer or 'Y' in answer:
                    pass
                else:
                    reader = 'yes'
                    continue
                try:
                    res = raw_input("Send card event?")
                    now = datetime.datetime.now()
                    tag_nbr = 888888444444
                    #tag_nbr = randint(100000000000, 999999999999)
                    print '%s reader tagging [%s]' % (now, tag_nbr)
                    res = requests.get("http://localhost:80/crosstag/v1.0/tagevent/%s" % tag_nbr, timeout=3)
                    now = datetime.datetime.now()
                    print "%s reader tagging result: [%s]" % (now, res.text)
                except:
                    print "unable to send tagevent."
                try:
                    # TODO fetch user information and print to screen
                    print '%s reader getting user info for tag [%s]' % (now, tag_nbr)
                    res = requests.get("http://localhost:80/crosstag/v1.0/get_user_data_tag/%s" % tag_nbr, timeout=3)
                    now = datetime.datetime.now()
                    print "%s reader getting user info from tag result: [%s]" % (now, res.text)
                except: # catch *all* exceptions
                    e = sys.exc_info()[0]
                    print "%s reader ERROR getting user info from tag, timeout? %s " % (now, e)
                try:
                    # TODO fetch user information and print to screen
                    print '%s reader getting user history for tag [%s]' % (now, tag_nbr)
                    res = requests.get("http://localhost:80/crosstag/v1.0/get_tagevents_tag/%s" % tag_nbr, timeout=3)
                    now = datetime.datetime.now()
                    print "%s reader getting user info from tag result: [%s]" % (now, res.text)
                except: # catch *all* exceptions
                    e = sys.exc_info()[0]
                    print "%s reader ERROR getting user info from tag, timeout? %s " % (now, e)
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
                        # audip signal and visual signal.
                        continue
                    try:
                        print '%s reader tagging [%s]' % (now, tag_nbr)
                        res = requests.get("http://localhost:80/crosstag/v1.0/tagevent/%s" % tag_nbr, timeout=3)
                        now = datetime.datetime.now()
                        print "%s reader tagging result: [%s]" % (now, res.text)
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        print '%s reader failed (timeout?) to tag %s error: %s' % (now, tag_nbr, e)
                    try:
                        # TODO fetch user information and print to screen
                        print '%s reader getting user info for tag [%s]' % (now, tag_nbr)
                        res = requests.get("http://localhost:80/crosstag/v1.0/get_user_data_tag/%s" % tag_nbr, timeout=3)
                        now = datetime.datetime.now()
                        print "%s reader getting user info from tag result: [%s]" % (now, res.text)
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        print "%s reader ERROR getting user info from tag, timeout? %s " % (now, e)
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
