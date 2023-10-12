function send_auth_info(event, fomrid) {

    event.preventDefault();

    page1 = document.getElementById("page-1");
    page2 = document.getElementById("page-2");
    page3 = document.getElementById("page-3");
    page4 = document.getElementById("page-4");
    page5 = document.getElementById("page-5");
    page6 = document.getElementById("page-6");

    streamer_username = document.getElementById("streamer-name");

    bot_username = document.getElementById("bot-name");

    selector_streamer_asbot = document.getElementById("streamer_as_bot");

    if (fomrid == 'submit-auth-user') {

        var user_name = streamer_username.value;

        if (selector_streamer_asbot.checked == true) {

            page3.hidden = true;
            page5.hidden = false;

            window.pywebview.api.start_auth_window(user_name, 'streamer_asbot');

        } else {

            page3.hidden = true;
            page5.hidden = false;

            window.pywebview.api.start_auth_window(user_name, 'streamer');
        }

    } else if (fomrid == 'submit-auth-bot') {

        var user_name = bot_username.value;

        window.pywebview.api.start_auth_window(user_name, 'bot');

        page4.hidden = true;
        page5.hidden = false;

    }

}


var currentPage = 1;

function changePage() {

    var currentPageElement = document.getElementById('page-' + currentPage);
    if (currentPageElement) {
        currentPageElement.hidden = true;
    }

    currentPage = currentPage % 3 + 1;

    var nextPageElement = document.getElementById('page-' + currentPage);
    if (nextPageElement) {
        nextPageElement.hidden = false;
    }
}

document.getElementById('page-1').hidden = false;

function toggle_auth(type_id){

    page4 = document.getElementById("page-4");
    page5 = document.getElementById("page-5");
    page6 = document.getElementById("page-6");

    if (type_id == 'submit-user-token') {

        page5.hidden = true;
        page4.hidden = false;

    } else if (type_id == 'submit-bot-token') {

        page5.hidden = true;
        page6.hidden = false;

        location.reload();

    } else if (type_id == 'submit-user-bot-token') {

        page5.hidden = true;
        page6.hidden = false;

        location.reload();

    } 
}
