from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
try:
	import simplejson as json
except ImportError:
	import json
import random
import string
import sys
import time
import pprint
from faker import Faker
import logging
import cgi
import jwt
import manageTokens

PORT_NUMBER = 80
HOST_NAME = "172.30.93.170"
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
	order["bunchOText"] = fake.paragraphs(150)
	
	return order

def mockDeal():
	deal = dict()
	deal['dealId'] = fake.uuid4()
	deal["summary"] = fake.sentence(10, True)
	deal['fullDesc'] = fake.paragraph(5, True)
	deal["price"] = str(random.randint(10,250))
	deal['dateDealEnd'] = str(fake.date_time_this_year())
	deal["bunchOText"] = fake.paragraphs(50)
	return deal

def mockCustomer():
	mockCustomer = fake.profile()
	mockCustomer['shipAddress'] = fake.address()
	mockCustomer['billAddress'] = fake.address()
	mockCustomer['phone'] = fake.phone_number()
	mockCustomer['occupation'] = fake.job()
	del mockCustomer["current_location"]	# this has some wierd decimal format that I didn't feel like figuring out
	mockCustomer["bunchOText"] = fake.paragraphs(50)
	return mockCustomer

def loginPage():
	
	return  """<!DOCTYPE html><html><body
	><form action="/" method="post">
    <div><label for="name">Username:</label><input type="text" id="username" name="user_name" /></div>
    <div><label for="mail">Password:</label><input type="text" id="password" name="user_pass" /></div>
    <div><label for="name">Firstname:</label><input type="text" id="username" name="firstName" /></div>
    <div><label for="mail">Lastname:</label><input type="text" id="password" name="lastName" /></div>
    <div><label for="msg">Secret Data:</label><textarea id="context" name="userContext"></textarea></div>
    <div class="button"><button type="submit">Send your message</button></div>
	</form></body></html>"""

class MyHandler(BaseHTTPRequestHandler):
	
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
	def do_GET(s):
		"""Respond to a GET request."""
		# need to split out the URL parameters
		urlElements = s.path.split("?")
		pathElements = urlElements.split("/")
		print(pathElements)
		
		if pathElements[0] == "/api":
			if pathElements[1] == "/order":
				myResponse = mockOrder(random.randint(1,25))
			elif pathElements[1] == "/deal":
				myResponse = mockDeal()
			elif pathElements[1] == "/customer":
				myResponse = mockCustomer()
			else:
				myResponse = mockDeal()
			output = json.dumps(myResponse, indent=4, sort_keys=True)
			contentType = "application/json"

		elif pathElements[0]== "/login":
			output = loginPage()
			contentType = "text/html"
			
		else:
			output = loginPage()
			contentType = "text/html"
		
		for hdr in s.headers:
			logging.debug(hdr)
		
		s.send_response(200)
		s.send_header("Content-type", contentType)
		s.end_headers()
		s.wfile.write(bytes(output, "utf-8"))

	def do_POST(self):
		# Handle POST requests.
		logging.debug('POST %s' % (self.path))

		# CITATION: http://stackoverflow.com/questions/4233218/python-basehttprequesthandler-post-variables
		ctype, pdict = cgi.parse_header(self.headers['content-type'])
		if ctype == 'multipart/form-data':
			postvars = cgi.parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers['content-length'])
			postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}

		# Print out logging information about the path and args.
		logging.debug('TYPE %s' % (ctype))
		logging.debug('PATH %s' % (self.path))
		logging.debug('ARGS %d' % (len(postvars)))
		
		for hdr in self.headers:
			logging.debug(hdr)
		
		if len(postvars):
			i = 0
			for key in sorted(postvars):
				logging.debug('ARG[%d] %s=%s' % (i, key, postvars[key]))
				i += 1

		logging.debug(postvars[b'userContext'][0].decode("utf-8"))
		userContext = postvars[b'userContext'][0].decode("utf-8")
		firstName = postvars[b'firstName'][0].decode("utf-8")
		lastName = postvars[b'lastName'][0].decode("utf-8")
		
		myJwt = jwt.encode({'userContext': userContext, 'firstName': firstName, 'lastName': lastName}, 'secret', algorithm='HS256')
		
		x = manageTokens.createToken("pkdydc7bcayyp6cd5xmsqfnd", "dygum537t28pgsjqbtsnsnze", "1234567890", myJwt.decode("utf-8"))
		logging.debug(x)

		# Tell the browser everything is okay and that there is
		# HTML to display.
		self.send_response(200)	 # OK
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		# Display the POST variables.
		pageHead = '<html><head><title>Server POST Response</title></head>'
		self.wfile.write(pageHead.encode('utf-8'))
		pageBody = '<body><p>POST variables (%s).</p>' % (str(len(postvars)))
		self.wfile.write(pageBody.encode('utf-8'))

		if len(postvars):
			# Write out the POST variables in 3 columns.
			tblTop ='<table><tbody>'
			self.wfile.write(tblTop.encode('utf-8'))
			i = 0
			for key in sorted(postvars):
				i += 1
				val = postvars[key]
				row = '<tr><td align="right">{0}</td><td align="right">{1}</td><td align="left">{2}</td></tr>'.format( i, key, val)
				self.wfile.write(row.encode('utf-8'))

			tblTop ='</tbody></table>'
			self.wfile.write(tblTop.encode('utf-8'))

		pageBottom = '</body></html>' 
		self.wfile.write(pageBottom.encode('utf-8'))

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
	
	
