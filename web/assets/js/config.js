//CONFIG

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function get_redeem_js_config(el_id) {

    var list_redem_parse = await window.pywebview.api.get_redeem('player');

    if (list_redem_parse) {

        list_redem_parse = JSON.parse(list_redem_parse)
        
        $("#" + el_id).empty();

        $("#" + el_id).append('<option style="background: #000; color: #fff;" value="None">Sem recompensa</option>');
        $("#" + el_id).selectpicker("refresh");

        for (var i = 0; i < list_redem_parse.redeem.length; i++) {
            var optn = list_redem_parse.redeem[i];

            $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + el_id).selectpicker("refresh");
        }
    }
}

async function messages_config_js(type_id) {
    
    var enable_tts_command = document.getElementById("enable-tts-module");
    var enable_commands = document.getElementById("enable-commands");
    var enable_responses = document.getElementById("enable-responses");
    var enable_delay_response = document.getElementById("enable-delay-response");
    var enable_clip_responses = document.getElementById("enable-clip-responses");
    var enable_permisson_responses = document.getElementById("enable-permisson-responses");
    var enable_message_music = document.getElementById("enable-message-music");
    var enable_message_next = document.getElementById("enable-message-next");
    var enable_message_error_music = document.getElementById("enable-message-error-music");

    if (type_id == 'get'){

        var messages_status_parse = await window.pywebview.api.messages_config('get','none');

        if (messages_status_parse) {
    
            messages_status_parse = JSON.parse(messages_status_parse)
    
            enable_tts_command.checked = messages_status_parse.STATUS_TTS == 1 ? true : false;
            enable_commands.checked = messages_status_parse.STATUS_COMMANDS == 1 ? true : false;
            enable_responses.checked = messages_status_parse.STATUS_RESPONSE == 1 ? true : false;
            enable_delay_response.checked = messages_status_parse.STATUS_ERROR_TIME == 1 ? true : false;
            enable_clip_responses.checked = messages_status_parse.STATUS_CLIP == 1 ? true : false;
            enable_permisson_responses.checked = messages_status_parse.STATUS_ERROR_USER == 1 ? true : false;
            enable_message_music.checked = messages_status_parse.STATUS_MUSIC == 1 ? true : false;
            enable_message_next.checked = messages_status_parse.STATUS_MUSIC_CONFIRM == 1 ? true : false;
            enable_message_error_music.checked = messages_status_parse.STATUS_MUSIC_ERROR == 1 ? true : false;

        }
    } else if (type_id == 'save'){

        enable_tts_command = enable_tts_command.checked ? 1 : 0;
        enable_commands = enable_commands.checked ? 1 : 0;
        enable_responses = enable_responses.checked ? 1 : 0;
        enable_delay_response = enable_delay_response.checked ? 1 : 0;
        enable_clip_responses = enable_clip_responses.checked ? 1 : 0;
        enable_permisson_responses = enable_permisson_responses.checked ? 1 : 0;
        enable_message_music = enable_message_music.checked ? 1 : 0;
        enable_message_next = enable_message_next.checked ? 1 : 0;
        enable_message_error_music = enable_message_error_music.checked ? 1 : 0
    
        data = {
            status_tts: enable_tts_command,
            status_commands: enable_commands,
            status_response: enable_responses,
            status_delay: enable_delay_response,
            status_clip: enable_clip_responses,
            status_permission: enable_permisson_responses,
            status_music : enable_message_music,
            status_next : enable_message_next,
            status_error_music :enable_message_error_music
        };
    
        var formData = JSON.stringify(data);
    
        window.pywebview.api.messages_config('save',formData);
    }

}

async function obs_config_js(event,type_id) {


    if (type_id == 'get'){

        var conn_info_parse = await window.pywebview.api.obs_config_py(type_id,'null');

        if (conn_info_parse) {

            conn_info_parse = JSON.parse(conn_info_parse)
            document.getElementById("obs-host").value = conn_info_parse.host;
            document.getElementById("obs-port").value = conn_info_parse.port;
            document.getElementById("obs-password").value = conn_info_parse.password;
        }

    } else if (type_id == 'get_not'){

        var not_redeem_enabled_status = document.getElementById('not-redeem-enabled');
        var not_music_enabled_status = document.getElementById('not-music-enabled');
        var not_emote_enabled_status = document.getElementById('not-emote-enabled');
        var emote_size = document.getElementById('emote-px')
        var time_show_not = document.getElementById('time-show-not')
        var time_show_music = document.getElementById('time-show-music')

        var not_info_parse = await window.pywebview.api.obs_config_py(type_id,'null');

        if (not_info_parse) {
            not_info_parse = JSON.parse(not_info_parse)

            not_redeem_enabled_status.checked = not_info_parse.html_redem_active == 1 ? true : false;
            not_music_enabled_status.checked = not_info_parse.html_player_active == 1 ? true : false;
            not_emote_enabled_status.checked = not_info_parse.html_emote_active == 1 ? true : false;

            time_show_not.value = not_info_parse.html_redeem_time
            time_show_music.value = not_info_parse.html_music_time
            emote_size.value = not_info_parse.emote_px
            
        }
    } else if (type_id == 'save_conn'){
        event.preventDefault();

        var form = document.querySelector("#obs-conn-form");
    
        data = {
            host: form.querySelector('#obs-host').value,
            port: form.querySelector('#obs-port').value,
            pass: form.querySelector('#obs-password').value,
        };
    
        var formData = JSON.stringify(data);
        window.pywebview.api.obs_config_py(type_id,formData);

    } else if (type_id == 'save_not'){
        event.preventDefault();

        var not_redeem_enabled_status = document.getElementById('not-redeem-enabled').checked;
        var not_music_enabled_status = document.getElementById('not-music-enabled').checked;
        var not_emote_enabled_status = document.getElementById('not-emote-enabled').checked;
        var emote_px = document.getElementById('emote-px').value
        var time_show_not = document.getElementById('time-show-not').value
        var time_show_music = document.getElementById('time-show-music').value
        
        not_redeem_enabled_status = not_redeem_enabled_status ? 1 : 0;
        not_music_enabled_status = not_music_enabled_status ? 1 : 0;
        not_emote_enabled_status = not_emote_enabled_status ? 1 : 0;
        
        data = {
            not_redeem: not_redeem_enabled_status,
            not_music: not_music_enabled_status,
            not_emote: not_emote_enabled_status,
            emote_px: emote_px,
            time_showing_not: time_show_not,
            time_showing_music : time_show_music
        };
    
        var formData = JSON.stringify(data);
        window.pywebview.api.obs_config_py(type_id,formData);

    }

}

