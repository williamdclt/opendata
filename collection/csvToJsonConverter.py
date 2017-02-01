#!/usr/bin/env python

import csv
import json
import sys
import country_identifier
import math
from json import JSONEncoder
from sets import Set
from collections import defaultdict
from string import ascii_lowercase
reload(sys)

sys.setdefaultencoding('utf-8')

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


class MaleRatio:
    def __init__(self):
        self.nb_male = 0
        self.nb_artists = 0

    def add(self, ratio):
        self.nb_male += ratio.nb_male
        self.nb_artists += ratio.nb_artists


class Drawable:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def male_ratio(self):
        ratio = MaleRatio()
        for child in self.children:
            ratio.add(child.male_ratio())
        if len(self.children) == 0:
            ratio.nb_male = 1
            ratio.nb_artists = 1
        self.ratio = float(ratio.nb_male) / ratio.nb_artists
        return ratio


class Ensemble(Drawable):
    def __init__(self, name, level):
        Drawable.__init__(self, name, level)
        self.children = []

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)


class Part(Ensemble):
    def __init__(self, level, children):
        Ensemble.__init__(self, "", level)
        self.children = children
        self.name = self.get_child_name(0) + " - " + self.get_child_name(-1)

    def get_child_name(self, child_index):
        return self.children[child_index].name.split(',')[0].capitalize()


class Decoupable(Ensemble):
    def __init__(self, name, level, level_child):
        Ensemble.__init__(self, name, level)
        self.level_child = level_child

    def compute_decoupable(self):
        self.children.sort(key = lambda c: c.name)
        if len(self.children) <= 10: # no need to decouping
            return

        partition = []
        size_part = int(math.ceil(math.sqrt(len(self.children))))
        i = 0
        while i < len(self.children):
            children_part = self.children[i:min(i+size_part,len(self.children))] 
            part = Part(self.level_child, children_part)
            partition.append(part)
            i += size_part 
        self.children = partition

    def get_children_beginning_with(self, char):
        part = []
        for child in self.children:
            if child.name[0] == char:
                part.append(child)
        return part


class Artist(Decoupable):
    def __init__(self, id, name, year, url, placeOfBirth, placeOfDeath, gender):
        Decoupable.__init__(self, name, "Artist", "Artwork")
        self.id = id
        self.size = 1
        self.year = year
        self.url = url
        self.placeOfBirth = placeOfBirth
        self.placeOfDeath = placeOfDeath
        self.gender = gender.lower()

    def place(self):
        if self.placeOfBirth is None or self.placeOfBirth == "":
            return placeOfDeath
        return placeOfBirth

    def male_ratio(self):
        ratio = MaleRatio()
        ratio.nb_artists = 1
        if self.gender == "male":
            ratio.nb_male = 1
        else:
            ratio.nb_male = 0
        self.ratio = float(ratio.nb_male) / ratio.nb_artists
        return ratio

    def add_child(self, child): # Do not check if exists, would be too computationally heavy
        self.children.append(child)


class Dimensions:
    def __init__(self, width, height, depth, unit):
        self.width = width
        self.height = height
        self.depth = depth
        self.unit = unit


class Continent(Decoupable):
    def __init__(self, name):
        Decoupable.__init__(self, name, "Continent", "Country")


class Country(Decoupable):
    def __init__(self, name):
        Decoupable.__init__(self, name, "Country", "City")


class City(Decoupable):
    def __init__(self, name):
        Decoupable.__init__(self, name, "City", "Artist")


class Collection(Decoupable):
    def __init__(self):
        Decoupable.__init__(self, "collection", "Collection",  "Continent")


class Artwork:
    def __init__(self, id, artist_id, title, year, width, height, depth, unit, thumbnail_url, url):
        self.id = id
        self.name = title.lower()
        self.artist_id = artist_id
        self.year = year
        self.dimensions = Dimensions(width, height, depth, unit)
        self.thumbnail_url = thumbnail_url
        self.url = url


#pour l'affichage des tableaux par artiste
class Node:
    def __init__(self,id, size, name, gender, url, tatelink):
        self.id = id
        self.group = 1
        self.size = size
        self.name = name
        self.url = url
        self.tatelink = tatelink
        self.gender = gender


class Link:
    def __init__(self,source, target):
        self.source = source
        self.target = target
        self.value = 1


