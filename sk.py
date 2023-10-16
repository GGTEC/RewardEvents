from websocket_server import WebsocketServer
import time
import threading
import json
import utils
from datetime import datetime


connections_by_type = {
    'music': {},
    'emote': {},
    'reward': {},
    'highlight': {},
    'video': {}
}

last_pong_times = {}


def on_client_connected(client, server):

    print(f'Cliente conectado: {client["address"]}')


def on_client_disconnected(client, server):

    client_id = client['id']

    print(f'Cliente desconectado: {client["address"]}')

    for connection_type in connections_by_type:
        if client_id in connections_by_type[connection_type]:
            del connections_by_type[connection_type][client_id]


def broadcast_message(message):

    message_loads = json.loads(message) 

    connection_type = message_loads['type']

    if connection_type in connections_by_type:
        for client in connections_by_type[connection_type].values():
            client_handler = client['handler']
            try:
                client_handler.send_message(message)
            except Exception as e:
                utils.error_log(e)


def add_client_to_type(connection_type, client):

    client_id = client['id']
    connections_by_type[connection_type][client_id] = {
        "handler": client['handler'],
        "addr": client['address'][0]
    }


def message_received(client, server, message):

    if 'music' in message:

        add_client_to_type('music', client)
 
    elif 'emote' in message:

        add_client_to_type('emote', client)

    elif 'reward' in message:

        add_client_to_type('reward', client)
        
    elif 'video' in message:

        add_client_to_type('video', client)


def ping_clients():

    while True:

        for connection_type, clients in connections_by_type.items():
            for client_id, client_info in clients.items():
                client_handler = client_info["handler"]
                try:
                    client_handler.send_message('ping')
                    last_pong_times[client_id] = time.time()
                except Exception as e:
                    utils.error_log(e)

        time.sleep(5)


def check_pong():

    while True:

        current_time = time.time()
        
        for client_id, last_pong_time in list(last_pong_times.items()):
            if current_time - last_pong_time > 5:
                for connection_type, clients in connections_by_type.items():
                    if client_id in clients:
                        try:
                            del clients[client_id]
                        except KeyError:
                            pass
                try:
                    del last_pong_times[client_id]
                except KeyError:
                    pass
        time.sleep(1)


def start_server(host, port):

    threading.Thread(target=ping_clients).start()
    threading.Thread(target=check_pong).start()

    server = WebsocketServer(port=port, host=host)
    server.set_fn_new_client(on_client_connected)
    server.set_fn_message_received(message_received)
    server.set_fn_client_left(on_client_disconnected)

    server.run_forever()



