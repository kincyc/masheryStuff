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
import argparse
import requests
import datetime

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"
 
developers = json.load(open('developers.json'))['kincy']
areaID = 93

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
	data["params"] = ['SELECT * FROM ' + objectType + ' PAGE ' + str(pageNum) + ' ITEMS 100']
	# data["params"] = ["SELECT *, keys.application.name FROM members WHERE username = 'bryanlokey' PAGE " + str(pageNum) + " ITEMS 100"]
	# data["params"] = ['SELECT username, keys.application.name, keys.apikey FROM members ' + ' PAGE ' + str(pageNum) + ' ITEMS 100']
	# data["params"] = ['SELECT username, name, keys.apikey FROM applications ' + ' PAGE ' + str(pageNum) + ' ITEMS 100']
	result = callAPI("getList", data)
	if not result:
		return False
	
	return result['result']['items']

def fetchKey(key):
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ["SELECT * FROM keys WHERE apikey = '" + key +"'"]	
	result = callAPI("fetchKey", data)
	if not result:
		return False
	
	if len(result['result']['items']) == 0:
		writeMasheryError("fetchKey", key, "Key not found in Mashery database")
		return False 
	
	logging.debug("Successfully fetched key: " + key)
	logging.debug(result['result']['items'][0])
	return result['result']['items'][0]

def callAPI(operation, data):

	data = json.dumps(data, ensure_ascii=True).encode('utf-8') # , sort_keys = True, indent=4)
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()

	try:
		response = requests.post(url, data, timeout=30)
	
	except requests.exceptions.RequestException as e:
		# we have to decode the json object for pretty printing
		# Otherwise, just outputs a byte object that isn't pretty printable
		errorOutput = {}
		errorOutput['operation'] = operation
		errorOutput["message"] = str(e)
		errorOutput["oldapikey"] = oldApiKey.rstrip()
		errorOutput["time"] = str(datetime.datetime.now().time())
		logging.warn(errorOutput)
		# 		with open(keyErrorsFile, "a") as errorFile:
		# 			errorFile.write(str(errorOutput) + "\n")
		# 		time.sleep(5)
		return False

	if response.headers['Content-Length'] == 0:
		logging.warn("Zero-byte Content Returned")
		writeMasheryError("fetchKey", key, "Key not found in Mashery database")
		time.sleep(2)
		return False

	try:
		return response.json()
	except (ValueError, TypeError):
		errorOutput = {}
		errorOutput['operation'] = operation
		errorOutput["message"] = "No JSON Response" + str(response.headers)
		errorOutput["oldapikey"] = oldApiKey.rstrip()
		errorOutput["time"] = str(datetime.datetime.now().time())
		logging.warn(errorOutput)
# 		with open(keyErrorsFile, "a") as errorFile:
# 			errorFile.write(str(errorOutput) + "\n")
# 		time.sleep(2)
		return False		
	return response.json()

def writeMasheryError(operation, apikey, reason):
	errorOutput = {}
	errorOutput['message'] = reason
	errorOutput['apikey'] = apikey.rstrip()
	errorOutput["time"] = str(datetime.datetime.now().time())
	errorOutput['operation'] = operation
	logging.warn(errorOutput)
# 	with open(keyErrorsFile, "a") as errorFile:
# 		errorFile.write(str(errorOutput) + "\n")
	return False

if __name__ == "__main__":

	logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
	pageNum = 0

	listing = getList("package_keys", pageNum)

	while True: 
		pageNum = pageNum + 1
		listing = getList("package_keys", pageNum)
		if len(listing) < 1:
			break
		for o in listing:
			pprint.pprint(o)
				
			# pprint.pprint(o)

