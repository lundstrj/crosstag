# -*- coding: utf-8 -*-
import os
from pyfiglet import Figlet
from optparse import OptionParser
import requests
import json
import time
#Test commit

class CrosstagViewer(object):
    server = None
    port = None
    online = None
    last_event = None
    counter = 0
    display_user = False
    user_data = None
    user_tagins = None
    display_time = 20
    sleep_time = 2

    def main(self, server, port):
        self.server = server
        self.port = port
        current = self.poll_server()
        try:
            self.last_event = current['index']
        except:
            print("unable to fetch data =(")
            self.last_event = 0
        while True:
            # current could be NONE you need to deal with that. Make it robust!
            # you need to supress the output from the server.
            # you need to supress the output from the reader.
            # use a logger?

            current = self.poll_server()
            if self.online:
                pass
                #self.print_clear_screen("online")
            else:
                self.print_clear_screen("offline")

            if current is None:
                self.display_user = False
                self.print_clear_screen("offline")
            elif current['index'] != self.last_event: # THIS FAILS WHEN THE DB IS EMPTY
                self.print_clear_screen("online")
                self.last_event = current['index']
                self.display_user = True
                self.counter = 0

            if self.display_user and self.counter >= 0:
                # todo johan: imptimize this so we only pull the user data once
                self.user_data = self.get_user_data(current['tag_id'])
            if not self.user_data and self.display_user:
                print("read tag: %s" % current['tag_id'])
                self.display_user = False
            if self.display_user and self.user_data and self.counter == 0:
                self.print_user(self.user_data, self.user_tagins)
                self.counter += 1
            if self.display_user and self.user_data and self.counter != 0:
                self.counter += 1
                #print self.display_time - self.counter * self.sleep_time
            if self.counter == self.display_time / self.sleep_time:
                self.counter = 0
                self.display_user = False
                self.user_data = None
                self.print_clear_screen("online")

            time.sleep(self.sleep_time)

    def ascii_print(self, text, font='slant'):
        f = Figlet(font=font)
        print(f.renderText(text))

    def get_user_data(self, tag_nbr):
        try:
            res = requests.get("http://localhost:80/crosstag/v1.0/get_user_data_tag/%s" % tag_nbr, timeout=3)
            return json.loads(res.text)
        except:
            return None

    def get_user_stats(self, user_id):
        res = requests.get("http://localhost:80/crosstag/v1.0/get_tagevents_user/%s" % user_id, timeout=3)
        return json.loads(res.text)

    def print_user(self, user_data, user_tagins):
        to_print = {}
        keys = ['name', 'expiry_date', 'create_date', 'gender']
        for k, v in user_data.items():
            if k in keys:
                to_print[k] = v

        for k, v in to_print.items():
            print(k.rjust(15), str(v).ljust(10))

    def print_clear_screen(self, msg=None):
        os.system('clear')
        self.ascii_print("Crossfit Kalmar")
        if msg:
            print (msg)

    def poll_server(self):
        try:
            res = requests.get("http://%s:%d/crosstag/v1.0/last_tagin" % (
                               self.server, self.port), timeout=3)
            res = json.loads(res.text)
            self.online = True
            return res
        except:
            self.online = False
            return None


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] arg \nTry this: \
                          python crosstag_viewer.py", version="%prog 1.0")
    parser.add_option("-s", "--server", action="store", type="string",
                      dest="server", default="localhost",
                      help="What is the URL to the crosstag server?")
    parser.add_option("-p", "--port", action="store", type="int",
                      dest="port", default=80,
                      help="What is the PORT of the crosstag server?")
    (options, args) = parser.parse_args()
    r = CrosstagViewer()
    r.main(options.server, options.port)
