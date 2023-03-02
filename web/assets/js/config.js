//CONFIG

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function getFolder_image(id) {
    var dosya_path = await eel.select_file_image_py()();
    if (dosya_path) {
        document.getElementById(id).value = dosya_path;
    }
}

async function get_redeem_js_config(el_id) {

    var list_redem = await eel.get_redeem('null')();

    if (list_redem) {
        
        $("#" + el_id).empty();

        var list_redem_parse = JSON.parse(list_redem);

        $("#" + el_id).append('<option style="background: #000; color: #fff;" value="None">Sem recompensa</option>');
        $("#" + el_id).selectpicker("refresh");

        for (var i = 0; i < list_redem_parse.redeem.length; i++) {
            var optn = list_redem_parse.redeem[i];

            $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + el_id).selectpicker("refresh");
        }
    }
}

async function get_messages_config_js() {
    
    var enable_tts_command = document.getElementById("enable-tts-module");
    var enable_commands = document.getElementById("enable-commands");
    var enable_responses = document.getElementById("enable-responses");
    var enable_delay_response = document.getElementById("enable-delay-response");
    var enable_clip_responses = document.getElementById("enable-clip-responses");
    var enable_permisson_responses = document.getElementById("enable-permisson-responses");
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

async function obs_config_js(event,type_id) {


    if (type_id == 'get'){

        var conn_info = await eel.obs_config_py(type_id,'null')();

        if (conn_info) {

            var conn_info_parse = JSON.parse(conn_info);

            document.getElementById("obs-host").value = conn_info_parse.host;
            document.getElementById("obs-port").value = conn_info_parse.port;
            document.getElementById("obs-password").value = conn_info_parse.password;
        }

    } else if (type_id == 'get_not'){

        

        var not_enabled = document.getElementById('not-enabled')
        var not_music = document.getElementById('not-music-enabled')
        var not_events = document.getElementById('not-events-enabled')
        var time_show_not_events = document.getElementById('time-show-not-events')
        var time_show_not = document.getElementById('time-show-not')

        var not_info = await eel.obs_config_py(type_id,'null')();

        if (not_info) {

            var not_info_parse = JSON.parse(not_info);

            not_enabled.checked = not_info_parse.html_active == 1 ? true : false;
            not_music.checked = not_info_parse.html_player_active == 1 ? true : false;
            not_events.checked = not_info_parse.html_events_active == 1 ? true : false;

            time_show_not_events.value = not_info_parse.html_events_time
            time_show_not.value = not_info_parse.html_time

            $("#not-source-name").append('<option style="background: #000; color: #fff;" value="'+ not_info_parse.html_title +'"selected> '+ not_info_parse.html_title +'</option>');
            $("#video-source-name").append('<option style="background: #000; color: #fff;" value="'+ not_info_parse.html_video +'" selected> '+ not_info_parse.html_video +'</option>');
            $("#events-source-name").append('<option style="background: #000; color: #fff;" value="'+ not_info_parse.html_events +'" selected>'+ not_info_parse.html_events +'</option>');

            $("#not-source-name").selectpicker("refresh");
            $("#video-source-name").selectpicker("refresh");
            $("#events-source-name").selectpicker("refresh");

            
        }
    } else if (type_id == 'save_conn'){
        event.preventDefault();

        var form = document.querySelector("#obs-conn-form");
    
        data = {
            host: form.querySelector('#obs-host').value,
            port: form.querySelector('#obs-port').value,
            pass: form.querySelector('#obs-password').value,
            conn: auto_con
        };
    
        var formData = JSON.stringify(data);
        eel.obs_config_py(type_id,formData);

    } else if (type_id == 'save_not'){
        event.preventDefault();

        var form = document.querySelector("#obs-not-form");
        var not_enabled_status = form.querySelector('#not-enabled').checked;
        var not_music_enabled_status = form.querySelector('#not-music-enabled').checked;
        var not_event_enabled_status = form.querySelector('#not-events-enabled').checked;
        
        not_enabled_status = not_enabled_status ? 1 : 0;
        not_music_enabled_status = not_music_enabled_status ? 1 : 0;
        not_event_enabled_status = not_event_enabled_status ? 1 : 0;
        
        data = {
            not_enabled: not_enabled_status,
            not_music: not_music_enabled_status,
            not_event: not_event_enabled_status,
            source_name: form.querySelector('#not-source-name').value,
            video_source_name: form.querySelector('#video-source-name').value,
            event_source_name: form.querySelector('#events-source-name').value,
            time_showing_not: form.querySelector('#time-show-not').value,
            time_showing_event_not: form.querySelector('#time-show-not-events').value,
        };
    
        var formData = JSON.stringify(data);
        eel.obs_config_py(type_id,formData);

    }

}

async function config_responses_js(event,fun_id_responses) {

    event.preventDefault();

    var button_el = document.getElementById('submit-responses-config');
    var select_id_el = document.getElementById('response-select-edit').value;
    var in_reponse_el = document.getElementById('response-message-new');

    if (fun_id_responses == 'get_response'){
        
        console.log(select_id_el)

        var messages = await eel.responses_config('get_response',select_id_el,'none')();
    
        if (messages) {

            button_el.removeAttribute("disabled");
            in_reponse_el.value = messages;
    
            }

    } else if (fun_id_responses == "save-response"){

        eel.responses_config('save_response',select_id_el,in_reponse_el.value)
        in_reponse_el = '';
    }
}

function show_config_div(div_id) {

    if (div_id == "config-conn-obs-div") {
        obs_config_js('event','get');
    } else if (div_id == "config-not-obs-div") {
        obs_config_js('event','get_not');
    } else if (div_id == "config-chat-messages-div") {
        get_messages_config_js();
    } else if (div_id == "config-discord-div") {
        discord_js('event','get');
    } else if (div_id == "config-music-div"){
        get_redeem_js_config('redeem-select-music')
        sr_config_js('event','get')
    } else if (div_id == "chat-config-div"){
        chat_config('get')
    } else if (div_id == "userdata-div"){
        userdata_js('get')
    }

    document.getElementById("config-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_config_div(div_id, modal) {
    $("#" + modal).modal("hide");
    document.getElementById("config-div").hidden = false;
    document.getElementById(div_id).hidden = true;
}

function config_messages_change(event) {
    event.preventDefault();

    var form = document.querySelector("#chat-messages-config-form");

    var enable_tts_module = form.querySelector('input[id="enable-tts-module"]');
    var enable_commands = form.querySelector('input[id="enable-commands"]');
    var enable_responses = form.querySelector('input[id="enable-responses"]');
    var enable_delay_response = form.querySelector('input[id="enable-delay-response"]');
    var enable_clip_responses = form.querySelector('input[id="enable-clip-responses"]');
    var enable_permisson_responses = form.querySelector('input[id="enable-permisson-responses"]');
    var enable_timer_module = form.querySelector('input[id="enable-timer-module"]');
    var enable_message_music = form.querySelector('input[id="enable-message-music"]');
    var enable_message_next = form.querySelector('input[id="enable-message-next"]');
    var enable_message_error_music = form.querySelector('input[id="enable-message-error-music"]');

    if (enable_tts_module.checked == true) {
        enable_tts_module = 1;
    } else {
        enable_tts_module = 0;
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
        status_tts: enable_tts_module,
        status_commands: enable_commands,
        status_response: enable_responses,
        status_delay: enable_delay_response,
        status_clip: enable_clip_responses,
        status_permission: enable_permisson_responses,
        status_timer: enable_timer_module
    };

    var formData = JSON.stringify(data);

    eel.save_messages_config(formData);
}

function test_not(type_id){

    if (type_id == 'follow'){

        data = {
            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.follow",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "channel.follow",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "user_id": "836288612",
                    "user_login": "teste",
                    "user_name": "teste",
                    "broadcaster_user_id": "000000",
                    "broadcaster_user_login": "gg_tec",
                    "broadcaster_user_name": "GG_TEC",
                    "followed_at": "2022-02-15T21:26:03.58790142Z"
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);

    } else if (type_id == 'sub'){

        msg = '@badge-info=subscriber/1;badges=subscriber/0,premium/1;color=#8A2BE2;display-name=Teste;emotes=;flags=;id=00000;login=teste;mod=0;msg-id=sub;msg-param-cumulative-months=1;msg-param-goal-contribution-type=SUB_POINTS;msg-param-goal-current-contributions=1;msg-param-goal-target-contributions=50;msg-param-goal-user-contributions=1;msg-param-months=0;msg-param-multimonth-duration=1;msg-param-multimonth-tenure=0;msg-param-should-share-streak=0;msg-param-sub-plan-name=GG\sSubzim;msg-param-sub-plan=Prime;msg-param-was-gifted=false;room-id=779823875;subscriber=1;system-msg=Teste\ssubscribed\swith\sPrime.;tmi-sent-ts=1676675858543;user-id=0000000;user-type= :tmi.twitch.tv USERNOTICE #{USERLOGIN} : Teste de mensagem'
        eel.command_fallback(msg);

    } else if (type_id == 'resub'){
        
        data = {
            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.subscription.message",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "channel.subscription.message",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "user_id": "1234",
                    "user_login": "Teste",
                    "user_name": "Teste",
                    "broadcaster_user_id": "1337",
                    "broadcaster_user_login": "Teste",
                    "broadcaster_user_name": "Teste",
                    "tier": "1000",
                    "message": {
                        "text": "Love the stream! FevziGG",
                        "emotes": [
                            {
                                "begin": 17,
                                "end": 23,
                                "id": "302976485"
                            }
                        ]
                    },
                    "cumulative_months": 15,
                    "streak_months": 1, // null if not shared
                    "duration_months": 6
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);

    } else if (type_id == 'giftsub'){

        data = {
            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.subscription.gift",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "channel.subscription.gift",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "user_id": "1234",
                    "user_login": "cool_user",
                    "user_name": "Cool_User",
                    "broadcaster_user_id": "1337",
                    "broadcaster_user_login": "cooler_user",
                    "broadcaster_user_name": "Cooler_User",
                    "total": 2,
                    "tier": "1000",
                    "cumulative_total": 284, //null if anonymous or not shared by the user
                    "is_anonymous": false
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);
         
    } else if (type_id == 'raid'){
        
        data = {
            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.raid",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "cchannel.raid",
                    "version": "1",
                    "condition": {
                        "to_broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "from_broadcaster_user_id": "1234",
                    "from_broadcaster_user_login": "cool_user",
                    "from_broadcaster_user_name": "Cool_User",
                    "to_broadcaster_user_id": "1337",
                    "to_broadcaster_user_login": "cooler_user",
                    "to_broadcaster_user_name": "Cooler_User",
                    "viewers": 9001
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);

    } else if (type_id == 'bits1'){
        
        data = {
            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.cheer",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "channel.cheer",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "is_anonymous": false,
                    "user_id": "1234",
                    "user_login": "cool_user",  
                    "user_name": "Cool_User",   
                    "broadcaster_user_id": "1337",
                    "broadcaster_user_login": "cooler_user",
                    "broadcaster_user_name": "Cooler_User",
                    "message": "pogchamp",
                    "bits": 1
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);

    } else if (type_id == 'bits100'){


        data = {
            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.cheer",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "channel.cheer",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "is_anonymous": false,
                    "user_id": "1234",
                    "user_login": "cool_user",  
                    "user_name": "Cool_User",   
                    "broadcaster_user_id": "1337",
                    "broadcaster_user_login": "cooler_user",
                    "broadcaster_user_name": "Cooler_User",
                    "message": "pogchamp",
                    "bits": 100
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);

    } else if (type_id == 'bits1000'){

        data = {
            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.cheer",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "channel.cheer",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "is_anonymous": false,
                    "user_id": "1234",
                    "user_login": "cool_user",  
                    "user_name": "Cool_User",   
                    "broadcaster_user_id": "1337",
                    "broadcaster_user_login": "cooler_user",
                    "broadcaster_user_name": "Cooler_User",
                    "message": "pogchamp",
                    "bits": 1000
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);
        
    } else if (type_id == 'bits5000'){

        data = {

            "metadata": {
                "message_id": "Rz5CUTXgiX7y3ZYAwSwX8ID7dYm1zkDW43W-w0DK3TY=",
                "message_type": "notification",
                "message_timestamp": "2023-02-15T21:26:03.587909679Z",
                "subscription_type": "channel.cheer",
                "subscription_version": "1"
            },
            "payload": {
                "subscription": {
                    "id": "8ff22d32-4697-4d7e-a3a7-17535610af0f",
                    "status": "enabled",
                    "type": "channel.cheer",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": "0000000"
                    },
                    "transport": {
                        "method": "websocket",
                        "session_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    },
                    "created_at": "2022-02-15T21:24:56.760792011Z",
                    "cost": 0
                },
                "event": {
                    "is_anonymous": false,
                    "user_id": "1234",
                    "user_login": "cool_user",  
                    "user_name": "Cool_User",   
                    "broadcaster_user_id": "1337",
                    "broadcaster_user_login": "cooler_user",
                    "broadcaster_user_name": "Cooler_User",
                    "message": "pogchamp",
                    "bits": 5000
                }
            }
        }

        var not_data = JSON.stringify(data);
        eel.on_message('null',not_data);
        
    }
}

async function sr_config_js(event,type_id){
    
    if (type_id == 'get'){

        var music_not_status = document.querySelector("#not-music");
        var check_seletor = document.querySelector('#music-enable');
        var max_duration = document.getElementById("max-duration")
        var command_request = document.querySelector("#comand-request");
        var command_request_status = document.querySelector("#command-request-status");
        var command_request_delay = document.querySelector("#comand-request-delay");
        var command_volume = document.querySelector("#comand-volume");
        var command_volume_status = document.querySelector("#command-volume-status");
        var command_volume_delay = document.querySelector("#comand-volume-delay");
        var command_skip = document.querySelector("#comand-skip");
        var command_skip_status = document.querySelector("#command-skip-status");
        var command_skip_delay = document.querySelector("#comand-skip-delay");
        var command_next = document.querySelector("#comand-next");
        var command_next_status = document.querySelector("#command-next-status");
        var command_next_delay = document.querySelector("#comand-next-delay");
        var command_atual = document.querySelector("#comand-atual");
        var command_atual_status = document.querySelector("#command-atual-status");
        var command_atual_delay = document.querySelector("#comand-atual-delay");
    
        var data = await eel.sr_config_py(type_id,'null')();
    
        if(data){
    
            var music_config = JSON.parse(data);
    
            if(music_config.not_status == 1){
                music_not_status.checked = true
            }

            if (music_config.allow_music == 1){
                check_seletor.checked = true;
            } else if (music_config.allow_music == 0){
                check_seletor.checked = false;
            }
            
            if (music_config.cmd_request_status == 1){
                command_request_status.checked = true;
            } else if (music_config.cmd_request_status == 0){
                command_request_status.checked = false;
            }

            if (music_config.cmd_volume_status == 1){
                command_volume_status.checked = true;
            } else if (music_config.cmd_volume_status == 0){
                command_volume_status.checked = false;
            }

            if (music_config.cmd_skip_status == 1){
                command_skip_status.checked = true;
            } else if (music_config.cmd_skip_status == 0){
                command_skip_status.checked = false;
            }

            if (music_config.cmd_next_status == 1){
                command_next_status.checked = true;
            } else if (music_config.cmd_next_status == 0){
                command_next_status.checked = false;
            }

            if (music_config.cmd_atual_status == 1){
                command_atual_status.checked = true;
            } else if (music_config.cmd_atual_status == 0){
                command_atual_status.checked = false;
            }

            max_duration.value = music_config.max_duration;
            command_request.value = music_config.cmd_request;
            command_request_delay.value = music_config.cmd_request_delay;
            command_volume.value = music_config.cmd_volume;
            command_volume_delay.value = music_config.cmd_volume_delay;
            command_skip.value = music_config.cmd_skip;
            command_skip_delay.value = music_config.cmd_skip_delay;
            command_next.value = music_config.cmd_next;
            command_next_delay.value = music_config.cmd_next_delay;
            command_atual.value = music_config.cmd_atual;
            command_atual_delay.value = music_config.cmd_atual_delay;
    
            $("#redeem-select-music").selectpicker('val',music_config.redeem_music)
            $("#comand-sr-perm").selectpicker('val',music_config.request_perm)
            $("#comand-volume-perm").selectpicker('val',music_config.volume_perm)
            $("#comand-skip-perm").selectpicker('val',music_config.skip_perm)
            $("#comand-next-perm").selectpicker('val',music_config.next_perm)
            $("#comand-atual-perm").selectpicker('val',music_config.atual_perm)
    
            
        }
    } else if (type_id == 'save'){

        var check_seletor = document.getElementById('music-enable');
        var redeem_music_save = document.getElementById("redeem-select-music");
        var max_duration = document.getElementById("max-duration")
        var music_not_status_save = document.getElementById("not-music");
        var command_request_save = document.getElementById("comand-request");
        var command_request_status = document.getElementById("command-request-status");
        var command_request_perm = document.getElementById("comand-sr-perm");
        var command_request_delay = document.getElementById("comand-request-delay");
        var command_volume_save = document.getElementById("comand-volume");
        var command_volume_status = document.getElementById("command-volume-status");
        var command_volume_perm = document.getElementById("comand-volume-perm");
        var command_volume_delay = document.getElementById("comand-volume-delay");
        var command_skip_save = document.getElementById("comand-skip");
        var command_skip_status = document.getElementById("command-skip-status");
        var command_skip_perm = document.getElementById("comand-skip-perm");
        var command_skip_delay = document.getElementById("comand-skip-delay");
        var command_next_save = document.getElementById("comand-next");
        var command_next_status = document.getElementById("command-next-status");
        var command_next_perm = document.getElementById("comand-next-perm");
        var command_next_delay = document.getElementById("comand-next-delay");
        var command_atual_save = document.getElementById("comand-atual");
        var command_atual_status = document.getElementById("command-atual-status");
        var command_atual_perm = document.getElementById("comand-atual-perm");
        var command_atual_delay = document.getElementById("comand-atual-delay");
    
    
        if (music_not_status_save.checked == true){
            music_not_status_save = 1
        } else {
            music_not_status_save = 0
        }

        if (command_request_status.checked == true){
            command_request_status = 1
        } else {
            command_request_status = 0
        }

        if (command_volume_status.checked == true){
            command_volume_status = 1
        } else {
            command_volume_status = 0
        }

        if (command_skip_status.checked == true){
            command_skip_status = 1
        } else {
            command_skip_status = 0
        }

        if (command_next_status.checked == true){
            command_next_status = 1
        } else {
            command_next_status = 0
        }

        if (command_atual_status.checked == true){
            command_atual_status = 1
        } else {
            command_atual_status = 0
        }

        if (check_seletor.checked == true){
            allow_music = 1
        } else if (check_seletor.checked == false) {
            allow_music = 0
        }
    
    
        data = {
            redeem_music_data: redeem_music_save.value,
            max_duration: max_duration.value,
            allow_music_save : allow_music,
            music_not_status_data: music_not_status_save,
            command_request_data: command_request_save.value,
            command_request_perm: command_request_perm.value,
            command_request_delay: command_request_delay.value,
            command_request_status : command_request_status,
            command_volume_data: command_volume_save.value,
            command_volume_status : command_volume_status,
            command_volume_perm: command_volume_perm.value,
            command_volume_delay : command_volume_delay.value,
            command_skip_data: command_skip_save.value,
            command_skip_status: command_skip_status,
            command_skip_perm: command_skip_perm.value,
            command_skip_delay: command_skip_delay.value,
            command_next_data: command_next_save.value,
            command_next_status: command_next_status,
            command_next_perm: command_next_perm.value,
            command_next_delay: command_next_delay.value,
            command_atual_data: command_atual_save.value,
            command_atual_status : command_atual_status,
            command_atual_perm: command_atual_perm.value,
            command_atual_delay: command_atual_delay.value,
        }
    
        var formData = JSON.stringify(data);
        eel.sr_config_py(type_id,formData);
        
    } else if (type_id == 'list_get'){

        var music_data = await eel.sr_config_py(type_id,'null')()
        
        if (music_data){

            var music_data_parse = JSON.parse(music_data);

            $("#modal_list_block").modal("show")

            var tbody = document.getElementById('block-list-body');

            tbody.innerHTML = "";
        
            Object.entries(music_data_parse).forEach(([v,k]) => {
        
              tbody.innerHTML += '<tr><td>' + k + '</td></tr>';
              
            })
        }

    } else if (type_id == 'list_add'){

        var blocked_music = document.getElementById('blocked-music').value;

        eel.sr_config_py(type_id,blocked_music);

        blocked_music.value = '';
        
    } else if (type_id == 'list_rem'){

        var blocked_music = document.getElementById('blocked-music').value;

        eel.sr_config_py(type_id,blocked_music);

        blocked_music.value = '';
        
    } 
}

async function not_config_js(event, type_id){
    

    if (type_id == 'get_sub'){    

        var sub_not = document.getElementById('sub-not');
        var sub_image_over = document.getElementById('sub-over-image');
        var sub_image = document.getElementById('sub-image');
        var sub_image_px = document.getElementById('sub-image-px');
        var sub_audio = document.getElementById('sub-audio');
        var sub_audio_volume = document.getElementById('sub-audio-volume');
        var sub_tts = document.getElementById('sub-tts');
        var sub_response = document.getElementById('sub-response');
        var sub_response_chat = document.getElementById('sub-response-chat');
        var sub_response_px = document.getElementById('sub-response-px');

        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);

            sub_not.checked = not_config_data_load.sub_not == 1 ? true : false;
            sub_tts.checked = not_config_data_load.sub_tts == 1 ? true : false;
            sub_image_over.checked = not_config_data_load.sub_image_over == 1 ? true : false;

            sub_image.value = not_config_data_load.sub_image;
            sub_image_px.value = not_config_data_load.sub_image_px;
            sub_audio.value = not_config_data_load.sub_audio;
            sub_audio_volume.value = not_config_data_load.sub_audio_volume;
            sub_response.value = not_config_data_load.sub_response;
            sub_response_chat.value = not_config_data_load.sub_response_chat;
            sub_response_px.value = not_config_data_load.sub_response_px;

        }
        
    } else if (type_id == 'get_resub'){

        var resub_not = document.getElementById('resub-not');
        var resub_image_over = document.getElementById('resub-over-image');
        var resub_image = document.getElementById('resub-image');
        var resub_image_px = document.getElementById('resub-image-px');
        var resub_audio = document.getElementById('resub-audio');
        var resub_audio_volume = document.getElementById('resub-audio-volume');
        var resub_tts = document.getElementById('resub-tts');
        var resub_response = document.getElementById('resub-response');
        var resub_response_chat = document.getElementById('resub-response-chat');
        var resub_response_px = document.getElementById('resub-response-px');

        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);

            resub_tts.checked = not_config_data_load.resub_tts == 1 ? true : false;
            resub_not.checked = not_config_data_load.resub_not == 1 ? true : false;
            resub_image_over.checked = not_config_data_load.resub_image_over == 1 ? true : false;

            resub_image.value = not_config_data_load.resub_image;
            resub_image_px.value = not_config_data_load.resub_image_px;
            resub_audio.value = not_config_data_load.resub_audio;
            resub_audio_volume.value = not_config_data_load.resub_audio_volume;
            resub_response.value = not_config_data_load.resub_response;
            resub_response_chat.value = not_config_data_load.resub_response_chat;
            resub_response_px.value = not_config_data_load.resub_response_px;

        }

    } else if (type_id == 'get_giftsub'){

        var giftsub_not = document.getElementById('giftsub-not'); 
        var giftsub_image_over = document.getElementById('giftsub-over-image');
        var giftsub_image = document.getElementById('giftsub-image');
        var giftsub_image_px = document.getElementById('giftsub-image-px');
        var giftsub_audio = document.getElementById('giftsub-audio');
        var giftsub_audio_volume = document.getElementById('giftsub-audio-volume');
        var giftsub_tts = document.getElementById('giftsub-tts');

        var giftsub_response = document.getElementById('giftsub-response');
        var giftsub_response_chat = document.getElementById('giftsub-response-chat');
        var giftsub_response_px = document.getElementById('giftsub-response-px');
    
        var mysterygift_response = document.getElementById('mysterygift-response');
        var mysterygift_response_chat = document.getElementById('mysterygift-response-chat');
        var mysterygift_response_px = document.getElementById('mysterygift-response-px');
        
        var re_mysterygift_response = document.getElementById('re-mysterygift-response');
        var re_mysterygift_response_chat = document.getElementById('re-mysterygift-response-chat');
        var re_mysterygift_response_px = document.getElementById('re-mysterygift-response-px');


        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);

            
            giftsub_tts.checked = not_config_data_load.giftsub_tts == 1 ? true : false;
            giftsub_not.checked = not_config_data_load.giftsub_not == 1 ? true : false;
            giftsub_image_over.checked = not_config_data_load.giftsub_image_over == 1 ? true : false;

            giftsub_image.value = not_config_data_load.giftsub_image;
            giftsub_image_px.value = not_config_data_load.giftsub_image_px;
            giftsub_audio.value = not_config_data_load.giftsub_audio;
            giftsub_audio_volume.value = not_config_data_load.giftsub_audio_volume;

            giftsub_response.value = not_config_data_load.giftsub_response;
            giftsub_response_chat.value = not_config_data_load.giftsub_response_chat;
            giftsub_response_px.value = not_config_data_load.giftsub_response_px;

            mysterygift_response.value = not_config_data_load.mysterygift_response;
            mysterygift_response_chat.value = not_config_data_load.mysterygift_response_chat;
            mysterygift_response_px.value = not_config_data_load.mysterygift_response_px;

            re_mysterygift_response.value = not_config_data_load.re_mysterygift_response;
            re_mysterygift_response_chat.value = not_config_data_load.re_mysterygift_response_chat;
            re_mysterygift_response_px.value = not_config_data_load.re_mysterygift_response_px;
        }


    } else if (type_id == 'get_raid'){

        var raid_not = document.getElementById('raid-not');
        var raid_image_over = document.getElementById('raid-over-image');
        var raid_image = document.getElementById('raid-image');
        var raid_image_px = document.getElementById('raid-image-px');
        var raid_audio = document.getElementById('raid-audio');
        var raid_audio_volume = document.getElementById('raid-audio-volume');
        var raid_tts = document.getElementById('raid-tts');
    
        var raid_response = document.getElementById('raid-response');
        var raid_response_px = document.getElementById('raid-response-px');

        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);

            raid_tts.checked = not_config_data_load.raid_tts == 1 ? true : false;
            raid_not.checked = not_config_data_load.raid_not == 1 ? true : false;
            raid_image_over.checked = not_config_data_load.raid_image_over == 1 ? true : false;
            
            raid_image.value = not_config_data_load.raid_image;
            raid_image_px.value = not_config_data_load.raid_image_px;
            raid_audio.value = not_config_data_load.raid_audio;
            raid_audio_volume.value = not_config_data_load.raid_audio_volume;
            raid_response.value = not_config_data_load.raid_response;
            raid_response_px.value = not_config_data_load.raid_response_px;

        }

    } else if (type_id == 'get_follow'){

        var follow_not = document.getElementById('follow-not');
        var follow_image_over = document.getElementById('follow-over-image');
        var follow_image = document.getElementById('follow-image');
        var follow_image_px = document.getElementById('follow-image-px');
        var follow_audio = document.getElementById('follow-audio');
        var follow_audio_volume = document.getElementById('follow-audio-volume');
        var follow_tts = document.getElementById('follow-tts');
    
        var follow_response = document.getElementById('follow-response');
        var follow_response_chat = document.getElementById('follow-response-chat');
        var follow_response_px = document.getElementById('follow-response-px');

        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);
            
            follow_not.checked = not_config_data_load.follow_not == 1 ? true : false;
            follow_tts.checked = not_config_data_load.follow_tts == 1 ? true : false;
            follow_image_over.checked = not_config_data_load.follow_image_over == 1 ? true : false;

            follow_image.value = not_config_data_load.follow_image;
            follow_image_px.value = not_config_data_load.follow_image_px;
            follow_audio.value = not_config_data_load.follow_audio;
            follow_audio_volume.value = not_config_data_load.rfollow_audio_volume;
            follow_response.value = not_config_data_load.follow_response;
            follow_response_chat.value = not_config_data_load.follow_response_chat;
            follow_response_px.value = not_config_data_load.follow_response_px;

        }

    } else if (type_id == 'get_bits1'){
        
        var bits1_not = document.getElementById('bits1-not');
        var bits1_image_over = document.getElementById('bits1-over-image');
        var bits1_image = document.getElementById('bits1-image');
        var bits1_image_px = document.getElementById('bits1-image-px');
        var bits1_audio = document.getElementById('bits1-audio');
        var bits1_audio_volume = document.getElementById('bits1-audio-volume');
        var bits1_tts = document.getElementById('bits1-tts');
        var bits1_response = document.getElementById('bits1-response');
        var bits1_response_chat = document.getElementById('bits1-response-chat');
        var bits1_response_px = document.getElementById('bits1-response-px');

        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);

            bits1_not.checked = not_config_data_load.bits1_not == 1 ? true : false;
            bits1_tts.checked = not_config_data_load.bits1_tts == 1 ? true : false;
            bits1_image_over.checked = not_config_data_load.bits1_image_over == 1 ? true : false;

            bits1_image.value = not_config_data_load.bits1_image;
            bits1_image_px.value = not_config_data_load.bits1_image_px;
            bits1_audio.value = not_config_data_load.bits1_audio;
            bits1_audio_volume.value = not_config_data_load.bits1_audio_volume;
            bits1_response.value = not_config_data_load.bits1_response;
            bits1_response_chat.value = not_config_data_load.bits1_response_chat;
            bits1_response_px.value = not_config_data_load.bits1_response_px;

        }
    } else if (type_id == 'get_bits100'){

        var bits100_not = document.getElementById('bits100-not');
        var bits100_image_over = document.getElementById('bits100-over-image');
        var bits100_image = document.getElementById('bits100-image');
        var bits100_image_px = document.getElementById('bits100-image-px');
        var bits100_audio = document.getElementById('bits100-audio');
        var bits100_audio_volume = document.getElementById('bits100-audio-volume');
        var bits100_tts = document.getElementById('bits100-tts');
        var bits100_response = document.getElementById('bits100-response');
        var bits100_response_chat = document.getElementById('bits100-response-chat');
        var bits100_response_px = document.getElementById('bits100-response-px');
        
        var not_config_data = await eel.not_config_py('data',type_id)();
        
        if (not_config_data){
        
            var not_config_data_load = JSON.parse(not_config_data);
        
            bits100_not.checked = not_config_data_load.bits100_not == 1 ? true : false;
            bits100_tts.checked = not_config_data_load.bits100_tts == 1 ? true : false;
            bits100_image_over.checked = not_config_data_load.bits100_image_over == 1 ? true : false;
        
            bits100_image.value = not_config_data_load.bits100_image;
            bits100_image_px.value = not_config_data_load.bits100_image_px;
            bits100_audio.value = not_config_data_load.bits100_audio;
            bits100_audio_volume.value = not_config_data_load.bits100_audio_volume;
            bits100_response.value = not_config_data_load.bits100_response;
            bits100_response_chat.value = not_config_data_load.bits100_response_chat;
            bits100_response_px.value = not_config_data_load.bits100_response_px;
        
        }

    } else if (type_id == 'get_bits1000'){

        var bits1000_not = document.getElementById('bits1000-not');
        var bits1000_image_over = document.getElementById('bits1000-over-image');
        var bits1000_image = document.getElementById('bits1000-image');
        var bits1000_image_px = document.getElementById('bits1000-image-px');
        var bits1000_audio = document.getElementById('bits1000-audio');
        var bits1000_audio_volume = document.getElementById('bits1000-audio-volume');
        var bits1000_tts = document.getElementById('bits1000-tts');
        var bits1000_response = document.getElementById('bits1000-response');
        var bits1000_response_chat = document.getElementById('bits1000-response-chat');
        var bits1000_response_px = document.getElementById('bits1000-response-px');

        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);

            bits1000_not.checked = not_config_data_load.bits1000_not == 1 ? true : false;
            bits1000_tts.checked = not_config_data_load.bits1000_tts == 1 ? true : false;
            bits1000_image_over.checked = not_config_data_load.bits1000_image_over == 1 ? true : false;

            bits1000_image.value = not_config_data_load.bits1000_image;
            bits1000_image_px.value = not_config_data_load.bits1000_image_px;
            bits1000_audio.value = not_config_data_load.bits1000_audio;
            bits1000_audio_volume.value = not_config_data_load.bits1000_audio_volume;
            bits1000_response.value = not_config_data_load.bits1000_response;
            bits1000_response_chat.value = not_config_data_load.bits1000_response_chat;
            bits1000_response_px.value = not_config_data_load.bits1000_response_px;

        }

    } else if (type_id == 'get_bits5000'){

        var bits5000_not = document.getElementById('bits5000-not');
        var bits5000_image_over = document.getElementById('bits5000-over-image');
        var bits5000_image = document.getElementById('bits5000-image');
        var bits5000_image_px = document.getElementById('bits5000-image-px');
        var bits5000_audio = document.getElementById('bits5000-audio');
        var bits5000_audio_volume = document.getElementById('bits5000-audio-volume');
        var bits5000_tts = document.getElementById('bits5000-tts');
        var bits5000_response = document.getElementById('bits5000-response');
        var bits5000_response_chat = document.getElementById('bits5000-response-chat');
        var bits5000_response_px = document.getElementById('bits5000-response-px');

        var not_config_data = await eel.not_config_py('data',type_id)();

        if (not_config_data){

            var not_config_data_load = JSON.parse(not_config_data);

            bits5000_not.checked = not_config_data_load.bits5000_not == 1 ? true : false;
            bits5000_tts.checked = not_config_data_load.bits5000_tts == 1 ? true : false;
            bits5000_image_over.checked = not_config_data_load.bits5000_image_over == 1 ? true : false;

            bits5000_image.value = not_config_data_load.bits5000_image;
            bits5000_image_px.value = not_config_data_load.bits5000_image_px;
            bits5000_audio.value = not_config_data_load.bits5000_audio;
            bits5000_audio_volume.value = not_config_data_load.bits5000_audio_volume;
            bits5000_response.value = not_config_data_load.bits5000_response;
            bits5000_response_chat.value = not_config_data_load.bits5000_response_chat;
            bits5000_response_px.value = not_config_data_load.bits5000_response_px;

        }

    } else if (type_id == 'save_sub'){

        var sub_not = document.getElementById('sub-not');
        var sub_image_over = document.getElementById('sub-over-image');
        var sub_image = document.getElementById('sub-image');
        var sub_image_px = document.getElementById('sub-image-px');
        var sub_audio = document.getElementById('sub-audio');
        var sub_audio_volume = document.getElementById('sub-audio-volume');
        var sub_tts = document.getElementById('sub-tts');
        var sub_response = document.getElementById('sub-response');
        var sub_response_chat = document.getElementById('sub-response-chat');
        var sub_response_px = document.getElementById('sub-response-px');

        sub_not_save = sub_not.checked ? 1 : 0;
        sub_tts_save = sub_tts.checked ? 1 : 0;
        sub_image_over = sub_image_over.checked ? 1 : 0;

        data = {
            sub_not: sub_not_save,
            sub_image_over: sub_image_over,
            sub_image: sub_image.value,
            sub_image_px: sub_image_px.value,
            sub_audio: sub_audio.value,
            sub_audio_volume: sub_audio_volume.value,
            sub_tts: sub_tts_save,
            sub_response: sub_response.value,
            sub_response_chat: sub_response_chat.value,
            sub_response_px: sub_response_px.value,
        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);

    } else if (type_id == 'save_resub'){
        
        var resub_not = document.getElementById('resub-not');
        var resub_image_over = document.getElementById('resub-over-image');
        var resub_image = document.getElementById('resub-image');
        var resub_image_px = document.getElementById('resub-image-px');
        var resub_audio = document.getElementById('resub-audio');
        var resub_audio_volume = document.getElementById('resub-audio-volume');
        var resub_tts = document.getElementById('resub-tts');
        var resub_response = document.getElementById('resub-response');
        var resub_response_chat = document.getElementById('resub-response-chat');
        var resub_response_px = document.getElementById('resub-response-px');

        resub_not_save = resub_not.checked ? 1 : 0;
        resub_tts_save = resub_tts.checked ? 1 : 0;
        resub_image_over = resub_image_over.checked ? 1 : 0;

        data = {
            resub_not: resub_not_save,
            resub_image_over: resub_image_over,
            resub_image: resub_image.value,
            resub_image_px: resub_image_px.value,
            resub_audio: resub_audio.value,
            resub_audio_volume: resub_audio_volume.value,
            resub_tts: resub_tts_save,
            resub_response: resub_response.value,
            resub_response_chat: resub_response_chat.value,
            resub_response_px: resub_response_px.value,
        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);

    } else if (type_id == 'save_giftsub'){

        var giftsub_not = document.getElementById('giftsub-not'); 
        var giftsub_image_over = document.getElementById('giftsub-over-image');
        var giftsub_image = document.getElementById('giftsub-image');
        var giftsub_image_px = document.getElementById('giftsub-image-px');
        var giftsub_audio = document.getElementById('giftsub-audio');
        var giftsub_audio_volume = document.getElementById('giftsub-audio-volume');
        var giftsub_tts = document.getElementById('giftsub-tts');

        var giftsub_response = document.getElementById('giftsub-response');
        var giftsub_response_chat = document.getElementById('giftsub-response-chat');
        var giftsub_response_px = document.getElementById('giftsub-response-px');
    
        var mysterygift_response = document.getElementById('mysterygift-response');
        var mysterygift_response_chat = document.getElementById('mysterygift-response-chat');
        var mysterygift_response_px = document.getElementById('mysterygift-response-px');
        
        var re_mysterygift_response = document.getElementById('re-mysterygift-response');
        var re_mysterygift_response_chat = document.getElementById('re-mysterygift-response-chat');
        var re_mysterygift_response_px = document.getElementById('re-mysterygift-response-px');

        giftsub_not_save = giftsub_not.checked ? 1 : 0;
        giftsub_tts_save = giftsub_tts.checked ? 1 : 0;
        giftsub_image_over = giftsub_image_over.checked ? 1 : 0;

        data = {
            giftsub_not: giftsub_not_save,
            giftsub_image_over: giftsub_image_over,
            giftsub_image: giftsub_image.value,
            giftsub_image_px: giftsub_image_px.value,
            giftsub_audio: giftsub_audio.value,
            giftsub_audio_volume: giftsub_audio_volume.value,
            giftsub_tts:giftsub_tts_save,
            giftsub_response: giftsub_response.value,
            giftsub_response_chat: giftsub_response_chat.value,
            giftsub_response_px: giftsub_response.value,    
            mysterygift_response: mysterygift_response.value,
            mysterygift_response_chat: mysterygift_response_chat.value,
            mysterygift_response_px: mysterygift_response_px.value,
            re_mysterygift_response: re_mysterygift_response.value,
            re_mysterygift_response_chat: re_mysterygift_response_chat.value,
            re_mysterygift_response_px: re_mysterygift_response_px.value,
        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);

    } else if (type_id == 'save_raid'){

        var raid_not = document.getElementById('raid-not');
        var raid_image_over = document.getElementById('raid-over-image');
        var raid_image = document.getElementById('raid-image');
        var raid_image_px = document.getElementById('raid-image-px');
        var raid_audio = document.getElementById('raid-audio');
        var raid_audio_volume = document.getElementById('raid-audio-volume');
        var raid_tts = document.getElementById('raid-tts');
    
        var raid_response = document.getElementById('raid-response');
        var raid_response_chat = document.getElementById('raid-response-chat');
        var raid_response_px = document.getElementById('raid-response-px');

        raid_not_save = raid_not.checked ? 1 : 0;
        raid_tts_save = raid_tts.checked ? 1 : 0;
        raid_image_over = raid_image_over.checked ? 1 : 0;

        data = {

            raid_not: raid_not_save,
            raid_image_over: raid_image_over,
            raid_image: raid_image.value,
            raid_image_px: raid_image_px.value,
            raid_audio: raid_audio.value,
            raid_audio_volume: raid_audio_volume.value,
            raid_tts: raid_tts_save,
            raid_response: raid_response.value,
            raid_response_chat: raid_response_chat.value,
            raid_response_px: raid_response_px.value,

        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);


    } else if (type_id == 'save_follow'){

        var follow_not = document.getElementById('follow-not');
        var follow_image_over = document.getElementById('follow-over-image');
        var follow_image = document.getElementById('follow-image');
        var follow_image_px = document.getElementById('follow-image-px');
        var follow_audio = document.getElementById('follow-audio');
        var follow_audio_volume = document.getElementById('follow-audio-volume');
        var follow_tts = document.getElementById('follow-tts');
    
        var follow_response = document.getElementById('follow-response');
        var follow_response_chat = document.getElementById('follow-response-chat');
        var follow_response_px = document.getElementById('follow-response-px');

        follow_not_save = follow_not.checked ? 1 : 0;
        follow_tts_save = follow_tts.checked ? 1 : 0;
        follow_image_over = follow_image_over.checked ? 1 : 0;

        data = {

            follow_not: follow_not_save,
            follow_image_over: follow_image_over,
            follow_image: follow_image.value,
            follow_image_px: follow_image_px.value,
            follow_audio: follow_audio.value,
            follow_audio_volume: follow_audio_volume.value,
            follow_tts:  follow_tts_save,
            follow_response: follow_response.value,
            follow_response_chat: follow_response_chat.value,
            follow_response_px: follow_response_px.value,

        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);


    } else if (type_id == 'save_bits1'){

        var bits1_not = document.getElementById('bits1-not');
        var bits1_image_over = document.getElementById('bits1-over-image');
        var bits1_image = document.getElementById('bits1-image');
        var bits1_image_px = document.getElementById('bits1-image-px');
        var bits1_audio = document.getElementById('bits1-audio');
        var bits1_audio_volume = document.getElementById('bits1-audio-volume');
        var bits1_tts = document.getElementById('bits1-tts');
        var bits1_response = document.getElementById('bits1-response');
        var bits1_response_chat = document.getElementById('bits1-response-chat');
        var bits1_response_px = document.getElementById('bits1-response-px');

        bits1_not_save = bits1_not.checked ? 1 : 0;
        bits1_tts_save = bits1_tts.checked ? 1 : 0;
        bits1_image_over = bits1_image_over.checked ? 1 : 0;

        data = {
            bits1_not: bits1_not_save,
            bits1_image_over: bits1_image_over,
            bits1_image: bits1_image.value,
            bits1_image_px: bits1_image_px.value,
            bits1_audio: bits1_audio.value,
            bits1_audio_volume: bits1_audio_volume.value,
            bits1_tts: bits1_tts_save,
            bits1_response: bits1_response.value,
            bits1_response_chat: bits1_response_chat.value,
            bits1_response_px: bits1_response_px.value,
        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);

    } else if (type_id == 'save_bits100'){

        var bits100_not = document.getElementById('bits100-not');
        var bits100_image_over = document.getElementById('bits100-over-image');
        var bits100_image = document.getElementById('bits100-image');
        var bits100_image_px = document.getElementById('bits100-image-px');
        var bits100_audio = document.getElementById('bits100-audio');
        var bits100_audio_volume = document.getElementById('bits100-audio-volume');
        var bits100_tts = document.getElementById('bits100-tts');
        var bits100_response = document.getElementById('bits100-response');
        var bits100_response_chat = document.getElementById('bits100-response-chat');
        var bits100_response_px = document.getElementById('bits100-response-px');

        bits100_not_save = bits100_not.checked ? 1 : 0;
        bits100_tts_save = bits100_tts.checked ? 1 : 0;
        bits100_image_px = bits100_image_px.checked ? 1 : 0;

        data = {
            bits100_not: bits100_not_save,
            bits100_image_over: bits100_image_over.value,
            bits100_image: bits100_image.value,
            bits100_image_px: bits100_image_px,
            bits100_audio: bits100_audio.value,
            bits100_audio_volume: bits100_audio_volume.value,
            bits100_tts: bits100_tts_save,
            bits100_response: bits100_response.value,
            bits100_response_chat: bits100_response_chat.value,
            bits100_response_px: bits100_response_px.value,
        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);

    } else if (type_id == 'save_bits1000'){

        var bits1000_not = document.getElementById('bits1000-not');
        var bits1000_image_over = document.getElementById('bits1000-over-image');
        var bits1000_image = document.getElementById('bits1000-image');
        var bits1000_image_px = document.getElementById('bits1000-image-px');
        var bits1000_audio = document.getElementById('bits1000-audio');
        var bits1000_audio_volume = document.getElementById('bits1000-audio-volume');
        var bits1000_tts = document.getElementById('bits1000-tts');
        var bits1000_response = document.getElementById('bits1000-response');
        var bits1000_response_chat = document.getElementById('bits1000-response-chat');
        var bits1000_response_px = document.getElementById('bits1000-response-px');

        bits1000_not_save = bits1000_not.checked ? 1 : 0;
        bits1000_tts_save = bits1000_tts.checked ? 1 : 0;
        bits1000_image_over = bits1000_image_over.checked ? 1 : 0;

        data = {
            bits1000_not: bits1000_not_save,
            bits1000_image_over: bits1000_image_over,
            bits1000_image: bits1000_image.value,
            bits1000_image_px: bits1000_image_px.value,
            bits1000_audio: bits1000_audio.value,
            bits1000_audio_volume: bits1000_audio_volume.value,
            bits1000_tts: bits1000_tts_save,
            bits1000_response: bits1000_response.value,
            bits1000_response_chat: bits1000_response_chat.value,
            bits1000_response_px: bits1000_response_px.value,
        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);

    } else if (type_id == 'save_bits5000'){

        var bits5000_not = document.getElementById('bits5000-not');
        var bits5000_image_over = document.getElementById('bits5000-over-image');
        var bits5000_image = document.getElementById('bits5000-image');
        var bits5000_image_px = document.getElementById('bits5000-image-px');
        var bits5000_audio = document.getElementById('bits5000-audio');
        var bits5000_audio_volume = document.getElementById('bits5000-audio-volume');
        var bits5000_tts = document.getElementById('bits5000-tts');
        var bits5000_response = document.getElementById('bits5000-response');
        var bits5000_response_chat = document.getElementById('bits5000-response-chat');
        var bits5000_response_px = document.getElementById('bits5000-response-px');

        bits5000_not_save = bits5000_not.checked ? 1 : 0;
        bits5000_tts_save = bits5000_tts.checked ? 1 : 0;
        bits5000_image_over = bits5000_image_over.checked ? 1 : 0;

        data = {
            bits5000_not: bits5000_not_save,
            bits5000_image_over: bits5000_image_over,
            bits5000_image: bits5000_image.value,
            bits5000_image_px: bits5000_image_px.value,
            bits5000_audio: bits5000_audio.value,
            bits5000_audio_volume: bits5000_audio_volume.value,
            bits5000_tts: bits5000_tts_save,
            bits5000_response: bits5000_response.value,
            bits5000_response_chat: bits5000_response_chat.value,
            bits5000_response_px: bits5000_response_px.value,
        }

        var formData = JSON.stringify(data);
        eel.not_config_py(formData,type_id);

    } else if (type_id == 'select_edit'){

        const notDivs = {
            sub: document.getElementById('sub-not-div'),
            resub: document.getElementById('resub-not-div'),
            giftsub: document.getElementById('giftsub-not-div'),
            raid: document.getElementById('raid-not-div'),
            follow: document.getElementById('follow-not-div'),
            bits1: document.getElementById('bits1-not-div'),
            bits100: document.getElementById('bits100-not-div'),
            bits1000: document.getElementById('bits1000-not-div'),
            bits5000: document.getElementById('bits5000-not-div'),
          };
          
          const selectEdit = document.getElementById('not-select-edit');
          
          for (const [key, value] of Object.entries(notDivs)) {
            value.hidden = key !== selectEdit.value;
            not_config_js(event, `get_${key}`);
          }
    }
}

