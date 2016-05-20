import time
import requests
import random
import hashlib
import argparse

__author__="kincy"
 
apikey = "gfhpht2ffsfejd88g7pcnexe"
apisecret = "e7Af9xbEtm"

parser = argparse.ArgumentParser()
parser.add_argument('--target', choices=['proxy6', 'proxy', 'direct'], default='direct')
parser.add_argument('--count', type=int, default=4)
args = parser.parse_args()

def buildApiSignature():
    """This function takes our API key and shared secret and uses it to create the signature that mashery wants """
    authHash = hashlib.sha256();
    #time.time() gets the current time since the epoch (1970) with decimals seconds
    temp = str.encode(apikey + apisecret + repr(int(time.time())))
    authHash.update(temp)
    return authHash.hexdigest()

def buildHeaders():

	# build headers 	
	headers = {'Accept':'application/xml'}
	headers['Api-Key'] = apikey
	headers['X-Signature'] = buildApiSignature()
	headers['Content-Type'] = 'application/xml;charset=UTF-8'
	headers['Host'] = 'api.test.hotelbeds.com'
	return headers
	
if __name__ == "__main__":

	counter = args.count
	success = 0
	total_perf = 0	
	if args.target == 'direct':
		url = direct = "apps.test.hotelbeds.com"
	elif args.target == "proxy6":
		url = "api-hotelbeds-test-j-805013038.eu-west-1.elb.amazonaws.com"
	else:
		url = "api.test.hotelbeds.com"
	
	url = "https://" + url + "/hotel-api/1.0/hotels"
	
	print("target:", url)

	for x in range(1, counter+1):
		xmldata = '<availabilityRQ xmlns="http://www.hotelbeds.com/schemas/messages" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ><stay checkIn="2016-10-19" checkOut="2016-10-21"/><occupancies> <occupancy rooms="1" adults="1" children="0"/></occupancies><destination code="MCO"/><debug><provider>ACE</provider></debug></availabilityRQ>'
		myheaders=buildHeaders()		
		t_start = time.time()
		response = requests.post(url, data=xmldata, headers=myheaders, verify=False)
		perf_time = 0
# 		print (response.request.body)
		if response.status_code == 200:
			success = success + 1
			perf_time = round((time.time() - t_start) * 1000)
			total_perf = total_perf + perf_time
		else:
			print(perf_time = response.text)
		print(x, response.status_code, perf_time)
	avg_response = round(total_perf / success, 2)
	print( args.target + " results:", avg_response)