async function config_responses_js(event,fun_id_responses) {

    event.preventDefault();

    var button_el = document.getElementById('submit-responses-config');
    var select_id_el = document.getElementById('response-select-edit').value;
    var in_reponse_el = document.getElementById('response-message-new');
    var aliases_responses = document.getElementById('aliases-responses');

    if (fun_id_responses == 'get_response'){

        var messages = await window.pywebview.api.responses_config('get_response',select_id_el,'none');
    
        if (messages) {

            button_el.removeAttribute("disabled");
            in_reponse_el.value = messages;
    
            }

        const responses_aliases_respo = {
            giveaway_clear : '',
            music_disabled : '{username}',
            clip_create_clip : '{username}, {clip_id}',
            clip_button_create_clip : '{username}, {clip_id}',
            clip_created_by : '{username}',
            create_clip_discord : ' {username}, {clip_id}',
            create_clip_discord_edit : '{username}, {clip_url}',
            response_delay_error : '{username}, {seconds}',
            error_user_level: '{username}, {user_level}, {command}',
            response_counter: '{username}, {value}',
            response_set_counter: '{username}, {value}',
            giveaway_response_user_add: '{username}',
            giveaway_response_mult_add: '{username}, {perm}',
            giveaway_response_perm: '{username}, {perm}',
            giveaway_status_disable: '{username}, {perm}, {giveaway_name}',
            giveaway_status_enable: '{username}, {giveaway_name}, {redeem}',
            response_giveaway_disabled: '{username}, {giveaway_name}, {redeem}',
            giveaway_response_win: '{name}',
            music_playing: '{music_name}, {music_name_short}, {music_artist}, {username}',
            music_added_to_queue: '{username}, {user_input}, {music}, {music_short}',
            music_leght_error: '{max_duration}, {username}, {user_input}, {music}, {music_short}',
            music_blacklist: '{username}, {user_input}, {music}, {music_short}',
            music_add_error: '{username}, {user_input}',
            command_sr_error_link: '{username}',
            command_current_confirm: '{username}, {music}',
            command_next_no_music: '{username}',
            command_next_confirm: '{username}, {music}, {request_by}',
            command_volume_confirm: '{username}, {volume}',
            command_volume_error: '{username}, {volume}',
            command_volume_response: '{username}, {volume}',
            command_skip_confirm: '{username}',
            duel_yorself: '{username}',
            duel_again:'{username}',
            duel_request: '{time}, {username}, {challenged}, {command}, {accept}',
            duel_already_started: '{username}',
            duel_other: '{username}',
            duel_accepted: '{username}, {challenger}',
            duel_long: '{challenged}',
            duel_start: '{challenger}, {challenged}, {time_to_start}',
            duel_title: '{challenger}, {challenged}, {time_to_start}',
            duel_parm: '{username}, {command}, {accept}',
            no_duel_request: '{username}',
            duel_delay: '{username}{time}'

        };
            
        aliases_responses.value = responses_aliases_respo[select_id_el];

        if (select_id_el in responses_aliases_respo) {
            aliases_responses.value = responses_aliases_respo[select_id_el];
          } else {
            aliases_responses.value = "{username}";
          }

    } else if (fun_id_responses == "save-response"){

        window.pywebview.api.responses_config('save_response',select_id_el,in_reponse_el.value)
        in_reponse_el = '';
    }
}

