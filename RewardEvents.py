import sys,os,platform
import subprocess
from collections import namedtuple
import utils
import webview
import eel
import threading
import validators
import webbrowser
import websocket
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
import datetime
import pytz
import re

from bs4 import BeautifulSoup as bs

from ChatIRC import TwitchBot

from dotenv import load_dotenv
from pytube import Playlist, YouTube, Search
from io import BytesIO
from gtts import gTTS
from tkinter import filedialog as fd
from requests.structures import CaseInsensitiveDict
from random import randint

from discord_webhook import DiscordWebhook, DiscordEmbed

from twitchAPI.twitch import Twitch, AuthScope, PredictionStatus, PollStatus
from flask import Flask, request


extDataDir = os.getcwd()

ffmpeg_loc = '.'

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS
        ffmpeg_loc = extDataDir

load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

clientid = os.getenv('CLIENTID')
appdata_path = os.getenv('APPDATA')

global caching, loaded_status, chat, window, twitch_api,bot_loaded


chat_active = False
caching = 0
loaded_status = 0
bot_loaded = 0

authdata = auth.auth_data(f'{appdata_path}/rewardevents/web/src/auth/auth.json')

app = Flask(__name__)

@app.route("/")
def receive_url():

    with open("web/auth_sucess.html", "r") as html:
        soup = bs(html, 'html.parser')
        
    return soup.prettify('utf-8')


@eel.expose
def save_access_token(type_id: str, token: str) -> None:
    """Saves a token for a given type_id to a JSON file.

    Args:
        type_id: The type of token, either 'streamer', 'bot', or 'streamer_asbot'.
        token: The token to be saved.

    Raises:
        ValueError: If type_id is not one of the valid options.
    """
    # Define constants
    CLIENT_ID = "your_client_id"
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
    AUTH_FILE = f"{appdata_path}/rewardevents/web/src/auth/auth.json"

    # Load data from JSON file
    with open(AUTH_FILE) as auth_file:
        data = json.load(auth_file)

    # Create Twitch API object
    twitch_api = Twitch(CLIENT_ID, authenticate_app=False)
    twitch_api.auto_refresh_auth = False

    # Set user authentication based on type_id
    if type_id == "streamer":
        username = data["USERNAME"]
        twitch_api.set_user_authentication(token, SCOPES)
        
    elif type_id == "bot":
        username = data["BOTUSERNAME"]
        twitch_api.set_user_authentication(token, SCOPES)

    elif type_id == "streamer_asbot":
        username = data["USERNAME"]
        twitch_api.set_user_authentication(token, SCOPES)

    else:
        raise ValueError(f"Invalid type_id: {type_id}")

    # Get user id from Twitch API
    user_id_resp = twitch_api.get_users(logins=[username])["data"][0]["id"]

    # Update data based on type_id
    if type_id == "streamer":
        data["TOKEN"] = token
        data["BROADCASTER_ID"] = user_id_resp

    elif type_id == "bot":
        data["TOKENBOT"] = token
        data["BOT_ID"] = user_id_resp

    elif type_id == "streamer_asbot":
         data["TOKEN"] = token
         data["BROADCASTER_ID"] = user_id_resp 
         data["TOKENBOT"] = token

    # Save updated data to JSON file   
    with open(AUTH_FILE, "w") as out_file:
        json.dump(data, out_file, indent=6)


@eel.expose
def start_auth_window(username,type_id):

    """Exposes a python function to javascript and opens an OAuth URI in a web browser.

    Args:
        username (str): The username of the user or the bot.
        type_id (str): The type of the user: 'streamer', 'bot' or 'streamer_asbot'.

    Raises:
        FileNotFoundError: If the json files for authentication or authorization are not found.
        ValueError: If the type_id is not one of the valid options.
    """

    with open(f"{appdata_path}/rewardevents/web/src/auth/auth.json") as auth_file:
        data = json.load(auth_file)
    # Intern strings for efficiency
    type_id = sys.intern(type_id)
    if type_id == 'streamer':
        data['USERNAME'] = username
    elif type_id == 'bot':
        data['BOTUSERNAME'] = username
    elif type_id == 'streamer_asbot':
        data['USERNAME'] = username
        data['BOTUSERNAME'] = username

    # Write to file only once instead of multiple times
    with open(f"{appdata_path}/rewardevents/web/src/auth/auth.json", "w") as out_file:
        json.dump(data, out_file, indent=6)

    with open(f'{appdata_path}/rewardevents/web/src/auth/scopes.json', 'r') as file:
        scope_auth = json.load(file)

    redirect_uri = scope_auth['redirect_uri']
    url = scope_auth['url']
    response_type = scope_auth['response_type']
    force_verify = scope_auth['force_verify']

    # Use generator expression instead of list comprehension for scope
    scope_list = scope_auth['scopes']

    scope = '+'.join(scope for scope in scope_list)

    oauth_uri = f"{url}oauth2/authorize?response_type={response_type}&force_verify={force_verify}&client_id={clientid}&redirect_uri={redirect_uri}&scope={scope}"
    webbrowser.open(oauth_uri)


@eel.expose
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
    url = f"https://api.twitch.tv/helix/chat/announcements?broadcaster_id={authdata.BROADCASTER_ID()}&moderator_id={authdata.BOT_ID()}"
    
    headers = {
        "Authorization": f"Bearer {authdata.TOKENBOT()}",
        "Client-Id": clientid,
        "Content-Type": "application/json"
    }
    data = json.dumps({"message": message, "color": color})

    response = req.post(url, headers=headers, data=data.encode('utf-8'))

    return response.ok # Returns True if status code is 200


@eel.expose
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
    
    if loaded_status == 1:

        # Check if the message is an announcement command
        if message.startswith('/announce'):
            # Get the color from the command or use primary as default
            color = message.split('/')[1].replace('announce', '') or 'primary'
            # Get the actual message from the command
            announcement = message.split(color)[1]
            # Send the announcement using the send_announcement function
            send_announcement(announcement, color)

        else:
            
            # Send the message using the twitchio chat object
            chat.send(message)
            
            # Load the chat configuration from a json file
            with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json','r',encoding='utf-8') as chat_file:
                chat_data = json.load(chat_file)

            now = datetime.datetime.now()
            
            # Format and show the time according to the configuration
            if chat_data['data-show'] == 1:
                format = chat_data['time-format']
                if chat_data['type-data'] == "passed":
                    chat_time = now.strftime('%Y-%m-%dT%H:%M:%S')
                elif chat_data['type-data'] == "current":
                    chat_time = now.strftime(format)
            else: 
                chat_time = ''
                    
            
            # Create a dictionary with the response data and configuration
            data_res = {
                "response": 0,
                "frist_message" : 0,
                "appply_colors" : chat_data["appply-colors"],
                "appply_no_colors" : chat_data["appply-no-colors"],
                "color_apply" : chat_data["color-apply"],
                "show_badges" : chat_data["show-badges"],
                "wrapp_message" : chat_data["wrapp-message"],
                "font_size" : chat_data["font-size"],
                'chat_time' : f'{chat_time}',
                'type': 'PRIVMSG',
                "color": '',
                "display_name": authdata.BOTUSERNAME(),
                "user_name": authdata.BOTUSERNAME(),
                "badges" : f'<img class="badges" src="https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1" />', 
                "mod": 1,
                "vip": 0,
                "subscriber": 0,
                "user_id": authdata.BROADCASTER_ID(),
                "message": message,
                "user_replied" : '',
                "message_replied" : '',
                "data_show" : chat_data["data-show"],
                "type_data" : chat_data["type-data"],
                "block_color" : chat_data["block-color"],
                
             }
             
            message_data_dump = json.dumps(data_res, ensure_ascii=False)
            eel.append_message(message_data_dump)
        

def send_discord_webhook(data):
    
    """Send a discord webhook by a type message.

    Args:
        data (dict): A dictionary containing the type_id and other relevant data for the webhook.

    Raises:
        FileNotFoundError: If the discord.json file is not found.
        discord_webhook.DiscordWebhookException: If the webhook execution failed for any reason.
    """

    type_id = data['type_id']

    with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'r', encoding='utf-8') as discord_config_file:
        discord_config_data = json.load(discord_config_file)

    webhook_status = discord_config_data[type_id]['status']
    webhook_color = discord_config_data[type_id]['color']
    webhook_content = discord_config_data[type_id]['content']
    webhook_url = discord_config_data[type_id]['url']
    webhook_title = discord_config_data[type_id]['title']
    webhook_description = discord_config_data[type_id]['description']

    if webhook_status == 1 and not webhook_url == "":
        
        
        if type_id == 'clips_create':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   
            
            clip_id = data['clip_id']
            username = data['username']
            
            aliases = {
                '{url}' : f'https://clips.twitch.tv/{clip_id}',
                '{user}' : username
            }
            
            webhook_title = utils.replace_all(webhook_title, aliases)
            webhook_description = utils.replace_all(webhook_description, aliases)
            
            embed = DiscordEmbed(
                title=webhook_title,
                description= webhook_description,
                color= webhook_color
            )

            webhook.add_embed(embed)
            webhook.execute() 

        if type_id == 'clips_edit':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

            clip_id = data['clip_id']
            username = data['username']
            
            aliases = {
                '{url}' : f'https://clips.twitch.tv/{clip_id}/edit',
                '{user}' : username
            }
            
            webhook_title = utils.replace_all(webhook_title, aliases)
            webhook_description = utils.replace_all(webhook_description, aliases)
            
            embed = DiscordEmbed(
                title=webhook_title,
                description= webhook_description,
                color= webhook_color
            )

            webhook.add_embed(embed)
            webhook.execute() 

        elif type_id == 'follow':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

            username = data['follow_name']
            
            aliases = {
                '{user}' : username
            }
            
            webhook_title = utils.replace_all(webhook_title, aliases)
            webhook_description = utils.replace_all(webhook_description, aliases)
            
            embed = DiscordEmbed(
                title=webhook_title,
                description= webhook_description,
                color= webhook_color
            )

            webhook.add_embed(embed)
            webhook.execute() 

        elif type_id == 'sub':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')

            webhook.add_embed(embed)
            webhook.execute() 

        elif type_id == 'live_start':
            
            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

            response = twitch_api.get_streams(first=1,user_id=authdata.BROADCASTER_ID())
            
            title = response['data'][0]['title']
            game = response['data'][0]['game_name']
            viewer_count = response['data'][0]['viewer_count']
            is_mature = response['data'][0]['viewer_count']
            thumb_url = response['data'][0]['thumbnail_url']
            

            embed = DiscordEmbed(
                title=webhook_title,
                description=webhook_description,
                color=webhook_color
            )
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')
            
            embed.set_image(url=thumb_url)
            embed.add_embed_field(name='Titulo', value=title,inline=False)
            embed.add_embed_field(name='Jogo', value=game,inline=False)
            embed.add_embed_field(name='Espectadores', value=viewer_count,inline=True)
            embed.add_embed_field(name='+18?', value=is_mature,inline=True)

            webhook.add_embed(embed)
            webhook.execute() 
                                   
        elif type_id == 'live_cat':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

            response = twitch_api.get_streams(first=1,user_id=authdata.BROADCASTER_ID())
            
            if 'send_offline' in data:
                
                send_offline = data['send_offline']
                
                if len(response['data']) > 1 or send_offline == 1:
                
                    title = data['title']
                    tag = data['tag']  
                            
                    aliases = {
                        '{title}' : title,
                        '{tag}' : tag
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                    embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')
                    
                    embed.add_embed_field(name='Titulo', value=title,inline=False)
                    embed.add_embed_field(name='Jogo', value=tag,inline=False)

                    webhook.add_embed(embed)
                    webhook.execute() 
                    
                elif len(response['data']) > 1 != '':
                    
                    title = data['title']
                    tag = data['tag']  
                            
                    aliases = {
                        '{title}' : title,
                        '{tag}' : tag
                    }
                    
                    webhook_title = utils.replace_all(webhook_title, aliases)
                    webhook_description = utils.replace_all(webhook_description, aliases)
                    
                    embed = DiscordEmbed(
                        title=webhook_title,
                        description= webhook_description,
                        color= webhook_color
                    )
                    
                    embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')
                    
                    embed.add_embed_field(name='Titulo', value=title,inline=False)
                    embed.add_embed_field(name='Jogo', value=tag,inline=False)

                    webhook.add_embed(embed)
                    webhook.execute() 

        elif type_id == 'live_end':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')

            webhook.add_embed(embed)
            webhook.execute()     

        elif type_id == 'poll_start':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            
            if points_status == 1:
                points_status = 'Sim'
            else:
                points_status = 'Não'
                
            
            if bits_voting == 1:
                bits_voting = 'Sim'
            else:
                bits_voting = 'Não'
                
            webhook_title = utils.replace_all(webhook_title, aliases)
            webhook_description = utils.replace_all(webhook_description, aliases)
            
            embed.add_embed_field(name=f'Votação com pontos do canal ?', value=points_status,inline=False)
            embed.add_embed_field(name=f'Votação com bits ?', value=bits_voting,inline=False)
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')
            
            op_count = 0
            
            for option in choices:
                title_op = option['title']
                op_count += 1
                embed.add_embed_field(name=f'Opção {op_count}', value=title_op,inline=False)

            webhook.add_embed(embed)
            webhook.execute() 

        elif type_id == 'poll_status':
            
            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            
            if points_status == 1:
                points_status = 'Sim'
            else:
                points_status = 'Não'
                
            
            if bits_voting == 1:
                bits_voting = 'Sim'
            else:
                bits_voting = 'Não'
            
            webhook_title = utils.replace_all(webhook_title, aliases)
            webhook_description = utils.replace_all(webhook_description, aliases)
            
            embed.add_embed_field(name=f'Votação com pontos do canal ?', value=f"Status : {points_status} | Pontos para votar: {points_amount}",inline=False)
            embed.add_embed_field(name=f'Votação com bits ?', value=f"Status : {bits_voting} | Bits para votar: {bits_amount}",inline=False)
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')
            
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

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            
            if points_status == 1:
                points_status = 'Sim'
            else:
                points_status = 'Não'
                
            
            if bits_voting == 1:
                bits_voting = 'Sim'
            else:
                bits_voting = 'Não'
            
            webhook_title = utils.replace_all(webhook_title, aliases)
            webhook_description = utils.replace_all(webhook_description, aliases)
            
            embed.add_embed_field(name=f'Votação com pontos do canal ?', value=f"Status : {points_status} | Pontos para votar: {points_amount}",inline=False)
            embed.add_embed_field(name=f'Votação com bits ?', value=f"Status : {bits_voting} | Bits para votar: {bits_amount}",inline=False)
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')
            
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

        elif type_id == 'prediction_start':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')

            webhook.add_embed(embed)
            webhook.execute()

        elif type_id == 'prediction_progress':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')

            webhook.add_embed(embed)
            webhook.execute()

        elif type_id == 'prediction_end':

            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content   

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
            embed.set_author(name='RewardEvents', url='https://ggtec.netlify.app', icon_url='https://ggtec.netlify.app/assets/img/about.png')

            webhook.add_embed(embed)
            webhook.execute()


@eel.expose
def get_auth_py(type_id):
    """Exposes a python function to javascript and returns an authentication value based on the type_id.

    Args:
        type_id (str): The type of authentication value to be returned. Valid values are: 'USERNAME', 'TOKEN', 'BROADCASTER_ID', 'CLIENTID', 'TOKENBOT', 'BOTNAME'.

    Returns:
        str: The authentication value corresponding to the type_id.

    Raises:
        ValueError: If the type_id is not valid.
    """
    
    # Use a dictionary to map the type_id to the authentication value
    auth_values = {
        'USERNAME': authdata.USERNAME(),
        'TOKEN': authdata.TOKEN(),
        'BROADCASTER_ID': authdata.BROADCASTER_ID(),
        'CLIENTID': clientid,
        'TOKENBOT': authdata.TOKEN(),
        'BOTNAME': authdata.BOTUSERNAME()
    }
    
    # Check if the type_id is valid and return the value or raise an exception
    if type_id in auth_values:
        return auth_values[type_id]
    else:
        raise ValueError(f"Invalid type_id: {type_id}")


@eel.expose
def log_data(data):
    
    with open(f'{appdata_path}/rewardevents/web/src/chat_log.txt','a',encoding='utf-8') as chat_log:
        chat_log.write(f'{data} \n')
     
        
@eel.expose
def minimize():
    window.minimize()


@eel.expose
def logout_auth():
    data = {'USERNAME': '',
            'BROADCASTER_ID': '',
            'REFRESH_TOKEN': '',
            'TOKENBOT':'',
            'BOTUSERNAME': ''
            }

    with open(f"{appdata_path}/rewardevents/web/src/auth/auth.json", "w") as logout_file:
        json.dump(data, logout_file, indent=6)

    close('normal')


@eel.expose
def get_spec():
    
    while True:
        
        try:
            
            if loaded_status == 1 and bot_loaded == 1:
                
                data_count = twitch_api.get_streams(user_login=[authdata.USERNAME()])
                data_count_keys = data_count['data']

                with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as timer_data_file:
                    timer_data = json.load(timer_data_file)

                message_key = timer_data['LAST']
                message_list = timer_data['MESSAGES']

                if message_key in message_list.keys():
                    last_timer = message_list[message_key]['message']
                else:
                    last_timer = 'Nenhuma mensagem enviada'
                    
                if not data_count_keys:

                    data_time = {
                        'specs': 'Offline',
                        'time': 'Offline',
                        'follow': '',
                        'last_timer': last_timer,
                    }

                    data_time_dump = json.dumps(data_time, ensure_ascii=False)
                    eel.receive_live_info(data_time_dump)
                
                    time.sleep(600)

                else:

                    count = data_count['data'][0]['viewer_count']
                    started = data_count['data'][0]['started_at']
                    
                    time_in_live = utils.calculate_time(started)
                    
                    h = time_in_live['hours']
                    m = time_in_live['minutes']
                    
                    h = "{:02d}".format(int(h))
                    m = "{:02d}".format(int(m))
                    
                    time_live = f"{h}:{m}"

                    data_time = {
                        'specs': count,
                        'time': time_live,
                        'follow': '',
                    }

                    data_time_dump = json.dumps(data_time, ensure_ascii=False)
                    eel.receive_live_info(data_time_dump)
                    
                    time.sleep(600)
                
            else:
                
                time.sleep(5)

        except Exception as e:

            utils.error_log(e)

            data_time = {
                'specs': 'Offline',
                'time': 'Offline',
                'follow': '',
            }

            data_time_dump = json.dumps(data_time, ensure_ascii=False)
            eel.receive_live_info(data_time_dump)
            time.sleep(600)

    
@eel.expose
def get_chat_list():
    
    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_sess_join.json', 'r' , encoding='utf-8') as user_list_file:
        user_list_data = json.load(user_list_file)
    
    data = {
        'user_list': user_list_data['spec'],
        'bot_list': user_list_data['bot'],
    }
    
    data_dump = json.dumps(data, ensure_ascii=False)

    return data_dump
      
        
@eel.expose
def profile_info():
    
    if authdata.TOKEN() and authdata.TOKENBOT():
        
        user = twitch_api.get_users(logins=[authdata.USERNAME()])

        resp_user_id = user['data'][0]['id']
        resp_display_name = user['data'][0]['display_name']
        resp_login_name = user['data'][0]['login']
        resp_email = user['data'][0]['email']
        resp_profile_img = user['data'][0]['profile_image_url']

        profile_img = req.get(resp_profile_img).content

        with open(f'{appdata_path}/rewardevents/web/src/profile.png', 'wb') as profile_image:
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
def get_redeem(type_id):

    if type_id == 'del' or type_id == "edit":

        list_titles = {"redeem": []}
        path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
        path = json.load(path_file)

        for key in path:
            list_titles["redeem"].append(key)

        list_titles_dump = json.dumps(list_titles, ensure_ascii=False)

        path_file.close()

        return list_titles_dump
    
    else:

        list_titles = {"redeem": []}
        
        with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8') as path_file:
            path = json.load(path_file)

        with open(f'{appdata_path}/rewardevents/web/src/counter/config.json', 'r', encoding='utf-8') as path_counter_file:
            path_counter = json.load(path_counter_file)

        counter_redeem = path_counter['redeem']

        with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'r', encoding='utf-8') as path_giveaway_file:
            path_giveaway = json.load(path_giveaway_file)

        giveaway_redeem = path_giveaway['redeem']

        list_rewards = twitch_api.get_custom_reward(broadcaster_id=authdata.BROADCASTER_ID())
        
        for indx in list_rewards['data'][0:]:
            
            if type_id == 'counter': 

                if indx['title'] not in path and indx['title'] != giveaway_redeem:
                    list_titles["redeem"].append(indx['title'])
                    
            elif type_id == 'giveaway':
                
                if indx['title'] not in path and indx['title'] != counter_redeem:
                    list_titles["redeem"].append(indx['title'])
                
            else:
                if indx['title'] not in path and indx['title'] != giveaway_redeem and indx['title'] != counter_redeem:
                    list_titles["redeem"].append(indx['title'])
                
        list_titles_dump = json.dumps(list_titles, ensure_ascii=False)

        return list_titles_dump


@eel.expose
def get_edit_type_py(redeem_name):
    with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8') as path_file:
        path = json.load(path_file)

    redeem_type = path[redeem_name]['type']

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
        initialdir=f'{appdata_path}/rewardevents/web/src/files',
        filetypes=filetypes)

    return folder


@eel.expose
def select_file_video_py():
    filetypes = (
        ('video files', '*.mp4'),
        ('gif files', '*.gif'),
        ('All files', '*.*')
    )

    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    folder = fd.askopenfilename(
        initialdir=f'{appdata_path}/rewardevents/web/src/files',
        filetypes=filetypes)

    return folder


@eel.expose
def select_file_image_py():
    filetypes = (
        ('png files', '*.png'),
        ('gif files', '*.gif')
    )

    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    folder = fd.askopenfilename(
        initialdir=f'{appdata_path}/rewardevents/web/src/files',
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


@eel.expose
def get_stream_info_py():
    
    resp_stream_info = twitch_api.get_channel_information(authdata.BROADCASTER_ID())
    
    title = resp_stream_info['data'][0]['title']
    game = resp_stream_info['data'][0]['game_name']
    game_id = resp_stream_info['data'][0]['game_id']
    tag_list = resp_stream_info['data'][0]['tags']
    
    with open(f'{appdata_path}/rewardevents/web/src/games/games.json', 'r', encoding='utf-8') as file_games:
        games_data = json.load(file_games)
        
    with open(f'{appdata_path}/rewardevents/web/src/games/tags.json', 'r', encoding='utf-8') as file_tags:
        tags_data = json.load(file_tags)
        
    data = {
        'game_name': game,
        'game_id': game_id,
        'title': title,
        'tag': tag_list,
        'game_list': games_data,
        'tag_list': tags_data
    }
    
    stream_info_dump = json.dumps(data, ensure_ascii=False)

    return stream_info_dump


@eel.expose
def save_stream_info_py(data):
    
    data = json.loads(data)
    
    title = data['title']
    game = data['game']
    tags = data['tags']
    send_discord = data['discord']
    send_offline = data['offline']
    
    headers = {
        'Authorization': f'Bearer {authdata.TOKEN()}',
        'Client-Id': clientid,
        'Content-Type': 'application/json',
    }

    params = {
        'broadcaster_id': authdata.BROADCASTER_ID(),
    }

    json_data = {
        'game_id': game,
        'title': title,
        'broadcaster_language': '',
        'tags': tags,
    }
    
    response = req.patch('https://api.twitch.tv/helix/channels', params=params, headers=headers, json=json_data)
    
    
    with open(f'{appdata_path}/rewardevents/web/src/games/games_new.json', 'r',encoding='utf-8') as games_file:
        games_data = json.load(games_file)
        
    game_dc = games_data[game]['name']
    
    data_discord = {
        'type_id' : 'live_cat',
        'title': title,
        'tag' : game_dc,
        'send_discord': send_discord,
        'send_offline' : send_offline
    }
    
    if send_offline == 1:
        send_discord_webhook(data_discord)
    
    if response.status_code == 204:
        eel.toast_notifc('success')
    else:
        eel.toast_notifc(f'error {response.json()}')
        
    
def create_command_redeem(data,type_id):
    
    if type_id == "create":
        
        command_delay = data['command_delay']
        
        if command_delay == '':
            command_delay = 0
            
        command_status = 1
        command_value = data['command_value']
        redeem_value = data['redeem_value']
        user_level_value = data['user_level_value']

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', 'r', encoding='utf-8') as commands_file:
            new_data_command = json.load(commands_file)

        new_data_command[command_value.lower().strip()] = {
            'status' : command_status,
            'delay' : command_delay,
            'last_use': 0,
            'redeem': redeem_value, 
            'user_level': user_level_value
        }

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', 'w', encoding='utf-8') as commands_file_write:
            json.dump(new_data_command, commands_file_write, indent=6, ensure_ascii=False)
       
    elif type_id == "edit":
        
        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        command_old = data['old_command']
        command_new = data['command']
        command_status = data['command_status']
        command_delay = data['delay']
        command_redeem = data['redeem']
        command_user_level = data['user_level']
        
        if command_old != '':
            del command_data[command_old.strip()]

        if command_new != "":
            
            command_data[command_new.lower().strip()] = {
                'last_use': 0,
                'status' : int(command_status),
                'delay' : int(command_delay),
                'redeem': command_redeem,
                'user_level': command_user_level
            }

            with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', 'w', encoding='utf-8') as command_file_write:
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)


