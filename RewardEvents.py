
import platform
import sys
import webview
import eel
import threading
import _thread

from dotenv import load_dotenv
import os

import obs_events
import time
import auth
import smt
import json
import twitch as twc
import html_edit
import pygame
import requests as req
import tkinter
import check_delay_file
import textwrap
import keyboard
import timer_module
import random

import yt_dlp
from pytube import Playlist, YouTube, Search
from albumart import album_search
from removesimbols import removestring
import validators
import webbrowser  

from io import BytesIO
from gtts import gTTS
from tkinter import filedialog as fd
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
from dateutil import tz
from random import randint

from discord_webhook import DiscordWebhook, DiscordEmbed

from uuid import UUID
from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch, AuthScope
from twitchAPI.oauth import refresh_access_token


extDataDir = os.getcwd()
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('Executando em Build')

    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS
else:
    print('Executando em modo dev')

load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

clientid = os.getenv('CLIENTID')
clientsecret = os.getenv('CLIENTSECRET')

global caching
caching = 0

USERNAME,BROADCASTER_ID,BOTNAME,CODE,TOKENBOT,TOKEN,REFRESH_TOKEN = auth.auth_data()

def messages_file_load(key):

    messages_file = open('web/src/messages/messages_file.json', "r", encoding='utf-8') 
    messages_data = json.load(messages_file) 

    message = messages_data[key]

    messages_file.close()

    return message

def error_log(ex):

    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    trace = []
    tb = ex.__traceback__

    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "lineno": tb.tb_lineno
        })
        tb = tb.tb_next

    error = str(f'Erro = type:{type(ex).__name__} | message: {str(ex)} | trace: {trace} | time: {time} \n')

    print(error)

    with open("web/src/config/error_log.txt", "a+",encoding='utf-8') as log_file_r:
            log_file_r.write(error)

def replace_all(text, dic):

    for i, j in dic.items():
        text = text.replace(i, j)
        
    return text

@eel.expose
def start_auth_window(username,type):
    
    def save_access_token_bot(code_received):

        out_file1 = open("web/src/auth/auth.json") 
        data1 = json.load(out_file1)
        
        username = data1['USERNAME']
        user_id = data1['BROADCASTER_ID']
        code_streamer = data1['CODE']
        user_token = data1['TOKEN']
        user_refresh_token = data1['REFRESH_TOKEN']
        bot_username = data1['BOTUSERNAME']

        data = {}
        data['USERNAME'] = username
        data['BROADCASTER_ID'] = user_id
        data['CODE'] = code_streamer
        data['TOKEN'] = user_token
        data['REFRESH_TOKEN'] = user_refresh_token
        data['TOKENBOT'] = code_received
        data['BOTUSERNAME'] = bot_username
        
        out_file = open("web/src/auth/auth.json", "w") 
        json.dump(data, out_file, indent = 6)  
        out_file.close()
        
        window_auth.load_html("<!DOCTYPE html>\n"
                    "<html lang='pt'>\n"
                    "<head>\n"
                    "<script type='text/javascript'>window.history.pushState('', '', '/');</script>"
                    "<meta charset='UTF-8'>\n"
                    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                    "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css'>\n"
                    "<title>Document</title>\n"
                    "</head>\n"
                    "<style>"
                    "html, body {height: 100%;}\n"
                    ".container {height: 100%;}\n"
                    "</style>\n"
                    "<body style='background-color: #191919;'>"
                    "<div class='container'>\n<div class='row h-100'>\n"
                    "<div class='col-sm-12 my-auto'>\n"
                    "<div class='card card-block w-50 mx-auto text-center' style='background-color: #4b1a6a;color:azure'>\n"
                    "<div class='card-body'>\n<h1 class='card-title'>Sucesso!</h5>\n<p class='card-text'>Pode fechar esta pagina.</p>\n"
                    "</div>\n</div>\n</div>\n</div>\n</div>\n</body>\n</html>")

        eel.auth_user_sucess('bot')

    def save_access_token(code_received):

        url_auth = "https://id.twitch.tv/oauth2/token"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        data_token = "client_id="+clientid+"&client_secret="+clientsecret+"&code="+code_received+"&grant_type=authorization_code&redirect_uri=http://localhost:5555"

        resp_token = req.post(url_auth, headers=headers, data=data_token)
        resp_token_data = json.loads(resp_token.text)

        access_token = resp_token_data['access_token']
        refresh_token = resp_token_data['refresh_token']

        out_file1 = open("web/src/auth/auth.json") 
        data1 = json.load(out_file1)
        
        username = data1['USERNAME']

        time.sleep(3)

        twitchAPI_auth = Twitch(clientid,clientsecret)

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

        twitchAPI_auth.set_user_authentication(access_token, scopes, refresh_token)

        user_id = twitchAPI_auth.get_users(logins=[username])
        user_id_resp = user_id['data'][0]['id']

        data = {}
        data['USERNAME'] = username
        data['BROADCASTER_ID'] = user_id_resp
        data['CODE'] = code_received
        data['TOKEN'] = access_token
        data['REFRESH_TOKEN'] = refresh_token
        data['TOKENBOT'] = ''
        data['BOTUSERNAME'] = ''
        
        out_file = open("web/src/auth/auth.json", "w") 
        json.dump(data, out_file, indent = 6)  
        out_file.close()
        
        window_auth.load_html("<!DOCTYPE html>\n"
                                "<html lang='pt'>\n"
                                "<head>\n"
                                "<script type='text/javascript'>window.history.pushState('', '', '/');</script>"
                                "<meta charset='UTF-8'>\n"
                                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                                "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css'>\n"
                                "<title>Document</title>\n"
                                "</head>\n"
                                "<style>"
                                "html, body {height: 100%;}\n"
                                ".container {height: 100%;}\n"
                                "</style>\n"
                                "<body style='background-color: #191919;'>"
                                "<div class='container'>\n<div class='row h-100'>\n"
                                "<div class='col-sm-12 my-auto'>\n"
                                "<div class='card card-block w-50 mx-auto text-center' style='background-color: #4b1a6a;color:azure'>\n"
                                "<div class='card-body'>\n<h1 class='card-title'>Sucesso!</h5>\n<p class='card-text'>Pode fechar esta pagina.</p>\n"
                                "</div>\n</div>\n</div>\n</div>\n</div>\n</body>\n</html>")

        eel.auth_user_sucess('streamer')

    def save_access_token_as_bot(code_received):

        url_auth = "https://id.twitch.tv/oauth2/token"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        data_token = "client_id="+clientid+"&client_secret="+clientsecret+"&code="+code_received+"&grant_type=authorization_code&redirect_uri=http://localhost:5555"

        resp_token = req.post(url_auth, headers=headers, data=data_token)
        resp_token_data = json.loads(resp_token.text)

        access_token = resp_token_data['access_token']
        refresh_token = resp_token_data['refresh_token']

        out_file1 = open("web/src/auth/auth.json") 
        data1 = json.load(out_file1)
        
        username = data1['USERNAME']
    
        time.sleep(3)

        twitchAPI_auth = Twitch(clientid,clientsecret)

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

        twitchAPI_auth.set_user_authentication(access_token, scopes, refresh_token)

        user_id = twitchAPI_auth.get_users(logins=[username])
        
        user_id_resp = user_id['data'][0]['id']
        data = {}
        data['USERNAME'] = username
        data['BROADCASTER_ID'] = user_id_resp
        data['CODE'] = code_received
        data['TOKEN'] = access_token
        data['REFRESH_TOKEN'] = refresh_token
        data['TOKENBOT'] = access_token
        data['BOTUSERNAME'] = username
        
        out_file = open("web/src/auth/auth.json", "w") 
        json.dump(data, out_file, indent = 6)  
        out_file.close()
        
        window_auth.load_html("<!DOCTYPE html>\n"
                                "<html lang='pt'>\n"
                                "<head>\n"
                                "<script type='text/javascript'>window.history.pushState('', '', '/');</script>"
                                "<meta charset='UTF-8'>\n"
                                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                                "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css'>\n"
                                "<title>Document</title>\n"
                                "</head>\n"
                                "<style>"
                                "html, body {height: 100%;}\n"
                                ".container {height: 100%;}\n"
                                "</style>\n"
                                "<body style='background-color: #191919;'>"
                                "<div class='container'>\n<div class='row h-100'>\n"
                                "<div class='col-sm-12 my-auto'>\n"
                                "<div class='card card-block w-50 mx-auto text-center' style='background-color: #4b1a6a;color:azure'>\n"
                                "<div class='card-body'>\n<h1 class='card-title'>Sucesso!</h5>\n<p class='card-text'>Pode fechar esta pagina.</p>\n"
                                "</div>\n</div>\n</div>\n</div>\n</div>\n</body>\n</html>")

        eel.auth_user_sucess('streamer_as_bot')

    def find_between(s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]

        except ValueError:

            return ""

    def on_loaded():

        uri = window_auth.get_current_url()
        try:

            if type == 'bot':
                access_token = find_between(uri,'#access_token=','&')
            else:
                access_token = find_between(uri,'?code=','&')

            if len(access_token) > 29:

                if type == 'bot':

                    save_access_token_bot(access_token)

                elif type == 'streamer':

                    save_access_token(access_token)

                elif type == 'streamer_as_bot':
                    
                    save_access_token_as_bot(access_token)


        except Exception as e:
            print(e)
            pass

    REDIRECT_URI ="http://localhost:5555"
    TWITCH_PREFIX = "https://api.twitch.tv/kraken/"
    SCOPE = "clips:edit+user:read:email+chat:edit+chat:read+channel:read:redemptions+moderation:read+channel:read:subscriptions+user:read:subscriptions"
    OAUTH_URI = TWITCH_PREFIX + "oauth2/authorize?response_type=code&force_verify=true&client_id="+ clientid +"&redirect_uri="+ REDIRECT_URI +"&scope="+ SCOPE
    OAUTH_URI_BOT = TWITCH_PREFIX + "oauth2/authorize?response_type=token&force_verify=true&client_id="+ clientid +"&redirect_uri="+ REDIRECT_URI +"&scope="+ SCOPE

    if type =='streamer':

        streamer_name = username
        data_user = {}
        data_user['USERNAME'] = streamer_name.lower()
        data_user['BROADCASTER_ID'] = ''
        data_user['CODE'] = ''
        data_user['TOKEN'] = ''
        data_user['REFRESH_TOKEN'] = ''
        data_user['TOKENBOT'] = ''
        data_user['BOTUSERNAME'] = ''
        
        auth_file_user = open("web/src/auth/auth.json", "w",encoding='utf-8') 
        json.dump(data_user, auth_file_user, indent = 6)  
        auth_file_user.close()

        window_auth = webview.create_window('Auth','')
        window_auth.load_url(OAUTH_URI)

        window_auth.events.loaded += on_loaded

    elif type =='bot':

        auth_file_bot_load = open("web/src/auth/auth.json") 
        data_bot_load = json.load(auth_file_bot_load)

        username_streamer = data_bot_load['USERNAME']
        user_id_streamer = data_bot_load['BROADCASTER_ID']
        code_streamer = data_bot_load['CODE']
        user_token_streamer = data_bot_load['TOKEN']
        user_refresh_token_streamer = data_bot_load['REFRESH_TOKEN']

        auth_file_bot_load.close()

        bot_username = username
        data_bot_save = {}
        data_bot_save['USERNAME'] = username_streamer
        data_bot_save['BROADCASTER_ID'] = user_id_streamer
        data_bot_save['CODE'] = code_streamer
        data_bot_save['TOKEN'] = user_token_streamer
        data_bot_save['REFRESH_TOKEN'] = user_refresh_token_streamer
        data_bot_save['TOKENBOT'] = ''
        data_bot_save['BOTUSERNAME'] = bot_username.lower()

        auth_file_bot = open("web/src/auth/auth.json", "w") 
        json.dump(data_bot_save, auth_file_bot, indent = 6)  
        auth_file_bot.close()

        window_auth = webview.create_window('Auth','')
        window_auth.load_url(OAUTH_URI_BOT)

        window_auth.events.loaded += on_loaded

    elif type =='streamer_as_bot':

        streamer_name = username
        data_user = {}
        data_user['USERNAME'] = streamer_name.lower()
        data_user['BROADCASTER_ID'] = ''
        data_user['CODE'] = ''
        data_user['TOKEN'] = ''
        data_user['REFRESH_TOKEN'] = ''
        data_user['TOKENBOT'] = ''
        data_user['BOTUSERNAME'] = streamer_name.lower()
        
        auth_file_user = open("web/src/auth/auth.json", "w",encoding='utf-8') 
        json.dump(data_user, auth_file_user, indent = 6)  
        auth_file_user.close()

        window_auth = webview.create_window('Auth','')
        window_auth.load_url(OAUTH_URI)

        window_auth.events.loaded += on_loaded

