function removeOptions(selectElement) {

    $("#" + selectElement).empty();
    $("#" + selectElement).selectpicker("refresh");

}

function show_edit_redeem_div(div_id){
    const divs_redem_edit = [ 
        "#edit-sound-div",
        "#edit-tts-div",
        "#edit-scene-div",
        "#edit-video-div",
        "#edit-response-div",
        "#edit-filter-div",
        "#edit-source-div",
        "#edit-keypress-div",
        "#edit-clip-div",
    ]

    for (const item of divs_redem_edit) {
        document.querySelector(item).hidden = true;
      }
    
      document.querySelector(`#edit-${div_id}-div`).hidden = false;
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

async function reward(type_id,reward_name,reward_id) {

    var reward_events_dom = document.getElementById('rewards-events');
    var reward_list_dom = document.getElementById('rewards-list');
    var reward_list_internal_dom = document.getElementById('rewards-list-internal');
    var reward_edit_dom = document.getElementById('rewards-edit');
    var reward_back_button_top = document.getElementById('reward-back-button-top');

    if (type_id == 'get_list'){

        reward_edit_div = document.getElementById('rewards-edit');
        card_edit = document.getElementById('card-reward-edit');

        if (card_edit) {
            reward_edit_div.removeChild(card_edit);
        }

        data = {
            type_id : 'get_list'
        }
        
        var data_dump = JSON.stringify(data);
    
        var list_reward_parse = await window.pywebview.api.reward(data_dump);
    
        if (list_reward_parse) {
            
            reward_edit_dom.hidden = true;
            reward_list_dom.hidden = false;
            reward_back_button_top.hidden = true;

            list_reward_parse = JSON.parse(list_reward_parse)
        

            reward_list_internal_dom.innerHTML = '';

            list_reward_parse.forEach(function(reward) {
                var cardConfig = {
                    type: 'card_list',
                    id: reward.id,
                    imageSrc: reward.image,
                    title: reward.title,
                    text: reward.prompt,
                    action: reward.action,
                    buttonText: "Editar ação da recompensa"
                };
            
                // Chame a função para criar o card
                createCard("rewards-list-internal", cardConfig);
            });

            start_search_rewards()
            

        }

    } else if (type_id == 'edit_reward') {

        data = {
            type_id : 'edit_reward',
            reward_name : reward_name,
            reward_id : reward_id
        }
        
        var data_dump = JSON.stringify(data);

        var reward_parse = await window.pywebview.api.reward(data_dump);

        if (reward_parse) {

            reward_events_dom.hidden = false;
            reward_list_dom.hidden = true;

            var reward_info_parse = JSON.parse(reward_parse)

            var type_edit = reward_info_parse.reward_type
            
            if (reward_info_parse.reward_edit == "true"){
                
                document.querySelector(`#reward-save-button-${type_edit}`).setAttribute('onclick',`reward('save_reward','${reward_info_parse.title}','${type_edit}')`);
                
                document.getElementById('reward-type-select-div').hidden = true;
                reward_edit_dom.hidden = false;

                show_edit_redeem_div(type_edit)

                var cardConfig = {
                    type: 'card_editor',
                    id: type_edit,
                    imageSrc: reward_info_parse.image,
                    title: reward_info_parse.title,
                    text: reward_info_parse.prompt,
                    action : type_edit,
                    buttonText: "Remover evento de recompensa"
                };

                createCard("rewards-edit", cardConfig);
            
                reward_info_parse = reward_info_parse.reward_data
                
                if (type_edit == 'sound'){
            
                    var old_command_audio = document.querySelector('#old-sound-command');
                    var command_audio = document.querySelector('#command-text-sound-edit');
                    var command_audio_status = document.querySelector('#command-sound-status');
                    var command_delay = document.querySelector('#command-sound-delay');
                    var chat_message = document.querySelector('#chat-message-sound-edit');
                    var sound_info = document.querySelector('#file-select-sound-edit');
                    var audio_volume = document.querySelector('#sound-volume-edit');
    
                    if (reward_info_parse.command_status == 1){
                        command_audio_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_audio_status.checked = false;
                    }
    
                    old_command_audio.value = reward_info_parse.command
                    command_audio.value = reward_info_parse.command
                    
                    chat_message.value = reward_info_parse.response
                    command_delay.value = reward_info_parse.delay
                    sound_info.value = reward_info_parse.sound
                    audio_volume.values = reward_info_parse.volume

                    $('#user-level-sound-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-sound-edit').selectpicker('refresh');
        
                } else if (type_edit == 'video'){
    
                    var old_command_video = document.querySelector('#old-video-command');
                    var command_video = document.querySelector('#command-text-video-edit');
                    var command_video_status = document.querySelector('#command-video-status');
                    var command_delay = document.querySelector('#command-video-delay');
                    var chat_message = document.querySelector('#chat-message-video-edit');
                    var video_info = document.querySelector('#file-select-video-edit');
                    var time_showing_video = document.querySelector('#time-showing-video-edit');
    

                    if (reward_info_parse.command_status == 1){
                        command_video_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_video_status.checked = false;
                    }
    
                    old_command_video.value = reward_info_parse.command
                    command_video.value = reward_info_parse.command
                    command_delay.value = reward_info_parse.delay
                    chat_message.value = reward_info_parse.response
                    video_info.value = reward_info_parse.video
                    time_showing_video.value = reward_info_parse.time_showing

        
                    $('#user-level-video-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-video-edit').selectpicker('refresh');
                        
                } else if (type_edit == 'tts'){
    
                    var old_command_tts = document.querySelector('#old-tts-command');
                    var command_tts = document.querySelector('#command-text-tts-edit');
                    var command_tts_status = document.querySelector('#command-tts-status');
                    var command_delay = document.querySelector('#command-tts-delay');
                    var characters = document.querySelector('#characters-tts-edit');
    
                    old_command_tts.value = reward_info_parse.command;
                    command_tts.value = reward_info_parse.command;
    
                    if (reward_info_parse.command_status == 1){
                        command_tts_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_tts_status.checked = false;
                    }
    
                    command_delay.value = reward_info_parse.delay;
                    characters.value = reward_info_parse.characters;


                    $('#user-level-tts-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-tts-edit').selectpicker('refresh');
    
                } else if (type_edit == 'scene'){
        
                    var command_scene = document.querySelector('#command-text-scene-edit');
                    var old_command_scene = document.querySelector('#old-scene-command');
                    var command_scene_status = document.querySelector('#command-scene-status');
                    var chat_message = document.querySelector('#chat-message-scene-edit');
                    var command_delay = document.querySelector('#command-scene-delay');
                    var scene_name = document.querySelector('#scene-name-edit');
                    var keep = document.querySelector('#keep-switch-scene-edit');
                    var time = document.querySelector('#time-to-return-scene-edit');
    

                    if (reward_info_parse.keep == 1){
                        keep.checked = true
                    }
    
                    if (reward_info_parse.command_status == 1){
                        command_scene_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_scene_status.checked = false;
                    }
    
                    old_command_scene.value = reward_info_parse.command;
                    command_scene.value = reward_info_parse.command;
                    command_delay.value = reward_info_parse.delay;
                    chat_message.value = reward_info_parse.response;
                    time.value = reward_info_parse.time;
    
    
                    $("#scene-name-edit").selectpicker('val',reward_info_parse.scene_name)
                    $("#scene-name-edit").selectpicker("refresh");

                    $('#user-level-scene-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-scene-edit').selectpicker('refresh');
                    
    
                } else if (type_edit == 'response'){
        
                    var old_command_response = document.querySelector('#old-response-command');
                    var command_response = document.querySelector('#command-text-response-edit');
                    var command_response_status = document.querySelector('#command-reponse-status');
                    var chat_message = document.querySelector('#chat-message-response-edit');
                    var command_delay = document.querySelector('#command-response-delay');
    
                    old_command_response.value = reward_info_parse.command;
                    command_response.value = reward_info_parse.command;
    
                    if (reward_info_parse.command_status == 1){
                        command_response_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_response_status.checked = false;
                    }
    
                    command_delay.value = reward_info_parse.delay;
                    chat_message.value = reward_info_parse.response;

                    $('#user-level-response-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-response-edit').selectpicker('refresh');
        
                } else if (type_edit == 'filter'){
        
                    var old_command_filter = document.querySelector('#old-filter-command');
                    var command_filter = document.querySelector('#command-text-filter-edit');
                    var command_filter_status = document.querySelector('#command-filter-status');
                    var chat_message = document.querySelector('#chat-message-filter-edit');
                    var source_name = document.querySelector('#source-name-filter-edit');
                    var filter_name = document.querySelector('#filter-name-filter-edit');
                    var command_delay = document.querySelector('#command-filter-delay');
                    var keep = document.querySelector('#keep-filter-switch-edit');
                    var time = document.querySelector('#time-filter-edit');
    
                    if (reward_info_parse.keep == 1){
                        keep.checked = true
                    }
    
                    old_command_filter.value = reward_info_parse.command;
                    command_filter.value = reward_info_parse.command;
    
                    if (reward_info_parse.command_status == 1){
                        command_filter_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_filter_status.checked = false;
                    }
    
                    command_delay.value = reward_info_parse.delay;
                    chat_message.value = reward_info_parse.response;
                    time.value = reward_info_parse.time;

                    $('#user-level-filter-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-filter-edit').selectpicker('refresh');
        
                } else if (type_edit == 'source'){
        
                    var old_command_source = document.querySelector('#old-source-command');
                    var command_source = document.querySelector('#command-text-source-edit');
                    var command_source_status = document.querySelector('#command-source-status');
                    var chat_message = document.querySelector('#chat-message-source-edit');
                    var source_name = document.querySelector('#source-name-edit');
                    var command_delay = document.querySelector('#command-source-delay');
                    var keep = document.querySelector('#keep-source-edit');
                    var time = document.querySelector('#time-source-edit');

    
                    if (reward_info_parse.keep == 1){
                        keep.checked = true
                    }
    
                    old_command_source.value = reward_info_parse.command;
                    command_source.value = reward_info_parse.command;
    
                    if (reward_info_parse.command_status == 1){
                        command_source_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_source_status.checked = false;
                    }
    
                    command_delay.value = reward_info_parse.delay;
                    chat_message.value = reward_info_parse.response;
                    time.value = reward_info_parse.time;

                    $('#user-level-source-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-source-edit').selectpicker('refresh');
        
                } else if (type_edit == 'keypress'){
    
                    var old_command_keypress = document.querySelector('#old-keypress-command');
                    var command_keypress = document.querySelector('#command-keypress-edit');
                    var command_keypress_status = document.querySelector('#command-keypress-status');
                    var command_delay = document.querySelector('#command-keypress-delay');
                    var chat_message = document.querySelector('#chat-message-keypress-edit');
                    var mode = document.querySelector('#key-mode-select-edit');
                    var mult_press_time_input = document.querySelector('#mult-press-times-edit');
                    var mult_press_interval_input = document.querySelector('#mult-press-interval-edit');
                    var keep_press_time_input = document.querySelector('#keep-press-time-edit');
                    var re_press_time_input = document.querySelector('#re-press-time-edit');
                    var key1_inp = document.querySelector('#key-1-edit');
                    var key2_inp = document.querySelector('#key-2-edit');
                    var key3_inp = document.querySelector('#key-3-edit');
                    var key4_inp = document.querySelector('#key-4-edit');
    
                    old_command_keypress.value = reward_info_parse.command;
                    command_keypress.value = reward_info_parse.command;
    
                    if (reward_info_parse.command_status == 1){
                        command_keypress_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_keypress_status.checked = false;
                    }
    
                    command_delay.value = reward_info_parse.delay;
                    chat_message.value = reward_info_parse.response;
    
                    if (reward_info_parse.mode == 'mult'){
    
                        mode.value = 'mult'
                        mult_press_time_input.value = reward_info_parse.time_press
                        mult_press_interval_input.value = reward_info_parse.interval
    
                    } else if (reward_info_parse.mode == 're') {
    
                        mode.value = 're'
                        re_press_time_input.value = reward_info_parse.re_press_time
    
                    } else if (reward_info_parse.mode == 'keep') {
    
                        mode.value = 'keep'
                        keep_press_time_input.value = reward_info_parse.keep_press_time
                        
                    }
    
                    key1_inp.value = reward_info_parse.key1
                    key2_inp.value = reward_info_parse.key2
                    key3_inp.value = reward_info_parse.key3
                    key4_inp.value = reward_info_parse.key4
    
                    get_key_mode_edit()

                    $('#user-level-key-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-key-edit').selectpicker('refresh');
    
                } else if (type_edit == 'clip'){
        
                    var old_command_clip = document.querySelector('#old-clip-command');
                    var command_clip = document.querySelector('#command-text-clip-edit');
                    var command_clip_status = document.querySelector('#command-clip-status');
                    var command_delay = document.querySelector('#command-clip-delay');
    
                    old_command_clip.value = reward_info_parse.command;
                    command_clip.value = reward_info_parse.command;
    
                    if (reward_info_parse.command_status == 1){
                        command_clip_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_clip_status.checked = false;
                    }
    
                    command_delay.value = reward_info_parse.delay;


                    $('#user-level-clip-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-clip-edit').selectpicker('refresh');
    
                } else if (type_edit == 'highlight'){
    
                    var old_command_highlight = document.querySelector('#old-highlight-command');
                    var command_highlight = document.querySelector('#command-text-highlight-edit');
                    var command_highlight_status = document.querySelector('#command-highlight-status');
                    var command_delay = document.querySelector('#command-highlight-delay');
    
                    old_command_highlight.value = reward_info_parse.command;
                    command_highlight.value = reward_info_parse.command;
    
                    if (reward_info_parse.command_status == 1){
                        command_highlight_status.checked = true;
                    } else if (reward_info_parse.command_status == 0){
                        command_highlight_status.checked = false;
                    }
    
                    command_delay.value = reward_info_parse.delay;

                    $('#user-level-highlight-edit').selectpicker('val', reward_info_parse.user_level);
                    $('#user-level-highlight-edit').selectpicker('refresh');
                }

            } else if (reward_info_parse.reward_edit == "false"){

                reward_back_button_top.hidden = false;

                var cardConfig = {
                    type: 'card_editor',
                    imageSrc: reward_info_parse.image,
                    title: reward_info_parse.title,
                    text: reward_info_parse.prompt,
                    buttonText: "Remover evento de recompensa"
                };

                createCard("rewards-edit", cardConfig);

                document.getElementById('reward-type-select-div').hidden = false;
                reward_edit_dom.hidden = false;
            }

        }
    } else if (type_id == 'save_reward') {

        var type_edit = reward_id

        if (type_edit == 'sound'){
            
            var old_command = document.querySelector('#old-sound-command').value;
            var command = document.querySelector('#command-text-sound-edit').value;
            var command_status = document.querySelector('#command-sound-status');
            var command_delay = document.querySelector('#command-sound-delay').value;
            var chat_message = document.querySelector('#chat-message-sound-edit').value;
            var sound_path = document.querySelector('#file-select-sound-edit').value;
            var audio_volume = document.querySelector('#sound-volume-edit').value;
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-sound-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
    
            data = {
                redeem: reward_name,
                type_id: "save_reward",
                type_edit: type_edit,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                chat_message: chat_message,
                user_level: roles,
                sound_path: sound_path,
                audio_volume: audio_volume
            }
    
        } else if (type_edit == 'video'){
    
            var old_command = document.querySelector('#old-video-command').value;
            var command = document.querySelector('#command-text-video-edit').value;
            var command_status = document.querySelector('#command-video-status');
            var command_delay = document.querySelector('#command-video-delay').value;
            var chat_message = document.querySelector('#chat-message-video-edit').value;
            var video_path = document.querySelector('#file-select-video-edit').value;
            var time_showing_video = document.querySelector('#time-showing-video-edit').value;
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-video-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
            data = {
                redeem: reward_name,
                type_id: "save_reward",
                type_edit: type_edit,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                chat_message: chat_message,
                user_level: roles,
                video_path: video_path,
                time_showing_video: time_showing_video
            }
    
        } else if (type_edit == 'tts'){
    
            var old_command = document.querySelector('#old-tts-command').value;
            var command = document.querySelector('#command-text-tts-edit').value;
            var command_status = document.querySelector('#command-tts-status');
            var command_delay = document.querySelector('#command-tts-delay').value;
            var characters = document.querySelector('#characters-tts-edit').value;
    
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-tts-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
            data = {
                redeem: reward_name,
                type_id: "save_reward",
                type_edit: type_edit,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                user_level: roles,
                characters: characters
            }
    
        } else if (type_edit == 'scene'){
    
            var old_command = document.querySelector('#old-scene-command').value;
            var command = document.querySelector('#command-text-scene-edit').value;
            var command_status = document.querySelector('#command-scene-status');
            var command_delay = document.querySelector('#command-scene-delay').value;
            var chat_message = document.querySelector('#chat-message-scene-edit').value;
            var scene_name = document.querySelector('#scene-name-edit').value;
            var keep = document.querySelector('#keep-switch-scene-edit').checked;
            var time = document.querySelector('#time-to-return-scene-edit').value;
    
    
            if (keep == true){
                keep = 1
            } else {
                keep = 0
            }
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-scene-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
            data = {
                redeem: reward_name,
                type_id: "save_reward",
                type_edit: type_edit,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                chat_message: chat_message,
                user_level: roles,
                scene_name: scene_name,
                keep: keep,
                time: time
            }
    
        } else if (type_edit == 'response'){
    
            var old_command = document.querySelector('#old-response-command').value;
            var command = document.querySelector('#command-text-response-edit').value;
            var command_status = fodocumentrm_save.querySelector('#command-response-status');
            var command_delay = document.querySelector('#command-response-delay').value;
            var chat_message = document.querySelector('#chat-message-response-edit').value;
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-response-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
            data = {
                redeem: reward_name,
                type_id: "save_reward",
                type_edit: type_edit,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                chat_message: chat_message,
                user_level: roles,
            }

    
        } else if (type_edit == 'filter'){
    
            var old_command = document.querySelector('#old-filter-command').value;
            var command = document.querySelector('#command-text-filter-edit').value;
            var command_status = document.querySelector('#command-filter-status');
            var command_delay = document.querySelector('#command-filter-delay').value;
            var chat_message = document.querySelector('#chat-message-filter-edit').value;
    
            var source = document.querySelector('#source-name-filter-edit').value;
            var filter = document.querySelector('#filter-name-edit').value;
            var keep = document.querySelector('#keep-filter-switch-edit').checked;
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }
    
            if (keep == true ){
                keep = 1
            } else {
                keep = 0
            }

            var roles = []; 

            $('#user-level-filter-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
            data = {
    
                redeem: reward_name,
                type_id: "save_reward",
                type_edit: type_edit,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                chat_message: chat_message,
                user_level: roles,
                source: source,
                filter: filter,
                keep: keep
            }
    
        } else if (type_edit == 'source'){
    
            var old_command = document.querySelector('#old-source-command').value;
            var command = document.querySelector('#command-text-source-edit').value;
            var command_status = document.querySelector('#command-source-status');
            var command_delay = document.querySelector('#command-source-delay').value;
            var chat_message = document.querySelector('#chat-message-source-edit').value;
            var time = document.querySelector('#time-source-edit').value;
            var source = document.querySelector('#source-name-source-edit').value;
            var keep = document.querySelector('#keep-source-edit').checked;
    
            if (keep == true ){
                keep = 1
            } else {
                keep = 0
            }
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-source-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
            data = {
                
                redeem: reward_name,
                type_id: "save_reward",
                type_edit: type_edit,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                chat_message: chat_message,
                user_level: roles,
                source: source,
                time: time,
                keep: keep
            }
            
        } else if (type_edit == 'keypress'){
    
            var old_command = document.querySelector('#old-keypress-command').value;
            var command = document.querySelector('#command-keypress-edit').value;
            var command_status = document.querySelector('#command-keypress-status');
            var command_delay = document.querySelector('#command-keypress-delay').value;
            var chat_message = document.querySelector('#chat-message-keypress-edit').value;
    
            var mode = document.querySelector('#key-mode-select-edit').value;
            var mult_press_time_input = document.querySelector('#mult-press-times-edit').value;
            var mult_press_interval_input = document.querySelector('#mult-press-interval-edit').value;
            var keep_press_time_input = document.querySelector('#keep-press-time-edit').value;
            var re_press_time_input = fordocumentm_save.querySelector('#re-press-time-edit').value;
            var key1_inp = document.querySelector('#key-1-edit').value;
            var key2_inp = document.querySelector('#key-2-edit').value;
            var key3_inp = document.querySelector('#key-3-edit').value;
            var key4_inp = document.querySelector('#key-4-edit').value;
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-key-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
    
            if (mode == 'mult'){
    
                data = {
                
                    redeem: reward_name,
                    type_id: "save_reward",
                    type_edit: type_edit,
                    old_command: old_command,
                    command: command,
                    command_status: command_status,
                    delay: command_delay,
                    chat_message: chat_message,
                    user_level: roles,
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
                
                    redeem: reward_name,
                    type_id: "save_reward",
                    type_edit: type_edit,
                    old_command: old_command,
                    command: command,
                    command_status: command_status,
                    chat_message: chat_message,
                    user_level: roles,
                    mode: mode,
                    re_press_time: re_press_time_input,
                    key1: key1_inp,
                    key2: key2_inp,
                    key3: key3_inp,
                    key4: key4_inp,
                }
    
            } else if (mode == 'keep') {
    
                data = {
                
                    redeem: reward_name,
                    type_id: "save_reward",
                    type_edit: type_edit,
                    old_command: old_command,
                    command: command,
                    command_status: command_status,
                    chat_message: chat_message,
                    user_level: roles,
                    mode: mode,
                    keep_press_time: keep_press_time_input,
                    key1: key1_inp,
                    key2: key2_inp,
                    key3: key3_inp,
                    key4: key4_inp,
                }
                
            }
    
        } else if (type_edit == 'clip'){
    
            var old_command = document.querySelector('#old-clip-command').value;
            var command = document.querySelector('#command-text-clip-edit').value;
            var command_status = document.querySelector('#command-clip-status');
            var command_delay = document.querySelector('#command-clip-delay').value;
    
            if (command_status.checked == true){
                command_status = 1
            } else if (command_status.checked == false){
                command_status = 0
            }
            
            var roles = []; 

            $('#user-level-clip-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });

            data = {
                type_id: "save_reward",
                type_edit: type_edit,
                redeem: reward_name,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                user_level: roles,
            }
    
            
        } else if (type_edit == 'highlight'){
    
            var old_command_highlight = document.querySelector('#old-highlight-command');
            var command_highlight = document.querySelector('#command-text-highlight-edit');
            var command_highlight_status = document.querySelector('#command-highlight-status');
            var command_delay = document.querySelector('#command-highlight-delay');
    
            if (command_highlight_status.checked == true){
                command_status = 1
            } else if (command_highlight_status.checked == false){
                command_status = 0
            }

            var roles = []; 

            $('#user-level-highlight-edit :selected').each(function(i, selected){ 
                roles[i] = $(selected).val(); 
            });
            
            data = {
                type_id: "save_reward",
                type_edit: type_edit,
                redeem: reward_name,
                old_command: old_command,
                command: command,
                command_status: command_status,
                delay: command_delay,
                user_level: roles,
            }
    
            
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.reward(formData)


        if (type_edit == 'sound'){

            document.querySelector('#old-sound-command').value = '';
            document.querySelector('#command-text-sound-edit').value = '';
            document.querySelector('#command-sound-delay').value = '';
            document.querySelector('#chat-message-sound-edit').value = '';
            document.querySelector('#file-select-sound-edit').value = '';
            document.querySelector('#sound-volume-edit').value = 50;
        
        } else if (type_edit == 'video'){

            document.querySelector('#old-video-command').value = '';
            document.querySelector('#command-text-video-edit').value = '';
            document.querySelector('#command-video-delay').value = '';
            document.querySelector('#chat-message-video-edit').value = '';
            document.querySelector('#file-select-video-edit').value = '';
            document.querySelector('#time-showing-video-edit').value = '';
        
        } else if (type_edit == 'tts'){

            document.querySelector('#old-tts-command').value = '';
            document.querySelector('#command-text-tts-edit').value = '';
            document.querySelector('#command-tts-delay').value = '';
            document.querySelector('#characters-tts-edit').value = '';

        } else if (type_edit == 'scene'){
        
            document.querySelector('#old-scene-command').value = '';
            document.querySelector('#command-text-scene-edit').value = '';
            document.querySelector('#command-scene-delay').value = '';
            document.querySelector('#scene-name-edit').value = '';
            document.querySelector('#time-to-return-scene-edit').value = '';
        
        } else if (type_edit == 'response'){

            document.querySelector('#old-response-command').value = '';
            document.querySelector('#command-text-response-edit').value = '';
            document.querySelector('#command-response-status').value = '';
            document.querySelector('#command-response-delay').value = '';
            document.querySelector('#chat-message-response-edit').value = '';

        
        } else if (type_edit == 'filter'){

            document.querySelector('#old-filter-command').value = '';
            document.querySelector('#command-text-filter-edit').value = '';
            document.querySelector('#command-filter-delay').value = '';
            document.querySelector('#chat-message-filter-edit').value = '';
        
        } else if (type_edit == 'source'){

            document.querySelector('#old-source-command').value = '';
            document.querySelector('#command-text-source-edit').value = '';
            document.querySelector('#command-source-delay').value = '';
            document.querySelector('#chat-message-source-edit').value = '';
            document.querySelector('#time-source-edit').value = '';
        
        } else if (type_edit == 'keypress'){
        
            document.querySelector('#old-keypress-command').value = '';
            document.querySelector('#command-keypress-edit').value = '';
            document.querySelector('#command-keypress-delay').value = '';
            document.querySelector('#chat-message-keypress-edit').value = '';
            document.querySelector('#re-press-time-edit').value = '';
            document.querySelector('#key-1-edit').value = '';
            document.querySelector('#key-2-edit').value = '';
            document.querySelector('#key-3-edit').value = '';
            document.querySelector('#key-4-edit').value = '';
        
        } else if (type_edit == 'clip'){

            document.querySelector('#old-clip-command').value = '';
            document.querySelector('#command-text-clip-edit').value = '';
            document.querySelector('#command-clip-delay').value = '';
        
        } else if (type_edit == 'highlight'){

            document.querySelector('#old-highlight-command').value = '';
            document.querySelector('#command-text-highlight-edit').value = '';
            document.querySelector('#command-highlight-delay').value = '';
        }

        reward_edit_div = document.getElementById('rewards-edit');
        card_edit = document.getElementById('card-reward-edit');

        if (card_edit) {
            reward_edit_div.removeChild(card_edit);
        }

        document.getElementById(`edit-${type_edit}-div`).hidden = true

        reward_edit_dom.hidden = true;
        reward_list_dom.hidden = false;

        document.getElementById('rewards-editor-div').scrollTop = 0;

    } else if (type_id == 'back'){

        action_type = reward_name

        reward_edit_div = document.getElementById('rewards-edit');
        card_edit = document.getElementById('card-reward-edit');


        if (action_type == 'sound'){

            document.querySelector('#old-sound-command').value = '';
            document.querySelector('#command-text-sound-edit').value = '';
            document.querySelector('#command-sound-delay').value = '';
            document.querySelector('#chat-message-sound-edit').value = '';
            document.querySelector('#file-select-sound-edit').value = '';
            document.querySelector('#sound-volume-edit').value = 50;
        
        } else if (action_type == 'video'){

            document.querySelector('#old-video-command').value = '';
            document.querySelector('#command-text-video-edit').value = '';
            document.querySelector('#command-video-delay').value = '';
            document.querySelector('#chat-message-video-edit').value = '';
            document.querySelector('#file-select-video-edit').value = '';
            document.querySelector('#time-showing-video-edit').value = '';
        
        } else if (action_type == 'tts'){

            document.querySelector('#old-tts-command').value = '';
            document.querySelector('#command-text-tts-edit').value = '';
            document.querySelector('#command-tts-delay').value = '';
            document.querySelector('#characters-tts-edit').value = '';

        } else if (action_type == 'scene'){
        
            document.querySelector('#old-scene-command').value = '';
            document.querySelector('#command-text-scene-edit').value = '';
            document.querySelector('#command-scene-delay').value = '';
            document.querySelector('#scene-name-edit').value = '';
            document.querySelector('#time-to-return-scene-edit').value = '';
        
        } else if (action_type == 'response'){

            document.querySelector('#old-response-command').value = '';
            document.querySelector('#command-text-response-edit').value = '';
            document.querySelector('#command-response-status').value = '';
            document.querySelector('#command-response-delay').value = '';
            document.querySelector('#chat-message-response-edit').value = '';

        
        } else if (action_type == 'filter'){

            document.querySelector('#old-filter-command').value = '';
            document.querySelector('#command-text-filter-edit').value = '';
            document.querySelector('#command-filter-delay').value = '';
            document.querySelector('#chat-message-filter-edit').value = '';
        
        } else if (action_type == 'source'){

            document.querySelector('#old-source-command').value = '';
            document.querySelector('#command-text-source-edit').value = '';
            document.querySelector('#command-source-delay').value = '';
            document.querySelector('#chat-message-source-edit').value = '';
            document.querySelector('#time-source-edit').value = '';
        
        } else if (action_type == 'keypress'){
        

            document.querySelector('#old-keypress-command').value = '';
            document.querySelector('#command-keypress-edit').value = '';
            document.querySelector('#command-keypress-delay').value = '';
            document.querySelector('#chat-message-keypress-edit').value = '';
            document.querySelector('#re-press-time-edit').value = '';
            document.querySelector('#key-1-edit').value = '';
            document.querySelector('#key-2-edit').value = '';
            document.querySelector('#key-3-edit').value = '';
            document.querySelector('#key-4-edit').value = '';
        
        } else if (action_type == 'clip'){

            document.querySelector('#old-clip-command').value = '';
            document.querySelector('#command-text-clip-edit').value = '';
            document.querySelector('#command-clip-delay').value = '';
        
        } else if (action_type == 'highlight'){

            document.querySelector('#old-highlight-command').value = '';
            document.querySelector('#command-text-highlight-edit').value = '';
            document.querySelector('#command-highlight-delay').value = '';
        }
        
        if (card_edit) {
            reward_edit_div.removeChild(card_edit);
        }

        document.getElementById(`edit-${action_type}-div`).hidden = true

        reward_edit_dom.hidden = true;
        reward_list_dom.hidden = false;

        document.getElementById('rewards-editor-div').scrollTop = 0;

    } else if (type_id == 'remove_action'){

        action_type = reward_id
        
        reward_edit_div = document.getElementById('rewards-edit');
        card_edit = document.getElementById('card-reward-edit');

        if (card_edit) {
            reward_edit_div.removeChild(card_edit);
        }

        if (action_type == 'sound'){

            document.querySelector('#old-sound-command').value = '';
            document.querySelector('#command-text-sound-edit').value = '';
            document.querySelector('#command-sound-delay').value = '';
            document.querySelector('#chat-message-sound-edit').value = '';
            document.querySelector('#file-select-sound-edit').value = '';
            document.querySelector('#sound-volume-edit').value = 50;
        
        } else if (action_type == 'video'){

            document.querySelector('#old-video-command').value = '';
            document.querySelector('#command-text-video-edit').value = '';
            document.querySelector('#command-video-delay').value = '';
            document.querySelector('#chat-message-video-edit').value = '';
            document.querySelector('#file-select-video-edit').value = '';
            document.querySelector('#time-showing-video-edit').value = '';
        
        } else if (action_type == 'tts'){

            document.querySelector('#old-tts-command').value = '';
            document.querySelector('#command-text-tts-edit').value = '';
            document.querySelector('#command-tts-delay').value = '';
            document.querySelector('#characters-tts-edit').value = '';

        } else if (action_type == 'scene'){
        
            document.querySelector('#old-scene-command').value = '';
            document.querySelector('#command-text-scene-edit').value = '';
            document.querySelector('#command-scene-delay').value = '';
            document.querySelector('#scene-name-edit').value = '';
            document.querySelector('#time-to-return-scene-edit').value = '';
        
        } else if (action_type == 'response'){

            document.querySelector('#old-response-command').value = '';
            document.querySelector('#command-text-response-edit').value = '';
            document.querySelector('#command-response-status').value = '';
            document.querySelector('#command-response-delay').value = '';
            document.querySelector('#chat-message-response-edit').value = '';

        
        } else if (action_type == 'filter'){

            document.querySelector('#old-filter-command').value = '';
            document.querySelector('#command-text-filter-edit').value = '';
            document.querySelector('#command-filter-delay').value = '';
            document.querySelector('#chat-message-filter-edit').value = '';
        
        } else if (action_type == 'source'){

            document.querySelector('#old-source-command').value = '';
            document.querySelector('#command-text-source-edit').value = '';
            document.querySelector('#command-source-delay').value = '';
            document.querySelector('#chat-message-source-edit').value = '';
            document.querySelector('#time-source-edit').value = '';
        
        } else if (action_type == 'keypress'){
        

            document.querySelector('#old-keypress-command').value = '';
            document.querySelector('#command-keypress-edit').value = '';
            document.querySelector('#command-keypress-delay').value = '';
            document.querySelector('#chat-message-keypress-edit').value = '';
            document.querySelector('#re-press-time-edit').value = '';
            document.querySelector('#key-1-edit').value = '';
            document.querySelector('#key-2-edit').value = '';
            document.querySelector('#key-3-edit').value = '';
            document.querySelector('#key-4-edit').value = '';
        
        } else if (action_type == 'clip'){

            document.querySelector('#old-clip-command').value = '';
            document.querySelector('#command-text-clip-edit').value = '';
            document.querySelector('#command-clip-delay').value = '';
        
        } else if (action_type == 'highlight'){

            document.querySelector('#old-highlight-command').value = '';
            document.querySelector('#command-text-highlight-edit').value = '';
            document.querySelector('#command-highlight-delay').value = '';
        }

        document.getElementById(`edit-${action_type}-div`).hidden = true

        reward_edit_dom.hidden = true;
        reward_list_dom.hidden = false;

        document.getElementById('rewards-editor-div').scrollTop = 0;

        data = {
            type_id: "remove_action",
            reward: reward_name
        }
        

        var formData = JSON.stringify(data);
        window.pywebview.api.reward(formData);
    }

}

function getToastMessage(action) {
    switch (action) {
        case 'Sorteio':
            return "toast_notifc('Altere a configuração para esta recompensa na aba Sorteio');";
        case 'Contador':
            return "toast_notifc('Altere a configuração para esta recompensa na aba Contador');";
        case 'Pedido de musica':
            return "toast_notifc('Altere a configuração para esta recompensa na aba Configurações > Pedido de musica');";
        case 'Fila de espera':
            return "toast_notifc('Altere a configuração para esta recompensa na aba Fila de espera');";
    }
}

function createCard(containerId, config) {

    const container = document.getElementById(containerId);

    const card = document.createElement("div");
    card.setAttribute("data-title",config.title)
    if (config.type === "card_list"){
        card.classList.add("card", "bg-dark", "mt-5","mb-5","card_reward");
    }else if (config.type === "card_editor"){
        card.id = "card-reward-edit";
        card.classList.add("card", "bg-dark", "mt-5","card_reward");
    }   

    card.innerHTML = `
        <div class="row" >
            <div class="col-3">
                <img src="${config.imageSrc}" class="card-img m-3" />
            </div>
            <div class="col-md-9 d-flex flex-column">
                <div class="card-body mt-2 ">
                    <h3 id="reward-title-card" class="card-title">${config.title}</h3>
                    <p class="card-text">${config.text}</p>
                    ${
                        config.action != "None"
                        ? `<p class="card-text">Recompensa vinculada a ação '${config.action}'</p>`
                        : `<p class="card-text">Recompensa sem ação vinculada</p>`
                    }
                </div>
                <div class="card-footer justify-self-end mb-3">
                ${
                    config.type === "card_list" && ['Sorteio', 'Contador', 'Pedido de musica', 'Fila de espera'].includes(config.action)
                    ? `<button class="btn bt-submit" onclick="${getToastMessage(config.action)}" type="button">${config.buttonText}</button>`
                    : config.type === "card_list"
                    ? `<button class="btn bt-submit" onclick="reward('edit_reward', '${config.title}', '${config.id}')" type="button">${config.buttonText}</button>`
                    : config.type === "card_editor"
                    ? `<button class="btn bt-submit" onclick="reward('remove_action', '${config.title}', '${config.id}')" type="button">${config.buttonText}</button>`
                    : ""
                }
                
                </div>
            </div>
        </div>
    `;

    if (config.type === "card_list"){
        container.append(card);
    }else if (config.type === "card_editor"){
        container.prepend(card);
    }   

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

