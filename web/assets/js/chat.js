
$(window).on("load",async function(){

    while (true){

        data_receive = await eel.get_chat_list()();

        if (data_receive){

            var list_data = JSON.parse(data_receive);

            var div_user = document.getElementById('div_users');
            var div_bot = document.getElementById('div_bots');

            div_user.innerHTML = ''
            div_bot.innerHTML = ''

            for (let item of list_data.user_list){

                div_item = document.createElement("div");
                div_item.setAttribute('hidden','false');
                div_item.classList.add("d-flex", "justify-content-between");
                
                div_name = document.createElement("div");

                div_buttom = document.createElement("div");

                buttom_ban = document.createElement("button");
                buttom_ban.innerHTML = "<i class='fa-solid fa-ban'></i>"
                buttom_ban.classList.add("btn", "bt-submit", "btn-sm", "me-1");
                buttom_ban.setAttribute('onclick','eel.timeout_user("'+item+'","ban")');
                buttom_ban.setAttribute('title','Banir usuário');

                buttom_timeout = document.createElement("button");
                buttom_timeout.innerHTML = "<i class='fa-solid fa-clock'></i>"
                buttom_timeout.classList.add("btn", "bt-submit", "btn-sm", "me-1");
                buttom_timeout.setAttribute('onclick','eel.timeout_user("'+item+'","timeout")');
                buttom_timeout.setAttribute('title','Aplicar timeout no usuário');
                
                buttom_addlist = document.createElement("button");
                buttom_addlist.innerHTML = "<i class='fa-solid fa-plus'></i>"
                buttom_addlist.classList.add("btn", "bt-submit", "btn-sm", "me-1");
                buttom_addlist.setAttribute('onclick','eel.chat_config("'+item+'","list_add")');
                buttom_addlist.setAttribute('title','Adicionar na lista para ser ignorado');
                
                name_user = document.createElement("spam");
                name_user.innerHTML = item
                name_user.classList.add("name-user-list");
                name_user.setAttribute('onclick','eel.open_py("user","'+item+'")');

                div_name.appendChild(name_user);
                div_buttom.appendChild(buttom_ban);
                div_buttom.appendChild(buttom_timeout);
                div_buttom.appendChild(buttom_addlist);

                div_item.appendChild(div_name);
                div_item.appendChild(div_buttom);

                div_user.appendChild(div_item);
            }

            for (let item of list_data.bot_list){

                div_item = document.createElement("div");
                div_item.setAttribute('hidden','false');
                div_item.classList.add("d-flex", "justify-content-between");
                
                div_name = document.createElement("div");

                div_buttom = document.createElement("div");

                buttom_ban = document.createElement("button");
                buttom_ban.innerHTML = "<i class='fa-solid fa-ban'></i>"
                buttom_ban.classList.add("btn", "bt-submit", "btn-sm", "me-1");
                buttom_ban.setAttribute('onclick','eel.timeout_user("'+item+'","ban")');
                buttom_ban.setAttribute('title','Banir usuário');

                buttom_timeout = document.createElement("button");
                buttom_timeout.innerHTML = "<i class='fa-solid fa-clock'></i>"
                buttom_timeout.classList.add("btn", "bt-submit", "btn-sm", "me-1");
                buttom_timeout.setAttribute('onclick','eel.timeout_user("'+item+'","timeout")');
                buttom_timeout.setAttribute('title','Aplicar timeout no usuário');
                
                buttom_addlist = document.createElement("button");
                buttom_addlist.innerHTML = "<i class='fa-solid fa-plus'></i>"
                buttom_addlist.classList.add("btn", "bt-submit", "btn-sm", "me-1");
                buttom_addlist.setAttribute('onclick','eel.chat_config("'+item+'","list_add")');
                buttom_addlist.setAttribute('title','Adicionar na lista para ser ignorado');
                
                name_user = document.createElement("spam");
                name_user.innerHTML = item
                name_user.classList.add("name-user-list");
                name_user.setAttribute('onclick','eel.open_py("user","'+item+'")');

                div_name.appendChild(name_user);
                div_buttom.appendChild(buttom_ban);
                div_buttom.appendChild(buttom_timeout);
                div_buttom.appendChild(buttom_addlist);

                div_item.appendChild(div_name);
                div_item.appendChild(div_buttom);

                div_bot.appendChild(div_item);
            }
            
        }

        await sleep(10000)
    }

});

function collapse(div_id){
    div_el = document.getElementById(div_id);

    if (div_el.hidden == false) {

        div_el.hidden = true;

    } else {

        div_el.hidden = false;
    }
}

