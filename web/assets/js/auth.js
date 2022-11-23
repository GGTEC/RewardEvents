function send_auth_info(event, fomrid) {

    event.preventDefault();

    if (fomrid == 'submit-auth-user') {

        var form = document.querySelector("#" + fomrid);
        var user_name = form.querySelector('input[id="streamer-name"]').value;
        var streamer_as_bot = form.querySelector('input[id="streamer_as_bot"]').checked;

        if (streamer_as_bot == true) {

            eel.start_auth_window(user_name, 'streamer_as_bot');

        } else {

            eel.start_auth_window(user_name, 'streamer');

        }

    } else if (fomrid == 'submit-auth-bot') {

        var form = document.querySelector("#" + fomrid);
        var user_name = form.querySelector('input[id="bot-name"]').value;

        eel.start_auth_window(user_name, 'bot');

    } else if (fomrid == 'next') {

        document.getElementById("div-auth-terms").hidden = true;
        document.getElementById("div-user-auth").hidden = false;

    } else if (fomrid == 'next-terms'){

        document.getElementById("div-auth-start").hidden = true;
        document.getElementById("div-auth-terms").hidden = false;
    }

}

eel.expose(auth_user_sucess);
function auth_user_sucess(type_auth) {
    if (type_auth == 'streamer') {
        document.getElementById("div-user-auth").hidden = true;
        document.getElementById("div-bot-auth").hidden = false;
    } else if (type_auth == 'bot') {
        document.getElementById("div-bot-auth").hidden = true;
        document.getElementById("div-auth-sucess").hidden = false;
    } else if (type_auth == 'streamer_as_bot') {
        document.getElementById("div-user-auth").hidden = true;
        document.getElementById("div-auth-sucess").hidden = false;
    }

}