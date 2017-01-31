#!/usr/bin/env python

from math import sqrt
from json import JSONEncoder
import csv
import json
from sets import Set
from collections import defaultdict
from string import ascii_lowercase

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


class Part:
    def __init__(self, begin):
        self.name = begin
        self.children = []

    def end(self, letter):
        self.name = self.name + "-" + letter


class Decoupable:
    def __init__(self):
        self.children = []

    def add_children(self, child):
        if child not in self.children:
            self.children.append(child)

    def compute_decoupable(self):
        min_dec = 7
        if len(self.children) <= min_dec: # no need to decouping
            return

        partition = []
        current_char = 0 # 'a'
        while current_char < len(ascii_lowercase):
            current_part = Part(ascii_lowercase[current_char])
            while len(current_part.children) < min_dec and current_char < len(ascii_lowercase):
                children = self.get_children_beginning_with(ascii_lowercase[current_char])
                current_part.children.extend(children)
                current_char += 1
            current_part.end(ascii_lowercase[current_char - 1])
            partition.append(current_part)
        self.children = partition

    def get_children_beginning_with(self, char):
        part = []
        for child in self.children:
            if child.name[0] == char:
                part.append(child)
        return part


class Artist(Decoupable):
    def __init__(self, id, name, year, url, placeOfBirth, placeOfDeath):
        self.id = id
        self.name = name.lower()
        self.size = 1
        self.year = year
        self.url = url
        self.placeOfBirth = placeOfBirth
        self.placeOfDeath = placeOfDeath
        self.children = []

    def place(self):
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


class Pays(Decoupable):
    def __init__(self, name):
        self.name = name.lower()
        self.children = []


class City(Decoupable):
    def __init__(self, name):
        self.name = name.lower()
        self.children = []


class Collection(Decoupable):
    def __init__(self):
        self.name = "collection"
        self.children = []


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
    def __init__(self,id, size, name, url, tatelink):
        self.id = id
        self.group = 1
        self.size = size
        self.name = name
        self.url = url
        self.tatelink = tatelink

class Link:
    def __init__(self,source, target):
        self.source = source
        self.target = target
        self.value = 1

def get_pays(pays):
    if pays not in pays_dict:
        pays_dict[pays] = Pays(pays)
    return pays_dict[pays]


def get_city(city, pays):
    index = city + pays
    if index not in cities_dict:
        cities_dict[index] = City(city)
    return cities_dict[index]

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
    city = get_city(city, pays)
    pays = get_pays(pays)

    artists_dict[id] = artist
    city.add_children(artist)
    pays.add_children(city)
    collection.add_children(pays)

for artwork in artworkreader:
    artist_id = artwork[4]
    if artist_id not in artists_dict:
        continue
    artwork = Artwork(artwork[0], artist_id, artwork[5], artwork[9], artwork[12], artwork[13], artwork[14], artwork[15], artwork[18], artwork[19])
    artists_dict[artist_id].add_artwork(artwork)

for a in artists_dict:
    artists_dict[a].size = sqrt(len(artists_dict[a].children))
    #on va desormais creer un fichier json pour chaque artiste contenant ses oeuvres
    #on cree chaque tableau
    #le nodes contient au moins l'artiste, avec un lien vesr sa page
    nodeArtist = Node("Artist", 5, artists_dict[a].name, None, artists_dict[a].url)
    tableauNodes = [nodeArtist]
    tableauLinks = []
    for artwork in artists_dict[a].children:
        #print(artwork)
        artnode = Node(str(artwork.id),50,artwork.name, artwork.thumbnail_url,artwork.url)
        tableauNodes.append(artnode)
        artlink = Link("Artist",str(artwork.id))
        tableauLinks.append(artlink)
    artistPersonaljson = {"nodes" : tableauNodes, "links" : tableauLinks};

    #on ouvre 1 fichier par artiste et on dump le json
    f = open(str(artists_dict[a].id)+".json",'w')
    f.write(json.dumps(artistPersonaljson, default=dumper, indent=2, separators=(',', ': ')))
    f.close()

    #on reset pour l'affichage
    artists_dict[a].children = []


for c in cities_dict:
    cities_dict[c].compute_decoupable()
for p in pays_dict:
    pays_dict[p].compute_decoupable()
collection.compute_decoupable()

f = open("collection.json", 'w')
f.write(json.dumps(collection, default=dumper, indent=2, separators=(',', ': ')))
f.close()