function pass_message(message_to){

    if (message_to.startsWith('/me')){

        message_ret = message_to.replace("/me", "<i>");
        message_ret = message_ret + "</i>";

        return message_ret

    } else if (message_to.startsWith('\x01ACTION')){  

        message_ret = message_to.replace("\x01ACTION", "<i>");
        message_ret = message_ret.replace("\x01", "</i>");

        return message_ret

    } else {

        return message_to

    }
}

function choose(choices) {
    var index = Math.floor(Math.random() * choices.length);
    return choices[index];
}

eel.expose(append_announce);
function append_announce(message_data){

    var div_chat = document.getElementById('chat-block');
    var message_data_parse = JSON.parse(message_data);
    
    var message_rec = pass_message(message_data_parse.message)
    var name = message_data_parse.display_name;
    var text_size = message_data_parse.font_size;
    var color_message = message_data_parse.color_message;
    var color_get = message_data_parse.color;
    var chat_data = message_data_parse.data_show;
    var chat_time = message_data_parse.chat_time;
    var type_data = message_data_parse.type_data;
    var show_badges = message_data_parse.show_badges;
    var badges = message_data_parse.badges;
    var chat_newline = message_data_parse.wrapp_message;
    
    if (show_badges == 1){
        badges_data = badges
    } else {
        badges_data = '';
    }

    if (type_data == 'passed'){

        let date = new Date(chat_time);
        let formattedDate = date.toLocaleDateString() + " " + date.toLocaleTimeString();
        var time_chat = document.createElement("span");
        time_chat.id = 'time_chat';
        time_chat.setAttribute("data-time", chat_time);
        time_chat.setAttribute("title", formattedDate);
        time_chat.classList.add("message-time");
        time_chat.innerHTML = 'Agora';

    } else if (type_data == 'current'){
        var time_chat = document.createElement("span");
        time_chat.id = 'time_chat';
        time_chat.classList.add("message-time-current");
        time_chat.innerHTML = chat_time;
    }

    var annnoucement = document.createElement("span");
    annnoucement.id = 'annoucement-span';
    annnoucement.innerHTML = '<i class="fa-solid fa-bullhorn"></i> Anúncio <br>'
    annnoucement.style.fontSize = text_size + "px";

    var span_badges = document.createElement("span");
    span_badges.id = 'user-badges';
    span_badges.innerHTML = badges_data;

    var message_name = document.createElement('span');
    message_name.id = "message-chat";
    message_name.style.color = color_get;
    message_name.innerHTML = name + ' :';

    var message_span = document.createElement('span');
    message_span.id = "message-chat";
    message_span.innerHTML = message_rec;

    var new_line = document.createElement("br");

    message_div = document.createElement('div');

    message_div.appendChild(annnoucement);

    if (chat_data == 1){
        message_div.appendChild(time_chat);
    }
    
    message_div.appendChild(span_badges);
    message_div.appendChild(message_name);
    
    if (chat_newline == 1) {
        message_div.appendChild(new_line);
    }

    message_div.appendChild(message_span);
    
    
    var div = document.createElement("div");

    div.id = 'chat-message-block'
    div.classList.add('chat-message', 'chat-block-color-announce');
    div.style.color = 'white' ;
    div.style.borderLeftColor = color_message;
    div.style.fontSize = text_size + "px";

    div.appendChild(message_div);
    div_chat.appendChild(div);

    div_chat.scrollTop = div_chat.scrollHeight;
}

eel.expose(append_notice);
function append_notice(message_data){

    var div_chat = document.getElementById('chat-block');
    var message_data_parse = JSON.parse(message_data);
    
    var message_rec = pass_message(message_data_parse.message)
    var text_size = message_data_parse.font_size;
    var color_get = message_data_parse.color;
    var chat_data = message_data_parse.data_show;
    var chat_time = message_data_parse.chat_time;
    var type_data = message_data_parse.type_data;

    if (type_data == 'passed'){

        let date = new Date(chat_time);
        let formattedDate = date.toLocaleDateString() + " " + date.toLocaleTimeString();
        var time_chat = document.createElement("span");
        time_chat.id = 'time_chat';
        time_chat.setAttribute("data-time", chat_time);
        time_chat.setAttribute("title", formattedDate);
        time_chat.classList.add("message-time");
        time_chat.innerHTML = 'Agora';

    } else if (type_data == 'current'){
        var time_chat = document.createElement("span");
        time_chat.id = 'time_chat';
        time_chat.classList.add("message-time-current");
        time_chat.innerHTML = chat_time;
    }

    var message_span = document.createElement('span');
    message_span.id = "message-chat";
    message_span.style.color = color_get;
    message_span.innerHTML = message_rec
    
    
    message_div = document.createElement('div');
    if (chat_data == 1){
        message_div.appendChild(time_chat);
    }

    message_div.appendChild(message_span);
    
    
    var div = document.createElement("div");

    div.id = 'chat-message-block'
    div.classList.add('chat-message', 'chat-block-color');
    div.style.color = color_get ;
    div.style.fontSize = text_size + "px";

    div.appendChild(message_div);
    div_chat.appendChild(div);

    div_chat.scrollTop = div_chat.scrollHeight;
}


