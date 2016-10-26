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
import datetime
import logging
import os
from dateutil.parser import *
from datetime import timedelta
import pandas as pd
import numpy as ny

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"

developers = json.load(open('/Users/kincy/Projects/masheryStuff/developers.json'))['kincy']
argparse = argparse.ArgumentParser()
argparse.add_argument("--startdate", type=str, help="Start Date")
argparse.add_argument("--enddate", type=str, help="End Date")
argparse.add_argument('--keys',  nargs='+', help='List of keys to include in results, space separated')
argparse.add_argument('--services',  nargs='+', help='List of services to include in results, space separated')
argparse.add_argument('--reports',  nargs='+', choices=['status', 'errorcodes', 'methods'], help='List of services to include in results, space separated')
args = argparse.parse_args()

# areaID, uuid = 780, 'ff368e6f-4f41-4d4b-8f9b-10ea76b301f2' 	# trainingarea4
# areaID, uuid = 93, '78ff7613-ae2a-4481-827b-9255b8307ebd' 	# solutions

areaID, uuid = 295, 'cfea444a-e396-442f-b38b-a2dafc000195'	# nordstrom

tokenPath = "https://api.mashery.com/v3/token"
v3endpoint = "https://api.mashery.com/v3/rest"
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
		errorOutput["time"] = str(datetime.datetime.now().time())
		errorOutput['operation'] = operation
		logging.warn(errorOutput)
		# with open(keyErrorsFile, "a") as errorFile:
		#	errorFile.write(str(errorOutput) + "\n")

	
def getEndpoints(serviceId):
	url = v3endpoint + "/services/" + serviceId + "/endpoints"
	print(url)
	response = requests.get(url, headers=getOAuthHeaders())
	print(response)
	return response.json()

def genReportAPIUrl(report, serviceId, developerId):
	
	return "/reports/calls/" + report + "/service/" + serviceId + "/developer/" + developerId

def callReportingAPI(operation, dateTimeRange):
	# generate the URL to call the Mashery API
	url = endpoint + path + operation + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams() + "&" + dateTimeRange + "&format=json"
	logging.debug(url)
	try:
		response = requests.get(url, timeout=60)
		logging.debug(response.status_code)
	
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

	if response.status_code != 200:
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

def getServicesV2(services = None):

	# if no service keys are provided at the command line, then we retrieve all of them from the area
	if services is None:
		payload = '{"method":"object.query","id":1,"params":["select * from services items 1000"]}'
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

def getDates(startDate, endDate):

	dateList = []
	if startDate + datetime.timedelta(days=7) < endDate:		
		dateList.extend(getDates(startDate + datetime.timedelta(days=7), endDate))
		
	if len(dateList) == 0 :
		dateList.insert(0, [startDate, endDate])		
	else:
		dateList.insert(0, [startDate, startDate + datetime.timedelta(days=6)]) # , hours=23, minutes=59, seconds=59, milliseconds=999)])		

	return dateList
	
def getReports(reportList):	
	if reportList is None:
		logging.info("running all reports")
		return ['status', 'errorcodes', 'methods']
	else:
		return reportList

def reportConfig():

	reportConfigs = {'methods': {'pivot': True, 'pivotColumns': ['apiMethod'], 'pivotValue': 'methodCount', }, 'errorcodes': {'pivot': True, 'pivotColumns': ['errorcode'], 'pivotValue': 'errorcodeCount'}, 'status': {'pivot': False, 'pivotColumns': ['callStatusSuccessful', 'callStatusBlocked', 'callStatusOther'], 'pivotValue': 'methodCount'}}
	return reportConfigs

def getObjectV2():

	payload = '{"method":"object.query","id":1,"params":["select *, keys from applications items 1000"]}'
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
		# for x in servicesList:
			# this renames service_key to id
			# x['id'] = x.pop("service_key")
		
	return servicesList

if __name__ == "__main__":

	# generate a list of application keys
	applications = getObjectV2()
	appKeys = {}
	for a in applications:
		for k in a['keys']:
			appKeys[k['apikey']] = a['name']
			
	pprint.pprint(appKeys)
	exit.sys()
	report = "status"
	
	startDate, endDate = parse(str(args.startdate)), parse(str(args.enddate))
	dateList = getDates(startDate, endDate)
	services = getServicesV2()
	if services is None:
		exit()
	logging.debug(services)
	reportTypes = getReports(args.reports)
	reportConfig = reportConfig()
	printedHeader = False
	doPivot = True
	
	# loop through report types	
	for reportType in reportTypes:
	
		for developerId in args.keys:
			# we create a new file for each developer
			printedHeader = False
			tmpReportFile = developerId + "_tmp_" + (datetime.datetime.now().strftime("%Y-%m-%d"))+ "_"+ (datetime.datetime.now().strftime("%H-%M-%S")) + ".csv"
			# loop through services
			for service in services:
	
				for reportDate in dateList:
					strStartDate = reportDate[0].strftime("%Y-%m-%dT%H:%M:%SZ")
					strEndDate = reportDate[1].strftime("%Y-%m-%dT%H:%M:%SZ")
					dateRange = "start_date=" + urllib.parse.quote(strStartDate) + "&" + "end_date=" + urllib.parse.quote(strEndDate)
					uri = genReportAPIUrl(reportType, service['id'], developerId)
					report = callReportingAPI(uri, dateRange)
					if report == False:
						logging.info("no data found in service:{} for:{} during:{} - {}".format(service["id"], developerId, reportDate[0].strftime("%Y-%m-%d"), reportDate[1].strftime("%Y-%m-%d")))
					else:
						logging.info("processing reporting data for service:{} for:{} during:{} - {}".format(service["id"], developerId, reportDate[0].strftime("%Y-%m-%d"), reportDate[1].strftime("%Y-%m-%d")))
						for line in report:
							if "auditInfo" in line: 
								del line["auditInfo"]
							# add service name to dict
							line['serviceName'] = service['name']
							with open(tmpReportFile, "a") as f:
								reportWriter = csv.DictWriter(f, fieldnames=list(line.keys()), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
								if printedHeader == False:
									reportWriter.writeheader()
									printedHeader = True
								else:
									reportWriter.writerow(line)
			# once we write out the raw data, we need to pivot the data
			if os.path.isfile(tmpReportFile) is True and doPivot is True:
				pd.set_option('expand_frame_repr', False)
				if reportConfig[reportType]["pivot"] is True:
					result = genPivotTable(pd.read_csv(tmpReportFile), "startDate", reportConfig[reportType]["pivotValue"], reportConfig[reportType]["pivotColumns"])
				else:
					# do something here in the non-pivot case
					result = filterTable(pd.read_csv(tmpReportFile))

				outFile = developerId + "_" + reportType + "_" + (startDate.strftime("%Y-%m-%d"))+ "_"+ (endDate.strftime("%Y-%m-%d")) + ".csv"
				result.to_csv(outFile)
				# os.remove(tmpReportFile)
	
	
	
	
	