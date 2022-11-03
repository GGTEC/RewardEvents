import os.path
import json
from datetime import datetime
import requests as req
import wget
import zipfile

src_dir = os.path.isdir('src')

now = datetime.now()
time_now = now.strftime("%d/%m/%Y %H:%M:%S")
t2 = str(time_now)


def update_language_file():

    lang_config_file = open('src/config/lang.json', 'r', encoding='utf-8')
    lang_config_data = json.load(lang_config_file)

    lang_selected = lang_config_data['lang']

    lang_file = open(f'src/lang/{lang_selected}.json', 'r', encoding='utf-8')
    lang_data = json.load(lang_file)


    if 'webhook_config_title' not in lang_data.keys():

        lang_data["webhook_config_button"] = "Configurar Discord"
        lang_data["webhook_config_title"] = "Configuração Discord"
        lang_data["webhook_url_label"] = "Webhook Url :"
        lang_data["webhook_edit_url_label"] = "Webhook Url Edit:"
        lang_data["webhook_color_label"] = "Cor do bloco (HEX sem '#')"
        lang_data["webhook_message_label"] = "Titulo do Bloco"
        lang_data["webhook_message_edit_label"] = "Titulo do Bloco para edição"
        lang_data["webhook_enable_edit_label"] = "Ativar Webhook para edição do Clip?"
        lang_data["webhook_enable_label"] = "Ativar Webhook ?"
        lang_data["webhook_desc_label"] = "Descrição do bloco"
        lang_data["config_webhook_saved"] = "Configuração Salva"
        lang_data["config_webhook_save_error"] = "Erro ao salvar o Webhook"

        lang_file.close()

        lang_file_w = open(f'src/lang/{lang_selected}.json', 'w', encoding='utf-8')
        json.dump(lang_data,lang_file_w,indent=4, ensure_ascii=False)
    

        messages_file_webhook = open("src/messages/messages_file.json", "r", encoding="utf-8")
        messages_data_webhook = json.load(messages_file_webhook)

        messages_data_webhook['create_clip_discord'] = "Um novo clip foi criado , confira! https://clips.twitch.tv/{clip_id}"
        messages_data_webhook['create_clip_discord_edit'] = "Link para editar o clip : {clip_url}"
        messages_data_webhook['clip_created_by'] = "Clip criado por :{user}"
        messages_file_webhook.close()

        messages_webhook_file_write = open("src/messages/messages_file.json", "w", encoding="utf-8")
        json.dump(messages_data_webhook, messages_webhook_file_write, indent=6, ensure_ascii=False)

        config_webhook_data = {}
        config_webhook_data['url'] = "NONE"
        config_webhook_data['url_edit'] = "NONE"
        config_webhook_data['color'] = "03b2f8"
        config_webhook_data['status'] = 0
        config_webhook_data['status_edit'] = 0

        config_webhook_file_save = open('src/config/discord.json','w',encoding='utf-8')
        json.dump(config_webhook_data, config_webhook_file_save, indent=6, ensure_ascii=False)


        mods = {}
        config_mod_file_save = open('src/config/mods.json','w',encoding='utf-8')
        json.dump(mods, config_mod_file_save, indent=6, ensure_ascii=False)



def check_files():

    if src_dir == False:
        create_src = os.path.join('', 'src')
        os.mkdir(create_src)

        response_acets = req.get("https://api.github.com/repos/GGTEC/RewardEvents/releases/latest")
        response_json_acets = json.loads(response_acets.text)
        url_src = response_json_acets['assets'][1]['browser_download_url']

        wget.download(url_src, "src.zip")

        with zipfile.ZipFile('src.zip', 'r') as zip_ref:
            zip_ref.extractall('src')
        
        os.remove('src.zip')


    update_language_file()
    
    return True

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
        
        "execute_giveaway":"!sortear",
        "clear_giveaway":"!limparsorteio",
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