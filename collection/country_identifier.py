#!/usr/bin/env python

import json
import requests
import os.path

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
		return None
	with open('buffer_countries.json', 'r') as json_data:
		d = json.load(json_data)
		if text not in d:
			return None
		return CountryContinent(d[text]["countryName"], d[text]["continentName"])

def appendInBuffer(text, contiCountry):
	data = {}
	data[text] = {
		'countryName': contiCountry.countryName,
		'continentName': contiCountry.continentName
		}

	with open('buffer_countries.json', 'a+') as outfile:
		json.dump(data, outfile)

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
    	print("JE L'AI TROUVE OMGGG")
        return res

    codeRes = getAPICountry(text)
    if codeRes is None:
        countryContinent = CountryContinent(text, "unknown")
        appendInBuffer(text, countryContinent)
        return countryContinent
    with open('countries.json') as json_data:
        d = json.load(json_data)
        continentCode = d["countries"][codeRes.countryCode]["continent"]
        codeRes.countryContinent.continentName = d["continents"][continentCode]
        appendInBuffer(text, codeRes.countryContinent)
        return codeRes.countryContinent

res = getContinentCountry("Mabyth")
print(res.countryName + " " + res.continentName)