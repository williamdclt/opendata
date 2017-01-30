#!/usr/bin/env python

from json import JSONEncoder
import csv
import json
from sets import Set
from collections import defaultdict

####### Structure des fichiers csv #######
## artists
# [0]id,[1]name,[2]gender,[3]dates,[4]yearOfBirth,[5]yearOfDeath,[6]placeOfBirth,[7]placeOfDeath,[8]url
## artworks
# [0]id,[1]accession_number,[2]artist,[3]artistRole,[4]artistId,[5]title,[6]dateText,[7]medium,[8]creditLine,[9]year,[10]acquisitionYear,[11]dimensions,[12]width,[13]height,[14]depth,[15]units,[16]inscription,[17]thumbnailCopyright,[18]thumbnailUrl,[19]url
##########################################

#noms des fichiers
fartistname = "artist_data.csv"
fartworkname = "artwork_data.csv"

#fichiers
fileartist = open(fartistname, 'rb')
fileartwork = open(fartworkname, 'rb')

artistreader = csv.reader(fileartist)
artworkreader = csv.reader(fileartwork)
next(artistreader) # skip header
next(artworkreader) # skip header

def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__

class Artist:
    def __init__(self, id, name, year, url, placeOfBirth, placeOfDeath):
        self.id = id
        self.name = name
        self.year = year
        self.url = url
        self.placeOfBirth = placeOfBirth
        self.placeOfDeath = placeOfDeath
        self.children = [] 

    def place():
        if self.placeOfBirth is None or self.placeOfBirth == "":
            return placeOfDeath
        return placeOfBirth

    def add_artwork(self, artwork):
        self.children.append(artwork)

class Dimensions:
    def __init__(self, width, height, depth, unit):
        self.width = width
        self.height = height
        self.depth = depth
        self.unit = unit


class Pays:
    def __init__(self, name):
        self.name = name.lower()
        self.children = []

    def add_city(self, city):
        if city not in self.children:
            self.children.append(city)


class City:
    def __init__(self, name):
        self.name = name.lower()
        self.children = []

    def add_artist(self, artist):
        self.children.append(artist)


class Collection:
    def __init__(self):
        self.name = "collection"
        self.children = []

    def add_pays(self, pays):
        if pays not in self.children:
            self.children.append(pays)


class Artwork:
    def __init__(self, id, artist_name, artist_id, title, year, width, height, depth, unit, thumbnail_url, url):
        self.id = id
        self.title = title
        self.artist_name = artist_name
        self.artist_id = artist_id
        self.year = year
        self.dimensions = Dimensions(width, height, depth, unit)
        self.thumbnail_url = thumbnail_url
        self.url = url


def get_pays(pays):
    if pays not in pays_dict:
        pays_dict[pays] = Pays(pays)
    return pays_dict[pays]


def get_city(city):
    if city not in cities_dict:
        cities_dict[city] = City(city)
    return cities_dict[city]

pays_dict = {}
cities_dict = {}
artists_dict = {}
collection = Collection()


for artist in artistreader:
    #on extrait le city,pays
    citypaysstring = artist[6]

    #on trie, on extrait la city et le pays
    #on fait en sorte que l'artiste ne soit la que si son pays est present, sinn NSM
    if citypaysstring is None :
        citypaysstring = "unknown, unknown"

    citypaysstrings = citypaysstring.split(',')
    pays, city = None, None
    if len(citypaysstrings)==2 :
        pays = citypaysstrings[1].strip()
        city = citypaysstrings[0].strip()
    elif len(citypaysstrings)==1 :
        pays = citypaysstrings[0].strip()
    else:  #c'est 3
        pays = citypaysstrings[2].strip()
        city = citypaysstrings[0].strip()

    #on insere pas ceux qui sont vide, apres tout ballec
    if pays=='' or pays is None:
        pays = 'unknown'
    if city=='' or city is None:
        city = 'unknown'

    #on extrait l'artiste
    id = artist[0]
    artist = Artist(id, artist[1], artist[4], artist[8], artist[6], artist[7])
    city = get_city(city)
    pays = get_pays(pays)

    artists_dict[id] = artist
    city.add_artist(artist)
    pays.add_city(city)
    collection.add_pays(pays)

for artwork in artworkreader:
    artist_id = artwork[4]
    if artist_id not in artists_dict:
        continue
    artwork = Artwork(artwork[0], artwork[2], artist_id, artwork[5], artwork[9], artwork[12], artwork[13], artwork[14], artwork[15], artwork[18], artwork[19])
    artists_dict[artist_id].add_artwork(artwork)

print(json.dumps(collection, default=dumper, sort_keys=True,indent=4, separators=(',', ': ')))
