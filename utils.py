import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta

import coverpy
import requests
import validators
import yt_dlp
from bs4 import BeautifulSoup as bs
from dateutil import tz
from PIL import Image
from pytube import Search, YouTube

coverpy = coverpy.CoverPy()

messages_file = open('web/src/messages/messages_file.json', "r", encoding='utf-8') 
messages_data = json.load(messages_file) 

message_error = messages_data['response_delay_error']

extDataDir = os.getcwd()

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS

def calculate_time(started):
    
    try:

        ts = time.strptime(started[:19], "%Y-%m-%dT%H:%M:%S")
        time_conv = time.strftime("%Y-%m-%d %H:%M:%S", ts)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()

        utc = datetime.strptime(time_conv, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)

        central = utc.astimezone(to_zone)

        now = datetime.now()
        time_now = now.strftime("%H:%M:%S")

        time_not = datetime.strftime(central, '%H:%M:%S')

        t1 = datetime.strptime(time_not, '%H:%M:%S')
        t2 = datetime.strptime(time_now, '%H:%M:%S')

        diff = t2 - t1

        seconds_get = diff.seconds

        time_in_live = str(timedelta(seconds=seconds_get))

        time_obj = time.strptime(time_in_live, "%H:%M:%S")

        time_in_live_stip = time.strftime("%H:%M", time_obj)

        return time_in_live_stip

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

    with open("web/src/error_log.txt", "a+", encoding='utf-8') as log_file_r:
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

def album_search(user_input):
    
    music = '0'
    artist = '0'
    url_youtube = "0"
    success = 0

    try:

        if validators.url(user_input):
            
            yt = YouTube(user_input)
            url_youtube = user_input
            video_title = yt.title
            rep_input = removestring(video_title)

        else:

            search_youtube = Search(user_input)
            result_search = search_youtube.results[0].__dict__
            url_youtube = result_search['watch_url']

            yt = YouTube(url_youtube)
            video_title = yt.title
            rep_input = user_input 

        try:
            
            result = coverpy.get_cover(rep_input, 1)
            album_art = result.artwork(625)
            artist = result.artist
            music = result.name

            img_data = requests.get(album_art).content

            album_art_mei = open(extDataDir + '/web/src/player/images/album.png', 'wb')
            album_art_mei.write(img_data)
            album_art_mei.close()

            album_art_local = open('web/src/player/images/album.png', 'wb')
            album_art_local.write(img_data)
            album_art_local.close()
        
        except:

            ydl_opts={
                'skip_download' : True,
                'noplaylist': True,
                'quiet' : True,
                'no_color': True,
                'write_thumbnails' : True,
                'outtmpl': 'web/src/player/images/album.%(ext)s',
                'force-write-archive' : True
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_youtube])

            img_webp = Image.open('web/src/player/images/album.webp').convert("RGB")
            img_webp.save('web/src/player/images/album.png','png')

            try:
                
                title_split = video_title.split(' - ')
                artist = title_split[0]
                music = title_split[1]
            
            except Exception as e:

                music = video_title
                artist = '0'

        success = 1

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

def check_delay():
    
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    time_delay_file = open('web/src/config/prefix_tts.json')
    time_delay_data = json.load(time_delay_file)

    delay = time_delay_data['delay_date']

    delay_compare = time_delay_data['delay_config']

    t1 = datetime.strptime(delay, "%d/%m/%Y %H:%M:%S")
    t2 = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

    if t1 > t2:
        
        diff = t1 - t2
        
        message = message_error.replace('{seconds}', str(diff.seconds))
        value = False
        
        return message,value
        
    else:

        datetime_object = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

        time_delay_file = open('web/src/config/prefix_tts.json')
        time_delay_data = json.load(time_delay_file)
        delay_compare = time_delay_data['delay_config']

        future_date = datetime_object + timedelta(seconds= int(delay_compare))
        delay_save = future_date.strftime("%d/%m/%Y %H:%M:%S")

        time_delay_data['delay_date'] = delay_save

        time_delay_write = open('web/src/config/prefix_tts.json' , 'w', encoding='utf-8') 
        json.dump(time_delay_data, time_delay_write, indent = 4, ensure_ascii=False)
        
        message = 'OK'
        value = True
        
        return message,value

def check_global_delay():
    
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    time_delay_file = open('web/src/config/commands_config.json')
    time_delay_data = json.load(time_delay_file)

    delay = time_delay_data['delay_date']

    delay_compare = time_delay_data['delay_config'] 

    t1 = datetime.strptime(delay, "%d/%m/%Y %H:%M:%S")
    t2 = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

    if t1 > t2:
        
        diff = t1 - t2
        

        message = message_error.replace('{seconds}', str(diff.seconds))
        value = False
        
        return message,value
        
    else:

        datetime_object = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

        time_delay_file = open('web/src/config/commands_config.json')
        time_delay_data = json.load(time_delay_file)
        delay_compare = time_delay_data['delay_config']

        future_date = datetime_object + timedelta(seconds= int(delay_compare))
        delay_save = future_date.strftime("%d/%m/%Y %H:%M:%S")

        time_delay_data['delay_date'] = delay_save

        time_delay_write = open('web/src/config/commands_config.json' , 'w', encoding='utf-8') 
        json.dump(time_delay_data, time_delay_write, indent = 4, ensure_ascii=False)
        
        message = 'OK'
        value = True
        
        return message,value

def send_message(type_message):
    
    try:
        status_commands_check = open('web/src/config/commands_config.json')
        status_commands_data = json.load(status_commands_check)
        
        status_error_time = status_commands_data['STATUS_ERROR_TIME']
        status_error_user = status_commands_data['STATUS_ERROR_USER']
        status_response = status_commands_data['STATUS_RESPONSE']
        status_clip = status_commands_data['STATUS_CLIP']
        status_tts = status_commands_data['STATUS_TTS']
        status_timer = status_commands_data['STATUS_TIMER']
        status_bot = status_commands_data['STATUS_BOT']
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
                    
        elif type_message == 'ERROR_TTS':
            
            if status_tts == 1:
                return True
                
        elif type_message == 'TIMER':
            
            if status_timer == 1:
                return True
                
        elif type_message == 'STATUS_BOT':
            
            if status_bot == 1:
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

    os.remove("web/src/html/backup.html")

    if copy_file('web/src/html/notification.html', 'web/src/html/backup.html') == 1:

        html = open('web/src/html/notification.html')

        try:
            
            soup = bs(html, 'html.parser')

            redeem_block = soup.find("div", {"class": "redem_block"})
            music_block = soup.find("div", {"class": "music_block"})

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
                
                html.close()
                f_output = open("web/src/html/notification.html", "wb")
                f_output.write(soup.prettify("utf-8"))
                f_output.close()

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
                
                html.close()
                f_output = open("web/src/html/notification.html", "wb")
                f_output.write(soup.prettify("utf-8"))
                f_output.close()

        except Exception as e:
            html.close()

            os.remove("web/src/html/notification.html")

            copy_file('web/src/html/backup.html', 'web/src/html/notification.html')

            error_log(e)




