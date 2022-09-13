import os.path
import json
from datetime import datetime, timedelta

commands = os.path.exists('src/config/commands.json')
simple_commands = os.path.exists('src/config/simple_commands.json')
notifc = os.path.exists('src/config/notfic.json')
obs = os.path.exists('src/config/obs.json')
pathfiles = os.path.exists('src/config/pathfiles.json')
config_commands = os.path.exists('src/config/commands_config.json')
prefix_tts = os.path.exists('src/config/prefix_tts.json')
timer = os.path.exists('src/config/timer.json')


now = datetime.now()
time_now = now.strftime("%d/%m/%Y %H:%M:%S")
t2 = datetime.strptime(time_now, "%d/%m/%Y %H:%M:%S")

def check_files():
    
    if commands == False:
        
        commands_data = {}
        
        commands_data_write = open('src/config/commands.json' , 'w', encoding='utf-8') 
        json.dump(commands_data, commands_data_write, indent = 4, ensure_ascii=False)

    if simple_commands == False:
        
        simple_commands_data = {}
        
        simple_commands_data_write = open('src/config/simple_commands.json' , 'w', encoding='utf-8') 
        json.dump(simple_commands_data, simple_commands_data_write, indent = 4, ensure_ascii=False)
        
    if pathfiles == False:
        
        pathfiles_data = {}
        
        pathfiles_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
        json.dump(pathfiles_data, pathfiles_data_write, indent = 4, ensure_ascii=False)
        
    if notifc == False:
        
        notifc_data = {
                            "TEXT_TITLE_REDEEM": "",
                            "TEXT_USER_REDEM": "",
                            "NOTF_GROUP_OBS": ""
                        }
        
        notifc_data_write = open('src/config/notfic.json' , 'w', encoding='utf-8') 
        json.dump(notifc_data, notifc_data_write, indent = 4, ensure_ascii=False)
    else:
        notifc_data_load = open('src/config/notfic.json' , 'r', encoding='utf-8') 
        notifc_data_loaded = json.load(notifc_data_load)
        notifc_list = {"TEXT_TITLE_REDEEM","TEXT_USER_REDEM","NOTF_GROUP_OBS"} 
        
        if not all(key in notifc_data_loaded for key in notifc_list):  
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
    else:
        obs_data_load = open('src/config/obs.json' , 'r', encoding='utf-8') 
        obs_data_loads = json.load(obs_data_load)
        obs_data_list = {"OBS_HOST","OBS_PORT","OBS_PASSWORD","OBS_AUTO_CON"}
        
        if not all(key in obs_data_loads for key in obs_data_list): 
            
            obs_data = {    
                "OBS_HOST": "localhost",
                "OBS_PORT": "",
                "OBS_PASSWORD": "",
                "OBS_AUTO_CON": 0
                }
        
            obs_data_write = open('src/config/obs.json' , 'w', encoding='utf-8') 
            json.dump(obs_data, obs_data_write, indent = 4, ensure_ascii=False) 
        
    if prefix_tts == False:
        
        prefix_tts_data = {
                            "command": "",
                            "status": 0,
                            "redeem": "",
                            "user_level": "",
                            "delay_date": t2,
                            "delay_config": "60"
                            }
        
        prefix_tts_data_write = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
        json.dump(prefix_tts_data, prefix_tts_data_write, indent = 4, ensure_ascii=False)
    else:
        prefix_tts_data_load = open('src/config/prefix_tts.json' , 'r', encoding='utf-8') 
        prefix_tts_data_loads = json.load(prefix_tts_data_load)
        prefix_tts_data_list = {"command","status","redeem","user_level","caracters","delay_date","delay_config"}
        
        if not all(key in prefix_tts_data_loads for key in prefix_tts_data_list): 
            prefix_tts_data = {
                    "command": "",
                    "status": 0,
                    "redeem": "",
                    "caracters": 300,
                    "user_level": "",
                    "delay_date": t2,
                    "delay_config": "60"
                    }
            
            prefix_tts_data_write = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
            json.dump(prefix_tts_data, prefix_tts_data_write, indent = 4, ensure_ascii=False)
              
    if timer == False:
        
        timer_data = {
            "TIME": "120",
            "TIME_MAX": "120",
            "ENABLE": "0",
            "LAST": "",
            "MESSAGES": {}
            }
        
        timer_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
        json.dump(timer_data, timer_data_write, indent = 4, ensure_ascii=False)
    else:
        timer_data_load = open('src/config/timer.json' , 'r', encoding='utf-8')
        timer_data_loads = json.load(timer_data_load) 
        time_list = {"TIME","TIME_MAX","LAST","MESSAGES"}
        
        if not all(key in timer_data_loads for key in time_list): 
            timer_data = {
                "TIME": 20,
                "TIME_MAX": 120,
                "LAST": "",
                "MESSAGES": {}
                }
        
            timer_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
            json.dump(timer_data, timer_data_write, indent = 4, ensure_ascii=False) 

    if config_commands == False:
        
        config_commands_data = {
            "STATUS_COMMANDS": 1,
            "STATUS_ERROR_TIME": 1,
            "STATUS_ERROR_USER": 1,
            "STATUS_RESPONSE": 1,
            "STATUS_CLIP": 1,
            "STATUS_TTS": 1,
            "STATUS_TIMER": 1,
            "STATUS_BOT": 0,
            "delay_date": t2,
            "delay_config": "60"
            }
        
        config_commands_data_write = open('src/config/commands_config.json' , 'w', encoding='utf-8') 
        json.dump(config_commands_data, config_commands_data_write, indent = 4, ensure_ascii=False)
    else:
        config_commands_data_load = open('src/config/commands_config.json' , 'r', encoding='utf-8')
        config_commands_data_loads = json.load(config_commands_data_load)
        prefix_commands_list = {"STATUS_COMMANDS","STATUS_ERROR_TIME","STATUS_ERROR_USER","STATUS_RESPONSE",
                            "STATUS_CLIP","STATUS_TTS","STATUS_TIMER","STATUS_BOT","delay_date","delay_config"}
        
        if not all(key in config_commands_data_loads for key in prefix_commands_list): 
            
            config_commands_data = {
                
                "STATUS_COMMANDS": 1,
                "STATUS_ERROR_TIME": 1,
                "STATUS_ERROR_USER": 1,
                "STATUS_RESPONSE": 1,
                "STATUS_CLIP": 1,
                "STATUS_TTS": 1,
                "STATUS_TIMER": 1,
                "STATUS_BOT": 0,
                "delay_date": t2,
                "delay_config": "60"
                
                }
        
            config_commands_data_write = open('src/config/commands_config.json' , 'w', encoding='utf-8') 
            json.dump(config_commands_data, config_commands_data_write, indent = 4, ensure_ascii=False)