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
	data["params"] = ['SELECT * FROM ' + objectType + ' WHERE area_status = \'disabled\' PAGE ' + str(pageNum)]
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