async function userdata_js(type_id,data){

    if (type_id == "get"){

        var userdata = ""
        var userdata = await eel.userdata_py('get','None')()
        
        if (userdata){

            if ($.fn.DataTable.isDataTable("#userdata_table")) {
                console.log('destroy')
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

            userdata_parse = ""
            var userdata_parse = JSON.parse(userdata);

            
            for (var key in userdata_parse) {
                
                    var removeBtn = document.createElement("button");
                    removeBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
                    removeBtn.setAttribute("type", "button");
                    removeBtn.setAttribute("title", "Remover usuário");
                    removeBtn.setAttribute("data-toggle", "tooltip");
                    removeBtn.setAttribute("data-bs-placement", "top");
                    removeBtn.setAttribute("onclick", "eel.userdata_py('remove','" + userdata_parse[key].display_name + "')");

                    var removeIcon = document.createElement("i");
                    removeIcon.classList.add("fa-solid", "fa-user-xmark");

                    removeBtn.appendChild(removeIcon);

                    var addBtn = document.createElement("button");
                    addBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
                    addBtn.setAttribute("type", "button");
                    addBtn.setAttribute("title", "Adicionar na lista de bots e remover desta tabela");
                    addBtn.setAttribute("data-toggle", "tooltip");
                    addBtn.setAttribute("data-bs-placement", "top");
                    addBtn.setAttribute("onclick", "eel.userdata_py('list_add','" + userdata_parse[key].display_name + "')");

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
                $(this).html('<input type="text" class="form-control bg-dark" placeholder="Procure em' + title + '" />');
            });

            $('[data-toggle="tooltip"]').tooltip();



        }

    
    } else if (type_id == 'remove'){
        eel.userdata_py(type_id,data)
    } else if (type_config == 'list_add'){
        eel.chat_config(data,type_config);
    }
}


