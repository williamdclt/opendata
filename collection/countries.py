#!/usr/bin/env python

import json
import sys

#code taken from rosettacode
#https://rosettacode.org/wiki/Levenshtein_distance#Iterative
def minimumEditDistance(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]

class CountryCheck:
    def __init__(self, name, levenValue):
        self.name = name
        self.levenValue = levenValue
 
    def getBiCountryDistance(self, country):
        return min (minimumEditDistance(country, self.name), minimumEditDistance(country, self.native))

def getMiniCountry(text, name, native):
	tmp1 = minimumEditDistance(text, name)
	tmp2 = minimumEditDistance(text, native)

	if tmp1 <= tmp2:
		return CountryCheck(name, tmp1)
	else:
		return CountryCheck(native, tmp2)

def getWordsRatio(length1, length2, levenValue):
	s = float(length1 + length2)
	return (s - levenValue) / s

def getCountry(text):
	with open('countries.json') as json_data:
		d = json.load(json_data)
		res = CountryCheck(None, sys.maxsize)
		for country in d["countries"]:
			name = d["countries"][country]["name"].lower()
			native = d["countries"][country]["native"].lower()
			tmp = getMiniCountry(text, name, native)
			if tmp.levenValue <= res.levenValue or res.name is None:
				res.name = tmp.name
				res.levenValue = tmp.levenValue
		
		if getWordsRatio(len(text), len(res.name), res.levenValue) < 0.54:
			return None

		return res.name
