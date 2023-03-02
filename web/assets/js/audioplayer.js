function update_image(){
    var player_img = document.getElementById('song-img');
    player_img.style.backgroundImage = "linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.7483368347338936) 89%, rgba(0,0,0,1) 100%),url('/src/player/images/album.png?noCache=" + Math.floor(Math.random() * 1000000)+")";
  }
  
  eel.expose(update_music_name);
  function update_music_name(name,artist){
  
  
    var player_music_name = document.getElementById('music-name');
    var player_artist_name = document.getElementById('music-artist');
  
    player_artist_name.innerHTML = artist;
    player_music_name.innerHTML = name;
  
  }
  
  const player_id = new Plyr('#player', {
    settings: ['']
  });
  
  
  async function list_modal(){
  
    $("#list-mod").modal("show");
  
    var list = await eel.list_queue()();
  
    if (list){
  
      list_parse = JSON.parse(list);
  
      var tbody = document.getElementById('list-body');
  
      tbody.innerHTML = '';
  
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
  
    console.log(playlist_url)
  
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
  
    if(event_type == 'play'){
  
      player_id.stop();
  
      update_image()
  
      player_id.source = {
        type: 'audio',
        sources: [
          {
            src: music_src + '?noCache=' + Math.floor(Math.random() * 1000000),
            type: 'audio/mp3',
          },
        ],
  
      }
    
      player_id.play();
  
    } else if (event_type == 'stop'){
  
      player_id.stop();
  
    } else if (event_type == 'volume'){
  
      player_id.volume = volume
  
    } else if (event_type == 'get_volume'){
  
      var vol_atual = Math.trunc( player_id.volume * 100 ) 
      
      return vol_atual
  
    } else if (event_type == 'playing'){
  
      if (player_id.playing == true ){
  
        return 'True'
  
      } else {
  
        return 'False'
  
      }
    }
  }