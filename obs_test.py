import obsws_python as obs
import json

file_obs = open("src/config/obs.json")
data_obs = json.load(file_obs)

host = data_obs['OBS_HOST']
port_string = data_obs['OBS_PORT']
password = data_obs['OBS_PASSWORD']
port = int(port_string)

# pass conn info if not in config.toml
cl = obs.ReqClient(host='192.168.0.111', port='4445', password='12345678')

resp_scene = cl.get_scene_list()
resp_source = cl.get_scene_item_list('LIVE 2')


scene_name_list = []
for s in resp_scene.scenes:
    scene_name = s['sceneName']
    scene_name_list.append(scene_name)

print(scene_name_list)

source_list = []
for s in resp_source.scene_items:
    source_item_name = s['sourceName']
    source_list.append(source_item_name)

print(source_list)

current_scene = cl.get_current_program_scene().current_program_scene_name

itemid = cl.get_scene_item_id(current_scene,'KDR').scene_item_id
cl.set_scene_item_enabled(current_scene,itemid,enabled=True)