function show_userdata_modal(){
    $("#userdata-modal").modal("show");
    userdata_js('get')
}

async function get_stream_info(){

    var select_games = "stream-game";
    var select_tags = "stream-tags";
    var button_submt = document.getElementById('submit-stream-info');
    var title_inp = document.getElementById("stream-title");

    button_submt.disabled = true
    var stream_games_list = await eel.get_stream_info_py()()
    
    if (stream_games_list){

        var stream_games_parse = JSON.parse(stream_games_list);

        streamer_game = stream_games_parse.game;
        streamer_game_id = stream_games_parse.game_id;
        games = stream_games_parse.game_list;
        tags = stream_games_parse.tag_list;
        streamer_tags = stream_games_parse.tag;
        title_inp.value = stream_games_parse.title;

        $("#" + select_games).empty();
        $("#" + select_games).selectpicker("refresh");

        $("#" + select_tags).empty();
        $("#" + select_tags).selectpicker("refresh");

        for (var id in streamer_tags){
            
            tag = streamer_tags[id]

            var span_tags = document.createElement("p")
            span_tags.innerHTML = tag.toLowerCase();
            span_tags.id = tag.toLowerCase();
            document.getElementById("tags").appendChild(span_tags);
        }
        
        for (var id in games) {

            var game_new = games[id];
            $("#" + select_games).append('<option class="bg-dark" style="color: #fff;" data-img="'+ game_new.box_art_url +'" value="'+ id +'">'+ game_new.name +'</option>');

        }

        for (var name in tags) {

            var tags_new = tags[name];
            $("#" + select_tags).append('<option class="bg-dark" style="color: #fff;" data-desc="'+ tags_new.description +'" data-id="'+ tags_new.id +'" value="'+ name +'">'+ name +'</option>');

        }

        $("#" + select_games).selectpicker("refresh");
        
        $("#" + select_tags).selectpicker("refresh");

        $("#" + select_games).selectpicker('val', streamer_game_id); 

        
        var game_box_img = games[streamer_game_id].box_art_url;

        const width = 285;
        const height = 380;
        const newUrl = game_box_img.replace(/\{width\}x\{height\}/, `${width}x${height}`);


        var img_tag = document.getElementById("game_img");
        img_tag.src = newUrl

        button_submt.disabled = false

    }
}

