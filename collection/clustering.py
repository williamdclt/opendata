#!/usr/bin/env python

from math import sqrt
from json import JSONEncoder
import csv
import json
import os
import sys
from sets import Set
from collections import defaultdict
reload(sys)

sys.setdefaultencoding('utf-8')

def to_list(a, string):
    return [ "class"+str(d.strip()) for d in a[string].split(',') ]

def create_artwork(a):
    title = a["title"]
    if "acquisitionYear" not in a:
        acquisitionYear = 0
    else:
        acquisitionYear = a["acquisitionYear"]
    if "id" not in a["catalogueGroup"]:
        group = 0
    else:
        group = a["catalogueGroup"]["id"]
    if a["dateRange"] is None:
        date = '0'
    else:
        date = a["dateRange"]["startYear"]
    width = a["width"]
    height = a["height"]
    depth = a["depth"]
    medium = a["medium"]
    return Artwork(title, acquisitionYear, group, date, medium, width, height, depth)

class Artwork:
    def __init__(self, title, acquisitionYear, group, date, medium, width, height, depth):
        self.title = title
        self.acquisitionYear = acquisitionYear
        self.group = group
        self.date = date
        self.width = width
        self.height = height
        self.depth = depth
        self.medium = medium


artworks = []

for folder, subs, files in os.walk("artworks"):
    for filename in files:
        with open(os.path.join(folder, filename), 'r') as json_file:
            artworks.append(create_artwork(json.load(json_file)))
            
csv_columns = ["title", "acquisitionYear", "group", "date", "width", "height", "depth", "medium"]
with open('to_cluster.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for a in artworks:
        writer.writerow(a.__dict__)
