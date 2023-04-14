$(document).ready(async function () {

  eel.loaded()();
  updateTimeDiff()
  event_log_js('div-events')
  event_updatetime()
  prediction_small()
  poll_small()
  goal()
  $('[data-toggle="tooltip"]').tooltip();
  $("input, select, textarea").attr("autocomplete", "off");
  $("input, select, textarea").attr("spellcheck", "false");


  $('select').selectpicker({
    liveSearch: true,
    showSubtext: true,
    size: 5,
    width: '100%',
    style: 'btn-dark',
    noneResultsText: "Nenhum resultado para {0}",
    liveSearchPlaceholder: "Pesquise o item",
    noneSelectedText : 'Selecione um item'
  });

  const carousel = document.querySelector('.carousel');
  const flkty = new Flickity(carousel, {
    // Opções do Flickity aqui
    contain: true,
    wrapAround: true,
    autoPlay: true,
    prevNextButtons: false,
    pageDots: false,
    setGallerySize: false
  });

  var disclosure = await eel.disclosure_py('get','null')();
  if (disclosure){
      document.getElementById('message-disclosure-send').value = disclosure
  }
  

});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

eel.expose(receive_live_info)
function receive_live_info(data){

    const spec_data = JSON.parse(data);

    document.getElementById('text-counter').innerText = " " + spec_data.specs;
    document.getElementById('time-in-live').innerText = spec_data.time;

    if (spec_data.specs != 'Offline'){
        document.getElementById('live-dot').style.color = 'red';
    }
}

eel.profile_info()(async function(data_auth){

    const data_profile = JSON.parse(data_auth);

    var profile_image = document.getElementById("profile_image");
    var profile_image_new = profile_image.src;
    profile_image.src = profile_image_new; 

    document.getElementById('email').innerText = data_profile.email;;
    document.getElementById('user_id').innerText = data_profile.user_id;
    document.getElementById('ex_name').innerText = data_profile.display_name;
    document.getElementById('login_name').innerText = data_profile.login_name;
    
})

async function create_clip() {
  var buttom_clip = document.getElementById('create-clip');
  eel.clip()
  buttom_clip.disabled = true;
  buttom_clip.classList.add('disabled');
  await sleep(5000)
  buttom_clip.disabled = false;
  buttom_clip.classList.remove('disabled');
}

eel.expose(toast_notifc);
function toast_notifc(text){

  if (text == 'error'){
    text = 'Ocorreu um erro no salvamento, verifique se os dados estão corretos ou entre em contato com o suporte.'
  } else if (text == 'success') {
    text = 'Sucesso ao salvar'
  }

  Bs5Utils.defaults.toasts.position = 'bottom-right';
  Bs5Utils.defaults.toasts.container = 'toast-container';
  Bs5Utils.defaults.toasts.stacking = true;

  const bs5Utils = new Bs5Utils();

  Bs5Utils.registerStyle('dark-purple', {
    btnClose: ['btn-close-white'],
    main: ['bg-dark', 'text-white'],
    border: ['custom-border-modal']
  });

  bs5Utils.Toast.show({
    type: 'dark-purple',
    icon: `<i class="far fa-check-circle fa-lg me-2"></i>`,
    title: 'Notificação',
    subtitle: '',
    buttons : [],
    content: text,
    delay: 5000,
    dismissible: true
});

}

function logout() {
  $("#confirm-logout").modal("show");
}

function confirm_logout(){
  eel.logout_auth()
}

eel.expose(callback_obs);
function callback_obs(type_id){
  if(type_id == 'sucess'){
    document.getElementById('obs_conn_status').innerHTML = 'Conectado'
  } else if (type_id == 'error'){
    document.getElementById('obs_conn_status').innerHTML = 'Desconectado'
  }
}

