//establishing basis margin
var margin = {top: 20, right: 30, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height= 500 - margin.top - margin.bottom;

var dataSet = [];

//import JSON format data from meetup API
    d3.json("/assets/json/meetups.json", function(error, data){
        start(data)
    });

var yScale = d3.scale.linear()
    .range([height, 0]);

var xScale = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

//the chart where all the magic happens
var chart = d3.select(".chart")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var bar = chart.selectAll("g.bar")
    .data(dataSet)

//start function for bar chart data
var start = function(data) {
    xScale.domain(data.results.map(function(d) {return d.city; }));
    
    yScale.domain([0, d3.max(data.results, function(d) {return d.member_count; })]);
    
    //binding data
    g = chart.selectAll(".cityData")
        .data(data.results)
        .enter().append("g")
            .attr("class", "cityData")
    };

function columnChart(){

    //Graph axes
    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");
    
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

    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) { return "<strong>Members: </strong><span style='color:#E74C3C'>" + d.member_count + "</span>";})

    chart.call(tip);
    
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

    function type(d){
        d.member_count = +d.member_count; //force member_count to int
        console.log(d.member_count);
        return d;
    }
}

function buildScatter(){
    var xScale = d3.scale.linear()
        .domain()
}

columnChart()
