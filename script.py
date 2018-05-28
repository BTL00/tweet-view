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
from sklearn import tree
from sklearn.neural_network import MLPClassifier
import re
import cgi
from sklearn.externals import joblib


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
			tweet = re.sub(r"[^a-zA-Z0-9]+", ' ', tweet)
			for span in range(tweet.count(' '), 1, -1):
				words = tweet.split(" ")
				for word in ([" ".join(words[i:i+span]) for n in range(0, len(words), span)]):
					for key, value in self.dictionary.items():
						if(word == key):
							tweet.replace(word, " ")
							result[i] += value
			for word in tweet.split():
				for key, value in self.dictionary.items():
					if(word == key):
						result[i] += value

			i+=1

		return result

class DataPredictor:
	clf = 0;
	def predict(self):
		reader = csv.DictReader(open("output.csv", 'rb'))
		ldt = []
		for line in reader:
			 ldt.append(int(line["close"]))
		#print ldt
		if(self.clf == 0):
			self.loadClassifier()
		pred = self.clf.predict([[ldt[-5], ldt[-4], ldt[-3], ldt[-2], ldt[-1] ]])
		return pred
	
	def loadClassifier(self):
		global classifierType
		if(not classifierType):
			classifierType="mlpc"
		self.clf = joblib.load(classifierType+'.clsf') 	

	def learn(self):
		startTime  = time.time() 
		global keyword
		reader = csv.DictReader(open("output.csv", 'rb'))
		ldt = []
		for line in reader:
			 ldt.append(int(line["close"]))
		features = []
		labels = []
		for d in range(0, len(ldt)-6, 1):
			features.append([  ldt[d] , ldt[d+1] , ldt[d+2], ldt[d+3], ldt[d+4]    ])
			labels.append(ldt[d+5])
		global classifierType
		if (classifierType == "mlpc"):
			print "Using MLPC"
			self.clf =  MLPClassifier(solver='lbfgs', alpha=1e-5,
                    hidden_layer_sizes=(5, 3), random_state=1)
			#Note: The default solver adam works pretty well on relatively large datasets (with thousands of training samples or more) in terms of both training time and validation score. For small datasets, however, lbfgs can converge faster and perform better.
			self.clf = self.clf.fit(features, labels)
			joblib.dump(self.clf, 'mlpc.clsf') 

		elif(classifierType == "tree"):
			print "Using Tree"
			self.clf =  tree.DecisionTreeClassifier()
			self.clf = self.clf.fit(features, labels)
			joblib.dump(self.clf, 'tree.clsf') 


		t = time.time() - startTime
		print "%s: %.3f" % ("DataPredictor learn:", t)




class TweetScraper():

	url = "https://api.twitter.com/1.1/search/tweets.json?q={}&result_type=mixed"

	### REMOVE WHILE COMMITING!

	### REMOVE WHILE COMMITING!

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
			writer = csv.writer(csvfile, delimiter=',',
							quotechar='', quoting=csv.QUOTE_NONE)
			dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			writer.writerow([dt, str(data)])
		with open("output.csv", 'a') as csvfile:
			writer = csv.writer(csvfile, delimiter=',',
							quotechar='', quoting=csv.QUOTE_NONE)
			dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			writer.writerow([dt, str(data)])


###########################################################################


class GitStatsScraper():
	def __init__(self):
		self.path = 'https://api.github.com/repos/BTL00/tweet-view/contributors'
	def getCommits(self):
		return 5
	def getContributors(self):
		return 1


###########################################################################

