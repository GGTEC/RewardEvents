async function get_redeem_edit(el_id) {

    var list_redem = await eel.get_redeem('null')();

    if (list_redem) {

        $("#" + el_id).empty();

        var list_redem_parse = JSON.parse(list_redem);

        for (var i = 0; i < list_redem_parse.redeem.length; i++) {
            var optn = list_redem_parse.redeem[i];

            $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + el_id).selectpicker("refresh");

        }
    
    return true
    }
}

function get_key_mode_edit() {
    
    var mode_selected = document.getElementById("key-mode-select-edit").value;

    var buttom_keypress = document.getElementById("submit-keypress-edit");
    var re_press_time_input = document.getElementById("re-press-time-edit");
    var keep_press_time_input = document.getElementById("keep-press-time-edit");
    var mult_press_time_input = document.getElementById("mult-press-times-edit");
    var mult_press_interval_input = document.getElementById("mult-press-interval-edit");

    var re_pres_div = document.getElementById("re-press-div-edit");
    var mult_press_div = document.getElementById("mult-press-div-edit");
    var keep_press_div = document.getElementById("keep-press-div-edit");

    if (mode_selected === "keep") {

        buttom_keypress.removeAttribute("disabled");
        keep_press_time_input.setAttribute("required", "");
        re_press_time_input.removeAttribute("required");
        mult_press_time_input.removeAttribute("required");
        mult_press_interval_input.removeAttribute("required");

        re_pres_div.hidden = true;
        mult_press_div.hidden = true;
        keep_press_div.hidden = false;


    } else if (mode_selected === "mult") {

        buttom_keypress.removeAttribute("disabled");

        keep_press_time_input.removeAttribute("required");
        re_press_time_input.removeAttribute("required");

        mult_press_time_input.setAttribute("required", "");
        mult_press_interval_input.setAttribute("required", "");

        re_pres_div.hidden = true;
        mult_press_div.hidden = false;
        keep_press_div.hidden = true;

    } else if (mode_selected === "re") {

        buttom_keypress.removeAttribute("disabled");

        re_press_time_input.setAttribute("required", "");

        keep_press_time_input.removeAttribute("required");
        mult_press_time_input.removeAttribute("required");
        mult_press_interval_input.removeAttribute("required");

        re_pres_div.hidden = false;
        mult_press_div.hidden = true;
        keep_press_div.hidden = true;

    } else if (mode_selected === "none") {

        buttom_keypress.setAttribute("disabled", "");

        re_pres_div.hidden = true;
        mult_press_div.hidden = true;
        keep_press_div.hidden = true;
    }
}

eel.expose(modal_edit_actions);
function modal_edit_actions(type,div_id){
    if (type == 'sucess' ){
        $("#modal-edit-sucess").modal("show");
    } else if (type == 'error'){
        $("#modal-edit-error").modal("show");
    }
    document.getElementById(div_id).hidden = true;
}

