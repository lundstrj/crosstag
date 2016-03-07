window.onload = function() {
    
    var counter = 0;
    var display_user = false;
    var user_data = null;
    var display_time = 20;
    var sleep_time = 2;
<<<<<<< HEAD
    var current_user = null;

    

    //Asks the server if there's a new tagevent
    function poll_server(callback) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "http://localhost:80/crosstag/v1.0/last_tagin", true);
            xhr.addEventListener("load", function(){
                callback(display_user_after_user_data_set, JSON.parse(xhr.response));
            });
            xhr.send(null);
        }
        catch (exception){
            return null
        }
    }
=======
>>>>>>> 8360843e917631a2ceb53e721ba4f847dc6e5ec1

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
            document.getElementById("tagin_month").innerHTML = user_data.tagins;
        }
    };


    top_five_tag();

    function top_five_tag() {
        try{
           var xhr = new XMLHttpRequest();
           xhr.open("GET", "http://localhost:80/crosstag/v1.0/static_top_five", true);
           xhr.addEventListener("load", function(){
               var data_arr = JSON.parse(xhr.response);
               console.log(data_arr);
               //print_top_five(data_arr);
           });

           xhr.send();
       }
        catch(exception){
            return null;
        }
    }

<<<<<<< HEAD
    function top_five_tag() {
        try{
           var xhr = new XMLHttpRequest();
           xhr.open("GET", "http://localhost:80/crosstag/v1.0/static_top_five", true);
           xhr.addEventListener("load", function(){

                var r = JSON.parse(xhr.response);

           });

           xhr.send();
       }
        catch(exception){
            return null;
        }
    }

    function print_top_five(user_data) {
        // Create a table. Make loop that runs 5 times. In the loop, append these to elements.
        console.log(user_data);
    }
        //document.getElementById("top_five_user_name").innerHTML = user_data.name;
        //document.getElementById("tag_amount").innerHTML = user_data.amount;

    //Controls if a object is empty or not
    function is_not_empty(object){
        for(var key in object){
            if(object.hasOwnProperty(key)){
                return true;
            }
        }
        return false;
    }
=======
    function print_top_five(user_data) {
        // Create a table. Make loop that runs 5 times. In the loop, append these to elements.
        var test = document.createElement("label");
        test.innerHTML = user_data['name'];
        document.getElementById("top-five").appendChild(test);
>>>>>>> 8360843e917631a2ceb53e721ba4f847dc6e5ec1

        //document.getElementById("top_five_user_name").innerHTML = user_data.name;
        //document.getElementById("tag_amount").innerHTML = user_data.amount;
    }

    //Controls if the user should be shown, for how long and removes the diaplyed user from the page
    function CheckTagins() {
        if (!user_data && display_user) {
            //print("read tag: %s" % current['tag_id'])
            display_user = false
        }

        if (display_user && user_data && counter == 0) {
            //this.print_user(this.user_data, this.user_tagins);
            //print_user(user_data, user_tagins);
            counter += 1
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
};