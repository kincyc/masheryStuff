import urllib.request
import urllib.parse
import time
import hashlib
import json
import sys 
import pprint
import string
import random
from base64 import b64encode
import logging

__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"

endpoint = "https://api.mashery.com"
path = "/v2/json-rpc/" + str(areaID)

# initialize logging

def buildAuthParams(apiKey, apiSecret):
	authHash = hashlib.md5();
	#time.time() gets the current time since the epoch (1970) with decimals seconds
	temp = str.encode(apiKey] + apiSecret + repr(int(time.time())))
	authHash.update(temp)
	return authHash.hexdigest()

def callAPI(data):
	# convert the dict to a JSON payload
	data = json.dumps(data, ensure_ascii=True) # , sort_keys = True, indent=4)
	data = data.encode('utf-8')
	url = endpoint + path + "?apikey=" + developers['apikey'] + "&sig=" + buildAuthParams() + "&mashery_debug=a3nty5awn3nvr9zresv3eunv"
	logging.debug("URL:\n" + url + "\n")
	req = urllib.request.Request(url, data)
	try:
		response = urllib.request.urlopen(req)
		
	except urllib.error.URLError as e:
		# we have to decode the json object for pretty printing
		# Otherwise, just outputs a byte object that isn't pretty printable
		pprint.pprint(json.loads(data.decode("utf-8")))
		print (e.code)
		print (e.reason)
		print (e.args)
		sys.exit()

	logging.debug(response.headers)
	return response.read()
	
if __name__ == "__main__":

	pageNum = 0
	counter = 0
	with open(datafile, "w") as keyfile:
		while True: 
			pageNum = pageNum + 1
			data = getList("keys", pageNum)
			listing = json.loads(callAPI(data).decode("utf-8"))
			if listing['result']['items'] == []:
				break
			for f in listing['result']['items']:
				counter += 1
				print (counter, f['apikey'])
				result = updateKey(f['id'])
				looging.info(pprint.pprint(result))
				keyfile.write(f['apikey'] + "\n")
				