@eel.expose
def prediction_py(data):

    data_receive = json.loads(data)
    type_id = data_receive['type_id']

    if type_id == 'start':

        titlerec = data_receive['title']
        options = data_receive['options']
        duration = int(data_receive['duration'])
        discord = int(data_receive['discord'])

        with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'r', encoding='utf-8') as discord_data_file:
            discord_data = json.load(discord_data_file)
        
            discord_data['prediction_start']['status'] = discord
            discord_data['prediction_progress']['status'] = discord
            discord_data['prediction_end']['status'] = discord

            with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'w', encoding='utf-8') as discord_data_file:
                json.dump(discord_data, discord_data_file, indent=6, ensure_ascii=False)

        twitch_api.create_prediction(
            authdata.BROADCASTER_ID(),
            title=titlerec,
            outcomes=options,
            prediction_window=int(duration)
        )

    elif type_id == 'get':

        with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'r', encoding='utf-8') as pred_file:
            pred_data = json.load(pred_file)

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

            data_dump = json.dumps(data)

        return data_dump

    elif type_id == 'lock':

        with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'r', encoding='utf-8') as pred_file:
            pred_data = json.load(pred_file)

        pred_id = pred_data['current']

        twitch_api.end_prediction(authdata.BROADCASTER_ID(),prediction_id=pred_id,status=PredictionStatus.LOCKED)

    elif type_id == 'cancel':

        with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'r', encoding='utf-8') as pred_file:
            pred_data = json.load(pred_file)

        pred_id = pred_data['current']

        twitch_api.end_prediction(authdata.BROADCASTER_ID(),prediction_id=pred_id,status=PredictionStatus.CANCELED)
    
    elif type_id == 'send':
        
        with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'r', encoding='utf-8') as pred_file:
            pred_data = json.load(pred_file)

        pred_id = pred_data['current']
        winner_id = data_receive['op_id']

        response = twitch_api.end_prediction(authdata.BROADCASTER_ID(),prediction_id=pred_id,status=PredictionStatus.RESOLVED,winning_outcome_id=winner_id)


@eel.expose
def poll_py(data):
    
    data_receive = json.loads(data)
    
    type_id = data_receive['type_id']

    if type_id == "create" :

        title = data_receive['title']
        options = data_receive['options']
        duration = int(data_receive['duration'])
        points_enable = data_receive['points_status']
        points = int(data_receive['points'])
        discord = int(data_receive['discord'])
    
        with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'r', encoding='utf-8') as discord_data_file:
            discord_data = json.load(discord_data_file)
        
        discord_data['poll_start']['status'] = discord
        discord_data['poll_status']['status'] = discord
        discord_data['poll_end']['status'] = discord
                
        with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'w', encoding='utf-8') as discord_data_file:
            json.dump(discord_data, discord_data_file, indent=6, ensure_ascii=False)
                    
        if points_enable == 1:
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

        with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'r', encoding='utf-8') as poll_file:
            poll_data = json.load(poll_file)

        poll_id = poll_data['current']

        twitch_api.end_poll(authdata.BROADCASTER_ID(),poll_id=poll_id,status=PollStatus.TERMINATED)

    elif type_id == "get":
        
        with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json' , 'r' , encoding='utf-8') as poll_file:
            poll_data = json.load(poll_file)

        data = {
            "status" : poll_data['status'],
            "title" : poll_data['title'],
            "time_start" : poll_data['time_start'],
            "time_end" : poll_data['time_end'],
            "options" : poll_data['options'],
        }

        data_dump = json.dumps(data)

        return data_dump


@eel.expose
def goal_py():
    with open(f'{appdata_path}/rewardevents/web/src/config/goal.json') as goal_file:
        goal_data = json.load(goal_file)

    data_dump = json.dumps(goal_data)

    return data_dump


@eel.expose
def create_action_save(data, type_id):
    data_receive = json.loads(data)

    try:

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

            with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8') as path_file:
                path_data = json.load(path_file)

            path_data[redeem_value] = {
                'type': 'sound',
                'path': audio_path,
                'volume': volume,
                'command': command_value.lower(),
                'send_response': send_response,
                'chat_response': chat_response
            }

            with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8') as path_file_write:
                json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'video':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            video_path = data_receive['video_path']
            time_showing_video = data_receive['time_showing_video']

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            old_data = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {

                'type': 'video',
                'path': video_path,
                'command': command_value.lower(),
                'send_response': send_response,
                'chat_response': chat_response,
                'show_time': time_showing_video
            }

            old_data.close()

            old_data_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)

            old_data_write.close()

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'tts':

            redeem_value = data_receive['redeem_value']
            command_value = data_receive['command_value']

            characters = data_receive['characters']

            old_data = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {
                'type': 'tts',
                'command': command_value.lower(),
                'characters': characters
            }

            old_data.close()

            old_data_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()
            
            if command_value != "":
                create_command_redeem(data_receive,'create')

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

            with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8') as old_data:
                new_data = json.load(old_data)

            new_data[redeem_value] = {

                'type': 'scene',
                'send_response': send_response,
                'command': command_value.lower(),
                'chat_response': chat_response,
                'scene_name': scene_name,
                'keep': keep_scene_value,
                'time': time_to_return
            }


            with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8') as old_data_write:
                json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            
            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'response':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']

            old_data = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {
                'type': 'response',
                'command': command_value.lower(),
                'chat_response': chat_response
            }

            old_data.close()

            old_data_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

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

            if chat_response == "":
                send_response = 0
            else:
                send_response = 1

            if time_showing == "":
                time_showing = 0

            old_data = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            old_data_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

            if command_value != "":
                create_command_redeem(data_receive,'create')

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

            old_data = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            old_data_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)
            old_data_write.close()

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'keypress':

            command_value = data_receive['command_value']
            chat_response = data_receive['chat_response']
            redeem_value = data_receive['redeem_value']
            mode_press = data_receive['mode']

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

            key_data_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            key_data_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(key_data, key_data_file_write, indent=6, ensure_ascii=False)
            key_data_file_write.close()

            if command_value != "":
                create_command_redeem(data_receive,'create')

        elif type_id == 'clip':

            command_value = data_receive['command_value']
            redeem_value = data_receive['redeem_value']

            old_data = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            new_data[redeem_value] = {'type': 'clip', 'command': command_value.lower(), }
            old_data.close()

            old_data_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(new_data, old_data_write, indent=6, ensure_ascii=False)

            if command_value != "":
                create_command_redeem(data_receive,'create')

            old_data_write.close()

        elif type_id == 'delete':

            data = data_receive['redeem']

            data_event_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            data_event = json.load(data_event_file)

            command = data_event[data]['command']

            data_command_file = open(f'{appdata_path}/rewardevents/web/src/config/commands.json', 'r', encoding='utf-8')
            data_command = json.load(data_command_file)

            if command in data_command.keys():
                del data_command[command]

                data_command_file.close()

                command_data_write = open(f'{appdata_path}/rewardevents/web/src/config/commands.json', 'w', encoding='utf-8')
                json.dump(data_command, command_data_write, indent=6, ensure_ascii=False)
                command_data_write.close()
            else:
                data_command_file.close()

            del data_event[data]
            data_event_file.close()

            event_data_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(data_event, event_data_write, indent=6, ensure_ascii=False)

            event_data_write.close()

        eel.toast_notifc('success')

    except Exception as e:

        utils.error_log(e)

        eel.toast_notifc('error')


@eel.expose
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

            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'r', encoding='utf-8') as data_command_file:
                data_command = json.load(data_command_file)

            data_command[command.lower().strip()] = {
                'status' : 1,
                'response': message,
                'user_level': user_level_check,
                'counts' : command_counts,
                'delay' : delay,
                'last_use': 0,
            }

            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'w', encoding='utf-8') as data_command_file_w:
                json.dump(data_command, data_command_file_w, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:
            utils.error_log(e)

            eel.toast_notifc('error')

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

            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'r', encoding='utf-8') as command_data_file:
                command_data = json.load(command_data_file)

            del command_data[old_command]
            command_data[new_command] = {
                "status" : status,
                "response": new_message,
                "user_level": user_level,
                "counts" : command_count,
                "delay" : new_delay,
                "last_use" : 0
            }

            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'w', encoding='utf-8') as old_data_write:
                json.dump(command_data, old_data_write, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:
            utils.error_log(e)
            eel.toast_notifc('error')

    elif type_rec == 'delete':

        try:
            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'r', encoding='utf-8') as command_file:
                command_data = json.load(command_file)

            del command_data[data_receive]

            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'w', encoding='utf-8') as command_file_write:
                json.dump(command_data, command_file_write, indent=6, ensure_ascii=False)

            eel.toast_notifc('Comando excluido')

        except Exception as e:
            utils.error_log(e)
            
            eel.toast_notifc('error')

    elif type_rec == 'get_info':
        try:
            
            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'r', encoding='utf-8') as command_file:
                command_data = json.load(command_file)

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

            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump

        except Exception as e:
            utils.error_log(e)

    elif type_rec == 'get_list':

        try:

            old_data = open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'r', encoding='utf-8')
            new_data = json.load(old_data)

            list_commands = []

            for key in new_data:
                list_commands.append(key)

            list_commands_dump = json.dumps(list_commands, ensure_ascii=False)

            old_data.close()
            return list_commands_dump

        except Exception as e:
            utils.error_log(e)

    elif type_rec == 'get_duel':

        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json', 'r', encoding='utf-8') as duel_file:
            duel_data = json.load(duel_file)
            
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
            
            duel_return_data = json.dumps(data, ensure_ascii=False)

            return duel_return_data
        
    elif type_rec == 'get_battles':
        
        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json', 'r', encoding='utf-8') as duel_file:
            duel_data = json.load(duel_file)
            
            battle = duel_data['duel_battle'][data_receive]
            
            
            data = {
                'message_0' : battle['start_mess'],
                'message_1' : battle['stage_1'],
                'message_2' : battle['stage_2'],
                'message_3' : battle['stage_3'],
                'message_4' : battle['stage_4'],
                'message_5' : battle['stage_5'],
            }
            
            duel_return_data = json.dumps(data, ensure_ascii=False)

            return duel_return_data
        
    elif type_rec == 'save_duel':
        
        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'r',encoding='utf-8') as duel_file:
            data_duel = json.load(duel_file)
            
        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'w',encoding='utf-8') as duel_file:
            
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
            
            json.dump(data_duel,duel_file,indent=6,ensure_ascii=False)
            
            
            eel.toast_notifc('Duelo salvo')
    
    elif type_rec == 'get_default':
    
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)
            
            data = {
                "cmd" : default_data_commands['cmd'],
                "cmd_status" : default_data_commands['cmd_status'],
                "cmd_delay" : default_data_commands['cmd_delay'],
                "cmd_resp" : default_data_commands['cmd_response'],
                "cmd_perm" : default_data_commands['cmd_perm'],
                "dice" : default_data_commands['dice'],
                "dice_status" : default_data_commands['dice_status'],
                "dice_delay" : default_data_commands['dice_delay'],
                "dice_resp" : default_data_commands['dice_response'],
                "dice_perm" : default_data_commands['dice_perm'],
                "random" : default_data_commands['random'],
                "random_status" : default_data_commands['random_status'],
                "random_delay" : default_data_commands['random_delay'],
                "random_resp" : default_data_commands['random_response'],
                "random_perm" : default_data_commands['random_perm'],
                "uptime" : default_data_commands['uptime'],
                "uptime_status" : default_data_commands['uptime_status'],
                "uptime_delay" : default_data_commands['uptime_delay'],
                "uptime_resp" : default_data_commands['uptime_response'],
                "uptime_perm" : default_data_commands['uptime_perm'],
                
                "game" : default_data_commands['game'],
                "game_status" : default_data_commands['game_status'],
                "game_delay" : default_data_commands['game_delay'],
                "game_resp" : default_data_commands['game_response'],
                "game_perm" : default_data_commands['game_perm'],
                
                "followage" : default_data_commands['followage'],
                "followage_status" : default_data_commands['followage_status'],
                "followage_delay" : default_data_commands['followage_delay'],
                "followage_resp" : default_data_commands['followage_response'],
                "followage_perm" : default_data_commands['followage_perm'],
                
                "watchtime" : default_data_commands['watchtime'],
                "watchtime_status" : default_data_commands['watchtime_status'],
                "watchtime_delay" : default_data_commands['watchtime_delay'],
                "watchtime_resp" : default_data_commands['watchtime_response'],
                "watchtime_perm" : default_data_commands['watchtime_perm'],
                
                "msgcount" : default_data_commands['msgcount'],
                "msgcount_status" : default_data_commands['msgcount_status'],
                "msgcount_delay" : default_data_commands['msgcount_delay'],
                "msgcount_resp" : default_data_commands['msgcount_response'],
                "msgcount_perm" : default_data_commands['msgcount_perm'],
                
                "interaction_1" : default_data_commands['interaction_1'],
                "interaction_1_status" : default_data_commands['interaction_1_status'],
                "interaction_1_delay" : default_data_commands['interaction_1_delay'],
                "interaction_1_resp" : default_data_commands['interaction_1_response'],
                "interaction_1_perm" : default_data_commands['interaction_1_perm'],
                "interaction_2" : default_data_commands['interaction_2'],
                "interaction_2_status" : default_data_commands['interaction_2_status'],
                "interaction_2_delay" : default_data_commands['interaction_2_delay'],
                "interaction_2_resp" : default_data_commands['interaction_2_response'],
                "interaction_2_perm" : default_data_commands['interaction_2_perm'],
                "interaction_3" : default_data_commands['interaction_3'],
                "interaction_3_status" : default_data_commands['interaction_3_status'],
                "interaction_3_delay" : default_data_commands['interaction_3_delay'],
                "interaction_3_resp" : default_data_commands['interaction_3_response'],
                "interaction_3_perm" : default_data_commands['interaction_3_perm'],
                "interaction_4" : default_data_commands['interaction_4'],
                "interaction_4_status" : default_data_commands['interaction_4_status'],
                "interaction_4_delay" : default_data_commands['interaction_4_delay'],
                "interaction_4_resp" : default_data_commands['interaction_4_response'],
                "interaction_4_perm" : default_data_commands['interaction_4_perm'],
                "interaction_5" : default_data_commands['interaction_5'],
                "interaction_5_status" : default_data_commands['interaction_5_status'],
                "interaction_5_delay" : default_data_commands['interaction_5_delay'],
                "interaction_5_resp" : default_data_commands['interaction_5_response'],
                "interaction_5_perm" : default_data_commands['interaction_5_perm'],
            }
            
            default_return_data = json.dumps(data, ensure_ascii=False)

            return default_return_data           
    
    elif type_rec == 'save_default-cmd':
    
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["cmd"] = data['cmd']
        default_data_commands["cmd_status"] = data['cmd_status']
        default_data_commands["cmd_delay"] = data['cmd_delay']
        default_data_commands["cmd_response"] = data['cmd_respo']
        default_data_commands["cmd_perm"] = data['cmd_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')

    elif type_rec == 'save_default-dice':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["dice"] = data['dice']
        default_data_commands["dice_status"] = data['dice_status']
        default_data_commands["dice_delay"] = data['dice_delay']
        default_data_commands["dice_response"] = data['dice_respo']
        default_data_commands["dice_perm"] = data['dice_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')

    elif type_rec == 'save_default-random':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["random"] = data['random']
        default_data_commands["random_status"] = data['random_status']
        default_data_commands["random_delay"] = data['random_delay']
        default_data_commands["random_response"] = data['random_respo']
        default_data_commands["random_perm"] = data['random_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-uptime':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["uptime"] = data['uptime']
        default_data_commands["uptime_status"] = data['uptime_status']
        default_data_commands["uptime_delay"] = data['uptime_delay']
        default_data_commands["uptime_response"] = data['uptime_respo']
        default_data_commands["uptime_perm"] = data['uptime_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-game':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["game"] = data['game']
        default_data_commands["game_status"] = data['game_status']
        default_data_commands["game_delay"] = data['game_delay']
        default_data_commands["game_response"] = data['game_respo']
        default_data_commands["game_perm"] = data['game_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-followage':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["followage"] = data['followage']
        default_data_commands["followage_status"] = data['followage_status']
        default_data_commands["followage_delay"] = data['followage_delay']
        default_data_commands["followage_response"] = data['followage_respo']
        default_data_commands["followage_perm"] = data['followage_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-msgcount':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["msgcount"] = data['msgcount']
        default_data_commands["msgcount_status"] = data['msgcount_status']
        default_data_commands["msgcount_delay"] = data['msgcount_delay']
        default_data_commands["msgcount_response"] = data['msgcount_respo']
        default_data_commands["msgcount_perm"] = data['msgcount_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')     
    elif type_rec == 'save_default-watchtime':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["watchtime"] = data['watchtime']
        default_data_commands["watchtime_status"] = data['watchtime_status']
        default_data_commands["watchtime_delay"] = data['watchtime_delay']
        default_data_commands["watchtime_response"] = data['watchtime_respo']
        default_data_commands["watchtime_perm"] = data['watchtime_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-interaction_1':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["interaction_1"] = data['interaction_1']
        default_data_commands["interaction_1_status"] = data['interaction_1_status']
        default_data_commands["interaction_1_delay"] = data['interaction_1_delay']
        default_data_commands["interaction_1_response"] = data['interaction_1_respo']
        default_data_commands["interaction_1_perm"] = data['interaction_1_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-interaction_2':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["interaction_2"] = data['interaction_2']
        default_data_commands["interaction_2_status"] = data['interaction_2_status']
        default_data_commands["interaction_2_delay"] = data['interaction_2_delay']
        default_data_commands["interaction_2_response"] = data['interaction_2_respo']
        default_data_commands["interaction_2_perm"] = data['interaction_2_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-interaction_3':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["interaction_3"] = data['interaction_3']
        default_data_commands["interaction_3_status"] = data['interaction_3_status']
        default_data_commands["interaction_3_delay"] = data['interaction_3_delay']
        default_data_commands["interaction_3_response"] = data['interaction_3_respo']
        default_data_commands["interaction_3_perm"] = data['interaction_3_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-interaction_4':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["interaction_4"] = data['interaction_4']
        default_data_commands["interaction_4_status"] = data['interaction_4_status']
        default_data_commands["interaction_4_delay"] = data['interaction_4_delay']
        default_data_commands["interaction_4_response"] = data['interaction_4_respo']
        default_data_commands["interaction_4_perm"] = data['interaction_4_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
    elif type_rec == 'save_default-interaction_5':
        
        data = json.loads(data_receive)  
        
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'r',encoding='utf-8') as default_commands_file:
            default_data_commands = json.load(default_commands_file)

        default_data_commands["interaction_5"] = data['interaction_5']
        default_data_commands["interaction_5_status"] = data['interaction_5_status']
        default_data_commands["interaction_5_delay"] = data['interaction_5_delay']
        default_data_commands["interaction_5_response"] = data['interaction_5_respo']
        default_data_commands["interaction_5_perm"] = data['interaction_5_perm']
            
        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json' , 'w',encoding='utf-8') as default_commands_file:
            json.dump(default_data_commands,default_commands_file,indent=6,ensure_ascii=False)
            
            eel.toast_notifc('Comando salvo')
 
 
@eel.expose
def timer_py(type_id, data_receive):
    
    if type_id == "get":
        
        with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as timer_data_file:
            timer_data = json.load(timer_data_file)

        with open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json', 'r', encoding="utf-8") as message_file_get:
            message_data_get = json.load(message_file_get)

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

        timer_data = json.dumps(data, ensure_ascii=False)

        return timer_data
    
    elif type_id == "get_message":
        
        with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as timer_data_file:
            timer_data = json.load(timer_data_file)

        message = timer_data['MESSAGES'][data_receive]['message']
        type_timer = timer_data['MESSAGES'][data_receive]['type_timer']
        timer_color = timer_data['MESSAGES'][data_receive]['color']

        data = {
            "message": message,
            "type_timer": type_timer,
            "color" : timer_color
        }

        timer_data = json.dumps(data, ensure_ascii=False)

        timer_data_file.close()

        return timer_data
    
    elif type_id == "edit":
        
        try:    

            data = json.loads(data_receive)

            data_key = data['key']
            data_message = data['message']
            data_type = data['type_timer']
            data_color = data['color']


            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as timer_data_file:
                timer_data = json.load(timer_data_file)

            timer_data['MESSAGES'][data_key] = {'message' : data_message, 'type_timer' :data_type, 'color' : data_color}

            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'w', encoding='utf-8') as timer_data_file_w:
                json.dump(timer_data, timer_data_file_w, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')
            
    elif type_id == "add":
        
        try:
            
            data = json.loads(data_receive)

            data_color = data['color']
            data_message = data['message']
            data_type = data['type_timer']

            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as timer_data_file_w:
                timer_data = json.load(timer_data_file_w)

            timer_message = timer_data['MESSAGES']

            if not timer_message:

                keytoadd = 1

            else:
                key = list(timer_message.keys())[-1]
                keytoadd = int(key) + 1

            timer_data['MESSAGES'][str(keytoadd)] = {"message" : data_message, "type_timer": data_type, "color" : data_color}

            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'w', encoding='utf-8') as timer_data_write:
                json.dump(timer_data, timer_data_write, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')
            
    elif type_id == "del":
        
        try:

            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as message_del_file:
                message_del_data = json.load(message_del_file)

            del message_del_data['MESSAGES'][data_receive]

            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'w', encoding='utf-8') as message_del_file_write:
                json.dump(message_del_data, message_del_file_write, indent=6, ensure_ascii=False)

            eel.toast_notifc('Mensagem excluida')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    elif type_id == "delay":
        
        try:    
            data = json.loads(data_receive)
            
            min_time = data['min_time']
            max_time = data['max_time']
            
            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as timer_data_file:
                timer_data = json.load(timer_data_file)
                
            timer_data['TIME'] = int(min_time)
            timer_data['TIME_MAX'] = int(max_time)
            
            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'w', encoding='utf-8') as timer_data_file_w:
                json.dump(timer_data, timer_data_file_w, indent=6, ensure_ascii=False)
                
            eel.toast_notifc('success')
        except Exception as e:

            utils.error_log(e)
            eel.toast_notifc('error')

    elif type_id == "status":
        
        try:    
            
            with open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json', 'r', encoding="utf-8") as command_config_file:
                command_config_data = json.load(command_config_file)

            command_config_data['STATUS_TIMER'] = data_receive

            with open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json', 'w', encoding="utf-8") as command_config_file_w:
                json.dump(command_config_data, command_config_file_w, indent=6, ensure_ascii=False)
                
            eel.toast_notifc('success')
                
        except Exception as e:

            utils.error_log(e)
            eel.toast_notifc('error')


@eel.expose
def giveaway_py(type_id, data_receive):
    
    if type_id == 'get_config':
        
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'r', encoding='utf-8') as giveaway_file:
                giveaway_data = json.load(giveaway_file)
                
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/commands.json', 'r', encoding='utf-8') as giveaway_commands_file:
                giveaway_commands_data = json.load(giveaway_commands_file)
                
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'r', encoding='utf-8') as giveaway_delay_file:
                giveaway_delay_data = json.load(giveaway_delay_file)

            data = {
                "giveaway_name": giveaway_data['name'],
                "giveaway_level": giveaway_data['user_level'],
                "giveaway_clear": giveaway_data['clear'],
                "giveaway_enable": giveaway_data['enable'],
                "giveaway_redeem": giveaway_data['redeem'],
                "giveaway_mult": giveaway_data['allow_mult_entry'],
                "execute_giveaway": giveaway_commands_data['execute_giveaway'],
                "execute_delay": giveaway_delay_data['execute_delay'],
                "user_check_giveaway": giveaway_commands_data['check_name'],
                "user_check_delay" :giveaway_delay_data['check_delay'],
                "self_check_giveaway": giveaway_commands_data['check_self_name'],
                "self_check_delay" : giveaway_delay_data['check_self_delay'],
                "clear_giveaway": giveaway_commands_data['clear_giveaway'],
                "clear_delay" : giveaway_delay_data['clear_delay'],
                "add_user_giveaway": giveaway_commands_data['add_user'],
                "add_user_delay": giveaway_delay_data['add_user_delay']
            }

            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump

    elif type_id == 'show_names':
        
        with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'r', encoding='utf-8') as giveaway_commands_file:
            giveaway_commands_data = json.load(giveaway_commands_file)

        data_dump = json.dumps(giveaway_commands_data, ensure_ascii=False)

        return data_dump

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
            
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'r', encoding='utf-8') as giveaway_file:
                giveaway_data = json.load(giveaway_file)
                
            if giveaway_data['enable'] == 1 and data['giveaway_enable'] == 0:
                
                response_give_stop = utils.messages_file_load('giveaway_status_disable')

                aliases = {
                    '{giveaway_name_data}' : giveaway_data['name'],
                }
                
                response_redus = utils.replace_all(response_give_stop, aliases)
                if utils.send_message("RESPONSE"):
                    send(response_redus)

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'w', encoding="utf-8") as giveaway_commands_file:
                json.dump(giveaway_data_new, giveaway_commands_file, indent=6, ensure_ascii=False)


            eel.toast_notifc('success')
                            
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'r', encoding='utf-8') as giveaway_file:
                giveaway_data = json.load(giveaway_file)
                
            if giveaway_data['enable'] == 1:
                
                response_give_start = utils.messages_file_load('giveaway_status_enable')

                aliases = {
                    '{giveaway_name_data}' : giveaway_data['name'],
                    '{redeem}' : giveaway_data['redeem']
                }
                
                response_redus = utils.replace_all(response_give_start, aliases)
                if utils.send_message("RESPONSE"):
                    send(response_redus)
                    
                eel.toast_notifc('Sorteio iniciado')


        except Exception as e:

            utils.error_log(e)
            eel.toast_notifc('error')
        
    elif type_id == 'save_commands':
        
        data = json.loads(data_receive)

        try:

            giveaway_data_new = {
                "execute_giveaway": data['execute_giveaway'],
                "clear_giveaway": data['clear_giveaway'],
                "check_name": data['check_user_giveaway'],
                "check_self_name": data['self_check_giveaway'],
                "add_user": data['add_user_giveaway'],
            }

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/commands.json', 'w', encoding="utf-8") as giveaway_commands_w:
                json.dump(giveaway_data_new, giveaway_commands_w, indent=6, ensure_ascii=False)
                
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'r', encoding='utf-8') as giveaway_delay_file:
                giveaway_delay_data = json.load(giveaway_delay_file)
                
                giveaway_delay_data['execute_delay'] = data['execute_delay']
                giveaway_delay_data['clear_delay'] = data['clear_delay']
                giveaway_delay_data['check_delay'] = data['check_user_delay']
                giveaway_delay_data['check_self_delay'] = data['self_check_delay']
                giveaway_delay_data['add_user_delay'] = data['add_user_delay']
                
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                json.dump(giveaway_delay_data, giveaway_delay_w, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')
        
    elif type_id == 'add_user':
        
        if not type(data_receive) is dict:
            data = json.loads(data_receive)
        else: 
            data = data_receive
    
        new_name = data['new_name']
        user_level = data['user_level']
        
        def check_perm(user_level, command_level):
            
            level = ["spec","regular","top_chatter", "vip", "subs", "mod", "streamer"]
            if level.index(user_level) >= level.index(command_level):
                return True
            else:
                return False

        try:

            def append_name(new_name):
                
                with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'r', encoding='utf-8') as giveaway_name_file:
                    giveaway_name_data = json.load(giveaway_name_file)
                            
                giveaway_name_data.append(new_name)

                with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'w', encoding="utf-8") as giveaway_save_file:
                    json.dump(giveaway_name_data, giveaway_save_file, indent=6, ensure_ascii=False)
                    
                    
                with open(f'{appdata_path}/rewardevents/web/src/giveaway/backup.json', 'r', encoding='utf-8') as back_giveaway_name_file:
                    back_giveaway_name_data = json.load(back_giveaway_name_file)
                            
                back_giveaway_name_data.append(new_name)

                with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'w', encoding="utf-8") as giveaway_save_file:
                    json.dump(giveaway_name_data, giveaway_save_file, indent=6, ensure_ascii=False)

                response_give_load = utils.messages_file_load('giveaway_response_user_add')

                response_redus = utils.replace_all(response_give_load, aliases)
                if utils.send_message("RESPONSE"):
                    send(response_redus)


                eel.toast_notifc(f'O usuário {new_name} foi adicionado na lista')
            

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'r', encoding='utf-8') as giveaway_name_file:
                giveaway_name_data = json.load(giveaway_name_file)

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'r', encoding='utf-8') as giveaway_config_file:
                giveaway_config_data = json.load(giveaway_config_file)

            
            if giveaway_config_data['enable'] == 1:
                
                giveaway_perm = giveaway_config_data['user_level']
                giveaway_mult_config = giveaway_config_data['allow_mult_entry']


                aliases = {
                    '{user}': str(new_name),
                    '{perm}' : str(giveaway_perm)
                }

                if giveaway_mult_config == 0:

                    if new_name in giveaway_name_data:

                        response_give_load = utils.messages_file_load('giveaway_response_mult_add')
                        eel.toast_notifc(f'Este nome já está no sorteio, para adicionar ative a opção para permitir multiplas entradas no sorteio.')

                        response_redus = utils.replace_all(response_give_load, aliases)
                        if utils.send_message("RESPONSE"):
                            send(response_redus)
                    else:
                        
                        if check_perm(user_level, giveaway_perm):
                            append_name(new_name)

                        else:
                            response_give_perm = utils.messages_file_load('giveaway_response_perm')
                            response_redus = utils.replace_all(response_give_perm, aliases)

                            if utils.send_message("RESPONSE"):
                                send(response_redus)
                else:

                    if check_perm(user_level, giveaway_perm):
                        append_name(new_name)

                    else:
                        response_give_perm = utils.messages_file_load('giveaway_response_perm')
                        response_redus = utils.replace_all(response_give_perm, aliases)

                        if utils.send_message("RESPONSE"):
                            send(response_redus)

            else:
                response_give_load = utils.messages_file_load('giveaway_status_disabled')

                response_redus = utils.replace_all(response_give_load, aliases)
                if utils.send_message("RESPONSE"):
                    send(response_redus)

        except Exception as e:
            
            utils.error_log(e)
            eel.toast_notifc('error')
        
    elif type_id == 'execute':
        
        try:
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'r', encoding='utf-8') as giveaway_file:
                giveaway_data = json.load(giveaway_file)

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'r', encoding='utf-8') as giveaway_name_file:
                giveaway_name_data = json.load(giveaway_name_file)

            reset_give = giveaway_data['clear']
            name = random.choice(giveaway_name_data)


            message_load_winner_giveaway = utils.messages_file_load('giveaway_response_win')

            message_win = message_load_winner_giveaway.replace('{name}', name)
            if utils.send_message("RESPONSE"):
                send(message_win)

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/backup.json', 'w', encoding="utf-8") as giveaway_backup_file:
                json.dump(giveaway_name_data, giveaway_backup_file, indent=6, ensure_ascii=False)

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/result.json', 'w', encoding="utf-8") as giveaway_result_file:
                json.dump(name, giveaway_result_file, indent=6, ensure_ascii=False)

            if reset_give == 1:
                reset_data = []

                with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'w', encoding="utf-8") as giveaway_reset_file:
                    json.dump(reset_data, giveaway_reset_file, indent=6, ensure_ascii=False)

            eel.toast_notifc(f'{name} Ganhou o sorteio !', )

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('Erro ao executar o sorteio')
        
    elif type_id == 'clear_list':
        
        try:

            reset_data = []

            with open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'w', encoding="utf-8") as giveaway_reset_file:
                json.dump(reset_data, giveaway_reset_file, indent=6, ensure_ascii=False)

            eel.toast_notifc('Lista de sorteio limpa')

        except Exception as e:
            utils.error_log(e)
            eel.toast_notifc('error')
  
  
