#!/usr/bin/env python

import json
import requests
import os.path
import time
import sys
import codecs
reload(sys)

sys.setdefaultencoding('utf-8')

class Location:
	def __init__(self, cityName="unknown", countryName="unknown", continentName="unknown"):
		self.cityName = cityName
		self.countryName = countryName
		self.continentName = continentName

class CodeLocation:
	def __init__(self, cityName, countryName, countryCode):
		self.location = Location(cityName, countryName)
		self.countryCode = countryCode

def getLocationInBuffer(text):
	if not os.path.isfile('buffer_countries.json'):
		with open('buffer_countries.json', 'a') as json_data:
			d = {}
			json.dump(d, json_data, ensure_ascii=False)
			return None
	with codecs.open('buffer_countries.json', 'r', "utf-8") as json_data:
		d = json.load(json_data)
		if text not in d:
			return None
		return Location(d[text]["cityName"], d[text]["countryName"], d[text]["continentName"])

def appendLocationInBuffer(text, contiCountry):
	with codecs.open('buffer_countries.json', 'r', "utf-8") as json_data:
		d = json.load(json_data)
		d[text] = {
			'cityName': contiCountry.cityName,
			'countryName': contiCountry.countryName,
			'continentName': contiCountry.continentName
			}

	with codecs.open('buffer_countries.json', 'w', "utf-8") as outfile:
		json.dump(d, outfile, ensure_ascii=False)

def getCountry(country):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + country + '&username=OpenBoniData&fuzzy=0.8')
	d = r.json()
	for elem in d["geonames"]:
		if "fcode" in elem and elem["fcode"]=="PCLI":
			return CodeLocation("unknown", elem["countryName"], elem["countryCode"])

	return None

def getAPILocationStereo(splitText):
	countryObj = getCountry(splitText[-1])
	if countryObj is None:
		return getAPILocationMono(splitText[0])

	r = requests.get('http://api.geonames.org/searchJSON?q=' + splitText[0] + '&country=' + countryObj.countryCode + '&username=OpenBoniData&fuzzy=0.8')
	d = r.json()

	if d["totalResultsCount"] == 0:
		return countryObj

	for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"].startswith("PP"):
				countryObj.location.cityName=elem["name"]
				break

	return countryObj


def getAPILocationMono(text):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData&fuzzy=0.8')
	d = r.json()
	for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"]=="PCLI":
				return CodeLocation("unknown", elem["countryName"], elem["countryCode"])

	for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"].startswith("PP"):
				return CodeLocation(elem["name"], elem["countryName"], elem["countryCode"])

	return None

def getLocation(text):
	if not text.strip():
		return Location()

	text = unicode(text, "utf-8")
	splitText = text.split(",")
	b = len(splitText) > 1

	res = getLocationInBuffer(text)
	if res is not None:
		return res

	if b:
		codeRes = getAPILocationStereo(splitText)
	else:
		codeRes = getAPILocationMono(text)
	if codeRes is None:
		if b:
			location = Location(splitText[0].strip(), splitText[-1].strip())
		else:
			location = Location(text)
		appendLocationInBuffer(text, location)
		return location
	with codecs.open('countries.json', 'r', "utf-8") as json_data:
		d = json.load(json_data)
		continentCode = d["countries"][codeRes.countryCode]["continent"]
		codeRes.location.continentName = d["continents"][continentCode]
		appendLocationInBuffer(text, codeRes.location)
		return codeRes.location

if __name__ == '__main__':
	res = getLocation(" ".join(sys.argv[1:]))
	print(res.cityName + " " + res.countryName + " " + res.continentName)