async function get_edit_type(){

    var select_edit = document.getElementById('action-edit-select');
    var edit_redeem_name = select_edit.value;
    var type = await eel.get_edit_type_py(edit_redeem_name)();

    if (type){

        if (type == 'sound'){

            document.getElementById("edit-audio-div").hidden = false;
            document.getElementById("edit-tts-div").hidden = true;
            document.getElementById("edit-scene-div").hidden = true;
            document.getElementById("edit-response-div").hidden = true;
            document.getElementById("edit-filter-div").hidden = true;
            document.getElementById("edit-source-div").hidden = true;
            document.getElementById("edit-keypress-div").hidden = true;
            document.getElementById("edit-clip-div").hidden = true;

            
            var sound_data = await eel.get_edit_data(edit_redeem_name,type)()

            if (sound_data) {

                var return_true = await get_redeem_edit('redeem-select-audio-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-audio-edit');
    
                    var data_sound_parse = JSON.parse(sound_data);
                    var form_sound = document.querySelector('#audio-edit-form');
                    var old_command_audio = form_sound.querySelector('#old-audio-command');
                    var command_audio = form_sound.querySelector('#command-text-audio-edit');
                    var chat_message = form_sound.querySelector('#chat-message-audio-edit');
                    var user_level = form_sound.querySelector('#mod-switch-audio-edit');
                    var sound_info = form_sound.querySelector('#file-select-audio-edit');
    
                    $("#redeem-select-audio-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    $("#redeem-select-audio-edit").selectpicker("refresh");

                    if (data_sound_parse.user_level == 'mod'){
                        user_level.checked = true
                    }

                    old_command_audio.value = data_sound_parse.command
                    command_audio.value = data_sound_parse.command
                    chat_message.value = data_sound_parse.response
                    select.value = edit_redeem_name;
                    sound_info.value = data_sound_parse.sound
                }

                
            }

        } else if (type == 'tts'){

            document.getElementById("edit-audio-div").hidden = true;
            document.getElementById("edit-tts-div").hidden = false;
            document.getElementById("edit-scene-div").hidden = true;
            document.getElementById("edit-response-div").hidden = true;
            document.getElementById("edit-filter-div").hidden = true;
            document.getElementById("edit-source-div").hidden = true;
            document.getElementById("edit-keypress-div").hidden = true;
            document.getElementById("edit-clip-div").hidden = true;


            var tts_data = await eel.get_edit_data(edit_redeem_name,type)()

            if (tts_data) {

                var return_true = await get_redeem_edit('redeem-select-tts-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-tts-edit');
    
                    var data_tts_parse = JSON.parse(tts_data);
                    var form_tts = document.querySelector('#tts-edit-form');
                    var command_tts = form_tts.querySelector('#command-text-tts-edit');
                    var chat_message = form_tts.querySelector('#chat-message-tts-edit');
                    var user_level = form_tts.querySelector('#mod-switch-tts-edit');
                    var characters = form_tts.querySelector('#characters-tts-edit');
    
                    $("#redeem-select-tts-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    $("#redeem-select-tts-edit").selectpicker("refresh");

                    if (data_tts_parse.user_level == 'mod'){
                        user_level.checked = true
                    }

                    select.value = edit_redeem_name;
                    command_tts.value = data_tts_parse.command;
                    chat_message.value = data_tts_parse.response;
                    characters.value = data_tts_parse.characters;

                    $("select").selectpicker("refresh");
                }

                
            }

        } else if (type == 'scene'){

            document.getElementById("edit-audio-div").hidden = true;
            document.getElementById("edit-tts-div").hidden = true;
            document.getElementById("edit-scene-div").hidden = false;
            document.getElementById("edit-response-div").hidden = true;
            document.getElementById("edit-filter-div").hidden = true;
            document.getElementById("edit-source-div").hidden = true;
            document.getElementById("edit-keypress-div").hidden = true;
            document.getElementById("edit-clip-div").hidden = true;


            var scene_data = await eel.get_edit_data(edit_redeem_name,type)()

            if (scene_data) {

                var return_true = await get_redeem_edit('redeem-select-scene-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-scene-edit');
    
                    var data_scene_parse = JSON.parse(scene_data);
                    var form_scene = document.querySelector('#scene-edit-form');
                    var command_scene = form_scene.querySelector('#command-text-scene-edit');
                    var chat_message = form_scene.querySelector('#chat-message-scene-edit');
                    var user_level = form_scene.querySelector('#mod-switch-scene-edit');
                    var scene_name = form_scene.querySelector('#scene-name-edit');
                    var keep = form_scene.querySelector('#keep-switch-scene-edit');
                    var time = form_scene.querySelector('#time-to-return-scene-edit');
    
                    $("#redeem-select-scene-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    $("#redeem-select-scene-edit").selectpicker("refresh");

                    if (data_scene_parse.user_level == 'mod'){
                        user_level.checked = true
                    }
                    if (data_scene_parse.keep == 1){
                        keep.checked = true
                    }

                    select.value = edit_redeem_name;
                    command_scene.value = data_scene_parse.command;
                    chat_message.value = data_scene_parse.response;
                    time.value = data_scene_parse.time;
                    $("select").selectpicker("refresh");
                }  
            }

        } else if (type == 'response'){

            document.getElementById("edit-audio-div").hidden = true;
            document.getElementById("edit-tts-div").hidden = true;
            document.getElementById("edit-scene-div").hidden = true;
            document.getElementById("edit-response-div").hidden = false;
            document.getElementById("edit-filter-div").hidden = true;
            document.getElementById("edit-source-div").hidden = true;
            document.getElementById("edit-keypress-div").hidden = true;
            document.getElementById("edit-clip-div").hidden = true;

            var response_data = await eel.get_edit_data(edit_redeem_name,type)()

            if (response_data) {

                var return_true = await get_redeem_edit('redeem-select-response-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-response-edit');
    
                    var data_response_parse = JSON.parse(response_data);
                    var form_response = document.querySelector('#response-edit-form');
                    var old_command_response = form_response.querySelector('#old-response-command');
                    var command_response = form_response.querySelector('#command-text-response-edit');
                    var chat_message = form_response.querySelector('#chat-message-response-edit');
                    var user_level = form_response.querySelector('#mod-switch-response-edit');
    
                    $("#redeem-select-response-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    $("#redeem-select-response-edit").selectpicker("refresh");

                    if (data_response_parse.user_level == 'mod'){
                        user_level.checked = true
                    }

                    select.value = edit_redeem_name;
                    old_command_response.value = data_response_parse.command;
                    command_response.value = data_response_parse.command;
                    chat_message.value = data_response_parse.response;
                    $("select").selectpicker("refresh");
                }  
            }

        } else if (type == 'filter'){

            document.getElementById("edit-audio-div").hidden = true;
            document.getElementById("edit-tts-div").hidden = true;
            document.getElementById("edit-scene-div").hidden = true;
            document.getElementById("edit-response-div").hidden = true;
            document.getElementById("edit-filter-div").hidden = false;
            document.getElementById("edit-source-div").hidden = true;
            document.getElementById("edit-keypress-div").hidden = true;
            document.getElementById("edit-clip-div").hidden = true;

            var filter_data = await eel.get_edit_data(edit_redeem_name,type)()
            console.log('AAA')
            if (filter_data) {

                var return_true = await get_redeem_edit('redeem-select-filter-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-filter-edit');
    
                    var data_filter_parse = JSON.parse(filter_data);
                    var form_filter = document.querySelector('#filter-edit-form');
                    var old_command_filter = form_filter.querySelector('#old-filter-command');
                    var command_filter = form_filter.querySelector('#command-text-filter-edit');
                    var chat_message = form_filter.querySelector('#chat-message-filter-edit');
                    var user_level = form_filter.querySelector('#mod-switch-filter-edit');
                    var source_name = form_filter.querySelector('#source-name-filter-edit');
                    var filter_name = form_filter.querySelector('#filter-name-filter-edit');
                    var keep = form_filter.querySelector('#keep-filter-switch-edit');
                    var time = form_filter.querySelector('#time-filter-edit');
    
                    $("#redeem-select-filter-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    $("#redeem-select-filter-edit").selectpicker("refresh");

                    if (data_filter_parse.user_level == 'mod'){
                        user_level.checked = true
                    }
                    if (data_filter_parse.keep == 1){
                        keep.checked = true
                    }

                    select.value = edit_redeem_name;
                    old_command_filter.value = data_filter_parse.command;
                    command_filter.value = data_filter_parse.command;
                    chat_message.value = data_filter_parse.response;
                    time.value = data_filter_parse.time;
                    $("select").selectpicker("refresh");
                }  
            }

        } else if (type == 'source'){

            document.getElementById("edit-audio-div").hidden = true;
            document.getElementById("edit-tts-div").hidden = true;
            document.getElementById("edit-scene-div").hidden = true;
            document.getElementById("edit-response-div").hidden = true;
            document.getElementById("edit-filter-div").hidden = true;
            document.getElementById("edit-source-div").hidden = false;
            document.getElementById("edit-keypress-div").hidden = true;
            document.getElementById("edit-clip-div").hidden = true;


            var source_data = await eel.get_edit_data(edit_redeem_name,type)()

            if (source_data) {

                var return_true = await get_redeem_edit('redeem-select-source-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-source-edit');
    
                    var data_source_parse = JSON.parse(source_data);
                    var form_source = document.querySelector('#source-edit-form');
                    var old_command_source = form_source.querySelector('#old-source-command');
                    var command_source = form_source.querySelector('#command-text-source-edit');
                    var chat_message = form_source.querySelector('#chat-message-source-edit');
                    var user_level = form_source.querySelector('#mod-switch-source-edit');
                    var source_name = form_source.querySelector('#source-name-edit');
                    var keep = form_source.querySelector('#keep-source-edit');
                    var time = form_source.querySelector('#time-source-edit');
    
                    $("#redeem-select-source-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    $("#redeem-select-source-edit").selectpicker("refresh");

                    if (data_source_parse.user_level == 'mod'){
                        user_level.checked = true
                    }
                    if (data_source_parse.keep == 1){
                        keep.checked = true
                    }

                    select.value = edit_redeem_name;
                    old_command_source.value = data_source_parse.command;
                    command_source.value = data_source_parse.command;
                    chat_message.value = data_source_parse.response;
                    time.value = data_source_parse.time;

                    
                }  
            }

        } else if (type == 'keypress'){

            document.getElementById("edit-audio-div").hidden = true;
            document.getElementById("edit-tts-div").hidden = true;
            document.getElementById("edit-scene-div").hidden = true;
            document.getElementById("edit-response-div").hidden = true;
            document.getElementById("edit-filter-div").hidden = true;
            document.getElementById("edit-source-div").hidden = true;
            document.getElementById("edit-keypress-div").hidden = false;
            document.getElementById("edit-clip-div").hidden = true;

            var keypress_data = await eel.get_edit_data(edit_redeem_name,type)()

            if (keypress_data) {

                var return_true = await get_redeem_edit('redeem-select-keypress-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-keypress-edit');
    
                    var data_keypress_parse = JSON.parse(keypress_data);
                    var form_keypress = document.querySelector('#keypress-edit-form');
                    var old_command_keypress = form_keypress.querySelector('#old-keypress-command');
                    var command_keypress = form_keypress.querySelector('#command-keypress-edit');
                    var chat_message = form_keypress.querySelector('#chat-message-keypress-edit');
                    var user_level = form_keypress.querySelector('#mod-switch-keypress-edit');
                    var mode = form_keypress.querySelector('#key-mode-select-edit');
                    var mult_press_time_input = form_keypress.querySelector('#mult-press-times-edit');
                    var mult_press_interval_input = form_keypress.querySelector('#mult-press-interval-edit');
                    var keep_press_time_input = form_keypress.querySelector('#keep-press-time-edit');
                    var re_press_time_input = form_keypress.querySelector('#re-press-time-edit');
                    var key1_inp = form_keypress.querySelector('#key-1-edit');
                    var key2_inp = form_keypress.querySelector('#key-2-edit');
                    var key3_inp = form_keypress.querySelector('#key-3-edit');
                    var key4_inp = form_keypress.querySelector('#key-4-edit');
    
                    $("#redeem-select-keypress-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    
                    select.value = edit_redeem_name;
                    old_command_keypress.value = data_keypress_parse.command;
                    command_keypress.value = data_keypress_parse.command;
                    chat_message.value = data_keypress_parse.response;

                    if (data_keypress_parse.user_level == 'mod'){
                        user_level.checked = true
                    }

                    if (data_keypress_parse.mode == 'mult'){

                        mode.value = 'mult'
                        mult_press_time_input.value = data_keypress_parse.time_press
                        mult_press_interval_input.value = data_keypress_parse.interval

                    } else if (data_keypress_parse.mode == 're') {

                        mode.value = 're'
                        re_press_time_input.value = data_keypress_parse.re_press_time

                    } else if (data_keypress_parse.mode == 'keep') {

                        mode.value = 'keep'
                        keep_press_time_input.value = data_keypress_parse.keep_press_time
                        
                    }

                    key1_inp.value = data_keypress_parse.key1
                    key2_inp.value = data_keypress_parse.key2
                    key3_inp.value = data_keypress_parse.key3
                    key4_inp.value = data_keypress_parse.key4

                    $("select").selectpicker("refresh");
                    get_key_mode_edit()
                }  
            }

        } else if (type == 'clip'){

            document.getElementById("edit-audio-div").hidden = true;
            document.getElementById("edit-tts-div").hidden = true;
            document.getElementById("edit-scene-div").hidden = true;
            document.getElementById("edit-response-div").hidden = true;
            document.getElementById("edit-filter-div").hidden = true;
            document.getElementById("edit-source-div").hidden = true;
            document.getElementById("edit-keypress-div").hidden = true;
            document.getElementById("edit-clip-div").hidden = false;

            var clip_data = await eel.get_edit_data(edit_redeem_name,type)()

            if (clip_data) {

                var return_true = await get_redeem_edit('redeem-select-clip-edit')

                if(return_true){

                    var select = document.getElementById('redeem-select-clip-edit');
    
                    var data_clip_parse = JSON.parse(clip_data);
                    var form_clip = document.querySelector('#clip-edit-form');
                    var old_command_clip = form_clip.querySelector('#old-clip-command');
                    var command_clip = form_clip.querySelector('#command-text-clip-edit');
                    var user_level = form_clip.querySelector('#mod-switch-clip-edit');
    
                    $("#redeem-select-clip-edit").append('<option style="background: #000; color: #fff;" value="'+ edit_redeem_name +'">'+ edit_redeem_name +'</option>');
                    $("#redeem-select-clip-edit").selectpicker("refresh");

                    if (data_clip_parse.user_level == 'mod'){
                        user_level.checked = true
                    }

                    select.value = edit_redeem_name;
                    old_command_clip.value = data_clip_parse.command;
                    command_clip.value = data_clip_parse.command;
                }  
            }
        }
    }
}

