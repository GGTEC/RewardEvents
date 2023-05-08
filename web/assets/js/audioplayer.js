
function update_image(){
    var player_img = document.getElementById('song-img');
    player_img.style.backgroundImage = `linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.7483368347338936) 89%, rgba(0,0,0,1) 100%),url('/src/player/images/album.png?noCache=` + Math.floor(Math.random() * 1000000)+")";
}

function update_music_name(name,artist){


  var player_music_name = document.getElementById('music-name');
  var player_artist_name = document.getElementById('music-artist');

  player_artist_name.innerHTML = artist;
  player_music_name.innerHTML = name;

}

const player_id = new Plyr('#player', {
  settings: ['']
});

async function playlist_js(event,type_id){

    if (type_id == "add"){

      event.preventDefault();

      var form_playlist = document.querySelector('#playlist-add-form');
      var playlist_url = form_playlist.querySelector('#playlist-url').value;
    
      window.pywebview.api.playlist_py('add',playlist_url)

    } else if (type_id == "save"){

      event.preventDefault();

      var switch_value_playlist = document.getElementById('playlist-switch');
  
      value = switch_value_playlist.checked ? 1 : 0;
      
      window.pywebview.api.playlist_py('save',value)

    } else if (type_id == "get"){

      var switch_value = document.getElementById('playlist-switch');
  
      var status = await window.pywebview.api.playlist_py('get','null')
    
      if (status){

        switch_value.checked = status ? true : false

      }

      $("#playlist-mod").modal("show");
      
    } else if (type_id == "clear"){

      window.pywebview.api.playlist_py("clear","null")

      $("#playlist-mod").modal("hide");

    } else if (type_id == "queue"){
  
      var list_parse = await window.pywebview.api.playlist_py('queue',"null");
    
      if (list_parse){
        
        list_parse = JSON.parse(list_parse)
        var tbody = document.getElementById('list-body');
    
        tbody.innerHTML = '';
    
        Object.entries(list_parse).forEach(([k,v]) => {
    
          var k = k.slice(0,50);
          
          tbody.innerHTML += '<tr><td>' + k + '</td><td>' + v + '</td></tr>';
    
        })
      }

      $("#list-mod").modal("show");

    } else if (type_id == "queue_add"){

      var music_name_playlist = document.getElementById('playlist-music-added');
      music_name_playlist.innerHTML = event

    } else if (type_id == "queue_close"){

      var music_name_playlist = document.getElementById('playlist-music-added');
      music_name_playlist.innerHTML = ''
      $("#playlist-mod").modal("hide");

    }

}

function player(event_type,music_src,volume){

  if(event_type == 'play'){

    player_id.stop();

    player_id.source = {
      type: 'audio',
      sources: [
        {
          src: music_src + '?noCache=' + Math.floor(Math.random() * 1000000),
          type: 'audio/webm',
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