@eel.expose  
def close(mode): 

    if mode == 'auth':
        window.destroy()
        sys.exit(0)

    elif mode == 'normal':
        pubsub.stop()
        window.destroy()
        sys.exit(0)

@eel.expose
def minimize():
    window.minimize()

@eel.expose
def logout_auth():

    data = {}
    data['USERNAME'] = ''
    data['BROADCASTER_ID'] = ''
    data['CODE'] = ''
    data['TOKEN'] = ''
    data['REFRESH_TOKEN'] = ''
    data['CODEBOT'] = ''
    data['TOKENBOT'] = ''
    data['REFRESH_TOKENBOT'] = ''
    data['BOTUSERNAME'] = ''
    
    logout_file = open("web/src/auth/auth.json", "w") 
    json.dump(data, logout_file, indent = 6)  
    logout_file.close()

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

@eel.expose
def get_user_follow():

    file_follows = open('web/src/config/follow.txt','r+',encoding='utf-8')
    follow_name = file_follows.read()
    file_follows.close()

    try:

        data_follow = twitchAPI.get_users_follows(to_id=BROADCASTER_ID,first=1)
        
        last_follow_name = data_follow['data'][0]['from_name']

        if follow_name != last_follow_name :
            file_follows = open('web/src/config/follow.txt','w',encoding='utf-8')
            file_follows.write(last_follow_name)
            file_follows.close()

        return last_follow_name

    except Exception as e:

        error_log(e)

        return follow_name
    
@eel.expose
def get_spec():

    if TOKEN and TOKENBOT:

        try:
        
            data_count = twitchAPI.get_streams(user_login=[USERNAME])
            data_count_keys = data_count['data']
            name_last_folow = get_user_follow()

            timer_data_file = open('web/src/config/timer.json' , 'r', encoding='utf-8')
            timer_data = json.load(timer_data_file)

            message_key = timer_data['LAST']
            message_list = timer_data['MESSAGES']

            if message_key in message_list.keys():
                last_timer = message_list[message_key]
            else:
                last_timer = 'Nenhuma mensagem enviada'

            if data_count_keys == []:

                data_time = {
                    'specs' : 'Offline',
                    'time' : 'Offline',
                    'follow' : name_last_folow,
                    'last_timer' : last_timer
                }
                
                data_time_dump = json.dumps(data_time,ensure_ascii=False)

                return data_time_dump


            else:

                count = data_count['data'][0]['viewer_count']
                started = data_count['data'][0]['started_at']

                time_in_live  = calculate_time(started)

                data_time = {
                    'specs' : count,
                    'time' : time_in_live,
                    'follow' : name_last_folow,
                    'last_timer' : last_timer
                }
                
                data_time_dump = json.dumps(data_time,ensure_ascii=False)
                return data_time_dump
            
        except Exception as e:

            error_log(e)

            data_time = {
                'specs' : 'Offline',
                'time' : 'Offline',
                'follow' : '',
                'last_timer' : ''
            }
            
            data_time_dump = json.dumps(data_time,ensure_ascii=False)

            return data_time_dump

    else:
        return 'Offline'

@eel.expose
def profile_info():
    
    if TOKEN and TOKENBOT:
        
        
        user = twitchAPI.get_users(logins=[USERNAME])

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
            "user_id" : resp_user_id,
            "display_name" :  resp_display_name,
            "login_name" : resp_login_name,
            "email" : resp_email
        }

        
        
        data_auth_json = json.dumps(data_auth,ensure_ascii=False)

        return data_auth_json

@eel.expose
def get_redeem():
    
    
    list_titles = {"redeem":[]}
    path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8') 
    path = json.load(path_file)

    path_counter_file = open('web/src/counter/config.json', 'r', encoding='utf-8') 
    path_counter = json.load(path_counter_file)

    counter_redeem = path_counter['redeem']

    path_giveaway_file = open('web/src/giveaway/config.json', 'r', encoding='utf-8') 
    path_giveaway = json.load(path_giveaway_file)
    
    giveaway_redeem = path_giveaway['redeem']

    list_rewards = twitchAPI.get_custom_reward(broadcaster_id = BROADCASTER_ID)
    for indx in list_rewards['data'][0:] :
        
        if indx['title'] not in path and indx['title'] != giveaway_redeem and indx['title'] != counter_redeem:   
            list_titles["redeem"].append(indx['title'])

    list_titles_dump = json.dumps(list_titles,ensure_ascii=False)

    path_giveaway_file.close()
    path_counter_file.close()
    path_file.close()
    return list_titles_dump

@eel.expose
def get_redeem_created():
    
    list_titles = {"redeem":[]}
    path_file = open('web/src/config/pathfiles.json', 'r', encoding='utf-8') 
    path = json.load(path_file)

    for key in path:

        list_titles["redeem"].append(key)

    list_titles_dump = json.dumps(list_titles,ensure_ascii=False)

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

    old_data_command = open('web/src/config/commands.json' , 'r', encoding='utf-8') 
    new_data_command = json.load(old_data_command)
    
    new_data_command[command_value.lower()] = {'redeem': redeem_value,'user_level':user_level_value}
    old_data_command.close()
    
    old_data_write_command = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
    json.dump(new_data_command, old_data_write_command ,indent = 6,ensure_ascii=False)

    old_data_write_command.close()

@eel.expose
def create_audio(data):
    
    data_receive = json.loads(data)

    try:

        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']
        audio_path = data_receive['audio_path']

        if chat_response == "":
            send_response = 0
        else:
            send_response = 1
            
        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {
            
            'type': 'sound',
            'path': audio_path,
            'command': command_value.lower(), 
            'send_response': send_response, 
            'chat_response':chat_response
                        }

        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6,ensure_ascii=False)
        
        old_data_write.close()

        if command_value != "":
            create_command_redeem(data_receive)

        eel.modal_actions('sucess-audio-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-audio-create')
    
@eel.expose
def create_tts(data):

    data_receive = json.loads(data)

    try:

        redeem_value = data_receive['redeem_value']
        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        characters = data_receive['characters']
        user_level_value = data_receive['user_level_value']


        if chat_response == "":
            send_response = 0
        else:
            send_response = 1
            
        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {

            'type': 'tts',
            'send_response':send_response, 
            'chat_response':chat_response, 
            'command':command_value.lower(),
            'characters': characters

            }

        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6,ensure_ascii=False)
        old_data_write.close()
        if command_value != "":

            old_data_command = open('web/src/config/prefix_tts.json' , 'r', encoding='utf-8') 
            new_data_command = json.load(old_data_command)

            new_data_command['command'] = command_value.lower()
            new_data_command['redeem'] = redeem_value
            new_data_command['user_level'] = user_level_value
            
            old_data.close()
            
            old_data_write_command = open('web/src/config/prefix_tts.json' , 'w', encoding='utf-8') 
            json.dump(new_data_command, old_data_write_command , indent = 6, ensure_ascii=False)
            old_data_write_command.close()

        eel.modal_actions('sucess-tts-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-tts-create')

@eel.expose
def create_scene(data):

    data_receive = json.loads(data)

    try:

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
            
        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {

            'type': 'scene',
            'send_response':send_response,
            'command': command_value.lower(),
            'chat_response':chat_response,
            'scene_name': scene_name,
            'keep':keep_scene_value,
            'time':int(time_to_return)
            }

        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6,ensure_ascii=False)
        old_data_write.close()
        if command_value != "":
            create_command_redeem(data_receive)

        eel.modal_actions('sucess-scene-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-scene-create')

@eel.expose
def create_response(data):
            
    data_receive = json.loads(data)

    try:            
        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']
            
        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {
            'type': 'response', 
            'command': command_value.lower(), 
            'chat_response': chat_response
            }

        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6, ensure_ascii=False)
        old_data_write.close()

        if command_value != "":
            create_command_redeem(data_receive)
    

        eel.modal_actions('sucess-response-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-response-create')

@eel.expose            
def create_filter(data):

    data_receive = json.loads(data)

    try:
                
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
            
        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {

            'type': 'filter',
            'source_name': source_name, 
            'send_response':send_response, 
            'chat_response':chat_response, 
            'command': command_value.lower(), 
            'filter':filter_name, 
            'keep': keep,
            'time':int(time_showing)
            }

        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6, ensure_ascii=False)
        old_data_write.close()

        if command_value != "":
            create_command_redeem(data_receive)
        
        eel.modal_actions('sucess-filter-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-filter-create')

@eel.expose 
def create_keypress(data):

    data_receive = json.loads(data)

    try:
                
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

                
        key_data_file = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        key_data = json.load(key_data_file)

        if mode_press == 'mult':

            mult_press_times = data_receive['mult_press_times']
            mult_press_interval = data_receive['mult_press_interval']

            key_data[redeem_value] = {

                'type': 'keypress',
                'send_response': send_response, 
                'chat_response': chat_response,
                'command': command_value.lower(),
                'mode' :  mode_press,
                'mult_press_times' : int(mult_press_times),
                'mult_press_interval' : int(mult_press_interval),
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
                'mode' :  mode_press,
                're_press_time' : int(re_press_time),
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
                'mode' :  mode_press,
                'keep_press_time' : int(keep_press_time),
                'key1': key1, 
                'key2': key2, 
                'key3': key3, 
                'key4': key4
                }

        key_data_file.close()

        key_data_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(key_data, key_data_file_write, indent = 6, ensure_ascii=False)
        key_data_file_write.close()

        if command_value != "":
            create_command_redeem(data_receive)
    
        eel.modal_actions('sucess-keypress-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-keypress-create')

@eel.expose 
def create_source(data):

    data_receive = json.loads(data)

    try:

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
            
        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {

            'type': 'source',
            'send_response':send_response, 
            'chat_response':chat_response,
            'command': command_value.lower(), 
            'source_name': source_name,
            'keep' : keep,
            'time': int(time_showing)

            }

        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6 ,ensure_ascii=False)
        old_data_write.close()
        
        if command_value != "":
            create_command_redeem(data_receive)

    
        eel.modal_actions('sucess-source-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-source-create')
    
@eel.expose
def create_clip(data):
    
    data_receive = json.loads(data)

    try:
                
        command_value = data_receive['command_value']
        redeem_value = data_receive['redeem_value']

        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {'type': 'clip','command': command_value.lower(),}
        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6,ensure_ascii=False)

        if command_value != "":
            create_command_redeem(data_receive)

        old_data_write.close()
        eel.modal_actions('sucess-clip-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-clip-create')

@eel.expose
def create_counter(data):
    
    data_receive = json.loads(data)

    try:
                
        command_value = data_receive['command_value']
        redeem_value = data_receive['redeem_value']
        chat_response = data_receive['chat_response']

        if chat_response == "":
            send_response = 0
        else:
            send_response = 1
            
        old_data = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        new_data[redeem_value] = {

            'type': 'counter',
            'command': command_value.lower(),
            'send_response':send_response, 
            'chat_response':chat_response

            }

        old_data.close()

        old_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6,ensure_ascii=False)
        old_data_write.close()

        if command_value != "":
            create_command_redeem(data_receive)


        eel.modal_actions('sucess-counter-create')

    except Exception as e:

        error_log(e)

        eel.modal_actions('error-counter-create')

@eel.expose
def del_action_py(value):

    try:

        data_event_file = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
        data_event = json.load(data_event_file)

        command = data_event[value]['command']

        data_command_file = open('web/src/config/commands.json' , 'r', encoding='utf-8') 
        data_command = json.load(data_command_file)

        if command in data_command.keys():
            del data_command[command]

            data_command_file.close()

            command_data_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
            json.dump(data_command, command_data_write, indent = 6, ensure_ascii=False)
            command_data_write.close()
        else:
            data_command_file.close()


        del data_event[value]
        data_event_file.close()

        event_data_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(data_event, event_data_write, indent = 6, ensure_ascii=False)

        event_data_write.close()

        eel.modal_actions('modal_del_sucess')

    except Exception as e:

        error_log(e)
        eel.modal_actions('modal_del_error')

