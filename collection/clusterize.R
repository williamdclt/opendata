# 0 acno
# 1 acquisitionYear
# 2 group
# 3 date
# 4 width
# 5 height
# 6 depth
# 7 medium
weight <- c(0, 1, 1, 1, 1, 1, 1, 1);
k = 10;
nbAw = 200;

tmp <- read.csv("to_cluster.csv", sep=",", row.names=NULL);
artworks = as.data.frame(tmp);
artworks$title = as.factor(artworks$title)
artworks$acquisitionYear <- as.numeric(artworks$acquisitionYear);
artworks$group <- as.factor(artworks$group);
artworks$date <- as.numeric(artworks$date);
artworks$width <- as.numeric(artworks$width);
artworks$height <- as.numeric(artworks$height);
artworks$depth <- as.numeric(artworks$depth);
artworks$medium <- as.factor(artworks$medium);
artworks = artworks[!duplicated(artworks$title),]
rownames(artworks) <- artworks$title

dissimilarities = cluster::daisy(artworks[0:nbAw,], "gower", weights = weight)

dendo <- hclust(dissimilarities, "complete")

write(as.character(artworks$title[0:nbAw]), file = paste("acno"), ncolumns = nbAw)
write(cluster$clustering, file = paste("clustering", k), ncolumns = nbAw)
library(jsonlite)

options(expressions = 10000)
halfway <- hclustToTree(dendo)
jsonTree <- jsonlite::toJSON(halfway, pretty = FALSE)
write(substr(jsonTree, 2, nchar(jsonTree)-1), file = "tree.json", ncolumns = nbAw)
