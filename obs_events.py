import obsws_python as obs
import time
import json
import utils
import os

appdata_path = os.getenv('APPDATA')
is_started = 0
showing = 0

def load_config():
    
    with open(f'{appdata_path}/rewardevents/web/src/config/obs.json','r',encoding='utf-8') as config_file:
        config_data = json.load(config_file)
        
    return config_data
    
def test_obs_conn():

    try:
        config_data = load_config()

        cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])
        
        return True

    except:
        
        return False
    
def get_scenes():

    try:
        
        config_data = load_config()
    
        cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

        resp_OBS = cl.get_scene_list()

        scenes_resp = resp_OBS.scenes
        scene_list = {"scenes":[]}

        for item in scenes_resp:
            scenes = item['sceneName']
            scene_list['scenes'].append(scenes)

        scene_list_dump = json.dumps(scene_list)

        return scene_list_dump

    except:

        scene_list = {"scenes":["OBS Desconectado"]}
        scene_list_dump = json.dumps(scene_list)

        return scene_list_dump

def get_sources():

    try:

        config_data = load_config()
        
        cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

        actual_scene_name_resp = cl.get_current_program_scene()

        actual_scene_name = actual_scene_name_resp.current_program_scene_name

        resp_OBS = cl.get_scene_item_list(actual_scene_name)
        itens_resp = resp_OBS.scene_items
        source_list = {"source":[]}

        for item in itens_resp:

            sources = item['sourceName']
            source_list['source'].append(sources)

        source_list_dump = json.dumps(source_list)

        return source_list_dump

    except:

        source_list = {"source":['OBS Desconectado']}
        source_list_dump = json.dumps(source_list)
        
        return source_list_dump       

def get_filters(source_name):

    config_data = load_config()
    
    cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

    resp_OBS = cl.get_source_filter_list(source_name)

    filters_resp = resp_OBS.filters
    filter_list = {"filters":[]}

    for item in filters_resp:

        filters = item['filterName']
        filter_list['filters'].append(filters)
    
    filter_list_dump = json.dumps(filter_list)

    return filter_list_dump

def show_scene(scene_name, time_show, keep):

    try:
        config_data = load_config()
        
        cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

        actual_scene_name_resp = cl.get_current_program_scene()

        actual_scene_name = actual_scene_name_resp.current_program_scene_name

        if keep == 1:

            cl.set_current_program_scene(scene_name)

        else:

            cl.set_current_program_scene(scene_name)
            time.sleep(time_show)
            cl.set_current_program_scene(actual_scene_name)

    except:

        pass
        
def show_source(source_name, time_show, keep):

    global showing
    try:
        
        showing = 1

        config_data = load_config()
        
        cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

        scene_resp = cl.get_current_program_scene()
        scene_atual = scene_resp.current_program_scene_name

        item_id_resp = cl.get_scene_item_id(scene_atual,source_name)
        item_id = item_id_resp.scene_item_id

        if keep == 1:

            cl.set_scene_item_enabled(scene_atual,item_id,enabled= True)
            showing = 0

        else:

            cl.set_scene_item_enabled(scene_atual,item_id,enabled= True)
            time.sleep(int(time_show))
            cl.set_scene_item_enabled(scene_atual,item_id,enabled= False)

            showing = 0
    except:
        
        pass

def show_source_video(source_name, time_show):

    try:
    
        config_data = load_config()
        
        cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

        scene_resp = cl.get_current_program_scene()
        scene_atual = scene_resp.current_program_scene_name

        item_id_resp = cl.get_scene_item_id(scene_atual,source_name)

        item_id = item_id_resp.scene_item_id

        cl.set_scene_item_enabled(scene_atual,item_id,enabled= True)
        
        time.sleep(int(time_show))

        cl.set_scene_item_enabled(scene_atual,item_id,enabled= False)

    except:
        
        pass

def show_filter(source_name, filter_name, time_show,keep):

    try:
        
        config_data = load_config()

        cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

        if keep == 1:

            cl.set_source_filter_enabled(source_name,filter_name,True)

        else:

            cl.set_source_filter_enabled(source_name,filter_name,True)

            time.sleep(time_show)

            cl.set_source_filter_enabled(source_name,filter_name,False)

    except:
        pass

def create_source(type_id):
    
    
    config_data = load_config()

    cl = obs.ReqClient(host=config_data['OBS_HOST'], port=config_data['OBS_PORT'], password=config_data['OBS_PASSWORD'])

    scene_resp = cl.get_current_program_scene()
    scene_atual = scene_resp.current_program_scene_name


    if type_id == 'highlight':

        data_settings = {
            'is_local_file' : True,
            'local_file': f'{appdata_path}/rewardevents/web/src/html/highlight/iframe.html' 
        }
        
        cl.create_input(scene_atual,'Highlight RewardEvents','browser_source',data_settings,True)
    
    elif type_id == 'redeem':

        data_settings = {
            'is_local_file' : True,
            'local_file': f'{appdata_path}/rewardevents/web/src/html/redeem/iframe.html' 
        }
        
        cl.create_input(scene_atual,'Redeem RewardEvents','browser_source',data_settings,True)

    elif type_id == 'music':

        data_settings = {
            'is_local_file' : True,
            'local_file': f'{appdata_path}/rewardevents/web/src/html/music/iframe.html' 
        }
        
        cl.create_input(scene_atual,'Music RewardEvents','browser_source',data_settings,True)

    elif type_id == 'video':

        data_settings = {
            'is_local_file' : True,
            'local_file': f'{appdata_path}/rewardevents/web/src/html/video/iframe.html' 
        }
        
        cl.create_input(scene_atual,'Video RewardEvents','browser_source',data_settings,True)

    elif type_id == 'emote':

        data_settings = {
            'is_local_file' : True,
            'local_file': f'{appdata_path}/rewardevents/web/src/html/emote/iframe.html' 
        }
        
        cl.create_input(scene_atual,'Emote RewardEvents','browser_source',data_settings,True)

