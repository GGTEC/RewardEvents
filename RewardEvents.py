import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import logging
import difflib
import subprocess
import utils
import webview
import threading
import validators
import webbrowser
import websocket
import obs_events
import time
import json
import requests as req
import tkinter
import textwrap
import keyboard
import random
import yt_dlp
import datetime
import pytz
import re
import tkinter.messagebox as messagebox
import sk
import pygame

from lockfile import LockManager
from collections import namedtuple
from auth import auth_data
from ChatIRC import TwitchBot
from io import BytesIO
from gtts import gTTS
from tkinter import messagebox
from tkinter import filedialog as fd
from requests.structures import CaseInsensitiveDict
from random import randint
from discord_webhook import DiscordWebhook, DiscordEmbed
from twitchAPI.twitch import Twitch, AuthScope, PredictionStatus, PollStatus

global caching, loaded_status, window, window_auth, window_chat_open, window_chat, window_events, window_events_open, twitch_api, streaming

caching = False
loaded_status = False
window_chat_open = False
window_events_open = False
window_auth_open = False
streaming = False

lock_manager = LockManager('RewardEvents')
lock_manager.lock()

def toast(message):

    window.evaluate_js(f"toast_notifc('{message}')")


def save_access_token(token: str) -> None:

    """Saves a token for a given type_id to a JSON file.

    Args:
        type_id: The type of token, either 'streamer', 'bot', or 'streamer_asbot'.
        token: The token to be saved.

    Raises:
        ValueError: If type_id is not one of the valid options.
    """
    
    try:
        CLIENT_ID = os.getenv('CLIENTID')
        
        SCOPES = [
            AuthScope.CHANNEL_MANAGE_PREDICTIONS,
            AuthScope.CHANNEL_MANAGE_POLLS,
            AuthScope.USER_READ_SUBSCRIPTIONS,
            AuthScope.USER_READ_EMAIL,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
            AuthScope.MODERATION_READ,
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.CLIPS_EDIT,
            AuthScope.CHAT_EDIT,
            AuthScope.CHAT_READ
        ]

        data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "load")
        
        twitch_api = Twitch(CLIENT_ID, authenticate_app=False)
        twitch_api.auto_refresh_auth = False

        scope_auth = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/scopes.json", "load")
        
        type_id = scope_auth['auth_type']

        if type_id == "streamer":

            username = data["USERNAME"]

            twitch_api.set_user_authentication(token, SCOPES)

            window.evaluate_js(f"toggle_auth('submit-user-token')")

        elif type_id == "bot":
        
            username = data["BOTUSERNAME"]

            twitch_api.set_user_authentication(token, SCOPES)

            window.evaluate_js(f"toggle_auth('submit-bot-token')")

        elif type_id == "streamer_asbot":
        
            username = data["USERNAME"]

            twitch_api.set_user_authentication(token, SCOPES)

            window.evaluate_js(f"toggle_auth('submit-user-bot-token')")

        else:

            raise ValueError(f"Invalid type_id: {type_id}")

        user_id_resp = twitch_api.get_users(logins=[username])["data"][0]["id"]

        if type_id == "streamer":

            data["TOKEN"] = token
            data["BROADCASTER_ID"] = user_id_resp

        elif type_id == "bot":
            data["TOKENBOT"] = token
            data["BOT_ID"] = user_id_resp

        elif type_id == "streamer_asbot":
            data["TOKEN"] = token
            data["BROADCASTER_ID"] = user_id_resp 
            data["BOT_ID"] = user_id_resp 
            data["TOKENBOT"] = token

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "save",data)

        WEBHOOKURL = os.getenv('WEBHOOKURL')
        webhook_login = DiscordWebhook(url=WEBHOOKURL)

        embed_login = DiscordEmbed(
            title='Nova autenticação',
            description= F'https://www.twitch.tv/{username}' ,
            color= '03b2f8'
        )

        embed_login.set_author(name=username, url=f'https://www.twitch.tv/{username}')
        
        webhook_login.add_embed(embed_login)
        webhook_login.execute() 

    except Exception as e:
        utils.error_log(e)


def start_auth_window(username,type_id):

    global window_auth

    def set_window_auth_open():
        global window_auth_open
        window_auth_open = True

    def set_window_auth_close():
        global window_auth_open
        window_auth_open = False


    """Exposes a python function to javascript and opens an OAuth URI in a web browser.

    Args:
        username (str): The username of the user or the bot.
        type_id (str): The type of the user: 'streamer', 'bot' or 'streamer_asbot'.

    Raises:
        FileNotFoundError: If the json files for authentication or authorization are not found.
        ValueError: If the type_id is not one of the valid options.
    """

    try:

        data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "load")

        type_id = sys.intern(type_id)
        
        if type_id == 'streamer':
            data['USERNAME'] = username

        elif type_id == 'bot':
            data['BOTUSERNAME'] = username

        elif type_id == 'streamer_asbot':
            data['USERNAME'] = username
            data['BOTUSERNAME'] = username


        utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "save", data)
        
        scope_auth = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/scopes.json", "load")
        
        redirect_uri = scope_auth['redirect']
        url = scope_auth['url']
        response_type = scope_auth['response_type']
        force_verify = scope_auth['force_verify']

        scope_list = scope_auth['scopes']

        scope = '+'.join(scope for scope in scope_list)

        scope_auth['auth_type'] = type_id
                 
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/scopes.json", "save",scope_auth)

        oauth_uri = f"{url}oauth2/authorize?response_type={response_type}&force_verify={force_verify}&client_id={os.getenv('CLIENTID')}&redirect_uri={redirect_uri}&scope={scope}"
        
        window_auth = webview.create_window('RewardEvents Auth Twitch', oauth_uri)

        window_auth.events.loaded += set_window_auth_open
        window_auth.events.closed += set_window_auth_close

        window_auth.expose(save_access_token)
        

    except Exception as e:
        utils.error_log(e)


def start_twitch():

    global twitch_api

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if authdata.TOKEN() and authdata.TOKENBOT():

        twitch_api = Twitch(os.getenv('CLIENTID'),authenticate_app=False)
        twitch_api.auto_refresh_auth = False

        scopes = [
            AuthScope.CHANNEL_MANAGE_PREDICTIONS,
            AuthScope.CHANNEL_MANAGE_POLLS,
            AuthScope.USER_READ_SUBSCRIPTIONS,
            AuthScope.USER_READ_EMAIL,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
            AuthScope.MODERATION_READ,
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.CHANNEL_MANAGE_BROADCAST,
            AuthScope.CLIPS_EDIT,
            AuthScope.CHAT_EDIT,
            AuthScope.CHAT_READ
        ]

        try:

            twitch_api.set_user_authentication(authdata.TOKEN(),scopes)
            
            return True

        except Exception as e:
            
            if isinstance(e, ConnectionError):
                
                ask = messagebox.showerror("Erro", "Erro de conexão, verifique a conexão com a internet e tente novamente.")
                if ask == 'ok':
                    sys.exit(0)
                    
            else:
                
                utils.error_log(e)
                return False
                
    else:
        
        return False
   
   
def send_announcement(message,color):
    
    """Exposes a python function to javascript and sends an announcement message to a Twitch chat.

    Args:
        message (str): The announcement message to be sent.
        color (str): The color of the announcement message.

    Returns:
        bool: True if the request was successful, False otherwise.

    Raises:
        requests.exceptions.RequestException: If the request failed for any reason.
    """
    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():
        
        url = f"https://api.twitch.tv/helix/chat/announcements?broadcaster_id={authdata.BROADCASTER_ID()}&moderator_id={authdata.BOT_ID()}"
        
        headers = {
            "Authorization": f"Bearer {authdata.TOKENBOT()}",
            "Client-Id": os.getenv('CLIENTID'),
            "Content-Type": "application/json"
        }

        data = json.dumps({"message": message, "color": color})

        response = req.post(url, headers=headers, data=data.encode('utf-8'))

        return response.ok


def send(message):
    
    """Exposes a python function to javascript and sends a message to a Twitch chat.

    Args:
        message (str): The message to be sent.

    Returns:
        dict: A dictionary containing the response data and the chat configuration.

    Raises:
        FileNotFoundError: If the chat_config.json file is not found.
        twitchio.errors.HTTPException: If the chat.send() method failed for any reason.
    """
    
    global chat
    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    def add_user_database(data): 
        
        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
        
        if data not in user_data_load:

            user_data_load[data] = {
                'display_name' : data,
                "roles" : ['mod'],
                'sub_count': '',
                'chat_freq' : '',
                'color': '',
                'badges': '',
                'last_join' : '',
                'time_w': 0
            }
            
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save",user_data_load)
        

    if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():

        if message.startswith('/announce'):

            color = message.split('/')[1].replace('announce', '') or 'primary'

            announcement = message.split(color)[1]

            send_announcement(announcement, color)

            
        else:
            
            add_user_database(authdata.BOTUSERNAME())

            chat.send(message)
            
            chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "load")
            chat_time = utils.time_date()

            data_res = {
                'type': 'PRIVMSG',
                "response": 0,
                "color": '#4f016c',
                "display_name": authdata.BOTUSERNAME(),
                "badges" : f'<img class="badges" src="https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1" />', 
                "emotes": "",    
                "user_name": authdata.BOTUSERNAME(),
                "user_replied" : '',
                "roles" : ['mod'],
                "user_id": authdata.BOT_ID(),
                "frist_message" : 0,
                "message": message,
                "message_replied" : '',
                "message_no_url": message,
                "appply_colors" : chat_data["appply-colors"],
                "appply_no_colors" : chat_data["appply-no-colors"],
                "data_show" : chat_data["data-show"],
                'chat_time' : f'{chat_time}',
                "type_data" : chat_data["type-data"],
                "color_apply" : chat_data["color-apply"],
                "block_color" : chat_data["block-color"],
                "font_size" : chat_data["font-size"],
                "show_badges" : chat_data["show-badges"],
                "wrapp_message" : chat_data["wrapp-message"],
             }
             

            window.evaluate_js(f"append_message({json.dumps(data_res, ensure_ascii=False)})")

            if window_chat_open:
                window_chat.evaluate_js(f"append_message_out({json.dumps(data_res, ensure_ascii=False)})")

            commands_module(data_res)

        
def append_notice(data_receive):

    type_id = data_receive['type']
    message = data_receive['message']
    user_input = data_receive['user_input']

    event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "load")
    chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "load")
    
    now = datetime.datetime.now()

    data = {
        "message" : message,
        "user_input" : user_input,
        "font_size" : event_log_data['font_size'],
        'font_size_chat' : chat_data['font-size'],
        "color" : event_log_data['color_events'],
        "data_time" : now.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "data_show" : event_log_data["data_show"],
        "type_event" : type_id,
        "show_commands" : event_log_data["show_commands"],
        "show_redeem" : event_log_data["show_redeem"],
        "show_events" : event_log_data["show_events"], 
        "show_join" : event_log_data["show_join"], 
        "show_leave" : event_log_data["show_leave"], 
        "show_commands_chat" : event_log_data["show_commands_chat"],
        "show_redeem_chat" : event_log_data["show_redeem_chat"],
        "show_events_chat" : event_log_data["show_events_chat"], 
        "show_join_chat" : event_log_data["show_join_chat"], 
        "show_leave_chat" : event_log_data["show_leave_chat"], 
    }

    
    event_log_data['event_list'].append(f"{now} | {type_id} | {message} | {user_input}")

    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "save",event_log_data)

    if type_id == 'command':

        if event_log_data['show_commands']:

            event_dump = json.dumps(data, ensure_ascii=False)

            window.evaluate_js(f"append_notice({event_dump})")

            if window_events_open:
                window_events.evaluate_js(f"append_notice({event_dump})")

            if window_chat_open:
                window_chat.evaluate_js(f"append_notice_chat_w({event_dump})")
                
    elif type_id == 'event':

        if event_log_data['show_events']:

            event_dump = json.dumps(data, ensure_ascii=False)
            
            window.evaluate_js(f"append_notice({event_dump})")

            if window_events_open:
                window_events.evaluate_js(f"append_notice({event_dump})")

            if window_chat_open:
                window_chat.evaluate_js(f"append_notice_chat_w({event_dump})")

    elif type_id == 'redeem' :
        if event_log_data['show_redeem']:

            event_dump = json.dumps(data, ensure_ascii=False)
            window.evaluate_js(f"append_notice({event_dump})")

            if window_events_open:
                window_events.evaluate_js(f"append_notice_w({event_dump})")

            if window_chat_open:
                window_chat.evaluate_js(f"append_notice_chat_w({event_dump})")
    
    elif type_id == 'join' :

        if event_log_data['show_join']:

            event_dump = json.dumps(data, ensure_ascii=False)

            window.evaluate_js(f"append_notice({event_dump})")
            if window_events_open:
                window_events.evaluate_js(f"append_notice_w({event_dump})")

            if window_chat_open:
                window_chat.evaluate_js(f"append_notice_chat_w({event_dump})")
    
    elif type_id == 'leave' :

        if event_log_data['show_leave']:

            event_dump = json.dumps(data, ensure_ascii=False)

            window.evaluate_js(f"append_notice({event_dump})")

            if window_events_open:
                window_events.evaluate_js(f"append_notice_w({event_dump})")

            if window_chat_open:
                window_chat.evaluate_js(f"append_notice_chat_w({event_dump})")


def send_discord_webhook(data):
    
    """Send a discord webhook by a type message.

    Args:
        data (dict): A dictionary containing the type_id and other relevant data for the webhook.

    Raises:
        FileNotFoundError: If the discord.json file is not found.
        discord_webhook.DiscordWebhookException: If the webhook execution failed for any reason.
    """

    try:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        
        if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():

            type_id = data['type_id']

            discord_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "load")

            webhook_status = discord_config_data[type_id]['status']
            webhook_color = discord_config_data[type_id]['color']
            webhook_content = discord_config_data[type_id]['content']
            webhook_url = discord_config_data[type_id]['url']
            webhook_title = discord_config_data[type_id]['title']
            webhook_description = discord_config_data[type_id]['description']

            webhook_profile_status = discord_config_data['profile_status']
            webhook_profile_image = discord_config_data['profile_image']
            webhook_profile_name = discord_config_data['profile_name']

            if webhook_status and not webhook_url == "":

                webhook = DiscordWebhook(url=webhook_url)
                webhook.content = webhook_content 

                embed = ''

                if type_id == 'clips_create':  
                    
                    clip_id = data['clip_id']
                    username = data['username']
                    
                    aliases = {
                        '{url}' : f'https://clips.twitch.tv/{clip_id}',
                        '{username}' : username
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )


                elif type_id == 'clips_edit':  

                    clip_id = data['clip_id']
                    username = data['username']
                    
                    aliases = {
                        '{url}' : f'https://clips.twitch.tv/{clip_id}/edit',
                        '{username}' : username
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )


                elif type_id == 'follow':  

                    username = data['follow_name']
                    
                    aliases = {
                        '{username}' : username
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )


                elif type_id == 'sub':  

                    username = data['username']
                    
                    aliases = {
                        '{username}' : username
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    

                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                
                elif type_id == 'resub':  

                    username = data['username']
                    
                    aliases = {
                        '{username}' : username,
                        '{tier}' : data['tier'],
                        '{total_months}' : data['total_months'],
                        '{streak_months}' : data['streak_months'],
                        '{months}' : data['months'],
                        '{user_mesage}' : data['user_mesage']
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)

                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )


                elif type_id == 'bits':  


                    aliases = {
                        '{username}' : data['username'],
                        '{amount}' : data['amount']
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'live_start':
                
                    
                    response = twitch_api.get_streams(first=1,user_id=authdata.BROADCASTER_ID())
                    
                    if not response['data']:

                        aliases = {
                            "{broadcaster}" : data['username'],
                            '{url}' : f'https://twitch.tv/{authdata.USERNAME()}'
                        }

                        message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                        aliases = {
                            '{url}' : f'https://twitch.tv/{authdata.USERNAME()}'
                        }

                        webhook_description = utils.replace_all(webhook_description, aliases)

                        embed = DiscordEmbed(
                            title=webhook_title,
                            description=webhook_description,
                            color=webhook_color
                        )

                        embed.add_embed_field(name='Titulo', value=message_event,inline=False)

                    else:

                        title = response['data'][0]['title']
                        game = response['data'][0]['game_name']
                        viewer_count = response['data'][0]['viewer_count']
                        is_mature = response['data'][0]['viewer_count']
                        thumb_url = response['data'][0]['thumbnail_url']
                        
                        aliases = {
                            '{url}' : f'https://twitch.tv/{authdata.USERNAME()}'
                        }

                        webhook_description = utils.replace_all(webhook_description, aliases)

                        embed = DiscordEmbed(
                            title=webhook_title,
                            description=webhook_description,
                            color=webhook_color
                        )
                        
                        embed.set_image(url=thumb_url)
                        embed.add_embed_field(name='Titulo', value=title,inline=False)
                        embed.add_embed_field(name='Jogo', value=game,inline=False)
                        embed.add_embed_field(name='Espectadores', value=viewer_count,inline=True)
                        embed.add_embed_field(name='+18?', value=is_mature,inline=True)

                        
                elif type_id == 'live_cat':  
                    
                    title = data['title']
                    tag = data['tag']  
                            
                    aliases = {
                        '{title}' : str(title),
                        '{tag}' : str(tag),
                        '{url}' : f'https://twitch.tv/{authdata.USERNAME()}'
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                    
                    embed.add_embed_field(name='Titulo', value=title,inline=False)
                    embed.add_embed_field(name='Jogo', value=tag,inline=False)

        
                elif type_id == 'live_end':  

                    username = data['username']
                            
                    aliases = {
                        '{username}' : username,
                    }
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    

                elif type_id == 'poll_start':  

                    title = data['title']
                    choices = data['choices']
                    bits_voting = data['bits_status']
                    bits_amount = data['bits_amount']
                    points_status = data['points_status']
                    points_amount = data['points_amount']
                            
                    aliases = {
                        '{title}' : title,
                        '{bits_voting}' : str(bits_voting),
                        '{bits_amount}' : str(bits_amount),
                        '{points_status}' : str(points_status),
                        '{points_amount}' : str(points_amount),
                        '{url}' : f'https://twitch.tv/{authdata.USERNAME()}'
                    }
                    
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                    if points_status:
                        points_status = 'Sim'
                    else:
                        points_status = 'Não'
                        
                    
                    if bits_voting:
                        bits_voting = 'Sim'
                    else:
                        bits_voting = 'Não'
                        
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed.add_embed_field(name=f'Votação com pontos do canal ?', value=points_status,inline=False)
                    embed.add_embed_field(name=f'Votação com bits ?', value=bits_voting,inline=False)
                    

                    
                    op_count = 0
                    
                    for option in choices:
                        title_op = option['title']
                        op_count += 1
                        embed.add_embed_field(name=f'Opção {op_count}', value=title_op,inline=False)


                elif type_id == 'poll_status':
                
                    title = data['title']
                    choices = data['choices']
                    bits_voting = data['bits_status']
                    bits_amount = data['bits_amount']
                    points_status = data['points_status']
                    points_amount = data['points_amount']
                            
                    aliases = {
                        '{title}' : title,
                        '{bits_voting}' : str(bits_voting),
                        '{bits_amount}' : str(bits_amount),
                        '{points_status}' : str(points_status),
                        '{points_amount}' : str(points_amount),
                        '{url}' : f'https://twitch.tv/{authdata.USERNAME()}'
                    }
                    
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                    if points_status:
                        points_status = 'Sim'
                    else:
                        points_status = 'Não'
                        
                    
                    if bits_voting:
                        bits_voting = 'Sim'
                    else:
                        bits_voting = 'Não'
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed.add_embed_field(name=f'Votação com pontos do canal ?', value=f"Status : {points_status} | Pontos para votar: {points_amount}",inline=False)
                    embed.add_embed_field(name=f'Votação com bits ?', value=f"Status : {bits_voting} | Bits para votar: {bits_amount}",inline=False)
                    

                    
                    op_count = 0
                    
                    for option in choices:

                        title_op = option['title']
                        votes_op = option['votes']
                        points_votes_op = option['channel_points_votes']
                        bits_votes_op = option['bits_votes']
                        
                        op_count += 1
                        embed.add_embed_field(name=f'{title_op}', value=f"Votos : {votes_op} | Votos com pontos do canal : {points_votes_op} | Votos com bits : {bits_votes_op}",inline=False)
                        
                        webhook.add_embed(embed)
                        webhook.execute()   


                elif type_id == 'poll_end':  

                    title = data['title']
                    choices = data['choices']
                    bits_voting = data['bits_status']
                    bits_amount = data['bits_amount']
                    points_status = data['points_status']
                    points_amount = data['points_amount']
                            
                    aliases = {
                        '{title}' : title,
                        '{bits_voting}' : str(bits_voting),
                        '{bits_amount}' : str(bits_amount),
                        '{points_status}' : str(points_status),
                        '{points_amount}' : str(points_amount),
                        '{url}' : f'https://twitch.tv/{authdata.USERNAME()}'
                    }
                    
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                    if points_status:
                        points_status = 'Sim'
                    else:
                        points_status = 'Não'
                        
                    
                    if bits_voting:
                        bits_voting = 'Sim'
                    else:
                        bits_voting = 'Não'
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed.add_embed_field(name=f'Votação com pontos do canal ?', value=f"Status : {points_status} | Pontos para votar: {points_amount}",inline=False)
                    embed.add_embed_field(name=f'Votação com bits ?', value=f"Status : {bits_voting} | Bits para votar: {bits_amount}",inline=False)
                    

                    
                    op_count = 0
                    
                    for option in choices:
                        title_op = option['title']
                        votes_op = option['votes']
                        points_votes_op = option['channel_points_votes']
                        bits_votes_op = option['bits_votes']
                        op_count += 1
                        embed.add_embed_field(name=f'{title_op}', value=f"Votos : {votes_op} | Votos com pontos do canal : {points_votes_op} | Votos com bits : {bits_votes_op}",inline=False)
                    

                elif type_id == 'prediction_start':  

                    title = data['title']
                    options = data['outcomes']
                            
                    aliases = {
                        '{title}' : title,
                    }
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )

                    op_count = 0
                    for option in options:
                        title_op = option['title']
                        op_count += 1
                        embed.add_embed_field(name=f'Opção {op_count}', value=title_op,inline=False)

                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    

                elif type_id == 'prediction_progress':  

                    title = data['title']
                    options = data['outcomes']
                            
                    aliases = {
                        '{title}' : title,
                    }
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )

                    op_count = 0

                    for option in options:
                        title_op = option['title']
                        users = option['users']
                        points = option['channel_points']
                        op_count += 1
                        embed.add_embed_field(name=f'Opção {op_count}', value=f"{title_op} | Votos: {users} | Pontos do canal: {points}",inline=False)
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    

                elif type_id == 'prediction_end':  

                    title = data['title']
                    outcome_win = data['outcome_win']
                    channel_points = data['channel_points']
            
                    aliases = {
                        '{title}' : title,
                        '{outcome_win}' : str(outcome_win),
                        '{channel_points}' : str(channel_points)
                    }
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed.add_embed_field(name=f'Vencedor', value=f"{outcome_win} | Pontos do canal: {channel_points}",inline=False)


                elif type_id == 'giftsub':  
            
                    aliases = {
                        '{tier}' : str(data['tier']),
                        '{total}' : str(data['total']),
                        '{cumulative_total}' :str(data['user_name']),
                        '{is_anonymous}' : str(data['user_name']),
                        '{username}' : str(data['user_name'])
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'subend':  
            
                    aliases = {
                        '{username}' : str(data['user_name'])
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
            

                elif type_id == 'raid':  
            
                    aliases = {
                        '{username}' : str(data['username']),
                        '{specs}' : str(data['specs'])
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'ban':  
            
                    aliases = {
                        '{reason}' : data['reason'],
                        '{moderator}' : data['moderator'],
                        '{username}' : data['username'],
                        '{time}' : data['time']
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'unban':  
            
                    aliases = {
                        '{moderator}' : data['moderator'],
                        '{username}' : data['username'],
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'goal_start':  
            
                    aliases = {
                        '{target}' : str(data['target']),
                        '{current}' : str(data['current']),
                        '{description}' : str(data['description']),
                        '{type}' : data['goal_type']
                    }

                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'goal_progress':  
            
                    aliases = {
                        '{target}' : str(data['target']),
                        '{current}' : str(data['current']),
                        '{description}' : str(data['description']),
                        '{type}' : data['goal_type']
                    }

                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'goal_end':  
            
                    aliases = {
                        '{target}' : str(data['target']),
                        '{current}' : str(data['current']),
                        '{description}' : str(data['description']),
                        '{type}' : data['goal_type']
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    

                elif type_id == 'shoutout_start':  
            
                    aliases = {
                        '{broadcaster}' : str(data['broadcaster']),
                        '{moderator}' : str(data['moderator']),
                        '{to_broadcaster}': str(data['to_broadcaster']),
                        '{viewer_count}': str(data['viewer_count'])
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                
                elif type_id == 'shoutout_receive':  
            
                    aliases = {
                        '{broadcaster}' : str(data['broadcaster']),
                        '{from_broadcaster}' : str(data['from_broadcaster'])
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
    
                elif type_id == 'shield_start':
            
            
                    aliases = {
                        '{broadcaster}' : str(data['broadcaster']),
                        '{moderator}' : str(data['moderator'])
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )

        
                elif type_id == 'shield_end':
            
            
                    aliases = {
                        '{broadcaster}' : str(data['broadcaster']),
                        '{moderator}' : str(data['moderator'])
                    }
                    
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )

                
                elif type_id == 'charity_campaign_donate':
            
            
                    aliases = {
                        '{username}': data['username'],
                        '{charity_name}': data['charity_name'],
                        '{charity_logo}': data['charity_logo'],
                        '{value}': str(data['value']),
                        '{decimal_places}': str(data['decimal_places']),
                        '{currency}': data['currency']
                    }
                                
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )

                    embed.add_embed_field(name=f'Valor', value=f"{data['currency']} {str(data['value'])}",inline=True)

                    embed.set_thumbnail(url=data['charity_logo'])


                if webhook_profile_status and webhook_profile_image.endswith('.png'):

                    embed.set_author(name=webhook_profile_name, url=f'https://www.twitch.tv/{authdata.USERNAME()}', icon_url=webhook_profile_image)
            
                if embed != '':
                    webhook.add_embed(embed)
                    webhook.execute() 
                
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)


def get_auth_py(type_id):
    
    """Exposes a python function to javascript and returns an authentication value based on the type_id.

    Args:
        type_id (str): The type of authentication value to be returned. Valid values are: 'USERNAME', 'TOKEN', 'BROADCASTER_ID', 'CLIENTID', 'TOKENBOT', 'BOTNAME'.

    Returns:
        str: The authentication value corresponding to the type_id.

    Raises:
        ValueError: If the type_id is not valid.
    """
    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():
        
        auth_values = {
            'USERNAME': authdata.USERNAME(),
            'TOKEN': authdata.TOKEN(),
            'BROADCASTER_ID': authdata.BROADCASTER_ID(),
            'CLIENTID': os.getenv('CLIENTID'),
            'TOKENBOT': authdata.TOKEN(),
            'BOTNAME': authdata.BOTUSERNAME()
        }
        
        if type_id in auth_values:
            return auth_values[type_id]
        else:
            raise ValueError(f"Invalid type_id: {type_id}")


def logout_auth():
    
    data = {
        'USERNAME': '',
        'BOTUSERNAME': '',
        'BROADCASTER_ID': '',
        'BOT_ID' : '',
        'TOKEN': '',
        'TOKENBOT':'',
    }

    utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "save", data)
    
    close()


def event_log(type_id,data_save):

    if type_id == "get" :

        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "load")
        
        data = {
            "messages" : event_log_data['event_list'],
            "font_size" : event_log_data['font_size'],
            "color" : event_log_data['color_events'],
            "data_show" : event_log_data["data_show"],
            "show_commands" : event_log_data["show_commands"],
            "show_redeem" : event_log_data["show_redeem"],
            "show_events" : event_log_data["show_events"], 
            "show_join" : event_log_data["show_join"], 
            "show_leave" : event_log_data["show_leave"], 
            "show_commands_chat" : event_log_data["show_commands_chat"],
            "show_redeem_chat" : event_log_data["show_redeem_chat"],
            "show_events_chat" : event_log_data["show_events_chat"], 
            "show_join_chat" : event_log_data["show_join_chat"], 
            "show_leave_chat" : event_log_data["show_leave_chat"], 
        }

        data_dump = json.dumps(data, ensure_ascii=False)

        return data_dump
    
    elif type_id == "get_config" :

        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "load")
        
        data = {
            "font_size" : event_log_data['font_size'],
            "color_events" : event_log_data['color_events'],
            "show_time_events" : event_log_data["data_show"],
            "show_commands" : event_log_data["show_commands"],
            "show_redeem" : event_log_data["show_redeem"],
            "show_events" : event_log_data["show_events"], 
            "show_join" : event_log_data["show_join"], 
            "show_leave" : event_log_data["show_leave"],
            "show_commands_chat" : event_log_data["show_commands_chat"],
            "show_redeem_chat" : event_log_data["show_redeem_chat"],
            "show_events_chat" : event_log_data["show_events_chat"], 
            "show_join_chat" : event_log_data["show_join_chat"], 
            "show_leave_chat" : event_log_data["show_leave_chat"],  
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save" :
        
        try:

            event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "load")
            
            data_save = json.loads(data_save)

            event_log_data['font_size'] = data_save['font_size']
            event_log_data['color_events'] = data_save['color_events']
            event_log_data['show_time_events'] = data_save['data_show']
            event_log_data['show_commands'] = data_save['show_commands']
            event_log_data['show_redeem'] = data_save['show_redeem']
            event_log_data['show_events'] = data_save['show_events']
            event_log_data['show_join'] = data_save['show_join']
            event_log_data['show_leave'] = data_save['show_leave']
            event_log_data['show_commands_chat'] = data_save['show_commands_chat']
            event_log_data['show_redeem_chat'] = data_save['show_redeem_chat']
            event_log_data['show_events_chat'] = data_save['show_events_chat']
            event_log_data['show_join_chat'] = data_save['show_join_chat']
            event_log_data['show_leave_chat'] = data_save['show_leave_chat']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "save",event_log_data)

            toast('Salvo')
            
        except Exception as e:
            utils.error_log(e)
            toast('error')
            

def get_spec():
    
    global streaming

    while True:
        
        try:
            
            authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
            
            if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():
                
                data_count = twitch_api.get_streams(user_login=[authdata.USERNAME()])

                data_count_keys = data_count['data']
                    
                if not data_count_keys:

                    data_time = {
                        'specs': 'Offline',
                        'time': 'Offline',
                    }

                    window.evaluate_js(f"receive_live_info({json.dumps(data_time, ensure_ascii=False)})")

                    streaming = False

                    time.sleep(300)

                else:

                    time_in_live = utils.calculate_time(data_count['data'][0]['started_at'])

                    data_time = {
                        'specs': data_count['data'][0]['viewer_count'],
                        'time': "{:02d}:{:02d}".format(int(time_in_live['hours']), int(time_in_live['minutes'])),
                    }

                    window.evaluate_js(f"receive_live_info({json.dumps(data_time, ensure_ascii=False)})")
                    
                    streaming = True

                    time.sleep(300)
                
            else:
                
                time.sleep(300)

        except Exception as e:

            utils.error_log(e)

            data_time = {
                'specs': 'Offline',
                'time': 'Offline',
            }

            streaming = False

            window.evaluate_js(f"receive_live_info({json.dumps(data_time, ensure_ascii=False)})")
            time.sleep(300)

    
def get_chat_list():
    
    user_list_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "load")
    
    data = {
        'user_list': user_list_data['spec'],
        'bot_list': user_list_data['bot'],
    }

    return json.dumps(data, ensure_ascii=False)
      
        
