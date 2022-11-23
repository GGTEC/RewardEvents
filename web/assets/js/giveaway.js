//GIVEAWAY
eel.expose(giveaway_modal_show);
function giveaway_modal_show(id,name) {
    $("#giveaway-modal").modal("show");

    if (id == 'giveway-winner' ){
        document.getElementById('winner-name').innerHTML = name; 
    } 
    document.getElementById(id).hidden = false;
}


function giveaway_modal_hide(id) {
    $("#giveaway-modal").modal("hide");
    document.getElementById(id).hidden = true;
}

async function get_giveaway_config() {

    var giveaway_name_inp = document.getElementById("giveaway-name");
    var giveaway_user_level = document.getElementById("user-level-giveaway");
    var giveaway_clear = document.getElementById("giveaway-clear-names-end");
    var giveaway_enable = document.getElementById('giveaway-enable');
    var giveaway_atual_redeem = document.getElementById('giveaway-atual-redeem');

    var giveaway_info = await eel.get_giveaway_info()();

    if (giveaway_info) {

        var giveaway_info_parse = JSON.parse(giveaway_info);

        giveaway_clear_receive = giveaway_info_parse.giveaway_clear
        giveaway_enable_receive = giveaway_info_parse.giveaway_enable
        

        if (giveaway_clear_receive == 1) {
            giveaway_clear.checked = true
        } else if (giveaway_clear_receive == 0) {
            giveaway_clear.checked = false
        }

        if (giveaway_enable_receive == 1) {
            giveaway_enable.checked = true
        } else if (giveaway_enable_receive == 0) {
            giveaway_enable.checked = false
        }

        giveaway_name_inp.value = giveaway_info_parse.giveaway_name;
        giveaway_user_level.value = giveaway_info_parse.giveaway_level;
        giveaway_atual_redeem.innerHTML= giveaway_info_parse.giveaway_redeem;

    }
}

async function get_giveaway_commands_js() {

    var execute_giveaway = document.getElementById("command-execute-giveaway");
    var check_user_giveaway = document.getElementById("command-check-user-giveaway");
    var clear_giveaway = document.getElementById("command-clear-giveaway");
    var add_user_giveaway = document.getElementById('command-add-user-giveaway');
    var self_check_giveaway = document.getElementById('command-self-check-giveaway');

    var giveaway_commands = await eel.get_giveaway_commands()();

    if (giveaway_commands) {

        var giveaway_commands_parse = JSON.parse(giveaway_commands);

        execute_giveaway.value = giveaway_commands_parse.execute_giveaway
        check_user_giveaway.value = giveaway_commands_parse.user_check_giveaway
        clear_giveaway.value = giveaway_commands_parse.clear_giveaway;
        add_user_giveaway.value = giveaway_commands_parse.add_user_giveaway;
        self_check_giveaway.value = giveaway_commands_parse.self_check_giveaway;
    }
}

async function show_name_list_js() {

    var textbox = document.getElementById('giveaway-names-list');

    $("#giveaway-names-list").val('');

    var name_list = await eel.get_giveaway_names()();

    if (name_list) {

        name_list_parse = JSON.parse(name_list);

        name_list_parse.forEach(element => textbox.value += element + '\n');

        $("#giveaway-modal").modal("show");

        document.getElementById('giveway-names-modal').hidden = false;

    }

}

function save_giveaway_config(event) {
    event.preventDefault();

    var form = document.querySelector("#giveaway-config-form");
    giveaway_clear_check_inp = form.querySelector('input[id="giveaway-clear-names-end"]').checked;
    giveaway_enable_inp = form.querySelector('input[id="giveaway-clear-names-end"]').checked;

    if (giveaway_clear_check_inp == true) {
        giveaway_clear_check_value = 1;
    } else {
        giveaway_clear_check_value = 0;
    }

    if (giveaway_enable_inp == true) {
        giveaway_enable_value = 1;
    } else {
        giveaway_enable_value = 0;
    }

    data = {
        giveaway_name: form.querySelector('input[id="giveaway-name"]').value,
        giveaway_redeem: form.querySelector('select[id="redeem-select-giveaway"]').value,
        giveaway_user_level: form.querySelector('select[id="user-level-giveaway"]').value,
        giveaway_clear_check: giveaway_clear_check_value,
        giveaway_enable: giveaway_enable_value,
    };

    var formData = JSON.stringify(data);

    eel.save_giveaway_config_py(formData);
}

function save_giveaway_commands(event) {
    event.preventDefault();

    var form = document.querySelector("#giveaway-config-commands-form");

    data = {
        
        execute_giveaway: form.document.querySelector("#command-execute-giveaway"),
        self_check_giveaway: form.document.querySelector("#command-self-check-giveaway"),
        check_user_giveaway: form.document.querySelector("#command-check-user-giveaway"),
        clear_giveaway: form.document.querySelector("#command-clear-giveaway"),
        add_user_giveaway: form.document.querySelector("#command-add-user-giveaway"),
    }

    var formData = JSON.stringify(data);

    eel.save_giveaway_commands_py(formData);
}

function add_user_giveaway_js(event) {
    event.preventDefault();

    var form = document.querySelector("#giveaway-add-user-form");
    var add_name = form.elements[0].value;

    eel.add_name_giveaway(add_name);
}

function execute_giveaway_js() {
    eel.execute_giveaway();
}

function clear_name_list_js() {
    eel.clear_name_list();
}



