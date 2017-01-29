function parse(callback) {
    d3.csv("collection/artist_data.csv", function (artists) {
        retypeArtists(artists);

        d3.csv("collection/artwork_data.csv", function (artworks) {
            retypeArtworks(artworks);

            artists.forEach(function (artist) {
                artist.artworks = artworks.filter(function (artwork) {
                    artwork.artistId == artist.id;   
                });
            });

            callback(artists);
        });
    });
}

function retypeArtists(artists) {
    artists.forEach(function (artist) {
        artist.id = +artist.id;
        artist.yearOfBirth = +artist.yearOfBirth;
        artist.yearOfDeath = +artist.yearOfDeath;
    });
}

function retypeArtworks(artworks) {
    artworks.forEach(function (artwork) {
        artwork.id = +artwork.id;
        artwork.artistId = +artwork.artistId;
        artwork.year = +artwork.year;
        artwork.acquisitionYear = +artwork.acquisitionYear;
        artwork.dimensions = {
            width: +artwork.width,
            height: +artwork.height,
            depth: +artwork.depth,
            unit: artwork.unit,
        };
    });
}
