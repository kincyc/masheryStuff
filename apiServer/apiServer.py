from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
from faker import Faker
import socketserver
import random
import string
import sys
import time
import pprint
import logging
import cgi
import jwt

sys.path.append('/Users/kincy/Projects/masheryStuff')
import manageTokens
import argparse
try:
	import simplejson as json
except ImportError:
	import json


developers = json.load(open('developers.json'))['kincy']

parser = argparse.ArgumentParser()
parser.add_argument("--hostname", type=str, default="127.0.0.1", help="hostname to be served")
parser.add_argument("-p", "--port", type=int, default="80", help="listening port")
args = parser.parse_args()

PORT_NUMBER = args.port
HOST_NAME = args.hostname

fake = Faker()

_item = """helmet,greeting card,sharpie,clothes,pool stick,street lights,
	camera,flowers,tweezers,sun glasses,tomato,radio,canvas,newspaper,keys,
	headphones,sponge,mp3 player,clock,buckle,bottle,screw,USB drive,scotch tape,
	tv,face wash,window,broccoli,truck,hanger,charger,cookie jar,table,food,
	zipper,lamp shade,chocolate,cup,phone,tissue box,video games,lotion,pillow,
	lace,slipper,chapter book,credit card,glasses,shirt,rubber duck""".split(",")

def mockOrder(numItems):
	order = dict()
	order['address'] = fake.address()
	order['custName'] = fake.name()
	order['shippingCost'] = random.randint(50,100)
	order['email'] = fake.safe_email()
	order['orderDate'] = str(fake.date_time_this_year())
	order['orderId'] = fake.uuid4()

	items = []
	for x in range(0,numItems):
		item = dict()
		item["item"] = random.choice(_item)
		item["summary"] = fake.sentence(10, True)
		item["itemId"] = fake.uuid4()
		item["price"] = str(random.randint(10,250))
		items.append(item)
	order['items'] = items	
	order["bunchOText"] = fake.paragraphs(1)
	
	return order

def mockDeal():
	deal = dict()
	deal['dealId'] = fake.uuid4()
	deal["summary"] = fake.sentence(10, True)
	deal['fullDesc'] = fake.paragraph(5, True)
	deal["price"] = str(random.randint(10,250))
	deal['dateDealEnd'] = str(fake.date_time_this_year())
	deal["bunchOText"] = fake.paragraphs(1)
	return deal

def mockCustomer():
	mockCustomer = fake.profile()
	mockCustomer['shipAddress'] = fake.address()
	mockCustomer['billAddress'] = fake.address()
	mockCustomer['phone'] = fake.phone_number()
	mockCustomer['occupation'] = fake.job()
	del mockCustomer["current_location"]	# this has some wierd decimal format that I didn't feel like figuring out
	mockCustomer["bunchOText"] = fake.paragraphs(1)
	return mockCustomer

def serveLocalPage(path):
		
	if path.endswith(".jpg"):
		mimetype='image/jpg'
		sendReply = True
	elif path.endswith(".gif"):
		mimetype='image/gif'
		sendReply = True
	elif path.endswith(".js"):
		mimetype='application/javascript'
		sendReply = True
	elif path.endswith(".css"):
		mimetype='text/css'
		sendReply = True
	else:
		mimetype='text/html'
		sendReply = True

	try:
		logging.debug(curdir + sep + path)
		f = open(curdir + sep + path) 
		output = f.read()
		f.close()
		return (output, mimetype)

	except IOError:
		
		return ("error", "text/html")

def serveAPI(api):
		
	if api == "order":
		myResponse = mockOrder(random.randint(1,25))
	elif api == "deal":
		myResponse = mockDeal()
	elif api == "customer":
		myResponse = mockCustomer()
	else:
		myResponse = mockDeal()
	
	output = json.dumps(myResponse, indent=4, sort_keys=True)
	contentType = "application/json"
	return (output, contentType)

