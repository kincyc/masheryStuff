#!/usr/local/bin/python

import time
import hashlib
import math
import json
import pprint
import string
from base64 import b64encode
import argparse
import logging
import requests

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"
 
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--users', help="enter username of members to be removed from area, separate by a space", nargs='*')
parser.add_argument('-a', '--area', help="enter area id that username from which will be remove", type=int, required=True)
args = parser.parse_args()

# developers = json.load(open('developers.json'))['kincy']

developers = {}
developers['apikey'] = "qwe6b3khns3aww9e225scnw3"
developers['secret'] = "PAYJ2GXvNM"


areaID = args.area

endpoint = "https://api.mashery.com"
path = "/v2/json-rpc/" + str(areaID)
 
def buildAuthParams():
    """This function takes our API key and shared secret and uses it to create the signature that mashery wants """
    authHash = hashlib.md5();
    #time.time() gets the current time since the epoch (1970) with decimals seconds
    temp = str.encode(str(developers['apikey']) + str(developers['secret']) + repr(int(time.time())))
    authHash.update(temp)
    return authHash.hexdigest()

def getList(objectType, pageNum):	
	data = {}
	data["method"] = "object.query"
	data["id"] = 1
	data["params"] = ['SELECT * FROM ' + objectType + ' PAGE ' + str(pageNum)]
	result = callAPI(data)
	if not result:
		return False

	if result['error'] == None:
		return result['result']['items']
	else:
		print(result)
		print("error retrieving list of users. Possibly a bad Mashery API key")
		return False

def deleteMember(memberID):
	data = {}
	data["method"] = "member.delete"
	data["id"] = 1
	data["params"] = [memberID]
	result = callAPI(data)
	if (result['error'] == None):
		logging.warn("User " + memberID + " successfully removed from area " + str(areaID))
		return True
	
	return False

def callAPI(data):

	data = json.dumps(data, ensure_ascii=True).encode('utf-8') # , sort_keys = True, indent=4)
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()

	try:
		response = requests.post(url, data, timeout=30)
	
	except requests.exceptions.RequestException as e:
		logging.warn(str(e))
		time.sleep(1)
		return False

	logging.debug("RESPONSE HEADERS")
	logging.debug(response.headers)
	
	if response.headers['Content-Length'] == 0:
		logging.warn("Zero-byte Content Returned")
		time.sleep(1)
		return False

	try:
		return response.json()
	except (ValueError, TypeError):
		logging.warn("No JSON Response" + str(response.headers))
		time.sleep(1)
		return False

	return response.json()

if __name__ == "__main__":

	if args.users:
		# if delete argument is passed, just remove that username and exit
		for m in args.users:
			data = deleteMember(m)
	else:

	# 	list existing members and ask to delete them
		pageNum = 0
		while True: 
			pageNum = pageNum + 1			
			listing = getList("members", pageNum)
			if(listing):
				for m in listing:
					deleteme = raw_input('remove %s (%s : %s) from %i? (y/n/q) ' % (m['display_name'],m['username'],m['email'], areaID))
					if deleteme == 'y':
						print("Deleting %s" % m['display_name'])
						data = deleteMember(m['username'])
					if deleteme == 'q':
						exit()
			else:
				exit()