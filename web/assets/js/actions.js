function removeOptions(selectElement) {

    $("#" + selectElement).empty();
    $("#" + selectElement).selectpicker("refresh");

}

async function get_redeem_js(el_id, type_get) {

    if (type_get == 'del' || type_get == 'edit'){

        var list_redem_parse = await window.pywebview.api.get_redeem('del');

        if (list_redem_parse) {
            
            list_redem_parse = JSON.parse(list_redem_parse)

            removeOptions(el_id)
    
            for (var i = 0; i < list_redem_parse.redeem.length; i++) {
                var optn = list_redem_parse.redeem[i];
    
                $("#" + el_id).append('<option class="bg-dark" style="color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#" + el_id).selectpicker("refresh");
            }
        }

    } else {

        var list_redem_parse = await window.pywebview.api.get_redeem('null');

        if (list_redem_parse) {
            
            list_redem_parse = JSON.parse(list_redem_parse)
            removeOptions(el_id)

            for (var i = 0; i < list_redem_parse.redeem.length; i++) {
                var optn = list_redem_parse.redeem[i];

                $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#" + el_id).selectpicker("refresh");
            }

            if (el_id == 'redeem-select-giveaway' || el_id == 'redeem-select-counter') {

                $("#" + el_id).append('<option class="bg-dark" style="color: #fff;" value="None">Sem recompensa</option>');
                $("#" + el_id).selectpicker("refresh");
                
            }
        }
        $("#" + el_id + " option[value='Carregando']").remove();

    }

}

function show_div(div_id, select_redeem) {

    if (div_id == 'del-div'){

        get_redeem_js(select_redeem,'del');

        document.getElementById("create-redeem").hidden = true;
        document.getElementById(div_id).hidden = false;

    } else if (div_id == 'edit-div') {

        get_redeem_js(select_redeem,'edit');

        document.getElementById("create-redeem").hidden = true;
        document.getElementById(div_id).hidden = false;

    } else {

        get_redeem_js(select_redeem,'null');

        document.getElementById("create-redeem").hidden = true;
        document.getElementById(div_id).hidden = false;
    }
}

function hide_create(div_id_hide) {
    
    document.getElementById("create-redeem").hidden = false;
    document.getElementById(div_id_hide).hidden = true;

}

function get_key_mode() {
    
    var mode_selected = document.getElementById("key-mode-select").value;
    var buttom_keypress = document.getElementById("submit-keypress");
    var re_press_time_input = document.getElementById("re-press-time");
    var keep_press_time_input = document.getElementById("keep-press-time");
    var mult_press_time_input = document.getElementById("mult-press-times");
    var mult_press_interval_input = document.getElementById("mult-press-interval");

    if (mode_selected === "keep") {

        buttom_keypress.removeAttribute("disabled");

        keep_press_time_input.setAttribute("required", "");

        re_press_time_input.removeAttribute("required");
        mult_press_time_input.removeAttribute("required");
        mult_press_interval_input.removeAttribute("required");

        document.getElementById("re-press-div").hidden = true;
        document.getElementById("mult-press-div").hidden = true;
        document.getElementById("keep-press-div").hidden = false;

    } else if (mode_selected === "mult") {

        buttom_keypress.removeAttribute("disabled");

        keep_press_time_input.removeAttribute("required");
        re_press_time_input.removeAttribute("required");

        mult_press_time_input.setAttribute("required", "");
        mult_press_interval_input.setAttribute("required", "");

        document.getElementById("re-press-div").hidden = true;
        document.getElementById("mult-press-div").hidden = false;
        document.getElementById("keep-press-div").hidden = true;

    } else if (mode_selected === "re") {

        buttom_keypress.removeAttribute("disabled");

        re_press_time_input.setAttribute("required", "");

        keep_press_time_input.removeAttribute("required");
        mult_press_time_input.removeAttribute("required");
        mult_press_interval_input.removeAttribute("required");

        document.getElementById("re-press-div").hidden = false;
        document.getElementById("mult-press-div").hidden = true;
        document.getElementById("keep-press-div").hidden = true;

    } else if (mode_selected === "none") {
        buttom_keypress.setAttribute("disabled", "");

        document.getElementById("re-press-div").hidden = true;
        document.getElementById("mult-press-div").hidden = true;
        document.getElementById("keep-press-div").hidden = true;
    }
}


function create_action(event,type_id){
    event.preventDefault();

    if (type_id == 'audio'){

        var form = document.querySelector("#audio-create");

        data = {
            redeem_value: form.querySelector('select[id="redeem-select-audio"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            audio_path: form.querySelector('input[id="file-select"]').value,
            audio_volume: form.querySelector('input[id="audio-volume"]').value,
            user_level_value: form.querySelector('select[id="user-level-audio"]').value,
        };

    } else if (type_id == 'video'){

        var form = document.querySelector("#video-create");
        
        data = {
            redeem_value: form.querySelector('select[id="redeem-select-video"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            video_path: form.querySelector('input[id="file-select-video"]').value,
            time_showing_video: form.querySelector('input[id="time-showing-video"]').value,
            user_level_value: form.querySelector('select[id="user-level-video"]').value,
        };

            
    } else if (type_id == 'tts') {

        var form = document.querySelector("#tts-create");

        data = {
            redeem_value: form.querySelector('select[id="redeem-select-tts"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            characters: form.querySelector('input[id="characters"]').value,
            user_level_value: form.querySelector('select[id="user-level-tts"]').value,
        };



    } else if (type_id == 'scene') {

        var form = document.querySelector("#scene-create");
        var keep_scene = form.querySelector('input[id="keep-switch-scene"]').checked;

        keep_scene = keep_scene ? 1 : 0;

        data = {
            redeem_value: form.querySelector('select[id="redeem-select-scene"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            user_level_value: form.querySelector('select[id="user-level-scene"]').value,
            scene_name: form.querySelector('select[id="scene_name"]').value,
            time: form.querySelector('input[id="time-to-return-scene"]').value,
            keep_scene_value: keep_scene,
        };


    } else if (type_id == 'response') {

        var form = document.querySelector("#response-create");

        data = {
            redeem_value: form.querySelector('select[id="redeem-select-response"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            user_level_value: form.querySelector('select[id="user-level-response"]').value,
        };

    } else if (type_id == 'filter') {

        var form = document.querySelector("#filter-create");
        var keep_filter = form.querySelector('input[id="keep-filter-switch"]').checked;

        if (keep_filter == true) {
            keep_filter = 1;
        } else {
            keep_filter = 0;
        }

        data = {
            redeem_value: form.querySelector('select[id="redeem-select-filter"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            user_level_value: form.querySelector('select[id="user-level-filter"]').value,
            source_name: form.querySelector('select[id="source_name_filter"]').value,
            filter_name: form.querySelector('select[id="filter_name"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            time_showing: form.querySelector('input[id="time-filter-create"]').value,
            keep: keep_filter,
        };
 
    } else if (type_id == 'source') {

        var form = document.querySelector("#source-create");
        var keep_source = form.querySelector('input[id="keep-source"]').checked;

        if (keep_source == true) {
            keep_source = 1;
        } else {
            keep_source = 0;
        }

        data = {
            redeem_value: form.querySelector('select[id="redeem-select-source"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            user_level_value: form.querySelector('select[id="user-level-source"]').value,
            source_name: form.querySelector('select[id="source_name_source"]').value,
            time_showing: form.querySelector('input[id="time_showing-source"]').value,
            keep: keep_source,
        };

        

    } else if (type_id == 'keypress') {

        var form = document.querySelector("#keypress-create");
        var mode = form.querySelector('select[id="key-mode-select"]').value;

        if (mode == "mult") {

            data = {
                redeem_value: form.querySelector('select[id="redeem-select-keypress"]').value,
                command_value: form.querySelector('input[id="command-text"]').value,
                chat_response: form.querySelector('input[id="chat-message"]').value,
                command_delay: form.querySelector('input[id="command-delay"]').value,
                user_level_value: form.querySelector('select[id="user-level-key"]').value,

                mode: form.querySelector('select[id="key-mode-select"]').value,

                mult_press_times: form.querySelector('input[id="mult-press-times"]').value,
                mult_press_interval: form.querySelector('input[id="mult-press-interval"]').value,

                key1: form.querySelector('select[id="key-1"]').value,
                key2: form.querySelector('select[id="key-2"]').value,
                key3: form.querySelector('select[id="key-3"]').value,
                key4: form.querySelector('select[id="key-4"]').value,
            };
        } else if (mode == "re") {

            data = {
                redeem_value: form.querySelector('select[id="redeem-select-keypress"]').value,
                command_value: form.querySelector('input[id="command-text"]').value,
                chat_response: form.querySelector('input[id="chat-message"]').value,
                user_level_value: form.querySelector('select[id="user-level-key"]').value,
                mode: form.querySelector('select[id="key-mode-select"]').value,

                re_press_time: form.querySelector('input[id="re-press-time"]').value,

                key1: form.querySelector('select[id="key-1"]').value,
                key2: form.querySelector('select[id="key-2"]').value,
                key3: form.querySelector('select[id="key-3"]').value,
                key4: form.querySelector('select[id="key-4"]').value,
            };
        } else if (mode == "keep") {

            data = {
                redeem_value: form.querySelector('select[id="redeem-select-keypress"]')
                    .value,
                command_value: form.querySelector('input[id="command-text"]').value,
                chat_response: form.querySelector('input[id="chat-message"]').value,
                user_level_value: form.querySelector('select[id="user-level-key"]').value,
                mode: form.querySelector('select[id="key-mode-select"]').value,

                keep_press_time: form.querySelector('input[id="keep-press-time"]').value,

                key1: form.querySelector('select[id="key-1"]').value,
                key2: form.querySelector('select[id="key-2"]').value,
                key3: form.querySelector('select[id="key-3"]').value,
                key4: form.querySelector('select[id="key-4"]').value,
            };
        }

    } else if (type_id == 'clip') {
        
        var form = document.querySelector("#clip-create");

        data = {
            redeem_value: form.querySelector('select[id="redeem-select-clip"]').value,
            command_value: form.querySelector('input[id="command-text"]').value,
            command_delay: form.querySelector('input[id="command-delay"]').value,
            user_level_value: form.querySelector('#user-level-clip').value,
        };

    } else if (type_id == 'highlight') {
        
        var form = document.querySelector("#highlight-create");

        data = {
            redeem_value: form.querySelector('#redeem-select-highlight').value,
            command_value: form.querySelector('#command-text-highlight').value,
            command_delay: form.querySelector("#command-delay-highlight").value,
            user_level_value: form.querySelector('#user-level-highlight').value,
        };

    } else if (type_id == 'delete') {
        event.preventDefault();

        var selec_del = document.getElementById("action-del-select").value;

        data = {
            redeem: selec_del
        }

        removeOptions("action-del-select");
        get_redeem_js("action-del-select","del");
    }

    var formData = JSON.stringify(data);
    window.pywebview.api.create_action_save(formData,type_id);

}

async function get_scenes(id) {

    $("#" + id).empty();

    var list_scenes = await window.pywebview.api.update_scene_obs();

    if (list_scenes) {

        var list_scenes_parse = JSON.parse(list_scenes);

        for (var i = 0; i < list_scenes_parse.scenes.length; i++) {
            var optn = list_scenes_parse.scenes[i];

            $("#" + id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + id).selectpicker("refresh");

        }
    }
}

async function get_sources(select_id) {

    $("#" + select_id).empty();

    var list_sources = await window.pywebview.api.get_sources_obs();

    if (list_sources) {
        var list_sources_parse = JSON.parse(list_sources);

        for (var i = 0; i < list_sources_parse.source.length; i++) {
            var optn = list_sources_parse.source[i];

            $("#" + select_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + select_id).selectpicker("refresh");
        }
    }
}

async function get_filters(id,id_sources) {

    var selected_sources_id = document.getElementById(id_sources);
    var value = selected_sources_id.value;

    $("#" + id).empty();

    var list_filters = await window.pywebview.api.get_filters_obs(value);

    if (list_filters) {

        var list_filters_parse = JSON.parse(list_filters);

        for (var i = 0; i < list_filters_parse.filters.length; i++) {
            var optn = list_filters_parse.filters[i];

            $("#" + id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + id).selectpicker("refresh");
        }
    }
}

