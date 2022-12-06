import sys,os,platform
import get_key
import webview
import eel
import threading
import validators
import webbrowser
import obs_events
import time
import auth
import json
import pygame
import requests as req
import tkinter
import textwrap
import keyboard
import random
import yt_dlp
import simple_chat as chat_res
from screeninfo import get_monitors
import utils

from dotenv import load_dotenv
from pytube import Playlist, YouTube, Search
from io import BytesIO
from gtts import gTTS
from tkinter import filedialog as fd
from requests.structures import CaseInsensitiveDict
from random import randint

from discord_webhook import DiscordWebhook, DiscordEmbed

from uuid import UUID
from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch, AuthScope
from twitchAPI.oauth import refresh_access_token


extDataDir = os.getcwd()

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS

load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

clientid = os.getenv('CLIENTID')
clientsecret = get_key.start_apikey()

global caching, loaded_status, chat, window, twitch_api,bot_loaded

screen = get_monitors()[0]
chat_active = False
caching = 0
loaded_status = 0
bot_loaded = 0
maximized = 0
namelist = []

USERNAME, BROADCASTER_ID, BOTNAME, CODE, TOKENBOT, TOKEN, REFRESH_TOKEN = auth.auth_data()

def bot():
    global chat, bot_loaded

    if loaded_status == 1:
        data_res = {
            "type": "CONNSUCESS",
        }

        message_data_dump = json.dumps(data_res, ensure_ascii=False)
        eel.append_message(message_data_dump)

        chat = chat_res.Chat(channel=USERNAME, nickname=BOTNAME, oauth='oauth:' + TOKENBOT)
        chat.subscribe(command_fallback)
        bot_loaded = 1


@eel.expose
def loaded():
    global loaded_status

    loaded_status = 1

    return loaded_status


def messages_file_load(key):
    messages_file = open('web/src/messages/messages_file.json', "r", encoding='utf-8')
    messages_data = json.load(messages_file)

    message = messages_data[key]

    messages_file.close()

    return message


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)

    return text


@eel.expose
def get_auth_py(type_id):
    if type_id == 'USERNAME':
        type_id = USERNAME

    elif type_id == 'TOKEN':
        type_id = TOKEN

    elif type_id == 'BROADCASTER_ID':
        type_id = BROADCASTER_ID

    elif type_id == 'REFRESH_TOKEN':
        type_id = REFRESH_TOKEN

    elif type_id == 'CLIENTID':
        type_id = clientid

    elif type_id == 'CLIENTSECRET':
        type_id = clientsecret

    return type_id


@eel.expose
def start_auth_window(username, type_auth):
    def save_access_token_bot(code_received):

        out_file1 = open("web/src/auth/auth.json")
        data1 = json.load(out_file1)

        username_to_bot = data1['USERNAME']
        user_id = data1['BROADCASTER_ID']
        code_streamer_to_bot = data1['CODE']
        user_token = data1['TOKEN']
        user_refresh_token = data1['REFRESH_TOKEN']
        bot_username_to_bot = data1['BOTUSERNAME']

        data = {'USERNAME': username_to_bot, 'BROADCASTER_ID': user_id, 'CODE': code_streamer_to_bot,
                'TOKEN': user_token, 'REFRESH_TOKEN': user_refresh_token, 'TOKENBOT': code_received,
                'BOTUSERNAME': bot_username_to_bot}

        out_file = open("web/src/auth/auth.json", "w")
        json.dump(data, out_file, indent=6)
        out_file.close()

        window_auth.load_html("<!DOCTYPE html>\n"
                              "<html lang='pt'>\n"
                              "<head>\n"
                              "<script type='text/javascript'>window.history.pushState('', '', '/');</script>"
                              "<meta charset='UTF-8'>\n"
                              "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                              "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css"
                              "/bootstrap.min.css'>\n "
                              "<title>Document</title>\n"
                              "</head>\n"
                              "<style>"
                              "html, body {height: 100%;}\n"
                              ".container {height: 100%;}\n"
                              "</style>\n"
                              "<body style='background-color: #191919;'>"
                              "<div class='container'>\n<div class='row h-100'>\n"
                              "<div class='col-sm-12 my-auto'>\n"
                              "<div class='card card-block w-50 mx-auto text-center' style='background-color: "
                              "#4b1a6a;color:azure'>\n "
                              "<div class='card-body'>\n<h1 class='card-title'>Sucesso!</h5>\n<p "
                              "class='card-text'>Pode fechar esta pagina.</p>\n "
                              "</div>\n</div>\n</div>\n</div>\n</div>\n</body>\n</html>")

        eel.auth_user_sucess('bot')

    def save_access_token(code_received):

        url_auth = "https://id.twitch.tv/oauth2/token"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        param = f"client_id={clientid}&client_secret={clientsecret}&code={code_received}"
        data_token = param + "&grant_type=authorization_code&redirect_uri=http://localhost:5555"

        resp_token = req.post(url_auth, headers=headers, data=data_token)
        resp_token_data = json.loads(resp_token.text)

        access_token = resp_token_data['access_token']
        refresh_token = resp_token_data['refresh_token']

        out_file1 = open("web/src/auth/auth.json")
        data1 = json.load(out_file1)

        username_token = data1['USERNAME']

        time.sleep(3)

        twitch_api_auth = Twitch(clientid, clientsecret)

        scopes = [
            AuthScope.USER_READ_SUBSCRIPTIONS,
            AuthScope.USER_READ_EMAIL,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
            AuthScope.MODERATION_READ,
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.CLIPS_EDIT,
            AuthScope.CHAT_EDIT,
            AuthScope.CHAT_READ
        ]

        twitch_api_auth.set_user_authentication(access_token, scopes, refresh_token)

        user_id = twitch_api_auth.get_users(logins=[username_token])
        user_id_resp = user_id['data'][0]['id']

        data = {'USERNAME': username_token, 'BROADCASTER_ID': user_id_resp, 'CODE': code_received,
                'TOKEN': access_token, 'REFRESH_TOKEN': refresh_token, 'TOKENBOT': '', 'BOTUSERNAME': ''}

        out_file = open("web/src/auth/auth.json", "w")
        json.dump(data, out_file, indent=6)
        out_file.close()

        window_auth.load_html("<!DOCTYPE html>\n"
                              "<html lang='pt'>\n"
                              "<head>\n"
                              "<script type='text/javascript'>window.history.pushState('', '', '/');</script>"
                              "<meta charset='UTF-8'>\n"
                              "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                              "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css"
                              "/bootstrap.min.css'>\n "
                              "<title>Document</title>\n"
                              "</head>\n"
                              "<style>"
                              "html, body {height: 100%;}\n"
                              ".container {height: 100%;}\n"
                              "</style>\n"
                              "<body style='background-color: #191919;'>"
                              "<div class='container'>\n<div class='row h-100'>\n"
                              "<div class='col-sm-12 my-auto'>\n"
                              "<div class='card card-block w-50 mx-auto text-center' style='background-color: "
                              "#4b1a6a;color:azure'>\n "
                              "<div class='card-body'>\n<h1 class='card-title'>Sucesso!</h5>\n<p "
                              "class='card-text'>Pode fechar esta pagina.</p>\n "
                              "</div>\n</div>\n</div>\n</div>\n</div>\n</body>\n</html>")

        eel.auth_user_sucess('streamer')

    def save_access_token_as_bot(code_received):

        url_auth = "https://id.twitch.tv/oauth2/token"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        param_bot = f"client_id={clientid}&client_secret={clientsecret}&code={code_received}"
        data_token = param_bot + "&grant_type=authorization_code&redirect_uri=http://localhost:5555"

        resp_token = req.post(url_auth, headers=headers, data=data_token)
        resp_token_data = json.loads(resp_token.text)

        access_token = resp_token_data['access_token']
        refresh_token = resp_token_data['refresh_token']

        out_file1 = open("web/src/auth/auth.json")
        data1 = json.load(out_file1)

        username_as_bot = data1['USERNAME']

        time.sleep(3)

        twitch_api_auth = Twitch(clientid, clientsecret)

        scopes = [
            AuthScope.USER_READ_SUBSCRIPTIONS,
            AuthScope.USER_READ_EMAIL,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
            AuthScope.MODERATION_READ,
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.CLIPS_EDIT,
            AuthScope.CHAT_EDIT,
            AuthScope.CHAT_READ
        ]

        twitch_api_auth.set_user_authentication(access_token, scopes, refresh_token)

        user_id = twitch_api_auth.get_users(logins=[username])

        user_id_resp = user_id['data'][0]['id']
        data = {'USERNAME': username_as_bot, 'BROADCASTER_ID': user_id_resp, 'CODE': code_received,
                'TOKEN': access_token, 'REFRESH_TOKEN': refresh_token, 'TOKENBOT': access_token,
                'BOTUSERNAME': username}

        out_file = open("web/src/auth/auth.json", "w")
        json.dump(data, out_file, indent=6)
        out_file.close()

        window_auth.load_html("<!DOCTYPE html>\n"
                              "<html lang='pt'>\n"
                              "<head>\n"
                              "<script type='text/javascript'>window.history.pushState('', '', '/');</script>"
                              "<meta charset='UTF-8'>\n"
                              "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                              "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css"
                              "/bootstrap.min.css'>\n "
                              "<title>Document</title>\n"
                              "</head>\n"
                              "<style>"
                              "html, body {height: 100%;}\n"
                              ".container {height: 100%;}\n"
                              "</style>\n"
                              "<body style='background-color: #191919;'>"
                              "<div class='container'>\n<div class='row h-100'>\n"
                              "<div class='col-sm-12 my-auto'>\n"
                              "<div class='card card-block w-50 mx-auto text-center' style='background-color: "
                              "#4b1a6a;color:azure'>\n "
                              "<div class='card-body'>\n<h1 class='card-title'>Sucesso!</h5>\n<p "
                              "class='card-text'>Pode fechar esta pagina.</p>\n "
                              "</div>\n</div>\n</div>\n</div>\n</div>\n</body>\n</html>")

        eel.auth_user_sucess('streamer_as_bot')

    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]

        except ValueError:

            return ""

    def on_loaded():

        uri = window_auth.get_current_url()
        try:

            if type_auth == 'bot':
                access_token = find_between(uri, '#access_token=', '&')
            else:
                access_token = find_between(uri, '?code=', '&')

            if len(access_token) > 29:

                if type_auth == 'bot':

                    save_access_token_bot(access_token)

                elif type_auth == 'streamer':

                    save_access_token(access_token)

                elif type_auth == 'streamer_as_bot':

                    save_access_token_as_bot(access_token)


        except Exception as e:
            print(e)
            pass

    redirect_uri = "http://localhost:5555"
    twitch_prefix = "https://api.twitch.tv/kraken/"
    scope = "clips:edit+user:read:email+chat:edit+chat:read+channel:read:redemptions+moderation:read+channel:read:subscriptions+user:read:subscriptions "

    oauth_uri = f"{twitch_prefix}oauth2/authorize?response_type=code&force_verify=true&client_id={clientid}&redirect_uri={redirect_uri}&scope={scope} "

    oauth_uri_bot = f"{twitch_prefix}oauth2/authorize?response_type=token&force_verify=true&client_id={clientid}&redirect_uri={redirect_uri}&scope={scope}"

    if type == 'streamer':

        streamer_name = username
        data_user = {'USERNAME': streamer_name.lower(), 'BROADCASTER_ID': '', 'CODE': '', 'TOKEN': '',
                     'REFRESH_TOKEN': '', 'TOKENBOT': '', 'BOTUSERNAME': ''}

        auth_file_user = open("web/src/auth/auth.json", "w", encoding='utf-8')
        json.dump(data_user, auth_file_user, indent=6)
        auth_file_user.close()

        window_auth = webview.create_window('Auth', '')
        window_auth.load_url(oauth_uri)

        window_auth.events.loaded += on_loaded

    elif type == 'bot':

        auth_file_bot_load = open("web/src/auth/auth.json")
        data_bot_load = json.load(auth_file_bot_load)

        username_streamer = data_bot_load['USERNAME']
        user_id_streamer = data_bot_load['BROADCASTER_ID']
        code_streamer = data_bot_load['CODE']
        user_token_streamer = data_bot_load['TOKEN']
        user_refresh_token_streamer = data_bot_load['REFRESH_TOKEN']

        auth_file_bot_load.close()

        bot_username = username
        data_bot_save = {'USERNAME': username_streamer, 'BROADCASTER_ID': user_id_streamer, 'CODE': code_streamer,
                         'TOKEN': user_token_streamer, 'REFRESH_TOKEN': user_refresh_token_streamer, 'TOKENBOT': '',
                         'BOTUSERNAME': bot_username.lower()}

        auth_file_bot = open("web/src/auth/auth.json", "w")
        json.dump(data_bot_save, auth_file_bot, indent=6)
        auth_file_bot.close()

        window_auth = webview.create_window('Auth', '')
        window_auth.load_url(oauth_uri_bot)

        window_auth.events.loaded += on_loaded

    elif type == 'streamer_as_bot':

        streamer_name = username
        data_user = {'USERNAME': streamer_name.lower(), 'BROADCASTER_ID': '', 'CODE': '', 'TOKEN': '',
                     'REFRESH_TOKEN': '', 'TOKENBOT': '', 'BOTUSERNAME': streamer_name.lower()}

        auth_file_user = open("web/src/auth/auth.json", "w", encoding='utf-8')
        json.dump(data_user, auth_file_user, indent=6)
        auth_file_user.close()

        window_auth = webview.create_window('Auth', '')
        window_auth.load_url(oauth_uri)

        window_auth.events.loaded += on_loaded


@eel.expose
def close(mode):
    if mode == 'auth':

        window.destroy()
        sys.exit(0)

    elif mode == 'normal':

        window.destroy()
        sys.exit(0)


@eel.expose
def minimize():
    window.minimize()


@eel.expose
def maximize():
    global maximized

    if maximized == 0:

        maximized = 1

        window.resize(screen.width, screen.height)
        window.move(0, 0)

    elif maximized == 1:

        maximized = 0

        window.resize(1200, 680)


@eel.expose
def logout_auth():
    data = {'USERNAME': '', 'BROADCASTER_ID': '', 'CODE': '', 'TOKEN': '', 'REFRESH_TOKEN': '', 'CODEBOT': '',
            'TOKENBOT': '', 'REFRESH_TOKENBOT': '', 'BOTUSERNAME': ''}

    logout_file = open("web/src/auth/auth.json", "w")
    json.dump(data, logout_file, indent=6)
    logout_file.close()


@eel.expose
def get_user_follow():
    file_follows = open('web/src/config/follow.txt', 'r+', encoding='utf-8')
    follow_name = file_follows.read()
    file_follows.close()

    try:

        data_follow = twitch_api.get_users_follows(to_id=BROADCASTER_ID, first=1)

        last_follow_name = data_follow['data'][0]['from_name']

        if follow_name != last_follow_name:
            file_follows = open('web/src/config/follow.txt', 'w', encoding='utf-8')
            file_follows.write(last_follow_name)
            file_follows.close()

        return last_follow_name

    except Exception as e:

        utils.error_log(e)
        return follow_name


