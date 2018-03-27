import unittest
import csv
import requests
from requests_oauthlib import OAuth1
import json
import time
from datetime import datetime
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from threading import Thread
import mimetypes

class CsvParser():
	def parseFile(self, vf):
		reader = csv.DictReader(open(vf, 'rb'))
		dict_list = {}
		for line in reader:
			dict_list[line["word"].lower()] = int(line["value"])
		return dict_list

class TweetParser():
	tweets = []
	dictionary = {}
	def __init__(self, t, d):
		self.tweets = t
		self.dictionary = d
	def assertValueToTweets(self):
		result = []
		i = 0
		for tweet in self.tweets:
			result.append(0);
			for word in tweet.split():
				for key, value in self.dictionary.items():
					if(word == key):
						#print "	key ", key
						#print "	value ", value
						result[i] += value
			i+=1

		return result


class TweetScraper():
	url = "https://api.twitter.com/1.1/search/tweets.json?q={}&result_type=mixed"

	cid = "G5d723AqGuasGX09SemgP4lrI"
	secret = "UvRlIY0ChIDRAO8pqhYMVnuVlcyWxPQPaSyko4ZAm159wgvC5V"
	at = "1264777160-Qr8ZfD4xIWlKrBqocVnBK8oRp8CoUJTcLu8BqSO"
	ats = "ZIuakrJ7A6pAGdX0w0q6a7Uz9zt8QXvfPTwTIyKtvxDbG"

	def getTweets(self, hashtag):
		auth = OAuth1(self.cid, self.secret, self.at, self.ats)
		r = requests.get(self.url.format(hashtag), auth=auth)
		# add error code and maybe a try catch
		result = []
		texts = r.json()["statuses"]
		for t in texts:
			result.append( t["text"].lower() )
		return result

class CsvDataSaver():	
	def __init__(self, vf):
		self.vf = vf

	def saveData(self, data):
		with open(self.vf, 'a') as csvfile:
			writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
			dt = datetime.now()
			writer.writerow([dt, str(data)])


###########################################################################
###########################################################################
###########################################################################
###########################################################################

class TemplateInflater():
	template = ""
	inflatedTemplate = ""
	filename = ""
	def __init__(self, filename):
		self.filename = filename	
		self.refresh()
	def refresh(self):
		with open(self.filename, 'r') as f:
			self.template = f.read()
	def inflate(self, argument):
		inflatedTemplate = self.template
		for i, j in argument.items():
			inflatedTemplate = inflatedTemplate.replace(i, j)
			self.inflatedTemplate = inflatedTemplate
		return inflatedTemplate
	def getInflatedTemplate(self):
		return self.inflatedTemplate

class S(BaseHTTPRequestHandler):

	def _set_headers_for(self, t, r = 200, mtype = False):
		self.send_response(r)
		if(t == False and mtype != False):
			self.send_header('Content-type', mtype)
		elif(t.upper() == "JSON"):
			self.send_header('Content-type', 'application/json')
		elif(t.upper() == "HTML"):
			self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		if(self.path == "/"):
			global slashCounter
			slashCounter = slashCounter + 1
			self._set_headers_for("html")
			templateInflater.refresh()
			self.wfile.write(templateInflater.getInflatedTemplate())
		elif(self.path == "/update"):
			self._set_headers_for("json")
			self.wfile.write("{\"sum\" : %d }" % lastSum)
		else:
			try:
				f = open("."+self.path, "r")
				mt = mimetypes.guess_type("."+self.path)[0]
				print mt
				self._set_headers_for(False, mtype = mt)
				self.wfile.write(f.read())
			except IOError:
				self._set_headers_for("text/html", 404)

			

	def do_HEAD(self):
		self._set_headers_for()
        
	def do_POST(self):
		self._set_headers_for("JSON")
		self.wfile.write("{\"response\":\"OK\"}")
        
def runServer(port=8081, server_class=HTTPServer, handler_class=S):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()




###########################################################################
###########################################################################
###########################################################################
###########################################################################



