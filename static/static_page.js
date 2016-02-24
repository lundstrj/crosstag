window.onload = function() {

    var last_event = null;
    var counter = 0;
    var display_user = false;
    var user_data = null;
    var user_tagins = null;
    var display_time = 20;
    var sleep_time = 2;
    var current_user = null;


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

    function check_if_tagevent_exists(callback, current){
        if (current == null) {
            display_user = false;
            console.log("current = null")
        }
        else if(is_not_empty(current)){
            if (current['index'] != last_event) {
                last_event = current['index'];
                display_user = true;
                counter = 0;
                current_user = current;
                callback();
            }
        }
    }

    function display_user_after_user_data_set(){
        if (display_user && counter >= 0) {
            get_user_data(set_user_data, current_user['tag_id'])
        }
    }

    function get_user_data(callback, tag_nbr) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "http://localhost:80/crosstag/v1.0/get_user_data_tag/" + tag_nbr, true);
            xhr.addEventListener("load", function(){
                callback(JSON.parse(xhr.response));
            });
            xhr.send(null);
        }
        catch(exception) {
            return null
        }
    }

    function set_user_data(data){
        user_data = data;
    }

    function is_not_empty(object){
        for(var key in object){
            if(object.hasOwnProperty(key)){
                return true;
            }
        }
        return false;
    }


    function print_user(user_data, user_tagins){
        if(is_not_empty(user_data)){
            console.log(user_data)
            document.getElementById("tagins").innerHTML = user_data.name;
        }

    }

    function CheckTagins() {
        if (!user_data && display_user) {
            //print("read tag: %s" % current['tag_id'])
            display_user = false
        }

        if (display_user && user_data && counter == 0) {
            //this.print_user(this.user_data, this.user_tagins);
            print_user(user_data, user_tagins);
            counter += 1
        }

        if (display_user && user_data && counter != 0) {
            counter += 1;
        }

        if (counter >= display_time / sleep_time) {
            counter = 0;
            display_user = false;
            user_data = null;
            document.getElementById("tagins").innerHTML = "ingen tag";
            //this.print_clear_screen("online")
        }
    }

    setInterval(function(){
        CheckTagins();
    }, 1000)

    setInterval(function(){
        poll_server(check_if_tagevent_exists);
    }, 2500)
}