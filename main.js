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

var svg = d3.select("#map"),
margin = 20,
diameter = +svg.attr("width"),
g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

var pack = d3.pack()
.size([diameter - margin, diameter - margin])
.padding(2);


var color = d3.scaleLinear()
.domain([0, 1])
.range(["rgb(253, 63, 146)", "rgb(4, 109, 154)"])
.interpolate(d3.interpolateHcl);

function main(countries) {
    root = d3.hierarchy(countries)
    .sum(function(d) { return d.size; });

    var focus = root,
    nodes = pack(root).descendants(),
    view;

    var circle = g.selectAll("circle")
    .data(nodes)
    .enter().append("circle")
    .attr("class", function(d) { return d.parent ? (d.children ? "node" : "node") : "node node--root"; })
    .style("fill", function(d) { return color(d.data.ratio); })
    .style("display", function(d) { return d.parent === root || d.depth == 0 ? "inline" : "none"; })
    .on("click", function(d) {
        currentDepth = d.depth;

        if(! d.children){
            artist(d.data.id);
            console.log(d.data.id);
            d3.event.stopPropagation();
        }
        else{
            if (focus !== d)
                zoom(d), d3.event.stopPropagation();
            else
                zoom(d.parent), d3.event.stopPropagation();
        }



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
    svg.style("background", "rgb(108, 142, 186)")
    .on("click", function() { console.log("svg"); zoom(root); currentDepth = 0 });

    zoomTo([root.x, root.y, root.r * 2 + margin]);

    function zoom(d) {
        var focus0 = focus;
        focus = d;

        d3.select("#infos").text("Level : "+d.data.level+", "+d.data.name);
        var transition = d3.transition()
        .duration(d3.event.altKey ? 7500 : 750)
        .tween("zoom", function(d) {
            var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
            return function(t) { zoomTo(i(t)); };
        });

        transition.selectAll("text")
        .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
        .style("fill-opacity", function(d) { return d.parent === focus ? 1 : 0; })
        .style("stroke-opacity", function(d) { return d.parent === focus ? 1 : 0; })
        .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
        .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });

        transition.selectAll("circle")
        .filter(function(d) {
            return d.parent === focus || this.style.display === "inline"
        })
        .style("fill-opacity", function(d) {
            return d.parent === focus || d.depth <= currentDepth ? 1 : 0;
        })
        .on("start", function(d) {
            if (d.parent === focus || d.depth <= currentDepth)
            this.style.display = "inline";
        })
        .on("end", function(d) {
            if (d.parent !== focus && d !== focus && d !== root && d.depth > currentDepth)
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

function artist(_id_artist){
    d3.select("#artists").selectAll("*").remove();
    var svg = d3.select("#artists"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }).distance(200))
    .force("charge", d3.forceManyBody().strength(-1000))
    .force("center", d3.forceCenter(width / 2, height / 2));

    d3.json("collection/artists/"+_id_artist+".json", function(error, graph) {
        if (error) throw error;

        var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

        var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("r", function(d){return d.size;})
        .attr("fill", function(d){return "url(#image"+d.id+")"})
        //.attr("fill", function(d) { return color(d.group); })
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

          console.log(graph.nodes);
          var pictures = svg.append("defs")
          .selectAll("pattern")
          .data(graph.nodes)
          .enter()
          .append("pattern")
          .attr("id", function(d){return "image"+d.id;})
          .attr("x", "0%")
          .attr("y", "0%")
          .attr("height", "100%")
          .attr("width", "100%")
          .attr("viewBox", "0 0 512 512");

          pictures.append("rect")
          .attr("fill","white")
          .attr("width","512")
          .attr("height","512");

          pictures.append("image")
          .attr("xlink:href",function(d){return d.url != "" ? d.url : "copyright.png";})
          .attr("width","512")
          .attr("height","512");




        node.append("title")
        .text(function(d) { return d.id; });

        simulation.nodes(graph.nodes).on("tick", ticked);

        simulation.force("link").links(graph.links);

        function ticked() {
            link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

            node
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
        }
    });

        function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }

    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
}
