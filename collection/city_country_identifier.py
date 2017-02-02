#!/usr/bin/env python

import json
import requests
import os.path
import time
import sys
import codecs
reload(sys)

sys.setdefaultencoding('utf-8')

# La classe Location represente la localisation geographique de l'artiste.
# A noter que dans certains cas cityName peut correspondre plutot a une region
class Location:
	def __init__(self, cityName="unknown", countryName="unknown", continentName="unknown"):
		self.cityName = cityName
		self.countryName = countryName
		self.continentName = continentName

# Structure intermediaire permettant de recuperer le continent d'une location
# grace a son countryCode (et le fichier country.json)
class CodeLocation:
	def __init__(self, cityName, countryName, countryCode):
		self.location = Location(cityName, countryName)
		self.countryCode = countryCode

# On essaye de recuperer un objet location selon la cle specifiee
# Si le fichier buffer_countries.json n'existe pas, il est cree a la volee
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

# Ajout d'une location au fichier json
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

# Recuperation d'un pays d'apres le parametre country, tolerence specifiee par fuzzy
# PCLH est le cas particulier d'un pays historique n'existant plus (ex : Yougoslavie)
def getCountryFuzzy(country, fuzzy):
	r = requests.get('http://api.geonames.org/searchJSON?q=' + country + '&username=OpenBoniData&fuzzy=' + fuzzy)
	d = r.json()
	isPCLH=False
	for elem in d["geonames"]:
		if "fcode" in elem and elem["fcode"].startswith("PC"):
			if elem["fcode"]=="PCLH":
				isPCLH=True
			return CodeLocation("unknown", elem["countryName"], elem["countryCode"]), isPCLH

	return None, isPCLH

# Recuperation d'un pays, ou l'on essaye de trouver un pays avec deux requetes avec
# fuzzy differents, car dans certains cas un fuzzy de 1 est plus pertinent que 0.85 (Al-Lubnan)
def getCountry(country):

	res, isPCLH=getCountryFuzzy(country, "0.85")

	if res is not None:
		return res, isPCLH

	res, isPCLH=getCountryFuzzy(country, "1")
	if res is not None:
		return res, isPCLH

	return None, isPCLH

# Recuperation de la location dans le cas ou on a deux elements
def getAPILocationStereo(splitText):
	countryObj, isPCLH = getCountry(splitText[-1])
	if countryObj is None:
		return getAPILocationMono(splitText[0])
	# PCLH correspond a un pays historique, nous ne pouvons que creer
	# une location qu'avec le nom de ville de base, car geoName renvoit
	# la ville dans le pays actuel
	# Je garde le nom de pays aussi, mais c'est juste car geonames a du mal
	# avec la yougoslavie (il la nomme YU, ce qui est son code)
	elif isPCLH:
		countryObj.location.cityName=splitText[0]
		countryObj.location.countryName=splitText[-1]
		return countryObj

	r = requests.get('http://api.geonames.org/searchJSON?q=' + splitText[0] + '&country=' + countryObj.countryCode + '&username=OpenBoniData&fuzzy=0.85')
	d = r.json()

	countryObj.location.cityName=splitText[0]

	if d["totalResultsCount"] == 0:
		return countryObj

	for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"].startswith("PP") or elem["fcode"].startswith("AD"):
				countryObj.location.cityName=elem["name"]
				break

	return countryObj

# Recuperation de la location dans le cas ou on a un element
def getAPILocationMono(text):
	res, isPCLH = getCountry(text)
	if res is not None:
		return res

	r = requests.get('http://api.geonames.org/searchJSON?q=' + text + '&username=OpenBoniData&fuzzy=0.85')
	d = r.json()
	for elem in d["geonames"]:
			if "fcode" in elem and elem["fcode"].startswith("PP") or elem["fcode"].startswith("AD"):
				return CodeLocation(elem["name"], elem["countryName"], elem["countryCode"])

	return None

# Fonction principale permettant de recuperer au mieux la location
# du texte passse en parametre, selon les differents cas
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
		# Dans ce cas, on laisse les informations telles qu'on les a recues
		if b:
			location = Location(splitText[0].strip(), splitText[-1].strip())
		else:
			location = Location(text)
		appendLocationInBuffer(text, location)
		return location
	with codecs.open('countries.json', 'r', "utf-8") as json_data:
		d = json.load(json_data)
		if codeRes.countryCode in d["countries"]:
			continentCode = d["countries"][codeRes.countryCode]["continent"]
			codeRes.location.continentName = d["continents"][continentCode]
		appendLocationInBuffer(text, codeRes.location)
		return codeRes.location

if __name__ == '__main__':
	res = getLocation(" ".join(sys.argv[1:]))
	print(res.cityName + " " + res.countryName + " " + res.continentName)
