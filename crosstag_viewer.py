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
import crosstag_server
import subprocess

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


class CrosstagViewer(object):
    last_tagin = None
    timeout = 3

    def date_strip(self, date):
        return date.split(" ")[0]

    def str_to_datetime(self, str):
        return datetime.strptime(str, "%Y-%m-%d %H:%M:%S.%f")

    def ascii_print(self, text, font='slant'):
        f = Figlet(font=font)
        print f.renderText(text)

    def print_clear_screen(self):
        #os.system('clear')
        self.ascii_print("Crossfit Kalmar")

    def get_plot(self, data):
        # make file
        data_ = str(data)[1:-1]
        data_ = data_.replace(',','\n')
        file = open("/Users/lundstrj/repos/crosstag/data.txt", "w")
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

    def print_user_screen(self, user, stats):
        #os.system('clear')
        if user == {}:
            pass
        else:
            now = datetime.now()
            user_name = user['name']
            created_str = user['created_date']
            created_date = self.str_to_datetime(created_str)
            created_date_short = self.date_strip(created_str)
            memeber_for_weeks = str((now - created_date).days/7)
            member_for_days = str((now - created_date).days)
            expiry_str = self.date_strip(user['expiry_date'])
            days_left = str((self.str_to_datetime(user['expiry_date']) - now).days)
            last_visit = str(stats['last_visit']).split('.')[0][0:-3]
            visits_last_week = str(stats['unique_visits_last_seven'])
            average_per_week = str(stats['unique_visits'] / int(memeber_for_weeks))
            total_visits = str(stats['unique_visits'])

            print u''+profile % ((u"Namn: "+user_name), 
                (u"Senaste besök: "+last_visit), 
                (u"Dagar kvar av medlemskap: "+str(days_left))+" ("+expiry_str+")", 
                (u"Du har varit här: "+visits_last_week+u" gånger de senaste 7 dagarna"), 
                (u"Du snittar "+average_per_week+u" besök per vecka"), 
                (u"Du har taggat in "+total_visits+u" gånger"), 
                (u"Du har varit medlem sedan "+created_date_short+u', det blir '+memeber_for_weeks+u' veckor eller '+member_for_days+u" dagar"))


            def remove_(str):
                return int(str.replace("-",""))
            print u"Din besökshistorik den senaste tiden"
            dates = stats['unique_visits_raw']
            dates = map(str, dates)
            dates = map(self.date_strip, dates)
            dates = map(remove_, dates)
            self.get_plot(data=dates)

    def poll_server(self):
        res = requests.get("http://localhost:80/crosstag/v1.0/last_tagin", timeout=3)
        res = json.loads(res.text)
        return res

    def get_user_stats(self, user_id):
        now = datetime.now()
        #print '%s reader getting user history for user [%s]' % (now, user_id)
        res = requests.get("http://localhost:80/crosstag/v1.0/get_tagevents_user/%s" % user_id, timeout=3)
        now = datetime.now()
        #print "%s reader getting user info from tag result: [%s]" % (now, res.text)
        return json.loads(res.text)

    def parse_user_stats(self, data):
        res = {}

        keys = sorted(map(int,data.keys()), reverse=True)
        res['total_tagins'] = len(keys)

        last = None
        unique_visits = []
        for key in reversed(keys):
            current = self.str_to_datetime(data[str(key)]['timestamp'])
            if last == None:
                last = current
                continue
            if (current - last) > timedelta(minutes=60):
                print "    ", last
                print "    ", current
                print "         ", current - last
                last = current
                unique_visits.append(current)
                # Count as a new visit
            print current
        
        one_week_ago = datetime.now() - timedelta(days=7)
        last_seven = []
        for data in unique_visits:
            if data > one_week_ago:
                last_seven.append(data)

        res['unique_visits'] = len(unique_visits)
        res['last_visit'] = unique_visits[-1]
        res['unique_visits_last_seven'] = len(last_seven)
        res['unique_visits_raw'] = unique_visits
        return res

    def get_user_data(self, tag_nbr):
        now = datetime.now()
        #print '%s reader getting user info for tag [%s]' % (now, tag_nbr)
        res = requests.get("http://localhost:80/crosstag/v1.0/get_user_data_tag/%s" % tag_nbr, timeout=3)
        now = datetime.now()
        #print "%s reader getting user info from tag result: [%s]" % (now, res.text)
        return json.loads(res.text)

    def main(self, options):
        self.last_tagin = self.poll_server()
        self.print_clear_screen()
        counter = 0
        new = False
        screen_cleard = True
        while True:
            new_tagin = self.poll_server()
            if not new_tagin == self.last_tagin:
                new = True
                user_data = self.get_user_data(self.last_tagin[u'tag'])
                # todo: should this be tag independet?
                user_stats_data = self.get_user_stats(user_data['id'])
                user_stats = self.parse_user_stats(user_stats_data)
                self.print_user_screen(user_data, user_stats)
                screen_cleard = False
                counter = 0
            elif new:
                counter += 1
            if counter == self.timeout:
                counter = 0
                new = False
                if not screen_cleard:
                    self.print_clear_screen()
                    screen_cleard = True
            self.last_tagin = new_tagin
            time.sleep(1)
            # if change. Show and keep polling:

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] arg \nTry this: python crosstag_viewer.py", version="%prog 1.0")
    parser.add_option("-s", "--server",
                  action="store", type="string", dest="server", default="", help="What is the URL to the crosstag server?")
    (options, args) = parser.parse_args()
    r = CrosstagViewer()
    r.main(options.server)