jQuery($ => { // DOM ready and $ alias in scope.

    $("#stream-game").on({
        
        change() {
            
            var selec_game = document.getElementById("stream-game").value;
            var game_box_img = games[selec_game].box_art_url;

            const width = 285;
            const height = 380;
            const newUrl = game_box_img.replace(/\{width\}x\{height\}/, `${width}x${height}`);


            var img_tag = document.getElementById("game_img");
            img_tag.src = newUrl
        }
    });
    // TAGS BOX
    $("#stream-tags").on({

        change() {

          var div_tags = document.getElementById("tags");
          var spans = div_tags.querySelectorAll('p');
          var txt = $(this).val();
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
                span_tags.id = txt.toLowerCase();
                document.getElementById("tags").appendChild(span_tags);
            }
          }
        }
    });

    $("#tags").on("click", "p", function() {
      $(this).remove(); 
    });
    
  });

function save_stream_info(){

    var stream_title = document.getElementById("stream-title").value;
    var stream_game = document.getElementById("stream-game").value;
    
    var seletor_not_discord = document.getElementById('enable-discord-not-stream');
    var seletor_not_discord_off  = document.getElementById('enable-discord-not-stream-off');

    seletor_not_discord_off = seletor_not_discord_off.checked ? 1 : 0;
    seletor_not_discord = seletor_not_discord.checked ? 1 : 0;
    
    var div_tags = document.getElementById("tags");
    var tags_get = div_tags.querySelectorAll('p');
    var tags_list = []

    for (var i = 0; i < tags_get.length; i++) { // percorre todos os elementos span
        tags_list.push(tags_get[i].textContent)
    }

    data = {
        title : stream_title,
        game : stream_game,
        tags : tags_list,
        discord : seletor_not_discord,
        offline : seletor_not_discord_off
    }

    var formData = JSON.stringify(data);
    eel.save_stream_info_py(formData);

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
        get_poll = await eel.poll_py(formData)();
    
        if (get_poll){
            
            var get_poll_parse = JSON.parse(get_poll);
    
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
        get_poll = await eel.poll_py(formData)();

        if (get_poll){
            
            var get_poll_parse = JSON.parse(get_poll);
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
        eel.poll_py(formData);
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
    
    while (true){

        data = {
            type_id : 'get',
        }

        var formData = JSON.stringify(data);
        var pred_info = await eel.prediction_py(formData)()

        if (pred_info){

            var pred_info_parse = JSON.parse(pred_info);

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

        await sleep(1000)
    }
}


async function poll_small() {
    
    while (true){

        data = {
            type_id : 'get',
        }

        var formData = JSON.stringify(data);
        var poll_info = await eel.poll_py(formData)()

        if (poll_info){

            var poll_info_parse = JSON.parse(poll_info);

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

eel.expose(prediction);
async function prediction(type_id) {

    console.log(type_id)

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
        eel.prediction_py(formData);

    } else if (type_id == 'get'){

        var data = {
            type_id : 'get'
        }

        var formData = JSON.stringify(data);
        var pred_info = await eel.prediction_py(formData)()
    
        if (pred_info){
    
            var pred_info_parse = JSON.parse(pred_info);

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
        var pred_info = await eel.prediction_py(formData)()

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
        eel.prediction_py(formData)

        

    }
}

eel.expose(goal);
async function goal() {

    while (true){

        data_goal = await eel.goal_py()()

        var data_goal_parse = JSON.parse(data_goal);

        var goal_status = document.getElementById('status-goal-small')
        var goal_status_bar = document.getElementById('progress-goal-small-int')

        var goal_name = ""

        if (data_goal_parse.type == "subscription") {
            goal_name = "Meta de inscrições"
        } else if (data_goal_parse.type == "follow") {
            goal_name = "Meta de seguidores"
        }
    
        goal_status.innerHTML = `${goal_name} : ${data_goal_parse.current_amount}/${data_goal_parse.target_amount}`
        
        var value = (data_goal_parse.current_amount / data_goal_parse.target_amount) * 100;
        goal_status_bar.value = value;
        goal_status_bar.style.width = `${(value)}%`;

        await sleep(10000)

    }
}
