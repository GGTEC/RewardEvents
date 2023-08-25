async function discord_js(event,type_id) {

    if (type_id == 'save'){
    

        var input_type_edit = document.getElementById('type_edit');

        var webhook_url = document.getElementById('url-webhook');
        var webhook_content  = document.getElementById('embed-content');
        var webhook_title = document.getElementById('embed-title');
        var webhook_color = document.getElementById('embed-color');
        var webhook_description = document.getElementById('embed-description');
        var webhook_status = document.getElementById('webhook-status');

        var not = document.getElementById(`not`);
        var response_chat = document.getElementById(`response-chat`);


        enable_status = webhook_status ? 1 : 0;
        not = not.checked ? 1 : 0,
    
        data_discord_save = {
            
            webhook_url: webhook_url.value,
            embed_color: webhook_color.value,
            embed_content : webhook_content.value,
            embed_title: webhook_title.value,
            embed_description: webhook_description.value,
            webhook_status: enable_status,
            response_chat: response_chat.value,
            not: not
        }
    
        var formData_discord = JSON.stringify(data_discord_save);
    
        window.pywebview.api.discord_config(formData_discord, 'save', input_type_edit.value);

    } else if (type_id == 'save-profile'){
    
        var webhook_profile_status = document.getElementById('profile-webhook-status');
        var webhook_profile_image_url = document.getElementById('url-profile-image-webhook');
        var webhook_profile_name  = document.getElementById('profile-name-webhook');

        webhook_profile_status.checked = webhook_profile_status ? 1 : 0;
    
        data_discord_save = {
            
            webhook_profile_status: webhook_profile_status,
            webhook_profile_image_url: webhook_profile_image_url.value,
            webhook_profile_name : webhook_profile_name.value
        }
    
        var formData_discord = JSON.stringify(data_discord_save);
    
        window.pywebview.api.discord_config(formData_discord, 'save-profile', 'none');

    } else if (type_id == 'get-profile'){
    
        var webhook_profile_status = document.getElementById('profile-webhook-status');
        var webhook_profile_image_url = document.getElementById('url-profile-image-webhook');
        var webhook_profile_name  = document.getElementById('profile-name-webhook');
        
        var data_discord_parse = await window.pywebview.api.discord_config('none', 'get-profile','none');

        if (data_discord_parse) {

            data_discord_parse = JSON.parse(data_discord_parse)

            webhook_profile_status.checked  = data_discord_parse.webhook_profile_status == 1 ? true : false;
            webhook_profile_image_url.value =  data_discord_parse.webhook_profile_image_url;
            webhook_profile_name.value = data_discord_parse.webhook_profile_name;

        }

    } else if (type_id == 'select_edit'){

        var select = document.getElementById('select_edit_not');
        var event_not_divs = document.getElementById('event_not_divs');
        var response_aliases = document.getElementById('aliases-event');
        var input_type_edit = document.getElementById('type_edit');

        var not = document.getElementById(`not`);
        var response_chat = document.getElementById(`response-chat`);

        var chat_alert_form = document.getElementById('chat-alert-form')

        var ignore_list = [
            'clips_create',
            'clips_edit',
        ]

        input_type_edit.value = select.value

        var webhook_url= document.getElementById('url-webhook');
        var webhook_title = document.getElementById('embed-title');
        var webhook_content  = document.getElementById('embed-content');
        var webhook_color = document.getElementById('embed-color');
        var webhook_description = document.getElementById('embed-description');
        var webhook_status = document.getElementById('webhook-status');
        

        var data_discord_parse = await window.pywebview.api.discord_config('none', 'get',select.value);

        if (data_discord_parse) {
            
            event_not_divs.hidden = false

            data_discord_parse = JSON.parse(data_discord_parse)

            webhook_url.value = data_discord_parse.url_webhook;
            webhook_color.value = data_discord_parse.embed_color;
            webhook_content.value = data_discord_parse.embed_content;
            webhook_description.value = data_discord_parse.embed_description;
            webhook_title.value = data_discord_parse.embed_title;
            webhook_status.checked = data_discord_parse.status ? true : false;

            if(ignore_list.includes(select.value)){
                chat_alert_form.hidden = true
            } else {
                chat_alert_form.hidden = false
                not.checked = data_discord_parse.not == 1 ? true : false;
                response_chat.value = data_discord_parse.response_chat;
            }

        }

        const responses_aliases = {
            live_start: '{url}',
            live_cat : '',
            live_end : '',
            follow: '{username}',
            ban : '{reason}, {moderator}, {username}, {time}',
            unban : '{moderator},{username}',
            sub: '{username}, {type}, {plan}, {months}, {cumulative}',
            resub: ' {username}, {tier}, {total_months}, {streak_months}, {months}, {user_message}',
            subend: '{username}',
            giftsub: ' {username}, {months}, {rec_username}, {plan}',
            mysterygift: '{username}, {count}, {plan}',
            're-mysterygift': ' {username}',
            raid: ' {username}, {specs}',
            bits: ' {username}, {amount}',
            shoutout_start: '{broadcaster_user_name}, {moderator_user_name}, {to_broadcaster_user_name}, {viewer_count}',
            shoutout_receive: '{broadcaster_user_name} ,{to_broadcaster_user_name}',
            poll_start: '{title}, {choices}, {current_id}, {bits_voting_status}, {bits_voting_amount}, {channel_points_voting_status}, {channel_points_voting_amount}, {start_at}, {ends_at}',
            poll_status: '{title}, {choices}, {bits_voting_status}, {bits_voting_amount}, {channel_points_voting_status}, {channel_points_voting_amount}',
            poll_end: '{title}, {choices}, {current_id}, {poll_status}, {bits_voting_status}, {bits_voting_amount}, {channel_points_voting_status}, {channel_points_voting_amount}',
            prediction_start: '{title}',
            prediction_progress: '{title}',
            prediction_end: '{title}',
            goal_start: '{target}, {current}, {description}, {type}',
            goal_progress: '{target}, {current}, {description}, {type}',
            goal_end: '{target}, {current}, {description}, {type}',
            shield_start: '{broadcaster},{moderator}',
            shield_end: '{broadcaster},{moderator}',
            charity_campaign_donate: '{username}, {charity_name}, {charity_logo}, {value}, {decimal_places}, {currency}',
            charity_campaign_progress: '{charity_name}, {charity_logo}, {current_amount_value}, {current_amount_currency}, {target_amount_value}, {target_amount_currency}',
            charity_campaign_start: '{charity_name}, {charity_logo}, {current_amount_value}, {current_amount_currency}, {target_amount_value}, {target_amount_currency}',
            charity_campaign_stop: '{charity_name}, {charity_logo}, {current_amount_value}, {current_amount_currency}, {target_amount_value}, {target_amount_currency}'
        };
        
        
        response_aliases.value = responses_aliases[select.value];

    }
}

