import os.path
import json

commands = os.path.exists('src/config/commands.json')
simple_commands = os.path.exists('src/config/simple_commands.json')
notifc = os.path.exists('src/config/notfic.json')
obs = os.path.exists('src/config/obs.json')
pathfiles = os.path.exists('src/config/pathfiles.json')
prefix_commands = os.path.exists('src/config/prefix_commands.json')
prefix_tts = os.path.exists('src/config/prefix_tts.json')
timer = os.path.exists('src/config/timer.json')

def check_files():
    if commands == False:
        
        commands_data = {}
        
        commands_data_write = open('src/config/commands.json' , 'w', encoding='utf-8') 
        json.dump(commands_data, commands_data_write, indent = 4, ensure_ascii=False)

    if simple_commands == False:
        
        simple_commands_data = {}
        
        simple_commands_data_write = open('src/config/simple_commands.json' , 'w', encoding='utf-8') 
        json.dump(simple_commands_data, simple_commands_data_write, indent = 4, ensure_ascii=False)
        
    if notifc == False:
        
        notifc_data = {
                            "TEXT_TITLE_REDEEM": "",
                            "TEXT_USER_REDEM": "",
                            "NOTF_GROUP_OBS": ""
                        }
        
        notifc_data_write = open('src/config/notfic.json' , 'w', encoding='utf-8') 
        json.dump(notifc_data, notifc_data_write, indent = 4, ensure_ascii=False)
        
    if obs == False:
        
        obs_data = {    
                        "OBS_HOST": "localhost",
                        "OBS_PORT": "",
                        "OBS_PASSWORD": "",
                        "OBS_AUTO_CON": 0
                    }
        
        obs_data_write = open('src/config/obs.json' , 'w', encoding='utf-8') 
        json.dump(obs_data, obs_data_write, indent = 4, ensure_ascii=False)
        
    if pathfiles == False:
        
        pathfiles_data = {}
        
        pathfiles_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(pathfiles_data, pathfiles_data_write, indent = 4, ensure_ascii=False)
        
    if prefix_tts == False:
        
        prefix_tts_data = {
                            "command": "",
                            "status": 0,
                            "redeem": "",
                            "user_level": "",
                            "delay_date": "",
                            "delay_config": ""
                            }
        
        prefix_tts_data_write = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
        json.dump(prefix_tts_data, prefix_tts_data_write, indent = 4, ensure_ascii=False)
        
    if timer == False:
        
        timer_data = {
                                "TIMERMESSAGE": {
                                "TIME": "120",
                                "TIME_MAX": "120",
                                "ENABLE": "0",
                                "MESSAGES": {}
                            }
                        }
        
        timer_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(timer_data, timer_data_write, indent = 4, ensure_ascii=False)

    if prefix_commands == False:
        
        prefix_commands_data = {
                                    "prefix": "!",
                                    "STATUS_COMMANDS": 1,
                                    "STATUS_ERROR_TIME": 1,
                                    "STATUS_ERROR_USER": 1,
                                    "STATUS_RESPONSE": 1,
                                    "STATUS_CLIP": 1,
                                    "STATUS_TTS": 1,
                                    "STATUS_TIMER": 1,
                                    "delay_date": "",
                                    "delay_config": ""
                                }
        
        prefix_commands_data_write = open('src/config/prefix_commands.json' , 'w', encoding='utf-8') 
        json.dump(prefix_commands_data, prefix_commands_data_write, indent = 4, ensure_ascii=False)