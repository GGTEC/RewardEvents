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

eel.expose(append_message);
function append_message(message_data){

    var div_chat = document.getElementById('chat-block');
    var apply_color = document.getElementById('chat-colors').checked;
    var fix_color = document.getElementById('chat-colors-fixed').checked;
    var select_color = document.getElementById('select-color').value;
    var show_badges = document.getElementById('chat-bageds-show').checked;
    var chat_newline = document.getElementById('chat-newline').checked;

    
    var message_data_parse = JSON.parse(message_data);
    var type_message = message_data_parse.type

    if (type_message == 'PRIVMSG'){
    
        var message_rec = pass_message(message_data_parse.message)
        var user_rec = message_data_parse.display_name
        var mod_rec = message_data_parse.mod
        var sub_rec = message_data_parse.subscriber
        var color_rec = message_data_parse.color

        console.log(message_data_parse.message)
        

        if (apply_color == true){
            if (color_rec == null){
                
                if (fix_color == true){

                    var color_rec = select_color;
                } else {
                    colors = ['Blue', 'Coral', 'DodgerBlue', 'SpringGreen', 'YellowGreen', 'Green', 'OrangeRed', 'Red', 'GoldenRod', 'HotPink', 'CadetBlue', 'SeaGreen', 'Chocolate', 'BlueViolet','Firebrick']
                
                    var color_rec = choose(colors);
                }
            }
        } else {
            color_rec = ""
        }

        if (chat_newline == true) {
            chat_newline_val = '<br>'
        } else {
            chat_newline_val = ''
        }

        if (show_badges == true){
            if (mod_rec == 1){
                sword = '<i class="fa-solid fa-user-shield" id="usershield"></i>'
            } else {
                sword = ''
            }
            if (sub_rec == 1){
                star = '<i class="fa-solid fa-star" id="userstar"></i>'
            } else {
                star = ''
            }

        } else {
            star = ''
            sword = ''
        }


        
        var message_div = '<span id="user-badges">'+ star + sword +' </span><span id="user-chat" style=color:'+ color_rec +';>'+ user_rec + ' : </span>'+ chat_newline_val +'<span id="message-chat">'+ message_rec +'</span>';
        var div = document.createElement("div");
        div.innerHTML = message_div;
        div.id = 'chat-message-block'

        div_chat.appendChild(div);
        div_chat.scrollTop = div_chat.scrollHeight;

    } else if (type_message == 'CONN'){

        toast_notifc('Bot desconectado, conectando ao chat...')

    } else if (type_message == 'CONNSUCESS'){

        toast_notifc('Bot conectado!')

    }

}


eel.expose(users_chat);
function users_chat(user_list){

  var users_block = document.getElementById('users-chat-list');

  users_block.innerHTML = '';

  user_list.forEach(function (item, index) {

    text_item = document.createElement("p");

    text_item.innerHTML = "<spam class='name-user-list'>"+item+"</spam>"
    text_item.setAttribute('onclick','eel.open_link("'+item+'")')
    users_block.appendChild(text_item);

  });
}


function send_message_chat_js(event){

    event.preventDefault()
  
    var form_message = document.querySelector('#input-chat-form');
    var message = form_message.querySelector('#message-chat-send').value;
  
    console.log(message)
    eel.send_message_chat(message);
  
    document.getElementById('message-chat-send').value = "";
  
  }


$("#slider-font").on("input",function () {
    $('#chat-message-block').css("font-size", $(this).val() + "px");
});
