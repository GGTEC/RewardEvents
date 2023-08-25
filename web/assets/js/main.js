window.addEventListener('pywebviewready',async function() {

  var progressBar_start = document.getElementById("progress-bar-start");
  var progress_span = document.getElementById("progress-span");
  
  progressBar_start.style.width = `0%`;

  var functionsCount = 18; //defina a quantidade de funções a serem executadas
  var functionsExecuted = 0; //inicialize o contador de funções executadas


  $('[data-toggle="tooltip"]').tooltip();
  $("input, select, textarea").attr("autocomplete", "off");
  $("input, select, textarea").attr("spellcheck", "false");

  functionsExecuted++;
  progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  progress_span.innerHTML = 'Tooltips, inputs.'

  loaded = await window.pywebview.api.loaded();
  
  if (loaded){

    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
    progress_span.innerHTML = 'Start chat.'

    var disclosure = await window.pywebview.api.disclosure_py('get','null');
    if (disclosure){
        document.getElementById('message-disclosure-send').value = disclosure

        progress_span.innerHTML = 'disclosure.'
        functionsExecuted++;
        progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
    }

    get_users = await window.pywebview.api.get_users_info('save','null');
    if (get_users){

      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'Update users data.'

    }

    start_obs = await window.pywebview.api.start_obs();
    if (start_obs){

      if(start_obs == 'sucess'){
        document.getElementById('obs_conn_status').innerHTML = 'Conectado'
      } else if (start_obs == 'error'){
        document.getElementById('obs_conn_status').innerHTML = 'Desconectado'
      } else if (start_obs == 'None'){
        document.getElementById('obs_conn_status').innerHTML = 'Desconhecido'
      }

      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'start obs.'

    }


    start_selectpicker()

    progress_span.innerHTML = 'selectpicker.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso


    start_sidebar()

    progress_span.innerHTML = 'sidebar.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso


    start_scroll()

    progress_span.innerHTML = 'scroll.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso


    start_resizable()

    progress_span.innerHTML = 'resizable.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso


    start_update_time_chat()

    progress_span.innerHTML = 'auto update time chat.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    start_events_log('div-events')

    progress_span.innerHTML = 'get event logs.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    start_event_updatetime()

    progress_span.innerHTML = 'auto update time events.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    prediction_small()

    progress_span.innerHTML = 'predicitons status.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    poll_small()

    progress_span.innerHTML = 'polls status.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    goal()

    progress_span.innerHTML = 'goal status.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso


    start_profile_info()

    progress_span.innerHTML = 'streamer profile info.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    $('#main').removeClass('d-none')
    $('#loading').addClass('remove-loading')

    setTimeout(function() {
      $('#loading').addClass('d-none');
      
      update_modal('get_start')
    }, 1000);

    progress_span.innerHTML = 'remove loading.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    start_carousel()

    progress_span.innerHTML = 'start info carroucel.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    progress_span.innerHTML = 'Finish start.'
    functionsExecuted++;
    progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

    $("#tags").on("click", "p", function() {
      $(this).remove(); 
    });
    

  }

});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function start_selectpicker(){
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
}
function start_carousel(){

  const carousel = document.querySelector('.carousel');
  const flkty = new Flickity(carousel, {
    contain: true,
    wrapAround: true,
    autoPlay: true,
    prevNextButtons: false,
    pageDots: false,
    setGallerySize: false
  });
}
function start_scroll(){

  const scrollToBottomButton = document.querySelector("#scrollBtn");
  const chatWindow = document.getElementById("chat-block-inner");


  scrollToBottomButton.addEventListener("click", () => {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });


  chatWindow.addEventListener("scroll", () => {
    if (chatWindow.scrollTop < chatWindow.scrollHeight - chatWindow.clientHeight) {
      scrollToBottomButton.classList.add("show");
    } else {
      scrollToBottomButton.classList.remove("show");
    }
  });


  const scrollToBottomButtontwo = document.querySelector("#scrollBtntwo");
  const chatWindowtwo = document.getElementById("chat-block-inner-two");


  scrollToBottomButtontwo.addEventListener("click", () => {
    chatWindowtwo.scrollTop = chatWindowtwo.scrollHeight;
  });

  chatWindowtwo.addEventListener("scroll", () => {
    if (chatWindowtwo.scrollTop < chatWindowtwo.scrollHeight - chatWindowtwo.clientHeight) {
      scrollToBottomButtontwo.classList.add("show");
    } else {
      scrollToBottomButtontwo.classList.remove("show");
    }
  });


  const scrollToBottomButtonthree = document.querySelector("#scrollBtnthree");
  const chatWindowthree = document.getElementById("chat-block-inner-three");


  scrollToBottomButtonthree.addEventListener("click", () => {
    chatWindowthree.scrollTop = chatWindowthree.scrollHeight;
  });


  chatWindow.addEventListener("scroll", () => {
    if (chatWindowthree.scrollTop < chatWindowthree.scrollHeight - chatWindowthree.clientHeight) {
      scrollToBottomButtonthree.classList.add("show");
    } else {
      scrollToBottomButtonthree.classList.remove("show");
    }
  });

}

