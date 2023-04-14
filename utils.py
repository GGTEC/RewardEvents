import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta
import pytz

import coverpy
import requests
from pytube import YouTube
from bs4 import BeautifulSoup as bs
from dateutil import tz
from PIL import Image
from random import randint

import urllib.request
import zipfile
import tempfile

import tkinter.messagebox as messagebox

coverpy = coverpy.CoverPy()

extDataDir = os.getcwd()

appdata_path = os.getenv('APPDATA')

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS

def find_between( s, first, last ):

    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    
    except ValueError:
        
        return False

def calculate_time(started):
    
    try:
        
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_date = datetime.fromisoformat(started).replace(tzinfo=pytz.utc)

        gmt_minus_3_now = utc_now.astimezone(pytz.timezone("Etc/GMT+3"))
        gmt_minus_3_date = utc_date.astimezone(pytz.timezone("Etc/GMT+3"))
        

        difference = gmt_minus_3_now - gmt_minus_3_date
    
        days = difference.days
        hours = difference.seconds//3600
        minutes = (difference.seconds//60)%60
        sec = difference.seconds%60
        
        time_in_live = {
            'days' : str(days),
            'hours': str(hours),
            'minutes': str(minutes),
            'sec': str(sec)
        }

        return time_in_live

    except Exception as e:

        error_log(e)

        return 'none'

def error_log(ex):

    now = datetime.now()
    time_error = now.strftime("%d/%m/%Y %H:%M:%S")

    trace = []
    tb = ex.__traceback__

    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "lineno": tb.tb_lineno
        })
        tb = tb.tb_next

    error = str(f'Erro = type: {type(ex).__name__} | message: {str(ex)} | trace: {trace} | time: {time_error} \n')

    with open(f"{appdata_path}/rewardevents/web/src/error_log.txt", "a+", encoding='utf-8') as log_file_r:
        log_file_r.write(error)

def removestring(value):
    try:
        simbolos = [['[', ']'], ['(', ')'], ['"', '"']]
        for simbolo in simbolos:
            if value.find(simbolo[0]) and value.find(simbolo[1]):
                value = value.replace(value[(indice := value.find(simbolo[0])):value.find(simbolo[1], indice + 1) + 1],
                                    '').strip()
                
        return value
    except:
        return value

def album_search(title,user_input):
    
    user_input = user_input.strip()
    
    music = '0'
    artist = '0'
    url_youtube = "0"
    success = 0

    try:
        url_youtube = user_input
        rep_input = removestring(title)

        try:
            
            result = coverpy.get_cover(rep_input, 1)
            album_art = result.artwork(625)

            img_data = requests.get(album_art).content

            with open(f'{extDataDir}/web/src/player/images/album.png', 'wb') as album_art_local:
                album_art_local.write(img_data)
        
        except:

            yt = YouTube(url_youtube)
            thumb_link = yt.thumbnail_url
            img_data = requests.get(thumb_link).content
            
            with open(f'{extDataDir}/web/src/player/images/album.png', 'wb') as album_art_local:
                album_art_local.write(img_data)

        success = 1
        
        try:
            
            title_split = rep_input.split(' - ')
            artist = title_split[0]
            music = title_split[1]
        
        except Exception as e:

            music = rep_input
            artist = '0'

    except Exception as e:
        error_log(e)
        success = 0


    response_albumart = {
        
        "music" : music,
        "artist" : artist,
        "link" : url_youtube,
        "success" : success
    }

    return response_albumart

def check_delay(delay_command,last_use):
    
    with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', "r", encoding='utf-8')  as messages_file:
        messages_data = json.load(messages_file) 

    message_error = messages_data['response_delay_error']

    last_command_time = last_use
    delay_compare = int(delay_command)
    
    current_time = int(time.time())

    if current_time >= last_command_time + delay_compare:

        message = 'OK'
        value = True
        
        return message, value, current_time
    
    else:
        
        remaining_time = last_command_time + delay_compare - current_time
    
        message = message_error.replace('{seconds}', str(remaining_time))
        value = False
        current_time = ''
        
        return message, value, current_time
    
