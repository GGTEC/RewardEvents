function discord_js(event) {
    event.preventDefault();

    var form_discord = document.querySelector('#discord-config-form');

    var webhook_urlvalue = form_discord.querySelector('input[id="url-webhook-discord"]').value;

    var enable_status = form_discord.querySelector('input[id="webhook-enable"]').checked;
    var enable_status_edit = form_discord.querySelector('input[id="webhook-edit-enable"]').checked;

    if (enable_status == true){
        enable_status = 1
    }

    if (enable_status_edit == true){
        enable_status_edit = 1
    }

    data_discord_save = {

        webhook_url: webhook_urlvalue,
        webhook_url_edit: form_discord.querySelector('input[id="url-webhook-discord-edit"]').value,
        embed_color: form_discord.querySelector('input[id="embed-color"]').value,
        embed_title: form_discord.querySelector('input[id="embed-title"]').value,
        embed_edit_title: form_discord.querySelector('input[id="embed-edit-title"]').value,
        embed_description: form_discord.querySelector('input[id="embed-description"]').value,
        webhook_enable: enable_status,
        webhook_enable_edit: enable_status_edit,

    }

    var formData_discord = JSON.stringify(data_discord_save);

    eel.discord_config(formData_discord, 'save');

}

async function get_discord_config() {

    var webhook_url = document.getElementById('url-webhook-discord');
    var webhook_url_edit = document.getElementById('url-webhook-discord-edit');
    var embed_color = document.getElementById('embed-color');
    var embed_title = document.getElementById('embed-title');
    var embed_edit_title = document.getElementById('embed-edit-title');
    var embed_description = document.getElementById('embed-description');
    var webhook_enable = document.getElementById('webhook-enable');
    var webhook_enable_edit = document.getElementById('webhook-enable-edit');

    var data_discord_receive = await eel.discord_config('none', 'get')();


    if (data_discord_receive) {

        var data_discord_parse = JSON.parse(data_discord_receive);

        webhook_url.value = data_discord_parse.url_webhook;
        webhook_url_edit.value = data_discord_parse.url_webhook_edit;
        embed_color.value = data_discord_parse.embed_color;
        embed_title.value = data_discord_parse.embed_title;
        embed_edit_title.value = data_discord_parse.embed_title_edit;
        embed_description.value = data_discord_parse.embed_description;

        if (data_discord_parse.status == 1) {
            webhook_enable.checked = true;
        }
        if (data_discord_parse.satus_edit == 1) {
            webhook_enable_edit.checked = true;
        }
    }
}

