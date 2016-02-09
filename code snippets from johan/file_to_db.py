import time
import sys
import requests

f = open('boxen.csv', 'r')
while True:
    try:
        data = f.readline()
    except:
        print "EOF, exiting"
    data = data.strip("/n")
    data = data.strip("/n")
    data = data.strip("/n")
    data = data.strip("/n")
    data = data.strip("/t")
    data = data.strip("/t")
    data = data.strip("/t")
    data = data.strip("/t")

    parts = data.split(",")
    box_id = parts[0]
    name = parts[1]
    postalcode = parts[2]
    city = parts[3]
    phone = parts[4]
    if len(phone) < 1:
        phone = "00000000000"
    email = parts[5]
    if len(email) < 1:
        email = "NA"


    url = "http://localhost:80/crosstag/v1.0/create_user/%s/%s/%s/%s" % (name, email, phone, box_id)
    res = requests.get(url, timeout=10)
    #print type(res)
    print "URL:", url
    print "RES:",res.text
    print "created user: %s" % name