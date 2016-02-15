import http.client
import json
import fortnox_cfg as cfg
from pyfiglet import Figlet
import os

##testar fortnox hämtning.
class Fortnox:

    def get_all_customers(self):

        connection = http.client.HTTPSConnection('api.fortnox.se')
        connection.request('GET', '/3/customers/', None, cfg.fortnox)

        try:
            response = connection.getresponse()
            content = response.read()
            # Success
            print('Response status ' + str(response.status))
            print (content)

            str_response = content.decode('utf-8')
            obj = json.loads(str_response)
            return obj["Customers"]
        except http.client.HTTPException:
            # Exception
            print('Exception during request')

    def get_customer_by_id(self, id):
        connection = http.client.HTTPSConnection('api.fortnox.se')
        connection.request('GET', '/3/customers/'+id+'/', None, cfg.fortnox)

        try:
            response = connection.getresponse()
            content = response.read()
            # Success
            print('Response status ' + str(response.status))
            print (content)

            return content
        except http.client.HTTPException:
            # Exception
            print('Exception during request')













