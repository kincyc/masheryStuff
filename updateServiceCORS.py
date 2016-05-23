# This code will update all of the "Cross-Domain Policy for API Access via Flash" fields for all the services in a given area
# This is written in Python3. Take care to make sure you import the libraries.
# Important - I'm using the Python 3 Requests library.
# I chose this because it is an easy http client that supports different HTTP methods (GET, DELETE, PUT, etc.)
# This code uses Mashery v3 API. 

import time
import hashlib
import pprint
import requests
import string
import json
from base64 import b64encode
import csv

# load developer username, password and apikey / secret from text file.
# doing this for demo purposes.
# expected format is:
# { "dev1": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" }, 
# "dev2": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" } }

# i'm manually setting the developer name here 
developers = json.load(open('developers.json'))['kincy']

# endpoints
v3endpoint = "https://api.mashery.com/v3/rest"
tokenPath = "https://api.mashery.com/v3/token"
uuid = 'ff368e6f-4f41-4d4b-8f9b-10ea76b301f2'	# trainingarea4

def getOAuthHeaders():
	# create the necessary authorization header	
	userAndPass = b64encode(bytes(developers['apikey'] + ":" + developers['secret'], 'utf-8')).decode("utf-8")
	headers = { 'Authorization' : 'Basic %s' % userAndPass, "Content-Type": "application/x-www-form-urlencoded"}
	# pass the creds and the area UUID - NOT THE AREA ID
	data = 'grant_type=password&username=' + developers['username'] + '&password=' + developers['password'] + '&scope=' + uuid
	response = requests.post(tokenPath, data=str(data), headers=headers)
	# return the token
	return { 'Authorization' : 'Bearer %s' % response.json()["access_token"], "Content-Type": "application/json" }

def getService(serviceId):
	url = v3endpoint + "/services/" + serviceId + "?fields=crossdomainPolicy"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getServices():
	url = v3endpoint + "/services"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def updateService(serviceId, data):
	url = v3endpoint + "/services/" + serviceId
	response = requests.put(url, data=json.dumps(data), headers=OAuthheaders)
	return response.json()

if __name__ == "__main__":
	global OAuthheaders

	OAuthheaders = getOAuthHeaders()	
	# initialize a python dictionary
	myData = {}
	# load with crossdomain XML. Include newlines for readability in the GUI
# 	myData['crossdomainPolicy'] = '<?xml version="1.0"?>\n<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">\n<cross-domain-policy>\n\n<allow-access-from domain="assetsw.sellpoint.net" />\n<allow-access-from domain="a.sellpoint.net" />\n<allow-access-from domain="assets.sellpoint.net" />\n<allow-access-from domain="*.walmart.com"/>\n<allow-access-from domain="t.sellpoints.com"/>\n</cross-domain-policy>'

	myData['crossdomainPolicy'] = ''

	for service in getServices():
		response = updateService(service["id"], myData)
		pprint.pprint(response)
		details = getService(service["id"])
		pprint.pprint(details)
		