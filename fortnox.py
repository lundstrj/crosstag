import http.client
import fortnox_cfg as cfg
from pyfiglet import Figlet
import os

##testar fortnox hämtning.
class Fortnox:
    def __init__(self):

        self.get_all_customers()

    def get_all_customers(self):

        connection = http.client.HTTPSConnection('api.fortnox.se')
        connection.request('GET', '/3/customers', None, cfg.headers_json)

        response = connection.getresponse()
        content = response.read()


        return content