@eel.expose
def get_spec():
    if TOKEN and TOKENBOT:

        try:

            data_count = twitch_api.get_streams(user_login=[USERNAME])
            data_count_keys = data_count['data']
            name_last_folow = get_user_follow()

            timer_data_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
            timer_data = json.load(timer_data_file)

            message_key = timer_data['LAST']
            message_list = timer_data['MESSAGES']

            if message_key in message_list.keys():
                last_timer = message_list[message_key]
            else:
                last_timer = 'Nenhuma mensagem enviada'

            if not data_count_keys:

                data_time = {
                    'specs': 'Offline',
                    'time': 'Offline',
                    'follow': name_last_folow,
                    'last_timer': last_timer
                }

                data_time_dump = json.dumps(data_time, ensure_ascii=False)

                return data_time_dump


            else:

                count = data_count['data'][0]['viewer_count']
                started = data_count['data'][0]['started_at']

                time_in_live = utils.calculate_time(started)

                data_time = {
                    'specs': count,
                    'time': time_in_live,
                    'follow': name_last_folow,
                    'last_timer': last_timer
                }

                data_time_dump = json.dumps(data_time, ensure_ascii=False)
                return data_time_dump

        except Exception as e:

            utils.error_log(e)

            data_time = {
                'specs': 'Offline',
                'time': 'Offline',
                'follow': '',
                'last_timer': ''
            }

            data_time_dump = json.dumps(data_time, ensure_ascii=False)

            return data_time_dump

    else:
        return 'Offline'


@eel.expose
def profile_info():
    if TOKEN and TOKENBOT:
        user = twitch_api.get_users(logins=[USERNAME])

        resp_user_id = user['data'][0]['id']
        resp_display_name = user['data'][0]['display_name']
        resp_login_name = user['data'][0]['login']
        resp_email = user['data'][0]['email']
        resp_profile_img = user['data'][0]['profile_image_url']

        profile_img = req.get(resp_profile_img).content

        with open('web/src/profile.png', 'wb') as profile_image:
            profile_image.write(profile_img)
            profile_image.close()

        data_auth = {
            "user_id": resp_user_id,
            "display_name": resp_display_name,
            "login_name": resp_login_name,
            "email": resp_email
        }

        data_auth_json = json.dumps(data_auth, ensure_ascii=False)

        return data_auth_json


@eel.expose
def get_redeem():
    list_titles = {"redeem": []}
    path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
    path = json.load(path_file)

    path_counter_file = open('web/src/counter/config.json', 'r', encoding='utf-8')
    path_counter = json.load(path_counter_file)

    counter_redeem = path_counter['redeem']

    path_giveaway_file = open('web/src/giveaway/config.json', 'r', encoding='utf-8')
    path_giveaway = json.load(path_giveaway_file)

    giveaway_redeem = path_giveaway['redeem']

    list_rewards = twitch_api.get_custom_reward(broadcaster_id=BROADCASTER_ID)
    for indx in list_rewards['data'][0:]:

        if indx['title'] not in path and indx['title'] != giveaway_redeem and indx['title'] != counter_redeem:
            list_titles["redeem"].append(indx['title'])

    list_titles_dump = json.dumps(list_titles, ensure_ascii=False)

    path_giveaway_file.close()
    path_counter_file.close()
    path_file.close()
    return list_titles_dump


@eel.expose
def get_redeem_created():
    list_titles = {"redeem": []}
    path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
    path = json.load(path_file)

    for key in path:
        list_titles["redeem"].append(key)

    list_titles_dump = json.dumps(list_titles, ensure_ascii=False)

    path_file.close()
    return list_titles_dump


@eel.expose
def get_edit_type_py(redeem_name):
    path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
    path = json.load(path_file)

    redeem_type = path[redeem_name]['type']
    path_file.close()

    return redeem_type


@eel.expose
def select_file_py():
    filetypes = (
        ('audio files', '*.mp3'),
        ('All files', '*.*')
    )

    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    folder = fd.askopenfilename(
        initialdir='web/src/files',
        filetypes=filetypes)

    return folder


@eel.expose
def update_scene_obs():
    scenes = obs_events.get_scenes()

    return scenes


@eel.expose
def get_filters_obs(source):
    filters = obs_events.get_filters(source)
    return filters


@eel.expose
def get_sources_obs():
    sources = obs_events.get_sources()

    return sources


def create_command_redeem(data):
    command_value = data['command_value']
    redeem_value = data['redeem_value']
    user_level_value = data['user_level_value']

    old_data_command = open('web/src/config/commands.json', 'r', encoding='utf-8')
    new_data_command = json.load(old_data_command)

    new_data_command[command_value.lower()] = {'redeem': redeem_value, 'user_level': user_level_value}
    old_data_command.close()

    old_data_write_command = open('web/src/config/commands.json', 'w', encoding='utf-8')
    json.dump(new_data_command, old_data_write_command, indent=6, ensure_ascii=False)

    old_data_write_command.close()


@eel.expose
def create_action_save(data, type_id):
    data_receive = json.loads(data)

    try:

        if type_id == 'audio':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            audio_path = data_receive['audio_path']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            old_data = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {

                'type': 'sound',
                'path': audio_path,
                'command': command_value.lower(),
                'send_response': send_response,
                'chat_response': chat_response
            }

            old_data.close()

            old_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)

            old_data_write.close()

            if command_value != "":
                create_command_redeem(data_receive)

        elif type_id == 'tts':

            redeem_value = data_receive['redeem_value']
            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            characters = data_receive['characters']
            user_level_value = data_receive['user_level_value']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            old_data = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {

                'type': 'tts',
                'send_response': send_response,
                'chat_response': chat_response,
                'command': command_value.lower(),
                'characters': characters

            }

            old_data.close()

            old_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()
            if command_value != "":
                old_data_command = open('web/src/config/prefix_tts.json', 'r', encoding='utf-8')
                new_data_command = json.load(old_data_command)

                new_data_command['command'] = command_value.lower()
                new_data_command['redeem'] = redeem_value
                new_data_command['user_level'] = user_level_value

                old_data.close()

                old_data_write_command = open('web/src/config/prefix_tts.json', 'w', encoding='utf-8')
                json.dump(new_data_command, old_data_write_command, indent=6, ensure_ascii=False)
                old_data_write_command.close()

        elif type_id == 'scene':

            redeem_value = data_receive['redeem_value']
            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']

            scene_name = data_receive['scene_name']
            time_to_return = data_receive['time']
            keep_scene_value = data_receive['keep_scene_value']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            if time_to_return == "":
                time_to_return = 0

            old_data = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {

                'type': 'scene',
                'send_response': send_response,
                'command': command_value.lower(),
                'chat_response': chat_response,
                'scene_name': scene_name,
                'keep': keep_scene_value,
                'time': int(time_to_return)
            }

            old_data.close()

            old_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()
            if command_value != "":
                create_command_redeem(data_receive)

        elif type_id == 'response':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']

            old_data = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {
                'type': 'response',
                'command': command_value.lower(),
                'chat_response': chat_response
            }

            old_data.close()

            old_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

            if command_value != "":
                create_command_redeem(data_receive)

        elif type_id == 'filter':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            filter_name = data_receive['filter_name']
            source_name = data_receive['source_name']
            time_showing = data_receive['time_showing']
            keep = data_receive['keep']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            if time_showing == "":
                time_showing = 0

            old_data = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {

                'type': 'filter',
                'source_name': source_name,
                'send_response': send_response,
                'chat_response': chat_response,
                'command': command_value.lower(),
                'filter': filter_name,
                'keep': keep,
                'time': int(time_showing)
            }

            old_data.close()

            old_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

            if command_value != "":
                create_command_redeem(data_receive)

        elif type_id == 'source':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            source_name = data_receive['source_name']
            time_showing = data_receive['time_showing']
            keep = data_receive['keep']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            if time_showing == "":
                time_showing = 0

            old_data = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {

                'type': 'source',
                'send_response': send_response,
                'chat_response': chat_response,
                'command': command_value.lower(),
                'source_name': source_name,
                'keep': keep,
                'time': int(time_showing)

            }

            old_data.close()

            old_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

            if command_value != "":
                create_command_redeem(data_receive)

        elif type_id == 'keypress':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            mode_press = data_receive['mode']

            key1 = data_receive['key1']
            key2 = data_receive['key2']
            key3 = data_receive['key3']
            key4 = data_receive['key4']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            key_data_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            key_data = json.load(key_data_file)

            if mode_press == 'mult':

                mult_press_times = data_receive['mult_press_times']
                mult_press_interval = data_receive['mult_press_interval']

                key_data[redeem_value] = {

                    'type': 'keypress',
                    'send_response': send_response,
                    'chat_response': chat_response,
                    'command': command_value.lower(),
                    'mode': mode_press,
                    'mult_press_times': int(mult_press_times),
                    'mult_press_interval': int(mult_press_interval),
                    'key1': key1,
                    'key2': key2,
                    'key3': key3,
                    'key4': key4
                }

            elif mode_press == 're':

                re_press_time = data_receive['re_press_time']

                key_data[redeem_value] = {

                    'type': 'keypress',
                    'send_response': send_response,
                    'chat_response': chat_response,
                    'command': command_value.lower(),
                    'mode': mode_press,
                    're_press_time': int(re_press_time),
                    'key1': key1,
                    'key2': key2,
                    'key3': key3,
                    'key4': key4
                }

            elif mode_press == 'keep':

                keep_press_time = data_receive['keep_press_time']

                key_data[redeem_value] = {

                    'type': 'keypress',
                    'send_response': send_response,
                    'chat_response': chat_response,
                    'command': command_value.lower(),
                    'mode': mode_press,
                    'keep_press_time': int(keep_press_time),
                    'key1': key1,
                    'key2': key2,
                    'key3': key3,
                    'key4': key4
                }

            key_data_file.close()

            key_data_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(key_data, key_data_file_write, indent=6, ensure_ascii=False)
            key_data_file_write.close()

            if command_value != "":
                create_command_redeem(data_receive)

        elif type_id == 'clip':

            command_value = data_receive['command_value']
            redeem_value = data_receive['redeem_value']

            old_data = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {'type': 'clip', 'command': command_value.lower(), }
            old_data.close()

            old_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)

            if command_value != "":
                create_command_redeem(data_receive)

            old_data_write.close()

        elif type_id == 'delete':

            data = data_receive['redeem']

            data_event_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            data_event = json.load(data_event_file)

            command = data_event[data]['command']

            data_command_file = open('web/src/config/commands.json', 'r', encoding='utf-8')
            data_command = json.load(data_command_file)

            if command in data_command.keys():
                del data_command[command]

                data_command_file.close()

                command_data_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(data_command, command_data_write, indent=6, ensure_ascii=False)
                command_data_write.close()
            else:
                data_command_file.close()

            del data_event[data]
            data_event_file.close()

            event_data_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(data_event, event_data_write, indent=6, ensure_ascii=False)

            event_data_write.close()

        eel.modal_actions('sucess-create')

    except Exception as e:

        utils.error_log(e)

        eel.modal_actions('error-create')


