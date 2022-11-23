//CONFIG

eel.expose(config_modal);
function config_modal(modal_id) {
    $("#" + modal_id).modal("show");
}

async function get_redeem_js_config(el_id) {

    console.log('exec')
    var list_redem = await eel.get_redeem()();

    if (list_redem) {
        
        $("#" + el_id).empty();

        var list_redem_parse = JSON.parse(list_redem);

        for (var i = 0; i < list_redem_parse.redeem.length; i++) {
            var optn = list_redem_parse.redeem[i];

            $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + el_id).selectpicker("refresh");
        }
    }
    $("#" + el_id + " option[value='Carregando']").remove();
}


async function get_messages_config_js() {
    
    var enable_tts_command = document.getElementById("enable-tts-command");
    var enable_commands = document.getElementById("enable-commands");
    var enable_responses = document.getElementById("enable-responses");
    var enable_delay_response = document.getElementById("enable-delay-response");
    var enable_clip_responses = document.getElementById("enable-clip-responses");
    var enable_permisson_responses = document.getElementById("enable-permisson-responses");
    var enable_message_status = document.getElementById("enable-message-status");
    var enable_message_music = document.getElementById("enable-message-music");
    var enable_message_next = document.getElementById("enable-message-next");
    var enable_message_error_music = document.getElementById("enable-message-error-music");

    var messages_status = await eel.get_messages_config()();

    if (messages_status) {

        var messages_status_parse = JSON.parse(messages_status);

        if (messages_status_parse.STATUS_TTS == 1) {
            enable_tts_command.checked = true;
        }
        if (messages_status_parse.STATUS_COMMANDS == 1) {
            enable_commands.checked = true;
        }
        if (messages_status_parse.STATUS_RESPONSE == 1) {
            enable_responses.checked = true;
        }
        if (messages_status_parse.STATUS_ERROR_TIME == 1) {
            enable_delay_response.checked = true;
        }
        if (messages_status_parse.STATUS_CLIP == 1) {
            enable_clip_responses.checked = true;
        }
        if (messages_status_parse.STATUS_ERROR_USER == 1) {
            enable_permisson_responses.checked = true;
        }
        if (messages_status_parse.STATUS_BOT == 1) {
            enable_message_status.checked = true;
        }
        if (messages_status_parse.STATUS_MUSIC == 1) {
            enable_message_music.checked = true;
        }
        if (messages_status_parse.STATUS_MUSIC_CONFIRM == 1) {
            enable_message_next.checked = true;
        }
        if (messages_status_parse.STATUS_MUSIC_ERROR == 1) {
            enable_message_error_music.checked = true;
        }
    }
}

async function get_obs_conn_info() {

    var host_inp = document.getElementById("obs-host");
    var port_inp = document.getElementById("obs-port");
    var password_inp = document.getElementById("obs-password");
    var auto_con_chk = document.getElementById("auto-conn");

    var conn_info = await eel.get_obs_conn_info_py()();

    if (conn_info) {

        var conn_info_parse = JSON.parse(conn_info);

        host_inp.value = conn_info_parse.host;
        port_inp.value = conn_info_parse.port;
        password_inp.value = conn_info_parse.password;

        if (conn_info_parse.auto_conn == "on") {
            auto_con_chk.checked = true;
        } else if (conn_info_parse.auto_conn == "off") {
            auto_con_chk.checked = false;
        }
    }
}

async function config_responses_js(event,fun_id_responses) {

    event.preventDefault();

    var button_el = document.getElementById('submit-responses-config');
    var select_id_el = document.getElementById('response-select-edit');
    var in_reponse_el = document.getElementById('response-message-new');

    if (fun_id_responses == 'get_response'){
    
        var messages = await eel.responses_config('get_response',select_id_el.value,'none')();
    
        if (messages) {

            button_el.removeAttribute("disabled");
            in_reponse_el.value = messages;
    
            }

    } else if (fun_id_responses == "save-response"){
        console.log('aaa')
        eel.responses_config('save_response',select_id_el.value,in_reponse_el.value)

        in_reponse_el.value = '';
    }




}

