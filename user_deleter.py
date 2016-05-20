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
import requests

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"
 
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--delete', help="enter username of member to be removed from area", type=str)
args = parser.parse_args()

developers = json.load(open('developers.json'))['kincy']
areaID = 295

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
	result = callAPI("getList", data)
	if not result:
		return False
	
	if len(result['result']['items']) == 0:
		writeMasheryError("getList", key, "Objects not found in area")
		return False 
	
	return result['result']['items'][0]
	

def deleteMember(memberID):
	data = {}
	data["method"] = "member.delete"
	data["id"] = 1
	data["params"] = [memberID]
	result = callAPI("deleteMember", data)
	if not result:
		return False
	
	if len(result['result']['items']) == 0:
		writeMasheryError("deleteMember", key, "Member not found in area")
		return False 

	return result['result']['items'][0]

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

	# convert the dict to a JSON payload
	data = json.dumps(data, ensure_ascii=True).encode('utf-8') # , sort_keys = True, indent=4)
	# generate the URL to call the Mashery API
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
		with open(keyErrorsFile, "a") as errorFile:
			errorFile.write(str(errorOutput) + "\n")
		time.sleep(5)
		return False

	logging.debug("RESPONSE HEADERS")
	logging.debug(response.headers)
	
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
		with open(keyErrorsFile, "a") as errorFile:
			errorFile.write(str(errorOutput) + "\n")
		time.sleep(2)
		return False
		
	return response.json()
	
def writeMasheryError(operation, apikey, reason):
		errorOutput = {}
		errorOutput['message'] = reason
		errorOutput['oldapikey'] = oldApiKey.rstrip()
		errorOutput["time"] = str(datetime.datetime.now().time())
		errorOutput['operation'] = operation
		logging.warn(errorOutput)
		with open(keyErrorsFile, "a") as errorFile:
			errorFile.write(str(errorOutput) + "\n")
	

if __name__ == "__main__":

	if args.delete:
		# if delete argument is passed, just remove that username and exit
		data = deleteMember(args.delete)
		print(data)
		result = json.loads(callAPI(data).decode("utf-8"))
		pprint.pprint(result)
	else:

	# 	list existing members and ask to delete them
		pageNum = 0
		while True: 
			pageNum = pageNum + 1
			data = getList("members", pageNum)
			listing = json.loads(callAPI(data).decode("utf-8"))
			if listing['result']['items'] == []:
				break
			members = (listing['result']['items'])
			for m in members:
				print(m['display_name'])
				print(m)
				deleteme = input('should I remove %s (%s : %s) from %i? ' % (m['display_name'],m['username'],m['email'], areaID))
				if deleteme == 'y':
					print("I would be deleting %s" % m['display_name'])
					data = deleteMember(m['username'])
					result = json.loads(callAPI(data).decode("utf-8"))
					pprint.pprint(result)

