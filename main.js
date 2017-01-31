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
var currentDepth = 0;

var svg = d3.select("svg"),
    margin = 20,
    diameter = +svg.attr("width"),
    g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

var pack = d3.pack()
     .size([diameter - margin, diameter - margin])
     .padding(2);


var color = d3.scaleLinear()
    .domain([-1, 5])
    .range(["rgb(234, 251, 255)", "rgb(21, 154, 178)"])
    .interpolate(d3.interpolateHcl);

function main(countries) {
    root = d3.hierarchy(countries)
        .sum(function(d) { return d.size; })
        .sort(function(a, b) { return b.value - a.value; });

    /*function collapse(d) {
        if (d.children) {
            d._children = d.children;
            d._children.forEach(collapse);
            d.children = null;
        }
    }

    root.children.forEach(collapse);*/

    var focus = root,
        nodes = pack(root).descendants(),
        view;

    var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("class", function(d) { return d.parent ? (d.children ? "node" : "node node--leaf") : "node node--root"; })
        .style("fill", function(d) { return d.children ? color(d.depth) : null; })
        .style("display", function(d) { return d.parent === root || d.depth == 0 ? "inline" : "none"; })
        .on("click", function(d) {
            /*if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }*/

            currentDepth = d.depth;
            console.log(currentDepth);
            if (focus !== d)
                zoom(d), d3.event.stopPropagation();

        });

    var text = g.selectAll("text")
        .data(nodes)
        .enter().append("text")
        .attr("class", "label")
        .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
        .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
        .text(function(d) { return d.data.name; });

    var node = g.selectAll("circle,text");

    // Ajout d'un event qui dézoome sur l'ensemble du graphe au clic sur le background du svg
    svg.style("background", color(-1))
        .on("click", function() { zoom(root); currentDepth = 0 });

    zoomTo([root.x, root.y, root.r * 2 + margin]);


    function zoom(d) {
        var focus0 = focus;
        focus = d;

        var transition = d3.transition()
            .duration(d3.event.altKey ? 7500 : 750)
            .tween("zoom", function(d) {
                var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
                return function(t) { zoomTo(i(t)); };
            });

        transition.selectAll("text")
            .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
            .style("fill-opacity", function(d) { return d.parent === focus ? 1 : 0; })
            .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
            .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });

        transition.selectAll("circle")
            .filter(function(d) {
                // Retourne tous les noeuds de même niveau que le noeud sur lequel on a cliqué +
                // les noeuds children
                return this.style.display === "inline" || d.parent === focus
            })
            .style("fill-opacity", function(d) {
                return d.parent === focus || d === focus ? 1 : 0;
            })
            .on("start", function(d) {
                 if (d.parent === focus)
                    this.style.display = "inline";
            })
            .on("end", function(d) {
                if (d.parent !== focus && d !== focus && d !== root)
                    this.style.display = "none";
            });

    }

    function zoomTo(v) {
        var k = diameter / v[2];
        view = v;
        node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
        circle.attr("r", function(d) { return d.r * k; });
    }
}