def profile_info():
    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():
        
        user = twitch_api.get_users(logins=[authdata.USERNAME()])

        resp_user_id = user['data'][0]['id']
        resp_display_name = user['data'][0]['display_name']
        resp_login_name = user['data'][0]['login']
        resp_email = user['data'][0]['email']
        resp_profile_img = user['data'][0]['profile_image_url']

        profile_img = req.get(resp_profile_img).content

        with open(f"{utils.local_work('appdata_path')}/profile.png", 'wb') as profile_image:
            profile_image.write(profile_img)
            profile_image.close()

        data_auth = {
            "user_id": resp_user_id,
            "display_name": resp_display_name,
            "login_name": resp_login_name,
            "email": resp_email
        }


        return json.dumps(data_auth, ensure_ascii=False)
    
    else: 
        
        data_auth = {
            "user_id": 'RewardEvents',
            "display_name": 'RewardEvents',
            "login_name": 'RewardEvents',
            "email": 'RewardEvents'
        }


        return json.dumps(data_auth, ensure_ascii=False)

 
def get_redeem(type_id):

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():
        
        list_titles = {"redeem": []}

        path = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
        path_counter = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/config.json", "load")
        path_giveaway = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")
        path_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
        path_queue = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")
        
        counter_redeem = path_counter['redeem']
        giveaway_redeem = path_giveaway['redeem']
        player_redeem = path_player['redeem']
        queue_redeem = path_queue['redeem']

        list_rewards = twitch_api.get_custom_reward(broadcaster_id=authdata.BROADCASTER_ID())
        
        for indx in list_rewards['data'][0:]:
            
            if type_id == 'counter': 

                if indx['title'] not in path and indx['title'] not in [giveaway_redeem, queue_redeem, player_redeem]:
                    list_titles["redeem"].append(indx['title'])
                    
            elif type_id == 'giveaway':
                
                if indx['title'] not in path and indx['title'] not in [counter_redeem, queue_redeem, player_redeem]:
                    list_titles["redeem"].append(indx['title'])

            elif type_id == 'player':
                
                if indx['title'] not in path and indx['title'] not in [giveaway_redeem, queue_redeem, counter_redeem]:
                    list_titles["redeem"].append(indx['title'])

            elif type_id == 'queue':
                
                if indx['title'] not in path and indx['title'] not in [giveaway_redeem, counter_redeem, player_redeem]:
                    list_titles["redeem"].append(indx['title'])
                            
            else:

                if indx['title'] not in path and indx['title'] not in [giveaway_redeem, counter_redeem, player_redeem, queue_redeem]:
                    list_titles["redeem"].append(indx['title'])


        return json.dumps(list_titles, ensure_ascii=False)
    
    else:
        
        list_titles = {"redeem": []}
        return json.dumps(list_titles, ensure_ascii=False)


def get_edit_data(redeen, type_action):
    
    redeem_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

    if type_action == 'sound':

        sound = redeem_data[redeen]['path']
        command = redeem_data[redeen]['command']
        
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        audio_volume = redeem_data[redeen]['volume']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
            
        else:
            
            command_level = ''
            command_status = ''
            delay = ''
            

        data = {
            "sound": sound,
            "command": command,
            "delay": delay,
            "command_status": command_status,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "volume": audio_volume
        }

        return data

    if type_action == 'video':

        video = redeem_data[redeen]['path']
        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        time_showing_video = redeem_data[redeen]['show_time']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")


        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''
            

        data = {
            "video": video,
            "command": command,
            "command_status": command_status,
            "delay": delay,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "time_showing": time_showing_video
        }

        return data

    if type_action == 'tts':

        characters = redeem_data[redeen]['characters']
        command = redeem_data[redeen]['command']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json","load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''
            

        data = {
            "characters": characters,
            "command_status":command_status,
            "command": command,
            "user_level": command_level,
            "delay" : delay
        }

        return data

    if type_action == 'response':

        command = redeem_data[redeen]['command']
        response = redeem_data[redeen]['chat_response']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        data = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
            "user_level": command_level,
            "response": response,
        }

        return data

    if type_action == 'scene':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        scene_name = redeem_data[redeen]['scene_name']
        keep = redeem_data[redeen]['keep']
        time_scene = redeem_data[redeen]['time']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        data = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "scene_name": scene_name,
            "keep": keep,
            "time": time_scene
        }


        return data

    if type_action == 'filter':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        keep = redeem_data[redeen]['keep']
        time_filter = redeem_data[redeen]['time']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        data = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "keep": keep,
            "time": time_filter
        }

        return data

    if type_action == 'source':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        keep = redeem_data[redeen]['keep']
        time = redeem_data[redeen]['time']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''
        data = {
            "command": command,
            "command_status" : command_status,
            "delay" : delay,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "keep": keep,
            "time": time
        }

        return data

    if type_action == 'keypress':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        mode = redeem_data[redeen]['mode']

        key1 = redeem_data[redeen]['key1']
        key2 = redeem_data[redeen]['key2']
        key3 = redeem_data[redeen]['key3']
        key4 = redeem_data[redeen]['key4']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''
            
        if mode == 'keep':

            keep_press_time = redeem_data[redeen]['keep_press_time']

            data = {
                "command": command,
                "command_status": command_status,
                "delay": delay,
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

            return data

        elif mode == 'mult':

            time_press = redeem_data[redeen]['mult_press_times']
            interval = redeem_data[redeen]['mult_press_interval']

            data = {

                "command": command,
                "delay": delay,
                "command_status": command_status,
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

            return data

        elif mode == 're':

            re_press_time = redeem_data[redeen]['re_press_time']

            data = {
                "command": command,
                "delay" : delay,
                "command_status": command_status,
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

            return data

    if type_action == 'clip':

        command = redeem_data[redeen]['command']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        data = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
            "user_level": command_level,
        }

        return data

    if type_action == 'highlight':

        command = redeem_data[redeen]['command']

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        data = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
            "user_level": command_level,
        }

        return data


def reward(data):

    data = json.loads(data)
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

    type_id = data['type_id']

    def check_action(reward):

        path = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
        path_counter = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/config.json", "load")
        path_giveaway = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")
        path_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
        path_queue = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")
        
        counter_redeem = path_counter['redeem']
        giveaway_redeem = path_giveaway['redeem']
        player_redeem = path_player['redeem']
        queue_redeem = path_queue['redeem']

        reward_type = 'None'

        if reward in path:
            reward_type = path[reward]['type']
        elif reward in giveaway_redeem:
            reward_type = 'Sorteio'
        elif reward in counter_redeem:
            reward_type = 'Contador'
        elif reward in player_redeem:
            reward_type = 'Pedido de musica'
        elif reward in queue_redeem:
            reward_type = 'Fila de espera'
        else:
            reward_type = 'None'
        
        type_actions = {
            'sound' : "Audio",
            'video' : "Video",
            'tts' : "Texto Falado",
            'scene' : "Cena OBS Studio",
            'response' : "Resposta no chat",
            'filter' : "Filtro OBS Studio",
            'source' : "Fonte OBS Studio",
            'keypress' : "Precionar teclas ou atalho",
            'clip' : "Criar um clip",
            'highlight' : "Mensagem destacada"
        }

        if reward_type in type_actions:
            reward_type = type_actions[reward_type]

        return reward_type

    if type_id == 'get_list':

        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        
        if authdata.TOKEN() and authdata.USERNAME():
            
            list_rewards = twitch_api.get_custom_reward(broadcaster_id=authdata.BROADCASTER_ID())

            res_list_rewards = []

            for indx in list_rewards['data'][0:]:
                
                if indx['image'] != None:
                    image = indx['image']['url_4x']
                else:
                    image = indx['default_image']['url_4x']

                data = {
                    "title" : indx['title'],
                    "id" : indx['id'],
                    "image" : image, 
                    "prompt" : indx['prompt'],
                    "cost" : indx['cost'],
                    'action' : check_action(indx['title']),
                    "status" : indx['is_enabled']
                }

                res_list_rewards.append(data)

            return json.dumps(res_list_rewards, ensure_ascii=False)
        
        else:
            res_list_rewards = []
            
            return json.dumps(res_list_rewards, ensure_ascii=False)
    
    elif type_id == 'edit_reward':

        reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
        
        reward_name = data['reward_name']
        reward_id = data['reward_id']

        if reward_name in reward_data:

            reward_type = reward_data[reward_name]['type']

            reward_info = twitch_api.get_custom_reward(broadcaster_id=authdata.BROADCASTER_ID(),reward_id=reward_id)

            reward_info_data = reward_info['data'][0]

            reward_data_edit = get_edit_data(reward_name,reward_type)

            if reward_info_data['image'] != None:
                image = reward_info_data['image']['url_4x']
            else:
                image = reward_info_data['default_image']['url_4x']
            
            data = {
                "reward_edit" : 'true',
                "reward_type" : reward_type,
                "reward_data" : reward_data_edit,
                "image" : image,
                "title" : reward_info_data["title"],
                "prompt" : reward_info_data["prompt"],
                "cost" : reward_info_data["cost"],
                "status" : reward_info_data['is_enabled']
            } 

            return json.dumps(data, ensure_ascii=False)

        else :

            reward_info = twitch_api.get_custom_reward(broadcaster_id=authdata.BROADCASTER_ID(),reward_id=reward_id)

            reward_info_data = reward_info['data'][0]

            if reward_info_data['image'] != None:
                image = reward_info_data['image']['url_4x']
            else:
                image = reward_info_data['default_image']['url_4x']
        
            data = {
                "reward_edit" : 'false',
                "reward_type" : 'none',
                "reward_data" : 'none',                
                "image" : image,
                "title" : reward_info_data["title"],
                "prompt" : reward_info_data["prompt"],
                "cost" : reward_info_data["cost"],
                "status" : reward_info_data['is_enabled']
            }  

            return json.dumps(data, ensure_ascii=False)
        
    elif type_id == "save_reward":


        reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
        
        data_received = data

        redeem_type = data_received['type_edit']

        if redeem_type == 'sound':

            try:

                redeem = data_received['redeem']
                command = data_received['command']
                chat_message = data_received['chat_message']
                sound_path = data_received['sound_path']
                volume = data_received['audio_volume']

                if chat_message != "":
                    send_message = 1
                else:
                    send_message = 0

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
                
                reward_data[redeem] = {
                    'type': "sound",
                    'path': sound_path,
                    'volume' : volume,
                    'command': command,
                    'send_response': send_message,
                    'chat_response': chat_message,
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",reward_data )

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')
        
        if redeem_type == 'video':

            try:

                redeem = data_received['redeem']
                command = data_received['command']
                chat_message = data_received['chat_message']
                video_path = data_received['video_path']
                time_showing_video = data_received['time_showing_video']

                if chat_message != "":
                    send_message = 1
                else:
                    send_message = 0

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {
                    'type': "video",
                    'path': video_path,
                    'command': command,
                    'send_response': send_message,
                    'chat_response': chat_message,
                    'show_time' : time_showing_video
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)
                
                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')

        if redeem_type == 'tts':

            try:

                redeem = data_received['redeem']
                command = data_received['command']
                characters = data_received['characters']


                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {
                    'type': "tts",
                    'characters': characters,
                    'command': command
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')
        
        if redeem_type == 'scene':

            try:
                redeem = data_received['redeem']
                command = data_received['command']
                chat_message = data_received['chat_message']
                scene_name = data_received['scene_name']
                keep = data_received['keep']
                time = data_received['time']

                if chat_message != "":
                    send_message = 1
                else:
                    send_message = 0

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {
                    'type': "scene",
                    'command': command,
                    'send_response': send_message,
                    'chat_response': chat_message,
                    'scene_name': scene_name,
                    'keep': keep,
                    'time': time
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')

        if redeem_type == 'response':

            try:

                redeem = data_received['redeem']
                command = data_received['command']
                chat_message = data_received['chat_message']

                if chat_message != "":
                    send_message = 1
                else:
                    send_message = 0

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {
                    'type': "response",
                    'command': command,
                    'send_response': send_message,
                    'chat_response': chat_message,
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')

        if redeem_type == 'filter':

            try:

                redeem = data_received['redeem']
                command = data_received['command']
                chat_message = data_received['chat_message']
                source_name = data_received['source_name']
                filter_name = data_received['filter']
                keep = data_received['keep']
                time = data_received['time']

                if chat_message != "":
                    send_message = 1
                else:
                    send_message = 0

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {
                    'type': "filter",
                    'command': command,
                    'send_response': send_message,
                    'chat_response': chat_message,
                    'source_name': source_name,
                    'filter_name': filter_name,
                    'keep': keep,
                    'time': time
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')

        if redeem_type == 'source':

            try:
                redeem = data_received['redeem']
                command = data_received['command']
                chat_message = data_received['chat_message']
                source_name = data_received['source']
                keep = data_received['keep']
                time = data_received['time']

                if chat_message != "":
                    send_message = 1
                else:
                    send_message = 0

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {

                    'type': "source",
                    'command': command,
                    'send_response': send_message,
                    'chat_response': chat_message,
                    'source_name': source_name,
                    'keep': keep,
                    'time': time
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')

        if redeem_type == 'keypress':

            try:
                redeem = data_received['redeem']
                command = data_received['command']
                chat_message = data_received['chat_message']
                mode_press = data_received['mode']

                key1 = data_received['key1']
                key2 = data_received['key2']
                key3 = data_received['key3']
                key4 = data_received['key4']

                if chat_message != "":
                    send_message = 1
                else:
                    send_message = 0

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                if mode_press == 'mult':

                    mult_press_times = data_received['mult_press_times']
                    mult_press_interval = data_received['mult_press_interval']

                    reward_data[redeem] = {

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

                    reward_data[redeem] = {

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

                    reward_data[redeem] = {

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

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')

        if redeem_type == 'clip':

            try:
                redeem = data_received['redeem']
                command = data_received['command']

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {
                    'type': "clip",
                    'command': command,
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)

                toast('error')

        if redeem_type == 'highlight':

            try:
                redeem = data_received['redeem']
                command = data_received['command']

                reward_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

                reward_data[redeem] = {
                    'type': "highlight",
                    'command': command,
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

                create_command_redeem(data_received,'edit')

                toast('success')

            except Exception as e:

                utils.error_log(e)
                toast('error')
    
    elif type_id == "create_reward":

        data_receive = data

        if type_id == 'sound':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            audio_path = data_receive['audio_path']
            volume = data_receive['audio_volume']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            reward_data[redeem_value] = {
                'type': 'sound',
                'path': audio_path,
                'volume': volume,
                'command': command_value.lower(),
                'send_response': send_response,
                'chat_response': chat_response
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'video':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            video_path = data_receive['video_path']
            time_showing_video = data_receive['time_showing_video']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 
            
            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            reward_data[redeem_value] = {

                'type': 'video',
                'path': video_path,
                'command': command_value.lower(),
                'send_response': send_response,
                'chat_response': chat_response,
                'show_time': time_showing_video
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'tts':


            redeem_value = data_receive['redeem_value']
            command_value = data_receive['command_value']

            characters = data_receive['characters']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            reward_data[redeem_value] = {
                'type': 'tts',
                'command': command_value.lower(),
                'characters': characters
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)
            
            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'scene':

            redeem_value = data_receive['redeem_value']
            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']

            scene_name = data_receive['scene_name']
            time_to_return = data_receive['time']
            keep_scene_value = data_receive['keep_scene_value']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 
            
            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            if time_to_return == "":
                time_to_return = 0

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            reward_data[redeem_value] = {

                'type': 'scene',
                'send_response': send_response,
                'command': command_value.lower(),
                'chat_response': chat_response,
                'scene_name': scene_name,
                'keep': keep_scene_value,
                'time': time_to_return
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            
            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'response':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            reward_data[redeem_value] = {
                'type': 'response',
                'command': command_value.lower(),
                'chat_response': chat_response
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'filter':


            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            filter_name = data_receive['filter_name']
            source_name = data_receive['source_name']
            time_showing = data_receive['time_showing']
            keep = data_receive['keep']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            if time_showing == "":
                time_showing = 0

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            reward_data[redeem_value] = {

                'type': 'filter',
                'source_name': source_name,
                'send_response': send_response,
                'chat_response': chat_response,
                'command': command_value.lower(),
                'filter': filter_name,
                'keep': keep,
                'time': int(time_showing)
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'source':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            source_name = data_receive['source_name']
            time_showing = data_receive['time_showing']
            keep = data_receive['keep']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            if time_showing == "":
                time_showing = 0

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            reward_data[redeem_value] = {

                'type': 'source',
                'send_response': send_response,
                'chat_response': chat_response,
                'command': command_value.lower(),
                'source_name': source_name,
                'keep': keep,
                'time': int(time_showing)

            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)


            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'keypress':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            mode_press = data_receive['mode']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            key1 = data_receive['key1']
            key2 = data_receive['key2']
            key3 = data_receive['key3']
            key4 = data_receive['key4']

            if key1 == "none":
                key1 = "NONE"
            if key2 == "none":
                key2 = "NONE"
            if key3 == "none":
                key3 = "NONE"
            if key4 == "none":
                key4 = "NONE"

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if mode_press == 'mult':

                mult_press_times = data_receive['mult_press_times']
                mult_press_interval = data_receive['mult_press_interval']

                reward_data[redeem_value] = {

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

                reward_data[redeem_value] = {

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

                reward_data[redeem_value] = {

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


            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'clip':

            command_value = data_receive['command_value']
            redeem_value = data_receive['redeem_value']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            reward_data[redeem_value] = {'type': 'clip', 'command': command_value.lower(), }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)


            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'highlight':

            command_value = data_receive['command_value']
            redeem_value = data_receive['redeem_value']

            if redeem_value == '':
                redeem_value = f'RandomRedeem_{int(time.time())}' 

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            reward_data[redeem_value] = {'type': 'highlight', 'command': command_value.lower(), }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)


            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'delete':

            data = data_receive['redeem']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)

            command = reward_data[data]['command']

            data_command = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

            if command in data_command.keys():
                del data_command[command]

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "save",data_command)

            del reward_data[data]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", reward_data)
    
    elif type_id == "remove_action":

        try:

            reward = data['reward']
                
            data_event = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
            data_command = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

            command = data_event[reward]['command']

            if command in data_command.keys():
                del data_command[command]
     
            del data_event[reward]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "save",data_command)  
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",data_event)
            
            toast(f'Evento removido da recompensa ${reward}')

        except Exception as e:

            utils.error_log(e)
            toast('Erro ao excluir o evento')
        

def select_file_py(type_id):
    
    if type_id == 'sound':
    
        filetypes = (
            ('audio files', '*.mp3'),
            ('All files', '*.*')
        )

    elif type_id == 'video':

        filetypes = (
            ('video files', '*.mp4'),
            ('gif files', '*.gif'),
            ('All files', '*.*')
        )

    elif type_id == 'image':

        filetypes = (
        ('png files', '*.png'),
        ('gif files', '*.gif')
        )

    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    folder = fd.askopenfilename(
        initialdir= f"{utils.local_work('appdata_path')}",
        filetypes= filetypes)

    root.destroy()
    
    return folder


def update_scene_obs():
    scenes = obs_events.get_scenes()

    return scenes


def get_filters_obs(source):

    filters = obs_events.get_filters(source)

    return filters


def get_sources_obs():

    sources = obs_events.get_sources()

    return sources


def get_stream_info_py():
    
    try:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        
        if authdata.TOKEN() and authdata.USERNAME():

            resp_stream_info = twitch_api.get_channel_information(authdata.BROADCASTER_ID())
            
            title = resp_stream_info['data'][0]['title']
            game = resp_stream_info['data'][0]['game_name']
            game_id = resp_stream_info['data'][0]['game_id']
            tag_list = resp_stream_info['data'][0]['tags']
            
            data = {
                'game_name': game,
                'game_id': game_id,
                'title': title,
                'tag': tag_list,
            }
            
            return json.dumps(data, ensure_ascii=False)
        
        else:
            
            data = {
                'game_name': 'RewardEvents',
                'game_id': 'RewardEvents',
                'title': 'RewardEvents',
                'tag': 'RewardEvents',
            }

            return json.dumps(data, ensure_ascii=False)
            
    
    except Exception as e:

        utils.error_log(e)
        toast('Erro ao obter informações da stream')


def save_stream_info_py(data):
    
    try:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        
        if authdata.TOKEN() and authdata.USERNAME():
            
            data = json.loads(data)
            
            title = data['title']
            game = data['game']
            game_id = data['game_id']
            tags = data['tags']
            
            headers = {
                'Authorization': f'Bearer {authdata.TOKEN()}',
                'Client-Id': os.getenv('CLIENTID'),
                'Content-Type': 'application/json',
            }

            params = {
                'broadcaster_id': authdata.BROADCASTER_ID(),
            }

            json_data = {
                'game_id': game_id,
                'title': title,
                'broadcaster_language': '',
                'tags': tags,
            }
            
            response = req.patch('https://api.twitch.tv/helix/channels', params=params, headers=headers, json=json_data)
            
            if response.status_code != 204:
                toast(f'Erro ao atualizar as informações da stream : {response.json()}')  
            else:
                toast('success')

            
    except Exception as e:

        utils.error_log(e)
        toast('error')


def create_command_redeem(data,type_id):
    
    if type_id == "create":
        
        command_delay = data['command_delay']
        
        if command_delay == '':
            command_delay = 0
            
        command_status = 1
        command_value = data['command_value']
        redeem_value = data['redeem_value']
        user_level_value = data['user_level_value']

        new_data_command = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")  
        
        new_data_command[command_value.lower().strip()] = {
            'status' : command_status,
            'delay' : command_delay,
            'last_use': 0,
            'redeem': redeem_value, 
            'user_level': user_level_value
        }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "save", new_data_command)  
       
    elif type_id == "edit":
        
        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")  
        
        command_old = data['old_command']
        command_new = data['command']
        command_status = data['command_status']
        command_delay = data['delay']
        command_redeem = data['redeem']
        command_user_level = data['user_level']
        
        if command_old != '' and command_old in command_data:
            del command_data[command_old.strip()]

        if command_new != "":
            command_data[command_new.lower().strip()] = {
                'last_use': 0,
                'status' : int(command_status),
                'delay' : int(command_delay),
                'redeem': command_redeem,
                'user_level': command_user_level
            }
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "save", command_data)  


def get_command_list():
    
    command_redem_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")
    command_simple_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")
    command_default_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "load")
    command_data_counter = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "load")
    command_data_giveaway = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "load")
    command_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
    
    data = {
        'commands_redeem' : [command_redem_data],
        'commands_simple' : [command_simple_data],
        'commands_default' : [command_default_data],
        'commands_counter' : [command_data_counter],
        'commands_giveaway' : [command_data_giveaway],
        'commands_player' : [command_data_player], 
    }

    return json.dumps(data, ensure_ascii=False)


def prediction_py(data):

    data_receive = json.loads(data)
    type_id = data_receive['type_id']
    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if authdata.TOKEN() and authdata.USERNAME():
        
        if type_id == 'start':

            titlerec = data_receive['title']
            options = data_receive['options']
            duration = int(data_receive['duration'])
            discord = int(data_receive['discord'])

            discord_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "load")
            
            discord_data['prediction_start']['status'] = discord
            discord_data['prediction_progress']['status'] = discord
            discord_data['prediction_end']['status'] = discord

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "save",discord_data)

            twitch_api.create_prediction(
                authdata.BROADCASTER_ID(),
                title=titlerec,
                outcomes=options,
                prediction_window=int(duration)
            )
            
        elif type_id == 'get':

            pred_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", "load")
            
            if pred_data['status'] == 'running':

                status = pred_data['status']
                title = pred_data['title']
                options = pred_data['options']
                start_time = pred_data['time_start']
                lock_time = pred_data['time_locks']

            elif pred_data['status'] == 'locked' :

                status = pred_data['status']
                title = pred_data['title']
                options = pred_data['options']
                start_time = pred_data['time_start']
                lock_time = pred_data['time_locks']

            elif pred_data['status'] == 'end' :

                status = pred_data['status']
                title = ''
                options = ''
                start_time = ''
                lock_time = ''


            data = {
                'status' : status,
                'title' : title,
                'options' : options,
                'start_time' : start_time,
                'lock_time' : lock_time
            }


            return json.dumps(data)

        elif type_id == 'lock':

            pred_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", "load")

            twitch_api.end_prediction(authdata.BROADCASTER_ID(),prediction_id=pred_data['current'],status=PredictionStatus.LOCKED)

        elif type_id == 'cancel':

            pred_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", "load")

            twitch_api.end_prediction(authdata.BROADCASTER_ID(),prediction_id=pred_data['current'],status=PredictionStatus.CANCELED)
        
        elif type_id == 'send':
            
            pred_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", "load")

            twitch_api.end_prediction(authdata.BROADCASTER_ID(),prediction_id=data_receive['op_id'],status=PredictionStatus.RESOLVED,winning_outcome_id=pred_data['current'])

    else:
        toast("Não autenticado")


def poll_py(data):
    
    data_receive = json.loads(data)
    
    type_id = data_receive['type_id']

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if authdata.TOKEN() and authdata.USERNAME():
        
        if type_id == "create" :

            title = data_receive['title']
            options = data_receive['options']
            duration = int(data_receive['duration'])
            points_enable = data_receive['points_status']
            points = int(data_receive['points'])
            discord = int(data_receive['discord'])
        
            discord_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "load")
            
            discord_data['poll_start']['status'] = discord
            discord_data['poll_status']['status'] = discord
            discord_data['poll_end']['status'] = discord
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "save",discord_data)
            
            if points_enable:
                points_enable == True
                twitch_api.create_poll(
                    authdata.BROADCASTER_ID(),
                    title=title,
                    choices=options,
                    duration=duration,
                    channel_points_voting_enabled=points_enable,
                    channel_points_per_vote=points
                )
            else:
                points_enable == False
                
                twitch_api.create_poll(
                    authdata.BROADCASTER_ID(),
                    title=title,
                    choices=options,
                    duration=duration,
                )

        elif type_id == "end":

            poll_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", "load") 

            twitch_api.end_poll(authdata.BROADCASTER_ID(),poll_id=poll_data['current'],status=PollStatus.TERMINATED)

        elif type_id == "get":
            
            poll_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", "load") 

            data = {
                "status" : poll_data['status'],
                "title" : poll_data['title'],
                "time_start" : poll_data['time_start'],
                "time_end" : poll_data['time_end'],
                "options" : poll_data['options'],
            }

            return json.dumps(data)

    else:
        toast("Não autenticado")


def goal_py():

    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "load") 

    return json.dumps(goal_data)


def create_action_save(data, type_id):
    
    data_receive = json.loads(data)

    if type_id == 'audio':

        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']
        audio_path = data_receive['audio_path']
        volume = data_receive['audio_volume']

        if chat_response == "":
            send_response = 0
        else:
            send_response = 1


        path_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
            

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        path_data[redeem_value] = {
            'type': 'sound',
            'path': audio_path,
            'volume': volume,
            'command': command_value.lower(),
            'send_response': send_response,
            'chat_response': chat_response
        }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",path_data)
            
            
        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'video':

        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']
        video_path = data_receive['video_path']
        time_showing_video = data_receive['time_showing_video']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 
        
        if chat_response == "":
            send_response = 0
        else:
            send_response = 1

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

        new_data[redeem_value] = {

            'type': 'video',
            'path': video_path,
            'command': command_value.lower(),
            'send_response': send_response,
            'chat_response': chat_response,
            'show_time': time_showing_video
        }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)

        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'tts':


        redeem_value = data_receive['redeem_value']
        command_value = data_receive['command_value']

        characters = data_receive['characters']

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        new_data[redeem_value] = {
            'type': 'tts',
            'command': command_value.lower(),
            'characters': characters
        }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)
        
        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'scene':


        redeem_value = data_receive['redeem_value']
        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']

        scene_name = data_receive['scene_name']
        time_to_return = data_receive['time']
        keep_scene_value = data_receive['keep_scene_value']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 
        
        if chat_response == "":
            send_response = 0
        else:
            send_response = 1

        if time_to_return == "":
            time_to_return = 0

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

        new_data[redeem_value] = {

            'type': 'scene',
            'send_response': send_response,
            'command': command_value.lower(),
            'chat_response': chat_response,
            'scene_name': scene_name,
            'keep': keep_scene_value,
            'time': time_to_return
        }


        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)
        
        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'response':


        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

        new_data[redeem_value] = {
            'type': 'response',
            'command': command_value.lower(),
            'chat_response': chat_response
        }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)

        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'filter':


        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']
        filter_name = data_receive['filter_name']
        source_name = data_receive['source_name']
        time_showing = data_receive['time_showing']
        keep = data_receive['keep']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        if chat_response == "":
            send_response = 0
        else:
            send_response = 1

        if time_showing == "":
            time_showing = 0

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

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

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)

        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'source':

        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']
        source_name = data_receive['source_name']
        time_showing = data_receive['time_showing']
        keep = data_receive['keep']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        if chat_response == "":
            send_response = 0
        else:
            send_response = 1

        if time_showing == "":
            time_showing = 0

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

        new_data[redeem_value] = {

            'type': 'source',
            'send_response': send_response,
            'chat_response': chat_response,
            'command': command_value.lower(),
            'source_name': source_name,
            'keep': keep,
            'time': int(time_showing)

        }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)

        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'keypress':

        command_value = data_receive['command_value']
        chat_response = data_receive['chat_response']
        redeem_value = data_receive['redeem_value']
        mode_press = data_receive['mode']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        key1 = data_receive['key1']
        key2 = data_receive['key2']
        key3 = data_receive['key3']
        key4 = data_receive['key4']

        if key1 == "none":
            key1 = "NONE"
        if key2 == "none":
            key2 = "NONE"
        if key3 == "none":
            key3 = "NONE"
        if key4 == "none":
            key4 = "NONE"

        if chat_response == "":
            send_response = 0
        else:
            send_response = 1

        key_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
        
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

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", key_data)

        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'clip':

        command_value = data_receive['command_value']
        redeem_value = data_receive['redeem_value']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

        new_data[redeem_value] = {'type': 'clip', 'command': command_value.lower(), }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)

        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'highlight':


        command_value = data_receive['command_value']
        redeem_value = data_receive['redeem_value']

        if redeem_value == '':
            redeem_value = f'RandomRedeem_{int(time.time())}' 

        new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")

        new_data[redeem_value] = {'type': 'highlight', 'command': command_value.lower(), }

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save",new_data)

        if command_value != "":
            create_command_redeem(data_receive,'create')

    elif type_id == 'delete':

        data = data_receive['redeem']

        data_event = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
        
        command = data_event[data]['command']

        data_command = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")

        if command in data_command.keys():
            
            del data_command[command]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "save", data_command)

        del data_event[data]


        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "save", data_event)
   
        
