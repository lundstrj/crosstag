import http.client
import fortnox_cfg as cfg
from pyfiglet import Figlet
import os
import json


#testar fortnox hämtning.
class Fortnox:
    def __init__(self):

        self.get_all_customers()

    def get_all_customers(self):

        connection = http.client.HTTPSConnection('api.fortnox.se')
        connection.request('GET', '/3/customers', None, cfg.fortnox)

        try:
            response = connection.getresponse()
            content = response.read()
            # Success
            print('Response status ' + str(response.status))
            print (content)
        except http.client.HTTPException:
            # Exception
            print('Exception during request')



        return content["Customer"]













