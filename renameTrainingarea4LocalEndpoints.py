# This code will create a package, then create a plan and finally add an endpoint.
# This is written in Python3. Take care to make sure you import the libraries.
# Important - I'm using the Python 3 Requests library.
# I chose this because it is an easy http client that supports different HTTP methods (GET, DELETE, PUT, etc.)
# This code uses Mashery v3 API. 

import time
import hashlib
import pprint
import random
import requests
import logging
import json
import string
from base64 import b64encode
import csv
import http.client # need to be explicit for logging

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"

# load developer username, password and apikey / secret from text file.
# doing this for demo purposes.
# expected format is:
# { "dev1": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" }, 
# "dev2": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" } }

developers = json.load(open('developers.json'))['kincy']

# endpoints
tokenPath = "https://api.mashery.com/v3/token"
v3endpoint = "https://api.mashery.com/v3/rest"
uuid = 'ff368e6f-4f41-4d4b-8f9b-10ea76b301f2'

def getOAuthHeaders():

	# create the necessary authorization header	
	userAndPass = b64encode(bytes(developers['apikey'] + ":" + developers['secret'], 'utf-8')).decode("utf-8")
	headers = { 'Authorization' : 'Basic %s' % userAndPass, "Content-Type": "application/x-www-form-urlencoded"}	
	data = 'grant_type=password&username=' + developers['username'] + '&password=' + developers['password'] + '&scope=' + uuid
	response = requests.post(tokenPath, data=str(data), headers=headers)
	
	# return the token
	return { 'Authorization' : 'Bearer %s' % response.json()["access_token"], "Content-Type": "application/json" }

def updateEndpoint(serviceId, endpointId, data):
	url = v3endpoint + "/services/" + serviceId + "/endpoints/" + endpointId
	response = requests.put(url, data=json.dumps(data), headers=OAuthheaders)
	response = requests.put(url, data=str(data), headers=OAuthheaders)
	return response.json()

def getEndpoint(serviceId, endpointId):
	url = v3endpoint + "/services/" + serviceId + "/endpoints/" + endpointId + "?fields=name,id"
	print(url)
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getEndpoints(serviceId):
	url = v3endpoint + "/services/" + serviceId + "/endpoints"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

if __name__ == "__main__":
	global OAuthheaders

	# print (getFillerText())
	OAuthheaders = getOAuthHeaders()
	# this gets endpoints for the Mashery Local Endpoints service
	endpoints = getEndpoints("t5waw6r7frfkdz9z28swm638")
	
	for e in endpoints:
		# pprint.pprint("{'name':'" + e["name"] + "2'}")
		if (e['name'][-2:]) == '12':
			newname = e["name"][:-2]
		else:
			newname = e["name"] + "_1"
			response = updateEndpoint("t5waw6r7frfkdz9z28swm638", e["id"], '{"name":"' + newname + '"}')
		print(response)
