async function discord_js(event,type_id) {

    if (type_id == 'save'){
    

        var input_type_edit = document.getElementById('type_edit_discord');

        var webhook_url = document.getElementById('url-webhook');
        var webhook_content  = document.getElementById('embed-content');
        var webhook_title = document.getElementById('embed-title');
        var webhook_color = document.getElementById('embed-color');
        var webhook_description = document.getElementById('embed-description');
        var webhook_status = document.getElementById('webhook-status');

        enable_status = webhook_status ? 1 : 0;
    
        data_discord_save = {
            
            webhook_url: webhook_url.value,
            embed_color: webhook_color.value,
            embed_content : webhook_content.value,
            embed_title: webhook_title.value,
            embed_description: webhook_description.value,
            webhook_status: enable_status,
        }
    
        var formData_discord = JSON.stringify(data_discord_save);
    
        eel.discord_config(formData_discord, 'save', input_type_edit.value);

    } else if (type_id == 'select_edit'){

        var select = document.getElementById('discord_select_edit');
        var input_type_edit = document.getElementById('type_edit_discord');

        input_type_edit.value = select.value

        var webhook_url= document.getElementById('url-webhook');
        var webhook_title = document.getElementById('embed-title');
        var webhook_content  = document.getElementById('embed-content');
        var webhook_color = document.getElementById('embed-color');
        var webhook_description = document.getElementById('embed-description');
        var webhook_status = document.getElementById('webhook-status');

        var data_discord_receive = await eel.discord_config('none', 'get',select.value)();

    
        if (data_discord_receive) {

            var data_discord_parse = JSON.parse(data_discord_receive);

            webhook_url.value = data_discord_parse.url_webhook;
            webhook_color.value = data_discord_parse.embed_color;
            webhook_content.value = data_discord_parse.embed_content;
            webhook_description.value = data_discord_parse.embed_description;
            webhook_title.value = data_discord_parse.embed_title;
            webhook_status.checked = data_discord_parse.status ? true : false;
        }
    }
}

