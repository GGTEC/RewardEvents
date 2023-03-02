import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta
import pytz

import coverpy
import requests
import validators
import yt_dlp
from bs4 import BeautifulSoup as bs
from dateutil import tz
from PIL import Image
from pytube import Search, YouTube

import urllib.request
import zipfile

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

    print(error)

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

            with open(extDataDir + 'f/{appdata_path}/rewardevents/web/src/player/images/album.png', 'wb') as album_art_mei:
                album_art_mei.write(img_data)

            with open(f'{appdata_path}/rewardevents/web/src/player/images/album.png', 'wb') as album_art_local:
                album_art_local.write(img_data)
        
        except:

            ydl_opts={
                'skip_download' : True,
                'noplaylist': True,
                'quiet' : True,
                'no_color': True,
                'write_thumbnails' : True,
                'outtmpl': f'{appdata_path}/rewardevents/web/src/player/images/album.%(ext)s',
                'force-write-archive' : True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_youtube])

            img_webp = Image.open(f'{appdata_path}/rewardevents/web/src/player/images/album.webp').convert("RGB")
            img_webp.save(f'{appdata_path}/rewardevents/web/src/player/images/album.png','png')

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
    
def update_notif(redeem,user,artist,type_not):

   html_backup = f"{appdata_path}/rewardevents/web/src/html/notification.html.tmp"
   html_file = f"{appdata_path}/rewardevents/web/src/html/notification.html"


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
            music_name_tag.string = redeem
            artist_name_tag.string = artist
            redeem_user_music_tag.string = user
                
        with open(html_file, "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))


   except Exception as e:
      error_log(e)
      
def update_video(video):
    
    html_video_backup = f"{appdata_path}/rewardevents/web/src/html/video.html.tmp"
    html_video_file = f"{appdata_path}/rewardevents/web/src/html/video.html"

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
    
    html_event_backup = f"{appdata_path}/rewardevents/web/src/html/event.html.tmp"
    html_event_file = f"{appdata_path}/rewardevents/web/src/html/event.html"

    image_src = data['img_src']
    img_px = data['img_px']
    response_px = data['response_px']
    duration = int(data['duration']) - 1
    image_above = data['image_above']	
    audio_src = data['audio_src']
    audio_volume = data['audio_volume']
    tts_src = 'src/player/cache/tts.mp3'
    play_tts = data['play_tts']
    
    audio_volume = int(audio_volume)/100
    
    username = data['username']
    message = data['message']
    
    username_soup = bs(username, 'html.parser')
    message_soup = bs(message, 'html.parser')
    
    try:
        
        if image_above == 0: 

            with open(html_event_backup, "r",encoding='utf-8') as html:
                soup = bs(html, 'html.parser')

                png_div = soup.find("div", {"id": "png_div_above"})
                gif_div = soup.find("div", {"id": "gif_div_above"})

                main_div = soup.find("div", {"id": "main_div_above"})
                main_div['style'] = f'animation-duration: {duration}s'
                
                main_div_over = soup.find("div", {"id": "main_div_over"})
                main_div_over['style'] = 'display: none !important;'
                
                audio_tag = soup.find("audio", {"id": "audio1"})
                audio_tag['src'] = f'http://absolute/{audio_src}'
                
                audio2_tag = soup.find("audio", {"id": "audio2"})
                
                if play_tts == 0:
                    audio2_tag['src'] = f''
                else:
                    audio2_tag['src'] = f'http://localhost:7000/{tts_src}'
                    
                volume_tag = soup.find("input", {"id": "volume"})
                volume_tag['value'] = audio_volume

                if image_src.endswith('.gif'):
                    
                    png_div['style'] = 'display: none !important;'
                    gif_div['style'] = 'display: block;'

                    gif_source = soup.find("img" ,{"id":"gif_above"})
                    gif_source['src'] = 'http://absolute/' + image_src
                    gif_source['style'] = f'width: {img_px}px;'
                    
                    user_tag = soup.find("p", {"id": "username-gif-above"})
                    user_tag['style'] = f'font-size: {response_px}px;'
                    
                    message_tag = soup.find("p", {"id": "message-gif-above"})
                    message_tag['style'] = f'font-size: {response_px}px;'
                    
                    user_tag.insert(1,username_soup)
                    message_tag.insert(1,message_soup)
                    
                elif image_src.endswith('.png'):
                    
                    png_div['style'] = 'display: block;'
                    gif_div['style'] = 'display: none !important;'

                    png_source = soup.find("img" ,{"id":"png_above"})
                    png_source['src'] = 'http://absolute/' + image_src
                    png_source['style'] = f'width: {img_px}px;'
                    
                    user_tag = soup.find("p", {"id": "username-png-above"})
                    user_tag['style'] = f'font-size: {response_px}px;'
                    
                    message_tag = soup.find("p", {"id": "message-png-above"})
                    message_tag['style'] = f'font-size: {response_px}px;'
                    
                    user_tag.string = ""
                    message_tag.string = ""
                    
                    user_tag.insert(1,username_soup)
                    message_tag.insert(1,message_soup)
                
                with open(html_event_file, "wb") as f_output:
                    f_output.write(soup.prettify("utf-8"))

            return True
        
        else:
            
            with open(html_event_backup, "r",encoding='utf-8') as html:
                soup = bs(html, 'html.parser')

                png_div = soup.find("div", {"id": "png_div_over"})
                gif_div = soup.find("div", {"id": "gif_div_over"})

                main_div = soup.find("div", {"id": "main_div_over"})
                main_div['style'] = f'animation-duration: {duration}s'
                
                main_div_above = soup.find("div", {"id": "main_div_above"})
                main_div_above['style'] = 'display: none !important;'
                
                audio_tag = soup.find("audio", {"id": "audio1"})
                audio_tag['src'] = f'http://absolute/{audio_src}'
                
                audio2_tag = soup.find("audio", {"id": "audio2"})
                
                if play_tts == 0:
                    audio2_tag['src'] = f''
                else:
                    audio2_tag['src'] = f'http://localhost:7000/{tts_src}'
                    
                volume_tag = soup.find("input", {"id": "volume"})
                volume_tag['value'] = audio_volume

                if image_src.endswith('.gif'):
                    
                    png_div['style'] = 'display: none !important;'
                    gif_div['style'] = 'display: block;'

                    gif_source = soup.find("img" ,{"id":"gif_over"})
                    gif_source['src'] = 'http://absolute/' + image_src
                    gif_source['style'] = f'width: {img_px}px;'
                    
                    user_tag = soup.find("p", {"id": "username-gif-over"})
                    user_tag['style'] = f'font-size: {response_px}px;'
                    
                    message_tag = soup.find("p", {"id": "message-gif-over"})
                    message_tag['style'] = f'font-size: {response_px}px;'
                    
                    user_tag.string = ""
                    message_tag.string = ""
                    
                    user_tag.insert(1,username_soup)
                    message_tag.insert(1,message_soup)
                    
                elif image_src.endswith('.png'):
                    
                    png_div['style'] = 'display: block;'
                    gif_div['style'] = 'display: none !important;'

                    png_source = soup.find("img" ,{"id":"png_over"})
                    png_source['src'] = 'http://absolute/' + image_src
                    png_source['style'] = f'width: {img_px}px;'
                    
                    user_tag = soup.find("p", {"id": "username-png-over"})
                    user_tag['style'] = f'font-size: {response_px}px;'
                    message_tag = soup.find("p", {"id": "message-png-over"})
                    message_tag['style'] = f'font-size: {response_px}px;'
                    
                    user_tag.string = ""
                    message_tag.string = ""
                    
                    user_tag.insert(1,username_soup)
                    message_tag.insert(1,message_soup)
                
                with open(html_event_file, "wb") as f_output:
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
    
    dir = f"{appdata_path}/rewardevents/web"

    if not os.path.exists(dir):
    
        os.makedirs(dir)

        url = "https://ggtec.github.io/GGTECApps/assets/web.zip"

        zip_path = f"{appdata_path}/rewardevents/web.zip"
        unzip_path = f"{appdata_path}/rewardevents/"

        # Baixar o arquivo zip
        urllib.request.urlretrieve(url, zip_path)

        # Descompactar o arquivo zip
        with zipfile.ZipFile(unzip_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_path)

        # Excluir o arquivo zip baixado
        os.remove(zip_path)


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

        
get_files_list()

