window.onload = function() {
    
    var counter = 0;
    var display_user = false;
    var user_data = null;
    var display_time = 30;
    var sleep_time = 2;


    var eventSource = new EventSource("/stream");
    eventSource.onmessage = function(e){
        if(e.data != 'None'){
            user_data = JSON.parse(e.data);
            display_user = true;
            counter = 0;
            document.getElementById("tagins").style.visibility = 'visible';
            document.getElementById("user_name").innerHTML = user_data.name;
            document.getElementById("status_member").innerHTML = user_data.status;
            document.getElementById("expire_date").innerHTML = user_data.expiry_date;
            document.getElementById("create_date").innerHTML = user_data.create_date;
            document.getElementById("user_email").innerHTML = user_data.email;
            document.getElementById("tagin_month").innerHTML = user_data.tagcounter;

        }
    };

    //Controls if the user should be shown, for how long and removes the diaplyed user from the page
    function CheckTagins() {
        if (!user_data && display_user) {
            //print("read tag: %s" % current['tag_id'])
            display_user = false;
        }

        if (display_user && user_data && counter == 0) {
            //this.print_user(this.user_data, this.user_tagins);
            //print_user(user_data, user_tagins);
            counter += 1;
            top_five_tag();
        }

        if (display_user && user_data && counter != 0) {
            counter += 1;
        }

        if (counter >= display_time / sleep_time) {
            counter = 0;
            display_user = false;
            user_data = null;
            document.getElementById("tagins").style.visibility = 'hidden';
            //this.print_clear_screen("online")
        }
    }


    setInterval(function(){
        CheckTagins();
    }, 1000);


    function top_five_tag() {
        try{
           var xhr = new XMLHttpRequest();
           xhr.open("GET", "http://192.168.0.90:80/crosstag/v1.0/static_top_five", true);
           xhr.addEventListener("load", function(){
               var data_arr = JSON.parse(xhr.response);

               console.log(data_arr);
               if(data_arr['json_arr'] != null) {
                   if (data_arr['json_arr'].length == 5) {
                       //data_arr['json_arr'].sort(function (a, b) {
                       //    return parseFloat(b.amount) - parseFloat(a.amount);
                       //});
                       print_top_five(data_arr);
                   }
               }
           });

           xhr.send();
       }
        catch(exception){
            return null;
        }
    }

     function print_top_five(user_data) {
         var data = {
             labels: [user_data['json_arr'][0]['name'], user_data['json_arr'][1]['name'], user_data['json_arr'][2]['name'],
                        user_data['json_arr'][3]['name'], user_data['json_arr'][4]['name']],
             datasets: [
                 {
                     label: "Topp 5 taggningar denna månad",
                     fillColor: "rgba(255,105,180,0.2)",
                     strokeColor: "rgba(255,105,180,0.9)",
                     pointColor: "rgba(220,220,220,1)",
                     pointStrokeColor: "#fff",
                     pointHighlightFill: "#fff",
                     pointHighlightStroke: "rgba(220,220,220,1)",
                     data: [user_data['json_arr'][0]['amount'],
                            user_data['json_arr'][1]['amount'],
                            user_data['json_arr'][2]['amount'],
                            user_data['json_arr'][3]['amount'],
                            user_data['json_arr'][4]['amount']]
                 }
             ]
         };

         var options = {
             segmentShowStroke: false,
             animateScale: true,
             showTooltips: false,
             animationSteps: 4,
             animationEasing: 'easeInCubic',
             scaleFontStyle: "bold",
             onAnimationComplete: function () {

                 var ctx = this.chart.ctx;
                 ctx.font = this.scale.font;
                 ctx.fillStyle = this.scale.textColor;
                 ctx.textAlign = "center";
                 ctx.textBaseline = "bottom";
                 this.datasets.forEach(function (dataset) {
                     dataset.bars.forEach(function (bar) {
                         if (bar.value !== 0) {
                             ctx.fillText(bar.value, bar.x, bar.y);
                         }
                     });
                 })
             }
         };

         var chart1 = document.getElementById("top-five-chart").getContext("2d");
         new Chart(chart1).Bar(data, options);
     }
    top_five_tag();
};