async function disclosure(event,type_id){

  if (type_id == 'save'){

      event.preventDefault()

      var form_disclosure = document.querySelector('#form-disclosure');
      var disclosure = form_disclosure.querySelector('#message-disclosure-send').value;
      var button_copy = document.getElementById("copy-dis");
      var button_save = document.getElementById("submit-message-disclosure");
    
      eel.disclosure_py(type_id,disclosure);
    
      button_copy.disabled = true;
      button_save.disabled = true;
      document.getElementById('message-disclosure-send').value = 'Salvo!';
    
      await sleep(3000)
    
      button_copy.disabled = false;
      button_save.disabled = false;
      
      document.getElementById('message-disclosure-send').value = disclosure;

  } else if (type_id == 'copy'){

      var copyText = document.getElementById("message-disclosure-send");
      var button_copy = document.getElementById("copy-dis");
      var button_save = document.getElementById("submit-message-disclosure");

      var saved_message = copyText.value

      copyText.select(); 
      navigator.clipboard.writeText(copyText.value);

      button_copy.disabled = true;
      button_save.disabled = true;
      document.getElementById('message-disclosure-send').value = 'Copiado para a Clipboard!';


      await sleep(3000)

      button_copy.disabled = false;
      button_save.disabled = false;
      document.getElementById('message-disclosure-send').value = saved_message;
  }
}

eel.expose(update_modal);
async function update_modal(type_id){

  if (type_id == 'get'){
    var status = await eel.update_check('check')();

    if(status){
      if (status == 'true'){
        $("#update-modal").modal("show");
      } else if (status == 'false'){
        document.getElementById('no-update').hidden = false;
      }
    }
  } else if (type_id == 'open'){
    eel.update_check('open')();
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

eel.expose(update_div_redeem);
function update_div_redeem(data_redeem) {

    var data_redem_parse = JSON.parse(data_redeem);

    var image_redeem = document.getElementById("image_redeem");
    var name_redeem = document.getElementById("name_redeem");
    var user_redeem = document.getElementById("user_redeem");

    var image_redeem_new = image_redeem.src;
    image_redeem.src = image_redeem_new; 

    name_redeem.innerText = data_redem_parse.redeem_name
    user_redeem.innerText = data_redem_parse.redeem_user
}


async function getFolder(id,type_id) {
  var dosya_path = await eel.select_file_py(type_id)();
  if (dosya_path) {
      document.getElementById(id).value = dosya_path;
      if (id == 'file-select-notific'){
          chat_config('save')
      }
  }
}

var redeem_icon =  document.querySelector('#redeem-icon-toggler');
var collpase_redeem = document.getElementById('colapse-redeem')

collpase_redeem.addEventListener('hidden.bs.collapse', function () {
  redeem_icon.innerHTML = "<i class='fa-solid fa-square-caret-down'></i>"
})

collpase_redeem.addEventListener('shown.bs.collapse', function () {
  redeem_icon.innerHTML = "<i class='fa-solid fa-square-caret-up'></i>"
})

var utils_icon =  document.querySelector('#utils-icon-toggler');
var collpase_utils = document.getElementById('colapse-utils')

collpase_utils.addEventListener('hidden.bs.collapse', function () {
  utils_icon.innerHTML = "<i class='fa-solid fa-square-caret-down'></i>"
})

collpase_utils.addEventListener('shown.bs.collapse', function () {
  utils_icon.innerHTML = "<i class='fa-solid fa-square-caret-up'></i>"
})


var carroucel_icon =  document.querySelector('#carroucel-icon-toggler');
var collpase_carroucel = document.getElementById('colapse-carroucel')

collpase_utils.addEventListener('hidden.bs.collapse', function () {
  carroucel_icon.innerHTML = "<i class='fa-solid fa-square-caret-down'></i>"
})

collpase_utils.addEventListener('shown.bs.collapse', function () {
  carroucel_icon.innerHTML = "<i class='fa-solid fa-square-caret-up'></i>"
})


const div_events_scroll = document.getElementById("div-events");

const itensPorPagina = 10;
let paginaAtual = 1;

div_events_scroll.addEventListener("scroll",async function() {

  if (div_events_scroll.scrollTop + div_events_scroll.clientHeight >= div_events_scroll.scrollHeight) {

    var list_messages = await eel.event_log('get', 'null')();

    if (list_messages) {

      var list_messages_parse = JSON.parse(list_messages);
      var lista = list_messages_parse.messages

      lista.reverse()
      // usuário rolou para baixo até o final da div
      const startIndex = paginaAtual * itensPorPagina;
      const endIndex = startIndex + itensPorPagina;
      const items = lista.slice(startIndex, endIndex);

      // adicione os itens na div
      for (let i = 0; i < items.length; i++) {

        var part = items[i].split(" | ");
  
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
          div_events_scroll.appendChild(div_event);
        }
        
      }
      // atualize a página atual
      paginaAtual++;
    }
    
  }
});