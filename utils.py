import json
import os
import shutil
import sys
import time
import requests
import tkinter.messagebox as messagebox
import pytz

import importlib

from datetime import datetime
from random import randint
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

extDataDir = os.getcwd()
appdata_path = os.getenv('APPDATA')

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
        extDataDir = sys._MEIPASS


def local_work(type_id):

    if type_id == 'data_dir':

        extDataDir = os.getcwd()

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            if getattr(sys, 'frozen', False):
                if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
                    import pyi_splash
                extDataDir = sys._MEIPASS

        return extDataDir
    
    elif type_id == 'appdata_path':

        appdata_path = os.getenv('APPDATA')

        return appdata_path


load_dotenv(dotenv_path=os.path.join(local_work('data_dir'), '.env'))


def splash_close():
    pyi_splash.close()


def manipulate_json(custom_path, type_id, data=None):

    try:

        if type_id == 'load':
            with open(custom_path, 'r',encoding='utf-8') as file:
                loaded_data = json.load(file)
            return loaded_data
        elif type_id == 'save':
            with open(custom_path, 'w',encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

    except FileNotFoundError as e:
        error_log(e)
        print(f'The file {custom_path} was not found.')

    except Exception as e:

        error_log(e)


def find_between(s, first, last):

    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
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
        minutes = (difference.seconds//60) % 60
        sec = difference.seconds % 60

        time_in_live = {
            'days': str(days),
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

    error = str(
        f'Erro = type: {type(ex).__name__} | message: {str(ex)} | trace: {trace} | time: {time_error} \n')

    with open(f"{appdata_path}/rewardevents/web/src/error_log.txt", "a+", encoding='utf-8') as log_file_r:
        log_file_r.write(error)


def check_delay(delay_command, last_use):

    messages_data = manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/messages/messages_file.json", "load")

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


def check_delay_duel(delay_command, last_use):

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


def time_date():
    
    chat_data = manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/config/chat_config.json", "load")

    now = datetime.now()
    
    if chat_data['data-show'] == 1:
        format = chat_data['time-format']
        if chat_data['type-data'] == "passed":
            chat_time = now.strftime('%Y-%m-%dT%H:%M:%S')
        elif chat_data['type-data'] == "current":
            chat_time = now.strftime(format)
    else: 
        chat_time = ''
        
    return chat_time


def send_message(type_message):

    try:
            
        status_commands_data = manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/config/commands_config.json", "load")

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


def update_notif(data):

    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/config/notfic.json", "load")

    duration = notifc_config_Data['HTML_REDEEM_TIME']

    redeem = data['redeem_name']
    user = data['redeem_user']
    image = data['redeem_image']

    try:

        with open(f"{local_work('appdata_path')}/rewardevents/web/src/html/redeem/redeem.html", "r") as html:
            soup = bs(html, 'html.parser')

        redeem_src = image

        main_div = soup.find("div", {"id": f"main-block"})
        main_div['style'] = f'animation-duration: {duration}s'

        image_redeem = soup.find("img", {"class": "img-responsive"})
        redeem_name_tag = soup.find("span", {"class": "redem_name"})
        redeem_user_tag = soup.find("span", {"class": "redem_user"})

        image_redeem['src'] = redeem_src
        redeem_name_tag.string = redeem
        redeem_user_tag.string = user

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_music(data):
    
    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/config/notfic.json", "load")

    duration = notifc_config_Data['HTML_MUSIC_TIME']

    user = data['redeem_user']
    artist = data['artist']
    music = data['music']

    try:

        with open(f"{local_work('appdata_path')}/rewardevents/web/src/html/music/music.html", "r") as html:
            soup = bs(html, 'html.parser')

        album_src = f"../../player/images/album.png?noCache={randint(0, 100000)}"

        main_div = soup.find("div", {"id": f"main-block"})
        main_div['style'] = f'animation-duration: {duration}s'

        image_redeem = soup.find("img", {"class": "img-responsive"})
        music_name_tag = soup.find("span", {"class": "music_name"})
        artist_name_tag = soup.find("span", {"class": "artist_name"})
        redeem_user_music_tag = soup.find(
            "span", {"class": "redem_user_music"})

        image_redeem['src'] = album_src
        music_name_tag.string = music
        artist_name_tag.string = artist
        redeem_user_music_tag.string = user

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_video(video, time):

    try:

        with open(f"{local_work('appdata_path')}/rewardevents/web/src/html/video/video.html", "r") as html:
            soup = bs(html, 'html.parser')

        video_div = soup.find("div", {"id": "video_div"})
        gif_div = soup.find("div", {"id": "gif_div"})

        main_div = soup.find("div", {"id": f"main-block"})
        main_div['style'] = f'animation-duration: {time}s'

        if video.endswith('.gif'):

            video_div['style'] = 'display: none !important;'
            gif_div['style'] = 'display: block;'

            video_redeem = soup.find("img")
            video_redeem['src'] = f'http://absolute/{video}{randint(0, 10000)}'

        else:

            gif_div['style'] = 'display: none !important;'
            video_div['style'] = 'display: block;'

            video_redeem = soup.find("video")
            video_redeem['src'] = f'http://absolute/{video}{randint(0, 10000)}'

        return str(soup)

    except Exception as e:

        error_log(e)

        return True


def update_highlight(data):

    duration = int(data['duration']) - 1

    color_highligh_username = data['color_username']
    color_highligh_message = data['color_message']
    font_weight = data['weight']
    font_size = data['size']

    message = data['user_input']
    username = data['username']

    try:

        with open(f"{local_work('appdata_path')}/rewardevents/web/src/html/highlight/highlight.html", "r", encoding='utf-8') as html:
            soup = bs(html, 'html.parser')

        main_div = soup.find("div", {"id": f"highlight-block"})
        main_div['style'] = f'animation-duration: {duration}s'

        font_style = soup.find("p", {"id": f"text_style"})
        font_style['style'] = f'font-size: {font_size};font-weight: {font_weight};'

        username_tag = soup.find("span", {"id": f"username"})
        username_tag['style'] = f'color: {color_highligh_username};'
        username_tag.string = username

        message_tag = soup.find("span", {"id": f"message"})
        message_tag['style'] = f'color: {color_highligh_message};'
        message_tag.string = message

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_emote(data):

    obs_not_data = manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/config/notfic.json", "load")

    width = obs_not_data['EMOTE_PX']
    height = obs_not_data['EMOTE_PX']

    try:

        with open(f"{local_work('appdata_path')}/rewardevents/web/src/html/emote/emote.html", "r", encoding='utf-8') as html:
            soup = bs(html, 'html.parser')

        main_div = soup.find("div", {"id": f"emojis"})

        for emote in data:

            random = randint(0, 5)
            element = bs(emote, 'html.parser')
            element_style = element.find("img", {"class": f"emoji"})
            element_style['style'] = f'width:{width}px;height:{height}px;animation-delay:{random}s'
            main_div.append(element)

        return str(soup)

    except Exception as e:

        error_log(e)
        return False


def replace_all(text, dic_res):

    try:
        for i, j in dic_res.items():
            text = text.replace(str(i), str(j))

        return text

    except Exception as e:
        error_log(e)

        return ''


def messages_file_load(key):

    messages_data = manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/messages/messages_file.json", "load")

    return messages_data[key]


def compare_and_insert_keys():
    
    source_directory = f"{local_work('data_dir')}/web/src"
    destination_directory = f"{local_work('appdata_path')}/rewardevents/web/src"
    ignored_files = ['games.json','tags.json','bot_list.json', 'bot_list.json', 'badges_global.json', 'badges_global.json']

    try:

        if not os.path.exists(destination_directory):

            shutil.copytree(source_directory, destination_directory)

        for root_directory, _, files in os.walk(source_directory):
            
            for file in files:
                
                if file.endswith('.json') and file not in ignored_files:
                    
                    source_file_path = os.path.join(root_directory, file)
                    destination_file_path = source_file_path.replace(source_directory, destination_directory)

                    if not os.path.exists(destination_file_path):
                        print(f"File missing in the destination directory: {destination_file_path}")
                        shutil.copy2(source_file_path, destination_file_path)

                    try:
                        
                        with open(source_file_path, 'r', encoding='utf-8') as src_file, open(destination_file_path, 'r+', encoding='utf-8') as dest_file:
                            data1 = json.load(src_file)
                            dest_file.seek(0)
                            
                            try:
                                data2 = json.load(dest_file)

                                if isinstance(data1, list) and isinstance(data2, list):
                                    updated_content = data1 + [item for item in data2 if item not in data1]

                                    if updated_content != data2:
                                        
                                        dest_file.seek(0)
                                        
                                        json.dump(updated_content, dest_file, indent=4, ensure_ascii=False)
                                        
                                        dest_file.truncate()
                                        
                                        print(f"Content updated in the file {destination_file_path}")

                                elif isinstance(data1, dict) and isinstance(data2, dict):
                                    
                                    keys1 = set(data1.keys())
                                    keys2 = set(data2.keys())
                                    
                                    missing_keys = keys1 - keys2

                                    if missing_keys:
                                        
                                        print(f"Keys missing in the file {destination_file_path}:")
                                        
                                        for key in missing_keys:
                                            print(key)
                                            
                                        content = data2
                                        altered = False

                                        for key in missing_keys:
                                            
                                            if key not in content or content[key] != data1[key]:
                                                content[key] = data1[key]
                                                altered = True

                                        if altered:
                                            
                                            dest_file.seek(0)
                                            json.dump(content, dest_file, indent=4, ensure_ascii=False)
                                            dest_file.truncate()
                                            print(f"Content updated in the file {destination_file_path}")

                                else:
                                    
                                    print(f"Error: File {source_file_path} or {destination_file_path} contains an incompatible format.")

                            except json.JSONDecodeError as e:
                                
                                print(f"Error decoding the destination JSON file: {destination_file_path}")
                                print(e)
                                
                                # If a read error occurs, copy the source file to the destination file
                                
                                shutil.copy2(source_file_path, destination_file_path)
                                print(f"Destination file copied to resolve the issue: {destination_file_path}")
                                
                    except json.JSONDecodeError as e:
                        print(f"Error decoding the source JSON file: {source_file_path}")
                        print(e)

    except Exception as e:
        error_log(e)


def get_files_list():

    try:

        compare_and_insert_keys()
        
        response = requests.get('https://api.twitchinsights.net/v1/bots/all')

        data = json.loads(response.text)
        data_save = []
        data = data['bots']

        for idx, i in enumerate(data):
            name = data[idx][0]
            data_save.append(name)
            
        manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/user_info/bot_list.json", "save",data_save)
        
        respo_tags = requests.get("https://ggtec.github.io/list_games_tags_tw/tags.json")
        data_save_tags = json.loads(respo_tags.text)

        manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/games/tags.json", "save",data_save_tags)


        respo_games = requests.get("https://ggtec.github.io/list_games_tags_tw/games.json")
        data_save_games = json.loads(respo_games.text)
            
        manipulate_json(f"{local_work('appdata_path')}/rewardevents/web/src/games/games.json", "save", data_save_games)

        html_roaming = f"{local_work('appdata_path')}/rewardevents/web/src/html/video/iframe.html"
        html_internal = f"{local_work('data_dir')}/web/src/html/video/iframe.html"

        shutil.copy(html_internal, html_roaming)

        return True
    
    except Exception as e:

        if isinstance(e,ConnectionError):
            ask = messagebox.showerror("Erro", "Erro de conexão, verifique a conexão com a internet e tente novamente.")
            if ask == 'ok':
                sys.exit(0)
        else:
            error_log(e)