def commands_py(type_rec, data_receive):

    if type_rec == 'create':

        try:

            data = json.loads(data_receive)
            command = data['new_command']
            message = data['new_message']
            delay = data['new_delay']
            command_counts = 0
            if delay == '':
                delay = 0
            user_level_check = data['new_user_level']

            data_command = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")

            data_command[command.lower().strip()] = {
                'status' : 1,
                'response': message,
                'user_level': user_level_check,
                'counts' : command_counts,
                'delay' : delay,
                'last_use': 0,
            }
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "save",data_command )

            toast('success')

        except Exception as e:
            utils.error_log(e)

            toast('error')

    elif type_rec == 'edit':

        try:
            data = json.loads(data_receive)

            old_command = data['old_command']
            new_command = data['edit_command']
            status = data['status_command']
            new_message = data['edit_message']
            new_delay = data['edit_delay']

            if "edit_used_times" in data:
                command_count = data['edit_used_times']
            else:
                command_count = 0

            if new_delay == '':
                new_delay = 0

            user_level = data['edit_user_level']

            command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")

            del command_data[old_command]
            command_data[new_command] = {
                "status" : status,
                "response": new_message,
                "user_level": user_level,
                "counts" : command_count,
                "delay" : new_delay,
                "last_use" : 0
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "save",command_data)

            toast('success')

        except Exception as e:
            utils.error_log(e)
            toast('error')

    elif type_rec == 'delete':

        try:
            command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")

            del command_data[data_receive]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "save",command_data)

            toast('Comando excluido')

        except Exception as e:
            utils.error_log(e)
            
            toast('error')

    elif type_rec == 'get_info':
        
        try:

            command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")
            
            message = command_data[data_receive]['response']
            user_level = command_data[data_receive]['user_level']
            delay = command_data[data_receive]['delay']
            if delay == '':
                delay = 0
            status = command_data[data_receive]['status']

            data = {
                "status" : status,
                'edit_command': data_receive,
                'edit_message': message,
                'edit_level': user_level,
                'edit_delay': delay
            }

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:
            utils.error_log(e)

    elif type_rec == 'get_list':

        try:

            new_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")

            list_commands = []

            for key in new_data:
                list_commands.append(key)

            return json.dumps(list_commands, ensure_ascii=False)

        except Exception as e:
            utils.error_log(e)

    elif type_rec == 'get_duel':

        duel_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/duel/duel.json", "load")
            
        data = {
            'command_duel' : duel_data['command'],
            'command_accept' : duel_data['command_accept'],
            'user_level' : duel_data['user_level'],
            'delay' : duel_data['delay'],
            'time_to_accept' : duel_data['time_to_accept'],
            'time_to_message' : duel_data['time_to_message'],
            'time_to_start' : duel_data['time_to_start'],
            'create_pred' : duel_data['create_pred'],
            'duel_battle_list' : duel_data['duel_battle']
        }

        return json.dumps(data, ensure_ascii=False)
        
    elif type_rec == 'get_battles':
        
        duel_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/duel/duel.json", "load")
            
        battle = duel_data['duel_battle'][data_receive]
        
        data = {
            'message_0' : battle['start_mess'],
            'message_1' : battle['stage_1'],
            'message_2' : battle['stage_2'],
            'message_3' : battle['stage_3'],
            'message_4' : battle['stage_4'],
            'message_5' : battle['stage_5'],
        }


        return json.dumps(data, ensure_ascii=False)
        
    elif type_rec == 'save_duel':
        
        data_duel = utils.manipulate_json(f"{utils.local_work('appdata_path')}/duel/duel.json", "load")

        data = json.loads(data_receive)
        
        data_duel['command'] = data['command_duel']
        data_duel['command_accept'] = data['command_accept']
        data_duel['user_level'] = data['user_level_duel'] 
        data_duel['delay'] = data['delay']                                  
        data_duel['time_to_accept'] = int(data['time_to_accept'])
        data_duel['time_to_message'] = int(data['time_to_message'])
        data_duel['time_to_start'] = int(data['time_to_start'])
        data_duel['create_pred'] = data['create_pred']
        
        if data['select_batle'] != 'None' :
            
            data_duel['duel_battle'][data['select_batle']]['start_mess'] = data['message_0']
            data_duel['duel_battle'][data['select_batle']]['stage_1'] = data['message_1']
            data_duel['duel_battle'][data['select_batle']]['stage_2'] = data['message_2']
            data_duel['duel_battle'][data['select_batle']]['stage_3'] = data['message_3']
            data_duel['duel_battle'][data['select_batle']]['stage_4'] = data['message_4']
            data_duel['duel_battle'][data['select_batle']]['stage_5'] = data['message_5']
        
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/duel/duel.json", "save",data_duel)
        
        toast('Duelo salvo')
    
    elif type_rec == 'get_default':
    
        default_data_commands = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "load")

        data = {
            "command": default_data_commands[data_receive]['command'],
            "status": default_data_commands[data_receive]['status'],
            "delay": default_data_commands[data_receive]['delay'],
            "last_use": default_data_commands[data_receive]['last_use'],
            "response": default_data_commands[data_receive]['response'],
            "user_level": default_data_commands[data_receive]['user_level'],
        }

        return json.dumps(data, ensure_ascii=False)           

    elif type_rec == 'save_default':
        
        try:

            data = json.loads(data_receive)  

            default_data_commands = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "load")

            type_cmd = data["default_type"]

            default_data_commands[type_cmd]["command"] = data['command']
            default_data_commands[type_cmd]["status"] = data['status']
            default_data_commands[type_cmd]["delay"] = data['delay']
            default_data_commands[type_cmd]["response"] = data['response']
            default_data_commands[type_cmd]["user_level"] = data['perm']
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "save", default_data_commands)
            
            toast('Comando salvo')

        except Exception as e:
            utils.error_log(e)

 
def timer_py(type_id, data_receive):
    
    if type_id == "get":
        
        timer_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "load")
        message_data_get = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands_config.json", "load")

        status_timer = message_data_get['STATUS_TIMER']
        timer_delay_min = timer_data['TIME']
        timer_delay_max = timer_data['TIME_MAX']
        messages_list = timer_data['MESSAGES']
        last = timer_data['LAST']

        data = {
            "delay_min": timer_delay_min,
            "delay_max": timer_delay_max,
            "messages": messages_list,
            "status": status_timer,
            "last" : last
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "get_message":
               
        timer_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "load")
        
        message = timer_data['MESSAGES'][data_receive]['message']
        type_timer = timer_data['MESSAGES'][data_receive]['type_timer']
        timer_color = timer_data['MESSAGES'][data_receive]['color']

        data = {
            "message": message,
            "type_timer": type_timer,
            "color" : timer_color
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "edit":
        
        try:    

            data = json.loads(data_receive)

            data_key = data['key']
            data_message = data['message']
            data_type = data['type_timer']
            data_color = data['color']

            timer_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "load")
        
            timer_data['MESSAGES'][data_key] = {'message' : data_message, 'type_timer' :data_type, 'color' : data_color}

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "save", timer_data)
            
            toast('success')

        except Exception as e:

            utils.error_log(e)

            toast('error')
            
    elif type_id == "add":
        
        try:
            
            data = json.loads(data_receive)

            data_color = data['color']
            data_message = data['message']
            data_type = data['type_timer']
            
            timer_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "load")
        
            timer_message = timer_data['MESSAGES']

            if not timer_message:

                keytoadd = 1

            else:
                key = list(timer_message.keys())[-1]
                keytoadd = int(key) + 1

            timer_data['MESSAGES'][str(keytoadd)] = {"message" : data_message, "type_timer": data_type, "color" : data_color}

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "save", timer_data)
            
            toast('success')

        except Exception as e:

            utils.error_log(e)

            toast('error')
            
    elif type_id == "del":
        
        try:

            message_del_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "load")
        
            del message_del_data['MESSAGES'][data_receive]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "save", timer_data)
            
            toast('Mensagem excluida')

        except Exception as e:

            utils.error_log(e)

            toast('error')

    elif type_id == "delay":
        
        try:    
            data = json.loads(data_receive)
            
            min_time = data['min_time']
            max_time = data['max_time']
                
            timer_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "load")
         
            timer_data['TIME'] = int(min_time)
            timer_data['TIME_MAX'] = int(max_time)
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "save", timer_data)
            
            toast('success')
            
        except Exception as e:

            utils.error_log(e)
            toast('error')

    elif type_id == "status":
        
        try:    
            command_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands_config.json", "load")
         
            command_config_data['STATUS_TIMER'] = data_receive
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands_config.json", "save", command_config_data)
             
            if data_receive:

                toast('Timer ativado')
                
            elif data_receive == 0:

                toast('Timer desativado')
                
        except Exception as e:

            utils.error_log(e)
            toast('error')


def giveaway_py(type_id, data_receive):
    
    if type_id == 'get_config':
        
            giveaway_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")
          
            data = {
                "giveaway_name": giveaway_data['name'],
                "giveaway_level": giveaway_data['user_level'],
                "giveaway_clear": giveaway_data['clear'],
                "giveaway_enable": giveaway_data['enable'],
                "giveaway_redeem": giveaway_data['redeem'],
                "giveaway_mult": giveaway_data['allow_mult_entry'],
            }
            
            return json.dumps(data, ensure_ascii=False)

    elif type_id == 'get_commands':
                    
        giveaway_commands_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "load")
          
        data = {
            "command" : giveaway_commands_data[data_receive]["command"],
            "status" : giveaway_commands_data[data_receive]["status"],
            "delay": giveaway_commands_data[data_receive]["delay"],
            "last_use" : giveaway_commands_data[data_receive]["last_use"],
            "user_level" : giveaway_commands_data[data_receive]["user_level"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == 'show_names':
        
        giveaway_commands_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")

        return json.dumps(giveaway_commands_data, ensure_ascii=False)

    elif type_id == 'save_config':

        try:
            
            data = json.loads(data_receive)

            giveaway_data_new = {
                "name": data['giveaway_name'],
                "redeem": data['giveaway_redeem'],
                "user_level": data['giveaway_user_level'],
                "clear": data['giveaway_clear_check'],
                "enable": data['giveaway_enable'],
                "allow_mult_entry" : data['giveaway_mult'],
            }
            
                
            giveaway_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")

            if giveaway_data['enable'] and data['giveaway_enable'] == 0:
                
                aliases = {
                    '{giveaway_name}' : giveaway_data['name'],
                }
                
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('giveaway_status_disable'), aliases))

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "save", giveaway_data_new)

            toast('success')
                            
            giveaway_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")

            if giveaway_data['enable']:
                
                aliases = {
                    '{giveaway_name}' : giveaway_data['name'],
                    '{redeem}' : giveaway_data['redeem']
                }
                
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('giveaway_status_enable'), aliases))
                    
                toast('Sorteio iniciado')


        except Exception as e:

            utils.error_log(e)
            toast('error')
        
    elif type_id == 'save_commands':
        
        data = json.loads(data_receive)

        try:

            giveaway_commands_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "load")


            giveaway_commands_data[data['type_command']] = {
                "command" : data['command'],
                "status" :data['status'],
                "delay" : data['delay'],
                "last_use": giveaway_commands_data[data['type_command']]['last_use'],
                "user_level" : data['user_level']
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "save", giveaway_commands_data)

            toast('success')

        except Exception as e:

            utils.error_log(e)

            toast('error')
        
    elif type_id == 'add_user':
        
        if not type(data_receive) is dict:
            data = json.loads(data_receive)
        else: 
            data = data_receive
    
        new_name = data['new_name']
        user_level = data['user_level']
        
        def check_perm(user_list, command_list):
            list_1 = set(user_list)
            list_2 = set(command_list)

            if list_1.intersection(list_2):
                return True
            else:
                return False


        try:

            def append_name(new_name):
                
                giveaway_name_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")
                back_giveaway_name_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/backup.json", "load")

                giveaway_name_data.append(new_name)
                back_giveaway_name_data.append(new_name)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "save", giveaway_name_data)
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/backup.json", "save", back_giveaway_name_data)
                
                aliases = {
                    "{username}" : new_name
                }

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('giveaway_response_user_add'), aliases))


                toast(f'O usuário {new_name} foi adicionado na lista')
            
            giveaway_name_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")
            giveaway_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")

            if giveaway_config_data['enable']:
                
                giveaway_perm = giveaway_config_data['user_level']
                giveaway_mult_config = giveaway_config_data['allow_mult_entry']

                aliases = {
                    '{username}': str(new_name),
                    '{perm}' : str(giveaway_perm)
                }

                if giveaway_mult_config == 0:

                    if new_name in giveaway_name_data:

                        toast('Este nome já está no sorteio, para adicionar ative a opção para permitir multiplas entradas no sorteio.')

                        if utils.send_message("RESPONSE"):
                            send(utils.replace_all(utils.messages_file_load('giveaway_response_mult_add'), aliases))
                            
                    else:
                        
                        if check_perm(user_level, giveaway_perm):
                            append_name(new_name)

                        else:

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('giveaway_response_perm'), aliases))
                else:

                    if check_perm(user_level, giveaway_perm):
                        append_name(new_name)

                    else:
                        if utils.send_message("RESPONSE"):
                            send(utils.replace_all(utils.messages_file_load('giveaway_response_perm'), aliases))

            else:

                aliases = {
                    '{username}': str(giveaway_config_data['user_level']),
                    '{perm}' : str(giveaway_config_data['allow_mult_entry'])
                }

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('giveaway_status_disabled'), aliases))

        except Exception as e:
            
            utils.error_log(e)
            toast('error')
        
    elif type_id == 'execute':
        
        try:
            
            giveaway_name_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")
            giveaway_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")

            reset_give = giveaway_data['clear']

            name = random.choice(giveaway_name_data)

            aliases = {
                '{username}': str(name)
            }
            
            if utils.send_message("RESPONSE"):
                send(utils.replace_all(utils.messages_file_load('giveaway_response_win')))

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/backup.json", "save",giveaway_name_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/result.json", "save",[name])
            
            if reset_give:
                
                reset_data = []

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "save",reset_data)


            toast(f'{name} Ganhou o sorteio !')

        except Exception as e:

            utils.error_log(e)

            toast('Erro ao executar o sorteio')
        
    elif type_id == 'clear_list':
        
        try:
            reset_data = []

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "save",reset_data)

            toast('Lista de sorteio limpa')

        except Exception as e:
            utils.error_log(e)
            toast('error')
  
  
def counter(type_id, data_receive):
    
    if type_id == 'get_counter_config':
        
        counter_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/config.json", "load")
        
        with open( f"{utils.local_work('appdata_path')}/counter/counter.txt", "r") as counter_file_r:
            counter_file_r.seek(0)
            counter_value_get = counter_file_r.read()

        data = {

            "redeem": counter_data['redeem'],
            "response" : counter_data['response'],
            "response_chat" : utils.messages_file_load('response_counter'),
            "response_set_chat" : utils.messages_file_load('response_set_counter'),
            "value_counter": counter_value_get,   
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save_counter_config":

        try:
            data_save = json.loads(data_receive)
            
            counter_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/config.json", "load")
            messages_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/messages/messages_file.json", "load")

            messages_data['response_counter'] = data_save['response_chat']
            messages_data['response_set_counter'] = data_save['response_set_chat']

            counter_data['redeem'] = data_save['redeem']
            counter_data['response'] = data_save['response']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/config.json", "save", counter_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/messages/messages_file.json", "save", messages_data)
            

            toast('success')

        except Exception as e:

            utils.error_log(e)
            toast('error')

    elif type_id == "save_counter_commands":

        try:
            
            data_received = json.loads(data_receive)
        
            command_counter_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "load")

            command_counter_data[data_received['type_command']] = {
                "command" : data_received['command'],
                "status" :data_received['status'],
                "delay" : data_received['delay'],
                "last_use": command_counter_data[data_received['type_command']]['last_use'],
                "user_level" : data_received['user_level']
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "save", command_counter_data)

            toast('success')

        except Exception as e:

            utils.error_log(e)
            toast('error')

    elif type_id == "get_counter_commands":
    
        try:

            counter_commands_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "load")
            
            data = {
                "command" : counter_commands_data[data_receive]["command"],
                "status" : counter_commands_data[data_receive]["status"],
                "delay": counter_commands_data[data_receive]["delay"],
                "last_use" : counter_commands_data[data_receive]["last_use"],
                "user_level" : counter_commands_data[data_receive]["user_level"],
            }
            
            return json.dumps(data, ensure_ascii=False)

        except Exception as e:

            utils.error_log(e)
            toast('error')

    elif type_id == "set-counter-value":
        
        with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "w") as counter_file_w:
            counter_file_w.write(str(data_receive))

        aliases = {
            '{value}' : str(data_receive)    
        }

        if utils.send_message("RESPONSE"):
            send(utils.replace_all(utils.messages_file_load('response_set_counter'),aliases))


def queue(type_id, data_receive):

    if type_id == 'get':

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")
        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "load")

        data = {

            "redeem": queue_config_data['redeem'],
            "response" : queue_config_data['response'],
            "response_chat" : utils.messages_file_load('response_queue'),
            "response_add_chat" : utils.messages_file_load('response_add_queue'),
            "queue": queue_data,   
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == 'save_config': 

        try:
            data_save = json.loads(data_receive)

            queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")
            messages_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/messages/messages_file.json", "load")

            messages_data['response_queue'] = data_save['response_chat']
            messages_data['response_add_queue'] = data_save['response_add_chat']

            queue_config_data['redeem'] = data_save['redeem']
            queue_config_data['response'] = data_save['response']

                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "save",queue_config_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/messages/messages_file.json", "save",messages_data)


            toast('success')

        except Exception as e:

            utils.error_log(e)
            toast('error')

    elif type_id == 'queue_add':

        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "load")
        
        if data_receive not in queue_data:
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "save", queue_data)
            
            toast('Nome adicionado')

            aliases = {
                '{value}' : str(data_receive)
            }

            if utils.send_message("RESPONSE"):
                send(utils.replace_all(str(utils.messages_file_load('response_add_queue')), aliases))

            return json.dumps(queue_data, ensure_ascii=False)

        else:
            
            toast('O nome já está na lista') 

            aliases = {
                '{value}' : str(data_receive)
            }

            if utils.send_message("RESPONSE"):
                send(utils.replace_all(str(utils.messages_file_load('response_namein_queue')), aliases))
            
            return json.dumps(queue_data, ensure_ascii=False)

    elif type_id == 'queue_rem':

        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "load")
        
        if data_receive in queue_data:
        
            queue_data.remove(data_receive)
        
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "save", queue_data)
        
            toast('Nome removido')

            aliases = {
                '{value}' : str(data_receive)
            }

            if utils.send_message("RESPONSE"):
                send(utils.replace_all(str(utils.messages_file_load('response_rem_queue')), aliases) )

            return json.dumps(queue_data, ensure_ascii=False)
        
        else:
            
            toast('O nome não está na lista') 

            aliases = {
                '{value}' : str(data_receive)
            }

            if utils.send_message("RESPONSE"):
                send(utils.replace_all(str(utils.messages_file_load('response_noname_queue')), aliases) )
                
            return json.dumps(queue_data, ensure_ascii=False)

    elif type_id == 'get_commands':

        try:

            command_queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "load")
        
            data = {
                "command" : command_queue_data[data_receive]["command"],
                "status" : command_queue_data[data_receive]["status"],
                "delay": command_queue_data[data_receive]["delay"],
                "last_use" : command_queue_data[data_receive]["last_use"],
                "user_level" : command_queue_data[data_receive]["user_level"],
            }

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:

            utils.error_log(e)
            toast('error')

    elif type_id == 'save_commands':

        data_received = json.loads(data_receive)

        try:
            
            command_queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "load")

            command_queue_data[data_received['type_command']] = {
                "command" : data_received['command'],
                "status" :data_received['status'],
                "delay" : data_received['delay'],
                "last_use": command_queue_data[data_received['type_command']]['last_use'],
                "user_level" : data_received['user_level']
            }
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "save",command_queue_data)

            toast('success')

        except Exception as e:

            utils.error_log(e)
            toast('error')


def obs_config_py(type_id,data_receive):
    
    if type_id == "get":
        
        obs_conn_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/obs.json", "load")
        
        data = {
            "host": obs_conn_data['OBS_HOST'],
            "port": obs_conn_data['OBS_PORT'],
            "password": obs_conn_data['OBS_PASSWORD'],
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "get_not":
        
        obs_not_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/notfic.json", "load")
        
        data = {
            'html_player_active': obs_not_data['HTML_PLAYER_ACTIVE'],
            'html_emote_active': obs_not_data['HTML_EMOTE_ACTIVE'],
            'html_redem_active': obs_not_data['HTML_REDEEM_ACTIVE'],
            'html_redeem_time': obs_not_data['HTML_REDEEM_TIME'],
            'html_music_time': obs_not_data['HTML_MUSIC_TIME'],
            'emote_px' : obs_not_data['EMOTE_PX'],
        }


        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save_conn":

        try:
            
            data = json.loads(data_receive)

            data_save = {
                'OBS_HOST': data['host'],
                'OBS_PORT': data['port'],
                'OBS_PASSWORD': data['pass']
            }
        
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/obs.json", "save", data_save)
        
            toast('success')

        except Exception as e:

            utils.error_log(e)
            toast('error')
            
    elif type_id == "save_not":
        
        try:
            data = json.loads(data_receive)

            data_save = {
                'HTML_PLAYER_ACTIVE': data['not_music'],
                'HTML_EMOTE_ACTIVE': data['not_emote'],
                'HTML_REDEEM_ACTIVE': data['not_redeem'],
                'HTML_REDEEM_TIME': int(data['time_showing_not']),
                'HTML_MUSIC_TIME': int(data['time_showing_music']),
                'EMOTE_PX' : data['emote_px'],
            }
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/notfic.json", "save", data_save)
        
            toast('success')

        except Exception as e:

            utils.error_log(e)
            toast('error')


def create_source(type_id):
        
    if type_id == 'redeem':

        try:

            obs_events.create_source('redeem')

        except Exception as e:
            
            if '601' in str(e):

                utils.error_log(e)
                toast('A cena já foi criada no Obs Studio.')

    elif type_id == 'music':

        try:

            obs_events.create_source('music')

        except Exception as e:
            
            if '601' in str(e):

                utils.error_log(e)
                toast('A cena já foi criada no Obs Studio.')

    elif type_id == 'video':

        try:

            obs_events.create_source('video')

        except Exception as e:
            
            if '601' in str(e):

                utils.error_log(e)
                toast('A cena já foi criada no Obs Studio.')

    elif type_id == 'highlight':

        try:

            obs_events.create_source('highlight')

        except Exception as e:
            
            if '601' in str(e):

                utils.error_log(e)
                toast('A cena já foi criada no Obs Studio.')

    elif type_id == 'emote':

        try:

            obs_events.create_source('emote')

        except Exception as e:
            
            if '601' in str(e):

                utils.error_log(e)
                toast('A cena já foi criada no Obs Studio.')


def not_config_py(data_receive,type_id,type_not):
    
    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")
        
    if type_id == "get":   
         
        data = {
            'not': event_config_data[type_not]['status'],
            'response_chat': event_config_data[type_not]['response_chat'],
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save":
        
        try:

            data = json.loads(data_receive)
            
            event_config_data[type_not]['status'] = data['not']
            event_config_data[type_not]['response_chat'] = data['response_chat']
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "save",event_config_data )
                
            toast('success')
            
        except Exception as e:

            utils.error_log(e)
            toast('error')
    
        
def messages_config(type_id,data_receive):

    message_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands_config.json", "load")
     
    if type_id == "get":

        messages_data_get = {
            "STATUS_TTS": message_data['STATUS_TTS'],
            "STATUS_COMMANDS": message_data['STATUS_COMMANDS'],
            "STATUS_RESPONSE": message_data['STATUS_RESPONSE'],
            "STATUS_ERROR_TIME": message_data['STATUS_ERROR_TIME'],
            "STATUS_CLIP": message_data['STATUS_CLIP'],
            "STATUS_ERROR_USER": message_data['STATUS_ERROR_USER'],
            "STATUS_MUSIC": message_data['STATUS_MUSIC'],
            "STATUS_MUSIC_CONFIRM": message_data['STATUS_MUSIC_CONFIRM'],
            "STATUS_MUSIC_ERROR": message_data['STATUS_MUSIC_ERROR']
        }

        return json.dumps(messages_data_get, ensure_ascii=False)
    
    elif type_id == "save":

        try:

            data = json.loads(data_receive)

            message_data['STATUS_TTS'] = data['status_tts']
            message_data['STATUS_COMMANDS'] = data['status_commands']
            message_data['STATUS_RESPONSE'] = data['status_response']
            message_data['STATUS_ERROR_TIME'] = data['status_delay']
            message_data['STATUS_CLIP'] = data['status_clip']
            message_data['STATUS_ERROR_USER'] = data['status_permission']
            message_data['STATUS_MUSIC'] = data['status_next']
            message_data['STATUS_MUSIC_CONFIRM'] = data['status_music']
            message_data['STATUS_MUSIC_ERROR'] = data['status_error_music']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands_config.json", "save", message_data)

            toast('success')

        except Exception as e:

            utils.error_log(e)

            toast('error')


def responses_config(fun_id, response_key, message):

    responses_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/messages/messages_file.json", "load")

    if fun_id == 'get_response':

        return responses_data[response_key]

    elif fun_id == 'save_response':

        try:
            responses_data[response_key] = message

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/messages/messages_file.json", "save",responses_data )

            toast('success')

        except Exception as e:

            toast('error')
            utils.error_log(e)


def discord_config(data_discord_save, mode,type_id):
       
    ignore_list = [
        'clips_create',
        'clips_edit',
    ]
    
    discord_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "load")
    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")
    
    if mode == 'save':

        try:

            data_receive = json.loads(data_discord_save)
            
            url_webhook = data_receive['webhook_url']
            embed_color = data_receive['embed_color']
            embed_content = data_receive['embed_content']
            embed_title = data_receive['embed_title']
            embed_description = data_receive['embed_description']
            status = data_receive['webhook_status']
            
            
            discord_data[type_id] = {
                'url' : url_webhook,
                'status' : status,
                'color' : embed_color,
                'content' : embed_content,
                'title' : embed_title,
                'description' : embed_description
            }

            if type_id not in ignore_list:
                event_config_data[type_id]['status'] = data_receive['not']
                event_config_data[type_id]['response_chat'] = data_receive['response_chat']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "save",event_config_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "save",discord_data)
            
            toast('success')

        except Exception as e:

            toast('error')
            utils.error_log(e)

    elif mode == 'get':

        url_webhook = discord_data[type_id]['url']
        embed_content = discord_data[type_id]['content']
        embed_title = discord_data[type_id]['title']
        embed_description = discord_data[type_id]['description']
        embed_color = discord_data[type_id]['color']
        status = discord_data[type_id]['status']

        if type_id in ignore_list:
            notifc = '' 
            response_chat = ''
        else:
            file_data = event_config_data[type_id]
            notifc = file_data['status']
            response_chat = file_data['response_chat']  

        data_get = {
            "url_webhook" : url_webhook,
            "embed_content" : embed_content,
            "embed_color": embed_color,
            "embed_title": embed_title,
            "embed_description": embed_description,
            "status": status,
            'not': notifc,
            'response_chat': response_chat,
        }

        return json.dumps(data_get, ensure_ascii=False)

    elif mode == 'save-profile':

        
        data_receive = json.loads(data_discord_save)

        discord_data['profile_status'] = data_receive['webhook_profile_status']
        discord_data['profile_image'] = data_receive['webhook_profile_image_url']
        discord_data['profile_name'] = data_receive['webhook_profile_name']

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json", "save",discord_data)
            
    elif mode == 'get-profile':

        data_get = {
            "webhook_profile_status" : discord_data['profile_status'],
            "webhook_profile_image_url" : discord_data['profile_image'],
            "webhook_profile_name": discord_data['profile_name']
        }

        return json.dumps(data_get, ensure_ascii=False)


