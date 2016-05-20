# import urllib.request
# import urllib.parse
import requests
import time
import hashlib
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
import datetime
import pdb

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"

developers = json.load(open('developers.json'))['kincy']

tokenPath = "https://api.mashery.com/v3/token"
v3endpoint = "https://api.mashery.com/v3/rest"

developerId = "mxwpckrtpsnjvsryqdd73q4v"
startDate = 
endDate = 

uuid = 'ff368e6f-4f41-4d4b-8f9b-10ea76b301f2' 	# trainingarea4
areaID = 780		# training area 4
# uuid = "f858dc90-2730-4d39-b598-2b83776c56e3"	# macys staging
# areaID = 266		# macysstaging

count = 0
endpoint = "https://api.mashery.com"
path = "/v2/rest/" + str(areaID)
reportFile = "reportOutput" + "_" + (time.strftime("%d-%m-%Y"))+ "-"+ (time.strftime("%I-%M-%S")) + ".txt"
print(reportFile)

logging.basicConfig(level=logging.WARN)

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

def callReportingAPI(operation, dateTimeRange):
	# generate the URL to call the Mashery API
	url = endpoint + path + operation + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams() + "&" + dateTimeRange + "&format=json"

	try:
		response = requests.get(url, timeout=60)
	
	except requests.exceptions.RequestException as e:
		# we have to decode the json object for pretty printing
		# Otherwise, just outputs a byte object that isn't pretty printable
		errorOutput = {}
		errorOutput['operation'] = operation
		errorOutput["message"] = str(e)
		errorOutput["time"] = str(datetime.datetime.now().time())
		logging.warn(errorOutput)
		# 		with open(keyErrorsFile, "a") as errorFile:
		# 			errorFile.write(str(errorOutput) + "\n")
		time.sleep(5)
		return False

	logging.debug("RESPONSE HEADERS")
	logging.debug(response.headers)
	
	if response.headers['Content-Length'] == 0:
		logging.warn("Zero-byte Content Returned")
		# writeMasheryError("fetchKey", key, "Key not found in Mashery database")
		return False

	try:
		return response.json()
	except (ValueError, TypeError):
		errorOutput = {}
		errorOutput['operation'] = operation
		errorOutput["message"] = "No JSON Response" + str(response.headers)
		errorOutput["time"] = str(datetime.datetime.now().time())
		logging.warn(errorOutput)
		# 		with open(keyErrorsFile, "a") as errorFile:
		# 			errorFile.write(str(errorOutput) + "\n")
		time.sleep(2)
		return False
	
	return response.json()
	

def writeMasheryError(operation, apikey, reason):
		errorOutput = {}
		errorOutput['message'] = reason
		errorOutput["time"] = str(datetime.datetime.now().time())
		errorOutput['operation'] = operation
		logging.warn(errorOutput)
		# with open(keyErrorsFile, "a") as errorFile:
		#	errorFile.write(str(errorOutput) + "\n")


def loopDate(startDate,endDate):
	
	s = datetime.datetime.strptime(startDate, "%d-%b-%Y")
	e = datetime.datetime.strptime(endDate, "%d-%b-%Y")
	
	if e > s + 7:
		print("looped!", s, s+6)
		loopDate(s+7, e)
	else:
		print("looped!", s, e)

	loopDate(s,e)

def reportDeveloperMethods(serviceId, developerId):	
	return "/reports/calls/methods/service/" + serviceId + "/developer/" + developerId

def reportDeveloperStatus(serviceId, developerId):	
	return "/reports/calls/status/service/" + serviceId + "/developer/" + developerId

def reportCallsDeveloperActivityForService(serviceId):
	return "/reports/calls/developer_activity/service/" + serviceId 

def getServices():
	response = requests.get(v3endpoint + "/services", headers=getOAuthHeaders())
	return response.json()	

if __name__ == "__main__":

	for service in getServices():
		print(service["id"] + " " + service["name"])
		uri = reportCallsDeveloperActivityForService(service["id"])
		# uri = reportDeveloperStatus(service["id"], developerId)
		report = callReportingAPI(uri, dateRange)
		print(report)
		if type(report) is list:
			for line in report:
				# {'endDate': '2016-03-28T00:00:00Z', 'methodCount': 2, 'serviceDevKey': 'zkvrhg8ueup56sccnm83ef8m', 'startDate': '2016-03-27T00:00:00Z', 'serviceKey': 'cbcwnrturtn3h6umssqr3fk5', 'auditInfo': '1459443212 CallsMethodsForServiceForDeveloper', 'apiMethod': 'v3 catalog reviews'}
# 				with open(reportFile, 'a', newline='') as csvfile: 
# 					reportWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 					mylist=[line["startDate"], line["endDate"], line["methodCount"], line["apiMethod"], line["methodCount"]]
# 					print(myList)
# 					reportWriter.writerow(mylist)

				print(line)
