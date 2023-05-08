
function append_notice_chat_w(message_data_parse){

  console.log(message_data_parse)
  
  var chatBlockOut = document.getElementById('chat-block-out');

  var message_rec = message_data_parse.message;
  var user_input = message_data_parse.user_input;
  var color_get = message_data_parse.color;
  var font_size_chat = message_data_parse.font_size_chat;

  var show_commands_chat = message_data_parse.show_commands_chat;
  var show_events_chat = message_data_parse.show_events_chat;
  var show_join_chat = message_data_parse.show_join_chat;
  var show_leave_chat = message_data_parse.show_leave_chat;
  var show_redeem_chat = message_data_parse.show_redeem_chat;

  var type_message = message_data_parse.type_event;

  if ((type_message === "command" && show_commands_chat === 1) ||
  (type_message === "redeem" && show_redeem_chat === 1) ||
  (type_message === "event" && show_events_chat === 1) ||
  (type_message === "join" && show_join_chat === 1) ||
  (type_message === "leave" && show_leave_chat === 1)) {


    var message_span = document.createElement('span');
    message_span.id = "message-chat";
    message_span.style.color = color_get;

    if (user_input === null || user_input === undefined || user_input === ''){
      message_span.innerHTML = message_rec
    } else {
      message_span.innerHTML = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`
    }
    
    message_div = document.createElement('div');

    message_div.appendChild(message_span);

    var div_event_create = document.createElement("div");

    div_event_create.id = 'recent-message-block'
    div_event_create.classList.add('event-message', 'chat-block-color');
    div_event_create.style.fontSize = font_size_chat + 'px';

    div_event_create.appendChild(message_div);

    console.log(div_event_create)

    chatBlockOut.appendChild(div_event_create);
    chatBlockOut.scrollTop = chatBlockOut.scrollHeight;


  }

}



