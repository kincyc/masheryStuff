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
# doing this for demo purposes.
# expected format is:
# { "dev1": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" }, 
# "dev2": { "username": "dev1", "password": "secret", "apiKey": "key", "sharedSecret": "secret" } }

# i'm manually setting the developer name here 
developers = json.load(open('developers.json'))['kincy']

# you can uncomment this code if you want to get http logging messages.
# This is useful if there is a proxy or something else getting in the way of your HTTP calls
# The logging output will come out as STDERR

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


# command line arguments

# --addplan "name"
# --addpackage "name"
# --addendpoint "name"
# --addservice "name"
# --showall - shows all packages and plans
# --showpackage "name" - shows the contents of a particular package
# --showplan "name" - shows the contents of a particular plan

# --area uuid of area
# --developer filename with developer info
# --copytoarea copies what has been shown to a particular area uuid


# endpoints
tokenPath = "https://api.mashery.com/v3/token"
v3endpoint = "https://api.mashery.com/v3/rest"
uuid = 'ff368e6f-4f41-4d4b-8f9b-10ea76b301f2'

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

def createEndpoint(serviceId, endpointName, data):
	url = v3endpoint + "/services/" + serviceId + "/endpoints"
	# data = {"name" : endpointName, "description" : "blah blah blah " }
	# pathAlias = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
	# data["requestPathAlias"] = "v1/foo/" + pathAlias
	# data["trafficManagerDomain"] = "api.intel.com"
	data["requestPathAlias"] = data["requestPathAlias"] + "_1"
	response = requests.post(url, data=json.dumps(data), headers=OAuthheaders)
	return response.json()
	
def updateEndpoint(serviceId, endpointId, data):
	url = v3endpoint + "/services/" + serviceId + "/endpoints/" + endpointId
	response = requests.put(url, data=json.dumps(data), headers=OAuthheaders)
	return response.json()


def getEndpoint(serviceId, endpointId):
	url = v3endpoint + "/services/" + serviceId + "/endpoints/" + endpointId + "?fields=inboundSslRequired,jsonpCallbackParameter,jsonpCallbackParameterValue,scheduledMaintenanceEvent,forwardedHeaders,returnedHeaders,name,numberOfHttpRedirectsToFollow,outboundRequestTargetPath,outboundRequestTargetQueryParameters,outboundTransportProtocol,processor,publicDomains,requestAuthenticationType,requestPathAlias,requestProtocol,oauthGrantTypes,supportedHttpMethods,systemDomainAuthentication,systemDomains,trafficManagerDomain,updated,useSystemDomainCredentials,systemDomainCredentialKey,systemDomainCredentialSecret,methods,methods.id,methods.name,methods.sampleXmlResponse,methods.sampleJsonResponse,strictSecurity,highSecurity,apiKeyValueLocations,apiKeyValueLocationKey,allowMissingApiKey,hostPassthroughIncludedInBackendCallHeader"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getEndpoints(serviceId):
	url = v3endpoint + "/services/" + serviceId + "/endpoints"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()


def getService(serviceId):
	url = v3endpoint + "/services/" + serviceId
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

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
	endpoints = getEndpoints("pkdydc7bcayyp6cd5xmsqfnd")
	pprint.pprint(endpoints)
	
	for e in endpoints:
		# pprint.pprint(e)
		endpoint_obj = getEndpoint("pkdydc7bcayyp6cd5xmsqfnd", e["id"])
		pprint.pprint(endpoint_obj)
		# newRequestPathAlias = endpoint_obj["requestPathAlias"].replace("_1", "")
		# data = {"requestPathAlias" : newRequestPathAlias}
		# pprint.pprint(updateEndpoint("h7s6ckwndmjqj5aj2va84m6f", e["id"], data))
		
		# x = createEndpoint("h7s6ckwndmjqj5aj2va84m6f", e["name"], endpoint_obj)
		# pprint.pprint(x)
	
	
	# createEndpoint("66vy32fesybp39arksujauqv", me.name)
	
	
# 	OPEN CSV FILE and convert it into a list of lists	
# 	with open('it_portfolio.csv') as csvfile:
# 		service_listing = csv.DictReader(csvfile)
# # 		packagePlan = [[row['Segment'],row['Portfolio'], row['Service'].splitlines()[0]]  for row in servic  Segment Owner: e_listing]
# 		for row in service_listing:
# 			print(row['Segment'])
		
# 	serviceObject = createService("API Definition " + str(time.time()))
# 	newEndpointName = "Endpoint " + str(time.time())
# 	endpointObject = createEndpoint(serviceObject["id"], newEndpointName)
#	pprint.pprint(getService("h2ua6yy8mysh76gzypht7kuw"))
# 	addServiceToPlan(packageId, planId, serviceObject)
# 	addEndpointToPlan(packageId, planId, serviceObject["id"], endpointObject)
# 	showPlanContents(packageId, planId, serviceObject["id"]) 
	
#	showAllPackagesPlans()
# 	deleteAllPlans()



