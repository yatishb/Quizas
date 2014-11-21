function barChartIdFor(gameId) {
    // Kindof assumes that you don't show the same graph from the perspective
    // of two different users at the same time. (That would be a conflict).
    return "stackedBarGraph_" + fsid.replace(":", "");
}

// `outputStatsForGame` assumes that the `graphDivId` already exists.
// You can create it with jQuery in the following way, appending to
// #gameLineGraphs (say):
//   $("<div/>", { "id": lineGraphId  }).appendTo("#gameLineGraphs");
// I suggest using `barChartIdFor`
function outputStatsForFlashset(user_id, fsid, fsGraphId) {
    // var fsid = "quizlet:57054880"

    $.get("/api/user/" + user_id + "/stats/sets/" + fsid, function (data) {

        // Yo dawg, I herd you liked AJAX
        // (We need to get the *contents* of the FlashSet in order to
        //  create a useful visualisation).
        $.get("/api/sets/" + fsid, function (setData) {
            var fs = JSON.parse(setData);

            // Map fs.cards {id, question, answer} to {id -> {question, answer}}
            var flashsetDict = {};
            fs.cards.forEach(function (fc) {
                flashsetDict[fc.id] = { question: fc.question,
                                        answer  : fc.answer };
            });

            outputFlashsetBarGraph(fsGraphId, JSON.parse(data), flashsetDict);
        });
    });
}

function outputFlashsetBarGraph (graphId, flashsetResults, flashsetDict) {

    // draws
    // played
    // fcids: []
    // wins
    // losses
    // flashcards: fcid -> {correct: #, total: #}
    // gameids: []

    // Computations we'll need for constructing the bar chart
    var numFlashcardsWithResults = flashsetResults.fcids.filter(function (fcid) {
        return flashsetResults.flashcards[fcid] !== undefined;
    }).length;

    var graphWidth = 600;
    var graphHeight = 45 * numFlashcardsWithResults;

    var data = flashsetResults.fcids.map(function (fcid) {
        var result = flashsetResults.flashcards[fcid];

        return { fcid: fcid,
                 question: flashsetDict[fcid].question,
                 correct: result.correct,
                 total: result.total }
    });

    var maxTotal = d3.max(data, function(d) { return d.total; });

    var margin = {top: 20, right: 20, bottom: 20, left: 20};
    var width = graphWidth - margin.left - margin.right;
    var height = graphHeight - margin.top - margin.bottom;

    var pGapBetweenBars = 0.05; // padding, proportion of bar thickness.
    var x = d3.scale.linear().range([0, width]);
    var y = d3.scale.ordinal().rangeRoundBands([0, height], pGapBetweenBars);

    var svg = d3.select("#" + graphId).append("svg")
        .attr("class", "bargraph")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", 
              "translate(" + margin.left + "," + margin.top + ")");

    x.domain([0, 1]);
    y.domain(data.map(function(d) { return d.fcid; }));

    // "Correct" Clip Rects
    function correctClipRectId(i) { return graphId + "_correctClip" + i; };
    function refCorrectClipRectId(d, i) { return "url(#" + correctClipRectId(i) + ")"; }
    svg.append("defs").selectAll("bar") // why does it need selectAll here??
        .data(data)
      .enter().append("clipPath")
        .attr("id", function(d, i) { return correctClipRectId(i); })
      .append("rect")
        .attr("x", function(d) { return x(0); })
        .attr("width", function(d) { return x(d.correct / d.total); })
        .attr("y", function(d) { return y(d.fcid); })
        .attr("height", y.rangeBand())

    // "Incorrect" Clip Rects
    function incorrectClipRectId(i) { return graphId + "_incorrectClip" + i; };
    function refIncorrectClipRectId(d, i) { return "url(#" + incorrectClipRectId(i) + ")"; }
    svg.append("defs").selectAll("bar") // why does it need selectAll here??
        .data(data)
      .enter().append("clipPath")
        .attr("id", function(d, i) { return incorrectClipRectId(i); })
      .append("rect")
        .attr("x", function(d) { return x(d.correct / d.total); })
        .attr("width", function(d) { return x((d.total - d.correct) / d.total); })
        .attr("y", function(d) { return y(d.fcid); })
        .attr("height", y.rangeBand())

    // Green, "Correct" bar
    svg.selectAll("bar")
        .data(data)
      .enter().append("rect")
        .attr("class", "correct bar")
        .attr("x", function(d) { return x(0); })
        .attr("width", function(d) { return x(d.correct / d.total); })
        .attr("y", function(d) { return y(d.fcid); })
        .attr("height", y.rangeBand())

    // Red, "Incorrect" bar
    svg.selectAll("bar")
        .data(data)
      .enter().append("rect")
        .attr("class", "incorrect bar")
        .attr("x", function(d) { return x(d.correct / d.total); })
        .attr("width", function(d) { return x((d.total - d.correct) / d.total); })
        .attr("y", function(d) { return y(d.fcid); })
        .attr("height", y.rangeBand());

    // Text for # correct answers
    svg.selectAll("bar")
        .data(data)
      .enter().append("text")
        .attr("class", "correct score")
        .attr("x", 10)
        .attr("y", function(d) { return y(d.fcid); })
        .attr("dy", y.rangeBand() * 3 / 5) // Fiddly. Really, this will depend on font size.
        .style("text-anchor", "start")
        .style("font-size", (y.rangeBand() / 2) + "px")
        .style("clip-path", refCorrectClipRectId)
        .text(function(d) { return d.correct; })

    // Text for # incorrect answers
    svg.selectAll("bar")
        .data(data)
      .enter().append("text")
        .attr("class", "incorrect score")
        .attr("x", function(d) { return x(1) - 10; })
        .attr("y", function(d) { return y(d.fcid); })
        .attr("dy", y.rangeBand() * 3 / 5) // Fiddly. Really, this will depend on font size.
        .style("text-anchor", "end")
        .style("font-size", (y.rangeBand() / 2) + "px")
        .style("clip-path", refIncorrectClipRectId)
        .text(function(d) { return d.total - d.correct; })

    // Question text. (Correct half)
    svg.selectAll("bar")
        .data(data)
      .enter().append("text")
        .attr("class", "correct word")
        .attr("x", function(d) { return x(0.5); })
        .attr("y", function(d) { return y(d.fcid); })
        .attr("dy", y.rangeBand() * 3 / 4) // Fiddly. Really, this will depend on font size.
        .style("text-anchor", "middle")
        .style("font-size", (y.rangeBand() * 3 / 4) + "px")
        .style("clip-path", refCorrectClipRectId)
        .text(function(d) { return d.question; })

    // Question text. (Incorrect half)
    svg.selectAll("bar")
        .data(data)
      .enter().append("text")
        .attr("class", "incorrect word")
        .attr("x", function(d) { return x(0.5); })
        .attr("y", function(d) { return y(d.fcid); })
        .attr("dy", y.rangeBand() * 3 / 4) // Fiddly. Really, this will depend on font size.
        .style("text-anchor", "middle")
        .style("font-size", (y.rangeBand() * 3 / 4) + "px")
        .style("clip-path", refIncorrectClipRectId)
        .text(function(d) { return d.question; })
}
