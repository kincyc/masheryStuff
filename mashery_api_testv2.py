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

areaID = 903
endpoint = "https://api.mashery.com"
path = "/v2/json-rpc/" + str(areaID)
 
def buildAuthParams():
    """This function takes our API key and shared secret and uses it to create the signature that mashery wants """
    authHash = hashlib.md5();
    #time.time() gets the current time since the epoch (1970) with decimals seconds
    temp = str.encode(developers['apikey'] + developers['secret'] + repr(int(time.time())))
    authHash.update(temp)
    return authHash.hexdigest()
 
def createPackage(packageName, description):
	data = {}
	data["method"] = "package.create"
	data["id"] = 42
	params = {}
	params["name"] = packageName
	params["description"] = description
	params["key_length"] = 24
	params["shared_secret_length"] = 8
	data["params"] = [params]
	return data
	
def createPlan(packageID, planName, description):
	data = {}
	data["method"] = "plan.create"
	data["id"] = 2
	params = {}
	params["name"] = planName
	params["description"] = description
	params["order_max"] = 4
	params["is_moderated"] = True
	params["package"] = {"id":packageID}
	data["params"] = [params]
	return data

def createApplication(appName, username, description):
	data = {}
	params = {}
	member = {}
	data["method"] = "application.create"
	data["id"] = 1
	params["name"] = appName
	member["username"] = username
	params["member"] = {"username" : username}
	params["external_id"] = "1234567890"
	data["params"] = [params]
	return data
		
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

def getEndpointByName(endpoint):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT * FROM service_definition_endpoints WHERE name = '" + endpoint + "'"]
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
	with open('plans_packages.csv') as csvfile:
		service_listing = csv.DictReader(csvfile)
		packagePlan = [[row['Segment'],row['Portfolio'], row['Service'].splitlines()[0]]  for row in service_listing]
	
		# LOOP THROUGH LIST OF LISTS
		n = 0
		for f in packagePlan:
			time.sleep(0.5)
			if n >= args.add:
				break
			description = f[0] + "\n" + f[1]
			packagePlanName = f[2]
			# here we check to see if the plan exists
			data = checkObject("packages", packagePlanName)
			result = json.loads(callAPI(data).decode("utf-8"))
			if result["result"]["total_items"] > 0:
				print("ALREADY EXISTS: " + str(result['result']['items']))
			else:
			# create the data necessary for package creation
				data = createPackage(packagePlanName, description)
				#call the API and create the package
				# we get the results, decode them and load them into a json object
				packageResults = json.loads(callAPI(data).decode("utf-8"))
				packageID = (packageResults['result']['id'])
				data = createPlan(packageID, packagePlanName, description)
				planResults = json.loads(callAPI(data).decode("utf-8"))
				pprint.pprint (planResults)
			n = n + 1			

# 	# PRINT OUT EXiSTING PLANS
	pageNum = 0
	while True: 
		pageNum = pageNum + 1
		data = getList("plans", pageNum)
		listing = json.loads(callAPI(data).decode("utf-8"))
		if listing['result']['items'] == []:
			break
		print ("f listing loop")		
		for f in listing['result']['items']:
			print ("%s\t%s\t%s" % (f['name'], str(f['id']), f['uuid']))

			if args.delete:
				if f['id'] > 5800:
					print("deleting package %i" % f['id'])
					data = deleteObject("package" ,f['id'])
					listing = json.loads(callAPI(data).decode("utf-8"))
					pprint.pprint(listing)