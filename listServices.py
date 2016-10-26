import requests
import urllib 	# this is needed for some URL safe parsing
import time
import hashlib	# needed for md5 / sha for the signature 
import json
import csv 		# necessary for parsing excel / csv file
import sys 
import pprint
import string
from base64 import b64encode
import argparse
import logging
import os
from dateutil.parser import *
from datetime import timedelta
from datetime import datetime
# import datetime
import pandas as pd
import numpy as ny

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"

developers = json.load(open('/Users/kincy/Projects/masheryStuff/developers.json'))['kincy']
argparse = argparse.ArgumentParser()
args = argparse.parse_args()

areaID, uuid, domain = 295, '3c3d5610-7de8-41bf-8ea4-31043c719bfe', "nordstrom" # DNB

masheryDateFormat="%Y-%m-%dT%H:%M:%SZ"

tokenPath = "https://api.mashery.com/v3/token"
v3endpoint = "https://" + domain + ".mashery.com/v3/rest"
endpoint = "https://api.mashery.com"
path = "/v2/rest/" + str(areaID)

logging.basicConfig(level=logging.INFO)

def buildAuthParams():
	# This function takes the API key and shared secret and uses it to create the signature
	authHash = hashlib.md5();
	temp = str.encode(developers['apikey'] + developers['secret'] + repr(int(time.time())))
	authHash.update(temp)
	return authHash.hexdigest()
	

def getOAuthHeaders():

	# create the necessary authorization header	
	userAndPass = b64encode(bytes(developers['apikey'] + ":" + developers['secret'], 'utf-8')).decode("utf-8")
	headers = { 'Authorization' : 'Basic %s' % userAndPass, "Content-Type": "application/x-www-form-urlencoded"}
	
	# pass the creds and the area UUID - NOT THE AREA ID
	data = 'grant_type=password&username=' + developers['username'] + '&password=' + developers['password'] + '&scope=' + uuid
	response = requests.post(tokenPath, data=str(data), headers=headers)
	
	# return the token
	return { 'Authorization' : 'Bearer %s' % response.json()["access_token"], "Content-Type": "application/json" }

def writeMasheryError(operation, apikey, reason):
		errorOutput = {}
		errorOutput['message'] = reason
		errorOutput["time"] = str(datetime.now().time())
		errorOutput['operation'] = operation
		logging.warn(errorOutput)
		# with open(keyErrorsFile, "a") as errorFile:
		#	errorFile.write(str(errorOutput) + "\n")


def getServicesv3(services = None):
	# if services aren't provided then we will get all them from the associated area
	if services is None:
		response = requests.get(v3endpoint + "/services", headers=getOAuthHeaders())
		if response.status_code != 200:
			print(str(response.status_code) + " response trying to get list of services: " + response.text)
			return None
		return response.json()	
		
	else:
		servicesDesc = []
		for serviceId in services:
			print("service ID provided: " + str(serviceId))
			response = requests.get(v3endpoint + "/services/" + serviceId, headers=getOAuthHeaders())
			servicesDesc.insert(0, response.json())
		return servicesDesc	

def getServicesV2(services = None):

	# if no service keys are provided at the command line, then we retrieve all of them from the area
	if services is None:
		payload = '{"method":"object.query","id":1,"params":["select *, endpoints from services items 1000"]}'
		# data = json.dumps(data, ensure_ascii=True).encode('utf-8')
		url = endpoint + "/v2/json-rpc/" + str(areaID) + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()
		try:
			response = requests.post(url, data=payload)		
		except urllib.error.URLError as e:
			pprint.pprint(data)
			print (e.code)
			print (e.reason)
			print (e.args)
			sys.exit()

		if response.json()['error'] is not None:
			logging.error("Error retrieving list of services from Area")
			sys.exit()
		else:
			servicesList = response.json()['result']['items']
			for x in servicesList:
				# this renames service_key to id
				x['id'] = x.pop("service_key")
			
		return servicesList

	else:
		# if a list of services is provided at the command line, we need to loop through to get the details. 
		servicesList = []
		for serviceId in services:
			payload = '{"method":"object.query","id":1,"params":["select * from services where service_key = \'' + serviceId + '\'"]}'
			logging.debug(payload)
			url = endpoint + "/v2/json-rpc/" + str(areaID) + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams()
			try:
				response = requests.post(url, data=payload)		
			except urllib.error.URLError as e:
				pprint.pprint(data)
				print (e.code)
				print (e.reason)
				print (e.args)
				sys.exit()
			
			if len(response.json()['result']['items']) < 1:
				logging.error("Error retrieving list of service " + serviceId + " from Area")
				logging.error(response.json())
			else:
				service = response.json()['result']['items'][0]
				service['id'] = service.pop("service_key")
				servicesList.insert(0, service)
		
		if len(servicesList) < 1:
			logging.error("no valid services found for area")
			sys.exit()

		return servicesList	

if __name__ == "__main__":

	# we use parse so we don't need a strict date format
	services = getServicesV2(None)
	if services is None:
		exit()
	for service in services:
		pprint.pprint(service)
		# print("{") service["id"],",",service["name"])
	
	
	
	
