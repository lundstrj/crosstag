import httplib

# Request: Account Charts (https://api.fortnox.se/3/accountcharts)

#connection = httplib.HTTPSConnection('api.fortnox.se', 443, timeout = 30)
connection = httplib.HTTPSConnection('api-acce-current.fortnox.se', 443, timeout = 30)

# Headers

headers = {"Client-Secret":"R1438E69IP",
           "Content-Type":"application/xml",
           "Access-Token":"6d50f61c-a545-420c-80a6-2989cb78cc5e",
           "Accept":"application/xml"}

# Send synchronously

connection.request('GET', '/3/invoices/', None, headers)
try:
	response = connection.getresponse()
	content = response.read()
	# Success
	print('Response status ' + str(response.status))
	print content
except httplib.HTTPException, e:
	# Exception
	print('Exception during request')