class TemplateInflater():
	template = ""
	inflatedTemplate = ""
	filename = ""
	def __init__(self, filename, args):
		self.filename = filename	
		self.refresh(args)

	def refresh(self,args):
		with open(self.filename, 'r') as f:
			self.template = f.read()
			self.inflate(args)
		print "Template refreshed"

	def inflate(self, argument):
		inflatedTemplate = self.template
		argument = self.addSpecial(argument)
		
		for i, j in argument.items():
			inflatedTemplate = inflatedTemplate.replace(i, j)
			self.inflatedTemplate = inflatedTemplate
		return inflatedTemplate


	def addSpecial(self, argument):
		global slashCounter
		global apiCounter
		global hashtag
		global classifierType
		gitStatsScraper = GitStatsScraper()
		argument['{requestsHandledHome}'] =  str( slashCounter ) 
		argument['{requestsHandledAPI}'] =  str( apiCounter ) 
		argument['{dateStart}'] = str(datetime.now()).split(".")[0] 
		argument['{totalCommits}'] = str(gitStatsScraper.getCommits())
		argument['{totalContributors}'] = str(gitStatsScraper.getContributors())
		argument['{keyword}'] = str(hashtag)

		if(classifierType == "mlpc"):
			argument['{mlpSelected}'] = "selected"
			argument['{treeSelected}'] = ""

		if(classifierType == "tree"):
			argument['{mlpSelected}'] = ""
			argument['{treeSelected}'] = "selected"

		if(hashtag == "bitcoin"):
			argument['{bitcoinSelected}'] = "selected"
			argument['{moneroSelected}'] = ""
			argument['{musicSelected}'] = ""

		if(hashtag == "monero"):
			argument['{bitcoinSelected}'] = ""
			argument['{moneroSelected}'] = "selected"
			argument['{musicSelected}'] = ""

		if(hashtag == "music"):
			argument['{bitcoinSelected}'] = ""
			argument['{moneroSelected}'] = ""
			argument['{musicSelected}'] = "selected"
			

		return argument


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
		global apiCounter
		global slashCounter
		global predict
		
		if(self.path == "/"):
			slashCounter = slashCounter + 1
			self._set_headers_for("html")
			self.wfile.write(templateInflater.getInflatedTemplate())
		elif(self.path == "/update"):
			apiCounter = apiCounter + 1
			self._set_headers_for("json")
			self.wfile.write("{\"sum\" : %d }" % lastSum)
		elif(self.path == "/tweets"):
			apiCounter = apiCounter + 1
			self._set_headers_for("json")
			self.wfile.write("{\"tweets\" : %s }" % "Some tweets \n Some tweet-view")	
		elif(self.path == "/predict"):
			apiCounter = apiCounter + 1
			self._set_headers_for("json")
			self.wfile.write("{\"predict\" : %d }" % predict)	
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
		global apiCounter
		global slashCounter
		global predict
		global classifierType
		global databaseType
		global hashtag
		

		apiCounter = apiCounter + 1


		if(self.path == "/"):
		
			slashCounter = slashCounter + 1

			form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD': 'POST'}
			)
			hashtag = form.getvalue("keyword")
			classifierType = form.getvalue("classifier")
			databaseType = form.getvalue("database")

			d = CsvDataSaver(hashtag+".csv")
			templateInflater.refresh({})

			self._set_headers_for("html")
			self.wfile.write(templateInflater.getInflatedTemplate())

		else:
			self._set_headers_for("JSON")
			self.wfile.write("{\"response\":\"OK\"}")
		
def runServer(port=8082, server_class=HTTPServer, handler_class=S):
	global dateStart
	dateStart = datetime.now()
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()




###########################################################################
###########################################################################
###########################################################################
###########################################################################



# class SeparateClassTests(unittest.TestCase):
# 	def setUp(self):
# 		self.startTime 
# 	def tearDown(self):
# 		t = time.time() - self.startTime
# 		print "%s: %.3f" % (self.id(), t)

