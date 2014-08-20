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

profile = """-------------------
| ::::::::::::::: | %s
| ::::::,..,::::: | 
| :::::......:::: | %s
| :::::......:::: | 
| :::::......:::: | %s
| :::::......:::: |
| ::::::....::::: | %s
| ::::::....::::: |
| ::::,......,::: | %s
| :,............, | 
------------------- %s
                    
                    %s
"""

plot = """ 4|                       o
  |                       o
 3|o  o                   o                o
  |o  o                   o                o
  |o  o                   o                o
 2|o  o              o o  o                o
  |o  o              o o  o                o
 1|o  o o  o o  o o  o o  o o              o
  |o  o o  o o  o o  o o  o o              o
  |o  o o  o o  o o  o o  o o              o
   ----------------------------------------------------------------------------------"""

wod = u"""
Dagens WOD är:
Fran
20 Ryska svingar
50 Wallballs
10 Farmers walk
100m shuttle run
"""

def get_plot(data=[1,1,1,2,2,3,3,3,3,3,4,4,5,5,6,6,6,6,7,7,7,8,8,8,8,11,12,13]):
    # make file
    data_ = str(data)[1:-1]
    data_ = data_.replace(',','\n')
    file = open("/Users/lundstrj/repos/data.txt", "w")
    file.write(data_)
    file.close()

    #command = "echo %s > data.txt" % data_
    #print command
    #p = subprocess.Popen(command)
    #p.communicate()
    # run hist
    p = subprocess.Popen("hist --file '/Users/lundstrj/repos/data.txt' --pch o --colour blue -n --bins 40 -r", shell=True)
    #> /Users/lundstrj/repos/res.txt
    p.communicate()
    # read file
    #file = open("/Users/lundstrj/repos/res.txt", "r")
    #all_data = file.read()
    # retun user_data
    #print all_data


def ascii_print(text, font='slant'):
    f = Figlet(font=font)
    print f.renderText(text)


def heardEnter():
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            return True
    return False

class CrosstagReader(object):
    def main(self, server, reader, display):
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

        os.system('clear')
        ascii_print("CrossFit Kalmar")
        print "-----------------------------------------------------------------------"
        print u"Välkommen till CrossFit Kalmar. Lägg din tag mot Nintendot för att tagga-på"
        print ""
        print wod
        laps = 0
        answer = raw_input("Running in simulation mode. Without the actual reader? yes/no ")
        while True:
            if laps > 20:
                laps = 0
                os.system('clear')
                ascii_print("CrossFit Kalmar")
                print "-----------------------------------------------------------------------"
                print u"Välkommen till CrossFit Kalmar. Lägg din tag mot Nintendot för att tagga-på"
                print ""
                print wod
            if reader == 'no':
                if heardEnter():
                    laps = 0
                    user_data = None
                    user_tags = None
                    #answer = raw_input("Running in simulation mode. Without the actual reader? yes/no ")
                    
                    #if 'y' in answer or 'Y' in answer or answer=='':
                    #    pass
                    #else:
                    #    reader = 'yes'
                    #    continue
                    try:
                        #res = raw_input("Send card event?")
                        now = datetime.now()
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
                        now = datetime.now()
                        user_data = json.loads(res.text)
                        print "%s reader getting user info from tag result: [%s]" % (now, res.text)
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        print "%s reader ERROR getting user info from tag, timeout? %s " % (now, e)
                    try:
                        # TODO fetch user tag_events and print to screen
                        print '%s reader getting user history for user [%s]' % (now, user_data['id'])
                        res = requests.get("http://localhost:80/crosstag/v1.0/get_tagevents_user/%s" % user_data['id'], timeout=3)
                        now = datetime.now()
                        user_tags = json.loads(res.text)
                        print "%s reader getting user info from tag result: [%s]" % (now, res.text)
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        print "%s reader ERROR getting user info from tag, timeout? %s " % (now, e)
                    os.system('clear')
                    #print header
                    ascii_print("CrossFit Kalmar")
                    print "-----------------------------------------------------------------------"
                    expiry_date = datetime.strptime(user_data['expiry_date'], "%Y-%m-%d %H:%M:%S.%f")
                    one_week_ago=datetime.now()-timedelta(days=7)
                    keep = []
                    all_dates = []
                    compare_to_stamp = datetime.strptime(user_tags[user_tags.keys()[0]]['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
                    for key in reversed(sorted(map(int, user_tags.keys()))):
                        foo = datetime.strptime(user_tags[str(key)]['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
                        #print "comparing: %s and %s" % (compare_to_stamp, foo) 
                        if (compare_to_stamp - foo) < timedelta(hours=1):
                            #print "Less than one hour apart"
                            pass
                            # do nothing really
                            # do not count as unique event
                        else:
                            #print "MORE than one hour apart"
                            if foo > one_week_ago:
                                keep.append(foo)
                            kee = user_tags[str(key)]['timestamp'].split(' ')[0]
                            kee = kee.replace('-','')
                            all_dates.append(int(kee))
                            # count!
                            # update to the new fresh event
                            compare_to_stamp = foo

                    created_date = datetime.strptime(user_data['created_date'], "%Y-%m-%d %H:%M:%S.%f")

                    weeks_since_signup = (datetime.now() - created_date).days/7
                    days_since_signup = (datetime.now() - created_date).days
                    last_visit = str(user_tags[str(max(map(int, user_tags.keys())))]['timestamp']).split('.')[0]
                    days_left = str((expiry_date - datetime.now()).days)
                    visits_this_week = str(len(keep))
                    average_visits_per_week = str(len(all_dates)/weeks_since_signup)
                    print u''+profile % ((u"Namn: "+user_data['name']), (u"Senaste besök: "+last_visit), (u"Dagar kvar av medlemskap: "+days_left), (u"Du har varit här: "+visits_this_week+u" gånger de senaste 7 dagarna"), (u"Du snittar "+average_visits_per_week+u" besök per vecka"), (u"Du har taggat in "+str(len(all_dates))+u" gånger"), (u"Du har varit medlem sedan "+user_data['created_date'].split(' ')[0]+u', det blir '+str(weeks_since_signup)+u' veckor eller '+str(days_since_signup)+u" dagar"))
                    print u"Din historik de senaste månaderna"
                    get_plot(data=all_dates)
                    print '\nCrosstag 0.2'
                time.sleep(1)
                laps += 1
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
                        now = datetime.now()
                        print "%s reader tagging result: [%s]" % (now, res.text)
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        print '%s reader failed (timeout?) to tag %s error: %s' % (now, tag_nbr, e)
                    try:
                        # TODO fetch user information and print to screen
                        print '%s reader getting user info for tag [%s]' % (now, tag_nbr)
                        res = requests.get("http://localhost:80/crosstag/v1.0/get_user_data_tag/%s" % tag_nbr, timeout=3)
                        now = datetime.now()
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
    parser.add_option("-d","--displaymode",
                  action="store", type="choice", dest="display", default="no", choices=['yes','no'], help="do want to run the reader in fancy display mode?")
    parser.add_option("-s", "--server",
                  action="store", type="string", dest="server", default="", help="What is the URL to the crosstag server?")
    (options, args) = parser.parse_args()
    r = CrosstagReader()
    r.main(options.server, options.reader, options.display)