function show_config_div(div_id) {

    if (div_id == "config-conn-obs-div") {
        obs_config_js('event','get');
    } else if (div_id == "config-not-obs-div") {
        obs_config_js('event','get_not');
    } else if (div_id == "config-chat-messages-div") {
        messages_config_js('get');
    } else if (div_id == "config-discord-div") {
        discord_js('event','get-profile');
    } else if (div_id == "config-music-div"){
        get_redeem_js_config('redeem-select-music')
        sr_config_js('event','get')
    } else if (div_id == "chat-config-div"){
        chat_config('get')
    } else if (div_id == "userdata-div"){
        userdata_js('get')
    } else if (div_id == "events-config-div"){
        event_log_config('get')
    } else if (div_id == "config-highlight-div"){
        highlight_js('get')
    }

    document.getElementById("config-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_config_div(div_id, modal) {
    $("#" + modal).modal("hide");
    document.getElementById("config-div").hidden = false;
    document.getElementById(div_id).hidden = true;
}


async function sr_config_js(event,type_id){
    
    if (type_id == 'get'){

        var music_not_status = document.querySelector("#not-music");
        var check_seletor = document.querySelector('#music-enable');
        var max_duration = document.getElementById("max-duration")

        var skip_votes = document.getElementById("skip-requests");
        var skip_mod = document.getElementById("skip-ignore");
    
        var music_config = await window.pywebview.api.sr_config_py(type_id,'null');
    
        if(music_config){
            
            music_config = JSON.parse(music_config)

            if(music_config.not_status == 1){
                music_not_status.checked = true
            }

            if (music_config.allow_music == 1){
                check_seletor.checked = true;
            } else if (music_config.allow_music == 0){
                check_seletor.checked = false;
            }

            if(music_config.skip_mod == 1){
                skip_mod.checked = true
            }
            
            max_duration.value = music_config.max_duration;

            skip_votes.value = music_config.skip_votes;

            $("#redeem-select-music").selectpicker('val', music_config.redeem);
    
            
        }

    } else if (type_id == 'get_command'){

        var select_command_player = document.getElementById('command-player-edit');

        var form_player = document.getElementById('command_player_form');
        var command_player_command = document.getElementById('command-player-command');
        var command_player_status = document.getElementById('command-player-status');
        var command_player_delay = document.getElementById('command-player-delay');

        var command_data_parse = await window.pywebview.api.sr_config_py(type_id,select_command_player.value)

        if (command_data_parse){

            command_data_parse = JSON.parse(command_data_parse)

            form_player.hidden = false

            command_player_command.value = command_data_parse.command
            command_player_status.checked = command_data_parse.status == 1 ? true : false
            command_player_delay.value = command_data_parse.delay

            $("#command-player-perm").selectpicker('val', command_data_parse.user_level);
            $("#command-player-perm").selectpicker("refresh");

        }

    } else if (type_id == 'save_command') {

        var select_command_player = document.getElementById('command-player-edit');

        var form_player = document.getElementById('command_player_form');
        
        var command_player_command = document.getElementById('command-player-command');
        var command_player_status = document.getElementById('command-player-status');
        var command_player_delay = document.getElementById('command-player-delay');
        var command_player_perm = document.getElementById('command-player-perm');
        
        data = {
            type_command : select_command_player.value,
            command: command_player_command.value,
            delay: command_player_delay.value,
            user_level: command_player_perm.value,
            status: command_player_status = command_player_status.checked ? 1 : 0
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.sr_config_py(type_id,formData);

    } else if (type_id == 'save'){

        var check_seletor = document.getElementById('music-enable');
        var redeem_music_save = document.getElementById("redeem-select-music");
        var max_duration = document.getElementById("max-duration")
        var music_not_status_save = document.getElementById("not-music");

        var skip_votes = document.getElementById("skip-requests");
        var skip_mod = document.getElementById("skip-ignore");
    
        music_not_status_save = music_not_status_save.checked == true ? 1 : 0
        allow_music = check_seletor.checked == true ? 1 : 0

        skip_mod = skip_mod.checked == true ? 1 : 0
    
        data = {
            redeem_music_data: redeem_music_save.value,
            max_duration: max_duration.value,
            allow_music_save : allow_music,
            music_not_status_data: music_not_status_save,
            skip_votes : skip_votes.value,
            skip_mod : skip_mod
        }
    
        var formData = JSON.stringify(data);
        window.pywebview.api.sr_config_py(type_id,formData);
        
    } else if (type_id == 'list_get'){

        var music_data_parse = await window.pywebview.api.sr_config_py(type_id,'null')
        
        if (music_data_parse){

            $("#modal_list_block").modal("show")

            var tbody = document.getElementById('block-list-body');

            tbody.innerHTML = "";
        
            Object.entries(music_data_parse).forEach(([v,k]) => {
        
              tbody.innerHTML += '<tr><td>' + k + '</td></tr>';
              
            })
        }

    } else if (type_id == 'list_add'){

        var blocked_music = document.getElementById('blocked-music').value;

        window.pywebview.api.sr_config_py(type_id,blocked_music);

        blocked_music.value = '';
        
    } else if (type_id == 'list_rem'){

        var blocked_music = document.getElementById('blocked-music').value;

        window.pywebview.api.sr_config_py(type_id,blocked_music);

        blocked_music.value = '';
        
    } 
}

async function userdata_js(type_id,data){

    if (type_id == "get"){

        var userdata_parse = await window.pywebview.api.userdata_py('get','None')
        
        if (userdata_parse){

            userdata_parse = JSON.parse(userdata_parse)
            if ($.fn.DataTable.isDataTable("#userdata_table")) {
                $('#userdata_table').DataTable().clear().draw();
                $('#userdata_table').DataTable().destroy();
            }

            var table = $('#userdata_table').DataTable( {
                destroy: true,
                initComplete: function () {
                    this.api()
                        .columns()
                        .every(function () {
                            var that = this;
         
                            $('input', this.footer()).on('keyup change clear', function () {
                                if (that.search() !== this.value) {
                                    that.search(this.value).draw();
                                }
                            });
                        });
                },
                scrollX: true,
                paging: true,
                ordering:  true,
                retrieve : false,
                processing: true,
                responsive: false,
                lengthMenu: [
                    [10, 25, 50, -1],
                    [10, 25, 50, 'All'],
                ],
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
                }
            } );


            for (var key in userdata_parse) {
                
                    var removeBtn = document.createElement("button");
                    removeBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
                    removeBtn.setAttribute("type", "button");
                    removeBtn.setAttribute("title", "Remover usuário");
                    removeBtn.setAttribute("data-toggle", "tooltip");
                    removeBtn.setAttribute("data-bs-placement", "top");
                    removeBtn.setAttribute("onclick", "window.pywebview.api.userdata_py('remove','" + userdata_parse[key].display_name + "')");

                    var removeIcon = document.createElement("i");
                    removeIcon.classList.add("fa-solid", "fa-user-xmark");

                    removeBtn.appendChild(removeIcon);

                    var addBtn = document.createElement("button");
                    addBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
                    addBtn.setAttribute("type", "button");
                    addBtn.setAttribute("title", "Adicionar na lista de bots e remover desta tabela");
                    addBtn.setAttribute("data-toggle", "tooltip");
                    addBtn.setAttribute("data-bs-placement", "top");
                    addBtn.setAttribute("onclick", "window.pywebview.api.userdata_py('list_add','" + userdata_parse[key].display_name + "')");

                    var addIcon = document.createElement("i");
                    addIcon.classList.add("fa-solid", "fa-robot");

                    addBtn.appendChild(addIcon);
                    
                    var div_color = document.createElement("div");
                    div_color.classList.add("color_icon")
                    div_color.style.backgroundColor = userdata_parse[key].color

                    var regular = userdata_parse[key].regular ? "Sim" : "Não";
                    var time_w = (userdata_parse[key].time_w / 60).toFixed(2) + 'h';

                    var top_chatter = userdata_parse[key].top_chatter ? "Sim" : "Não";
                    var chat_freq = userdata_parse[key].chat_freq + " Msg's";

                var row = table.row.add([

                  "<div class='d-flex'>"+ div_color.outerHTML + userdata_parse[key].display_name + "</div>",
                  (userdata_parse[key].mod || userdata_parse[key].sub || userdata_parse[key].vip) 
                  ? (userdata_parse[key].mod ? "Mod, " : "") + 
                  (userdata_parse[key].sub ? "Sub, " : "") + 
                  (userdata_parse[key].vip ? "vip" : "") : "",
                  userdata_parse[key].sub_count,
                  time_w  + ' | ' +  regular,
                  chat_freq + ' | ' + top_chatter,
                  userdata_parse[key].badges,
                  userdata_parse[key].last_join,
                  removeBtn.outerHTML + addBtn.outerHTML
                ]);

                
              }

            $('#userdata_table tfoot th').each(function () {
                var title = $(this).text();
                $(this).html('<input type="text" class="form-control bg-dark" placeholder="Procure em ' + title + '" />');
            });

            $('[data-toggle="tooltip"]').tooltip();

        }

    
    } else if (type_id == 'remove'){
        window.pywebview.api.userdata_py(type_id,data)
    } else if (type_config == 'list_add'){
        window.pywebview.api.chat_config(data,type_config);
    }
}


function show_userdata_modal(){
    $("#userdata-modal").modal("show");
    userdata_js('get')
}

let runned = false
async function get_stream_info_test(){

    var button_submt = document.getElementById('submit-stream-info');
    var title_inp = document.getElementById("stream-title");

    var loading_title = document.getElementById('loading_title');
    var title_body = document.getElementById('title_body');
    
    button_submt.disabled = true
    
    var stream_games_parse = await window.pywebview.api.get_stream_info_py()
    
    if (stream_games_parse){

        stream_games_parse = JSON.parse(stream_games_parse)

        streamer_game = stream_games_parse.game;
        streamer_game_id = stream_games_parse.game_id;
        streamer_tags = stream_games_parse.tag;
        title_inp.value = stream_games_parse.title;

        var div_tags = document.getElementById("tags");
        var spans = div_tags.querySelectorAll('p');
        var finded = false;
    
        for (var id in streamer_tags){

            for (var i = 0; i < spans.length; i++) { 
    
                if (spans[i].textContent.trim() === tag) { 
                  finded = true;
                }
            }
  
            if (!finded) {

                tag = streamer_tags[id]

                var span_tags = document.createElement("p")
                span_tags.innerHTML = tag.toLowerCase();
                span_tags.id = tag.toLowerCase();
                document.getElementById("tags").appendChild(span_tags);

            }

        }

        button_submt.disabled = false

    }

    if (runned == false){


        runned = true
        // Obtém a lista JSON da URL
        fetch('https://ggtec.github.io/list_games_tags_tw/games.json')
        .then(response => response.json())
        .then(data => {
        // Obtém o seletor do seletor de opções
        const selectpicker = document.getElementById('stream-game');
        
        $("#stream-game").empty();
        $("#stream-game").selectpicker("refresh");

        // Adiciona cada nome como uma opção no seletor de opções
        Object.values(data).forEach(item => {
            $("#stream-game").append('<option class="bg-dark" style="color: #fff;" value="'+ item.id +'">'+ item.name +'</option>');
        });
    
        $("#stream-game").selectpicker("refresh");

        title_body.hidden = false
        loading_title.hidden = true

        $("#stream-game").selectpicker('val', streamer_game_id);

        var image = document.getElementById('game_img');
        
        var item_url = Object.values(data).find(item => item.id === streamer_game_id);
        var width = 215;
        var height = 300;
        var url = item_url.box_art_url;
        
        

        var newUrl = url.replace(/\{width\}x\{height\}/, `${width}x${height}`);

        image.src = newUrl


        // Adiciona um listener de evento para o seletor de opções
        selectpicker.addEventListener('change', event => {
            // Obtém o valor do seletor de opções selecionado
            const selectedValue = event.target.value;

            // Encontra o objeto JSON correspondente com base no nome selecionado
            const selectedItem = Object.values(data).find(item => item.id === selectedValue);
            // Obtém o seletor da imagem
            const image = document.getElementById('game_img');
            const game_inp = document.getElementById('stream-game-inp');

            game_inp.value = selectedItem.name
    
            // Define o atributo src da imagem como o valor de box_art_url do objeto JSON selecionado
            var width = 215;
            var height = 300;
            var url = selectedItem.box_art_url;
            var newUrl = url.replace(/\{width\}x\{height\}/, `${width}x${height}`);
    
            image.src = newUrl
        });
        });
    
        // Obtém a lista JSON da URL
        fetch('https://ggtec.github.io/list_games_tags_tw/tags.json')
        .then(response_tags => response_tags.json())
        .then(data_tags => {
        // Obtém o seletor do seletor de opções
        const selectpicker_tags = document.getElementById('stream-tags');
            
        $("#stream-tags").empty();
        $("#stream-tags").selectpicker("refresh");

        // Adiciona cada nome como uma opção no seletor de opções
        Object.values(data_tags).forEach((value) => {
            $("#stream-tags").append(`<option class="bg-dark" style="color: #fff;" data-desc="${value.description}" data-id="${value.id}" value="${value.name}">${value.name}</option>`);
          });
        
    
        $("#stream-tags").selectpicker("refresh");

        // Adiciona um listener de evento para o seletor de opções
        selectpicker_tags.addEventListener('change', event => {
            // Obtém o valor do seletor de opções selecionado
            const selectedValue_tags = event.target.value;
            // Encontra o objeto JSON correspondente com base no nome selecionado
            const selectedItem_tags = Object.values(data_tags).find(key => key.name === selectedValue_tags);
    
            var div_tags = document.getElementById("tags");
            var spans = div_tags.querySelectorAll('p');
            var txt = selectedItem_tags.name
            var id_tag = selectedItem_tags.description
            var finded = false;
    
            if(txt){
    
              for (var i = 0; i < spans.length; i++) { 
    
                  if (spans[i].textContent.trim() === txt) { 
                    finded = true;
                  }
              }
    
              if (!finded) {
    
                  var span_tags = document.createElement("p")
                  span_tags.innerHTML = txt.toLowerCase();
                  span_tags.id = id_tag.toLowerCase();
                  document.getElementById("tags").appendChild(span_tags);
              }
            }
    
        });
        });
    }
    
}

function save_stream_info(){

    var stream_title = document.getElementById("stream-title").value;
    var stream_game = document.getElementById("stream-game").value;
    var stream_game_name = document.getElementById('stream-game-inp').value;

    var div_tags = document.getElementById("tags");
    var tags_get = div_tags.querySelectorAll('p');
    var tags_list = []

    for (var i = 0; i < tags_get.length; i++) { // percorre todos os elementos span
        tags_list.push(tags_get[i].textContent)
    }

    data = {
        title : stream_title,
        game : stream_game_name,
        game_id : stream_game,
        tags : tags_list
    }

    var formData = JSON.stringify(data);
    window.pywebview.api.save_stream_info_py(formData);

}

function create_poll_option(){
    

    var options_len = document.getElementById("poll-options");
    var options_count = options_len.children.length;


    if (options_count < 5) {

        var label = document.createElement("label");
        label.setAttribute("for", `poll-${parseInt(options_count,10)}`);
        label.innerHTML = `Opção ${parseInt(options_count,10) + 1}`;
    
        var new_option = document.createElement('input');
        new_option.type = "text";
        new_option.classList.add("form-control","w-100","bg-dark","mt-3");
        new_option.id = `poll-${parseInt(options_count,10)}`
    
        var div_option = document.createElement('div');
        div_option.classList.add("form-group", "w-100");
        div_option.appendChild(label);
        div_option.appendChild(new_option);
    
        options_len.appendChild(div_option);

    } else {

        var warn_text = document.getElementById('poll-warn');
        warn_text.style.display = 'block';
    
    }


}

function create_prediction_option(){

    var options_len = document.getElementById("prediction-options");
    var options_count = options_len.children.length;

    if (options_count < 10) {

        var label = document.createElement("label");
        label.setAttribute("for", `prediction-${parseInt(options_count,10)}`);
        label.innerHTML = `Opção ${parseInt(options_count,10) + 1}`;
    
        var new_option = document.createElement('input');
        new_option.type = "text";
        new_option.classList.add("form-control","w-100","bg-dark","mt-3");
        new_option.id = `prediction-${parseInt(options_count,10)}`
    
        var div_option = document.createElement('div');
        div_option.classList.add("form-group", "w-100");
        div_option.appendChild(label);
        div_option.appendChild(new_option);
    
        options_len.appendChild(div_option);

    } else {

        var warn_text = document.getElementById('prediction-warn');
        warn_text.style.display = 'block';
    
    }
}

function channel_points_pool(){

    var enable_channel_points = document.getElementById('enable-channelpoints-pool');
    var div_channel_points = document.getElementById('channel-points-poll-div');
    var input_channel_points = document.getElementById('poll-channel-points');

    if (enable_channel_points.checked == true){
        div_channel_points.style.display = 'block';
        input_channel_points.setAttribute('required', 'true');
    } else if (enable_channel_points.checked == false){
        div_channel_points.style.display = 'none';
        input_channel_points.setAttribute('required', 'false');
    }
}

let isRunning_poll

async function updateProgressBar_poll(startTime, endTime) {

    if (isRunning_poll) { // Verifica se a função já está sendo executada
        return;
      }
      
      isRunning_poll = true; // Define a variável de controle como true

    startTime = startTime.replace(/\.(\d{1,})/, '');
    endTime = endTime.replace(/\.(\d{1,})/, '')

    startTime = new Date(startTime)
    startTime = new Date(startTime).toUTCString();
    startTime = Date.parse(startTime);

    endTime = new Date(endTime)
    endTime = new Date(endTime).toUTCString();
    endTime = Date.parse(endTime);
    
    while (true){

        var now_gmt = new Date().getTime();
        var now_utc = new Date(now_gmt).toUTCString();
        var now = Date.parse(now_utc);  // Obtém o tempo atual em milissegundos
        var totalTime = endTime - startTime; // Calcula o tempo total em milissegundos
        var elapsedTime = now - startTime; // Calcula o tempo decorrido em milissegundos
        var progress = elapsedTime / totalTime; // Calcula a porcentagem de progresso
        
        // Seleciona a barra de progresso e atualiza sua largura de acordo com o progresso
        var progressBar_polç = document.getElementById("progress-bar-poll");

        progressBar_polç.style.width = `${(1 - progress) * 100}%`;

        if (progress >= 1) {

            var progress_bar_poll = document.getElementById("progress-poll-modal");

            progress_bar_poll.hidden = true
            break; 
        }

        await sleep(1000)
    }

    isRunning_poll = false;
}

function getBarWithMaxVotes() {

    var progressBars = document.querySelectorAll(".progress-bar-options");
    var maxVotes = 0;
    var barWithMaxVotes;
    progressBars.forEach((bar) => {
      var votes = parseInt(bar.getAttribute("votes"));
      if (votes > maxVotes) {
        maxVotes = votes;
        barWithMaxVotes = bar.dataset.title;
      } else {
        barWithMaxVotes = 0
      }
    });
    return barWithMaxVotes;
}

async function updateProgressBar_votes() {

    while (true){

        var data = {
            type_id : 'get'
        }
    
        var formData = JSON.stringify(data);
        get_poll_parse = await window.pywebview.api.poll_py(formData);
    
        if (get_poll_parse){
            get_poll_parse = JSON.parse(get_poll_parse)
            var options_poll = get_poll_parse.options
            var status_poll = get_poll_parse.status
            
            if (status_poll == "started"){

                for (item in options_poll) {
    
                    var title = options_poll[item]['title']
                    var votes = options_poll[item]['votes']
        
                    var bar_up = document.querySelector(`div[data-title="${title}"]`)
                    var span_bar = document.querySelector(`span[data-title="${title}"]`);
                    
                    bar_up.setAttribute('votes',votes)
                    span_bar.innerHTML = `Opção : ${title} | Votos : ${votes}`
                }

                                // Seleciona todas as divs com a classe "progress-bar"
                var progressBars = document.querySelectorAll(".progress-bar-options");
                // Itera sobre as divs e atualiza a largura da barra de progresso com base nos votos
                var totalVotes = 0;
            
                // Calcula o total de votos
                progressBars.forEach((bar) => {
                    var votes = parseInt(bar.getAttribute("votes"));
                    totalVotes += votes;
                });
                
                // Calcula a média de votos para cada barra e atualiza a largura da barra de progresso
                progressBars.forEach((bar) => {
                    var votes = parseInt(bar.getAttribute("votes"));
                    var percentage = totalVotes === 0 ? 0 : (votes / totalVotes) * 100;
                    bar.style.width = percentage.toFixed(1) + "%";
                });

                await sleep(1000)

            } else if (status_poll == "completed"){
                
                var poll_status = document.getElementById("poll_status");
                poll_status.innerHTML = "Votação concluida! Aguarde alguns instantes para iniciar uma nova votação.";

                var bar_max = getBarWithMaxVotes();

                if (bar_max != 0) {

                    var bar_winner = document.querySelector(`div[data-title="${bar_max}"]`)
                    bar_winner.style.backgroundColor = "#04db83";
    
                    var span_bar = document.querySelector(`span[data-title="${bar_max}"]`);
                    span_bar.style.color = "#000"
                    span_bar.style.fontSize = "20px"
    
                    var content_winner = span_bar.textContent ;
    
                    bar_winner.style.height = "50px";
                    span_bar.innerHTML = `<i class="fa-solid fa-trophy"></i> Vencedor !! ${content_winner}`
    
                    break;

                } else {
                    poll_status.innerHTML = "Sem votos. Aguarde alguns instantes para iniciar uma nova votação.";
                }
                
            }
        }
    }
}

async function poll(type_id){
 
    var poll_running_div = document.getElementById("poll-running");
    var poll_start_div = document.getElementById("poll-start")
    var title_poll_running = document.getElementById("title_poll_running")
    var progress_bar_poll = document.getElementById("progress-poll-modal");
    var options_current_poll = document.getElementById('options-poll-running');

    if (type_id == 'get'){

        var data = {
            type_id : 'get'
        }

        var formData = JSON.stringify(data);
        get_poll_parse = await window.pywebview.api.poll_py(formData);

        if (get_poll_parse){
            get_poll_parse = JSON.parse(get_poll_parse)
            var status_poll = get_poll_parse.status

            if (status_poll == "started") {

                progress_bar_poll.hidden = false
                options_current_poll.innerHTML = ""
                poll_start_div.hidden = true
                poll_running_div.hidden = false

                var title_poll = get_poll_parse.title
                var options_poll = get_poll_parse.options
                var time_started = get_poll_parse.time_start
                var time_ends = get_poll_parse.time_end

                title_poll_running.innerHTML = title_poll

                for (item in options_poll) {

                    var title = options_poll[item]['title']
                    var id = options_poll[item]['id']
                    var votes = options_poll[item]['votes']

                    var create_progress = document.createElement('div')
                    create_progress.classList.add('progress', 'progress-poll-options', 'mt-3', "position-relative")

                    var create_progress_inner = document.createElement('div')
                    create_progress_inner.setAttribute('data-title',`${title}`)
                    create_progress_inner.setAttribute('votes',votes)
                    create_progress_inner.style.width = 0 + "%";
                    create_progress_inner.classList.add('progress-bar','progress-bar-options', 'progress-bar-striped', 'progress-bar-animated')

                    var text_inner = document.createElement('span');
                    text_inner.classList.add("position-absolute","w-100","text-center","h-100","bar-text")
                    text_inner.setAttribute('data-title',`${title}`)
                    text_inner.innerHTML = `Opção : ${title} | Votos : ${votes}`


                    create_progress.appendChild(create_progress_inner)
                    create_progress.appendChild(text_inner)

                    options_current_poll.appendChild(create_progress)

                }

                updateProgressBar_poll(time_started,time_ends)
                updateProgressBar_votes()

            } else if  (status_poll == "archived"){

                poll_start_div.hidden = false
                poll_running_div.hidden = true

            }

        }

    } else if (type_id == 'create'){

        poll_start_div.hidden = false
        poll_running_div.hidden = true

        var poll_title = document.getElementById('poll-title').value;
        var poll_options = document.querySelectorAll('#poll-options input');
        var poll_duration = document.getElementById('poll-duration');
        var poll_points_status = document.getElementById('enable-channelpoints-pool');
        var poll_points = document.getElementById('poll-channel-points');
        var poll_discord = document.getElementById('enable-discord-not-pool');

        poll_options_list = []

        poll_options.forEach(input => {
            const val = input.value;
            poll_options_list.push(val);
        });

        poll_points_status = poll_points_status.checked ? 1 : 0;
        poll_discord = poll_discord.checked ? 1 : 0;

        var data = {
            type_id : 'create',
            title :poll_title,
            options : poll_options_list,
            duration : poll_duration.value,
            points_status :poll_points_status,
            points : poll_points.value,
            discord : poll_discord
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.poll_py(formData);
    }
}

let isRunning = false;

async function updateProgressBar(startTime, endTime) {

    if (isRunning) { // Verifica se a função já está sendo executada
        return;
      }
      
    isRunning = true; // Define a variável de controle como true

    startTime = startTime.replace(/\.(\d{1,})/, '');
    endTime = endTime.replace(/\.(\d{1,})/, '')

    startTime = new Date(startTime)
    startTime = new Date(startTime).toUTCString();
    startTime = Date.parse(startTime);

    endTime = new Date(endTime)
    endTime = new Date(endTime).toUTCString();
    endTime = Date.parse(endTime);
    
    while (true){

        const now_gmt = new Date().getTime();
        const now_utc = new Date(now_gmt).toUTCString();
        const now = Date.parse(now_utc);  // Obtém o tempo atual em milissegundos
        const totalTime = endTime - startTime; // Calcula o tempo total em milissegundos
        const elapsedTime = now - startTime; // Calcula o tempo decorrido em milissegundos
        const progress = elapsedTime / totalTime; // Calcula a porcentagem de progresso
        
        // Seleciona a barra de progresso e atualiza sua largura de acordo com o progresso
        const progressBar = document.getElementById("progress-bar");
        progressBar.style.width = `${(1 - progress) * 100}%`;

        if (progress >= 1) {
            var progress_bar = document.getElementById("progress-pred-modal");
            var status_pred = document.getElementById('status-pred');
            progress_bar.hidden = true
            status_pred.innerHTML = "Selecione e envie o resultado do palpite"
            break; 
        }

        await sleep(1000)
    }

    isRunning = false;
}


async function prediction_small() {

    data = {
        type_id : 'get',
    }

    var formData = JSON.stringify(data);
    var pred_info_parse = await window.pywebview.api.prediction_py(formData)

    if (pred_info_parse){

        pred_info_parse = JSON.parse(pred_info_parse)

        var status = pred_info_parse.status;

        var title_current = document.getElementById('status-pred-small');
        var bar = document.getElementById('progress-small');

        if (status == 'running') {

            bar.hidden = false

            var time_start = pred_info_parse.start_time
            var time_end = pred_info_parse.lock_time

            startTime = time_start.replace(/\.(\d{1,})/, '');
            endTime = time_end.replace(/\.(\d{1,})/, '')
        
            startTime = new Date(startTime)
            startTime = new Date(startTime).toUTCString();
            startTime = Date.parse(startTime);
        
            endTime = new Date(endTime)
            endTime = new Date(endTime).toUTCString();
            endTime = Date.parse(endTime);

            const now_gmt = new Date().getTime();
            const now_utc = new Date(now_gmt).toUTCString();
            const now = Date.parse(now_utc);  // Obtém o tempo atual em milissegundos
            const totalTime = endTime - startTime; // Calcula o tempo total em milissegundos
            const elapsedTime = now - startTime; // Calcula o tempo decorrido em milissegundos
            const progress = elapsedTime / totalTime; // Calcula a porcentagem de progresso
            
            // Seleciona a barra de progresso e atualiza sua largura de acordo com o progresso
            const progressBar = document.getElementById("progress-bar-small");
            progressBar.style.width = `${(1 - progress) * 100}%`;
            
            title_current.innerHTML = "Palpite em andamento, recebendo votações."

        } else if (status == 'locked'){

            bar.hidden = true

            title_current.innerHTML = "Palpite aguardando seleção de resultado."

        } else if (status == 'end'){

            bar.hidden = true
            
            title_current.innerHTML = "Nenhum palpite em andamento."
        }
    }
}

async function poll_small() {
    
    data = {
        type_id : 'get',
    }

    var formData = JSON.stringify(data);
    var poll_info_parse = await window.pywebview.api.poll_py(formData)

    if (poll_info_parse){

        poll_info_parse = JSON.parse(poll_info_parse)

        var status = poll_info_parse.status;

        var poll_running_div = document.getElementById("poll-running");
        var poll_start_div = document.getElementById("poll-start")
        
        var title_current = document.getElementById('status-poll-small');
        var poll_bar_smal = document.getElementById('progress-poll-small');

        if (status == 'started') {

            poll_bar_smal.hidden = false

            var time_start_poll = poll_info_parse.time_start
            var time_end_poll = poll_info_parse.time_end

            startTime_poll = time_start_poll.replace(/\.(\d{1,})/, '');
            endTime_poll = time_end_poll.replace(/\.(\d{1,})/, '')
        
            startTime_poll = new Date(startTime_poll)
            startTime_poll = new Date(startTime_poll).toUTCString();
            startTime_poll = Date.parse(startTime_poll);
        
            endTime_poll = new Date(endTime_poll)
            endTime_poll = new Date(endTime_poll).toUTCString();
            endTime_poll = Date.parse(endTime_poll);

            const now_gmt_poll = new Date().getTime();
            const now_utc_poll = new Date(now_gmt_poll).toUTCString();
            const now_poll = Date.parse(now_utc_poll);  // Obtém o tempo atual em milissegundos
            const totalTime_poll = endTime_poll - startTime_poll; // Calcula o tempo total em milissegundos
            const elapsedTime_poll = now_poll - startTime_poll; // Calcula o tempo decorrido em milissegundos
            const progress_poll = elapsedTime_poll / totalTime_poll; // Calcula a porcentagem de progresso
            
            // Seleciona a barra de progresso e atualiza sua largura de acordo com o progresso
            const progressBar_poll = document.getElementById("progress-bar-poll-small");
            progressBar_poll.style.width = `${(1 - progress_poll) * 100}%`;
            
            title_current.innerHTML = "Votação em andamento, recebendo votos."

        } else if (status == 'completed'){

            poll_bar_smal.hidden = true
            title_current.innerHTML = "Votação finalizada, clique para ver o resultado."

        } else if (status == 'archived'){

            poll_running_div.hidden = true
            poll_start_div.hidden = false
            poll_bar_smal.hidden = true

            title_current.innerHTML = "Nenhuma votação em andamento."
        }
    }
}

async function update_small(){

    while (true){

        poll_small()
        prediction_small()

        await sleep(1000)
    }

}

function show_modal(modal_id){

    var modal = new bootstrap.Modal(document.getElementById(modal_id))

    if (modal_id == 'create-prediction'){
        prediction('get')
    } else if (modal_id == 'create-poll'){
        poll('get')
    }
    modal.show()
}

async function prediction(type_id) {

    if (type_id == 'start'){

        var pred_title = document.getElementById('prediction-title');
        var pred_options = document.querySelectorAll('#prediction-options input');
        var pred_time = document.getElementById('prediction-duration');
        var pred_discord = document.getElementById('enable-discord-not-prediction')

        pred_options_list = []

        pred_options.forEach(input => {
            const val = input.value;
            pred_options_list.push(val);
        });


        pred_discord = pred_discord.checked ? 1 : 0;

        var data = {
            type_id : 'start',
            title :pred_title.value,
            options : pred_options_list,
            duration : pred_time.value,
            discord : pred_discord
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.prediction_py(formData);

    } else if (type_id == 'get'){

        var data = {
            type_id : 'get'
        }

        var formData = JSON.stringify(data);
        var pred_info_parse = await window.pywebview.api.prediction_py(formData)
    
        if (pred_info_parse){
            pred_info_parse = JSON.parse(pred_info_parse)
            var status = pred_info_parse.status;

            var body_running = document.getElementById('current-pred');
            var body_start = document.getElementById('start-pred');

            var status_pred = document.getElementById('status-pred');
            var title_current = document.getElementById('pred_current_title');
            var options_current = document.getElementById('options_current');
            var progress_bar = document.getElementById("progress-pred-modal");

            var btn_pred_lock = document.getElementById("lock_pred");
            var btn_pred_send = document.getElementById("send_pred");

            if (status == 'running') {

                progress_bar.hidden = false
                options_current.innerHTML = "";

                body_running.hidden = false;
                body_start.hidden = true;
        
                btn_pred_lock.hidden = false
                btn_pred_send.hidden = true

                title_current.innerHTML = pred_info_parse.title
                options_list = pred_info_parse.options

                var time_start = pred_info_parse.start_time
                var time_end = pred_info_parse.lock_time

                updateProgressBar(time_start,time_end)
                
                for (id in options_list) {
                    idx_dict = options_list[id];

                    key = Object.keys(idx_dict)[0]
                    id_op = options_list[id][key];

                    var div_form = document.createElement('div');
                    div_form.classList.add('form-check',"d-grid", "gap-2", "mx-auto", "mt-2")

                    var op_checkbox = document.createElement('input');
                    op_checkbox.setAttribute('type', 'radio')
                    op_checkbox.classList.add('btn-check')
                    op_checkbox.setAttribute('name', 'options')
                    op_checkbox.setAttribute('id',id_op)
                    op_checkbox.setAttribute('value', id_op)

                    var op_checkbox_label = document.createElement('label');
                    op_checkbox_label.classList.add('btn' ,'btn-outline-secondary')
                    op_checkbox_label.setAttribute('for', id_op)
                    op_checkbox_label.innerHTML = key

                    div_form.appendChild(op_checkbox)
                    div_form.appendChild(op_checkbox_label)

                    options_current.appendChild(div_form)

                    status_pred.innerHTML = "Palpite em andamento, recebendo votações."
                }

            } else if (status == 'locked'){

                
                options_current.innerHTML = "";

                btn_pred_lock.hidden = true
                btn_pred_send.hidden = false

                body_running.hidden = false;
                body_start.hidden = true;
                progress_bar.hidden = true

                title_current.innerHTML = pred_info_parse.title
                options_list = pred_info_parse.options

                for (id in options_list) {

                    idx_dict = options_list[id];

                    key = Object.keys(idx_dict)[0]
                    id_op = options_list[id][key];

                    var div_form = document.createElement('div');
                    div_form.classList.add('form-check',"d-grid", "gap-2", "mx-auto", "mt-2")

                    var op_checkbox = document.createElement('input');
                    op_checkbox.setAttribute('type', 'radio')
                    op_checkbox.classList.add('btn-check')
                    op_checkbox.setAttribute('name', 'options')
                    op_checkbox.setAttribute('id',id_op)
                    op_checkbox.setAttribute('value', id_op)

                    var op_checkbox_label = document.createElement('label');
                    op_checkbox_label.classList.add('btn' ,'btn-outline-secondary')
                    op_checkbox_label.setAttribute('for', id_op)
                    op_checkbox_label.innerHTML = key

                    div_form.appendChild(op_checkbox)
                    div_form.appendChild(op_checkbox_label)

                    options_current.appendChild(div_form)

                    status_pred.innerHTML = "Aguardando seleção de resultado."
                }

            } else if (status == 'end'){

                body_running.hidden = true;
                body_start.hidden = false

            }

        }
    } else if (type_id == 'lock') {

        var btn_pred_lock = document.getElementById("lock_pred");
        var btn_pred_send = document.getElementById("send_pred");
        var status_pred = document.getElementById('status-pred');
        var progress_bar = document.getElementById("progress-pred-modal");

        progress_bar.hidden = true
        btn_pred_lock.hidden = true
        btn_pred_send.hidden = false

        data = {
            type_id : 'lock',
        }

        var formData = JSON.stringify(data);
        var pred_info = await window.pywebview.api.prediction_py(formData)

        status_pred.innerHTML = "Aguardando seleção de resultado."

    } else if (type_id == 'send') {

        const radioDiv = document.getElementById("options_current"); // Seleciona o elemento div
        const radios = radioDiv.querySelectorAll("input[type='radio']");

        let selectedValue = null; // Inicializa a variável de valor selecionado como nula

        radios.forEach((radio) => {
            if (radio.checked) { // Verifica se o input de rádio está selecionado
                selectedValue = radio.value; // Armazena o valor do input selecionado na variável
            }
        });

        data = {
            type_id : 'send',
            op_id: selectedValue,
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.prediction_py(formData)

        

    }
}

async function goal() {

    while (true){

        data_goal_parse = await window.pywebview.api.goal_py()

        if (data_goal_parse){

            data_goal_parse = JSON.parse(data_goal_parse)

            var goal_follow_status = document.getElementById('status-goal-follows-small')
            var goal_sub_status = document.getElementById('status-goal-subs-small')
    
            var goal_follow_status_bar_value = document.getElementById('progress-goal-follows-small-int')
            var goal_sub_status_bar_value = document.getElementById('progress-goal-subs-small-int')

            var goal_follow_status_bar = document.getElementById('progress-goal-follows-small')
            var goal_sub_status_bar = document.getElementById('progress-goal-subs-small')
    
            var follow_current = data_goal_parse.follow.current_amount
            var follow_target = data_goal_parse.follow.target_amount
    
            var sub_current = data_goal_parse.subscription_count.current_amount
            var sub_target = data_goal_parse.subscription_count.target_amount
    
            if (follow_target != 0){
                
                goal_follow_status_bar.hidden = false

                goal_follow_status.innerHTML = `${follow_current}/${follow_target}`
    
                var value_follow = (follow_current / follow_target) * 100;
                
                goal_follow_status_bar_value.value = value_follow;
                goal_follow_status_bar_value.style.width = `${(value_follow)}%`;
    
            } else {
                goal_follow_status_bar.hidden = true
            }
            
            if (sub_target != 0){

                goal_sub_status_bar.hidden = false 

                goal_sub_status.innerHTML = `${sub_current}/${sub_target}`
    
                var value_subs = (sub_current / sub_target) * 100;
                
                goal_sub_status_bar_value.value = value_subs;
                goal_sub_status_bar_value.style.width = `${(value_subs)}%`;

            } else {

                goal_sub_status_bar.hidden = true
            }
        }

        await sleep(10000)

    }
}

function slider_font_events() {
    slider = document.getElementById('slider-font-events');
    output = document.getElementById('rangevalue_config_events');
    $('.chat-message ').css("font-size", slider.value + "px");
    output.innerHTML = slider.value
};


async function event_log_config(type_id){

    var font_size_events = document.getElementById('slider-font-events');
    var font_size_range = document.getElementById('rangevalue_config_events');
    var show_time_events = document.getElementById('data-show-events');
    var color_events = document.getElementById('color-events').value;
    var show_redeem = document.getElementById('show-redeem');
    var show_commands = document.getElementById('show-commands');
    var show_events = document.getElementById('show-events');
    var show_join = document.getElementById('show-join');
    var show_leave = document.getElementById('show-leave');

    var show_redeem_chat = document.getElementById('show-redeem-chat');
    var show_commands_chat = document.getElementById('show-commands-chat');
    var show_events_chat = document.getElementById('show-events-chat');
    var show_join_chat = document.getElementById('show-join-chat');
    var show_leave_chat = document.getElementById('show-leave-chat');



    if (type_id == 'save'){

        show_time_events = show_time_events.checked ? 1 : 0;
        show_join = show_join.checked ? 1 : 0;
        show_leave = show_leave.checked ? 1 : 0;
        show_events = show_events.checked ? 1 : 0;
        show_commands = show_commands.checked ? 1 : 0;
        show_redeem = show_redeem.checked ? 1 : 0;
        
        show_join_chat = show_join_chat.checked ? 1 : 0;
        show_leave_chat = show_leave_chat.checked ? 1 : 0;
        show_events_chat = show_events_chat.checked ? 1 : 0;
        show_commands_chat = show_commands_chat.checked ? 1 : 0;
        show_redeem_chat = show_redeem_chat.checked ? 1 : 0;

        data = {
            data_show : show_time_events,
            show_join : show_join,
            show_leave : show_leave,
            show_events : show_events,
            show_commands : show_commands,
            show_redeem : show_redeem,
            show_join_chat : show_join_chat,
            show_leave_chat : show_leave_chat,
            show_events_chat : show_events_chat,
            show_commands_chat : show_commands_chat,
            show_redeem_chat : show_redeem_chat,
            font_size : font_size_events.value,
            color_events : color_events
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.event_log(type_id,formData);

    } else if (type_id == 'get'){

        var event_data_parse = await window.pywebview.api.event_log('get_config','null')

        if (event_data_parse){

            event_data_parse = JSON.parse(event_data_parse)

            font_size_events.value = event_data_parse.font_size
            show_time_events.checked = event_data_parse.show_time_events == 1 ? true : false;
            show_redeem.checked = event_data_parse.show_redeem == 1 ? true : false;
            show_commands.checked = event_data_parse.show_commands == 1 ? true : false;
            show_events.checked = event_data_parse.show_events == 1 ? true : false; 
            show_join.checked = event_data_parse.show_join == 1 ? true : false;
            show_leave.checked = event_data_parse.show_leave == 1 ? true : false;


            show_redeem_chat.checked = event_data_parse.show_redeem_chat == 1 ? true : false;
            show_commands_chat.checked = event_data_parse.show_commands_chat == 1 ? true : false;
            show_events_chat.checked = event_data_parse.show_events_chat == 1 ? true : false; 
            show_join_chat.checked = event_data_parse.show_join_chat == 1 ? true : false;
            show_leave_chat.checked = event_data_parse.show_leave_chat == 1 ? true : false;

            font_size_range.innerHTML = event_data_parse.font_size + 'px';

            $("#color-events").selectpicker('val', event_data_parse.color_events);

        }

    }


}

async function show_error_log(type_id){

    if (type_id == 'get-errorlog'){

        $("#errorlog-modal").modal("show");

        $('#errorlog-textarea').val('');

        var errors_data = await window.pywebview.api.open_py('errolog','null')
    
        if (errors_data){
    
            var textarea = document.getElementById('errorlog-textarea');
    
            $('#errorlog-textarea').val(errors_data);
            
            textarea.scrollTop = textarea.scrollHeight;
        }

    } else if (type_id == 'clear-errorlog'){

        $("#errorlog-modal").modal("hide");
        $('#errorlog-textarea').val('');

        window.pywebview.api.open_py('errolog_clear','null')

    }

}

async function highlight_js(type_id){

    var status_highlight = document.getElementById("status-highlight");
    var font_size = document.getElementById("font-size-highlight");
    var font_weight = document.getElementById("font-weight-highlight");
    var color_message = document.getElementById("color-message-highlight");
    var color_username = document.getElementById("color-username-highlight");
    var duration = document.getElementById("duration-highlight");

    if (type_id == 'get'){

        get_highlight_parse = await window.pywebview.api.highlight_py(type_id,'null');

        if (get_highlight_parse){

            get_highlight_parse = JSON.parse(get_highlight_parse)

            status_highlight.checked = get_highlight_parse.status == 1 ? true : false;

            font_size.value = get_highlight_parse.font_size;
            font_weight.value = get_highlight_parse.font_weight;
            color_message.value = get_highlight_parse.color_message;
            color_username.value = get_highlight_parse.color_username;
            duration.value = get_highlight_parse.duration;

        }

    } else if (type_id == 'save'){
        
        var status = status_highlight.checked ? 1 : 0;

        data = {
            status : status,
            font_size : font_size.value,
            font_weight : font_weight.value,
            color_message : color_message.value,
            color_username : color_username.value,
            duration : duration.value
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.highlight_py(type_id,formData);
    }

}

async function debug_status(type_id){

    var status_debug = document.getElementById("debug-status");

    if (type_id == "debug-save"){

        status_debug = status_debug.checked ? 1 : 0;

        window.pywebview.api.open_py(type_id,status_debug)

    } else if (type_id == "debug-get"){

        var get_debug = await window.pywebview.api.open_py(type_id,'null');

        if (get_debug){

            status_debug.checked = get_debug == 1 ? true : false;

        }
    }

}

async function create_source(type_id){
    window.pywebview.api.create_source(type_id,);
}