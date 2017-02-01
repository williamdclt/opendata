
function artist(_id_artist){
    // Efface les informations déjà affichées
    d3.select("#artists").selectAll("*").remove();
    // Affiche le conteneur d'artiste
    d3.select("#artist").style("display","inline-block");

    var svg = d3.select("#artists"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    // Simulation des forces entre les cercles représentant les oeuvres
    var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }).distance(150))
    .force("charge", d3.forceManyBody().strength(-2000))
    .force("collision", d3.forceCollide(50) )
    .force("center", d3.forceCenter(width / 2, height / 2));

    d3.json("collection/artists/"+_id_artist+".json", function(error, graph) {
        if (error) throw error;

        // Création des liens entre l'artiste et ses oeuvres
        var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", "1");

        // Création des cercles pour les oeuvres et l'artiste
        var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("r", function(d){return d.size;})
        .attr("fill", function(d){return "url(#image"+d.id+")"})
        .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
        .on("click", redirect); // Ouvre la page d'information de l'oeuvre ou de l'artiste

        // Ajout des images
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
        .attr("viewBox","0 0 256 256");

        // Ajout d'un fond blanc pour remplir le cercle
        pictures.append("rect")
        .attr("fill","white")
        .attr("width","256")
        .attr("height","256");

        pictures.append("image")
        .attr("xlink:href",function(d){
            if(d.id == "Artist"){ // Si c'est un artiste on affiche une image en fonction de son genre
                return d.gender ? "assets/"+d.gender+".png" : "assets/female.png";
            }
            // Si l'image n'est pas disponible on affiche le logo copyright
            return d.url != "" ? d.url : "assets/copyright.png";
        })
        .attr("width","256")
        .attr("height","256");

        node.append("title").text(function(d) { return d.name; });

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

    function redirect(d) {
        window.open(d.tatelink)
    }
}
