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
 	
def getList(objectType, pageNum):	
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ['SELECT * FROM ' + objectType + ' PAGE ' + str(pageNum)]
	return data
	
def genQuery(pageNum):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT * FROM members ITEMS 10"]	
	# data["params"] = ["SELECT username, keys FROM members 	
	return data
	
def getKeys(username):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT * FROM keys WHERE username = '" + username + "'"]
	return data

def getApps(username):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT name FROM applications WHERE username = '" + username + "'"]
	return data

def getMembers(pageNum):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT publisher_key, email, username  FROM members PAGE " + str(pageNum)]
	return data


def callAPI(data):
	# convert the dict to a JSON payload
	data = json.dumps(data, ensure_ascii=True) # , sort_keys = True, indent=4)
	data = data.encode('utf-8')
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()
	req = urllib.request.Request(url, data)
	# print (url)
	try:
		response = urllib.request.urlopen(req)
		
	except urllib.error.URLError as e:
		pprint.pprint(data)
		print (e.code)
		print (e.reason)
		print (e.args)
		sys.exit()

	return response.read()

if __name__ == "__main__":

	# OPEN CSV FILE and convert it into a list of lists	
# 	with open('plans_packages.csv') as csvfile:
# 		service_listing = csv.DictReader(csvfile)
# 		packagePlan = [[row['Segment'],row['Portfolio'], row['Service'].splitlines()[0]]  for row in service_listing]
		
	
	while True: 
		pageNum = 0
		pageNum = pageNum + 1
		data = genQuery(pageNum)
		output = json.loads(callAPI(data).decode("utf-8"))
		pprint.pprint(output)

# 		data = getMembers(pageNum)
# 		members = json.loads(callAPI(data).decode("utf-8"))
		if output['result']['items'] == []:
			break
# 		for member in members['result']['items']:
# 			# f = open("sharethis_users.json", "a")
# 			m = m + 1
# 			print("%i: %s" % (m, member['username']))
# 			data = getKeys(member['username'])
# 			keys = json.loads(callAPI(data).decode("utf-8"))
# 			data = getApps(member['username'])
# 			apps = json.loads(callAPI(data).decode("utf-8"))
# 			member = json.dumps(member, ensure_ascii=True)
# 			apps = json.dumps(apps['result']['items'], ensure_ascii=True)
# 			keys = json.dumps(keys['result']['items'], ensure_ascii=True)
# 			# f.write('{"member": ' + member + ', "apps": ' + apps + ', "keys": ' + keys + ' }\n')
# 			print('{"member": ' + member + ', "apps": ' + apps + ', "keys": ' + keys + ' }')
# 			# f.close()