# 	test_tweets = ["Meet our new adviser @icokingmaker Nathan Christian! Nathan is a technical expert in Blockchain-based accounting and rise rise financial applications. He is deeply entrenched in the blockchain space and has made it both his career fall and life passion.  Let's all welcome him!   #AMON #Crypto ", "Meet our new adviser @icokingmaker Nathan Christian! Nathan is a technical expert in Blockchain-based accounting and fall fall financial applications. He is deeply entrenched in the blockchain space and has made it both his career fall and life passion.  Let's all welcome him!   #AMON #Crypto " ]
# 	test_dictionary = {"fall": -5, "rise": 5} # 5 -15


	# def testTweetParser(self):
	# 	t = TweetParser(self.test_tweets, self.test_dictionary)
	# 	self.assertEqual(t.assertValueToTweets() , [5,-15])

	# def testTweetScraper(self):
	# 	t = TweetScraper()
	# 	self.assertIsInstance(t.getTweets("bitcoin") , list)

	# def testCsvParser(self):
	# 	csvParser = CsvParser();
	# 	self.assertIsInstance(csvParser.parseFile("data.csv") , dict)
	# def testWholeApp(self):
	# 	scr = TweetScraper()
	# 	cps = CsvParser()
	# 	t = TweetParser(scr.getTweets("bitcoin"), cps.parseFile("testdata.csv"))
	# 	res = t.assertValueToTweets()
	# 	d = CsvDataSaver("testoutput.csv")
	# 	global lastSum 
	# 	lastSum = sum(res)
	# 	d.saveData(sum(res))
	# 	self.assertIsInstance(res, list)


# class APITest(unittest.TestCase):
# 	def setUp(self):
# 		self.startTime = time.time()
# 	def tearDown(self):
# 		t = time.time() - self.startTime
# 		print "%s: %.3f" % (self.id(), t)
	# def testTemplateInflater(self):
	# 	templateInflater = TemplateInflater("template.html")
	# 	data = templateInflater.inflate({"{toBeReplaced}" : "forThat", "{somethingDifferent}" : "8"})
	# 	print data
	# 	self.assertGreater(len(data), 5)
	# 	pass
	# def testGETRequestOnSlash(self):
	# 	testport = 8090
	# 	global templateInflater
	# 	global lastSum
	# 	lastSum = 5
	# 	templateInflater = TemplateInflater("template.html")
	# 	templateInflater.inflate({"{toBeReplaced}" : "forThat", "{somethingDifferent}" : "8"})
	# 	templateInflater.refresh()
	# 	serverThread = Thread(target = runServer, args = (testport, ))
	# 	serverThread.start()
	# 	try:
	# 		time.sleep(1)
	# 		response = requests.get("http://localhost:%d/" % testport)
	# 		responseText = response.text
	# 	except:
	# 		responseText = "FAIL!"

	# 	self.assertEqual(templateInflater.inflatedTemplate ,responseText)
	# def testGETRequestOnUpdate(self):
	# 	print "PAS?"
	# 	pass
	# def testGitHubApi(self):
	# 	gitStatsScraper = GitStatsScraper()
	# 	r = gitStatsScraper.getCommits()
	# 	self.assertIsInstance(r, str)
	# Basic Template: read file -> format with parameters -> output !!! done <3
	#  GET request: on "/" -> put data into template -> output
	#  GET request: on "/update" -> respond with JSON with new data 





###########################################################################
###########################################################################
###########################################################################
###########################################################################



if __name__ == '__main__':
	# unittest.main()

	testport = 8092

	lastSum = 5

	hashtag = "bitcoin"

	predict = 0

	classifierType = "mlpc"

	databaseType = "data.csv"	

	slashCounter = 0

	apiCounter = 0

	dateStart = datetime.now().date()


	templateInflater = TemplateInflater("template.html", {})

	dataPredictor = DataPredictor()


	serverThread = Thread(target = runServer, args = (testport, ))
	serverThread.start()
	
	while(True):

		if(time.time() % 5 == 0):

			scr = TweetScraper()
			cps = CsvParser()
			t = TweetParser(scr.getTweets(hashtag), cps.parseFile(databaseType))
			res = t.assertValueToTweets()
			d = CsvDataSaver(hashtag+".csv")
			lastSum = sum(res)
			d.saveData(sum(res))

		if(time.time() % 10 == 0):

			templateInflater.refresh({})
			predictorThread = Thread(target = dataPredictor.learn(), args = ( ))
			predictorThread.start()
			predict = dataPredictor.predict()
