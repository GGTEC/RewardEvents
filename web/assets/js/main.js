$(document).ready(function () {

  eel.loaded()();
  updateTimeDiff()
  prediction_small()
  poll_small()
  update_timer_small()
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
  

});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

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

eel.expose(last_command);
function last_command(command){

  var command_text = document.getElementById('last_command_text');

  command_text.innerHTML = command

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