eel.expose(modal_messages_config);
function modal_messages_config(id){
    $("#modal-chat-messages").modal("show");
    if (id == 'sucess'){
        document.getElementById('modal-chat-messages-sucess').hidden = false;
        document.getElementById('modal-chat-messages-error').hidden = true;
    } else if (id == 'error'){
        document.getElementById('modal-chat-messages-sucess').hidden = true;
        document.getElementById('modal-chat-messages-error').hidden = false;
    }
}

eel.expose(modal_responses);
function modal_responses(modal_id_resp){
    $("#modal-responses").modal("show");
    document.getElementById(modal_id_resp).hidden = false
}

eel.expose(modal_responses);
function modal_responses_hide(modal_id_resp){

    document.getElementById(modal_id_resp).hidden = true
}

function show_config_div(div_id) {

    if (div_id == "config-conn-obs-div") {
        get_obs_conn_info();
    } else if (div_id == "config-chat-messages-div") {
        get_messages_config_js();
    } else if (div_id == "config-discord-div") {
        get_discord_config();
    } else if (div_id == "config-music-div"){
        get_redeem_js_config('redeem-select-music')
        get_music_config()
    }

    document.getElementById("config-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_config_div(div_id, modal) {
    $("#" + modal).modal("hide");
    document.getElementById("config-div").hidden = false;
    document.getElementById(div_id).hidden = true;
}

function save_obs_conn(event) {
    event.preventDefault();

    var form = document.querySelector("#obs-conn-form");
    var auto_con = form.querySelector('input[id="auto-conn"]').checked;

    if (auto_con == true){
        auto_con = 1
    } else {
        auto_con = 0
    }

    data = {
        host: form.querySelector('input[id="obs-host"]').value,
        port: form.querySelector('input[id="obs-port"]').value,
        pass: form.querySelector('input[id="obs-password"]').value,
        conn: auto_con
    };

    var formData = JSON.stringify(data);

    eel.save_obs_conn_py(formData);
}

function save_obs_not(event) {

    event.preventDefault();

    var form = document.querySelector("#obs-not-form");
    var not_enabled_status = form.querySelector('input[id="not-enabled"]').checked;
    var not_music_enabled_status = form.querySelector('input[id="not-music-enabled"]').checked;
    

    if (not_enabled_status == true){
        not_enabled_status = 1
    } else if (not_enabled_status == false){
        not_enabled_status = 0
    }

    if (not_music_enabled_status == true){
        not_music_enabled_status = 1
    } else if (not_music_enabled_status == false){
        not_music_enabled_status = 0
    }
    
    data = {
        not_enabled: not_enabled_status,
        not_music: not_music_enabled_status,
        source_name: form.querySelector('select[id="not-source-name"]').value,
        time_showing_not: form.querySelector('input[id="time-show-not"]').value,
    };

    var formData = JSON.stringify(data);
    eel.save_obs_not_py(formData);
}

function config_messages_change(event) {
    event.preventDefault();

    var form = document.querySelector("#chat-messages-config-form");

    var enable_tts_command = form.querySelector('input[id="enable-tts-command"]');
    var enable_commands = form.querySelector('input[id="enable-commands"]');
    var enable_responses = form.querySelector('input[id="enable-responses"]');
    var enable_delay_response = form.querySelector('input[id="enable-delay-response"]');
    var enable_clip_responses = form.querySelector('input[id="enable-clip-responses"]');
    var enable_permisson_responses = form.querySelector('input[id="enable-permisson-responses"]');
    var enable_timer_module = form.querySelector('input[id="enable-timer-module"]');
    var enable_message_status = form.querySelector('input[id="enable-message-status"]');
    var enable_message_music = form.querySelector('input[id="enable-message-music"]');
    var enable_message_next = form.querySelector('input[id="enable-message-next"]');
    var enable_message_error_music = form.querySelector('input[id="enable-message-error-music"]');

    if (enable_tts_command.checked == true) {
        enable_tts_command = 1;
    } else {
        enable_tts_command = 0;
    }
    if (enable_tts_command.checked == true) {
        enable_tts_command = 1;
    } else {
        enable_tts_command = 0;
    }

    if (enable_commands.checked == true) {
        enable_commands = 1;
    } else {
        enable_commands = 0;
    }

    if (enable_responses.checked == true) {
        enable_responses = 1;
    } else {
        enable_responses = 0;
    }

    if (enable_delay_response.checked == true) {
        enable_delay_response = 1;
    } else {
        enable_delay_response = 0;
    }

    if (enable_clip_responses.checked == true) {
        enable_clip_responses = 1;
    } else {
        enable_clip_responses = 0;
    }

    if (enable_permisson_responses.checked == true) {
        enable_permisson_responses = 1;
    } else {
        enable_permisson_responses = 0;
    }

    if (enable_timer_module.checked == true) {
        enable_timer_module = 1;
    } else {
        enable_timer_module = 0;
    }

    if (enable_message_status.checked == true) {
        enable_message_status = 1;
    } else {
        enable_message_status = 0;
    }

    if (enable_message_music.checked == true) {
        enable_message_music = 1;
    } else {
        enable_message_music = 0;
    }

    if (enable_message_next.checked == true) {
        enable_message_next = 1;
    } else {
        enable_message_next = 0;
    }

    if (enable_message_error_music.checked == true) {
        enable_message_error_music = 1;
    } else {
        enable_message_error_music = 0;
    }

    data = {
        status_error_music :enable_message_error_music,
        status_next : enable_message_next,
        status_music : enable_message_music,
        status_tts: enable_tts_command,
        status_commands: enable_commands,
        status_response: enable_responses,
        status_delay: enable_delay_response,
        status_clip: enable_clip_responses,
        status_permission: enable_permisson_responses,
        status_timer: enable_timer_module,
        status_message: enable_message_status,
    };

    var formData = JSON.stringify(data);

    eel.save_messages_config(formData);
}

async function get_music_config(){

    var music_not_status = document.querySelector("#not-music");
    var command_request = document.querySelector("#comand-request");
    var command_volume = document.querySelector("#comand-volume");
    var command_skip = document.querySelector("#comand-skip");
    var command_next = document.querySelector("#comand-next");
    var command_atual= document.querySelector("#comand-atual");

    var data = await eel.get_music_config_py()();

    if(data){

        var music_config = JSON.parse(data);

        if(music_config.not_status == 1){
            music_not_status.checked = true
        }

        command_request.value = music_config.cmd_request;
        command_volume.value = music_config.cmd_volume;
        command_skip.value = music_config.cmd_skip;
        command_next.value = music_config.cmd_next;
        command_atual.value = music_config.cmd_atual;
    }
}

function save_music_config(event){

    event.preventDefault();

    var form_music = document.querySelector("#music-config-form");

    var redeem_music_save = form_music.querySelector("#redeem-select-music");
    var music_not_status_save = form_music.querySelector("#not-music");
    var command_request_save = form_music.querySelector("#comand-request");
    var command_volume_save = form_music.querySelector("#comand-volume");
    var command_skip_save = form_music.querySelector("#comand-skip");
    var command_next_save = form_music.querySelector("#comand-next");
    var command_atual_save = form_music.querySelector("#comand-atual");


    if (music_not_status_save.checked == true){
        music_not_status_save = 1
    } else {
        music_not_status_save = 0
    }

    data = {
        redeem_music_data: redeem_music_save.value,
        music_not_status_data: music_not_status_save,
        command_request_data: command_request_save.value,
        command_volume_data: command_volume_save.value,
        command_skip_data: command_skip_save.value,
        command_next_data: command_next_save.value,
        command_atual_data: command_atual_save.value
    }

    var formData = JSON.stringify(data);

    eel.save_music_config(formData);
    
}

