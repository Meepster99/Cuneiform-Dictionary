
import json
import time
import os
import re
import json
from difflib import SequenceMatcher

from unidecode import unidecode

import pymongo

from bs4 import BeautifulSoup 

from colorama import init, Fore, Back, Style
init(convert=True)

from bs4 import BeautifulSoup

import signal

RED = Style.BRIGHT + Fore.RED
GREEN = Style.BRIGHT + Fore.GREEN
YELLOW = Style.BRIGHT + Fore.YELLOW
BLUE = Style.BRIGHT + Fore.BLUE
MAGENTA = Style.BRIGHT + Fore.MAGENTA
CYAN = Style.BRIGHT + Fore.CYAN
WHITE = Style.BRIGHT + Fore.WHITE

RESET = Style.RESET_ALL

def loadEPSD2():

	print("loading base EPSD2 dictionary")
	
	startTime = time.perf_counter()
	data = json.load(open("./epsd2/gloss-sux.json", encoding='utf-8'))
	endTime = time.perf_counter()
	print("loading took {:.02f} seconds".format(endTime - startTime))
	
	print("creating database, this may take a while")
		
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")

	mydb = myclient["cuneiformSearch"]
	
	base = mydb["EPSD2"]
	
	glossSux = base["gloss-sux"]
	
	glossSux.drop()
	
	glossSuxEntries = glossSux["entries"]
	glossSuxInstances = glossSux["instances"]
	glossSuxSummaries = glossSux["summaries"]
	
	glossSuxEntries.drop()
	glossSuxInstances.drop()
	glossSuxSummaries.drop()
	
	print("inserting {:d} entries".format(len(data["entries"])))
	glossSuxEntries.insert_many(data["entries"])
	
	print("inserting {:d} instances".format(len(data["instances"])))
	

	instancesData = []
	
	print("preprocessing instance data")
	for key, val in data["instances"].items():
		
		instancesData.append({
		"xis": key,
		"instances": val,
		})
	
	print("actually inserting instance data")
	glossSuxInstances.insert_many(instancesData)
	
	
	print("inserting {:d} summaries".format(len(data["summaries"])))
	
	summariesData = []
	
	print("preprocessing summaries data")
	for key, val in data["summaries"].items():
		
		soup = BeautifulSoup(val.encode("utf-8"), "html.parser")
		
		baseSummary = soup.find_all("span", {"class": "summary"})[0]
		
		baseTexts = baseSummary.find_all(text=True, recursive=False)
		reg = re.compile(r"^(;|,) $")
		baseTexts = [ i.strip(' "\'\t\r\n') for i in baseTexts if not reg.match(i) ]
		
		headwordText = baseSummary.find_all("span", {"class": "summary-headword"})[0].text
		
		writings = baseSummary.find_all("span", {"class": "wr"})
		writingsList = [ w.get_text(separator = " ") for w in writings ]
			
		summariesData.append({
			
			"headword": headwordText,
			
			"oid": key,
			
			"periods": baseTexts[0],
			"definitions": baseTexts[1],
			
			"forms": writingsList,
		})
	
	print("actually inserting summaries data")
	glossSuxSummaries.insert_many(summariesData)
	
	print("all data inserted, exiting")

