# This code will create a package, then create a plan and finally add an endpoint.
# This is written in Python3. Take care to make sure you import the libraries.
# Important - I'm using the Python 3 Requests library.
# I chose this because it is an easy http client that supports different HTTP methods (GET, DELETE, PUT, etc.)
# This code uses Mashery v3 API. 

import pdb
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

# endpoints
tokenPath = "https://api.mashery.com/v3/token"
v3endpoint = "https://api.mashery.com/v3/rest"
uuid = 'ff368e6f-4f41-4d4b-8f9b-10ea76b301f2' 	# trainingarea4
uuid = 'f6516519-bd01-4a5e-9d9a-6d3d7c1885da' 	# macys'

def getOAuthHeaders():

	# create the necessary authorization header	
	userAndPass = b64encode(bytes(developers['apikey'] + ":" + developers['secret'], 'utf-8')).decode("utf-8")
	headers = { 'Authorization' : 'Basic %s' % userAndPass, "Content-Type": "application/x-www-form-urlencoded"}
	
	# pass the creds and the area UUID - NOT THE AREA ID
	data = 'grant_type=password&username=' + developers['username'] + '&password=' + developers['password'] + '&scope=' + uuid
	response = requests.post(tokenPath, data=str(data), headers=headers)
	
	# return the token
	return { 'Authorization' : 'Bearer %s' % response.json()["access_token"], "Content-Type": "application/json" }

def updateEndpoint(serviceId, endpointId, data):
	url = v3endpoint + "/services/" + serviceId + "/endpoints/" + endpointId
	response = requests.put(url, data=json.dumps(data), headers=OAuthheaders)
	return response.json()

def getEndpoints(serviceId):
	url = v3endpoint + "/services/" + serviceId + "/endpoints"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getEndpoint(serviceId, endpointId):
	url = v3endpoint + "/services/" + serviceId + "/endpoints/" + endpointId + "?fields=id,inboundSslRequired,jsonpCallbackParameter,jsonpCallbackParameterValue,scheduledMaintenanceEvent,forwardedHeaders,returnedHeaders,name,numberOfHttpRedirectsToFollow,outboundRequestTargetPath,outboundRequestTargetQueryParameters,outboundTransportProtocol,processor,publicDomains,requestAuthenticationType,requestPathAlias,requestProtocol,oauthGrantTypes,supportedHttpMethods,systemDomainAuthentication,systemDomains,trafficManagerDomain,updated,useSystemDomainCredentials,systemDomainCredentialKey,systemDomainCredentialSecret,methods,methods.id,methods.name,methods.sampleXmlResponse,methods.sampleJsonResponse,strictSecurity,highSecurity,apiKeyValueLocations,apiKeyValueLocationKey,allowMissingApiKey,hostPassthroughIncludedInBackendCallHeader"
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getService(serviceId):
	url = v3endpoint + "/services/" + serviceId
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getPackage(packageId):
	url = v3endpoint + "/packages/" + packageId
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getPackages():
	url = v3endpoint + "/packages" 
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getPlan(packageId, planId):
	url = v3endpoint + "/packages/" + packageId + "/plans/" + planId
	response = requests.get(url, headers=OAuthheaders)
	return response.json()

def getPlans(packageId):
	url = v3endpoint + "/packages/" + packageId + "/plans"
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
	
	packageObject = getPackage(args.package)
	planObject = getPlan(args.package, args.plan)
	
	print("\n")
	print("pkg\t" + packageObject['name'])
	print("plan\t\t" + planObject['name'])
	
	
	for service in response.json():
		if bService ==1:
			print("svc\t\t\t" + service["name"]) 
		url = v3endpoint + "/packages/" + packageId + "/plans/" + planId + "/services/" + service["id"] + "/endpoints"
		response = requests.get(url, headers=OAuthheaders)
		for endpoint in response.json():
			print("\t\t\t\t" + endpoint["name"])

def createPackage(packageName):
	url = v3endpoint + "/packages"
	myPackage = {}
	myPackage["name"] = "deleteme"
	myPackage["description"] = "gravida nisi sollicitudin vitae consectetuer eget rutrum at lorem integer"
	response = requests.post(url, data=json.dumps(myPackage), headers=OAuthheaders)
	return response

def deletePackage(objectId):
	url = v3endpoint + "/packages/" + objectId
	response = requests.delete(url, headers=OAuthheaders)
	if response.content == b'':		
		return("OK")
	else:
		return response.json()

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

	OAuthheaders = getOAuthHeaders()
	
	# createPackage("deleteme")
	
	for package in getPackages():
		for plan in getPlans(package["id"]):
			pprint.pprint(plan)
