#!/usr/bin/env python

import json
import requests

def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__

class CountryContinent:
	def __init__(self, countryName, continentName="unknown"):
		self.countryName = countryName
		self.continentName = continentName

class CodeCountryContinent:
	def __init__(self, countryName, countryCode):
		self.countryContinent = CountryContinent(countryName)
		self.countryCode = countryCode

def getCountryInBuffer(text):
	with open('buffer_countries.json', 'w+') as json_data:
            try:
		d = json.load(json_data)
	    except ValueError:
                return None
            if text not in d or d[text]["countryName"] is None:
                    return None
            return CountryContinent(d[text]["countryName"], d[text]["continentName"])

def appendInBuffer(text, contiCountry):
	data = {}
	data[text] = []
	data[text].append({
		'countryName': contiCountry.countryName,
		'continentName': contiCountry.continentName
		})
        print("dumping "+contiCountry.countryName + " " + contiCountry.continentName)
	with open('buffer_countries.json', 'a+') as outfile:
		json.dump(data, outfile)

def getCountry(text):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData')
	d = r.json()

	for elem in d["geonames"]:
		if "fcode" in elem and elem["fcode"]=="PCLI":
			return CodeCountryContinent(elem["countryName"], elem["countryCode"])

	return None

def getContinentCountry(text):
    print("Looking for "+text)
    res = getCountryInBuffer(text)
    if res is not None:
        return res

    print("Calling API...")
    codeRes = getCountry(text)
    print("KK")
    if codeRes is None:
        countryContinent = CountryContinent(text, "unknown")
        return countryContinent
    with open('countries.json') as json_data:
        d = json.load(json_data)
        continentCode = d["countries"][codeRes.countryCode]["continent"]
        codeRes.countryContinent.continentName = d["continents"][continentCode]
        appendInBuffer(text, codeRes.countryContinent)
        return codeRes.countryContinent
