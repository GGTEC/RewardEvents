
function append_notice(message_data_parse){

    var div_events = document.getElementById('div-events');

    var chatBlockInner = document.getElementById('chat-block-inner');
    var dchatBlockInnertwo = document.getElementById('chat-block-inner-two');
    var chatBlockInnerthree = document.getElementById('chat-block-inner-three');
    var chatBlockOut = document.getElementById('chat-block-out');

    var message_rec = message_data_parse.message;
    var user_input = message_data_parse.user_input;
    var color_get = message_data_parse.color;
    var chat_data = message_data_parse.data_show;
    var chat_time = message_data_parse.data_time;
    var font_size = message_data_parse.font_size;
    var font_size_chat = message_data_parse.font_size_chat;

    var show_commands = message_data_parse.show_commands;
    var show_events = message_data_parse.show_events;
    var show_join = message_data_parse.show_join;
    var show_leave = message_data_parse.show_leave;
    var show_redeem = message_data_parse.show_redeem;

    var show_commands_chat = message_data_parse.show_commands_chat;
    var show_events_chat = message_data_parse.show_events_chat;
    var show_join_chat = message_data_parse.show_join_chat;
    var show_leave_chat = message_data_parse.show_leave_chat;
    var show_redeem_chat = message_data_parse.show_redeem_chat;

    var type_message = message_data_parse.type_event;

    if ((type_message === "command" && show_commands === 1) ||
    (type_message === "redeem" && show_redeem === 1) ||
    (type_message === "event" && show_events === 1) ||
    (type_message === "join" && show_join === 1) ||
    (type_message === "leave" && show_leave === 1)) {

      var time_chat = document.createElement("span");
      time_chat.setAttribute('data-passed',chat_time)
      time_chat.classList.add("event-time-current");
      time_chat.innerHTML = 'Agora';

      var message_span = document.createElement('span');
      message_span.id = "message-chat";
      message_span.style.color = color_get;

      if (user_input === null || user_input === undefined || user_input === ''){
        message_span.innerHTML = message_rec
      } else {
        message_span.innerHTML = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`
      }
      
      message_div = document.createElement('div');
      if (chat_data == 1){
          message_div.appendChild(time_chat);
      }

      message_div.appendChild(message_span);

      var div_event_create = document.createElement("div");

      div_event_create.id = 'recent-message-block'
      div_event_create.classList.add('event-message', 'chat-block-color');
      div_event_create.style.fontSize = font_size + 'px';

      div_event_create.appendChild(message_div);

      div_events.insertBefore(div_event_create, div_events.firstChild);

    }

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

      chatBlockInner.appendChild(div_event_create);
      chatBlockInner.scrollTop = chatBlockInner.scrollHeight;
  
      dchatBlockInnertwo.appendChild(div_event_create.cloneNode(true));
      dchatBlockInnertwo.scrollTop = dchatBlockInnertwo.scrollHeight;
  
      chatBlockInnerthree.appendChild(div_event_create.cloneNode(true));
      chatBlockInnerthree.scrollTop = chatBlockInnerthree.scrollHeight;

      if (chatBlockOut != undefined || chatBlockOut != null){

        chatBlockOut.appendChild(chatBlockOut.cloneNode(true));
        chatBlockOut.scrollTop = chatBlockOut.scrollHeight;
        
      }

    }

}

function append_notice_w(message_data_parse){

  var div_events_w = document.getElementById('div-events-w');

  var message_rec = message_data_parse.message;
  var user_input = message_data_parse.user_input;
  var color_get = message_data_parse.color;
  var chat_data = message_data_parse.data_show;
  var chat_time = message_data_parse.data_time;
  var show_commands = message_data_parse.show_commands;
  var show_events = message_data_parse.show_events;
  var show_join = message_data_parse.show_join;
  var show_leave = message_data_parse.show_leave;
  var show_redeem = message_data_parse.show_redeem;
  var type_message = message_data_parse.type_event;
  var font_size = message_data_parse.font_size;

  var time_chat = document.createElement("span");
  time_chat.setAttribute('data-passed',chat_time)
  time_chat.classList.add("event-time-current");
  time_chat.innerHTML = 'Agora';

  var message_span = document.createElement('span');
  message_span.id = "message-chat";
  message_span.style.color = color_get;

  if (user_input === null || user_input === undefined || user_input === ''){
    message_span.innerHTML = message_rec
  } else {
    message_span.innerHTML = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`
  }
  
  message_div = document.createElement('div');
  if (chat_data == 1){
      message_div.appendChild(time_chat);
  }

  message_div.appendChild(message_span);

  var div_event = document.createElement("div");

  div_event.id = 'recent-message-block'
  div_event.classList.add('event-message', 'chat-block-color');
  div_event.style.fontSize = font_size + "px";

  div_event.appendChild(message_div);

  if ((type_message === "command" && show_commands === 1) ||
  (type_message === "redeem" && show_redeem === 1) ||
  (type_message === "event" && show_events === 1) ||
  (type_message === "join" && show_join === 1) ||
  (type_message === "leave" && show_leave === 1)) {

  div_events_w.insertBefore(div_event, div_events_w.firstChild);

  }
}

async function start_event_updatetime(){
  
  while (true){

    var div_event = document.querySelectorAll('.event-time-current');

    for(var i = 0; i < div_event.length; i++ ){

      get_data = div_event[i].getAttribute("data-passed");

      var date = new Date(get_data);
      var now = new Date();

      var difftimeMs = now.getTime() - date.getTime();
      var difftimes = difftimeMs / 1000;

      var days = Math.floor(difftimes / 86400);
      var hours = Math.floor((difftimes % 86400) / 3600);
      var minutes = Math.floor((difftimes % 3600) / 60);

      var chat_time = '';

      if (days >= 1) {
        chat_time += days + 'd';
      } else if (hours >= 1){
        chat_time += hours + 'h';
      } else if (minutes >= 1){
        chat_time += minutes + 'm';
      } else {
        chat_time += 'Agora';
      }

      div_event[i].innerHTML = chat_time

    }
    await sleep(60000)

  }

}

async function start_events_log(div_id){

    var div_events = document.getElementById(div_id);

    var list_messages_parse = await window.pywebview.api.event_log('get', 'null');

    if (list_messages_parse) {
      
      list_messages_parse = JSON.parse(list_messages_parse)
      
      var list = list_messages_parse.messages

      list.reverse();

      div_events.innerHTML = ""
      
      if (div_id == 'div-events'){
        if (list.length < 5){
          max = list.length
        } else {
          max = 5
        }
        
      } else if (div_id == 'div-events-w'){
        if (list.length < 15){
          max = list.length
        } else {
          max = 15
        }
      }

      
      for(var i = 0; i < max; i++) {
        
        var part = list[i].split(" | ");
        
        var dateString = part[0];
        var message_rec = part[2];
        var type_message = part[1];

        if (part.length > 3){
          var user_input = part[3];
        } else {
          var user_input = ''
        }
        
  
        var date = new Date(dateString);
        var now = new Date();
  
        var difftimeMs = now.getTime() - date.getTime();
        var difftimes = difftimeMs / 1000;
  
        var days = Math.floor(difftimes / 86400);
        var hours = Math.floor((difftimes % 86400) / 3600);
        var minutes = Math.floor((difftimes % 3600) / 60);

        var chat_time = '';
  
        if (days >= 1) {
          chat_time += days + 'd';
        } else if (hours >= 1){
          chat_time += hours + 'h';
        } else if (minutes >= 1){
          chat_time += minutes + 'm';
        } else {
          chat_time += 'Agora';
        }
  
        var color_get = list_messages_parse.color;
        var chat_data = list_messages_parse.data_show;
        var show_commands = list_messages_parse.show_commands;
        var show_events = list_messages_parse.show_events;
        var show_join = list_messages_parse.show_join;
        var show_leave = list_messages_parse.show_leave;
        var show_redeem = list_messages_parse.show_redeem;

        var time_chat = document.createElement("span");
        time_chat.setAttribute('data-passed',dateString)
        time_chat.classList.add("event-time-current");
        time_chat.innerHTML = chat_time;

        var message_span = document.createElement('span');
        message_span.id = "message-chat";
        message_span.style.color = color_get;

        if (user_input === null || user_input === undefined || user_input === ''){
          message_span.innerHTML = message_rec
        } else {
          message_span.innerHTML = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`
        }
        
        
        message_div = document.createElement('div');
        if (chat_data == 1){
            message_div.appendChild(time_chat);
        }
  
        message_div.appendChild(message_span);
  
        var div_event = document.createElement("div");
  
        div_event.id = 'recent-message-block'
        div_event.classList.add('chat-message','event-message');
        div_event.style.fontSize = "16px";
  
        div_event.appendChild(message_div);
        
        if ((type_message === "command" && show_commands === 1) ||
        (type_message === "redeem" && show_redeem === 1) ||
        (type_message === "event" && show_events === 1) ||
        (type_message === "join" && show_join === 1) ||
        (type_message === "leave" && show_leave === 1)) {
          div_events.appendChild(div_event);
        }
  
  
      }
    }
}


