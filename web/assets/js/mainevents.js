window.addEventListener('pywebviewready',async function() {

  start_events_log('div-events-w')
  start_event_updatetime()

  });


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}



const div_events_w_scroll = document.getElementById("div-events-w");
const itensPorPagina_w = 10;
let paginaAtual_w = 1;


div_events_w_scroll.addEventListener("scroll",async function() {

  if (div_events_w_scroll.scrollTop + div_events_w_scroll.clientHeight >= div_events_w_scroll.scrollHeight) {

    var list_messages = await window.pywebview.api.event_log('get', 'null');

    if (list_messages) {

      var list_messages_parse = JSON.parse(list_messages);
      var lista = list_messages_parse.messages

      lista.reverse()
      // usuário rolou para baixo até o final da div
      const startIndex_w = paginaAtual_w * itensPorPagina_w;
      const endIndex_w = startIndex_w + itensPorPagina_w;
      const items_w = lista.slice(startIndex_w, endIndex_w);

      // adicione os itens na div
      for (let i = 0; i < items_w.length; i++) {

        var part = items_w[i].split(" | ");
  
        var dateString = part[0];
  
        var date = new Date(dateString);
        var now = new Date();
  
        var difftimeMs = now.getTime() - date.getTime();
        var difftimes = difftimeMs / 1000;
  
        var days = Math.floor(difftimes / 86400);
        var hours = Math.floor((difftimes % 86400) / 3600);
        var minutes = Math.floor((difftimes % 3600) / 60);
  
        var chat_time = '';
  
        if (days > 0) {
          chat_time += days + 'd';
        } else if (hours > 1){
          chat_time += hours + 'h';
        } else if (minutes >= 1){
          chat_time += minutes + 'm ';
        } else {
          chat_time += 'agora';
        }
  
        var message_rec = part[2];
        var type_message = part[1];
  
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
        message_span.innerHTML = message_rec
        
        
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
          div_events_w_scroll.appendChild(div_event);
        }
        
      }
      // atualize a página atual
      paginaAtual_w++;
    }
    
  }
});


div_events_w_scroll.addEventListener("wheel",async function(event) {
  if (event.deltaY > 0) {
    if (div_events_w_scroll.scrollHeight <= div_events_w_scroll.clientHeight) {
      if (div_events_w_scroll.scrollTop + div_events_w_scroll.clientHeight >= div_events_w_scroll.scrollHeight) {

        var list_messages = await window.pywebview.api.event_log('get', 'null');
    
        if (list_messages) {
    
          var list_messages_parse = JSON.parse(list_messages);
          var lista = list_messages_parse.messages
    
          lista.reverse()
          // usuário rolou para baixo até o final da div
          const startIndex_w = paginaAtual_w * itensPorPagina_w;
          const endIndex_w = startIndex_w + itensPorPagina_w;
          const items_w = lista.slice(startIndex_w, endIndex_w);
    
          // adicione os itens na div
          for (let i = 0; i < items_w.length; i++) {
    
            var part = items_w[i].split(" | ");
      
            var dateString = part[0];
      
            var date = new Date(dateString);
            var now = new Date();
      
            var difftimeMs = now.getTime() - date.getTime();
            var difftimes = difftimeMs / 1000;
      
            var days = Math.floor(difftimes / 86400);
            var hours = Math.floor((difftimes % 86400) / 3600);
            var minutes = Math.floor((difftimes % 3600) / 60);
      
            var chat_time = '';
      
            if (days > 0) {
              chat_time += days + 'd';
            } else if (hours > 1){
              chat_time += hours + 'h';
            } else if (minutes >= 1){
              chat_time += minutes + 'm ';
            } else {
              chat_time += 'agora';
            }
      
            var message_rec = part[2];
            var type_message = part[1];
      
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
            message_span.innerHTML = message_rec
            
            
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
              div_events_w_scroll.appendChild(div_event);
            }
            
          }
          // atualize a página atual
          paginaAtual_w++;
        }
        
      }
    }
  }
});


