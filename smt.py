from twitch_chat_irc import twitch_chat_irc
import auth
import json
import time
from tkinter import messagebox


USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()

def conect_chat():
    global connection
    try:
        connection = twitch_chat_irc.TwitchChatIRC(BOTNAME, TOKENBOT)
        value = True
        return value
    
    except:
        value = False
        return value  


def send_message(message,type_message):
    
    status_commands_check = open('src/config/commands_config.json')
    status_commands_data = json.load(status_commands_check)
    
    status_error_time = status_commands_data['STATUS_ERROR_TIME']
    status_error_user = status_commands_data['STATUS_ERROR_USER']
    status_response = status_commands_data['STATUS_RESPONSE']
    status_clip = status_commands_data['STATUS_CLIP']
    status_tts = status_commands_data['STATUS_TTS']
    status_timer = status_commands_data['STATUS_TIMER']
    status_bot = status_commands_data['STATUS_BOT']
    
    
    if TOKEN and TOKENBOT:
        
        if type_message == 'ERROR_TIME':
            
            if status_error_time == 1:
                connection.send(USERNAME, message)
                    
        elif type_message == 'RESPONSE':
            
            if status_response == 1:
                connection.send(USERNAME, message)
                
        elif type_message == 'ERROR_USER':
            
            if status_error_user == 1:
                connection.send(USERNAME, message)
                    
        elif type_message == 'CLIP':
            
            if status_clip == 1:
                connection.send(USERNAME, message)
                    
        elif type_message == 'ERROR_TTS':
            
            if status_tts == 1:
                connection.send(USERNAME, message)
                
        elif type_message == 'TIMER':
            
            if status_timer == 1:
                connection.send(USERNAME, message) 
                
        elif type_message == 'STATUS_BOT':
            
            if status_bot == 1:
                connection.send(USERNAME, message)
    else:
        messagebox.showerror('Erro','Conta não autenticada.')
        


