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
giveway_commands = os.path.exists('src/giveway/commands.json')
giveway_config = os.path.exists('src/giveway/config.json')
counter_commands = os.path.exists('src/counter/commands.json')
lang_config = os.path.exists('src/config/lang.json')


now = datetime.now()
time_now = now.strftime("%d/%m/%Y %H:%M:%S")
t2 = str(time_now)

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
        prefix_tts_data_list = {"command","redeem","user_level","caracters","delay_date","delay_config"}
        
        if not all(key in prefix_tts_data_loads for key in prefix_tts_data_list): 
            prefix_tts_data = {
                    "command": "",
                    "redeem": "",
                    "caracters": "300",
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



    if giveway_commands == False:
        
        giveway_commands_data = {
                "execute_giveway" : "!sortear",
                "clear_giveway": "!limparsorteio",
                "check_name": "!checksorteio",
                "check_self_name" : "!estounosorteio"
            }
        
        giveway_commands_data_write = open('src/giveway/commands.json' , 'w', encoding='utf-8') 
        json.dump(giveway_commands_data, giveway_commands_data_write, indent = 4, ensure_ascii=False)
    else:
        giveway_commands_data_load = open('src/giveway/commands.json' , 'r', encoding='utf-8')
        giveway_commands_data_loads = json.load(giveway_commands_data_load)
        giveway_commands_list = {
                "execute_giveway",
                "clear_giveway",
                "check_name",
                "check_self_name",
                "add_user"
                }
        
        if not all(key in giveway_commands_data_loads for key in giveway_commands_list): 
            
            giveway_commands_data = {
                
                "execute_giveway":"!sortear",
                "clear_giveway":"!limparsorteio",
                "check_name":"!checksorteio",
                "check_self_name":"!estounosorteio",
                "add_user" : "!add_sorteio"
                
                }
        
            giveway_commands_data = open('src/giveway/commands.json' , 'w', encoding='utf-8') 
            json.dump(giveway_commands_data, giveway_commands_data, indent = 4, ensure_ascii=False)


    if giveway_config == False:
        
        giveway_config_data = {
                "name": "", 
                "reset": 0,
                "enable": 0
            }
        
        giveway_config_data_write = open('src/giveway/config.json' , 'w', encoding='utf-8') 
        json.dump(giveway_config_data, giveway_config_data_write, indent = 4, ensure_ascii=False)
    else:
        giveway_config_data_load = open('src/giveway/config.json' , 'r', encoding='utf-8')
        giveway_config_data_loads = json.load(giveway_config_data_load)
        giveway_config_list = {"name", "reset","enable"}
        
        if not all(key in giveway_config_data_loads for key in giveway_config_list): 
            
            giveway_config_data = {
                
                "name": "", 
                "reset": 0,
                "enable": 0
                
                }
        
            giveway_config_data_write = open('src/giveway/config.json' , 'w', encoding='utf-8') 
            json.dump(giveway_config_data, giveway_config_data_write, indent = 4, ensure_ascii=False)

    if counter_commands == False:
        
        counter_commands_data = {
            "reset_counter": "!r_deaths",
            "set_counter": "!a_deaths", 
            "check_counter": "!deaths"
            }
        
        counter_commands_data_write = open('src/counter/commands.json' , 'w', encoding='utf-8') 
        json.dump(counter_commands_data, counter_commands_data_write, indent = 4, ensure_ascii=False)
    else:
        counter_commands_data_load = open('src/counter/commands.json' , 'r', encoding='utf-8')
        counter_commands_data_loads = json.load(counter_commands_data_load)
        counter_commands_list = {"reset_counter", "set_counter","check_counter"}
        
        if not all(key in counter_commands_data_loads for key in counter_commands_list): 
            
            counter_commands_data = {
                    "reset_counter": "!r_deaths",
                    "set_counter": "!a_deaths", 
                    "check_counter": "!deaths"
                }
        
            counter_commands_data_write = open('src/counter/commands.json' , 'w', encoding='utf-8') 
            json.dump(counter_commands_data, counter_commands_data_write, indent = 4, ensure_ascii=False)


def clear_files():

    commands_data = {}
    
    commands_data_write = open('src/config/commands.json' , 'w', encoding='utf-8') 
    json.dump(commands_data, commands_data_write, indent = 4, ensure_ascii=False)


    simple_commands_data = {}
    
    simple_commands_data_write = open('src/config/simple_commands.json' , 'w', encoding='utf-8') 
    json.dump(simple_commands_data, simple_commands_data_write, indent = 4, ensure_ascii=False)


    pathfiles_data = {}
    
    pathfiles_data_write = open('src/config/pathfiles.json' , 'w', encoding='utf-8') 
    json.dump(pathfiles_data, pathfiles_data_write, indent = 4, ensure_ascii=False)



    notifc_data = {
                    "TEXT_TITLE_REDEEM": "",
                    "TEXT_USER_REDEM": "",
                    "NOTF_GROUP_OBS": ""
                }

    notifc_data_write = open('src/config/notfic.json' , 'w', encoding='utf-8') 
    json.dump(notifc_data, notifc_data_write, indent = 4, ensure_ascii=False)


    obs_data = {    
        "OBS_HOST": "localhost",
        "OBS_PORT": "",
        "OBS_PASSWORD": "",
        "OBS_AUTO_CON": 0
        }
    
    obs_data_write = open('src/config/obs.json' , 'w', encoding='utf-8') 
    json.dump(obs_data, obs_data_write, indent = 4, ensure_ascii=False)


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


    timer_data = {
        "TIME": "120",
        "TIME_MAX": "120",
        "ENABLE": "0",
        "LAST": "",
        "MESSAGES": {}
        }
    
    timer_data_write = open('src/config/timer.json' , 'w', encoding='utf-8') 
    json.dump(timer_data, timer_data_write, indent = 4, ensure_ascii=False)


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


    auth_data = {'USERNAME': '', 'USERID': '', 'TOKEN': '', 'TOKENBOT': '', 'BOTUSERNAME': ''}

    auth_out_file = open("src/auth/auth.json", "w", encoding='utf-8')
    json.dump(auth_data, auth_out_file, indent=6,ensure_ascii=False)
    auth_out_file.close()


    config_commands_data = {
        
        "execute_giveway":"!sortear",
        "clear_giveway":"!limparsorteio",
        "check_name":"!checksorteio",
        "check_self_name":"!estounosorteio"
        
        }

    config_commands_data_write = open('src/config/commands_config.json' , 'w', encoding='utf-8') 
    json.dump(config_commands_data, config_commands_data_write, indent = 4, ensure_ascii=False)




    counter_commands_data = {
            "reset_counter": "!r_deaths",
            "set_counter": "!a_deaths", 
            "check_counter": "!deaths"
        }

    counter_commands_data_write = open('src/counter/commands.json' , 'w', encoding='utf-8') 
    json.dump(counter_commands_data, counter_commands_data_write, indent = 4, ensure_ascii=False)