def disclosure_py(type_id,data_receive):
    
    disclosure_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/disclosure.json", "load")
            
    if type_id == "save":

        disclosure_data['message'] = data_receive
    
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/disclosure.json", "save", disclosure_data)
        
    elif type_id == "get":

        if disclosure_data['message'] == "":
            
            disclosure = 'Digite aqui a sua mensagem rápida de divulgação em chats'
            
        else:
            
            disclosure = disclosure_data['message']
            
        return disclosure


def get_video_info(title):

    def removestring(value):
        try:
            simbolos = [['[', ']'], ['(', ')'], ['"', '"']]
            for simbolo in simbolos:
                if value.find(simbolo[0]) and value.find(simbolo[1]):
                    value = value.replace(value[(indice := value.find(simbolo[0])):value.find(simbolo[1], indice + 1) + 1],'').strip()
            return value
        except:
            return value
    
    ydl_opts = {'skip_download': True, 'quiet': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        if validators.url(title):
            video_info = ydl.extract_info(title, download=False)
        else:
            video_info = ydl.extract_info(f"ytsearch:{title}", download=False)['entries'][0]
            
        video_id = video_info.get("id", None)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_title = video_info.get('title', None)
        video_length = video_info.get('duration', None)
        video_thumb = video_info.get('thumbnail', None)

        data = {
            "url" : video_url,
            "title"  : removestring(video_title),
            "thumb" : video_thumb,
            "length" : video_length
        }
        
        return namedtuple('result', data.keys())(*data.values())


def playlist_py(type_id,data):
    
    def start_add(playlist_url):

        try:
            playlist_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "load")

            check_have = any(playlist_data.keys())

            if not check_have:
                last_key = 0
            else:
                playlist_keys = [int(x) for x in playlist_data.keys()]
                last_key = max(playlist_keys)

            def cli_to_api(*opts):
                default = yt_dlp.parse_options([]).ydl_opts
                diff = {k: v for k, v in yt_dlp.parse_options(opts).ydl_opts.items() if default[k] != v}
                return diff

            ytdlp_opts = cli_to_api('--flat-playlist','--quiet','--ignore-errors')

            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
                playlist = ydl.extract_info(playlist_url, download=False)

                for video in playlist['entries']:

                    last_key = last_key + 1
                    video_title = video['title']
                    video_url = video['url']

                    playlist_data[last_key] = {"MUSIC": video_url, "USER": "playlist", "MUSIC_NAME": video_title}

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "save", playlist_data)

        except Exception as e:
            utils.error_log(e)

    if type_id == "add":

        def is_youtube_url(string):
            
            youtube_regex = re.compile(r"(http(s)?://)?(www\.)?(youtube\.com/(watch\?v=|playlist\?list=)|youtu\.be/)[^\s]+")

            match = youtube_regex.match(string)

            if match:
                return True
            else:
                return False
            
        if is_youtube_url:

            if re.match(r"https?://(www\.)?youtube\.com/playlist\?list=.*", data):
                
                toast('Adicionando, aguarde')

                threading.Thread(target=start_add, args=(data,), daemon=True).start()

            elif re.match(r"https?://(www\.)?youtube\.com/watch\?v=.*&list=.*", data):

                url = re.sub(r"watch\?v=[^&]*&?", "", data)
                url = url.replace("list=", "playlist?list=")

                toast('Adicionando, aguarde')
                                 
                threading.Thread(target=start_add, args=(url,), daemon=True).start()

            else:
                toast('A url deve ser do youtube e conter uma id de playlist, ex: https://www.youtube.com/watch?v=xxxxxxxxxx&list=xxxxxxxxxxxxxxxxxxxxxxxxxx ou https://www.youtube.com/playlist?list=xxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        else:
            toast('A url deve ser do youtube e conter uma id de playlist, ex: https://www.youtube.com/watch?v=xxxxxxxxxx&list=xxxxxxxxxxxxxxxxxxxxxxxxxx ou https://www.youtube.com/playlist?list=xxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        
    elif type_id == 'save':
        
        playlist_stats_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

        playlist_stats_data['STATUS'] = data

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", playlist_stats_data)
        
        if data:
            toast('Reprodução de playlist ativada')
        else:
            toast('Reprodução de playlist desativada')
   
    elif type_id == 'get':

        playlist_stats_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")
        
        return playlist_stats_data['STATUS']

    elif type_id == 'clear':
   
        playlist_data = {}
        
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "save", playlist_data)

    elif type_id == 'queue':
        
        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "load")

        playlist_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "load")

        list_queue_list = {}
        
        for key in queue_data:
            
            music = queue_data[key]['MUSIC_NAME']
            user = queue_data[key]['USER']

            list_queue_list[music] = user

        for key in playlist_data:
            
            music = playlist_data[key]['MUSIC_NAME']
            user = playlist_data[key]['USER']

            list_queue_list[music] = user

        return json.dumps(list_queue_list, ensure_ascii=False)


def sr_config_py(type_id,data_receive):
    
    if type_id == 'get':
        
        commands_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
        not_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/notfic.json", "load")
        status_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")
        
        data = {
            "allow_music" : status_music_data['STATUS_MUSIC_ENABLE'],
            "max_duration" : status_music_data['max_duration'],
            "skip_votes" : status_music_data['skip_votes'],
            "skip_mod" : status_music_data['skip_mod'],
            "redeem_music" : commands_music_data['redeem'],
            "not_status": not_music_data['HTML_PLAYER_ACTIVE'],
        }

        return json.dumps(data, ensure_ascii=False)
    
    if type_id == 'get_command':
        
        try:
            commands_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
        
            data = {
                'command': commands_music_data[data_receive]['command'],
                'status' : commands_music_data[data_receive]['status'],
                'delay' : commands_music_data[data_receive]['delay'],
                'last_use' : commands_music_data[data_receive]['last_use'],
                'user_level' :commands_music_data[data_receive]['user_level'],
            }

            return json.dumps(data, ensure_ascii=False)
        
        except Exception as e:
            
            utils.error_log(e)
            toast('error')
    
    elif type_id == 'save':
        
        data = json.loads(data_receive)

        try:

            not_status_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/notfic.json", "load")
            commands_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
            status_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")
            
            not_status_music_data['HTML_PLAYER_ACTIVE'] = data['music_not_status_data']
            commands_music_data['redeem'] = data['redeem_music_data']
            
            status_music_data['STATUS_MUSIC_ENABLE'] = data['allow_music_save']
            status_music_data['max_duration'] = data['max_duration']
            status_music_data['skip_votes'] = data['skip_votes']
            status_music_data['skip_mod'] = data['skip_mod']
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/notfic.json", "save", not_status_music_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "save", commands_music_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/config.json", "save", status_music_data)
                    
            toast('success')

        except Exception as e:
            
            utils.error_log(e)
            toast('error')

    elif type_id == 'save_command':

        try:

            data = json.loads(data_receive)
                   
            commands_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
            
            commands_music_data[data['type_command']] = {
                'command': data['command'],
                'status' : data['status'],
                'delay' : data['delay'],
                'last_use' : commands_music_data[data['type_command']]['last_use'],
                'user_level' : data['user_level'],
            }
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", commands_music_data)

            toast('Comando salvo')

        except Exception as e:
            
            utils.error_log(e)
            toast('Ocorreu um erro ao salvar o comando')

    elif type_id == 'get-status':
        
        status_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

        return status_music_data['STATUS_MUSIC_ENABLE']

    elif type_id == 'list_add':

        config_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

        config_music_data["blacklist"].append(data_receive)
        
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/config.json", "save", config_music_data)
        
        toast('Termo ou nome adicionado')
            
    elif type_id == 'list_get':
        
        config_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

        return json.dumps(config_music_data["blacklist"], ensure_ascii=False)
        
    elif type_id == 'list_rem':
        
        config_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

        if data_receive in commands_music_data:
        
            config_music_data["blacklist"].remove(data_receive)
        
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/config.json", "save", config_music_data)
            
            toast('Termo ou nome removido') 
        
        else:
            
            toast('O termo ou nome não está na lista') 


def update_check(type_id):
    
    if type_id == 'check':

        response = req.get("https://api.github.com/repos/GGTEC/RewardEvents/releases/latest")
        response_json = json.loads(response.text)
        version = response_json['tag_name']

        if version != 'v5.9.41':

            return 'true'
        
        else:

            return 'false'

    elif type_id == 'open':

        url = 'https://github.com/GGTEC/RewardEvents/releases'
        webbrowser.open(url, new=0, autoraise=True)


def clip():
    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
    if authdata.TOKEN() and authdata.USERNAME():

        info_clip = twitch_api.create_clip(broadcaster_id=authdata.BROADCASTER_ID())

        if 'error' in info_clip.keys():

            message_clip_error_load = utils.messages_file_load('clip_error_clip')
            
            if utils.send_message("CLIP"):
                send(message_clip_error_load)

            toast('Erro ao criar o clip')

        else:

            clip_id = info_clip['data'][0]['id']

            message_clip_user_load = utils.messages_file_load('clip_create_clip')

            message_clip_user = message_clip_user_load.replace('{username}', authdata.USERNAME())
            message_final = message_clip_user.replace('{clip_id}', clip_id)

            toast({message_final})

            if utils.send_message("CLIP"):
                send(message_final)
                
                data = {
                    'type_id' : 'clips_create',
                    'clip_id': clip_id,
                    'username' : authdata.USERNAME()
                }
                
                
                send_discord_webhook(data)
                
                data = {
                    'type_id' : 'clips_edit',
                    'clip_id': clip_id,
                    'username' : authdata.USERNAME()
                }
                
                send_discord_webhook(data)
    
    else:
        toast("Não autenticado")


def timer():
    
    """
        Modulo para mensagens automaticas.
    """
    
    while True:

        try:
            
            if 'chat' in globals():

                if chat.Connected and loaded_status and streaming:
                                
                    timer_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "load")

                    timer_int = timer_data['TIME']
                    timer_max_int = timer_data['TIME_MAX']

                    next_timer = randint(timer_int, timer_max_int)

                    if utils.send_message('TIMER'):
                        
                        timer_message = timer_data['MESSAGES']
                        last_key = timer_data['LAST']

                        key_value = timer_message.keys()
                        
                        if bool(timer_message):
                            
                            message_key = random.choice(list(key_value))

                            if len(timer_message) > 1:
                                
                                if message_key == last_key:
                                    
                                    time.sleep(1)
                                    
                                else:

                                    timer_data['LAST'] = message_key

                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/timer.json", "save",timer_data)

                                    if timer_message[message_key]['type_timer'] == 0:
                                        send(timer_message[message_key]['message'])
                                    
                                    elif timer_message[message_key]['type_timer']:
                                        send_announcement(timer_message[message_key]['message'],timer_message[message_key]['color'])

                                    time.sleep(next_timer)
                            else:

                                if timer_message[message_key]['type_timer'] == 0:
                                    send(timer_message[message_key]['message'])
                                
                                elif timer_message[message_key]['type_timer']:
                                    send_announcement(timer_message[message_key]['message'],timer_message[message_key]['color'])

                                time.sleep(next_timer)

                        else:
                            
                            time.sleep(1)

                    else:
                        
                        time.sleep(10)

        except Exception as e:
            
            utils.error_log(e)
            
            time.sleep(5)
            
        time.sleep(1)


def get_users_info(type_id, user_id):

    os.makedirs(f"{utils.local_work('appdata_path')}/user_info", exist_ok=True)

    def compare_dictionaries(received, saved):

        items_not_received = {}

        for key, value in saved.items():
            if key not in received or received[key] != value:
                items_not_received[key] = value

        return items_not_received

    if type_id == 'save':

        try:
            
            authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    
            if authdata.TOKEN() and authdata.USERNAME():
                
                mod_dict = {}

                mod_info_url = f'https://api.twitch.tv/helix/moderation/moderators?broadcaster_id={authdata.BROADCASTER_ID()}&first=100'

                headers = {
                    "Authorization": f"Bearer {authdata.TOKEN()}",
                    "Client-Id": os.getenv('CLIENTID'),
                    "Content-Type": "application/json"
                }

                mod_info_response = req.get(mod_info_url, headers=headers)

                if mod_info_response.status_code == 200:

                    mod_info = json.loads(mod_info_response.content)

                    for index in range(len(mod_info['data'])):
                        user_id = mod_info['data'][index]['user_id']
                        user_name = mod_info['data'][index]['user_name']
                        mod_dict[user_id] = user_name

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/mods.json", "save",mod_dict)


                sub_dict_saved = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/subs.json", "load")

                sub_dict_rec = {}

                sub_info_url = f'https://api.twitch.tv/helix/subscriptions?broadcaster_id={authdata.BROADCASTER_ID()}&first=100'

                headers = {
                    "Authorization": f"Bearer {authdata.TOKEN()}",
                    "Client-Id": os.getenv('CLIENTID'),
                    "Content-Type": "application/json"
                }

                sub_info_response = req.get(sub_info_url, headers=headers)

                if sub_info_response.status_code == 200:

                    sub_info = json.loads(sub_info_response.content)

                    for index in range(len(sub_info['data'])):
                        user_id = sub_info['data'][index]['user_id']
                        user_name = sub_info['data'][index]['user_name']

                        sub_dict_rec[user_id] = user_name

                    dict_compare = compare_dictionaries(sub_dict_rec,sub_dict_saved)
                    
                    if dict_compare:

                        for key, value in dict_compare.items():

                            aliases = {
                                '{username}' : value
                            }

                            data_append = {
                                "type" : "event",
                                "message" : utils.replace_all(str(utils.messages_file_load('event_subend')), aliases),
                                "user_input" : '',
                            }
                            
                            append_notice(data_append)

                        
                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/subs.json", "save", sub_dict_rec)



                return True
            
            else:
                
                return True
        
        except Exception as e:
            
            utils.error_log(e)

            return True

    elif type_id == 'get_sub':

        subs_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/subs.json", "load")

        if 'user_id' in subs_data.keys():
            return True
        else:
            return False

    elif type_id == 'get_mod':

        mod_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/mods.json", "load")

        if 'user_id' in mod_data.keys():
            return True
        else:
            return False


def start_play(link, user):

    global caching

    music_dir_check = os.path.exists(f"{utils.local_work('data_dir')}/web/src/player/cache/music.webm")

    if music_dir_check:

        os.remove(f"{utils.local_work('data_dir')}/web/src/player/cache/music.webm")

    def download_music(link):

        def my_hook(d):
            if d['status'] == 'finished':
                toast('Download concluido, Em pós processamento')

        try:

            
            ydl_opts = {
                'progress_hooks': [my_hook],
                'final_ext': 'webm',
                'format': 'bestaudio',
                'noplaylist': True,
                'quiet': True,
                'no_color': True,
                'outtmpl': f"{utils.local_work('data_dir')}/web/src/player/cache/music.%(ext)s",
                'force-write-archive': True,
                'force-overwrites': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            return True

        except Exception as e:
            
            utils.error_log(e)
            
            return False

    try:

        response = get_video_info(link)

        media_name = response.title
        music_link = response.url
        music_thumb = response.thumb

        title_split = media_name.split(' - ')

        if len(title_split) > 1:
            music_name = title_split[0]
            music_artist = title_split[1]
        else:
            music_name = media_name
            music_artist = ''

        img_data = req.get(music_thumb).content
        
        with open(f"{utils.local_work('data_dir')}/web/src/player/images/album.png", 'wb') as album_art_local:
            album_art_local.write(img_data)

        with open(f"{utils.local_work('appdata_path')}/player/images/album.png", 'wb') as album_art_file:
            album_art_file.write(img_data)

        window.evaluate_js(f"update_image()")

        caching = True

        if download_music(music_link):

            with open(f"{utils.local_work('appdata_path')}/player/list_files/currentsong.txt", "w", encoding="utf-8") as file_object:
                file_object.write(f"{media_name}")

            music_name_short = textwrap.shorten(media_name, width=13, placeholder="...")

            redeem_data = {
                "redeem_user": user,
                "music" : media_name,
                "artist" : music_artist,
            }
            
            data = {
                'type' : 'music',
                'html' : utils.update_music(redeem_data)
            }

            data_dump = json.dumps(data)

            sk.broadcast_message(data_dump)

            window.evaluate_js(f"update_music_name('{music_name}', '{music_artist}')")

            aliases = {
                '{music_name}': music_name,
                '{music_name_short}': music_name_short,
                '{music_artist}': music_artist,
                '{username}': user
            }

            message_replace = utils.replace_all(utils.messages_file_load('music_playing'), aliases)
            if utils.send_message("STATUS_MUSIC"):
                send(message_replace)

            window.evaluate_js(f"player('play', 'http://localhost:7000/src/player/cache/music.webm', '1')")
            toast(f'Reproduzindo {music_name_short} - {music_artist}')
            
                
            config_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")
                
            config_data_player['skip_requests'] = 0
            config_data_player['skip_users'] = []

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", config_data_player)
            

            caching = False

        else:

            caching = False
            toast(f'Erro ao processar musica {link} - {user}')
            if utils.send_message("STATUS_MUSIC_ERROR"):
                send(utils.messages_file_load('music_process_cache_error'))

    except Exception as e:
        
        utils.error_log(e)
        
        toast(f'Erro ao processar musica {link} - {user}')
        if utils.send_message("STATUS_MUSIC_ERROR"):
            send(utils.messages_file_load('music_process_error'))


def loopcheck():

    while True:

        try:
            if loaded_status and chat.Connected:
                
                playlist_execute_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")
                playlist_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "load")
                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "load")
                                 
                playlist_execute_value = playlist_execute_data['STATUS']
                playlist_execute = int(playlist_execute_value)
                
                check_have_playlist = any(playlist_data.keys())
                check_have_queue = any(queue_data.keys())

                playing = window.evaluate_js(f"player('playing', 'none', 'none')")
                
                if not caching and playing == 'False':
                    
                    if check_have_queue:

                        queue_keys = [int(x) for x in queue_data.keys()]
                        music_data_key = str(min(queue_keys))

                        music = queue_data[music_data_key]['MUSIC']
                        user = queue_data[music_data_key]['USER']

                        del queue_data[music_data_key]

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "save",queue_data)
                        
                        start_play(music, user)

                        time.sleep(5)

                    elif check_have_playlist:

                        if playlist_execute:

                            playlist_keys = [int(x) for x in playlist_data.keys()]
                            music_data = str(min(playlist_keys))

                            music = playlist_data[music_data]['MUSIC']
                            user = playlist_data[music_data]['USER']

                            del playlist_data[music_data]
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "save",playlist_data)

                            start_play(music, user)


                        else:
                            time.sleep(3)
                    else:
                        time.sleep(3)
                        window.evaluate_js(f"update_music_name('Aguardando', 'Aguardando')")
                        
                time.sleep(3)
        except:
            time.sleep(3)


def process_redem_music(user_input, redem_by_user):

    user_input = user_input.strip()
    
    toast(f'Processando pedido {user_input} - {redem_by_user}...')
        
    config_music_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")
    queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "load")

    blacklist = config_music_data['blacklist']
    max_duration = int(config_music_data['max_duration'])

    if not any(queue_data.keys()):
        last_key = 1
    else:
        last_key = str(max(map(int, queue_data.keys()), default=0) + 1)

    def start_process(user_input):

        try:
            
            if not any(item in user_input for item in blacklist):
                
                response = get_video_info(user_input)

                music_name = response.title
                video_url = response.url
                music_leght = response.length

                if int(music_leght) < int(max_duration):

                    queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "load")

                    queue_data[last_key] = {"MUSIC": video_url, "USER": redem_by_user, "MUSIC_NAME": music_name}

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "save", queue_data)
                    
                    aliases = {'{username}': redem_by_user, '{user_input}': video_url, '{music}': music_name}
                    
                    if utils.send_message("STATUS_MUSIC_CONFIRM"):
                        send(utils.replace_all(utils.messages_file_load('music_added_to_queue'), aliases))

                else:

                    aliases = {
                        '{max_duration}' : str(max_duration),
                        '{username}': str(redem_by_user),
                        '{user_input}': str(user_input),
                        '{music}': str(music_name),
                        '{music_short}': str(textwrap.shorten(music_name, width=18, placeholder="..."))
                    }

                    if utils.send_message("STATUS_MUSIC_ERROR"):
                        send(utils.replace_all(utils.messages_file_load('music_leght_error'), aliases))
            
            else:
                
                music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                aliases = {
                    '{username}': str(redem_by_user),
                    '{user_input}': str(user_input),
                    '{music}': str(music_name),
                    '{music_short}': str(music_name_short)
                }

                if utils.send_message("STATUS_MUSIC_CONFIRM"):
                    send(utils.replace_all(utils.messages_file_load('music_blacklist'), aliases))
                        
        except Exception as e:
            
            utils.error_log(e)

            aliases = {'{username}': str(redem_by_user), '{user_input}': str(user_input)}

            if utils.send_message("STATUS_MUSIC_ERROR"):
                send(utils.replace_all(utils.messages_file_load('music_add_error'), aliases))

    def convert_address(original_address):

        pattern = r"youtu\.be\/(\w+)\?.*"
        result = re.match(pattern, original_address)
        
        if result:
            video_code = result.group(1)
            new_address = f"https://www.youtube.com/watch?v={video_code}"
            return new_address
        else:
            return original_address
    
    if validators.url(user_input):
        
        find_youtube = user_input.find('youtube')
        find_youtu = user_input.find('youtu')

        if find_youtube != -1 or find_youtu != -1:

            start_process(convert_address(user_input))

        else:
            
            if utils.send_message("STATUS_MUSIC_CONFIRM"):
                send(utils.messages_file_load('music_link_youtube'))
    else:     

        start_process(user_input)


def receive_redeem(data_rewards, received_type):
    
    with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "r",  encoding='utf-8') as counter_file_r:
        counter_file_r.seek(0)
        digit = counter_file_r.read()
        counter_actual = int(digit)

    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
    path = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pathfiles.json", "load")
    player_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
    giveaway_path = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/config.json", "load")
    giveaway_commands = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "load")
    counter_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/config.json", "load")
    queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")
    queue_command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "load")
        
    counter_redeem = counter_data['redeem']
    giveaway_redeem = giveaway_path['redeem']
    command_giveaway = giveaway_commands['add_user']['command']
    player_reward = player_data['redeem']
    command_player = player_data['request']['command']
    queue_redeem = queue_data['redeem']
    command_queue = queue_command_data['add_queue']['command']

    redeem_reward_name = '0'
    redeem_by_user = '0'
    user_input = '0'
    user_level = '0'
    user_id_command = '0'
    command_receive = '0'
    prefix = '0'

    if authdata.TOKEN() and authdata.USERNAME():
                
        if received_type == 'redeem':

            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
            
            redeem_reward_name = data_rewards['reward_title']
            redeem_by_user = data_rewards['user_name']
            user_id = data_rewards['user_id']
            user_input = data_rewards['user_input']
            redeem_reward_image = data_rewards['image']

            if redeem_by_user in user_data_load:
                user_level = user_data_load[redeem_by_user]['roles']
            else:
                user_level = ['spec']
        
        elif received_type == 'command':
            
            redeem_reward_name = data_rewards['REDEEM']
            redeem_by_user = data_rewards['USERNAME']
            user_input = data_rewards['USER_INPUT']
            user_level = data_rewards['USER_LEVEL']
            user_id = data_rewards['USER_ID']
            redeem_reward_image = f"http://127.0.0.1:7000/src/defaultreward.png"

            command_receive = data_rewards['COMMAND']
            prefix = data_rewards['PREFIX']

        redeem_data = {
            "redeem_name": redeem_reward_name,
            "redeem_user": redeem_by_user,
            "redeem_image" : redeem_reward_image
        }

        window.evaluate_js(f"update_div_redeem({json.dumps(redeem_data, ensure_ascii=False)})")

        aliases = {
            '{username}': str(redeem_by_user),
            '{reward}' : str(redeem_reward_name),
            '{command}': str(command_receive),
            '{prefix}': str(prefix),
            '{user_level}': str(user_level),
            '{user_id}': str(user_id_command),
            '{user_input}': str(user_input),
            '{counter}': str(counter_actual)
        }

        data = {
            'type' : 'reward',
            'html' : utils.update_notif(redeem_data)
        }
        
        sk.broadcast_message(json.dumps(data))

        def play_sound():

            audio_path = path[redeem_reward_name]['path']
            audio_volume = path[redeem_reward_name]['volume']
            send_response_value = path[redeem_reward_name]['send_response']

            convert_vol = int(audio_volume)/100

            tts_playing = pygame.mixer.music.get_busy()

            while tts_playing:
                tts_playing = pygame.mixer.music.get_busy()
                time.sleep(2)

            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(convert_vol)
            pygame.mixer.music.play()

            if send_response_value:

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(path[redeem_reward_name]['chat_response'], aliases))
        
        def play_video():

            video_path = path[redeem_reward_name]['path']
            send_response_value = path[redeem_reward_name]['send_response']
            time_show = path[redeem_reward_name]['show_time']

            data = {
                'type' : 'video',
                'html' : utils.update_video(video_path,time_show)
            }

            data_dump = json.dumps(data)

            sk.broadcast_message(data_dump)

            if send_response_value:

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(path[redeem_reward_name]['chat_response'], aliases))

        def play_tts():

            characters = path[redeem_reward_name]['characters']
            characters_int = int(characters)
            
            if utils.send_message("STATUS_TTS"):
                if user_input != '':

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

                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('error_tts_no_text'), aliases))
                            
            else:
                    
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('error_tts_disabled'), aliases))
                                        
        def change_scene():

            scene_name = path[redeem_reward_name]['scene_name']
            keep = path[redeem_reward_name]['keep']
            time_show = path[redeem_reward_name]['time']
            send_response_value = path[redeem_reward_name]['send_response']

            if send_response_value:
                
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(path[redeem_reward_name]['chat_response'], aliases))

            obs_events.show_scene(scene_name, time_show, keep)

        def send_message():

            if utils.send_message("RESPONSE"):
                send(utils.replace_all(path[redeem_reward_name]['chat_response'], aliases))

        def toggle_filter():

            source_name = path[redeem_reward_name]['source_name']
            filter_name = path[redeem_reward_name]['filter_name']
            time_show = path[redeem_reward_name]['time']
            keep = path[redeem_reward_name]['keep']

            send_response_value = path[redeem_reward_name]['send_response']

            if send_response_value:

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(path[redeem_reward_name]['chat_response'], aliases))


            obs_events.show_filter(source_name, filter_name, time_show, keep)

        def key_press():

            keyskeyboard = path[redeem_reward_name]
            send_response_value = path[redeem_reward_name]['send_response']

            mode = path[redeem_reward_name]['mode']

            if send_response_value:

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(path[redeem_reward_name]['chat_response'], aliases))


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

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(path[redeem_reward_name]['chat_response'], aliases))

            obs_events.show_source(source_name, time_show, keep)

        def clip():

            info_clip = twitch_api.create_clip(broadcaster_id=authdata.BROADCASTER_ID())

            if 'error' in info_clip.keys():

                message_clip_error_load = utils.messages_file_load('clip_error_clip')

                if utils.send_message("CLIP"):
                    send(message_clip_error_load)

            else:
                
                
                clip_id = info_clip['data'][0]['id']

                message_clip_user_load = utils.messages_file_load('clip_create_clip')

                message_clip_user = message_clip_user_load.replace('{username}', redeem_by_user)
                message_final = message_clip_user.replace('{clip_id}', clip_id)


                if utils.send_message("CLIP"):
                    send(message_final)
                    
                data = {
                    'type_id' : 'clips_create',
                    'clip_id': clip_id,
                    'username' : redeem_by_user
                    
                }
                
                
                send_discord_webhook(data)
                
                data = {
                    'type_id' : 'clips_edit',
                    'clip_id': clip_id,
                    'username' : redeem_by_user
                    
                }
                
                send_discord_webhook(data)

        def add_counter():

            
            send_response_value = counter_data['response']

            with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "r") as counter_file_r:
                if len(counter_file_r.read()) == 0:
                    
                    with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "w") as counter_file_w:
                        countercount = 1 
                        counter_file_w.write(countercount)
                        window.evaluate_js(f"update_counter_value('{countercount}')")

                else:

                    counter_file_r.seek(0)
                    digit = counter_file_r.read()

                    if digit.isdigit():

                        counter = int(digit)
                        countercount = counter + 1

                    else:
                        countercount = 0

                    with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "w") as counter_file_w:
                        counter_file_w.write(str(countercount))
                        window.evaluate_js(f"update_counter_value('{countercount}')")

            if send_response_value:

                aliases = {'{value}' : str(countercount)}

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('response_counter'), aliases))
                        
        def add_giveaway():

            
            data = {
                'new_name' : redeem_by_user,
                'user_level' : user_level
            }

            giveaway_py('add_user', data)

        def add_queue():

            send_response_value = queue_data['response']
                
            queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "load")

            if redeem_by_user not in queue_data:

                queue_data.append(redeem_by_user)
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "save",queue_data)
                
                toast('Nome adicionado')

                if send_response_value:

                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('response_queue'), aliases))

            else:
                
                toast('O nome já está na lista') 

                if send_response_value:

                    aliases = {'{value}' : str(redeem_by_user)}

                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('response_namein_queue'), aliases))

        def highlight():

            data_highlight = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/highlight.json", "load")
            
            status = data_highlight['status']
            color_message = data_highlight['color_message']
            color_username = data_highlight['color_username']
            size = data_highlight['font-size']
            weight = data_highlight['font-weight']
            duration = data_highlight['duration']

            if status and user_input != None:

                data = {
                    "type" : 'HIGH',
                    "username" : redeem_by_user,
                    "user_input" : user_input,
                    "color_message" : color_message,
                    "color_username" : color_username,
                    "size" : size,
                    "weight" : weight,
                    "duration" : duration
                }

                data = {
                    'type' : 'highlight',
                    'html' : utils.update_highlight(data)
                }

                sk.broadcast_message(json.dumps(data))
                
            else:
                
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_value'), aliases))
                        
            
        eventos = {
            'sound': play_sound,
            'video': play_video,
            'scene': change_scene,
            'response': send_message,
            'filter': toggle_filter,
            'keypress': key_press,
            'source': toggle_source,
            'clip': clip,
            'tts': play_tts,
            'counter': add_counter,
            'giveaway': add_giveaway,
            'queue' : add_queue,
            'highlight' : highlight
        }

        if received_type == 'redeem':

            data_append = {
                "type" : "redeem",
                "message" : utils.replace_all(str(utils.messages_file_load('event_redeem')), aliases),
                "user_input" : user_input,
            }

            append_notice(data_append)
        
            if redeem_reward_name in path.keys():
                redeem_type = path[redeem_reward_name]['type']
                if redeem_type in eventos:
                    eventos[redeem_type]()
                    
            elif redeem_reward_name == giveaway_redeem:
                add_giveaway()
                
            elif redeem_reward_name == player_reward:
                
                status_music = sr_config_py('get-status','null')
                
                if status_music:

                    threading.Thread(target=process_redem_music, args=(user_input, redeem_by_user,), daemon=True).start()
                    
                else:
                    
                    aliases_commands = {'{username}': str(redeem_by_user)}

                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('music_disabled'), aliases_commands))
                        
            elif redeem_reward_name == counter_redeem:
                add_counter()
                
            elif redeem_reward_name == queue_redeem:
                add_queue()

        if received_type == 'command':

            if redeem_reward_name in path.keys():
                
                redeem_type = path[redeem_reward_name]['type']
                if redeem_type in eventos:
                    eventos[redeem_type]()
                    
            if command_receive == command_player:

                status_music = sr_config_py('get-status','null')
                
                if status_music:

                    threading.Thread(target=process_redem_music, args=(user_input, redeem_by_user,), daemon=True).start()
                    
                else:

                    aliases_commands = {'{username}': str(redeem_by_user)}
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('music_disabled'), aliases_commands))
                        
            if command_receive == command_queue:
                add_queue()
                
            if command_receive == command_giveaway:
                add_giveaway()