def check_delay_duel(delay_command,last_use):
    
    last_command_time = last_use
    delay_compare = int(delay_command)
    
    current_time = int(time.time())

    if current_time >= last_command_time + delay_compare:

        message = 'OK'
        value = True
        
        return message, value, current_time
    
    else:
        
        remaining_time = last_command_time + delay_compare - current_time
    
        value = False
        current_time = ''
        
        return remaining_time, value, current_time

def send_message(type_message):
    
    try:
        with open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json') as status_commands_check:
            status_commands_data = json.load(status_commands_check)
        
        status_error_time = status_commands_data['STATUS_ERROR_TIME']
        status_error_user = status_commands_data['STATUS_ERROR_USER']
        status_response = status_commands_data['STATUS_RESPONSE']
        status_clip = status_commands_data['STATUS_CLIP']
        status_tts = status_commands_data['STATUS_TTS']
        status_timer = status_commands_data['STATUS_TIMER']
        status_music = status_commands_data['STATUS_MUSIC']
        status_music_error = status_commands_data['STATUS_MUSIC_ERROR']
        status_music_confirm = status_commands_data['STATUS_MUSIC_CONFIRM']

        if type_message == 'CHAT':
                return True
        
        elif type_message == 'ERROR_TIME':
            
            if status_error_time == 1:
                return True
                    
        elif type_message == 'RESPONSE':

            if status_response == 1:
                return True
                
        elif type_message == 'ERROR_USER':
            
            if status_error_user == 1:
                return True
                    
        elif type_message == 'CLIP':
            
            if status_clip == 1:
                return True
                    
        elif type_message == 'STATUS_TTS':
            
            if status_tts == 1:
                return True
                
        elif type_message == 'TIMER':
            
            if status_timer == 1:
                return True

        elif type_message == 'STATUS_MUSIC':
            
            if status_music == 1:
                return True
                
        elif type_message == 'STATUS_MUSIC_CONFIRM':
            
            if status_music_confirm == 1:
                return True
                
        elif type_message == 'STATUS_MUSIC_ERROR':
            
            if status_music_error == 1:
                return True
        


    except Exception as e:
        error_log(e)
 
def copy_file(source, dest):
    copy = 0
    
    try:

        shutil.copy2(source, dest)

    except Exception as e:

        error_log(e)
        copy = 1
        return copy
    
    copy = 1
    return copy
    
