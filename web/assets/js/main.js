

$(function() {
  $('audio').audioPlayer();
});

$(document).ready(function () {

  $("input, select, textarea").attr("autocomplete", "off");
  $("input, select, textarea").attr("spellcheck", "false");
  $('select').selectpicker({
    liveSearch: true,
    showSubtext: true,
    size: 5,
    width: '100%',
    style: 'btn-dark',
    noneResultsText: "Nenhum resultado para {0}",
    liveSearchPlaceholder: "Pesquise o item"
  });

});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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
    document.getElementById('obs_retry_button').style.display = 'None'
  } else if (type_id == 'error'){
    document.getElementById('obs_conn_status').innerHTML = 'Desconectado'
    document.getElementById('obs_retry_button').style.display = 'inline-block'
  }
}

function try_obs(){
  document.getElementById('obs_conn_status').innerHTML = 'Conectando...'
  document.getElementById('obs_retry_button').style.display = 'None'
  eel.obs_try_conn();
}

function send_message_chat_js(event){

  event.preventDefault()

  var form_message = document.querySelector('#input-chat-form');
  var message = form_message.querySelector('#message-chat-send').value;

  console.log(message)
  eel.send_message_chat(message);

  document.getElementById('message-chat-send').value = "";

}

async function save_message_disclosure(event){

  event.preventDefault()

  var form_disclosure = document.querySelector('#form-disclosure');
  var disclosure = form_disclosure.querySelector('#message-disclosure-send').value;

  eel.save_disclosure(disclosure);

  document.getElementById('message-disclosure-send').value = 'Salvo!';

  await sleep(3000)

  document.getElementById('message-disclosure-send').value = disclosure;

}

async function copy_message_disclosure() {

  var copyText = document.getElementById("message-disclosure-send");

  var saved_message = copyText.value
  copyText.select(); 

  navigator.clipboard.writeText(copyText.value);

  document.getElementById('message-disclosure-send').value = 'Copiado para a Clipboard!';

  await sleep(3000)

  document.getElementById('message-disclosure-send').value = saved_message;

}

eel.expose(last_command);
function last_command(command){

  var command_text = document.getElementById('last_command_text');

  command_text.innerHTML = command

}

async function save_music_status(type_id){

  var check_seletor = document.getElementById('music-enable');

  if (type_id == 'save'){

    if (check_seletor.checked == true){

        eel.music_status_save(1,'save')
    } else if (check_seletor.checked == false) {

        eel.music_status_save(0,'save')
    }

  } else if (type_id == 'get'){

    var value = await eel.music_status_save('null','get')();

    if (value){

    if (value == 1){
      check_seletor.checked = true
    } else {
      check_seletor.checked = false
    }

    }

  }


}

function update_image(){
  var player_img = document.getElementsByClassName('song-img')[0];
  player_img.style.backgroundImage = "url('/src/player/images/album.png?noCache=" + Math.floor(Math.random() * 1000000)+")";
}

eel.expose(update_music_name);
function update_music_name(name,artist){
  var player_music_name = document.getElementsByClassName('music-name')[0];
  var player_artist_name = document.getElementsByClassName('music-artist')[0];

  player_artist_name.innerHTML = artist;
  player_music_name.innerHTML = name;
}

function play_pause(){

  var player_id = document.getElementById('player');

  if (player_id.currentTime == player_id.duration){
    player_id.play()
  }
}

function player_stop(){
  var player_id = document.getElementById('player');
  player_id.pause();
  player_id.currentTime = 0;
}

async function list_modal(){

  $("#list-mod").modal("show");

  var list = await eel.list_queue()();

  if (list){

    list_parse = JSON.parse(list);

    var tbody = document.getElementById('list-body');

    Object.entries(list_parse).forEach(([k,v]) => {

      tbody.innerHTML += '<tr><td>' + k + '</td><td>' + v + '</td></tr>';

    })
  }
}

async function playlist_modal(){
  $("#playlist-mod").modal("show");

  var switch_value = document.getElementById('playlist-switch');

  var status = await eel.playlist_execute_save('none','get')()

  if (status){

    if (status == 1){ 

      switch_value.checked = true;

    } else if (status == 0){

      switch_value.checked = false;

    }
  }
}

function playlist_add(event){

  event.preventDefault();

  var form_playlist = document.querySelector('#playlist-add-form');
  var playlist_url = form_playlist.querySelector('#playlist-url').value;

  eel.add_playlist(playlist_url)

}

function playlist_execute(){

  var switch_value_playlist = document.getElementById('playlist-switch');
  
  console.log(switch_value_playlist.checked)

  if (switch_value_playlist.checked == true){

    value = 1;

  } else if (switch_value_playlist.checked == false){

    value = 0;

  }
  
  eel.playlist_execute_save(value,'save')
}

eel.expose(playlist_stats_music);
function playlist_stats_music(name,type_id){

  var music_name_playlist = document.getElementById('playlist-music-added');

  if (type_id == "Add"){

    music_name_playlist.innerHTML = name

  } else if (type_id == "Close"){

    music_name_playlist.innerHTML = ''

    $("#playlist-mod").modal("hide");

  }

}

function playlist_clear(){
  eel.playlist_clear_py()
  $("#playlist-mod").modal("hide");
}

eel.expose(player);
function player(event_type,music_src,volume){

  var player_id = document.getElementById('player');
  
  if(event_type == 'play'){

    player_id.pause();

    update_image()

    $("#player").attr("src", music_src + '?noCache=' + Math.floor(Math.random() * 1000000))
  
    player_id.load();
    player_id.play();

  } else if (event_type == 'stop'){

    player_id.pause();
    player_id.currentTime = 0;

  } else if (event_type == 'volume'){

    player_id.volume = volume

  } else if (event_type == 'playing'){

    if (player_id.paused == true && player_id.ended == false && player_id.currentTime == 0){

      return 'False'

    } else if (player_id.paused == false && player_id.ended == false && player_id.currentTime > 0){

      return 'True'
      
    } else if (player_id.paused == true && player_id.ended == false && player_id.currentTime > 0){

      return 'True'

    } else if (player_id.paused == true && player_id.ended == true && player_id.currentTime == player_id.duration){

      return 'False'
    }
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

