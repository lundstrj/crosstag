import http.client

# Request: Account Charts (https://api.fortnox.se/3/accountcharts)


connection = http.client.HTTPSConnection('api.fortnox.se')

# Headers

headers = {"Client-Secret": "WcL4oKGKf9",
           "Access-Token": "3f01c142-04ae-4e33-8199-b671bfe0f008",
           "Content-Type": "application/json",
           "Accept": "application/json"}

connection.request('GET', '/3/customers', None, headers)

response = connection.getresponse()
content = response.read()

print(str(response.status))
print(content)