@eel.expose
def counter(fun_id, redeem, commands, value):
    
    if fun_id == 'get_counter_config':
        
        with open(f'{appdata_path}/rewardevents/web/src/counter/config.json', 'r', encoding='utf-8') as counter_file:
            counter_data = json.load(counter_file)
            
        with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'r', encoding='utf-8') as delay_counter_file:
            delay_counter_data = json.load(delay_counter_file)
            
        with open(f'{appdata_path}/rewardevents/web/src/counter/commands.json', 'r', encoding='utf-8') as counter_commands_file:
            counter_commands_data = json.load(counter_commands_file)

        with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "r") as counter_file_r:
            counter_file_r.seek(0)
            counter_value_get = counter_file_r.read()

        response_chat = utils.messages_file_load('response_counter')

        data = {

            "redeem": counter_data['redeem'],
            "response" : counter_data['response'],
            "response_chat" : response_chat,
            "value_counter": counter_value_get,
            "counter_command_reset": counter_commands_data['reset_counter'],
            "counter_delay_reset" : delay_counter_data['reset'],
            "counter_status_reset": delay_counter_data['reset_status'],
            "counter_command_set": counter_commands_data['set_counter'],
            "counter_delay_set" : delay_counter_data['set'],
            "counter_status_apply": delay_counter_data['set_status'],
            "counter_command_check": counter_commands_data['check_counter'],
            "counter_delay_check" : delay_counter_data['check'],
            "counter_status_check" : delay_counter_data['check_status'],
            
        }

        counter_data_parse = json.dumps(data, ensure_ascii=False)

        return counter_data_parse

    if fun_id == "save_counter_config":

        try:
            with open(f'{appdata_path}/rewardevents/web/src/counter/config.json', 'r', encoding='utf-8') as counter_file:
                counter_data = json.load(counter_file)

            with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', "r", encoding='utf-8') as messages_file:
                messages_data = json.load(messages_file)
            
            data_save = json.loads(redeem)

            messages_data['response_counter'] = data_save['response_chat']

            with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', "w", encoding='utf-8') as messages_file:
                json.dump(messages_data, messages_file, indent=6, ensure_ascii=False)

            counter_data['redeem'] = data_save['redeem']
            counter_data['response'] = data_save['response']

            with open(f'{appdata_path}/rewardevents/web/src/counter/config.json', 'w', encoding='utf-8') as counter_file_save:
                json.dump(data_save, counter_file_save, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    if fun_id == "save-counter-commands":

        data_received = json.loads(commands)

        try:

            with open(f'{appdata_path}/rewardevents/web/src/counter/commands.json', 'r', encoding='utf-8') as command_counter_file:
                command_counter_data = json.load(command_counter_file)
                
            command_counter_data["reset_counter"] = data_received['counter_command_reset']
            command_counter_data["set_counter"] = data_received['counter_command_apply']
            command_counter_data["check_counter"] = data_received['counter_command_check']
            
            with open(f'{appdata_path}/rewardevents/web/src/counter/commands.json', 'w', encoding='utf-8') as counter_file_save_commands:
                json.dump(command_counter_data, counter_file_save_commands, indent=6, ensure_ascii=False)
            
            
            with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'r', encoding='utf-8') as delay_counter_file:
                delay_counter_data = json.load(delay_counter_file)
             
            delay_counter_data['set'] = data_received['counter_apply_delay']
            delay_counter_data['set_status'] = data_received['counter_status_apply']
            delay_counter_data['reset'] = data_received['counter_reset_delay']   
            delay_counter_data['reset_status'] = data_received['counter_status_reset']  
            delay_counter_data['check'] = data_received['counter_check_delay']
            delay_counter_data['check_status'] = data_received['counter_status_check']
            
            with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'w', encoding='utf-8') as delay_counter_file_w:
                json.dump(delay_counter_data, delay_counter_file_w, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)
            eel.toast_notifc('error')

    if fun_id == "set-counter-value":
        with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "w") as counter_file_w:
            counter_file_w.write(str(value))


@eel.expose
def obs_config_py(type_id,data_receive):
    
    if type_id == "get":
        
        with open(f'{appdata_path}/rewardevents/web/src/config/obs.json', 'r', encoding='utf-8') as obs_conn_file:
            obs_conn_data = json.load(obs_conn_file)

        data = {
            "host": obs_conn_data['OBS_HOST'],
            "port": obs_conn_data['OBS_PORT'],
            "password": obs_conn_data['OBS_PASSWORD'],
            "auto_conn": obs_conn_data['OBS_TEST_CON']
        }

        conm_data = json.dumps(data, ensure_ascii=False)

        return conm_data
    
    elif type_id == "get_not":
        
        
        with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding='utf-8') as obs_not_file:
            obs_not_data = json.load(obs_not_file)
        
        data = {
            'html_events_active' : obs_not_data['HTML_EVENTS_ACTIVE'],
            'html_player_active': obs_not_data['HTML_PLAYER_ACTIVE'],
            'html_active': obs_not_data['HTML_ACTIVE'],
            'html_title': obs_not_data['HTML_TITLE'],
            'html_video': obs_not_data['HTML_VIDEO'],
            'html_events' : obs_not_data['HTML_EVENTS'],
            'html_time': obs_not_data['HTML_TIME'],
            'html_events_time': obs_not_data['HTML_EVENTS_TIME'],
        }
        
        not_data = json.dumps(data, ensure_ascii=False)

        return not_data
    
    elif type_id == "save_conn":

        try:
            data = json.loads(data_receive)

            data_save = {
                'OBS_HOST': data['host'],
                'OBS_PORT': data['port'],
                'OBS_PASSWORD': data['pass']
            }

            with open(f"{appdata_path}/rewardevents/web/src/config/obs.json", "w", encoding='utf-8') as obs_file:
                json.dump(data_save, obs_file, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)
            eel.toast_notifc('error')
            
    elif type_id == "save_not":
        
        try:
            data = json.loads(data_receive)

            data_save = {
                'HTML_EVENTS_ACTIVE' : data['not_event'],
                'HTML_PLAYER_ACTIVE': data['not_music'],
                'HTML_ACTIVE': data['not_enabled'],
                'HTML_TITLE': data['source_name'],
                'HTML_VIDEO': data['video_source_name'],
                'HTML_EVENTS' : data['event_source_name'],
                'HTML_TIME': int(data['time_showing_not']),
                'HTML_EVENTS_TIME': int(data['time_showing_event_not']),
            }

            with open(f"{appdata_path}/rewardevents/web/src/config/notfic.json", "w", encoding='utf-8') as obs_not_file:
                json.dump(data_save, obs_not_file, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)
            eel.toast_notifc('error')


@eel.expose
def not_config_py(data_receive,type_id,type_not):
    
    with open(f'{appdata_path}/rewardevents/web/src/config/event_not.json', 'r', encoding='utf-8') as event_config_file:
        event_config_data = json.load(event_config_file)

    if type_id == "get":   
         
        file_data = event_config_data[type_not]

        data = {
            'not': file_data['status'],
            'image_over': file_data['text_over_image'],
            'image': file_data['image'],
            'image_px': file_data['image_px'],
            'audio': file_data['audio'],
            'audio_volume': file_data['audio_volume'],
            'tts': file_data['tts'],
            'response': file_data['response'],
            'response_chat': file_data['response_chat'],
            'response_px': file_data['response_px'],
            'response_weight': file_data['response_weight'],
            'response_color': file_data['response_color'],
        }
        
        event_not_data_dump = json.dumps(data, ensure_ascii=False)

        return event_not_data_dump
    
    elif type_id == "save":
        
        try:

            data = json.loads(data_receive)
            
            event_config_data[type_not]['status'] = data['not']
            event_config_data[type_not]['text_over_image'] = data['image_over']
            event_config_data[type_not]['image'] = data['image']
            event_config_data[type_not]['image_px'] = data['image_px']
            event_config_data[type_not]['audio'] = data['audio']
            event_config_data[type_not]['audio_volume'] = data['audio_volume']
            event_config_data[type_not]['tts'] = data['tts']
            event_config_data[type_not]['response'] = data['response']
            event_config_data[type_not]['response_chat'] = data['response_chat']
            event_config_data[type_not]['response_px'] = data['response_px']
            event_config_data[type_not]['response_weight'] = data['response_weight']
            event_config_data[type_not]['response_color'] = data['response_color']
            
            
            with open(f'{appdata_path}/rewardevents/web/src/config/event_not.json', 'w', encoding='utf-8') as event_config_file_w:
                json.dump(event_config_data, event_config_file_w,indent=6,ensure_ascii=False)
                
            eel.toast_notifc('success')
            
        except Exception as e:

            utils.error_log(e)
            eel.toast_notifc('error')
    
        
@eel.expose
def get_messages_config():

    message_file_get = open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json', 'r', encoding="utf-8")
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

        old_message_file = open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json', 'r', encoding="utf-8")
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

        old_data_write = open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json', 'w', encoding="utf-8")
        json.dump(old_message_data, old_data_write, indent=6, ensure_ascii=False)
        old_data_write.close()

        eel.toast_notifc('success')

    except Exception as e:

        utils.error_log(e)

        eel.toast_notifc('error')


@eel.expose
def responses_config(fun_id, response_key, message):
    if fun_id == 'get_response':

        with open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', 'r', encoding='utf-8') as responses_file:
            responses_data = json.load(responses_file)

        response = responses_data[response_key]

        return response

    elif fun_id == 'save_response':

        try:

            responses_file = open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', 'r', encoding='utf-8')
            responses_data = json.load(responses_file)

            responses_data[response_key] = message

            responses_file.close()
            responses_file_w = open(f'{appdata_path}/rewardevents/web/src/messages/messages_file.json', 'w', encoding='utf-8')
            json.dump(responses_data, responses_file_w, indent=6, ensure_ascii=False)

            responses_file_w.close()
            eel.toast_notifc('success')

        except Exception as e:

            eel.toast_notifc('error')
            utils.error_log(e)


@eel.expose
def discord_config(data_discord_save, mode,type_id):
    
    if mode == 'save':

        try:
            data_discord_receive = json.loads(data_discord_save)
            
            with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'r', encoding='utf-8') as discord_data_file:
                discord_data = json.load(discord_data_file)
            
            url_webhook = data_discord_receive['webhook_url']
            embed_color = data_discord_receive['embed_color']
            embed_content = data_discord_receive['embed_content']
            embed_title = data_discord_receive['embed_title']
            embed_description = data_discord_receive['embed_description']
            status = data_discord_receive['webhook_status']
            
            
            discord_data[type_id] = {
                
                'url' : url_webhook,
                'status' : status,
                'color' : embed_color,
                'content' : embed_content,
                'title' : embed_title,
                'description' : embed_description
            }
                  
            with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'w', encoding='utf-8') as discord_data_file:
                json.dump(discord_data, discord_data_file, indent=6, ensure_ascii=False)

            eel.toast_notifc('success')

        except Exception as e:

            eel.toast_notifc('error')
            utils.error_log(e)

    if mode == 'get':
        
        with open(f'{appdata_path}/rewardevents/web/src/config/discord.json', 'r', encoding='utf-8') as discord_data_file:
            discord_data = json.load(discord_data_file)

        url_webhook = discord_data[type_id]['url']
        embed_content = discord_data[type_id]['content']
        embed_title = discord_data[type_id]['title']
        embed_description = discord_data[type_id]['description']
        embed_color = discord_data[type_id]['color']
        status = discord_data[type_id]['status']


        data_get = {
            "url_webhook" : url_webhook,
            "embed_content" : embed_content,
            "embed_color": embed_color,
            "embed_title": embed_title,
            "embed_description": embed_description,
            "status": status,
        }

        data_get_sent = json.dumps(data_get, ensure_ascii=False)

        return data_get_sent


@eel.expose
def disclosure_py(type_id,data_receive):
    
    if type_id == "save":
        
        with open(f'{appdata_path}/rewardevents/web/src/config/disclosure.json', 'r', encoding='utf-8') as file_disclosure:
            disclosure_data = json.load(file_disclosure)

            disclosure_data['message'] = data_receive
    
        with open(f'{appdata_path}/rewardevents/web/src/config/disclosure.json', 'w', encoding='utf-8') as file_disclosure_w:
            json.dump(disclosure_data,file_disclosure_w,indent=4,ensure_ascii=False)
            
    elif type_id == "get":
        
        with open(f'{appdata_path}/rewardevents/web/src/config/disclosure.json', 'r', encoding='utf-8') as file_disclosure:
            disclosure_data = json.load(file_disclosure)

            if disclosure_data['message'] == "":
                disclosure = 'Digite aqui a sua mensagem rápida de divulgação em chats'
            else:
                disclosure = disclosure_data['message']
                
            return disclosure


@eel.expose
def get_edit_data(redeen, type_action):
    
    with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8') as redeem_file:
        redeem_data = json.load(redeem_file)

    if type_action == 'sound':

        sound = redeem_data[redeen]['path']
        command = redeem_data[redeen]['command']
        
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        audio_volume = redeem_data[redeen]['volume']

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        if command in command_data.keys():
            
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
            
        else:
            
            command_level = ''
            command_status = ''
            delay = ''
            

        redeem_data_return = {
            "sound": sound,
            "command": command,
            "delay": delay,
            "command_status": command_status,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "volume": audio_volume
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)
        return redeem_data_dump

    if type_action == 'video':

        video = redeem_data[redeen]['path']
        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        time_showing_video = redeem_data[redeen]['show_time']

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''
            

        redeem_data_return = {
            "video": video,
            "command": command,
            "command_status": command_status,
            "delay": delay,
            "response_status": response_status,
            "user_level": command_level,
            "response": response,
            "time_showing": time_showing_video
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'tts':

        characters = redeem_data[redeen]['characters']
        command = redeem_data[redeen]['command']

        command_file = open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8')
        command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''
            

        redeem_data_return = {
            "characters": characters,
            "command_status":command_status,
            "command": command,
            "user_level": command_level,
            "delay" : delay
        }

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'response':

        command = redeem_data[redeen]['command']
        response = redeem_data[redeen]['chat_response']

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        redeem_data_return = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
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

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        redeem_data_return = {
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

        redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

        return redeem_data_dump

    if type_action == 'filter':

        command = redeem_data[redeen]['command']
        response_status = redeem_data[redeen]['send_response']
        response = redeem_data[redeen]['chat_response']
        keep = redeem_data[redeen]['keep']
        time_filter = redeem_data[redeen]['time']

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        redeem_data_return = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
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

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''
        redeem_data_return = {
            "command": command,
            "command_status" : command_status,
            "delay" : delay,
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

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

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

            redeem_data_return = {
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

            redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

            return redeem_data_dump

        elif mode == 'mult':

            time_press = redeem_data[redeen]['mult_press_times']
            interval = redeem_data[redeen]['mult_press_interval']

            redeem_data_return = {

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

            redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

            return redeem_data_dump

        elif mode == 're':

            re_press_time = redeem_data[redeen]['re_press_time']

            redeem_data_return = {
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

            redeem_data_dump = json.dumps(redeem_data_return, ensure_ascii=False)

            return redeem_data_dump

    if type_action == 'clip':

        command = redeem_data[redeen]['command']

        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
            command_data = json.load(command_file)

        if command in command_data.keys():
            command_level = command_data[command]['user_level']
            command_status = command_data[command]['status']
            delay = command_data[command]['delay']
        else:
            command_level = ''
            command_status = ''
            delay = ''

        redeem_data_return = {
            "command": command,
            "command_status": command_status,
            "delay": delay,
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
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            sound_path = data_received['sound_path']
            volume = data_received['audio_volume']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "sound",
                'path': sound_path,
                'volume' : volume,
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
            }

            path_file.close()

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')
    
    if redeem_type == 'video':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']
            video_path = data_received['video_path']
            time_showing_video = data_received['time_showing_video']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "video",
                'path': video_path,
                'command': command,
                'send_response': send_message,
                'chat_response': chat_message,
                'show_time' : time_showing_video
            }

            path_file.close()

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    if redeem_type == 'tts':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            command = data_received['command']
            characters = data_received['characters']


            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "tts",
                'characters': characters,
                'command': command
            }

            path_file.close()

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')
    
    if redeem_type == 'scene':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
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

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    if redeem_type == 'response':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            command = data_received['command']
            chat_message = data_received['chat_message']
            user_level = data_received['user_level']

            if chat_message != "":
                send_message = 1
            else:
                send_message = 0

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            command_file = open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8')
            command_data = json.load(command_file)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    if redeem_type == 'filter':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
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

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    if redeem_type == 'source':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
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

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    if redeem_type == 'keypress':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
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

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
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

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

    if redeem_type == 'clip':

        try:
            old_redeem = data_received['old_redeem']
            redeem = data_received['redeem']
            command = data_received['command']
            user_level = data_received['user_level']

            path_file = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8')
            path_data = json.load(path_file)

            if old_redeem != redeem:
                del path_data[old_redeem]

            path_data[redeem] = {
                'type': "clip",
                'command': command,
            }

            path_file.close()

            path_file_write = open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'w', encoding='utf-8')
            json.dump(path_data, path_file_write, indent=6, ensure_ascii=False)

            create_command_redeem(data_received,'edit')

            eel.toast_notifc('success')

        except Exception as e:

            utils.error_log(e)

            eel.toast_notifc('error')

@eel.expose
def playlist_py(type_id,data):
    
    def start_add(playlist_url):

        try:

            p = Playlist(playlist_url)
            
            with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "r", encoding="utf-8") as playlist_file:
                playlist_data = json.load(playlist_file)

            check_have = any(playlist_data.keys())

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

                    eel.playlist_js('Adicionando, aguarde... ' + video_title_short, 'queue_add')

                    with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "r", encoding="utf-8") as playlist_file:
                        playlist_data = json.load(playlist_file)

                    playlist_data[last_key] = {"MUSIC": url, "USER": "playlist", "MUSIC_NAME": video_title}

                    with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "w", encoding="utf-8") as playlist_file_write:
                        json.dump(playlist_data, playlist_file_write, indent=4, ensure_ascii=False)

                except Exception as e:

                    utils.error_log(e)

            eel.playlist_js('None', 'queue_close')

        except Exception as e:

            utils.error_log(e)

    if type_id == "add":

        playlist_thread = threading.Thread(target=start_add, args=(data,), daemon=True)
        playlist_thread.start()

    
    elif type_id == 'save':

        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r', encoding="utf-8") as playlist_stats_file:
            playlist_stats_data = json.load(playlist_stats_file)

        playlist_stats_data['STATUS'] = data

        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'w', encoding="utf-8") as playlist_stats_file_w:
            json.dump(playlist_stats_data, playlist_stats_file_w, indent=4)
   
    elif type_id == 'get':

        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r', encoding="utf-8") as playlist_stats_file:
            playlist_stats_data = json.load(playlist_stats_file)

        value_status = playlist_stats_data['STATUS']

        return value_status
    
    elif type_id == 'clear':
   
        playlist_data = {}

        with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "w", encoding="utf-8") as playlist_file_write:
            json.dump(playlist_data, playlist_file_write, indent=4, ensure_ascii=False)

    elif type_id == 'queue':
        
        with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "r", encoding="utf-8") as queue_file:
            queue_data = json.load(queue_file)

        with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "r", encoding="utf-8") as playlist_file:
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

        data_dump = json.dumps(list_queue_list, ensure_ascii=False)

        return data_dump