def loadEPSD2Names():

	print("loading The Electronic Text Corpus of Sumerian Royal Inscriptions Names Database")	
	startTime = time.perf_counter()
	data = json.load(open("./epsd2/names/gloss-qpn.json", encoding='utf-8'))
	endTime = time.perf_counter()
	print("loading took {:.02f} seconds".format(endTime - startTime))
	
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")

	mydb = myclient["cuneiformSearch"]

	base = mydb["EPSD2"]
	
	names = base["names"]
	
	names.drop()
	
	namesEntries = names["entries"]
	namesInstances = names["instances"]
	namesSummaries = names["summaries"]
	
	namesEntries.drop()
	namesInstances.drop()
	namesSummaries.drop()

	print("inserting entries")
	namesEntries.insert_many(data["entries"])
	
	print("inserting instances")
	namesInstances.insert_many([ {"key": k, "instances": v} for k, v in data["instances"].items() ])
	
	print("inserting summaries")
	
	print("preprocessing summaries data")
	summariesData = []
	for key, val in data["summaries"].items():
		
		soup = BeautifulSoup(val.encode("utf-8"), "html.parser")
		
		baseSummary = soup.find_all("span", {"class": "summary"})[0]
		
		baseTexts = baseSummary.find_all(text=True, recursive=False)
		reg = re.compile(r"^(;|,) $")
		baseTexts = [ i.strip(' "\'\t\r\n') for i in baseTexts if not reg.match(i) ]
		
		headwordText = baseSummary.find_all("span", {"class": "summary-headword"})[0].text
		
		writings = baseSummary.find_all("span", {"class": "wr"})
		writingsList = [ w.get_text(separator = " ") for w in writings ]
		
		summariesData.append({
			
			"headword": headwordText,
			
			"oid": key,
			
			"periods": baseTexts[0],
			"definitions": baseTexts[1],
			
			"forms": writingsList,
		})
	
	print("actually inserting summaries data")
	namesSummaries.insert_many(summariesData)
	
	
	print("all data inserted, exiting")

	pass

def loadETCSRI():
	
	print("loading The Electronic Text Corpus of Sumerian Royal Inscriptions")
	
	startTime = time.perf_counter()
	data = json.load(open("./etcsri/index-qpn.json", encoding='utf-8'))
	endTime = time.perf_counter()
	print("loading took {:.02f} seconds".format(endTime - startTime))
	

	myclient = pymongo.MongoClient("mongodb://localhost:27017/")

	mydb = myclient["cuneiformSearch"]
	
	ETCSRIDatabase = mydb["ETCSRI"]
	
	indexqpn = ETCSRIDatabase["index-qpn"]
	
	indexqpn.drop()
	
	keysDatabase = indexqpn["keys"]
	
	keysDatabase.drop()
	
	print("inserting {:d} entries".format(len(data["keys"])))
	keysDatabase.insert_many(data["keys"])
	
	pass
	
def loadDatabase():
	
	loadEPSD2()
	
	loadEPSD2Names()
	
	loadETCSRI()
	
	print("loaded all data successfully, exiting")
	
	exit(0)

# 

def swapState(signum, frame):
	
	
	if not hasattr(swapState, "state"):
		swapState.state = 0
		swapState.stateStrings = ["translator", "lookup"]
		swapState.stateFunctions = [translator, lookup]
		
	#print(swapState.state, swapState.stateStrings[swapState.state])
	swapState.state = 1 - swapState.state
	
	swapState.stateFunctions[swapState.state]()

	pass

