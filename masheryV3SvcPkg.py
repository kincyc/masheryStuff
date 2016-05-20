# This code will create a package, then create a plan and finally add an endpoint.
# This is written in Python3. Take care to make sure you import the libraries.
# Important - I'm using the Python 3 Requests library.
# I chose this because it is an easy http client that supports different HTTP methods (GET, DELETE, PUT, etc.)
# This code uses Mashery v3 API. 

import time
import hashlib
import pprint
import random
import requests
import logging
import json
import string
from base64 import b64encode
import csv
import http.client # need to be explicit for logging

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"

# load developer username, password and apikey / secret from text file.

developers = json.load(open('developers.json'))['kincy']

# endpoints
tokenPath = "https://api.mashery.com/v3/token"
v3endpoint = "https://api.mashery.com/v3/rest"
uuid = 'ff368e6f-4f41-4d4b-8f9b-10ea76b301f2' 	# training area four

def getOAuthHeaders():

	# create the necessary authorization header	
	userAndPass = b64encode(bytes(developers['apikey'] + ":" + developers['secret'], 'utf-8')).decode("utf-8")
	headers = { 'Authorization' : 'Basic %s' % userAndPass, "Content-Type": "application/x-www-form-urlencoded"}
	
	# pass the creds and the area UUID - NOT THE AREA ID
	data = 'grant_type=password&username=' + developers['username'] + '&password=' + developers['password'] + '&scope=' + uuid
	response = requests.post(tokenPath, data=str(data), headers=headers)
	
	# return the token
	return { 'Authorization' : 'Bearer %s' % response.json()["access_token"], "Content-Type": "application/json" }

# 	this function creates a service.
# 
def createService(service_name):
	url = v3endpoint + "/services"
	data = {"name" : service_name, "description" : "blah blah blah "}
	response = requests.post(url, data=json.dumps(data), headers=OAuthheaders)
	return response.json()

def createEndpoint(serviceId, endpointName):
	url = v3endpoint + "/services/" + serviceId + "/endpoints"
	data = {"name" : endpointName, "description" : "blah blah blah " }
	pathAlias = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
	data["requestPathAlias"] = "v1/foo/" + pathAlias
	data["trafficManagerDomain"] = "api.intel.com"
	response = requests.post(url, data=json.dumps(data), headers=OAuthheaders)
	return response.json()

def listServices():
	url = v3endpoint + "/services"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getEndpoint(serviceId, endpointId):
	url = v3endpoint + "/services/" + serviceId + "/endpoint/" + endpointId
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getService(serviceId):
	url = v3endpoint + "/services/" + serviceId
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def deleteService(serviceId):
	url = v3endpoint + "/services/" + serviceId
	response = requests.delete(url, headers=OAuthheaders)
	return response

def addServiceToPlan(packageId, planId, serviceObject):
	url = v3endpoint + "/packages/" + packageId + "/plans/" + planId + "/services"
	response = requests.post(url, data=json.dumps(serviceObject), headers=OAuthheaders)
	return response.json()

def addEndpointToPlan(packageId, planId, serviceId, endpointObject):
	url = v3endpoint + "/packages/" + packageId + "/plans/" + planId + "/services/" + serviceId + "/endpoints"
	response = requests.post(url, data=json.dumps(endpointObject), headers=OAuthheaders)
	return response.json()

def showPlanContents(packageId, planId, bService = 1):
	# bService is a flag to show service definitions (or not)
	url = v3endpoint + "/packages/" + packageId + "/plans/" + planId + "/services"
	response = requests.get(url, headers=OAuthheaders)
	for service in response.json():
		if bService ==1:
			print("\t\t\t" + service["name"]) 
		url = v3endpoint + "/packages/" + packageId + "/plans/" + planId + "/services/" + service["id"] + "/endpoints"
		response = requests.get(url, headers=OAuthheaders)
		for endpoint in response.json():
			print("\t\t\t\t" + endpoint["name"])

def deleteAllPlans():
	url = v3endpoint + "/packages"
	response = requests.get(url, headers=OAuthheaders)
	for definition in response.json():
		if definition["name"][0:4].lower() == "api ":
			print ("DELETE: %s" % definition["id"])
			r = requests.delete(url + "/" + definition["id"], headers=OAuthheaders)

def showAllPackagesPlans():
	print ("PLANS AND PACKAGES")
	url = v3endpoint + "/members"
	response = requests.get(url, headers=OAuthheaders)
	for package in response.json():
		# print("\r\n%s:%s" % (package["name"], package["id"]))
		# 		url = "%s/packages/%s/plans" % (v3endpoint, package["id"])
		# 		response = requests.get(url, headers=OAuthheaders)
		# 		print("\t%s:%s" % (package["name"], package["id"]))
		# 		for plan in response.json():
		# 			print("\t\t%s:%s" % (plan["name"], plan["id"]))
		# 			showPlanContents(package["id"], plan["id"], 0)
		print(package)
			
def getFillerText():
	
	url = "http://baconipsum.com/api/?type=meat-and-filler&paras=1&start-with-lorem=1"
	response = requests.get(url)
	return response.json()[0]
	

if __name__ == "__main__":
	global OAuthheaders

	# print (getFillerText())
	OAuthheaders = getOAuthHeaders()
	services = listServices()
	for myService in services:
		deleteme = input('should I remove %s from %s? ' % (myService['name'], uuid))
		if deleteme == 'y':
			print ("DELETE: %s" % myService["id"])
			resp = deleteService(myService['id'])
	
# 	OPEN CSV FILE and convert it into a list of lists	
# 	with open('it_portfolio.csv') as csvfile:
# 		service_listing = csv.DictReader(csvfile)
# # 		packagePlan = [[row['Segment'],row['Portfolio'], row['Service'].splitlines()[0]]  for row in servic  Segment Owner: e_listing]
# 		for row in service_listing:
# 			print(row['Segment'])
		
