#!/usr/bin/env python

import json
import requests

class CountryContinent:
	def __init__(self, countryName, continentName=None):
		self.countryName = countryName
		self.continentName = continentName

class CodeCountryContinent:
	def __init__(self, countryName, countryCode):
		self.countryContinent = CountryContinent(countryName)
		self.countryCode = countryCode

def getCountryInBuffer(text)
	with open('buffer_countries.json') as json_data:
		d = json.load(json_data)
		if text not in d or d[text]["countryName"] is None:
			return None
		return CountryContinent(d[text]["countryName"], d[text]["continentName"])

def appendInBuffer(text, contiCountry)
	data = {}
	data[text] = []
	data[text].append({
		'countryName': contiCountry.countryName,
		'continentName': contiCountry.countryContinent
		})
	with open('buffer_countries.json', 'w') as outfile:
		json.dump(data, outfile)

def getCountry(text):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData')
	d = r.json()

	for elem in d["geonames"]:
		if elem["fcode"]=="PCLI":
			return CodeCountryContinent(CountryContinent(elem["countryName"]), elem["countryCode"])

	return None

def getContinentCountry(text):
	res = getCountryInBuffer(text)
	if res is not None:
		return res

	codeRes = getCountry(text)
	if codeRes is None:
		appendInBuffer(text, CountryContinent(None))
		return None
	with open('countries.json') as json_data:
		d = json.load(json_data)
		continentCode = d["countries"][codeRes.countryCode]["continent"]
		codeRes.countryContinent.continentName = d["continents"][continentCode]
		appendInBuffer(text, codeRes.countryContinent)
		return codeRes.countryContinent