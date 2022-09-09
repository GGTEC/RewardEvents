#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import customtkinter
import os
import auth
import apitoken
import keyboard
import pygame
import PIL.Image
import random
import _thread
import requests as req
import auth_user
import auth_bot
import subprocess
import wget
import check_delay_file
from  load_files import check_files
from tooltiptkinter import CreateToolTip
from math import trunc
from gtts import gTTS
from random import randint
from PIL import ImageTk
from requests.structures import CaseInsensitiveDict
from twitchAPI.pubsub import PubSub
from uuid import UUID
from tkinter import *
from tkinter import PhotoImage
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog as fd
from ttkthemes import ThemedStyle
from obswebsocket import obsws, requests
from twitch_chat_irc import twitch_chat_irc
from twitchAPI.twitch import Twitch, AuthScope


check_files()
                
def run_cmd(command):
    subprocess.call(command, creationflags=0x08000000)
    
def callback_whisper(uuid: UUID, data: dict) -> None:
    received_type = 'redeem'
    receive_redeem(data,received_type)

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

pygame.init()
pygame.mixer.init()
   
app = customtkinter.CTk()
app.title('RewardEvents by GG-TEC')
app.geometry('490x620')
app.resizable(False, False)
app.iconbitmap("src/icon.ico")

style = ThemedStyle(app)
style.set_theme("black")

s = ttk.Style(app)
s.configure('black.TFrame', background='black')

frame = ttk.Notebook(app)
frame.pack(expand= True, fill=BOTH)

tab1 = customtkinter.CTkFrame(frame)
tab2 = customtkinter.CTkFrame(frame)
tab3 = customtkinter.CTkFrame(frame)
tab4 = customtkinter.CTkFrame(frame)
tab5 = customtkinter.CTkFrame(frame)
tab6 = customtkinter.CTkFrame(frame)
tab7 = customtkinter.CTkFrame(frame)

frame.add(tab1, text ='Aguardando')
frame.add(tab2, text ='Eventos')
frame.add(tab3, text ='Comandos')
frame.add(tab4, text ='Timers')
frame.add(tab5, text ='Configurações')
frame.add(tab6, text ='Perfil')
frame.add(tab7, text ='Sobre')

path_text = customtkinter.StringVar()
count = 0

def replace_all(text, dic):
    
    for i, j in dic.items():
        text = text.replace(i, j)
        
    return text

def con_chat():
    
    global connection,con_status
    con_status = '0'
    
    try:
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        if TOKEN and TOKENBOT:
            
            connection = twitch_chat_irc.TwitchChatIRC(BOTNAME, TOKENBOT)
            status_send_label.configure(text="Conectado!")
            con_status = '1'
            
            url = f"https://api.twitch.tv/helix/streams?user_id={USERID}"

            headers = CaseInsensitiveDict()
            headers["Authorization"] = "Bearer "+ TOKEN
            headers["Client-Id"] = apitoken.CLIENTID

            resp = req.get(url, headers=headers)
            data_count = json.loads(resp.text)
            try:
                count = data_count['data'][0]['viewer_count']
                view_count.configure(text=f'Spec : {count}')
            except:
                view_count.configure(text=f'Spec : Offline')      
    except:
        
        con_status = '0'
        status_send_label.configure(text="Desconectado!")
    
def keep_conn_chat(tid):
        while True:
            con_chat()
            time.sleep(120)

class Obsconect:
    def __init__(self):
        super().__init__()
        self.ws = None
        self.conn_status = '0'

    def conect_obs(self):

        out_file_obs_atual = open("src/config/obs.json")
        data_obs_atual = json.load(out_file_obs_atual)

        obs_host_data_atual = data_obs_atual['OBS_HOST']
        obs_port_data_atual = data_obs_atual['OBS_PORT']
        obs_port_int = int(obs_port_data_atual)
        obs_password_data_atual = data_obs_atual['OBS_PASSWORD']

        try:
            self.ws = obsws(obs_host_data_atual, obs_port_int, obs_password_data_atual)
            self.ws.connect()
            status_obs.configure(text=f"Conectado!")
            self.conn_status = '1'
        except:
            pass    
            
    def show_filter(self,source_name,filter_name,time_show_int):
        
        if self.conn_status == "1":
            self.ws.call(requests.SetSourceFilterVisibility(source_name,filter_name,True))
            time.sleep(time_show_int)
            self.ws.call(requests.SetSourceFilterVisibility(source_name,filter_name,False))
                   
    def scene(self,scene_name,return_scene,time_show,principal_scene_name):

        if self.conn_status == "1":
            
            if return_scene == 1:
                self.ws.call(requests.SetCurrentScene(scene_name))
                
                time.sleep(int(time_show))
                self.ws.call(requests.SetCurrentScene(principal_scene_name))
            else:
                self.ws.call(requests.SetCurrentScene(scene_name))
            
    def show_notifc(self,redem_reward_name,redem_by_user,int_time_show):
        
        not_file = open('src/config/notfic.json') 
        not_data = json.load(not_file)
        
        text_request_title= not_data["TEXT_TITLE_REDEEM"]
        text_user_name = not_data["TEXT_USER_REDEM"]
        group_obs = not_data["NOTF_GROUP_OBS"]
        
        if self.conn_status == "1":
            self.ws.call(requests.SetTextGDIPlusProperties(text_request_title,text=redem_reward_name))
            self.ws.call(requests.SetTextGDIPlusProperties(text_user_name,text=redem_by_user))
            self.ws.call(requests.SetSceneItemProperties(group_obs,visible= True))

            time.sleep(int_time_show)

            self.ws.call(requests.SetSceneItemProperties(group_obs,visible= False))
            self.ws.call(requests.SetTextGDIPlusProperties(text_user_name,text='Aguardando'))
            self.ws.call(requests.SetTextGDIPlusProperties(text_request_title,text='Aguardando'))
        
    def show_source(self,source_name,time_show_int):
        
        if self.conn_status == "1":
        
            self.ws.call(requests.SetSceneItemProperties(source_name,visible= True))
            time.sleep(time_show_int)
            self.ws.call(requests.SetSceneItemProperties(source_name,visible= False))
    
obs_con = Obsconect()
               
def send_message(message,type_message):
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
    
    global connection
    
    status_commands_check = open('src/config/prefix_commands.json')
    status_commands_data = json.load(status_commands_check)
    
    status_error_time = status_commands_data['STATUS_ERROR_TIME']
    status_error_user = status_commands_data['STATUS_ERROR_USER']
    status_response = status_commands_data['STATUS_RESPONSE']
    status_clip = status_commands_data['STATUS_CLIP']
    status_tts = status_commands_data['STATUS_TTS']
    status_timer = status_commands_data['STATUS_TIMER']
    
    
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
    else:
        messagebox.showerror('Erro','Conta não autenticada.')
                
def receive_redeem(data_rewards,received_type):
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
    
    redem_reward_name = '0'
    redem_by_user = '0'
    user_input = '0'
    user_level =  '0'
    user_id_command = '0'
    command_receive = '0'
    prefix = '0'
        
    if received_type == 'redeem':
    
        redem_reward_name = data_rewards['data']['redemption']['reward']['title']
        redem_by_user = data_rewards['data']['redemption']['user']['display_name']
        
        try:
            redem_reward_image = data_rewards['data']['redemption']['reward']['image']['url_4x']
        except:
            redem_reward_image = data_rewards['data']['redemption']['reward']['default_image']['url_4x']
            
        img_data = req.get(redem_reward_image).content
        with open('src/Request.png', 'wb') as handler:
            handler.write(img_data)
            handler.close()
            
    elif received_type == 'command':

        redem_reward_name = data_rewards['REDEEM']
        redem_by_user = data_rewards['USERNAME']
        user_input = data_rewards['USER_INPUT']
        user_level =  data_rewards['USER_LEVEL']
        user_id_command = data_rewards['USER_ID']
        command_receive = data_rewards['COMMAND']
        prefix = data_rewards['PREFIX']
        


    request_img_result = ImageTk.PhotoImage(PIL.Image.open("src/Request.png").resize((200, 200)).convert("RGBA"))
    request_img.configure(image=request_img_result)
    request_img.image = request_img_result

    request_name.configure(text=redem_reward_name)
    user_request.configure(text='  '+ redem_by_user + '  ')

    path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
    path = json.load(path_file)    
        
    def playsound():
        
        audio_path = path[redem_reward_name]['PATH']
        time_show = path[redem_reward_name]['TEMPO']
        send_response_value = path[redem_reward_name]['send_response']
        int_time_show = int(time_show)
        
        tts_playing = pygame.mixer.music.get_busy()
        
        while tts_playing:
                tts_playing = pygame.mixer.music.get_busy()
                time.sleep(2)
                  
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        if send_response_value:
            chat_response = path[redem_reward_name]['chat_response']
            
            aliases = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
            response_redus = replace_all(chat_response, aliases)
                    
            send_message(response_redus,'RESPONSE')
            
        obs_con.show_notifc(redem_reward_name,redem_by_user,int_time_show)

    def playtts():
        
        
        global count
        
        try:
            user_input = data_rewards['data']['redemption']['user_input']
        except:
            user_input = data_rewards['USER_INPUT']
            
        time_show = path[redem_reward_name]['TEMPO']
        send_response_value = path[redem_reward_name]['send_response']
        int_time_show = int(time_show)
        
        language = 'pt-br'
        
        tts = gTTS(text=user_input, lang=language, slow=False)
        
        tts.save(f'src/files/tts_sound{count%2}.mp3')
        
        
        tts_playing = pygame.mixer.music.get_busy()
        
        while tts_playing:
                tts_playing = pygame.mixer.music.get_busy()
                time.sleep(2)  
        
        pygame.mixer.music.load(f'src/files/tts_sound{count%2}.mp3')
        pygame.mixer.music.play()
        
        if send_response_value:
            
            chat_response = path[redem_reward_name]['chat_response']
            
            aliases = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
            response_redus = replace_all(chat_response, aliases)
                    
            send_message(response_redus,'RESPONSE')

        count += 1
        
        obs_con.show_notifc(redem_reward_name,redem_by_user,int_time_show)

    def changescene():
        
        princial_scene_name = path[redem_reward_name]['CURRENTSCENENAME']
        scene_name = path[redem_reward_name]['SCENENAME']
        send_response_value = path[redem_reward_name]['send_response']
        return_scene = path[redem_reward_name]['return_scene']
        
        time_show = path[redem_reward_name]['TIME']
        
        if send_response_value == 1:
 
            chat_response = path[redem_reward_name]['chat_response']
            
            aliases = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
            response_redus = replace_all(chat_response, aliases)
                    
            send_message(response_redus,'RESPONSE')
            
        obs_con.scene(scene_name,time_show,return_scene,princial_scene_name)

    def sendmessage():

        message = path[redem_reward_name]['MESSAGELABEL']
        
        aliases = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
        response_redus = replace_all(message, aliases)
                
        send_message(response_redus,'RESPONSE')

    def changefilter():

        source_name = path[redem_reward_name]['SOURCE']
        send_response_value = path[redem_reward_name]['send_response']
        filter_name = path[redem_reward_name]['FILTER']
        time_show = path[redem_reward_name]['TIME']

        time_show_int = int(time_show)
        
        
        if send_response_value:
            chat_response = path[redem_reward_name]['chat_response']
            
            aliases = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
            response_redus = replace_all(chat_response, aliases)
                    
            send_message(response_redus,'RESPONSE')
        
        obs_con.show_filter(source_name,filter_name,time_show_int)
        
    def keypress():


        keyskeyboard = path[redem_reward_name]
        send_response_value = path[redem_reward_name]['send_response']
        press_again_value = path[redem_reward_name]['press_again']
        time_press_value = path[redem_reward_name]['TIME']
        
        if press_again_value == 1:
            
            if send_response_value:
                
                chat_response = path[redem_reward_name]['chat_response']
                
                aliases = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
                response_redus = replace_all(chat_response, aliases)
                    
                send_message(response_redus,'RESPONSE')
                
            time_press = int(time_press_value)
            received = [*keyskeyboard.keys()][6:]

            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']


            keyboard.press_and_release('+'.join(keys_to_pressed))
            
            time.sleep(time_press)
            
            keyboard.press_and_release('+'.join(keys_to_pressed))
            

            
        else:       
            
            if send_response_value:
                
                chat_response = path[redem_reward_name]['chat_response']
                
                aliases = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
                response_redus = replace_all(chat_response, aliases)
                    
                send_message(response_redus,'RESPONSE')
                
            received = [*keyskeyboard.keys()][6:]
            
            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']
        
            keyboard.press_and_release('+'.join(keys_to_pressed))           
                   
    def source():

        source_name = path[redem_reward_name]['SOURCENAME']
        send_response_value = path[redem_reward_name]['send_response']
        time_show = path[redem_reward_name]['TIME']

        time_show_int = int(time_show)
        
        
        if send_response_value:
            
            chat_response_source = path[redem_reward_name]['chat_response']
            
            aliases_source = {'{user}': redem_by_user,'{command}': command_receive, '{prefix}': prefix,'{user_level}': user_level, '{user_id}': user_id_command}
            response_redus_source = replace_all(chat_response_source, aliases_source)
            
            send_message(response_redus_source,'RESPONSE')
        
        obs_con.show_source(source_name,time_show_int)
        
    def clip():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        
    
        url1 = "https://api.twitch.tv/helix/clips?broadcaster_id=" + USERID

        headers1 = CaseInsensitiveDict()
        headers1["Authorization"] = 'Bearer ' + TOKEN
        headers1["Client-Id"] = apitoken.CLIENTID
        headers1["Content-Length"] = "0"


        resp1 = req.post(url1, headers=headers1)

        response_clip = json.loads(resp1.text)
        
        try:
            response_error = 'None'
            response_create = response_clip['data'][0]['id']
            
            send_message(f"/me Um novo clip foi criado por = {redem_by_user}, confira! https://clips.twitch.tv/{response_create}","CLIP")
            
        except:
            response_error = response_clip['message']

            if response_error:
                send_message('/me Erro ao criar o clip','CLIP')

    eventos = {
        'SOUND' : playsound,
        'SCENE' : changescene,
        'MESSAGE' : sendmessage,
        'FILTER' : changefilter,
        'KEYPRESS' : keypress,
        'SOURCE' : source,
        'CLIP': clip,
        'TTS' : playtts
    }
    
    try:
        if TOKEN and TOKENBOT:
            redem_type = path[redem_reward_name]['TYPE']
            if redem_type in eventos:
                eventos[redem_type]()
    except:
        pass
       