eel.expose(chat_config);
async function chat_config(type_config){

    var slider_font = document.getElementById('slider-font');
    var rangevalue_config = document.getElementById('rangevalue_config');
    var chat_colors = document.getElementById('chat-colors');
    var data_show = document.getElementById('data-show');
    var type_data = document.getElementById('select-time-mode');
    var time_format = document.getElementById('time-format');
    var chat_colors_fixed = document.getElementById('chat-colors-fixed');
    var chat_colors_block = document.getElementById('chat-colors-block');
    var select_color = document.getElementById('select-color').value;
    var select_color_not_join = document.getElementById('select-color-join').value;
    var select_color_not_leave = document.getElementById('select-color-leave').value;
    var select_color_not = document.getElementById('select-color-geral').value;
    var chat_bageds_show = document.getElementById('chat-bageds-show');
    var chat_newline = document.getElementById('chat-newline');
    var notfic_show_join = document.getElementById('notfic-show-join');
    var notfic_show_leave = document.getElementById('notfic-show-leave');
    var notfic_play = document.getElementById('notfic-play');
    var file_notific = document.getElementById('file-select-notific');
    var notfic_show_greetings = document.getElementById('notfic-show-greetings');
    var greetings = document.getElementById('greetings');
    var top_chatter = document.getElementById('top_chatter_limit');
    var regular = document.getElementById('regular_limit');

    rangevalue_config.innerHTML = slider_font.value + 'px';


    if (type_config == 'save'){

        chat_colors = chat_colors.checked ? 1 : 0;
        chat_colors_fixed = chat_colors_fixed.checked ? 1 : 0;
        chat_colors_block = chat_colors_block.checked ? 1 : 0;
        data_show = data_show.checked ? 1 : 0;
        chat_bageds_show = chat_bageds_show.checked ? 1 : 0;
        chat_newline = chat_newline.checked ? 1 : 0;
        notfic_show_join = notfic_show_join.checked ? 1 : 0;
        notfic_show_leave = notfic_show_leave.checked ? 1 : 0;
        notfic_play = notfic_play.checked ? 1 : 0;
        notfic_show_greetings = notfic_show_greetings.checked ? 1 : 0;

        data = {
            appply_colors : chat_colors,
            appply_no_colors : chat_colors_fixed,
            chat_colors_block: chat_colors_block,
            data_show : data_show,
            type_data : type_data.value,
            time_format : time_format.value,
            color_apply : select_color,
            color_not_join : select_color_not_join,
            color_not_leave : select_color_not_leave,
            color_not : select_color_not,
            font_size : slider_font.value,
            show_badges : chat_bageds_show,
            wrapp_message : chat_newline,
            not_user_join : notfic_show_join,
            not_user_leave : notfic_show_leave,
            not_user_sound : notfic_play,
            not_sound_path : file_notific.value,
            greetings_join : notfic_show_greetings,
            greetings : greetings.value,
            top_chatter : top_chatter.value,
            regular : regular.value
        }

        var formData = JSON.stringify(data);
        eel.chat_config(formData,type_config);
        
    } else if (type_config == 'get'){

        var chat_data = await eel.chat_config('null',type_config)()
        if (chat_data){

            var chat_data_parse = JSON.parse(chat_data);

            chat_colors.checked = chat_data_parse.appply_colors == 1 ? true : false;
            chat_colors_fixed.checked = chat_data_parse.appply_no_colors == 1 ? true : false;
            data_show.checked = chat_data_parse.data_show == 1 ? true : false;
            chat_colors_block.checked = chat_data_parse.block_color == 1 ? true : false;
            chat_bageds_show.checked = chat_data_parse.show_badges == 1 ? true : false;
            chat_newline.checked = chat_data_parse.wrapp_message == 1 ? true : false;
            notfic_show_join.checked = chat_data_parse.not_user_join == 1 ? true : false;
            notfic_show_leave.checked = chat_data_parse.not_user_leave == 1 ? true : false;
            notfic_show_greetings.checked = chat_data_parse.greetings_join == 1 ? true : false;
            notfic_play.checked = chat_data_parse.not_user_sound == 1 ? true : (chat_data_parse.not_user_sound == 0 ? false : notfic_play.checked);

            
            greetings.value = chat_data_parse.greetings;
            slider_font.value = chat_data_parse.font_size;
            rangevalue_config.innerHTML = chat_data_parse.font_size + 'px';
            time_format.value = chat_data_parse.time_format;
            top_chatter.value = chat_data_parse.top_chatter;
            regular.value = chat_data_parse.regular;


            $("#select-color").selectpicker('val', chat_data_parse.color_apply);
            $("#select-color-join").selectpicker('val', chat_data_parse.color_not_join);
            $("#select-color-leave").selectpicker('val', chat_data_parse.color_not_leave);
            $("#select-color-geral").selectpicker('val', chat_data_parse.color_not);
            $("#select-time-mode").selectpicker('val', chat_data_parse.type_data);
            
            file_notific.value = chat_data_parse.not_sound_path;
        }

    } else if (type_config == 'list_get'){

        var chat_data = await eel.chat_config('null',type_config)()

        if (chat_data){

            var chat_data_parse = JSON.parse(chat_data);

            $("#modal_list_chat").modal("show")

            var tbody = document.getElementById('chat-list-body');

            tbody.innerHTML = "";
        
            Object.entries(chat_data_parse).forEach(([v,k]) => {
        
              tbody.innerHTML += '<tr><td>' + k + '</td></tr>';
              
            })
        }

    } else if (type_config == 'list_add'){

        var username = document.getElementById('add_name_user').value;
        eel.chat_config(username,type_config);
        document.getElementById('add_name_user').value = '';
        
    } else if (type_config == 'list_rem'){

        var username = document.getElementById('add_name_user').value;
        eel.chat_config(username,type_config);
        document.getElementById('add_name_user').value = '';
        
    } else if (type_config == 'list_bot_get'){

        var chat_data = await eel.chat_config('null',type_config)()
        
        if (chat_data){

            var chat_data_parse = JSON.parse(chat_data);

            $("#modal_list_chat").modal("show")

            var tbody = document.getElementById('chat-list-body');

            tbody.innerHTML = "";
        
            Object.entries(chat_data_parse).forEach(([v,k]) => {
        
              tbody.innerHTML += '<tr><td>' + k + '</td></tr>';
              
            })
        }

    } else if (type_config == 'list_bot_add'){

        var username = document.getElementById('add_name_bot').value;
        eel.chat_config(username,type_config);
        document.getElementById('add_name_user').value = '';
        
    } else if (type_config == 'list_bot_rem'){

        var username = document.getElementById('add_name_bot').value;
        eel.chat_config(username,type_config);
        document.getElementById('add_name_bot').value = '';
        
    }

}


