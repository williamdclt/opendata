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
	def __init__(self, countryName, continentName="unknown"):
		self.countryName = countryName
		self.continentName = continentName

class CodeCountryContinent:
	def __init__(self, countryName, countryCode):
		self.countryContinent = CountryContinent(countryName)
		self.countryCode = countryCode

def getCountryInBuffer(text):
	if not os.path.isfile('buffer_countries.json'):
		with codecs.open('buffer_countries.json', 'a', "utf-8-sig") as json_data:
			d = {}
			json.dump(d, json_data)
			return None
	with codecs.open('buffer_countries.json', 'r', "utf-8-sig") as json_data:
		d = json.load(json_data)
		if text not in d:
			return None
		return CountryContinent(d[text]["countryName"], d[text]["continentName"])

def appendInBuffer(text, contiCountry):
	with codecs.open('buffer_countries.json', 'r', "utf-8-sig") as json_data:
		d = json.load(json_data)
		d[text] = {
			'countryName': contiCountry.countryName,
			'continentName': contiCountry.continentName
			}

	with codecs.open('buffer_countries.json', 'w', "utf-8-sig") as outfile:
		json.dump(d, outfile)

def getAPICountry(text):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData')
	d = r.json()

	for elem in d["geonames"]:
		if "fcode" in elem and elem["fcode"]=="PCLI":
			return CodeCountryContinent(elem["countryName"], elem["countryCode"])
		elif "fcode" not in elem:
			print("Pas de fcode pour " + text)

	return None

def getContinentCountry(text):
    res = getCountryInBuffer(text)
    if res is not None:
        return res

    codeRes = getAPICountry(text)
    if codeRes is None:
        countryContinent = CountryContinent(text, "unknown")
        appendInBuffer(text, countryContinent)
        return countryContinent
    with codecs.open('countries.json', 'r', "utf-8-sig") as json_data:
		d = json.load(json_data)
		continentCode = d["countries"][codeRes.countryCode]["continent"]
		codeRes.countryContinent.continentName = d["continents"][continentCode]
		appendInBuffer(text, codeRes.countryContinent)
		return codeRes.countryContinent

#res = getContinentCountry("Ellas")
#print(res.countryName + " " + res.continentName)