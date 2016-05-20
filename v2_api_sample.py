import urllib.request
import urllib.parse
import time
import hashlib
import math
import json
import csv 		# necessary for parsing excel / csv file
import sys 
import pprint
import string
import random
from base64 import b64encode
import argparse
import logging
import http.client
import argparse

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"
 
parser = argparse.ArgumentParser()
parser.add_argument('--delete', action='store_true')
parser.add_argument('--add', type=int)
args = parser.parse_args()

# http.client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# ID	Area			UUID
# 903	Inteliteng		29fbd5ab-786e-4857-b122-7514acbeeedb
# 901	Intelittest		a8458120-9026-4c59-9a81-2a5730d17f2f
# 904	Intelitprod		43e53c0a-252c-4a34-9fed-c6661ee14ef8
# 842	Intelsecurity	ddd56b3c-007e-4b52-8310-1b0ecd278de4

# load developer username, password and apikey / secret from text file.
# doing this for demo purposes.
# expected format is:
# { "dev1": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" }, 
# "dev2": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" } }

# i'm manually setting the developer name here 
developers = json.load(open('developers.json'))['dan']
areaID = 877

endpoint = "https://api.mashery.com"
path = "/v2/json-rpc/" + str(areaID)
 
my_names = ["jwilfong","euruskim"]
 
def buildAuthParams():
    """This function takes our API key and shared secret and uses it to create the signature that mashery wants """
    authHash = hashlib.md5();
    #time.time() gets the current time since the epoch (1970) with decimals seconds
    temp = str.encode(developers['apikey'] + developers['secret'] + repr(int(time.time())))
    authHash.update(temp)
    return authHash.hexdigest()
 		
def deleteObject(objectType, objectID):
	data = {}
	data["method"] = objectType + ".delete"
	data["id"] = 1
	params = {}
	params["id"] = objectID
	data["params"] = [params]
	return data
	
def getList(objectType, pageNum):	
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ['SELECT * FROM ' + objectType + ' PAGE ' + str(pageNum)]
	return data
	
def checkObject(objectType, objectName):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT name FROM " + objectType + " WHERE name = '" + objectName + "'"]
	return data

def validateObject():
	data = {}
	data["method"] = "member.validate"
	data["id"] = 1
	data["params"] = [{"passwd_new" : "en1273678jhfjhUS"}]
	return data

def findApplicationByExternalID(external_id):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT *, package_key FROM applications WHERE external_id = '" + external_id + "'"]
	return data

def getApplicationKeys(applicationID):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT *, keys FROM applications where external_id ="]
	# create the json payload for the API call
		# print (data)
	return data

def deleteMember(memberID):
	data = {}
	data["method"] = "member.delete"
	data["id"] = 1
	data["params"] = [memberID]
	# create the json payload for the API call
		# print (data)
	return data


def callAPI(data):
	# convert the dict to a JSON payload
	data = json.dumps(data, ensure_ascii=True) # , sort_keys = True, indent=4)
	data = data.encode('utf-8')
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()
	print (url)
	req = urllib.request.Request(url, data)
	# print (url)
	try:
		response = urllib.request.urlopen(req)
		return response.read()
		
	except urllib.error.URLError as e:
		pprint.pprint(data)
		print (e.code)
		print (e.reason)
		print (e.args)
		return e.reason.encode("utf-8")
		# sys.exit()

	

if __name__ == "__main__":

	for my_name in my_names:
		data = deleteMember(my_name)
		print(data)
		
		x = callAPI(data)
		print(x)
		
		# result = json.loads(callAPI(data).decode("utf-8"))
		# print(result)
