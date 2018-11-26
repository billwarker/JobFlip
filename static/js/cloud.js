var word_freqs = {{ word_freqs|safe }};
max_freq = {{ max_freq }};
fill = d3.scale.category20();
layout = d3.layout.cloud()
    .size([1000, 500])
    .words(word_freqs)
    .padding(5)
    .rotate(0)
    .font("Impact")
    .fontSize(function(d) {
        return (d.size/max_freq)*100;
    })
    .on("end", draw);
layout.start();
function draw(words) {
    d3.select("body").append("svg")
    .attr("width", layout.size()[0])
    .attr("height", layout.size()[1])
    .attr("style", "display: block; margin-left: auto; margin-right: auto; text-align: center;")
    .append("g")
    .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
    .selectAll("text")
    .data(words)
    .enter().append("text")
    .style("font-size", function(d) { return d.size + "px"; })
    .style("font-family", "Impact")
    .style("fill", function(d, i) { return fill(i); })
    .attr("text-anchor", "middle")
    .attr("transform", function(d) {
        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
    })
    .text(function(d) { return d.text; });
}