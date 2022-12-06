//COMANDOS

eel.expose(command_modal);
function command_modal(modal_id) {
    $("#" + modal_id).modal("show");
}

function show_commands_div(div_id) {

    if (div_id == "del-commands-div") {
        commands_fun('event','get_list');
    } else if (div_id == "edit-commands-div") {
        commands_fun('event','get_list');
    } else if (div_id == "delay-commands-div") {
        commands_fun('event','get_delay');
    }

    document.getElementById("commands-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_commands_div(div_id, modal) {

    $("#" + modal).modal("hide");
    document.getElementById("commands-div").hidden = false;
    document.getElementById(div_id).hidden = true;

}

async function commands_fun(event,type_id){
    

    if (type_id == 'create'){
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

        eel.commands_py('create',formData);

        form.reset();

    
    } else if (type_id == 'edit'){
        event.preventDefault();

        var form = document.querySelector("#command-edit-form");
        var mod_value = form.querySelector('input[id="mod-switch-command-edit"]').checked;

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

        eel.commands_py(type_id,formData);
        form.reset();


    } else if (type_id == 'delete'){

        event.preventDefault();

        var form = document.querySelector("#command-del-form");
        var command = form.querySelector('select[id="command-select-del"]').value;

        eel.commands_py(type_id,command);
        form.reset();
        $("#command-select-del option:selected").remove();
        $("#command-select-del").selectpicker("refresh");

    } else if (type_id == 'edit_delay'){

        var form = document.querySelector("#command-delay-form");

        data = {
            command_delay: form.querySelector('input[id="command-delay"]').value,
            tts_delay: form.querySelector('input[id="tts-delay"]').value,
        };
    
        var formData = JSON.stringify(data);

        eel.commands_py(type_id, formData);
        form.reset();



    } else if (type_id == 'get_list'){

        var command_info = await eel.commands_py(type_id,'null')();

        if (command_info) {

            $("#command-select-del").empty();
            $("#command-select-del").selectpicker("refresh");
            $("#command-select-edit").empty();
            $("#command-select-edit").selectpicker("refresh");
    
            var list_command_parse = JSON.parse(command_info);
    
            for (var i = 0; i < list_command_parse.length; i++) {
                var optn = list_command_parse[i];
    
                $("#command-select-del").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-del").selectpicker("refresh");
                $("#command-select-edit").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-edit").selectpicker("refresh");
            }
        }

    } else if (type_id == 'get_delay'){

        var delay_command_inp = document.querySelector("#command-delay");
        var delay_tts_inp = document.querySelector("#tts-delay");

        var delay_info = await eel.commands_py(type_id,'null')();

        if (delay_info) {

            var delay_info_parse = JSON.parse(delay_info);

            var command_delay = delay_info_parse.command_delay;
            var tts_delay = delay_info_parse.tts_delay;

            delay_command_inp.value = command_delay;
            delay_tts_inp.value = tts_delay;
        }

    } else if (type_id == 'get_info'){

        var command = document.querySelector("#command-select-edit").value;
        var command_info = await eel.commands_py(type_id,command)();

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
}