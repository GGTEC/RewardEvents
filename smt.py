import twitch
import auth
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

clientid = os.getenv('CLIENTID')
clientsecret = os.getenv('CLIENTSECRET')


USERNAME,BROADCASTER_ID,BOTNAME,CODE,TOKENBOT,TOKEN,REFRESH_TOKEN = auth.auth_data()

messages_file = open('web/src/messages/messages_file.json', "r", encoding='utf-8') 
messages_data = json.load(messages_file)   

def error_log(message):

    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    error = f"erro = {message} horario = {time} \n"

    with open("web/src/config/error_log.txt", "a+",encoding='utf-8') as log_file_r:
            log_file_r.write(error)


def send_message(message,type_message):
    
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
        
        
        if TOKEN and TOKENBOT:

            if type_message == 'CHAT':

                    connection.send(message)
            
            elif type_message == 'ERROR_TIME':
                
                if status_error_time == 1:
                    connection.send(message)
                        
            elif type_message == 'RESPONSE':

                if status_response == 1:
                    connection.send(message)
                    
            elif type_message == 'ERROR_USER':
                
                if status_error_user == 1:
                    connection.send(message)
                        
            elif type_message == 'CLIP':
                
                if status_clip == 1:
                    connection.send(message)
                        
            elif type_message == 'ERROR_TTS':
                
                if status_tts == 1:
                    connection.send(message)
                    
            elif type_message == 'TIMER':
                
                if status_timer == 1:
                    
                    connection.send(message) 
                    
            elif type_message == 'STATUS_BOT':
                
                if status_bot == 1:
                    connection.send(message)

            elif type_message == 'STATUS_MUSIC':
                
                if status_music == 1:
                    connection.send(message)
                    
            elif type_message == 'STATUS_MUSIC_CONFIRM':
                
                if status_music_confirm == 1:
                    connection.send(message)
                    
            elif type_message == 'STATUS_MUSIC_ERROR':
                
                if status_music_error == 1:
                    connection.send(message)


    except Exception as e:

        error_log(repr(e) + ' Linha 78 - smt')
        time.sleep(10)
        send_message(message,type_message)


def conect_chat():

    global connection,value

    value = False

    if TOKEN and TOKENBOT:
        
        try:
            
            connection = twitch.Chat(channel=USERNAME, nickname=BOTNAME, oauth='oauth:' + TOKENBOT)

            module_send = messages_data['messages_chat_module_status']
            send_message(module_send,'STATUS_BOT')

            value = True

        except Exception as e:

            error_log(repr(e) + ' Linha 97 - smt-conn')
            time.sleep(10)

            value = False

            conect_chat()

    else:

        value = False
        


