// The parse() function (parse.js) expect a callback to which it will
// send the collection of artists. The index in the array is NOT the
// ID of the artist
parse(main);

/**
 * Properties of an Artist object:
 * id
 * name
 * yearOfBirth
 * yearOfDeath
 * placeOfBirth ("city, country" | "country")
 * placeOfDeath ("city, country" | "country")
 * gender ("Female" | "Male")
 * artworks (array of Artwork objects)
 */

/**
 * Properties of an Artwork object:
 * id
 * artist (theoretically equivalent to its artist name)
 * artistId (equivalent to its artist id)
 * title
 * medium
 * year
 * dimension (Dimension object)
 */

/**
 * Properties of a Dimension object:
 * width
 * height
 * depth
 * unit
 */

function main(artists) {
    artists.forEach(function (artist) {
        console.log(artist.name + " " + artist.artworks.length);
      //  $("body").append(artist.name + " " + artist.artworks.length+"</br>");
        artist.artworks.forEach(function (artwork) {
        });
    });
}
