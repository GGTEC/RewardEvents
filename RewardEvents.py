#!/usr/bin/env python
# -*- coding: utf-8 -*-

from load_files import check_files

if check_files() == True:
    import json
    import time
    import customtkinter
    import os
    import auth
    import apitoken
    import keyboard
    import pygame
    import PIL.Image
    import _thread
    import requests as req
    import auth_user
    import auth_bot
    import subprocess
    import wget
    import check_delay_file
    import textwrap
    import smt
    import timer_module
    import html_edit
    import tkinter
    from random import randint
    from load_files import clear_files
    from tooltiptkinter import CreateToolTip
    from gtts import gTTS
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
    from twitchAPI.twitch import Twitch, AuthScope
else:
    import os
    os._exit(1)


def keep_conn_chat(tid):
    global conn_status
    while True:

        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()

        if TOKEN and TOKENBOT:

            smt.conect_chat()
            conn_status = True
            time.sleep(120)

        else:
            conn_status = False
            time.sleep(5)
        
_thread.start_new_thread(keep_conn_chat, (5,))   

lang_config_file = open('src/config/lang.json', 'r', encoding='utf-8')
lang_config_data = json.load(lang_config_file)

lang_selected = lang_config_data['lang']

lang_file = open(f'src/lang/{lang_selected}.json', 'r', encoding='utf-8')
lang_data = json.load(lang_file)

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

pygame.init()
pygame.mixer.init()
   
app = customtkinter.CTk()
app.title(f'RewardEvents by GG-TEC')
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

frame.add(tab1, text = lang_data['waiting'])

USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()

if TOKEN and TOKENBOT:

    frame.add(tab2, text = lang_data['events'])
    frame.add(tab3, text = lang_data['commands'])
    frame.add(tab4, text = lang_data['timers'])
    frame.add(tab5, text = lang_data['config'])
    frame.add(tab6, text = lang_data['profile'])
    
frame.add(tab7, text = lang_data['about'])
path_text = customtkinter.StringVar()
count_tts = 0

messages_file = open('src/messages/messages_file.json', "r", encoding='utf-8') 
messages_data = json.load(messages_file)   

class Obsconect:
    def __init__(self):
        super().__init__()
        self.ws = None
        self.conn_status = '0'
        self.sources_list = None

    def connect_obs(self):

        out_file_obs_atual = open("src/config/obs.json")
        data_obs_atual = json.load(out_file_obs_atual)

        if any(value == '' for value in data_obs_atual.values()) == True:

            return False

        else:
            
            obs_host_data_atual = data_obs_atual['OBS_HOST']
            obs_port_data_atual = data_obs_atual['OBS_PORT']
            obs_port_int = int(obs_port_data_atual)
            obs_password_data_atual = data_obs_atual['OBS_PASSWORD']

            try:
                self.ws = obsws(obs_host_data_atual, obs_port_int, obs_password_data_atual)
                self.ws.connect()
                
                self.conn_status = '1'
                return True
                
            except:

                self.conn_status = '0'
                return False 
            
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
            
    def show_notifc_html(self):

        not_file = open('src/config/notfic.json') 
        not_data = json.load(not_file)
        
        html_source_title = not_data["HTML_TITLE"]
        html_source_time = not_data["HTML_TIME"]
        html_active = not_data["HTML_ACTIVE"]

        def notifc_thread(tid):

            self.ws.call(requests.SetSceneItemProperties(html_source_title,visible= True))

            time.sleep(html_source_time)

            self.ws.call(requests.SetSceneItemProperties(html_source_title,visible= False))


        if self.conn_status == "1":
                if html_active == 1:
                    _thread.start_new_thread(notifc_thread, (7,))
          
    def show_source(self,source_name,time_show_int):
        
        if self.conn_status == "1":
        
            self.ws.call(requests.SetSceneItemProperties(source_name,visible= True))
            time.sleep(time_show_int)
            self.ws.call(requests.SetSceneItemProperties(source_name,visible= False))
    
    def get_sources(self):
        
        if self.conn_status == "1":
        
            source_name_list = []
            
            sources = self.ws.call(requests.GetSourcesList())
            for s in sources.getSources():
                name = s['name']
                source_name_list.append(name)

        elif self.conn_status == "0":
            source_name_list = ""
            
        return source_name_list
    
    def get_scenes(self):
        
        if self.conn_status == "1":
        
            scene_name_list = []
            
            scenes = self.ws.call(requests.GetSceneList())
            for s in scenes.getScenes():
                name = s['name']
                scene_name_list.append(name)
                
        elif self.conn_status == "0":
            scene_name_list = ""
            
        return scene_name_list
    
    def get_filter_source(self,source):
        
        if self.conn_status == "1":
        
            filter_source_list = []
            
            filters = self.ws.call(requests.GetSourceFilters(source))
            for s in filters.getFilters():
                name = s['name']
                filter_source_list.append(name)
                
        elif self.conn_status == "0":
            filter_source_list = f""
            
        return filter_source_list
    
obs_con = Obsconect()
                
def run_cmd(command):
    subprocess.call(command, creationflags=0x08000000)
    
def callback_whisper(uuid: UUID, data: dict) -> None:
    received_type = 'redeem'
    receive_redeem(data,received_type)
    
def replace_all(text, dic):
    
    for i, j in dic.items():
        text = text.replace(i, j)
        
    return text

def get_spec(tid):
    
    while True:
    
        USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
        
        if TOKEN and TOKENBOT:
            
            url = f"https://api.twitch.tv/helix/streams?user_id={USERID}"

            headers = CaseInsensitiveDict()
            headers["Authorization"] = "Bearer "+ TOKEN
            headers["Client-Id"] = apitoken.CLIENTID

            resp = req.get(url, headers=headers)
            data_count = json.loads(resp.text)
            data_count_keys = data_count['data']
            
            if data_count_keys == []:

                view_count.configure(text=f" {lang_data['spectators_label']} : {lang_data['spectators_off']}") 

            else:
                count = data_count['data'][0]['viewer_count']
                spec = lang_data['spectators_label']
                view_count.configure(text=f'{spec} : {count}')

            if smt.value == True:
                status_send_label.configure(text= lang_data['connected'])
            else:
                status_send_label.configure(text= lang_data['disconnected'])  
                  
        else:
            view_count.configure(text=f" {lang_data['spectators_label']} : {lang_data['spectators_off']}")
            status_send_label.configure(text= lang_data['disconnected'])  
        
            
        time.sleep(120)
                 
def receive_redeem(data_rewards,received_type):
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
    
    with open("src/counter/counter.txt", "r") as counter_file_r:
            counter_file_r.seek(0)
            digit = counter_file_r.read()    
            if digit.isdigit():    
                counter = int(digit)
                
    redeem_reward_name = '0'
    redeem_by_user = '0'
    user_input = '0'
    user_level =  '0'
    user_id_command = '0'
    command_receive = '0'
    prefix = '0'
        
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
            
            
        img_data = req.get(redeem_reward_image).content
        with open('src/Request.png', 'wb') as handler:
            handler.write(img_data)
            handler.close()
            
    elif received_type == 'command':

        redeem_reward_name = data_rewards['REDEEM']
        redeem_by_user = data_rewards['USERNAME']
        user_input = data_rewards['USER_INPUT']
        user_level =  data_rewards['USER_LEVEL']
        user_id_command = data_rewards['USER_ID']
         
        command_receive = data_rewards['COMMAND']
        prefix = data_rewards['PREFIX']
        
    aliases = {
            '{user}': redeem_by_user,
            '{command}': command_receive, 
            '{prefix}': prefix,
            '{user_level}': user_level, 
            '{user_id}': user_id_command,
            '{counter}' : str(counter)
            }
    
    request_img_result = ImageTk.PhotoImage(PIL.Image.open("src/Request.png").resize((200, 200)).convert("RGBA"))
    request_img.configure(image=request_img_result)
    request_img.image = request_img_result

    html_edit.update_notif(redeem_reward_name,redeem_by_user)
    obs_con.show_notifc_html()

    request_name.configure(text=redeem_reward_name)
    user_request.configure(text='  '+ redeem_by_user + '  ')

    path_file = open('src/config/pathfiles.json', 'r', encoding='utf-8') 
    path = json.load(path_file)    
        
    def playsound():
        
        audio_path = path[redeem_reward_name]['PATH']
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

    def playtts():

        global count_tts

        send_response_value = path[redeem_reward_name]['send_response']
        characters = path[redeem_reward_name]['characters']
        characters_int = int(characters)
        
        user_input_short = textwrap.shorten(user_input, width=characters_int ,placeholder=" ")
        
        tts = gTTS(text=user_input_short, lang='pt-br', slow=False)
        tts.save(f'src/files/tts_sound{count_tts%2}.mp3')
        tts_playing = pygame.mixer.music.get_busy()
        
        while tts_playing:
                tts_playing = pygame.mixer.music.get_busy()
                time.sleep(2)  
        
        pygame.mixer.music.load(f'src/files/tts_sound{count_tts%2}.mp3')
        pygame.mixer.music.play()
        
        if send_response_value:
            
            chat_response = path[redeem_reward_name]['chat_response']
            print(chat_response)
            
            try:
                response_redus = replace_all(chat_response, aliases)
                smt.send_message(response_redus,'RESPONSE')
            except:
                smt.send_message(chat_response,'RESPONSE')

        count_tts += 1

    def changescene():
        
        principal_scene_name = path[redeem_reward_name]['CURRENTSCENENAME']
        scene_name = path[redeem_reward_name]['SCENENAME']
        send_response_value = path[redeem_reward_name]['send_response']
        return_scene = path[redeem_reward_name]['return_scene']
        
        time_show = path[redeem_reward_name]['TIME']
        
        if send_response_value == 1:
 
            chat_response = path[redeem_reward_name]['chat_response']
        
            try:
                response_redus = replace_all(chat_response, aliases)
                smt.send_message(response_redus,'RESPONSE')
            except:
                smt.send_message(chat_response,'RESPONSE')
            
        obs_con.scene(scene_name,time_show, return_scene, principal_scene_name)

    def sendmessage():

        chat_response = path[redeem_reward_name]['chat_response']
        
        try:
            response_redus = replace_all(chat_response, aliases)
            smt.send_message(response_redus,'RESPONSE')
        except:
            smt.send_message(chat_response,'RESPONSE')

    def changefilter():

        source_name = path[redeem_reward_name]['SOURCE']
        send_response_value = path[redeem_reward_name]['send_response']
        filter_name = path[redeem_reward_name]['FILTER']
        time_show = path[redeem_reward_name]['TIME']

        time_show_int = int(time_show)
        
        
        if send_response_value:
            chat_response = path[redeem_reward_name]['chat_response']
            

            try:
                response_redus = replace_all(chat_response, aliases)
                smt.send_message(response_redus,'RESPONSE')
            except:
                smt.send_message(chat_response,'RESPONSE')
        
        obs_con.show_filter(source_name,filter_name,time_show_int)
        
    def keypress():

        keyskeyboard = path[redeem_reward_name]

        send_response_value = path[redeem_reward_name]['send_response']

        press_again_value = path[redeem_reward_name]['press_again']
        time_press_value = path[redeem_reward_name]['time_press']

        keep_press_value = path[redeem_reward_name]['keep']
        keep_press_time = path[redeem_reward_name]['keep_time']

        repeat_value = path[redeem_reward_name]['repeat']
        repeat_times = path[redeem_reward_name]['repeat_times']
        repeat_interval = path[redeem_reward_name]['repeat_interval']

        aliases = {'{user}': redeem_by_user,'{command}': command_receive, '{prefix}': prefix, '{user_level}': user_level, '{user_id}': user_id_command}
        
        def press_again(tid):

            if send_response_value:
                
                chat_response = path[redeem_reward_name]['chat_response']
                
                try:
                    response_redus = replace_all(chat_response, aliases)
                    smt.send_message(response_redus,'RESPONSE')
                except:
                    smt.send_message(chat_response,'RESPONSE')
                
            received = [*keyskeyboard.keys()][11:]

            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']


            keyboard.press_and_release('+'.join(keys_to_pressed))
            
            time.sleep(time_press_value)
            
            keyboard.press_and_release('+'.join(keys_to_pressed))

        def repeated_press(tid):

            if send_response_value:
                
                chat_response = path[redeem_reward_name]['chat_response']
                
                try:
                    response_redus = replace_all(chat_response, aliases)
                    smt.send_message(response_redus,'RESPONSE')
                except:
                    smt.send_message(chat_response,'RESPONSE')
                
            value_repeated = 0
            
            while value_repeated < repeat_times:

                value_repeated = value_repeated + 1

                received = [*keyskeyboard.keys()][11:]
                keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']
                keyboard.press_and_release('+'.join(keys_to_pressed))
                time.sleep(repeat_interval)

        def keep_press(tid):

            if send_response_value:
                
                chat_response = path[redeem_reward_name]['chat_response']
                
                try:
                    response_redus = replace_all(chat_response, aliases)
                    smt.send_message(response_redus,'RESPONSE')
                except:
                    smt.send_message(chat_response,'RESPONSE')
                
            received = [*keyskeyboard.keys()][11:]

            keys_to_pressed = [keyskeyboard[key] for key in received if keyskeyboard[key]!='NONE']

            keyboard.press('+'.join(keys_to_pressed))
            keyboard.block_key('+'.join(keys_to_pressed))

            time.sleep(keep_press_time)

            keyboard.release('+'.join(keys_to_pressed))

        if repeat_value == 1:
            _thread.start_new_thread(repeated_press, (10,))
            
        elif press_again_value == 1:
            _thread.start_new_thread(press_again, (10,))

        elif keep_press_value == 1:
            _thread.start_new_thread(keep_press, (10,))
                      
    def source():

        source_name = path[redeem_reward_name]['SOURCENAME']
        send_response_value = path[redeem_reward_name]['send_response']
        time_show_int = path[redeem_reward_name]['TIME']       
        
        if send_response_value:
            
            chat_response = path[redeem_reward_name]['chat_response']
            response_redus = replace_all(chat_response, aliases)
            smt.send_message(response_redus,'RESPONSE')
        
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


            message_clip_user = messages_data['clip_create_clip'].replace('{user}',redeem_by_user)
            message_final = message_clip_user.replace('{clip_id}',response_create)
            smt.send_message(message_final,"CLIP")
            
        except:
            response_error = response_clip['message']

            if response_error:
                message_clip_error = messages_data['clip_error_clip']
                smt.send_message(message_clip_error,'CLIP')

    def add_counter():
        
        send_response_value = path[redeem_reward_name]['send_response']
        
        with open("src/counter/counter.txt", "r") as counter_file_r:

                if len(counter_file_r.read()) == 0:
                    
                    with open("src/counter/counter.txt", "w") as counter_file_w:
                        counter_file_w.write('1')

                else:
                    
                    counter_file_r.seek(0)
                    digit = counter_file_r.read()
                    
                    if digit.isdigit():
                        
                        counter = int(digit)
                        countercount = counter + 1
                        
                    else:
                        countercount = 0
                        
                    with open("src/counter/counter.txt", "w") as counter_file_w:      
                        counter_file_w.write(str(countercount))
                        
        if send_response_value:
        
            chat_response = path[redeem_reward_name]['chat_response']
            aliases['{counter}'] = str(countercount)
            
            try:
                response_redus = replace_all(chat_response, aliases)
                smt.send_message(response_redus,'RESPONSE')
            except:
                smt.send_message(chat_response,'RESPONSE')

    def add_giveaway():

        send_response_value = path[redeem_reward_name]['send_response']

        give_config_file = open("src/giveaway/config.json", "r",encoding='utf-8')
        give_config_data = json.load(give_config_file)

        enabled_give = give_config_data['enable']

        if enabled_give == 1:
        
            with open("src/giveaway/names.txt", "a+") as give_file_r:
                        give_file_r.write(redeem_by_user+"\n")
            
            if send_response_value:
            
                chat_response = path[redeem_reward_name]['chat_response']
                
                try:
                    response_redus = replace_all(chat_response, aliases)
                    smt.send_message(response_redus,'RESPONSE')
                except:
                    smt.send_message(chat_response,'RESPONSE')
        else:
            giveaway_disabled_message = messages_data['response_giveaway_disabled']
            smt.send_message(giveaway_disabled_message,'RESPONSE')

    eventos = {
        'SOUND' : playsound, 
        'SCENE' : changescene, 
        'MESSAGE' : sendmessage, 
        'FILTER' : changefilter, 
        'KEYPRESS' : keypress, 
        'SOURCE' : source, 
        'CLIP': clip, 
        'TTS' : playtts, 
        'COUNTER': add_counter, 
        'GIVEAWAY': add_giveaway
    }
    
    if TOKEN and TOKENBOT:
        if redeem_reward_name in path.keys():
            redeem_type = path[redeem_reward_name]['TYPE']
            if redeem_type in eventos:
                eventos[redeem_type]()
    