@eel.expose
def sr_config_py(type_id,data_receive):
    
    if type_id == 'get':
        
        with open(f'{appdata_path}/rewardevents/web/src/player/config/commands.json', 'r', encoding='utf-8') as commands_music_file:
            commands_music_data = json.load(commands_music_file)

        with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding='utf-8') as not_music_file:
            not_music_data = json.load(not_music_file)
        
        with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'r', encoding='utf-8') as delay_music_file:
            delay_music_data = json.load(delay_music_file)

        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r', encoding="utf-8") as status_music_file:
            status_music_data = json.load(status_music_file)
        
        data = {
            "allow_music" : status_music_data['STATUS_MUSIC_ENABLE'],
            "max_duration" : status_music_data['max_duration'],
            "redeem_music" : commands_music_data['redeem'],
            "not_status": not_music_data['HTML_PLAYER_ACTIVE'],
            "cmd_request": commands_music_data['request'],
            "cmd_request_status": delay_music_data['request-status'],
            "cmd_request_delay" : delay_music_data['request-delay'],
            "cmd_volume": commands_music_data['volume'],
            "cmd_volume_status": delay_music_data['volume-status'],
            "cmd_volume_delay" : delay_music_data['volume-delay'],
            "cmd_skip": commands_music_data['skip'],
            "cmd_skip_status": delay_music_data['skip-status'],
            "cmd_skip_delay" : delay_music_data['skip-delay'],
            "cmd_next": commands_music_data['next'],
            "cmd_next_status": delay_music_data['next-status'],
            "cmd_next_delay": delay_music_data['next-delay'],
            "cmd_atual": commands_music_data['atual'],
            "cmd_atual_status": delay_music_data['atual-status'],
            "cmd_atual_delay": delay_music_data['atual-delay'],
            "request_perm": commands_music_data['request-perm'],
            "atual_perm": commands_music_data['atual-perm'],
            "next_perm": commands_music_data['next-perm'],
            "skip_perm": commands_music_data['skip-perm'],
            "volume_perm": commands_music_data['volume-perm'],
        }

        music_dump = json.dumps(data, ensure_ascii=False)

        return music_dump
    
    elif type_id == 'save':
        
        data = json.loads(data_receive)

        try:

            allow = data['allow_music_save']
            redeem = data['redeem_music_data']
            max_duration = data['max_duration']
            status_music = data['music_not_status_data']
            command_request = data['command_request_data']
            command_request_status = data['command_request_status']
            command_request_perm = data['command_request_perm']
            command_request_delay = data['command_request_delay']
            command_volume = data['command_volume_data']
            command_volume_status = data['command_volume_status']
            command_volume_perm = data['command_volume_perm']
            command_volume_delay = data['command_volume_delay']
            command_skip = data['command_skip_data']
            command_skip_status = data['command_skip_status']
            command_skip_perm = data['command_skip_perm']
            command_skip_delay = data['command_skip_delay']
            command_next = data['command_next_data']
            command_next_status = data['command_next_status']
            command_next_perm = data['command_next_perm']
            command_next_delay = data['command_next_delay']
            command_atual = data['command_atual_data']
            command_atual_status = data['command_atual_status']
            command_atual_perm = data['command_atual_perm']
            command_atual_delay = data['command_atual_delay']

            with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'r', encoding="utf-8") as not_status_music_file:
                not_status_music_data = json.load(not_status_music_file)

            not_status_music_data['HTML_PLAYER_ACTIVE'] = status_music

            with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json', 'w', encoding="utf-8") as status_music_file_write:
                json.dump(not_status_music_data, status_music_file_write, indent=6, ensure_ascii=False)
                
                
            with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'r', encoding='utf-8') as delay_music_file:
                delay_music_data = json.load(delay_music_file)
                
            delay_music_data['request-status'] = command_request_status
            delay_music_data['volume-status'] = command_volume_status
            delay_music_data['skip-status'] = command_skip_status
            delay_music_data['next-status'] = command_next_status
            delay_music_data['atual-status'] = command_atual_status
            
            delay_music_data['request-delay'] = command_request_delay
            delay_music_data['volume-delay'] = command_volume_delay
            delay_music_data['skip-delay'] = command_skip_delay
            delay_music_data['next-delay'] = command_next_delay
            delay_music_data['atual-delay'] = command_atual_delay
            
            with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                json.dump(delay_music_data, delay_music_file_w, indent=6, ensure_ascii=False)


            with open(f'{appdata_path}/rewardevents/web/src/player/config/commands.json', 'r', encoding='utf-8') as commands_music_file:
                commands_music_data = json.load(commands_music_file)
            
            commands_music_data['redeem'] = redeem
            commands_music_data['request'] = command_request
            commands_music_data['request-perm'] = command_request_perm
            commands_music_data['volume'] = command_volume
            commands_music_data['volume-perm'] = command_volume_perm
            commands_music_data['skip'] = command_skip
            commands_music_data['skip-perm'] = command_skip_perm
            commands_music_data['next'] = command_next
            commands_music_data['next-perm'] = command_next_perm
            commands_music_data['atual'] = command_atual
            commands_music_data['atual-perm'] = command_atual_perm
            
            with open(f'{appdata_path}/rewardevents/web/src/player/config/commands.json', 'w', encoding='utf-8') as commands_music_file_w:
                json.dump(commands_music_data, commands_music_file_w, indent=6, ensure_ascii=False)
            
        

            with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r', encoding="utf-8") as status_music_file:
                status_music_data = json.load(status_music_file)
                
                status_music_data['STATUS_MUSIC_ENABLE'] = allow
                status_music_data['max_duration'] = max_duration
            
            with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'w', encoding="utf-8") as status_music_file_w:
                json.dump(status_music_data, status_music_file_w, indent=6, ensure_ascii=False)
                    
            eel.toast_notifc('success')

        except Exception as e:
            
            utils.error_log(e)

            eel.toast_notifc('error')

    elif type_id == 'get-status':
        
        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r', encoding="utf-8") as status_music_file:
            status_music_data = json.load(status_music_file)
            
        status = status_music_data['STATUS_MUSIC_ENABLE']

        return status

    elif type_id == 'list_add':

        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r+', encoding='utf-8') as config_music_file:
            config_music_data = json.load(config_music_file)

            config_music_data["blacklist"].append(data_receive)
            
            config_music_file.seek(0)
            json.dump(config_music_data, config_music_file, indent=6, ensure_ascii=False)
            config_music_file.truncate()  
            
            eel.toast_notifc('Termo ou nome adicionado')
            
    elif type_id == 'list_get':

        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r+', encoding='utf-8') as config_music_file:
            config_music_data = json.load(config_music_file)
            
            config_music_data_dump = json.dumps(config_music_data["blacklist"], ensure_ascii=False)

            return config_music_data_dump
         
    elif type_id == 'list_rem':

        with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r+', encoding='utf-8') as config_music_file:
            config_music_data = json.load(config_music_file)
            
            
            if data_receive in commands_music_data:
            
                config_music_data["blacklist"].remove(data_receive)
            
                config_music_file.seek(0)
                json.dump(config_music_data, config_music_file, indent=6, ensure_ascii=False)
                config_music_file.truncate()
                
                eel.toast_notifc('Termo ou nome removido') 
            
            else:
                
                eel.toast_notifc('O termo ou nome não está na lista') 


@eel.expose
def update_check(type_id):
    if type_id == 'check':

        response = req.get("https://api.github.com/repos/GGTEC/RewardEvents/releases/latest")
        response_json = json.loads(response.text)
        version = response_json['tag_name']

        if version != 'V5.0.0':

            return 'true'
        else:

            return 'false'

    elif type_id == 'open':

        url = 'https://github.com/GGTEC/RewardEvents/releases'
        webbrowser.open(url, new=0, autoraise=True)


@eel.expose
def clip():
    
    info_clip = twitch_api.create_clip(broadcaster_id=authdata.BROADCASTER_ID())

    if 'error' in info_clip.keys():

        message_clip_error_load = utils.messages_file_load('clip_error_clip')
        
        if utils.send_message("CLIP"):
            send(message_clip_error_load)

        eel.toast_notifc('Erro ao criar o clip')

    else:

        clip_id = info_clip['data'][0]['id']

        message_clip_user_load = utils.messages_file_load('clip_create_clip')

        message_clip_user = message_clip_user_load.replace('{user}', authdata.USERNAME())
        message_final = message_clip_user.replace('{clip_id}', clip_id)

        eel.toast_notifc(message_final)

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


@eel.expose
def timer():
    """
        Modulo para mensagens automaticas.
    """

    while True:

        try:
            
            with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'r', encoding='utf-8') as timer_data_file:
                timer_data = json.load(timer_data_file)

            timer_int = timer_data['TIME']
            timer_max_int = timer_data['TIME_MAX']

            next_timer = randint(timer_int, timer_max_int)


            if bot_loaded:

                
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

                                with open(f'{appdata_path}/rewardevents/web/src/config/timer.json', 'w', encoding='utf-8') as update_last_file:
                                    json.dump(timer_data, update_last_file, indent=4, ensure_ascii=False)

                                if timer_message[message_key]['type_timer'] == 0:
                                    send(timer_message[message_key]['message'])
                                
                                elif timer_message[message_key]['type_timer'] == 1:
                                    send_announcement(timer_message[message_key]['message'],timer_message[message_key]['color'])

                                time.sleep(next_timer)
                        else:

                            if timer_message[message_key]['type_timer'] == 0:
                                send(timer_message[message_key]['message'])
                            
                            elif timer_message[message_key]['type_timer'] == 1:
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
    os.makedirs(f'{appdata_path}/rewardevents/web/src/user_info', exist_ok=True)

    if type_id == 'save':

        mod_dict = {}
        mod_info = twitch_api.get_moderators(broadcaster_id=authdata.BROADCASTER_ID())

        for index in range(len(mod_info['data'])):
            user_id = mod_info['data'][index]['user_id']
            user_name = mod_info['data'][index]['user_name']
            mod_dict[user_id] = user_name

        with open(f'{appdata_path}/rewardevents/web/src/user_info/mods.json', 'w', encoding='utf-8') as mods_file:
            json.dump(mod_dict, mods_file, indent=4, ensure_ascii=False)


        sub_dict = {}
        sub_info = twitch_api.get_broadcaster_subscriptions(broadcaster_id=authdata.BROADCASTER_ID())

        for index in range(len(sub_info['data'])):
            user_id = sub_info['data'][index]['user_id']
            user_name = sub_info['data'][index]['user_name']
            sub_dict[user_id] = user_name

        with open(f'{appdata_path}/rewardevents/web/src/user_info/subs.json', 'w', encoding='utf-8') as subs_file:
            json.dump(sub_dict, subs_file, indent=4, ensure_ascii=False)

    elif type_id == 'get_sub':

        with open(f'{appdata_path}/rewardevents/web/src/user_info/subs.json', 'r', encoding='utf-8') as subs_file:
            subs_data = json.load(subs_file)

        if 'user_id' in subs_data.keys():
            return True
        else:
            return False

    elif type_id == 'get_mod':

        with open(f'{appdata_path}/rewardevents/web/src/user_info/mods.json', 'r', encoding='utf-8') as mod_file:
            mod_data = json.load(mod_file)

        if 'user_id' in mod_data.keys():
            return True
        else:
            return False


def start_play(title, user_input, redem_by_user):

    global caching

    def download_music(link):

        music_dir_check = os.path.exists(extDataDir + f'/web/src/player/cache/music.mp3')
        music_mp4_check = os.path.exists(extDataDir + f'/web/src/player/cache/music.mp4')

        if music_mp4_check:
            os.remove(extDataDir + f'/web/src/player/cache/music.mp4')

        if music_dir_check:
            os.remove(extDataDir + f'/web/src/player/cache/music.mp3')

        def my_hook(d):
            if d['status'] == 'finished':
                eel.update_music_name('Download concluido','Em pós processamento')
            else:
                eel.update_music_name('Baixando musica. aguarde', d['_percent_str'])

        try:
            
            #ffmpeg_loc
            #ffmpeg/ffmpeg.exe
            ydl_opts = {
                'progress_hooks': [my_hook],
                'final_ext': 'mp3',
                'format': 'bestaudio',
                'noplaylist': True,
                'quiet': True,
                'no_color': True,
                'outtmpl': extDataDir + f'/web/src/player/cache/music.%(ext)s',
                'ffmpeg_location': ffmpeg_loc,
                'force-write-archive': True,
                'force-overwrites': True,
                'keepvideo': False,
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

    response_album = utils.album_search(title,user_input)
    success = response_album['success']

    if success == 1:

        media_name = response_album['music']
        media_artist = response_album['artist']
        music_link = response_album['link']

        caching = 1

        if download_music(music_link):

            if media_artist == '0':
                music_artist = ""
            else:
                music_artist = media_artist

            with open(f'{appdata_path}/rewardevents/web/src/player/list_files/currentsong.txt', "w", encoding="utf-8") as file_object:
                file_object.write(media_name + ' - ' + music_artist + '\n')

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

            message_replace = utils.replace_all(utils.messages_file_load('music_playing'), aliases)
            if utils.send_message("STATUS_MUSIC"):
                send(message_replace)

            eel.player('play', 'http://localhost:7000/src/player/cache/music.mp3', '1')
            eel.toast_notifc(f'Reproduzindo {music_name_short} - {music_artist}')

            caching = 0

        else:

            caching = 0
            eel.update_music_name('Erro ao processar musica', 'Erro ao processar musica')
            eel.toast_notifc(f'Erro ao processar musica')
            if utils.send_message("STATUS_MUSIC"):
                send(utils.messages_file_load('music_process_cache_error'))

    else:
        
        eel.toast_notifc(f'Erro ao processar musica')
        if utils.send_message("STATUS_MUSIC"):
            send(utils.messages_file_load('music_process_error'))


def loopcheck():

    while True:

        if loaded_status == 1 and bot_loaded == 1:
            
            with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r', encoding="utf-8") as playlist_status_file:
                playlist_execute_data = json.load(playlist_status_file)
            playlist_execute_value = playlist_execute_data['STATUS']
            playlist_execute = int(playlist_execute_value)

            with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "r", encoding="utf-8") as playlist_file:
                playlist_data = json.load(playlist_file)
            check_have_playlist = any(playlist_data.keys())

            with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "r", encoding="utf-8") as queue_file:
                queue_data = json.load(queue_file)
                
            check_have_queue = any(queue_data.keys())

            playing = eel.player('playing', 'none', 'none')()
            
            if caching == 0 and playing == 'False':
                
                if check_have_queue:

                    queue_keys = [int(x) for x in queue_data.keys()]
                    music_data_key = str(min(queue_keys))

                    music = queue_data[music_data_key]['MUSIC']
                    user = queue_data[music_data_key]['USER']
                    title = queue_data[music_data_key]['MUSIC_NAME']

                    del queue_data[music_data_key]

                    with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "w", encoding="utf-8") as queue_file_write:
                        json.dump(queue_data, queue_file_write, indent=4)

                    start_play(title, music, user)

                    time.sleep(5)

                elif check_have_playlist:

                    if playlist_execute == 1:

                        playlist_keys = [int(x) for x in playlist_data.keys()]
                        music_data = str(min(playlist_keys))

                        music = playlist_data[music_data]['MUSIC']
                        user = playlist_data[music_data]['USER']
                        title = playlist_data[music_data]['MUSIC_NAME']

                        del playlist_data[music_data]


                        with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "w", encoding="utf-8") as playlist_file_write:
                            json.dump(playlist_data, playlist_file_write, indent=4)

                        start_play(title, music, user)


                    else:
                        time.sleep(3)
                else:
                    time.sleep(3)
                    eel.update_music_name('Aguardando', 'Aguardando')
            else:
                
                with open(f'{appdata_path}/rewardevents/web/src/player/list_files/currentsong.txt', "r", encoding="utf-8") as file_object:
                    songname = file_object.read()
                    
                    music = songname.split('-')[0]
                    artist = songname.split('-')[1]
                    
                    eel.update_music_name(music, artist)
                    
                time.sleep(3)


def process_redem_music(user_input, redem_by_user):

    user_input = user_input.strip()
    
    eel.update_music_name('Processando pedido', 'Aguarde')
    eel.toast_notifc(f'Processando pedido...')

    with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "r", encoding="utf-8") as queue_file:
        queue_data = json.load(queue_file)
        
    with open(f'{appdata_path}/rewardevents/web/src/player/config/config.json', 'r', encoding='utf-8') as config_music_file:
        config_music_data = json.load(config_music_file)
    
    blacklist = config_music_data['blacklist']
    max_duration = int(config_music_data['max_duration'])
    
    check_have = any(queue_data.keys())


    if not check_have:
        last_key = 1
    else:
        queue_keys = [int(x) for x in queue_data.keys()]
        last_key = str(max(queue_keys) + 1)
        

    if validators.url(user_input):
        
        find_youtube = user_input.find('youtube')
        find_youtu = user_input.find('youtu')

        if find_youtube != -1 or find_youtu != -1:
            
            try:
                
                if not any(item in user_input for item in blacklist):
                
                    yt = YouTube(user_input)
                    music_name = yt.title
                    music_leght = yt.length

                    if music_leght < max_duration:

                        with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "r", encoding="utf-8") as queue_file:
                            queue_data = json.load(queue_file)

                        queue_data[last_key] = {"MUSIC": user_input, "USER": redem_by_user, "MUSIC_NAME": music_name}

                        with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "w", encoding="utf-8") as queue_file_write:
                            json.dump(queue_data, queue_file_write, indent=4)

                        aliases = {'{user}': redem_by_user, '{user_input}': user_input, '{music}': music_name}
                        message = utils.messages_file_load('music_added_to_queue')
                        message_replaced = utils.replace_all(message, aliases)

                        if utils.send_message("STATUS_MUSIC_CONFIRM"):
                            send(message_replaced)

                    else:

                        music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                        aliases = {
                            '{user}': str(redem_by_user),
                            '{user_input}': str(user_input),
                            '{music}': str(music_name),
                            '{music_short}': str(music_name_short)
                        }

                        message = utils.messages_file_load('music_leght_error')
                        message_replaced = utils.replace_all(message, aliases)

                        if utils.send_message("STATUS_MUSIC_CONFIRM"):
                            send(message_replaced)
                
                else:
                    
                    music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                    aliases = {
                        '{user}': str(redem_by_user),
                        '{user_input}': str(user_input),
                        '{music}': str(music_name),
                        '{music_short}': str(music_name_short)
                    }

                    message = utils.messages_file_load('music_blacklist')
                    message_replaced = utils.replace_all(message, aliases)

                    if utils.send_message("STATUS_MUSIC_CONFIRM"):
                        send(message_replaced)
                            
            except Exception as e:
                
                utils.error_log(e)

                aliases = {'{user}': str(redem_by_user), '{user_input}': str(user_input)}
                message = utils.messages_file_load('music_add_error')
                message_replaced = utils.replace_all(message, aliases)

                if utils.send_message("STATUS_MUSIC_CONFIRM"):
                    send(message_replaced)

        else:
            
            message_replaced = utils.messages_file_load('music_link_youtube')
            if utils.send_message("STATUS_MUSIC_CONFIRM"):
                send(message_replaced)

    else:
        
        try:
            
            if not any(item in user_input for item in blacklist):
            
                search_youtube = Search(user_input)
                result_search = search_youtube.results[0].__dict__
                url_youtube = result_search['watch_url']
                
                yt = YouTube(url_youtube)
                video_title = yt.title
                music_leght = yt.length
                
                if music_leght < max_duration:

                    with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "r", encoding="utf-8") as queue_file:
                        queue_data = json.load(queue_file)

                    queue_data[last_key] = {"MUSIC": url_youtube, "USER": redem_by_user, "MUSIC_NAME": video_title}

                    with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "w", encoding="utf-8") as queue_file_write:
                        json.dump(queue_data, queue_file_write, indent=4)

                    music_name_short = textwrap.shorten(video_title, width=13, placeholder="...")

                    aliases = {
                        '{user}': redem_by_user,
                        '{user_input}': user_input,
                        '{music}': video_title,
                        '{music_short}': music_name_short
                    }

                    message = utils.messages_file_load('music_added_to_queue')

                    message_replaced = utils.replace_all(message, aliases)

                    if utils.send_message("STATUS_MUSIC_CONFIRM"):
                        send(message_replaced)
                        
                else:
                    
                    music_name_short = textwrap.shorten(video_title, width=13, placeholder="...")
                    
                    aliases = {
                        '{user}': str(redem_by_user),
                        '{user_input}': str(user_input),
                        '{music}': str(video_title),
                        '{music_short}': str(music_name_short)
                    }

                    message = utils.messages_file_load('music_leght_error')
                    message_replaced = utils.replace_all(message, aliases)

                    if utils.send_message("STATUS_MUSIC_CONFIRM"):
                        send(message_replaced)
                        
            else:
                    
                music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                aliases = {
                    '{user}': str(redem_by_user),
                    '{user_input}': str(user_input),
                    '{music}': str(music_name),
                    '{music_short}': str(music_name_short)
                }

                message = utils.messages_file_load('music_blacklist')
                message_replaced = utils.replace_all(message, aliases)

                if utils.send_message("STATUS_MUSIC_CONFIRM"):
                    send(message_replaced)
                    
        except Exception as e:
            utils.error_log(e)
            
            eel.update_music_name('Erro ao processar musica', 'Erro ao processar musica')
            eel.toast_notifc(f'Erro ao processar musica')
            if utils.send_message("STATUS_MUSIC"):
                send(utils.messages_file_load('music_process_cache_error'))
                
                
def receive_redeem(data_rewards, received_type):
    
    def check_user_level(user_levels):
    
        if "mod" in user_levels:
            return "mod"
        elif "subs" in user_levels:
            return "subs"
        elif "vip" in user_levels:
            return "vip"
        elif "top_chatter" in user_levels:
            return "top_chatter"
        else:
            return "spec"
        
    with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "r") as counter_file_r:
        counter_file_r.seek(0)
        digit = counter_file_r.read()
        counter_actual = int(digit)

    with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json','r',encoding='utf-8') as chat_file:
        chat_data = json.load(chat_file)
    
    
    now = datetime.datetime.now()
    format = chat_data['time-format']
    
    if chat_data['data-show'] == 1:
        if chat_data['type-data'] == "passed":
            chat_time = now.strftime('%Y-%m-%dT%H:%M:%S')
        elif chat_data['type-data'] == "current":
            chat_time = now.strftime(format)
    else: 
        chat_time = ''
            
    redeem_reward_name = '0'
    redeem_by_user = '0'
    user_input = '0'
    user_level = '0'
    user_id_command = '0'
    command_receive = '0'
    prefix = '0'

    with open(f'{appdata_path}/rewardevents/web/src/player/config/commands.json') as player_file:
        player_data = json.load(player_file)

    player_reward = player_data['redeem']

    if received_type == 'redeem':

        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
            user_data_load = json.load(user_data_file)
        
        redeem_reward_name = data_rewards['reward_title']
        redeem_by_user = data_rewards['user_name']
        user_id = data_rewards['user_id']
        user_input = data_rewards['user_input']
        redeem_reward_image = data_rewards['image']

        perms_list = []
        if user_id == authdata.BROADCASTER_ID():
            perms_list.append('streamer')
            
        elif redeem_by_user in user_data_load:
            
            message_mod = user_data_load[redeem_by_user]['mod']
            message_vip = user_data_load[redeem_by_user]['vip']
            message_sub = user_data_load[redeem_by_user]['sub']
            message_regular = user_data_load[redeem_by_user]['regular']
            message_chatter = user_data_load[redeem_by_user]['top_chatter']
            
            if message_mod == 1:
                perms_list.append('mod')
            if message_vip == 1:
                perms_list.append('vip')
            if message_sub == 1:
                perms_list.append('subs')
            if message_regular == 1:
                perms_list.append('regular')
            if message_chatter == 1:
                perms_list.append('top_chatter')
            
            user_level = check_user_level(perms_list)
            
        else:
            
            user_level = 'spec'

        img_redeem_data = req.get(redeem_reward_image).content

        with open(extDataDir + f'/web/src/Request.png', 'wb') as image_redeem:
            image_redeem.write(img_redeem_data)

        with open(f'{appdata_path}/rewardevents/web/src/Request.png', 'wb') as image_redeem:
            image_redeem.write(img_redeem_data)
            
        data = {
            "message" : f"Usuário {redeem_by_user} resgatou {redeem_reward_name}",
            "font_size" : chat_data['font-size'],
            "color" : chat_data['color-not'],
            "data_show" : chat_data["data-show"],
            "chat_time" : chat_time,
            "type_data" : chat_data["type-data"],
        }
        
        chat_data_dump = json.dumps(data, ensure_ascii=False)
        eel.append_notice(chat_data_dump)

    elif received_type == 'command':
        
        redeem_reward_name = data_rewards['REDEEM']
        redeem_by_user = data_rewards['USERNAME']
        user_input = data_rewards['USER_INPUT']
        user_level = data_rewards['USER_LEVEL']
        user_id = data_rewards['USER_ID']

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

    with open(f'{appdata_path}/rewardevents/web/src/config/pathfiles.json', 'r', encoding='utf-8') as path_file:
        path = json.load(path_file)

    with open(f'{appdata_path}/rewardevents/web/src/giveaway/config.json', 'r', encoding='utf-8') as giveaway_path_file:
        giveaway_path = json.load(giveaway_path_file)

    giveaway_redeem = giveaway_path['redeem']
    
    with open(f'{appdata_path}/rewardevents/web/src/counter/config.json','r',encoding='utf-8') as counter_file:
        counter_data = json.load(counter_file)
        
    counter_redeem = counter_data['redeem']

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

            chat_response = path[redeem_reward_name]['chat_response']
            response_redus = utils.replace_all(chat_response, aliases)

            if utils.send_message("RESPONSE"):
                send(response_redus)
    
    def play_video():

        video_path = path[redeem_reward_name]['path']
        send_response_value = path[redeem_reward_name]['send_response']

        if utils.update_video(video_path) == True:

            time.sleep(1)
            video_not_file = open(f"{appdata_path}/rewardevents/web/src/config/notfic.json","r",encoding="utf-8")
            video_not_data = json.load(video_not_file)
            
            time_show = path[redeem_reward_name]['show_time']
            source = video_not_data['HTML_VIDEO']
                
            obs_events.show_source_video(source,time_show)

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']
            response_redus = utils.replace_all(chat_response, aliases)

            if utils.send_message("RESPONSE"):
                send(response_redus)

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
                
                response_redus = utils.replace_all(utils.messages_file_load('error_tts_no_text'), aliases)
                if utils.send_message("RESPONSE"):
                    send(response_redus)
                        
        else:
                
            response_redus = utils.replace_all(utils.messages_file_load('error_tts_disabled'), aliases)
            if utils.send_message("RESPONSE"):
                send(response_redus)
                                     
    def change_scene():

        scene_name = path[redeem_reward_name]['scene_name']
        keep = path[redeem_reward_name]['keep']
        time_show = path[redeem_reward_name]['time']
        send_response_value = path[redeem_reward_name]['send_response']

        if send_response_value == 1:

            chat_response = path[redeem_reward_name]['chat_response']

            try:
                response_redus = utils.replace_all(chat_response, aliases)
                if utils.send_message("RESPONSE"):
                    send(response_redus)

            except Exception as e:

                utils.error_log(e)
                if utils.send_message("RESPONSE"):
                    send(chat_response)

        obs_events.show_scene(scene_name, time_show, keep)

    def send_message():

        chat_response = path[redeem_reward_name]['chat_response']

        try:
            response_redus = utils.replace_all(chat_response, aliases)

            if utils.send_message("RESPONSE"):
                send(response_redus)
        except Exception as e:

            utils.error_log(e)
            if utils.send_message("RESPONSE"):
                send(chat_response)

    def toggle_filter():

        source_name = path[redeem_reward_name]['source_name']
        filter_name = path[redeem_reward_name]['filter_name']
        time_show = path[redeem_reward_name]['time']
        keep = path[redeem_reward_name]['keep']

        send_response_value = path[redeem_reward_name]['send_response']

        if send_response_value:

            chat_response = path[redeem_reward_name]['chat_response']

            try:
                response_redus = utils.replace_all(chat_response, aliases)

                if utils.send_message("RESPONSE"):
                    send(response_redus)
            except Exception as e:

                utils.error_log(e)
                if utils.send_message("RESPONSE"):
                    send(chat_response)

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

                response_redus = utils.replace_all(chat_response, aliases)
                if utils.send_message("RESPONSE"):
                    send(response_redus)

            except Exception as e:

                utils.error_log(e)
                if utils.send_message("RESPONSE"):
                    send(chat_response)

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
            response_redus = utils.replace_all(chat_response, aliases)

            if utils.send_message("RESPONSE"):
                send(response_redus)

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

            message_clip_user = message_clip_user_load.replace('{user}', redeem_by_user)
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

        with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "r") as counter_file_r:
            if len(counter_file_r.read()) == 0:
                
                with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "w") as counter_file_w:
                    countercount = 1 
                    counter_file_w.write(countercount)
                    eel.update_counter_value(countercount)

            else:

                counter_file_r.seek(0)
                digit = counter_file_r.read()

                if digit.isdigit():

                    counter = int(digit)
                    countercount = counter + 1

                else:
                    countercount = 0

                with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "w") as counter_file_w:
                    counter_file_w.write(str(countercount))
                    eel.update_counter_value(countercount)

        if send_response_value:

            chat_response = utils.messages_file_load('response_set_counter')
            aliases = {
                '{value}' : str(countercount)
            }

            try:
                response_redus = utils.replace_all(chat_response, aliases)

                if utils.send_message("RESPONSE"):
                    send(response_redus)
                    
            except Exception as e:

                utils.error_log(e)

                if utils.send_message("RESPONSE"):
                    send(chat_response)

    def add_giveaway():

        data = {
            'new_name' : redeem_by_user,
            'user_level' : user_level
        }
        giveaway_py('add_user', data)

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
        'giveaway': add_giveaway
    }

    if authdata.TOKEN() and authdata.TOKENBOT():
        if redeem_reward_name in path.keys():
            redeem_type = path[redeem_reward_name]['type']
            if redeem_type in eventos:
                eventos[redeem_type]()
        elif redeem_reward_name == giveaway_redeem:
            add_giveaway()
        elif redeem_reward_name == player_reward:

            status_music = sr_config_py('get-status','null')
            
            if status_music == 1:

                music_process_thread = threading.Thread(target=process_redem_music, args=(user_input, redeem_by_user,),
                                                        daemon=True)
                music_process_thread.start()
                
            else:
                aliases_commands = {'{user}': str(redeem_by_user)}
                message_replace_response = utils.replace_all(utils.messages_file_load('music_disabled'), aliases_commands)

                if utils.send_message("RESPONSE"):
                    send(message_replace_response)

        elif redeem_reward_name == counter_redeem:
            add_counter()