def new_sound():
    
    topsound = customtkinter.CTkToplevel(app)
    topsound.title('RewardEvents - Reproduzir som')    
    
    def select_file():
        global filename

        filetypes = (
            ('audio files', '*.mp3'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            parent=topsound,
            title='Open a file',
            initialdir='src/files',
            filetypes=filetypes)
        
        path_text.set(filename)
    
    def create_new_sound():
        
        title = redem_title.get()
        command_event = command_entry.get()
        audio_dir = redem_path.get()
        time_in_screm = redem_time.get()
        chat_response = chat_response_entry.get()
        user_level_check = user_level_switch.get()
        
        if not [x for x in (title, audio_dir, time_in_screm) if x is None]:
            try:
                if chat_response is None:
                    
                    send_response = 0
                else:
                    
                    send_response = 1
                    
                    old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                    new_data = json.load(old_data)

                    new_data[title] = {
                                        'TYPE': 'SOUND',
                                        'PATH': audio_dir,
                                        'COMMAND': command_event, 
                                        'send_response': send_response, 
                                        'chat_response':chat_response, 
                                        'TEMPO':time_in_screm 
                                       }
                    old_data.close()

                    old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                    json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)
                    
                    old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                    new_data_command = json.load(old_data_command)
                    
                    if user_level_check:
                        user_level_data = "mod"
                    else:
                        user_level_data = ""
                    
                    new_data_command[command_event] = {'RECOMPENSA': title,'user_level':user_level_data}
                    old_data.close()
                    
                    old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                    
                    messagebox.showinfo("Sucesso!",f"Evento de audio '{title}' criado com sucesso!",parent=topsound)
                    
            except:
                messagebox.showinfo("Erro!",f"Erro ao criar evento!",parent=topsound)
        else:
            messagebox.showinfo("Erro!",f"Preencha os campos com (*)",parent=topsound)
       
    def update_titles_combox():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')
        
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox() 
           
    tittleredem1 = customtkinter.CTkLabel(topsound, text="Criar um som para uma recompensa", text_font=("default_theme","15"))
    tittleredem1.grid(row=0, column=0, columnspan=2, pady=20,)

    redem_title_label = customtkinter.CTkLabel(topsound, text="Recompensa* :", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label.grid(row=1,column=0,padx=20,pady=10,sticky='W')
    
    redem_title = customtkinter.CTkComboBox(topsound,values=list(messages_combox),width=200)
    redem_title.grid(row=1,column=1 ,padx=20, pady=10)
    
    command_label = customtkinter.CTkLabel(topsound, text="Comando para o chat (opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2,column=0,padx=20,pady=10,sticky='W')
    
    command_entry = customtkinter.CTkEntry(topsound,width=200)
    command_entry.grid(row=2, column=1,padx=20, pady=10)
    
    user_level_label = customtkinter.CTkLabel(topsound, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_switch = customtkinter.CTkSwitch(topsound, text=" ", text_font=("default_theme", "13"),)
    user_level_switch.grid(row=3, column=1,padx=20, pady=10)

    redem_path_label = customtkinter.CTkLabel(topsound, text="Arquivo de audio*:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_path_label.grid(row=3,column=0, padx=20, pady=10,sticky='W')

    redem_path = customtkinter.CTkEntry(topsound,width=200,textvariable=path_text,state=DISABLED)
    redem_path.grid(row=3,column=1,padx=20,pady=(0,10))

    redem_path_button = customtkinter.CTkButton(topsound,width=200, text="Selecionar arquivo:", text_font=("default_theme","13"),command=select_file)
    redem_path_button.grid(row=4,columnspan=2,padx=20, pady=10,sticky='WE')

    redem_time_label = customtkinter.CTkLabel(topsound,text="Tempo da notificação no OBS*:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_time_label.grid(row=5,column=0, padx=20,pady=10, sticky='W')

    redem_time = customtkinter.CTkEntry(topsound,width=200)
    redem_time.grid(row=5,column=1, padx=20, pady=10)
    
    chat_response_label = customtkinter.CTkLabel(topsound,text="Resposta no chat (opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    chat_response_label.grid(row=6,column=0, padx=20,pady=10, sticky='W')

    chat_response_entry = customtkinter.CTkEntry(topsound,width=200)
    chat_response_entry.grid(row=6,column=1, padx=20, pady=10)

    submit_buttom = customtkinter.CTkButton(topsound,text='Salvar',command = create_new_sound)
    submit_buttom.grid(row=8, column=1,padx=20, pady=(10,20), sticky='e')
    
    topsound.mainloop()
  
def new_tts():
    
    toptts = customtkinter.CTkToplevel(app)
    toptts.title('RewardEvents - Reproduzir tts')
    
    def create_new_tts():
        
        title = redem_title.get()
        time_in_screm = redem_time.get()
        command_event = command_entry.get()
        user_level_check = user_level_Switch.get()
        chat_response = chat_response_entry.get()
        
        if not [x for x in (title, time_in_screm) if x is None]:
            try:
                if chat_response is None:
                    send_response = 0
                else:
                    send_response = 1
                old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                new_data = json.load(old_data)

                new_data[title] = {'TYPE': 'TTS','send_response':send_response, 
                                   'chat_response':chat_response, 'COMMAND':command_event,'TEMPO':time_in_screm}
                old_data.close()

                old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)
                
                old_data_command = open('src/config/prefix_tts.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)
                
                command_tts = f"!{command_event}" 
                
                if user_level_check:
                    user_level_data = "mod"
                else:
                    user_level_data = ""

                new_data_command = {'command':command_tts,'redeem': title,'user_level': user_level_data}
                
                old_data.close()
                
                old_data_write_command = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
                json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
                
                
                messagebox.showinfo("Sucesso!",f"Evento de tts '{title}' criado com sucesso!",parent=toptts)
            except:
                messagebox.showinfo("Erro!",f"Erro ao criar evento!",parent=toptts)
        else:
            messagebox.showinfo("Erro!",f"Preencha os campos com (*)",parent=toptts)
            
    def update_titles_combox():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')
        
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox()         
            
    tittleredem1 = customtkinter.CTkLabel(toptts, text="Criar um resgate de texto para fala", text_font=("default_theme","15"))
    tittleredem1.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

    redem_title_label = customtkinter.CTkLabel(toptts, text="Recompensa* :", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label.grid(row=1,column=0,padx=20,pady=10,sticky='W')

    redem_title = customtkinter.CTkComboBox(toptts,values=list(messages_combox),width=200)
    redem_title.grid(row=1,column=1 ,padx=20, pady=10)
    
    command_label = customtkinter.CTkLabel(toptts, text="Comando para o chat(opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2,column=0,padx=20,pady=10,sticky='W')
    
    command_entry = customtkinter.CTkEntry(toptts,width=200)
    command_entry.grid(row=2, column=1,padx=20, pady=10)
    
    user_level_Switch_label = customtkinter.CTkLabel(toptts, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_Switch_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_Switch = customtkinter.CTkSwitch(toptts, text=" ", text_font=("default_theme", "13"),)
    user_level_Switch.grid(row=3, column=1,padx=20, pady=10)
    
    redem_time_label = customtkinter.CTkLabel(toptts,text="Tempo da notificação no OBS*:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_time_label.grid(row=5,column=0, padx=20,pady=10, sticky='W')

    redem_time = customtkinter.CTkEntry(toptts,width=200)
    redem_time.grid(row=5,column=1, padx=20, pady=10)
    
    chat_response_label = customtkinter.CTkLabel(toptts,text="Resposta no chat (opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    chat_response_label.grid(row=6,column=0, padx=20,pady=10, sticky='W')

    chat_response_entry = customtkinter.CTkEntry(toptts,width=200)
    chat_response_entry.grid(row=6,column=1, padx=20, pady=10)

    submit_buttom = customtkinter.CTkButton(toptts,text='Salvar',command = create_new_tts)
    submit_buttom.grid(row=7, column=1,padx=20, pady=(10,30), sticky='e')
    
    toptts.mainloop()
            
def new_scene():
    
    top_scene = customtkinter.CTkToplevel(app)
    top_scene.title('RewardEvents - Mudar Cena')
    
    def create_scene():
        
        title_redem = redem_title1.get()
        current_scene_name = scene_entry_current.get()
        scene_name = scene_entry.get()
        time_to_change = time_scene_entry.get()
        command_event = command_entry.get()
        chat_response = chat_response_entry.get()
        return_scene_value = return_scene_switch.get()
        user_level_check = user_level_switch.get()

        if not [x for x in (title_redem, current_scene_name, scene_name) if x is None]:
            
            try:
                if chat_response is None:
                    send_response = 0
                else:
                    send_response = 1
                    
                if user_level_check:
                    user_level_data = "mod"
                else:
                    user_level_data = ""
                    
                old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                new_data = json.load(old_data)

                new_data[title_redem] = {'TYPE': 'SCENE','SCENENAME': scene_name,'send_response':send_response,'COMMAND': command_event,
                                         'chat_response':chat_response,'return_scene':return_scene_value,'TIME':time_to_change,'CURRENTSCENENAME': current_scene_name}
                old_data.close()

                old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)
                
                old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)
                
                new_data_command[command_event] = {'RECOMPENSA': title_redem,'user_level': user_level_data}
                old_data.close()
                
                old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                
                
                messagebox.showinfo("Sucesso!",f"O evento de cena '{title_redem}' Foi criado!",parent=top_scene)
            except:
                messagebox.showerror("Erro","Erro ao criar o evento.",parent=top_scene)
        else:
            messagebox.showerror("Erro","Preencha os campos com *!",parent=top_scene)

    def update_titles_combox():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')
        
                
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox()   
                
    tittleredem1 = customtkinter.CTkLabel(top_scene, text="Mudança de cena com recompensa", text_font=("default_theme","15"))
    tittleredem1.grid(row=0, column=0, columnspan=2, pady=20)

    redem_title_label1 = customtkinter.CTkLabel(top_scene, text="Recompensa:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label1.grid(row=1,column=0,padx=20,pady=10,sticky='W')

    redem_title1 = customtkinter.CTkComboBox(top_scene,values=list(messages_combox),width=200)
    redem_title1.grid(row=1,column=1 ,padx=20, pady=10)
    
    command_label = customtkinter.CTkLabel(top_scene, text="Comando para o chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2,column=0,padx=20,pady=10,sticky='W')
    
    command_entry = customtkinter.CTkEntry(top_scene,width=200)
    command_entry.grid(row=2, column=1,padx=20, pady=10)
    
    user_level_label = customtkinter.CTkLabel(top_scene, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_switch = customtkinter.CTkSwitch(top_scene, text=" ", text_font=("default_theme", "13"),)
    user_level_switch.grid(row=3, column=1,padx=20, pady=10)

    scene_label_current = customtkinter.CTkLabel(top_scene,text="Cena Atual:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    scene_label_current.grid(row=4,column=0, padx=20,pady=10, sticky='W')

    scene_entry_current = customtkinter.CTkEntry(top_scene,width=200)
    scene_entry_current.grid(row=4,column=1, padx=20, pady=10)

    scene_label = customtkinter.CTkLabel(top_scene,text="Mudar para a cena:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    scene_label.grid(row=5,column=0, padx=20, pady=10, sticky='W')

    scene_entry = customtkinter.CTkEntry(top_scene,width=200)
    scene_entry.grid(row=5,column=1, padx=20, pady=10)
    
    return_scene = customtkinter.CTkLabel(top_scene, text='Retornar para cena anterior ?', text_font=("default_theme","13"))
    return_scene.grid(row=6, column=0, padx=20, pady=10, sticky='w')

    return_scene_switch = customtkinter.CTkSwitch(top_scene, text=" ",)
    return_scene_switch.grid(row=6, column=1, padx=20, pady=10, sticky='e')

    time_scene_label = customtkinter.CTkLabel(top_scene,text="Tempo para voltar para \na cena anterior:", text_font=("default_theme","13"),anchor="center", justify=CENTER)
    time_scene_label.grid(row=7,column=0, padx=20, pady=10, sticky='W')

    time_scene_entry = customtkinter.CTkEntry(top_scene,width=200)
    time_scene_entry.grid(row=7,column=1, padx=20, pady=10)

    chat_response_label = customtkinter.CTkLabel(top_scene,text="Resposta no chat (opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    chat_response_label.grid(row=8,column=0, padx=20,pady=10, sticky='W')

    chat_response_entry = customtkinter.CTkEntry(top_scene,width=200)
    chat_response_entry.grid(row=8,column=1, padx=20, pady=10)
    
    submit_buttom3 = customtkinter.CTkButton(top_scene,text='Salvar',command = create_scene)
    submit_buttom3.grid(row=9, column=1,padx=20, pady=(10,20), sticky='e')
    
    top_scene.mainloop()
    
def new_message():
    
    new_message_top = customtkinter.CTkToplevel(app)
    new_message_top.title('RewardEvents - Resposta no chat')
    
    def create_message():
    
        title = redem_title2.get()
        message = message_entry.get()
        command_event = command_entry.get()
        user_level_check = user_level_switch.get()

        if not [x for x in (title, message) if x is None]:
            try:
                
                if user_level_check:
                    user_level_data = "mod"
                else:
                    user_level_data = ""
                    
                old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                new_data = json.load(old_data)

                new_data[title] = {'TYPE': 'MESSAGE', 'COMMAND': command_event, 'MESSAGELABEL': message,}
                old_data.close()

                old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                json.dump(new_data, old_data_write, indent = 4, ensure_ascii=False)
                
                old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)
                
                new_data_command[command_event] = {'RECOMPENSA': title,'user_level': user_level_data}
                old_data.close()
                
                old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
                
                
                messagebox.showinfo("Sucesso!","Evento de mensagem criado com sucesso!",parent=new_message_top)
            except:
                messagebox.showerror("Erro","Erro ao criar o evento de mensagem.",parent=new_message_top)
        else:
            messagebox.showerror("Erro","Preencha todos os campos.",parent=new_message_top)
       
    def update_titles_combox():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')  
        
              
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox()  
            
    tittleredem2 = customtkinter.CTkLabel(new_message_top, text="Resposta no chat com recompensa", text_font=("default_theme","15"))
    tittleredem2.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

    redem_title_label2 = customtkinter.CTkLabel(new_message_top, text="Recompensa:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label2.grid(row=1,column=0,pady=10,padx=10,sticky='W')

    redem_title2 = customtkinter.CTkComboBox(new_message_top,values=list(messages_combox),width=200)
    redem_title2.grid(row=1,column=1 ,padx=10, pady=10)
    
    command_label = customtkinter.CTkLabel(new_message_top, text="Comando para o chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2,column=0,pady=10,padx=10,sticky='W')
    
    command_entry = customtkinter.CTkEntry(new_message_top,width=200)
    command_entry.grid(row=2, column=1,padx=10, pady=10)
    
    user_level_label = customtkinter.CTkLabel(new_message_top, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_switch = customtkinter.CTkSwitch(new_message_top, text=" ", text_font=("default_theme", "13"),)
    user_level_switch.grid(row=3, column=1,padx=20, pady=10)

    message_label = customtkinter.CTkLabel(new_message_top,text="Mensagem no Chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    message_label.grid(row=4,column=0, padx=10,pady=10, sticky='W')

    message_entry = customtkinter.CTkEntry(new_message_top,width=200)
    message_entry.grid(row=4,column=1, padx=10, pady=10)

    submit_buttom4 = customtkinter.CTkButton(new_message_top,text='Salvar',command = create_message)
    submit_buttom4.grid(row=5, column=1,padx=20, pady=(10,20), sticky='e')
    
    new_message_top.mainloop()
      
def new_filter():
    
    new_filter_top = customtkinter.CTkToplevel(app)
    new_filter_top.title('RewardEvents - Novo filtro')
    
    
    def create_new_filter():
        
        title = redem_title3.get()
        filter_name = obs_filter_entry.get()
        source_name = obs_source_entry.get()
        time_showing = time_filter_entry.get()
        command_event = command_entry.get()
        chat_response = chat_response_entry.get()
        user_level_check = user_level_switch.get()
        
        if not [x for x in (title, filter_name,source_name,time_showing) if x is None]:
            try:
                
                if chat_response is None:
                    send_response = 0
                else:
                    send_response = 1
                
                if user_level_check:
                    user_level_data = "mod"
                else:
                    user_level_data = ""    
                    
                old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                new_data = json.load(old_data)

                new_data[title] = {'TYPE': 'FILTER','SOURCE': source_name, 'send_response':send_response, 'chat_response':chat_response, 
                                   'COMMAND': command_event, 'FILTER':filter_name, 'TIME':time_showing}
                old_data.close()

                old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                json.dump(new_data, old_data_write, indent = 4, ensure_ascii=False)
                
                
                old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)

                new_data_command[command_event] = {'RECOMPENSA': title,'user_level': user_level_data}
                old_data.close()

                old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                
                
                messagebox.showinfo("Sucesso",f"Evento de filtro '{title}' criado com sucesso",parent=new_filter_top)
            except:
                messagebox.showerror("Erro","Erro ao criar o evento.",parent=new_filter_top)
        else:
            messagebox.showerror("Erro","Preencha todos os campos",parent=new_filter_top)            


    def update_titles_combox():
        
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')  
              
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox()  
        
    tittleredem3 = customtkinter.CTkLabel(new_filter_top, text="Aplicar filtro no OBS com recompensa", text_font=("default_theme","15"))
    tittleredem3.grid(row=0, column=0, columnspan=2, pady=20)

    redem_title_label3 = customtkinter.CTkLabel(new_filter_top, text="Recompensa:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label3.grid(row=1,column=0, padx=20, pady=10, sticky='W')

    redem_title3 = customtkinter.CTkComboBox(new_filter_top,values=list(messages_combox),width=200)
    redem_title3.grid(row=1,column=1 ,padx=10, pady=10)
    
    command_label = customtkinter.CTkLabel(new_filter_top, text="Comando para o chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2, column=0, padx=20, pady=10, sticky='W')

    command_entry = customtkinter.CTkEntry(new_filter_top,width=200)
    command_entry.grid(row=2, column=1,padx=20, pady=10)
    
    user_level_label = customtkinter.CTkLabel(new_filter_top, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_switch = customtkinter.CTkSwitch(new_filter_top, text=" ", text_font=("default_theme", "13"),)
    user_level_switch.grid(row=3, column=1,padx=20, pady=10)

    obs_source_label = customtkinter.CTkLabel(new_filter_top,text="Nome da Fonte do OBS:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    obs_source_label.grid(row=4, column=0, padx=20, pady=10, sticky='W')

    obs_source_entry = customtkinter.CTkEntry(new_filter_top,width=200)
    obs_source_entry.grid(row=4, column=1, padx=20, pady=10)

    obs_filter_label = customtkinter.CTkLabel(new_filter_top,text="Nome do filtro presente \nna fonte:", text_font=("default_theme","13"),anchor="center", justify=CENTER)
    obs_filter_label.grid(row=5, column=0, padx=20, pady=10, sticky='W')

    obs_filter_entry = customtkinter.CTkEntry(new_filter_top,width=200)
    obs_filter_entry.grid(row=5,column=1, padx=20, pady=10)

    time_filter_label = customtkinter.CTkLabel(new_filter_top,text="Tempo com o filtro ativo:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    time_filter_label.grid(row=6,column=0, padx=20,pady=10, sticky='W')

    time_filter_entry = customtkinter.CTkEntry(new_filter_top,width=200)
    time_filter_entry.grid(row=6,column=1, padx=20, pady=10)
    
    chat_response_label = customtkinter.CTkLabel(new_filter_top,text="Resposta no chat (opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    chat_response_label.grid(row=7,column=0, padx=20,pady=10, sticky='W')

    chat_response_entry = customtkinter.CTkEntry(new_filter_top,width=200)
    chat_response_entry.grid(row=7,column=1, padx=20, pady=10)

    submit_buttom5 = customtkinter.CTkButton(new_filter_top,text='Salvar',command = create_new_filter)
    submit_buttom5.grid(row=8, column=1,padx=20, pady=(10,20), sticky='e')
    
    new_filter_top.mainloop()
    
def new_key():
    
    new_key_top = customtkinter.CTkToplevel(app)
    new_key_top.title('RewardEvents - Atalho')
    
    def create_new_key():
        
        title = redem_title4.get()
        time_press_again = time_press_entry.get()
        press_again = time_press_entry.get()
        command_event = command_entry.get()
        key1 = combobox1.get()
        key2 = combobox2.get()
        key3 = combobox3.get()
        key4 = combobox4.get()
        chat_response = chat_response_entry.get()
        user_level_check = user_level_switch.get()

        try:
            if chat_response is None:
                send_response = 0
            else:
                send_response = 1
                
            if user_level_check:
                user_level_data = "mod"
            else:
                user_level_data = ""
                
            old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
            new_data = json.load(old_data)

            new_data[title] = {'TYPE': 'KEYPRESS','press_again':press_again ,'send_response':send_response, 'chat_response':chat_response,
                                'COMMAND': command_event, 'TIME': time_press_again,'KEY1':key1, 'KEY2':key2, 'KEY3':key3, 'KEY4':key4}
            old_data.close()

            old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(new_data, old_data_write, indent = 4, ensure_ascii=False)
            
            old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
            new_data_command = json.load(old_data_command)

            new_data_command[command_event] = {'RECOMPENSA': title,'user_level': user_level_data}
            old_data.close()

            old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
            json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
            
            
            messagebox.showinfo("Sucesso",f"Evento de atalho no teclado '{title}' criado com sucesso!",parent=new_key_top)
        except:
            messagebox.showerror("Erro","Erro ao criar o evento.",parent=new_key_top)

    def update_titles_combox():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')
        
        
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox() 
    
    
    tittleredem4 = customtkinter.CTkLabel(new_key_top, text="Executar um atalho com recompensa", text_font=("default_theme","15"))
    tittleredem4.grid(row=0, column=0, columnspan=4, padx=20, pady=20,)

    redem_title_label4 = customtkinter.CTkLabel(new_key_top, text="Recompensa:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label4.grid(row=1,column=0, columnspan=2,pady=10,padx=20,sticky='W')

    redem_title4 = customtkinter.CTkComboBox(new_key_top,values=list(messages_combox),width=200)
    redem_title4.grid(row=1,column=2, columnspan=2, padx=10, pady=10)
    
    command_label = customtkinter.CTkLabel(new_key_top, text="Comando para o chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2,column=0, columnspan=2,pady=10,padx=20,sticky='W')

    command_entry = customtkinter.CTkEntry(new_key_top,width=200)
    command_entry.grid(row=2, column=2, columnspan=2, padx=10, pady=20)
    
    user_level_label = customtkinter.CTkLabel(new_key_top, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_switch = customtkinter.CTkSwitch(new_key_top, text=" ", text_font=("default_theme", "13"),)
    user_level_switch.grid(row=3, column=1,padx=20, pady=10)
    
    press_again_switch = customtkinter.CTkSwitch(new_key_top, text="Pressionar a tecla novamente depois do tempo ?", text_font=("default_theme", "13"),)
    press_again_switch.grid(row=4, column=0, columnspan=4, pady=10)
    
    time_press = customtkinter.CTkLabel(new_key_top, text="Tempo para pressionar novamente:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    time_press.grid(row=5,column=0, columnspan=2,pady=10,padx=20,sticky='W')

    time_press_entry = customtkinter.CTkEntry(new_key_top,width=200)
    time_press_entry.grid(row=5, column=2, columnspan=2,padx=10, pady=20)

    selectkeys = customtkinter.CTkLabel(new_key_top, text="Selecione as teclas:\n\n CUIDADO E ATENÇÃO!!", text_font=("default_theme","15"))
    selectkeys.grid(row=6, column=0, columnspan=4, padx=20, pady=20,)

    combobox1 = customtkinter.CTkComboBox(new_key_top,values=["ctrl","NONE"],width=100)
    combobox1.grid(row=7,column=0,padx=20, pady=10)

    combobox2 = customtkinter.CTkComboBox(new_key_top,values=["shift","alt","space","NONE"],width=100)
    combobox2.grid(row=7,column=1,padx=20, pady=10)

    combobox3 = customtkinter.CTkComboBox(new_key_top,values=["1","2","3","4","5","6","7","8","9","NONE"],width=100)
    combobox3.grid(row=7,column=2,padx=20, pady=10)

    combobox4 = customtkinter.CTkComboBox(new_key_top,width=100,
                                        values=["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","ç","z","x","c","v","b","n","m","NONE"])
    combobox4.grid(row=7,column=3,padx=20, pady=10)
    
    chat_response_label = customtkinter.CTkLabel(new_key_top,text="Resposta no chat (opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    chat_response_label.grid(row=8,column=0, columnspan=2, padx=20,pady=10, sticky='W')

    chat_response_entry = customtkinter.CTkEntry(new_key_top,width=200)
    chat_response_entry.grid(row=8,column=2, columnspan=2, padx=20, pady=10)

    submit_buttom6 = customtkinter.CTkButton(new_key_top,text='Salvar',command = create_new_key)
    submit_buttom6.grid(row=9, column=3,padx=20, pady=(10,30), sticky='e')
    
    new_key_top.mainloop()
    
def new_source():
    
    new_source_top = customtkinter.CTkToplevel(app)
    new_source_top.title('RewardEvents - Alternar Source')
    
    def create_new_source():
        
        title = redem_title5.get()
        source_name = obs_source_entry_source.get()
        time_showing = time_filter_entry_source.get()
        command_event = command_entry.get()
        chat_response = chat_response_entry.get()
        user_level_check = user_level_switch.get()
        
        if not [x for x in (title, source_name,time_showing) if x is None]:
            try:
                if chat_response is None:
                    send_response = 0
                else:
                    send_response = 1
                    
                if user_level_check:
                    user_level_data = "mod"
                else:
                    user_level_data = ""
                    
                old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                new_data = json.load(old_data)

                new_data[title] = {'TYPE': 'SOURCE','send_response':send_response, 'chat_response':chat_response,
                                   'COMMAND': command_event, 'SOURCENAME': source_name,'TIME':time_showing}
                old_data.close()

                old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                json.dump(new_data, old_data_write, indent = 4 ,ensure_ascii=False)
                old_data_write.close()
                
                old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)

                new_data_command[command_event] = {'RECOMPENSA': title,'user_level': user_level_data}
                old_data.close()

                old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
                
                messagebox.showinfo("Sucesso",f"Evento de fonte '{title}' criado com sucesso.",parent=new_source_top)
            except:
                messagebox.showerror("Erro","Erro ao criar o evento.",parent=new_source_top)
        else:
            messagebox.showerror("Erro","Preencha todos os campos.",parent=new_source_top)

    def update_titles_combox():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')
        
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox() 
    
    
    tittleredem5 = customtkinter.CTkLabel(new_source_top, text="Exibir e ocultar uma Fonte do obs com recompensa", text_font=("default_theme","15"))
    tittleredem5.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

    redem_title_label5 = customtkinter.CTkLabel(new_source_top, text="Recompensa:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label5.grid(row=1,column=0,pady=10,padx=20,sticky='W')

    redem_title5 = customtkinter.CTkComboBox(new_source_top,values=list(messages_combox),width=200)
    redem_title5.grid(row=1,column=1 ,padx=10, pady=10)
    
    command_label = customtkinter.CTkLabel(new_source_top, text="Comando para o chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2,column=0,pady=10,padx=20,sticky='W')

    command_entry = customtkinter.CTkEntry(new_source_top,width=200)
    command_entry.grid(row=2, column=1,padx=10, pady=10)
    
    user_level_label = customtkinter.CTkLabel(new_source_top, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_switch = customtkinter.CTkSwitch(new_source_top, text=" ", text_font=("default_theme", "13"),)
    user_level_switch.grid(row=3, column=1,padx=20, pady=10)

    obs_source_label_source = customtkinter.CTkLabel(new_source_top,text="Nome da fonte no OBS:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    obs_source_label_source.grid(row=4,column=0, padx=20,pady=10, sticky='W')

    obs_source_entry_source = customtkinter.CTkEntry(new_source_top,width=200)
    obs_source_entry_source.grid(row=4,column=1, padx=20, pady=10)

    time_filter_label = customtkinter.CTkLabel(new_source_top,text="Tempo exibindo:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    time_filter_label.grid(row=5,column=0, padx=20,pady=10, sticky='W')

    time_filter_entry_source = customtkinter.CTkEntry(new_source_top,width=200)
    time_filter_entry_source.grid(row=5,column=1, padx=20, pady=10)
    
    chat_response_label = customtkinter.CTkLabel(new_source_top,text="Resposta no chat (opcional):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    chat_response_label.grid(row=6,column=0, padx=20,pady=10, sticky='W')

    chat_response_entry = customtkinter.CTkEntry(new_source_top,width=200)
    chat_response_entry.grid(row=6,column=1, padx=20, pady=10)

    submit_buttom6 = customtkinter.CTkButton(new_source_top,text='Salvar',command = create_new_source)
    submit_buttom6.grid(row=7, column=1,padx=20, pady=(10,20), sticky='e')

    new_source_top.mainloop()
   
def new_clip():
    
    new_clip_top = customtkinter.CTkToplevel(app)
    new_clip_top.title('RewardEvents - Criar um clip')
    
    def create_new_clip():
        
        title = redem_title6.get()
        command_event = command_entry.get()
        user_level_check = user_level_switch.get()

        if title:
            try:
                if user_level_check:
                    
                    user_level_data = "mod"
                    
                else:
                    user_level_data = ""
                    
                old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                new_data = json.load(old_data)

                new_data[title] = {'TYPE': 'CLIP','COMMAND': command_event,}
                old_data.close()

                old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)
                
                old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)

                new_data_command[command_event] = {'RECOMPENSA': title,'user_level': user_level_data}
                old_data.close()

                old_data_write_command = open('src/config/commands.json' , 'w') 
                json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                
                messagebox.showinfo("Sucesso",f"Evento de fonte '{title}' criado com sucesso.",parent=new_clip_top)
            except:
                messagebox.showerror("Erro","Erro ao criar o evento.",parent=new_clip_top)
        else:
            messagebox.showerror("Erro","Preencha o titulo.",parent=new_clip_top)

    def update_titles_combox():
        
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')
        
        list_titles = []
        path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
        path = json.load(path_file)
        list_rewards = twitch.get_custom_reward(broadcaster_id = USERID)
        for indx in list_rewards['data'][0:] :
            
            if indx['title'] not in path:   
                list_titles.append(indx['title'])

        return list_titles
    
    messages_combox = update_titles_combox()  

    tittleredem6 = customtkinter.CTkLabel(new_clip_top, text="Recompensa para criar clips de 30 segundos", text_font=("default_theme","15"))
    tittleredem6.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

    redem_title_label6 = customtkinter.CTkLabel(new_clip_top, text="Recompensa:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    redem_title_label6.grid(row=1,column=0,pady=20,padx=20,sticky='W')

    redem_title6 = customtkinter.CTkComboBox(new_clip_top,values=list(messages_combox),width=200)
    redem_title6.grid(row=1,column=1 ,padx=20, pady=20)
    
    command_label = customtkinter.CTkLabel(new_clip_top, text="Comando para o chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label.grid(row=2,column=0,pady=20,padx=20,sticky='W')

    command_entry = customtkinter.CTkEntry(new_clip_top,width=200)
    command_entry.grid(row=2, column=1, pady=20,padx=20)
    
    user_level_label = customtkinter.CTkLabel(new_clip_top, text="Somente moderador pode usar o comando ?", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
    
    user_level_switch = customtkinter.CTkSwitch(new_clip_top, text=" ", text_font=("default_theme", "13"),)
    user_level_switch.grid(row=3, column=1,padx=20, pady=10)

    submit_buttom7 = customtkinter.CTkButton(new_clip_top,text='Salvar',command = create_new_clip)
    submit_buttom7.grid(row=4, column=1,padx=20, pady=20, sticky='e')

    new_clip_top.mainloop()

def create_event():
    
    events_receive = {
        'Reproduzir Audio' : new_sound,
        'Texto falado google' : new_tts,
        'Mudar cena OBS' : new_scene,
        'Exibir/Ocultar Filtro OBS' : new_filter,
        'Exibir/Ocultar Fonte OBS' : new_source,
        'Atalho no teclado' : new_key,
        'Resposta no chat' : new_message,
        'Criar um Clip': new_clip
    }
    
    value_combox = events_combox.get()
    
    if value_combox in events_receive:
        events_receive[value_combox]()
       
def del_event():
    
    del_event_top = customtkinter.CTkToplevel(app)
    del_event_top.title('RewardEvents - Excluir um evento')
    
    def del_event_confirm():
        
        combox_key = combobox_events.get()
        
        old_data_event = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
        new_data_event = json.load(old_data_event)
        command_event_del_data = new_data_event[combox_key]['COMMAND']
        
        try:
            
            old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
            new_data = json.load(old_data)

            del new_data[combox_key]
            old_data.close()

            old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
            json.dump(new_data, old_data_write, indent = 4, ensure_ascii=False)
            old_data_write.close()
            
            
            if command_event_del_data:
                
                try:
        
                    old_data_commands_events = open('src/config/commands.json' , 'r', encoding='utf-8') 
                    new_data_commands_events = json.load(old_data_commands_events)

                    del new_data_commands_events[command_event_del_data]
                    old_data_commands_events.close()

                    old_data_commands_events_write = open('src/config/commands.json' , 'w', encoding='utf-8') 
                    json.dump(new_data_commands_events, old_data_commands_events_write, indent = 4, ensure_ascii=False)
                    old_data_commands_events_write.close()
                    
                except:
                    pass
            
            messagebox.showinfo("Sucesso!",f"Evento '{combox_key}' excluido com sucesso!",parent=del_event_top)
        except:
            messagebox.showerror("Erro!",f"Erro ao excluir o evento!",parent=del_event_top)
            
        var_events = customtkinter.StringVar(value='Selecione uma recompensa')
        
        events_data_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
        events_data = json.load(events_data_file)
        combobox_events.configure(values=list(events_data.keys()),variable=var_events)
    
    events_data_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
    events_data = json.load(events_data_file)

    var_events = customtkinter.StringVar(value='Selecione uma recompensa')
    
    tittleredem6 = customtkinter.CTkLabel(del_event_top, text="Excluir um evento de recompensa", text_font=("default_theme","15"))
    tittleredem6.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)
    
    tittleredem7 = customtkinter.CTkLabel(del_event_top, text="Selecione a recompensa abaixo para excluir\n  evento associado a ela", text_font=("default_theme","15"))
    tittleredem7.grid(row=0, column=0, columnspan=2, padx=20, pady=(30,10))
    
    combobox_events = customtkinter.CTkComboBox(del_event_top,values=list(events_data.keys()),variable=var_events,width=300)
    combobox_events.grid(row=4,column=0, columnspan=2,padx=10, pady=20)

    submit_buttom7 = customtkinter.CTkButton(del_event_top,text='Excluir',command = del_event_confirm)
    submit_buttom7.grid(row=5, column=1,padx=20, pady=20)

    del_event_top.mainloop()

def new_simple_command():
    
    new_simple = customtkinter.CTkToplevel(app)
    new_simple.title('RewardEvents - Comando simples')
    
    def create_message():
    
        user_level_check = user_level_Switch_new_simple.get()
        message = message_entry_new_simple.get()
        command_event = command_entry_new_simple.get()

        if not [x for x in (message) if x is None]:
            try:
                
                old_data_command = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)
                
                if user_level_check:
                    user_level_data = "mod"
                else:
                    user_level_data = ""
                    
                new_data_command[command_event] = {'response': message, 'user_level': user_level_data}
                
                old_data_write_command = open('src/config/simple_commands.json' , 'w', encoding='utf-8') 
                json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
                
                
                messagebox.showinfo("Sucesso!","Evento de mensagem criado com sucesso!",parent=new_simple)
                
            except:
                messagebox.showerror("Erro","Erro ao criar o evento de mensagem.",parent=new_simple)
        else:
            messagebox.showerror("Erro","Preencha todos os campos.",parent=new_simple)
         
            
    tittleredem2_new_simple = customtkinter.CTkLabel(new_simple, text="Resposta no chat por comando", text_font=("default_theme","15"))
    tittleredem2_new_simple.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

    command_label_new_simple = customtkinter.CTkLabel(new_simple, text="Comando (sem '!'):", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_label_new_simple.grid(row=2,column=0,pady=10,padx=10,sticky='W')
    
    command_entry_new_simple = customtkinter.CTkEntry(new_simple,width=200)
    command_entry_new_simple.grid(row=2, column=1,padx=10, pady=10)

    message_label_new_simple = customtkinter.CTkLabel(new_simple,text="Mensagem no Chat:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    message_label_new_simple.grid(row=3,column=0, padx=10,pady=10, sticky='W')

    message_entry_new_simple = customtkinter.CTkEntry(new_simple,width=200)
    message_entry_new_simple.grid(row=3,column=1, padx=10, pady=10)
    
    user_level_Switch_new_simple_label = customtkinter.CTkLabel(new_simple, text="Somente moderador ?", text_font=("default_theme","13"))
    user_level_Switch_new_simple_label.grid(row=4, column=0,  padx=10, pady=10, sticky='W')
    
    user_level_Switch_new_simple = customtkinter.CTkSwitch(new_simple, text="", text_font=("default_theme", "13"),)
    user_level_Switch_new_simple.grid(row=4, column=1, padx=10, pady=10, sticky='e')

    submit_buttom4_new_simple = customtkinter.CTkButton(new_simple,text='Salvar',command = create_message)
    submit_buttom4_new_simple.grid(row=5, column=1,padx=10, pady=(10,20), sticky='e')
    
    new_simple.mainloop()

def del_simple_command():
    
    del_simple = customtkinter.CTkToplevel(app)
    del_simple.title('RewardEvents - Excluir comando')
    
    def del_command_select():
    
        command_combox_key = combobox_commands.get()
        
        try:
            old_data = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
            new_data = json.load(old_data)

            del new_data[command_combox_key]
            old_data.close()

            old_data_write = open('src/config/simple_commands.json' , 'w', encoding='utf-8') 
            json.dump(new_data, old_data_write, indent = 4, ensure_ascii=False)
            old_data_write.close()
            
            messagebox.showinfo("Sucesso!",f"Comando '{command_combox_key}' excluido!",parent=del_simple)
      
        except:
            messagebox.showerror("Erro!",f"Erro ao excluir o comando!",parent=del_simple)
        
        var_commands = customtkinter.StringVar(value='Selecione um comando')
        commands_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
        commands_list = json.load(commands_data_file)
        combobox_commands.configure(values=list(commands_list.keys()),variable=var_commands)
         
    commands_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
    commands_list = json.load(commands_data_file)

    var_commands = customtkinter.StringVar(value='Selecione um comando')
    
    combobox_commands_label = customtkinter.CTkLabel(del_simple, text="Selecione o comando:", text_font=("default_theme","15"))
    combobox_commands_label.grid(row=1, column=0,columnspan=2, padx=20, pady=(30,10))
    
    combobox_commands = customtkinter.CTkComboBox(del_simple,values=list(commands_list.keys()),variable=var_commands,width=200)
    combobox_commands.grid(row=2,column=0,padx=20,columnspan=2, pady=20)

    submit_buttom7 = customtkinter.CTkButton(del_simple,text='Excluir',command = del_command_select)
    submit_buttom7.grid(row=3, column=1,padx=20, pady=20, sticky='e')
    
    del_simple.mainloop()

def edit_simple_command():
    
    edit_simple_command = customtkinter.CTkToplevel(app)
    edit_simple_command.title('RewardEvents - Editar um comando')
    
    def select_command_edit(message_edit):
        global command_edit_value
        
        command_edit_value = message_edit
        
        command_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
        command_data = json.load(command_data_file)
        
        command_message = command_data[message_edit]['response']
        
        edit_command_var = customtkinter.StringVar(value=f"{command_message}")
        edit_command_entry.configure(textvariable=edit_command_var)   
        
    def edit_command_confirm():
        
        edit_message_value = edit_command_entry.get()
        user_level_check = user_level_edit.get()
        
        command_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
        command_data = json.load(command_data_file)
        
        command_data[command_edit_value]['response'] = edit_message_value
        
        if user_level_check:
            user_level_data = "mod"
        else:
            user_level_data = ""
            
        command_data[command_edit_value]['user_level'] = user_level_data
                
        command_data_file.close()
        
        try:
            old_data_write = open('src/config/simple_commands.json' , 'w', encoding='utf-8') 
            json.dump(command_data, old_data_write, indent = 4, ensure_ascii=False)
            old_data_write.close()
            
            commands_list = update_edit_combox()
            message_edit_val = customtkinter.StringVar(value="Selecione uma mensagem")
            
            combobox_message.configure(variable=message_edit_val,values=list(commands_list.keys()))
            
            messagebox.showinfo('Sucesso','Comando editado', parent=edit_simple_command)
        except:
            messagebox.showerror('Erro','Não foi possível editar o comando', parent=edit_simple_command)
            
    def update_edit_combox():
        
        commands_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
        commands_list = json.load(commands_data_file)
    
        return commands_list
    
    
    commands_list = update_edit_combox()

    var_edit_commands = customtkinter.StringVar(value='Selecione um comando')
    
    title_command_edit = customtkinter.CTkLabel(edit_simple_command, text="Editar comando", text_font=("default_theme","13"))
    title_command_edit.grid(row=0, column=0 ,padx=20, pady=10)
    
    combobox_message = customtkinter.CTkComboBox(edit_simple_command, values=list(commands_list.keys()),
                                                 variable=var_edit_commands, width=300, command = select_command_edit)
    
    combobox_message.grid(row=1, column=0, padx=20, pady=10)
    
    edit_command_entry = customtkinter.CTkEntry(edit_simple_command, width=300)
    edit_command_entry.grid(row=2, column=0, padx=20, pady=(15, 5))
    
    user_level_edit = customtkinter.CTkSwitch(edit_simple_command, 
                                                           text="Somente moderador pode usar o comando ?", 
                                                           text_font=("default_theme", "13"),)
    user_level_edit.grid(row=3, column=0, columnspan=2, pady=10)

    del_command_buttom = customtkinter.CTkButton(edit_simple_command, text='Salvar', command = edit_command_confirm)
    del_command_buttom.grid(row=4, column=1, padx=20, pady=(20,60), sticky='e')
    
    edit_simple_command.mainloop()   

def edit_delay_commands():
    
    edit_delay_command = customtkinter.CTkToplevel(app)
    edit_delay_command.title('RewardEvents - Editar delay')
        
    def edit_delay_confirm():
        
        edit_delay_command_value = edit_delay_entry.get()
        
        if not edit_delay_command_value is None:
            
            if edit_delay_command_value.isnumeric():
                try:
                    time_delay_file = open('src/config/prefix_commands.json')
                    time_delay_data = json.load(time_delay_file)

                    time_delay_data['delay_config'] = edit_delay_command_value
                    time_delay_file.close()
                    
                    time_delay_write = open('src/config/prefix_commands.json' , 'w', encoding='utf-8') 
                    json.dump(time_delay_data, time_delay_write, indent = 4, ensure_ascii=False)
                    time_delay_write.close()
                    
                    messagebox.showinfo('Sucesso','Delay salvo', parent=edit_delay_command)
                except:
                    messagebox.showerror('Erro','Não foi possível editar o delay', parent=edit_delay_command)
            else:
                messagebox.showerror('Erro','O delay deve ser um numero.', parent=edit_delay_command)
        else:
            messagebox.showerror('Erro','O delay não deve ser um valor vazio', parent=edit_delay_command)
                       
    def edit_delay_tts_confirm():
        
        edit_tts_value = edit_delay_tts_entry.get()
        
        if not edit_tts_value is None:
            
            if edit_tts_value.isnumeric():
                
                try:
                    time_delay_file = open('src/config/prefix_tts.json')
                    time_delay_data = json.load(time_delay_file)

                    time_delay_data['delay_config'] = edit_tts_value
                    time_delay_file.close()
                    
                    time_delay_write = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
                    json.dump(time_delay_data, time_delay_write, indent = 4, ensure_ascii=False)
                    time_delay_write.close()
                    
                    messagebox.showinfo('Sucesso','Delay salvo', parent=edit_delay_command)
                except:
                    messagebox.showerror('Erro','Não foi possível editar o delay', parent=edit_delay_command)
            else:
                messagebox.showerror('Erro','O delay deve ser um numero.', parent=edit_delay_command)
        else:
            messagebox.showerror('Erro','O delay não deve ser um valor vazio', parent=edit_delay_command)
            
    def delay_atual():
        
        time_delay_file = open('src/config/prefix_commands.json')
        time_delay_data = json.load(time_delay_file)
        
        time_delay_tts_file = open('src/config/prefix_tts.json')
        time_delay_tts_data = json.load(time_delay_tts_file)
        
        edit_delay_entry_var = customtkinter.StringVar(value=f"{time_delay_data['delay_config']}")
        edit_delay_entry.configure(textvariable=edit_delay_entry_var)
        
        edit_delay_tts_entry_var = customtkinter.StringVar(value=f"{time_delay_tts_data['delay_config']}")
        edit_delay_tts_entry.configure(textvariable=edit_delay_tts_entry_var)
    
    title_delay_edit = customtkinter.CTkLabel(edit_delay_command, text="Editar delay para comandos gerais", text_font=("default_theme","13"))
    title_delay_edit.grid(row=0, column=0 ,padx=20, pady=10)
    
    edit_delay_entry = customtkinter.CTkEntry(edit_delay_command, width=300)
    edit_delay_entry.grid(row=1, column=0, padx=20, pady=(15, 5))
    
    save_delay_buttom = customtkinter.CTkButton(edit_delay_command, text='Salvar', command = edit_delay_confirm)
    save_delay_buttom.grid(row=2, column=0, padx=20, pady=(20,60), sticky='e')
    
    title_delay_tts_edit = customtkinter.CTkLabel(edit_delay_command, text="Editar delay para !tts", text_font=("default_theme","13"))
    title_delay_tts_edit.grid(row=3, column=0 ,padx=20, pady=10)
    
    edit_delay_tts_entry = customtkinter.CTkEntry(edit_delay_command, width=300)
    edit_delay_tts_entry.grid(row=4, column=0, padx=20, pady=(15, 5)) 

    save_delay_tts_buttom = customtkinter.CTkButton(edit_delay_command, text='Salvar', command = edit_delay_tts_confirm)
    save_delay_tts_buttom.grid(row=5, column=0, padx=20, pady=(20,60), sticky='e')
    
    delay_atual()
    
    edit_delay_command.mainloop()   
                         
def config_obs_conn_top():
    
    top_config_obs_conn = customtkinter.CTkToplevel(app)
    top_config_obs_conn.title('RewardEvents - Configurações de conexão com o OBS')    

    def salvar_obs_conn():
        
        auto_connect_value = auto_conn_obs.get()
        obs_host_data = 'localhost'
        obs_port_data = obs_port_entry.get()
        obs_password_data = obs_password_entry.get()

        if not [x for x in (obs_password_data, obs_port_data) if x is None]:
            
            data = {'OBS_HOST': obs_host_data, 'OBS_PORT': obs_port_data, 'OBS_PASSWORD': obs_password_data,
                    'OBS_AUTO_CON': auto_connect_value,}

            out_file = open("src/config/obs.json", "w", encoding='utf-8')
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()

            out_file_obs_atual = open("src/config/obs.json", "w", encoding='utf-8')
            data_obs_atual = json.load(out_file_obs_atual)
            
            obs_host_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_HOST']}")
            obs_port_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_PORT']}")
            obs_password_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_PASSWORD']}")
            
            obs_host_entry.configure(textvariable=obs_host_var)
            obs_port_entry.configure(textvariable=obs_port_var)
            obs_password_entry.configure(textvariable=obs_password_var)
            

            messagebox.showinfo('Config', 'Configuração salva com sucesso!',parent=top_config_obs_conn)

        else:
            messagebox.showerror('Config ERRO!', 'PREENCHA TODOS OS CAMPOS!',parent=top_config_obs_conn)
            
    
    def get_obs_atual_con():
            
        out_file_obs_atual = open("src/config/obs.json")
        data_obs_atual = json.load(out_file_obs_atual)
        

        try:
            
            obs_host_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_HOST']}")
            obs_port_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_PORT']}")
            obs_password_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_PASSWORD']}")
            
            obs_host_entry.configure(textvariable=obs_host_var)
            obs_port_entry.configure(textvariable=obs_port_var)
            obs_password_entry.configure(textvariable=obs_password_var)
            
        except:
            pass
            
            
    obs_host_var = customtkinter.StringVar(value=f"Carregando configuração")
        
    obs_port_var = customtkinter.StringVar(value=f"Carregando configuração")
    obs_password_var = customtkinter.StringVar(value=f"Carregando configuração")
                
    title_obs_confg = customtkinter.CTkLabel(top_config_obs_conn,text="Configurações do OBS Para Websocket",
                                                text_font=("default_theme", "13"))

    title_obs_confg.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

    obs_host_label = customtkinter.CTkLabel(top_config_obs_conn, text="OBS HOST:", text_font=("default_theme", "11"), anchor="w")
    obs_host_label.grid(row=1, column=0, padx=20, pady=(15, 5), sticky='W')

    obs_host_entry = customtkinter.CTkEntry(top_config_obs_conn, width=200, textvariable=obs_host_var)
    obs_host_entry.grid(row=1, column=1, padx=20, pady=(15, 5))

    obs_port_label = customtkinter.CTkLabel(top_config_obs_conn, text="OBS PORT:", text_font=("default_theme", "11"), anchor="w")
    obs_port_label.grid(row=2, column=0, padx=20, pady=(5, 5), sticky='W')

    obs_port_entry = customtkinter.CTkEntry(top_config_obs_conn, width=200, textvariable=obs_port_var)
    obs_port_entry.grid(row=2, column=1, padx=20, pady=(5, 5))

    obs_password_label = customtkinter.CTkLabel(top_config_obs_conn, text="OBS PASSWORD: ", text_font=("default_theme", "11"), anchor="w",)
    obs_password_label.grid(row=3, column=0, padx=20, pady=(5, 15), sticky='W')

    obs_password_entry = customtkinter.CTkEntry(top_config_obs_conn, width=200, textvariable=obs_password_var)
    obs_password_entry.grid(row=3, column=1, padx=20, pady=(5, 15))

    auto_conn_obs_label = customtkinter.CTkLabel(top_config_obs_conn, text="Conectar automaticamente ao iniciar: ", text_font=("default_theme", "11"), anchor="w",)
    auto_conn_obs_label.grid(row=4, column=0,padx=20, pady=(5, 15) , sticky='W')
    
    auto_conn_obs = customtkinter.CTkSwitch(top_config_obs_conn, text=" ", text_font=("default_theme", "13"),)
    auto_conn_obs.grid(row=4, column=1,padx=20, pady=(5, 15))

    save_config_obs = customtkinter.CTkButton(top_config_obs_conn, text='Salvar', command=salvar_obs_conn)
    save_config_obs.grid(row=6, column=1, padx=20, pady=10, sticky='e')
    
    get_obs_atual_con()
    
    top_config_obs_conn.mainloop()
    
def config_obs_not_top():
    
    top_config_obs_notifc = customtkinter.CTkToplevel(app)
    top_config_obs_notifc.title('RewardEvents - Configurações de notificações no OBS')
    
    def salvar_conf_not():
    
        group_name_value = group_name_entry.get()
        text_name_value = text_name_entry.get()
        text_user_name_value = text_user_name_entry.get()
        
        if not [x for x in (group_name_value, text_name_value, text_user_name_value) if x is None]:
                        
            data = {'TEXT_TITLE_REDEEM': text_name_value, 'TEXT_USER_REDEM': text_user_name_value, 'NOTF_GROUP_OBS': group_name_value,}

            out_file = open("src/config/notfic.json", "w", encoding='utf-8')
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()

            messagebox.showinfo('Config', 'Configuração salva com sucesso!',parent=top_config_obs_notifc)
        else:
            messagebox.showerror('Config ERRO!', 'PREENCHA TODOS OS CAMPOS!',parent=top_config_obs_notifc)
            
    def get_obs_confg_atual():
        
        file_obs_atual_source = open("src/config/notfic.json")
        data_obs_atual_source = json.load(file_obs_atual_source)
        
        try:
            group_name_var = customtkinter.StringVar(value=f"{data_obs_atual_source['TEXT_TITLE_REDEEM']}")
            text_name_var = customtkinter.StringVar(value=f"{data_obs_atual_source['TEXT_USER_REDEM']}")
            text_user_name_var = customtkinter.StringVar(value=f"{data_obs_atual_source['NOTF_GROUP_OBS']}")
            
            group_name_entry.configure(textvariable=group_name_var)
            text_name_entry.configure(textvariable=text_name_var)
            text_user_name_entry.configure(textvariable=text_user_name_var)
            
        except:
            pass
            
        
    title_notif = customtkinter.CTkLabel(top_config_obs_notifc, text="Configuração de notificações No OBS", text_font=("default_theme", "13"))
    title_notif.grid(row=7, column=0, columnspan=2, padx=20, pady=(25,15))

    group_name = customtkinter.CTkLabel(top_config_obs_notifc, text="Nome do grupo:", text_font=("default_theme", "11"), anchor="w")
    group_name.grid(row=8, column=0, padx=20, pady=(15, 5), sticky='W')

    group_name_entry = customtkinter.CTkEntry(top_config_obs_notifc, width=200)
    group_name_entry.grid(row=8, column=1, padx=20, pady=(20, 5))

    text_name = customtkinter.CTkLabel(top_config_obs_notifc, text="Titulo da recompensa: ", text_font=("default_theme", "11"), anchor="w")
    text_name.grid(row=9, column=0, padx=20, pady=(5, 5), sticky='W')

    text_name_entry = customtkinter.CTkEntry(top_config_obs_notifc, width=200)
    text_name_entry.grid(row=9, column=1, padx=20, pady=(5, 5))

    text_user_name = customtkinter.CTkLabel(top_config_obs_notifc, text="Usuário que resgatou: ", text_font=("default_theme", "11"), anchor="w")
    text_user_name.grid(row=10, column=0, padx=20, pady=(5, 15), sticky='W')

    text_user_name_entry = customtkinter.CTkEntry(top_config_obs_notifc, width=200)
    text_user_name_entry.grid(row=10, column=1, padx=20, pady=(5, 15))

    salvar = customtkinter.CTkButton(top_config_obs_notifc, text='Salvar', command=salvar_conf_not)
    salvar.grid(row=11, column=1,padx=20, pady=(10,10), sticky='e')
    
    get_obs_confg_atual()
    
    top_config_obs_notifc.mainloop()
  
def config_messages_top():
    
    top_config_messages = customtkinter.CTkToplevel(app)
    top_config_messages.title('RewardEvents - Configurações de mensagens')
    
    def timer_status():
    
        status_value = timer_status_value.get()
        
        timer_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        timer_data = json.load(timer_data_file)
        
        timer_data['STATUS_TIMER'] = status_value
        timer_data_file.close()
        
        old_data_write = open('src/config/prefix_commands.json' , 'w', encoding="utf-8") 
        json.dump(timer_data, old_data_write, indent = 4,ensure_ascii=False)
        old_data_write.close()    

    def tts_status():

        tts_status_value = tts_option.get()
        
        tts_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        tts_data = json.load(tts_data_file)
        
        tts_data['STATUS_TTS'] = tts_status_value
        tts_data_file.close()
        
        old_data_write = open('src/config/prefix_commands.json' , 'w', encoding="utf-8") 
        json.dump(tts_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()
        
    def command_status():

        command_status_value = commands_option.get()
        
        command_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        command_data = json.load(command_data_file)
        
        command_data['STATUS_COMMANDS'] = command_status_value
        command_data_file.close()
        
        old_data_write = open('src/config/prefix_commands.json' , 'w', encoding="utf-8") 
        json.dump(command_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()

    def response_status():

        response_status_value = response_option.get()
        
        response_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        response_data = json.load(response_data_file)
        
        response_data['STATUS_RESPONSE'] = response_status_value
        response_data_file.close()
        
        old_data_write = open('src/config/prefix_commands.json' , 'w', encoding="utf-8") 
        json.dump(response_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()

    def clip_status():

        clip_status_value = clip_option.get()
        
        clip_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        clip_data = json.load(clip_data_file)
        
        clip_data['STATUS_CLIP'] = clip_status_value
        clip_data_file.close()
        
        old_data_write = open('src/config/prefix_commands.json' , 'w', encoding="utf-8") 
        json.dump(clip_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()

    def user_error_status():

        user_error_status_value = user_error_option.get()
        
        user_error_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        user_error_data = json.load(user_error_data_file)
        
        user_error_data['STATUS_ERROR_USER'] = user_error_status_value
        user_error_data_file.close()
        
        old_data_write = open('src/config/prefix_commands.json' , 'w', encoding="utf-8") 
        json.dump(user_error_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()
    
    def time_error_status():

        time_status_value = time_option.get()
        
        time_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        time_data = json.load(time_data_file)
        
        time_data['STATUS_ERROR_TIME'] = time_status_value
        time_data_file.close()
        
        old_data_write = open('src/config/prefix_commands.json' , 'w', encoding="utf-8") 
        json.dump(time_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()
    
    def get_all_status_value():
        
        status_data_file = open('src/config/prefix_commands.json' , 'r', encoding="utf-8") 
        status_data = json.load(status_data_file)
        
        status_error_time = status_data['STATUS_ERROR_TIME']
        status_error_user = status_data['STATUS_ERROR_USER']
        status_response = status_data['STATUS_RESPONSE']
        status_clip = status_data['STATUS_CLIP']
        status_tts = status_data['STATUS_TTS']
        status_timer = status_data['STATUS_TIMER']
        status_commands = status_data['STATUS_COMMANDS']
        
        if status_tts == 1:
            tts_option.select()
            
        if status_commands == 1:
            commands_option.select()
            
        if status_response == 1:
            response_option.select()
            
        if status_error_time == 1:
            time_option.select()
            
        if status_clip == 1:
            clip_option.select()
            
        if status_error_user == 1:
            user_error_option.select()
            
        if status_timer == 1:
            timer_status_value.select()


    title_status = customtkinter.CTkLabel(top_config_messages, text='Status de comandos e mensagens/respostas', text_font=("default_theme","15"))
    title_status.grid(row=1, column=0, columnspan=2, padx=20, pady=(20,30))

    tts_option_label = customtkinter.CTkLabel(top_config_messages, text='Habilitar comando !tts ?', text_font=("default_theme","13"))
    tts_option_label.grid(row=2, column=0, padx=20, pady=5, sticky='w')

    tts_option = customtkinter.CTkSwitch(top_config_messages, text=" ", command=tts_status)
    tts_option.grid(row=2, column=1, padx=20, pady=5, sticky='e')

    commands_option_label = customtkinter.CTkLabel(top_config_messages, text='Habilitar comandos ?', text_font=("default_theme","13"))
    commands_option_label.grid(row=3, column=0, padx=20, pady=5, sticky='w')

    commands_option = customtkinter.CTkSwitch(top_config_messages, text=" ",command=command_status)
    commands_option.grid(row=3, column=1, padx=20, pady=5, sticky='e')

    response_option_label = customtkinter.CTkLabel(top_config_messages, text='Ativar respostas de comandos ?', text_font=("default_theme","13"))
    response_option_label.grid(row=4, column=0, padx=20, pady=5,sticky='w')

    response_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=response_status)
    response_option.grid(row=4, column=1, padx=20, pady=5,sticky='e')

    time_option_label = customtkinter.CTkLabel(top_config_messages, text='Exibir delay para comandos ?', text_font=("default_theme","13"))
    time_option_label.grid(row=5, column=0, padx=20, pady=5,sticky='w')

    time_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=time_error_status)
    time_option.grid(row=5, column=1, padx=20, pady=5,sticky='e')

    clip_option_label = customtkinter.CTkLabel(top_config_messages, text='Exibir confirmações/erros de clipes ?', text_font=("default_theme","13"))
    clip_option_label.grid(row=6, column=0, padx=20, pady=5,sticky='w')

    clip_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=clip_status)
    clip_option.grid(row=6, column=1, padx=20, pady=5,sticky='e')

    user_error_option_label = customtkinter.CTkLabel(top_config_messages, text='Exibir erro de permissão para comandos ?', text_font=("default_theme","13"))
    user_error_option_label.grid(row=7,column=0, padx=20, pady=5,sticky='w')

    user_error_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=user_error_status)
    user_error_option.grid(row=7, column=1, padx=20, pady=5, sticky='e')
    
    timer_status_value_label = customtkinter.CTkLabel(top_config_messages,text="Ativar Timer ?", text_font=("default_theme","13"))
    timer_status_value_label.grid(row=8, column=0, pady=(5,20),sticky='w')

    timer_status_value = customtkinter.CTkSwitch(top_config_messages,text=" ",command=timer_status)
    timer_status_value.grid(row=8, column=1, padx=20, pady=(5,20), sticky='e')
    
    get_all_status_value()
    
    top_config_messages.mainloop()
       
def clear_data():
    ask = messagebox.askyesno('Atenção',
                              'Atenção\n\n\nVocê irá limpar os seus dados de conexão configuração e licença\nsendo '
                              'necessário executar o setup\nnovamente.\n\nContinuar ?')
    if ask == 'yes':
        data = {'USERNAME': '', 'USERID': '', 'TOKEN': '', 'TOKENBOT': '', 'BOTUSERNAME': ''}

        out_file = open("src/auth/auth.json", "w", encoding='utf-8')
        json.dump(data, out_file, indent=6,ensure_ascii=False)
        out_file.close()

        data_obs = {'OBS_HOST': '', 'OBS_PORT': '', 'OBS_PASSWORD': '', 'OBS_AUTO_CON': ''}

        out_file = open("src/config/obs.json", "w", encoding='utf-8')
        json.dump(data_obs, out_file, indent=6,ensure_ascii=False)
        out_file.close()
        
        close()
        
def self_clip():

    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
    
    url = "https://api.twitch.tv/helix/clips?broadcaster_id=" + USERID

    headers = CaseInsensitiveDict()
    headers["Authorization"] = 'Bearer ' + TOKEN
    headers["Client-Id"] = apitoken.CLIENTID
    headers["Content-Length"] = "0"

    resp = req.post(url, headers=headers)
    response_clip = resp.json()
    
    try:
        response_error = 'None'
        response_create = response_clip['data'][0]['id']
        
        send_message(f"/me Um novo clip foi criado, confira! https://clips.twitch.tv/{response_create}",'CLIP')
        
    except:
        response_error = response_clip['message']

        if response_error:
            send_message('/me Erro ao criar o clip','CLIP')

def new_timer():
    
    new_timer_top = customtkinter.CTkToplevel(app)
    new_timer_top.title('RewardEvents - Gerenciar Timer')
    
    def create_new_timer():
        
        new_message_timer = message_timer_entry.get()
        
        if new_message_timer:
        
            timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
            timer_data = json.load(timer_data_file)
            
            timer_message = timer_data['TIMERMESSAGE']['MESSAGES']
            
            qnt = len(timer_message) + 1
            int_qnt = int(qnt)
            
            
            timer_data['TIMERMESSAGE']['MESSAGES'][int_qnt] = new_message_timer
            timer_data_file.close()
            
            try:
                old_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
                json.dump(timer_data, old_data_write, indent = 4,ensure_ascii=False)
                old_data_write.close()
                
                messagebox.showinfo('Sucesso','Timer Criado',parent=new_timer_top)
            except:
                messagebox.showerror('Erro','Erro ao criar o timer',parent=new_timer_top)
        else:
            messagebox.showerror('Erro','Não é possivel criar um timer vazio',parent=new_timer_top)
    
    title_timer = customtkinter.CTkLabel(new_timer_top, text="Criar uma mensagem automatica", text_font=("default_theme","15"))
    title_timer.grid(row=0, column=0,columnspan=2, padx=20, pady=10,)

    message_timer_label = customtkinter.CTkLabel(new_timer_top, text="Mensagem:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    message_timer_label.grid(row=2,column=0, pady=10,padx=20,sticky='w')

    message_timer_entry = customtkinter.CTkEntry(new_timer_top,width=300)
    message_timer_entry.grid(row=2, column=1, padx=10, pady=20)
    
    add_message_buttom = customtkinter.CTkButton(new_timer_top,text='Adicionar',command = create_new_timer)
    add_message_buttom.grid(row=3, column=1, padx=10,pady=(10,20),sticky='e')

    new_timer_top.mainloop()

def timer_interval():
        
    interval_timer_top = customtkinter.CTkToplevel(app)
    interval_timer_top.title('RewardEvents - Alterar intervalo')
    
    def timer_time_change():
        
        value_max = timer_max_interval_entry.get()
        value_min = timer_min_interval_entry.get()
        
        timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
        timer_data = json.load(timer_data_file)
        
        timer_data['TIMERMESSAGE']['TIME'] = int(value_min)
        timer_data['TIMERMESSAGE']['TIME_MAX'] = int(value_max)
        
        timer_data_file.close()
        
        try:
            old_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
            json.dump(timer_data, old_data_write, indent = 4, ensure_ascii=False)
            old_data_write.close()
            messagebox.showinfo('Sucesso','Intervalo alterado',parent=interval_timer_top)
        except:
            pass
        
    timer_interval_label = customtkinter.CTkLabel(interval_timer_top,text="Intervalo entre mensagens (segundos):", text_font=("default_theme","13"))
    timer_interval_label.grid(row=0, column=0,columnspan=2, padx=20,pady=(10,0))
    
    timer_min_interval_label = customtkinter.CTkLabel(interval_timer_top,text="MININMO:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    timer_min_interval_label.grid(row=1, column=0, padx=20,pady=10,sticky='w')

    timer_min_interval_entry = customtkinter.CTkEntry(interval_timer_top,width=300)
    timer_min_interval_entry.grid(row=1, column=1, padx=20, pady=10)
    
    timer_max_interval_label = customtkinter.CTkLabel(interval_timer_top,text="MAXIMO:", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    timer_max_interval_label.grid(row=2, column=0, padx=20,pady=10,sticky='w')
    
    timer_max_interval_entry = customtkinter.CTkEntry(interval_timer_top,width=300)
    timer_max_interval_entry.grid(row=2, column=1,  pady=10)
    
    interval_timer_buttom = customtkinter.CTkButton(interval_timer_top,text='Alterar',command = timer_time_change)
    interval_timer_buttom.grid(row=8, column=1,padx=20,pady=(10,20),sticky='e')
    
    interval_timer_top.mainloop()

def edit_timer():
    
    edit_timer_top = customtkinter.CTkToplevel(app)
    edit_timer_top.title('RewardEvents - Editar um timer')
    
    def select_timer_edit(message_edit):
        
        global timer_message_key
        
        timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
        timer_data = json.load(timer_data_file)
        
        timer_message = timer_data['TIMERMESSAGE']['MESSAGES']
        
        def get_key(val):
            
            for key, value in timer_message.items():
                if val == value:
                    return key
        
            return "key doesn't exist"
        
        timer_message_key = get_key(message_edit)
        
        edit_timer_var = customtkinter.StringVar(value=f"{message_edit}")
        edit_timer_entry.configure(textvariable=edit_timer_var)   
        
    def edit_timer_confirm():
        
        edit_message_value = edit_timer_entry.get()
        
        timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
        timer_data = json.load(timer_data_file)
        
        timer_data['TIMERMESSAGE']['MESSAGES'][timer_message_key] = edit_message_value
        timer_data_file.close()
        
        try:
            old_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
            json.dump(timer_data, old_data_write, indent = 4,ensure_ascii=False)
            old_data_write.close()
            
            messages_edit_combox = update_del_combox()
            message_edit_val = customtkinter.StringVar(value="Selecione uma mensagem")
            combobox_message.configure(variable=message_edit_val,values=list(messages_edit_combox.values()))
            
            messagebox.showinfo('Sucesso','Mensagem editada', parent=edit_timer_top)
        except:
            messagebox.showerror('Erro','Não foi possível editar a mensagem', parent=edit_timer_top)
            
    def update_del_combox():
        
        message_data_file = open('src/config/timer.json' , 'r',encoding='utf-8') 
        message_data = json.load(message_data_file)
        message_del = message_data['TIMERMESSAGE']['MESSAGES']
        message_data_file.close()
    
        return message_del
    
    messages_edit_combox = update_del_combox()
    
    message_edit_val = customtkinter.StringVar(value="Selecione uma mensagem")
    
    title_timer_del = customtkinter.CTkLabel(edit_timer_top, text="Editar timer", text_font=("default_theme","13"))
    title_timer_del.grid(row=0, column=0 ,padx=20, pady=10)
    
    combobox_message = customtkinter.CTkComboBox(edit_timer_top, values=list(messages_edit_combox.values()),
                                                 variable=message_edit_val, width=300, command = select_timer_edit)
    
    combobox_message.grid(row=1, column=0, padx=20, pady=10)
    
    
    edit_timer_entry = customtkinter.CTkEntry(edit_timer_top, width=300)
    edit_timer_entry.grid(row=2, column=0, padx=20, pady=(15, 5))

    del_timer_buttom = customtkinter.CTkButton(edit_timer_top, text='Salvar timer', command = edit_timer_confirm)
    del_timer_buttom.grid(row=3, column=0, padx=20, pady=(20,60), sticky='e')
    
    edit_timer_top.mainloop()   
    
def del_timer():
    
    del_timer_top = customtkinter.CTkToplevel(app)
    del_timer_top.title('RewardEvents - Excluir um timer')
    
    def del_timer_confirm():
        
        message_to_del = combobox_message.get()
        message_del_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
        message_del_date = json.load(message_del_file)

        message_list = message_del_date['TIMERMESSAGE']['MESSAGES']
        
        message_del_file.close()
        
        key_list = list(message_list.keys())
        val_list = list(message_list.values())
    
        position = val_list.index(message_to_del)
        
        key_value = key_list[position]
        
        try:
            del message_del_date['TIMERMESSAGE']['MESSAGES'][key_value]
            
            message_del_file_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
            json.dump(message_del_date, message_del_file_write, indent = 4,ensure_ascii=False)
            message_del_file_write.close()
            
            update_del_combox()
            combobox_message.update()
            
            messagebox.showinfo('Exluido','Timer Excluido com sucesso',parent=del_timer_top)
        except:
            messagebox.showerror('Erro','Erro ao excluir o timer',parent=del_timer_top)
            
    def update_del_combox():
        
        message_data_file = open('src/config/timer.json' , 'r',encoding='utf-8') 
        message_data = json.load(message_data_file)
        message_del = message_data['TIMERMESSAGE']['MESSAGES']
        message_data_file.close()
    
        return message_del
    
    messages_combox = update_del_combox()
    
    message_val = customtkinter.StringVar(value="Selecione uma mensagem")        
            
    title_timer_del = customtkinter.CTkLabel(del_timer_top, text="Excluir uma mensagem", text_font=("default_theme","13"))
    title_timer_del.grid(row=9, column=0 ,padx=20,columnspan=2, pady=10)
    
    combobox_message = customtkinter.CTkComboBox(del_timer_top,values=list(messages_combox.values()),variable=message_val,width=300)
    combobox_message.grid(row=10,column=0 ,padx=20, pady=10)

    del_timer_buttom = customtkinter.CTkButton(del_timer_top,text='Excluir',command = del_timer_confirm)
    del_timer_buttom.grid(row=10, column=1,padx=20, pady=10,sticky='e')
    
    del_timer_top.mainloop()
            
def timer(tid):
    
    while True:
        
        with open('src/config/timer.json' , 'r', encoding='utf-8') as timer_data_file:
            timer_data = json.load(timer_data_file)
        
        timer_data_timer = timer_data['TIMERMESSAGE']['TIME']
        timer_data_timer_max = timer_data['TIMERMESSAGE']['TIME_MAX']
        
        timer_int = int(timer_data_timer)
        timer_max_int = int(timer_data_timer_max)
        
        try:
            timer_message = timer_data['TIMERMESSAGE']['MESSAGES']
            message_value = [*timer_message.values()]
            message = random.choice(list(message_value))
            
            send_message(message,'TIMER')
            
        except:
            pass
            
        next_timer = randint(timer_int,timer_max_int)
        
        time.sleep(next_timer)
      
def top_auth():
    
    auth_top = customtkinter.CTkToplevel(app)
    auth_top.title('RewardEvents - Auth Login')
    auth_top.attributes('-topmost', 'true')
    
    def start_auth_user():
        
        username_entry = user_name_entry.get()

        if username_entry == '':
            messagebox.showerror('Nome de usuário', 'Insira o seu nome de usuário',parent=auth_top)
        else:
            
            data = {'USERNAME': username_entry.lower(), 'USERID': '', 'TOKEN': '', 'TOKENBOT': '',
                    'BOTUSERNAME': ''}

            out_file = open("src/auth/auth.json", "w", encoding='utf-8')
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()
            
            auth_user.Webview_Auth()

            out_file_check = open("src/auth/auth.json", encoding='utf-8')
            data_check = json.load(out_file_check)
            
            token = data_check['TOKEN']
            if token:
                messagebox.showinfo('Autenticado','Usuário autenticado',parent=auth_top)
                out_file_check.close()
                    
    def start_auth_bot():
    
        bot_username_entry = bot_user_name_entry.get()
        bot_user_op_value = bot_user_op.get()
        
        out_file1 = open("src/auth/auth.json")
        data1 = json.load(out_file1)
        username = data1['USERNAME']
        token = data1['TOKEN']
        USERI_auth = data1['USERID']

        if bot_user_op_value == "1":
            out_file1 = open("src/auth/auth.json", encoding='utf-8')
            data1 = json.load(out_file1)

            username = data1['USERNAME']
            token = data1['TOKEN']
            USERID = data1['USERID']

            data = {'USERNAME': username, 'USERID': USERID, 'TOKEN': token, 'TOKENBOT': token,
                    'BOTUSERNAME': username}

            out_file = open("src/auth/auth.json", "w", encoding='utf-8')
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()
            
            if messagebox.showinfo('Auntenticado', 'Conta Bot autenticada com sucesso, reinicie o programa!',parent=auth_top):
                os._exit(0)
            
        else:
            if bot_username_entry == '':
                messagebox.showerror('Nome de usuário', 'Insira o seu nome de usuário',parent=auth_top)
            else:
                
                data = {'USERNAME': username, 'USERID': USERI_auth, 'TOKEN': token, 'TOKENBOT': '',
                        'BOTUSERNAME': bot_username_entry.lower()}

                out_file = open("src/auth/auth.json", "w")
                json.dump(data, out_file, indent=6,ensure_ascii=False)
                out_file.close()
                
                auth_bot.Webview_Auth()
                
                out_file_check = open("src/auth/auth.json")
                data_check = json.load(out_file_check)
                
                token_bot = data_check['TOKENBOT']
                if token_bot:
                    if messagebox.showinfo('Autenticado','Usuário autenticado, reincie o programa'):
                        os._exit(0)
                else:
                    if messagebox.showinfo('Erro','Erro ao processar o token.'):
                        os._exit(0)
                    
    def status_bot():
        bot_user_name_entry.configure(state='disabled')      
    
    top_title = customtkinter.CTkLabel(auth_top, text="Execute o login com a conta streamer para receber as recompensas\ne com uma conta bot para enviar mensagens no chat\no nome de usuário precisar ser o mesmo da URL", text_font='20', justify=CENTER)
    top_title.grid(row=0, column=0, columnspan=2,padx=20 ,pady=(20, 20))
    
    user_name_label = customtkinter.CTkLabel(auth_top, text='Nome de usuário conta Streamer :',text_font='20', anchor="w",justify=LEFT)
    user_name_label.grid(row=1,column=0, padx=20, pady=(10, 5),sticky='W')
    
    user_name_entry = customtkinter.CTkEntry(auth_top,width=200)
    user_name_entry.grid(row=1,column=1, padx=20, pady=(10,5))
    
    user_name_auth_buttom = customtkinter.CTkButton(auth_top,text='Logar conta streamer',command = start_auth_user,width=200)
    user_name_auth_buttom.grid(row=3, column=0,columnspan=2, padx=20,pady=(5,50),)
    
    bot_user_name_label = customtkinter.CTkLabel(auth_top, text='Nome de usuário conta conta Bot',text_font='20', anchor="w",justify=LEFT)
    bot_user_name_label.grid(row=4,column=0,padx=20 ,pady=(20, 5),sticky='W')
    
    bot_user_name_entry = customtkinter.CTkEntry(auth_top,width=200)
    bot_user_name_entry.grid(row=4,column=1,padx=20 ,pady=(20,5))
    
    bot_user_name_auth_buttom = customtkinter.CTkButton(auth_top,text='Logar conta bot',command = start_auth_bot,width=200)
    bot_user_name_auth_buttom.grid(row=7, column=0,columnspan=2, padx=20,pady=(10,20))
    
    bot_user_op = customtkinter.CTkSwitch(auth_top,text="Usar a conta streamer como conta bot ?\n(Clique no botão 'login conta bot' para confirmar)", onvalue="1", offvalue="0",command=status_bot)
    bot_user_op.grid(row=8, column=0,columnspan=2, padx=20,pady=(10,30))
    
def con_pubsub():
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
    
    if TOKEN and TOKENBOT:
        twitch = Twitch(apitoken.CLIENTID,
                        apitoken.CLIENTSECRET,
                        target_app_auth_scope=[AuthScope.USER_EDIT])

        scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
        scope1 = [AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

        twitch.set_user_authentication(TOKEN, scope + scope1, 'refresh_token')
        pubsub = PubSub(twitch)
        pubsub.start()
        pubsub.listen_channel_points(USERID, callback_whisper)
        
        out_file_obs = open("src/config/obs.json")
        data_obs = json.load(out_file_obs)
        
        if data_obs['OBS_AUTO_CON'] == 1:
            obs_con.conect_obs()

        tab3.update()
    
        url = "https://api.twitch.tv/helix/users?login=" + USERNAME

        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer " + TOKEN
        headers["Client-Id"] = apitoken.CLIENTID

        resp = req.get(url, headers=headers)
        user = json.loads(resp.text)
        
        try:
            resp_user_id = user['data'][0]['id']
            resp_display_name = user['data'][0]['display_name']
            resp_login_name = user['data'][0]['login']
            resp_email = user['data'][0]['email']
            resp_profile_img = user['data'][0]['profile_image_url']
            
            prfile_img = req.get(resp_profile_img).content

            with open('src/profile.png', 'wb') as handler:
                handler.write(prfile_img)
                handler.close()

            profile_img_load= ImageTk.PhotoImage(PIL.Image.open("src/profile.png").resize((100, 100)).convert("RGBA"))
            profile_img_label.configure(image=profile_img_load)
            profile_img_label.image = profile_img_load

            exibition_name_label.configure(text=f'{resp_display_name}')
            profile_name_label.configure(text=f'{resp_login_name}')
            user_id_label.configure(text=f'{resp_user_id}')
            email_label.configure(text=f'{resp_email}')

        except:
            profile_img_label.grid_forget()
            exibition_name_label.grid_forget()
            profile_name_label.grid_forget()
            user_id_label.grid_forget()
            email_label.grid_forget()
            reconectar.grid_forget()
            
            profile_name_label_title.grid_forget()
            exibition_name_label_title.grid_forget()
            user_id_label_title.grid_forget()
            email_label_title.grid_forget()
            deslogar.grid_forget()
            
            status_send.grid_forget()
            status_send_label.grid_forget()
            status_receive.grid_forget()
            status_receive_label.grid_forget()
            
            auth_desc.grid(row=8, column=0, columnspan=2,pady=(150,20))
            auth_button.grid(row=9, column=0, columnspan=2,pady=10)
        
    else:
        if messagebox.showinfo('Erro','Execute o processo de autenticação.'):
            top_auth()
           
def receive_commands(tid):
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
         
    def do_something(message):
        
        command_file = open('src/config/commands.json', "r", encoding='utf-8') 
        command_data = json.load(command_file) 
        
        command_file_prefix = open('src/config/prefix_commands.json', "r", encoding='utf-8') 
        command_data_prefix = json.load(command_file_prefix)
        
        command_file_simple = open('src/config/simple_commands.json', "r", encoding='utf-8') 
        command_data_simple = json.load(command_file_simple)
        
        command_file_tts = open('src/config/prefix_tts.json', "r", encoding='utf-8') 
        command_data_tts = json.load(command_file_tts) 
            
        
        prefix = command_data_prefix['prefix']
        command_tts = command_data_tts['command']
        user_type_tts = command_data_tts['user_level']
        
        command = message['message']
        user = message['display-name'] 
        user_type = message['user-type'] 
        user_id_command = message['user-id']
        
        check_tts = command.startswith(command_tts)
        check_command = command.startswith(prefix)
        
        try:
            
            if check_tts:
                
                status_tts = command_data_tts['status']

                if status_tts == 1:
                    message_delay,check_time = check_delay_file.check_delay() 
                        
                    if check_time:
                    
                        if user_type == user_type_tts or user_id_command == USERID:
                            
                            receive = command.split(command_tts,1)[1]
                            redeem = command_data_tts['redeem']
                            
                            data_rewards = {}
                            data_rewards['USERNAME'] = user
                            data_rewards['REDEEM'] = redeem
                            data_rewards['USER_INPUT'] = receive
                            data_rewards['USER_LEVEL'] = user_type
                            data_rewards['USER_ID'] = user_id_command
                            data_rewards['COMMAND'] = receive
                            data_rewards['PREFIX'] = prefix
                            
                            received_type = 'command'
                            
                            receive_redeem(data_rewards,received_type)
                    else:
                        send_message(message_delay,'ERROR_TIME')
                else:

                    send_message("/me O comando '!tts' está desativado.","ERROR_TTS")
                
            elif check_command:

                status_commands = command_data_prefix['STATUS_COMMANDS']    
                    
                if status_commands == 1:

                    receive = command.split(prefix,1)[1]
                        
                    if receive in command_data.keys():
                        
                        redeem = command_data[receive]['RECOMPENSA']
                        user_level_simple = command_data[receive]['user_level']
                        
                        data_rewards = {}
                        data_rewards['USERNAME'] = user
                        data_rewards['REDEEM'] = redeem
                        data_rewards['USER_INPUT'] = receive
                        data_rewards['USER_LEVEL'] = user_type
                        data_rewards['USER_ID'] = user_id_command
                        data_rewards['COMMAND'] = receive
                        data_rewards['PREFIX'] = prefix

                        received_type = 'command'
                        
                        if user_type == user_level_simple or user_id_command == USERID:
                            
                            message_delay_global,check_time_global = check_delay_file.check_global_delay()
                            
                            if check_time_global:    
                                receive_redeem(data_rewards,received_type)
                            else:
                                send_message(message_delay_global,'ERROR_TIME')
                        else:
                            send_message(f"/me Somente usuários com permissão {user_level_simple} podem usar !{receive}",'ERROR_USER')
                        
                    elif receive in command_data_simple.keys():
                    
                        response = command_data_simple[receive]['response']
                        user_level_simple = command_data_simple[receive]['user_level']
                            
                        if user_type == user_level_simple or user_id_command == USERID:
                            
                            aliases = {'{user}': user,'{command}': receive, '{prefix}': prefix, '{user_level}': user_type, '{user_id}': user_id_command}
                            response_redus = replace_all(response, aliases)
                            
                            message_delay_global,check_time_global = check_delay_file.check_global_delay()
                            if check_time_global:        
                                send_message(response_redus,'RESPONSE')
                            else:
                                send_message(message_delay_global,'ERROR_TIME')
                        else:
                            send_message(f"/me Somente usuários com permissão {user_level_simple} podem usar !{receive}",'ERROR_USER')
                else:
                    
                    send_message("/me Os comandos estão desativados.","RESPONSE")
          
        except:
            pass
    
    command_connected = 0
    status_receive_label.configure(text="Aguarde!")
      
    while command_connected == 0:
        if TOKEN and TOKENBOT:
            try:   
                time.sleep(5)
                command_connected = 1
                status_receive_label.configure(text="Conectado!")   
                send_message('Módulo para comandos conectado...','RESPONSE')  
                connection.listen(USERNAME,on_message=do_something)
            except:
                command_connected = 0
                status_receive_label.configure(text="Desconectado!,Aguarde...")
                time.sleep(110)
        else:
            time.sleep(110)

def close():
    if messagebox.askokcancel("Sair", "Confirmar saída"):
        if con_status == '1':
            connection.close_connection()
        app.destroy() 
        time.sleep(2)
        run_cmd(os._exit(0))

def update_windown():
    
    update_windown_top = customtkinter.CTkToplevel(app)
    update_windown_top.title('RewardEvents - Download Update')
    
    def bar_progress(current, total,width=100):
        
        num_2 = current / total * 100
        num = trunc(num_2)
        
        status.configure(text='Baixando')
        
        if num == 100:
                status.configure(text='Download concluido\nFeche o programa e mova os arquivos dentro do .zip para os respectivos diretórios')  
              
    def download_update():    
        response = req.get("https://api.github.com/repos/GGTEC/RewardEvents/releases/latest")
        response_json = json.loads(response.text)
        download_link = response_json['assets'][0]['browser_download_url']
        response = wget.download(download_link, "RewardEvents.zip", bar=bar_progress)
    
    
    status_title = customtkinter.CTkLabel(update_windown_top, text="Clique no botão abaixo para iniciar o download da atualização\nao completar o download ele será salvo na pasta principal do programa\ndescompacte e mova os arquivos para os diretórios manualmente." ,text_font=("default_theme","13"))
    status_title.grid(row=0,column=0, padx=25, pady=20)
    
    status = customtkinter.CTkLabel(update_windown_top, text="Status" ,text_font=("default_theme","13"))
    status.grid(row=1,column=0, padx=25, pady=20)
    
    start_update = customtkinter.CTkButton(update_windown_top, text="Iniciar Download",command=download_update,text_font=("default_theme","13"))
    start_update.grid(row=2,column=0, padx=25, pady=20)
    
    
    update_windown_top.mainloop()
      
def update_check():
    response = req.get("https://api.github.com/repos/GGTEC/RewardEvents/releases/latest")
    response_json = json.loads(response.text)
    version = response_json['tag_name']

    if version != 'v1.0':
        update_info = messagebox.askquestion('Update','Nova versão encontrada, deseja efetuar o download ?')
        if update_info == 'yes':
            update_windown()
              
                   
tab1.columnconfigure(0, weight=1) 

clip_icon = PhotoImage(file="src/icons/clip.png")

view_count = customtkinter.CTkLabel(tab1, text="Spec : " ,text_font=("default_theme","10"))
view_count.grid(row=0,column=0,columnspan=2, pady=(20,0),sticky='W')

request_img_result = ImageTk.PhotoImage(PIL.Image.open("src/defaultreward.png").resize((200, 200)).convert("RGBA"))
request_img = customtkinter.CTkLabel(tab1, image=request_img_result)
request_img.grid(row=1,column=0,columnspan=2, pady=(5,0),sticky='WE')

request_name = customtkinter.CTkLabel(tab1, text="Recompensa Resgatada:" ,text_font=("default_theme","10"))
request_name.grid(row=2,column=0,columnspan=2, padx=25, pady=(10,0),sticky='WE')

request_name = customtkinter.CTkLabel(tab1, text="Aguardando..", text_font=("default_theme","15"))
request_name.grid(row=3,column=0,columnspan=2, padx=25, pady=(5,0),sticky='WE')

user_request = customtkinter.CTkLabel(tab1, text="Resgatado por:",text_font=("default_theme","10"),width=100)
user_request.grid(row=4,column=0,columnspan=2, padx=25, pady=(20,0),sticky='WE')

user_request = customtkinter.CTkLabel(tab1, text="Bem-vindo", text_font=("default_theme","15"),width=100)
user_request.grid(row=5,column=0,columnspan=2, padx=25, pady=(5,0),sticky='WE')

clip_buttom = customtkinter.CTkButton(tab1,image=clip_icon, text='',command = self_clip)
clip_buttom.grid(row=6, column=0,columnspan=2, pady=(20,10))
tooltip_clip_buttom = CreateToolTip(clip_buttom, text = 'Criar um clip de 30 segundos')



#EVENTOS
tab2.columnconfigure(0, weight=1) 

title_events = customtkinter.CTkLabel(tab2, text='Gerenciar Eventos', text_font=("default_theme","15"))
title_events.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,10))

events_combox_list = ['Reproduzir Audio','Texto falado google','Mudar cena OBS','Exibir/Ocultar Filtro OBS',
                      'Exibir/Ocultar Fonte OBS','Atalho no teclado','Resposta no chat','Criar um Clip']

events_combox_label = customtkinter.CTkLabel(tab2, text='Selecione o Evento :', text_font=("default_theme","13"),anchor="w", justify=RIGHT)
events_combox_label.grid(row=1,column=0,padx=20,pady=10,sticky='W')

events_combox = customtkinter.CTkComboBox(tab2,values=events_combox_list,width=200)
events_combox.grid(row=1,column=1 ,padx=20, pady=10)

plus_add_image = PhotoImage(file="src/icons/plus-square.png")
del_image = PhotoImage(file="src/icons/del.png")

create_event_buttom = customtkinter.CTkButton(tab2,image=plus_add_image, text='', width=150, height=150, command=create_event)
create_event_buttom.grid(row=2,column=0, pady=(20,20))
tooltip_create_event_buttom = CreateToolTip(create_event_buttom, text = 'Adicionar um evento ( selecione o tipo acima )')

del_event_buttom = customtkinter.CTkButton(tab2,image=del_image, text='', width=150, height=150, command=del_event)
del_event_buttom.grid(row=2, column=1, pady=(20,20))
tooltip_del_event_buttom = CreateToolTip(del_event_buttom, text = 'Remover um evento')

#COMANDOS
tab3.columnconfigure(0, weight=1) 

title_commands = customtkinter.CTkLabel(tab3, text='Gerenciar Comandos Simples', text_font=("default_theme","15"))
title_commands.grid(row=1, column=0, columnspan=2, pady=(20,30))

edit_image = PhotoImage(file="src/icons/edit.png")
edit_time_image = PhotoImage(file="src/icons/edit_time.png")

create_simple_buttom = customtkinter.CTkButton(tab3,image=plus_add_image, text='',width=150, height=150,command=new_simple_command)
create_simple_buttom.grid(row=2, column=0,padx=(60,25), pady=20,sticky='w')
tooltip_create_simple_buttom = CreateToolTip(create_simple_buttom, text = 'Criar um comando simples')

edit_simple_buttom = customtkinter.CTkButton(tab3,image=edit_image, text='',width=150, height=150,command=edit_simple_command)
edit_simple_buttom.grid(row=2, column=1,padx=(25,60), pady=20)
tooltip_edit_simple_buttom = CreateToolTip(edit_simple_buttom, text = 'Editar um comando simples')

edit_delay_buttom = customtkinter.CTkButton(tab3,image=edit_image, text='',width=150, height=150,command=edit_delay_commands)
edit_delay_buttom.grid(row=3, column=0,padx=(60,25), pady=20, sticky='w')
tooltip_edit_delay_buttom = CreateToolTip(edit_delay_buttom, text = 'Editar delay para comandos')

del_message_simple_buttom = customtkinter.CTkButton(tab3,image=del_image, text='',width=150, height=150,command=del_simple_command)
del_message_simple_buttom.grid(row=3, column=1,padx=(25,60), pady=20)
tooltip_del_message_simple_buttom = CreateToolTip(del_message_simple_buttom, text = 'Remover um comando')


#TIMERS
tab4.columnconfigure(0, weight=1)

add_timer_image = PhotoImage(file="src/icons/time_add.png")
del_timer_image = PhotoImage(file="src/icons/time_del.png")
interval_timer_image = PhotoImage(file="src/icons/time_interval.png")

title_timers = customtkinter.CTkLabel(tab4, text='Gerenciar mensagens automaticas', text_font=("default_theme","15"))
title_timers.grid(row=1, column=0, columnspan=2, padx=20, pady=(20,30))

new_timer_buttom = customtkinter.CTkButton(tab4,image=add_timer_image, text='', width=150, height=150, command=new_timer)
new_timer_buttom.grid(row=2, column=0,padx=(60,25), pady=20, sticky='w')
tooltip_new_timer_buttom = CreateToolTip(new_timer_buttom, text = 'Criar um timer')

edit_timer_buttom = customtkinter.CTkButton(tab4,image=edit_time_image, text='', width=150, height=150, command=edit_timer)
edit_timer_buttom.grid(row=2, column=1,padx=(25,60), pady=20)
tooltip_edit_timer_buttom = CreateToolTip(edit_timer_buttom, text = 'Editar um timer')

del_timer_buttom = customtkinter.CTkButton(tab4,image=del_timer_image, text='', width=150, height=150, command=del_timer )
del_timer_buttom.grid(row=3, column=0,padx=(60,25), pady=20, sticky='w')
tooltip_del_timer_buttom = CreateToolTip(del_timer_buttom, text = 'Remover um timer')

interval_timer_buttom = customtkinter.CTkButton(tab4,image=interval_timer_image, text='', width=150, height=150, command=timer_interval)
interval_timer_buttom.grid(row=3, column=1,padx=(25,60), pady=20)
tooltip_interval_timer_buttom = CreateToolTip(interval_timer_buttom, text = 'Alterar intervalo entre as mensagens automaticas')

#CONFIG OBS
tab5.columnconfigure(0, weight=1)



config_notifc_image = PhotoImage(file="src/icons/config_notifc.png")
obs_config = PhotoImage(file="src/icons/obs_config.png")
messages_config = PhotoImage(file="src/icons/enable_messages.png")

config_label = customtkinter.CTkLabel(tab5, text='Configurações gerais', text_font=("default_theme","15"))
config_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,30))

config_conn_obs_button = customtkinter.CTkButton(tab5,image=obs_config, width=150, height=150, text='', command=config_obs_conn_top)
config_conn_obs_button.grid(row=1, column=0, padx=20, pady=20)
tooltip_config_conn_obs_button = CreateToolTip(config_conn_obs_button, text = 'Conexão com o OBS studio')

config_notif_obs_button = customtkinter.CTkButton(tab5,image=config_notifc_image, width=150, height=150, text='', command=config_obs_not_top)
config_notif_obs_button.grid(row=1, column=1,padx=(25,60), pady=20)
tooltip_config_notif_obs_button = CreateToolTip(config_notif_obs_button, text = 'Notificações do OBS studio')

config_messages_top_buttom = customtkinter.CTkButton(tab5,image=messages_config, width=150, height=150, text='', command=config_messages_top)
config_messages_top_buttom.grid(row=2, column=0,columnspan=2, padx=20, pady=20)
tooltip_config_messages_top_buttom = CreateToolTip(config_messages_top_buttom, text = 'Habilitar/desabilitar mensagens')


#PERFIL
tab6.columnconfigure(0, weight=1)

profile_img_label = customtkinter.CTkLabel(tab6, image='')
profile_img_label.grid(row=1, column=0, columnspan=2, pady=20)

profile_name_label_title = customtkinter.CTkLabel(tab6, text=f"LOGIN NAME", text_font=("default_theme", "12"),anchor="w", justify=LEFT)
profile_name_label_title.grid(row=2, column=0, pady=2, padx=20, sticky='w')

profile_name_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "12"),anchor="e", justify=RIGHT)
profile_name_label.grid(row=2, column=1, pady=2, padx=20, sticky='e')

exibition_name_label_title = customtkinter.CTkLabel(tab6, text=f"NOME DE EXIBIÇÃO", text_font=("default_theme", "11"),anchor="w", justify=LEFT)
exibition_name_label_title.grid(row=3, column=0, pady=2, padx=20, sticky='w')

exibition_name_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT)
exibition_name_label.grid(row=3, column=1, pady=2, padx=20, sticky='e')

user_id_label_title = customtkinter.CTkLabel(tab6, text=f"ID DE USUÁRIO", text_font=("default_theme", "11"),anchor="w", justify=LEFT)
user_id_label_title.grid(row=4, column=0, pady=2, padx=20, sticky='w')

user_id_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT, )
user_id_label.grid(row=4, column=1, pady=2, padx=20, sticky='e')

email_label_title = customtkinter.CTkLabel(tab6, text=f"EMAIL", text_font=("default_theme", "11"),anchor="w", justify=LEFT)
email_label_title.grid(row=5, column=0, pady=2, padx=20, sticky='w')

email_label = customtkinter.CTkLabel(tab6, text=f"", text_font=("default_theme", "11"), anchor="e",justify=RIGHT)
email_label.grid(row=5, column=1, pady=2, padx=20, sticky='e')

status_send = customtkinter.CTkLabel(tab6, text=f"Enviar mensagens no chat:", text_font=("default_theme", "11"),anchor="w", justify=LEFT)
status_send.grid(row=6, column=0, pady=2, padx=20, sticky='w')

status_send_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT)
status_send_label.grid(row=6, column=1, pady=2, padx=20, sticky='e')

status_receive = customtkinter.CTkLabel(tab6, text=f"Receber comandos:", text_font=("default_theme", "11"),anchor="w", justify=LEFT)
status_receive.grid(row=7, column=0, pady=2, padx=20, sticky='w')

status_receive_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT)
status_receive_label.grid(row=7, column=1, pady=2, padx=20, sticky='e')

status_obs_label = customtkinter.CTkLabel(tab6, text=f"Conexão com OBS Studio:", text_font=("default_theme", "11"),anchor="w", justify=LEFT)
status_obs_label.grid(row=8, column=0, pady=2, padx=20, sticky='w')

status_obs = customtkinter.CTkLabel(tab6,width=100, text=f"", text_font=("default_theme", "11"))
status_obs.grid(row=8, column=1, pady=2,padx=(0,10),sticky='e')

deslogar = customtkinter.CTkButton(tab6, text='Limpar dados', command=clear_data)
deslogar.grid(row=9, column=0, padx=20,pady=30)

reconectar = customtkinter.CTkButton(tab6, text='Reconectar Sistema', command=con_pubsub)
reconectar.grid(row=9, column=1, padx=20, pady=30)

conn_obs_buttom = customtkinter.CTkButton(tab6, width=250, text='CONECTAR OBS', command=obs_con.conect_obs)
conn_obs_buttom.grid(row=10, column=0, columnspan=2, padx=20, pady=10)

auth_desc = customtkinter.CTkLabel(tab6,text=f"Efetue o login para executar o programa corretamente",
                                         text_font=("default_theme", "13"),
                                         anchor="w", justify=CENTER)

auth_button = customtkinter.CTkButton(tab6, text='Autenticar contas', command=top_auth,width=200)


tab7.columnconfigure(0, weight=1)

logo_image_src= ImageTk.PhotoImage(PIL.Image.open("src/about.png").resize((170, 170)).convert("RGBA"))
logo_image = customtkinter.CTkLabel(tab7, image=logo_image_src)
logo_image.grid(row=1, column=0,  pady=20)

about_name = customtkinter.CTkLabel(tab7, text=f"RewardEvents v1.0", text_font=("default_theme", "12"))
about_name.grid(row=2, column=0, pady=10, padx=20)

dev_name = customtkinter.CTkLabel(tab7, text=f"Dev By GG_TEC", text_font=("default_theme", "12"))
dev_name.grid(row=3, column=0, pady=10, padx=20)

update_check_buttom = customtkinter.CTkButton(tab7, text='Verificar Atualização', command=update_check)
update_check_buttom.grid(row=6, column=0, pady=(30,20))

con_pubsub()
update_check()


_thread.start_new_thread(timer, (2,))
_thread.start_new_thread(receive_commands, (3,))
_thread.start_new_thread(keep_conn_chat, (4,))


app.protocol("WM_DELETE_WINDOW", close)
app.mainloop()