def update_notif(data,type_not):

    redeem = data['redeem_name']
    user = data['redeem_user']
    artist = data['artist']
    music = data['music']


    html_backup = f"{appdata_path}/rewardevents/web/src/html/notification/notification.html.tmp"
    html_file = f"{appdata_path}/rewardevents/web/src/html/notification/notification.html"

    try:
        os.remove(html_file)
    
        with open(html_backup, "r") as html:
            soup = bs(html, 'html.parser')

        redeem_block = soup.find("div", {"class": "col-6 redem_block"})
        music_block = soup.find("div", {"class": "col-7 music_block"})

        if type_not == 'redeem':
            
            redeem_src = "../Request.png"
            music_block['style'] = 'display: none !important;'
            redeem_block['style'] = 'display: block;'
            
            image_redeem = soup.find("img", {"class": "img-responsive"})
            redeem_name_tag = soup.find("span", {"class": "redem_name"})
            redeem_user_tag = soup.find("span", {"class": "redem_user"})

            image_redeem['src'] = redeem_src
            redeem_name_tag.string = redeem
            redeem_user_tag.string = user
                        
        elif type_not == 'music':

            album_src = "../player/images/album.png"
            music_block['style'] = 'display: block ;'
            redeem_block['style'] = 'display: none !important;'
            
            image_redeem = soup.find("img", {"class": "img-responsive"})
            music_name_tag = soup.find("span", {"class": "music_name"})
            artist_name_tag = soup.find("span", {"class": "artist_name"})
            redeem_user_music_tag = soup.find("span", {"class": "redem_user_music"})

            image_redeem['src'] = album_src
            music_name_tag.string = music
            artist_name_tag.string = artist
            redeem_user_music_tag.string = user
                
        with open(html_file, "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))

        return True

    except Exception as e:
        error_log(e)

        return True
      
def update_video(video):
    
    html_video_backup = f"{appdata_path}/rewardevents/web/src/html/video/video.html.tmp"
    html_video_file = f"{appdata_path}/rewardevents/web/src/html/video/video.html"

    try:

        with open(html_video_backup, "r") as html:
            soup = bs(html, 'html.parser')

        video_div = soup.find("div", {"id": "video_div"})
        gif_div = soup.find("div", {"id": "gif_div"})

        if video.endswith('.gif'):

            video_div['style'] = 'display: none !important;'
            gif_div['style'] = 'display: block;'

            video_redeem = soup.find("img")
            video_redeem['src'] = 'http://absolute/' + video
        
        else:

            gif_div['style'] = 'display: none !important;'
            video_div['style'] = 'display: block;'

            video_redeem = soup.find("video")
            video_redeem['src'] = 'http://absolute/' + video
               
        with open(html_video_file, "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))

        return True


    except Exception as e:

        error_log(e)

        return True

def update_event(data):
    
    html_event_backup = f"{appdata_path}/rewardevents/web/src/html/event/event.html.tmp"
    html_event_file = f"{appdata_path}/rewardevents/web/src/html/event/event.html"
    
    type_id = data['type_id']
    image_src = data['img_src']
    img_px = data['img_px']
    response_px = data['response_px']
    duration = int(data['duration']) - 1
    image_above = data['image_above']	
    audio_src = data['audio_src']
    audio_volume = data['audio_volume']
    tts_src = f'{appdata_path}/rewardevents/web/src/player/cache/tts.mp3'
    play_tts = data['play_tts']
    color_highligh = data['color']
    font_weight = data['weight']
    
    html_event_style_path = f"event_styles/{type_id}.css"

    audio_volume = int(audio_volume)/100
    
    message = data['message']
    username = data['username']

    username_replace = f"<span id='username' style='color:{color_highligh};font-weight:{font_weight}'>{username}</span>"

    message = message.replace(username,username_replace)

    message_soup = bs(message, 'html.parser')
    
    try:

        with open(html_event_backup, "r",encoding='utf-8') as html:
            soup = bs(html, 'html.parser')

        # Encontre todas as tags <link> que referenciam folhas de estilo CSS
        link_tags = soup.find_all('link', rel='stylesheet')

        # Altere o atributo href da segunda tag <link> para apontar para o novo arquivo CSS
        link_tags[1]['href'] = html_event_style_path

        audio_tag = soup.find("input", {"id": "path_audio1"})
        audio_tag['value'] = f'http://absolute/{audio_src}'

        audio2_tag = soup.find("input", {"id": "path_audio2"})
        
        if play_tts == 0:
            audio2_tag['value'] = f''
        else:
            audio2_tag['value'] = f'http://absolute/{tts_src}'
            
        volume_tag = soup.find("input", {"id": "volume"})
        volume_tag['value'] = audio_volume
    
        if image_above == 0: 
            type_div = "above"
        else:
            type_div = "over"

        main_div = soup.find("div", {"id": f"main_div_{type_div}"})
        main_div['style'] = f'animation-duration: {duration}s'

        img_source = soup.find("img" ,{"id":f"img_{type_div}"})
        img_source['src'] = 'http://absolute/' + image_src
        img_source['style'] = f'width: {img_px}px;'

        message_tag = soup.find("p", {"id": f"message-{type_div}"})
        message_tag['style'] = f'font-size: {response_px}px;'
        message_tag.string = ""
        message_tag.insert(1,message_soup)


        with open(html_event_file, "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))

        return True
            
    except Exception as e:
        error_log(e)

        return False

def update_highlight(data):
    
    html_highlight_backup = f"{appdata_path}/rewardevents/web/src/html/highlight/highlight.html.tmp"
    html_highlight_file = f"{appdata_path}/rewardevents/web/src/html/highlight/highlight.html"
    
    duration = int(data['duration']) - 1

    color_highligh_username = data['color_username']
    color_highligh_message = data['color_message']
    font_weight = data['weight']
    font_size = data['size']
    
    message = data['user_input']
    username = data['username']

    try:

        with open(html_highlight_backup, "r",encoding='utf-8') as html:
            soup = bs(html, 'html.parser')

        main_div = soup.find("div", {"id": f"highlight-block"})
        main_div['style'] = f'animation-duration: {duration}s'

        username_tag = soup.find("span", {"id": f"username"})
        username_tag['style'] = f'font-size: {font_size};font-weight: {font_weight};color: {color_highligh_username};'
        username_tag.string = username

        message_tag = soup.find("span", {"id": f"message"})
        message_tag['style'] = f'font-size: {font_size};font-weight: {font_weight};color: {color_highligh_message};'
        message_tag.string = message

        with open(html_highlight_file, "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))

        return True
            
    except Exception as e:
        
        error_log(e)
        return False

def update_emote(data):

    with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding='utf-8') as obs_not_file:
        obs_not_data = json.load(obs_not_file)

    width = obs_not_data['EMOTE_PX']
    height = obs_not_data['EMOTE_PX']

    html_emote_backup = f"{appdata_path}/rewardevents/web/src/html/emote/emote.html.tmp"
    html_emote_file = f"{appdata_path}/rewardevents/web/src/html/emote/emote.html"

    try:

        with open(html_emote_backup, "r",encoding='utf-8') as html:
            soup = bs(html, 'html.parser')

        main_div = soup.find("div", {"id": f"emojis"})
        
        

        for emote in data:

            random = randint(0,5)
            element = bs(emote, 'html.parser')
            element_style = element.find("img", {"class": f"emoji"})
            element_style['style'] = f'width:{width}px;height:{height}px;animation-delay:{random}s'
            main_div.append(element)

        with open(html_emote_file, "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))

        return True
            
    except Exception as e:
        
        error_log(e)
        return False

def replace_all(text, dic_res):
    
    try:
        for i, j in dic_res.items():
            text = text.replace(i, j)

        return text
    
    except Exception as e:
        error_log(e)
        
        return ''

def messages_file_load(key):
    
    with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', "r", encoding='utf-8') as messages_file:
        messages_data = json.load(messages_file)

    message = messages_data[key]

    return message
 
def get_files_list():
    
    dir = f"{appdata_path}/rewardevents/web/src/auth"
    dir1 = f"{appdata_path}/rewardevents/"

    if not os.path.exists(dir):

        os.makedirs(dir1)

        is_writable = os.access(dir1, os.W_OK)

        if not is_writable:
            os.chmod(dir1, 0o700)
            is_writable = os.access(dir1, os.W_OK)

        if is_writable:

            url = "https://ggtec.github.io/GGTECApps/assets/web.zip"

            zip_path = f"{appdata_path}/rewardevents/web.zip"
            unzip_path = f"{appdata_path}/rewardevents"

            # Baixar o arquivo zip
            urllib.request.urlretrieve(url, zip_path)


            if os.path.exists(zip_path):

                with tempfile.TemporaryDirectory() as temp_dir:

                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    extracted_dir = os.path.join(temp_dir, "web")

                    if os.path.exists(extracted_dir):
                        shutil.move(extracted_dir, unzip_path)
                        os.remove(zip_path)

                    else:
                        print("Diretório extraído não encontrado:", extracted_dir)
            else:
                print("Extração do arquivo zip falhou:", zip_path)
        else:
            print("Não foi possível conceder permissão para escrever na pasta:", dir1)


    else:

        try:

            response = requests.get('https://api.twitchinsights.net/v1/bots/all')

            data = json.loads(response.text)
            data_save = []
            data = data['bots']

            for idx, i in enumerate(data):
                name = data[idx][0]
                data_save.append(name)

            with open(f"{appdata_path}/rewardevents/web/src/user_info/bot_list.json", "w") as outfile:
                json.dump(data_save, outfile,indent=6)

            respo_tags = requests.get("https://ggtec.github.io/list_games_tags_tw/tags.json")
            data_save_tags = json.loads(respo_tags.text)

            with open(f'{appdata_path}/rewardevents/web/src/games/tags.json', "w" , encoding="UTF-8") as tags_file:
                json.dump(data_save_tags,tags_file,indent=4,ensure_ascii=False)

            respo_games = requests.get("https://ggtec.github.io/list_games_tags_tw/games.json")
            data_save_games = json.loads(respo_games.text)

            with open(f'{appdata_path}/rewardevents/web/src/games/games.json', "w" , encoding="UTF-8") as games_file:
                json.dump(data_save_games,games_file,indent=4,ensure_ascii=False)

        except Exception as e:

            if type(e).__name__ ==  "ConnectionError":

                ask = messagebox.showerror("Erro", "Erro de conexão, verifique a conexão com a internet e tente novamente.")
            
                if ask == 'ok':
                    sys.exit(0)

            else:

                error_log(e)
        
        with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'r', encoding='utf-8') as poll_file:
            poll_data = json.load(poll_file)

            if poll_data["status"] == "":

                poll_data["status"] = "archived"

                with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'w', encoding='utf-8') as poll_file:
                    json.dump(poll_data, poll_file, indent=6, ensure_ascii=False)  

        with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', "r", encoding='utf-8') as messages_file:
            messages_data = json.load(messages_file)

            messages_data['emote_disabled'] = '/me O sistema de emotes está desativado'
            messages_data['response_get_queue'] = '/me {username} --> Estes valores estão na lista {queue-3}'
            messages_data['response_noname_queue'] = '/me O Nome {value} não está na fila'
            messages_data['response_rem_queue'] = '/me Nome {value} removido da fila'
            messages_data['response_namein_queue'] = '/me O Nome {value} já está na fila'
            messages_data['response_add_queue'] = '/me Nome {value} adicionado na fila'
            messages_data['response_queue'] = 'me {username} --> Você foi adicionado na fila de espera.'

        with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', "w", encoding='utf-8') as messages_file:
            json.dump(messages_data, messages_file, indent=6, ensure_ascii=False)  

        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', "r", encoding='utf-8') as commands_file:
            commands_data = json.load(commands_file)

            commands_data['emote'] = {
                "command": "!emote",
                "status": 1,
                "delay": "10",
                "last_use": 0,
                "response": "/me {username} --> Exibindo emotes na tela",
                "user_level": "mod"
            }

        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', "w", encoding='utf-8') as commands_file:
            json.dump(commands_data, commands_file, indent=6, ensure_ascii=False)  

        path_css = f'{appdata_path}/rewardevents/web/src/html/emote/emote.css'
        path_js = f'{appdata_path}/rewardevents/web/src/html/emote/emote.js'
        path_html = f'{appdata_path}/rewardevents/web/src/html/emote/emote.html'
        path_html_bk = f'{appdata_path}/rewardevents/web/src/html/emote/emote.html.tmp'

        dir_emote = f'{appdata_path}/rewardevents/web/src/html/emote'

        if not os.path.exists(path_html):
            
            os.makedirs(dir_emote)

            content = """
                <!DOCTYPE html>
                <html lang="pt-br">
                <head>
                <link href="emote.css" rel="stylesheet"/>
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet"/>
                <link href="https://fonts.googleapis.com/css?family=Kanit" rel="stylesheet"/>
                <meta charset="utf-8"/>
                <meta content="IE=edge" http-equiv="X-UA-Compatible"/>
                <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
                <title>
                Emote
                </title>
                </head>
                <body>
                <div id="emojis">
                </div>
                <script src="emote.js">
                </script>
                </body>
                </html>
                    """
            
            with open(path_html, "w", encoding='utf-8') as html_file:
                html_file.write(content)

            with open(path_html_bk, "w", encoding='utf-8') as html_bk_file:
                html_bk_file.write(content)

            content_css = """
                        body{
                                overflow:hidden;
                        }

                        #emojis img {
                                position: absolute;
                                opacity: 0.0;
                            }
                            
                        .drop {

                                animation-name: emojis-fall, emojis-shake;
                                animation-duration: 5s, 3s;
                                animation-timing-function: linear, ease-in-out;
                                animation-play-state: running, running;
                        }


                        @keyframes emojis-fall {
                                0% {
                                        top: -10%;
                                        opacity: 1.0;
                                }
                                80% {
                                        opacity: 1.0;
                                }
                                100% {
                                        top: 100%;
                                }
                        }
                        @keyframes emojis-shake {
                                0% {
                                        transform: translateX(0px);
                                }
                                25% {
                                        transform: translateX(15px);
                                }
                                50% {
                                        transform: translateX(-15px);
                                }
                                100% {
                                        transform: translateX(0px);
                                }
                        }
                    """
            
            with open(path_css, "w", encoding='utf-8') as css_file:
                css_file.write(content_css)

            content_js = """
                const emojis = document.querySelectorAll('#emojis img');
                emojis.forEach((emoji) => {
                emoji.style.left = `calc(100% * ${Math.random()})`;
                });
            """

            with open(path_js, "w", encoding='utf-8') as js_file:
                js_file.write(content_js)

        path_html_highlight = f'{appdata_path}/rewardevents/web/src/html/highlight/highlight.html'
        path_html_highlightbk = f'{appdata_path}/rewardevents/web/src/html/highlight/highlight.html.tmp'

        dir_highlight = f'{appdata_path}/rewardevents/web/src/html/highlight'

        if not os.path.exists(path_html_highlight):
            
            os.makedirs(dir_highlight)

            content_highlight = """
                    <!DOCTYPE html>
                    <html lang="pt-br">
                    <head>
                        <link href="highlight.css" rel="stylesheet">
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
                        <link href="https://fonts.googleapis.com/css?family=Kanit" rel="stylesheet">
                        <meta charset="UTF-8">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>highlight</title>
                    </head>
                    <body>
                        <div class="container-fluid d-flex justify-content-center">
                            <div class="fade-in fadeOut" id="highlight-block">
                                <p><i class="fa-solid fa-thumbtack"></i><span id="username"></span> : <span id="message"></span></p>
                            </div>
                        </div>
                    </body>
                    </html>
                """
            
            with open(path_html_highlight, "w", encoding='utf-8') as html_highlight:
                html_highlight.write(content_highlight)

            with open(path_html_highlightbk, "w", encoding='utf-8') as html_highlight_bk_file:
                html_highlight_bk_file.write(content_highlight)

        path_html = f'{appdata_path}/rewardevents/web/src/html/'
        path_events = f'{appdata_path}/rewardevents/web/src/html/event/event.html'
        path_notification = f'{appdata_path}/rewardevents/web/src/html/notification/notification.html'
        path_video = f'{appdata_path}/rewardevents/web/src/html/video/video.html'

        if not os.path.exists(path_events):

            os.makedirs(f'{appdata_path}/rewardevents/web/src/html/event')
            shutil.move(f'{path_html}/event.html', path_events)

            shutil.move(f'{path_html}/event_styles', f'{path_html}/event')
            shutil.move(f'{path_html}/event.html.tmp', f'{path_events}.tmp')
            shutil.move(f'{path_html}/default.mp3', f'{path_html}/event/default.mp3')

        if not os.path.exists(path_notification):

            os.makedirs(f'{appdata_path}/rewardevents/web/src/html/notification')

            shutil.move(f'{path_html}/notification.html', path_notification)
            shutil.move(f'{path_html}/notification.html.tmp', f'{path_notification}.tmp')
            shutil.move(f'{path_html}/theme.css', f'{path_html}/notification/theme.css')

        if not os.path.exists(path_video):

            os.makedirs(f'{appdata_path}/rewardevents/web/src/html/video')

            shutil.move(f'{path_html}/video.html', path_video)
            shutil.move(f'{path_html}/video.html.tmp', f'{path_video}.tmp')

        with open(f'{appdata_path}/rewardevents/web/src/config/goal.json') as goal_file:
            goal_data = json.load(goal_file)

        if not "subscription_count" in goal_data and not "follow" in goal_data:

            goal_data = {
                "subscription_count" : {
                    "type": "subscription_count",
                    "description": "",
                    "current_amount": 0,
                    "target_amount": 0,
                    "started_at": ""
                },
                "follow" : {
                    "type": "follow",
                    "description": "",
                    "current_amount": 0,
                    "target_amount": 0,
                    "started_at": ""
                }
            }

get_files_list()