function save_edit(event,type_edit){
    event.preventDefault()

    if (type_edit == 'sound'){

        var form_save = document.getElementById('audio-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-audio-edit').value;
        var old_command = form_save.querySelector('#old-audio-command').value;
        var command = form_save.querySelector('#command-text-audio-edit').value;
        var chat_message = form_save.querySelector('#chat-message-audio-edit').value;
        var user_level = form_save.querySelector('#mod-switch-audio-edit').checked;
        var sound_path = form_save.querySelector('#file-select-audio-edit').value;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }
        data = {
            old_redeem: old_redeem,
            redeem: redeem,
            old_command: old_command,
            command: command,
            chat_message: chat_message,
            user_level: user_level,
            sound_path: sound_path
        }

        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'audio')


    } else if (type_edit == 'tts'){

        var form_save = document.getElementById('tts-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-tts-edit').value;
        var command = form_save.querySelector('#command-text-tts-edit').value;
        var chat_message = form_save.querySelector('#chat-message-tts-edit').value;
        var user_level = form_save.querySelector('#mod-switch-tts-edit').checked;
        var characters = form_save.querySelector('#characters-tts-edit').value;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }
        data = {
            old_redeem: old_redeem,
            redeem: redeem,
            old_command: old_command,
            command: command,
            chat_message: chat_message,
            user_level: user_level,
            characters: characters
        }

        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'tts')

    } else if (type_edit == 'scene'){

        var form_save = document.getElementById('scene-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-scene-edit').value;
        var old_command = form_save.querySelector('#old-scene-command').value;
        var command = form_save.querySelector('#command-text-scene-edit').value;
        var chat_message = form_save.querySelector('#chat-message-scene-edit').value;
        var user_level = form_save.querySelector('#mod-switch-scene-edit').checked;
        var scene_name = form_save.querySelector('#scene-name-edit').value;
        var keep = form_save.querySelector('#keep-switch-scene-edit').checked;
        var time = form_save.querySelector('#time-to-return-scene-edit').value;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }

        if (keep == true){
            keep = 1
        } else {
            keep = 0
        }

        data = {
            old_redeem: old_redeem,
            redeem: redeem,
            old_command: old_command,
            command: command,
            chat_message: chat_message,
            user_level: user_level,
            scene_name: scene_name,
            keep: keep,
            time: time
        }

        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'scene')

    } else if (type_edit == 'response'){

        var form_save = document.getElementById('response-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-response-edit').value;
        var old_command = form_save.querySelector('#old-response-command').value;
        var command = form_save.querySelector('#command-text-response-edit').value;
        var chat_message = form_save.querySelector('#chat-message-response-edit').value;
        var user_level = form_save.querySelector('#mod-switch-response-edit').checked;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }

        data = {
            old_redeem: old_redeem,
            redeem: redeem,
            old_command: old_command,
            command: command,
            chat_message: chat_message,
            user_level: user_level,
        }

        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'response')

    } else if (type_edit == 'filter'){

        var form_save = document.getElementById('filter-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-filter-edit').value;

        var old_command = form_save.querySelector('#old-filter-command').value;
        var command = form_save.querySelector('#command-text-filter-edit').value;
        var chat_message = form_save.querySelector('#chat-message-filter-edit').value;
        var user_level = form_save.querySelector('#mod-switch-filter-edit').checked;

        var source = form_save.querySelector('#source-name-filter-edit').value;
        var filter = form_save.querySelector('#filter-name-edit').value;
        var keep = form_save.querySelector('#keep-filter-switch-edit').checked;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }

        if (keep == true ){
            keep = 1
        } else {
            keep = 0
        }

        data = {

            old_redeem: old_redeem,
            redeem: redeem,
            old_command: old_command,
            command: command,
            chat_message: chat_message,
            user_level: user_level,
            source: source,
            filter: filter,
            keep: keep
        }

        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'filter')

    } else if (type_edit == 'source'){

        var form_save = document.getElementById('source-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-source-edit').value;

        var old_command = form_save.querySelector('#old-source-command').value;
        var command = form_save.querySelector('#command-text-source-edit').value;
        var chat_message = form_save.querySelector('#chat-message-source-edit').value;
        var user_level = form_save.querySelector('#mod-switch-source-edit').checked;
        var time = form_save.querySelector('#time-source-edit').value;
        var source = form_save.querySelector('#source-name-source-edit').value;
        var keep = form_save.querySelector('#keep-source-edit').checked;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }

        if (keep == true ){
            keep = 1
        } else {
            keep = 0
        }

        data = {
            
            old_redeem: old_redeem,
            redeem: redeem,
            old_command: old_command,
            command: command,
            chat_message: chat_message,
            user_level: user_level,
            source: source,
            time: time,
            keep: keep
        }

        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'source')
        
    } else if (type_edit == 'keypress'){

        var form_save = document.getElementById('keypress-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-keypress-edit').value;

        var old_command = form_save.querySelector('#old-keypress-command').value;
        var command = form_save.querySelector('#command-keypress-edit').value;
        var chat_message = form_save.querySelector('#chat-message-keypress-edit').value;
        var user_level = form_save.querySelector('#mod-switch-keypress-edit').checked;

        var mode = form_save.querySelector('#key-mode-select-edit').value;
        var mult_press_time_input = form_save.querySelector('#mult-press-times-edit').value;
        var mult_press_interval_input = form_save.querySelector('#mult-press-interval-edit').value;
        var keep_press_time_input = form_save.querySelector('#keep-press-time-edit').value;
        var re_press_time_input = form_save.querySelector('#re-press-time-edit').value;
        var key1_inp = form_save.querySelector('#key-1-edit').value;
        var key2_inp = form_save.querySelector('#key-2-edit').value;
        var key3_inp = form_save.querySelector('#key-3-edit').value;
        var key4_inp = form_save.querySelector('#key-4-edit').value;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }

        if (mode == 'mult'){

            data = {
            
                old_redeem: old_redeem,
                redeem: redeem,
                old_command: old_command,
                command: command,
                chat_message: chat_message,
                user_level: user_level,
                mode: mode,
                mult_press_times: mult_press_time_input,
                mult_press_interval: mult_press_interval_input,
                key1: key1_inp,
                key2: key2_inp,
                key3: key3_inp,
                key4: key4_inp,

            }

        } else if (mode == 're') {

            data = {
            
                old_redeem: old_redeem,
                redeem: redeem,
                old_command: old_command,
                command: command,
                chat_message: chat_message,
                user_level: user_level,
                mode: mode,
                re_press_time: re_press_time_input,
                key1: key1_inp,
                key2: key2_inp,
                key3: key3_inp,
                key4: key4_inp,
            }

        } else if (mode == 'keep') {

            data = {
            
                old_redeem: old_redeem,
                redeem: redeem,
                old_command: old_command,
                command: command,
                chat_message: chat_message,
                user_level: user_level,
                mode: mode,
                keep_press_time: keep_press_time_input,
                key1: key1_inp,
                key2: key2_inp,
                key3: key3_inp,
                key4: key4_inp,
            }
            
        }


        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'keypress')


    } else if (type_edit == 'clip'){

        var form_save = document.getElementById('clip-edit-form');
        var old_redeem = document.getElementById('action-edit-select').value;
        var redeem = form_save.querySelector('#redeem-select-clip-edit').value;
        var old_command = form_save.querySelector('#old-clip-command').value;
        var command = form_save.querySelector('#command-text-clip-edit').value;
        var user_level = form_save.querySelector('#mod-switch-clip-edit').checked;

        if (user_level == true ){
            user_level = 'mod'
        } else {
            user_level = ''
        }

        data = {
            old_redeem: old_redeem,
            redeem: redeem,
            old_command: old_command,
            command: command,
            user_level: user_level,
        }

        var formData = JSON.stringify(data);

        eel.save_edit_redeen(formData,'clip')

    }
}