def highlight_py(type_id,data):

    if type_id == 'get':

        data_highlight = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/highlight.json", "load")
        
        status = data_highlight['status']
        color_message = data_highlight['color_message']
        color_username = data_highlight['color_username']
        size = data_highlight['font-size']
        weight = data_highlight['font-weight']
        duration = data_highlight['duration']

        data = {
            'status' : status,
            'color_message' : color_message,
            'color_username' : color_username,
            'font_size' : size,
            'font_weight' : weight,
            'duration' : duration,
        }
        
        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == 'save':

        data_received = json.loads(data)

        try:
            
            data_highlight = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/highlight.json", "load")

            data_highlight['status'] = data_received['status']
            data_highlight['color_message'] = data_received['color_message']
            data_highlight['color_username'] = data_received['color_username']
            data_highlight['font-size'] = data_received['font_size']
            data_highlight['font-weight'] = data_received['font_weight']
            data_highlight['durationt'] = data_received['duration']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/highlight.json", "save", data_highlight)
            
            toast('Salvo!')  

        except Exception as e:

            utils.error_log(e)
            toast('error')  

    elif type_id == 'create-source':

        try:
            obs_events.create_source('highlight')

        except Exception as e:
            
            if '601' in str(e):

                utils.error_log(e)
                toast('A cena já foi criada no Obs Studio.')


def open_py(type_id,link_profile):
 
    if type_id == "user":
        webbrowser.open('https://www.twitch.tv/'+link_profile, new=0, autoraise=True)

    if type_id == "link":
        webbrowser.open(link_profile, new=0, autoraise=True)

    elif type_id == "appdata":

        try:
            subprocess.Popen(f"explorer '{utils.local_work('appdata_path')}\\rewardevents\\web'")
        except subprocess.CalledProcessError as e:
            utils.error_log(e)
            toast('Ocorreu um erro.')

    elif type_id == "errolog":

        with open(f"{utils.local_work('appdata_path')}/error_log.txt", 'r', encoding='utf-8') as error_file:
            error_data = error_file.read()

        return error_data

    elif type_id == "errolog_clear":
        
        with open(f"{utils.local_work('appdata_path')}/error_log.txt", 'w', encoding='utf-8') as error_file:
            error_file.write('')

        toast('Relatório de erros limpo')
    
    elif type_id == "discord":
        webbrowser.open('https://discord.io/ggtec', new=0, autoraise=True)
    
    elif type_id == "wiki":
        webbrowser.open('https://ggtec.netlify.app/apps/re/', new=0, autoraise=True)

    elif type_id == "debug-get":

        debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/scopes.json", "load")

        return debug_data['debug']
    
    elif type_id == "debug-save":

        debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/scopes.json", "load")
        
        if link_profile: 
            
            debug_data['debug'] = True
            toast(f'Configuração salva, reinicie o programa para iniciar no modo Debug Visual...')
            
        elif link_profile == 0: 
            
            debug_data['debug'] = False
            toast(f'Configuração salva, reinicie o programa para sair do modo Debug Visual...')

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/scopes.json", "save", debug_data)


def chat_config(data_save,type_config):

    chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "load")
    
    if type_config == 'save':

        data_received = json.loads(data_save)
        
        chat_data["appply-colors"] = data_received["appply_colors"]
        chat_data["appply-no-colors"] = data_received["appply_no_colors"]
        chat_data["data-show"] = data_received["data_show"]
        chat_data["type-data"] = data_received["type_data"]
        chat_data["time-format"] = data_received["time_format"]
        chat_data["color-apply"] = data_received["color_apply"]
        chat_data["block-color"] = data_received["chat_colors_block"]
        chat_data["font-size"] = data_received["font_size"]
        chat_data["show-badges"] = data_received["show_badges"]
        chat_data["wrapp-message"] = data_received["wrapp_message"]
        chat_data["not-user-sound"] = data_received["not_user_sound"]
        chat_data["not-sound-path"] = data_received["not_sound_path"]
        chat_data["send-greetings"] = data_received["greetings_join"]
        chat_data["greetings"] = data_received["greetings"]
        chat_data['top_chatter_min'] = data_received['top_chatter']
        chat_data['regular_min'] = data_received['regular']
        
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "save",chat_data)
        
        toast('success')  
        
    elif type_config == 'get':

        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "load")
        
        chat_data_return = {
            "appply_colors" : chat_data["appply-colors"],
            "appply_no_colors" : chat_data["appply-no-colors"],
            "color_apply" : chat_data["color-apply"],
            "block_color" : chat_data["block-color"],
            "time_format" : chat_data["time-format"],
            "type_data" : chat_data["type-data"],
            "data_show" : chat_data["data-show"],
            "font_size" : chat_data["font-size"],
            "show_badges" : chat_data["show-badges"],
            "wrapp_message" : chat_data["wrapp-message"],
            "not_user_sound" : chat_data["not-user-sound"],
            "not_sound_path" : chat_data["not-sound-path"],
            "greetings_join" : chat_data["send-greetings"],
            "greetings" : chat_data["greetings"],
            "top_chatter" : chat_data["top_chatter_min"],
            "regular" :  chat_data["regular_min"],
        }

        return json.dumps(chat_data_return, ensure_ascii=False)

    elif type_config == 'list_add':

        if data_save not in chat_data["user_not_display"]:
            
            chat_data["user_not_display"].append(data_save)
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "save",chat_data)
    
            toast('Nome adicionado')
            
    elif type_config == 'list_get':
        
        return json.dumps(chat_data["user_not_display"], ensure_ascii=False)
         
    elif type_config == 'list_rem':
   
        if data_save in chat_data["user_not_display"]:
        
            chat_data["user_not_display"].remove(data_save)
        
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "save",chat_data)

            toast('Nome removido') 
        
        else:
            
            toast('O nome não está na lista') 

    elif type_config == 'list_bot_add':
        
        users_sess_join_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "load")
        userjoin_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_joined.json", "load")
        bot_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/bot_list_add.json", "load")
        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")

        if data_save in userjoin_data_load['spec']:
            userjoin_data_load['spec'].remove(data_save)

        if data_save in users_sess_join_data['spec']:
            users_sess_join_data['spec'].remove(data_save)
            
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "save",users_sess_join_data)
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_joined.json", "save",userjoin_data_load)
        
        if data_save not in bot_data:
            
            bot_data.append(data_save)
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/bot_list_add.json", "save", bot_data)
            
        if data_save in user_data_load:
            
            del user_data_load[data_save]
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save", user_data_load)
            
        toast('Nome adicionado')
            
    elif type_config == 'list_bot_rem':
        
        bot_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/bot_list_add.json", "load")
        
        if data_save in bot_data:
        
            bot_data.remove(data_save)
        
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/bot_list_add.json", "save", bot_data)
            
            toast('Nome removido') 
        
        else:
            
            toast('O nome não está na lista') 
                
    elif type_config == 'list_bot_get':
        
        bot_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/bot_list_add.json", "load")

        return json.dumps(bot_data, ensure_ascii=False)
        
  
def userdata_py(type_id,username):
    
    if type_id == 'get':
        
        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")

        return json.dumps(user_data_load, ensure_ascii=False)
        
    elif type_id == 'load':
        
        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
        
        if username in user_data_load:
            
            display_name = user_data_load[username]['display_name']
            roles = user_data_load[username]['roles']
            chat_freq = user_data_load[username]['chat_freq']
            color = user_data_load[username]['color']
            badges = user_data_load[username]['badges']
            last_join = user_data_load[username]['last_join']
            time_w = user_data_load[username]['time_w']
        
        else:
            
            display_name = username
            roles = 'Null'
            chat_freq = 'Null'
            color = 'Null'
            badges = 'Null'
            last_join = 'Null'
            time_w = 'Null'
            
            
        data = {
            'display_name' : display_name,
            'roles' : roles,
            'chat_freq' : chat_freq,
            'color' : color,
            'badges' : badges,
            'last_join' : last_join,
            'time_w' : time_w,
        }
            
        return namedtuple('result', data.keys())(*data.values())
        
    elif type_id == 'remove':
        
        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
        
        if username in user_data_load:
            
            del user_data_load[username]
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save",user_data_load)
                
            toast('Nome removido')
 
      