class Location:
    def __init__(self, city, country, continent):
        self.city = city
        self.country = country
        self.continent = continent


def get_continent(continent):
    if continent not in continents_dict:
        continents_dict[continent] = Continent(continent)
    return continents_dict[continent]


def get_country(country):
    if country not in countries_dict:
        countries_dict[country] = Country(country)
    return countries_dict[country]


def get_city(city, country):
    index = city + country
    if index not in cities_dict:
        cities_dict[index] = City(city)
    return cities_dict[index]


def getContiCountryCity(string):
    if string is None :
        string = "unknown, unknown"

    strings = string.split(',')
    country, city = None, None
    if len(strings)==2:
        country = strings[1].strip()
        city = strings[0].strip()
    elif len(strings)==1 :
        country = strings[0].strip()
    else:  #c'est 3
        country = strings[2].strip()
        city = strings[0].strip()

    if country=='' or country is None:
        country = 'unknown'
    if city=='' or city is None:
        city = 'unknown'

    conticountry = country_identifier.getContinentCountry(country) 
    return Location(city, conticountry.countryName, conticountry.continentName)


continents_dict = {}
countries_dict = {}
cities_dict = {}
artists_dict = {}
collection = Collection()


for artist in artistreader:
    location = getContiCountryCity(artist[6])

    #on trie, on extrait la city et le pays
    #on fait en sorte que l'artiste ne soit la que si son pays est present, sinn NSM

    #on extrait l'artiste
    id = artist[0]
    artist = Artist(id, artist[1], artist[4], artist[8], artist[6], artist[7], artist[2])
    city = get_city(location.city, location.country)
    country = get_country(location.country)
    continent = get_continent(location.continent)

    artists_dict[id] = artist
    city.add_child(artist)
    country.add_child(city)
    continent.add_child(country)
    collection.add_child(continent)


for artwork in artworkreader:
    artist_id = artwork[4]
    if artist_id not in artists_dict:
        continue
    artwork = Artwork(artwork[0], artist_id, artwork[5], artwork[9], artwork[12], artwork[13], artwork[14], artwork[15], artwork[18], artwork[19])
    artists_dict[artist_id].add_child(artwork)

#on limite a une trentaine de tableaux a cause de l'ami turner
for a in artists_dict:
    artists_dict[a].size = math.sqrt(len(artists_dict[a].children))
    if artists_dict[a].size < 1:
        artists_dict[a].size = 0.5;
    #on va desormais creer un fichier json pour chaque artiste contenant ses oeuvres
    #on cree chaque tableau
    #le nodes contient au moins l'artiste, avec un lien vesr sa page
    nodeArtist = Node("Artist", 30, artists_dict[a].name, artists_dict[a].gender, None, artists_dict[a].url)
    tableauNodes = [nodeArtist]
    tableauLinks = []
    ##########################Changer ici le nombre de bulles max par artiste###
    max_nodes=40
    ############################################################################
    for artwork in artists_dict[a].children:
        artnode = Node(str(artwork.id),50,artwork.name, None, artwork.thumbnail_url,artwork.url)
        tableauNodes.append(artnode)
        artlink = Link("Artist",str(artwork.id))
        tableauLinks.append(artlink)
        max_nodes-=1
        if max_nodes==0:
            break
    artistPersonaljson = {"nodes" : tableauNodes, "links" : tableauLinks};

    #on ouvre 1 fichier par artiste et on dump le json
    f = open("artists/"+str(artists_dict[a].id)+".json",'w')
    f.write(json.dumps(artistPersonaljson, default=dumper, indent=2, separators=(',', ': ')))
    f.close()

    #on reset pour l'affichage
    artists_dict[a].children = []


for c in cities_dict:
    cities_dict[c].compute_decoupable()
    print("CITY " + c + " : " + str(len(cities_dict[c].children)) + " parts artistes")
for c in countries_dict:
    countries_dict[c].compute_decoupable()
    print("PAYS " + c + " : " + str(len(countries_dict[c].children)) + " parts villes")
for c in continents_dict:
    continents_dict[c].compute_decoupable()
    print("CONT " + c + " : " + str(len(continents_dict[c].children)) + " parts pays")
collection.compute_decoupable()
collection.male_ratio()

f = open("collection.json", 'w')
f.write(json.dumps(collection, default=dumper, indent=2, separators=(',', ': ')))
f.close()
