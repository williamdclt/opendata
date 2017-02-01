#!/usr/bin/env python

import json
import requests

class CountryContinent:
	def __init__(self, countryName, countryCode):
		self.countryName = countryName
		self.countryCode = countryCode
		self.continentName = None

def getCountry(text):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData')
	d = r.json()

	for elem in d["geonames"]:
		if elem["fcode"]=="PCLI":
			return CountryContinent(elem["countryName"], elem["countryCode"])

	return None

def getContinentCountry(text):
	res = getCountry(text)
	if res is None:
		return None
	with open('countries.json') as json_data:
		d = json.load(json_data)
		continentCode = d["countries"][res.countryCode]["continent"]
		res.continentName = d["continents"][continentCode]
		return res