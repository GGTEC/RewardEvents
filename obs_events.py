import obsws_python as obs
import time
import json

config_file = open('web/src/config/obs.json','r',encoding='utf-8')
config_data = json.load(config_file)

host_data = config_data['OBS_HOST']
port_data = config_data['OBS_PORT']
pass_data = config_data['OBS_PASSWORD']
test_data = config_data['OBS_TEST_CON']


def test_obs_conn():

    if test_data == 1:

        try:
            cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

            return True

        except:
            
            return False

    else:

        return 'None'
    
def get_scenes():

    try:

        cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

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

        cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

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


    cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

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

        cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

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

    try:

        cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

        scene_resp = cl.get_current_program_scene()
        scene_atual = scene_resp.current_program_scene_name

        item_id_resp = cl.get_scene_item_id(scene_atual,source_name)
        item_id = item_id_resp.scene_item_id

        if keep == 1:

            cl.set_scene_item_enabled(scene_atual,item_id,enabled= True)

        else:

            cl.set_scene_item_enabled(scene_atual,item_id,enabled= True)
            time.sleep(time_show)
            cl.set_scene_item_enabled(scene_atual,item_id,enabled= False)
    
    except:
        pass

def show_filter(source_name, filter_name, time_show,keep):

    try:


        cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

        if keep == 1:

            cl.set_source_filter_enabled(source_name,filter_name,True)

        else:

            cl.set_source_filter_enabled(source_name,filter_name,True)

            time.sleep(time_show)

            cl.set_source_filter_enabled(source_name,filter_name,False)
    
    except:
        pass


def notification(tid):

    try:
        notifc_config_file = open('web/src/config/notfic.json','r',encoding='utf-8')
        notifc_config_Data = json.load(notifc_config_file)

        notifc_status = notifc_config_Data['HTML_ACTIVE']
        source_name = notifc_config_Data['HTML_TITLE']
        time_show = notifc_config_Data['HTML_TIME']

        if notifc_status == 1:

            cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

            scene_resp = cl.get_current_program_scene()
            scene_atual = scene_resp.current_program_scene_name

            item_id_resp = cl.get_scene_item_id(scene_atual,source_name)
            item_id = item_id_resp.scene_item_id

            cl.set_scene_item_enabled(scene_atual,item_id,enabled= True)
            time.sleep(time_show)
            cl.set_scene_item_enabled(scene_atual,item_id,enabled= False)
    
    except:
        pass

def notification_player(tid):

    try:
        notifc_config_file = open('web/src/config/notfic.json','r',encoding='utf-8')
        notifc_config_Data = json.load(notifc_config_file)

        notifc_status = notifc_config_Data['HTML_PLAYER_ACTIVE']
        source_name = notifc_config_Data['HTML_TITLE']
        time_show = notifc_config_Data['HTML_TIME']

        if notifc_status == 1:

            cl = obs.ReqClient(host=host_data, port=port_data, password=pass_data)

            scene_resp = cl.get_current_program_scene()
            scene_atual = scene_resp.current_program_scene_name

            item_id_resp = cl.get_scene_item_id(scene_atual,source_name)
            item_id = item_id_resp.scene_item_id

            cl.set_scene_item_enabled(scene_atual,item_id,enabled= True)
            time.sleep(time_show)
            cl.set_scene_item_enabled(scene_atual,item_id,enabled= False)
    
    except:
        pass