def commands_module(data) -> None:

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

    if authdata.TOKEN() and authdata.USERNAME():
        
        def send_error_level(user,user_level, command):
            
            if isinstance(user_level, str):
                result = user_level.strip("[]").replace("'", "")
                user_level = result.split(", ")

            user_level_string = ""

            if len(user_level) == 1:
                user_level_string = user_level[0]
            elif len(user_level) == 2:
                user_level_string = f"{user_level[0]} ou {user_level[1]}"
            else:
                for i in range(len(user_level) - 1):
                    user_level_string += user_level[i] + ", "
                user_level_string += "ou " + user_level[-1]

            aliases = {
                '{username}': str(user),
                '{user_level}' : str(user_level_string),
                '{command}' : str(command)
            }

            message_error_level = utils.replace_all(utils.messages_file_load('error_user_level'),aliases)

            if utils.send_message("ERROR_USER"):
                send(message_error_level)

        def check_perm(user_list, command_list):
            list_1 = set(user_list)
            list_2 = set(command_list)

            if 'mod' in user_list:
                return True
            else:
                if list_1.intersection(list_2):
                    return True
                else:
                    return False

        def compare_strings(s1, s2):

            if len(s1) > len(s2):

                return False
            for i in range(len(s1)):
                if s1[i] != s2[i]:

                    return False
            return True
        
        message_sender = data['display_name']
        message_sender_id = data['user_id'] 
        
        message_text = data['message_no_url']
        emotes = data['emotes']

        user = message_sender
        user_id_command = message_sender_id

        
        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")   
        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "load")
        command_data_prefix = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands_config.json", "load")
        command_data_simple = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")
        command_data_counter = utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "load")
        command_data_giveaway = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "load")
        command_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "load")
        command_data_duel = utils.manipulate_json(f"{utils.local_work('appdata_path')}/duel/duel.json", "load")
        command_data_default = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "load")
        command_data_queue = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "load")
        
        
        user_type = user_data_load[user.lower()]["roles"]
        command_string = message_text
        command_lower = command_string.lower()

        if len(command_string.split()) > 1:
            split_command = command_string.split(maxsplit=1)
            command ,sufix = split_command
        else:
            sufix = None
        
        command = command_lower.split()[0].strip()
        prefix = command[0]
        result_duel_check = command.startswith(command_data_duel['command'])
        status_commands = command_data_prefix['STATUS_COMMANDS']
        
        random_value = randint(0,100)
        
        aliases = {
            '{username}': str(user),
            '{command}': str(command),
            '{prefix}': str(prefix),
            '{user_level}': str(user_type),
            '{user_id}': str(user_id_command),
            '{sufix}': str(sufix),
            '{random}' : str(random_value),
        }

        if status_commands:
            
            if command in command_data.keys():

                status = command_data[command]['status']
                user_level = command_data[command]['user_level']
                delay = int(command_data[command]['delay'])
                last_use = command_data[command]['last_use']
                
                if check_perm(user_type, user_level):

                    message_delay, check_time, current = utils.check_delay(delay,last_use)

                    if check_time:
                        
                        if status:
                        
                            redeem = command_data[command]['redeem']

                            data_rewards = {'USERNAME': user, 'REDEEM': redeem, 'USER_INPUT': sufix, 'USER_LEVEL': user_type,
                                            'USER_ID': user_id_command, 'COMMAND': command, 'PREFIX': prefix}

                            received_type = 'command'
                            
                            command_data[command]['last_use'] = current
                            
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json", "save",command_data)
                            
                            data_append = {
                                "type" : "command",
                                "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                                "user_input" : sufix,
                            }
                            
                            append_notice(data_append)

                            threading.Thread(target=receive_redeem, args=(data_rewards, received_type,),daemon=True).start()

                        else:
                            
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                    else:

                        if utils.send_message("ERROR_TIME"):
                            send(message_delay)
                else:

                    send_error_level(user,str(user_level), str(command))

            elif command in command_data_simple.keys():

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "r") as counter_file_r:
                    counter_file_r.seek(0)
                    counter = counter_file_r.read()

                response = command_data_simple[command]['response']
                user_level = command_data_simple[command]['user_level']
                delay = command_data_simple[command]['delay']
                last_use = command_data_simple[command]['last_use']
                status = command_data_simple[command]['status']
                counts = command_data_simple[command]['counts']
                

                if check_perm(user_type, user_level):

                    aliases = {
                        '{username}': str(user),
                        '{command}': str(command),
                        '{prefix}': str(prefix),
                        '{user_level}': str(user_type),
                        '{user_id}': str(user_id_command),
                        '{counter}': str(counter),
                        '{counts}' : str(counts),
                        '{sufix}': str(sufix),
                        '{random}' : str(random_value),
                    }

                    if status:
                        
                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                            
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(str(response), aliases))

                            counts =+ 1
                            command_data_simple[command]['last_use'] = current
                            command_data_simple[command]['counts'] = counts
                            

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "save", command_data_simple)
                            
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    else:
                        
                        if utils.send_message("RESPONSE"):
                            send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                            
                else:

                    send_error_level(user,str(user_level), str(command))

            elif compare_strings(command,command_data_counter['reset_counter']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)
                
                status = command_data_counter['reset_counter']['status']
                user_level = command_data_counter['reset_counter']['user_level']
                delay = command_data_counter['reset_counter']['delay']
                last_use = command_data_counter['reset_counter']['last_use']
                
                if status:

                    if check_perm(user_type,user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)
                        
                        if check_time:

                            with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "w") as counter_file_w:
                                counter_file_w.write('0')

                            if utils.send_message("RESPONSE"):
                                send(utils.messages_file_load('response_reset_counter'))
                                
                            command_data_counter['reset_counter']['last_use'] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "save", command_data_counter)

                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)
                    else:
                        send_error_level(user,user_level, str(command))
                
                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_counter['set_counter']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)
            
                status = command_data_counter['set_counter']['status']
                user_level = command_data_counter['set_counter']['user_level']
                delay = command_data_counter['set_counter']['delay']
                last_use = command_data_counter['set_counter']['last_use']
                
                if status:
                    
                    if check_perm(user_type,user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)
                        prefix_counter = command_data_counter['set_counter']['command']

                        if check_time:
                            
                            user_input = command_string.split(prefix_counter.lower())

                            if len(user_input) > 1 and user_input[1] != "":
                                
                                user_input = user_input[1]
                                
                                if user_input.strip().isdigit():

                                    with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "w") as counter_file_w:
                                        counter_file_w.write(str(user_input))

                                    aliases = {"{username}" : str(user)}
                                    
                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('response_set_counter'),aliases))
                                        

                                else:

                                    aliases = {"{username}" : str(user)}

                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('response_not_digit_counter'),aliases))
                                        
                            else:

                                aliases = {"{username}" : str(user)}
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('response_null_set_counter'),aliases))
                            
                                    
                            command_data_counter['set_counter']['last_use'] = current
                        
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "save", command_data_counter)
                                    
                                    
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)
                    
                    else:
                        send_error_level(user,user_level, str(command))
                        
                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                    
            elif compare_strings(command,command_data_counter['check_counter']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)
            
                status = command_data_counter['check_counter']['status']
                user_level = command_data_counter['check_counter']['user_level']
                delay = command_data_counter['check_counter']['delay']
                last_use = command_data_counter['check_counter']['last_use']
                
                if status:

                    if check_perm(user_type,user_level):
                        
                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:

                            with open(f"{utils.local_work('appdata_path')}/counter/counter.txt", "r") as counter_file_r:
                                counter_file_r.seek(0)
                                digit = counter_file_r.read()

                            aliases = {"{username}" : str(user), "{value}" : str(digit)}

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('response_counter'),aliases))
                                
                            command_data_counter['check_counter']['last_use'] = current
                        
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/counter/commands.json", "save", command_data_counter)
                                    
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)

                    else:
                        send_error_level(user,user_level, str(command))
                
                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_giveaway['execute_giveaway']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                status = command_data_giveaway['execute_giveaway']['status']
                user_level = command_data_giveaway['execute_giveaway']['user_level']
                delay = command_data_giveaway['execute_giveaway']['delay']
                last_use = command_data_giveaway['execute_giveaway']['last_use']

                if status:

                    if check_perm(user_type, user_level):
                        
                        message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                        if check_time_global:

                            giveaway_py('execute','null')
                            
                            command_data_giveaway['execute_giveaway']['last_use'] = current
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "save", command_data_giveaway)
                        
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)
                    
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_giveaway['clear_giveaway']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                status = command_data_giveaway['clear_giveaway']['status']
                delay = command_data_giveaway['clear_giveaway']['delay']
                last_use = command_data_giveaway['clear_giveaway']['last_use']
                user_level = command_data_giveaway['clear_giveaway']['user_level']

                if status:

                    if check_perm(user_type, user_level):
                        
                        message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                        if check_time_global:

                            reset_data = []
                            
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "save", reset_data)

                            if utils.send_message("RESPONSE"):
                                send(utils.messages_file_load('giveaway_clear'))
                                
                            command_data_giveaway['clear_giveaway']['last_use'] = current
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "save", command_data_giveaway)

                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)
                    
                    else:

                        send_error_level(user, user_level, str(command))
                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
    
            elif compare_strings(command,command_data_giveaway['check_name']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                status = command_data_giveaway['check_name']['status']
                delay = command_data_giveaway['check_name']['delay']
                last_use = command_data_giveaway['check_name']['last_use']
                user_level = command_data_giveaway['clear_giveaway']['user_level']

                if status:

                    if check_perm(user_type, user_level):
                        
                        message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                        if check_time_global:
                            
                            user_input = command_string.split(command_data_giveaway['check_name']['command'])
                                
                            giveaway_name_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")

                            if len(user_input) > 1 and user_input[1] != "":
                                
                                user_input = user_input[1]
                                
                                if user_input.strip() in giveaway_name_data:

                                    aliases = {"{username}" : str(user), "{value}" : str(user_input)}

                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('response_user_giveaway'),aliases))
                                        
                                else:

                                    aliases = {"{username}" : str(user), "{value}" : str(user_input)}
                                    
                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('response_user_giveaway'),aliases))
                            else: 
                                        
                                aliases = {"{username}" : str(user)}
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('response_check_error_giveaway'),aliases))
                                    
                            giveaway_name_data['check_name']['last_use'] = current
                    
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "save", giveaway_name_data)
                                
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)

                    else:

                        send_error_level(user, user_level, str(command))
                
                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_giveaway['add_user']['command']):
            
                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                status = command_data_giveaway['add_user']['status']
                delay = command_data_giveaway['add_user']['delay']
                last_use = command_data_giveaway['add_user']['last_use']
                user_level = command_data_giveaway['add_user']['user_level']

                if status:

                    if check_perm(user_type, user_level):
                        
                        message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                        if check_time_global:

                            user_input = command_string.split(command_data_giveaway['add_user'])

                            if len(user_input) > 1 and user_input[1] != "":
                                
                                user_input = user_input[1]
                                
                                data = {
                                    'new_name': user_input.strip(),
                                    'user_level' : 'mod'
                                }

                                giveaway_py('add_user',data)
                                
                            else:
                                
                                aliases = {'{username}':user}

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('response_use_error_giveaway'),aliases))
                                    
                            command_data_giveaway['add_user']['last_use'] = current
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "save", command_data_giveaway)
                            
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)

                    else:
                        send_error_level(user, user_level, str(command))

                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_giveaway['check_self_name']['command']):
            
                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)
                
                status = command_data_giveaway['add_user']['status']
                delay = command_data_giveaway['check_self_name']['delay']
                last_use = command_data_giveaway['check_self_name']['last_use']
                user_level = command_data_giveaway['add_user']['user_level']

                if status:

                    if check_perm(user_type, user_level):

                        message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)
                            
                        if check_time_global:
                            
                            giveaway_name_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")

                            if user in giveaway_name_data:
                                
                                aliases = {'{username}':user}

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('response_user_giveaway'),aliases))

                            else:
                                aliases = {'{username}':user}

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('response_no_user_giveaway'),aliases))
                                    
                            command_data_giveaway['check_self_name']['last_use']

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json", "save",command_data_giveaway)
                            
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)

                    else:
                        send_error_level(user, user_level, str(command))

                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                        
            elif compare_strings(command,command_data_player['volume']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_player['volume']['delay']
                last_use = command_data_player['volume']['last_use']
                status = command_data_player['volume']['status']
                user_level = command_data_player['volume']['user_level']
                
                if status:

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:

                            prefix_volume = command_data_player['volume']['command']
                            volume_value_command = command_lower.split(prefix_volume.lower())

                            if len(volume_value_command) > 1 and volume_value_command[1] != "":
                                        
                                volume_value_command = volume_value_command[1]
                                
                                if volume_value_command.strip().isdigit():

                                    volume_value_int = int(volume_value_command)

                                    if volume_value_int in range(0, 101):

                                        volume_value = volume_value_int / 100
                                        
                                        window.evaluate_js(f"player('volume', 'none', {volume_value})")

                                        aliases_commands = {
                                            '{username}': str(user),
                                            '{volume}': str(volume_value_int)
                                        }

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('command_volume_confirm'),aliases_commands))

                                    else:

                                        aliases_commands = {
                                            '{username}': user,
                                            '{volume}': str(volume_value_int)
                                        }

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('command_volume_error'),aliases_commands))

                                else:

                                    if utils.send_message("RESPONSE"):
                                        send(utils.messages_file_load('command_volume_number'))
                                            
                                command_data_player['volume']['last_use'] = current
                                    
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save",command_data_player)
                            
                            else:
                                
                                volume_atual = window.evaluate_js(f"player('get_volume', 'none', 'none')")
                                
                                aliases_commands = {
                                    '{username}': str(user),
                                    '{volume}': str(volume_atual)
                                }

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_volume_response'), aliases_commands))
                                
                                command_data_player['volume']['last_use'] = current
                        
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save",command_data_player)

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                
            elif compare_strings(command,command_data_player['skip']['command']):
                
                config_data_player =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

                skip_votes = int(config_data_player['skip_votes'])
                skip_requests = int(config_data_player['skip_requests'])
                skip_mod = config_data_player['skip_mod']
                skip_users = config_data_player['skip_users']

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_player['skip']['delay']
                last_use = command_data_player['skip']['last_use']
                status = command_data_player['skip']['status']
                user_level = command_data_player['skip']['user_level']
                
                if status:
                    
                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:

                            playing = window.evaluate_js(f"player('playing', 'none', 'none')")

                            if not playing == "False":

                                if  'mod' in user_type and skip_mod:
                                    
                                    window.evaluate_js(f"player('stop', 'none', 'none')")

                                    aliases_commands = {
                                        '{username}': str(user),
                                    }

                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('command_skip_confirm'), aliases_commands))
                                        
                                    command_data_player['skip']['last_use'] = current
                                    config_data_player['skip_requests'] = 0
                                    
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", config_data_player)

                                else:

                                    if not user in skip_users:

                                        skip_requests = int(skip_requests) + 1

                                        aliases_commands = {
                                            '{username}': str(user),
                                            '{votes}' : str(skip_requests),
                                            '{minimum}' : str(skip_votes)
                                        }

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('skip_votes'), aliases_commands))
                                        
                                        
                                        if int(skip_requests) == skip_votes:
                                        
                                            window.evaluate_js(f"player('stop', 'none', 'none')")

                                            aliases_commands = {'{username}': str(user)}

                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('command_skip_confirm'), aliases_commands))
                                                
                                            command_data_player['skip']['last_use'] = current
                                        
                                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)
                                            
                                            config_data_player['skip_requests'] = 0
                                            config_data_player['skip_users'] = []
                                            
                                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", config_data_player)
                                            

                                        else:

                                            skip_users.append(user)
                                            config_data_player['skip_users'] = skip_users
                                            config_data_player['skip_requests'] = int(skip_requests)

                                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", config_data_player)
                                            
                                    else:
                                        
                                        aliases_commands = {'{username}': str(user)}

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('command_skip_inlist'), aliases_commands))
                                            
                                        command_data_player['skip']['last_use'] = current
                                
                                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)
                                            
                            else:

                                aliases_commands = {'{username}': str(user),}
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_skip_noplaying'), aliases_commands))
                                    
                                command_data_player['skip']['last_use'] = current
                                    
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)
                                        
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    else:

                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_player['request']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_player['request']['delay']
                last_use = command_data_player['request']['last_use']
                status = command_data_player['request']['status']
                user_level = command_data_player['request']['user_level']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)
                
                if status:

                    if check_perm(user_type, user_level):

                        if check_time:
                                
                                prefix_sr = command_data_player['request']['command']
                                user_input = command_string.split(prefix_sr)

                                if len(user_input) > 1 and user_input[1] != "":
                                    
                                    user_input = user_input[1]

                                    player_reward = command_data_player['redeem']

                                    data_rewards = {'USERNAME': user, 'REDEEM': player_reward, 'USER_INPUT': user_input,
                                                    'USER_LEVEL': user_type, 'USER_ID': user_id_command, 'COMMAND': command,
                                                    'PREFIX': prefix}

                                    received_type = 'command'

                                    threading.Thread(target=receive_redeem, args=(data_rewards, received_type,), daemon=True).start()
                                    
                                    command_data_player['request']['last_use'] = current
                                        
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)

                                else:

                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('command_sr_error_link'), aliases))
                                    
                                    command_data_player['request']['last_use'] = current
                                        
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_player['atual']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_player['atual']['delay']
                last_use = command_data_player['atual']['last_use']
                status = command_data_player['atual']['status']
                user_level = command_data_player['atual']['user_level']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if status:
                    
                    if check_perm(user_type, user_level):

                        if check_time:
                                
                            f = open(f"{utils.local_work('appdata_path')}/player/list_files/currentsong.txt", "r+", encoding="utf-8")
                            current_song = f.read()

                            aliases_commands = {'{username}': str(user), '{music}': str(current_song)}

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_current_confirm'),aliases_commands))
                                
                            command_data_player['atual']['last_use'] = current
                    
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)

                        else:
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_player['next']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_player['next']['delay']
                last_use = command_data_player['next']['last_use']
                status = command_data_player['next']['status']
                user_level = command_data_player['next']['user_level']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if status:

                    if check_perm(user_type, user_level):

                        if check_time:
                                
                            playlist_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "load")
                            queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "load")

                            check_playlist = any(playlist_data.keys())
                            check_queue = any(queue_data.keys())

                            if check_queue:

                                queue_keys = [int(x) for x in queue_data.keys()]
                                min_key_queue = min(queue_keys)
                                min_key_queue_str = str(min_key_queue)

                                next_song = queue_data[min_key_queue_str]['MUSIC_NAME']
                                resquest_by = queue_data[min_key_queue_str]['USER']

                                aliases_commands = {
                                    '{username}': str(user),
                                    '{music}': str(next_song),
                                    '{request_by}': str(resquest_by)
                                }

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_next_confirm'), aliases_commands))
                                    

                            elif check_playlist:

                                playlist_keys = [int(x) for x in playlist_data.keys()]
                                min_key_playlist = min(playlist_keys)
                                min_key_playlist_str = str(min_key_playlist)

                                next_song = playlist_data[min_key_playlist_str]['MUSIC_NAME']
                                resquest_by = playlist_data[min_key_playlist_str]['USER']

                                aliases_commands = {
                                    '{username}': str(user),
                                    '{music}': str(next_song),
                                    '{request_by}': str(resquest_by)
                                }

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_next_confirm'), aliases_commands))

                            else:

                                aliases_commands = {
                                    '{username}': str(user),
                                }

                                response_replace = utils.replace_all(utils.messages_file_load('command_next_no_music'), aliases_commands)

                                if utils.send_message("RESPONSE"):
                                    send(response_replace)
                                    
                            command_data_player['next']['last_use'] = current
                    
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)

                        else:
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif result_duel_check:

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                user_level = command_data_duel['user_level']
                
                if check_perm(user_type, user_level):
                
                    duel_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/duel/duel.json", "load")
                    
                    def loop_duel():
                        
                        def run_duel():
                        
                            duelo_messages_choice = random.choice(list(duel_data['duel_battle'].keys()))
                            duel_message = duel_data['duel_battle'][duelo_messages_choice]
                            
                            string_time = duel_data['time_to_start']
                            
                            aliases_challenger = {
                                "{challenger}" : duel_data['challenger'],
                                "{challenged}" : duel_data['challenged'],
                                "{time_to_start}" : str(string_time)
                            }

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load("duel_start"), aliases_challenger))
                            
                            duel_title_poll = utils.replace_all(utils.messages_file_load("duel_title"), aliases_challenger)
                            
                            if duel_data['create_pred']:
                                
                                predict_data = twitch_api.create_prediction(authdata.BROADCASTER_ID(),duel_title_poll,[duel_data['challenger'],duel_data['challenged']],duel_data["time_to_start"])
                                
                                pred_id = predict_data['data'][0]['id']

                                challenger_out_id = predict_data['data'][0]['outcomes'][0]['id']
                                challenger_out_title = predict_data['data'][0]['outcomes'][0]['title']
                                
                                challenged_out_id = predict_data['data'][0]['outcomes'][1]['id']
                                challenged_out_title = predict_data['data'][0]['outcomes'][1]['title']
                                
                                pred_data_temp = {
                                    'pred_id' : pred_id,
                                    challenger_out_title : challenger_out_id,
                                    challenged_out_title : challenged_out_id
                                }
                                
                                
                            time.sleep(duel_data["time_to_start"])
                            
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(duel_message["start_mess"], aliases_challenger))
                            
                            time.sleep(duel_data["time_to_message"])

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(duel_message["stage_1"], aliases_challenger))
                            
                            time.sleep(duel_data["time_to_message"])
                            
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(duel_message["stage_2"], aliases_challenger))
                            
                            time.sleep(duel_data["time_to_message"])

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(duel_message["stage_3"], aliases_challenger))
                            
                            time.sleep(duel_data["time_to_message"])
                            

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(duel_message["stage_4"], aliases_challenger))
                            
                            time.sleep(duel_data["time_to_message"])
                            
                            dict_players = {
                                "player_1" : duel_data['challenger'],
                                "player_2" : duel_data['challenged']
                            }
                            
                            item_sorteado = random.choice(list(dict_players.keys()))
                            winner = dict_players[item_sorteado]
                            
                            dict_players.pop(item_sorteado)
                            
                            looser = list(dict_players.values())[0]
                            
                            aliases_winner = {
                                "{challenger}" : duel_data['challenger'],
                                "{challenged}" : duel_data['challenged'],
                                "{winner}" : winner,
                                "{looser}" : looser
                            }
                            

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(duel_message["stage_5"], aliases_winner))
                            
                            
                            if duel_data['create_pred']:
                                twitch_api.end_prediction(authdata.BROADCASTER_ID(),pred_data_temp['pred_id'],PredictionStatus.RESOLVED,pred_data_temp[winner])
                                
                            duel_data['challenged'] = ""
                            duel_data['challenger'] = ""
                            duel_data['accept'] = 0
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/duel/duel.json", "save", duel_data)
                        
                        count = 0
                        
                        duel_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/duel/duel.json", "load")
                        
                        while count < duel_data['time_to_accept']:

                            duel_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/duel/duel.json", "load")
                                
                            if duel_data['accept'] == 0:
                                count = count + 1
                                time.sleep(1)
                                
                            elif duel_data['accept']:
                                break 
                        
                        if count == duel_data['time_to_accept'] and duel_data['accept'] == 0:
                            
                            message_duel_aliases = {
                                '{challenged}' : duel_data["challenged"]
                            }

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('duel_long'),message_duel_aliases))
                            
                            duel_data['challenged'] = ""
                            duel_data['challenger'] = ""
                            
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/duel/duel.json", "save", duel_data)
                                
                        elif duel_data['accept']:
                            run_duel()
                                
                    
                    if command_string.split(command_data_duel['command'])[1] != "":
                        
                        if user != duel_data['challenger']:
                            
                            second_command = command_string.split()[1]
                            
                            if second_command.startswith('@'):
                                second_command = second_command.split('@',0)[0]
                            
                            if second_command != user:
                                
                                if second_command != command_data_duel['command_accept']:
                                    
                                    delay = command_data_duel['delay']
                                    last_use = command_data_duel['last_use']
                                    
                                    message_delay, check_time, current = utils.check_delay_duel(delay,last_use)
                                    
                                    if duel_data['challenger'] == "":
                                        
                                        if check_time:
                                            
                                            challenged = second_command
                                            
                                            duel_data['challenged'] = challenged
                                            duel_data['challenger'] = user
                                            duel_data['last_use'] = current
                                    
                                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/duel/duel.json", "save", duel_data)
                                                
                                            message_duel_aliases = {
                                                '{time}' : str(duel_data['time_to_accept']),
                                                '{username}' : user,
                                                '{challenged}' : challenged,
                                                '{command}' : duel_data['command'],
                                                '{accept}' : duel_data['command_accept']
                                            }
                                            
                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('duel_request'),message_duel_aliases))

                                            threading.Thread(target=loop_duel, args=(),daemon=True).start()
                                            
                                        else:
                                            
                                            aliases = {
                                                '{username}' : user,
                                                '{time}' : message_delay
                                            }
                                            
                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('duel_delay'),aliases))
                                    
                                    elif user != duel_data['challenger']:
                                            
                                        message_duel_aliases = {'{username}' : user}
                                        
                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('duel_already_started'),message_duel_aliases))                                        
                                
                                elif second_command == command_data_duel['command_accept']:
                                    
                                    if duel_data['challenged'] == "":
                                        
                                        message_duel_aliases = {'{username}' : user}

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('no_duel_request'),message_duel_aliases))
                                            
                                    elif user == duel_data['challenged']:
                                    
                                        duel_data['accept'] = 1
                                        
                                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/duel/duel.json", "save", duel_data)
                                            
                                            
                                        message_duel_aliases = {
                                            '{username}' : user,
                                            '{challenger}' : duel_data["challenger"]
                                        }
                                        
                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('duel_accepted'),message_duel_aliases))
                                        
                                    elif user != duel_data['challenged']:
                                        
                                        message_duel_aliases = {'{username}' : user}
                                        
                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('duel_other'),message_duel_aliases))
                                            
                            elif second_command == user:
                                    
                                message_duel_aliases = { '{username}' : user}
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('duel_yorself'),message_duel_aliases))
                                        
                        elif user == duel_data['challenger']:
                            
                            message_duel_aliases = {
                                '{username}' : user
                            }
                            
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('duel_again'),message_duel_aliases))
                                
                    else:
                    
                        message_duel_aliases = {
                            '{username}' : user,
                            '{command}' : duel_data['command'],
                            '{accept}' : duel_data['command_accept']
                        }
                        
                        if utils.send_message("RESPONSE"):
                            send(utils.replace_all(utils.messages_file_load('duel_parm'),message_duel_aliases))
                else:
                    send_error_level(user,user_level, str(command))  

            elif compare_strings(command,command_data_default['cmd']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                data_command = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/simple_commands.json", "load")
            
                delay = command_data_default['cmd']['delay']
                last_use = command_data_default['cmd']['last_use']
                status = command_data_default['cmd']['status']
                user_level = command_data_default['cmd']['user_level']

                if status:

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:      

                            if len(command_lower.split()) >= 2:

                                padrao = r'\((?:[^()]*|\([^()]*\))*\)' 
                                matches = re.findall(padrao, command_string)

                                values = [match[1:-1] for match in matches]

                                type_cmd = command_lower.split()[1]

                                if type_cmd == "add":

                                    if len(values) > 1:

                                        cmd = values[0]
                                        response = values[1]

                                        data = {
                                            "new_command" : cmd,
                                            "new_message" : response,
                                            "new_delay" : 0,
                                            "new_user_level" : "spec",
                                        }

                                        data = json.dumps(data)

                                        if cmd not in data_command:

                                            commands_py("create",data)

                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('cmd_created'),{'{username}' : user}))  
                                                
                                        else:
                                            
                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('cmd_exists'),{'{username}' : user}))  

                                                            
                                    else:

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('cmd_use'),{'{username}' : user})) 
                                
                                elif type_cmd == "edit":

                                    if len(values) > 1:

                                        cmd = values[0]
                                        response = values[1]

                                        if cmd in data_command:

                                            new_delay = data_command[cmd]['delay']
                                            new_user_level = data_command[cmd]['user_level']
                                            new_used_times = data_command[cmd]['counts']

                                            data = {
                                                "old_command" : cmd,
                                                "edit_command" : cmd,
                                                "status_command" : 1,
                                                "edit_message" : response,
                                                "edit_delay" : new_delay,
                                                "edit_user_level" : new_user_level,
                                                "edit_used_times" : new_used_times
                                            }

                                            data = json.dumps(data)

                                            commands_py("edit",data)

                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('cmd_edited'),{'{username}' : user}))  
                                        
                                        else:

                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('cmd_not_exists'),{'{username}' : user})) 

                                    else:

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('cmd_use'),{'{username}' : user})) 

                                elif type_cmd == "remove":

                                    if len(values) > 0:

                                        cmd = values[0]

                                        if cmd in data_command:
                                            
                                            commands_py("delete",cmd)

                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('cmd_removed'),{'{username}' : user}))  
                                        
                                        else:
                                            
                                            if utils.send_message("RESPONSE"):
                                                send(utils.replace_all(utils.messages_file_load('cmd_not_exists'),{'{username}' : user})) 

                                    else:

                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('cmd_use'),{'{username}' : user})) 

                                elif type_cmd != "add" or type_cmd != "edit" or type_cmd != "remove":

                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('cmd_use'),{'{username}' : user})) 


                            else:

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('cmd_use'),{'{username}' : user})) 


                            command_data_default['cmd']['last_use'] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)
                                
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    else:
                        send_error_level(user,user_level, str(command))
                else:

                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))    

            elif compare_strings(command,command_data_default['dice']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['dice']['delay']
                last_use = command_data_default['dice']['last_use']
                status = command_data_default['dice']['status']
                user_level = command_data_default['dice']['user_level']
                
                if status:

                    if check_perm(user_type, user_level):
                    
                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                            
                            result = randint(1,6)
                            
                            aliases = {
                                "{value}" : str(result)
                            }
                            
                            command_data_default['dice']['last_use'] = current
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(command_data_default['dice']['response'], aliases))
                                
                        else:
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                    
            elif compare_strings(command,command_data_default['random']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['random']['delay']
                last_use = command_data_default['random']['last_use']
                status = command_data_default['random']['status']
                user_level = command_data_default['random']['user_level']
                
                if status:
                    
                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)
                        
                        if check_time:
                            
                            value = command_lower.split(command_data_default['random'].lower())[1]

                            if value != '' and value.strip().isnumeric():
                                
                                result = randint(0,int(value))
                                
                                aliases = {
                                    "{value}" : str(result)
                                }
                                
                                command_data_default['random']['last_use'] = current
                            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(command_data_default['random']['response'], aliases))
                            
                            else:
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_value'), aliases))
                                

                        else:
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                        
            elif compare_strings(command,command_data_default['game']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['game']['delay']
                last_use = command_data_default['game']['last_use']
                status = command_data_default['game']['status']
                user_level = command_data_default['game']['user_level']
                
                if status:
                    
                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:

                            result_data = twitch_api.get_streams(first=1,user_login=authdata.USERNAME())
                            
                            if result_data['data']:
                                
                                game_name = result_data['data'][0]['game_name']
                                
                                aliases = {"{game}" : str(game_name)}

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(command_data_default['game']['response'], aliases))
                                    
                            command_data_default['game']['last_use'] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "save",command_data_default)
                                    
                        else:
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    
                    else:
                        send_error_level(user,user_level, str(command))
                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases)) 
                        
            elif compare_strings(command,command_data_default['uptime']['command']):  

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['uptime']['delay']
                last_use = command_data_default['uptime']['last_use']
                status = command_data_default['uptime']['status']
                user_level = command_data_default['uptime']['user_level']
                
                if status:

                    if check_perm(user_type, user_level):
                        
                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                            
                            result_data = twitch_api.get_streams(first=1,user_login=authdata.USERNAME())
                            
                            if result_data['data']:
                                
                                started = result_data['data'][0]['started_at']

                                time_in_live = utils.calculate_time(started)
                                
                                hours = time_in_live['hours']
                                minutes = time_in_live['minutes']
                                
                                aliases = {
                                    "{username}" : str(user),
                                    "{h}" : str(hours),
                                    "{m}" : str(minutes)
                                }

                                if utils.send_message("RESPONSE"):    
                                    send(utils.replace_all(command_data_default['uptime']['response'], aliases))
                                    
                            command_data_default['uptime']['last_use'] = current
                                
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "save",command_data_default)
                            
                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                        
            elif compare_strings(command,command_data_default['followage']['command']):  
                
                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['followage']['delay']
                last_use = command_data_default['followage']['last_use']
                status = command_data_default['followage']['status']
                user_level = command_data_default['followage']['user_level']
                
                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                            
                            if user != authdata.USERNAME():   
                                
                                user_info = twitch_api.get_users_follows(first=1,from_id=user_id_command,to_id=authdata.BROADCASTER_ID())
                                
                                if user_info['total']:
                                
                                    data_folloed = user_info['data'][0]['followed_at']

                                    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                                    utc_date = datetime.datetime.fromisoformat(data_folloed).replace(tzinfo=pytz.utc)

                                    gmt_minus_3_now = utc_now.astimezone(pytz.timezone("Etc/GMT+3"))
                                    gmt_minus_3_date = utc_date.astimezone(pytz.timezone("Etc/GMT+3"))

                                    difference = gmt_minus_3_now - gmt_minus_3_date
                                    
                                    days = difference.days
                                    hours = difference.seconds//3600
                                    minutes = (difference.seconds//60)%60
                                    sec = difference.seconds%60
                                    
                                    aliases = {
                                        "{username}" : user,
                                        "{streamer}" : authdata.USERNAME(),
                                        "{d}" : str(days),
                                        "{h}" : str(hours),
                                        "{m}" : str(minutes),
                                        "{s}" : str(sec)
                                    }
                                    
                                    message = utils.replace_all(command_data_default['followage']['response'],aliases)
                                    if utils.send_message('RESPONSE'):
                                        send(message)
                                        
                                    command_data_default['followage']['last_use'] = current
                                
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "save",command_data_default)
                                        
                                else:
                                    aliases = {
                                        "{username}" : user,
                                        "{streamer}" : authdata.USERNAME(),
                                    }
                                    
                                    if utils.send_message("RESPONSE"):
                                        send(utils.replace_all(utils.messages_file_load('followage_no_follow'),aliases))
                            else:
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.messages_file_load('followage_error_streamer'))

                        else:
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                    
            elif compare_strings(command,command_data_default['accountage']['command']):  
                
                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['accountage']['delay']
                last_use = command_data_default['accountage']['last_use']
                status = command_data_default['accountage']['status']
                user_level = command_data_default['accountage']['user_level']
                
                if status:   

                    if check_perm(user_type, user_level):
                        
                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:

                            if sufix != None:

                                user_data = twitch_api.get_users(logins=[sufix.lower()])
                            else:
                                user_data = twitch_api.get_users(logins=[user.lower()])

                            if user_data['data'] != []:

                                created_at = user_data['data'][0]['created_at']

                                data = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                                today = datetime.datetime.now()

                                diff = today - data
                                year = diff.days // 365
                                month = (diff.days % 365) // 30
                                day = (diff.days % 365) % 30
                                hour = diff.seconds // 3600
                                minute = (diff.seconds % 3600) // 60

                                message_pre = utils.replace_all(command_data_default['accountage']['response'],aliases)

                                aliases = {
                                    '{day}' : str(day),
                                    '{month}' : str(month),
                                    '{year}' : str(year),
                                    '{hour}' : str(hour),
                                    '{minute}' : str(minute)
                                }

                                message = utils.replace_all(message_pre,aliases)
                                if utils.send_message('RESPONSE'):
                                    send(message)

                                command_data_default['accountage']['last_use'] = current
                            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)

                            else:

                                message = utils.replace_all(utils.messages_file_load('user_not_found'),aliases)
                                if utils.send_message('RESPONSE'):
                                    send(message)
                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    
                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
            
            elif compare_strings(command,command_data_default['msgcount']['command']):  
                
                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['msgcount']['delay']
                last_use = command_data_default['msgcount']['last_use']
                status = command_data_default['msgcount']['status']
                
                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
        
                            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
                                
                            if user in user_data_load:
                                
                                msgcount = user_data_load[user]['chat_freq']
                                
                                aliases = {
                                    '{username}' : user,
                                    '{count}' : str(msgcount)
                                }
                                
                                message = utils.replace_all(command_data_default['msgcount']['response'],aliases)
                                if utils.send_message('RESPONSE'):
                                    send(message)

                                command_data_default['msgcount']['last_use'] = current
                            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)
                            
                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)
                    else:
                        send_error_level(user,user_level, str(command))
                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
            
            elif compare_strings(command,command_data_default['watchtime']['command']):  
                
                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['watchtime']['delay']
                last_use = command_data_default['watchtime']['last_use']
                status = command_data_default['watchtime']['status']
                user_level = command_data_default['watchtime']['user_level']
                
                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                            
                            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
                            
                            if user in user_data_load:
                                
                                watchtime = user_data_load[user]['time_w']
                                
                                delta = datetime.timedelta(minutes=watchtime)
                                dias = delta.days
                                horas = delta.seconds // 3600
                                minutos = (delta.seconds % 3600) // 60
                                segundos = delta.seconds % 60
                                
                                aliases = {
                                    '{d}' : str(dias),
                                    '{h}' : str(horas),
                                    '{m}' : str(minutos),
                                    '{s}' : str(segundos),
                                    '{streamer}' : authdata.USERNAME(),
                                    '{username}' : str(user)
                                }
                                
                                message = utils.replace_all(command_data_default['watchtime']['response'],aliases)
                                if utils.send_message('RESPONSE'):
                                    send(message)

                                command_data_default['watchtime']['last_use'] = current
                            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_default['title']['command']):  
                
                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['title']['delay']
                last_use = command_data_default['title']['last_use']
                status = command_data_default['title']['status']
                user_level = command_data_default['title']['user_level']
                response_sucess = command_data_default['title']['response']
                
                if status:      
                        
                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:

                            if sufix != "":
                                
                                headers = {
                                    'Authorization': f'Bearer {authdata.TOKEN()}',
                                    'Client-Id': os.getenv('CLIENTID'),
                                    'Content-Type': 'application/json',
                                }

                                params = {
                                    'broadcaster_id': authdata.BROADCASTER_ID(),
                                }

                                json_data = {
                                    'title': sufix
                                }
                                
                                response = req.patch('https://api.twitch.tv/helix/channels', params=params, headers=headers, json=json_data)
                                
                                aliases = {
                                    '{username}': str(user),
                                    '{command}': str(command),
                                    '{prefix}': str(prefix),
                                    '{user_level}': str(user_type),
                                    '{user_id}': str(user_id_command),
                                    '{sufix}': str(user_input),
                                    '{random}' : str(random_value),
                                    '{error}' : str(f"{response.text}")
                                }

                                if response.status_code != 204:
                                    send(utils.replace_all(utils.messages_file_load('update_stream_error'),aliases))
                                else:
                                    send(utils.replace_all(response_sucess,aliases))
                            
                                command_data_default['title']['last_use'] = current
                            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)

                            else:
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_sufix'),aliases))

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))
                    
                else:

                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_default['setgame']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['setgame']['delay']
                last_use = command_data_default['setgame']['last_use']
                status = command_data_default['setgame']['status']
                user_level = command_data_default['setgame']['user_level']
                response_sucess = command_data_default['setgame']['response']

                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                        
                            if sufix != "":

                                data_games = utils.manipulate_json(f"{utils.local_work('appdata_path')}/games/games.json", "load")
                                
                                games_names = [jogo["name"] for jogo in data_games.values()]
                                best_matches = difflib.get_close_matches(sufix, games_names, n=1, cutoff=0.8)

                                if len(best_matches) > 0:
                                    
                                    game_id = [chave for chave, valor in data_games.items() if valor["name"] == best_matches[0]][0]

                                    headers = {
                                        'Authorization': f'Bearer {authdata.TOKEN()}',
                                        'Client-Id': os.getenv('CLIENTID'),
                                        'Content-Type': 'application/json',
                                    }

                                    params = {
                                        'broadcaster_id': authdata.BROADCASTER_ID(),
                                    }

                                    json_data = {
                                        'game_id': str(game_id)
                                    }
                                    
                                    response = req.patch('https://api.twitch.tv/helix/channels', params=params, headers=headers, json=json_data)
                                    
                                    aliases = {
                                        '{username}': str(user),
                                        '{command}': str(command),
                                        '{prefix}': str(prefix),
                                        '{user_level}': str(user_type),
                                        '{user_id}': str(user_id_command),
                                        '{sufix}': str(sufix),
                                        '{random}' : str(random_value),
                                        '{error}' : str(f"{response.text}"),
                                        '{game_name}' : str(best_matches[0])
                                    }

                                    if response.status_code != 204:
                                        send(utils.replace_all(utils.messages_file_load('update_game_error'),aliases))
                                    else:
                                        send(utils.replace_all(response_sucess,aliases))

                                else:
                                    send(utils.replace_all(utils.messages_file_load('update_game_notfound'),aliases))


                                command_data_default['setgame']['last_use'] = current
                            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)
                                    
                            else:
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_sufix'),aliases))

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_queue['check_queue']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_queue['check_queue']['delay']
                last_use = command_data_queue['check_queue']['last_use']
                status = command_data_queue['check_queue']['status']
                user_level = command_data_queue['check_queue']['user_level']

                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(str(utils.messages_file_load('response_get_queue')), aliases))

                            command_data_queue['check_queue']['last_use'] = current
                            
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/games/games.json", "save", command_data_queue)

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_queue['rem_queue']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_queue['rem_queue']['delay']
                last_use = command_data_queue['rem_queue']['last_use']
                status = command_data_queue['rem_queue']['status']
                user_level = command_data_queue['rem_queue']['user_level']

                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                        
                            if sufix != "":

                                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "load")

                                if sufix in queue_data:
                                
                                    queue_data.remove(sufix)

                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "save", queue_data)
                                    
                                    toast('Nome removido') 

                                    aliases = {
                                        '{username}': str(user),
                                        '{command}': str(command),
                                        '{prefix}': str(prefix),
                                        '{user_level}': str(user_type),
                                        '{user_id}': str(user_id_command),
                                        '{sufix}': str(sufix),
                                        '{random}' : str(random_value),
                                        '{value}' :str(sufix),
                                    }
                                    
                                    response = utils.messages_file_load('response_rem_queue')

                                else:
                                    
                                    toast('O nome não está na lista') 

                                    aliases = {
                                        '{username}': str(user),
                                        '{command}': str(command),
                                        '{prefix}': str(prefix),
                                        '{user_level}': str(user_type),
                                        '{user_id}': str(user_id_command),
                                        '{sufix}': str(sufix),
                                        '{random}' : str(random_value),
                                        '{value}' :str(sufix),
                                    }

                                    response = utils.messages_file_load('response_noname_queue')


                                command_data_queue['rem_queue']['last_use'] = current
                        
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "save", command_data_queue)

                            else:

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_sufix'),aliases))

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_queue['add_queue']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_queue['add_queue']['delay']
                last_use = command_data_queue['add_queue']['last_use']
                status = command_data_queue['add_queue']['status']
                user_level = command_data_queue['add_queue']['user_level']

                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                        
                            if sufix != "":
                                    
                                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "load")

                                if sufix not in queue_data:

                                    queue_data.append(sufix)

                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json", "save",queue_data)
                                    
                                    toast('Nome adicionado')

                                    aliases = {
                                        '{username}': str(user),
                                        '{command}': str(command),
                                        '{prefix}': str(prefix),
                                        '{user_level}': str(user_type),
                                        '{user_id}': str(user_id_command),
                                        '{sufix}': str(sufix),
                                        '{random}' : str(random_value),
                                        '{value}' :str(sufix),
                                    }
                                    
                                    response = utils.messages_file_load('response_add_queue')

                                else:
                                    
                                    toast('O nome já está na lista') 


                                    aliases = {
                                        '{username}': str(user),
                                        '{command}': str(command),
                                        '{prefix}': str(prefix),
                                        '{user_level}': str(user_type),
                                        '{user_id}': str(user_id_command),
                                        '{sufix}': str(sufix),
                                        '{random}' : str(random_value),
                                        '{value}' :str(sufix),
                                    }
                                    
                                    response = utils.messages_file_load('response_namein_queue')


                                command_data_queue['add_queue']['last_use'] = current

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "save",command_data_queue)

                            else:

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_sufix'),aliases))

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            elif compare_strings(command,command_data_default['emote']['command']):

                data_append = {
                    "type" : "command",
                    "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                    "user_input" : sufix,
                }
                
                append_notice(data_append)

                delay = command_data_default['emote']['delay']
                last_use = command_data_default['emote']['last_use']
                status = command_data_default['emote']['status']
                user_level = command_data_default['emote']['user_level']

                if status:      

                    if check_perm(user_type, user_level):

                        message_delay, check_time, current = utils.check_delay(delay,last_use)

                        if check_time:
                        
                            if emotes != []:

                                threading.Thread(target=emote_rain, args=(emotes,), daemon=True).start()

                                response = command_data_default['emote']['response']
                                
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(response,aliases))

                                command_data_default['emote']['last_use'] = current
                            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/default_commands.json", "save", command_data_default)

                            else:

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('command_sufix'),aliases))

                        else:
                            
                            if utils.send_message("ERROR_TIME"):
                                send(message_delay)

                    else:
                        send_error_level(user,user_level, str(command))

                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))

            else:

                interaction_list = [
                    "interaction_1",
                    "interaction_2",
                    "interaction_3",
                    "interaction_4",
                    "interaction_5"
                ]

                for item in interaction_list:

                    if compare_strings(command,command_data_default[item]['command']):
                        
                        data_append = {
                            "type" : "command",
                            "message" : utils.replace_all(str(utils.messages_file_load('event_command')), aliases),
                            "user_input" : sufix,
                        }
                
                        append_notice(data_append)

                        delay = command_data_default[item]['delay']
                        last_use = command_data_default[item]['last_use']
                        status = command_data_default[item]['status']
                        user_level = command_data_default[item]['user_level']
                        
                        if status:  

                            if check_perm(user_type, user_level):

                                message_delay, check_time, current = utils.check_delay(delay,last_use)

                                if check_time:
                                                
                                    value = command_lower.split(command_data_default[item]['command'].lower())
                                    
                                    if len(value) > 1 and value[1] != "":
                                        
                                        value = value[1]
                                        
                                        aliases = {
                                            "{user_1}" : user,
                                            "{user_2}" : str(value)
                                        }
                                        
                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(command_data_default[item]['response'], aliases))
                                    else:
                                        
                                        if utils.send_message("RESPONSE"):
                                            send(utils.replace_all(utils.messages_file_load('command_string'), aliases))
                                            
                                    command_data_default[item]['last_use'] = current
                                    
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/default_commands.json", "save", command_data_default)
                                    
                                    
                                else:
                                    if utils.send_message("ERROR_TIME"):
                                        send(message_delay)
                            
                            else:
                                send_error_level(user,user_level, str(command))

                        else:
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))
                                                    
        else:

            if utils.send_message("RESPONSE"):
                send(utils.replace_all(utils.messages_file_load('command_disabled'),aliases))