class SeparateClassTests(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()
	def tearDown(self):
		t = time.time() - self.startTime
		print "%s: %.3f" % (self.id(), t)

	test_tweets = ["Meet our new adviser @icokingmaker Nathan Christian! Nathan is a technical expert in Blockchain-based accounting and rise rise financial applications. He is deeply entrenched in the blockchain space and has made it both his career fall and life passion.  Let's all welcome him!   #AMON #Crypto ", "Meet our new adviser @icokingmaker Nathan Christian! Nathan is a technical expert in Blockchain-based accounting and fall fall financial applications. He is deeply entrenched in the blockchain space and has made it both his career fall and life passion.  Let's all welcome him!   #AMON #Crypto " ]
	test_dictionary = {"fall": -5, "rise": 5} # 5 -15


	def testTweetParser(self):
		t = TweetParser(self.test_tweets, self.test_dictionary)
		self.assertEqual(t.assertValueToTweets() , [5,-15])

	def testTweetScraper(self):
		t = TweetScraper()
		self.assertIsInstance(t.getTweets("bitcoin") , list)

	def testCsvParser(self):
		csvParser = CsvParser();
		self.assertIsInstance(csvParser.parseFile("data.csv") , dict)
	def testWholeApp(self):
		scr = TweetScraper()
		cps = CsvParser()
		t = TweetParser(scr.getTweets("bitcoin"), cps.parseFile("testdata.csv"))
		res = t.assertValueToTweets()
		d = CsvDataSaver("testoutput.csv")
		global lastSum 
		lastSum = sum(res)
		d.saveData(sum(res))
		self.assertIsInstance(res, list)


class APITest(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()
	def tearDown(self):
		t = time.time() - self.startTime
		print "%s: %.3f" % (self.id(), t)
	def testTemplateInflater(self):
		templateInflater = TemplateInflater("template.html")
		data = templateInflater.inflate({"{toBeReplaced}" : "forThat", "{somethingDifferent}" : "8"})
		print data
		self.assertGreater(len(data), 5)
		pass
	def testGETRequestOnSlash(self):
		testport = 8090
		global templateInflater
		global lastSum
		lastSum = 5
		templateInflater = TemplateInflater("template.html")
		templateInflater.inflate({"{toBeReplaced}" : "forThat", "{somethingDifferent}" : "8"})
		templateInflater.refresh()
		serverThread = Thread(target = runServer, args = (testport, ))
		serverThread.start()
		try:
			time.sleep(1)
			response = requests.get("http://localhost:%d/" % testport)
			responseText = response.text
		except:
			responseText = "FAIL!"

		self.assertEqual(templateInflater.inflatedTemplate ,responseText)
	def testGETRequestOnUpdate(self):
		print "PAS?"
		pass
	# Basic Template: read file -> format with parameters -> output !!! done <3
	#  GET request: on "/" -> put data into template -> output
	#  GET request: on "/update" -> respond with JSON with new data 





###########################################################################
###########################################################################
###########################################################################
###########################################################################



if __name__ == '__main__':
	#unittest.main()
	global templateInflater
	global lastSum
	lastSum = 5
	testport = 8091
	global slashCounter
	slashCounter = 0
	templateInflater = TemplateInflater("template.html")

	dateStart = datetime.now().date()


	templateInflater.inflate({"{toBeReplaced}" : str(slashCounter)  ,"{totalCommits}" : "4" , "{totalContributors}" : "1" ,"{dateStart}" : str(dateStart)})
	templateInflater.refresh()
	serverThread = Thread(target = runServer, args = (testport, ))
	serverThread.start()
	while(True):
		if(time.time() % 5 == 0):
			scr = TweetScraper()
			cps = CsvParser()
			t = TweetParser(scr.getTweets("bitcoin"), cps.parseFile("data.csv"))
			res = t.assertValueToTweets()
			d = CsvDataSaver("output.csv")
			lastSum = sum(res)
			d.saveData(sum(res))
		if(time.time() % 10 == 0):
			templateInflater.refresh()
