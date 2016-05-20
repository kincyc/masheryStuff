import time
import requests
import random


__author__="kincy"
__date__ ="$Jan 11, 2011 10:18:04 AM$"
 
users = ['jbdyujrhsay8gke63km7rz4g', 'evdpup597cme478qc2dvswwq', '8phycmczfgxhjw4pqty9s3ed', 'cheryl']
paths = ['baseball', 'standard', 'bacon']

def buildAuthParams():
    authHash = hashlib.md5();
    #time.time() gets the current time since the epoch (1970) with decimals seconds
    temp = str.encode(developers['apikey'] + developers['secret'] + repr(int(time.time())))
    authHash.update(temp)
    return authHash.hexdigest()

if __name__ == "__main__":

	for x in range(0, 10000):
		url = "http://api.kincy.com/ipsum/" + random.choice(paths) + "?api_key=" + random.choice(users)
		response = requests.get(url)
		print(url)
		print(response.text[0:30])
		delay = abs(round(random.paretovariate(1) / 2) - 1)
		if delay > 15: delay = 15
		print(delay)
		time.sleep(delay)
		