@eel.expose
def add_new_timer_message(message):

    try:
    
        timer_data_file = open('web/src/config/timer.json' , 'r', encoding='utf-8') 
        timer_data = json.load(timer_data_file)
        
        timer_message = timer_data['MESSAGES']
        
        qnt = len(timer_message) + 1
        int_qnt = int(qnt)
        
        timer_data['MESSAGES'][int_qnt] = message
        timer_data_file.close()
        
        old_data_write = open('web/src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(timer_data, old_data_write, indent = 6,ensure_ascii=False)
        old_data_write.close()

        eel.sucess_add_message()

    except Exception as e:

        error_log(e)
        eel.error_add_message()

@eel.expose        
def create_command(data_receive):

    data = json.loads(data_receive)

    try:
        command = data['new_command']
        message = data['new_message']
        user_level_check = data['new_user_level']


        old_data_command = open('web/src/config/simple_commands.json' , 'r', encoding='utf-8') 
        new_data_command = json.load(old_data_command)
        
            
        new_data_command[command.lower()] = {
            'response': message, 
            'user_level': user_level_check
            }
        
        old_data_command.close()

        old_data_write_command = open('web/src/config/simple_commands.json' , 'w', encoding='utf-8') 
        json.dump(new_data_command, old_data_write_command , indent = 6, ensure_ascii=False)
        old_data_write_command.close()

        eel.command_modal('sucess-command-create')

    except Exception as e:
        error_log(e)
        
        eel.command_modal('sucess-command-create')

@eel.expose
def del_command(command):

    try:
        old_data = open('web/src/config/simple_commands.json' , 'r', encoding='utf-8') 
        new_data = json.load(old_data)

        del new_data[command]
        old_data.close()

        old_data_write = open('web/src/config/simple_commands.json' , 'w', encoding='utf-8') 
        json.dump(new_data, old_data_write, indent = 6, ensure_ascii=False)
        old_data_write.close()

        eel.command_modal('sucess-command-del')

    except Exception as e:

        error_log(e)
        
        eel.command_modal('sucess-command-del')

@eel.expose
def get_command_info(command):

    old_data = open('web/src/config/simple_commands.json' , 'r', encoding='utf-8') 
    new_data = json.load(old_data)

    message = new_data[command]['response']
    user_level = new_data[command]['user_level']

    data = {
        'edit_command' : command,
        'edit_message' : message,
        'edit_level' : user_level,
    }

    old_data.close()
    data_dump = json.dumps(data,ensure_ascii=False)

    return data_dump

@eel.expose
def get_commands_list():

    old_data = open('web/src/config/simple_commands.json' , 'r', encoding='utf-8') 
    new_data = json.load(old_data)

    list_commands = []

    for key in new_data:

        list_commands.append(key)

    list_commands_dump = json.dumps(list_commands,ensure_ascii=False)

    old_data.close()
    return list_commands_dump

@eel.expose        
def edit_command(data_receive):

    data = json.loads(data_receive)

    try:
    
        old_command = data['old_command']
        new_command = data['edit_command']
        new_message = data['edit_message']
        user_level = data['edit_user_level']
        
        command_data_file = open('web/src/config/simple_commands.json' , 'r', encoding='utf-8') 
        command_data = json.load(command_data_file)

        del command_data[old_command]
        command_data[new_command] = {
            "response" : new_message,
            "user_level" : user_level
        }
                
        command_data_file.close()

        old_data_write = open('web/src/config/simple_commands.json' , 'w', encoding='utf-8') 
        json.dump(command_data, old_data_write, indent = 6, ensure_ascii=False)
        old_data_write.close()

        eel.command_modal('sucess-command-edit')

    except Exception as e:

        error_log(e)

        eel.command_modal('error-command-edit')

@eel.expose
def get_delay_info():

    time_delay_file = open('web/src/config/commands_config.json')
    time_delay_data = json.load(time_delay_file)

    command_delay = time_delay_data['delay_config']
    time_delay_file.close()
    
    time_delay_write = open('web/src/config/commands_config.json' , 'w', encoding='utf-8') 
    json.dump(time_delay_data, time_delay_write, indent = 6, ensure_ascii=False)
    time_delay_write.close()

    time_delay_file_tts = open('web/src/config/prefix_tts.json')
    time_delay_data_tts = json.load(time_delay_file_tts)

    tts_delay = time_delay_data_tts['delay_config']
    time_delay_file_tts.close()
    
    time_delay_write_tts = open('web/src/config/prefix_tts.json' , 'w', encoding='utf-8') 
    json.dump(time_delay_data_tts, time_delay_write_tts, indent = 6, ensure_ascii=False)
    time_delay_write_tts.close()

    data = {
        "command_delay": command_delay,
        "tts_delay" : tts_delay
    }

    delay_data = json.dumps(data,ensure_ascii=False)

    return delay_data

@eel.expose              
def edit_delay_commands(value_commands,value_tts):
    

    try:

        time_delay_file = open('web/src/config/commands_config.json')
        time_delay_data = json.load(time_delay_file)

        time_delay_data['delay_config'] = int(value_commands)
        time_delay_file.close()
        
        time_delay_write = open('web/src/config/commands_config.json' , 'w', encoding='utf-8') 
        json.dump(time_delay_data, time_delay_write, indent = 6, ensure_ascii=False)
        time_delay_write.close()

        time_delay_file_tts = open('web/src/config/prefix_tts.json')
        time_delay_data_tts = json.load(time_delay_file_tts)

        time_delay_data_tts['delay_config'] = int(value_tts)
        time_delay_file_tts.close()
        
        time_delay_write_tts = open('web/src/config/prefix_tts.json' , 'w', encoding='utf-8') 
        json.dump(time_delay_data_tts, time_delay_write_tts, indent = 6, ensure_ascii=False)
        time_delay_write_tts.close()

        eel.command_modal('sucess-command-delay')
    
    except Exception as e:

        error_log(e)
        eel.command_modal('error-command-delay')

@eel.expose
def get_timer_info():

    timer_data_file = open('web/src/config/timer.json','r',encoding='utf-8')
    timer_data = json.load(timer_data_file)

    message_file_get = open('web/src/config/commands_config.json' , 'r', encoding="utf-8") 
    message_data_get = json.load(message_file_get)

    status_timer = message_data_get['STATUS_TIMER']
    timer_delay_min = timer_data['TIME']
    timer_delay_max = timer_data['TIME_MAX']
    messages_list = timer_data['MESSAGES']

    data = {
        "delay_min" : timer_delay_min,
        "delay_max" : timer_delay_max,
        "messages" : messages_list,
        "status" : status_timer 
    }

    timer_data_file.close()
    message_file_get.close()

    timer_data = json.dumps(data,ensure_ascii=False)

    return timer_data

@eel.expose
def get_message_timer(message_id):

    timer_data_file = open('web/src/config/timer.json','r',encoding='utf-8')
    timer_data = json.load(timer_data_file)

    message = timer_data['MESSAGES'][message_id]

    timer_data_file.close()

    return message

@eel.expose
def edit_timer(key,message):

    try:
        timer_data_file = open('web/src/config/timer.json','r',encoding='utf-8')
        timer_data = json.load(timer_data_file)

        timer_data['MESSAGES'][key] = message
        timer_data_file.close()

        timer_data_file_w = open('web/src/config/timer.json','w',encoding='utf-8')
        json.dump(timer_data, timer_data_file_w, indent = 6, ensure_ascii=False)
        timer_data_file_w.close()
        
        eel.timer_modal('sucess-timer')
    
    except Exception as e:

        error_log(e)

        eel.timer_modal('error-timer')

@eel.expose
def add_timer(message):

    try:

        timer_data_file = open('web/src/config/timer.json' , 'r', encoding='utf-8') 
        timer_data = json.load(timer_data_file)
        
        timer_message = timer_data['MESSAGES']

        if not timer_message:

            keytoadd = 1

        else:
            key = list(timer_message.keys())[-1]
            keytoadd = int(key) + 1
        
        timer_data['MESSAGES'][str(keytoadd)] = message

        timer_data_file.close()
        
        old_data_write = open('web/src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(timer_data, old_data_write, indent = 6,ensure_ascii=False)

        old_data_write.close()

        eel.timer_modal('sucess-timer')
    
    except Exception as e:

        error_log(e)

        eel.timer_modal('error-timer')

@eel.expose
def del_timer(message_key):

    try:
        
        message_del_file = open('web/src/config/timer.json' , 'r', encoding='utf-8') 
        message_del_data = json.load(message_del_file)

        del message_del_data['MESSAGES'][message_key]

        message_del_file.close()
        
        message_del_file_write = open('web/src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(message_del_data, message_del_file_write, indent = 6,ensure_ascii=False)
        message_del_file_write.close()

        eel.timer_modal('sucess-timer')
    
    except Exception as e:

        error_log(e)

        eel.timer_modal('error-timer')

@eel.expose
def edit_delay_timer(min,max):

    try:
        
        message_del_file = open('web/src/config/timer.json' , 'r', encoding='utf-8') 
        message_del_data = json.load(message_del_file)

        message_del_data['TIME'] = int(min)
        message_del_data['TIME_MAX'] = int(max)

        message_del_file.close()
        
        message_del_file_write = open('web/src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(message_del_data, message_del_file_write, indent = 6,ensure_ascii=False)
        message_del_file_write.close()

        eel.timer_modal('sucess-timer')
    
    except Exception as e:

        error_log(e)

        eel.timer_modal('error-timer')

@eel.expose
def timer_status_save(status):

    message_file = open('web/src/config/commands_config.json' , 'r', encoding="utf-8") 
    message_data = json.load(message_file)

    message_data['STATUS_TIMER'] = status

    message_file.close()

    old_data_write = open('web/src/config/commands_config.json' , 'w', encoding="utf-8") 
    json.dump(message_data, old_data_write, indent = 6, ensure_ascii=False)
    old_data_write.close()

@eel.expose
def get_obs_conn_info_py():

    obs_conn_file = open('web/src/config/obs.json' , 'r', encoding='utf-8') 
    obs_conn_file_data = json.load(obs_conn_file)

    host = obs_conn_file_data['OBS_HOST']
    port = obs_conn_file_data['OBS_PORT']
    password = obs_conn_file_data['OBS_PASSWORD']
    auto_conn = obs_conn_file_data['OBS_TEST_CON']

    data = {
        "host" : host,
        "port" : port,
        "password" : password,
        "auto_conn" : auto_conn
    }

    obs_conn_file.close()

    conm_data = json.dumps(data,ensure_ascii=False)

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
        json.dump(data_save, out_file, indent=6,ensure_ascii=False)
        out_file.close()

        eel.config_modal('sucess-config-obs-conn')

    except Exception as e:

        error_log(e)

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

            'HTML_PLAYER_ACTIVE' : music_active,
            'HTML_ACTIVE': active,
            'HTML_TITLE': source, 
            'HTML_TIME': int(time_showing_not),
        }

        out_file = open("web/src/config/notfic.json", "w", encoding='utf-8')
        json.dump(data_save, out_file, indent=6,ensure_ascii=False)
        out_file.close()

        eel.config_modal('sucess-config-obs-not')

    except Exception as e:

        error_log(e)

        eel.config_modal('error-config-obs-not')

@eel.expose
def get_messages_config():

    message_file_get = open('web/src/config/commands_config.json' , 'r', encoding="utf-8") 
    message_data_get = json.load(message_file_get)

    status_tts = message_data_get['STATUS_TTS'] ,
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

    messages_data_dump = json.dumps(messages_data_get,ensure_ascii=False)

    return  messages_data_dump

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

        old_message_file = open('web/src/config/commands_config.json' , 'r', encoding="utf-8") 
        old_message_data = json.load(old_message_file)

        old_message_file.close

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

        old_data_write = open('web/src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(old_message_data, old_data_write, indent = 6, ensure_ascii=False)
        old_data_write.close()

        eel.modal_messages_config('sucess')

    except Exception as e:

        error_log(e)

        eel.modal_messages_config('error')

@eel.expose
def get_giveaway_info():

    giveaway_file = open('web/src/giveaway/config.json','r',encoding='utf-8')
    giveaway_data = json.load(giveaway_file)

    giveaway_name = giveaway_data['name']
    giveaway_level = giveaway_data['user_level']
    giveaway_enable = giveaway_data['enable']
    giveaway_clear = giveaway_data['clear']
    giveaway_redeem = giveaway_data['redeem']

    giveaway_file.close()

    data = {
        "giveaway_name" : giveaway_name,
        "giveaway_level" : giveaway_level,
        "giveaway_clear" : giveaway_clear,
        "giveaway_enable" : giveaway_enable,
        "giveaway_redeem" : giveaway_redeem
    }

    data_dump = json.dumps(data,ensure_ascii=False)

    return  data_dump

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
            "name" : giveaway_name,
            "redeem" : giveaway_redeem,
            "user_level" : giveaway_level,
            "clear" : giveaway_clear,
            "enable" : giveaway_enable,
        }

        old_data_write = open('web/src/giveaway/config.json' , 'w', encoding="utf-8") 
        json.dump(giveaway_data_new, old_data_write, indent = 6, ensure_ascii=False)
        old_data_write.close()

        eel.giveaway_modal_show('giveaway-sucess-save','none')

    except Exception as e:

        error_log(e)

        eel.giveaway_modal_show('giveway-error-save','none')

@eel.expose
def save_giveaway_commands_py(data_receive):

    data = json.loads(data_receive)

    execute_giveaway = data['execute_giveaway']
    user_check_giveaway = data['check_user_giveaway']
    self_check_giveaway = data['self_check_giveaway']
    clear_giveaway = data['clear_giveaway']
    add_user_giveaway = data['add_user_giveaway']

    try:

        giveaway_data_new = {
            "execute_giveaway" : execute_giveaway,
            "clear_giveaway" : user_check_giveaway,
            "check_name" : self_check_giveaway,
            "check_self_name" : clear_giveaway,
            "add_user" : add_user_giveaway,
        }

        old_data_write = open('web/src/giveaway/commands.json' , 'w', encoding="utf-8") 
        json.dump(giveaway_data_new, old_data_write, indent = 6, ensure_ascii=False)
        old_data_write.close()

        eel.giveaway_modal_show('giveaway-sucess-save','none')

    except Exception as e:

        error_log(e)

        eel.giveaway_modal_show('giveway-error-save','none')

@eel.expose
def get_giveaway_commands():

    giveaway_commands_file = open('web/src/giveaway/commands.json','r',encoding='utf-8')
    giveaway_commands_data = json.load(giveaway_commands_file)

    execute_giveaway = giveaway_commands_data['execute_giveaway']
    user_check_giveaway = giveaway_commands_data['check_name']
    self_check_giveaway = giveaway_commands_data['check_self_name']
    clear_giveaway = giveaway_commands_data['clear_giveaway']
    add_user_giveaway = giveaway_commands_data['add_user']

    giveaway_commands_file.close()
    data = {

        "execute_giveaway" : execute_giveaway,
        "user_check_giveaway" : user_check_giveaway,
        "self_check_giveaway" : self_check_giveaway,
        "clear_giveaway" : clear_giveaway,
        "add_user_giveaway" : add_user_giveaway
    }


    data_dump = json.dumps(data,ensure_ascii=False)

    return  data_dump

@eel.expose
def get_giveaway_names():

    giveaway_commands_file = open('web/src/giveaway/names.json','r',encoding='utf-8')
    giveaway_commands_data = json.load(giveaway_commands_file)

    
    data_dump = json.dumps(giveaway_commands_data,ensure_ascii=False)

    giveaway_commands_file.close()

    return  data_dump

@eel.expose
def execute_giveaway():

    try:
        giveaway_file = open('web/src/giveaway/config.json','r',encoding='utf-8')
        giveaway_data = json.load(giveaway_file)

        reset_give = giveaway_data['clear']
        giveaway_file.close()

        giveaway_name_file = open('web/src/giveaway/names.json','r',encoding='utf-8')
        giveaway_name_data = json.load(giveaway_name_file)

        name = random.choice(giveaway_name_data)
        giveaway_name_file.close()


        message_load_winner_giveaway = messages_file_load('giveaway_response_win')

        message_win = message_load_winner_giveaway.replace('{name}',name)
        smt.send_message(message_win,'RESPONSE')

        giveaway_backup_file = open('web/src/giveaway/backup.json' , 'w', encoding="utf-8") 
        json.dump(giveaway_name_data, giveaway_backup_file, indent = 6, ensure_ascii=False)
        giveaway_backup_file.close()

        giveaway_result_file = open('web/src/giveaway/result.json' , 'w', encoding="utf-8") 
        json.dump(name, giveaway_result_file, indent = 6, ensure_ascii=False)
        giveaway_backup_file.close()
        
        if reset_give == 1:

            reset_data = []

            giveaway_reset_file = open('web/src/giveaway/names.json' , 'w', encoding="utf-8") 
            json.dump(reset_data, giveaway_reset_file, indent = 6, ensure_ascii=False)
            giveaway_reset_file.close()

        
        eel.giveaway_modal_show('giveway-winner',name)
        
    except Exception as e:

        error_log(e)

        eel.giveaway_modal_show('giveway-error-execute',name)

@eel.expose
def clear_name_list():

    try:

        reset_data = []

        giveaway_reset_file = open('web/src/giveaway/names.json' , 'w', encoding="utf-8") 
        json.dump(reset_data, giveaway_reset_file, indent = 6, ensure_ascii=False)
        giveaway_reset_file.close()
    
        eel.giveaway_modal_show('giveaway-clear-sucess','none')


    except Exception as e:
        error_log(e)

        eel.giveaway_modal_show('giveaway-clear-error','none')

@eel.expose
def add_name_giveaway(new_name):

    try:
        giveaway_name_file = open('web/src/giveaway/names.json','r',encoding='utf-8')
        giveaway_name_data = json.load(giveaway_name_file)

        names = giveaway_name_data
        names.append(new_name)

        giveaway_name_file.close()

        giveaway_save_file = open('web/src/giveaway/names.json' , 'w', encoding="utf-8") 
        json.dump(names, giveaway_save_file, indent = 6, ensure_ascii=False)
        giveaway_save_file.close()

        eel.giveaway_modal_show('giveaway-add-name',new_name)


    except Exception as e:
        error_log(e)

        eel.giveaway_modal_show('giveaway-add-name-error',new_name)

@eel.expose
def counter(fun_id,redeem,commands,value):

    if fun_id == 'get_counter_redeem':

        counter_file = open('web/src/counter/config.json','r',encoding='utf-8')
        counter_data = json.load(counter_file)

        counter_commands_file = open('web/src/counter/commands.json','r',encoding='utf-8')
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

            "redeem" : counter_redeem,
            "value_counter" : counter_value_get,
            "counter_command_reset" : counter_command_reset,
            "counter_command_set" : counter_command_set,
            "counter_command_check" : counter_command_check,
        }

        counter_data_parse = json.dumps(data,ensure_ascii=False)

        return counter_data_parse

    if fun_id == "save_counter_redeem":


        try:

            data_save = {
                "redeem" : redeem
            }

            counter_file_save = open('web/src/counter/config.json','w',encoding='utf-8')
            json.dump(data_save,counter_file_save,indent = 6,ensure_ascii=False)
            counter_file_save.close()

            eel.counter_modal('save_redeem_sucess')

        except Exception as e:

            error_log(e)

            eel.counter_modal('save_redeem_error')
    
    if fun_id == "save-counter-commands":

        data_received = json.loads(commands)

        try:
            counter_command_check_save = data_received['counter_command_check']
            counter_command_reset_save = data_received['counter_command_reset']
            counter_command_apply_save = data_received['counter_command_apply']

            commands_save = {
                "reset_counter" : counter_command_reset_save,
                "set_counter" : counter_command_apply_save,
                "check_counter" : counter_command_check_save,
            }

            counter_file_save_commands = open('web/src/counter/commands.json','w',encoding='utf-8')
            json.dump(commands_save,counter_file_save,indent = 6,ensure_ascii=False)
            counter_file_save_commands.close()

            eel.counter_modal('save_commands_sucess')

        except Exception as e:

            error_log(e)

            eel.counter_modal('save_commands_error')

    if fun_id == "set-counter-value" :
        
        with open("web/src/counter/counter.txt", "w") as counter_file_w:      
            counter_file_w.write(str(value))

@eel.expose
def responses_config(fun_id,response_key,message):

    if fun_id == 'get_response':

        responses_file = open('web/src/messages/messages_file.json','r',encoding='utf-8')
        responses_data = json.load(responses_file)

        response = responses_data[response_key]

        responses_file.close()
        return response

    elif fun_id == 'save_response':

        try:

            responses_file = open('web/src/messages/messages_file.json','r',encoding='utf-8')
            responses_data = json.load(responses_file)

            responses_data[response_key] = message

            responses_file.close()
            responses_file_w = open('web/src/messages/messages_file.json','w',encoding='utf-8')
            json.dump(responses_data,responses_file_w,indent = 6,ensure_ascii=False)

            responses_file_w.close()
            eel.modal_responses('modal-sucess-response')
        
        except Exception as e:

            eel.modal_responses('modal-error-response')
            error_log(e)

@eel.expose
def discord_config(data_discord_save,mode):

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

            discord_data_file = open('web/src/config/discord.json','w',encoding='utf-8')
            json.dump(discord_data_save,discord_data_file,indent = 6,ensure_ascii=False)
            discord_data_file.close()

            responses_file = open('web/src/messages/messages_file.json','r',encoding='utf-8')
            responses_data = json.load(responses_file)

            responses_data['create_clip_discord'] = embed_title
            responses_data['create_clip_discord_edit'] = embed_title_edit
            responses_data['clip_created_by'] = embed_description

            responses_file.close()

            responses_file_w = open('web/src/messages/messages_file.json','w',encoding='utf-8')
            json.dump(responses_data,responses_file_w,indent = 6,ensure_ascii=False)
            responses_file_w.close()

            eel.modal_discord('sucess-discord-config')

        except Exception as e:

            eel.modal_discord('error-discord-config')
            error_log(e)

    if mode == 'get':

        responses_file_discord = open('web/src/messages/messages_file.json','r', encoding='utf-8')
        responses_data_discord = json.load(responses_file_discord)

        embed_title = responses_data_discord['create_clip_discord']
        embed_title_edit = responses_data_discord['create_clip_discord_edit']
        embed_description = responses_data_discord['clip_created_by']

        responses_file_discord.close()

        discord_data_file = open('web/src/config/discord.json','r',encoding='utf-8')
        discord_data = json.load(discord_data_file)

        url_webhook = discord_data['url'] 
        url_webhook_edit = discord_data['url_edit']
        embed_color = discord_data['color']
        status = discord_data['status']
        satus_edit =  discord_data['status_edit']

        discord_data_file.close()

        data_get = {

            "url_webhook" : url_webhook,
            "url_webhook_edit" : url_webhook_edit,
            "embed_color" : embed_color,
            "embed_title" : embed_title,
            "embed_title_edit" : embed_title_edit,
            "embed_description" : embed_description,
            "status" : status,
            "satus_edit" : satus_edit,
        }

        
        data_get_sent = json.dumps(data_get,ensure_ascii=False)

        return data_get_sent

@eel.expose
def obs_try_conn():

    _thread.start_new_thread(obs_test_conn, (3,))

@eel.expose
def send_message_chat(message):

    smt.send_message(message,'CHAT')

@eel.expose
def save_disclosure(disclosure):

    file_disclosure = open('web/src/config/disclosure.txt','w',encoding='utf-8')
    file_disclosure.write(disclosure)
    file_disclosure.close()

@eel.expose
def load_disclosure():

    file_disclosure = open('web/src/config/disclosure.txt','r',encoding='utf-8')
    disclosure = file_disclosure.read()

    if disclosure == "":
        disclosure = 'Digite aqui a sua mensagem rápida de divulgação em chats'

    return disclosure

@eel.expose
def get_edit_data(redeen,type_action):

    redeem_file = open('web/src/config/pathfiles.json' , 'r', encoding='utf-8') 
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
            "sound" : sound,
            "command" :command,
            "response_status": response_status,
            "user_level" : command_level,
            "response":response,
        }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

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
            "characters" : characters,
            "command" :command,
            "response_status": response_status,
            "user_level" : user_level,
            "response":response,
        }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

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
            "command" :command,
            "user_level" : command_level,
            "response":response,
        }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'scene':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        scene_name = redeem_data[redeen]['scene_name']
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
            "command" :command,
            "response_status": response_status,
            "user_level" : command_level,
            "response":response,
            "scene_name" : scene_name,
            "keep" : keep,
            "time" : time
        }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'filter':

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
            "command" :command,
            "response_status": response_status,
            "user_level" : command_level,
            "response": response,
            "keep": keep,
            "time": time
        }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

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
            "command" :command,
            "response_status": response_status,
            "user_level" : command_level,
            "response": response,
            "keep": keep,
            "time": time
        }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

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
                "command" :command,
                "response_status": response_status,
                "user_level" : command_level,
                "response": response,
                "mode": mode,
                "keep_press_time": keep_press_time,
                "key1": key1,
                "key2": key2,
                "key3": key3,
                "key4": key4
            }

        elif mode == 'mult':

            time_press = redeem_data[redeen]['mult_press_times']
            interval = redeem_data[redeen]['mult_press_interval']

            redeem_data_return = {

                "command" :command,
                "response_status": response_status,
                "user_level" : command_level,
                "response": response,
                "mode" : mode,
                "time_press": time_press,
                "interval": interval,
                "key1": key1,
                "key2": key2,
                "key3": key3,
                "key4": key4
            }

        elif mode == 're':

            re_press_time = redeem_data[redeen]['re_press_time']

            redeem_data_return = {

                "command" :command,
                "response_status": response_status,
                "user_level" : command_level,
                "response": response,
                "mode" : mode,
                "re_press_time": re_press_time,
                "key1": key1,
                "key2": key2,
                "key3": key3,
                "key4": key4
            }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

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
            "command" :command,
            "user_level" : command_level,
        }

        redeem_data_dump = json.dumps(redeem_data_return,ensure_ascii=False)

        return redeem_data_dump