def timeout_user(user,type_id):
    
    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

    if authdata.TOKEN() and authdata.USERNAME():
        
        user_id = twitch_api.get_users(logins=[user])
        user_id_resp = user_id['data'][0]['id']
        
        bot_id = twitch_api.get_users(logins=[authdata.BOTUSERNAME()])
        bot_id_resp = bot_id['data'][0]['id']
            
        url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={authdata.BROADCASTER_ID()}&moderator_id={bot_id_resp}"

        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bearer {authdata.TOKENBOT()}"
        headers["Client-Id"] = os.getenv('CLIENTID')
        headers["Content-Type"] = "application/json"
        
        if type_id == 'ban':
            data = '{"data": {"user_id": '+ user_id_resp +',"reason":"Comando aplicado pelo bot"}}'

        elif type_id == 'timeout':
            data = '{"data": {"user_id": '+ user_id_resp +',"duration":600,"reason":"Comando aplicado pelo bot"}}'
        
        resp = req.post(url, headers=headers, data=data)

        if resp.status_code == 200:
            toast('Ação executada')
        else:
            toast('Ocorreu um erro')


def emote_rain(emotes):
    
    obs_not_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/notfic.json", "load")

    if obs_not_data['HTML_EMOTE_ACTIVE']:

        data = {
            'type' : 'emotes',
            'html' : utils.update_emote(emotes)
        }

        sk.broadcast_message(json.dumps(data))

    else:
        
        if utils.send_message("RESPONSE"):
            send(utils.messages_file_load('emote_disabled'))

        
def parse_to_dict(message):

    try:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

        if authdata.TOKEN() and authdata.USERNAME():
            
            roles = ['spec']
            color = ''
            badges = ''
            badge_info = ''
            emotes_parsed = ''
            display_name = ''
            user_name = ''
            sub_count = 0
            user_replied = ''
            message_replied = ''
            response = 0
            user_id = ''
            emote_html_list = []

            def find_between( s, first, last ):
                    
                try:

                    start = s.index( first ) + len( first )
                    end = s.index( last, start )
                    return s[start:end]
                
                except Exception as e:
                    utils.error_log(e)
                    return False

            def parse_bages_info(badge_info):

                badges = badge_info.split(',')
                badge_info_dict = {}
                sub_count = 0

                for badge in badges:
                    badge_name = badge.split('/')[0]
                    badge_id = badge.split('/')[1]

                    badge_info_dict[badge_name] = badge_id
                    if badge_name == 'subscriber':
                        sub_count = badge_id

                return badge_info_dict , sub_count

            def parse_bages(badges):

                badges = badges.split(',')
                badge_dict = {}

                for badge in badges:
                    if badge != '':
                        badge_name = badge.split('/')[0]
                        badge_id = badge.split('/')[1]

                        badge_dict[badge_name] =  badge_id

                return badge_dict

            def parse_emotes(emotes):
                
                emotes = emotes.split('/')

                emote_dict = {}

                for emote in emotes:
                    emote_id = emote.split(':')[0]
                    emotes_pos = emote.split(':')[1].split(',')

                    emote_dict[emote_id] = []

                    for pos in emotes_pos:

                        pos_dict = {}
                        pos1 = pos.split('-')[0]
                        pos2 = pos.split('-')[1]

                        pos_dict = {
                            'startPosition' : pos1,
                            'endPosition' : pos2
                        }

                        emote_dict[emote_id].append(pos_dict)

                
                return emote_dict

            def parse_emotes_message(emote,parameters):

                emotes = {}

                for emote_id, emote_info in emote["emotes"].items():

                    for emote in emote_info:

                        start_position = int(emote["startPosition"])
                        end_position = int(emote["endPosition"]) + 1
                        emotes[start_position] = (end_position, emote_id)

                output = ""
                position = 0

                while position < len(parameters):

                    if position in emotes:

                        end_position, emote_id = emotes[position]
                        emote_html = "<img class='emoji drop' src='https://static-cdn.jtvnw.net/emoticons/v1/{}/1.0'/>".format(emote_id)
                        emote_html_list.append(emote_html)
                        output += emote_html
                        position = end_position
                        
                    else:
                        
                        output += parameters[position]
                        position += 1

                return output,emote_html_list
            
            def parse_bages_message(badges):

                tags = {"badges" : badges}

                channel_badges = utils.manipulate_json(f"{utils.local_work('appdata_path')}/badges/badges_channel.json", "load")
                global_badges = utils.manipulate_json(f"{utils.local_work('appdata_path')}/badges/badges_global.json", "load")
                
                badges = tags["badges"]

                badge_resp_list = ''

                for badge in badges:
                    
                    badge_id = badges[badge]

                    if badge not in channel_badges["badge_sets"]:

                        result = f'<img data-toggle="tooltip" data-bs-placement="left" title="{badge}-{badge_id}" class="badges" src="{global_badges["badge_sets"][badge]["versions"][badge_id]["image_url_1x"]}" />'

                        badge_resp_list += result

                    elif badge_id not in channel_badges["badge_sets"][badge]["versions"]:

                        result = f'<img data-toggle="tooltip" data-bs-placement="left" title="{badge}-{badge_id}" class="badges" src="{global_badges["badge_sets"][badge]["versions"][badge_id]["image_url_1x"]}" />'

                        badge_resp_list += result

                    else:

                        result = f'<img data-toggle="tooltip" data-bs-placement="left" title="{badge}-{badge_id}" class="badges" src="{channel_badges["badge_sets"][badge]["versions"][badge_id]["image_url_1x"]}" />'

                        badge_resp_list += result

                return badge_resp_list
            
            message_split = message.split(f'PRIVMSG #{authdata.USERNAME()} :')
            parameters = message_split[1]
            message = message_split[0]
            parameters_no_url = parameters
            url_regex = r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
            url_match = re.search(url_regex, parameters)

            if "color=" in message:
                color = find_between( message, 'color=', ';' )
        
            if '@badge-info=' in message:

                badge_info_find = find_between( message, '@badge-info=', ';' )

                if not badge_info_find == '':
                    badge_info ,sub_count = parse_bages_info(badge_info_find)
                else:
                    badge_info = ''
                    sub_count = 0

            if "user-id=" in message:
                user_id = find_between( message, 'user-id=', ';' )
        
            if 'emotes=' in message:
                
                emotes_find = find_between( message, 'emotes=', ';' )

                if not emotes_find == '':

                    emotes_parsed = parse_emotes(emotes_find)

                    emotes_dict = {'emotes': emotes_parsed}

                    parameters,emote_html_list = parse_emotes_message(emotes_dict,parameters)

            if 'badges=' in message:

                badges_find = find_between( message, 'badges=', ';' )

                if not badges_find == '':

                    badges = parse_bages(badges_find)

                    if 'subscriber' in badges:
                        sub = 1

                    badges = parse_bages_message(badges)
                
            if 'display-name=' in message:
                display_name = find_between( message, 'display-name=', ';' )

                user_name = display_name.lower()

            if 'vip=1' in message:
                roles.append('vip')
                
            if 'mod=1' in message:
                roles.append('mod')
                
            if user_id == authdata.BROADCASTER_ID() or user_id == authdata.BOT_ID():
                roles.append('mod')

            if 'subscriber=1' in message:
                roles.append('sub')
            
            if 'reply-parent-display-name' in message:
                
                user_replied = utils.find_between( message, 'reply-parent-display-name=', ';')
                message_replied = re.sub(r"\\s", " ", utils.find_between( message, 'reply-parent-msg-body=', ';'))
                response = 1
            
            if url_match:
                
                link_par = " '"+ url_match.group(0)+ "'"
                type_part = "'link'"
                link_html = f'<span class="link-style" onclick="window.pywebview.api.open_py({type_part},{link_par})" href="{url_match.group(0)}">{url_match.group(0)}</span>'
                parameters = parameters.replace(url_match.group(0), link_html)
            
            frist_message = utils.find_between( message, 'first-msg=', ';')
            
            data = {
                "parameters" : parameters,
                "parameters_no_url"  : parameters_no_url,
                "frist_message" : frist_message,
                "message_replied" : message_replied,
                "display_name"  : display_name,
                "user_name"  : user_name,
                "user_replied" : user_replied,
                "response": response,
                "user_id"  : user_id,
                "color"  : color,
                "badges"  : badges,
                "emote_list" : emote_html_list,
                "badge_info"  : badge_info,
                "roles"  : roles,
                "sub_count"  : sub_count,
            }
            
            result = namedtuple('result', data.keys())(*data.values())
            
            return result
        
    except Exception as e:
        utils.error_log(e)


def command_fallback(message: str) -> None:
    
    """
    Processa a mensagem recebida da twitch via IRC e transforma em dicionarios de acordo com o tipo de mensagem enviada.

    """

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

    if authdata.TOKEN() and authdata.USERNAME():
        
        if "REERRORCONNCHAT" in message:

            toast(message.split('|')[1].strip())

        message_data = message.split(f'#{authdata.USERNAME()} :')[0]

        if "Login authentication failed" in message:
            toast('Erro de autenticação, é recomendado fazer o login novamente ou reiniciar o programa, se o erro persistir contate o suporte.')
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "load")
        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "load")
        users_sess_join_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "load")
        bot_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/bot_list.json", "load")
        bot_list_user = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/bot_list_add.json", "load")
        userjoin_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_joined.json", "load")
        
        chat_time = utils.time_date()
                
        def add_user_join(data):
            
            if data['username'] not in bot_list and data['username'] not in bot_list_user:
                
                if data['username'] not in userjoin_data_load['spec']:
                    
                    userjoin_data_load['spec'].append(data['username'])
                    
                if data['username'] not in users_sess_join_data['spec']:  
                    
                    users_sess_join_data['spec'].append(data['username'])
                    
            else:
                
                if data['username'] not in userjoin_data_load['bot']:
                
                    userjoin_data_load['bot'].append(data['username'])
                
                if data['username'] not in users_sess_join_data['bot']:
                    
                    users_sess_join_data['bot'].append(data['username'])
                    
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_joined.json", "save",userjoin_data_load)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "save",users_sess_join_data)
                    
        def add_user_database(data): 
            
            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
            
            if data['username'] not in user_data_load:
                
                user_data_load[data['username']] = {
                    'display_name' : data['display_name'],
                    "roles" : ['spec'],
                    'sub_count': data['sub_count'],
                    'chat_freq' : data['chat_freq'],
                    'color': data['color'],
                    'badges': data['badges'],
                    'last_join' : data['last_join'],
                    'time_w': 0
                }
                
            else:

                if 'roles' in user_data_load[data['username']]:
                    roles = user_data_load[data['username']]['roles']
                else:
                    roles = []

                for role in data['roles']:
                    if role not in roles:
                        roles.append(role)

                chat_freq = user_data_load[data['username']]['chat_freq']
                chat_freq = chat_freq + 1
                
                if chat_freq > int(chat_data['top_chatter_min']) and "top_chatter" not in roles:
                    roles.append('top_chatter')
                    
                regular_time = user_data_load[data['username']]['time_w']
                regular_min = chat_data['regular_min']
                
                if regular_time > int(regular_min) and "regular" not in roles:
                    roles.append('regular')
                        
                user_data_load[data['username']] = {
                    'display_name' : data['display_name'],
                    "roles" : roles,
                    'chat_freq' : chat_freq,
                    'sub_count': data['sub_count'],
                    'color': data['color'],
                    'badges': data['badges'],
                    'last_join' : user_data_load[data['username']]['last_join'],
                    'time_w': user_data_load[data['username']]['time_w']
                }
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save",user_data_load)
                                        
        try:
            
            if len(message.split()) > 1:

                if '\r\n' in message:
                    message = message.split('\r\n')[0]
                        
                if 'USERNOTICE' in message_data:
                        
                    event_config_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")
                    
                    if 'msg-id' in message_data:
                        
                        msg_id = utils.find_between( message, 'msg-id=', ';' )               
                        
                        if msg_id == 'subgift': 
                            
                            data = {
                                'display_name' : utils.find_between( message, 'display-name=', ';' ),
                                'months' : utils.find_between( message, 'msg-param-gift-months=', ';' ),
                                'rec_username' : utils.find_between( message, 'msg-param-recipient-display-name=', ';' ),
                                'plan' : utils.find_between( message, 'msg-param-sub-plan-name=', ';').replace('\s', ' '),
                                'plan_type' : utils.find_between( message, 'msg-param-sub-plan=', ';'),
                            }
                            
                            aliases = {
                                '{months}' : data['months'],
                                '{username}' : data['display_name'],
                                '{rec_username}' : data['rec_username'],
                                '{plan}' : data['plan'],
                            }
                            
                            response_chat = utils.replace_all(event_config_data['giftsub']['response_chat'],aliases)
                            
                            send_announcement(response_chat,'purple')

                            data_discord = {
                                'type_id' : 'giftsub',
                                'username' : data['display_name'],
                                'rec_username' : data['rec_username'],
                                'plan' : data['plan']
                            }
                            
                            send_discord_webhook(data_discord)  
                        
                        elif msg_id == 'submysterygift': 
                            
                            data = {
                                'display_name' : utils.find_between( message, 'display-name=', ';' ),
                                'count' : utils.find_between( message, 'msg-param-mass-gift-count=', ';' ),
                                'plan' : utils.find_between( message, 'msg-param-sub-plan=', ';'),
                            }

                            aliases = {
                                '{username}' : data['display_name'],
                                '{count}' : data['count'],
                                '{plan}' : data['plan'],
                            }
                            
                            response_chat = utils.replace_all(event_config_data['mysterygift']['response_chat'],aliases) 
                            send_announcement(response_chat,'purple')

                            data_discord = {
                                'type_id' : 'mysterygift',
                                'username' : data['display_name'],
                                'count' : data['count'],
                                'plan' : data['plan']
                            }
                            
                            send_discord_webhook(data_discord)  

                        elif msg_id == 'anongiftpaidupgrade': 
                            
                            data = {
                                'display_name' : utils.find_between( message, 'display-name=', ';' ),
                            }

                            aliases = {
                                '{username}' : data['display_name'],
                            }
                        
                            response_chat = utils.replace_all(event_config_data['re-mysterygift']['response_chat'],aliases) 
                            send_announcement(response_chat,'purple')

                            data_discord = {
                                'type_id' : 're-mysterygift',
                                'username' : data['display_name']
                            }
                            
                            send_discord_webhook(data_discord)      

                        elif msg_id == 'announcement':
                                    
                            data = {
                                'display_name' : utils.find_between( message, 'display-name=', ';' ),
                                "message" : message.split(f'USERNOTICE #{authdata.USERNAME()} :')[1],
                                "font_size" : chat_data['font-size'],
                                "wrapp_message" : chat_data["wrapp-message"],
                                "color" : utils.find_between( message, 'color=', ';' ),
                                "color_message" : utils.find_between( message, 'msg-param-color=', ';' ),
                                "show_badges" : chat_data["show-badges"],
                                "badges" : f'<img class="badges" src="https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1" />', 
                                "mod": 1,
                                "vip": 0,
                                "subscriber": 0,
                                "data_show" : chat_data["data-show"],
                                "chat_time" : chat_time,
                                "type_data" : chat_data["type-data"],
                            }
                                    
                            window.evaluate_js(f"append_announce({json.dumps(data, ensure_ascii=False)})")
                            
                            if window_chat_open:
                                window_chat.evaluate_js(f"append_announce_out({json.dumps(data, ensure_ascii=False)})")          
                        
                if 'PRIVMSG' in message_data and not "custom-reward-id" in message_data:
                        
                    parse_res = parse_to_dict(message)

                    now = datetime.datetime.now()
                    last_join = now.strftime('%H:%M:%S %d/%m/%Y')
                    
                    data_database = {
                        'username' : parse_res.user_name,
                        'display_name' : parse_res.display_name,
                        'roles' : parse_res.roles,
                        'sub_count': parse_res.sub_count,
                        'chat_freq' : 1,
                        'color': parse_res.color,
                        'badges': parse_res.badges,
                        'last_join' : last_join
                    }

                    add_user_join(data_database)
                    add_user_database(data_database)
                        
                    response_userdata = userdata_py('load',parse_res.user_name) 
                    
                    data_res = {
                        'type': 'PRIVMSG',
                        "response" : parse_res.response,
                        "color": response_userdata.color,
                        "display_name": response_userdata.display_name,
                        "badges" : response_userdata.badges,
                        "emotes" : parse_res.emote_list,
                        "user_name": parse_res.user_name,
                        "user_replied" : parse_res.user_replied,
                        "roles": response_userdata.roles,
                        "user_id": parse_res.user_id,
                        "frist_message" : parse_res.frist_message,
                        "message": parse_res.parameters,
                        "message_replied" : parse_res.message_replied,
                        "message_no_url": parse_res.parameters_no_url,
                        "appply_colors" : chat_data["appply-colors"],
                        "appply_no_colors" : chat_data["appply-no-colors"],
                        "data_show" : chat_data["data-show"],
                        "chat_time" : chat_time,
                        "type_data" : chat_data["type-data"],
                        "block_color" : chat_data["block-color"],
                        "color_apply" : chat_data["color-apply"],
                        "font_size" : chat_data["font-size"],
                        "show_badges" : chat_data["show-badges"],
                        "wrapp_message" : chat_data["wrapp-message"],
                    }

                    window.evaluate_js(f"append_message({json.dumps(data_res, ensure_ascii=False)})")

                    if window_chat_open:

                        window_chat.evaluate_js(f"append_message_out({json.dumps(data_res, ensure_ascii=False)})")

                    commands_module(data_res)      

                if f'JOIN #{authdata.USERNAME()}'in message and not 'PRIVMSG' in message:
                    
                    user_join = utils.find_between(message.split()[0],'@','.tmi')
                    
                    data_database = {
                        'username' : user_join,
                    }
                    
                    add_user_join(data_database)
                        
                    if not user_join in userjoin_data_load['spec']:
                        
                        if user_join not in bot_list and user_join not in bot_list_user:
                            
                            if chat_data['send-greetings']:

                                aliases = {
                                    '{username}' : user_join
                                }
                                
                                send(utils.replace_all(chat_data['greetings'], aliases))        
                            
                            if chat_data['not-user-sound']:
                                
                                if user_join not in chat_data['user_not_display']:
                                
                                    sound_playing = pygame.mixer.music.get_busy()

                                    while sound_playing:
                                        sound_playing = pygame.mixer.music.get_busy()
                                        time.sleep(2)
                                        
                                    sound_path = chat_data['not-sound-path']
                                    pygame.mixer.music.load(sound_path)
                                    pygame.mixer.music.play()
                    
                    if user_join not in bot_list and user_join not in bot_list_user:       
                        
                        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
                        
                        now = datetime.datetime.now()
                        last_join = now.strftime('%H:%M:%S %d/%m/%Y')
                        
                        if user_join in user_data_load:
                            
                            user_data_load[user_join]['last_join'] = last_join
    
                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save",user_data_load)
                
                        if event_log_data['show_join']:
                            
                            if user_join not in chat_data['user_not_display']:    
                                
                                aliases = {
                                    '{username}' : user_join
                                }

                                data_append = {
                                    "type" : "join",
                                    "message" : utils.replace_all(str( utils.messages_file_load('event_join')), aliases),
                                    "user_input" : '',
                                }
                                
                                append_notice(data_append)
                                                                
                if '.twitch.tv 353' in message and not 'PRIVMSG' in message: 
                    
                    names_list = message.split(f'#{authdata.USERNAME()} :')
                    list_join = names_list[1].split(' ')
                                
                    for name in list_join:
                        
                        name = name.strip()
                        
                        if name not in bot_list and name not in bot_list_user:
                            
                            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")

                            now = datetime.datetime.now()
                            last_join = now.strftime('%H:%M:%S %d/%m/%Y')
                            
                            if name in user_data_load:
                                
                                user_data_load[name]['last_join'] = last_join
                                
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save",user_data_load)         
                        
                            if name not in users_sess_join_data['spec']:
                                
                                users_sess_join_data['spec'].append(name)
                                
                        else:
                            
                            if name not in users_sess_join_data['bot']:
                                
                                users_sess_join_data['bot'].append(name)
                                
                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "save",users_sess_join_data)    
                    
                if 'PART' in message and not 'PRIVMSG' in message:

                    user_part = utils.find_between(message.split()[0],':','!')

                    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")  
                        
                    if user_part in user_data_load:
                        
                        datetime2 = datetime.datetime.now()
                        
                        last_join = user_data_load[user_part]['last_join']
                        datetime1 = datetime.datetime.strptime(last_join, "%H:%M:%S %d/%m/%Y")
                        
                        diff = datetime2 - datetime1
                        minutes = diff.total_seconds() / 60
                        
                        current_min = user_data_load[user_part]['time_w']
                        
                        total_min = int(current_min) + int(minutes)
                        
                        user_data_load[user_part]['time_w'] = int(total_min)
                            
                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save",user_data_load)   

                    if user_part not in bot_list and user_part not in bot_list_user:
                        
                        if user_part in users_sess_join_data['spec']:
                            
                            users_sess_join_data['spec'].remove(user_part)
                            
                            if event_log_data['show_leave']:
                        
                                if user_part not in chat_data['user_not_display']:    
                                        
                                    aliases = {
                                        '{username}' : user_part
                                    }
                                    
                                    message_event = utils.messages_file_load('event_leave')
                                    message_event = utils.replace_all(str(message_event), aliases)

                                    data_append = {
                                    "type" : "join",
                                    "message" : message_event,
                                    "user_input" : '',
                                    }
                                    
                                    append_notice(data_append)

                    else:
                        
                        if user_part in users_sess_join_data['bot']:
                            
                            users_sess_join_data['bot'].remove(user_part)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "save",users_sess_join_data)
                            
                if '@ban-duration=' in message and not 'PRIVMSG' in message:
                    
                    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
            
                    timeout_time = utils.find_between(message,'@ban-duration=',';')
                    target_user = utils.find_between(message,'target-user-id=',';')
                    
                    if target_user in user_data_load:
                        
                        data = {
                            "message" : f"Usuário {user_data_load[target_user]['display_name']} colocado em timeout por {timeout_time} segundos",
                            "font-size" : chat_data['font-size'],
                            "color" : chat_data['color-not']
                        }
                        
                        window.evaluate_js(f"append_notice({json.dumps(data, ensure_ascii=False)})")
            
        except Exception as e:
            utils.error_log(e)
    

def close():

    if window_chat_open:
        window_chat.destroy()

    if window_events_open:
        window_events.destroy()

    try:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

        if authdata.TOKEN() and authdata.USERNAME():

            url = 'https://api.twitch.tv/helix/eventsub/subscriptions'

            header = CaseInsensitiveDict()
            header["Authorization"] = f"Bearer {authdata.TOKEN()}"
            header["Client-Id"] = os.getenv('CLIENTID')
            header['Content-Type'] = 'application/json'

            response = req.get(url, headers=header)
            data = response.json()

            if response.status_code == 200:

                subscriptions = data['data']

                for subscription in subscriptions:

                    status = subscription['status']
                    subscription_id = subscription['id']

                    if status != 'websocket_disconnected' and status != 'websocket_failed_ping_pong':

                        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'

                        header = CaseInsensitiveDict()
                        header["Authorization"] = f"Bearer {authdata.TOKEN()}"
                        header["Client-Id"] = os.getenv('CLIENTID')
                        header['Content-Type'] = 'application/json'

                        params = {'id': subscription_id}

                        response = req.delete(url, headers=header, params=params)
            else:
                print(f"Erro ao fazer a solicitação: {response.status_code} - {data['message']}")

    except Exception as e:

        utils.error_log(e)


    chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json", "load")
    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")
    userjoin_sess_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "load")

    names = userjoin_sess_load['spec']
    
    for name in names:
        
        if name in user_data_load:
            
            datetime2 = datetime.datetime.now()
            
            last_join = user_data_load[name]['last_join']
            datetime1 = datetime.datetime.strptime(last_join, "%H:%M:%S %d/%m/%Y")
            
            diff = datetime2 - datetime1
            minutes = diff.total_seconds() / 60
            
            current_min = user_data_load[name]['time_w']
            
            total_min = int(current_min) + int(minutes)
            
            user_data_load[name]['time_w'] = int(total_min)
            
            regular_min = chat_data['regular_min']
            
            if 'roles' in user_data_load[name].keys():
                if total_min > int(regular_min) and "regular" not in user_data_load[name]['roles']:
                    user_data_load[name]['roles'].append('regular')
                
    utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "save",user_data_load)
    
    lock_manager.unlock()

    sys.exit(0)


def download_badges():

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

    if authdata.TOKEN() and authdata.USERNAME():
            
        os.makedirs(f"{utils.local_work('appdata_path')}/badges",exist_ok=True)
    
        global_badge_url = 'https://api.twitch.tv/helix/chat/badges/global'
        channel_badge_url = f'https://api.twitch.tv/helix/chat/badges?broadcaster_id={authdata.BROADCASTER_ID()}'

        headers = {
            "Authorization": f"Bearer {authdata.TOKEN()}",
            "Client-Id": os.getenv('CLIENTID'),
            "Content-Type": "application/json"
        }

        response_global_badge = req.get(global_badge_url, headers=headers)

        if response_global_badge.status_code == 200:

            global_badge_json = json.loads(response_global_badge.content)

            new_dict = {
                "badge_sets": {}
            }

            for item in global_badge_json["data"]:
                set_id = item["set_id"]
                versions = item["versions"]

                new_dict["badge_sets"][set_id] = {
                    "versions": {}
                }

                for version in versions:
                    version_id = version["id"]
                    version.pop("id")

                    new_dict["badge_sets"][set_id]["versions"][version_id] = version

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/badges/badges_global.json", "save", new_dict)

        response_channel_badge = req.get(channel_badge_url, headers=headers)

        if response_channel_badge.status_code == 200:
            
            channel_badge_json = json.loads(response_channel_badge.content)

            new_dict = {
                "badge_sets": {}
            }

            for item in channel_badge_json["data"]:
                set_id = item["set_id"]
                versions = item["versions"]

                new_dict["badge_sets"][set_id] = {
                    "versions": {}
                }

                for version in versions:
                    version_id = version["id"]
                    version.pop("id")

                    new_dict["badge_sets"][set_id]["versions"][version_id] = version

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/badges/badges_channel.json", "save", new_dict)


def post_eventsub(id):
    
    while True:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

        if authdata.TOKEN() and authdata.USERNAME():

            header = CaseInsensitiveDict()
            header["Authorization"] = f"Bearer {authdata.TOKEN()}"
            header["Client-Id"] = os.getenv('CLIENTID')
            header['Content-Type'] = 'application/json'
            
            json_data_param = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/websocket_param.json", "load")

            for type_param in json_data_param:

                need_mod_list = ['channel.shoutout.receive','channel.shoutout.create','channel.shield_mode.end','channel.shield_mode.begin']
                
                if type_param == 'channel.raid':
                    
                    broadcast_type = 'to_broadcaster_user_id'
                    
                    parameters = {
                        "type": f"{type_param}",
                        "version": "1",
                        "condition": {
                            f"{broadcast_type}": authdata.BROADCASTER_ID()
                        },
                        "transport": {
                            "method": "websocket",
                            "session_id": id
                        }   
                    } 
                                    
                elif type_param == 'channel.follow':
                    
                    broadcast_type = 'broadcaster_user_id'
                
                    parameters = {
                        "type": f"{type_param}",
                        "version": "2",
                        "condition": {
                            f"{broadcast_type}": authdata.BROADCASTER_ID(),
                            "moderator_user_id": authdata.BROADCASTER_ID()
                        },
                        "transport": {
                            "method": "websocket",
                            "session_id": id
                        }   
                    }    
                
                elif type_param in need_mod_list:
                    
                    broadcast_type = 'broadcaster_user_id'
                
                    parameters = {
                        "type": f"{type_param}",
                        "version": "1",
                        "condition": {
                            f"{broadcast_type}": authdata.BROADCASTER_ID(),
                            "moderator_user_id": authdata.BROADCASTER_ID()
                        },
                        "transport": {
                            "method": "websocket",
                            "session_id": id
                        }   
                    }    
                
                else:
                
                    broadcast_type = 'broadcaster_user_id'
                
                    parameters = {
                        "type": f"{type_param}",
                        "version": "1",
                        "condition": {
                            f"{broadcast_type}": authdata.BROADCASTER_ID()
                        },
                        "transport": {
                            "method": "websocket",
                            "session_id": id
                        }   
                    }    

                req.post('https://api.twitch.tv/helix/eventsub/subscriptions', data=json.dumps(parameters), headers=header)
                
            break
        
        else:
            
            time.sleep(10)      
        
        