def new_event_top():
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()

    if TOKEN and TOKENBOT:

        new_event_top = customtkinter.CTkToplevel(app)
        new_event_top.title(f"RewardEvents - {lang_data['events_add_title_page']} ")
        new_event_top.iconbitmap("src/icon.ico")
        new_event_top.attributes('-topmost', 'true')
        new_event_top.anchor("center")
        
        def new_sound():

            topsound = customtkinter.CTkToplevel(app)
            topsound.title(f"RewardEvents - { lang_data['event_sound_title'] }")
            topsound.iconbitmap("src/icon.ico")
            topsound.attributes('-topmost', 'true')
                
        
            def select_file():

                global filename

                filetypes = (
                    ('audio files', '*.mp3'),
                    ('All files', '*.*')
                )

                filename = fd.askopenfilename(
                    parent=topsound,
                    title=lang_data['audio_file'],
                    initialdir='src/files',
                    filetypes=filetypes)
                
                path_text.set(filename)
            
            def create_new_sound():
                
                title = redeem_title.get()
                command_event = command_entry.get()
                audio_dir = redeem_path.get()
                chat_response = chat_response_entry.get()
                user_level_check = user_level_switch.get()
                
                if not [x for x in (title, audio_dir) if x is None]:
                    try:
                        if chat_response == "":

                            send_response = 0
 
                        else:
                            send_response = 1
                            
                        old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                        new_data = json.load(old_data)

                        new_data[title] = {
                                            'TYPE': 'SOUND',
                                            'PATH': audio_dir,
                                            'COMMAND': command_event.lower(), 
                                            'send_response': send_response, 
                                            'chat_response':chat_response
                                        }
                        old_data.close()

                        old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                        json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)
                        
                        if command_event != "":

                            old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                            new_data_command = json.load(old_data_command)
                            
                            if user_level_check:
                                user_level_data = "mod"
                            else:
                                user_level_data = ""
                            
                            new_data_command[command_event.lower()] = {'RECOMPENSA': title,'user_level':user_level_data}
                            old_data.close()
                            
                            old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                            json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                        
                        error_label.configure(text=lang_data['event_success_create'])
                            
                    except:
                        error_label.configure(text=lang_data['event_error_create'])
                else:
                    error_label.configure(text=lang_data['event_empty_data'])
        
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
                
            tittle_redeem = customtkinter.CTkLabel(topsound, text= lang_data['event_sound_label'], text_font=("default_theme","15"))
            tittle_redeem.grid(row=0, column=0, columnspan=2, pady=20,)

            redeem_title_label = customtkinter.CTkLabel(topsound, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label.grid(row=1,column=0,padx=20,pady=10,sticky='W')
            
            redeem_title = customtkinter.CTkComboBox(topsound,values=list(messages_combox),width=200)
            redeem_title.grid(row=1,column=1 ,padx=20, pady=10)
            
            command_label = customtkinter.CTkLabel(topsound, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,padx=20,pady=10,sticky='W')
            
            command_entry = customtkinter.CTkEntry(topsound,width=200)
            command_entry.grid(row=2, column=1,padx=20, pady=10)
            
            user_level_label = customtkinter.CTkLabel(topsound, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=20,pady=10, sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(topsound, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')

            redeem_path_label = customtkinter.CTkLabel(topsound, text= lang_data['audio_file'] , text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_path_label.grid(row=4,column=0, padx=20, pady=10,sticky='W')

            redeem_path = customtkinter.CTkEntry(topsound,width=200,textvariable=path_text,state=DISABLED)
            redeem_path.grid(row=4,column=1,padx=20,pady=(0,10))

            redeem_path_button = customtkinter.CTkButton(topsound,width=200, text= lang_data['select_file_button'], text_font=("default_theme","13"),command=select_file)
            redeem_path_button.grid(row=5,columnspan=2,padx=20, pady=10,sticky='WE')
            
            chat_response_label = customtkinter.CTkLabel(topsound,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=7,column=0, padx=20,pady=10, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(topsound,width=200)
            chat_response_entry.grid(row=7,column=1, padx=20, pady=10)

            submit_button = customtkinter.CTkButton(topsound,text= lang_data['save'],command = create_new_sound)
            submit_button.grid(row=8, column=1,padx=20, pady=(10,20), sticky='e')

            error_label = customtkinter.CTkLabel(topsound, text="", text_font=("default_theme","11"))
            error_label.grid(row=9, column=0, columnspan=2, pady=20)
            
            topsound.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            topsound.mainloop()
    
        def new_tts():
            
            toptts = customtkinter.CTkToplevel(app)
            toptts.title(f"RewardEvents -  {lang_data['event_tts_title']}")
            toptts.iconbitmap("src/icon.ico") 
            toptts.attributes('-topmost', 'true')
            
            def create_new_tts():
                
                title = redeem_title.get()
                command_event = command_entry.get()
                user_level_check = user_level_Switch.get()
                chat_response = chat_response_entry.get()
                characters = character_limit.get()

                if characters == "":
                    error_label.configure(text=lang_data['event_tts_character_error'])
                else:
                    if chat_response == "":
                        send_response = 0
                    else:
                        send_response = 1
                        
                    old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                    new_data = json.load(old_data)

                    new_data[title] = {
                        'TYPE': 'TTS',
                        'send_response':send_response, 
                        'chat_response':chat_response, 
                        'COMMAND':command_event.lower(),
                        'characters': characters
                        }

                    old_data.close()

                    old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                    json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)

                    if command_event != "":

                        old_data_command = open('src/config/prefix_tts.json' , 'r', encoding='utf-8') 
                        new_data_command = json.load(old_data_command)
                        
                        if user_level_check:
                            user_level_data = "mod"
                        else:
                            user_level_data = ""

                        new_data_command['command'] = command_event.lower()
                        new_data_command['redeem'] = title
                        new_data_command['user_level'] = user_level_data
                        
                        old_data.close()
                        
                        old_data_write_command = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
                        json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
                    
                    error_label.configure(text=lang_data['event_success_create'])

                    
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
                    
            tittleredeem1 = customtkinter.CTkLabel(toptts, text= lang_data['event_tts_label'], text_font=("default_theme","15"))
            tittleredeem1.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

            redeem_title_label = customtkinter.CTkLabel(toptts, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label.grid(row=1,column=0,padx=20,pady=10,sticky='W')

            redeem_title = customtkinter.CTkComboBox(toptts,values=list(messages_combox),width=200)
            redeem_title.grid(row=1,column=1 ,padx=20, pady=10)
            
            command_label = customtkinter.CTkLabel(toptts, text= lang_data['chat_command'] , text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,padx=20,pady=10,sticky='W')
            
            command_entry = customtkinter.CTkEntry(toptts,width=200)
            command_entry.grid(row=2, column=1,padx=20, pady=10)
            
            user_level_Switch_label = customtkinter.CTkLabel(toptts, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_Switch_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
            
            user_level_Switch = customtkinter.CTkSwitch(toptts, text="", text_font=("default_theme", "13"),)
            user_level_Switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')
            
            caracter_limit_label = customtkinter.CTkLabel(toptts, text= lang_data['character_limit'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            caracter_limit_label.grid(row=4,column=0,padx=20,pady=10,sticky='W')
            
            character_limit = customtkinter.CTkEntry(toptts,width=200)
            character_limit.grid(row=4, column=1,padx=20, pady=10, sticky='e')
            
            chat_response_label = customtkinter.CTkLabel(toptts,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=7,column=0, padx=20,pady=10, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(toptts,width=200)
            chat_response_entry.grid(row=7,column=1, padx=20, pady=10)

            submit_buttom = customtkinter.CTkButton(toptts,text=lang_data['save'],command = create_new_tts)
            submit_buttom.grid(row=8, column=1,padx=20, pady=(10,30), sticky='e')

            error_label = customtkinter.CTkLabel(toptts, text="", text_font=("default_theme","11"))
            error_label.grid(row=9, column=0, columnspan=2, pady=20)

            toptts.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            toptts.mainloop()
                    
        def new_scene():
            
            top_scene = customtkinter.CTkToplevel(app)
            top_scene.title(f"RewardEvents - {lang_data['event_obs_screen_title']}")
            top_scene.iconbitmap("src/icon.ico")
            top_scene.attributes('-topmost', 'true')
            
            def create_scene():
                
                title_redeem = redeem_title1.get()
                current_scene_name = scene_entry_current.get()
                scene_name = scene_entry.get()
                time_to_change = time_scene_entry.get()
                command_event = command_entry.get()
                chat_response = chat_response_entry.get()
                return_scene_value = return_scene_switch.get()
                user_level_check = user_level_switch.get()

                if not [x for x in (title_redeem, current_scene_name, scene_name) if x is None]:
                    
                    try:
                        if chat_response == "":

                            send_response = 0

                        else:
                            send_response = 1
                            
                        if user_level_check:

                            user_level_data = "mod"
                        else:

                            user_level_data = ""
                            
                        old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                        new_data = json.load(old_data)

                        new_data[title_redeem] = {
                            'TYPE': 'SCENE',
                            'SCENENAME': scene_name,
                            'send_response':send_response,
                            'COMMAND': command_event.lower(),
                            'chat_response':chat_response,
                            'return_scene':return_scene_value,
                            'TIME':time_to_change,
                            'CURRENTSCENENAME': current_scene_name
                            }

                        old_data.close()

                        old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                        json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)
                        
                        if command_event != "":

                            old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                            new_data_command = json.load(old_data_command)
                            
                            new_data_command[command_event.lower()] = {'RECOMPENSA': title_redeem,'user_level': user_level_data}
                            old_data.close()
                            
                            old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                            json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                        
                        
                        error_label.configure(text= lang_data['event_success_create'])
                    except:
                        error_label.configure(text= lang_data['event_error_create'])
                else:
                    error_label.configure(text= lang_data['event_empty_data'])

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
            
            def update_scene():

                scenes = obs_con.get_scenes()
                
                if not scenes:
                    scene_entry_current.configure(values= [f"{ lang_data['obs_disconnected'] }"])
                    scene_entry.configure(values= [f"{ lang_data['obs_disconnected'] }"])
                else:
                    scene_entry_current.configure(values=list(scenes))
                    scene_entry.configure(values=list(scenes))

            messages_combox = update_titles_combox()
            obs_font_variable = customtkinter.StringVar(value= lang_data['obs_select_scene']) 
            obs_font_variable_scene = customtkinter.StringVar(value= lang_data['obs_select_scene'])  
                        
            tittleredeem1 = customtkinter.CTkLabel(top_scene, text= lang_data['event_obs_screen_label'], text_font=("default_theme","15"))
            tittleredeem1.grid(row=0, column=0, columnspan=2, pady=20)

            redeem_title_label1 = customtkinter.CTkLabel(top_scene, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label1.grid(row=1,column=0,padx=20,pady=10,sticky='W')

            redeem_title1 = customtkinter.CTkComboBox(top_scene,values=list(messages_combox),width=200)
            redeem_title1.grid(row=1,column=1 ,padx=20, pady=10)
            
            command_label = customtkinter.CTkLabel(top_scene, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,padx=20,pady=10,sticky='W')
            
            command_entry = customtkinter.CTkEntry(top_scene,width=200)
            command_entry.grid(row=2, column=1,padx=20, pady=10)
            
            user_level_label = customtkinter.CTkLabel(top_scene, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(top_scene, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')

            scene_label_current = customtkinter.CTkLabel(top_scene,text= lang_data['event_obs_screen_atual'],text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            scene_label_current.grid(row=4,column=0, padx=20,pady=10, sticky='W')

            scene_entry_current = customtkinter.CTkOptionMenu(top_scene,values= lang_data['obs_select_scene'], variable=obs_font_variable, width=200)
            scene_entry_current.grid(row=4,column=1, padx=20, pady=10)

            scene_label = customtkinter.CTkLabel(top_scene,text= lang_data['event_obs_screen_change'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            scene_label.grid(row=5,column=0, padx=20, pady=10, sticky='W')

            scene_entry = customtkinter.CTkOptionMenu(top_scene,values= lang_data['obs_select_scene'], width=200,variable=obs_font_variable_scene)
            scene_entry.grid(row=5,column=1, padx=20, pady=10)
            
            return_scene = customtkinter.CTkLabel(top_scene, text= lang_data['event_obs_screen_return_ask'], text_font=("default_theme","13"))
            return_scene.grid(row=6, column=0, padx=20, pady=10, sticky='w')

            return_scene_switch = customtkinter.CTkSwitch(top_scene, text=" ",)
            return_scene_switch.grid(row=6, column=1, padx=20, pady=10, sticky='e')

            time_scene_label = customtkinter.CTkLabel(top_scene,text= lang_data['event_obs_screen_return_time'], text_font=("default_theme","13"),anchor="center", justify=CENTER)
            time_scene_label.grid(row=7,column=0, padx=20, pady=10, sticky='W')

            time_scene_entry = customtkinter.CTkEntry(top_scene,width=200)
            time_scene_entry.grid(row=7,column=1, padx=20, pady=10)

            chat_response_label = customtkinter.CTkLabel(top_scene,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=8,column=0, padx=20,pady=10, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(top_scene,width=200)
            chat_response_entry.grid(row=8,column=1, padx=20, pady=10)
            
            submit_buttom3 = customtkinter.CTkButton(top_scene,text=lang_data['save'],command = create_scene)
            submit_buttom3.grid(row=9, column=1,padx=20, pady=(10,20), sticky='e')

            error_label = customtkinter.CTkLabel(top_scene, text="", text_font=("default_theme","11"))
            error_label.grid(row=10, column=0, columnspan=2, pady=20)
            
            update_scene()

            top_scene.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            top_scene.mainloop()
            
        def new_message():
            
            new_message_top = customtkinter.CTkToplevel(app)
            new_message_top.title(f"RewardEvents - {lang_data['chat_response_title']}")
            new_message_top.iconbitmap("src/icon.ico")
            new_message_top.attributes('-topmost', 'true')
            
            def create_message():
            
                title = redeem_title2.get()
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

                        new_data[title] = {
                            'TYPE': 'MESSAGE', 
                            'COMMAND': command_event.lower(), 
                            'chat_response': message
                            }

                        old_data.close()

                        old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                        json.dump(new_data, old_data_write, indent = 4, ensure_ascii=False)
                        

                        if command_event != "":

                            old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                            new_data_command = json.load(old_data_command)
                            
                            new_data_command[command_event.lower()] = {
                                            'RECOMPENSA': title,
                                            'user_level': user_level_data
                                            }

                            old_data.close()
                            
                            old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                            json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
                        
                        error_label.configure(text=lang_data['event_success_create'])

                    except:

                        error_label.configure(text=lang_data['event_error_create'])
                else:
                    error_label.configure(text=lang_data['event_empty_data'])
            
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
                    
            tittleredeem2 = customtkinter.CTkLabel(new_message_top, text= lang_data['chat_response_label'], text_font=("default_theme","15"))
            tittleredeem2.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

            redeem_title_label2 = customtkinter.CTkLabel(new_message_top, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label2.grid(row=1,column=0,pady=10,padx=10,sticky='W')

            redeem_title2 = customtkinter.CTkComboBox(new_message_top,values=list(messages_combox),width=200)
            redeem_title2.grid(row=1,column=1 ,padx=10, pady=10)
            
            command_label = customtkinter.CTkLabel(new_message_top, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,pady=10,padx=10,sticky='W')
            
            command_entry = customtkinter.CTkEntry(new_message_top,width=200)
            command_entry.grid(row=2, column=1,padx=10, pady=10)
            
            user_level_label = customtkinter.CTkLabel(new_message_top, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=10,pady=10,sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(new_message_top, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')

            message_label = customtkinter.CTkLabel(new_message_top,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            message_label.grid(row=4,column=0, padx=10,pady=10, sticky='W')

            message_entry = customtkinter.CTkEntry(new_message_top,width=200)
            message_entry.grid(row=4,column=1, padx=10, pady=10)

            submit_buttom4 = customtkinter.CTkButton(new_message_top,text=lang_data['save'],command = create_message)
            submit_buttom4.grid(row=5, column=1,padx=20, pady=(10,20), sticky='e')

            error_label = customtkinter.CTkLabel(new_message_top, text="", text_font=("default_theme","11"))
            error_label.grid(row=6, column=0, columnspan=2, pady=20)
            
            new_message_top.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            new_message_top.mainloop()
            
        def new_filter():
            
            new_filter_top = customtkinter.CTkToplevel(app)
            new_filter_top.title(f"RewardEvents - {lang_data['obs_filter_title']}")
            new_filter_top.iconbitmap("src/icon.ico")
            new_filter_top.attributes('-topmost', 'true')
                    
            def create_new_filter():
                
                title = redeem_title3.get()
                filter_name = obs_filter_entry.get()
                source_name = obs_source_entry.get()
                time_showing = time_filter_entry.get()
                command_event = command_entry.get()
                chat_response = chat_response_entry.get()
                user_level_check = user_level_switch.get()
                
                if not [x for x in (title, filter_name,source_name,time_showing) if x is None]:
                    try:
                        
                        if chat_response == "":
                            send_response = 0
                        else:
                            send_response = 1
                        
                        if user_level_check:
                            user_level_data = "mod"
                        else:
                            user_level_data = ""    
                            
                        old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                        new_data = json.load(old_data)

                        new_data[title] = {
                            'TYPE': 'FILTER',
                            'SOURCE': source_name, 
                            'send_response':send_response, 
                            'chat_response':chat_response, 
                            'COMMAND': command_event.lower(), 
                            'FILTER':filter_name, 
                            'TIME':time_showing
                            }
                        old_data.close()

                        old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                        json.dump(new_data, old_data_write, indent = 4, ensure_ascii=False)
                        
                        if command_event != "":

                            old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                            new_data_command = json.load(old_data_command)

                            new_data_command[command_event.lower()] = {'RECOMPENSA': title,'user_level': user_level_data}
                            old_data.close()

                            old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                            json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                        
                        
                        error_label.configure(text= lang_data['event_success_create'])
                    except:
                        error_label.configure(text= lang_data['event_error_create'])
                else:
                    error_label.configure(text= lang_data['event_empty_data'])         

            def update_filter(source):
                
                filters = obs_con.get_filter_source(source)
                
                if not filters:
                    obs_filter_entry.configure(values= [f"{ lang_data['obs_empty_filter'] }"])
                else:
                    obs_filter_entry.configure(values=list(filters))

            def update_source():
                
                sources = obs_con.get_sources()
                
                if not sources:
                    obs_source_entry.configure(values= [f"{ lang_data['obs_disconnected'] }"])
                else:
                    obs_source_entry.configure(values=list(sources))
                    
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
                
            obs_font_variable = customtkinter.StringVar(value= lang_data['obs_select_source'])  
            obs_filter_variable = customtkinter.StringVar(value= lang_data['obs_filter_source']) 

            tittleredeem3 = customtkinter.CTkLabel(new_filter_top, text= lang_data['obs_filter_label'], text_font=("default_theme","15"))
            tittleredeem3.grid(row=0, column=0, columnspan=2, pady=20)

            redeem_title_label3 = customtkinter.CTkLabel(new_filter_top, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label3.grid(row=1,column=0, padx=20, pady=10, sticky='W')

            redeem_title3 = customtkinter.CTkComboBox(new_filter_top,values=list(messages_combox),width=200)
            redeem_title3.grid(row=1,column=1 ,padx=10, pady=10)
            
            command_label = customtkinter.CTkLabel(new_filter_top, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2, column=0, padx=20, pady=10, sticky='W')

            command_entry = customtkinter.CTkEntry(new_filter_top,width=200)
            command_entry.grid(row=2, column=1,padx=20, pady=10)
            
            user_level_label = customtkinter.CTkLabel(new_filter_top, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(new_filter_top, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')

            obs_source_label = customtkinter.CTkLabel(new_filter_top,text= lang_data['obs_source'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            obs_source_label.grid(row=4, column=0, padx=20, pady=10, sticky='W')

            obs_source_entry = customtkinter.CTkOptionMenu(new_filter_top,values= lang_data['obs_select_source'],variable=obs_font_variable, width=200, dynamic_resizing=True,command=update_filter)
            obs_source_entry.grid(row=4, column=1, padx=20, pady=10)

            obs_filter_label = customtkinter.CTkLabel(new_filter_top,text= lang_data['obs_filter_source'], text_font=("default_theme","13"),anchor="center", justify=CENTER)
            obs_filter_label.grid(row=5, column=0, padx=20, pady=10, sticky='W')

            obs_filter_entry = customtkinter.CTkOptionMenu(new_filter_top, values=[f"{lang_data['obs_select_source']}"],variable=obs_filter_variable, width=200, dynamic_resizing=True)
            obs_filter_entry.grid(row=5,column=1, padx=20, pady=10)

            time_filter_label = customtkinter.CTkLabel(new_filter_top,text= lang_data['obs_filter_time'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            time_filter_label.grid(row=6,column=0, padx=20,pady=10, sticky='W')

            time_filter_entry = customtkinter.CTkEntry(new_filter_top,width=200)
            time_filter_entry.grid(row=6,column=1, padx=20, pady=10)
            
            chat_response_label = customtkinter.CTkLabel(new_filter_top,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=7,column=0, padx=20,pady=10, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(new_filter_top,width=200)
            chat_response_entry.grid(row=7,column=1, padx=20, pady=10)

            submit_buttom5 = customtkinter.CTkButton(new_filter_top,text=lang_data['save'],command = create_new_filter)
            submit_buttom5.grid(row=8, column=1,padx=20, pady=(10,20), sticky='e')

            error_label = customtkinter.CTkLabel(new_filter_top, text="", text_font=("default_theme","11"))
            error_label.grid(row=9, column=0, columnspan=2, pady=20)

            update_source()
            new_filter_top.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            
            new_filter_top.mainloop()
            
        def new_key():
            
            new_key_top = customtkinter.CTkToplevel(app)
            new_key_top.title(f"RewardEvents - {lang_data['shortcut_title']}")
            new_key_top.iconbitmap("src/icon.ico")
            new_key_top.attributes('-topmost', 'true')
            
            def create_new_key():
                
                title = redeem_title4.get()
                command_event = command_entry.get()
                chat_response = chat_response_entry.get()
                user_level_check = user_level_switch.get()

                press_again = press_again_switch.get()
                time_press = time_press_entry.get()
                
                repeat_ask = repeat_press_switch.get()
                repeat_times = repeat_times_press_entry.get()
                repeat_interval = repeat_interval_press_entry.get()

                keep_ask = keep_press_switch.get()
                keep_time = keep_press_time_entry.get()

                key1 = combobox1.get()
                key2 = combobox2.get()
                key3 = combobox3.get()
                key4 = combobox4.get()

                list_check_times = [time_press, repeat_times, repeat_interval, keep_time]

                if all(str(value).isdigit() or value == '' for value in list_check_times):

                    if chat_response == "":
                        send_response = 0
                    else:
                        send_response = 1
                        
                    if user_level_check:
                        user_level_data = "mod"
                    else:
                        user_level_data = ""

                    if time_press != '':
                        time_press_int = int(time_press)
                    else:
                        time_press_int = time_press
                    
                    if repeat_times != '':
                        repeat_times_int = int(repeat_times)
                    else:
                        repeat_times_int = repeat_times

                    if repeat_interval != '':
                        repeat_interval_int = int(repeat_interval)
                    else:
                        repeat_interval_int = repeat_interval
                    
                    if keep_time != '':
                        keep_time_int = int(keep_time)
                    else:
                        keep_time_int = keep_time

                        
                    key_data_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                    key_data = json.load(key_data_file)

                    key_data[title] = {
                        'TYPE': 'KEYPRESS',
                        'press_again': press_again,
                        'repeat': repeat_ask,
                        'keep': keep_ask,
                        'time_press' : time_press_int,
                        'repeat_times': repeat_times_int,
                        'repeat_interval': repeat_interval_int,
                        'keep_time' : keep_time_int,
                        'send_response': send_response, 
                        'chat_response': chat_response,
                        'COMMAND': command_event.lower(), 
                        'KEY1': key1, 
                        'KEY2': key2, 
                        'KEY3': key3, 
                        'KEY4': key4
                        }

                    key_data_file.close()

                    key_data_file_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                    json.dump(key_data, key_data_file_write, indent = 4, ensure_ascii=False)


                    if command_event != "":

                        old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                        new_data_command = json.load(old_data_command)

                        new_data_command[command_event.lower()] = {'RECOMPENSA': title,'user_level': user_level_data}
                        old_data_command.close()

                        old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                        json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                    
                    
                    error_label.configure(text=lang_data['event_success_create'])

                else:

                    error_label.configure(text=lang_data['shortcut_value_not_digit'])  

            def switch_choice_press():
                repeat_press_switch.deselect()
                keep_press_switch.deselect()

            def switch_choice_repeat():
                press_again_switch.deselect()
                keep_press_switch.deselect()

            def switch_choice_keep():
                repeat_press_switch.deselect()
                press_again_switch.deselect()

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
            
            
            shortcuts_title = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_label'], text_font=("default_theme","15"))
            shortcuts_title.grid(row=0, column=0, columnspan=4, padx=20, pady=20)


            redeem_title_label4 = customtkinter.CTkLabel(new_key_top, text= lang_data['redeem_marked'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            redeem_title_label4.grid(row=1, column=0, columnspan=2, pady=5, padx=20, sticky='W')

            redeem_title4 = customtkinter.CTkComboBox(new_key_top,values=list(messages_combox),width=200)
            redeem_title4.grid(row=1, column=2, columnspan=2, padx=20, pady=5)

            
            command_label = customtkinter.CTkLabel(new_key_top, text= lang_data['chat_command'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0, columnspan=2, padx=20, pady=5, sticky='W')

            command_entry = customtkinter.CTkEntry(new_key_top,width=200)
            command_entry.grid(row=2, column=2, columnspan=2, padx=20, pady=5)

            chat_response_label = customtkinter.CTkLabel(new_key_top,text= lang_data['chat_message_label'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=3,column=0, columnspan=2, padx=20, pady=5, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(new_key_top,width=200)
            chat_response_entry.grid(row=3,column=2, columnspan=2, padx=5, pady=10)

            user_level_label = customtkinter.CTkLabel(new_key_top, text= lang_data['moderator_ask_label'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(5,20), sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(new_key_top, text="")
            user_level_switch.grid(row=4, column=2, columnspan=2, padx=20, pady=(5,20), sticky='e')

            
            press_again_switch_label = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_press_again_ask'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            press_again_switch_label.grid(row=5, column=0, columnspan=2, padx=20, pady=(20,5), sticky='W')
            
            press_again_switch = customtkinter.CTkSwitch(new_key_top, text="",command=switch_choice_press)
            press_again_switch.grid(row=5, column=2, columnspan=2,padx=20, pady=(20,5), sticky='e')

            time_press = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_press_again_time'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            time_press.grid(row=6,column=0, columnspan=2, padx=20, pady=(5,20), sticky='W')

            time_press_entry = customtkinter.CTkEntry(new_key_top,width=200)
            time_press_entry.grid(row=6, column=2, columnspan=2, padx=20, pady=(5,20))



            repeat_press_switch_label = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_repeat_press_ask'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            repeat_press_switch_label.grid(row=7, column=0, columnspan=2, padx=20, pady=(20,5), sticky='W')
            
            repeat_press_switch = customtkinter.CTkSwitch(new_key_top, text="",command=switch_choice_repeat)
            repeat_press_switch.grid(row=7, column=2, columnspan=2,padx=20, pady=(20,5), sticky='e')

            repeat_times_press = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_repeat_times'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            repeat_times_press.grid(row=8, column=0, columnspan=2, padx=20, pady=5, sticky='W')

            repeat_times_press_entry = customtkinter.CTkEntry(new_key_top, width=200)
            repeat_times_press_entry.grid(row=8, column=2, columnspan=2,padx=5, pady=10)

            repeat_interval_press = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_repeat_interval'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            repeat_interval_press.grid(row=9, column=0, columnspan=2, padx=20, pady=(5,20), sticky='W')

            repeat_interval_press_entry = customtkinter.CTkEntry(new_key_top, width=200)
            repeat_interval_press_entry.grid(row=9, column=2, columnspan=2, padx=20, pady=(5,20))



            keep_press_switch_label = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_keep_press_ask'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            keep_press_switch_label.grid(row=10, column=0, columnspan=2, padx=20, pady=(20,5), sticky='W')

            keep_press_switch = customtkinter.CTkSwitch(new_key_top, text="",command=switch_choice_keep)
            keep_press_switch.grid(row=10, column=2, columnspan=2,padx=20, pady=(20,5), sticky='e')

            keep_press_time = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_keep_press_time'], text_font=("default_theme","12"),anchor="w", justify=RIGHT)
            keep_press_time.grid(row=11,column=0, columnspan=2, padx=20, pady=(5,10), sticky='W')

            keep_press_time_entry = customtkinter.CTkEntry(new_key_top,width=200)
            keep_press_time_entry.grid(row=11, column=2, columnspan=2,padx=10, pady=(5,10))



            selectkeys = customtkinter.CTkLabel(new_key_top, text= lang_data['shortcut_select_keys'], text_font=("default_theme","13"))
            selectkeys.grid(row=12, column=0, columnspan=4, padx=20, pady=20)


            combobox1 = customtkinter.CTkComboBox(new_key_top,values=["ctrl","NONE"],width=100)
            combobox1.grid(row=13,column=0, columnspan=4, padx=20, pady=10, sticky='w')

            combobox2 = customtkinter.CTkComboBox(new_key_top,values=["shift","alt","space","NONE"],width=100)
            combobox2.grid(row=13,column=0, columnspan=4, padx=(30,200), pady=10)

            combobox3 = customtkinter.CTkComboBox(new_key_top,values=["1","2","3","4","5","6","7","8","9","NONE"],width=100)
            combobox3.grid(row=13,column=0, columnspan=4, padx=(200,30), pady=10)

            combobox4 = customtkinter.CTkComboBox(new_key_top,width=100,
                                                values=["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","ç","z","x","c","v","b","n","m","NONE"])
            combobox4.grid(row=13,column=0, columnspan=4, padx=20, pady=10, sticky='e')

            
            error_label = customtkinter.CTkLabel(new_key_top, text="", text_font=("default_theme","11"))
            error_label.grid(row=14, column=0, columnspan=2, pady=20)

            submit_buttom6 = customtkinter.CTkButton(new_key_top,text=lang_data['save'],command = create_new_key)
            submit_buttom6.grid(row=14, column=2,columnspan=2, padx=20, pady=20, sticky='e')
            
            new_key_top.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            new_key_top.mainloop()
            
        def new_source():
            
            new_source_top = customtkinter.CTkToplevel(app)
            new_source_top.title(f"RewardEvents - {lang_data['obs_source_title']}")
            new_source_top.iconbitmap("src/icon.ico")
            new_source_top.attributes('-topmost', 'true')
            
            
            def create_new_source():
                
                title = redeem_title5.get()
                source_name = obs_source_entry_source.get()
                time_showing = time_filter_entry_source.get()
                command_event = command_entry.get()
                chat_response = chat_response_entry.get()
                user_level_check = user_level_switch.get()
                
                if time_showing != "":

                    if time_showing.isdigit():

                        if chat_response == "":
                            send_response = 0
                        else:
                            send_response = 1
                            
                        if user_level_check:
                            user_level_data = "mod"
                        else:
                            user_level_data = ""
                            
                        old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                        new_data = json.load(old_data)

                        new_data[title] = {
                            'TYPE': 'SOURCE',
                            'send_response':send_response, 
                            'chat_response':chat_response,
                            'COMMAND': command_event.lower(), 
                            'SOURCENAME': source_name,
                            'TIME': int(time_showing)
                            }

                        old_data.close()

                        old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                        json.dump(new_data, old_data_write, indent = 4 ,ensure_ascii=False)
                        old_data_write.close()
                        
                        if command_event != "":

                            old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                            new_data_command = json.load(old_data_command)

                            new_data_command[command_event.lower()] = {
                                'RECOMPENSA': title,
                                'user_level': user_level_data
                                }
                            old_data.close()

                            old_data_write_command = open('src/config/commands.json' , 'w', encoding='utf-8') 
                            json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
                        
                        error_label.configure(text= lang_data['event_success_create'])
                    else:
                        error_label.configure(text= lang_data['event_digit'])
                else:
                    error_label.configure(text= lang_data['event_empty_data']) 

            def update_source():
                
                sources = obs_con.get_sources()
                
                if not sources:
                    obs_source_entry_source.configure(values= [f"{ lang_data['obs_disconnected'] }"])
                else:
                    obs_source_entry_source.configure(values=list(sources))

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

            obs_font_variable = customtkinter.StringVar(value= lang_data['obs_select_source'])  
            
            tittleredeem5 = customtkinter.CTkLabel(new_source_top, text= lang_data['obs_source_label'], text_font=("default_theme","15"))
            tittleredeem5.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

            redeem_title_label5 = customtkinter.CTkLabel(new_source_top, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label5.grid(row=1,column=0,pady=10,padx=20,sticky='W')

            redeem_title5 = customtkinter.CTkComboBox(new_source_top,values=list(messages_combox),width=200)
            redeem_title5.grid(row=1,column=1 ,padx=10, pady=10)
            
            command_label = customtkinter.CTkLabel(new_source_top, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,pady=10,padx=20,sticky='W')

            command_entry = customtkinter.CTkEntry(new_source_top,width=200)
            command_entry.grid(row=2, column=1,padx=10, pady=10)
            
            user_level_label = customtkinter.CTkLabel(new_source_top, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(new_source_top, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')

            obs_source_label_source = customtkinter.CTkLabel(new_source_top,text= lang_data['obs_source'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            obs_source_label_source.grid(row=4,column=0, padx=20,pady=10, sticky='W')

            obs_source_entry_source = customtkinter.CTkOptionMenu(new_source_top,values=lang_data['obs_select_source'],variable=obs_font_variable, width=200, dynamic_resizing=True)
            obs_source_entry_source.grid(row=4,column=1, padx=20, pady=10)

            time_filter_label = customtkinter.CTkLabel(new_source_top,text=lang_data['obs_source_time'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            time_filter_label.grid(row=5,column=0, padx=20,pady=10, sticky='W')

            time_filter_entry_source = customtkinter.CTkEntry(new_source_top,width=200)
            time_filter_entry_source.grid(row=5,column=1, padx=20, pady=10)
            
            chat_response_label = customtkinter.CTkLabel(new_source_top,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=6,column=0, padx=20,pady=10, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(new_source_top,width=200)
            chat_response_entry.grid(row=6,column=1, padx=20, pady=10)

            submit_buttom6 = customtkinter.CTkButton(new_source_top,text=lang_data['save'],command = create_new_source)
            submit_buttom6.grid(row=7, column=1,padx=20, pady=(10,20), sticky='e')

            error_label = customtkinter.CTkLabel(new_source_top, text="", text_font=("default_theme","11"))
            error_label.grid(row=8, column=0, columnspan=2, pady=20)

            update_source()

            new_source_top.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            new_source_top.mainloop()
        
        def new_clip():
            
            new_clip_top = customtkinter.CTkToplevel(app)
            new_clip_top.title(f"RewardEvents - {lang_data['clip_event_title']}")
            new_clip_top.iconbitmap("src/icon.ico")
            new_clip_top.attributes('-topmost', 'true')
            
            def create_new_clip():
                
                title = redeem_title6.get()
                command_event = command_entry.get()
                user_level_check = user_level_switch.get()

                try:
                    if user_level_check:
                        
                        user_level_data = "mod"
                        
                    else:
                        user_level_data = ""
                        
                    old_data = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
                    new_data = json.load(old_data)

                    new_data[title] = {'TYPE': 'CLIP','COMMAND': command_event.lower(),}
                    old_data.close()

                    old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                    json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)

                    if command_event != "":
                    
                        old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                        new_data_command = json.load(old_data_command)

                        new_data_command[command_event.lower()] = {

                            'RECOMPENSA': title,
                            'user_level': user_level_data

                            }

                        old_data.close()

                        old_data_write_command = open('src/config/commands.json' , 'w') 
                        json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                    
                    error_label.configure(text= lang_data['event_success_create'])
                except:
                    error_label.configure(text= lang_data['event_empty_data'])  

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

            tittleredeem6 = customtkinter.CTkLabel(new_clip_top, text= lang_data['clip_event_label'], text_font=("default_theme","15"))
            tittleredeem6.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

            redeem_title_label6 = customtkinter.CTkLabel(new_clip_top, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label6.grid(row=1,column=0,pady=20,padx=20,sticky='W')

            redeem_title6 = customtkinter.CTkComboBox(new_clip_top,values=list(messages_combox),width=200)
            redeem_title6.grid(row=1,column=1 ,padx=20, pady=20)
            
            command_label = customtkinter.CTkLabel(new_clip_top, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,pady=20,padx=20,sticky='W')

            command_entry = customtkinter.CTkEntry(new_clip_top,width=200)
            command_entry.grid(row=2, column=1, pady=20,padx=20)
            
            user_level_label = customtkinter.CTkLabel(new_clip_top, text=lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(new_clip_top, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')

            submit_buttom7 = customtkinter.CTkButton(new_clip_top,text=lang_data['save'],command = create_new_clip)
            submit_buttom7.grid(row=4, column=1,padx=20, pady=20, sticky='e')

            error_label = customtkinter.CTkLabel(new_clip_top, text="", text_font=("default_theme","11"))
            error_label.grid(row=5, column=0, columnspan=2, pady=20)

            new_clip_top.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))

            new_clip_top.mainloop()
        
        def new_counter():
            
            new_counter_top = customtkinter.CTkToplevel(app)
            new_counter_top.title(f"RewardEvents - {lang_data['counter_new_title']}")
            new_counter_top.iconbitmap("src/icon.ico")
            new_counter_top.attributes('-topmost', 'true')
            
            def create_new_counter():
                
                title = redeem_title6.get()
                chat_response = chat_response_entry.get()
                command_event = command_entry.get()
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

                    new_data[title] = {
                        'TYPE': 'COUNTER',
                        'COMMAND': command_event.lower(),
                        'send_response':send_response, 
                        'chat_response':chat_response
                        }
                    old_data.close()

                    old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                    json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)

                    if command_event != "":
                    
                        old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                        new_data_command = json.load(old_data_command)

                        new_data_command[command_event] = {
                            'RECOMPENSA': title,
                            'user_level': user_level_data
                            }
                        old_data.close()

                        old_data_write_command = open('src/config/commands.json' , 'w') 
                        json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)

                    error_label.configure(text= lang_data['event_success_create'])

                except:

                    error_label.configure(text=lang_data['event_empty_data']) 

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

            tittleredeem6 = customtkinter.CTkLabel(new_counter_top, text= lang_data['counter_new_label'], text_font=("default_theme","15"))
            tittleredeem6.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

            redeem_title_label6 = customtkinter.CTkLabel(new_counter_top, text=lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label6.grid(row=1,column=0,pady=20,padx=20,sticky='W')

            redeem_title6 = customtkinter.CTkComboBox(new_counter_top,values=list(messages_combox),width=200)
            redeem_title6.grid(row=1,column=1 ,padx=20, pady=20)
            
            command_label = customtkinter.CTkLabel(new_counter_top, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,pady=20,padx=20,sticky='W')

            command_entry = customtkinter.CTkEntry(new_counter_top,width=200)
            command_entry.grid(row=2, column=1, pady=20,padx=20)
            
            user_level_label = customtkinter.CTkLabel(new_counter_top, text= lang_data['moderator_ask_label'] , text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(new_counter_top, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')
            
            chat_response_label = customtkinter.CTkLabel(new_counter_top,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=4,column=0, padx=20,pady=10, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(new_counter_top,width=200)
            chat_response_entry.grid(row=4,column=1, padx=20, pady=10)

            submit_buttom7 = customtkinter.CTkButton(new_counter_top,text=lang_data['save'],command = create_new_counter)
            submit_buttom7.grid(row=5, column=1,padx=20, pady=20, sticky='e')

            error_label = customtkinter.CTkLabel(new_counter_top, text="", text_font=("default_theme","11"))
            error_label.grid(row=10, column=0, columnspan=2, pady=20)

            new_counter_top.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))
            new_counter_top.mainloop()
    
        def new_giveaway():

            new_giveaway_top = customtkinter.CTkToplevel(app)
            new_giveaway_top.title(f"RewardEvents - {lang_data['giveaway_new_title']}")
            new_giveaway_top.iconbitmap("src/icon.ico")
            new_giveaway_top.attributes('-topmost', 'true')
            
            def create_new_giveaway():
                
                title = redeem_title6.get()
                chat_response = chat_response_entry.get()
                command_event = command_entry.get()
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

                    new_data[title] = {
                        'TYPE': 'giveaway',
                        'COMMAND': command_event.lower(),
                        'send_response':send_response, 
                        'chat_response':chat_response
                        }
                    old_data.close()

                    old_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
                    json.dump(new_data, old_data_write, indent = 4,ensure_ascii=False)
                    
                    old_data_command = open('src/config/commands.json' , 'r', encoding='utf-8') 
                    new_data_command = json.load(old_data_command)

                    new_data_command[command_event] = {
                        'RECOMPENSA': title,
                        'user_level': user_level_data
                        }
                    old_data.close()

                    old_data_write_command = open('src/config/commands.json' , 'w') 
                    json.dump(new_data_command, old_data_write_command , indent = 4,ensure_ascii=False)
                    

                    
                    error_label.configure(text=lang_data['event_success_create'])

                except:
                    error_label.configure(text=lang_data['event_error_create'])

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

            tittleredeem6 = customtkinter.CTkLabel(new_giveaway_top, text= lang_data['giveaway_new_label'], text_font=("default_theme","15"))
            tittleredeem6.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

            redeem_title_label6 = customtkinter.CTkLabel(new_giveaway_top, text= lang_data['redeem_marked'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            redeem_title_label6.grid(row=1,column=0,pady=20,padx=20,sticky='W')

            redeem_title6 = customtkinter.CTkComboBox(new_giveaway_top,values=list(messages_combox),width=200)
            redeem_title6.grid(row=1,column=1 ,padx=20, pady=20)
            
            command_label = customtkinter.CTkLabel(new_giveaway_top, text= lang_data['chat_command'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            command_label.grid(row=2,column=0,pady=20,padx=20,sticky='W')

            command_entry = customtkinter.CTkEntry(new_giveaway_top,width=200)
            command_entry.grid(row=2, column=1, pady=20,padx=20)
            
            user_level_label = customtkinter.CTkLabel(new_giveaway_top, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            user_level_label.grid(row=3,column=0,padx=20,pady=10,sticky='W')
            
            user_level_switch = customtkinter.CTkSwitch(new_giveaway_top, text="", text_font=("default_theme", "13"),)
            user_level_switch.grid(row=3, column=1,padx=20, pady=10, sticky='e')
            
            chat_response_label = customtkinter.CTkLabel(new_giveaway_top,text= lang_data['chat_message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
            chat_response_label.grid(row=4,column=0, padx=20,pady=10, sticky='W')

            chat_response_entry = customtkinter.CTkEntry(new_giveaway_top,width=200)
            chat_response_entry.grid(row=4,column=1, padx=20, pady=10)

            submit_buttom7 = customtkinter.CTkButton(new_giveaway_top,text=lang_data['save'],command = create_new_giveaway)
            submit_buttom7.grid(row=5, column=1,padx=20, pady=20, sticky='e')

            error_label = customtkinter.CTkLabel(new_giveaway_top, text="", text_font=("default_theme","11"))
            error_label.grid(row=6, column=0, columnspan=2, pady=20)

            new_giveaway_top.protocol("WM_DELETE_WINDOW", new_event_top.attributes('-topmost', 'true'))

            new_giveaway_top.mainloop()   
    
        def select_event_type():
            value_combox = events_combox.get()
            
            events_receive = {
                
            'Reproduzir Audio' : new_sound,
            'Texto falado google' : new_tts,
            'Mudar cena OBS' : new_scene,
            'Exibir/Ocultar Filtro OBS' : new_filter,
            'Exibir/Ocultar Fonte OBS' : new_source,
            'Atalho no teclado' : new_key,
            'Resposta no chat' : new_message,
            'Sorteio com recompensa': new_giveaway,
            'Contador': new_counter,
            'Criar um Clip': new_clip
            }
            
            if value_combox in events_receive:
                new_event_top.attributes('-topmost', 'false')
                events_receive[value_combox]()
        
        
        events_combox_list = ['Reproduzir Audio','Texto falado google','Mudar cena OBS','Exibir/Ocultar Filtro OBS',
                        'Exibir/Ocultar Fonte OBS','Atalho no teclado','Resposta no chat','Contador','Sorteio com recompensa','Criar um Clip']

        events_combox_label = customtkinter.CTkLabel(new_event_top, text= lang_data['events_add_select_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        events_combox_label.grid(row=1,column=0,padx=20,pady=(30,10),sticky='W')

        events_combox = customtkinter.CTkComboBox(new_event_top,values=events_combox_list,width=200)
        events_combox.grid(row=1,column=1 ,padx=20, pady=(30,10))
        
        select_event_buttom = customtkinter.CTkButton(new_event_top,text= lang_data['create'],text_font=("default_theme","13"), command=select_event_type)
        select_event_buttom.grid(row=2,column=1 ,padx=20, pady=(10,30),sticky='e')
        
        
        new_event_top.mainloop()
    
def del_event():
    
    del_event_top = customtkinter.CTkToplevel(app)
    del_event_top.title(f"RewardEvents - {lang_data['event_del_title']}")
    del_event_top.iconbitmap("src/icon.ico")
    
    def del_event_confirm():
        
        combox_key = combobox_events.get()
        
        data_event_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
        data_event = json.load(data_event_file)
        command_event_del_data = data_event[combox_key]['COMMAND']
        command_type_data = data_event[combox_key]['TYPE']
        
        data_event_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
        data_event = json.load(data_event_file)

        del data_event[combox_key]
        data_event_file.close()

        event_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(data_event, event_data_write, indent = 4, ensure_ascii=False)
        event_data_write.close()
        
        
        if command_event_del_data != "":
            
            if command_type_data == 'TTS':

                old_data_command = open('src/config/prefix_tts.json' , 'r', encoding='utf-8') 
                new_data_command = json.load(old_data_command)

                new_data_command['command'] = ''
                new_data_command['redeem'] = ''
                new_data_command['user_level'] = ''
                
                old_data_command.close()
                
                old_data_write_command = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
                json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)

            else:
                
                data_commands_events_file = open('src/config/commands.json' , 'r', encoding='utf-8') 
                data_commands_events = json.load(data_commands_events_file)

                del data_commands_events[command_event_del_data]
                data_commands_events_file.close()

                data_commands_events_write = open('src/config/commands.json' , 'w', encoding='utf-8') 
                json.dump(data_commands_events, data_commands_events_write, indent = 4, ensure_ascii=False)
                data_commands_events_write.close()
                

        error_label.configure(text=lang_data['event_success_del'])

            
        var_events = customtkinter.StringVar(value=lang_data['select_redeem'])
        
        events_data_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
        events_data = json.load(events_data_file)
        combobox_events.configure(values=list(events_data.keys()),variable=var_events)
    
    def event_info_update(combox_key):

        data_event_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
        data_event = json.load(data_event_file)

        command_event = data_event[combox_key]['COMMAND']
        if command_event == "":
            command_event = lang_data['event_del_no_command']

        response_event = data_event[combox_key]['chat_response']
        if response_event == "":
            response_event = lang_data['event_del_no_response']

        combox_key_title = customtkinter.StringVar(value= combox_key)
        title_redeem_content.configure(text= combox_key_title)

        command_redeem_val = customtkinter.StringVar(value= command_event)
        command_redeem_content.configure(text= command_redeem_val)

        message_content = customtkinter.StringVar(value= response_event)
        response_redeem_content.configure(textvariable= message_content)
        

    events_data_file = open('src/config/pathfiles.json' , 'r', encoding='utf-8') 
    events_data = json.load(events_data_file)

    var_events = customtkinter.StringVar(value= lang_data['select_redeem'])
    
    title_del = customtkinter.CTkLabel(del_event_top, text= lang_data['event_del_label'], text_font=("default_theme","15"))
    title_del.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
    
    select_label = customtkinter.CTkLabel(del_event_top, text= lang_data['select_redeem'], text_font=("default_theme","12"))
    select_label.grid(row=1, column=0, columnspan=2, padx=20, pady=10)
    
    combobox_events = customtkinter.CTkComboBox(del_event_top,values=list(events_data.keys()),variable=var_events,width=400,command=event_info_update)
    combobox_events.grid(row=2,column=0, columnspan=2,padx=10, pady=20)

    title_redeem_label = customtkinter.CTkLabel(del_event_top, text= lang_data['redeem'], text_font=("default_theme","12"),anchor="w", justify=LEFT)
    title_redeem_label.grid(row=4, column=0, padx=20, pady=10)

    title_redeem_content = customtkinter.CTkEntry(del_event_top, text="",width=250, text_font=("default_theme","12"),state=DISABLED)
    title_redeem_content.grid(row=4, column=1, padx=20, pady=10)

    command_redeem_label = customtkinter.CTkLabel(del_event_top, text= lang_data['command'], text_font=("default_theme","12"),anchor="w", justify=LEFT)
    command_redeem_label.grid(row=5, column=0, padx=20, pady=10)

    command_redeem_content = customtkinter.CTkEntry(del_event_top, text="",width=250, text_font=("default_theme","12"),state=DISABLED)
    command_redeem_content.grid(row=5, column=1, padx=20, pady=10)

    response_redeem_label = customtkinter.CTkLabel(del_event_top, text=lang_data['chat_message_label'], text_font=("default_theme","12"),anchor="w", justify=LEFT)
    response_redeem_label.grid(row=6, column=0, padx=20, pady=10)

    response_redeem_content = customtkinter.CTkEntry(del_event_top, text="",width=250, text_font=("default_theme","12"),state=DISABLED)
    response_redeem_content.grid(row=6, column=1, padx=20, pady=10)
    
    del_button = customtkinter.CTkButton(del_event_top,text= lang_data['del'] ,command = del_event_confirm)
    del_button.grid(row=7, column=0, columnspan=2, padx=20, pady=20)

    error_label = customtkinter.CTkLabel(del_event_top, text="", text_font=("default_theme","11"))
    error_label.grid(row=8, column=0, columnspan=2, pady=20)

    del_event_top.mainloop()

def new_simple_command():
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()

    if TOKEN and TOKENBOT:

        new_simple = customtkinter.CTkToplevel(app)
        new_simple.title(f"RewardEvents - {lang_data['simple_commands_new_title']}")
        new_simple.iconbitmap("src/icon.ico")
        new_simple.attributes('-topmost', 'true')
        
        def create_message():
        
            user_level_check = user_level_Switch_new_simple.get()
            message = message_entry_new_simple.get()
            command_event = command_entry_new_simple.get()

            old_data_command = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
            new_data_command = json.load(old_data_command)
            
            if user_level_check:
                user_level_data = "mod"
            else:
                user_level_data = ""
                
            new_data_command[command_event.lower()] = {'response': message, 'user_level': user_level_data}
            
            old_data_write_command = open('src/config/simple_commands.json' , 'w', encoding='utf-8') 
            json.dump(new_data_command, old_data_write_command , indent = 4, ensure_ascii=False)
            
            
            error_label.configure(text=lang_data['simple_commands_create_success'])
                      
        tittleredeem2_new_simple = customtkinter.CTkLabel(new_simple, text= lang_data['simple_commands_new_label'], text_font=("default_theme","15"))
        tittleredeem2_new_simple.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

        command_label_new_simple = customtkinter.CTkLabel(new_simple, text= lang_data['command'] , text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        command_label_new_simple.grid(row=2,column=0,pady=10,padx=10,sticky='W')
        
        command_entry_new_simple = customtkinter.CTkEntry(new_simple,width=200)
        command_entry_new_simple.grid(row=2, column=1,padx=10, pady=10)

        message_label_new_simple = customtkinter.CTkLabel(new_simple,text= lang_data['message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        message_label_new_simple.grid(row=3,column=0, padx=10,pady=10, sticky='W')

        message_entry_new_simple = customtkinter.CTkEntry(new_simple,width=200)
        message_entry_new_simple.grid(row=3,column=1, padx=10, pady=10)
        
        user_level_Switch_new_simple_label = customtkinter.CTkLabel(new_simple, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        user_level_Switch_new_simple_label.grid(row=4, column=0,  padx=10, pady=10, sticky='W')
        
        user_level_Switch_new_simple = customtkinter.CTkSwitch(new_simple, text="", text_font=("default_theme", "13"),)
        user_level_Switch_new_simple.grid(row=4, column=1, padx=10, pady=10, sticky='e')

        submit_buttom4_new_simple = customtkinter.CTkButton(new_simple,text=lang_data['save'],command = create_message)
        submit_buttom4_new_simple.grid(row=5, column=1,padx=10, pady=(10,20), sticky='e')

        error_label = customtkinter.CTkLabel(new_simple, text="", text_font=("default_theme","11"))
        error_label.grid(row=6, column=0, columnspan=2, pady=20)
        
        new_simple.mainloop()
    
    else:
        messagebox.showerror(lang_data['error'], lang_data['error_auth'])

def del_simple_command():
    
    del_simple = customtkinter.CTkToplevel(app)
    del_simple.title(f"RewardEvents - {lang_data['simple_commands_del_title']}")
    del_simple.iconbitmap("src/icon.ico")
    del_simple.attributes('-topmost', 'true')
    
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
            
            error_label.configure(text=lang_data['simple_commands_del_success'])
      
        except:
            error_label.configure(text=lang_data['simple_commands_del_error'])
        
        var_commands = customtkinter.StringVar(value= lang_data['simple_commands_select'])

        commands_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
        commands_list = json.load(commands_data_file)
        combobox_commands.configure(values=list(commands_list.keys()),variable=var_commands)
         
    commands_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
    commands_list = json.load(commands_data_file)

    var_commands = customtkinter.StringVar(value=lang_data['simple_commands_select'])
     
    combobox_commands_label = customtkinter.CTkLabel(del_simple, text= lang_data['simple_commands_del_label'], text_font=("default_theme","15"))
    combobox_commands_label.grid(row=1, column=0,columnspan=2, padx=20, pady=(30,10))
    
    combobox_commands = customtkinter.CTkComboBox(del_simple,values=list(commands_list.keys()),variable=var_commands,width=200)
    combobox_commands.grid(row=2,column=0,padx=20,columnspan=2, pady=20)

    submit_buttom7 = customtkinter.CTkButton(del_simple,text= lang_data['del'],command = del_command_select)
    submit_buttom7.grid(row=3, column=1,padx=20, pady=20, sticky='e')

    error_label = customtkinter.CTkLabel(del_simple, text="", text_font=("default_theme","11"))
    error_label.grid(row=4, column=0, columnspan=2, pady=20)
    
    del_simple.mainloop()

def edit_simple_command():
    
    edit_simple_command = customtkinter.CTkToplevel(app)
    edit_simple_command.title(f"RewardEvents - {lang_data['simple_commands_edit_title']}")
    edit_simple_command.iconbitmap("src/icon.ico")
    edit_simple_command.attributes('-topmost', 'true')
    
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
            message_edit_val = customtkinter.StringVar(value= lang_data['simple_commands_select'])
            
            combobox_message.configure(variable=message_edit_val,values=list(commands_list.keys()))
            
            error_label.configure(text=lang_data['simple_commands_edit_success'])
        except:
            error_label.configure(text=lang_data['simple_commands_edit_error'])
            
    def update_edit_combox():
        
        commands_data_file = open('src/config/simple_commands.json' , 'r', encoding='utf-8') 
        commands_list = json.load(commands_data_file)
    
        return commands_list
    
    
    commands_list = update_edit_combox()

    var_edit_commands = customtkinter.StringVar(value= lang_data['simple_commands_select'])
    
    title_command_edit = customtkinter.CTkLabel(edit_simple_command, text= lang_data['simple_commands_edit_label'], text_font=("default_theme","13"))
    title_command_edit.grid(row=0, column=0 ,columnspan=2,padx=20, pady=10)
    
    combobox_label = customtkinter.CTkLabel(edit_simple_command, text= lang_data['command_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    combobox_label.grid(row=1, column=0, padx=20, pady=10, sticky='w')
    
    combobox_message = customtkinter.CTkComboBox(edit_simple_command, values=list(commands_list.keys()),
                                                 variable=var_edit_commands, width=300, command = select_command_edit)
    
    combobox_message.grid(row=1, column=1, padx=20, pady=10, sticky='e')
    
    edit_command_label = customtkinter.CTkLabel(edit_simple_command, text= lang_data['simple_commands_edit_content'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    edit_command_label.grid(row=2, column=0, padx=20, pady=20, sticky='w')
    
    edit_command_entry = customtkinter.CTkEntry(edit_simple_command, width=300)
    edit_command_entry.grid(row=2, column=1, padx=20, pady=10, sticky='e')
    
    user_level_edit_label = customtkinter.CTkLabel(edit_simple_command, text= lang_data['moderator_ask_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    user_level_edit_label.grid(row=3, column=0 ,padx=20, pady=10, sticky='w')
    
    user_level_edit = customtkinter.CTkSwitch(edit_simple_command,text="",text_font=("default_theme", "13"),)
    user_level_edit.grid(row=3, column=1,padx=15, pady=10, sticky='e')

    del_command_buttom = customtkinter.CTkButton(edit_simple_command, text=lang_data['save'], command = edit_command_confirm)
    del_command_buttom.grid(row=4, column=1, padx=20, pady=(20,60), sticky='e')

    error_label = customtkinter.CTkLabel(edit_simple_command, text="", text_font=("default_theme","11"))
    error_label.grid(row=4, column=0, columnspan=2, pady=20)
    
    edit_simple_command.mainloop()   

def edit_delay_commands():
    
    edit_delay_command = customtkinter.CTkToplevel(app)
    edit_delay_command.title(f"RewardEvents - {lang_data['simple_commands_edit_delay_title']}")
    edit_delay_command.iconbitmap("src/icon.ico")
    edit_delay_command.attributes('-topmost', 'true')
        
    def edit_delay_confirm():
        
        edit_delay_command_value = edit_delay_entry.get()
        
        if not edit_delay_command_value is None:
            
            if edit_delay_command_value.isnumeric():
                try:
                    time_delay_file = open('src/config/commands_config.json')
                    time_delay_data = json.load(time_delay_file)

                    time_delay_data['delay_config'] = edit_delay_command_value
                    time_delay_file.close()
                    
                    time_delay_write = open('src/config/commands_config.json' , 'w', encoding='utf-8') 
                    json.dump(time_delay_data, time_delay_write, indent = 4, ensure_ascii=False)
                    time_delay_write.close()
                    
                    error_label.configure(text=lang_data['simple_commands_edit_delay_success'])
                except:
                    error_label.configure(text=lang_data['simple_commands_edit_delay_error'])
            else:
                error_label.configure(text=lang_data['simple_commands_edit_delay_number'])
        else:
            error_label.configure(text=lang_data['simple_commands_edit_delay_empty'])
                       
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
                    
                    error_label.configure(text=lang_data['simple_commands_edit_delay_success'])
                except:
                    error_label.configure(text=lang_data['simple_commands_edit_delay_error'])
            else:
                error_label.configure(text=lang_data['simple_commands_edit_delay_number'])
        else:
            error_label.configure(text=lang_data['simple_commands_edit_delay_empty'])
            
    def delay_atual():
        
        time_delay_file = open('src/config/commands_config.json')
        time_delay_data = json.load(time_delay_file)
        
        time_delay_tts_file = open('src/config/prefix_tts.json')
        time_delay_tts_data = json.load(time_delay_tts_file)
        
        edit_delay_entry_var = customtkinter.StringVar(value=f"{time_delay_data['delay_config']}")
        edit_delay_entry.configure(textvariable=edit_delay_entry_var)
        
        edit_delay_tts_entry_var = customtkinter.StringVar(value=f"{time_delay_tts_data['delay_config']}")
        edit_delay_tts_entry.configure(textvariable=edit_delay_tts_entry_var)
    
    title_delay_edit = customtkinter.CTkLabel(edit_delay_command, text= lang_data['simple_commands_edit_delay_label'], text_font=("default_theme","13"))
    title_delay_edit.grid(row=0, column=0 ,padx=20, pady=10)
    
    edit_delay_entry = customtkinter.CTkEntry(edit_delay_command, width=300)
    edit_delay_entry.grid(row=1, column=0, padx=20, pady=(15, 5))
    
    save_delay_buttom = customtkinter.CTkButton(edit_delay_command, text= lang_data['save'], command = edit_delay_confirm)
    save_delay_buttom.grid(row=2, column=0, padx=20, pady=(20,60), sticky='e')
    
    title_delay_tts_edit = customtkinter.CTkLabel(edit_delay_command, text= lang_data['simple_commands_edit_delay_tts_label'], text_font=("default_theme","13"))
    title_delay_tts_edit.grid(row=3, column=0 ,padx=20, pady=10)
    
    edit_delay_tts_entry = customtkinter.CTkEntry(edit_delay_command, width=300)
    edit_delay_tts_entry.grid(row=4, column=0, padx=20, pady=(15, 5)) 

    save_delay_tts_buttom = customtkinter.CTkButton(edit_delay_command, text=lang_data['save'], command = edit_delay_tts_confirm)
    save_delay_tts_buttom.grid(row=5, column=0, padx=20, pady=(20,60), sticky='e')

    error_label = customtkinter.CTkLabel(edit_delay_command, text="", text_font=("default_theme","11"))
    error_label.grid(row=6, column=0, columnspan=2, pady=20)
    
    delay_atual()
    
    edit_delay_command.mainloop()   
                         
def config_obs_conn_top():
    
    top_config_obs_conn = customtkinter.CTkToplevel(app)
    top_config_obs_conn.title(f"RewardEvents - {lang_data['obs_conn_title']}")  
    top_config_obs_conn.iconbitmap("src/icon.ico")
    top_config_obs_conn.attributes('-topmost', 'true')

    def salvar_obs_conn():
        
        auto_connect_value = auto_conn_obs.get()
        obs_host_data = obs_host_entry.get()
        obs_port_data = obs_port_entry.get()
        obs_password_data = obs_password_entry.get()

        if not [x for x in (obs_password_data, obs_port_data) if x is None]:
            
            data = {
                'OBS_HOST': obs_host_data,
                'OBS_PORT': obs_port_data, 
                'OBS_PASSWORD': obs_password_data,
                'OBS_AUTO_CON': auto_connect_value,
                }

            out_file = open("src/config/obs.json", "w", encoding='utf-8')
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()

            out_file_obs_atual = open("src/config/obs.json", "r", encoding='utf-8')
            data_obs_atual = json.load(out_file_obs_atual)
            
            error_label.configure(text=lang_data['obs_conn_success'])
        else:
            error_label.configure(text=lang_data['obs_conn_error'])
                
    def get_obs_atual_con():
            
        out_file_obs_atual = open("src/config/obs.json")
        data_obs_atual = json.load(out_file_obs_atual)
            
        obs_host_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_HOST']}")
        obs_port_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_PORT']}")
        obs_password_var = customtkinter.StringVar(value=f"{data_obs_atual['OBS_PASSWORD']}")
        
        obs_host_entry.configure(textvariable=obs_host_var)
        obs_port_entry.configure(textvariable=obs_port_var)
        obs_password_entry.configure(textvariable=obs_password_var)
                       
    obs_host_var = customtkinter.StringVar(value= lang_data['obs_conn_loading'])
    obs_port_var = customtkinter.StringVar(value= lang_data['obs_conn_loading'])
    obs_password_var = customtkinter.StringVar(value= lang_data['obs_conn_loading'])
                
    title_obs_confg = customtkinter.CTkLabel(top_config_obs_conn,text=lang_data['obs_conn_label'],text_font=("default_theme", "13"))
    title_obs_confg.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

    obs_host_label = customtkinter.CTkLabel(top_config_obs_conn, text=lang_data['obs_host_label'], text_font=("default_theme", "11"), anchor="w")
    obs_host_label.grid(row=1, column=0, padx=20, pady=(15, 5), sticky='W')

    obs_host_entry = customtkinter.CTkEntry(top_config_obs_conn, width=200, textvariable=obs_host_var)
    obs_host_entry.grid(row=1, column=1, padx=20, pady=(15, 5))

    obs_port_label = customtkinter.CTkLabel(top_config_obs_conn, text=lang_data['obs_port_label'], text_font=("default_theme", "11"), anchor="w")
    obs_port_label.grid(row=2, column=0, padx=20, pady=(5, 5), sticky='W')

    obs_port_entry = customtkinter.CTkEntry(top_config_obs_conn, width=200, textvariable=obs_port_var)
    obs_port_entry.grid(row=2, column=1, padx=20, pady=(5, 5))

    obs_password_label = customtkinter.CTkLabel(top_config_obs_conn, text=lang_data['obs_password_label'], text_font=("default_theme", "11"), anchor="w",)
    obs_password_label.grid(row=3, column=0, padx=20, pady=(5, 15), sticky='W')

    obs_password_entry = customtkinter.CTkEntry(top_config_obs_conn, width=200, textvariable=obs_password_var)
    obs_password_entry.grid(row=3, column=1, padx=20, pady=(5, 15))

    auto_conn_obs_label = customtkinter.CTkLabel(top_config_obs_conn, text=lang_data['obs_conn_start_ask_label'], text_font=("default_theme", "11"), anchor="w",)
    auto_conn_obs_label.grid(row=4, column=0,padx=20, pady=(5, 15) , sticky='W')
    
    auto_conn_obs = customtkinter.CTkSwitch(top_config_obs_conn, text=" ", text_font=("default_theme", "13"),)
    auto_conn_obs.grid(row=4, column=1,padx=10, pady=(5, 15), sticky='e')

    save_config_obs = customtkinter.CTkButton(top_config_obs_conn, text=lang_data['save'], command=salvar_obs_conn)
    save_config_obs.grid(row=6, column=1, padx=20, pady=10, sticky='e')

    error_label = customtkinter.CTkLabel(top_config_obs_conn, text="", text_font=("default_theme","11"))
    error_label.grid(row=7, column=0, columnspan=2, pady=20)
    
    get_obs_atual_con()
    
    top_config_obs_conn.mainloop()
    
def config_obs_not_top():
    
    top_config_obs_notifc = customtkinter.CTkToplevel(app)
    top_config_obs_notifc.title(f"RewardEvents - {lang_data['obs_not_title']}")
    top_config_obs_notifc.iconbitmap("src/icon.ico")
    top_config_obs_notifc.attributes('-topmost', 'true')
    
    def salvar_conf_not():
    
        html_active = html_active_switch.get()
        html_source = html_source_combox.get()
        html_time = html_time_entry.get()
        
        if not [x for x in (html_time) if x is None]:
                        
            data = {
                'HTML_ACTIVE' : html_active,
                'HTML_TITLE': html_source,
                'HTML_TIME': int(html_time)
                }

            out_file = open("src/config/notfic.json", "w", encoding='utf-8')
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()

            error_label.configure(text=lang_data['obs_not_success'])
        else:
            error_label.configure(text=lang_data['obs_not_error'])
            
    obs_font_variable = customtkinter.StringVar(value= lang_data['obs_select_source'])  

    obs_not_title = customtkinter.CTkLabel(top_config_obs_notifc, text= lang_data['obs_not_label'], text_font=("default_theme", "11"), anchor="w")
    obs_not_title.grid(row=0, column=0,columnspan=2, padx=20, pady=20)

    html_active_label =customtkinter.CTkLabel(top_config_obs_notifc, text= lang_data['obs_not_html_active_label'], text_font=("default_theme", "11"), anchor="w")
    html_active_label.grid(row=4, column=0, padx=20, pady=(10, 15), sticky='W')

    html_active_switch = customtkinter.CTkSwitch(top_config_obs_notifc,text=" ")
    html_active_switch.grid(row=4, column=1, padx=20, pady=(10, 15), sticky='e')

    html_source_label = customtkinter.CTkLabel(top_config_obs_notifc, text= lang_data['obs_not_html'], text_font=("default_theme", "11"), anchor="w")
    html_source_label.grid(row=5, column=0, padx=20, pady=(5, 15), sticky='W')

    html_source_combox = customtkinter.CTkOptionMenu(top_config_obs_notifc,values=list(obs_con.get_sources()),variable=obs_font_variable, width=200)
    html_source_combox.grid(row=5, column=1, padx=20, pady=(5, 15))

    html_time_label = customtkinter.CTkLabel(top_config_obs_notifc, text= lang_data['obs_not_html_time'], text_font=("default_theme", "11"), anchor="w")
    html_time_label.grid(row=6, column=0, padx=20, pady=(5, 15), sticky='W')

    html_time_entry = customtkinter.CTkEntry(top_config_obs_notifc, width=200)
    html_time_entry.grid(row=6, column=1, padx=20, pady=(5, 15))

    salvar = customtkinter.CTkButton(top_config_obs_notifc, text=lang_data['save'], command=salvar_conf_not)
    salvar.grid(row=7, column=1,padx=20, pady=(10,10), sticky='e')

    error_label = customtkinter.CTkLabel(top_config_obs_notifc, text="", text_font=("default_theme","11"))
    error_label.grid(row=8, column=0, columnspan=2, pady=20)
    
    top_config_obs_notifc.mainloop()
  
def config_messages_top():
    
    top_config_messages = customtkinter.CTkToplevel(app)
    top_config_messages.title(f"RewardEvents - {lang_data['message_config_title']}")
    top_config_messages.iconbitmap("src/icon.ico")
    top_config_messages.attributes('-topmost', 'true')
    
    def timer_status():
    
        status_value = timer_status_value.get()
        
        timer_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        timer_data = json.load(timer_data_file)
        
        timer_data['STATUS_TIMER'] = status_value
        timer_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(timer_data, old_data_write, indent = 4,ensure_ascii=False)
        old_data_write.close()    

    def tts_status():

        tts_status_value = tts_option.get()
        
        tts_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        tts_data = json.load(tts_data_file)
        
        tts_data['STATUS_TTS'] = tts_status_value
        tts_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(tts_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()
        
    def command_status():

        command_status_value = commands_option.get()
        
        command_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        command_data = json.load(command_data_file)
        
        command_data['STATUS_COMMANDS'] = command_status_value
        command_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(command_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()

    def response_status():

        response_status_value = response_option.get()
        
        response_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        response_data = json.load(response_data_file)
        
        response_data['STATUS_RESPONSE'] = response_status_value
        response_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(response_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()

    def clip_status():

        clip_status_value = clip_option.get()
        
        clip_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        clip_data = json.load(clip_data_file)
        
        clip_data['STATUS_CLIP'] = clip_status_value
        clip_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(clip_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()

    def user_error_status():

        user_error_status_value = user_error_option.get()
        
        user_error_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        user_error_data = json.load(user_error_data_file)
        
        user_error_data['STATUS_ERROR_USER'] = user_error_status_value
        user_error_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(user_error_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()
    
    def time_error_status():

        time_status_value = time_option.get()
        
        time_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        time_data = json.load(time_data_file)
        
        time_data['STATUS_ERROR_TIME'] = time_status_value
        time_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(time_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()
        
    def bot_status():

        bot_status_value_opt = bot_status_value.get()
        
        bot_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        bot_data = json.load(bot_data_file)
        
        bot_data['STATUS_BOT'] = bot_status_value_opt
        bot_data_file.close()
        
        old_data_write = open('src/config/commands_config.json' , 'w', encoding="utf-8") 
        json.dump(bot_data, old_data_write, indent = 4, ensure_ascii=False)
        old_data_write.close()
    
    def get_all_status_value():
        
        status_data_file = open('src/config/commands_config.json' , 'r', encoding="utf-8") 
        status_data = json.load(status_data_file)
        
        status_error_time = status_data['STATUS_ERROR_TIME']
        status_error_user = status_data['STATUS_ERROR_USER']
        status_response = status_data['STATUS_RESPONSE']
        status_clip = status_data['STATUS_CLIP']
        status_tts = status_data['STATUS_TTS']
        status_timer = status_data['STATUS_TIMER']
        status_commands = status_data['STATUS_COMMANDS']
        status_bot = status_data['STATUS_BOT']
        
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
        if status_bot == 1:
            bot_status_value.select()


    title_status = customtkinter.CTkLabel(top_config_messages, text= lang_data['message_config_label'], text_font=("default_theme","15"))
    title_status.grid(row=1, column=0, columnspan=2, padx=20, pady=(20,30))

    tts_option_label = customtkinter.CTkLabel(top_config_messages, text=lang_data['message_config_tts'], text_font=("default_theme","13"))
    tts_option_label.grid(row=2, column=0, padx=20, pady=5, sticky='w')

    tts_option = customtkinter.CTkSwitch(top_config_messages, text=" ", command=tts_status)
    tts_option.grid(row=2, column=1, padx=20, pady=5, sticky='e')

    commands_option_label = customtkinter.CTkLabel(top_config_messages, text=lang_data['message_config_commands'], text_font=("default_theme","13"))
    commands_option_label.grid(row=3, column=0, padx=20, pady=5, sticky='w')

    commands_option = customtkinter.CTkSwitch(top_config_messages, text=" ",command=command_status)
    commands_option.grid(row=3, column=1, padx=20, pady=5, sticky='e')

    response_option_label = customtkinter.CTkLabel(top_config_messages, text=lang_data['message_config_response'], text_font=("default_theme","13"))
    response_option_label.grid(row=4, column=0, padx=20, pady=5,sticky='w')

    response_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=response_status)
    response_option.grid(row=4, column=1, padx=20, pady=5,sticky='e')

    time_option_label = customtkinter.CTkLabel(top_config_messages, text=lang_data['message_config_delay'], text_font=("default_theme","13"))
    time_option_label.grid(row=5, column=0, padx=20, pady=5, sticky='w')

    time_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=time_error_status)
    time_option.grid(row=5, column=1, padx=20, pady=5, sticky='e')

    clip_option_label = customtkinter.CTkLabel(top_config_messages, text=lang_data['message_config_clip'], text_font=("default_theme","13"))
    clip_option_label.grid(row=6, column=0, padx=20, pady=5, sticky='w')

    clip_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=clip_status)
    clip_option.grid(row=6, column=1, padx=20, pady=5, sticky='e')

    user_error_option_label = customtkinter.CTkLabel(top_config_messages, text= lang_data['message_config_perms'], text_font=("default_theme","13"))
    user_error_option_label.grid(row=7,column=0, padx=20, pady=5, sticky='w')

    user_error_option = customtkinter.CTkSwitch(top_config_messages,text=" ",command=user_error_status)
    user_error_option.grid(row=7, column=1, padx=20, pady=5, sticky='e')
    
    timer_status_value_label = customtkinter.CTkLabel(top_config_messages,text=lang_data['message_config_timer'] , text_font=("default_theme","13"), anchor="w", justify=RIGHT)
    timer_status_value_label.grid(row=8, column=0, padx=20, pady=5, sticky='w')

    timer_status_value = customtkinter.CTkSwitch(top_config_messages,text=" ",command=timer_status)
    timer_status_value.grid(row=8, column=1, padx=20, pady=5, sticky='e')
    
    bot_status_value_label = customtkinter.CTkLabel(top_config_messages,text=lang_data['message_config_bot'] , text_font=("default_theme","13"))
    bot_status_value_label.grid(row=9, column=0, padx=20, pady=(5,20), sticky='w')
    
    bot_status_value = customtkinter.CTkSwitch(top_config_messages,text=" ",command=bot_status)
    bot_status_value.grid(row=9, column=1, padx=20, pady=(5,20), sticky='e')
    
    get_all_status_value()
    
    top_config_messages.mainloop()

def config_responses_top():

    top_responses = customtkinter.CTkToplevel(app)
    top_responses.title(f"RewardEvents - {lang_data['config_responses_title']}")
    top_responses.iconbitmap("src/icon.ico")
    top_responses.attributes('-topmost', 'true')

    def response_select(value_combobox):

        global reponse_key_glob

        responses_file = open("src/messages/messages_file.json", "r", encoding="utf-8")
        response_data = json.load(responses_file)

        response_list = {

            lang_data['response_response_reset_counter'] :response_data['response_reset_counter'],
            lang_data['response_response_set_counter'] : response_data['response_set_counter'],
            lang_data['response_response_counter'] : response_data['response_counter'],
            lang_data['response_response_delay_error'] : response_data['response_delay_error'],
            lang_data['response_clip_create_clip'] : response_data['clip_create_clip'],
            lang_data['response_clip_button_create_clip'] : response_data['clip_button_create_clip'],
            lang_data['response_clip_error_clip'] : response_data['clip_error_clip'],
            lang_data['response_error_tts_disabled'] : response_data['error_tts_disabled'],
            lang_data['response_error_tts_no_text'] : response_data['error_tts_no_text'],
            lang_data['response_error_user_level'] : response_data['error_user_level'],
            lang_data['response_response_user_giveaway'] : response_data['response_user_giveaway'],
            lang_data['response_response_no_user_giveaway'] : response_data['response_no_user_giveaway'],
            lang_data['response_giveaway_response_win'] : response_data['giveaway_response_win'],
            lang_data['response_response_giveaway_disabled'] : response_data['response_giveaway_disabled'],
            lang_data['response_giveaway_response_user_add'] : response_data['giveaway_response_user_add'],
            lang_data['response_giveaway_status_enable'] : response_data['giveaway_status_enable'],
            lang_data['response_giveaway_status_disable'] : response_data['giveaway_status_disable'],
            lang_data['response_command_module_status'] : response_data['command_module_status'],
            lang_data['response_message_module_status'] : response_data['messages_chat_module_status'],
            lang_data['response_commands_disabled'] : response_data['commands_disabled'],
        }

        if value_combobox in response_list:
            reponse_val = customtkinter.StringVar(value=response_list[value_combobox])
            reponse_key_glob = [k for k, v in response_data.items() if v == response_list[value_combobox]][0]
            response_custom_entry.configure(textvariable=reponse_val)
            
    def save_response():

        global reponse_key_glob

        response_custom = response_custom_entry.get()

        if reponse_key_glob and response_custom != "":

            responses_file = open("src/messages/messages_file.json", "r", encoding="utf-8")
            response_data = json.load(responses_file)

            response_data[reponse_key_glob] = response_custom

            responses_file_write = open("src/messages/messages_file.json", "w", encoding="utf-8")
            json.dump(response_data, responses_file_write, indent=6, ensure_ascii=False)

            error_label.configure(text=lang_data['config_response_confirm'])
            reponse_val = customtkinter.StringVar(value='')
            response_custom_entry.configure(textvariable=reponse_val)
            reponse_key_glob = ""
        
        else:
            error_label.configure(text=lang_data['config_response_novalue'])


    response_combobox = {

        lang_data['response_response_reset_counter'],
        lang_data['response_response_set_counter'],
        lang_data['response_response_counter'],
        lang_data['response_response_delay_error'],
        lang_data['response_clip_create_clip'],
        lang_data['response_clip_button_create_clip'],
        lang_data['response_clip_error_clip'],
        lang_data['response_error_tts_disabled'],
        lang_data['response_error_tts_no_text'],
        lang_data['response_error_user_level'],
        lang_data['response_response_user_giveaway'],
        lang_data['response_response_no_user_giveaway'],
        lang_data['response_giveaway_response_win'],
        lang_data['response_response_giveaway_disabled'],
        lang_data['response_giveaway_response_user_add'],
        lang_data['response_giveaway_status_enable'],
        lang_data['response_giveaway_status_disable'],
        lang_data['response_command_module_status'],
        lang_data['response_message_module_status'],
        lang_data['response_commands_disabled']
    }

    tittle_responses = customtkinter.CTkLabel(top_responses, text=lang_data['select_response'], text_font=("default_theme","15"))
    tittle_responses.grid(row=1,column=0, columnspan=2,padx=20, pady=20,)

    response_label = customtkinter.CTkLabel(top_responses, text=lang_data['response_label'], text_font=("default_theme","13"))
    response_label.grid(row=2,column=0,padx=20, pady=10)
    
    response_combobox = customtkinter.CTkComboBox(top_responses,values=list(response_combobox),width=200,command=response_select)
    response_combobox.grid(row=2,column=1 ,padx=20, pady=20)

    response_custom_entry = customtkinter.CTkEntry(top_responses, width=450)
    response_custom_entry.grid(row=3,column=0 , columnspan=2, padx=20, pady=20)

    save = customtkinter.CTkButton(top_responses,text=lang_data['save'],command=save_response)
    save.grid(row=4, column=1,padx=20, pady=20,sticky='e')

    error_label = customtkinter.CTkLabel(top_responses, text="", text_font=("default_theme","12"))
    error_label.grid(row=5, column=0, columnspan=2, padx=20, pady=20)

    top_responses.mainloop()

def config_counter_counter():
    
    top_config_counter = customtkinter.CTkToplevel(app)
    top_config_counter.title(f"RewardEvents - {lang_data['counter_title']}")
    top_config_counter.iconbitmap("src/icon.ico")
    top_config_counter.attributes('-topmost', 'true')
    
    with open("src/counter/counter.txt", "r") as counter_file_r:
        counter_file_r.seek(0)
        digit = counter_file_r.read()    
        if digit.isdigit():    
            counter = digit
                
    def initial_value():
        value = initial_value_entry.get()
        
        with open("src/counter/counter.txt", "w") as counter_file_w:      
            counter_file_w.write(str(value))
            
            atual_value_label.configure(text=f"Valor atual: {value}")
                
    def restart_counter():
        with open("src/counter/counter.txt", "w") as counter_file_w:      
            counter_file_w.write('0')
            atual_value_label.configure(text=f"Valor atual: 0")

    def save_commands_counter():
        
        check_counter = command_check_value_entry.get()
        set_counter = command_set_value_entry.get()
        reset_counter = command_reset_value_entry.get()
        
        if not [x for x in (check_counter, set_counter, reset_counter) if x is None]:
            
            commands_counter_data = {
                'reset_counter':reset_counter,
                'set_counter' :set_counter,
                'check_counter':check_counter,
            }
            
            commands_counter_file = open("src/counter/commands.json", 'w', encoding='utf-8')
            json.dump(commands_counter_data,commands_counter_file,ensure_ascii=False)
            
            error_label.configure(text=lang_data['counter_success'])
        else:
            error_label.configure(text=lang_data['counter_error'])
        
    def start_commands_conter():

        commands_counter_file = open("src/counter/commands.json", 'r', encoding='utf-8')
        commands_counter_data = json.load(commands_counter_file)

        command_check_val = customtkinter.StringVar(value=commands_counter_data['check_counter'])
        command_set_val = customtkinter.StringVar(value=commands_counter_data['set_counter'])
        command_res_val = customtkinter.StringVar(value=commands_counter_data['reset_counter'])

        command_check_value_entry.configure(textvariable=command_check_val)
        command_set_value_entry.configure(textvariable=command_set_val)
        command_reset_value_entry.configure(textvariable=command_res_val)

    title_counter = customtkinter.CTkLabel(top_config_counter, text= lang_data['counter_label'], text_font=("default_theme","15"))
    title_counter.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)
    
    atual_value_label = customtkinter.CTkLabel(top_config_counter, text=f"{lang_data['counter_atual_value']} {counter}", text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    atual_value_label.grid(row=1,column=0, columnspan=2,pady=20,padx=20)
    
    initial_value_label = customtkinter.CTkLabel(top_config_counter, text= lang_data['counter_start_value_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    initial_value_label.grid(row=2,column=0,pady=20,padx=20, sticky='W')

    initial_value_entry = customtkinter.CTkEntry(top_config_counter,width=200)
    initial_value_entry.grid(row=2, column=1, pady=20,padx=20)
    
    initial_value_save = customtkinter.CTkButton(top_config_counter,text= lang_data['save'],command = initial_value)
    initial_value_save.grid(row=3,column=1,padx=20, pady=20, sticky='e')
    
    title_messages = customtkinter.CTkLabel(top_config_counter, text= lang_data['commands'], text_font=("default_theme","13"))
    title_messages.grid(row=4, column=0, columnspan=2, padx=20, pady=20,)
    
    command_check_value_label = customtkinter.CTkLabel(top_config_counter, text= lang_data['counter_check_command_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_check_value_label.grid(row=5,column=0, pady=(20,5),padx=20, sticky='W')

    command_check_value_entry = customtkinter.CTkEntry(top_config_counter,width=200)
    command_check_value_entry.grid(row=5, column=1, pady=(20,5),padx=20)
    
    command_set_value_label = customtkinter.CTkLabel(top_config_counter, text= lang_data['counter_apply_command_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_set_value_label.grid(row=6,column=0,pady=(5,5),padx=20, sticky='W')

    command_set_value_entry = customtkinter.CTkEntry(top_config_counter,width=200)
    command_set_value_entry.grid(row=6, column=1, pady=(5,5),padx=20)
    
    command_reset_value_label = customtkinter.CTkLabel(top_config_counter, text= lang_data['counter_reset_command_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    command_reset_value_label.grid(row=7,column=0, pady=(5,20),padx=20, sticky='W')

    command_reset_value_entry = customtkinter.CTkEntry(top_config_counter,width=200)
    command_reset_value_entry.grid(row=7, column=1, padx=20, pady=(5,20))
    
    commands_counter_save = customtkinter.CTkButton(top_config_counter,text= lang_data['save'],command = save_commands_counter)
    commands_counter_save.grid(row=8,column=1,padx=20, pady=(10,20), sticky='e')

    restart_counter_save = customtkinter.CTkButton(top_config_counter,text= lang_data['counter_reset_button'],command = restart_counter)
    restart_counter_save.grid(row=9,column=0, columnspan=2, padx=20, pady=(20,10))
    
    error_label = customtkinter.CTkLabel(top_config_counter, text=f"", text_font=("default_theme","12"),anchor="w", justify=RIGHT)
    error_label.grid(row=10,column=0, columnspan=2, pady=(10,10), padx=20)
    
    start_commands_conter()

    top_config_counter.mainloop()

def config_lang():

    top_config_lang = customtkinter.CTkToplevel(app)
    top_config_lang.title(f"RewardEvents - {lang_data['lang_title']}")
    top_config_lang.iconbitmap("src/icon.ico")
    top_config_lang.attributes('-topmost', 'true')

    def save_lang():
        lang_opt = lang_combox.get()
        lang_opt_repl = lang_opt.replace('.json','')
        
        lang_data_save = {"lang" :  lang_opt_repl}
        
        lang_config_file_save = open('src/config/lang.json', 'w')
        json.dump(lang_data_save,lang_config_file_save, ensure_ascii=False)

    def get_langs():

        files_lang = os.listdir('src/lang')
        lang_combox.configure(values=list(files_lang))


    lang_title = customtkinter.CTkLabel(top_config_lang, text= lang_data['lang_title'], text_font=("default_theme", "13"))
    lang_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(25,15))

    lang_label = customtkinter.CTkLabel(top_config_lang, text= lang_data['lang_select'], text_font=("default_theme", "11"), anchor="w")
    lang_label.grid(row=1, column=0, padx=20, pady=(15, 5), sticky='W')

    lang_combox = customtkinter.CTkOptionMenu(top_config_lang,values=[f"{lang_data['lang_select']}"], width=200,dynamic_resizing=True)
    lang_combox.grid(row=1, column=1, padx=20, pady=(20, 5))

    save = customtkinter.CTkButton(top_config_lang, text=lang_data['save'], command=save_lang)
    save.grid(row=4, column=1,padx=20, pady=(10,10), sticky='e')

    get_langs()

    top_config_lang.mainloop()

def config_giveaway():
    
    top_config_giveaway = customtkinter.CTkToplevel(app)
    top_config_giveaway.title(f"RewardEvents - {lang_data['giveaway_command_config_title']}")
    top_config_giveaway.iconbitmap("src/icon.ico")
               
    def giveaway_config_top():
        
        config_give_top = customtkinter.CTkToplevel(app)
        config_give_top.title(f"RewardEvents - {lang_data['giveaway_command_config_title']}")
        config_give_top.iconbitmap("src/icon.ico")

        def giveaway_reset_status():

            giveaway_reset_value = giveaway_reset_switch.get()

            reset_giveaway_file = open('src/giveaway/config.json','r',encoding='utf-8')
            reset_giveaway_data = json.load(reset_giveaway_file)

            reset_giveaway_data['reset'] = giveaway_reset_value

            status_giveaway_file_w = open('src/giveaway/config.json', 'w', encoding='utf-8')
            json.dump(reset_giveaway_data, status_giveaway_file_w, ensure_ascii=False)
        
        def giveaway_status():

            giveaway_status_value = giveaway_status_switch.get()

            status_giveaway_file = open('src/giveaway/config.json','r',encoding='utf-8')
            status_giveaway_data = json.load(status_giveaway_file)

            status_giveaway_data['enable'] = giveaway_status_value
            giveaway_name_data = status_giveaway_data['name']

            status_giveaway_file_w = open('src/giveaway/config.json', 'w', encoding='utf-8')
            json.dump(status_giveaway_data, status_giveaway_file_w, ensure_ascii=False)

            if giveaway_status_value == 1:
                message = messages_data['giveaway_status_enable'].replace('{giveaway_name_data}',giveaway_name_data)
                smt.send_message(message, "RESPONSE")
            else:
                message = messages_data['giveaway_status_disable'].replace('{giveaway_name_data}',giveaway_name_data)
                smt.send_message(message, "RESPONSE")

        def save_name():

            giveaway_name_value = giveaway_name_entry.get()

            name_giveaway_file = open('src/giveaway/config.json','r',encoding='utf-8')
            name_giveaway_data = json.load(name_giveaway_file)

            name_giveaway_data['name'] = giveaway_name_value

            name_giveaway_file_w = open('src/giveaway/config.json', 'w', encoding='utf-8')
            json.dump(name_giveaway_data, name_giveaway_file_w, ensure_ascii=False)

        def add_user():

            user = giveaway_add_name_entry.get()

            with open("src/giveaway/names.txt", "a+") as give_file_r:
                        give_file_r.write(user+"\n")
            
            
            chat_response = messages_data['giveaway_response_user_add'] 
            response_redus = chat_response.replace('{user}', user)

            smt.send_message(response_redus,'RESPONSE')

        def show_giveaway():

            show_giveaway_top = customtkinter.CTkToplevel(app)
            show_giveaway_top.title(f"RewardEvents - {lang_data['giveaway_names_title']}")
            show_giveaway_top.iconbitmap("src/icon.ico")

            title_names_giveaway = customtkinter.CTkLabel(show_giveaway_top, text=lang_data['giveaway_list_names_label'], text_font='20', justify=CENTER,)
            title_names_giveaway.grid(row=1, columnspan=2, pady=(10, 20))
            
            textbox_names_giveaway = tkinter.Listbox(show_giveaway_top,width=60,height=30,bg='black',fg='white')
            textbox_names_giveaway.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 0))
            
            file_giveaway = open("src/giveaway/names.txt","r")
            for lines in file_giveaway:
                textbox_names_giveaway.insert(END,f'{lines}')
                
            file_giveaway.close()

            show_giveaway_top.mainloop()
    
        def clear_giveaway():

            with open("src/giveaway/names.txt", "w") as counter_file_w:      
                counter_file_w.truncate(0)

        def execute_giveaway():

            giveaway_file = open('src/giveaway/config.json','r',encoding='utf-8')
            giveaway_data = json.load(giveaway_file)

            reset_give = giveaway_data['reset']

            with open("src/giveaway/names.txt", "r") as give_file_check:
                if len(give_file_check.read()) > 0:

                    with open("src/giveaway/names.txt", "r+") as give_file_r:
                            lines = give_file_r.readlines()

                            choice = randint(0,len(lines))
                            name = lines[choice].replace('\n','')

                            message_win = messages_data['giveaway_response_win'].replace('{name}',name)
                            smt.send_message(message_win,'RESPONSE')

                            with open("src/giveaway/backup.txt", "r+") as give_file_backup:
                                give_file_backup.writelines(lines)

                            with open("src/giveaway/result.txt", "w") as give_file_w:
                                give_file_w.write(name)
                            
                            if reset_give == 1:
                                give_file_r.truncate(0)

        title_giveaway_top = customtkinter.CTkLabel(config_give_top, text= lang_data['giveaway_command_config_title'], text_font=("default_theme","15"))
        title_giveaway_top.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

        title_giveaway_top1 = customtkinter.CTkLabel(config_give_top, text= lang_data['giveaway_config_create_label'], text_font=("default_theme","13"))
        title_giveaway_top1.grid(row=1, column=0, columnspan=2, padx=20, pady=(20,10))
        
        giveaway_name_label = customtkinter.CTkLabel(config_give_top, text= lang_data['giveaway_name_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        giveaway_name_label.grid(row=2,column=0,pady=(10,10),padx=20, sticky='W')

        giveaway_name_entry = customtkinter.CTkEntry(config_give_top,width=200)
        giveaway_name_entry.grid(row=2, column=1, padx=20, pady=(10,10), sticky='e')
        
        giveaway_name_save = customtkinter.CTkButton(config_give_top,text= lang_data['save'],command = save_name)
        giveaway_name_save.grid(row=3, column=1, padx=20, pady=(10,20), sticky='e')

        title_giveaway_add = customtkinter.CTkLabel(config_give_top, text= lang_data['giveaway_config_add_user_label'], text_font=("default_theme","13"))
        title_giveaway_add.grid(row=4, column=0, columnspan=2, padx=20, pady=(20,10))

        giveaway_add_name_label = customtkinter.CTkLabel(config_give_top, text= lang_data['giveaway_username_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        giveaway_add_name_label.grid(row=5,column=0,pady=(10,10),padx=20, sticky='W')

        giveaway_add_name_entry = customtkinter.CTkEntry(config_give_top,width=200)
        giveaway_add_name_entry.grid(row=5, column=1, padx=20, pady=(10,10), sticky='e')
        
        giveaway_name_add = customtkinter.CTkButton(config_give_top,text= lang_data['add'],command = add_user)
        giveaway_name_add.grid(row=6, column=1, padx=20, pady=(10,20), sticky='e')

        giveaway_status_label = customtkinter.CTkLabel(config_give_top, text= lang_data['giveaway_config_enable_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        giveaway_status_label.grid(row=7, column=0, padx=20, pady=(20,10), sticky='w')

        giveaway_status_switch = customtkinter.CTkSwitch(config_give_top, text="", command=giveaway_status)
        giveaway_status_switch.grid(row=7, column=1, padx=20, pady=(20,10), sticky='e')

        giveaway_reset_label = customtkinter.CTkLabel(config_give_top, text= lang_data['giveaway_config_clear_names_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        giveaway_reset_label.grid(row=8, column=0, padx=20, pady=(10,20), sticky='w')

        giveaway_reset_switch = customtkinter.CTkSwitch(config_give_top, text="", command=giveaway_reset_status)
        giveaway_reset_switch.grid(row=8, column=1, padx=20, pady=(10,20), sticky='e')

        clear_give = customtkinter.CTkButton(config_give_top,text= lang_data['giveaway_config_clear_names_button'], width=200, command = clear_giveaway)
        clear_give.grid(row=9, column=0, columnspan=2, padx=20, pady=(20,10))

        display_names_give = customtkinter.CTkButton(config_give_top,text= lang_data['giveaway_config_list_button'], width=200, command = show_giveaway)
        display_names_give.grid(row=10, column=0, columnspan=2, padx=20, pady=(10,10))

        execute_give = customtkinter.CTkButton(config_give_top,text= lang_data['giveaway_config_execute_button'], width=200, command = execute_giveaway)
        execute_give.grid(row=11, column=0, columnspan=2, padx=20, pady=(10,20))
    

        config_give_top.mainloop()

    def giveaway_commmands_top():

        config_give_comm_top = customtkinter.CTkToplevel(app)
        config_give_comm_top.title(f"RewardEvents - {lang_data['giveaway_command_config_title']}")
        config_give_comm_top.iconbitmap("src/icon.ico")

        def save_commands_give():
        
            check_giveaway = command_check_entry.get()
            selfcheck_giveaway = command_selfcheck_entry.get()
            clear_giveaway_value = command_clear_entry.get()
            execute_giveaway_value = command_execute_entry.get()
            
            if not [x for x in (check_giveaway, selfcheck_giveaway, clear_giveaway_value,execute_giveaway_value) if x is None]:
                
                giveaway_data = {
                    "execute_giveaway" : execute_giveaway_value.lower(),
                    "clear_giveaway": clear_giveaway_value.lower(),
                    "check_name": check_giveaway.lower(),
                    "check_self_name" : selfcheck_giveaway.lower()
                }
                
                commands_giveaway_file = open("src/giveaway/commands.json", 'w', encoding='utf-8')
                json.dump(giveaway_data, commands_giveaway_file, ensure_ascii=False)
                
                error_label.configure(text="Salvo!")
            else:
                error_label.configure(text="Preencha todos os campos!")

        def start_commands_giveaway():

            commands_giveaway_file = open("src/giveaway/commands.json", 'r', encoding='utf-8')
            commands_giveaway_data = json.load(commands_giveaway_file)

            command_execute_val = customtkinter.StringVar(value=commands_giveaway_data['execute_giveaway'])
            command_clear_val = customtkinter.StringVar(value=commands_giveaway_data['clear_giveaway'])
            command_check_val = customtkinter.StringVar(value=commands_giveaway_data['check_name'])
            command_selfcheck_val = customtkinter.StringVar(value=commands_giveaway_data['check_self_name'])

            command_execute_entry.configure(textvariable=command_execute_val)
            command_clear_entry.configure(textvariable=command_clear_val)
            command_check_entry.configure(textvariable=command_check_val)
            command_selfcheck_entry.configure(textvariable=command_selfcheck_val)


        title_messages = customtkinter.CTkLabel(config_give_comm_top, text= lang_data['giveaway_command_config_label'], text_font=("default_theme","13"))
        title_messages.grid(row=6, column=0, columnspan=2, padx=20, pady=20)
        
        command_execute_label = customtkinter.CTkLabel(config_give_comm_top, text= lang_data['giveaway_command_execute_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        command_execute_label.grid(row=7,column=0, padx=20, pady=(20,5), sticky='W')

        command_execute_entry = customtkinter.CTkEntry(config_give_comm_top,width=200)
        command_execute_entry.grid(row=7, column=1, padx=20, pady=(20,5))
        
        command_clear_label = customtkinter.CTkLabel(config_give_comm_top, text= lang_data['giveaway_command_clear_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        command_clear_label.grid(row=8,column=0, padx=20, pady=(5,5), sticky='W')

        command_clear_entry = customtkinter.CTkEntry(config_give_comm_top,width=200)
        command_clear_entry.grid(row=8, column=1, padx=20, pady=(5,5))
        
        command_check_label = customtkinter.CTkLabel(config_give_comm_top, text= lang_data['giveaway_command_check_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        command_check_label.grid(row=9,column=0, padx=20, pady=(5,20), sticky='W')

        command_check_entry = customtkinter.CTkEntry(config_give_comm_top,width=200)
        command_check_entry.grid(row=9, column=1, padx=20, pady=(5,5))

        command_selfcheck_label = customtkinter.CTkLabel(config_give_comm_top, text= lang_data['giveaway_command_self_check_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
        command_selfcheck_label.grid(row=10,column=0, padx=20, pady=(5,5), sticky='W')

        command_selfcheck_entry = customtkinter.CTkEntry(config_give_comm_top,width=200)
        command_selfcheck_entry.grid(row=10, column=1, padx=20, pady=(5,20))
        
        commands_counter_save = customtkinter.CTkButton(config_give_comm_top,text= lang_data['save'],command = save_commands_give)
        commands_counter_save.grid(row=11,column=1, padx=20, pady=(10,20), sticky='e')

        error_label = customtkinter.CTkLabel(config_give_comm_top, text=f"", text_font=("default_theme","12"),anchor="w", justify=RIGHT)
        error_label.grid(row=14,column=0, columnspan=2, padx=20, pady=20)
    
        start_commands_giveaway()

    title_giveaway_top = customtkinter.CTkLabel(top_config_giveaway, text= lang_data['giveaway_command_config_title'], text_font=("default_theme","15"))
    title_giveaway_top.grid(row=0, column=0, columnspan=2, padx=20, pady=20,)

    clear_give = customtkinter.CTkButton(top_config_giveaway ,text= lang_data['config_giveaway_button'], width=200 ,command = giveaway_config_top)
    clear_give.grid(row=1,column=0, columnspan=2, padx=20, pady=20)

    display_names_give = customtkinter.CTkButton(top_config_giveaway,text= lang_data['giveaway_commands_config_button'], width=200,command = giveaway_commmands_top)
    display_names_give.grid(row=2,column=0, columnspan=2, padx=20, pady=20)

    top_config_giveaway.mainloop()
          
def clear_data():

    ask = messagebox.askyesno( lang_data['warning'], lang_data['clear_data_warning'])
    if ask == 'yes':
        clear_files()
        close()
        
def self_clip():

    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
    
    url_clip = "https://api.twitch.tv/helix/clips?broadcaster_id=" + USERID

    headers1 = CaseInsensitiveDict()
    headers1["Authorization"] = 'Bearer ' + TOKEN
    headers1["Client-Id"] = apitoken.CLIENTID
    headers1["Content-Length"] = "0"


    resp1 = req.post(url_clip, headers=headers1)

    response_clip = json.loads(resp1.text)
    
    try:
        response_error = 'None'
        response_create = response_clip['data'][0]['id']

        message_final = messages_data['clip_button_create_clip'].replace('{clip_id}',response_create)
        smt.send_message(message_final,"CLIP")
        
    except:
        response_error = response_clip['message']

        if response_error:
            message_clip_error = messages_data['clip_error_clip']
            smt.send_message(message_clip_error,'CLIP')

def new_timer():
    
    new_timer_top = customtkinter.CTkToplevel(app)
    new_timer_top.title(f"RewardEvents - {lang_data['timer_tab_title']}")
    new_timer_top.iconbitmap("src/icon.ico")
    
    def create_new_timer():
        
        new_message_timer = message_timer_entry.get()
        
        if new_message_timer:
        
            timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
            timer_data = json.load(timer_data_file)
            
            timer_message = timer_data['MESSAGES']
            
            qnt = len(timer_message) + 1
            int_qnt = int(qnt)
            
            
            timer_data['MESSAGES'][int_qnt] = new_message_timer
            timer_data_file.close()
            
            old_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
            json.dump(timer_data, old_data_write, indent = 4,ensure_ascii=False)
            old_data_write.close()
            
            error_label.configure(text=lang_data['timer_created_label'])
        else:
            error_label.configure(text=lang_data['timer_empty_label'])
    
    title_timer = customtkinter.CTkLabel(new_timer_top, text= lang_data['timer_tab_title'], text_font=("default_theme","15"))
    title_timer.grid(row=0, column=0, columnspan=2, padx=20, pady=10,)

    message_timer_label = customtkinter.CTkLabel(new_timer_top, text= lang_data['message_label'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    message_timer_label.grid(row=2,column=0, pady=10,padx=20,sticky='w')

    message_timer_entry = customtkinter.CTkEntry(new_timer_top,width=300)
    message_timer_entry.grid(row=2, column=1, padx=10, pady=20)
    
    add_message_buttom = customtkinter.CTkButton(new_timer_top,text= lang_data['add'],command = create_new_timer)
    add_message_buttom.grid(row=3, column=1, padx=10,pady=(10,20),sticky='e')

    error_label = customtkinter.CTkLabel(new_timer_top, text="", text_font=("default_theme","12"))
    error_label.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

    new_timer_top.mainloop()

def timer_interval():
        
    interval_timer_top = customtkinter.CTkToplevel(app)
    interval_timer_top.title(f"RewardEvents - {lang_data['timer_interval_title']}")
    interval_timer_top.iconbitmap("src/icon.ico")
    
    def timer_time_change():
        
        value_max = timer_max_interval_entry.get()
        value_min = timer_min_interval_entry.get()

        if value_max.isdigit()  and value_min.isdigit():

            timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
            timer_data = json.load(timer_data_file)
        
            timer_data['TIME'] = int(value_min)
            timer_data['TIME_MAX'] = int(value_max)
            
            timer_data_file.close()

            old_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
            json.dump(timer_data, old_data_write, indent = 4, ensure_ascii=False)
            old_data_write.close()
            error_label.configure(text=lang_data['timer_success_label'])

        else:

            error_label.configure(text=lang_data['timer_digit_error_label'])
        
    timer_interval_label = customtkinter.CTkLabel(interval_timer_top,text=lang_data['timer_interval_label'], text_font=("default_theme","13"))
    timer_interval_label.grid(row=0, column=0,columnspan=2, padx=20,pady=(10,0))
    
    timer_min_interval_label = customtkinter.CTkLabel(interval_timer_top,text=lang_data['timer_min'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    timer_min_interval_label.grid(row=1, column=0, padx=20,pady=10,sticky='w')

    timer_min_interval_entry = customtkinter.CTkEntry(interval_timer_top,width=300)
    timer_min_interval_entry.grid(row=1, column=1, padx=20, pady=10)
    
    timer_max_interval_label = customtkinter.CTkLabel(interval_timer_top,text= lang_data['timer_max'], text_font=("default_theme","13"),anchor="w", justify=RIGHT)
    timer_max_interval_label.grid(row=2, column=0, padx=20,pady=10,sticky='w')
    
    timer_max_interval_entry = customtkinter.CTkEntry(interval_timer_top,width=300)
    timer_max_interval_entry.grid(row=2, column=1,  pady=10)
    
    interval_timer_buttom = customtkinter.CTkButton(interval_timer_top,text= lang_data['save'], command = timer_time_change)
    interval_timer_buttom.grid(row=3, column=1,padx=20,pady=(10,20),sticky='e')

    error_label = customtkinter.CTkLabel(interval_timer_top, text="", text_font=("default_theme","12"))
    error_label.grid(row=4, column=0, columnspan=2, padx=10, pady=20)
    
    interval_timer_top.mainloop()

def edit_timer():
    
    edit_timer_top = customtkinter.CTkToplevel(app)
    edit_timer_top.title(f"RewardEvents - {lang_data['timer_edit_title']}")
    edit_timer_top.iconbitmap("src/icon.ico")
    
    def select_timer_edit(message_edit):
        
        global timer_message_key
        
        timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
        timer_data = json.load(timer_data_file)
        
        timer_message = timer_data['MESSAGES']
        
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
        
        timer_data['MESSAGES'][timer_message_key] = edit_message_value
        timer_data_file.close()
        
        old_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(timer_data, old_data_write, indent = 4,ensure_ascii=False)
        old_data_write.close()
        
        messages_edit_combox = update_del_combox()
        message_edit_val = customtkinter.StringVar(value=lang_data['select_message_label'])
        combobox_message.configure(variable=message_edit_val,values=list(messages_edit_combox.values()))
        
        error_label.configure(text=lang_data['timer_message_success_label'])
            
    def update_del_combox():
        
        message_data_file = open('src/config/timer.json' , 'r',encoding='utf-8') 
        message_data = json.load(message_data_file)
        message_del = message_data['MESSAGES']
        message_data_file.close()
    
        return message_del
    
    messages_edit_combox = update_del_combox()
    
    message_edit_val = customtkinter.StringVar(value= lang_data['select_message_label'])
    
    title_timer_del = customtkinter.CTkLabel(edit_timer_top, text=lang_data['timer_edit_label'], text_font=("default_theme","13"))
    title_timer_del.grid(row=0, column=0 ,padx=20, pady=10)
    
    combobox_message = customtkinter.CTkComboBox(edit_timer_top, values=list(messages_edit_combox.values()),
                                                 variable=message_edit_val, width=300, command = select_timer_edit)
    
    combobox_message.grid(row=1, column=0, padx=20, pady=10)
    
    
    edit_timer_entry = customtkinter.CTkEntry(edit_timer_top, width=300)
    edit_timer_entry.grid(row=2, column=0, padx=20, pady=(15, 5))

    del_timer_buttom = customtkinter.CTkButton(edit_timer_top, text=lang_data['save'], command = edit_timer_confirm)
    del_timer_buttom.grid(row=3, column=0, padx=20, pady=(20,60), sticky='e')

    error_label = customtkinter.CTkLabel(edit_timer_top, text="", text_font=("default_theme","12"))
    error_label.grid(row=4, column=0, columnspan=2, padx=10, pady=20)
    
    edit_timer_top.mainloop()   
    
def del_timer():
    
    del_timer_top = customtkinter.CTkToplevel(app)
    del_timer_top.title(f"RewardEvents - {lang_data['timer_del_title']}")
    del_timer_top.iconbitmap("src/icon.ico")
    del_timer_top.attributes('-topmost', 'true')
    
    def del_timer_confirm():
        
        message_to_del = combobox_message.get()
        message_del_file = open('src/config/timer.json' , 'r', encoding='utf-8') 
        message_del_date = json.load(message_del_file)

        message_list = message_del_date['MESSAGES']
        message_del_file.close()
        
        key_list = list(message_list.keys())
        val_list = list(message_list.values())
    
        position = val_list.index(message_to_del)
        key_value = key_list[position]
        
        del message_del_date['MESSAGES'][key_value]
        
        message_del_file_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(message_del_date, message_del_file_write, indent = 4,ensure_ascii=False)
        message_del_file_write.close()
        
        update_del_combox()
        combobox_message.update()
        
        error_label.configure(text=lang_data['timer_del_success_label'])
            
    def update_del_combox():
        
        message_data_file = open('src/config/timer.json' , 'r',encoding='utf-8') 
        message_data = json.load(message_data_file)
        message_del = message_data['MESSAGES']
        message_data_file.close()
    
        return message_del
    
    messages_combox = update_del_combox()
    
    message_val = customtkinter.StringVar(value= lang_data['select_message_label'])        
            
    title_timer_del = customtkinter.CTkLabel(del_timer_top, text= lang_data['timer_del_label'], text_font=("default_theme","13"))
    title_timer_del.grid(row=9, column=0 ,padx=20,columnspan=2, pady=10)
    
    combobox_message = customtkinter.CTkComboBox(del_timer_top,values=list(messages_combox.values()),variable=message_val,width=300)
    combobox_message.grid(row=10,column=0 ,padx=20, pady=10)

    del_timer_buttom = customtkinter.CTkButton(del_timer_top,text=lang_data['del'],command = del_timer_confirm)
    del_timer_buttom.grid(row=10, column=1,padx=20, pady=10,sticky='e')

    error_label = customtkinter.CTkLabel(del_timer_top, text="", text_font=("default_theme","12"))
    error_label.grid(row=11, column=0, columnspan=2, padx=10, pady=20)
    
    del_timer_top.mainloop()
      
def top_auth():
    
    auth_top = customtkinter.CTkToplevel(app)
    auth_top.title(f"RewardEvents - {lang_data['auth_title']}")
    auth_top.attributes('-topmost', 'true')
    auth_top.iconbitmap("src/icon.ico")
        
    def start_auth_user():
        
        print('iniciou')
        username_entry = user_name_entry.get()

        if username_entry == '':
            error_label.configure(text=lang_data['auth_user_name_error'])
        else:
            
            data = {
                'USERNAME': username_entry.lower(), 
                'USERID': '', 
                'TOKEN': '', 
                'TOKENBOT': '',
                'BOTUSERNAME': ''}

            out_file = open("src/auth/auth.json", "w", encoding='utf-8')
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()

            print('iniciou auth')

            auth_top.attributes('-topmost', 'false')
            auth_user.Webview_Auth()

            out_file_check = open("src/auth/auth.json", encoding='utf-8')
            data_check = json.load(out_file_check)
            
            username_check = data_check['USERNAME']
            token_check = data_check['TOKEN']
            user_id_check = data_check['USERID']

            url_validate = "https://id.twitch.tv/oauth2/validate"
            headers_check_token = CaseInsensitiveDict()
            headers_check_token["Authorization"] = f"OAuth {token_check}"
            resp_check_token = req.get(url_validate, headers=headers_check_token)
            resp_token_json = json.loads(resp_check_token.text)
            resp_login = resp_token_json['login']
            resp_user_id = resp_token_json['user_id']

            if resp_login == username_check and resp_user_id == user_id_check:
                error_label.configure(text=lang_data['auth_user_success'])
                bot_user_name_auth_buttom.configure(state='normal')
                bot_user_name_entry.configure(state='normal')
                bot_user_op.configure(state='normal')
                auth_top.attributes('-topmost', 'true')
                out_file_check.close()
            else:
                error_label.configure(text=lang_data['auth_user_error'])
                auth_top.attributes('-topmost', 'true')
                out_file_check.close()
                    
    def start_auth_bot():
    
        bot_username_entry = bot_user_name_entry.get()
        
        out_file1 = open("src/auth/auth.json")
        data1 = json.load(out_file1)
        username = data1['USERNAME']
        token = data1['TOKEN']
        userid_auth = data1['USERID']

        if bot_username_entry == '':
            error_label.configure(text=lang_data['auth_user_name_error'])
        else:
            
            data = {
                'USERNAME': username, 
                'USERID': userid_auth, 
                'TOKEN': token, 
                'TOKENBOT': '',
                'BOTUSERNAME': bot_username_entry.lower()}

            out_file = open("src/auth/auth.json", "w")
            json.dump(data, out_file, indent=6,ensure_ascii=False)
            out_file.close()
            
            auth_top.attributes('-topmost', 'false')
            auth_bot.Webview_Auth()
            
            file_check_bot = open("src/auth/auth.json")
            data_check_bot = json.load(file_check_bot)
            
            token_bot = data_check_bot['TOKENBOT']
            username_check_bot = data_check_bot['BOTUSERNAME']

            url_validate = "https://id.twitch.tv/oauth2/validate"
            headers_check_token = CaseInsensitiveDict()
            headers_check_token["Authorization"] = f"OAuth {token_bot}"
            resp_check_token = req.get(url_validate, headers=headers_check_token)
            resp_token_json = json.loads(resp_check_token.text)
            resp_login = resp_token_json['login']

            if resp_login == username_check_bot:
                if messagebox.showinfo(lang_data['auth_success_alert_title'],lang_data['auth_bot_is_user_success']):
                    os._exit(0)
            else:
                error_label.configure(text=lang_data['auth_bot_error'])
                auth_top.attributes('-topmost', 'true')

    def auth_bot_is_user():

        out_file1 = open("src/auth/auth.json",'r', encoding='utf-8')
        data1 = json.load(out_file1)

        username = data1['USERNAME']
        token = data1['TOKEN']
        userid = data1['USERID']

        data = {
            'USERNAME': username, 
            'USERID': userid, 
            'TOKEN': token, 
            'TOKENBOT': token,
            'BOTUSERNAME': username
            }

        out_file = open("src/auth/auth.json", "w", encoding='utf-8')
        json.dump(data, out_file, indent=6, ensure_ascii=False)
        out_file.close()

        auth_top.attributes('-topmost', 'false')
        
        if messagebox.showinfo(lang_data['auth_success_alert_title'], lang_data['auth_bot_success'],parent=auth_top):
            os._exit(0)

    top_title = customtkinter.CTkLabel(auth_top, text= lang_data['auth_label'], text_font='20', justify=CENTER)
    top_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 20))
    
    user_name_label = customtkinter.CTkLabel(auth_top, text= lang_data['auth_username_label'],text_font='20', anchor="w",justify=LEFT)
    user_name_label.grid(row=1,column=0, padx=20, pady=(10, 5), sticky='W')
    
    user_name_entry = customtkinter.CTkEntry(auth_top,width=200)
    user_name_entry.grid(row=1,column=1, padx=20, pady=(10,5))
    
    user_name_auth_buttom = customtkinter.CTkButton(auth_top,text= lang_data['auth_login_streamer_button'],command = start_auth_user,width=200)
    user_name_auth_buttom.grid(row=2, column=0, columnspan=2, padx=20, pady=(5,50),sticky='e')
    
    bot_user_name_label = customtkinter.CTkLabel(auth_top, text= lang_data['auth_bot_username_label'],text_font='20', anchor="w",justify=LEFT)
    bot_user_name_label.grid(row=3, column=0, padx=20, pady=(20, 5), sticky='W')
    
    bot_user_name_entry = customtkinter.CTkEntry(auth_top,width=200,state="disabled")
    bot_user_name_entry.grid(row=3, column=1, padx=20 ,pady=(20,5))
    
    bot_user_name_auth_buttom = customtkinter.CTkButton(auth_top,text= lang_data['auth_login_bot_button'],state="disabled",command = start_auth_bot,width=200)
    bot_user_name_auth_buttom.grid(row=4, column=0, columnspan=2, padx=20, pady=(10,20), sticky='e')
    
    bot_user_op = customtkinter.CTkButton(auth_top,text=lang_data['auth_bot_is_user_ask'],state="disabled",command= auth_bot_is_user)
    bot_user_op.grid(row=5, column=0, columnspan=2, padx=20, pady=(10,30))

    error_label = customtkinter.CTkLabel(auth_top, text="", text_font=("default_theme","12"))
    error_label.grid(row=6, column=0, columnspan=2, padx=10, pady=20)

    auth_top.mainloop()

def conn_obs_button():

    if obs_con.connect_obs() == True:
        status_obs.configure(text=lang_data['connected'])
        conn_obs_buttom.grid_forget()
    else:
        status_obs.grid_forget()
        conn_obs_buttom.grid(row=8, column=1, pady=2, padx=20,sticky='e')

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

        value_conn = data_obs['OBS_AUTO_CON'] 
        
        if value_conn == 1:

            if obs_con.connect_obs() == True:
                status_obs.configure(text=lang_data['connected'])
                conn_obs_buttom.grid_forget()
            else:
                conn_obs_buttom.grid(row=8, column=1, pady=2, padx=20,sticky='e')

        else:
            conn_obs_buttom.grid(row=8, column=1, pady=2, padx=20,sticky='e' )

    
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
            top_auth()
        
    else:
        top_auth()
             
def receive_commands(tid):
    
    USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN = auth.auth_data()
    
    def command_fallback(message):    
            
        command_file = open('src/config/commands.json', "r", encoding='utf-8') 
        command_data = json.load(command_file) 
        
        command_file_prefix = open('src/config/commands_config.json', "r", encoding='utf-8') 
        command_data_prefix = json.load(command_file_prefix)
        
        command_file_simple = open('src/config/simple_commands.json', "r", encoding='utf-8') 
        command_data_simple = json.load(command_file_simple)
        
        command_file_tts = open('src/config/prefix_tts.json', "r", encoding='utf-8') 
        command_data_tts = json.load(command_file_tts) 
        
        command_file_counter = open('src/counter/commands.json', "r", encoding='utf-8') 
        command_data_counter = json.load(command_file_counter) 

        command_file_giveaway = open('src/giveaway/commands.json', "r", encoding='utf-8') 
        command_data_giveaway = json.load(command_file_giveaway) 
        
        messages_file = open('src/messages/messages_file.json', "r", encoding='utf-8') 
        messages_data = json.load(messages_file) 
        
        
        command_string = message['message']
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
        
        user = message['display-name'] 
        user_type = message['user-type'] 
        user_id_command = message['user-id']

        status_commands = command_data_prefix['STATUS_COMMANDS']  
        status_tts = command_data_prefix['STATUS_TTS']

        command_tts = command_data_tts['command']
        user_type_tts = command_data_tts['user_level']


        def receive_tts():

            if status_tts == 1:
                message_delay,check_time = check_delay_file.check_delay() 
                    
                if check_time:
                
                    if user_type == user_type_tts or user_id_command == USERID:
                        
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
                            
                            receive_redeem(data_rewards,received_type)
                        else:
                            smt.send_message(messages_data['error_tts_no_text'],"RESPONSE")
                else:
                    smt.send_message( message_delay , 'ERROR_TIME' )
            else:
                smt.send_message(messages_data['error_tts_disabled'],"RESPONSE")

        if command_tts != "":
            check_tts = command.startswith(command_tts)          
            if check_tts:
                receive_tts()
                           
        if status_commands == 1:
                
            if command in result_command_check.keys():
                
                redeem = command_data[command]['RECOMPENSA']
                user_level_simple = command_data[command]['user_level']
                
                data_rewards = {}
                data_rewards['USERNAME'] = user
                data_rewards['REDEEM'] = redeem
                data_rewards['USER_INPUT'] = command
                data_rewards['USER_LEVEL'] = user_type
                data_rewards['USER_ID'] = user_id_command
                data_rewards['COMMAND'] = command
                data_rewards['PREFIX'] = prefix

                received_type = 'command'
                
                if user_type == user_level_simple or user_type == 'mod' or user_id_command == USERID:
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:    
                        
                        receive_redeem(data_rewards,received_type)

                    else:
                        smt.send_message(message_delay_global,'ERROR_TIME')
                else:

                    message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                    message_error_level_command = message_error_level.replace('{command}', command)
                    smt.send_message(message_error_level_command,'ERROR_USER')
                
            elif command in result_command_simple.keys():
                
                with open("src/counter/counter.txt", "r") as counter_file_r:
                    counter_file_r.seek(0)
                    digit = counter_file_r.read()    
                    if digit.isdigit():    
                        counter = digit
            
                response = command_data_simple[command]['response']
                user_level_simple = command_data_simple[command]['user_level']
                    
                if user_type == user_level_simple or user_type == 'mod' or user_id_command == USERID:
                    
                    aliases = {
                        '{user}': user,
                        '{command}': command, 
                        '{prefix}': prefix, 
                        '{user_level}': user_type, 
                        '{user_id}': user_id_command,
                        '{counter}' : counter
                        }
                    
                    response_redus = replace_all(response, aliases)
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                    
                    if check_time_global:        
                        smt.send_message(response_redus,'RESPONSE')
                    else:
                        smt.send_message(message_delay_global,'ERROR_TIME')
                else:    
                    message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                    message_error_level_command = message_error_level.replace('{command}', command)
                    smt.send_message(message_error_level_command,'ERROR_USER')
                    
            elif command in result_counter_check.values():
                
                if 'reset_counter' in result_counter_check.keys() :
                    
                    if user_type == "mod" or user_id_command == USERID:
                        
                        message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                        if check_time_global:        
                            
                            with open("src/counter/counter.txt", "w") as counter_file_w:      
                                counter_file_w.write('0')
                            
                            response_reset = messages_data['response_reset_counter']
                            smt.send_message(response_reset,'RESPONSE')
                            
                        else:
                            
                            smt.send_message(message_delay_global,'ERROR_TIME')
                    else:
                        message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                        message_error_level_command = message_error_level.replace('{command}', command)
                        smt.send_message(message_error_level_command,'ERROR_USER')
                        
                elif 'set_counter' in result_counter_check.keys() :
                    
                    if user_type == "mod" or user_id_command == USERID:
                        
                        message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                        if check_time_global:    
                            
                            

                            if len(command_string.split()) > 1:

                                user_input = command_string.split()[1]
                                
                                if user_input.isdigit():
                                    with open("src/counter/counter.txt", "w") as counter_file_w:      
                                        counter_file_w.write(str(user_input))
                                        
                                    response_set = messages_data['response_set_counter']
                                    response_set_repl = response_set.replace('{value}', user_input)
                                    
                                    smt.send_message(response_set_repl,'RESPONSE')
                                else:
                                    smt.send_message(messages_data['response_not_digit_counter'],'RESPONSE')
                            else:
                                smt.send_message(messages_data['response_null_set_counter'],'RESPONSE')
                        else:
                            smt.send_message(message_delay_global,'ERROR_TIME')
                    else:
                        message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                        message_error_level_command = message_error_level.replace('{command}', command)
                        smt.send_message(message_error_level_command,'ERROR_USER')
                        
                elif 'check_counter' in result_counter_check.keys() :
                    
                    message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                    if check_time_global:    

                            with open("src/counter/counter.txt", "r") as counter_file_r:
                                counter_file_r.seek(0)
                                digit = counter_file_r.read()    
                                if digit.isdigit():    
                                    counter = digit
                                
                            response_set = messages_data['response_counter']
                            response_set_repl = response_set.replace('{value}', counter)
                            
                            smt.send_message(response_set_repl,'RESPONSE')
                    else:
                        smt.send_message(message_delay_global,'ERROR_TIME')

            elif command in result_giveaway_check.values():

                if 'execute_giveaway' in result_giveaway_check.keys() :

                    if user_type == "mod" or user_id_command == USERID:
                        
                        message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                        if check_time_global:

                            giveaway_file = open('src/giveaway/config.json','r',encoding='utf-8')
                            giveaway_data = json.load(giveaway_file)

                            reset_give = giveaway_data['reset']

                            with open("src/giveaway/names.txt", "r") as give_file_check:
                                if len(give_file_check.read()) > 0:

                                    with open("src/giveaway/names.txt", "r+") as give_file_r:
                                            lines = give_file_r.readlines()

                                            choice = randint(0,len(lines))
                                            name = lines[choice].replace('\n','')

                                            message_win = messages_data['giveaway_response_win'].replace('{name}',name)
                                            smt.send_message(message_win,'RESPONSE')

                                            with open("src/giveaway/backup.txt", "r+") as give_file_backup:
                                                give_file_backup.writelines(lines)

                                            with open("src/giveaway/result.txt", "w") as give_file_w:
                                                give_file_w.write(name)
                                            
                                            if reset_give == 1:
                                                give_file_r.truncate(0)
                            
                        else:
                            smt.send_message(message_delay_global,'ERROR_TIME')
                    else:
                        message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                        message_error_level_command = message_error_level.replace('{command}', command)
                        smt.send_message(message_error_level_command,'ERROR_USER')

                elif 'clear_giveaway' in result_giveaway_check.keys() :

                    if user_type == "mod" or user_id_command == USERID:
                        
                        message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                        if check_time_global:        
                            
                            with open("src/giveaway/names.txt", "w") as counter_file_w:      
                                counter_file_w.truncate(0)  
                        else:
                            
                            smt.send_message(message_delay_global,'ERROR_TIME')
                    else:
                        message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                        message_error_level_command = message_error_level.replace('{command}', command)
                        smt.send_message(message_error_level_command,'ERROR_USER')

                    pass

                elif 'check_name' in result_giveaway_check.keys() :

                    if user_type == "mod" or user_id_command == USERID:
                        
                        message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                        if check_time_global:
                            user_input = command_string.split()[1]

                            with open("src/giveaway/names.txt", "r+") as give_file_r:
                                lines_giveaway = give_file_r.readlines()

                                name_user = user_input + '\n'
                                
                                if name_user in lines_giveaway:
                                    
                                    message = messages_data['response_user_giveaway'].replace('{user}',user_input)
                                    smt.send_message(message, 'RESPONSE')
                                else:

                                    message = messages_data['response_nouser_giveaway'].replace('{user}', user_input)
                                    smt.send_message(message, 'RESPONSE')
                        else:
                            
                            smt.send_message(message_delay_global,'ERROR_TIME')
                    
                    else:
                        message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                        message_error_level_command = message_error_level.replace('{command}', command)
                        smt.send_message(message_error_level_command,'ERROR_USER')

                elif 'add_user' in result_giveaway_check.keys() :

                    if user_type == "mod" or user_id_command == USERID:
                        
                        message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                        if check_time_global:
                            user_input = command_string.split()[1]

                            with open("src/giveaway/names.txt", "r+") as give_file_r:
                                lines_giveaway = give_file_r.readlines()

                                with open("src/giveaway/names.txt", "a+") as give_file_r:
                                    give_file_r.write(user_input+"\n")
                                

                                message = messages_data['giveaway_response_user_add']
                                message_repl = message.replace('{user}',user_input)
                                smt.send_message(message_repl, 'RESPONSE')
                        else:
                            
                            smt.send_message(message_delay_global,'ERROR_TIME')
                    
                    else:
                        message_error_level = messages_data['error_user_level'].replace('{user_level_simple}', user_level_simple)
                        message_error_level_command = message_error_level.replace('{command}', command)
                        smt.send_message(message_error_level_command,'ERROR_USER')

                elif 'check_self_name' in result_giveaway_check.keys() :

                        message_delay_global,check_time_global = check_delay_file.check_global_delay()
                        
                        if check_time_global:
                               
                            with open("src/giveaway/names.txt", "r+") as give_file_r:
                                lines_giveaway = give_file_r.readlines()

                                name_user = user + '\n'
                                
                                if name_user in lines_giveaway:

                                    message_user_giveaway = messages_data['response_user_giveaway'].replace('{user}', user)
                                    smt.send_message(message_user_giveaway, 'RESPONSE')

                                else:
                                    message_user_giveaway = messages_data['response_nouser_giveaway'].replace('{user}', user)
                                    smt.send_message(message_user_giveaway, 'RESPONSE')
                            
                        else:
                            
                            smt.send_message(message_delay_global,'ERROR_TIME')

        else:
            
            message = messages_data['commands_disabled']
            smt.send_message(message,"RESPONSE")
    
    command_connected = 0
    
    status_receive_label.configure(text= lang_data['connecting'])
    
    while command_connected == 0:
        
        if TOKEN and TOKENBOT:
            try:
                if smt.value == True:
                    smt.send_message(messages_data['messages_chat_module_status'],'STATUS_BOT')
                    time.sleep(3)
                    
                    module_status_message = messages_data['command_module_status']
                    smt.send_message(module_status_message,'STATUS_BOT')

                    status_receive_label.configure(text= lang_data['connected'])     
                    smt.connection.listen(USERNAME,on_message=command_fallback)
                else:
                    time.sleep(1)
            except:
                command_connected = 0
                status_receive_label.configure(text=lang_data['disconnected']) 
                time.sleep(2)
                
        else:
            time.sleep(3)
    
def close():
    if messagebox.askokcancel("Exit", lang_data['exit']):
        if conn_status == True:
            if smt.value == True:
                smt.connection.close_connection()
        app.destroy() 
        time.sleep(2)
        run_cmd(os._exit(0))
      
def update_check():

    response = req.get("https://api.github.com/repos/GGTEC/RewardEvents/releases/latest")
    response_json = json.loads(response.text)
    version = response_json['tag_name']

    if version != 'v2.8.3':
        update_info = messagebox.askquestion('Update',lang_data['update_new_found'])
        if update_info == 'yes':
            download_link = response_json['assets'][0]['browser_download_url']
            response = wget.download(download_link, "RewardEvents v2.8.3.exe")
              
                   
tab1.columnconfigure(0, weight=1) 

clip_icon = PhotoImage(file="src/icons/clip.png")

view_count = customtkinter.CTkLabel(tab1, text=lang_data['spectators_label'],text_font=("default_theme","10"))
view_count.grid(row=0,column=0,columnspan=2, pady=(20,0),sticky='W')

request_img_result = ImageTk.PhotoImage(PIL.Image.open("src/defaultreward.png").resize((200, 200)).convert("RGBA"))
request_img = customtkinter.CTkLabel(tab1, image=request_img_result)
request_img.grid(row=1,column=0,columnspan=2, pady=(5,0),sticky='WE')

request_name = customtkinter.CTkLabel(tab1, text= lang_data['redeem_reward_label'] , text_font=("default_theme","10"))
request_name.grid(row=2,column=0,columnspan=2, padx=25, pady=(10,0),sticky='WE')

request_name = customtkinter.CTkLabel(tab1, text= lang_data['waiting'], text_font=("default_theme","15"))
request_name.grid(row=3,column=0,columnspan=2, padx=25, pady=(5,0),sticky='WE')

user_request = customtkinter.CTkLabel(tab1, text= lang_data['rewarded_by'], text_font=("default_theme","10"),width=100)
user_request.grid(row=4,column=0,columnspan=2, padx=25, pady=(20,0),sticky='WE')

user_request = customtkinter.CTkLabel(tab1, text= "", text_font=("default_theme","15"),width=100)
user_request.grid(row=5,column=0,columnspan=2, padx=25, pady=(5,0),sticky='WE')

clip_buttom = customtkinter.CTkButton(tab1,image=clip_icon, text='', command = self_clip)
clip_buttom.grid(row=6, column=0,columnspan=2, pady=(20,10))
tooltip_clip_buttom = CreateToolTip(clip_buttom, text = lang_data['create_clip_tip'])



#EVENTOS
tab2.columnconfigure(0, weight=1) 

title_events = customtkinter.CTkLabel(tab2, text= lang_data['events_page_title'], text_font=("default_theme","15"))
title_events.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,10))


plus_add_image = PhotoImage(file="src/icons/plus-square.png")
del_image = PhotoImage(file="src/icons/del.png")

create_event_buttom = customtkinter.CTkButton(tab2,image=plus_add_image, text='', width=150, height=150, command=new_event_top)
create_event_buttom.grid(row=2,column=0,padx=(60,25), pady=(20,20))
tooltip_create_event_buttom = CreateToolTip(create_event_buttom, text = lang_data['events_add_tip'])

del_event_buttom = customtkinter.CTkButton(tab2,image=del_image, text='', width=150, height=150, command=del_event)
del_event_buttom.grid(row=2, column=1,padx=(25,60), pady=(20,20))
tooltip_del_event_buttom = CreateToolTip(del_event_buttom, text = lang_data['events_del_tip'] )

#COMANDOS
tab3.columnconfigure(0, weight=1) 

title_commands = customtkinter.CTkLabel(tab3, text=lang_data['simple_commands_tab_title'], text_font=("default_theme","15"))
title_commands.grid(row=1, column=0, columnspan=2, pady=(20,30))

edit_image = PhotoImage(file="src/icons/edit.png")
edit_time_image = PhotoImage(file="src/icons/edit_time.png")

create_simple_buttom = customtkinter.CTkButton(tab3,image=plus_add_image, text='', width=150, height=150, command=new_simple_command)
create_simple_buttom.grid(row=2, column=0, padx=(60,25), pady=20, sticky='w')
tooltip_create_simple_buttom = CreateToolTip(create_simple_buttom, text = lang_data['simple_commands_add_tip'])

edit_simple_buttom = customtkinter.CTkButton(tab3,image=edit_image, text='', width=150, height=150, command=edit_simple_command)
edit_simple_buttom.grid(row=2, column=1, padx=(25,60), pady=20)
tooltip_edit_simple_buttom = CreateToolTip(edit_simple_buttom, text = lang_data['simple_commands_edit_tip'])

edit_delay_buttom = customtkinter.CTkButton(tab3,image=edit_image, text='', width=150, height=150, command=edit_delay_commands)
edit_delay_buttom.grid(row=3, column=0, padx=(60,25), pady=20, sticky='w')
tooltip_edit_delay_buttom = CreateToolTip(edit_delay_buttom, text = lang_data['simple_commands_edit_delay_tip'])

del_message_simple_buttom = customtkinter.CTkButton(tab3,image=del_image, text='', width=150, height=150, command=del_simple_command)
del_message_simple_buttom.grid(row=3, column=1,padx=(25,60), pady=20)
tooltip_del_message_simple_buttom = CreateToolTip(del_message_simple_buttom, text = lang_data['simple_commands_del_tip'])


#TIMERS
tab4.columnconfigure(0, weight=1)

add_timer_image = PhotoImage(file="src/icons/time_add.png")
del_timer_image = PhotoImage(file="src/icons/time_del.png")
interval_timer_image = PhotoImage(file="src/icons/time_interval.png")

title_timers = customtkinter.CTkLabel(tab4, text= lang_data['timer_tab_title'], text_font=("default_theme","15"))
title_timers.grid(row=1, column=0, columnspan=2, padx=20, pady=(20,30))

new_timer_buttom = customtkinter.CTkButton(tab4,image=add_timer_image, text='', width=150, height=150, command=new_timer)
new_timer_buttom.grid(row=2, column=0,padx=(60,25), pady=20, sticky='w')
tooltip_new_timer_buttom = CreateToolTip(new_timer_buttom, text = lang_data['timer_new_tip'])

edit_timer_buttom = customtkinter.CTkButton(tab4,image=edit_time_image, text='', width=150, height=150, command=edit_timer)
edit_timer_buttom.grid(row=2, column=1,padx=(25,60), pady=20)
tooltip_edit_timer_buttom = CreateToolTip(edit_timer_buttom, text = lang_data['timer_edit_tip'])

del_timer_buttom = customtkinter.CTkButton(tab4,image=del_timer_image, text='', width=150, height=150, command=del_timer )
del_timer_buttom.grid(row=3, column=0,padx=(60,25), pady=20, sticky='w')
tooltip_del_timer_buttom = CreateToolTip(del_timer_buttom, text = lang_data['timer_del_tip'])

interval_timer_buttom = customtkinter.CTkButton(tab4,image=interval_timer_image, text='', width=150, height=150, command=timer_interval)
interval_timer_buttom.grid(row=3, column=1,padx=(25,60), pady=20)
tooltip_interval_timer_buttom = CreateToolTip(interval_timer_buttom, text = lang_data['timer_interval_tip'])

#CONFIG OBS
tab5.columnconfigure(0, weight=1)


config_label = customtkinter.CTkLabel(tab5, text=lang_data['config_tab_label'], text_font=("default_theme","15"))
config_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,30))

config_conn_obs_button = customtkinter.CTkButton(tab5, width=250, text= lang_data['config_obs_conn_button'], command=config_obs_conn_top)
config_conn_obs_button.grid(row=1, column=0, columnspan=2, padx=20, pady=10)


config_notif_obs_button = customtkinter.CTkButton(tab5, width=250, text= lang_data['config_obs_not_button'], command=config_obs_not_top)
config_notif_obs_button.grid(row=2, column=0, columnspan=2, padx=20, pady=10)


config_messages_top_buttom = customtkinter.CTkButton(tab5, width=250, text= lang_data['config_chat_messages_button'], command=config_messages_top)
config_messages_top_buttom.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

config_responses_top_buttom = customtkinter.CTkButton(tab5, width=250, text= lang_data['config_chat_responses_button'], command=config_responses_top)
config_responses_top_buttom.grid(row=4, column=0, columnspan=2, padx=20, pady=10)


config_counter_top_buttom = customtkinter.CTkButton(tab5, width=250, text= lang_data['config_counter_button'], command=config_counter_counter)
config_counter_top_buttom.grid(row=5, column=0, columnspan=2, padx=20, pady=10)


config_give_top_buttom = customtkinter.CTkButton(tab5, width=250, text= lang_data['config_giveaway_button'], command=config_giveaway)
config_give_top_buttom.grid(row=6, column=0, columnspan=2, pady=10)


config_lang_top_buttom = customtkinter.CTkButton(tab5, width=250, text= lang_data['config_lang_button'], command=config_lang)
config_lang_top_buttom.grid(row=7, column=0, columnspan=2, pady=10) 



#PERFIL
tab6.columnconfigure(0, weight=1)

profile_img_label = customtkinter.CTkLabel(tab6, image='')
profile_img_label.grid(row=1, column=0, columnspan=2, pady=20)

profile_name_label_title = customtkinter.CTkLabel(tab6, text= lang_data['about_login_name_label'], text_font=("default_theme", "12"),anchor="w", justify=LEFT)
profile_name_label_title.grid(row=2, column=0, pady=2, padx=20, sticky='w')

profile_name_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "12"),anchor="e", justify=RIGHT)
profile_name_label.grid(row=2, column=1, pady=2, padx=20, sticky='e')

exibition_name_label_title = customtkinter.CTkLabel(tab6, text= lang_data['about_exhibition_name_label'], text_font=("default_theme", "11"),anchor="w", justify=LEFT)
exibition_name_label_title.grid(row=3, column=0, pady=2, padx=20, sticky='w')

exibition_name_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT)
exibition_name_label.grid(row=3, column=1, pady=2, padx=20, sticky='e')

user_id_label_title = customtkinter.CTkLabel(tab6, text= lang_data['about_id_label'], text_font=("default_theme", "11"),anchor="w", justify=LEFT)
user_id_label_title.grid(row=4, column=0, pady=2, padx=20, sticky='w')

user_id_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT, )
user_id_label.grid(row=4, column=1, pady=2, padx=20, sticky='e')

email_label_title = customtkinter.CTkLabel(tab6, text=lang_data['about_email_label'], text_font=("default_theme", "11"),anchor="w", justify=LEFT)
email_label_title.grid(row=5, column=0, pady=2, padx=20, sticky='w')

email_label = customtkinter.CTkLabel(tab6, text=f"", text_font=("default_theme", "11"), anchor="e",justify=RIGHT)
email_label.grid(row=5, column=1, pady=2, padx=20, sticky='e')

status_send = customtkinter.CTkLabel(tab6, text=lang_data['about_status_chat_conn'], text_font=("default_theme", "11"),anchor="w", justify=LEFT)
status_send.grid(row=6, column=0, pady=2, padx=20, sticky='w')

status_send_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT)
status_send_label.grid(row=6, column=1, pady=2, padx=20, sticky='e')

status_receive = customtkinter.CTkLabel(tab6, text= lang_data['about_status_receive_conn'], text_font=("default_theme", "11"),anchor="w", justify=LEFT)
status_receive.grid(row=7, column=0, pady=2, padx=20, sticky='w')

status_receive_label = customtkinter.CTkLabel(tab6, width=100, text=f"", text_font=("default_theme", "11"),anchor="e", justify=RIGHT)
status_receive_label.grid(row=7, column=1, pady=2, padx=20, sticky='e')

status_obs_label = customtkinter.CTkLabel(tab6, text= lang_data['about_status_obs_conn'], text_font=("default_theme", "11"),anchor="w", justify=LEFT)
status_obs_label.grid(row=8, column=0, pady=2, padx=20, sticky='w')

status_obs = customtkinter.CTkLabel(tab6,width=100, text=lang_data['disconnected'], text_font=("default_theme", "11"),anchor="e", justify=RIGHT)
status_obs.grid(row=8, column=1, pady=2, padx=20, sticky='e')

deslogar = customtkinter.CTkButton(tab6, text= lang_data['about_clear_data_button'], command=clear_data)
deslogar.grid(row=9, column=0,columnspan=2, padx=20, pady=30)

conn_obs_buttom = customtkinter.CTkButton(tab6, text= lang_data['about_con_obs_button'], command=conn_obs_button)


tab7.columnconfigure(0, weight=1)

logo_image_src= ImageTk.PhotoImage(PIL.Image.open("src/about.png").resize((170, 170)).convert("RGBA"))
logo_image = customtkinter.CTkLabel(tab7, image=logo_image_src)
logo_image.grid(row=1, column=0,  pady=20)

about_name = customtkinter.CTkLabel(tab7, text=f"RewardEvents v2.8.3", text_font=("default_theme", "12"))
about_name.grid(row=2, column=0, pady=10, padx=20)

dev_name = customtkinter.CTkLabel(tab7, text=f"Dev By GG_TEC", text_font=("default_theme", "12"))
dev_name.grid(row=3, column=0, pady=10, padx=20)

update_check_buttom = customtkinter.CTkButton(tab7, text='Verificar Atualização', command=update_check)
update_check_buttom.grid(row=6, column=0, pady=(30,20))

update_check()
con_pubsub()

_thread.start_new_thread(receive_commands, (3,))
_thread.start_new_thread(get_spec, (4,))
_thread.start_new_thread(timer_module.timer, (2,))

app.protocol("WM_DELETE_WINDOW", close)
app.mainloop()