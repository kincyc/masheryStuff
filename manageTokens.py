import time
import hashlib
import math
import json
import sys 
import requests
import pprint
import string
import random
from base64 import b64encode
import csv

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"
 
developers = json.load(open('developers.json'))['kincy']

areaID = 780
endpoint = "https://api.mashery.com"
path = "/v2/json-rpc/" + str(areaID)
 
def buildAuthParams():
    """This function takes our API key and shared secret and uses it to create the signature that mashery wants """
    authHash = hashlib.md5();
    #time.time() gets the current time since the epoch (1970) with decimals seconds
    temp = str.encode(developers['apikey'] + developers['secret'] + repr(int(time.time())))
    authHash.update(temp)
    return authHash.hexdigest()

def deleteTokens(spkey, client, token):
	payload = {}
	payload["jsonrpc"] = "2.0"
	payload["method"] = "oauth2.revokeAccessToken"
	payload["params"] = {}
	payload["params"]["service_key"] = spkey
	payload["params"]["client"] = {"client_id": client}
	payload["params"]["access_token"] = token
	payload["id"] = 1
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()
	pprint.pprint(payload)
	response = requests.post(url, data=json.dumps(payload))
	return response.json()

def createToken(spkey, client_id, secret, user_context):
	payload = {}
	payload["jsonrpc"] = "2.0"
	payload["method"] = "oauth2.createAccessToken"
	payload["params"] = {}
	payload["params"]["token_data"] = {"grant_type": "client_credentials"}
	payload["params"]["user_context"]= user_context
	payload["params"]["service_key"] = spkey
	payload["params"]["client"] = {"client_id": client_id, "client_secret": secret}
	payload["params"]["uri"] = {"redirect_uri": "https:\/\/client.example\/cb"}
	payload["id"] = 1
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()
	pprint.pprint(payload)
	response = requests.post(url, data=json.dumps(payload))
	return response.json()

def fetchToken(spkey, token):
	payload = {}
	payload["jsonrpc"] = "2.0"
	payload["method"] = "oauth2.fetchAccessToken"
	payload["params"] = {}
	payload["params"] = {"service_key": spkey, "access_token": token}
	payload["id"] = 1
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()
	pprint.pprint(payload)
	response = requests.post(url, data=json.dumps(payload))
	return response.json()

if __name__ == "__main__":

	x = createToken("g29353wbtdrxtxd4g3373ekv", "xk5nmy7gvtsjkp437mqn9dyr", "1234567890", "askhkjahkjahdkjash")
	print(x)
	
# 	with open('tokens.out', 'r') as tokens:
# 		tokenreader = csv.reader(tokens, delimiter ="\t")
# 		x = 0
# 		for row in tokenreader:
# 			x = x + 1
# 			print(row[0], row[1], row[2])
# 			print(deleteTokens(row[0], row[1], row[2]))
# 			if x == 8000:
# 				break
# 			# time.sleep(1)