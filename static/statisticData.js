"use strict";
var statistic = {};

statistic.Main = (function(){

});

statistic.Main.prototype.genderStats = function(stats) {
    //renders a pie chart, shows gender stats from the database.
    var data1 = [
    {
        value: stats[0][0],
        color:"#00759C",
        highlight: "#00759C",
        label: "Men"
    },
    {
        value: stats[0][1],
        color: "#FF19A7",
        highlight: "#FF19A7",
        label: "Women"
    },

    {
        value: stats[0][2],
        color: "#878787",
        highlight: "#878787",
        label: "Unknown"
    }
]
    var options = {
	segmentShowStroke : false,
	animateScale : true
    }
    var chart1 = document.getElementById("genderChart").getContext("2d");
    new Chart(chart1).Pie(data1, options);

}

statistic.Main.prototype.genderTags = function(stats) {
    //renders a pie chart, shows the gender statistic from the latest 4 weeks.
    var data = [
    {
        value: stats[1][0],
        color:"#00759C",
        highlight: "#00759C",
        label: "Men"
    },
    {
        value: stats[1][1],
        color: "#FF19A7",
        highlight: "#FF19A7",
        label: "Women"
    },

    {
        value: stats[1][2],
        color: "#878787",
        highlight: "#878787",
        label: "Unknown"
    }
]
    var options = {
	segmentShowStroke : false,
	animateScale : true
    }
    var chart1 = document.getElementById("genderChart1").getContext("2d");
    new Chart(chart1).Pie(data, options);


}

statistic.Main.prototype.tagsByMonths = function(stats) {
    //renders a bar chart with the tags per month.
    var data = {
    labels: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    datasets: [
        {
            label: "Tags this year",
            fillColor: "rgba(220,220,220,0.2)",
            strokeColor: "rgba(0, 114, 255, 0.9)",
            pointColor: "rgba(220,220,220,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data:
                [stats[2][0],
                stats[2][1],
                stats[2][2],
                stats[2][3],
                stats[2][4],
                stats[2][5],
                stats[2][6],
                stats[2][7],
                stats[2][8],
                stats[2][9],
                stats[2][10],
                stats[2][11]]
        },
      ]
    };

    var options = {
	segmentShowStroke : false,
	animateScale : true
    }


     var chart1 = document.getElementById("tagChart").getContext("2d");
     new Chart(chart1).Bar(data, options);

}

statistic.Main.prototype.ageOfMembers = function(stats) {
    //renders a bar chart with the tags per month.
    var data = {
    labels: ["15-25", "26-35", "36-45", "46-55", "56-65", "65+"],
    datasets: [
        {
            label: "Age",
            fillColor: "rgba(220,220,220,0.2)",
            strokeColor: "rgba(0, 114, 255, 0.9)",
            pointColor: "rgba(220,220,220,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data:
                [stats[3][0],
                stats[3][1],
                stats[3][2],
                stats[3][3],
                stats[3][4],
                stats[3][5]]

        },
      ]
    };

    var options = {
	segmentShowStroke : false,
	animateScale : true
    }


     var chart1 = document.getElementById("ageChart").getContext("2d");
     new Chart(chart1).Bar(data, options);

}