function start_sidebar(){
  const hoverDiv = document.querySelector('#sidebarMenu');
  const showDiv = document.querySelector('#sidebarMenu-hidden');
  
  function show_navbar(type_id){
    if(type_id == 'show'){
      showDiv.classList.add('sidebarMenu-show');
    } else if (type_id == 'hidden'){
      showDiv.classList.remove('sidebarMenu-show');
    }
  }
  
  hoverDiv.addEventListener('mouseenter',() => {
    show_navbar('show');
  });

  showDiv.addEventListener('mouseleave',() => {
    show_navbar('hidden');
  });

}

function start_resizable(){

  $('#events-col').resizable({
    handles: 'e',
    resize: function(event, ui) {

      var largura2 = 100 - (ui.size.width / $(this).parent().width() * 100);
  
      var chat_col = $('#chat-col');
      chat_col.css('width', largura2 + '%');
    }
  });

  $('#user-list-side').resizable({
    handles: 'e',
    resize: function(event, ui) {

      var largura_side = 100 - (ui.size.width / $(this).parent().width() * 100);
  
      var chat_col_side = $('#chat-list-side');
      chat_col_side.css('width', largura_side + '%');
    }
  });

  $('#colapse-recent').resizable({
    handles: 's'
  });


  $("#user-list-inner").resizable({
    handles: "s",
    minHeight: "20%",
    maxHeight: "80%",
    containment: "#chat-list",
    alsoResize: false,
    start: function(event, ui) {
      var userHeight = ui.size.height;
      var chatHeight = $(this).parent().height() - userHeight;
      $("#chat-list-inner").height(chatHeight);
      $('#user-list-inner').css('width', '100%');
    },
    resize: function(event, ui) {
      var userHeight = ui.size.height;
      var chatHeight = $(this).parent().height() - userHeight;
      
      $("#chat-list-inner").height(chatHeight);
      $('#user-list-inner').css('width', '100%');

    },
    stop: function(event, ui) {
      $('#user-list-inner').css('width', '100%');
    }
  });
  
}

function receive_live_info(data){

    document.getElementById('text-counter').innerText = " " + data.specs;
    document.getElementById('time-in-live').innerText = data.time;

    if (data.specs != 'Offline'){
        document.getElementById('live-dot').style.color = 'red';
    }
}


async function start_profile_info(){

  profile_info = await window.pywebview.api.profile_info();

    if (profile_info){

      profile_info = JSON.parse(profile_info)

      var profile_image = document.getElementById("profile_image");
      var profile_image_new = profile_image.src;
      profile_image.src = profile_image_new; 

      document.getElementById('email').innerText = profile_info.email;;
      document.getElementById('user_id').innerText = profile_info.user_id;
      document.getElementById('ex_name').innerText = profile_info.display_name;
      document.getElementById('login_name').innerText = profile_info.login_name;
    }
    
};

async function create_clip() {
  var buttom_clip = document.getElementById('create-clip');
  window.pywebview.api.clip()
  buttom_clip.disabled = true;
  buttom_clip.classList.add('disabled');
  await sleep(5000)
  buttom_clip.disabled = false;
  buttom_clip.classList.remove('disabled');
}

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
  window.pywebview.api.logout_auth()
}

