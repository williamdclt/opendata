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

def getCountryCode(text):
	s = (text.split(","))[-1]
	r = requests.get('http://api.geonames.org/searchJSON?q=' + s + '&username=OpenBoniData')
	d = r.json()
	for elem in d["geonames"]:
		if "fcode" in elem and elem["fcode"]=="PCLI":
			return elem["countryCode"]

	return None

def getAPILocation(text, twoParts):
	if twoParts:
		countryCode = getCountryCode(text)
		if countryCode == None:
			return None
		r = requests.get('http://api.geonames.org/searchJSON?q=' + (text.split(","))[0] + '&country=' + countryCode + '&username=OpenBoniData')
	else:
		r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData')

	d = r.json()

	if twoParts and d["totalResultsCount"] == 0:
		r = requests.get('http://api.geonames.org/searchJSON?q=' + (text.split(","))[-1] + '&username=OpenBoniData')
		d = r.json()
		twoParts=False

	if not twoParts:
		for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"]=="PCLI":
				return CodeLocation("unknown", elem["countryName"], elem["countryCode"])

	for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"].startswith("PP"):
				return CodeLocation(elem["name"], elem["countryName"], elem["countryCode"])

	return None

def isInTwoParts(text):
	return len(text.split(",")) >= 2

def getLocation(text):
	if not text.strip():
		return Location()

	text = unicode(text, "utf-8")

	b = isInTwoParts(text)
	res = getLocationInBuffer(text)
	if res is not None:
		return res

	codeRes = getAPILocation(text, b)
	if codeRes is None:
		if b:
			sp = text.split(",")
			location = Location(sp[0].strip(), sp[-1].strip())
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