@eel.expose
def open_py(type_id,link_profile):

    if type_id == "user":
        webbrowser.open('https://www.twitch.tv/'+link_profile, new=0, autoraise=True)

    elif type_id == "appdata":

        try:
            subprocess.Popen(f'explorer "{appdata_path}\\rewardevents\\web"')
        except subprocess.CalledProcessError as e:
            print(f"Erro ao chamar subprocesso: {e}")

    elif type_id == "errolog":
        arquivo = f'{appdata_path}/rewardevents/web/src/error_log.txt'
        os.system('notepad.exe ' + arquivo)

    elif type_id == "discord":
        webbrowser.open('https://discord.io/ggtec', new=0, autoraise=True)
    
    elif type_id == "wiki":
        webbrowser.open('https://ggtec.netlify.app', new=0, autoraise=True)


@eel.expose
def send_not_fun(data: dict) -> None:

    """
        Processa uma mensagem para enviar notificações de eventos.

        Args:
            data (dict): Um dicionário contendo as seguintes chaves obrigatórias:
                - 'type': Uma string que descreve o tipo de mensagem. Exemplo: 'follow', 'sub', resub. (minúscula)
                - 'username': Uma string contendo o nome de usuário.
                - 'message': Uma string contendo a mensagem preparada e codificada.

        Raises:
            TypeError: Se o argumento não for um dicionário ou não conter todas as chaves obrigatórias.

        Exemplo:
            >>> data = {'type': 'follow', 'username': 'gg_tec', 'message': 'GG_TEC Seguiu o canal'}
            >>> process_data(data)
    """
    
    with open(f'{appdata_path}/rewardevents/web/src/config/event_not.json','r',encoding='utf-8') as event_file:
        event_data = json.load(event_file)
        
    with open(f'{appdata_path}/rewardevents/web/src/config/notfic.json','r',encoding='utf-8') as not_config_file:
        not_config_data = json.load(not_config_file)
    
    
    type_id = data['type']
    
    def start_notification():
        
        def save_tts():
            
            message = data['message']
            message = message.replace('<br>','')
            
            if message != "":
                    
                tts = gTTS(text=message, lang='pt-br', slow=False)
                tts.save(f'{appdata_path}/rewardevents/web/src/player/cache/tts.mp3')
                
                return True
            
            else :
                
                return True

        img_src = event_data[type_id]['image']
        img_px = event_data[type_id]['image_px']
        audio_src = event_data[type_id]['audio']
        audio_volume = event_data[type_id]['audio_volume']
        response_px = event_data[type_id]['response_px']
        image_above = event_data[type_id]['text_over_image']
        weight = event_data[type_id]['response_weight']
        color = event_data[type_id]['response_color']
        

        if event_data[type_id]['tts'] == 1:

            data_not = {
                "type_id" : type_id,
                "username" : data['username'],
                "message" : data['message_html'],
                "duration" : not_config_data['HTML_EVENTS_TIME'],
                "img_src" : img_src,
                "img_px": img_px,
                "audio_src" : audio_src,
                "audio_volume" : audio_volume,
                "response_px": response_px,
                "image_above" : image_above,
                "play_tts" : 1,
                "weight" : weight,
                "color" : color
            }

            if save_tts():

                if utils.update_event(data_not):
                    
                    not_thread_2 = threading.Thread(target=obs_events.notification_event(), args=(), daemon=True)
                    not_thread_2.start()
        
        else :
            
            data_not = {
                "username" : data['username'],
                "message" : data['message_html'],
                "duration" : not_config_data['HTML_EVENTS_TIME'],
                "img_src" : img_src,
                "img_px": img_px,
                "audio_src" : audio_src,
                "audio_volume" : audio_volume,
                "response_px": response_px,
                "image_above" : image_above,
                "play_tts" : 0,
                "weight" : weight,
                "color" : color
            }
            
            if utils.update_event(data_not):
                    
                not_thread_2 = threading.Thread(target=obs_events.notification_event(), args=(), daemon=True)
                not_thread_2.start()
            

    if event_data[type_id]['status'] == 1:
        
        not_thread_4 = threading.Thread(target=start_notification, args=(), daemon=True)
        not_thread_4.start()
    
 
@eel.expose
def chat_config(data_save,type_config):

    if type_config == 'save':
        
        with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json', 'r+', encoding='utf-8') as chat_file:
            chat_data = json.load(chat_file)
            
            data_received = json.loads(data_save)
            
            chat_data["appply-colors"] = data_received["appply_colors"]
            chat_data["appply-no-colors"] = data_received["appply_no_colors"]
            chat_data["data-show"] = data_received["data_show"]
            chat_data["type-data"] = data_received["type_data"]
            chat_data["time-format"] = data_received["time_format"]
            chat_data["color-apply"] = data_received["color_apply"]
            chat_data["block-color"] = data_received["chat_colors_block"]
            chat_data["color-not"] = data_received["color_not"]
            chat_data["color-not-join"] = data_received["color_not_join"]
            chat_data["color-not-leave"] = data_received["color_not_leave"]
            chat_data["font-size"] = data_received["font_size"]
            chat_data["show-badges"] = data_received["show_badges"]
            chat_data["wrapp-message"] = data_received["wrapp_message"]
            chat_data["not-user-join"] = data_received["not_user_join"]
            chat_data["not-user-leave"] = data_received["not_user_leave"]
            chat_data["not-user-sound"] = data_received["not_user_sound"]
            chat_data["not-sound-path"] = data_received["not_sound_path"]
            chat_data["send-greetings"] = data_received["greetings_join"]
            chat_data["greetings"] = data_received["greetings"]
            chat_data['top_chatter_min'] = data_received['top_chatter']
            chat_data['regular_min'] = data_received['regular']
            
            chat_file.seek(0)
            json.dump(chat_data, chat_file, indent=6, ensure_ascii=False)
            chat_file.truncate()
            
            eel.toast_notifc('success')  
        
    elif type_config == 'get':

        with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json','r',encoding='utf-8') as chat_file:
            chat_data = json.load(chat_file)
            
            chat_data_return = {
                "appply_colors" : chat_data["appply-colors"],
                "appply_no_colors" : chat_data["appply-no-colors"],
                "color_apply" : chat_data["color-apply"],
                "block_color" : chat_data["block-color"],
                "time_format" : chat_data["time-format"],
                "type_data" : chat_data["type-data"],
                "data_show" : chat_data["data-show"],
                "color_not" : chat_data["color-not"],
                "color_not_join" : chat_data["color-not-join"],
                "color_not_leave" : chat_data["color-not-leave"],
                "font_size" : chat_data["font-size"],
                "show_badges" : chat_data["show-badges"],
                "wrapp_message" : chat_data["wrapp-message"],
                "not_user_join" : chat_data["not-user-join"],
                "not_user_leave" : chat_data["not-user-leave"],
                "not_user_sound" : chat_data["not-user-sound"],
                "not_sound_path" : chat_data["not-sound-path"],
                "greetings_join" : chat_data["send-greetings"],
                "greetings" : chat_data["greetings"],
                "top_chatter" : chat_data["top_chatter_min"],
                "regular" :  chat_data["regular_min"],
            }
            
            chat_data_dump = json.dumps(chat_data_return, ensure_ascii=False)

            return chat_data_dump

    elif type_config == 'list_add':

        with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json', 'r+', encoding='utf-8') as chat_file:
            chat_data = json.load(chat_file)
            
            chat_data["user_not_display"].append(data_save)
            
            chat_file.seek(0)
            json.dump(chat_data, chat_file, indent=6, ensure_ascii=False)
            chat_file.truncate()  
            
            eel.toast_notifc('Nome adicionado')
            
    elif type_config == 'list_get':

        with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json','r',encoding='utf-8') as chat_file:
            chat_data = json.load(chat_file)
            
            chat_data_dump = json.dumps(chat_data["user_not_display"], ensure_ascii=False)

            return chat_data_dump
         
    elif type_config == 'list_rem':

        with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json', 'r+', encoding='utf-8') as chat_file:
            chat_data = json.load(chat_file)
            
            if data_save in chat_data:
            
                chat_data["user_not_display"].remove(data_save)
            
                chat_file.seek(0)
                json.dump(chat_data, chat_file, indent=6, ensure_ascii=False)
                chat_file.truncate()
                
                eel.toast_notifc('Nome removido') 
            
            else:
                
                eel.toast_notifc('O nome não está na lista') 

    elif type_config == 'list_bot_add':
        
        with open(f'{appdata_path}/rewardevents/web/src/user_info/bot_list_add.json', 'r+', encoding='utf-8') as bot_file:
            
            bot_data = json.load(bot_file)
            
            bot_data.append(data_save)
            
            bot_file.seek(0)
            json.dump(bot_data, bot_file, indent=6, ensure_ascii=False)
            bot_file.truncate()  
            
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
            user_data_load = json.load(user_data_file)
                        
        if data_save in user_data_load:
            
            del user_data_load[data_save]
            
            with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','w',encoding='utf-8') as user_data_file_w:
                json.dump(user_data_load,user_data_file_w,indent=6,ensure_ascii=False)
                
        eel.toast_notifc('Nome adicionado')
            
    elif type_config == 'list_bot_rem':
        
        with open(f'{appdata_path}/rewardevents/web/src/user_info/bot_list_add.json', 'r+', encoding='utf-8') as bot_file:
            bot_data = json.load(bot_file)
            
            if data_save in bot_data:
            
                bot_data.remove(data_save)
            
                bot_file.seek(0)
                json.dump(bot_data, bot_file, indent=6, ensure_ascii=False)
                bot_file.truncate()
                
                eel.toast_notifc('Nome removido') 
            
            else:
                
                eel.toast_notifc('O nome não está na lista') 
                
    elif type_config == 'list_bot_get':
        
        with open(f'{appdata_path}/rewardevents/web/src/user_info/bot_list_add.json','r',encoding='utf-8') as bot_file:
            bot_data = json.load(bot_file)
            
            bot_data_dump = json.dumps(bot_data, ensure_ascii=False)

            return bot_data_dump
        
  
@eel.expose
def userdata_py(type_id,username):
    
    if type_id == 'get':
        
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
            user_data_load = json.load(user_data_file)
            
            userdata_dump = json.dumps(user_data_load, ensure_ascii=False)

            return userdata_dump
        
    elif type_id == 'load':
        
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
            user_data_load = json.load(user_data_file)
        
        if username in user_data_load:
            
            display_name = user_data_load[username]['display_name']
            mod = user_data_load[username]['mod']
            vip = user_data_load[username]['vip']
            sub = user_data_load[username]['sub']
            regular = user_data_load[username]['regular']
            top_chatter = user_data_load[username]['top_chatter']
            chat_freq = user_data_load[username]['chat_freq']
            color = user_data_load[username]['color']
            badges = user_data_load[username]['badges']
            last_join = user_data_load[username]['last_join']
            time_w = user_data_load[username]['time_w']
        
        else:
            
            display_name = username
            mod = 'Null'
            vip = 'Null'
            sub = 'Null'
            regular = 'Null'
            top_chatter = 'Null'
            chat_freq = 'Null'
            color = 'Null'
            badges = 'Null'
            last_join = 'Null'
            time_w = 'Null'
            
            
        data = {
            'display_name' : display_name,
            'mod' : mod,
            'vip' : vip,
            'sub' : sub,
            'regular' : regular,
            'top' : top_chatter,
            'chat_freq' : chat_freq,
            'color' : color,
            'badges' : badges,
            'last_join' : last_join,
            'time_w' : time_w,
        }
            
        result = namedtuple('result', data.keys())(*data.values())
    
        return result
        
    elif type_id == 'remove':
        
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
            user_data_load = json.load(user_data_file)
                        
        if username in user_data_load:
            
            del user_data_load[username]
            
            with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','w',encoding='utf-8') as user_data_file_w:
                json.dump(user_data_load,user_data_file_w,indent=6,ensure_ascii=False)
                
            eel.toast_notifc('Nome removido')
 
      
