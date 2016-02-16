import http.client
import json
import requests
import fortnox_cfg as cfg
from pyfiglet import Figlet
import os

##testar fortnox hämtning.
class Fortnox:

    def get_all_customers(self):
        try:
            r = requests.get(
                url = 'https://api.fortnox.se/3/customers',
                headers=cfg.fortnox
            )
            print('Response status: {status_code}'.format(status_code=r.status_code))
            content = json.loads(r.text)
            return content["Customers"]
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


    def insert_customer(self, user):
        try:
            r = requests.post(
                url = 'https://api.fortnox.se/3/customers',
                headers = cfg.fortnox,
                data = json.dumps({
                    "Customer": {
                        "Name": user.name,
                        "Email": user.email,
                        "Address1": user.address,
                        "Address2": user.address2,
                        "City": user.city,
                        "ZipCode": user.zip_code
                    }
                })
            )
            print('Response status: {status_code}'.format(status_code=r.status_code))
            print(user.name)
            print(user.email)
            print(user.address)
            print(user.address2)
            print(user.city)
            print(user.zip_code)
        except http.client.HTTPException as e:
            print('Exception during POST-request')