class MyHandler(BaseHTTPRequestHandler):
	
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
	

	def do_GET(s):
		"""Respond to a GET request."""
		# need to split out the URL parameters
		logging.debug(s.headers)
		
		if 'X-Mashery-Oauth-User-Context' in s.headers:
			logging.debug(s.headers.get('X-Mashery-Oauth-User-Context'))
			logging.debug(jwt.decode(s.headers.get('X-Mashery-Oauth-User-Context'), 'secret', algorithm='HS256'))
		
		urlElements = s.path.split("?")
		pathElements = urlElements[0].split("/")
		print(pathElements)
		
		if pathElements[1] == "api":
			output, contentType = serveAPI(pathElements[2])
		else:
			output, contentType = serveLocalPage(s.path) 

		if output == "error":
			s.send_error(404,'File Not Found: %s' % s.path)

		s.send_response(200)
		s.send_header("Content-type", contentType)
		s.end_headers()
		s.wfile.write(bytes(output, "utf-8"))

	def do_POST(s):
		logging.debug(s.headers)
		# Handle POST requests.
		logging.debug('POST %s' % (s.path))

		# CITATION: http://stackoverflow.com/questions/4233218/python-basehttprequesthandler-post-variables
		ctype, pdict = cgi.parse_header(s.headers['content-type'])
		if ctype == 'multipart/form-data':
			postvars = cgi.parse_multipart(s.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(s.headers['content-length'])
			postvars = cgi.parse_qs(s.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}

		# Print out logging information about the path and args.
		logging.debug('TYPE %s' % (ctype))
		logging.debug('PATH %s' % (s.path))
		logging.debug('ARGS %d' % (len(postvars)))
		
		if len(postvars):
			i = 0
			for key in sorted(postvars):
				logging.debug('ARG[%d] %s=%s' % (i, key, postvars[key]))
				i += 1

		logging.debug(postvars[b'secretData'][0].decode("utf-8"))
		userContext = postvars[b'userContext'][0].decode("utf-8")
		firstName = postvars[b'firstName'][0].decode("utf-8")
		lastName = postvars[b'lastName'][0].decode("utf-8")
		
		myJwt = jwt.encode({'secretData': secretData, 'firstName': firstName, 'lastName': lastName}, 'secret', algorithm='HS256')
		
		x = manageTokens.createToken(developers['apikey'], developers['secret'], "g29353wbtdrxtxd4g3373ekv", "xk5nmy7gvtsjkp437mqn9dyr", "1234567890", myJwt.decode("utf-8"))
		logging.debug(x)		
		# this is very brittle, does not handle an error case
		authToken = x['result']['access_token']

		# Tell the browser everything is okay and that there is HTML to display.
		s.send_response(200)	 # OK
		s.send_header('Content-type', 'text/html')
		s.end_headers()

		# Display the POST variables.
		pageHead = '<html><head><title>Server POST Response</title></head>'
		s.wfile.write(pageHead.encode('utf-8'))
		pageBody = '<body><p>POST variables (%s).</p>' % (str(len(postvars)))
		s.wfile.write(pageBody.encode('utf-8'))

		if len(postvars):
			# Write out the POST variables in 3 columns.
			tblTop ='<table><tbody>'
			s.wfile.write(tblTop.encode('utf-8'))
			i = 0
			for key in sorted(postvars):
				i += 1
				val = postvars[key]
				row = '<tr><td align="right">{0}</td><td align="left">{1}</td><td align="left">{2}</td></tr>'.format(i, key, val)
				s.wfile.write(row.encode('utf-8'))

			row = '<tr><td align="right">{0}</td><td align="left">AuthToken</td><td align="left">{1}</td></tr>'.format(i, authToken)
			s.wfile.write(row.encode('utf-8'))
			tblTop ='</tbody></table>'
			s.wfile.write(tblTop.encode('utf-8'))

		pageBottom = '</body></html>' 
		s.wfile.write(pageBottom.encode('utf-8'))


if __name__ == '__main__':

	logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)

	server_class = HTTPServer
	httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
	print (time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print (time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
 