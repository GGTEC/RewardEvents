function send_auth_info(event, fomrid) {

    event.preventDefault();

    div_user_auth = document.getElementById("div-user-auth");
    input_streamer_username = document.getElementById("streamer-name");
    streamer_token = document.getElementById("streamer-token");
    div_user_token = document.getElementById("div-user-token");

    div_bot_auth = document.getElementById("div-bot-auth");
    input_bot_username = document.getElementById("bot-name");

    bot_token = document.getElementById("bot-token");
    div_bot_token = document.getElementById("div-bot-token");

    selector_streamer_asbot = document.getElementById("streamer_as_bot");
    
    input_streamer_bot_username = document.getElementById("streamer-bot-token");
    div_streamer_bot_token = document.getElementById("div-user-bot-token");

    sucess_div = document.getElementById("div-auth-sucess");

    if (fomrid == 'submit-auth-user') {

        var user_name = input_streamer_username.value;

        if (selector_streamer_asbot.checked == true) {

            div_user_auth.hidden = true;
            div_streamer_bot_token.hidden = false;

            window.pywebview.api.start_auth_window(user_name, 'streamer_asbot');

        } else {

            div_user_auth.hidden = true;
            div_user_token.hidden = false;
            window.pywebview.api.start_auth_window(user_name, 'streamer');
        }

    } else if (fomrid == 'submit-user-token') {

        var token = streamer_token.value;
        
        window.pywebview.api.save_access_token('streamer',token)

        div_user_token.hidden = true;
        div_bot_auth.hidden = false;

    } else if (fomrid == 'submit-user-bot-token') {

        var token = input_streamer_bot_username.value;
        window.pywebview.api.save_access_token('streamer_asbot',token)

        div_streamer_bot_token.hidden = true;
        sucess_div.hidden = false;

    }  else if (fomrid == 'submit-auth-bot') {

        var user_name = input_bot_username.value;

        window.pywebview.api.start_auth_window(user_name, 'bot');

        div_bot_auth.hidden = true;
        div_bot_token.hidden = false;

    } else if (fomrid == 'submit-bot-token') {

        var token = bot_token.value;
        window.pywebview.api.save_access_token('bot',token)

        div_bot_token.hidden = true;
        sucess_div.hidden = false;

    } else if (fomrid == 'next') {

        document.getElementById("div-auth-terms").hidden = true;
        document.getElementById("div-user-auth").hidden = false;

    } else if (fomrid == 'next-terms'){

        document.getElementById("div-auth-start").hidden = true;
        document.getElementById("div-auth-terms").hidden = false;
    }

}