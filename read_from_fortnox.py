import requests

class ReadFromFortnox:

    def send_request(self):

            try:
                r = requests.get(
                    url="https://api.fortnox.se/3/customers",
                    headers = {
                        "Access-Token":"",
                        "Client-Secret":"",
                        "Content-Type":"application/json",
                        "Accept":"application/json",
                    },
                )
                print('Response HTTP Status Code : {status_code})'.format(status_code=r.status_code))
                print('Response HTTP Response Body : {content})'.format(content=r.content))
            except requests.exceptions.RequestException as e:
                print('HTTP Request failed')
