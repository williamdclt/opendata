#!/usr/bin/env python

import json
import requests
import os.path
import time
import sys
import codecs
reload(sys)

sys.setdefaultencoding('utf-8')

class CountryContinent:
	def __init__(self, cityName="unknown", countryName="unknown", continentName="unknown"):
		self.cityName = cityName
		self.countryName = countryName
		self.continentName = continentName

class CodeCountryContinent:
	def __init__(self, cityName, countryName, countryCode):
		self.countryContinent = CountryContinent(cityName, countryName)
		self.countryCode = countryCode

def getCountryInBuffer(text):
	if not os.path.isfile('buffer_countries.json'):
		with open('buffer_countries.json', 'a') as json_data:
			d = {}
			json.dump(d, json_data, ensure_ascii=False)
			return None
	with codecs.open('buffer_countries.json', 'r', "utf-8") as json_data:
		d = json.load(json_data)
		if text not in d:
			return None
		return CountryContinent(d[text]["cityName"], d[text]["countryName"], d[text]["continentName"])

def appendInBuffer(text, contiCountry):
	with codecs.open('buffer_countries.json', 'r', "utf-8") as json_data:
		d = json.load(json_data)
		d[text] = {
			'cityName': contiCountry.cityName,
			'countryName': contiCountry.countryName,
			'continentName': contiCountry.continentName
			}

	with codecs.open('buffer_countries.json', 'w', "utf-8") as outfile:
		json.dump(d, outfile, ensure_ascii=False)

def getAPICountry(text, twoParts):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData')
	d = r.json()

	if not twoParts:
		for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"]=="PCLI":
				return CodeCountryContinent("unknown", elem["countryName"], elem["countryCode"])

	for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"].startswith("PP"):
				return CodeCountryContinent(elem["name"], elem["countryName"], elem["countryCode"])

	return None

def isInTwoParts(text):
	return len(text.split(",")) >= 2

def getContinentCountry(text):
	b = isInTwoParts(text)
	text = unicode(text, "utf-8")
	res = getCountryInBuffer(text)
	if res is not None:
		return res

	codeRes = getAPICountry(text, b)
	if codeRes is None:
		if b:
			sp = text.split(",")
			countryContinent = CountryContinent(sp[0].trim(), sp[1].trim())
		else:
			countryContinent = CountryContinent(text)
		appendInBuffer(text, countryContinent)
		return countryContinent
	with codecs.open('countries.json', 'r', "utf-8") as json_data:
		d = json.load(json_data)
		continentCode = d["countries"][codeRes.countryCode]["continent"]
		codeRes.countryContinent.continentName = d["continents"][continentCode]
		appendInBuffer(text, codeRes.countryContinent)
		return codeRes.countryContinent

res = getContinentCountry("Zhonghua")
print(res.cityName + " " + res.countryName + " " + res.continentName)
