//COMANDOS

eel.expose(command_modal);
function command_modal(modal_id) {
    $("#" + modal_id).modal("show");
}

function show_commands_div(div_id) {
    if (div_id == "del-commands-div") {
        get_command_list_js("command-select-del");
    } else if (div_id == "edit-commands-div") {
        get_command_list_js("command-select-edit");
    } else if (div_id == "delay-commands-div") {
        get_delay_js();
    }

    document.getElementById("commands-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_commands_div(div_id, modal) {
    $("#" + modal).modal("hide");
    document.getElementById("commands-div").hidden = false;
    document.getElementById(div_id).hidden = true;
}

function create_command_js(event) {
    event.preventDefault();

    var form = document.querySelector("#command-create-form");
    var mod_value = form.querySelector('input[id="mod-switch-command"]').checked;

    if (mod_value == true) {
        mod_value = 1;
    } else {
        mod_value = 0;
    }

    data = {
        new_command: form.querySelector('input[id="new-command"]').value,
        new_message: form.querySelector('input[id="new-message"]').value,
        new_user_level: mod_value,
    };

    var formData = JSON.stringify(data);

    eel.create_command(formData);
}

function edit_command_js(event) {
    event.preventDefault();

    var form = document.querySelector("#command-edit-form");
    var mod_value = form.querySelector(
        'input[id="mod-switch-command-edit"]'
    ).checked;

    if (mod_value == true) {
        mod_value = 1;
    } else {
        mod_value = 0;
    }

    data = {
        old_command: form.querySelector('select[id="command-select-edit"]').value,
        edit_command: form.querySelector('input[id="edit-command"]').value,
        edit_message: form.querySelector('input[id="edit-message"]').value,
        edit_user_level: mod_value,
    };

    var formData = JSON.stringify(data);

    eel.edit_command(formData);
}

function del_command_js(event) {
    event.preventDefault();

    var form = document.querySelector("#command-del-form");
    var command = form.querySelector('select[id="command-select-del"]').value;

    eel.del_command(command);
}

function delay_command_js(event) {
    event.preventDefault();

    var form = document.querySelector("#command-delay-form");

    var command_delay = form.querySelector('input[id="command-delay"]').value;
    var tts_delay = form.querySelector('input[id="tts-delay"]').value;

    eel.edit_delay_commands(command_delay, tts_delay);
}

async function get_command_list_js(select_id) {

    var command_info = await eel.get_commands_list()();

    if (command_info) {
        $("#" + select_id).empty();

        var list_command_parse = JSON.parse(command_info);

        for (var i = 0; i < list_command_parse.length; i++) {
            var optn = list_command_parse[i];

            $("#" + select_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + select_id).selectpicker("refresh");
        }
    }
}

async function get_command_edit() {
    var command = document.querySelector("#command-select-edit").value;
    var command_info = await eel.get_command_info(command)();

    if (command_info) {
        var command_info_parse = JSON.parse(command_info);

        var command_edit = command_info_parse.edit_command;
        var message_edit = command_info_parse.edit_message;
        var user_level_edit = command_info_parse.edit_level;

        document.getElementById("edit-command").value = command_edit;
        document.getElementById("edit-message").value = message_edit;

        if (user_level_edit == "on") {
            document.getElementById("mod-switch-command-edit").checked = true;
        } else if (user_level_edit == "off") {
            document.getElementById("mod-switch-command-edit").checked = false;
        }
    }
}

async function get_delay_js() {
    var delay_command_inp = document.querySelector("#command-delay");
    var delay_tts_inp = document.querySelector("#tts-delay");

    var delay_info = await eel.get_delay_info()();

    if (delay_info) {
        var delay_info_parse = JSON.parse(delay_info);

        var command_delay = delay_info_parse.command_delay;
        var tts_delay = delay_info_parse.tts_delay;

        delay_command_inp.value = command_delay;
        delay_tts_inp.value = tts_delay;
    }
}
