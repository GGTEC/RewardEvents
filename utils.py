import json
import os
import shutil
import sys
import time
from datetime import datetime
import pytz
import random
from random import randint
import requests
from bs4 import BeautifulSoup as bs

import urllib.request
import zipfile
import tempfile

import tkinter.messagebox as messagebox

extDataDir = os.getcwd()

appdata_path = os.getenv('APPDATA')

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS


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

    with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', "r", encoding='utf-8') as messages_file:
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


def update_notif(data):

    with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding='utf-8') as notifc_config_file:
        notifc_config_Data = json.load(notifc_config_file)

    duration = notifc_config_Data['HTML_REDEEM_TIME']

    redeem = data['redeem_name']
    user = data['redeem_user']
    image = data['redeem_image']

    html_file = f"{appdata_path}/rewardevents/web/src/html/redeem/redeem.html"

    try:

        with open(html_file, "r") as html:
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

    with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding='utf-8') as notifc_config_file:
        notifc_config_Data = json.load(notifc_config_file)

    duration = notifc_config_Data['HTML_MUSIC_TIME']

    user = data['redeem_user']
    artist = data['artist']
    music = data['music']

    html_file = f"{appdata_path}/rewardevents/web/src/html/music/music.html"

    try:

        with open(html_file, "r") as html:
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

    html_video_file = f"{appdata_path}/rewardevents/web/src/html/video/video.html"

    try:

        with open(html_video_file, "r") as html:
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

    html_highlight = f"{appdata_path}/rewardevents/web/src/html/highlight/highlight.html"

    duration = int(data['duration']) - 1

    color_highligh_username = data['color_username']
    color_highligh_message = data['color_message']
    font_weight = data['weight']
    font_size = data['size']

    message = data['user_input']
    username = data['username']

    try:

        with open(html_highlight, "r", encoding='utf-8') as html:
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

    with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding='utf-8') as obs_not_file:
        obs_not_data = json.load(obs_not_file)

    width = obs_not_data['EMOTE_PX']
    height = obs_not_data['EMOTE_PX']

    html_emote_file = f"{appdata_path}/rewardevents/web/src/html/emote/emote.html"

    try:

        with open(html_emote_file, "r", encoding='utf-8') as html:
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


def comparar_e_inserir_chaves(diretorio_origem, diretorio_destino, arquivos_ignorados):

    for diretorio_raiz, _, arquivos in os.walk(diretorio_origem):
        for arquivo in arquivos:
            if arquivo.endswith('.json') and arquivo not in arquivos_ignorados:
                caminho_arquivo_origem = os.path.join(diretorio_raiz, arquivo)
                caminho_arquivo_destino = caminho_arquivo_origem.replace(
                    diretorio_origem, diretorio_destino)

                if not os.path.exists(caminho_arquivo_destino):
                    print(
                        f"Arquivo ausente no diretório de destino: {caminho_arquivo_destino}")
                    shutil.copy2(caminho_arquivo_origem,
                                 caminho_arquivo_destino)

                with open(caminho_arquivo_origem, 'r', encoding='utf-8') as f1, open(caminho_arquivo_destino, 'r+', encoding='utf-8') as f2:
                    try:
                        dados1 = json.load(f1)
                        dados2 = json.load(f2)

                        if isinstance(dados1, list) and isinstance(dados2, list):
                            conteudo_atualizado = dados1 + \
                                [item for item in dados2 if item not in dados1]
                            if conteudo_atualizado != dados2:
                                f2.seek(0)
                                json.dump(conteudo_atualizado, f2,
                                          indent=4, ensure_ascii=False)
                                f2.truncate()
                                print(
                                    f"Conteúdo atualizado no arquivo {caminho_arquivo_destino}")

                        elif isinstance(dados1, dict) and isinstance(dados2, dict):
                            chaves1 = set(dados1.keys())
                            chaves2 = set(dados2.keys())

                            chaves_ausentes = chaves1 - chaves2

                            if chaves_ausentes:
                                print(
                                    f"Chaves ausentes no arquivo {caminho_arquivo_destino}:")
                                for chave in chaves_ausentes:
                                    print(chave)

                                f2.seek(0)
                                conteudo = json.load(f2)

                                alterado = False

                                for chave in chaves_ausentes:
                                    if chave not in conteudo or conteudo[chave] != dados1[chave]:
                                        conteudo[chave] = dados1[chave]
                                        alterado = True

                                if alterado:  # Verifica se houve alterações antes de atualizar
                                    f2.seek(0)
                                    json.dump(conteudo, f2, indent=4,
                                              ensure_ascii=False)
                                    f2.truncate()
                                    print(
                                        f"Conteúdo atualizado no arquivo {caminho_arquivo_destino}")

                        else:
                            print(
                                f"Erro: Arquivo {caminho_arquivo_origem} ou {caminho_arquivo_destino} contém um formato incompatível.")

                    except json.JSONDecodeError as e:
                        print(
                            f"Erro: Falha ao decodificar o arquivo JSON: {caminho_arquivo_origem} ou {caminho_arquivo_destino}")
                        print(e)


