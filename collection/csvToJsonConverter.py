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

##le json final
jsoneddata={"name":"collection","children":[]}

try:
	artistreader = csv.reader(fileartist)
	artworkreader = csv.reader(fileartwork)
	pays_array = {}

	for artist in artistreader:
		#on extrait le ville,pays
		villepaysstring = artist[6]
		#on trie, on extrait la ville et le pays
		#on fait en sorte que l'artiste ne soit la que si son pays est present, sinn NSM
		if villepaysstring is not None :
			villepaysstrings = villepaysstring.split(',');
			pays = None
			ville = None
			if len(villepaysstrings)==2 :
				pays = villepaysstrings[1]
				ville = villepaysstrings[0]
			elif len(villepaysstrings)==1 :
				pays = villepaysstrings[0]
			else:  #c'est 3
				pays = villepaysstrings[2]
				ville = villepaysstrings[0]
			#si jamais y'a un espace devant, on l'enleve
			if pays is not None and pays!='' and pays[0]==' ':
				pays = pays[1:]

			#on enleve ceux qui sont vide, apres tout ballec
			if pays=='' :
				pays=None

			#on extrait l'artiste
			artistname=artist[1]
			year=artist[4]
			url=artist[8]

			##on insere dans le json TODO TODO
			if pays!=None :
				if pays not in pays_array:
					pays_array[pays] = []
				pays_array[pays].append(artistname)

finally:
	print(json.dumps(pays_array, sort_keys=True,indent=4, separators=(',', ': ')))