async function disclosure(event,type_id){

  if (type_id == 'save'){

      event.preventDefault()

      var form_disclosure = document.querySelector('#form-disclosure');
      var disclosure = form_disclosure.querySelector('#message-disclosure-send').value;
      var button_copy = document.getElementById("copy-dis");
      var button_save = document.getElementById("submit-message-disclosure");
    
      window.pywebview.api.disclosure_py(type_id,disclosure);
    
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

async function update_modal(type_id){

  if (type_id == 'get'){

    var status = await window.pywebview.api.update_check('check');

    if(status){
      
      if (status != 'false'){

        var repoOwner = 'GGTEC'
        var repoName = 'RewardEvents'

        fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`)
        .then(response => response.json())
        .then(data => {

          let releasesList = document.querySelector("#update_body");

          if (releasesList != undefined){
            
            const firstRelease = data; // Obter o primeiro item da lista
            
            const converter = new showdown.Converter()

            var html_release = converter.makeHtml(firstRelease.body);

            let releaseEl = document.createElement("div");

            releaseEl.classList.add('version_block')
            releaseEl.innerHTML = `
              <p>Versão: ${firstRelease.tag_name}</p>
              <p class='version_text'>${html_release}</p>
            `;

            releasesList.appendChild(releaseEl);
          }
          
        })
        .catch(error => console.error(error));


        $("#update-modal").modal("show");

      } else {
        document.getElementById('no-update').hidden = false
      }
    }

  } else if (type_id == 'get_start'){

    var status = await window.pywebview.api.update_check('check');

    if(status){
      
      if (status != 'false'){

        var repoOwner = 'GGTEC'
        var repoName = 'RewardEvents'

        fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`)
        .then(response => response.json())
        .then(data => {

          let releasesList = document.querySelector("#update_body");

          if (releasesList != undefined){
            
            const firstRelease = data; // Obter o primeiro item da lista
            
            const converter = new showdown.Converter()

            var html_release = converter.makeHtml(firstRelease.body);

            let releaseEl = document.createElement("div");

            releaseEl.classList.add('version_block')
            releaseEl.innerHTML = `
              <p>Versão: ${firstRelease.tag_name}</p>
              <p class='version_text'>${html_release}</p>
            `;

            releasesList.appendChild(releaseEl);
          }
          
        })
        .catch(error => console.error(error));


        $("#update-modal").modal("show");

      }
    }

  } else if (type_id == 'open'){
    window.pywebview.api.update_check('open');
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

function update_div_redeem(data_redem_parse) {

    var image_redeem = document.getElementById("image_redeem");
    var name_redeem = document.getElementById("name_redeem");
    var user_redeem = document.getElementById("user_redeem");

    if (data_redem_parse.redeem_image != 'None'){
      image_redeem.src = data_redem_parse.redeem_image
    }
    name_redeem.innerText = data_redem_parse.redeem_name
    user_redeem.innerText = data_redem_parse.redeem_user
}


async function getFolder(id,type_id) {
  var dosya_path = await window.pywebview.api.select_file_py(type_id);
  if (dosya_path) {
      document.getElementById(id).value = dosya_path;
      if (id == 'file-select-notific'){
          chat_config('save')
      }
  }
}

const div_events_scroll = document.getElementById("div-events");

const itensPorPagina = 10;
let paginaAtual = 1;

div_events_scroll.addEventListener("scroll",async function() {

  if (div_events_scroll.scrollTop + div_events_scroll.clientHeight >= div_events_scroll.scrollHeight) {

    var list_messages_parse = await window.pywebview.api.event_log('get', 'null');

    if (list_messages_parse) {

      list_messages_parse = JSON.parse(list_messages_parse);
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


let mode = 0
function mode_change(){
  
  var tabs = document.getElementById('nav-tabContent');
  var chat_list = document.getElementById('chat-list');
  var side_side = document.getElementById('chat-side');

  var chat_button = document.getElementById('nav-chat-tab');
  var user_list_button = document.getElementById('nav-users-tab');

  if(mode == 2){

    tabs.hidden = false
    chat_list.hidden = true
    side_side.hidden = true

    chat_button.hidden = false
    user_list_button.hidden = false

    mode = 0

  } else if(mode == 0){

    tabs.hidden = true
    chat_list.hidden = false
    side_side.hidden = true

    chat_button.hidden = true
    user_list_button.hidden = true
    mode = 1

  } else if(mode == 1){
    
    tabs.hidden = true
    chat_list.hidden = true
    side_side.hidden = false

    chat_button.hidden = true
    user_list_button.hidden = true
    mode = 2

  }
}


function openNav() {
  document.getElementById("sidebarMenu").style.width = "20%";
}

/* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
function closeNav() {
  document.getElementById("sidebarMenu").style.width = "0";
}