diretorio_origem = f'{extDataDir}/web/src'

diretorio_destino = f'{appdata_path}/rewardevents/web/src'

arquivos_ignorados = ['games.json','tags.json','bot_list.json', 'bot_list.json', 'badges_global.json', 'badges_global.json']


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

            url = "https://github.com/GGTEC/GGCORETEC/raw/main/assets/web.zip"

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
            comparar_e_inserir_chaves(
                diretorio_origem, diretorio_destino, arquivos_ignorados)

            response = requests.get(
                'https://api.twitchinsights.net/v1/bots/all')

            data = json.loads(response.text)
            data_save = []
            data = data['bots']

            for idx, i in enumerate(data):
                name = data[idx][0]
                data_save.append(name)

            with open(f"{appdata_path}/rewardevents/web/src/user_info/bot_list.json", "w") as outfile:
                json.dump(data_save, outfile, indent=6)

            respo_tags = requests.get(
                "https://ggtec.github.io/list_games_tags_tw/tags.json")
            data_save_tags = json.loads(respo_tags.text)

            with open(f'{appdata_path}/rewardevents/web/src/games/tags.json', "w", encoding="UTF-8") as tags_file:
                json.dump(data_save_tags, tags_file,
                          indent=4, ensure_ascii=False)

            respo_games = requests.get(
                "https://ggtec.github.io/list_games_tags_tw/games.json")
            data_save_games = json.loads(respo_games.text)

            with open(f'{appdata_path}/rewardevents/web/src/games/games.json', "w", encoding="UTF-8") as games_file:
                json.dump(data_save_games, games_file,
                          indent=4, ensure_ascii=False)

        except Exception as e:

            if type(e).__name__ == "ConnectionError":

                ask = messagebox.showerror(
                    "Erro", "Erro de conexão, verifique a conexão com a internet e tente novamente.")

                if ask == 'ok':
                    sys.exit(0)

            else:

                error_log(e)

    with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding='utf-8') as notif_file:
        notif_data = json.load(notif_file)

        if not 'HTML_REDEEM_ACTIVE' in notif_data:

            data = {
                "HTML_PLAYER_ACTIVE": 1,
                "HTML_EMOTE_ACTIVE": 1,
                "HTML_REDEEM_ACTIVE": 1,
                "HTML_REDEEM_TIME": 5,
                "HTML_MUSIC_TIME": 5,
                "EMOTE_PX": "40"
            }

            with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'w', encoding='utf-8') as notif_file:
                json.dump(data, notif_file, indent=4, ensure_ascii=False)

    notif_path = f'{appdata_path}/rewardevents/web/src/html/notification'
    remove_path = f'{appdata_path}\\rewardevents\\web\\src\\html'

    if os.path.exists(notif_path):

        shutil.rmtree(remove_path)

        url = "https://github.com/GGTEC/GGCORETEC/raw/main/assets/html.zip"

        zip_path = f"{appdata_path}/rewardevents/html.zip"
        unzip_path = f"{appdata_path}/rewardevents/web/src"

        urllib.request.urlretrieve(url, zip_path)

        if os.path.exists(zip_path):

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(unzip_path)

            if os.path.exists(f'{appdata_path}\\rewardevents\\web\\src\\html\\redeem'):
                os.remove(zip_path)

    with open(f'{appdata_path}/rewardevents/web/src/config/websocket_param.json', 'r', encoding='utf-8') as websocket_param_file:
        websocket_param_data = json.load(websocket_param_file)

    if 'channel.charity_campaign.donate' in websocket_param_data:

        websocket_param_data.remove('channel.charity_campaign.donate')
        websocket_param_data.remove('channel.charity_campaign.progress')
        websocket_param_data.remove('channel.charity_campaign.start')
        websocket_param_data.remove('channel.charity_campaign.stop')

        with open(f'{appdata_path}/rewardevents/web/src/config/websocket_param.json', 'w', encoding='utf-8') as websocket_param_file_w:
            json.dump(websocket_param_data, websocket_param_file_w, indent=4, ensure_ascii=False)

    end_sub_path = f'{appdata_path}/rewardevents/web/src/config/endsub.json'

    if not os.path.isfile(end_sub_path):

        end_sub_list = []

        with open(f'{appdata_path}/rewardevents/web/src/config/endsub.json', 'w', encoding='utf-8') as endsub_file_w:
            json.dump(end_sub_list, endsub_file_w, indent=4, ensure_ascii=False)



get_files_list()
