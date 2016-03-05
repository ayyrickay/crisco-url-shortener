/*--------------------------
establishing basis margin
----------------------------*/
var margin = {top: 20, right: 30, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height= 500 - margin.top - margin.bottom;

/*--------------------------
Linear scale of chart data
----------------------------*/
var yScale = d3.scale.linear()
    .range([height, 0]);

var xScale = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

/*--------------------------
Chart Axes (x && y)
----------------------------*/
var xAxis = d3.svg.axis()
    .scale(xScale)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(yScale)
    .orient("left");

/*--------------------------
Fundamental Chart
----------------------------*/
var chart = d3.select(".chart")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

/*--------------------------
Adding a tooltip
----------------------------*/
var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function(d) { return "<strong>Members: </strong><span style='color:#E74C3C'>" + d.member_count + "</span>" + "<br><strong>Latitude: </strong><span style='color:#E74C3C'>" + d.lat + "</span>";})

chart.call(tip);

/*--------------------------
Adding JSON Meetup Data
----------------------------*/
d3.json("/assets/json/meetups.json", function(error,data) {
    data.results.forEach(function(d){
        d.member_count = +d.member_count;
        d.lat = +d.lat;
        d.lon = +d.lon;
    });
    
    xScale.domain(data.results.map(function(d) {return d.city; }));
    yScale.domain([0, d3.max(data.results, function(d) {return d.member_count; })]);

    chart.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    chart.append("g")
        .attr("class", "y axis")
        .call(yAxis)
       .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 1)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Number of People Attending Meetups");

    chart.selectAll("bar")
        .data(data.results)
    .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d){ return xScale(d.city); })
        .attr("y", height)
        .attr("height", 0)
        .attr("width", xScale.rangeBand())
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide)
    .transition()
      .delay(400)
      .duration(1500)
      .attr("y", function(d){ return yScale(d.member_count); })
      .attr("height", function(d) { return height - yScale(d.member_count); })
        .call(yAxis);
    
    d3.select("input").on("change", change);
    
    var sortTimeout = setTimeout(function(){
        d3.select("input").property("checked", true).each(change);},2000);
    
    /*--------------------------
    Adding JSON Meetup Data
    ----------------------------*/
    function change(){
        clearTimeout(sortTimeout);
        
        var x0 = xScale.domain(data.results.sort(this.checked
            ? function(a, b){ return a.lat - b.lat; }
            : function(a, b){ return d3.descending(a.member_count, b.member_count);})
            .map(function(d){return d.city;}))
            .copy();
        
        chart.selectAll(".bar")
        .sort(function(a, b) { return x0(a.member_count) - x0(b.member_count); });
        
        var transition = chart.transition().duration(750),
        delay = function(d, i) { return i * 50; };
        
        transition.selectAll(".bar")
        .delay(delay)
        .attr("x", function(d) {return x0(d.city); });
        
        transition.select(".x.axis")
            .call(xAxis)
          .selectAll("g")
            .delay(delay);
        }
});


function type(d){
    d.member_count = +d.member_count; //force member_count to int
    console.log(d.member_count);
    return d;
}
