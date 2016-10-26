import urllib.request
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

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"
 
parser = argparse.ArgumentParser()
parser.add_argument('--area', type=int, default=780)
args = parser.parse_args()

developers = json.load(open('developers.json'))['kincy']

areaID = args.area
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
	data["params"] = ["SELECT * FROM members ITEMS 10000 PAGE " + str(pageNum)]
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
	data["params"] = ["SELECT * FROM members PAGE " + str(pageNum) + " ITEMS 1000"]
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

	pageNum = 1
	while True: 
		data = getMembers(pageNum)
		members = json.loads(callAPI(data).decode("utf-8"))
		if members['result']['items'] == []:
			break
		with open('developers_' + str(areaID) + '.csv', 'a') as csvfile:
			if pageNum == 1:
				fieldnames = list(members['result']['items'][0].keys())
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writeheader()
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			for member in members['result']['items']:
				writer.writerow(member)
		print(pageNum)
		pageNum = pageNum + 1