def commands_module(data) -> None:
    
    def send_error_level(user,user_level, command):

        message_error_level_load = utils.messages_file_load('error_user_level')

        aliases = {
            '{user}': str(user),
            '{user_level}' : str(user_level),
            '{command}' : str(command)
        }

        message_error_level = utils.replace_all(message_error_level_load,aliases)

        if utils.send_message("ERROR_USER"):
            send(message_error_level)

    def check_perm(user_level, command_level):
        level = ["spec","regular","top_chatter", "vip", "subs", "mod", "streamer"]
        if level.index(user_level) >= level.index(command_level):
            return True
        else:
            return False

    def check_user_level(user_levels):
        if "mod" in user_levels:
            return "mod"
        elif "subs" in user_levels:
            return "subs"
        elif "vip" in user_levels:
            return "vip"
        elif "top_chatter" in user_levels:
            return "top_chatter"
        else:
            return "spec"

    message_sender = data['display_name']
    message_sender_id = data['user_id']
    
    message_mod = data['mod']
    message_vip = data['vip']
    message_sub = data['subscriber']
    message_regular = data['regular']
    message_top_chatter = data['top_chatter']
    
    perms_list = []
    if message_mod == 1:
        perms_list.append('mod')
    if message_vip == 1:
        perms_list.append('vip')
    if message_sub == 1:
        perms_list.append('subs')
    if message_regular == 1:
        perms_list.append('regular')
    if message_top_chatter == 1:
        perms_list.append('top_chatter')
    
    message_text = data['message_no_url']

    user = message_sender
    user_id_command = message_sender_id

    if message_sender_id == authdata.BROADCASTER_ID():
        user_type = 'streamer'
    else:
        user_type = check_user_level(perms_list)
    

    with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', "r", encoding='utf-8') as command_file:
        command_data = json.load(command_file)
        
    with open(f'{appdata_path}/rewardevents/web/src/config/commands_config.json', "r", encoding='utf-8') as command_file_prefix:
        command_data_prefix = json.load(command_file_prefix)

    with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', "r", encoding='utf-8') as command_file_simple:
        command_data_simple = json.load(command_file_simple)

    with open(f'{appdata_path}/rewardevents/web/src/counter/commands.json', "r", encoding='utf-8') as command_file_counter:
        command_data_counter = json.load(command_file_counter)

    with open(f'{appdata_path}/rewardevents/web/src/giveaway/commands.json', "r", encoding='utf-8') as command_file_giveaway:
        command_data_giveaway = json.load(command_file_giveaway)

    with open(f'{appdata_path}/rewardevents/web/src/player/config/commands.json', 'r', encoding='utf-8') as command_file_player:
        command_data_player = json.load(command_file_player)
    
    with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json', 'r', encoding='utf-8') as command_file_duel:
        command_data_duel = json.load(command_file_duel)
    
    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'r', encoding='utf-8') as command_file_default:
        command_data_default = json.load(command_file_default)
    
    command_string = message_text
    command_lower = command_string.lower()
    command = command_lower.split()[0].strip()
    prefix = command[0]

    result_giveaway_check = {key: val for key, val in command_data_giveaway.items() if val.startswith(command)}

    result_counter_check = {key: val for key, val in command_data_counter.items() if val.startswith(command)}

    result_player_check = {key: val for key, val in command_data_player.items() if val.startswith(command)}
    
    result_duel_check = command.startswith(command_data_duel['command'])

    status_commands = command_data_prefix['STATUS_COMMANDS']

    if status_commands == 1:
        
        if command in command_data.keys():

            eel.last_command(command)

            status = command_data[command]['status']
            user_level = command_data[command]['user_level']
            delay = int(command_data[command]['delay'])
            last_use = command_data[command]['last_use']
            
            if check_perm(user_type, user_level):

                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    
                    if status == 1:
                    
                        redeem = command_data[command]['redeem']
                        user_input = command_lower.split(command)
                        
                        if len(user_input) > 1 and user_input[1] != "":
                            
                            user_input = command_lower.split(command)[1]

                        else:
                            
                            user_input = ""


                        data_rewards = {'USERNAME': user, 'REDEEM': redeem, 'USER_INPUT': user_input, 'USER_LEVEL': user_type,
                                        'USER_ID': user_id_command, 'COMMAND': command, 'PREFIX': prefix}

                        received_type = 'command'
                        
                        command_data[command]['last_use'] = current
                        
                        with open(f'{appdata_path}/rewardevents/web/src/config/commands.json', 'w', encoding='utf-8') as commands_save_delay:
                            json.dump(command_data, commands_save_delay, indent=6,ensure_ascii=False)

                        receive_thread = threading.Thread(target=receive_redeem, args=(data_rewards, received_type,),
                                                        daemon=True)
                        receive_thread.start()
                        
                    else:
                        
                        if utils.send_message("RESPONSE"):
                            send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                else:

                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            else:

                send_error_level(user,str(user_level), str(command))

        elif command in command_data_simple.keys():

            eel.last_command(command)

            with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "r") as counter_file_r:
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
                    '{user}': str(user),
                    '{command}': str(command),
                    '{prefix}': str(prefix),
                    '{user_level}': str(user_type),
                    '{user_id}': str(user_id_command),
                    '{counter}': str(counter),
                    '{counts}' : str(counts),
                }

                if status == 1:
                    
                    response_redus = utils.replace_all(str(response), aliases)

                    message_delay, check_time, current = utils.check_delay(delay,last_use)

                    if check_time:
                        
                        if utils.send_message("RESPONSE"):
                            send(response_redus)

                        counts =+ 1
                        command_data_simple[command]['last_use'] = current
                        command_data_simple[command]['counts'] = counts
                        
                        with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'w', encoding='utf-8') as data_command_file_w:
                            json.dump(command_data_simple, data_command_file_w, indent=6, ensure_ascii=False)

                    else:

                        if utils.send_message("ERROR_TIME"):
                            send(message_delay)
                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
            else:

                send_error_level(user,str(user_level), str(command))

        elif command in result_counter_check.values():

            eel.last_command(command)
            
            with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'r', encoding='utf-8') as delay_counter_file:
                delay_counter_data = json.load(delay_counter_file)

            if 'reset_counter' in result_counter_check.keys():
                
                status = delay_counter_data['reset_status']
                
                if status == 1:
                    if check_perm(user_type, 'mod'):

                        delay = delay_counter_data['reset']
                        last_use = delay_counter_data['reset_last']
                        
                        message_delay, check_time, current = utils.check_delay(delay,last_use)
                        
                        if check_time:

                            with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "w") as counter_file_w:
                                counter_file_w.write('0')

                            response_reset = utils.messages_file_load('response_reset_counter')
                            if utils.send_message("RESPONSE"):
                                send(response_reset)
                                
                            delay_counter_data['reset_last'] = current
                            
                            with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'w', encoding='utf-8') as delay_counter_file_w:
                                json.dump(delay_counter_data, delay_counter_file_w, indent=6, ensure_ascii=False)

                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)
                    else:
                        send_error_level(user,'mod', str(command))
                
                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                        
            elif 'set_counter' in result_counter_check.keys():

                status = delay_counter_data['set_status']
                
                if status == 1:
                    
                    if check_perm(user_type, 'mod'):

                        delay = delay_counter_data['set']
                        last_use = delay_counter_data['set_last']
                        
                        message_delay, check_time, current = utils.check_delay(delay,last_use)
                        
                        prefix_counter = command_data_counter['set_counter']

                        if check_time:
                            
                            user_input = command_string.split(prefix_counter.lower())

                            if len(user_input) > 1 and user_input[1] != "":
                                
                                user_input = user_input[1]
                                
                                if user_input.strip().isdigit():

                                    with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "w") as counter_file_w:
                                        counter_file_w.write(str(user_input))

                                    response_set = utils.messages_file_load('response_set_counter')
                                    response_set_repl = response_set.replace('{value}', user_input)

                                    if utils.send_message("RESPONSE"):
                                        send(response_set_repl)
                                        
                                    delay_counter_data['set_last'] = current
                                
                                    with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'w', encoding='utf-8') as delay_counter_file_w:
                                        json.dump(delay_counter_data, delay_counter_file_w, indent=6, ensure_ascii=False)
                                    
                                else:

                                    response_not_digit = utils.messages_file_load('response_not_digit_counter')
                                    if utils.send_message("RESPONSE"):
                                        send(response_not_digit.replace('{user}', user))
                                        
                                    delay_counter_data['set_last'] = current
                                
                                    with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'w', encoding='utf-8') as delay_counter_file_w:
                                        json.dump(delay_counter_data, delay_counter_file_w, indent=6, ensure_ascii=False)
                                    
                            else:

                                response_null_counter = utils.messages_file_load('response_null_set_counter')

                                if utils.send_message("RESPONSE"):
                                    send(response_null_counter.replace('{user}', user))
                                    
                                delay_counter_data['set_last'] = current
                            
                                with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'w', encoding='utf-8') as delay_counter_file_w:
                                    json.dump(delay_counter_data, delay_counter_file_w, indent=6, ensure_ascii=False)
                                    
                        else:

                            if utils.send_message("ERROR_TIME"):
                                send(message_delay_global)
                    else:
                        send_error_level(user,'mod', str(command))
                else:
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                        
            elif 'check_counter' in result_counter_check.keys():
                
                status = delay_counter_data['check_status']
                
                if status == 1:
                    
                    delay = delay_counter_data['check']
                    last_use = delay_counter_data['check_last']
                    
                    message_delay, check_time, current = utils.check_delay(delay,last_use)

                    if check_time:

                        with open(f"{appdata_path}/rewardevents/web/src/counter/counter.txt", "r") as counter_file_r:
                            counter_file_r.seek(0)
                            digit = counter_file_r.read()

                        response_check_counter = utils.messages_file_load('response_counter')
                        response_check_repl = response_check_counter.replace('{value}', str(digit))

                        if utils.send_message("RESPONSE"):
                            send(response_check_repl)
                            
                                
                        delay_counter_data['check_last'] = current
                    
                        with open(f'{appdata_path}/rewardevents/web/src/counter/delay.json', 'w', encoding='utf-8') as delay_counter_file_w:
                            json.dump(delay_counter_data, delay_counter_file_w, indent=6, ensure_ascii=False)   
                            

                    else:
                        if utils.send_message("ERROR_TIME"):
                            send(message_delay_global)
                
                else:
                    
                    if utils.send_message("RESPONSE"):
                        send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    
        elif command in result_giveaway_check.values():
            with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'r', encoding='utf-8') as delay_giveaway_file:
                delay_giveaway_data = json.load(delay_giveaway_file)
                
            eel.last_command(command)

            if 'execute_giveaway' in result_giveaway_check.keys():
                
                if check_perm(user_type, 'mod'):

                    delay = delay_giveaway_data['execute_delay']
                    last_use = delay_giveaway_data['execute_last_use']
                    
                    message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                    if check_time_global:

                        giveaway_py('execute','null')
                        
                        delay_giveaway_data['execute_last_use'] = current
                        
                        with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                            json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)

                    else:
                        if utils.send_message("ERROR_TIME"):
                            send(message_delay_global)

                else:

                    send_error_level(user,'mod', str(command))

            elif 'clear_giveaway' in result_giveaway_check.keys():

                if check_perm(user_type, 'mod'):
                    
                    delay = delay_giveaway_data['clear_delay']
                    last_use = delay_giveaway_data['clear_last_use']
                    
                    message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                    if check_time_global:

                        reset_data = []

                        giveaway_reset_file = open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'w', encoding="utf-8")
                        json.dump(reset_data, giveaway_reset_file, indent=6, ensure_ascii=False)
                        giveaway_reset_file.close()

                        message_clear = utils.messages_file_load('giveaway_clear')

                        if utils.send_message("RESPONSE"):
                            send(message_clear)
                            
                        delay_giveaway_data['clear_last_use'] = current
                        
                        with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                            json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)

                    else:

                        if utils.send_message("ERROR_TIME"):
                            send(message_delay_global)
                else:
                    send_error_level(user,'mod', str(command))

                pass

            elif 'check_name' in result_giveaway_check.keys():

                if check_perm(user_type, 'mod'):
                    
                    delay = delay_giveaway_data['check_delay']
                    last_use = delay_giveaway_data['check_last_use']
                    
                    message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                    if check_time_global:
                        
                        user_input = command_string.split(command_data_giveaway['check_name'])

                        giveaway_name_file = open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'r', encoding='utf-8')
                        giveaway_name_data = json.load(giveaway_name_file)

                        if len(user_input) > 1 and user_input[1] != "":
                            
                            user_input = user_input[1]
                            
                            if user_input.strip() in giveaway_name_data:

                                message_check_user = utils.messages_file_load('response_user_giveaway')

                                if utils.send_message("RESPONSE"):
                                    send(message_check_user.replace('{user}', user_input))
                                    
                                delay_giveaway_data['check_last_use'] = current
                        
                                with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                                    json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)

                            else:

                                message_check_no_user_load = utils.messages_file_load('response_no_user_giveaway')

                                if utils.send_message("RESPONSE"):
                                    send(message_check_no_user_load.replace('{user}', user_input))
                                    
                                delay_giveaway_data['check_last_use'] = current
                        
                                with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                                    json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)
                        else:
                            
                            message_check_error = utils.messages_file_load('response_check_error_giveaway')
                            if utils.send_message("RESPONSE"):
                                send(message_check_error.replace('{user}',user ))
                            
                            delay_giveaway_data['check_last_use'] = current
                    
                            with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                                json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)
                            
                    else:

                        if utils.send_message("ERROR_TIME"):
                            send(message_delay_global)

                else:
                    send_error_level(user,'mod', str(command))

            elif 'add_user' in result_giveaway_check.keys():

                if check_perm(user_type, 'mod'):
                    
                    delay = delay_giveaway_data['add_user_delay']
                    last_use = delay_giveaway_data['add_user_last_use']
                    
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
                            
                            delay_giveaway_data['add_user_last_use'] = current
                    
                            with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                                json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)
                            
                        else:
                            
                            message_add_user_error = utils.messages_file_load('response_use_error_giveaway')
                            if utils.send_message("RESPONSE"):
                                send(message_add_user_error.replace('{user}',user ))
                                
                            delay_giveaway_data['add_user_last_use'] = current
                    
                            with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                                json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)
                    else:

                        if utils.send_message("ERROR_TIME"):
                            send(message_delay_global)

                else:
                    send_error_level(user,'mod', str(command))

            elif 'check_self_name' in result_giveaway_check.keys():

                delay = delay_giveaway_data['check_self_delay']
                last_use = delay_giveaway_data['check_self_last_use']
                
                message_delay_global, check_time_global, current = utils.check_delay(delay,last_use)

                if check_time_global:

                    giveaway_name_file = open(f'{appdata_path}/rewardevents/web/src/giveaway/names.json', 'r', encoding='utf-8')
                    giveaway_name_data = json.load(giveaway_name_file)


                    if user in giveaway_name_data:

                        message_check_user_load = utils.messages_file_load('response_user_giveaway')
                        message_check_user = message_check_user_load.replace('{user}', str(user))

                        if utils.send_message("RESPONSE"):
                            send(message_check_user)
                            
                        delay_giveaway_data['check_self_last_use'] = current
                
                        with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                            json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)

                    else:

                        message_no_user_giveaway_load = utils.messages_file_load('response_no_user_giveaway')
                        message_no_user_giveaway = message_no_user_giveaway_load.replace('{user}', user)

                        if utils.send_message("RESPONSE"):
                            send(message_no_user_giveaway)
                            
                        delay_giveaway_data['check_self_last_use'] = current
                
                        with open(f'{appdata_path}/rewardevents/web/src/giveaway/delay.json', 'w', encoding="utf-8") as giveaway_delay_w:
                            json.dump(delay_giveaway_data, giveaway_delay_w, indent=6, ensure_ascii=False)

                else:

                    if utils.send_message("ERROR_TIME"):
                        send(message_delay_global)

        elif command in result_player_check.values():
            
            with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'r', encoding='utf-8') as delay_file_player:
                delay_data_player = json.load(delay_file_player)
        
            if 'volume' in result_player_check.keys():
                
                delay = delay_data_player['volume-delay']
                last_use = delay_data_player['volume-last']
                status = delay_data_player['volume-status']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                user_level = command_data_player['volume-perm']
                
                if check_perm(user_type, user_level):

                    if check_time:

                        if status == 1:
                            
                            prefix_volume = command_data_player['volume']
                            volume_value_command = command_lower.split(prefix_volume.lower())

                            if len(volume_value_command) > 1 and volume_value_command[1] != "":
                                        
                                volume_value_command = volume_value_command[1]
                                
                                if volume_value_command.strip().isdigit():

                                    volume_value_int = int(volume_value_command)

                                    if volume_value_int in range(0, 101):

                                        volume_value = volume_value_int / 100
                                        
                                        eel.player('volume', 'none', volume_value)

                                        aliases_commands = {
                                            '{user}': str(user),
                                            '{volume}': str(volume_value_int)
                                        }

                                        message_replace_response = utils.replace_all(utils.messages_file_load('command_volume_confirm'),aliases_commands)

                                        if utils.send_message("RESPONSE"):
                                            send(message_replace_response)
                                            
                                        delay_data_player['volume-last'] = current
                                
                                        with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                            json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

                                    else:

                                        aliases_commands = {
                                            '{user}': user,
                                            '{volume}': str(volume_value_int)
                                        }

                                        message_replace_response = utils.replace_all(utils.messages_file_load('command_volume_error'),aliases_commands)

                                        if utils.send_message("RESPONSE"):
                                            send(message_replace_response)
                                            
                                        delay_data_player['volume-last'] = current
                                
                                        with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                            json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

                                else:

                                    if utils.send_message("RESPONSE"):
                                        send(utils.messages_file_load('command_volume_number'))
                                        
                                        
                                    delay_data_player['volume-last'] = current
                            
                                    with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                        json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)
                            
                            else:
                                
                                volume_atual = eel.player('get_volume', 'none', 'none')()
                                
                                aliases_commands = {
                                        '{user}': str(user),
                                        '{volume}': str(volume_atual)
                                    }

                                message_replace_response = utils.replace_all(utils.messages_file_load('command_volume_response'), aliases_commands)

                                if utils.send_message("RESPONSE"):
                                    send(message_replace_response)
                                
                                delay_data_player['volume-last'] = current
                                
                                with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                    json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)
                                        
                                        
                            
                        else:
                            
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    else:
                        
                        if utils.send_message("ERROR_TIME"):
                            send(message_delay)

                else:
                    send_error_level(user,user_level, str(command))
              
            elif 'skip' in result_player_check.keys():

                delay = delay_data_player['skip-delay']
                last_use = delay_data_player['skip-last']
                status = delay_data_player['skip-status']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                user_level = command_data_player['skip-perm']
                
                if check_perm(user_type, user_level):

                    if check_time:

                        if status == 1:
                            
                            eel.player('stop', 'none', 'none')

                            aliases_commands = {
                                '{user}': str(user),
                            }
                            message_replace_response = utils.replace_all(utils.messages_file_load('command_skip_confirm'),
                                                                aliases_commands)

                            if utils.send_message("RESPONSE"):
                                send(message_replace_response)
                                
                            delay_data_player['skip-last'] = current
                            
                            with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)
                        else:
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))

                    else:

                        if utils.send_message("ERROR_TIME"):
                            send(message_delay)

                else:

                    send_error_level(user,user_level, str(command))

            elif 'request' in result_player_check.keys():

                delay = delay_data_player['request-delay']
                last_use = delay_data_player['request-last']
                status = delay_data_player['request-status']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                user_level = command_data_player['request-perm']
                
                if check_perm(user_type, user_level):

                    if check_time:

                        if status == 1:
                            
                            prefix_sr = command_data_player['request']
                            user_input = command_string.split(prefix_sr)

                            if len(user_input) > 1 and user_input[1] != "":
                                
                                user_input = user_input[1]

                                player_reward = command_data_player['redeem']

                                data_rewards = {'USERNAME': user, 'REDEEM': player_reward, 'USER_INPUT': user_input,
                                                'USER_LEVEL': user_type, 'USER_ID': user_id_command, 'COMMAND': command,
                                                'PREFIX': prefix}

                                received_type = 'command'

                                receive_thread = threading.Thread(target=receive_redeem,
                                                                args=(data_rewards, received_type,), daemon=True)
                                receive_thread.start()
                                
                                delay_data_player['request-last'] = current
                            
                                with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                    json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

                            else:

                                aliases_commands = {'{user}': str(user)}
                                message_replace_response = utils.replace_all(utils.messages_file_load('command_sr_error_link'),
                                                                    aliases_commands)

                                if utils.send_message("RESPONSE"):
                                    send(message_replace_response)
                                
                                delay_data_player['request-last'] = current
                            
                                with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                    json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

                        else:
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    else:

                        if utils.send_message("ERROR_TIME"):
                            send(message_delay)
                else:
                    send_error_level(user,user_level, str(command))

            elif 'atual' in result_player_check.keys():

                delay = delay_data_player['atual-delay']
                last_use = delay_data_player['atual-last']
                status = delay_data_player['atual-status']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                user_level = command_data_player['atual-perm']
                
                if check_perm(user_type, user_level):

                    if check_time:

                        if status == 1:
                            
                            f = open(f'{appdata_path}/rewardevents/web/src/player/list_files/currentsong.txt', 'r+', encoding="utf-8")
                            current_song = f.read()

                            aliases_commands = {'{user}': str(user), '{music}': str(current_song)}
                            message_replace_response = utils.replace_all(utils.messages_file_load('command_current_confirm'),
                                                                aliases_commands)
                            if utils.send_message("RESPONSE"):
                                send(message_replace_response)
                                
                            delay_data_player['atual-last'] = current
                            
                            with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

                        else:
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    else:
                        if utils.send_message("ERROR_TIME"):
                            send(message_delay)
                else:
                    send_error_level(user,user_level, str(command))

            elif 'next' in result_player_check.keys():

                delay = delay_data_player['next-delay']
                last_use = delay_data_player['next-last']
                status = delay_data_player['next-status']
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                user_level = command_data_player['next-perm']
                
                if check_perm(user_type, user_level):

                    if check_time:

                        if status == 1:
                            
                            with open(f'{appdata_path}/rewardevents/web/src/player/list_files/playlist.json', "r", encoding="utf-8") as playlist_file:
                                playlist_data = json.load(playlist_file)

                            with open(f'{appdata_path}/rewardevents/web/src/player/list_files/queue.json', "r", encoding="utf-8") as queue_file:
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

                                response_replace = utils.replace_all(utils.messages_file_load('command_next_confirm'), aliases_commands)

                                if utils.send_message("RESPONSE"):
                                    send(response_replace)
                                    
                                delay_data_player['next-last'] = current
                                
                                with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                    json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

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

                                response_replace = utils.replace_all(utils.messages_file_load('command_next_confirm'), aliases_commands)

                                if utils.send_message("RESPONSE"):
                                    send(response_replace)
                                
                                
                                delay_data_player['next-last'] = current
                                
                                with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                    json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

                            else:

                                aliases_commands = {
                                    '{user}': str(user),
                                }

                                response_replace = utils.replace_all(utils.messages_file_load('command_next_no_music'), aliases_commands)

                                if utils.send_message("RESPONSE"):
                                    send(response_replace)
                                    
                                delay_data_player['next-last'] = current
                                
                                with open(f'{appdata_path}/rewardevents/web/src/player/config/delay.json', 'w', encoding='utf-8') as delay_music_file_w:
                                    json.dump(delay_data_player, delay_music_file_w, indent=6, ensure_ascii=False)

                        else:
                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    else:
                        if utils.send_message("ERROR_TIME"):
                            send(message_delay)

                else:
                    send_error_level(user,user_level, str(command))

        elif result_duel_check:
            
            user_level = command_data_duel['user_level']
            
            if check_perm(user_type, user_level):
            
                with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'r', encoding='utf-8') as duel_file:
                    duel_data = json.load(duel_file)
                
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
                        
                        response_start = utils.replace_all(utils.messages_file_load("duel_start"), aliases_challenger)
                        if utils.send_message("RESPONSE"):
                            send(response_start)
                        
                        duel_title_poll = utils.replace_all(utils.messages_file_load("duel_title"), aliases_challenger)
                        
                        if duel_data['create_pred'] == 1:
                            
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
                        
                        response_1 = utils.replace_all(duel_message["start_mess"], aliases_challenger)
                        if utils.send_message("RESPONSE"):
                            send(response_1)
                        
                        time.sleep(duel_data["time_to_message"])
                        
                        response_2 = utils.replace_all(duel_message["stage_1"], aliases_challenger)
                        if utils.send_message("RESPONSE"):
                            send(response_2)
                        
                        time.sleep(duel_data["time_to_message"])
                        
                        response_3 = utils.replace_all(duel_message["stage_2"], aliases_challenger)
                        if utils.send_message("RESPONSE"):
                            send(response_3)
                        
                        time.sleep(duel_data["time_to_message"])
                        
                        response_4 = utils.replace_all(duel_message["stage_3"], aliases_challenger)
                        if utils.send_message("RESPONSE"):
                            send(response_4)
                        
                        time.sleep(duel_data["time_to_message"])
                        
                        response_5 = utils.replace_all(duel_message["stage_4"], aliases_challenger)
                        if utils.send_message("RESPONSE"):
                            send(response_5)
                        
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
                        
                        
                        response_6 = utils.replace_all(duel_message["stage_5"], aliases_winner)
                        if utils.send_message("RESPONSE"):
                            send(response_6)
                        
                        
                        if duel_data['create_pred'] == 1:
                            twitch_api.end_prediction(authdata.BROADCASTER_ID(),pred_data_temp['pred_id'],PredictionStatus.RESOLVED,pred_data_temp[winner])
                            
                        duel_data['challenged'] = ""
                        duel_data['challenger'] = ""
                        duel_data['accept'] = 0
                            
                        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'w', encoding='utf-8') as duel_file_w:
                            json.dump(duel_data,duel_file_w,indent=6,ensure_ascii=False)

                    
                    count = 0
                    
                    with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'r', encoding='utf-8') as duel_file:
                        duel_data = json.load(duel_file)
                    
                    while count < duel_data['time_to_accept']:
                        
                        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'r', encoding='utf-8') as duel_file:
                            duel_data = json.load(duel_file)
                            
                        if duel_data['accept'] == 0:
                            count = count + 1
                            print(count)
                            time.sleep(1)
                            
                        elif duel_data['accept'] == 1:
                            break 
                    
                    if count == duel_data['time_to_accept'] and duel_data['accept'] == 0:
                        
                        message_duel_aliases = {
                            '{challenged}' : duel_data["challenged"]
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('duel_long'),message_duel_aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                        
                        duel_data['challenged'] = ""
                        duel_data['challenger'] = ""
                            
                        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'w', encoding='utf-8') as duel_file_w:
                            json.dump(duel_data,duel_file_w,indent=6,ensure_ascii=False)
                            
                    elif duel_data['accept'] == 1:
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
                                            
                                        with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'w', encoding='utf-8') as duel_file_w:
                                            json.dump(duel_data,duel_file_w,indent=6,ensure_ascii=False)
                                            
                                        message_duel_aliases = {
                                            '{time}' : str(duel_data['time_to_accept']),
                                            '{user}' : user,
                                            '{challenged}' : challenged,
                                            '{command}' : duel_data['command'],
                                            '{accept}' : duel_data['command_accept']
                                        }
                                        
                                        message_replaced = utils.replace_all(utils.messages_file_load('duel_request'),message_duel_aliases)
                                        if utils.send_message("RESPONSE"):
                                            send(message_replaced)

                                        duel_thread = threading.Thread(target=loop_duel, args=(),daemon=True)
                                        duel_thread.start()
                                        
                                    else:
                                        
                                        aliases = {
                                            '{user}' : user,
                                            '{time}' : message_delay
                                        }
                                        
                                        message_duel_delay = utils.replace_all(utils.messages_file_load('duel_delay'),aliases)
                                        
                                        if utils.send_message("RESPONSE"):
                                            send(message_duel_delay)
                                
                                elif user != duel_data['challenger']:
                                        
                                    message_duel_aliases = {
                                        '{user}' : user
                                    }
                                    
                                    message_replaced = utils.replace_all(utils.messages_file_load('duel_already_started'),message_duel_aliases)
                                    if utils.send_message("RESPONSE"):
                                        send(message_replaced) 
                                            
                            
                            elif second_command == command_data_duel['command_accept']:
                                
                                if duel_data['challenged'] == "":
                                    
                                    message_duel_aliases = {
                                        '{user}' : user,
                                    }
                                    
                                    message_replaced = utils.replace_all(utils.messages_file_load('no_duel_request'),message_duel_aliases)
                                    if utils.send_message("RESPONSE"):
                                        send(message_replaced)
                                        
                                elif user == duel_data['challenged']:
                                
                                    duel_data['accept'] = 1
                                    
                                    with open(f'{appdata_path}/rewardevents/web/src/duel/duel.json' , 'w', encoding='utf-8') as duel_file_w:
                                        json.dump(duel_data,duel_file_w,indent=6,ensure_ascii=False)
                                        
                                        
                                    message_duel_aliases = {
                                        '{user}' : user,
                                        '{challenger}' : duel_data["challenger"]
                                    }
                                    
                                    message_replaced = utils.replace_all(utils.messages_file_load('duel_accepted'),message_duel_aliases)
                                    if utils.send_message("RESPONSE"):
                                        send(message_replaced)
                                    
                                elif user != duel_data['challenged']:
                                    
                                    message_duel_aliases = {
                                        '{user}' : user
                                    }
                                    
                                    message_replaced = utils.replace_all(utils.messages_file_load('duel_other'),message_duel_aliases)
                                    if utils.send_message("RESPONSE"):
                                        send(message_replaced)
                                        
                        elif second_command == user:
                                
                            message_duel_aliases = {
                                '{user}' : user
                            }
                            
                            message_replaced = utils.replace_all(utils.messages_file_load('duel_yorself'),message_duel_aliases)
                            if utils.send_message("RESPONSE"):
                                send(message_replaced)
                                    
                    elif user == duel_data['challenger']:
                        
                        message_duel_aliases = {
                            '{user}' : user
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('duel_again'),message_duel_aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                            
                else:
                
                    message_duel_aliases = {
                        '{user}' : user,
                        '{command}' : duel_data['command'],
                        '{accept}' : duel_data['command_accept']
                    }
                    
                    message_replaced = utils.replace_all(utils.messages_file_load('duel_parm'),message_duel_aliases)
                    if utils.send_message("RESPONSE"):
                        send(message_replaced)
            else:
                send_error_level(user,user_level, str(command))  

        elif command.startswith(command_data_default['cmd']):

            with open(f'{appdata_path}/rewardevents/web/src/config/simple_commands.json', 'r', encoding='utf-8') as data_command_file:
                data_command = json.load(data_command_file)
        
            delay = command_data_default['cmd_delay']
            last_use = command_data_default['cmd_last']
            status = command_data_default['cmd_status']

            if status == 1:

                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:      

                    if len(command_lower.split()) >= 2:

                        padrao = r'\((?:[^()]*|\([^()]*\))*\)' 
                        matches = re.findall(padrao, command_string)

                        values = [match[1:-1] for match in matches]
                         
                        type_cmd = command_lower.split()[1]

                        if type_cmd == "add":

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
                                    send(utils.replace_all(utils.messages_file_load('cmd_created'),{'{user}' : user}))  
                                    
                            else:
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('cmd_exists'),{'{user}' : user}))  
                        
                        if type_cmd == "edit":

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
                                    send(utils.replace_all(utils.messages_file_load('cmd_edited'),{'{user}' : user}))  
                            
                            else:

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('cmd_not_exists'),{'{user}' : user})) 

                        if type_cmd == "remove":

                            cmd = values[0]

                            if cmd in data_command:
                                
                                commands_py("delete",cmd)

                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('cmd_removed'),{'{user}' : user}))  
                            
                            else:
                                if utils.send_message("RESPONSE"):
                                    send(utils.replace_all(utils.messages_file_load('cmd_not_exists'),{'{user}' : user})) 

                        else:

                            if utils.send_message("RESPONSE"):
                                send(utils.replace_all(utils.messages_file_load('cmd_use'),{'{user}' : user})) 
                    else:

                        if utils.send_message("RESPONSE"):
                            send(utils.replace_all(utils.messages_file_load('cmd_use'),{'{user}' : user})) 


                    command_data_default['create_last'] = current
                    
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                        
                else:

                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            else:

                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))    

        elif command.startswith(command_data_default['dice']):
            
            delay = command_data_default['dice_delay']
            last_use = command_data_default['dice_last']
            status = command_data_default['dice_status']
            
            if status == 1:
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    
                    result = randint(1,6)
                    
                    aliases = {
                        "{value}" : str(result)
                    }
                    
                    command_data_default['dice_last'] = current
                    
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                    
                    message_replaced = utils.replace_all(command_data_default['dice_response'], aliases)
                    if utils.send_message("RESPONSE"):
                        send(message_replaced)
                        
                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                
        elif command.startswith(command_data_default['random']):
            
            delay = command_data_default['random_delay']
            last_use = command_data_default['random_last']
            status = command_data_default['random_status']
            
            if status == 1:
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)
                
                if check_time:
                    
                    value = command_lower.split(command_data_default['random'].lower())[1]

                    if value != '' and value.strip().isnumeric():
                        
                        result = randint(0,int(value))
                        
                        aliases = {
                            "{value}" : str(result)
                        }
                        
                        command_data_default['random_last'] = current
                    
                        with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                            json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                        
                        message_replaced = utils.replace_all(command_data_default['random_response'], aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                    
                    else:
                        
                        aliases = {
                            '{user}' : user
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('command_value'), aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                        

                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    
        elif command.startswith(command_data_default['game']):
            
            delay = command_data_default['game_delay']
            last_use = command_data_default['game_last']
            status = command_data_default['game_status']
            
            if status == 1:
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    result_data = twitch_api.get_streams(first=1,user_login=authdata.USERNAME())
                    
                    if result_data['data']:
                        
                        game_name = result_data['data'][0]['game_name']
                        
                        aliases = {
                            "{game}" : str(game_name)
                        }
                        
                        message_replaced = utils.replace_all(command_data_default['game_response'], aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                            
                    command_data_default['game_last'] = current
                
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                            
                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user})) 
                               
        elif command.startswith(command_data_default['uptime']):  
            
            delay = command_data_default['uptime_delay']
            last_use = command_data_default['uptime_last']
            status = command_data_default['uptime_status']
            
            if status == 1:
                
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    
                    result_data = twitch_api.get_streams(first=1,user_login=authdata.USERNAME())
                    
                    if result_data['data']:
                        
                        started = result_data['data'][0]['started_at']

                        time_in_live = utils.calculate_time(started)
                        
                        hours = time_in_live['hours']
                        minutes = time_in_live['minutes']
                        
                        aliases = {
                            "{user}" : str(user),
                            "{h}" : str(hours),
                            "{m}" : str(minutes)
                        }
                        
                        message_replaced = utils.replace_all(command_data_default['uptime_response'], aliases)
                        if utils.send_message("RESPONSE"):    
                            send(message_replaced)
                            
                    command_data_default['uptime_last'] = current
                
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                else:
                    
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
                        
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    
        elif command.startswith(command_data_default['followage']):  
            
            delay = command_data_default['followage_delay']
            last_use = command_data_default['followage_last']
            status = command_data_default['followage_status']
            
            if status == 1:      
                      
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    
                    if user != authdata.USERNAME():   
                        
                        user_info = twitch_api.get_users_follows(first=1,from_id=user_id_command,to_id=authdata.BROADCASTER_ID())
                        
                        if user_info['total'] == 1:
                        
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
                                "{user}" : user,
                                "{streamer}" : authdata.USERNAME(),
                                "{d}" : str(days),
                                "{h}" : str(hours),
                                "{m}" : str(minutes),
                                "{s}" : str(sec)
                            }
                            
                            message = utils.replace_all(command_data_default['followage_response'],aliases)
                            if utils.send_message('RESPONSE'):
                                send(message)
                                
                            command_data_default['followage_last'] = current
                        
                            with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                                json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                                
                        else:
                            aliases = {
                                "{user}" : user,
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
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                   
        elif command.startswith(command_data_default['msgcount']):  
            
            delay = command_data_default['msgcount_delay']
            last_use = command_data_default['msgcount_last']
            status = command_data_default['msgcount_status']
            
            if status == 1:      
                      
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    
                    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
                        user_data_load = json.load(user_data_file)

                        if user in user_data_load:
                            
                            msgcount = user_data_load[user]['chat_freq']
                            
                            aliases = {
                                '{user}' : user,
                                '{count}' : str(msgcount)
                            }
                            
                            message = utils.replace_all(command_data_default['msgcount_response'],aliases)
                            if utils.send_message('RESPONSE'):
                                send(message)
                    
                else:
                    
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
        
        elif command.startswith(command_data_default['watchtime']):  
            
            delay = command_data_default['watchtime_delay']
            last_use = command_data_default['watchtime_last']
            status = command_data_default['watchtime_status']
            
            if status == 1:      
                      
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    
                    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
                        user_data_load = json.load(user_data_file)
                        
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
                            '{user}' : str(user)
                        }
                        
                        message = utils.replace_all(command_data_default['watchtime_response'],aliases)
                        if utils.send_message('RESPONSE'):
                            send(message)

                else:
                    
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                                                  
        elif command.startswith(command_data_default['interaction_1']):

            delay = command_data_default['interaction_1_delay']
            last_use = command_data_default['interaction_1_last']
            status = command_data_default['interaction_1_status']
            
            if status == 1:     
                         
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                                
                    value = command_lower.split(command_data_default['interaction_1'].lower())
                    
                    if len(value) > 1 and value[1] != "":
                        
                        value = value[1]
                        
                        aliases = {
                            "{user_1}" : user,
                            "{user_2}" : str(value)
                        }
                        
                        message_replaced = utils.replace_all(command_data_default['interaction_1_response'], aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                    else:
                        aliases = {
                            '{user}' : user
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('command_string'), aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                            
                    command_data_default['interaction_1_last'] = current
                
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                    
                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    
        elif command.startswith(command_data_default['interaction_2']):

            delay = command_data_default['interaction_2_delay']
            last_use = command_data_default['interaction_2_last']
            status = command_data_default['interaction_2_status']
            
            if status == 1:     
            
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                    
                    value = command_lower.split(command_data_default['interaction_2'].lower())
                    
                    if len(value) > 1 and value[1] != "":
                        
                        value = value[1]
                        
                        aliases = {
                            "{user_1}" : user,
                            "{user_2}" : str(value)
                        }
                        
                        message_replaced = utils.replace_all(command_data_default['interaction_2_response'], aliases)
                        if utils.send_message("RESPONSE"):    
                            send(message_replaced)
                    
                    else:
                        aliases = {
                            '{user}' : user
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('command_string'), aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                            
                    command_data_default['interaction_2_last'] = current
                
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)

                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    
        elif command.startswith(command_data_default['interaction_3']):

            delay = command_data_default['interaction_3_delay']
            last_use = command_data_default['interaction_3_last']
            status = command_data_default['interaction_3_status']
            
            if status == 1:              
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:
                                    
                    value = command_lower.split(command_data_default['interaction_3'].lower())
                    
                    if len(value) > 1 and value[1] != "":
                        
                        value = value[1]
                        
                        aliases = {
                            "{user_1}" : user,
                            "{user_2}" : str(value)
                        }
                        
                        message_replaced = utils.replace_all(command_data_default['interaction_3_response'], aliases)
                        if utils.send_message("RESPONSE"):    
                            send(message_replaced)
                    
                    else:
                        aliases = {
                            '{user}' : user
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('command_string'), aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                            
                    command_data_default['interaction_3_last'] = current
                
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                            
                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    
        elif command.startswith(command_data_default['interaction_4']):

            delay = command_data_default['interaction_4_delay']
            last_use = command_data_default['interaction_4_last']
            status = command_data_default['interaction_4_status']
            
            if status == 1:     
                message_delay, check_time, current = utils.check_delay(delay,last_use)
                if check_time:    
                                
                    value = command_lower.split(command_data_default['interaction_4'].lower())
                    
                    if len(value) > 1 and value[1] != "":
                        
                        value = value[1]
                        
                        aliases = {
                            "{user_1}" : user,
                            "{user_2}" : str(value)
                        }
                        
                        message_replaced = utils.replace_all(command_data_default['interaction_4_response'], aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                    
                    else:
                        aliases = {
                            '{user}' : user
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('command_string'), aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                    
                            
                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)
            
            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))
                    
        elif command.startswith(command_data_default['interaction_5']):
            
            delay = command_data_default['interaction_5_delay']
            last_use = command_data_default['interaction_5_last']
            status = command_data_default['interaction_5_status']
            
            if status == 1:     
                message_delay, check_time, current = utils.check_delay(delay,last_use)

                if check_time:   
                                    
                    value = command_lower.split(command_data_default['interaction_2'].lower())
                    
                    if len(value) > 1 and value[1] != "":
                        
                        value = value[1]
                        
                        aliases = {
                            "{user_1}" : user,
                            "{user_2}" : str(value)
                        }
                        
                        message_replaced = utils.replace_all(command_data_default['interaction_5_response'], aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                    
                    else:
                        
                        aliases = {
                            '{user}' : user
                        }
                        
                        message_replaced = utils.replace_all(utils.messages_file_load('command_string'), aliases)
                        if utils.send_message("RESPONSE"):
                            send(message_replaced)
                            
                    command_data_default['interaction_5_last'] = current
                
                    with open(f'{appdata_path}/rewardevents/web/src/config/default_commands.json', 'w', encoding='utf-8') as default_save:
                        json.dump(command_data_default, default_save, indent=6,ensure_ascii=False)
                            
                else:
                    if utils.send_message("ERROR_TIME"):
                        send(message_delay)                

            else:
                if utils.send_message("RESPONSE"):
                    send(utils.replace_all(utils.messages_file_load('command_disabled'),{'{user}' : user}))        
                                
    else:

        message_command_disabled = utils.messages_file_load('commands_disabled')
        if utils.send_message("RESPONSE"):
            send(message_command_disabled)


@eel.expose
def timeout_user(user,type_id):
    
    user_id = twitch_api.get_users(logins=[user])
    user_id_resp = user_id['data'][0]['id']
    
    bot_id = twitch_api.get_users(logins=[authdata.BOTUSERNAME()])
    bot_id_resp = bot_id['data'][0]['id']
        
    url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={authdata.BROADCASTER_ID()}&moderator_id={bot_id_resp}"

    headers = CaseInsensitiveDict()
    headers["Authorization"] = f"Bearer {authdata.TOKENBOT()}"
    headers["Client-Id"] = clientid
    headers["Content-Type"] = "application/json"
    
    if type_id == 'ban':
        data = '{"data": {"user_id": '+ user_id_resp +',"reason":"Comando aplicado pelo bot"}}'

    elif type_id == 'timeout':
        data = '{"data": {"user_id": '+ user_id_resp +',"duration":600,"reason":"Comando aplicado pelo bot"}}'
    
    
    resp = req.post(url, headers=headers, data=data)

    if resp.status_code == 200:
        eel.toast_notifc('Ação executada')
    else:
        eel.toast_notifc('Ocorreu um erro')
        
        
def parse_to_dict(message):

    sub = 0
    mod = 0
    vip = 0
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

    def find_between( s, first, last ):

        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        
        except ValueError:
            
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
                emote_html = "<img src='https://static-cdn.jtvnw.net/emoticons/v1/{}/1.0'/>".format(emote_id)
                output += emote_html
                position = end_position

            else:
                
                output += parameters[position]
                position += 1

        return output
    
    def parse_bages_message(badges):

        tags = {"badges" : badges}

        with open(f'{appdata_path}/rewardevents/web/src/badges/badges_channel.json', 'r',encoding='utf-8') as channel_badge_file:
            channel_badges = json.load(channel_badge_file)
        with open(f'{appdata_path}/rewardevents/web/src/badges/badges_global.json', 'r',encoding='utf-8') as global_badge_file:
            global_badges = json.load(global_badge_file)

        badges = tags["badges"]

        badge_resp_list = ''

        for badge in badges:
            
            badge_id = badges[badge]

            if badge not in channel_badges["badge_sets"]:

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

            parameters = parse_emotes_message(emotes_dict,parameters)

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
        vip = 1
        
    if 'mod=1' in message:
        mod = 1
        
    if 'subscriber=1' in message:
        sub = 1
    
    if 'reply-parent-display-name' in message:
        
        user_replied = utils.find_between( message, 'reply-parent-display-name=', ';')
        message_replied = re.sub(r"\\s", " ", utils.find_between( message, 'reply-parent-msg-body=', ';'))
        response = 1
    
    if url_match:
        
        link_par = " '"+ url_match.group(0)+ "'"
        link_html = f'<span class="link-style" onclick="eel.open_link_chat({link_par})" href="{url_match.group(0)}">{url_match.group(0)}</span>'
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
        "badge_info"  : badge_info,
        "vip"  : vip,
        "mod"  : mod,
        "sub"  : sub,
        "sub_count"  : sub_count,
    }
    
    result = namedtuple('result', data.keys())(*data.values())
    
    return result


@eel.expose
def command_fallback(message: str) -> None:
    """
    
     Processa a mensagem recebida da twitch via IRC e transforma em dicionarios de acordo com o tipo de mensagem enviada.

    """
    id_message = utils.find_between( message, ';id=', ';' ),

    if id_message[0] == '00000':
        
        aliases = {
            '{USERLOGIN}' : authdata.USERNAME(),
        }
        
        message = utils.replace_all(message,aliases)

    message_data = message.split(f'#{authdata.USERNAME()} :')[0]
    
    if "Login authentication failed" in message:
        eel.toast_notifc('Erro de autenticação, é recomendado fazer o login novamente ou reiniciar o programa, se o erro persistir contate o suporte.')
        
    with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json','r',encoding='utf-8') as chat_file:
        chat_data = json.load(chat_file)
        
    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_sess_join.json','r',encoding='utf-8') as users_sess_join_file:
        users_sess_join_data = json.load(users_sess_join_file)
    
    with open(f'{appdata_path}/rewardevents/web/src/chat_log.txt','a',encoding='utf-8') as chat_log:
        if 'PRIVMSG' in message_data or 'USERNOTICE' in message_data:
            chat_log.write(f'{message} \n')

    with open(f'{appdata_path}/rewardevents/web/src/user_info/bot_list.json','r',encoding='utf-8') as bots_file:
        bot_list = json.load(bots_file)
    
    with open(f'{appdata_path}/rewardevents/web/src/user_info/bot_list_add.json','r',encoding='utf-8') as bots_file_user:
        bot_list_user = json.load(bots_file_user)
         
    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_joined.json','r',encoding='utf-8') as userjoin_data_file:
        userjoin_data_load = json.load(userjoin_data_file)
        
    now = datetime.datetime.now()
    format = chat_data['time-format']
    
    if chat_data['data-show'] == 1:
        if chat_data['type-data'] == "passed":
            chat_time = now.strftime('%Y-%m-%dT%H:%M:%S')
        elif chat_data['type-data'] == "current":
            chat_time = now.strftime(format)
    else: 
        chat_time = ''
            
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
                
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_joined.json','w',encoding='utf-8') as userjoin_data_file:
            json.dump(userjoin_data_load,userjoin_data_file,indent=6,ensure_ascii=False)
            
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_sess_join.json','w',encoding='utf-8') as user_join_sess_file_w:
            json.dump(users_sess_join_data,user_join_sess_file_w,indent=6,ensure_ascii=False)
                  
    def add_user_database(data): 
        
         with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
            user_data_load = json.load(user_data_file)
            
            if data['username'] not in user_data_load:
                
                user_data_load[data['username']] = {
                    'display_name' : data['display_name'],
                    'vip' : data['vip'],
                    'mod': data['mod'],
                    'sub': data['sub'],
                    'regular' : data['regular'],
                    'sub_count': data['sub_count'],
                    'top_chatter' : data['top_chatter'],
                    'chat_freq' : data['chat_freq'],
                    'color': data['color'],
                    'badges': data['badges'],
                    'last_join' : data['last_join'],
                    'time_w': data['time_w']
                }
                
            else:
                                
                chat_freq = user_data_load[data['username']]['chat_freq']
                chat_freq = chat_freq + 1
                
                if chat_freq > int(chat_data['top_chatter_min']):
                    top = 1
                else:
                    top = 0
                    
                regular_time = user_data_load[data['username']]['time_w']
                regular_min = chat_data['regular_min']
                
                if regular_time > int(regular_min):
                    regular = 1
                else:
                    regular = 0
                        
                user_data_load[data['username']] = {
                    'display_name' : data['display_name'],
                    'vip' : data['vip'],
                    'mod': data['mod'],
                    'sub': data['sub'],
                    'regular': regular,
                    'sub_count': data['sub_count'],
                    'top_chatter' : top,
                    'chat_freq' : chat_freq,
                    'color': data['color'],
                    'badges': data['badges'],
                    'last_join' : user_data_load[data['username']]['last_join'],
                    'time_w': user_data_load[data['username']]['time_w']
                }
                
                
            with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database_sess.json','w',encoding='utf-8') as user_data_sess_file_w:
                json.dump(user_data_load,user_data_sess_file_w,indent=6,ensure_ascii=False)
            
            with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','w',encoding='utf-8') as user_data_file_w:
                json.dump(user_data_load,user_data_file_w,indent=6,ensure_ascii=False)
                                       
    try:
        
        if len(message.split()) > 1:

            if '\r\n' in message:
                message = message.split('\r\n')[0]
                    
            if 'USERNOTICE' in message_data:
                
                with open(f'{appdata_path}/rewardevents/web/src/config/event_not.json', 'r', encoding='utf-8') as event_config_file:
                    event_config_data = json.load(event_config_file)
                    
                if 'msg-id' in message_data:
                    
                    msg_id = utils.find_between( message, 'msg-id=', ';' )
                                 
                    if msg_id == 'sub':

                        paran_talk_split = message.split(f'USERNOTICE #{authdata.USERNAME()} :')
                        
                        if len(paran_talk_split) > 1:
                            paran_talk_split = paran_talk_split[1]
                            
                        else:
                            paran_talk_split = ''
                             
                        data = {
                            'display_name' : utils.find_between( message, 'display-name=', ';' ),
                            'cumulative' : utils.find_between( message, 'msg-param-cumulative-months=', ';' ),
                            'monts' : utils.find_between( message, 'msg-param-months=', ';' ),
                            'plan' : utils.find_between( message, 'msg-param-sub-plan-name=', ';' ),
                            'plan_type' : utils.find_between( message, 'msg-param-sub-plan=', ';' ),
                            'gifited' : utils.find_between( message, 'msg-param-was-gifted=', ';' ),
                            'paran_talk' : paran_talk_split
                        }    
                        
                        response =  event_config_data['sub']['response']
                        response_chat =  event_config_data['sub']['response_chat']
                        
                        if data['paran_talk'] != '' :
                            response_send = response
                            response += f", : {data['paran_talk']}"
                            message = data['paran_talk']
                        
                        else:
                            response_send = response
                            message = ''   
                            
                        if data['plan_type'] != "Prime":
                            plan_type = "Sub"
                        else:
                            plan_type = "Prime"
                            
                        
                        data_discord = {
                            'type_id' : 'sub',
                            'username' : data['display_name'],
                        }
                        
                        send_discord_webhook(data_discord)

                        aliases = {
                            '{username}' : data['display_name'],
                            '{type}' : plan_type,
                            '{plan}' : data['plan'],
                            '{months}' : data['monts'],
                            '{cumulative}' : data['cumulative']
                        }
                        
                        response = utils.replace_all(response,aliases)
                        response_chat = utils.replace_all(response_chat,aliases)
                        response_send = utils.replace_all(response_send,aliases)  
                        
                        data = {
                            'type_id' : 'sub',
                            'type' : 'sub',
                            'username' : response_send,
                            'message_html' : message,
                            'message' : message
                        }
                        
                        send_announcement(response_chat,'purple')                
                        send_not_fun(data)   
                    
                    elif msg_id == 'subgift': 
                        
                        data = {
                            'display_name' : utils.find_between( message, 'display-name=', ';' ),
                            'months' : utils.find_between( message, 'msg-param-gift-months=', ';' ),
                            'rec_username' : utils.find_between( message, 'msg-param-recipient-display-name=', ';' ),
                            'plan' : utils.find_between( message, 'msg-param-sub-plan-name=', ';').replace('\s', ' '),
                            'plan_type' : utils.find_between( message, 'msg-param-sub-plan=', ';'),
                        }
                        
                        response =  event_config_data['giftsub']['response']
                        
                        aliases = {
                            '{months}' : data['months'],
                            '{username}' : data['display_name'],
                            '{rec_username}' : data['rec_username'],
                            '{plan}' : data['plan'],
                        }
                        
                        response = utils.replace_all(response,aliases)
                        
                        data = {
                            'type' : 'giftsub',
                            'username' : response,
                            'message' : ''
                        }  
                        
                        send_announcement(response,'purple')
                        send_not_fun(data)     
                    
                    elif msg_id == 'submysterygift': 
                        
                        data = {
                            'display_name' : utils.find_between( message, 'display-name=', ';' ),
                            'count' : utils.find_between( message, 'msg-param-mass-gift-count=', ';' ),
                            'plan' : utils.find_between( message, 'msg-param-sub-plan=', ';'),
                        }
                        
                        response =  event_config_data['mysterygift']['response']
                        
                        aliases = {
                            '{username}' : data['display_name'],
                            '{count}' : data['count'],
                            '{plan}' : data['plan'],
                        }
                    
                        
                        response = utils.replace_all(response,aliases) 
                        
                        data = {
                            'type' : 'giftsub',
                            'username' : response,
                            'message_html' : '',
                            'message' : ''
                        }  
                        
                        send_announcement(response,'purple')
                        send_not_fun(data)   

                    elif msg_id == 'anongiftpaidupgrade': 
                        
                        data = {
                            'display_name' : utils.find_between( message, 'display-name=', ';' ),
                        }
                        
                        response =  event_config_data['re-mysterygift']['response']
                        
                        aliases = {
                            '{username}' : data['display_name'],
                        }
                    
                        
                        response = utils.replace_all(response,aliases) 
                        
                        data = {
                            'type' : 'giftsub',
                            'username' : response,
                            'message_html' : '',
                            'message' : ''
                        }  
                        
                        send_announcement(response,'purple')
                        send_not_fun(data)         

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
                        
                        chat_data_dump = json.dumps(data, ensure_ascii=False)
                                
                        eel.append_announce(chat_data_dump)          
                    
            if 'PRIVMSG' in message_data:
                    
                parse_res = parse_to_dict(message)

                top = 0
                now = datetime.datetime.now()
                last_join = now.strftime('%H:%M:%S %d/%m/%Y')
                
                data_database = {
                    'username' : parse_res.user_name,
                    'display_name' : parse_res.display_name,
                    'vip' : parse_res.vip,
                    'mod': parse_res.mod,
                    'sub': parse_res.sub,
                    'sub_count': parse_res.sub_count,
                    'regular' : 0,
                    'top_chatter' : 0,
                    'chat_freq' : 1,
                    'color': parse_res.color,
                    'badges': parse_res.badges,
                    'last_join' : last_join,
                    'time_w': 0
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
                    "user_name": parse_res.user_name,
                    "user_replied" : parse_res.user_replied,
                    "mod": response_userdata.mod,
                    "vip" : response_userdata.vip,
                    "regular": response_userdata.regular,
                    "top_chatter": response_userdata.top,
                    "subscriber": response_userdata.sub,
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

                message_data_dump = json.dumps(data_res, ensure_ascii=False)
                eel.append_message(message_data_dump)
                commands_module(data_res)      

            if f'JOIN #{authdata.USERNAME()}'in message and not 'PRIVMSG' in message:
                
                user_join = utils.find_between(message.split()[0],'@','.tmi')
                
                data_database = {
                    'username' : user_join,
                }
                
                add_user_join(data_database)
                    
                if not user_join in userjoin_data_load['spec']:
                    
                    if user_join not in bot_list and user_join not in bot_list_user:
                        
                        if chat_data['send-greetings'] == 1:

                            aliases = {
                                '{user}' : user_join
                            }
                            
                            response_redus = utils.replace_all(chat_data['greetings'], aliases)
                            send(response_redus)        
                        
                        if chat_data['not-user-sound'] == 1:
                            
                            if user_join not in chat_data['user_not_display']:
                            
                                sound_playing = pygame.mixer.music.get_busy()

                                while sound_playing:
                                    sound_playing = pygame.mixer.music.get_busy()
                                    time.sleep(2)
                                    
                                sound_path = chat_data['not-sound-path']
                                pygame.mixer.music.load(sound_path)
                                pygame.mixer.music.play()
                 
                if user_join not in bot_list and user_join not in bot_list_user:       
                    
                    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
                        user_data_load = json.load(user_data_file)
                        
                        now = datetime.datetime.now()
                        last_join = now.strftime('%H:%M:%S %d/%m/%Y')
                        
                        if user_join in user_data_load:
                            
                            user_data_load[user_join]['last_join'] = last_join
                            
                            with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database_sess.json','w',encoding='utf-8') as user_data_sess_file_w:
                                json.dump(user_data_load,user_data_sess_file_w,indent=6,ensure_ascii=False)
                                
                            with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','w',encoding='utf-8') as user_data_file_w:
                                json.dump(user_data_load,user_data_file_w,indent=6,ensure_ascii=False)
                
                    if chat_data['not-user-join'] == 1:
                        
                        if user_join not in chat_data['user_not_display']:    
                            
                            data = {
                                "message" : f"Usuário {user_join} entrou no chat",
                                "font_size" : chat_data['font-size'],
                                "color" : chat_data['color-not-join'],
                                "data_show" : chat_data["data-show"],
                                "chat_time" : chat_time,
                                "type_data" : chat_data["type-data"],
                            }
                            
                            chat_data_dump = json.dumps(data, ensure_ascii=False)
                            eel.append_notice(chat_data_dump)
                                                               
            if '.twitch.tv 353' in message and not 'PRIVMSG' in message: 
                
                names_list = message.split(f'#{authdata.USERNAME()} :')
                list_join = names_list[1].split(' ')
                
                
                for name in list_join:
                    
                    name = name.strip()
                    
                    if name not in bot_list and name not in bot_list_user:
                        
                        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
                            user_data_load = json.load(user_data_file)
                            
                            now = datetime.datetime.now()
                            last_join = now.strftime('%H:%M:%S %d/%m/%Y')
                            
                            if name in user_data_load:
                                
                                user_data_load[name]['last_join'] = last_join
                                
                                with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database_sess.json','w',encoding='utf-8') as user_data_sess_file_w:
                                    json.dump(user_data_load,user_data_sess_file_w,indent=6,ensure_ascii=False)
                                    
                                with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','w',encoding='utf-8') as user_data_file_w:
                                    json.dump(user_data_load,user_data_file_w,indent=6,ensure_ascii=False)
                        
                        if name not in users_sess_join_data['spec']:
                            
                            users_sess_join_data['spec'].append(name)
                            
                    else:
                        
                        if name not in users_sess_join_data['bot']:
                            
                            users_sess_join_data['bot'].append(name)
                            
                with open(f'{appdata_path}/rewardevents/web/src/user_info/users_sess_join.json','w',encoding='utf-8') as user_join_sess_file_w:
                    json.dump(users_sess_join_data,user_join_sess_file_w,indent=6,ensure_ascii=False)
                
            if 'PART' in message and not 'PRIVMSG' in message:

                user_part = utils.find_between(message.split()[0],':','!')
                
                with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
                    user_data_load = json.load(user_data_file)
                    
                    if user_part in user_data_load:
                        
                        datetime2 = datetime.datetime.now()
                        
                        last_join = user_data_load[user_part]['last_join']
                        datetime1 = datetime.datetime.strptime(last_join, "%H:%M:%S %d/%m/%Y")
                        
                        diff = datetime2 - datetime1
                        minutes = diff.total_seconds() / 60
                        
                        current_min = user_data_load[user_part]['time_w']
                        
                        total_min = int(current_min) + int(minutes)
                        
                        user_data_load[user_part]['time_w'] = int(total_min)

                        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database_sess.json','w',encoding='utf-8') as user_data_sess_file_w:
                            json.dump(user_data_load,user_data_sess_file_w,indent=6,ensure_ascii=False)
                            
                        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','w',encoding='utf-8') as user_data_file_w:
                            json.dump(user_data_load,user_data_file_w,indent=6,ensure_ascii=False)

                if user_part not in bot_list and user_part not in bot_list_user:
                    
                    if user_part in users_sess_join_data['spec']:
                        
                        users_sess_join_data['spec'].remove(user_part)
                        
                        if chat_data['not-user-leave'] == 1:
                    
                            if user_part not in chat_data['user_not_display']:    
                                    
                                    data = {
                                        "message" : f"Usuário {user_part} saiu do chat",
                                        "font_size" : chat_data['font-size'],
                                        "color" : chat_data['color-not-leave'],
                                        "data_show" : chat_data["data-show"],
                                        "chat_time" : chat_time,
                                        "type_data" : chat_data["type-data"],
                                    }
                                    
                                    chat_data_dump = json.dumps(data, ensure_ascii=False)
                                    
                                    eel.append_notice(chat_data_dump)
                else:
                    
                    if user_part in users_sess_join_data['bot']:
                        
                        users_sess_join_data['bot'].remove(user_part)
                    
                with open(f'{appdata_path}/rewardevents/web/src/user_info/users_sess_join.json','w',encoding='utf-8') as user_join_sess_file_w:
                    json.dump(users_sess_join_data,user_join_sess_file_w,indent=6,ensure_ascii=False)
                        
            if '@ban-duration=' in message and not 'PRIVMSG' in message:
                
                with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
                    user_data_load = json.load(user_data_file)
        
                    timeout_time = utils.find_between(message,'@ban-duration=',';')
                    target_user = utils.find_between(message,'target-user-id=',';')
                    
                    if target_user in user_data_load:
                        
                        data = {
                            "message" : f"Usuário {user_data_load[target_user]['display_name']} colocado em timeout por {timeout_time} segundos",
                            "font-size" : chat_data['font-size'],
                            "color" : chat_data['color-not']
                        }
                            
                        chat_data_dump = json.dumps(data, ensure_ascii=False)
                        
                        eel.append_notice(chat_data_dump)
            
    except Exception as e:
        utils.error_log(e)
 
   
def close():
    
    with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json','r',encoding='utf-8') as chat_data_file:
        chat_data = json.load(chat_data_file)
        
    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','r',encoding='utf-8') as user_data_file:
        user_data_load = json.load(user_data_file)
        
    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_sess_join.json','r',encoding='utf-8') as user_join_sess_file:
        userjoin_sess_load = json.load(user_join_sess_file)
        
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
                
                if total_min > int(regular_min):
                    regular = 1
                else:
                    regular = 0
                    
                user_data_load[name]['regular'] = regular
                
    with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database.json','w',encoding='utf-8') as user_data_file_w:
        json.dump(user_data_load,user_data_file_w,indent=6,ensure_ascii=False)
        
    sys.exit(0)
           

def download_badges():

    os.makedirs(f'{appdata_path}/rewardevents/web/src/badges',exist_ok=True)

    global_badge_url = req.get(f'https://badges.twitch.tv/v1/badges/global/display')
    global_badge_json = json.loads(global_badge_url.content)

    channel_badge_url = req.get(f'https://badges.twitch.tv/v1/badges/channels/{authdata.BROADCASTER_ID()}/display')
    channel_badge_json = json.loads(channel_badge_url.content)

    with open(f'{appdata_path}/rewardevents/web/src/badges/badges_global.json','w',encoding='utf-8') as badge_global_file:
        json.dump(global_badge_json,badge_global_file,indent=6,ensure_ascii=False)

    with open(f'{appdata_path}/rewardevents/web/src/badges/badges_channel.json','w',encoding='utf-8') as badge_global_file:
        json.dump(channel_badge_json,badge_global_file,indent=6,ensure_ascii=False)


def eel_start(eel_mode):
    
    eel.init('web')
    
    if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:

        if eel_mode == "normal":

            window.load_url("http://localhost:7000/index.html")
            eel.start("index.html", size=(1200, 680), port=7000, mode=None, shutdown_delay=0.0)
            
        elif eel_mode == "auth":

            eel.start("auth.html", size=(1200, 680), port=7000, mode=None, shutdown_delay=0.0)

    else:
        raise


def post_eventsub(id):
    
        url_post = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        
        header = CaseInsensitiveDict()
        header["Authorization"] = f"Bearer {authdata.TOKEN()}"
        header["Client-Id"] = clientid
        header['Content-Type'] = 'application/json'
        
        with open(f'{appdata_path}/rewardevents/web/src/config/websocket_param.json') as json_file:
            json_data_param = json.load(json_file)
            
        for type_param in json_data_param:
            
            
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
            
            param_dump = json.dumps(parameters)
            
            response = req.post(url_post, data=param_dump, headers=header)
            
            if response.status_code != 202:
                print(f'{type_param},Erro = {response.json()}')
  

@eel.expose      
def on_message(ws, message): 
        
    data = json.loads(message)
    
    message_type = data["metadata"]["message_type"]
    
    if message_type == 'session_welcome':
        
        session_id = data["payload"]["session"]["id"]
        post_eventsub(session_id)
        
    elif message_type == 'notification':
        
        subscription_type = data["metadata"]["subscription_type"]
        
        if subscription_type == 'channel.follow':
            
            event = data['payload']['event']
            
            follow_name = event['user_name']
            follow_date = event['followed_at']
            
            data_send = {
                'type_id' : "follow",
                'follow_name' : follow_name,
                'follow_date' : follow_date
            }
            
            
            with open(f'{appdata_path}/rewardevents/web/src/config/chat_config.json','r',encoding='utf-8') as chat_file:
                chat_data = json.load(chat_file)

            now = datetime.datetime.now()
            format = chat_data['time-format']

            if chat_data['data-show'] == 1:
                if chat_data['type-data'] == "passed":
                    chat_time = now.strftime('%Y-%m-%dT%H:%M:%S')
                elif chat_data['type-data'] == "current":
                    chat_time = now.strftime(format)
            else: 
                chat_time = ''
        

            with open(f"{appdata_path}/rewardevents/web/src/config/follow.json", "r", encoding='utf-8') as file:
                follow_data = json.load(file)
                
            if follow_name in follow_data:
                
                follow_date_old = follow_data[follow_name]['follow_date']
                time_followed = utils.calculate_time(follow_date_old)
                
                if int(time_followed['days']) > 1:
                    
                    follow_data[follow_name]['follow_date'] = follow_date
                    
                    with open(f'{appdata_path}/rewardevents/web/src/config/follow.json', 'w', encoding='utf-8') as file_follows:
                        json.dump(follow_data,file_follows,ensure_ascii=False,indent=4)
                        
                    data_time = {
                        'follow': follow_name,
                    }

                    data_time_dump = json.dumps(data_time, ensure_ascii=False)
                    eel.receive_follow_info(data_time_dump)
                    
                    data_not = {
                        "message" : f"Usuário {follow_name} seguiu o Canal!!",
                        "font_size" : chat_data['font-size'],
                        "color" : chat_data['color-not'],
                        "data_show" : chat_data["data-show"],
                        "chat_time" : chat_time,
                        "type_data" : chat_data["type-data"],
                    }
                    
                    notific_dump = json.dumps(data_not, ensure_ascii=False)
                    eel.append_notice(notific_dump)
                    
                    with open(f"{appdata_path}/rewardevents/web/src/config/event_not.json", "r", encoding='utf-8') as message_file:
                        message_data = json.load(message_file)
                        
                    message_chat = message_data['follow']['response_chat']
                    message = message_data['follow']['response']
                    
                    
                    aliases = {
                        '{username}' : follow_name,
                    }
                    
                    message_chat = utils.replace_all(message_chat,aliases)
                    message = utils.replace_all(message,aliases)
                    
                    send_announcement(message_chat,'purple')   
                    
                    
                    data = {
                        'type' : 'follow',
                        'username' : follow_name,
                        'message_html' : message,
                        'message' : message
                    }
                    
                    send_not_fun(data)
                    send_discord_webhook(data_send)
                        
            else:
                
                follow_data[follow_name] = { 'follow_date' : follow_date}
                
                with open(f'{appdata_path}/rewardevents/web/src/config/follow.json', 'w', encoding='utf-8') as file_follows:
                    json.dump(follow_data,file_follows,ensure_ascii=False,indent=4)
                    
                data_time = {
                    'follow': follow_name,
                }

                data_time_dump = json.dumps(data_time, ensure_ascii=False)
                eel.receive_follow_info(data_time_dump)
                    
                data_not = {
                    "message" : f"Usuário {follow_name} seguiu o Canal!!",
                    "font_size" : chat_data['font-size'],
                    "color" : chat_data['color-not'],
                    "data_show" : chat_data["data-show"],
                    "chat_time" : chat_time,
                    "type_data" : chat_data["type-data"],
                }

                notific_dump = json.dumps(data_not, ensure_ascii=False)
                eel.append_notice(notific_dump)
                
                data = {
                    'type' : 'follow',
                    'username' : '',
                    'message' : data_not['message']
                }
                
                with open(f"{appdata_path}/rewardevents/web/src/config/event_not.json", "r", encoding='utf-8') as message_file:
                    message_data = json.load(message_file)
                        
                message_chat = message_data['follow']['response_chat']
                message = message_data['follow']['response']
                
                
                aliases = {
                    '{username}' : follow_name,
                }
                
                message_chat = utils.replace_all(message_chat,aliases)
                message = utils.replace_all(message,aliases)
                
                
                send_announcement(message_chat,'purple')   
                
                send_discord_webhook(data_send)


                data = {
                    'type' : 'follow',
                    'username' : follow_name,
                    'message_html' : message,
                    'message' : message
                }

                send_not_fun(data)
                   
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
                
            event = data['payload']['event']
            
            user_name = event['broadcaster_user_name']
            title = event['title']
            language = event['language']
            category_name = event['category_name']
            is_mature = event['is_mature']
            
            data = {
                'type_id' : "live_cat",
                'tag' : category_name,
                'title' : title,
                'is_mature' : is_mature
            }
            
            send_discord_webhook(data)
            
        elif subscription_type == 'stream.online':  
                
            event = data['payload']['event']
            
            user_name = event['broadcaster_user_name']
            
            data = {
                'type_id' : "live_start",
                'username' : user_name,
            }
            
            send_discord_webhook(data)
            
        elif subscription_type == 'stream.offline':  
                
            event = data['payload']['event']
            
            user_name = event['broadcaster_user_name']

            data = {
                'type_id' : "live_end",
                'username' : user_name,
            }
            
            send_discord_webhook(data)
                    
        elif subscription_type == 'channel.subscribe':  
                
            event = data['payload']['event']
            
            user_name = event['user_name']
            broadcaster_user_name = event['broadcaster_user_name']
            tier = event['tier']
            is_gift = event['is_gift']
            
            
            data = {
                'type' : 'sub',
                'username' : user_name,
                
            }
            
            print(event)

        elif subscription_type == 'channel.subscription.gift':  
                
            event = data['payload']['event']
            
            print(event)
                      
        elif subscription_type == 'channel.subscription.end':  
                
            event = data['payload']['event']
            
            user_name = event['user_name']
            tier = event['tier']
            is_gift = event['is_gift']
            
            print(f"Sub Acabou {event}")
                
        elif subscription_type == 'channel.subscription.message':  
                
            def parse_emotes(emotes):
                
                emote_dict = {}

                for emote in emotes:

                    emote_id = emote['id']
                    emote_dict[emote_id] = []

                    pos_dict = {}
                    pos1 = emote['begin']
                    pos2 = emote['end']

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
                        emote_html = "<img src='https://static-cdn.jtvnw.net/emoticons/v1/{}/1.0'/>".format(emote_id)
                        output += emote_html
                        position = end_position

                    else:
                        
                        output += parameters[position]
                        position += 1

                return output
                
            event = data['payload']['event']
            
            with open(f"{appdata_path}/rewardevents/web/src/config/event_not.json", "r", encoding='utf-8') as message_file:
                message_data = json.load(message_file)
            
            user_name = event['user_name']
            
            tier = event['tier']
            message_text = event['message']['text']
            emotes = event['message']['emotes']

            if not emotes == "" and not emotes == None:
                message_parse_chat = parse_emotes_message({'emotes': parse_emotes(emotes)},message_text)
            else :
                message_parse_chat = message_text

            cumulative_months = event['cumulative_months']
            streak_months = event['streak_months']
            duration_months = event['duration_months']
            
            response =  message_data['resub']['response']
            
            aliases_html = {
                '{username}' : user_name,
                '{tier}' : str(tier),
                '{total_months}' : str(cumulative_months),
                '{streak_months}' : str(streak_months),
                '{months}' : str(duration_months),
                '{user_mesage}' : str(message_text)
            }

            response_html = utils.replace_all(response,aliases_html) 


            response_chat =  message_data['resub']['response_chat']
            

            data = {
                'type_id' : 'resub',
                'username' : user_name,
                'message' : response_chat
            }
            
            send_discord_webhook(data)

            aliases_chat = {
                    '{username}' : user_name,
                    '{tier}' : str(tier),
                    '{total_months}' : str(cumulative_months),
                    '{streak_months}' : str(streak_months),
                    '{months}' : str(duration_months),
                    '{user_mesage}' : str(message_parse_chat)
                }
            
            response_chat = utils.replace_all(response_chat,aliases_chat)     

            send_announcement(response_chat,'purple')


            data = {
                'type' : 'resub',
                'username' : response_html,
                'message_html' : response_html,
                'message' : message_text
            }

            send_not_fun(data) 
            
        elif subscription_type == 'channel.raid':  
                
            event = data['payload']['event']
            
            username = event['from_broadcaster_user_name']
            viewers = event['viewers']
        
            with open(f'{appdata_path}/rewardevents/web/src/config/event_not.json', 'r', encoding='utf-8') as event_config_file:
                event_config_data = json.load(event_config_file)
    
            response = event_config_data['raid']['response']
            response_chat = event_config_data['raid']['response_chat']
            
            aliases = {
                '{username}' : username,
                '{specs}' : str(viewers),
            }

            response = utils.replace_all(response,aliases) 
            response_chat = utils.replace_all(response_chat,aliases) 
            
            data = {
                'type_id' : 'raid',
                'username' : username,
                'message_html' : response,
                'message' : response
            }  
            
            send_announcement(response_chat,'purple')
            send_discord_webhook(data)
            send_not_fun(data)   
                            
        elif subscription_type == 'channel.cheer':  
                
            event = data['payload']['event']
            
            is_anonymous = event['is_anonymous']
            
            if is_anonymous == 'True':
                user_name = ""
            else:
                user_name = event['user_name']

            message = event['message']
            bits = event['bits']
            
            with open(f'{appdata_path}/rewardevents/web/src/config/event_not.json', 'r', encoding='utf-8') as event_config_file:
                event_config_data = json.load(event_config_file)

            if int(bits) >= 1:
                type_not = 'bits1'

            elif int(bits) >= 100:
                type_not = 'bits100'

            elif int(bits) >= 1000:
                type_not = 'bits1000'

            elif int(bits) >= 1000:
                type_not = 'bits5000'

            response = event_config_data[type_not]['response']
            response_chat = event_config_data[type_not]['response_chat']
                
            aliases = {
                '{username}' : user_name,
                '{amount}' : str(bits),
            }   

            response = utils.replace_all(response,aliases) 
            response_chat = utils.replace_all(response_chat,aliases) 
            
            data = {
                'type_id' : 'bits',
                'type' : type_not,
                'username' : user_name,
                'message_html' : message,
                'message' : message
            }  
            
            send_announcement(response_chat,'purple')
            send_discord_webhook(data)
            send_not_fun(data)  

        elif subscription_type == 'channel.ban':  
            
            event = data['payload']['event']
            
            user_name = event['user_name']
            moderator_user_name = event['moderator_user_name']
            reason = event['reason']
            banned_at = event['ends_at']
            is_permanent = event['is_permanent']
            
            print(event)
            
        elif subscription_type == 'channel.unban':  
            
            event = data['payload']['event']
        
            user_name = event['user_name']
            moderator_user_name = event['moderator_user_name']
            
            print(event)
            
        elif subscription_type == 'channel.poll.begin':  
            
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
            
            data = {
                "type_id" : "poll_start",
                "title" : title,
                "choices" : choices,
                "bits_status" : bits_voting_status,
                "bits_amount" : bits_voting_amount,
                "points_status" : channel_points_voting_status,
                "points_amount" : channel_points_voting_amount,
            }

            with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'r',encoding='utf-8') as poll_file:
                poll_data = json.load(poll_file)

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

            
            with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'w',encoding='utf-8') as poll_filedump:
                json.dump(poll_data,poll_filedump,indent=4,ensure_ascii=False)

            
            send_discord_webhook(data)
            
        elif subscription_type == 'channel.poll.progress':  
            
            event = data['payload']['event']
            
            title = event['title']
            choices = event['choices']
            
            bits_voting_status = event['bits_voting']['is_enabled']
            bits_voting_amount = event['bits_voting']['amount_per_vote']
            channel_points_voting_status = event['channel_points_voting']['is_enabled']
            channel_points_voting_amount = event['channel_points_voting']['amount_per_vote']

            start_at = event['started_at']
            ends_at = event['ends_at']
            
            data = {
                "type_id" : "poll_status",
                "title" : title,
                "choices" : choices,
                "bits_status" : bits_voting_status,
                "bits_amount" : bits_voting_amount,
                "points_status" : channel_points_voting_status,
                "points_amount" : channel_points_voting_amount
            }

            with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'r',encoding='utf-8') as poll_file:
                poll_data = json.load(poll_file)

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

            with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'w',encoding='utf-8') as poll_filedump:
                json.dump(poll_data,poll_filedump,indent=4,ensure_ascii=False)
            
            send_discord_webhook(data)
            
        elif subscription_type == 'channel.poll.end':  
            
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
            
            data = {
                "type_id" : "poll_end",
                "title" : title,
                "choices" : choices,
                "bits_status" : bits_voting_status,
                "bits_amount" : bits_voting_amount,
                "points_status" : channel_points_voting_status,
                "points_amount" : channel_points_voting_amount
            }


            with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'r',encoding='utf-8') as poll_file:
                poll_data = json.load(poll_file)

            options_list = []
            poll_data['status'] = poll_status
            poll_data['current'] = current_id
            poll_data['title'] = title
            poll_data['time_start'] = start_at
            poll_data['time_end'] = ends_at

            for option in choices:
                title = option['title']
                choice_id = option['id']
                votes = option['votes']
                option_data = {
                    "title": title, "id" : choice_id, "votes" : votes
                }

                options_list.append(option_data)
                poll_data['options'] = options_list

            
            with open(f'{appdata_path}/rewardevents/web/src/config/poll_id.json', 'w',encoding='utf-8') as poll_filedump:
                json.dump(poll_data,poll_filedump,indent=4,ensure_ascii=False)
            
            send_discord_webhook(data)
            
        elif subscription_type == 'channel.prediction.begin':  
            
            with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'r',encoding='utf-8') as pred_file:
                pred_data = json.load(pred_file)

            event = data['payload']['event']
            
            title = event['title']
            outcomes = event['outcomes']
            current_id = event['id']
            time_start = event['started_at']
            time_locks = event['locks_at']

            
            data = {
                'type_id': "prediction_start",
                "title" : title,
                "outcomes" : outcomes
            }

            options_list = []
            pred_data['status'] = 'running'
            pred_data['current'] = current_id
            pred_data['title'] = title
            pred_data['time_start'] = time_start
            pred_data['time_locks'] = time_locks

            for outcome in outcomes:
                title = outcome['title']
                outcome_id = outcome['id']
                option_data = {
                    title : outcome_id
                }

                options_list.append(option_data)
                pred_data['options'] = options_list
            
            with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'w',encoding='utf-8') as pred_filedump:
                json.dump(pred_data,pred_filedump,indent=4,ensure_ascii=False)

            send_discord_webhook(data)

            eel.toast_notifc('Um palpite foi iniciado')
            
        elif subscription_type == 'channel.prediction.progress':  
            
            event = data['payload']['event']
            
            title = event['title']
            outcomes = event['outcomes']
            
            data = {
                'type_id': "prediction_progress",
                "title" : title,
                "outcomes" : outcomes
            }
            
            send_discord_webhook(data)
            
            eel.toast_notifc('O palpite foi atualizado.')
                            
        elif subscription_type == 'channel.prediction.lock':
            
            event = data['payload']['event']

            with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'r',encoding='utf-8') as pred_file:
                pred_data = json.load(pred_file)

            pred_data['status'] = 'locked'

            with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'w',encoding='utf-8') as pred_filedump:
                json.dump(pred_data,pred_filedump,indent=4,ensure_ascii=False)

            title = event['title']
            outcomes = event['outcomes']
            
            data = {
                'type_id': "prediction_progress",
                'title': title,
                'outcomes' : outcomes
            }
            
            send_discord_webhook(data)
            
            eel.toast_notifc('A votação do palpite foi encerrada.')
                                    
        elif subscription_type == 'channel.prediction.end':    
            
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
            else :
                channel_points = 0
                winner = "Nenhum"
                
            data = {
                'type_id': "prediction_end",
                'title': title,
                'outcome_win' : winner,
                'channel_points' : channel_points,
            }

            pred_data = {
                "status" : "end",
                "winner" : winner
            }   

            with open(f'{appdata_path}/rewardevents/web/src/config/pred_id.json', 'w',encoding='utf-8') as pred_filedump:
                json.dump(pred_data,pred_filedump,indent=4,ensure_ascii=False)
            
            send_discord_webhook(data)
            
            eel.toast_notifc('O palpite foi encerrado.')
            
        elif subscription_type == 'channel.goal.begin':  
                
            event = data['payload']['event']
                
            goal_type = event['type']
            description = event['description']
            current_amount = event['current_amount']
            target_amount = event['target_amount']
            started_at = event['started_at']
            
            data = {
                "type" : goal_type,
                "description" : description,
                "current_amount" : current_amount,
                "target_amount" : target_amount,
                "started_at" : started_at
            }

            with open(f"{appdata_path}/rewardevents/web/src/config/goal.json" ,"w", encoding="utf-8" ) as goal_file:
                json.dump(data,goal_file,indent=4,ensure_ascii=False)
               
        elif subscription_type == 'channel.goal.progress':  
                
            event = data['payload']['event']
            
            goal_type = event['type']
            description = event['description']
            current_amount = event['current_amount']
            target_amount = event['target_amount']
            started_at = event['started_at']

            data = {
                "type" : goal_type,
                "description" : description,
                "current_amount" : current_amount,
                "target_amount" : target_amount,
                "started_at" : started_at
            }

            with open(f"{appdata_path}/rewardevents/web/src/config/goal.json" ,"w", encoding="utf-8" ) as goal_file:
                json.dump(data,goal_file,indent=4,ensure_ascii=False)
              
        elif subscription_type == 'channel.goal.end':  
                
            event = data['payload']['event']
            
            goal_type = event['type']
            description = event['description']
            current_amount = event['current_amount']
            target_amount = event['target_amount']
            started_at = event['started_at']
            ended_at = event['ended_at']
            

            data = {
                "type" : goal_type,
                "description" : description,
                "current_amount" : current_amount,
                "target_amount" : target_amount,
                "started_at" : started_at
            }


            with open(f"{appdata_path}/rewardevents/web/src/config/goal.json" ,"w", encoding="utf-8" ) as goal_file:
                json.dump(data,goal_file,indent=4,ensure_ascii=False)

        else:
            
            event = data['payload']['event']
       
    elif message_type == 'session_keepalive':
        pass
    else:
        print(message_type)