def on_message(ws, message): 

    try:

        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

        data = json.loads(message)

        message_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")

        message_type = data["metadata"]["message_type"]
        
        if message_type == 'session_welcome':
            threading.Thread(target=post_eventsub, args=(data["payload"]["session"]["id"],), daemon=True).start()
            
        elif message_type == 'notification':
            
            subscription_type = data["metadata"]["subscription_type"]
            
            if subscription_type == 'channel.follow':
                
                type_id = 'follow'
                
                event = data['payload']['event']
                
                follow_name = event['user_name']
                follow_date = event['followed_at']
                
                aliases = {
                    '{username}' : follow_name
                }
                
                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type" : "event",
                    "message" : message_event,
                    "user_input" : '',
                }
                
                append_notice(data_append)

                data_send = {
                    'type_id' : "follow",
                    'follow_name' : follow_name,
                    'follow_date' : follow_date
                }
                
                
                send_discord_webhook(data_send)

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                    
            elif subscription_type == 'channel.channel_points_custom_reward_redemption.add':
                
                event = data['payload']['event']
                user_name = event['user_name']
                user_id = event['user_id']
                user_input = event['user_input']
                reward_id = event['reward']['id']
                reward_title = event['reward']['title']
                
                reward_data = twitch_api.get_custom_reward(authdata.BROADCASTER_ID(),reward_id) 
                
                image = reward_data["data"][0]["image"]
                
                if not image == None:
                    redeem_image = reward_data["data"][0]["image"]["url_4x"]
                else:
                    redeem_image = reward_data["data"][0]["default_image"]["url_4x"]
                
                data_reward_send = {
                    'user_name' : user_name,
                    'user_id' : user_id,
                    'user_input' : user_input,
                    'reward_title' : reward_title,
                    'image' : redeem_image
                }
                
                receive_redeem(data_reward_send, 'redeem')
            
            elif subscription_type == 'channel.update':  

                type_id = 'live_cat'

                event = data['payload']['event']
                
                user_name = event['broadcaster_user_name']
                title = event['title']
                category_name = event['category_name']
                is_mature = event['is_mature']
                
                data = {
                    'type_id' : "live_cat",
                    'tag' : str(category_name),
                    'title' : str(title),
                    'is_mature' : str(is_mature)
                }
                
                send_discord_webhook(data)

                aliases = {
                    '{tag}' : str(category_name),
                    '{title}' : str(title),
                    '{is_mature}' : str(is_mature)
                }

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type" : "event",
                    "message" : message_event,
                    "user_input" : '',
                }
                
                append_notice(data_append)

                if message_data[type_id]['status']:

                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                
            elif subscription_type == 'stream.online':  
                
                type_id = 'live_start'

                event = data['payload']['event']
                
                user_name = event['broadcaster_user_name']
                
                data = {
                    'type_id' : "live_start",
                    'username' : user_name,
                }
                
                aliases = {
                    '{broadcaster}' : user_name
                }
                
                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }
                
                send_discord_webhook(data)
                append_notice(data_append)

                if message_data[type_id]['status']:

                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                
            elif subscription_type == 'stream.offline':  
                
                type_id = 'live_end'

                event = data['payload']['event']
                
                user_name = event['broadcaster_user_name']

                data = {
                    'type_id' : "live_end",
                    'username' : user_name,
                }
                
                send_discord_webhook(data)

                aliases = {
                    '{broadcaster}' : user_name
                }

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }
                
                append_notice(data_append)

                if message_data[type_id]['status']:
                    
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                                
            elif subscription_type == 'channel.subscribe':  
                
                type_id = 'sub'

                event = data['payload']['event']
                
                user_name = event['user_name']

                data = {
                    'type_id' : 'sub',
                    'username' : user_name,
                }

                aliases = {
                    '{username}' : user_name
                }
                    
                end_sub_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/endsub.json", "load")

                if user_name not in end_sub_list:

                    data_append = {
                        "type" : "event",
                        "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                        "user_input" : '',
                    }

                    append_notice(data_append)
                    send_discord_webhook(data)

                    if message_data[type_id]['status']:
                        send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                else:

                    end_sub_list.remove(user_name)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/endsub.json", "save",end_sub_list)

            elif subscription_type == 'channel.subscription.gift':  

                type_id = 'giftsub'

                event = data['payload']['event']
                
                aliases = {
                    '{tier}' : str(event['tier']),
                    '{total}' : str(event['total']),
                    '{cumulative_total}' :str(event['user_name']),
                    '{is_anonymous}' : str(event['user_name']),
                    '{username}' : str(event['user_name'])
                }
                
                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }
                
                data_discord = {
                    "type_id" : "giftsub",
                    "user_name" : event['user_name'],
                    "tier" : event['tier'],
                    "total" : event['total'],
                    "cumulative_total" : event['cumulative_total'],
                    "is_anonymous" : event['is_anonymous'],
                }

                send_discord_webhook(data_discord)
                append_notice(data_append)

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
    
            elif subscription_type == 'channel.subscription.end':  
                    
                type_id = 'subend'

                event = data['payload']['event']
                
                user_name = event['user_name']
                tier = event['tier']
                
                aliases = {
                    '{username}' : event['user_name']
                }

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    'type_id' : 'subend',
                    'user_name' : user_name,
                }
                
                send_discord_webhook(data_discord)
                append_notice(data_append)

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')

                end_sub_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/endsub.json", "load")

                if user_name not in end_sub_list:

                    end_sub_list.append(user_name)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/endsub.json", "save",end_sub_list)
                    
            elif subscription_type == 'channel.subscription.message':  

                type_id = 'resub'

                event = data['payload']['event']

                user_name = event['user_name']
                
                tier = event['tier']
                message_text = event['message']['text']
                cumulative_months = event['cumulative_months']
                streak_months = event['streak_months']
                duration_months = event['duration_months']
                
                aliases = {
                    '{username}' : user_name,
                    '{tier}' : str(tier),
                    '{total_months}' : str(cumulative_months),
                    '{streak_months}' : str(streak_months),
                    '{months}' : str(duration_months),
                    '{user_mesage}' : str(message_text)
                }

                data_discord = {
                    'type_id' : 'resub',
                    'username' : user_name,
                    'tier' : str(tier),
                    'total_months' : str(cumulative_months),
                    'streak_months': str(streak_months),
                    'months': str(duration_months),
                    'user_mesage' : str(message_text)
                }
                
                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }
                
                send_discord_webhook(data_discord)
                append_notice(data_append)

                if message_data[type_id]['status']:

                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')

            elif subscription_type == 'channel.raid':  

                type_id = 'raid'

                event = data['payload']['event']
                
                username = event['from_broadcaster_user_name']
                viewers = event['viewers']
            

                aliases = {
                    '{username}' : username,
                    '{specs}' : str(viewers),
                }

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    "type_id" : "raid",
                    "specs" : str(viewers),
                    "username" : username,
                }
                
                send_discord_webhook(data_discord)
                append_notice(data_append)  

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                            
            elif subscription_type == 'channel.cheer':  

                type_id = 'bits'

                event = data['payload']['event']
                
                is_anonymous = event['is_anonymous']
                
                if is_anonymous == 'True':
                    user_name = "Anonymous"
                else:
                    user_name = event['user_name']

                message = event['message']
                bits = event['bits']
                
                    
                aliases = {
                    '{username}' : user_name,
                    '{amount}' : str(bits),
                }   

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }
                
                append_notice(data_append) 

                data_discord = {
                    'type_id' : 'bits',
                    'username' : user_name,
                    'amount' : str(bits)
                }

                send_discord_webhook(data_discord)

                if message_data[type_id]['status']:

                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')

            elif subscription_type == 'channel.ban':  
                
                type_id = 'ban'

                event = data['payload']['event']
                
                user_name = event['user_name']
                moderator_user_name = event['moderator_user_name']
                reason = event['reason']

                banned_at = event['banned_at']
                ends_at = event['ends_at']
                
                is_permanent = event['is_permanent']

                banned_at = datetime.datetime.fromisoformat(banned_at)
                ends_at = datetime.datetime.fromisoformat(ends_at)
                interval = ends_at - banned_at

                if is_permanent:

                    time = 'Permanente'

                else:

                    time = interval

                aliases = {
                    '{reason}' : reason,
                    '{moderator}' : moderator_user_name,
                    '{username}' : user_name,
                    '{time}' : str(time)
                }   
                                
                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    'type_id' : 'ban',
                    'username' : user_name,
                    'reason' : reason,
                    'moderator' : moderator_user_name,
                    'time' : str(time)
                }
                
                send_discord_webhook(data_discord)
                append_notice(data_append)

                if message_data[type_id]['status']:

                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                
            elif subscription_type == 'channel.unban':  
                
                type_id = 'unban'

                event = data['payload']['event']
            
                user_name = event['user_name']
                moderator_user_name = event['moderator_user_name']
                
                aliases = {
                    '{moderator}' : moderator_user_name,
                    '{username}' : user_name
                } 

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    "type_id" : "unban",
                    "username" : user_name,
                    "moderator" : moderator_user_name
                }

                send_discord_webhook(data_discord)
                append_notice(data_append) 

                if message_data[type_id]['status']:

                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                
            elif subscription_type == 'channel.poll.begin':  
                
                type_id = 'poll_start'

                event = data['payload']['event']

                ##POOL = ENQUETE
                
                title = event['title']
                choices = event['choices']
                current_id = event['id']
                bits_voting_status = event['bits_voting']['is_enabled']
                bits_voting_amount = event['bits_voting']['amount_per_vote']
                channel_points_voting_status = event['channel_points_voting']['is_enabled']
                channel_points_voting_amount = event['channel_points_voting']['amount_per_vote']
                start_at = event['started_at']
                ends_at = event['ends_at']
                

                aliases = {
                    '{title}': title,
                    '{choices}': choices,
                    '{current_id}': current_id,
                    '{bits_voting_status}': str(bits_voting_status),
                    '{bits_voting_amount}': str(bits_voting_amount),
                    '{channel_points_voting_status}': str(channel_points_voting_status),
                    '{channel_points_voting_amount}': str(channel_points_voting_amount),
                    '{start_at}': start_at,
                    '{ends_at}': ends_at
                }

                poll_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", "load")

                options_list = []
                poll_data['status'] = 'started'
                poll_data['current'] = current_id
                poll_data['title'] = title
                poll_data['time_start'] = start_at
                poll_data['time_end'] = ends_at

                for option in choices:
                    title = option['title']
                    choice_id = option['id']
                    option_data = {
                        "title": title, "id" : choice_id, "votes" : 0
                    }

                    options_list.append(option_data)
                    poll_data['options'] = options_list

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", "save",poll_data)
             
                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data = {
                    "type_id" : "poll_start",
                    "title" : title,
                    "choices" : choices,
                    "bits_status" : bits_voting_status,
                    "bits_amount" : bits_voting_amount,
                    "points_status" : channel_points_voting_status,
                    "points_amount" : channel_points_voting_amount,
                }

                
                send_discord_webhook(data)
                append_notice(data_append) 

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')
                
            elif subscription_type == 'channel.poll.progress':  
                
                type_id = 'poll_status'

                event = data['payload']['event']
                
                title = event['title']
                choices = event['choices']
                
                bits_voting_status = event['bits_voting']['is_enabled']
                bits_voting_amount = event['bits_voting']['amount_per_vote']
                channel_points_voting_status = event['channel_points_voting']['is_enabled']
                channel_points_voting_amount = event['channel_points_voting']['amount_per_vote']

                start_at = event['started_at']
                ends_at = event['ends_at']

                aliases = {
                    '{title}': title,
                    '{choices}': choices,
                    '{bits_voting_status}': str(bits_voting_status),
                    '{bits_voting_amount}': str(bits_voting_amount),
                    '{channel_points_voting_status}': str(channel_points_voting_status),
                    '{channel_points_voting_amount}': str(channel_points_voting_amount)
                }
                    
                poll_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", "load")

                options_list = []

                for option in choices:
                    title = option['title']
                    choice_id = option['id']
                    votes = option['votes']
                    option_data = {
                        "title": title, "id" : choice_id, "votes" : votes
                    }

                    options_list.append(option_data)
                    poll_data['options'] = options_list

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", "save",poll_data)

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type" : "event",
                    "message" : message_event,
                    "user_input" : '',
                }

                data = {
                    "type_id" : "poll_status",
                    "title" : title,
                    "choices" : choices,
                    "bits_status" : bits_voting_status,
                    "bits_amount" : bits_voting_amount,
                    "points_status" : channel_points_voting_status,
                    "points_amount" : channel_points_voting_amount
                }

                send_discord_webhook(data)

                if message_data[type_id]['status']:
                    message_chat = utils.replace_all(message_data[type_id]['response_chat'],aliases)
                    send_announcement(message_chat,'purple')
                
            elif subscription_type == 'channel.poll.end':
                
                type_id = 'poll_end'

                event = data['payload']['event']

                title = event['title']
                choices = event['choices']
                current_id = event['id']

                poll_status = event['status']
                bits_voting_status = event['bits_voting']['is_enabled']
                bits_voting_amount = event['bits_voting']['amount_per_vote']
                channel_points_voting_status = event['channel_points_voting']['is_enabled']
                channel_points_voting_amount = event['channel_points_voting']['amount_per_vote']

                start_at = event['started_at']
                ends_at = event['ended_at']

                aliases = {
                    '{title}': title,
                    '{choices}': choices,
                    '{current_id}': current_id,
                    '{poll_status}': poll_status,
                    '{bits_voting_status}': str(bits_voting_status),
                    '{bits_voting_amount}': str(bits_voting_amount),
                    '{channel_points_voting_status}': str(channel_points_voting_status),
                    '{channel_points_voting_amount}': str(channel_points_voting_amount)
                }

                poll_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", 'load')

                options_list = []
                poll_data['status'] = poll_status
                poll_data['current'] = current_id
                poll_data['title'] = title
                poll_data['time_start'] = start_at
                poll_data['time_end'] = ends_at

                for option in choices:
                    option_data = {
                        "title": option['title'], "id": option['id'], "votes": option['votes']
                    }
                    options_list.append(option_data)

                poll_data['options'] = options_list

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/poll_id.json", "save", poll_data)

                data = {
                    "type_id": "poll_end",
                    "title": title,
                    "choices": choices,
                    "bits_status": bits_voting_status,
                    "bits_amount": bits_voting_amount,
                    "points_status": channel_points_voting_status,
                    "points_amount": channel_points_voting_amount
                }

                send_discord_webhook(data)

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": '',
                }

                append_notice(data_append)

                if message_data[type_id]['status']:
                    message_chat = utils.replace_all(message_data[type_id]['response_chat'], aliases)
                    send_announcement(message_chat, 'purple')
                        
            elif subscription_type == 'channel.prediction.begin':
                
                type_id = 'prediction_start'

                pred_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", 'load')

                event = data['payload']['event']

                title = event['title']
                outcomes = event['outcomes']
                current_id = event['id']
                time_start = event['started_at']
                time_locks = event['locks_at']

                options_list = []
                pred_data['status'] = 'running'
                pred_data['current'] = current_id
                pred_data['title'] = title
                pred_data['time_start'] = time_start
                pred_data['time_locks'] = time_locks

                for outcome in outcomes:
                    option_data = {
                        outcome['title']: outcome['id']
                    }
                    options_list.append(option_data)

                pred_data['options'] = options_list

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", 'save', pred_data)

                data = {
                    'type_id': "prediction_start",
                    "title": title,
                    "outcomes": outcomes
                }

                send_discord_webhook(data)

                aliases = {
                    '{title}': title
                }

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": '',
                }

                if message_data[type_id]['status']:
                    message_chat = utils.replace_all(message_data[type_id]['response_chat'], aliases)
                    send_announcement(message_chat, 'purple')
      
            elif subscription_type == 'channel.prediction.progress':
                type_id = 'prediction_progress'

                event = data['payload']['event']

                title = event['title']
                outcomes = event['outcomes']

                aliases = {
                    '{title}': title,
                }

                data = {
                    'type_id': "prediction_progress",
                    "title": title,
                    "outcomes": outcomes
                }

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": '',
                }

                send_discord_webhook(data)

                if message_data[type_id]['status']:
                    message_chat = utils.replace_all(message_data[type_id]['response_chat'], aliases)
                    send_announcement(message_chat, 'purple')

            elif subscription_type == 'channel.prediction.lock':
                type_id = 'prediction_progress'

                event = data['payload']['event']

                pred_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", 'load')

                pred_data['status'] = 'locked'

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", "save", pred_data)

                title = event['title']
                outcomes = event['outcomes']

                data = {
                    'type_id': "prediction_progress",
                    'title': title,
                    'outcomes': outcomes
                }

                aliases = {
                    '{title}': title,
                }

                send_discord_webhook(data)

                toast('A votação do palpite foi encerrada.')

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": '',
                }

                if message_data[type_id]['status']:
                    message_chat = utils.replace_all(message_data[type_id]['response_chat'], aliases)
                    send_announcement(message_chat, 'purple')

            elif subscription_type == 'channel.prediction.end':
                
                type_id = 'prediction_end'

                event = data['payload']['event']

                title = event['title']
                outcomes = event['outcomes']

                winning_outcome_id = event['winning_outcome_id']

                if winning_outcome_id != "":
                    for outcome in event["outcomes"]:
                        if outcome["id"] == winning_outcome_id:
                            winner = outcome["title"]
                            channel_points = outcome["channel_points"]
                            break
                else:
                    channel_points = 0
                    winner = "Nenhum"

                data = {
                    'type_id': "prediction_end",
                    'title': title,
                    'outcome_win': winner,
                    'channel_points': channel_points,
                }

                pred_data = {
                    "status": "end",
                    "winner": winner
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/pred_id.json", "save", pred_data)

                send_discord_webhook(data)

                aliases = {
                    '{title}': title,
                }

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases)

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": '',
                }

                append_notice(data_append)

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'], aliases), 'purple')

            elif subscription_type == 'channel.goal.begin':
                
                type_id = 'goal_start'

                event = data['payload']['event']

                goal_type = event['type']
                description = event['description']
                current_amount = event['current_amount']
                target_amount = event['target_amount']
                started_at = event['started_at']

                if goal_type == "subscription":
                    goal_type = 'subscription_count'

                data_goal = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "load")

                data_goal[goal_type] = {
                    "type": goal_type,
                    "status" : "running",
                    "description": description,
                    "current_amount": current_amount,
                    "target_amount": target_amount,
                    "started_at": started_at
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", data_goal)

                if goal_type == "subscription_count":
                    goal_type = 'Inscrições'
                elif goal_type == "follow":
                    goal_type = 'Seguidores'

                aliases = {
                    "{target}": str(target_amount),
                    "{current}": str(current_amount),
                    "{description}": str(description),
                    "{type}": goal_type
                }

                message_event = utils.replace_all(str(utils.messages_file_load(f'event_goal_begin')), aliases)

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": '',
                }

                data_discord = {
                    'type_id': type_id,
                    'target': target_amount,
                    'current': current_amount,
                    'description': description,
                    'goal_type': goal_type
                }

                send_discord_webhook(data_discord)

                append_notice(data_append)

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'], aliases), 'purple')   
            
            elif subscription_type == 'channel.goal.progress':  

                type_id = 'goal_progress'

                event = data['payload']['event']
                
                goal_type = event['type']
                description = event['description']
                current_amount = event['current_amount']
                target_amount = event['target_amount']
                started_at = event['started_at']

                if goal_type == "subscription":
                    goal_type = 'subscription_count'
   
                data_goal = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "load")

                data_goal[goal_type] = {
                    "type" : goal_type,
                    "status" : "running",
                    "description" : description,
                    "current_amount" : current_amount,
                    "target_amount" : target_amount,
                    "started_at" : started_at
                }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save",data_goal)

                aliases = {
                    "{target}" : str(target_amount),
                    "{current}" : str(current_amount),
                    "{description}" : str(description),
                    "{type}" : goal_type
                } 

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple')  
  
            elif subscription_type == 'channel.goal.end':  
                    
                type_id = 'goal_end'

                event = data['payload']['event']
                
                goal_type = event['type']
                description = event['description']
                current_amount = event['current_amount']
                target_amount = event['target_amount']
                started_at = event['started_at']
                
                if goal_type == "subscription":
                    goal_type = 'subscription_count'

                data_goal = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "load")

                data_goal[goal_type] = {
                    "type" : goal_type,
                    "status" : "end",
                    "description" : description,
                    "current_amount" : current_amount,
                    "target_amount" : target_amount,
                    "started_at" : started_at
                }
                    
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save",data_goal)

                if goal_type == "subscription_count":
                    goal_type = 'Inscrições'

                elif goal_type == "follow":
                    goal_type = 'Seguidores'

                aliases = {
                    "{target}" : str(target_amount),
                    "{current}" : str(current_amount),
                    "{description}" : str(description),
                    "{type}" : goal_type
                }    

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    'type_id' : 'goal_end',
                    'target' : target_amount,
                    'current' : current_amount,
                    'description' : description,
                    'goal_type' : goal_type
                }
                
                send_discord_webhook(data_discord)
                append_notice(data_append) 

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple') 

            elif subscription_type == 'channel.shoutout.create':

                type_id = 'shoutout_start'

                event = data['payload']['event']

                broadcaster_user_name = event['broadcaster_user_name']
                moderator_user_name = event['moderator_user_name']
                
                to_broadcaster_user_name = event['to_broadcaster_user_name']

                viewer_count = event['viewer_count']


                aliases = {
                    "{broadcaster_user_name}": broadcaster_user_name,
                    "{moderator_user_name}": moderator_user_name,
                    "{to_broadcaster_user_name}": to_broadcaster_user_name,
                    "{viewer_count}": str(viewer_count)
                }

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    'type_id': 'shoutout_start',
                    'broadcaster': broadcaster_user_name,
                    'moderator': moderator_user_name,
                    'to_broadcaster': to_broadcaster_user_name,
                    'viewer_count': viewer_count
                }

                send_discord_webhook(data_discord)
                append_notice(data_append) 
                
                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple') 

            elif subscription_type == 'channel.shoutout.receive':
                
                type_id = 'shoutout_receive'

                event = data['payload']['event']

                broadcaster_user_name = event['broadcaster_user_name']
                from_broadcaster_user_name = event['from_broadcaster_user_name']

                aliases = {
                    "{broadcaster_user_name}": broadcaster_user_name,
                    "{from_broadcaster_user_name}": from_broadcaster_user_name
                }

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    'type_id': 'shoutout_receive',
                    'broadcaster': broadcaster_user_name,
                    'from_broadcaster' : from_broadcaster_user_name
                }

                send_discord_webhook(data_discord)
                append_notice(data_append) 

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple') 

            elif subscription_type == 'channel.shield_mode.begin':
                
                type_id = 'shield_start'

                event = data['payload']['event']

                broadcaster_user_name = event['broadcaster_user_name']
                moderator_user_name = event['moderator_user_name']
                
                aliases = {
                    "{broadcaster}": broadcaster_user_name,
                    "{moderator}": moderator_user_name
                }

                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    'type_id': 'shield_start',
                    'broadcaster': broadcaster_user_name,
                    'moderator' : moderator_user_name
                }

                send_discord_webhook(data_discord)
                append_notice(data_append) 

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple') 

            elif subscription_type == 'channel.shield_mode.end':
                
                type_id = 'shield_end'
                
                event = data['payload']['event']

                broadcaster_user_name = event['broadcaster_user_name']
                moderator_user_name = event['moderator_user_name']


                aliases = {
                    "{broadcaster}": broadcaster_user_name,
                    "{moderator}": moderator_user_name
                }
                data_append = {
                    "type" : "event",
                    "message" : utils.replace_all(str(utils.messages_file_load(f'event_{type_id}')), aliases),
                    "user_input" : '',
                }

                data_discord = {
                    'type_id': 'shield_end',
                    'broadcaster': broadcaster_user_name,
                    'moderator' : moderator_user_name
                }

                send_discord_webhook(data_discord)
                append_notice(data_append) 

                if message_data[type_id]['status']:
                    send_announcement(utils.replace_all(message_data[type_id]['response_chat'],aliases),'purple') 

            else:
                
                event = data['payload']['event']
        
        elif message_type == 'session_keepalive':
            pass

    except Exception as e:
        
        logging.error("Exception occurred", exc_info=True)


def on_resize(width, height):

    min_width = 1200 
    min_height = 600
    
    if width < min_width or height < min_height:
            
        toast('A janela não pode ser redimensionada para um tamanho menor.')

        window.resize(min_width, min_height)


def start_websocket():
    
    while True:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        
        if authdata.TOKEN() and authdata.USERNAME():
            
            def on_error(ws, message_error):

                if message_error == "[Errno 11001] getaddrinfo failed":
                    
                    ask = messagebox.showerror("Erro", "Erro de conexão, verifique a conexão com a internet e tente novamente.")
                    if ask == 'ok':
                        sys.exit(0)
                    else:
                        utils.error_log(message_error)
                
            def on_close(ws, close_status_code, close_msg):

                time.sleep(5)

                print('reconectando',close_status_code,close_msg)

                ws.run_forever()

            localhost = "ws://localhost:8080/ws"
            twitch = "wss://eventsub.wss.twitch.tv/ws"
            
            ws = websocket.WebSocketApp(twitch,on_message=on_message,on_error=on_error,on_close=on_close)

            ws.run_forever()
            
        else:
            
            time.sleep(10)


def start_obs():

    try:

        sucess_conn = obs_events.test_obs_conn()
        return sucess_conn

    except Exception as e:
        
        if not isinstance(e, TimeoutError):
            utils.error_log(e)

        return 'error'

     
def loaded():
    
    global loaded_status

    loaded_status = True

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

    if authdata.TOKEN() and authdata.USERNAME():
        
        autenticated = start_twitch()
        
        if autenticated:
            data = {"autenticated": "true"}
        else:
            data = {"autenticated": "false"}

        return json.dumps(data, ensure_ascii=False)
    
    else:
        data = {"autenticated": "false"}
        
        return json.dumps(data, ensure_ascii=False)


def webview_start_app(app_mode):

    global window, window_chat, window_events, window_chat_open

    def set_window_chat_open():
        global window_chat_open
        window_chat_open = True

    def set_window_chat_close():
        global window_chat_open
        window_chat_open = False

    def set_window_events_open():
        global window_events_open
        window_events_open = True

    def set_window_events_close():
        global window_events_open
        window_events_open = False

    debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/scopes.json", "load")
    debug_status = debug_data['debug']
        
    if app_mode == "normal":

        window = webview.create_window("RewardEvents", f"{utils.local_work('data_dir')}/web/index.html", width=1200, height=680, min_size=(1200, 680))

        window.events.closed += close
        window.events.resized += on_resize

        window.expose(loaded, on_message, command_fallback, timeout_user, userdata_py, chat_config,
            open_py, highlight_py, timer, update_check, sr_config_py, playlist_py, get_video_info,
            get_edit_data, disclosure_py, discord_config, responses_config,
            messages_config, not_config_py, clip, obs_config_py, queue, counter, giveaway_py, 
            timer_py, commands_py, create_action_save, goal_py, poll_py, prediction_py, 
            get_command_list, save_stream_info_py, get_stream_info_py, get_sources_obs, 
            get_filters_obs, update_scene_obs, select_file_py, get_redeem, 
            profile_info, get_chat_list, event_log, logout_auth, get_auth_py, send,
            send_announcement, save_access_token, start_auth_window,webview_start_app,get_users_info,
            start_obs,create_source,reward)

        webview.start(storage_path=utils.local_work('data_dir'),private_mode=True,debug=debug_status,http_server=True,http_port=7000)
        
    elif app_mode == "chat":
        
        window_chat = webview.create_window('RewardEvents Chat', '')
        window_chat.load_url('http://localhost:7000/chat.html')
        window_chat.events.loaded += set_window_chat_open
        window_chat.events.closed += set_window_chat_close

        window_chat.expose(send,send_announcement,get_chat_list,open_py)
    
    elif app_mode == "events":
        
        window_events = webview.create_window('RewardEvents Eventos', '')
        window_events.load_url('http://localhost:7000/events.html')

        window_events.events.loaded += set_window_events_open
        window_events.events.closed += set_window_events_close

        window_events.expose(event_log)


def bot():

    global chat

    while True:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        
        if loaded_status and authdata.TOKEN() and authdata.USERNAME() and authdata.TOKENBOT():

            toast('Conectando ao chat')

            chat = TwitchBot(callback=command_fallback,TOKEN=authdata.TOKENBOT(), USERNAME=authdata.BOTUSERNAME(),CHANNEL=authdata.USERNAME())
            chat.connect()

        else:
            
            time.sleep(5)
 

def start_app():

          
    def start_log_files():

        MAX_LOG_SIZE = 1024 * 1024 * 10  # 10 MB

        log_file_path = f"{utils.local_work('appdata_path')}/error_log.txt"

        if os.path.exists(log_file_path):
            log_file_size = os.path.getsize(log_file_path)
            if log_file_size > MAX_LOG_SIZE:
                with open(log_file_path, 'r',encoding='UTF-8') as f:
                    lines = f.readlines()
                with open(log_file_path, 'w',encoding='UTF-8') as f:
                    f.writelines(lines[-1000:]) 

        user_join_sess_load = {
            'spec': [],
            'bot' :[]
        }  
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "load")

        if len(event_log_data['event_list']) > 100:
            event_list = event_log_data['event_list'][-100:]
            event_log_data['event_list'] = event_list
            
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_sess_join.json", "save",user_join_sess_load)
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json", "save",event_log_data)
    
    if utils.get_files_list():

        download_badges()
        start_log_files()
        
        pygame.init()
        pygame.mixer.init()
        
        threading.Thread(target=bot, args=(), daemon=True).start()
        threading.Thread(target=get_spec, args=(), daemon=True).start()
        threading.Thread(target=loopcheck, args=(), daemon=True).start()
        threading.Thread(target=timer, args=(), daemon=True).start()
        threading.Thread(target=start_websocket, args=(), daemon=True).start()
        threading.Thread(target=sk.start_server, args=('localhost', 7688), daemon=True).start()

        if getattr(sys, 'frozen', False):
            utils.splash_close()

        webview_start_app('normal')


if lock_manager.already_running:

    error_message = "O programa já está em execução, aguarde."
    messagebox.showerror("Erro", error_message)
    sys.exit(0)

else:
    start_app()