parse(main);

function main(artists) {
    artists.forEach(function (artist) {
        console.log(artist.name + " " + artist.artworks.length);
        artist.artworks.forEach(function (artwork) {
        });
    });
}