async function get_redeem_edit_js(el_id) {
    
    var list_redem = await eel.get_redeem('edit')();

    if (list_redem) {
        
        $("#" + el_id).empty();
        $("#" + el_id).selectpicker("refresh");

        var list_redem_parse = JSON.parse(list_redem);

        for (var i = 0; i < list_redem_parse.redeem.length; i++) {
            var optn = list_redem_parse.redeem[i];
            $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + el_id).selectpicker("refresh");
        }
    }
}

function show_div_edit(div_id, select_redeem) {
    get_redeem_edit_js(select_redeem);
    document.getElementById("create-redeem").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_div_edit(div_id, select_redeem) {
    get_redeem_edit_js(select_redeem);
    document.getElementById("create-redeem").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_create_edit(div_id_hide) {
    document.getElementById("create-redeem").hidden = false;
    document.getElementById(div_id_hide).hidden = true;
}

function edit_action_save(event,type){
    event.preventDefault()

    if (type == 'audio'){

        var form_sound = document.querySelector('#audio-edit-form');
        var redeem = form_sound.querySelector('#redeem-select-audio-edit');
        var command = form_sound.querySelector('#command-text-audio-edit');
        var message = form_sound.querySelector('#chat-message-audio-edit');
        var user_level = form_sound.querySelector('#mod-switch-audio-edit');
        var sound_path = form_sound.querySelector('#file-select-audio-edit');

        if (user_level.checked == true){
            user_level = 1
        } else {
            user_level = 0
        }

        data = {
            redeem_save : redeem,
            command_save : command,
            message_save : message,
            user_level_save : user_level,
            sound_path_save : sound_path,
        }
    }
}
