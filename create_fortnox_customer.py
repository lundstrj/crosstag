# Install the Python Requests library:
# `pip install requests`
# We can use this clas to create members on fortnox.

import requests
import json

class ReadFromFortnox:

    def send_request(self):
        # Customer (POST https://api.fortnox.se/3/customers)

        try:
            r = requests.post(
                url="https://api.fortnox.se/3/customers",
                headers={
                    "Access-Token":"",
                    "Client-Secret":"",
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                },
                data=json.dumps({
                    "Customer": {
                        "fortnox_id": "",
                        "name": "",
                        "email": "",
                        "phone": "",
                        "tag_id": "",
                        "gender": "",
                        "birth_date": "",
                        "expiry_date": "",
                        "create_date": "",
                        "status": ""
                    }
                })
            )
            print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            print('Response HTTP Response Body : {content}'.format(content=r.content))
        except requests.exceptions.RequestException as e:
            print('HTTP Request failed')