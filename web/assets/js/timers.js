//TIMERS
function show_timer_div(div_id) {
    document.getElementById("timers-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

async function get_timer_info() {

    document.getElementById("timer-add-form").reset();
    document.getElementById("timer-edit-form").reset();
    document.getElementById("timer-del-form").reset();
    document.getElementById("timer-delay-form").reset();
    

    $("#timer-select-edit").empty();
    $("#timer-select-del").empty();

    var timer_enable_check = document.getElementById("timer-enable");

    var timer_inp_delay_min = document.getElementById("timer-delay-min");
    var timer_inp_delay_max = document.getElementById("timer-delay-max");

    var list_messages = await eel.get_timer_info()();

    if (list_messages) {

        var list_messages_parse = JSON.parse(list_messages);

        var delay_min_info = list_messages_parse.delay_min;
        var delay_max_info = list_messages_parse.delay_max;

        timer_inp_delay_min.value = delay_min_info;
        timer_inp_delay_max.value = delay_max_info;
        
        if (list_messages_parse.status = 1){
            timer_enable_check.checked = true;
        }
            

        data = list_messages_parse.messages;

        for (var key in data) {
            
            var value = data[key];
            var valuesl = value.slice(0, 80)

            $("#timer-select-edit").append('<option class="timer-wrap" style="background: #000; color: #fff;" value="'+ key +'">'+ valuesl +'</option>');
            $("#timer-select-edit").selectpicker("refresh");

        }

        for (var key in data) {

            var value = data[key];
            var valuesl = value.slice(0, 80)


            $("#timer-select-del").append('<option class="timer-wrap style="background: #000; color: #fff;" value="'+ key +'">'+ valuesl +'</option>');
            $("#timer-select-del").selectpicker("refresh");
        }

        $("select").selectpicker("refresh");
    }
}

async function get_timer_edit() {

    var timer_select_edit_value = document.getElementById("timer-select-edit").value;
    var timer_edit_inp = document.getElementById("timer-edit-message");

    console.log(timer_select_edit_value)
    var message_edit_to = await eel.get_message_timer(timer_select_edit_value)();

    timer_edit_inp.value = message_edit_to;
}

function add_timer_js(event) {
    event.preventDefault();

    var form = document.querySelector("#timer-add-form");
    var new_timer_message = form.querySelector('input[id="add-message-timer"]').value;

    eel.add_timer(new_timer_message);
    $("select").selectpicker("refresh");
}

function edit_timer_js(event) {
    event.preventDefault();

    var timer_select_edit_value =
        document.getElementById("timer-select-edit").value;
    var timer_edit_new = document.getElementById("timer-edit-message").value;

    eel.edit_timer(timer_select_edit_value, timer_edit_new);
}

function del_timer_js(event) {
    event.preventDefault();
    var timer_select_del_value =
        document.getElementById("timer-select-del").value;

    eel.del_timer(timer_select_del_value);
}

function interval_timer_js(event) {
    event.preventDefault();
    var timer_delay_min = document.getElementById("timer-delay-min").value;
    var timer_delay_max = document.getElementById("timer-delay-max").value;

    eel.edit_delay_timer(timer_delay_min, timer_delay_max);
}

function save_timer_status(){

    var check_seletor = document.getElementById('timer-enable');

    if (check_seletor.checked == true){
        eel.timer_status_save(1)
    } else if (check_seletor.checked == false) {
        eel.timer_status_save(0)
    }
}