def on_resize(width, height):
    min_width = 1200 
    min_height = 600
    
    if width < min_width or height < min_height:
        window.resize(min_width, min_height)


def start_websocket():
    
    def on_error(ws, message_error):
        utils.error_log(message_error)
        
    def on_close(ws, close_status_code, close_msg):
        print(f"{close_status_code} - {close_msg}")
        time.sleep(5)  # Aguarda 5 segundos antes de tentar se reconectar
        ws.run_forever()

    def on_open(ws):
        print("Conectado!")

    ws = websocket.WebSocketApp("wss://eventsub-beta.wss.twitch.tv/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever()
    

@eel.expose
def webview_start_app(app_mode):

    global window

    if app_mode == "normal":

        window = webview.create_window("RewardEvents", extDataDir + "/web/loading.html", width=1200, height=680, min_size=(1200, 680))

        window.events.closed += close
        window.events.resized += on_resize
        
        webview.start(storage_path=extDataDir,private_mode=False,debug=False,http_server=False)
        
    elif app_mode == "auth":

        window = webview.create_window("RewardEvents auth", "http://localhost:7000/auth.html", width=1200, height=680, min_size=(1200, 680))
        window.events.resized += on_resize
        
        webview.start(storage_path=extDataDir,private_mode=False,debug=True,http_server=False)

    elif app_mode == "chat":
        
        window_chat = webview.create_window('RewardEvents Chat', '')
        window_chat.load_url('http://localhost:7000/chat.html')


def bot():
    
    global bot_loaded, chat

    while True:
        
        if loaded_status == 1:

            eel.toast_notifc('Conectando bot ao chat')
            chat = TwitchBot(callback=command_fallback,TOKEN=authdata.TOKENBOT(), USERNAME=authdata.BOTUSERNAME(),CHANNEL=authdata.USERNAME())
            
            while True:
                
                try:
                    chat.connect()
                except ConnectionResetError:
                    eel.toast_notifc('Erro de conexão, tentando novamente em 10 segundos | COD = SOCK1')
                    time.sleep(10)
                    
                if chat.Connected == True:
                    bot_loaded = 1
                    eel.toast_notifc('Bot conectado')
                    
                    break
                else:
                    eel.toast_notifc('Erro de conexão, tentando novamente em 10 segundos | COD = AUTHCRED')
                    time.sleep(10)
                    
            chat.run()
            break
            
        else:
            
            time.sleep(10)
 
        
def start_app(start_mode):

    if start_mode == "normal":

        with open(f"{appdata_path}/rewardevents/web/src/chat_log.txt", "w") as file:
            file.truncate(0)
        
        user_data_sess_load = {}
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_database_sess.json','w',encoding='utf-8') as user_data_sess_file_w:
            json.dump(user_data_sess_load,user_data_sess_file_w,indent=6,ensure_ascii=False)
         
        user_join_sess_load = {
            'spec': [],
            'bot' :[]
        }  
        
        with open(f'{appdata_path}/rewardevents/web/src/user_info/users_sess_join.json','w',encoding='utf-8') as user_join_sess_file_w:
            json.dump(user_join_sess_load,user_join_sess_file_w,indent=6,ensure_ascii=False)
                        
        pygame.init()
        pygame.mixer.init()
        
        loopcheck_thread = threading.Thread(target=loopcheck, args=(), daemon=True)
        loopcheck_thread.start()
    
        timer_thread = threading.Thread(target=timer, args=(), daemon=True)
        timer_thread.start()

        check_bot_thread = threading.Thread(target=bot, args=(), daemon=True)
        check_bot_thread.start()

        download_badges()
        get_users_info('save', 'null')
        
        eel_thread = threading.Thread(target=eel_start, args=('normal',), daemon=True)
        eel_thread.start()
        
        get_spec_thread = threading.Thread(target=get_spec, args=(), daemon=True)
        get_spec_thread.start()
        
        websocket_thread = threading.Thread(target=start_websocket, args=(), daemon=True)
        websocket_thread.start()
        
        webview_start_app('normal')

    elif start_mode == "auth":

        eel_thread = threading.Thread(target=eel_start, args=('auth',), daemon=True)
        eel_thread.start()
        
        flask_thread = threading.Thread(target=app.run, args=('localhost',5555,), daemon=True)
        flask_thread.start()

        webview_start_app('auth')


@eel.expose
def loaded():
    
    global loaded_status
    
    loaded_status = 1
    
    eel.chat_config('get')
    
    sucess_conn = obs_events.test_obs_conn()

    if sucess_conn:

        eel.callback_obs('sucess')

    elif not sucess_conn:

        eel.callback_obs('error')

    elif sucess_conn == 'None':
        pass
    
    return loaded_status


def start_auth_pub():

    global twitch_api

    if authdata.TOKEN() and authdata.TOKENBOT():

        twitch_api = Twitch(clientid,authenticate_app=False)
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
            start_app('normal')

        except Exception as e:
            
            if e != 'invalid access token':
                utils.error_log(e)
                start_app('auth')
                
    else:
        start_app('auth')


start_auth_pub()