def translator():

	print("")
	print("ctrl + c to switch, fn + ctrl + b to exit")

	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	mydb = myclient["cuneiformSearch"]
	dataEntries = mydb["EPSD2"]["gloss-sux"]["entries"]

	normalNumbers = "".join([ chr(i) for i in range(0x30, 0x3A) ])
	subscriptNumbers = "".join([ chr(i) for i in range(0x2080, 0x208A) ])
	
	# j=ŋ sz=š s,=ṣ t,=ṭ 0-9=₀-₉; '=alef
		
	def formatSign(s):
	
		s = s.translate(s.maketrans(normalNumbers, subscriptNumbers))
		
		s = s.replace("sz", "\u0161")
		

		s = s.replace("j", "ŋ")
		s = s.replace("ĝ", "ŋ")
	
		s = s.replace("[", "").replace("]", "")
		
		# as for what to do with / and \, idek! just removing them now 
		s = s.replace("/", "").replace("\\", "")
		
	
		while "--" in s:
			s = s.replace("--", "-")
		
		return s
		

		
	prefixGrammar = {	
		"nu": "Negative",
		"bara":	"Vetitive, Negative Affirmative",
		"na": "Prohibitive, Affirmative",
		"ga": "Cohortative",
		"ha": "Precative, Affirmative",
		"sa": "IDEK BRO",
		"u": "Prospective",
		"iri":	"IDEK BRO",
		"nus":	"IDEK BRO",
		
		"an": "I REALLY HAVE 0 CLUE",
	}
	
	suffixGrammar = {
		"ak": "denotes x of y",
		"e": "denotes the agent",
		"Ø": "denotes the patient",
		"a": "denotes location",
		"ir": "denotes a beneficiary",
		"da": "denotes with",
		"ta": "denotes motion going away",
		"še": "denotes motion going toward",
		"gin": "denotes like",
		"e": "denotes nearness",
			  
		"ki": "denotes place",		

		"ŋu": "my",
		"zu": "your (s)",
		"ani": "his/her",
		"bi": "its",
		"me": "our",
	
		"mu": "venitive",
		"ba": "middle voice",
		
		"zu": "2nd person singular",
		
		
		"ga": "Locative, in my",
		
	}
	

	try:
		while True:
			
			print("")
			print(WHITE + "j=ŋ sz=š s,=ṣ t,=ṭ 0-9=₀-₉; '=alef" + RESET)
			rawSign = input(WHITE + "input sign>" + RESET)
			
			sign = formatSign(rawSign)
				
			query = {"forms": 
						{"$elemMatch": 
							{"n": 
								{"$regex": "^" + sign + "$", "$options": "i"}
					} 
				} 
			}
			temp = dataEntries.find(query)
			temp = list(temp)
			
			
			res = None
			
			if len(temp) == 0:
				print(u"no matches for query of \"{:s}\" raw: \"{:s}\" were found!".format(sign, rawSign))
				continue
			if len(temp) == 1:
				fullRes = temp
			else:			
				
				matchDict = {}
				for t in temp:
					
					matchScore = SequenceMatcher(None, sign, t["cf"].lower()).ratio()
					
					if matchScore not in matchDict:
						matchDict[matchScore] = []
					
					matchDict[matchScore].append(t)
				
				bestMatches = matchDict[max(matchDict.keys())]
		
				res = max(bestMatches, key = lambda obj : int(obj["icount"]))
				
		
				fullRes = [res]
			
			for res in fullRes:
				
				print(WHITE + "Base: " + CYAN + res["cf"] + WHITE + " Pos: " + MAGENTA + res["pos"] + RESET)
				
				if res["cf"] in sign:
					
					splitSigns = sign.split("-")
					
					output = []
					
					after = False
					for spl in splitSigns:
					
						numberFree = spl.translate({ord(i): None for i in subscriptNumbers})
						
						
						if numberFree == res["cf"]:
							output.append(CYAN + spl + RESET)
							after = True
						else:
						
							tempGrammar = [prefixGrammar, suffixGrammar][after]
							
							if numberFree in tempGrammar:
								explanation = tempGrammar[numberFree]
								print(GREEN + numberFree + RESET + ":" + WHITE + explanation + RESET)
						
							output.append(GREEN + spl + RESET)
						
					
					print("-".join(output))
					
				for sense in res["senses"]:
					print(sense["mng"])
			
			
				
			
	except KeyboardInterrupt:
		pass

	pass
	
def lookup():

	print("")
	print("ctrl + c to switch, fn + ctrl + b to exit")

	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	mydb = myclient["cuneiformSearch"]
	dataEntries = mydb["EPSD2"]["gloss-sux"]["entries"]

	try:
		while True:
			
			print("")
			lookupString = input(WHITE + "input lookup word>" + RESET)
			
			query = {"gw": 
				{"$regex": "^" + lookupString + "$", "$options": "i"}
			}
			
			temp = dataEntries.find(query)
			temp = list(temp)
	
			if len(temp) == 0:
				print("no results found for " + lookupString)
				continue
	
			for t in temp:
				print(t["headword"])

			
			
			
	except KeyboardInterrupt:
		pass
	

	pass

#
	
if __name__ == "__main__":
	
	#loadDatabase()
	
	while True:
		translator()
		lookup()

	print("exiting")