@eel.expose
def save_edit_redeen(data,redeem_type):

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
                'command':  command,
                'send_response': send_message,
                'chat_response': chat_message,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            command_file = open('web/src/config/commands.json', "r", encoding='utf-8') 
            command_data = json.load(command_file) 

            if old_command != command and old_command != "":
                
                del command_data[old_command]

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                        }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                    command_file_write.close()


                command_file.close()

                command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                command_file_write.close()

            elif old_command != command and old_command == "":

                print('SEGUNDA')

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                    }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)
 

            eel.modal_edit_actions('sucess','edit-audio-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-audio-div')
            
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
                'command':  command,
                'send_response': send_message,
                'chat_response': chat_message,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            tts_command_file = open('web/src/config/prefix_tts.json' , 'r', encoding='utf-8') 
            tts_command_data = json.load(tts_command_file)

            tts_command_data['command'] = command.lower()
            tts_command_data['redeem'] = redeem
            tts_command_data['user_level'] = user_level
            
            tts_command_file.close()
            
            tts_command_file_write = open('web/src/config/prefix_tts.json' , 'w', encoding='utf-8') 
            json.dump(tts_command_data, tts_command_file_write , indent = 6, ensure_ascii=False)
            tts_command_file_write.close()

            eel.modal_edit_actions('sucess','edit-tts-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-tts-div')
            
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
                'command':  command,
                'send_response': send_message,
                'chat_response': chat_message,
                'scene': scene_name,
                'keep': keep,
                'time' : time
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            command_file = open('web/src/config/commands.json', "r", encoding='utf-8') 
            command_data = json.load(command_file) 

            if old_command != command and old_command != "":
                
                del command_data[old_command]

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                        }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                    command_file_write.close()


                command_file.close()

                command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                command_file_write.close()


            eel.modal_edit_actions('sucess','edit-scene-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-scene-div')
      
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
                'command':  command,
                'send_response': send_message,
                'chat_response': chat_message,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            command_file = open('web/src/config/commands.json', "r", encoding='utf-8') 
            command_data = json.load(command_file) 

            if old_command != command and old_command != "":
                
                del command_data[old_command]

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                        }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                    command_file_write.close()


                command_file.close()

                command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                command_file_write.close()


            eel.modal_edit_actions('sucess','edit-response-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-response-div')
      
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
                'command':  command,
                'send_response': send_message,
                'chat_response': chat_message,
                'source_name' : source_name,
                'filter_name' : filter_name,
                'keep': keep,
                'time': time   
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            command_file = open('web/src/config/commands.json', "r", encoding='utf-8') 
            command_data = json.load(command_file) 

            if old_command != command and old_command != "":
                
                del command_data[old_command]

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                        }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                    command_file_write.close()


                command_file.close()

                command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                command_file_write.close()


            eel.modal_edit_actions('sucess','edit-filter-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-filter-div')

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
                'command':  command,
                'send_response': send_message,
                'chat_response': chat_message,
                'source_name': source_name,
                'keep': keep ,
                'time': time
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            command_file = open('web/src/config/commands.json', "r", encoding='utf-8') 
            command_data = json.load(command_file) 

            if old_command != command and old_command != "":
                
                del command_data[old_command]

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                        }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                    command_file_write.close()


                command_file.close()

                command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                command_file_write.close()


            eel.modal_edit_actions('sucess','edit-source-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-source-div')

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
                    'mode' :  mode_press,
                    'mult_press_times' : int(mult_press_times),
                    'mult_press_interval' : int(mult_press_interval),
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
                    'mode' :  mode_press,
                    're_press_time' : int(re_press_time),
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
                    'mode' :  mode_press,
                    'keep_press_time' : int(keep_press_time),
                    'key1': key1, 
                    'key2': key2, 
                    'key3': key3, 
                    'key4': key4
                    }


            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            command_file = open('web/src/config/commands.json', "r", encoding='utf-8') 
            command_data = json.load(command_file) 

            if old_command != command and old_command != "":
                
                del command_data[old_command]

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                        }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                    command_file_write.close()


                command_file.close()

                command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                command_file_write.close()

            eel.modal_edit_actions('sucess','edit-keypress-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-keypress-div')

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
                'command':  command,
            }

            path_file.close()

            path_file_write = open('web/src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(path_data, path_file_write, indent = 6,ensure_ascii=False)
            
            command_file = open('web/src/config/commands.json', "r", encoding='utf-8') 
            command_data = json.load(command_file) 

            if old_command != command and old_command != "":
                
                del command_data[old_command]

                if command != "":

                    command_data[command.lower()] = {
                        'redeem': redeem,
                        'user_level':user_level
                        }

                    command_file.close()

                    command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                    command_file_write.close()


                command_file.close()

                command_file_write = open('web/src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(command_data, command_file_write, indent = 6,ensure_ascii=False)

                command_file_write.close()


            eel.modal_edit_actions('sucess','edit-clip-div')

        except Exception as e:

            error_log(e)

            eel.modal_edit_actions('error','edit-clip-div')

@eel.expose
def add_playlist(playlist_url):
    
    def start_add(tid):
        
        try:
            
            p = Playlist(playlist_url)

            playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
            playlist_data = json.load(playlist_file)
            
            check_have = any(playlist_data.keys())
            playlist_file.close()

            if check_have == False:

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

                    eel.playlist_stats_music('Adicionando, aguarde... '+ video_title_short,'Add')
                    
                    playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
                    playlist_data = json.load(playlist_file)

                    playlist_data[last_key] = {"MUSIC":url,"USER":"playlist","MUSIC_NAME":video_title}
                    playlist_file.close()

                    playlist_file_write = open('web/src/player/list_files/playlist.json', "w", encoding="utf-8")
                    json.dump(playlist_data,playlist_file_write, indent = 4, ensure_ascii=False)
                    playlist_file_write.close()

                except Exception as e:

                    error_log(e)

            eel.playlist_stats_music('None','Close')
            
        except Exception as e:

            error_log(e)


    _thread.start_new_thread(start_add, (8,))
            
@eel.expose
def playlist_clear_py():

    playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
    playlist_data = json.load(playlist_file)

    playlist_data = {}
    playlist_file.close()

    playlist_file_write = open('web/src/player/list_files/playlist.json', "w", encoding="utf-8")
    json.dump(playlist_data,playlist_file_write, indent = 4,ensure_ascii=False)
    playlist_file_write.close()

@eel.expose
def playlist_execute_save(value,type_rec):

    if type_rec == 'save':

        value_status = value
        
        playlist_stats_data_file = open('web/src/player/config/playlist.json' , 'r',encoding="utf-8") 
        playlist_stats_data = json.load(playlist_stats_data_file)
        
        playlist_stats_data['STATUS'] = value_status
        playlist_stats_data_file.close()
        
        old_data_write = open('web/src/player/config/playlist.json' , 'w',encoding="utf-8") 
        json.dump(playlist_stats_data, old_data_write, indent = 4)
        old_data_write.close()  

    elif  type_rec == 'get':

        playlist_stats_data_file = open('web/src/player/config/playlist.json' , 'r',encoding="utf-8") 
        playlist_stats_data = json.load(playlist_stats_data_file)
        
        value_status = playlist_stats_data['STATUS'] 
        playlist_stats_data_file.close()

        return value_status

@eel.expose
def music_status_save(status,type_id):

    if type_id == 'save':

        status_music_file = open('web/src/player/config/playlist.json' , 'r', encoding="utf-8") 
        status_music_data = json.load(status_music_file)

        status_music_data['STATUS_MUSIC_ENABLE'] = status
        status_music_file.close()

        status_music_file_write = open('web/src/player/config/playlist.json' , 'w', encoding="utf-8") 
        json.dump(status_music_data, status_music_file_write, indent = 6, ensure_ascii=False)
        status_music_file_write.close()

    elif type_id == 'get':

        status_music_file = open('web/src/player/config/playlist.json' , 'r', encoding="utf-8") 
        status_music_data = json.load(status_music_file)

        status = status_music_data['STATUS_MUSIC_ENABLE']

        status_music_file.close()

        return status

@eel.expose
def get_music_config_py():

    commands_music_file = open('web/src/player/config/commands.json','r',encoding='utf-8')
    commands_music_data = json.load(commands_music_file)

    command_request = commands_music_data['request']
    command_volume = commands_music_data['volume']
    command_skip = commands_music_data['skip']
    command_next = commands_music_data['next']
    command_atual = commands_music_data['atual']

    commands_music_file.close()

    not_music_file = open('web/src/config/notfic.json','r',encoding='utf-8')
    not_music_data = json.load(not_music_file)

    not_status = not_music_data['HTML_PLAYER_ACTIVE']


    data = {
        "not_status" : not_status,
        "cmd_request" : command_request,
        "cmd_volume" : command_volume,
        "cmd_skip" : command_skip,
        "cmd_next" : command_next,
        "cmd_atual" : command_atual
    }

    music_dump = json.dumps(data,ensure_ascii=False)

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

        not_status_music_file = open('web/src/config/notfic.json' , 'r', encoding="utf-8") 
        not_status_music_data = json.load(not_status_music_file)

        not_status_music_data['HTML_PLAYER_ACTIVE'] = status_music
        not_status_music_file.close()

        status_music_file_write = open('web/src/config/notfic.json' , 'w', encoding="utf-8") 
        json.dump(not_status_music_data, status_music_file_write, indent = 6, ensure_ascii=False)
        status_music_file_write.close()

        commands_music_file = open('web/src/player/config/commands.json','r',encoding='utf-8')
        commands_music_data = json.load(commands_music_file)

        commands_music_data['request'] = command_request
        commands_music_data['volume'] = command_volume
        commands_music_data['skip'] = command_skip
        commands_music_data['next'] = command_next
        commands_music_data['atual'] = command_atual

        commands_music_file_w = open('web/src/player/config/commands.json','w',encoding='utf-8')
        json.dump(commands_music_data, commands_music_file_w, indent = 6, ensure_ascii=False)

        redeem_music_file = open('web/src/player/config/redem_data.json','r',encoding='utf-8')
        redeem_music_data = json.load(redeem_music_file)

        redeem_music_data['title'] = redeem

        redeem_music_file_w = open('web/src/player/config/redem_data.json','w',encoding='utf-8')
        json.dump(redeem_music_data, redeem_music_file_w, indent = 6, ensure_ascii=False)

        eel.config_modal('sucess-config-music')

    except Exception as e:
        error_log(e)
        
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

    data_dump = json.dumps(list_queue_list,ensure_ascii=False)

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

def start_play(user_input, redem_by_user):

    def my_hook(d):

        if d['status'] == 'downloading':

            percent = d['_percent_str']
            try:
                percent_numbers = int(float(percent.split()[0].replace('%',''))) / 10
            except:
                pass


        if d['status'] == 'finished':
            pass

    def download_music(link):

        music_dir_check = os.path.exists(sys._MEIPASS + '/web/src/player/cache/music.mp3')
        music_mp4_check = os.path.exists(sys._MEIPASS + '/web/src/player/cache/music.mp4')
        
        if music_mp4_check :
            os.remove(sys._MEIPASS + '/web/src/player/cache/music.mp4')

        if music_dir_check :
            os.remove(sys._MEIPASS + '/web/src/player/cache/music.mp3')
        
        try:
            ## sys._MEIPASS
            ## 'ffmpeg/ffmpeg.exe'
            ydl_opts={
                'final_ext': 'mp3',
                'format': 'best',
                'noplaylist': True,
                'quiet' : True,
                'no_color': True,
                'outtmpl': sys._MEIPASS + '/web/src/player/cache/music.%(ext)s',
                'ffmpeg_location': sys._MEIPASS,
                'force-write-archive' : True,
                'force-overwrites' : True, 
                'keepvideo' : True,
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
            
        except:

            return False

    global caching

    response_album = album_search(user_input, redem_by_user)
    success = response_album['success']

    if success == 1:

        media_name = response_album['music']
        media_artist = response_album['artist']
        music_link = response_album['link']

        yt = YouTube(music_link)
        music_leght = yt.length

        if music_leght < 600:

            caching = 1

            if download_music(music_link) == True:
            
                if media_artist == '0':
                    music_artist = ""
                else:
                    music_artist = media_artist

                with open('web/src/player/list_files/currentsong.txt', "w", encoding="utf-8") as file_object:
                    file_object.write(media_name + music_artist + '\n')
                    file_object.close()
                
                music_name_short = textwrap.shorten(media_name, width=13, placeholder="...")

                html_edit.update_notif(music_name_short,redem_by_user,music_artist,'music')
                _thread.start_new_thread(obs_events.notification_player, (5,))
                eel.update_music_name(media_name,music_artist)

                aliases = {
                    '{music_name}' : media_name,
                    '{music_name_short}' : music_name_short,
                    '{music_artist}' : music_artist,
                    '{user}' : redem_by_user
                    }

                message_replace = replace_all(messages_file_load('music_playing'),aliases)
                smt.send_message(message_replace,'STATUS_MUSIC')

                eel.player('play','http://localhost:8000/src/player/cache/music.mp3','1')

                caching = 0

            else:

                caching = 0
                smt.send_message(messages_file_load('music_process_cache_error'),'STATUS_MUSIC')

        else:

            aliases = {
                '{music_name}' : media_name,
                '{user}' : redem_by_user
                }

            message_replace = replace_all(messages_file_load('music_leght_error'),aliases)
            smt.send_message(message_replace,'STATUS_MUSIC')

    else:
        smt.send_message(messages_file_load('music_process_error'),'STATUS_MUSIC')

def loopcheck(tid):
    
    time.sleep(5)

    while True:

        playlist_status_file = open('web/src/player/config/playlist.json' , 'r',encoding="utf-8")
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


        playing = eel.player('playing','none','none')()

        if caching == 0 and playing == 'False':

            if check_have_queue == True:   

                queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
                queue_data = json.load(queue_file)

                queue_keys = [int(x) for x in queue_data.keys()]
                music_data_key = str(min(queue_keys))

                music = queue_data[music_data_key]['MUSIC']
                user = queue_data[music_data_key]['USER']
                music_name = queue_data[music_data_key]['MUSIC_NAME']

                del queue_data[music_data_key]

                queue_file.close()

                queue_file_write = open('web/src/player/list_files/queue.json', "w", encoding="utf-8")
                json.dump(queue_data,queue_file_write, indent = 4)
                queue_file_write.close()

                start_play(music, user)

                time.sleep(5)

                        
            elif check_have_playlist == True:   

                if playlist_execute == 1:
                    
                    playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
                    playlist_data = json.load(playlist_file)

                    playlist_keys = [int(x) for x in playlist_data.keys()]
                    music_data = str(min(playlist_keys))

                    music = playlist_data[music_data]['MUSIC']
                    user = playlist_data[music_data]['USER']
                    music_name = playlist_data[music_data]['MUSIC_NAME']

                    del playlist_data[music_data]

                    playlist_file.close()

                    playlist_file_write = open('web/src/player/list_files/playlist.json', "w", encoding="utf-8")
                    json.dump(playlist_data,playlist_file_write, indent = 4)
                    playlist_file_write.close()

                    start_play(music, user)


                else:
                    time.sleep(3)
            else:
                time.sleep(3)
        else:
            time.sleep(3)       
   
def obs_test_conn(tid):

    time.sleep(5)
    sucess_conn = obs_events.test_obs_conn()

    if sucess_conn == True:

        eel.callback_obs('sucess')

    elif sucess_conn == False:

        eel.callback_obs('error')

    elif sucess_conn == 'None':
        pass

def callback_whisper(uuid: UUID, data: dict) -> None:
    received_type = 'redeem'
    _thread.start_new_thread(receive_redeem, (3,data,received_type))

def receive_redeem(tid,data_rewards,received_type):

    def process_redem_music(tid,user_input,redem_by_user):

        eel.update_music_name('Processando musica','Processando musica')

        queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
        queue_data = json.load(queue_file)

        check_have = any(queue_data.keys())

        if check_have == False:
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

                        queue_data[last_key] = {"MUSIC":user_input, "USER":redem_by_user, "MUSIC_NAME": music_name}
                        queue_file.close()

                        queue_file_write = open('web/src/player/list_files/queue.json', "w", encoding="utf-8")
                        json.dump(queue_data,queue_file_write, indent = 4)
                        queue_file_write.close()
                        
                        aliases = {'{user}': redem_by_user,'{user_input}': user_input,'{music}': music_name}
                        message = messages_file_load('music_added_to_queue')
                        message_replaced = replace_all(message,aliases)

                        smt.send_message(message_replaced,'STATUS_MUSIC_CONFIRM')
                    
                    else:

                        music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                        aliases = {
                            '{user}': str(redem_by_user),
                            '{user_input}': str(user_input),
                            '{music}': str(music_name),
                            '{music_short}': str(music_name_short)
                            }

                        message = messages_file_load('music_leght_error')
                        message_replaced = replace_all(message,aliases)

                        smt.send_message(message_replaced,'STATUS_MUSIC_CONFIRM')

                except:

                    aliases = {'{user}': str(redem_by_user),'{user_input}': str(user_input)}
                    message = messages_file_load('music_add_error')
                    message_replaced = replace_all(message,aliases)

                    smt.send_message(message_replaced,'STATUS_MUSIC_CONFIRM')

            else :
                smt.send_message(messages_file_load('music_link_youtube'),'STATUS_MUSIC_ERROR')

        else:
            
            music_name = removestring(user_input)

            search_youtube = Search(music_name)
            result_search = search_youtube.results[0].__dict__
            url_youtube = result_search['watch_url']

            yt = YouTube(url_youtube)
            video_title = yt.title

            queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
            queue_data = json.load(queue_file)

            queue_data[last_key] = {"MUSIC": music_name, "USER":redem_by_user, "MUSIC_NAME": music_name}
            queue_file.close()

            queue_file_write = open('web/src/player/list_files/queue.json', "w", encoding="utf-8")
            json.dump(queue_data,queue_file_write, indent = 4)
            queue_file_write.close()

            music_name_short = textwrap.shorten(video_title, width=13, placeholder="...")

            aliases = {
                '{user}': redem_by_user,
                '{user_input}': user_input,
                '{music}': video_title,
                '{music_short}': music_name_short
                }

            message = messages_file_load('music_added_to_queue')

            message_replaced = replace_all(message,aliases)

            smt.send_message(message_replaced,'STATUS_MUSIC_CONFIRM')

    with open("web/src/counter/counter.txt", "r") as counter_file_r:
        counter_file_r.seek(0)
        digit = counter_file_r.read()    
        counter = int(digit)
                
    redeem_reward_name = '0'
    redeem_by_user = '0'
    user_input = '0'
    user_level =  '0'
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

        if data_rewards['data']['redemption']['reward']['image'] == None:
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
        user_level =  data_rewards['USER_LEVEL']
        user_id_command = data_rewards['USER_ID']
         
        command_receive = data_rewards['COMMAND']
        prefix = data_rewards['PREFIX']

    redeem_data_js = {
        "redeem_name" : redeem_reward_name,
        "redeem_user" : redeem_by_user
    }

    aliases = {

        '{user}': str(redeem_by_user),
        '{command}': str(command_receive), 
        '{prefix}': str(prefix),
        '{user_level}':str(user_level), 
        '{user_id}': str(user_id_command),
        '{user_input}': str(user_input),
        '{counter}' : str(counter)

        }

    redeem_data_js_parse = json.dumps(redeem_data_js,ensure_ascii=False)

    eel.update_div_redeem(redeem_data_js_parse)

    html_edit.update_notif(redeem_reward_name,redeem_by_user,'None','redeem')

    _thread.start_new_thread(obs_events.notification, (5,))

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
            smt.send_message(response_redus,'RESPONSE')

    def play_tts():

        send_response_value = path[redeem_reward_name]['send_response']
        characters = path[redeem_reward_name]['characters']
        characters_int = int(characters)
        
        user_input_short = textwrap.shorten(user_input, width=characters_int ,placeholder=" ")
        
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
                smt.send_message(response_redus,'RESPONSE')
            except Exception as e:

                error_log(e)
                smt.send_message(chat_response,'RESPONSE')

    def change_scene():
        
        scene_name = path[redeem_reward_name]['scene_name']
        keep = path[redeem_reward_name]['keep']
        time_show = path[redeem_reward_name]['time']
        send_response_value = path[redeem_reward_name]['send_response']
        
        if send_response_value == 1:

            chat_response = path[redeem_reward_name]['chat_response']
        
            try:
                response_redus = replace_all(chat_response, aliases)
                smt.send_message(response_redus,'RESPONSE')
            except Exception as e:

                error_log(e)
                smt.send_message(chat_response,'RESPONSE')

        obs_events.show_scene(scene_name,time_show,keep)
            
    def send_message():

        chat_response = path[redeem_reward_name]['chat_response']
        
        try:
            response_redus = replace_all(chat_response, aliases)
            smt.send_message(response_redus,'RESPONSE')
        except Exception as e:

            error_log(e)
            smt.send_message(chat_response,'RESPONSE')

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
                smt.send_message(response_redus,'RESPONSE')
            except Exception as e:

                error_log(e)
                smt.send_message(chat_response,'RESPONSE')

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
                smt.send_message(response_redus,'RESPONSE')

            except Exception as e:

                error_log(e)
                smt.send_message(chat_response,'RESPONSE')
        

        def mult_press(tid):

            mult_press_times = path[redeem_reward_name]['mult_press_times']
            mult_press_interval = path[redeem_reward_name]['mult_press_interval']

            value_repeated = 0
            
            while value_repeated < mult_press_times:

                value_repeated = value_repeated + 1

                received = [*keyskeyboard.keys()][7:]
                keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']

                keyboard.press_and_release('+'.join(keys_to_pressed))

                time.sleep(mult_press_interval)

        def re_press(tid):

            re_press_time = path[redeem_reward_name]['re_press_time']

            received = [*keyskeyboard.keys()][6:]

            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']

            keyboard.press_and_release('+'.join(keys_to_pressed))
            
            time.sleep(re_press_time)
            
            keyboard.press_and_release('+'.join(keys_to_pressed))
            
        def keep_press(tid):

            keep_press_time = path[redeem_reward_name]['keep_press_time']

            received = [*keyskeyboard.keys()][6:]

            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']

            keyboard.press('+'.join(keys_to_pressed))
            keyboard.block_key('+'.join(keys_to_pressed))

            time.sleep(keep_press_time)

            keyboard.release('+'.join(keys_to_pressed))


        if mode == "re":

            _thread.start_new_thread(re_press, (4,))
            
        elif mode == "mult":

            _thread.start_new_thread(mult_press, (5,))

        elif mode == "keep":
  
            _thread.start_new_thread(keep_press, (6,))
                    
    def toggle_source():

        source_name = path[redeem_reward_name]['source_name']
        time_show = path[redeem_reward_name]['time']  
        keep = path[redeem_reward_name]['keep']       

        
        send_response_value = path[redeem_reward_name]['send_response']
        
        if send_response_value:
            
            chat_response = path[redeem_reward_name]['chat_response']
            response_redus = replace_all(chat_response, aliases)
            smt.send_message(response_redus,'RESPONSE')

        obs_events.show_source(source_name, time_show, keep)
        
    def clip():
        
        info_clip = twitchAPI.create_clip(broadcaster_id = BROADCASTER_ID)

        if 'error' in info_clip.keys():

            message_clip_error_load = messages_file_load('clip_error_clip')
            smt.send_message(message_clip_error_load,'CLIP')

        else:

            clip_id = info_clip['data'][0]['id']

            message_clip_user_load = messages_file_load('clip_create_clip')

            message_clip_user = message_clip_user_load.replace('{user}',redeem_by_user)
            message_final = message_clip_user.replace('{clip_id}',clip_id)

            smt.send_message(message_final,"CLIP")

            discord_config_file = open('web/src/config/discord.json', 'r', encoding='utf-8')
            discord_config_data = json.load(discord_config_file)

            webhook_status = discord_config_data['status']
            webhook_color = discord_config_data['color']
            webhook_url = discord_config_data['url']

            if webhook_status  == 1:

                message_discord_load = messages_file_load('create_clip_discord')
                message_discord_desc_load = messages_file_load('clip_created_by')

                message_discord = message_discord_load.replace('{clip_id}',clip_id)

                webhook = DiscordWebhook(url=webhook_url)

                embed = DiscordEmbed(title=message_discord, description=message_discord_desc_load.replace('{user}',redeem_by_user), color=webhook_color)

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
                smt.send_message(response_redus,'RESPONSE')
            except Exception as e:

                error_log(e)
                smt.send_message(chat_response,'RESPONSE')

    def add_giveaway():

        give_config_file = open("web/src/giveaway/config.json", "r",encoding='utf-8')
        give_config_data = json.load(give_config_file)

        enabled_give = give_config_data['enable']

        if enabled_give == 1:
        
            with open("web/src/giveaway/names.txt", "a+") as give_file_r:
                        give_file_r.write(redeem_by_user+"\n")

            try:

                response_give_load = messages_file_load('giveaway_response_user_add')

                response_redus = replace_all(response_give_load, aliases)
                smt.send_message(response_redus,'RESPONSE')

            except Exception as e:

                error_log(e)
                smt.send_message(response_give_load,'RESPONSE')
        else:

            response_give_disabled_load = messages_file_load('response_giveaway_disabled')
            smt.send_message(response_give_disabled_load,'RESPONSE')

    eventos = {

        'sound' : play_sound, 
        'scene' : change_scene, 
        'response' : send_message, 
        'filter' : toggle_filter, 
        'keypress' : key_press, 
        'source' : toggle_source, 
        'clip': clip, 
        'tts' : play_tts, 
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
            _thread.start_new_thread(process_redem_music, (1,user_input,redeem_by_user))
            
def pubsub_start():

    global pubsub

    print('Iniciando pubsub')
    
    pubsub = PubSub(twitchAPI)
    
    pubsub.start()

    print('Pubsub Iniciado')

    pubsub.listen_channel_points(BROADCASTER_ID, callback_whisper)

def pubsub_stop():

    pubsub.stop()

def get_user_color(user_id_chatter):

    return ''

def command_fallback(message: twc.chat.Message) -> None: 

    def send_error_level(user_level, command):

        message_error_level_load = messages_file_load('error_user_level')

        message_error_level = message_error_level_load.replace('{user_level}', str(user_level))
        message_error_level_command = message_error_level.replace('{command}', str(command))

        smt.send_message(message_error_level_command,'ERROR_USER')

    user_chatter_login = message.sender

    user_info = twitchAPI.get_users(logins=[user_chatter_login])

    user_id_chatter = user_info['data'][0]['id']
    display_name_chatter = user_info['data'][0]['display_name']

    sub_info = twitchAPI.get_broadcaster_subscriptions(broadcaster_id=BROADCASTER_ID,user_ids=[user_id_chatter]) 
    mod_info = twitchAPI.get_moderators(broadcaster_id=BROADCASTER_ID,user_ids=[user_id_chatter])

    color = get_user_color(user_id_chatter)

    sub_dict = sub_info['data']
    if not sub_dict:
        sub = 'False'
    else:
        sub = 'True'

    mod_dict = mod_info['data']

    if bool(mod_dict) == True or user_id_chatter == BROADCASTER_ID:

        mod = 'True'
    else :
        mod = 'False'

    message_data = {

        'user_id' : user_id_chatter,
        'user' : message.sender,
        'display_name' : display_name_chatter,
        'chat_color' : color,
        'message' : message.text,
        'sub': sub,
        'mod': mod,
    }
        
    message_data_dump = json.dumps(message_data,ensure_ascii=False)

    eel.append_message(message_data_dump)

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

    command_string = message_data['message']
    command_lower = command_string.lower()
    command = command_lower.split()[0]
    prefix = command[0]


    result_giveaway_check = {key:val for key, val in command_data_giveaway.items() 
                                if val.startswith(command)}
    
    result_counter_check = {key:val for key, val in command_data_counter.items() 
                                if val.startswith(command)}
    
    result_command_check = {key:val for key, val in command_data.items() 
                                if key.startswith(command)}
    
    result_command_simple = {key:val for key, val in command_data_simple.items() 
                                if key.startswith(command)}
    
    result_player_check = {key:val for key, val in command_data_player.items() if val.startswith(command)}

    user = message_data['display_name'] 
    mod = message_data['mod'] 
    sub = message_data['sub'] 

    if mod == 'True' or sub == 'True':
        user_type = 'mod'
    else:
        user_type = ''
    
    user_id_command = message_data['user_id']

    status_commands = command_data_prefix['STATUS_COMMANDS']  
    status_tts = command_data_prefix['STATUS_TTS']

    command_tts = command_data_tts['command']
    user_type_tts = command_data_tts['user_level']


    def receive_tts():

        if status_tts == 1:
            
            message_delay,check_time = check_delay_file.check_delay() 
                
            if check_time:

                if user_type == user_type_tts:

                    redeem = command_data_tts['redeem']

                    if len(command_lower.split(command_tts,1)) > 1:
                        user_input = command_lower.split(command_tts,1)[1]
                        
                        data_rewards = {}
                        data_rewards['USERNAME'] = user
                        data_rewards['REDEEM'] = redeem
                        data_rewards['USER_INPUT'] = user_input
                        data_rewards['USER_LEVEL'] = user_type
                        data_rewards['USER_ID'] = user_id_command
                        data_rewards['COMMAND'] = command
                        data_rewards['PREFIX'] = prefix
                        
                        received_type = 'command'

                        _thread.start_new_thread(receive_redeem, (3,data_rewards,received_type))

                    else:

                        message_error_tts_no_txt = messages_file_load('error_tts_no_text')
                        smt.send_message(message_error_tts_no_txt,"RESPONSE")
            else:
                smt.send_message( message_delay , 'ERROR_TIME' )
        else:

            error_tts_disabled = messages_file_load('error_tts_disabled')
            smt.send_message(error_tts_disabled, "RESPONSE")

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
            
            data_rewards = {}
            data_rewards['USERNAME'] = user
            data_rewards['REDEEM'] = redeem
            data_rewards['USER_INPUT'] = command
            data_rewards['USER_LEVEL'] = user_type
            data_rewards['USER_ID'] = user_id_command
            data_rewards['COMMAND'] = command
            data_rewards['PREFIX'] = prefix

            received_type = 'command'
            
            if user_type == user_level or user_type == 'mod':
                
                message_delay_global,check_time_global = check_delay_file.check_global_delay()
                
                if check_time_global:    

                    _thread.start_new_thread(receive_redeem, (3,data_rewards,received_type))

                else:
                    smt.send_message(message_delay_global,'ERROR_TIME')
            else:

                send_error_level(str(user_level),str(command))
            
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
                    '{counter}' : str(counter)
                    }
                
                response_redus = replace_all(str(response), aliases)
                
                message_delay_global,check_time_global = check_delay_file.check_global_delay()
                
                if check_time_global:        

                    smt.send_message(response_redus,'RESPONSE')

                else:

                    smt.send_message(message_delay_global,'ERROR_TIME')

            else:   

                send_error_level(str(user_level),str(command))
                
        elif command in result_counter_check.values():
            
            eel.last_command(command)

            if 'reset_counter' in result_counter_check.keys() :
                
                if user_type == "mod":
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:        
                        
                        with open("web/src/counter/counter.txt", "w") as counter_file_w:      
                            counter_file_w.write('0')

                        
                        response_reset = messages_file_load('response_reset_counter')
                        smt.send_message(response_reset,'RESPONSE')
                        
                    else:
                        
                        smt.send_message(message_delay_global,'ERROR_TIME')
                else:
                    send_error_level('Moderador',str(command))
                    
            elif 'set_counter' in result_counter_check.keys() :
                
                if user_type == "mod":
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:    

                        if len(command_string.split()) > 1:

                            user_input = command_string.split()[1]
                            
                            if user_input.isdigit():

                                with open("web/src/counter/counter.txt", "w") as counter_file_w:      
                                    counter_file_w.write(str(user_input))
                                    
                                response_set = messages_file_load('response_set_counter')
                                response_set_repl = response_set.replace('{value}', user_input)
                                
                                smt.send_message(response_set_repl,'RESPONSE')
                            else:
                                
                                response_not_digit = messages_file_load('response_not_digit_counter')
                                smt.send_message(response_not_digit,'RESPONSE')
                        else:
                            
                            response_null_counter = messages_file_load('response_null_set_counter')
                            smt.send_message(response_null_counter,'RESPONSE')
                    else:

                        smt.send_message(message_delay_global,'ERROR_TIME')
                else:
                    send_error_level('Moderador',str(command))
                    
            elif 'check_counter' in result_counter_check.keys() :
                
                message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                if check_time_global:    

                        with open("web/src/counter/counter.txt", "r") as counter_file_r:
                            counter_file_r.seek(0)
                            digit = counter_file_r.read()    
                        
                        response_check_counter = messages_file_load('response_counter')
                        response_check_repl = response_check_counter.replace('{value}', str(digit))
                        
                        smt.send_message(response_check_repl,'RESPONSE')
                else:
                    smt.send_message(message_delay_global,'ERROR_TIME')

        elif command in result_giveaway_check.values():

            eel.last_command(command)

            if 'execute_giveaway' in result_giveaway_check.keys() :

                if user_type == "mod":
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:

                        giveaway_file = open('web/src/giveaway/config.json','r',encoding='utf-8')
                        giveaway_data = json.load(giveaway_file)

                        reset_give = giveaway_data['reset']

                        with open("web/src/giveaway/names.txt", "r") as give_file_check:
                            if len(give_file_check.read()) > 0:

                                with open("web/src/giveaway/names.txt", "r+") as give_file_r:
                                        lines = give_file_r.readlines()

                                        choice = randint(0,len(lines))
                                        name = lines[choice].replace('\n','')

                                        message_win_load = messages_file_load('giveaway_response_win')

                                        message_win = message_win_load.replace('{name}',name)
                                        smt.send_message(message_win,'RESPONSE')

                                        with open("web/src/giveaway/backup.txt", "r+") as give_file_backup:
                                            give_file_backup.writelines(lines)

                                        with open("web/src/giveaway/result.txt", "w") as give_file_w:
                                            give_file_w.write(name)
                                        
                                        if reset_give == 1:
                                            give_file_r.truncate(0)
                        
                    else:
                        smt.send_message(message_delay_global,'ERROR_TIME')
                
                else:

                    send_error_level('Moderador',str(command))

            elif 'clear_giveaway' in result_giveaway_check.keys() :

                if user_type == "mod":
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:        
                        
                        with open("web/src/giveaway/names.txt", "w") as counter_file_w:      
                            counter_file_w.truncate(0)  
                    else:
                        
                        smt.send_message(message_delay_global,'ERROR_TIME')
                else:
                    send_error_level('Moderador',str(command))

                pass

            elif 'check_name' in result_giveaway_check.keys() :

                if user_type == "mod":
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:
                        user_input = command_string.split()[1]

                        with open("web/src/giveaway/names.txt", "r+") as give_file_r:
                            lines_giveaway = give_file_r.readlines()

                            name_user = user_input + '\n'
                            
                            if name_user in lines_giveaway:
                                
                                message_check_user = messages_file_load('response_user_giveaway')

                                message_check = message_check_user.replace('{user}',user_input)
                                smt.send_message(message_check, 'RESPONSE')
                            else:

                                message_check_no_user_load = messages_file_load('response_nouser_giveaway')

                                message_check_no_user = message_check_no_user_load.replace('{user}', user_input)
                                smt.send_message(message, 'RESPONSE')
                    else:
                        
                        smt.send_message(message_delay_global,'ERROR_TIME')
                
                else:
                    send_error_level('Moderador',str(command))

            elif 'add_user' in result_giveaway_check.keys() :

                if user_type == "mod":
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:
                        user_input = command_string.split()[1]

                        with open("web/src/giveaway/names.txt", "r+") as give_file_r:
                            lines_giveaway = give_file_r.readlines()

                            with open("web/src/giveaway/names.txt", "a+") as give_file_r:
                                give_file_r.write(user_input+"\n")
                            

                            message_add_user_load = messages_file_load('giveaway_response_user_add')
                            message_add_user = message_add_user_load.replace('{user}',user_input)
                            smt.send_message(message_add_user, 'RESPONSE')
                    else:
                        
                        smt.send_message(message_delay_global,'ERROR_TIME')
                
                else:
                    send_error_level('Moderador',str(command))

            elif 'check_self_name' in result_giveaway_check.keys() :

                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:
                            
                        with open("web/src/giveaway/names.txt", "r+") as give_file_r:
                            lines_giveaway = give_file_r.readlines()

                            name_user = user + '\n'
                            
                            if name_user in lines_giveaway:


                                message_check_user_load = messages_file_load('response_user_giveaway')
                                message_check_user = message_check_user_load.replace('{user}', str(user))
                                smt.send_message(message_check_user, 'RESPONSE')

                            else:

                                message_no_user_giveaway_load = messages_file_load('response_nouser_giveaway')
                                message_no_user_giveaway = message_no_user_giveaway_load.replace('{user}', user)
                                smt.send_message(message_no_user_giveaway, 'RESPONSE')
                        
                    else:
                        
                        smt.send_message(message_delay_global,'ERROR_TIME')

        elif command in result_player_check.values():      
        
            if 'volume' in result_player_check.keys():
         
                message_delay,check_time = check_delay_file.check_global_delay()

                if user_type == "mod":

                    if check_time:

                        prefix_volume =  command_data_player['volume']

                        volume_value_command = command_lower.split(prefix_volume.lower(),1)[1]
                        volume_value_int = int(volume_value_command)
                        
                        if volume_value_int in range(0, 101):
                            
                            volume_value = volume_value_int/100
                            eel.player('volume','none',volume_value)

                            aliases_commands = {
                                '{user}' : str(user),
                                '{volume}' : str(volume_value_int)
                            }

                            message_replace_response = replace_all(messages_file_load('command_volume_confirm'),aliases_commands)
                            smt.send_message(message_replace_response,'RESPONSE')

                        else:

                            aliases_commands = {
                                '{user}' : user,
                                '{volume}' : str(volume_value_int)
                            }
                            message_replace_response = replace_all(message_data['command_volume_error'],aliases_commands)
                            smt.send_message(message_replace_response,'RESPONSE')
                            
                    else:
                        smt.send_message( message_delay , 'STATUS_ERROR_TIME' )

                else:
                    send_error_level('Moderador',str(command))
                
            elif 'skip' in result_player_check.keys():

                message_delay,check_time = check_delay_file.check_global_delay()

                if user_type == "mod":

                    if check_time:

                        eel.player('stop','none','none')

                        aliases_commands = {
                                '{user}' : str(user),
                            }
                        message_replace_response = replace_all(messages_file_load('command_skip_confirm'),aliases_commands)
                        smt.send_message(message_replace_response,'RESPONSE')


                    else:

                        smt.send_message( message_delay , 'STATUS_ERROR_TIME' )

                else:

                    send_error_level('Moderador',str(command))
                
            elif 'request' in result_player_check.keys():

                message_delay,check_time = check_delay_file.check_global_delay()
                
                if user_type == 'mod':

                    if check_time:

                        prefix_sr = command_data_player['request']
                        user_input = command_lower.split(prefix_sr.lower(),1)[1]

                        if user_input != "":

                            player_file = open('web/src/player/config/redem_data.json')
                            player_data = json.load(player_file)

                            player_reward = player_data['title']

                            data_rewards = {}

                            data_rewards['USERNAME'] = user
                            data_rewards['REDEEM'] = player_reward
                            data_rewards['USER_INPUT'] = user_input
                            data_rewards['USER_LEVEL'] = user_type
                            data_rewards['USER_ID'] = user_id_command
                            data_rewards['COMMAND'] = command
                            data_rewards['PREFIX'] = prefix

                            received_type = 'command'

                            _thread.start_new_thread(receive_redeem, (3,data_rewards,received_type))

                        else:

                            aliases_commands = {'{user}' : str(user)}
                            message_replace_response = replace_all(messages_file_load('command_sr_error_link'),aliases_commands)
                            smt.send_message(message_replace_response,'RESPONSE')

                    else:

                        smt.send_message( message_delay , 'STATUS_ERROR_TIME' )
                else:        
                    send_error_level('Moderador',str(command))

            elif 'atual' in result_player_check.keys():

                message_delay,check_time = check_delay_file.check_global_delay()

                if check_time:

                    f = open('web/src/player/list_files/currentsong.txt', 'r+', encoding="utf-8")
                    current_song = f.read()

                    aliases_commands = {'{user}' : str(user),'{music}':str(current_song)}
                    message_replace_response = replace_all(messages_file_load('command_current_confirm'),aliases_commands)
                    smt.send_message(message_replace_response, 'RESPONSE')

                else:
                    smt.send_message( message_delay , 'STATUS_ERROR_TIME' )

            elif 'next' in result_player_check.keys():

                message_delay,check_time = check_delay_file.check_global_delay()

                if check_time:

                    playlist_file = open('web/src/player/list_files/playlist.json', "r", encoding="utf-8")
                    playlist_data = json.load(playlist_file)

                    queue_file = open('web/src/player/list_files/queue.json', "r", encoding="utf-8")
                    queue_data = json.load(queue_file)
                    
                    check_playlist = any(playlist_data.keys())
                    check_queue = any(queue_data.keys())

                    if check_queue == True:

                        queue_keys = [int(x) for x in queue_data.keys()]
                        min_key_queue = min(queue_keys)
                        min_key_queue_str = str(min_key_queue)

                        next_song = queue_data[min_key_queue_str]['MUSIC_NAME'] 
                        resquest_by = queue_data[min_key_queue_str]['USER']

                        aliases_commands = {
                            '{user}' : str(user),
                            '{music}': str(next_song),
                            '{request_by}': str(resquest_by)
                            }

                        response_replace = replace_all(messages_file_load('command_next_confirm'),aliases_commands)
                        smt.send_message(response_replace,'RESPONSE')
                        
                    elif check_playlist == True:

                        playlist_keys = [int(x) for x in playlist_data.keys()]
                        min_key_playlist = min(playlist_keys)
                        min_key_playlist_str = str(min_key_playlist)

                        next_song = playlist_data[min_key_playlist_str]['MUSIC_NAME']
                        resquest_by = playlist_data[min_key_playlist_str]['USER'] 

                        aliases_commands = {
                            '{user}' : str(user),
                            '{music}': str(next_song),
                            '{request_by}': str(resquest_by)
                        }

                        response_replace = replace_all(message_data['command_next_confirm'],aliases_commands)
                        smt.send_message(response_replace,'RESPONSE')
                        
                    else:

                        aliases_commands = {
                            '{user}' : str(user),
                            }

                        response_replace = replace_all(messages_file_load('command_next_no_music'),aliases_commands)
                        smt.send_message(response_replace,'RESPONSE')

                else:
                    smt.send_message( message_delay , 'STATUS_ERROR_TIME' )                    
            
    else:
        
        message_command_disabled = messages_file_load('commands_disabled')
        smt.send_message(message_command_disabled,"RESPONSE")

def bot(tid):

    try:
        print('Iniciando modulo comandos')

        time.sleep(2)

        smt.conect_chat()

        time.sleep(2)

        chat = twc.Chat(channel=USERNAME, nickname=BOTNAME, oauth='oauth:' + TOKENBOT)

        time.sleep(2)

        status_bot_load = messages_file_load('command_module_status')
        smt.send_message(status_bot_load,"STATUS_BOT")

        chat.subscribe(command_fallback)

    except Exception as e:

        error_log(e)

def eel_start(eel_mode):

    eel.init('web','--disk-cache-dir=/dev/null')

    if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:

        if eel_mode == "normal":

            eel.start("index.html",size=(1200, 680), port=8000, mode=None, shutdown_delay=0.0)

        elif eel_mode == "auth":
            
            eel.start("auth.html",size=(1200, 680), port=8000, mode=None, shutdown_delay=0.0)

    else:
        raise
    
def webview_start_app(app_mode):

    global window

    if app_mode == "normal":
        
        window = webview.create_window("RewardEvents 3.0", "http://localhost:8000/index.html", width=1200, height=680, min_size=(1200, 680),frameless=True,easy_drag=True)
        
        window.events.closed += pubsub.stop

        webview.start(debug=False)

    elif app_mode == "auth":

        window = webview.create_window("RewardEvents auth", "http://localhost:8000/auth.html", width=1200, height=680, min_size=(1200, 680),frameless=True,easy_drag=True)
        
        webview.start()

def start_app(start_mode):

    if start_mode == "normal":

        pubsub_start()

        pygame.init()
        pygame.mixer.init()

        eel_thread = threading.Thread(target=eel_start,args=('normal',),daemon=True)
        eel_thread.start()

        _thread.start_new_thread(bot, (1,))

        _thread.start_new_thread(timer_module.timer, (2,))
        _thread.start_new_thread(obs_test_conn, (3,))
        _thread.start_new_thread(loopcheck, (4,))

        webview_start_app('normal')
    
    elif start_mode == "auth":

        eel_thread = threading.Thread(target=eel_start,args=('auth',),daemon=True)
        eel_thread.start()
        
        webview_start_app('auth')

def update_auth_tkn(access_token,refresh_token):

    if USERNAME == BOTNAME:

        data_bot = {}
        data_bot['USERNAME'] = USERNAME
        data_bot['BROADCASTER_ID'] = BROADCASTER_ID
        data_bot['CODE'] = CODE
        data_bot['TOKEN'] = access_token
        data_bot['REFRESH_TOKEN'] = refresh_token
        data_bot['TOKENBOT'] = access_token
        data_bot['BOTUSERNAME'] = BOTNAME
        
        auth_file_bot = open("web/src/auth/auth.json", "w") 
        json.dump(data_bot, auth_file_bot, indent = 6,ensure_ascii=False)  
        auth_file_bot.close()

    else:

        data_bot = {}
        data_bot['USERNAME'] = USERNAME
        data_bot['BROADCASTER_ID'] = BROADCASTER_ID
        data_bot['CODE'] = CODE
        data_bot['TOKEN'] = access_token
        data_bot['REFRESH_TOKEN'] = refresh_token
        data_bot['TOKENBOT'] = TOKENBOT
        data_bot['BOTUSERNAME'] = BOTNAME
        
        auth_file_bot = open("web/src/auth/auth.json", "w") 
        json.dump(data_bot, auth_file_bot, indent = 6,ensure_ascii=False)  
        auth_file_bot.close()

def auto_refresh_token(token,refresh_token):
    
    if USERNAME == BOTNAME:

        data_bot = {}
        data_bot['USERNAME'] = USERNAME
        data_bot['BROADCASTER_ID'] = BROADCASTER_ID
        data_bot['CODE'] = CODE
        data_bot['TOKEN'] = token
        data_bot['REFRESH_TOKEN'] = refresh_token
        data_bot['TOKENBOT'] = token
        data_bot['BOTUSERNAME'] = BOTNAME
        
        auth_file_bot = open("web/src/auth/auth.json", "w") 
        json.dump(data_bot, auth_file_bot, indent = 6,ensure_ascii=False)  
        auth_file_bot.close()

    else:

        data_bot = {}
        data_bot['USERNAME'] = USERNAME
        data_bot['BROADCASTER_ID'] = BROADCASTER_ID
        data_bot['CODE'] = CODE
        data_bot['TOKEN'] = token
        data_bot['REFRESH_TOKEN'] = refresh_token
        data_bot['TOKENBOT'] = TOKENBOT
        data_bot['BOTUSERNAME'] = BOTNAME
        
        auth_file_bot = open("web/src/auth/auth.json", "w") 
        json.dump(data_bot, auth_file_bot, indent = 6,ensure_ascii=False)  
        auth_file_bot.close()

if CODE and TOKENBOT :

    twitchAPI = Twitch(clientid,clientsecret)
    twitchAPI.user_auth_refresh_callback = auto_refresh_token

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
        
        twitchAPI.set_user_authentication(TOKEN, scopes, REFRESH_TOKEN)

        start_app('normal')

    except Exception as e:

        try:

            token_new, refresh_token_new = refresh_access_token(REFRESH_TOKEN, clientid, clientsecret)
            update_auth_tkn(token_new, refresh_token_new)

            twitchAPI.set_user_authentication(token_new, scopes , refresh_token_new)

            start_app('normal')
        
        except Exception as e:

            error_log(e)

            start_app('auth')

else:

    start_app('auth')