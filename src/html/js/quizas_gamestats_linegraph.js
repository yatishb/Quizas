function lineGraphIdFor(gameId) {
    // Kindof assumes that you don't show the same graph from the perspective
    // of two different users at the same time. (That would be a conflict).
    return "ID" + gameId + "gameLineGraph";
}



// `outputStatsForGame` assumes that the `graphDivId` already exists.
// You can create it with jQuery in the following way, appending to
// #gameLineGraphs (say):
//   $("<div/>", { "id": lineGraphId  }).appendTo("#gameLineGraphs");
// I suggest using `lineGraphIdFor`
// HOWEVER, no assumption is made about what the id is. So. Go figure.
function outputStatsForGame(user_id, gameId, graphDivId) {
    $.get("/api/user/" + user_id + "/stats/game/" + gameId, function (data) {
        // Line chart!
        outputGameResultsLineChart(lineGraphIdFor(gameId), JSON.parse(data));
    });
}



function outputGameResultsLineChart(lineGraphId, gameResults) {
    // constraints: two opponents. (gameResults makes this constraint, also).

    // Compute the Div width/height based on the div size.
    var divWidth = $("#" + lineGraphId).width();
    var divHeight = $("#" + lineGraphId).height();
    var graphWidth = divWidth;
    var graphHeight = divHeight || (graphWidth * 0.75);

    // againstUser : userid
    // result
    // questions : #
    // flashcards:[{ enemy: fcid
    //               question: fcid
    //               ans: fcid }]
    var maxResult = gameResults.questions;

    // implementation adapted from http://bl.ocks.org/benjchristensen/2579599
    // implementation heavily influenced by http://bl.ocks.org/1166403

    // define dimensions of graph
    var m = [80, 80, 80, 80]; // margins
    var w = graphWidth  - m[1] - m[3]; // width
    var h = graphHeight - m[0] - m[2]; // height


    // create a simple data array that we'll plot with a line
    // (this array represents only the Y values,
    //  X will just be the index location)
    var userData = [0];
    var oppoData = [0];

    // Construct data from `gameResults`
    for (var i = 0; i < gameResults.flashcards.length; i += 1) {
        var fc = gameResults.flashcards[i];
        userData.push(fc.question === fc.ans   ? userData[i] + 1 : userData[i]) ;
        oppoData.push(fc.question === fc.enemy ? oppoData[i] + 1 : oppoData[i]) ;
    }


    // X scale will fit all values from data[] within pixels 0-w
    var x = d3.scale.linear().domain([0, userData.length - 1]).range([0, w]);
    // Y scale will fit values from 0-10 within pixels h-0
    // (Note the inverted domain for the y-scale => bigger is up!)
    var y = d3.scale.linear().domain([0, maxResult]).range([h, 0]);

    // create a line function that can convert data[] into x and y points
    var line = d3.svg.line()
        .x(function(d,i) { // assign the X function to plot our line as we wish
            return x(i);
        })
        .y(function(d) {
            return y(d);
        })

    // Add an SVG element with the desired dimensions and margin.
    var graph = d3.select("#" + lineGraphId).append("svg:svg")
        .attr("class", "linegraph")
        .attr("width", w + m[1] + m[3])
        .attr("height", h + m[0] + m[2])
        .append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

    // create axes
    var xAxis = d3.svg.axis().scale(x)
        .ticks(maxResult).tickSize(-h).tickSubdivide(true);
    var yAxisLeft = d3.svg.axis().scale(y)
        .ticks(maxResult / 2).orient("left");

    // Add axes
    graph.append("svg:g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + h + ")")
        .call(xAxis);
    graph.append("svg:g")
        .attr("class", "y axis")
        .attr("transform", "translate(-25,0)")
        .call(yAxisLeft);

    // Score Lines
    graph.append("svg:path").attr("d", line(userData))
        .attr("class", "line user")
    graph.append("svg:path").attr("d", line(oppoData))
        .attr("class", "line opponent")
}