async function updateTimeDiff() {

    while (true){
        let dateTimeObjs = [];

        let messageTimeElements = document.querySelectorAll(".message-time");

        messageTimeElements.forEach(function(element) {
            let dateString = element.getAttribute("data-time");
            dateTimeObjs.push(new Date(dateString));
        });

        //Data e hora atual
        let now = new Date();
        messageTimeElements.forEach(function(element, index) {
            let dateTimeObj = dateTimeObjs[index];
            //Calculando a diferença entre as datas
            let delta = now - dateTimeObj;
            let minutes = Math.floor(delta / (1000 * 60));
            let hours = Math.floor(delta / (1000 * 60 * 60));
            let seconds = Math.floor(delta / 1000);
            if(hours < 1){
                if(minutes < 1){
                    element.innerHTML = seconds + " segundos";
                }else{
                    element.innerHTML = minutes + " minutos";
                }
            }else {
                element.innerHTML = hours + " horas";
            }
        });

        await sleep(5000)
    }
}

eel.expose(append_message);
function append_message(message_data){
    
    var div_chat = document.getElementById('chat-block');

    var message_data_parse = JSON.parse(message_data);
    var type_message = message_data_parse.type
    const maxMessages = 100;

    if (type_message == 'PRIVMSG'){

        var frist_message = message_data_parse.frist_message;
        var reply = message_data_parse.response;
        var apply_color = message_data_parse.appply_colors;
        var block_color = message_data_parse.block_color;
        var fix_color = message_data_parse.appply_no_colors;
        var select_color = message_data_parse.color_apply;
        var show_badges = message_data_parse.show_badges;
        var chat_newline = message_data_parse.wrapp_message;
        var text_size = message_data_parse.font_size;
        var chat_data = message_data_parse.data_show;
        var chat_time = message_data_parse.chat_time;
        var type_data = message_data_parse.type_data;

        var message_rec_reply = pass_message(message_data_parse.message_replied)
        var user_replied = pass_message(message_data_parse.user_replied)
        var message_rec = pass_message(message_data_parse.message)
        var user_rec = message_data_parse.display_name
        var badges = message_data_parse.badges
        var color_rec = message_data_parse.color
        var color_block = message_data_parse.color

        if (apply_color == 1) {
            var color_rec = (color_rec == null && fix_color == 1) ? select_color : choose(['Blue', 'Coral', 'DodgerBlue', 'SpringGreen', 'YellowGreen', 'Green', 'OrangeRed', 'Red', 'GoldenRod', 'HotPink', 'CadetBlue', 'SeaGreen', 'Chocolate', 'BlueViolet','Firebrick']);
            } else {
            var color_rec = "";
            }
            
            var border_color = (block_color == 1) ? ((color_block == "" && fix_color == 1) ? select_color : color_block) : '#4f016c';
            
            var badges_data = (show_badges == 1) ? badges : '';
        
        var div = document.createElement("div");

        if (type_data == 'passed'){
            let date = new Date(chat_time);
            let formattedDate = date.toLocaleDateString() + " " + date.toLocaleTimeString();
            var time_chat = document.createElement("span");
            time_chat.id = 'time_chat';
            time_chat.setAttribute("data-time", chat_time);
            time_chat.setAttribute("title", formattedDate);
            time_chat.classList.add("message-time");
            time_chat.innerHTML = 'Agora';

        } else if (type_data == 'current'){
            var time_chat = document.createElement("span");
            time_chat.id = 'time_chat';
            time_chat.classList.add("message-time-current");
            time_chat.innerHTML = chat_time;
        }

        
        var frist_div = document.createElement("div");
        frist_div.id = 'message-replyed-div';
        frist_div.style.fontSize = text_size - (text_size * 0.2) + "px";

        var span_new = document.createElement("span");
        span_new.id = 'new-user';
        span_new.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> Primeira vez no chat';

        frist_div.appendChild(span_new)

        var div_reply = document.createElement('div');
        div_reply.id = 'message-replyed-div';
        div_reply.style.fontSize = text_size - (text_size * 0.2) + "px";
        
        var span_user_reply = document.createElement('span');
        span_user_reply.id = 'user-reply';
        span_user_reply.innerHTML = '<i class="fa-solid fa-reply"></i> Respondendo á @' + user_replied +': ';

        var span_message_reply = document.createElement('span');
        span_message_reply.id = 'message-reply';
        span_message_reply.innerHTML = message_rec_reply;

        div_reply.appendChild(span_user_reply);
        div_reply.appendChild(span_message_reply);


        var span_badges = document.createElement("span");
        span_badges.id = 'user-badges';
        span_badges.innerHTML = badges_data;

        var span_username = document.createElement("span");
        span_username.id = 'user-chat';
        span_username.style.color = color_rec;
        span_username.innerHTML = user_rec + ' :';
        span_username.setAttribute('onclick','eel.open_py("user","'+user_rec+'")');

        var span_message = document.createElement("span");
        span_message.id = 'message-chat';
        span_message.innerHTML = message_rec;
        
        var new_line = document.createElement("br");

        div.id = 'chat-message-block'
        div.classList.add('chat-message', 'chat-block-color');
        div.style.fontSize = text_size + "px";
        div.style.border = "3px solid "+ border_color + "";

        reply == 1 ? div.appendChild(div_reply) : null;
        frist_message == 1 ? div.appendChild(frist_div) : null;
        chat_data == 1 ? div.appendChild(time_chat) : null;

        div.appendChild(span_badges);
        div.appendChild(span_username);

        chat_newline == 1 ? div.appendChild(new_line) : null;

        div.appendChild(span_message);

        div_chat.appendChild(div);
        div_chat.scrollTop = div_chat.scrollHeight;

        if (div_chat.childNodes.length > maxMessages) {
            div_chat.removeChild(div_chat.firstChild);
        }

        $('[data-toggle="tooltip"]').tooltip();

    }

        

}

function send_message_chat_js(event){

    event.preventDefault()
  
    var message = document.getElementById('message-chat-send').value;

    eel.send(message);
  
    document.getElementById('message-chat-send').value = "";
  
}


function slider_font() {
    slider = document.getElementById('slider-font');
    output = document.getElementById('rangevalue_config');
    $('.chat-message ').css("font-size", slider.value + "px");
    output.innerHTML = slider.value

};

