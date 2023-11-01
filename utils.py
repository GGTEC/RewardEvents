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


if getattr(sys, 'frozen', False):
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash


def local_work(type_id):

    if type_id == 'data_dir':

        extDataDir = os.getcwd()

        if getattr(sys, 'frozen', False):
            extDataDir = f"{sys._MEIPASS}"

        return extDataDir
    
    elif type_id == 'appdata_path':

        appdata_path = f"{os.getenv('APPDATA')}/rewardevents/web/src"

        return appdata_path
    
    elif type_id == 'tempdir':

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
        print(f'Erro no arquivo {custom_path}.')
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
    error_type = "Unknown"
    error_message = ""

    if isinstance(ex, BaseException):  # Verifica se ex é uma exceção
        tb = ex.__traceback__

        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next

        error_type = type(ex).__name__
        error_message = str(ex)
    else:
        error_message = ex

    error = str(f'Erro = type: {error_type} | message: {error_message} | trace: {trace} | time: {time_error} \n\n')

    with open(f"{local_work('appdata_path')}/error_log.txt", "a+", encoding='utf-8') as log_file_r:
        log_file_r.write(error)


def check_delay(delay_command, last_use):

    messages_data = manipulate_json(f"{local_work('appdata_path')}/messages/messages_file.json", "load")

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
    
    chat_data = manipulate_json(f"{local_work('appdata_path')}/config/chat_config.json", "load")

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
            
        status_commands_data = manipulate_json(f"{local_work('appdata_path')}/config/commands_config.json", "load")

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

    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/config/notfic.json", "load")

    duration = notifc_config_Data['HTML_REDEEM_TIME']

    redeem = data['redeem_name']
    user = data['redeem_user']
    image = data['redeem_image']

    try:

        with open(f"{local_work('appdata_path')}/html/redeem/redeem.html", "r") as html:
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

    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/config/notfic.json", "load")
    
    duration = notifc_config_Data['HTML_MUSIC_TIME']

    user = data['redeem_user']
    artist = data['artist']
    music = data['music']

    html_file = f"{local_work('appdata_path')}/html/music/music.html"

    try:

        with open(html_file, "r") as html:
            soup = bs(html, 'html.parser')

        album_src = f"../../player/images/album.png?noCache={randint(0, 100000)}"

        main_div = soup.find("div", {"class": f"player"})
        main_div['style'] = f'animation-duration: {duration}s'

        music_name_tag = soup.find("span", {"class": "music_name"})
        artist_name_tag = soup.find("span", {"class": "artist_name"})
        user_name_tag = soup.find("span", {"class": "user_name"})

        music_name_tag.string = music
        artist_name_tag.string = artist
        user_name_tag.string = user

        artwork_tag = soup.find("div", {'class':'artwork'})

        if artwork_tag:

            artwork_tag['style'] = f"background: url(https://i.imgur.com/3idGgyU.png), url({album_src}) center no-repeat;"

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_video(video, time):

    try:

        with open(f"{local_work('appdata_path')}/html/video/video.html", "r") as html:
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

        with open(f"{local_work('appdata_path')}/html/highlight/highlight.html", "r", encoding='utf-8') as html:
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

    obs_not_data = manipulate_json(f"{local_work('appdata_path')}/config/notfic.json", "load")

    width = obs_not_data['EMOTE_PX']
    height = obs_not_data['EMOTE_PX']

    try:

        with open(f"{local_work('appdata_path')}/html/emote/emote.html", "r", encoding='utf-8') as html:
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

    messages_data = manipulate_json(f"{local_work('appdata_path')}/messages/messages_file.json", "load")

    return messages_data[key]


def compare_and_insert_keys():
    
    source_directory = f"{local_work('data_dir')}/web/src"
    destination_directory = f"{local_work('appdata_path')}"

    if not os.path.exists(destination_directory):

        shutil.copytree(source_directory, destination_directory)

    def update_dict_recursive(dest_dict, source_dict):
        for key, value in source_dict.items():
            if key in dest_dict:
                if isinstance(value, dict) and isinstance(dest_dict[key], dict):
                    update_dict_recursive(dest_dict[key], value)
            else:
                dest_dict[key] = value
                error_log(f"Chave '{key}' atualizada: {value}")

    for root_directory, _, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.json'):
                source_file_path = os.path.join(root_directory, file)
                destination_file_path = source_file_path.replace(source_directory, destination_directory)

                if not os.path.exists(destination_file_path):
                    error_log(f"File missing in the destination directory: {destination_file_path}")
                    shutil.copy2(source_file_path, destination_file_path)

                try:
                    with open(source_file_path, 'r', encoding='utf-8') as src_file, open(destination_file_path, 'r+', encoding='utf-8') as dest_file:
                        data1 = json.load(src_file)
                        data2 = json.load(dest_file)

                        if isinstance(data1, dict) and isinstance(data2, dict):
                            update_dict_recursive(data2, data1)
                            dest_file.seek(0)
                            json.dump(data2, dest_file, indent=4, ensure_ascii=False)
                            dest_file.truncate()

                except json.JSONDecodeError as e:
                    error_log(f"Error decoding the source JSON file: {source_file_path}")


    for root_directory, dirs, files in os.walk(destination_directory):
        for d in dirs:
            destination_path = os.path.join(root_directory, d)
            source_path = destination_path.replace(destination_directory, source_directory)

            
            if not os.path.exists(source_path):
                if os.path.isdir(destination_path):
                    error_log(f"File or directory in the destination directory that is not in the source directory: {destination_path}")
                    shutil.rmtree(destination_path)

        for file in files:

            destination_path = os.path.join(root_directory, file)
            source_path = destination_path.replace(destination_directory, source_directory)

            if not os.path.exists(source_path):
                if os.path.isfile(destination_path):
                    error_log(f"File in the destination directory that is not in the source directory: {destination_path}")
                    os.remove(destination_path)


    return True


def normpath_simple(path):
    
    path_norm = os.path.normpath(path)
    
    path_norm_simple = path_norm.replace('\\', '/')
    
    return path_norm_simple


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
            
        manipulate_json(f"{local_work('appdata_path')}/user_info/bot_list.json", "save",data_save)
        
        respo_tags = requests.get("https://ggtec.github.io/list_games_tags_tw/tags.json")
        data_save_tags = json.loads(respo_tags.text)

        manipulate_json(f"{local_work('appdata_path')}/games/tags.json", "save",data_save_tags)


        respo_games = requests.get("https://ggtec.github.io/list_games_tags_tw/games.json")
        data_save_games = json.loads(respo_games.text)
            
        manipulate_json(f"{local_work('appdata_path')}/games/games.json", "save", data_save_games)

        return True
    
    except Exception as e:

        if isinstance(e,ConnectionError):
            ask = messagebox.showerror("Erro", "Erro de conexão, verifique a conexão com a internet e tente novamente.")
            if ask == 'ok':
                sys.exit(0)
        else:
            error_log(e)