@eel.expose
def commands_py(type_rec, data_receive):

    if type_rec == 'create':

        try:

            data = json.loads(data_receive)
            command = data['new_command']
            message = data['new_message']
            user_level_check = data['new_user_level']

            old_data_command = open('web/src/config/simple_commands.json', 'r', encoding='utf-8')
            new_data_command = json.load(old_data_command)

            new_data_command[command.lower()] = {
                'response': message,
                'user_level': user_level_check
            }

            old_data_command.close()

            old_data_write_command = open('web/src/config/simple_commands.json', 'w', encoding='utf-8')
            json.dump(new_data_command, old_data_write_command, indent=6, ensure_ascii=False)
            old_data_write_command.close()

            eel.command_modal('sucess-command')

        except Exception as e:
            utils.error_log(e)

            eel.command_modal('error-command')

    elif type_rec == 'edit':

        try:
            data = json.loads(data_receive)

            old_command = data['old_command']
            new_command = data['edit_command']
            new_message = data['edit_message']
            user_level = data['edit_user_level']

            command_data_file = open('web/src/config/simple_commands.json', 'r', encoding='utf-8')
            command_data = json.load(command_data_file)

            del command_data[old_command]
            command_data[new_command] = {
                "response": new_message,
                "user_level": user_level
            }

            command_data_file.close()

            old_data_write = open('web/src/config/simple_commands.json', 'w', encoding='utf-8')
            json.dump(command_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

            eel.command_modal('sucess-command')

        except Exception as e:
            utils.error_log(e)
            eel.command_modal('error-command')

    elif type_rec == 'delete':

        try:
            old_data = open('web/src/config/simple_commands.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            del new_data[data_receive]
            old_data.close()

            old_data_write = open('web/src/config/simple_commands.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

            eel.command_modal('sucess-command')

        except Exception as e:
            utils.error_log(e)
            eel.command_modal('error-command')

    elif type_rec == 'get_info':
        try:
            command_file = open('web/src/config/simple_commands.json', 'r', encoding='utf-8')
            command_data = json.load(command_file)

            message = command_data[data_receive]['response']
            user_level = command_data[data_receive]['user_level']

            data = {
                'edit_command': data_receive,
                'edit_message': message,
                'edit_level': user_level,
            }

            command_file.close()
            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump

        except Exception as e:
            utils.error_log(e)

    elif type_rec == 'get_list':

        try:

            old_data = open('web/src/config/simple_commands.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            list_commands = []

            for key in new_data:
                list_commands.append(key)

            list_commands_dump = json.dumps(list_commands, ensure_ascii=False)

            old_data.close()
            return list_commands_dump

        except Exception as e:
            utils.error_log(e)

    elif type_rec == 'get_delay':

        try:
            time_delay_file = open('web/src/config/commands_config.json')
            time_delay_data = json.load(time_delay_file)

            command_delay = time_delay_data['delay_config']
            time_delay_file.close()

            time_delay_write = open('web/src/config/commands_config.json', 'w', encoding='utf-8')
            json.dump(time_delay_data, time_delay_write, indent=6, ensure_ascii=False)
            time_delay_write.close()

            time_delay_file_tts = open('web/src/config/prefix_tts.json')
            time_delay_data_tts = json.load(time_delay_file_tts)

            tts_delay = time_delay_data_tts['delay_config']
            time_delay_file_tts.close()

            time_delay_write_tts = open('web/src/config/prefix_tts.json', 'w', encoding='utf-8')
            json.dump(time_delay_data_tts, time_delay_write_tts, indent=6, ensure_ascii=False)
            time_delay_write_tts.close()

            data = {
                "command_delay": command_delay,
                "tts_delay": tts_delay
            }

            delay_data = json.dumps(data, ensure_ascii=False)

            return delay_data

        except Exception as e:
            utils.error_log(e)

    elif type_rec == 'edit_delay':

        try:
            data = json.loads(data_receive)

            value_commands = data['value_commands']
            value_tts = data['value_tts']

            time_delay_file = open('web/src/config/commands_config.json')
            time_delay_data = json.load(time_delay_file)

            time_delay_data['delay_config'] = int(value_commands)
            time_delay_file.close()

            time_delay_write = open('web/src/config/commands_config.json', 'w', encoding='utf-8')
            json.dump(time_delay_data, time_delay_write, indent=6, ensure_ascii=False)
            time_delay_write.close()

            time_delay_file_tts = open('web/src/config/prefix_tts.json')
            time_delay_data_tts = json.load(time_delay_file_tts)

            time_delay_data_tts['delay_config'] = int(value_tts)
            time_delay_file_tts.close()

            time_delay_write_tts = open('web/src/config/prefix_tts.json', 'w', encoding='utf-8')
            json.dump(time_delay_data_tts, time_delay_write_tts, indent=6, ensure_ascii=False)
            time_delay_write_tts.close()

            eel.command_modal('sucess-command')
        except Exception as e:
            utils.error_log(e)
            eel.command_modal('error-command')


@eel.expose
def get_timer_info():
    
    timer_data_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
    timer_data = json.load(timer_data_file)

    message_file_get = open('web/src/config/commands_config.json', 'r', encoding="utf-8")
    message_data_get = json.load(message_file_get)

    status_timer = message_data_get['STATUS_TIMER']
    timer_delay_min = timer_data['TIME']
    timer_delay_max = timer_data['TIME_MAX']
    messages_list = timer_data['MESSAGES']

    data = {
        "delay_min": timer_delay_min,
        "delay_max": timer_delay_max,
        "messages": messages_list,
        "status": status_timer
    }

    timer_data_file.close()
    message_file_get.close()

    timer_data = json.dumps(data, ensure_ascii=False)

    return timer_data


@eel.expose
def get_message_timer(message_id):
    timer_data_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
    timer_data = json.load(timer_data_file)

    message = timer_data['MESSAGES'][message_id]

    timer_data_file.close()

    return message


@eel.expose
def edit_timer(key, message):
    try:
        timer_data_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
        timer_data = json.load(timer_data_file)

        timer_data['MESSAGES'][key] = message
        timer_data_file.close()

        timer_data_file_w = open('web/src/config/timer.json', 'w', encoding='utf-8')
        json.dump(timer_data, timer_data_file_w, indent=6, ensure_ascii=False)
        timer_data_file_w.close()

        eel.timer_modal('sucess-timer')

    except Exception as e:

        utils.error_log(e)

        eel.timer_modal('error-timer')


@eel.expose
def add_timer(message):
    try:

        timer_data_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
        timer_data = json.load(timer_data_file)

        timer_message = timer_data['MESSAGES']

        if not timer_message:

            keytoadd = 1

        else:
            key = list(timer_message.keys())[-1]
            keytoadd = int(key) + 1

        timer_data['MESSAGES'][str(keytoadd)] = message

        timer_data_file.close()

        old_data_write = open('web/src/config/timer.json', 'w', encoding='utf-8')
        json.dump(timer_data, old_data_write, indent=6, ensure_ascii=False)

        old_data_write.close()

        eel.timer_modal('sucess-timer')

    except Exception as e:

        utils.error_log(e)

        eel.timer_modal('error-timer')


@eel.expose
def del_timer(message_key):
    try:

        message_del_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
        message_del_data = json.load(message_del_file)

        del message_del_data['MESSAGES'][message_key]

        message_del_file.close()

        message_del_file_write = open('web/src/config/timer.json', 'w', encoding='utf-8')
        json.dump(message_del_data, message_del_file_write, indent=6, ensure_ascii=False)
        message_del_file_write.close()

        eel.timer_modal('sucess-timer')

    except Exception as e:

        utils.error_log(e)

        eel.timer_modal('error-timer')


@eel.expose
def edit_delay_timer(min_time, max_time):
    try:

        message_del_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
        message_del_data = json.load(message_del_file)

        message_del_data['TIME'] = int(min_time)
        message_del_data['TIME_MAX'] = int(max_time)

        message_del_file.close()

        message_del_file_write = open('web/src/config/timer.json', 'w', encoding='utf-8')
        json.dump(message_del_data, message_del_file_write, indent=6, ensure_ascii=False)
        message_del_file_write.close()

        eel.timer_modal('sucess-timer')

    except Exception as e:

        utils.error_log(e)

        eel.timer_modal('error-timer')


@eel.expose
def timer_status_save(status):
    message_file = open('web/src/config/commands_config.json', 'r', encoding="utf-8")
    message_data = json.load(message_file)

    message_data['STATUS_TIMER'] = status

    message_file.close()

    old_data_write = open('web/src/config/commands_config.json', 'w', encoding="utf-8")
    json.dump(message_data, old_data_write, indent=6, ensure_ascii=False)
    old_data_write.close()


@eel.expose
def get_obs_conn_info_py():
    obs_conn_file = open('web/src/config/obs.json', 'r', encoding='utf-8')
    obs_conn_file_data = json.load(obs_conn_file)

    host = obs_conn_file_data['OBS_HOST']
    port = obs_conn_file_data['OBS_PORT']
    password = obs_conn_file_data['OBS_PASSWORD']
    auto_conn = obs_conn_file_data['OBS_TEST_CON']

    data = {
        "host": host,
        "port": port,
        "password": password,
        "auto_conn": auto_conn
    }

    obs_conn_file.close()

    conm_data = json.dumps(data, ensure_ascii=False)

    return conm_data


@eel.expose
def save_obs_conn_py(data_receive):
    try:

        data = json.loads(data_receive)

        host = data['host']
        port = data['port']
        password = data['pass']
        auto_conn = data['conn']

        data_save = {
            'OBS_HOST': host,
            'OBS_PORT': port,
            'OBS_PASSWORD': password,
            'OBS_TEST_CON': auto_conn
        }

        out_file = open("web/src/config/obs.json", "w", encoding='utf-8')
        json.dump(data_save, out_file, indent=6, ensure_ascii=False)
        out_file.close()

        eel.config_modal('sucess-config-obs-conn')

    except Exception as e:

        utils.error_log(e)

        eel.config_modal('error-config-obs-conn')


@eel.expose
def save_obs_not_py(data_receive):
    try:

        data = json.loads(data_receive)

        active = data['not_enabled']
        music_active = data['not_music']
        source = data['source_name']
        time_showing_not = data['time_showing_not']

        data_save = {

            'HTML_PLAYER_ACTIVE': music_active,
            'HTML_ACTIVE': active,
            'HTML_TITLE': source,
            'HTML_TIME': int(time_showing_not),
        }

        out_file = open("web/src/config/notfic.json", "w", encoding='utf-8')
        json.dump(data_save, out_file, indent=6, ensure_ascii=False)
        out_file.close()

        eel.config_modal('sucess-config-obs-not')

    except Exception as e:

        utils.error_log(e)

        eel.config_modal('error-config-obs-not')


@eel.expose
def get_messages_config():

    message_file_get = open('web/src/config/commands_config.json', 'r', encoding="utf-8")
    message_data_get = json.load(message_file_get)

    status_tts = message_data_get['STATUS_TTS'],
    status_commands = message_data_get['STATUS_COMMANDS']
    status_response = message_data_get['STATUS_RESPONSE']
    status_delay = message_data_get['STATUS_ERROR_TIME']
    status_clip = message_data_get['STATUS_CLIP']
    status_permission = message_data_get['STATUS_ERROR_USER']
    status_message = message_data_get['STATUS_BOT']
    status_message_music = message_data_get['STATUS_MUSIC']
    status_message_music_confirm = message_data_get['STATUS_MUSIC_CONFIRM']
    status_message_music_error = message_data_get['STATUS_MUSIC_ERROR']

    message_file_get.close()

    messages_data_get = {

        "STATUS_TTS": status_tts,
        "STATUS_COMMANDS": status_commands,
        "STATUS_RESPONSE": status_response,
        "STATUS_ERROR_TIME": status_delay,
        "STATUS_CLIP": status_clip,
        "STATUS_ERROR_USER": status_permission,
        "STATUS_BOT": status_message,
        "STATUS_MUSIC": status_message_music,
        "STATUS_MUSIC_CONFIRM": status_message_music_confirm,
        "STATUS_MUSIC_ERROR": status_message_music_error
    }

    messages_data_dump = json.dumps(messages_data_get, ensure_ascii=False)

    return messages_data_dump


@eel.expose
def save_messages_config(data_receive):
    data = json.loads(data_receive)

    status_tts = data['status_tts']
    status_commands = data['status_commands']
    status_response = data['status_response']
    status_delay = data['status_delay']
    status_clip = data['status_clip']
    status_permission = data['status_permission']
    status_timer = data['status_timer']
    status_message = data['status_message']
    status_error_music = data['status_error_music']
    status_next = data['status_next']
    status_music = data['status_music']

    try:

        old_message_file = open('web/src/config/commands_config.json', 'r', encoding="utf-8")
        old_message_data = json.load(old_message_file)

        old_message_file.close()

        old_message_data['STATUS_TTS'] = status_tts
        old_message_data['STATUS_COMMANDS'] = status_commands
        old_message_data['STATUS_RESPONSE'] = status_response
        old_message_data['STATUS_ERROR_TIME'] = status_delay
        old_message_data['STATUS_CLIP'] = status_clip
        old_message_data['STATUS_ERROR_USER'] = status_permission
        old_message_data['STATUS_TIMER'] = status_timer
        old_message_data['STATUS_BOT'] = status_message
        old_message_data['STATUS_MUSIC'] = status_next
        old_message_data['STATUS_MUSIC_CONFIRM'] = status_music
        old_message_data['STATUS_MUSIC_ERROR'] = status_error_music

        old_data_write = open('web/src/config/commands_config.json', 'w', encoding="utf-8")
        json.dump(old_message_data, old_data_write, indent=6, ensure_ascii=False)
        old_data_write.close()

        eel.modal_messages_config('sucess')

    except Exception as e:

        utils.error_log(e)

        eel.modal_messages_config('error')


@eel.expose
def get_giveaway_info():
    giveaway_file = open('web/src/giveaway/config.json', 'r', encoding='utf-8')
    giveaway_data = json.load(giveaway_file)

    giveaway_name = giveaway_data['name']
    giveaway_level = giveaway_data['user_level']
    giveaway_enable = giveaway_data['enable']
    giveaway_clear = giveaway_data['clear']
    giveaway_redeem = giveaway_data['redeem']

    giveaway_file.close()

    data = {
        "giveaway_name": giveaway_name,
        "giveaway_level": giveaway_level,
        "giveaway_clear": giveaway_clear,
        "giveaway_enable": giveaway_enable,
        "giveaway_redeem": giveaway_redeem
    }

    data_dump = json.dumps(data, ensure_ascii=False)

    return data_dump


@eel.expose
def save_giveaway_config_py(data_receive):
    data = json.loads(data_receive)

    giveaway_name = data['giveaway_name']
    giveaway_level = data['giveaway_user_level']
    giveaway_enable = data['giveaway_enable']
    giveaway_clear = data['giveaway_clear_check']
    giveaway_redeem = data['giveaway_redeem']

    try:

        giveaway_data_new = {
            "name": giveaway_name,
            "redeem": giveaway_redeem,
            "user_level": giveaway_level,
            "clear": giveaway_clear,
            "enable": giveaway_enable,
        }

        old_data_write = open('web/src/giveaway/config.json', 'w', encoding="utf-8")
        json.dump(giveaway_data_new, old_data_write, indent=6, ensure_ascii=False)
        old_data_write.close()

        eel.giveaway_modal_show('giveaway-sucess-save', 'none')

    except Exception as e:

        utils.error_log(e)

        eel.giveaway_modal_show('giveway-error-save', 'none')


@eel.expose
def save_giveaway_commands_py(data_receive):
    data = json.loads(data_receive)

    execute_giveaway_comm = data['execute_giveaway']
    user_check_giveaway_comm = data['check_user_giveaway']
    self_check_giveaway_comm = data['self_check_giveaway']
    clear_giveaway_comm = data['clear_giveaway']
    add_user_giveaway_comm = data['add_user_giveaway']

    try:

        giveaway_data_new = {
            "execute_giveaway": execute_giveaway_comm,
            "clear_giveaway": user_check_giveaway_comm,
            "check_name": self_check_giveaway_comm,
            "check_self_name": clear_giveaway_comm,
            "add_user": add_user_giveaway_comm,
        }

        old_data_write = open('web/src/giveaway/commands.json', 'w', encoding="utf-8")
        json.dump(giveaway_data_new, old_data_write, indent=6, ensure_ascii=False)
        old_data_write.close()

        eel.giveaway_modal_show('giveaway-sucess-save', 'none')

    except Exception as e:

        utils.error_log(e)

        eel.giveaway_modal_show('giveway-error-save', 'none')


@eel.expose
def get_giveaway_commands():
    giveaway_commands_file = open('web/src/giveaway/commands.json', 'r', encoding='utf-8')
    giveaway_commands_data = json.load(giveaway_commands_file)

    execute_giveaway_get = giveaway_commands_data['execute_giveaway']
    user_check_giveaway_get = giveaway_commands_data['check_name']
    self_check_giveaway_get = giveaway_commands_data['check_self_name']
    clear_giveaway_get = giveaway_commands_data['clear_giveaway']
    add_user_giveaway_get = giveaway_commands_data['add_user']

    giveaway_commands_file.close()
    data = {

        "execute_giveaway": execute_giveaway_get,
        "user_check_giveaway": user_check_giveaway_get,
        "self_check_giveaway": self_check_giveaway_get,
        "clear_giveaway": clear_giveaway_get,
        "add_user_giveaway": add_user_giveaway_get
    }

    data_dump = json.dumps(data, ensure_ascii=False)

    return data_dump


@eel.expose
def get_giveaway_names():
    giveaway_commands_file = open('web/src/giveaway/names.json', 'r', encoding='utf-8')
    giveaway_commands_data = json.load(giveaway_commands_file)

    data_dump = json.dumps(giveaway_commands_data, ensure_ascii=False)

    giveaway_commands_file.close()

    return data_dump


@eel.expose
def execute_giveaway():
    try:
        giveaway_file = open('web/src/giveaway/config.json', 'r', encoding='utf-8')
        giveaway_data = json.load(giveaway_file)

        reset_give = giveaway_data['clear']
        giveaway_file.close()

        giveaway_name_file = open('web/src/giveaway/names.json', 'r', encoding='utf-8')
        giveaway_name_data = json.load(giveaway_name_file)

        name = random.choice(giveaway_name_data)
        giveaway_name_file.close()

        message_load_winner_giveaway = messages_file_load('giveaway_response_win')

        message_win = message_load_winner_giveaway.replace('{name}', name)
        if utils.send_message("RESPONSE"):
            chat.send(message_win)

        giveaway_backup_file = open('web/src/giveaway/backup.json', 'w', encoding="utf-8")
        json.dump(giveaway_name_data, giveaway_backup_file, indent=6, ensure_ascii=False)
        giveaway_backup_file.close()

        giveaway_result_file = open('web/src/giveaway/result.json', 'w', encoding="utf-8")
        json.dump(name, giveaway_result_file, indent=6, ensure_ascii=False)
        giveaway_backup_file.close()

        if reset_give == 1:
            reset_data = []

            giveaway_reset_file = open('web/src/giveaway/names.json', 'w', encoding="utf-8")
            json.dump(reset_data, giveaway_reset_file, indent=6, ensure_ascii=False)
            giveaway_reset_file.close()

        eel.giveaway_modal_show('giveway-winner', name)

    except Exception as e:

        utils.error_log(e)

        eel.giveaway_modal_show('giveway-error-execute')


@eel.expose
def clear_name_list():
    try:

        reset_data = []

        giveaway_reset_file = open('web/src/giveaway/names.json', 'w', encoding="utf-8")
        json.dump(reset_data, giveaway_reset_file, indent=6, ensure_ascii=False)
        giveaway_reset_file.close()

        eel.giveaway_modal_show('giveaway-clear-sucess', 'none')


    except Exception as e:
        utils.error_log(e)

        eel.giveaway_modal_show('giveaway-clear-error', 'none')


@eel.expose
def add_name_giveaway(new_name):
    try:
        giveaway_name_file = open('web/src/giveaway/names.json', 'r', encoding='utf-8')
        giveaway_name_data = json.load(giveaway_name_file)

        names = giveaway_name_data
        names.append(new_name)

        giveaway_name_file.close()

        giveaway_save_file = open('web/src/giveaway/names.json', 'w', encoding="utf-8")
        json.dump(names, giveaway_save_file, indent=6, ensure_ascii=False)
        giveaway_save_file.close()

        eel.giveaway_modal_show('giveaway-add-name', new_name)


    except Exception as e:
        utils.error_log(e)

        eel.giveaway_modal_show('giveaway-add-name-error', new_name)


@eel.expose
def counter(fun_id, redeem, commands, value):
    if fun_id == 'get_counter_redeem':
        counter_file = open('web/src/counter/config.json', 'r', encoding='utf-8')
        counter_data = json.load(counter_file)

        counter_commands_file = open('web/src/counter/commands.json', 'r', encoding='utf-8')
        counter_commands_data = json.load(counter_commands_file)

        with open("web/src/counter/counter.txt", "r") as counter_file_r:
            counter_file_r.seek(0)
            counter_value_get = counter_file_r.read()

        counter_command_reset = counter_commands_data['reset_counter']
        counter_command_set = counter_commands_data['set_counter']
        counter_command_check = counter_commands_data['check_counter']

        counter_redeem = counter_data['redeem']
        counter_file.close()
        counter_commands_file.close()

        data = {

            "redeem": counter_redeem,
            "value_counter": counter_value_get,
            "counter_command_reset": counter_command_reset,
            "counter_command_set": counter_command_set,
            "counter_command_check": counter_command_check,
        }

        counter_data_parse = json.dumps(data, ensure_ascii=False)

        return counter_data_parse

    if fun_id == "save_counter_redeem":

        try:

            data_save = {
                "redeem": redeem
            }

            counter_file_save = open('web/src/counter/config.json', 'w', encoding='utf-8')
            json.dump(data_save, counter_file_save, indent=6, ensure_ascii=False)
            counter_file_save.close()

            eel.counter_modal('save_redeem_sucess')

        except Exception as e:

            utils.error_log(e)

            eel.counter_modal('save_redeem_error')

    if fun_id == "save-counter-commands":

        data_received = json.loads(commands)

        try:
            counter_command_check_save = data_received['counter_command_check']
            counter_command_reset_save = data_received['counter_command_reset']
            counter_command_apply_save = data_received['counter_command_apply']

            commands_save = {
                "reset_counter": counter_command_reset_save,
                "set_counter": counter_command_apply_save,
                "check_counter": counter_command_check_save,
            }

            counter_file_save_commands = open('web/src/counter/commands.json', 'w', encoding='utf-8')
            json.dump(commands_save, counter_file_save_commands, indent=6, ensure_ascii=False)
            counter_file_save_commands.close()

            eel.counter_modal('save_commands_sucess')

        except Exception as e:

            utils.error_log(e)

            eel.counter_modal('save_commands_error')

    if fun_id == "set-counter-value":
        with open("web/src/counter/counter.txt", "w") as counter_file_w:
            counter_file_w.write(str(value))


@eel.expose
def responses_config(fun_id, response_key, message):
    if fun_id == 'get_response':

        responses_file = open('web/src/messages/messages_file.json', 'r', encoding='utf-8')
        responses_data = json.load(responses_file)

        response = responses_data[response_key]

        responses_file.close()
        return response

    elif fun_id == 'save_response':

        try:

            responses_file = open('web/src/messages/messages_file.json', 'r', encoding='utf-8')
            responses_data = json.load(responses_file)

            responses_data[response_key] = message

            responses_file.close()
            responses_file_w = open('web/src/messages/messages_file.json', 'w', encoding='utf-8')
            json.dump(responses_data, responses_file_w, indent=6, ensure_ascii=False)

            responses_file_w.close()
            eel.modal_responses('modal-sucess-response')

        except Exception as e:

            eel.modal_responses('modal-error-response')
            utils.error_log(e)


@eel.expose
def discord_config(data_discord_save, mode):
    if mode == 'save':

        try:

            data_discord_receive = json.loads(data_discord_save)

            url_webhook = data_discord_receive['webhook_url']
            url_webhook_edit = data_discord_receive['webhook_url_edit']
            embed_color = data_discord_receive['embed_color']
            embed_title = data_discord_receive['embed_title']
            embed_title_edit = data_discord_receive['embed_edit_title']
            embed_description = data_discord_receive['embed_description']
            status = data_discord_receive['webhook_enable']
            satus_edit = data_discord_receive['webhook_enable_edit']

            discord_data_save = {

                "url": url_webhook,
                "url_edit": url_webhook_edit,
                "color": embed_color,
                "status": status,
                "status_edit": satus_edit
            }

            discord_data_file = open('web/src/config/discord.json', 'w', encoding='utf-8')
            json.dump(discord_data_save, discord_data_file, indent=6, ensure_ascii=False)
            discord_data_file.close()

            responses_file = open('web/src/messages/messages_file.json', 'r', encoding='utf-8')
            responses_data = json.load(responses_file)

            responses_data['create_clip_discord'] = embed_title
            responses_data['create_clip_discord_edit'] = embed_title_edit
            responses_data['clip_created_by'] = embed_description

            responses_file.close()

            responses_file_w = open('web/src/messages/messages_file.json', 'w', encoding='utf-8')
            json.dump(responses_data, responses_file_w, indent=6, ensure_ascii=False)
            responses_file_w.close()

            eel.modal_discord('sucess-discord-config')

        except Exception as e:

            eel.modal_discord('error-discord-config')
            utils.error_log(e)

    if mode == 'get':
        responses_file_discord = open('web/src/messages/messages_file.json', 'r', encoding='utf-8')
        responses_data_discord = json.load(responses_file_discord)

        embed_title = responses_data_discord['create_clip_discord']
        embed_title_edit = responses_data_discord['create_clip_discord_edit']
        embed_description = responses_data_discord['clip_created_by']

        responses_file_discord.close()

        discord_data_file = open('web/src/config/discord.json', 'r', encoding='utf-8')
        discord_data = json.load(discord_data_file)

        url_webhook = discord_data['url']
        url_webhook_edit = discord_data['url_edit']
        embed_color = discord_data['color']
        status = discord_data['status']
        satus_edit = discord_data['status_edit']

        discord_data_file.close()

        data_get = {

            "url_webhook": url_webhook,
            "url_webhook_edit": url_webhook_edit,
            "embed_color": embed_color,
            "embed_title": embed_title,
            "embed_title_edit": embed_title_edit,
            "embed_description": embed_description,
            "status": status,
            "satus_edit": satus_edit,
        }

        data_get_sent = json.dumps(data_get, ensure_ascii=False)

        return data_get_sent


@eel.expose
def obs_try_conn():
    obs_thread = threading.Thread(target=obs_test_conn, args=(), daemon=True)
    obs_thread.start()


@eel.expose
def send_message_chat(message):
    chat.send(message)


@eel.expose
def save_disclosure(disclosure):
    file_disclosure = open('web/src/config/disclosure.txt', 'w', encoding='utf-8')
    file_disclosure.write(disclosure)
    file_disclosure.close()


@eel.expose
def load_disclosure():
    file_disclosure = open('web/src/config/disclosure.txt', 'r', encoding='utf-8')
    disclosure = file_disclosure.read()

    if disclosure == "":
        disclosure = 'Digite aqui a sua mensagem rápida de divulgação em chats'

    return disclosure


@eel.expose
def get_edit_data(redeen, type_action):
    redeem_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
    redeem_data = json.load(redeem_file)

    if type_action == 'sound':

        sound = redeem_data[redeen]['path']
        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']

        redeem_file.close()

        command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
        else:
            command_level = ''

        command_file.close()

        redeem_data_return = {
            "sound": sound,
            "command": command,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'tts':

        characters = redeem_data[redeen]['characters']
        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']

        redeem_file.close()

        if command != "":

            command_file_tts = open('web/src/config/prefix_tts.json', "r", encoding='utf-8')
            command_data_tts = json.load(command_file_tts)

            user_level = command_data_tts['user_level']

            command_file_tts.close()

        else:

            user_level = ""

        redeem_data_return = {
            "characters": characters,
            "command": command,
            "response_status": response_status,
            "user_level": user_level,
            "response": response,
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'response':

        command = redeem_data[redeen]['command']
        response = redeem_data[redeen]['chat_response']

        redeem_file.close()

        command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
        else:
            command_level = ''

        command_file.close()

        redeem_data_return = {
            "command": command,
            "user_level": command_level,
            "response": response,
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'scene':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        scene_name = redeem_data[redeen]['scene_name']
        keep = redeem_data[redeen]['keep']
        time_scene = redeem_data[redeen]['time']

        redeem_file.close()

        command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
        else:
            command_level = ''

        command_file.close()

        redeem_data_return = {
            "command": command,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "scene_name": scene_name,
            "keep": keep,
            "time": time_scene
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'filter':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        keep = redeem_data[redeen]['keep']
        time_filter = redeem_data[redeen]['time']

        redeem_file.close()

        command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
        else:
            command_level = ''

        command_file.close()

        redeem_data_return = {
            "command": command,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "keep": keep,
            "time": time_filter
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'source':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        keep = redeem_data[redeen]['keep']
        time = redeem_data[redeen]['time']

        redeem_file.close()

        command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
        else:
            command_level = ''

        command_file.close()

        redeem_data_return = {
            "command": command,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "keep": keep,
            "time": time
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'keypress':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        mode = redeem_data[redeen]['mode']

        key1 = redeem_data[redeen]['key1']
        key2 = redeem_data[redeen]['key2']
        key3 = redeem_data[redeen]['key3']
        key4 = redeem_data[redeen]['key4']

        redeem_file.close()

        command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
        else:
            command_level = ''

        command_file.close()

        if mode == 'keep':

            keep_press_time = redeem_data[redeen]['keep_press_time']

            redeem_data_return = {
                "command": command,
                "response_status": response_status,
                "user_level": command_level,
                "response": response,
                "mode": mode,
                "keep_press_time": keep_press_time,
                "key1": key1,
                "key2": key2,
                "key3": key3,
                "key4": key4
            }

            redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

            return redeem_data_dump

        elif mode == 'mult':

            time_press = redeem_data[redeen]['mult_press_times']
            interval = redeem_data[redeen]['mult_press_interval']

            redeem_data_return = {

                "command": command,
                "response_status": response_status,
                "user_level": command_level,
                "response": response,
                "mode": mode,
                "time_press": time_press,
                "interval": interval,
                "key1": key1,
                "key2": key2,
                "key3": key3,
                "key4": key4
            }

            redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

            return redeem_data_dump

        elif mode == 're':

            re_press_time = redeem_data[redeen]['re_press_time']

            redeem_data_return = {
                "command": command,
                "response_status": response_status,
                "user_level": command_level,
                "response": response,
                "mode": mode,
                "re_press_time": re_press_time,
                "key1": key1,
                "key2": key2,
                "key3": key3,
                "key4": key4
            }

            redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

            return redeem_data_dump

    if type_action == 'clip':

        command = redeem_data[redeen]['command']

        redeem_file.close()

        command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
        else:
            command_level = ''

        command_file.close()

        redeem_data_return = {
            "command": command,
            "user_level": command_level,
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump


@eel.expose
def save_edit_redeen(data, redeem_type):
    data_received = json.loads(data)

    if redeem_type == 'audio':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            old_command = data_received['old_command']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            sound_path = data_received['sound_path']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "sound",
                'path': sound_path,
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            if old_command != command and old_command != "":

                del command_data[old_command]

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                    command_file_write.close()

                command_file.close()

                command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                command_file_write.close()

            elif old_command != command and old_command == "":

                print('SEGUNDA')

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

            eel.modal_edit_actions('sucess', 'edit-audio-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-audio-div')

    if redeem_type == 'tts':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            characters = data_received['characters']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "tts",
                'characters': characters,
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            tts_command_file = open('web/src/config/prefix_tts.json', 'r', encoding='utf-8')
            tts_command_data = json.load(tts_command_file)

            tts_command_data['command'] = command.lower()
            tts_command_data['redeem'] = redeem
            tts_command_data['user_level'] = user_level

            tts_command_file.close()

            tts_command_file_write = open('web/src/config/prefix_tts.json', 'w', encoding='utf-8')
            json.dump(tts_command_data, tts_command_file_write, indent=6, ensure_ascii=False)
            tts_command_file_write.close()

            eel.modal_edit_actions('sucess', 'edit-tts-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-tts-div')

    if redeem_type == 'scene':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            old_command = data_received['old_command']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            scene_name = data_received['scene_name']
            keep = data_received['keep']
            time = data_received['time']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "scene",
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
                'scene': scene_name,
                'keep': keep,
                'time': time
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            if old_command != command and old_command != "":

                del command_data[old_command]

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                    command_file_write.close()

                command_file.close()

                command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                command_file_write.close()

            eel.modal_edit_actions('sucess', 'edit-scene-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-scene-div')

    if redeem_type == 'response':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            old_command = data_received['old_command']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "response",
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            if old_command != command and old_command != "":

                del command_data[old_command]

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                    command_file_write.close()

                command_file.close()

                command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                command_file_write.close()

            eel.modal_edit_actions('sucess', 'edit-response-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-response-div')

    if redeem_type == 'filter':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            old_command = data_received['old_command']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            source_name = data_received['source_name']
            filter_name = data_received['filter']
            keep = data_received['keep']
            time = data_received['time']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "filter",
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
                'source_name': source_name,
                'filter_name': filter_name,
                'keep': keep,
                'time': time
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            if old_command != command and old_command != "":

                del command_data[old_command]

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                    command_file_write.close()

                command_file.close()

                command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                command_file_write.close()

            eel.modal_edit_actions('sucess', 'edit-filter-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-filter-div')

    if redeem_type == 'source':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            old_command = data_received['old_command']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            source_name = data_received['source']
            keep = data_received['keep']
            time = data_received['time']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {

                'type': "source",
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
                'source_name': source_name,
                'keep': keep,
                'time': time
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            if old_command != command and old_command != "":

                del command_data[old_command]

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                    command_file_write.close()

                command_file.close()

                command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                command_file_write.close()

            eel.modal_edit_actions('sucess', 'edit-source-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-source-div')

    if redeem_type == 'keypress':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            old_command = data_received['old_command']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            mode_press = data_received['mode']

            key1 = data_received['key1']
            key2 = data_received['key2']
            key3 = data_received['key3']
            key4 = data_received['key4']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            if mode_press == 'mult':

                mult_press_times = data_received['mult_press_times']
                mult_press_interval = data_received['mult_press_interval']

                path_data[redeem] = {

                    'type': 'keypress',
                    'send_response': send_message,
                    'chat_response': chat_message,
                    'command': command.lower(),
                    'mode': mode_press,
                    'mult_press_times': int(mult_press_times),
                    'mult_press_interval': int(mult_press_interval),
                    'key1': key1,
                    'key2': key2,
                    'key3': key3,
                    'key4': key4
                }

            elif mode_press == 're':

                re_press_time = data_received['re_press_time']

                path_data[redeem] = {

                    'type': 'keypress',
                    'send_response': send_message,
                    'chat_response': chat_message,
                    'command': command.lower(),
                    'mode': mode_press,
                    're_press_time': int(re_press_time),
                    'key1': key1,
                    'key2': key2,
                    'key3': key3,
                    'key4': key4
                }

            elif mode_press == 'keep':

                keep_press_time = data_received['keep_press_time']

                path_data[redeem] = {

                    'type': 'keypress',
                    'send_response': send_message,
                    'chat_response': chat_message,
                    'command': command.lower(),
                    'mode': mode_press,
                    'keep_press_time': int(keep_press_time),
                    'key1': key1,
                    'key2': key2,
                    'key3': key3,
                    'key4': key4
                }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            if old_command != command and old_command != "":

                del command_data[old_command]

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                    command_file_write.close()

                command_file.close()

                command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                command_file_write.close()

            eel.modal_edit_actions('sucess', 'edit-keypress-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-keypress-div')

    if redeem_type == 'clip':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            old_command = data_received['old_command']
            command = data_received['command']
            user_level = data_received['user_level']

            path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "clip",
                'command': command,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            if old_command != command and old_command != "":

                del command_data[old_command]

                if command != "":
                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level': user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                    json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                    command_file_write.close()

                command_file.close()

                command_file_write = open('web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

                command_file_write.close()

            eel.modal_edit_actions('sucess', 'edit-clip-div')

        except Exception as e:

            utils.error_log(e)

            eel.modal_edit_actions('error', 'edit-clip-div')


@eel.expose
def add_playlist(playlist_url):
    def start_add():

        try:

            p = Playlist(playlist_url)

            playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
            playlist_data = json.load(playlist_file)

            check_have = any(playlist_data.keys())
            playlist_file.close()

            if not check_have:

                last_key = 0

            else:

                playlist_keys = [int(x) for x in playlist_data.keys()]
                last_key = max(playlist_keys)

            for url in p.video_urls:

                last_key = last_key + 1

                try:

                    yt = YouTube(url)
                    video_title = yt.title

                    video_title_short = textwrap.shorten(video_title, width=40, placeholder="...")

                    eel.playlist_stats_music('Adicionando, aguarde... ' + video_title_short, 'Add')

                    playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
                    playlist_data = json.load(playlist_file)

                    playlist_data[last_key] = {"MUSIC": url, "USER": "playlist", "MUSIC_NAME": video_title}
                    playlist_file.close()

                    playlist_file_write = open('web/src/player/list_files/playlist.json', "w", encoding="utf-8")
                    json.dump(playlist_data, playlist_file_write, indent=4, ensure_ascii=False)
                    playlist_file_write.close()

                except Exception as e:

                    utils.error_log(e)

            eel.playlist_stats_music('None', 'Close')

        except Exception as e:

            utils.error_log(e)

    playelist_thread = threading.Thread(target=start_add, args=(), daemon=True)
    playelist_thread.start()


@eel.expose
def playlist_clear_py():
    playlist_data = {}

    playlist_file_write = open('web/src/player/list_files/playlist.json', "w", encoding="utf-8")
    json.dump(playlist_data, playlist_file_write, indent=4, ensure_ascii=False)
    playlist_file_write.close()


@eel.expose
def playlist_execute_save(value, type_rec):
    if type_rec == 'save':

        value_status = value

        playlist_stats_data_file = open('web/src/player/config/playlist.json', 'r', encoding="utf-8")
        playlist_stats_data = json.load(playlist_stats_data_file)

        playlist_stats_data['STATUS'] = value_status
        playlist_stats_data_file.close()

        old_data_write = open('web/src/player/config/playlist.json', 'w', encoding="utf-8")
        json.dump(playlist_stats_data, old_data_write, indent=4)
        old_data_write.close()

    elif type_rec == 'get':

        playlist_stats_data_file = open('web/src/player/config/playlist.json', 'r', encoding="utf-8")
        playlist_stats_data = json.load(playlist_stats_data_file)

        value_status = playlist_stats_data['STATUS']
        playlist_stats_data_file.close()

        return value_status


@eel.expose
def music_status_save(status, type_id):
    if type_id == 'save':

        status_music_file = open('web/src/player/config/playlist.json', 'r', encoding="utf-8")
        status_music_data = json.load(status_music_file)

        status_music_data['STATUS_MUSIC_ENABLE'] = status
        status_music_file.close()

        status_music_file_write = open('web/src/player/config/playlist.json', 'w', encoding="utf-8")
        json.dump(status_music_data, status_music_file_write, indent=6, ensure_ascii=False)
        status_music_file_write.close()

    elif type_id == 'get':

        status_music_file = open('web/src/player/config/playlist.json', 'r', encoding="utf-8")
        status_music_data = json.load(status_music_file)

        status = status_music_data['STATUS_MUSIC_ENABLE']

        status_music_file.close()

        return status


@eel.expose
def get_music_config_py():
    commands_music_file = open('web/src/player/config/commands.json', 'r', encoding='utf-8')
    commands_music_data = json.load(commands_music_file)

    command_request = commands_music_data['request']
    command_volume = commands_music_data['volume']
    command_skip = commands_music_data['skip']
    command_next = commands_music_data['next']
    command_atual = commands_music_data['atual']

    commands_music_file.close()

    not_music_file = open('web/src/config/notfic.json', 'r', encoding='utf-8')
    not_music_data = json.load(not_music_file)

    not_status = not_music_data['HTML_PLAYER_ACTIVE']

    data = {
        "not_status": not_status,
        "cmd_request": command_request,
        "cmd_volume": command_volume,
        "cmd_skip": command_skip,
        "cmd_next": command_next,
        "cmd_atual": command_atual
    }

    music_dump = json.dumps(data, ensure_ascii=False)

    return music_dump


@eel.expose
def save_music_config(data_receive):
    data = json.loads(data_receive)

    try:

        redeem = data['redeem_music_data']
        status_music = data['music_not_status_data']
        command_request = data['command_request_data']
        command_volume = data['command_volume_data']
        command_skip = data['command_skip_data']
        command_next = data['command_next_data']
        command_atual = data['command_atual_data']

        not_status_music_file = open('web/src/config/notfic.json', 'r', encoding="utf-8")
        not_status_music_data = json.load(not_status_music_file)

        not_status_music_data['HTML_PLAYER_ACTIVE'] = status_music
        not_status_music_file.close()

        status_music_file_write = open('web/src/config/notfic.json', 'w', encoding="utf-8")
        json.dump(not_status_music_data, status_music_file_write, indent=6, ensure_ascii=False)
        status_music_file_write.close()

        commands_music_file = open('web/src/player/config/commands.json', 'r', encoding='utf-8')
        commands_music_data = json.load(commands_music_file)

        commands_music_data['request'] = command_request
        commands_music_data['volume'] = command_volume
        commands_music_data['skip'] = command_skip
        commands_music_data['next'] = command_next
        commands_music_data['atual'] = command_atual

        commands_music_file_w = open('web/src/player/config/commands.json', 'w', encoding='utf-8')
        json.dump(commands_music_data, commands_music_file_w, indent=6, ensure_ascii=False)

        redeem_music_file = open('web/src/player/config/redem_data.json', 'r', encoding='utf-8')
        redeem_music_data = json.load(redeem_music_file)

        redeem_music_data['title'] = redeem

        redeem_music_file_w = open('web/src/player/config/redem_data.json', 'w', encoding='utf-8')
        json.dump(redeem_music_data, redeem_music_file_w, indent=6, ensure_ascii=False)

        eel.config_modal('sucess-config-music')

    except Exception as e:
        utils.error_log(e)

        eel.config_modal('error-config-music')


@eel.expose
def list_queue():
    queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
    queue_data = json.load(queue_file)

    playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
    playlist_data = json.load(playlist_file)

    list_queue_list = {}
    for key in queue_data:
        music = queue_data[key]['MUSIC_NAME']
        user = queue_data[key]['USER']

        list_queue_list[music] = user

    for key in playlist_data:
        music = playlist_data[key]['MUSIC_NAME']
        user = playlist_data[key]['USER']

        list_queue_list[music] = user

    queue_file.close()
    playlist_file.close()

    data_dump = json.dumps(list_queue_list, ensure_ascii=False)

    return data_dump


@eel.expose
def update_check(type_id):
    if type_id == 'check':

        response = req.get("https://api.github.com/repos/GGTEC/RewardEvents/releases/latest")
        response_json = json.loads(response.text)
        version = response_json['tag_name']

        if version != 'V3.0.0':

            return 'true'
        else:

            return 'false'

    elif type_id == 'open':

        url = 'https://github.com/GGTEC/RewardEvents/releases'
        webbrowser.open(url, new=0, autoraise=True)


@eel.expose
def clip():
    info_clip = twitch_api.create_clip(broadcaster_id=BROADCASTER_ID)

    if 'error' in info_clip.keys():

        message_clip_error_load = messages_file_load('clip_error_clip')
        if utils.send_message("CLIP"):
            chat.send(message_clip_error_load)

    else:

        clip_id = info_clip['data'][0]['id']

        message_clip_user_load = messages_file_load('clip_create_clip')

        message_clip_user = message_clip_user_load.replace('{user}', USERNAME)
        message_final = message_clip_user.replace('{clip_id}', clip_id)

        if utils.send_message("CLIP"):
            chat.send(message_final)

        discord_config_file = open('web/src/config/discord.json', 'r', encoding='utf-8')
        discord_config_data = json.load(discord_config_file)

        webhook_status = discord_config_data['status']
        webhook_color = discord_config_data['color']
        webhook_url = discord_config_data['url']

        if webhook_status == 1:
            message_discord_load = messages_file_load('create_clip_discord')
            message_discord_desc_load = messages_file_load('clip_created_by')

            message_discord = message_discord_load.replace('{clip_id}', clip_id)

            webhook = DiscordWebhook(url=webhook_url)

            embed = DiscordEmbed(title=message_discord,
                                 description=message_discord_desc_load.replace('{user}', USERNAME), color=webhook_color)

            webhook.add_embed(embed)

            webhook.execute()

        discord_config_file.close()


@eel.expose
def timer():
    print('Modulo timer iniciado')

    while True:

        try:

            timer_data_file = open('web/src/config/timer.json', 'r', encoding='utf-8')
            timer_data = json.load(timer_data_file)

            timer_int = timer_data['TIME']
            timer_max_int = timer_data['TIME_MAX']

            next_timer = randint(timer_int, timer_max_int)

            if chat_active:

                if utils.send_message('TIMER'):

                    timer_message = timer_data['MESSAGES']
                    last_key = timer_data['LAST']

                    key_value = timer_message.keys()

                    if bool(timer_message):
                        message_key = random.choice(list(key_value))

                        if message_key == last_key:
                            time.sleep(1)
                        else:

                            timer_data['LAST'] = message_key

                            update_last_file = open('web/src/config/timer.json', 'w', encoding='utf-8')
                            json.dump(timer_data, update_last_file, indent=4, ensure_ascii=False)
                            update_last_file.close()

                            chat.send(timer_message[message_key])
                            time.sleep(next_timer)

                    else:
                        time.sleep(1)

                else:
                    time.sleep(10)

        except Exception as e:
            utils.error_log(e)
            time.sleep(5)


def get_users_info(type_id, user_id):
    os.makedirs('web/src/user_info', exist_ok=True)

    if type_id == 'save':

        mod_dict = {}
        mod_info = twitch_api.get_moderators(broadcaster_id=BROADCASTER_ID)

        for index in range(len(mod_info['data'])):
            user_id = mod_info['data'][index]['user_id']
            user_name = mod_info['data'][index]['user_name']
            mod_dict[user_id] = user_name

        mods_file = open('web/src/user_info/mods.json', 'w', encoding='utf-8')
        json.dump(mod_dict, mods_file, indent=4, ensure_ascii=False)
        mods_file.close()

        sub_dict = {}
        sub_info = twitch_api.get_broadcaster_subscriptions(broadcaster_id=BROADCASTER_ID)

        for index in range(len(sub_info['data'])):
            user_id = sub_info['data'][index]['user_id']
            user_name = sub_info['data'][index]['user_name']
            sub_dict[user_id] = user_name

        subs_file = open('web/src/user_info/subs.json', 'w', encoding='utf-8')
        json.dump(sub_dict, subs_file, indent=4, ensure_ascii=False)
        subs_file.close()

    elif type_id == 'get_sub':

        subs_file = open('web/src/user_info/subs.json', 'r', encoding='utf-8')
        subs_data = json.load(subs_file)

        if 'user_id' in subs_data.keys():
            return True
        else:
            return False

    elif type_id == 'get_mod':

        mod_file = open('web/src/user_info/mods.json', 'r', encoding='utf-8')
        mod_data = json.load(mod_file)

        if 'user_id' in mod_data.keys():
            return True
        else:
            return False


def start_play(user_input, redem_by_user):
    def my_hook(d):

        if d['status'] == 'downloading':

            percent = d['_percent_str']
            try:
                percent_numbers = int(float(percent.split()[0].replace('%', ''))) / 10
            except Exception as e:
                utils.error_log(e)
                pass


    def download_music(link):

        music_dir_check = os.path.exists(extDataDir + '/web/src/player/cache/music.mp3')
        music_mp4_check = os.path.exists(extDataDir + '/web/src/player/cache/music.mp4')

        if music_mp4_check:
            os.remove(extDataDir + '/web/src/player/cache/music.mp4')

        if music_dir_check:
            os.remove(extDataDir + '/web/src/player/cache/music.mp3')

        try:
            ydl_opts = {
                'final_ext': 'mp3',
                'format': 'best',
                'noplaylist': True,
                'quiet': True,
                'no_color': True,
                'outtmpl': extDataDir + '/web/src/player/cache/music.%(ext)s',
                'ffmpeg_location': extDataDir,
                'force-write-archive': True,
                'force-overwrites': True,
                'keepvideo': True,
                'progress_hooks': [my_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'nopostoverwrites': False,
                    'preferredcodec': 'mp3',
                    'preferredquality': '5'
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            return True

        except Exception as e:
            utils.error_log(e)

            return False

    response_album = utils.album_search(user_input, redem_by_user)
    success = response_album['success']

    if success == 1:

        media_name = response_album['music']
        media_artist = response_album['artist']
        music_link = response_album['link']

        yt = YouTube(music_link)
        music_leght = yt.length

        if music_leght < 600:

            caching = 1

            if download_music(music_link):

                if media_artist == '0':
                    music_artist = ""
                else:
                    music_artist = media_artist

                with open('web/src/player/list_files/currentsong.txt', "w", encoding="utf-8") as file_object:
                    file_object.write(media_name + music_artist + '\n')
                    file_object.close()

                music_name_short = textwrap.shorten(media_name, width=13, placeholder="...")

                utils.update_notif(music_name_short, redem_by_user, music_artist, 'music')

                not_thread = threading.Thread(target=obs_events.notification_player, args=(), daemon=True)
                not_thread.start()

                eel.update_music_name(media_name, music_artist)

                aliases = {
                    '{music_name}': media_name,
                    '{music_name_short}': music_name_short,
                    '{music_artist}': music_artist,
                    '{user}': redem_by_user
                }

                message_replace = replace_all(messages_file_load('music_playing'), aliases)
                if utils.send_message("STATUS_MUSIC"):
                    chat.send(message_replace)

                eel.player('play', 'http://localhost:8000/src/player/cache/music.mp3', '1')

                caching = 0

            else:

                caching = 0
                eel.update_music_name('Erro ao processar musica', 'Erro ao processar musica')
                if utils.send_message("STATUS_MUSIC"):
                    chat.send(messages_file_load('music_process_cache_error'))


        else:

            aliases = {
                '{music_name}': media_name,
                '{user}': redem_by_user
            }

            message_replace = replace_all(messages_file_load('music_leght_error'), aliases)
            if utils.send_message("STATUS_MUSIC"):
                chat.send(message_replace)

    else:
        message_replace = messages_file_load('music_process_error')
        if utils.send_message("STATUS_MUSIC"):
            chat.send(message_replace)


def loopcheck():

    while True:

        if loaded_status == 1 and bot_loaded == 1:

            playlist_status_file = open('web/src/player/config/playlist.json', 'r', encoding="utf-8")
            playlist_execute_data = json.load(playlist_status_file)
            playlist_execute_value = playlist_execute_data['STATUS']
            playlist_execute = int(playlist_execute_value)
            playlist_status_file.close()

            playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
            playlist_data = json.load(playlist_file)
            check_have_playlist = any(playlist_data.keys())
            playlist_file.close()

            queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
            queue_data = json.load(queue_file)
            check_have_queue = any(queue_data.keys())
            queue_file.close()

            playing = eel.player('playing', 'none', 'none')()

            if caching == 0 and playing == 'False':

                if check_have_queue:

                    queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
                    queue_data = json.load(queue_file)

                    queue_keys = [int(x) for x in queue_data.keys()]
                    music_data_key = str(min(queue_keys))

                    music = queue_data[music_data_key]['MUSIC']
                    user = queue_data[music_data_key]['USER']

                    del queue_data[music_data_key]

                    queue_file.close()

                    queue_file_write = open('web/src/player/list_files/queue.json', "w", encoding="utf-8")
                    json.dump(queue_data, queue_file_write, indent=4)
                    queue_file_write.close()

                    start_play(music, user)

                    time.sleep(5)


                elif check_have_playlist:

                    if playlist_execute == 1:

                        playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
                        playlist_data = json.load(playlist_file)

                        playlist_keys = [int(x) for x in playlist_data.keys()]
                        music_data = str(min(playlist_keys))

                        music = playlist_data[music_data]['MUSIC']
                        user = playlist_data[music_data]['USER']

                        del playlist_data[music_data]

                        playlist_file.close()

                        playlist_file_write = open('web/src/player/list_files/playlist.json', "w", encoding="utf-8")
                        json.dump(playlist_data, playlist_file_write, indent=4)
                        playlist_file_write.close()

                        start_play(music, user)


                    else:
                        time.sleep(3)
                else:
                    time.sleep(3)
                    eel.update_music_name('Aguardando', 'Aguardando')
            else:
                time.sleep(3)


def obs_test_conn():
    if loaded_status == 1:

        sucess_conn = obs_events.test_obs_conn()

        if sucess_conn:

            eel.callback_obs('sucess')

        elif not sucess_conn:

            eel.callback_obs('error')

        elif sucess_conn == 'None':
            pass


def callback_whisper(uuid: UUID, data: dict) -> None:
    receive_redeem_thread = threading.Thread(target=receive_redeem, args=(data, 'redeem',), daemon=True)
    receive_redeem_thread.start()


def receive_redeem(data_rewards, received_type):
    def process_redem_music(user_input, redem_by_user):

        eel.update_music_name('Processando musica', 'Aguarde')

        queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
        queue_data = json.load(queue_file)

        check_have = any(queue_data.keys())

        if not check_have:
            last_key = 1
        else:
            queue_keys = [int(x) for x in queue_data.keys()]
            last_key = str(max(queue_keys) + 1)

        if validators.url(user_input):

            find_youtube = user_input.find('youtube')
            find_youtu = user_input.find('youtu')

            if not find_youtube or find_youtu != -1:

                try:
                    yt = YouTube(user_input)
                    music_name = yt.title
                    music_leght = yt.length

                    if music_leght < 600:

                        queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
                        queue_data = json.load(queue_file)

                        queue_data[last_key] = {"MUSIC": user_input, "USER": redem_by_user, "MUSIC_NAME": music_name}
                        queue_file.close()

                        queue_file_write = open('web/src/player/list_files/queue.json', "w", encoding="utf-8")
                        json.dump(queue_data, queue_file_write, indent=4)
                        queue_file_write.close()

                        aliases = {'{user}': redem_by_user, '{user_input}': user_input, '{music}': music_name}
                        message = messages_file_load('music_added_to_queue')
                        message_replaced = replace_all(message, aliases)

                        if utils.send_message("STATUS_MUSIC_CONFIRM"):
                            chat.send(message_replaced)

                    else:

                        music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                        aliases = {
                            '{user}': str(redem_by_user),
                            '{user_input}': str(user_input),
                            '{music}': str(music_name),
                            '{music_short}': str(music_name_short)
                        }

                        message = messages_file_load('music_leght_error')
                        message_replaced = replace_all(message, aliases)

                        if utils.send_message("STATUS_MUSIC_CONFIRM"):
                            chat.send(message_replaced)

                except Exception as e:
                    utils.error_log(e)

                    aliases = {'{user}': str(redem_by_user), '{user_input}': str(user_input)}
                    message = messages_file_load('music_add_error')
                    message_replaced = replace_all(message, aliases)

                    if utils.send_message("STATUS_MUSIC_CONFIRM"):
                        chat.send(message_replaced)

            else:
                message_replaced = messages_file_load('music_link_youtube')
                if utils.send_message("STATUS_MUSIC_CONFIRM"):
                    chat.send(message_replaced)

        else:

            music_name = utils.removestring(user_input)

            search_youtube = Search(music_name)
            result_search = search_youtube.results[0].__dict__
            url_youtube = result_search['watch_url']

            yt = YouTube(url_youtube)
            video_title = yt.title

            queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
            queue_data = json.load(queue_file)

            queue_data[last_key] = {"MUSIC": music_name, "USER": redem_by_user, "MUSIC_NAME": music_name}
            queue_file.close()

            queue_file_write = open('web/src/player/list_files/queue.json', "w", encoding="utf-8")
            json.dump(queue_data, queue_file_write, indent=4)
            queue_file_write.close()

            music_name_short = textwrap.shorten(video_title, width=13, placeholder="...")

            aliases = {
                '{user}': redem_by_user,
                '{user_input}': user_input,
                '{music}': video_title,
                '{music_short}': music_name_short
            }

            message = messages_file_load('music_added_to_queue')

            message_replaced = replace_all(message, aliases)

            if utils.send_message("STATUS_MUSIC_CONFIRM"):
                chat.send(message_replaced)

    with open("web/src/counter/counter.txt", "r") as counter_file_r:
        counter_file_r.seek(0)
        digit = counter_file_r.read()
        counter_actual = int(digit)

    redeem_reward_name = '0'
    redeem_by_user = '0'
    user_input = '0'
    user_level = '0'
    user_id_command = '0'
    command_receive = '0'
    prefix = '0'

    player_file = open('web/src/player/config/redem_data.json')
    player_data = json.load(player_file)

    player_reward = player_data['title']

    if received_type == 'redeem':

        redeem_reward_name = data_rewards['data']['redemption']['reward']['title']
        redeem_by_user = data_rewards['data']['redemption']['user']['display_name']
        user_input_check = data_rewards['data']['redemption']

        if 'user_input' in user_input_check.keys():
            user_input = data_rewards['data']['redemption']['user_input']

        if data_rewards['data']['redemption']['reward']['image'] is None:
            redeem_reward_image = data_rewards['data']['redemption']['reward']['default_image']['url_4x']
        else:
            redeem_reward_image = data_rewards['data']['redemption']['reward']['image']['url_4x']

        img_redeem_data = req.get(redeem_reward_image).content

        with open(extDataDir + '/web/src/Request.png', 'wb') as image_redeem:
            image_redeem.write(img_redeem_data)
            image_redeem.close()

        with open('web/src/Request.png', 'wb') as image_redeem:
            image_redeem.write(img_redeem_data)
            image_redeem.close()

    elif received_type == 'command':

        redeem_reward_name = data_rewards['REDEEM']
        redeem_by_user = data_rewards['USERNAME']
        user_input = data_rewards['USER_INPUT']
        user_level = data_rewards['USER_LEVEL']
        user_id_command = data_rewards['USER_ID']

        command_receive = data_rewards['COMMAND']
        prefix = data_rewards['PREFIX']

    redeem_data_js = {
        "redeem_name": redeem_reward_name,
        "redeem_user": redeem_by_user
    }

    aliases = {

        '{user}': str(redeem_by_user),
        '{command}': str(command_receive),
        '{prefix}': str(prefix),
        '{user_level}': str(user_level),
        '{user_id}': str(user_id_command),
        '{user_input}': str(user_input),
        '{counter}': str(counter_actual)

    }

    redeem_data_js_parse = json.dumps(redeem_data_js, ensure_ascii=False)

    eel.update_div_redeem(redeem_data_js_parse)

    utils.update_notif(redeem_reward_name, redeem_by_user, 'None', 'redeem')

    not_thread_1 = threading.Thread(target=obs_events.notification, args=(), daemon=True)
    not_thread_1.start()

    path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8')
    path = json.load(path_file)

    giveaway_path_file = open('web/src/giveaway/config.json', 'r', encoding='utf-8')
    giveaway_path = json.load(giveaway_path_file)

    giveaway_redeem = giveaway_path['redeem']

    def play_sound():

        audio_path = path[redeem_reward_name]['path']
        send_response_value = path[redeem_reward_name]['send_response']

        tts_playing = pygame.mixer.music.get_busy()

        while tts_playing:
            tts_playing = pygame.mixer.music.get_busy()
            time.sleep(2)

        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']
            response_redus = replace_all(chat_response, aliases)

            if utils.send_message("RESPONSE"):
                chat.send(response_redus)

    def play_tts():

        send_response_value = path[redeem_reward_name]['send_response']
        characters = path[redeem_reward_name]['characters']
        characters_int = int(characters)

        user_input_short = textwrap.shorten(user_input, width=characters_int, placeholder=" ")

        tts = gTTS(text=user_input_short, lang='pt-br', slow=False)

        mp3_fp = BytesIO()

        tts.write_to_fp(mp3_fp)

        mp3_fp.seek(0)

        tts_playing = pygame.mixer.music.get_busy()

        while tts_playing:
            tts_playing = pygame.mixer.music.get_busy()
            time.sleep(2)

        pygame.mixer.music.load(mp3_fp, "mp3")
        pygame.mixer.music.play()

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']

            try:
                response_redus = replace_all(chat_response, aliases)
                if utils.send_message("RESPONSE"):
                    chat.send(response_redus)
            except Exception as e:

                utils.error_log(e)
                if utils.send_message("RESPONSE"):
                    chat.send(chat_response)

    def change_scene():

        scene_name = path[redeem_reward_name]['scene_name']
        keep = path[redeem_reward_name]['keep']
        time_show = path[redeem_reward_name]['time']
        send_response_value = path[redeem_reward_name]['send_response']

        if send_response_value == 1:

            chat_response = path[redeem_reward_name]['chat_response']

            try:
                response_redus = replace_all(chat_response, aliases)
                if utils.send_message("RESPONSE"):
                    chat.send(response_redus)

            except Exception as e:

                utils.error_log(e)
                if utils.send_message("RESPONSE"):
                    chat.send(chat_response)

        obs_events.show_scene(scene_name, time_show, keep)

    def send_message():

        chat_response = path[redeem_reward_name]['chat_response']

        try:
            response_redus = replace_all(chat_response, aliases)

            if utils.send_message("RESPONSE"):
                chat.send(response_redus)
        except Exception as e:

            utils.error_log(e)
            if utils.send_message("RESPONSE"):
                chat.send(chat_response)

    def toggle_filter():

        source_name = path[redeem_reward_name]['source_name']
        filter_name = path[redeem_reward_name]['filter_name']
        time_show = path[redeem_reward_name]['time']
        keep = path[redeem_reward_name]['keep']

        send_response_value = path[redeem_reward_name]['send_response']

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']

            try:
                response_redus = replace_all(chat_response, aliases)

                if utils.send_message("RESPONSE"):
                    chat.send(response_redus)
            except Exception as e:

                utils.error_log(e)
                if utils.send_message("RESPONSE"):
                    chat.send(chat_response)

        obs_events.show_filter(source_name, filter_name, time_show, keep)

    def key_press():

        keyskeyboard = path[redeem_reward_name]
        send_response_value = path[redeem_reward_name]['send_response']

        mode = path[redeem_reward_name]['mode']

        aliases = {
            '{user}': str(redeem_by_user),
            '{command}': str(command_receive),
            '{prefix}': str(prefix),
            '{user_level}': str(user_level),
            '{user_id}': str(user_id_command)
        }

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']

            try:

                response_redus = replace_all(chat_response, aliases)
                if utils.send_message("RESPONSE"):
                    chat.send(response_redus)

            except Exception as e:

                utils.error_log(e)
                if utils.send_message("RESPONSE"):
                    chat.send(chat_response)

        def mult_press():

            mult_press_times = path[redeem_reward_name]['mult_press_times']
            mult_press_interval = path[redeem_reward_name]['mult_press_interval']

            value_repeated = 0

            while value_repeated < mult_press_times:
                value_repeated = value_repeated + 1

                received = [*keyskeyboard.keys()][7:]
                keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key] != 'NONE']

                keyboard.press_and_release('+'.join(keys_to_pressed))

                time.sleep(mult_press_interval)

        def re_press():

            re_press_time = path[redeem_reward_name]['re_press_time']

            received = [*keyskeyboard.keys()][6:]

            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key] != 'NONE']

            keyboard.press_and_release('+'.join(keys_to_pressed))

            time.sleep(re_press_time)

            keyboard.press_and_release('+'.join(keys_to_pressed))

        def keep_press():

            keep_press_time = path[redeem_reward_name]['keep_press_time']

            received = [*keyskeyboard.keys()][6:]

            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key] != 'NONE']

            keyboard.press('+'.join(keys_to_pressed))
            keyboard.block_key('+'.join(keys_to_pressed))

            time.sleep(keep_press_time)

            keyboard.release('+'.join(keys_to_pressed))

        if mode == "re":

            re_press_thread = threading.Thread(target=re_press, args=(), daemon=True)
            re_press_thread.start()

        elif mode == "mult":

            mult_press_thread = threading.Thread(target=mult_press, args=(), daemon=True)
            mult_press_thread.start()

        elif mode == "keep":

            keep_press_thread = threading.Thread(target=keep_press, args=(), daemon=True)
            keep_press_thread.start()

    def toggle_source():

        source_name = path[redeem_reward_name]['source_name']
        time_show = path[redeem_reward_name]['time']
        keep = path[redeem_reward_name]['keep']

        send_response_value = path[redeem_reward_name]['send_response']

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']
            response_redus = replace_all(chat_response, aliases)

            if utils.send_message("RESPONSE"):
                chat.send(response_redus)

        obs_events.show_source(source_name, time_show, keep)

    def clip():

        info_clip = twitch_api.create_clip(broadcaster_id=BROADCASTER_ID)

        if 'error' in info_clip.keys():

            message_clip_error_load = messages_file_load('clip_error_clip')

            if utils.send_message("CLIP"):
                chat.send(message_clip_error_load)

        else:

            clip_id = info_clip['data'][0]['id']

            message_clip_user_load = messages_file_load('clip_create_clip')

            message_clip_user = message_clip_user_load.replace('{user}', redeem_by_user)
            message_final = message_clip_user.replace('{clip_id}', clip_id)

            if utils.send_message("CLIP"):
                chat.send(message_final)

            discord_config_file = open('web/src/config/discord.json', 'r', encoding='utf-8')
            discord_config_data = json.load(discord_config_file)

            webhook_status = discord_config_data['status']
            webhook_color = discord_config_data['color']
            webhook_url = discord_config_data['url']

            if webhook_status == 1:
                message_discord_load = messages_file_load('create_clip_discord')
                message_discord_desc_load = messages_file_load('clip_created_by')

                message_discord = message_discord_load.replace('{clip_id}', clip_id)

                webhook = DiscordWebhook(url=webhook_url)

                embed = DiscordEmbed(title=message_discord,
                                     description=message_discord_desc_load.replace('{user}', redeem_by_user),
                                     color=webhook_color)

                webhook.add_embed(embed)

                webhook.execute()

            discord_config_file.close()

    def add_counter():

        send_response_value = path[redeem_reward_name]['send_response']

        with open("web/src/counter/counter.txt", "r") as counter_file_r:

            if len(counter_file_r.read()) == 0:

                with open("web/src/counter/counter.txt", "w") as counter_file_w:
                    counter_file_w.write('1')

            else:

                counter_file_r.seek(0)
                digit = counter_file_r.read()

                if digit.isdigit():

                    counter = int(digit)
                    countercount = counter + 1

                else:
                    countercount = 0

                with open("web/src/counter/counter.txt", "w") as counter_file_w:
                    counter_file_w.write(str(countercount))

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']
            aliases['{counter}'] = str(countercount)

            try:
                response_redus = replace_all(chat_response, aliases)

                if utils.send_message("RESPONSE"):
                    chat.send(response_redus)
            except Exception as e:

                utils.error_log(e)

                if utils.send_message("RESPONSE"):
                    chat.send(chat_response)

    def add_giveaway():

        give_config_file = open("web/src/giveaway/config.json", "r", encoding='utf-8')
        give_config_data = json.load(give_config_file)

        enabled_give = give_config_data['enable']

        if enabled_give == 1:

            with open("web/src/giveaway/names.txt", "a+") as give_file_r:
                give_file_r.write(redeem_by_user + "\n")

                response_give_load = messages_file_load('giveaway_response_user_add')

            try:
                response_redus = replace_all(response_give_load, aliases)

                if utils.send_message("RESPONSE"):
                    chat.send(response_redus)

            except Exception as e:

                utils.error_log(e)

                if utils.send_message("RESPONSE"):
                    chat.send(response_give_load)
        else:

            response_give_disabled_load = messages_file_load('response_giveaway_disabled')

            if utils.send_message("RESPONSE"):
                chat.send(response_give_disabled_load)

    eventos = {

        'sound': play_sound,
        'scene': change_scene,
        'response': send_message,
        'filter': toggle_filter,
        'keypress': key_press,
        'source': toggle_source,
        'clip': clip,
        'tts': play_tts,
        'counter': add_counter,
        'giveaway': add_giveaway
    }

    if TOKEN and TOKENBOT:
        if redeem_reward_name in path.keys():
            redeem_type = path[redeem_reward_name]['type']
            if redeem_type in eventos:
                eventos[redeem_type]()
        elif redeem_reward_name == giveaway_redeem:
            add_giveaway()
        elif redeem_reward_name == player_reward:

            status_music = music_status_save('null', 'get')

            if status_music == 1:

                music_process_thread = threading.Thread(target=process_redem_music, args=(user_input, redeem_by_user,),
                                                        daemon=True)
                music_process_thread.start()
            else:
                aliases_commands = {'{user}': str(redeem_by_user)}
                message_replace_response = replace_all(messages_file_load('music_disabled'), aliases_commands)

                if utils.send_message("RESPONSE"):
                    chat.send(message_replace_response)


def pubsub_start():

    global pubsub

    pubsub = PubSub(twitch_api)
    pubsub.start()
    pubsub.listen_channel_points(BROADCASTER_ID, callback_whisper)


def pubsub_stop():
    pubsub.stop()

@eel.expose
def open_link(link_profile):

    webbrowser.open('https://www.twitch.tv/'+link_profile, new=0, autoraise=True)


def commands_module(data) -> None:

    def send_error_level(user_level, command):

        message_error_level_load = messages_file_load('error_user_level')

        message_error_level = message_error_level_load.replace('{user_level}', str(user_level))
        message_error_level_command = message_error_level.replace('{command}', str(command))

        if utils.send_message("ERROR_USER"):
            chat.send(message_error_level_command)

    message_sender = data['display_name']
    message_sender_id = data['user_id']
    message_mod = data['mod']
    message_sub = data['subscriber']
    message_text = data['message']

    if message_sub == '1':
        sub = 'True'
    else:
        sub = 'False'

    if message_mod == '1' or message_sender_id == BROADCASTER_ID:
        mod = 'True'
    else:
        mod = 'False'

    command_file = open('web/src/config/commands.json', "r", encoding='utf-8')
    command_data = json.load(command_file)

    command_file_prefix = open('web/src/config/commands_config.json', "r", encoding='utf-8')
    command_data_prefix = json.load(command_file_prefix)

    command_file_simple = open('web/src/config/simple_commands.json', "r", encoding='utf-8')
    command_data_simple = json.load(command_file_simple)

    command_file_tts = open('web/src/config/prefix_tts.json', "r", encoding='utf-8')
    command_data_tts = json.load(command_file_tts)

    command_file_counter = open('web/src/counter/commands.json', "r", encoding='utf-8')
    command_data_counter = json.load(command_file_counter)

    command_file_giveaway = open('web/src/giveaway/commands.json', "r", encoding='utf-8')
    command_data_giveaway = json.load(command_file_giveaway)

    command_file_player = open('web/src/player/config/commands.json', 'r', encoding='utf-8')
    command_data_player = json.load(command_file_player)

    command_string = message_text
    command_lower = command_string.lower()
    command = command_lower.split()[0]
    prefix = command[0]

    result_giveaway_check = {key: val for key, val in command_data_giveaway.items()
                             if val.startswith(command)}

    result_counter_check = {key: val for key, val in command_data_counter.items()
                            if val.startswith(command)}

    result_command_check = {key: val for key, val in command_data.items()
                            if key.startswith(command)}

    result_command_simple = {key: val for key, val in command_data_simple.items()
                             if key.startswith(command)}

    result_player_check = {key: val for key, val in command_data_player.items() if val.startswith(command)}

    user = message_sender

    if mod == 'True' or sub == 'True':
        user_type = 'mod'
    else:
        user_type = ''

    user_id_command = message_sender

    status_commands = command_data_prefix['STATUS_COMMANDS']
    status_tts = command_data_prefix['STATUS_TTS']

    command_tts = command_data_tts['command']
    user_type_tts = command_data_tts['user_level']

    def receive_tts():

        if status_tts == 1:

            message_delay, check_time = utils.check_delay()

            if check_time:

                if user_type == user_type_tts:

                    redeem = command_data_tts['redeem']

                    if len(command_lower.split(command_tts, 1)) > 1:
                        user_input = command_lower.split(command_tts, 1)[1]

                        data_rewards = {'USERNAME': user, 'REDEEM': redeem, 'USER_INPUT': user_input,
                                        'USER_LEVEL': user_type, 'USER_ID': user_id_command, 'COMMAND': command,
                                        'PREFIX': prefix}

                        received_type = 'command'

                        receive_thread = threading.Thread(target=receive_redeem, args=(data_rewards, received_type,),
                                                          daemon=True)
                        receive_thread.start()

                    else:

                        message_error_tts_no_txt = messages_file_load('error_tts_no_text')

                        if utils.send_message("RESPONSE"):
                            chat.send(message_error_tts_no_txt)
            else:

                if utils.send_message("ERROR_TIME"):
                    chat.send(message_delay)
        else:

            error_tts_disabled = messages_file_load('error_tts_disabled')

            if utils.send_message("RESPONSE"):
                chat.send(error_tts_disabled)

    if command_tts != "":

        check_tts = command.startswith(command_tts)

        if check_tts:
            eel.last_command(command_tts)
            receive_tts()

    if status_commands == 1:

        if command in result_command_check.keys():

            eel.last_command(command)

            redeem = command_data[command]['redeem']
            user_level = command_data[command]['user_level']

            data_rewards = {'USERNAME': user, 'REDEEM': redeem, 'USER_INPUT': command, 'USER_LEVEL': user_type,
                            'USER_ID': user_id_command, 'COMMAND': command, 'PREFIX': prefix}

            received_type = 'command'

            if user_type == user_level or user_type == 'mod':

                message_delay_global, check_time_global = utils.check_global_delay()

                if check_time_global:

                    receive_thread = threading.Thread(target=receive_redeem, args=(data_rewards, received_type,),
                                                      daemon=True)
                    receive_thread.start()

                else:

                    if utils.send_message("ERROR_TIME"):
                        chat.send(message_delay_global)
            else:

                send_error_level(str(user_level), str(command))

        elif command in result_command_simple.keys():

            eel.last_command(command)

            with open("web/src/counter/counter.txt", "r") as counter_file_r:
                counter_file_r.seek(0)
                counter = counter_file_r.read()

            response = command_data_simple[command]['response']
            user_level = command_data_simple[command]['user_level']

            if user_type == user_level or user_type == 'mod':

                aliases = {
                    '{user}': str(user),
                    '{command}': str(command),
                    '{prefix}': str(prefix),
                    '{user_level}': str(user_type),
                    '{user_id}': str(user_id_command),
                    '{counter}': str(counter)
                }

                response_redus = replace_all(str(response), aliases)

                message_delay_global, check_time_global = utils.check_global_delay()

                if check_time_global:

                    if utils.send_message("RESPONSE"):
                        chat.send(response_redus)

                else:

                    if utils.send_message("ERROR_TIME"):
                        chat.send(message_delay_global)

            else:

                send_error_level(str(user_level), str(command))

        elif command in result_counter_check.values():

            eel.last_command(command)

            if 'reset_counter' in result_counter_check.keys():

                if user_type == "mod":

                    message_delay_global, check_time_global = utils.check_global_delay()

                    if check_time_global:

                        with open("web/src/counter/counter.txt", "w") as counter_file_w:
                            counter_file_w.write('0')

                        response_reset = messages_file_load('response_reset_counter')
                        if utils.send_message("RESPONSE"):
                            chat.send(response_reset)

                    else:

                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay_global)
                else:
                    send_error_level('Moderador', str(command))

            elif 'set_counter' in result_counter_check.keys():

                if user_type == "mod":

                    message_delay_global, check_time_global = utils.check_global_delay()

                    if check_time_global:

                        if len(command_string.split()) > 1:

                            user_input = command_string.split()[1]

                            if user_input.isdigit():

                                with open("web/src/counter/counter.txt", "w") as counter_file_w:
                                    counter_file_w.write(str(user_input))

                                response_set = messages_file_load('response_set_counter')
                                response_set_repl = response_set.replace('{value}', user_input)

                                if utils.send_message("RESPONSE"):
                                    chat.send(response_set_repl)
                            else:

                                response_not_digit = messages_file_load('response_not_digit_counter')
                                if utils.send_message("RESPONSE"):
                                    chat.send(response_not_digit)
                        else:

                            response_null_counter = messages_file_load('response_null_set_counter')

                            if utils.send_message("RESPONSE"):
                                chat.send(response_null_counter)
                    else:

                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay_global)
                else:
                    send_error_level('Moderador', str(command))

            elif 'check_counter' in result_counter_check.keys():

                message_delay_global, check_time_global = utils.check_global_delay()

                if check_time_global:

                    with open("web/src/counter/counter.txt", "r") as counter_file_r:
                        counter_file_r.seek(0)
                        digit = counter_file_r.read()

                    response_check_counter = messages_file_load('response_counter')
                    response_check_repl = response_check_counter.replace('{value}', str(digit))

                    if utils.send_message("RESPONSE"):
                        chat.send(response_check_repl)
                else:
                    if utils.send_message("ERROR_TIME"):
                        chat.send(message_delay_global)

        elif command in result_giveaway_check.values():

            eel.last_command(command)

            if 'execute_giveaway' in result_giveaway_check.keys():

                if user_type == "mod":

                    message_delay_global, check_time_global = utils.check_global_delay()

                    if check_time_global:

                        giveaway_file = open('web/src/giveaway/config.json', 'r', encoding='utf-8')
                        giveaway_data = json.load(giveaway_file)

                        reset_give = giveaway_data['reset']

                        with open("web/src/giveaway/names.txt", "r") as give_file_check:
                            if len(give_file_check.read()) > 0:

                                with open("web/src/giveaway/names.txt", "r+") as give_file_r:
                                    lines = give_file_r.readlines()

                                    choice = randint(0, len(lines))
                                    name = lines[choice].replace('\n', '')

                                    message_win_load = messages_file_load('giveaway_response_win')

                                    message_win = message_win_load.replace('{name}', name)

                                    if utils.send_message("RESPONSE"):
                                        chat.send(message_win)

                                    with open("web/src/giveaway/backup.txt", "r+") as give_file_backup:
                                        give_file_backup.writelines(lines)

                                    with open("web/src/giveaway/result.txt", "w") as give_file_w:
                                        give_file_w.write(name)

                                    if reset_give == 1:
                                        give_file_r.truncate(0)

                    else:
                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay_global)

                else:

                    send_error_level('Moderador', str(command))

            elif 'clear_giveaway' in result_giveaway_check.keys():

                if user_type == "mod":

                    message_delay_global, check_time_global = utils.check_global_delay()

                    if check_time_global:

                        with open("web/src/giveaway/names.txt", "w") as counter_file_w:
                            counter_file_w.truncate(0)
                    else:

                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay_global)
                else:
                    send_error_level('Moderador', str(command))

                pass

            elif 'check_name' in result_giveaway_check.keys():

                if user_type == "mod":

                    message_delay_global, check_time_global = utils.check_global_delay()

                    if check_time_global:
                        user_input = command_string.split()[1]

                        with open("web/src/giveaway/names.txt", "r+") as give_file_r:
                            lines_giveaway = give_file_r.readlines()

                            name_user = user_input + '\n'

                            if name_user in lines_giveaway:

                                message_check_user = messages_file_load('response_user_giveaway')

                                message_check = message_check_user.replace('{user}', user_input)

                                if utils.send_message("RESPONSE"):
                                    chat.send(message_check)
                            else:

                                message_check_no_user_load = messages_file_load('response_nouser_giveaway')

                                message_check_no_user = message_check_no_user_load.replace('{user}', user_input)
                                if utils.send_message("RESPONSE"):
                                    chat.send(message_check_no_user)
                    else:

                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay_global)

                else:
                    send_error_level('Moderador', str(command))

            elif 'add_user' in result_giveaway_check.keys():

                if user_type == "mod":

                    message_delay_global, check_time_global = utils.check_global_delay()

                    if check_time_global:

                        print(command_string)

                        user_input = command_string.split()[1]

                        with open("web/src/giveaway/names.txt", "a+") as give_file_r:
                            give_file_r.write(user_input + "\n")

                        message_add_user_load = messages_file_load('giveaway_response_user_add')
                        message_add_user = message_add_user_load.replace('{user}', user_input)

                        if utils.send_message("RESPONSE"):
                            chat.send(message_add_user)

                    else:

                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay_global)

                else:
                    send_error_level('Moderador', str(command))

            elif 'check_self_name' in result_giveaway_check.keys():

                message_delay_global, check_time_global = utils.check_global_delay()

                if check_time_global:

                    with open("web/src/giveaway/names.txt", "r+") as give_file_r:
                        lines_giveaway = give_file_r.readlines()

                        name_user = user + '\n'

                        if name_user in lines_giveaway:

                            message_check_user_load = messages_file_load('response_user_giveaway')
                            message_check_user = message_check_user_load.replace('{user}', str(user))

                            if utils.send_message("RESPONSE"):
                                chat.send(message_check_user)

                        else:

                            message_no_user_giveaway_load = messages_file_load('response_nouser_giveaway')
                            message_no_user_giveaway = message_no_user_giveaway_load.replace('{user}', user)

                            if utils.send_message("RESPONSE"):
                                chat.send(message_no_user_giveaway)

                else:

                    if utils.send_message("ERROR_TIME"):
                        chat.send(message_delay_global)

        elif command in result_player_check.values():

            if 'volume' in result_player_check.keys():

                message_delay, check_time = utils.check_global_delay()

                if user_type == "mod":

                    if check_time:

                        prefix_volume = command_data_player['volume']

                        volume_value_command = command_lower.split(prefix_volume.lower(), 1)[1]
                        volume_value_int = int(volume_value_command)

                        if volume_value_int in range(0, 101):

                            volume_value = volume_value_int / 100
                            eel.player('volume', 'none', volume_value)

                            aliases_commands = {
                                '{user}': str(user),
                                '{volume}': str(volume_value_int)
                            }

                            message_replace_response = replace_all(messages_file_load('command_volume_confirm'),
                                                                   aliases_commands)

                            if utils.send_message("RESPONSE"):
                                chat.send(message_replace_response)

                        else:

                            aliases_commands = {
                                '{user}': user,
                                '{volume}': str(volume_value_int)
                            }
                            message_replace_response = replace_all(messages_file_load('command_volume_error'),
                                                                   aliases_commands)

                            if utils.send_message("RESPONSE"):
                                chat.send(message_replace_response)

                    else:
                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay)

                else:
                    send_error_level('Moderador', str(command))

            elif 'skip' in result_player_check.keys():

                message_delay, check_time = utils.check_global_delay()

                if user_type == "mod":

                    if check_time:

                        eel.player('stop', 'none', 'none')

                        aliases_commands = {
                            '{user}': str(user),
                        }
                        message_replace_response = replace_all(messages_file_load('command_skip_confirm'),
                                                               aliases_commands)

                        if utils.send_message("RESPONSE"):
                            chat.send(message_replace_response)


                    else:

                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay)

                else:

                    send_error_level('Moderador', str(command))

            elif 'request' in result_player_check.keys():

                message_delay, check_time = utils.check_global_delay()

                if user_type == 'mod':

                    if check_time:

                        prefix_sr = command_data_player['request']
                        user_input = command_string.split(" ", 1)[1]

                        if user_input != "":

                            player_file = open('web/src/player/config/redem_data.json')
                            player_data = json.load(player_file)

                            player_reward = player_data['title']

                            data_rewards = {'USERNAME': user, 'REDEEM': player_reward, 'USER_INPUT': user_input,
                                            'USER_LEVEL': user_type, 'USER_ID': user_id_command, 'COMMAND': command,
                                            'PREFIX': prefix}

                            received_type = 'command'

                            receive_thread = threading.Thread(target=receive_redeem,
                                                              args=(data_rewards, received_type,), daemon=True)
                            receive_thread.start()

                        else:

                            aliases_commands = {'{user}': str(user)}
                            message_replace_response = replace_all(messages_file_load('command_sr_error_link'),
                                                                   aliases_commands)

                            if utils.send_message("RESPONSE"):
                                chat.send(message_replace_response)

                    else:

                        if utils.send_message("ERROR_TIME"):
                            chat.send(message_delay)
                else:
                    send_error_level('Moderador', str(command))

            elif 'atual' in result_player_check.keys():

                message_delay, check_time = utils.check_global_delay()

                if check_time:

                    f = open('web/src/player/list_files/currentsong.txt', 'r+', encoding="utf-8")
                    current_song = f.read()

                    aliases_commands = {'{user}': str(user), '{music}': str(current_song)}
                    message_replace_response = replace_all(messages_file_load('command_current_confirm'),
                                                           aliases_commands)
                    if utils.send_message("RESPONSE"):
                        chat.send(message_replace_response)

                else:
                    if utils.send_message("ERROR_TIME"):
                        chat.send(message_delay)

            elif 'next' in result_player_check.keys():

                message_delay, check_time = utils.check_global_delay()

                if check_time:

                    playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
                    playlist_data = json.load(playlist_file)

                    queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
                    queue_data = json.load(queue_file)

                    check_playlist = any(playlist_data.keys())
                    check_queue = any(queue_data.keys())

                    if check_queue:

                        queue_keys = [int(x) for x in queue_data.keys()]
                        min_key_queue = min(queue_keys)
                        min_key_queue_str = str(min_key_queue)

                        next_song = queue_data[min_key_queue_str]['MUSIC_NAME']
                        resquest_by = queue_data[min_key_queue_str]['USER']

                        aliases_commands = {
                            '{user}': str(user),
                            '{music}': str(next_song),
                            '{request_by}': str(resquest_by)
                        }

                        response_replace = replace_all(messages_file_load('command_next_confirm'), aliases_commands)

                        if utils.send_message("RESPONSE"):
                            chat.send(response_replace)

                    elif check_playlist:

                        playlist_keys = [int(x) for x in playlist_data.keys()]
                        min_key_playlist = min(playlist_keys)
                        min_key_playlist_str = str(min_key_playlist)

                        next_song = playlist_data[min_key_playlist_str]['MUSIC_NAME']
                        resquest_by = playlist_data[min_key_playlist_str]['USER']

                        aliases_commands = {
                            '{user}': str(user),
                            '{music}': str(next_song),
                            '{request_by}': str(resquest_by)
                        }

                        response_replace = replace_all(messages_file_load('command_next_confirm'), aliases_commands)

                        if utils.send_message("RESPONSE"):
                            chat.send(response_replace)

                    else:

                        aliases_commands = {
                            '{user}': str(user),
                        }

                        response_replace = replace_all(messages_file_load('command_next_no_music'), aliases_commands)

                        if utils.send_message("RESPONSE"):
                            chat.send(response_replace)

                else:
                    if utils.send_message("ERROR_TIME"):
                        chat.send(message_delay)

    else:

        message_command_disabled = messages_file_load('commands_disabled')
        if utils.send_message("RESPONSE"):
            chat.send(message_command_disabled)


def command_fallback(message_data) -> None:
    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    message_parse = eel.parseMessage(message_data.text)()

    print(message_parse)
    if message_parse is not None:

        try:

            message_load = json.loads(message_parse)
            message_type = message_load['command']

            if message_type['command'] == 'JOIN':

                if message_load['parameters'] is not None:

                    if '/NAMES list' in message_load['parameters']:

                        string_to = message_load['parameters']

                        find_names = find_between(string_to, f'ROOMSTATE', 'End of /NAMES list')
                        filter_names = find_between(find_names, f'{BOTNAME} = #{USERNAME} :',
                                                    f'\r\n:{BOTNAME}.tmi.twitch.tv')
                        restult = filter_names.split(" ")

                        print(restult)
                        for item in restult:
                            namelist.append(item)

                        print(f"Lista = {namelist} | {restult}")
                        eel.users_chat(namelist)

                else:

                    source = message_load['source']
                    name_to_add = source['nick']

                    if name_to_add not in namelist:
                        namelist.append(name_to_add)

                        print(f"Nome adicionado = {name_to_add} | Lista = {namelist}")
                        eel.users_chat(namelist)

            if message_type['command'] == 'PART':

                source = message_load['source']
                name_to_remove = source['nick']

                if name_to_remove in namelist:
                    print(namelist)
                    namelist.remove(name_to_remove)

                    print(f"Nome removido = {name_to_remove} | Lista = {namelist}")
                    eel.users_chat(namelist)

            if message_type['command'] == 'PRIVMSG':

                tags = message_load['tags']
                source = message_load['source']

                data_res = {
                    'type': 'PRIVMSG',
                    "color": tags['color'],
                    "display_name": tags['display-name'],
                    "user_name": source['nick'],
                    "mod": tags['mod'],
                    "subscriber": tags['subscriber'],
                    "user_id": tags['user-id'],
                    "message": message_load['parameters']
                }

                message_data_dump = json.dumps(data_res, ensure_ascii=False)
                eel.append_message(message_data_dump)

                commands_module(data_res)

            if message_type['command'] == 'USERNOTICE':

                tags = message_load['tags']

                if tags['msg-id'] == 'resub':

                    data = {
                        'user' : tags['display-name'],
                        'months' : tags['msg-param-cumulative-months'],
                        'type' : tags['msg-param-sub-plan'],
                        'plan' : tags['msg-param-sub-plan-name'],
                        'gifted' : tags['msg-param-was-gifted'],
                        'system_msg' : tags['system-msg'],
                        'message' : message_load['parameters']
                    }

        except Exception as e:
            utils.error_log(e)


def check_bot():
    global chat_active

    while True:

        time.sleep(5)

        if loaded_status == 1:

            if not chat_active:

                data_res = {
                    "type": "CONN"
                }

                message_data_dump = json.dumps(data_res, ensure_ascii=False)
                eel.append_message(message_data_dump)

                time.sleep(2)

                bot_thread = threading.Thread(target=bot, args=(), daemon=True)
                bot_thread.start()

                chat_active = True

            else:

                chat_active = chat.irc.active


def eel_start(eel_mode):
    eel.init('web')

    if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:

        if eel_mode == "normal":

            eel.start("index.html", size=(1200, 680), port=8000, mode=None, shutdown_delay=0.0)

        elif eel_mode == "auth":

            eel.start("auth.html", size=(1200, 680), port=8000, mode=None, shutdown_delay=0.0)

    else:
        raise


def webview_start_app(app_mode):

    global window

    if app_mode == "normal":

        window = webview.create_window("RewardEvents 3.0", "http://localhost:8000/index.html", width=1200, height=680,
                                       min_size=(1200, 680), frameless=True, easy_drag=True)
        window.events.closed += pubsub.stop
        webview.start(debug=True, gui='edgechromium')

    elif app_mode == "auth":

        window = webview.create_window("RewardEvents auth", "http://localhost:8000/auth.html", width=1200, height=680,
                                       min_size=(1200, 680), frameless=True, easy_drag=True)

        webview.start()


def start_app(start_mode):

    if start_mode == "normal":

        pubsub_start()

        pygame.init()
        pygame.mixer.init()

        eel_thread = threading.Thread(target=eel_start, args=('normal',), daemon=True)
        eel_thread.start()

        timer_thread = threading.Thread(target=timer, args=(), daemon=True)
        timer_thread.start()

        check_bot_thread = threading.Thread(target=check_bot, args=(), daemon=True)
        check_bot_thread.start()

        obs_test_conn_thread = threading.Thread(target=obs_test_conn, args=(), daemon=True)
        obs_test_conn_thread.start()

        loopcheck_thread = threading.Thread(target=loopcheck, args=(), daemon=True)
        loopcheck_thread.start()

        get_users_info('save', 'null')

        webview_start_app('normal')

    elif start_mode == "auth":

        eel_thread = threading.Thread(target=eel_start, args=('auth',), daemon=True)
        eel_thread.start()

        webview_start_app('auth')


def update_auth_tkn(access_token, refresh_token):
    if USERNAME == BOTNAME:

        data_bot = {'USERNAME': USERNAME, 'BROADCASTER_ID': BROADCASTER_ID, 'CODE': CODE, 'TOKEN': access_token,
                    'REFRESH_TOKEN': refresh_token, 'TOKENBOT': access_token, 'BOTUSERNAME': BOTNAME}

        auth_file_bot = open("web/src/auth/auth.json", "w")
        json.dump(data_bot, auth_file_bot, indent=6, ensure_ascii=False)
        auth_file_bot.close()

    else:

        data_bot = {'USERNAME': USERNAME, 'BROADCASTER_ID': BROADCASTER_ID, 'CODE': CODE, 'TOKEN': access_token,
                    'REFRESH_TOKEN': refresh_token, 'TOKENBOT': TOKENBOT, 'BOTUSERNAME': BOTNAME}

        auth_file_bot = open("web/src/auth/auth.json", "w")
        json.dump(data_bot, auth_file_bot, indent=6, ensure_ascii=False)
        auth_file_bot.close()


def auto_refresh_token(token, refresh_token):
    if USERNAME == BOTNAME:

        data_bot = {'USERNAME': USERNAME, 'BROADCASTER_ID': BROADCASTER_ID, 'CODE': CODE, 'TOKEN': token,
                    'REFRESH_TOKEN': refresh_token, 'TOKENBOT': token, 'BOTUSERNAME': BOTNAME}

        auth_file_bot = open("web/src/auth/auth.json", "w")
        json.dump(data_bot, auth_file_bot, indent=6, ensure_ascii=False)
        auth_file_bot.close()

    else:

        data_bot = {'USERNAME': USERNAME, 'BROADCASTER_ID': BROADCASTER_ID, 'CODE': CODE, 'TOKEN': token,
                    'REFRESH_TOKEN': refresh_token, 'TOKENBOT': TOKENBOT, 'BOTUSERNAME': BOTNAME}

        auth_file_bot = open("web/src/auth/auth.json", "w")
        json.dump(data_bot, auth_file_bot, indent=6, ensure_ascii=False)
        auth_file_bot.close()


def start_auth_pub():

    global twitch_api

    if CODE and TOKENBOT:

        twitch_api = Twitch(clientid, clientsecret)

        twitch_api.user_auth_refresh_callback = auto_refresh_token

        scopes = [
            AuthScope.USER_READ_SUBSCRIPTIONS,
            AuthScope.USER_READ_EMAIL,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
            AuthScope.MODERATION_READ,
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.CLIPS_EDIT,
            AuthScope.CHAT_EDIT,
            AuthScope.CHAT_READ
        ]

        try:

            twitch_api.set_user_authentication(TOKEN, scopes, REFRESH_TOKEN)

            start_app('normal')

        except Exception as e:
            utils.error_log(e)
            try:

                token_new, refresh_token_new = refresh_access_token(REFRESH_TOKEN, clientid, clientsecret)
                update_auth_tkn(token_new, refresh_token_new)

                twitch_api.set_user_authentication(token_new, scopes, refresh_token_new)

                start_app('normal')

            except Exception as e:

                utils.error_log(e)

                start_app('auth')

    else:

        start_app('auth')


start_auth_pub()
