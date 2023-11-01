import time
import threading
import json
from datetime import datetime
import socket
import hashlib
import base64

def error_log(ex):

    now = datetime.now()
    time_error = now.strftime("%d/%m/%Y %H:%M:%S")

    trace = []
    error_type = "Unknown"
    error_message = ""

    if isinstance(ex, BaseException):  # Verifica se ex é uma exceção
        tb = ex.__traceback__

        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next

        error_type = type(ex).__name__
        error_message = str(ex)
    else:
        error_message = ex

    error = str(f'Erro = type: {error_type} | message: {error_message} | trace: {trace} | time: {time_error} \n\n')

    print(error)

connections_by_type = {
    'music': {},
    'emote': {},
    'reward': {},
    'highlight': {},
    'video': {}
}

last_pong_times = {}


def on_client_disconnected(client_socket):

    client_id = str(client_socket.fileno())

    for type_conn, clients in connections_by_type.items():
        if client_id in clients:
            if clients[client_id]['socket'] == client_socket:
                client_socket.close()
                print(f"desconectado {client_id}")
                del clients[client_id]


def broadcast_message(message):

    message_loads = json.loads(message) 

    connection_type = message_loads['type']

    if connection_type in connections_by_type:

        for client_id, client_info in connections_by_type[connection_type].items():

            client_socket = client_info["socket"]

            try:

                client_socket.send(encode_websocket_frame(message))

            except Exception as e:

                error_log(e)


def add_client_to_type(connection_type, client_socket):

    client_id = str(client_socket.fileno())

    print(f"Conectado {client_id}")

    connections_by_type[connection_type][client_id] = {
        "socket": client_socket,
        "pong" : time.time()
    }

def message_received(client, message):

    if 'music' in message:

        add_client_to_type('music', client)
 
    elif 'emote' in message:

        add_client_to_type('emote', client)

    elif 'reward' in message:

        add_client_to_type('reward', client)
        
    elif 'video' in message:

        add_client_to_type('video', client)

    elif str('pong') in str(message):

        client_id = str(client.fileno())

        for type_conn, clients in connections_by_type.items():

            if client_id in clients:

                clients[client_id]['pong'] = time.time()

def decode_websocket_frame(data):

    payload_length = data[1] & 127
    if payload_length <= 125:
        payload_start = 2
        mask = data[2:6]
    elif payload_length == 126:
        payload_start = 4
        mask = data[4:8]
    elif payload_length == 127:
        payload_start = 10
        mask = data[10:14]

    decoded = bytearray()
    for i in range(payload_start, len(data)):
        decoded.append(data[i] ^ mask[(i - payload_start) % 4])

    return decoded.decode()

def encode_websocket_frame(data):

    payload = data.encode()
    length = len(payload)
    encoded = bytearray()

    if length <= 125:
        encoded.append(129)
        encoded.append(length)
    elif length >= 126 and length <= 65535:
        encoded.append(129)
        encoded.append(126)
        encoded.extend(length.to_bytes(2, byteorder='big'))
    else:
        encoded.append(129)
        encoded.append(127)
        encoded.extend(length.to_bytes(8, byteorder='big'))

    encoded.extend(payload)

    return encoded

def ping_clients():

    while True:

        for connection_type, clients in connections_by_type.items():

            for client_id, client_info in list(clients.items()):

                client_socket = client_info["socket"]

                try:

                    client_socket.send(encode_websocket_frame('ping'))

                    pong_time = client_info['pong']
                    ping_time = time.time()

                    interval =  ping_time - pong_time

                    if int(interval) > 6:
                        on_client_disconnected(client_socket)


                except Exception as e:
                    error_log(e)
                    on_client_disconnected(client_socket)

        time.sleep(5)

def handshake(client_socket):

    data = client_socket.recv(1024).decode()

    key = ''
    for line in data.split('\r\n'):
        if 'Sec-WebSocket-Key:' in line:
            key = line.split(':')[1].strip()

    response = (
        'HTTP/1.1 101 Switching Protocols\r\n'
        'Upgrade: websocket\r\n'
        'Connection: Upgrade\r\n'
        'Sec-WebSocket-Accept: {accept_key}\r\n'
        'Access-Control-Allow-Origin: *\r\n'
        '\r\n'
    ).format(accept_key=generate_accept_key(key))

    client_socket.send(response.encode())

def generate_accept_key(key):

    magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    concatenated = key + magic_string
    sha1 = hashlib.sha1(concatenated.encode())
    encoded = base64.b64encode(sha1.digest()).strip()
    return encoded.decode()

def handle_client(client_socket):

    handshake(client_socket)

    while True:

        try:
            data = client_socket.recv(1024)

            if not data:
                break

            decoded_message = decode_websocket_frame(data)
            message_received(client_socket, decoded_message)

        except Exception as e:
            if isinstance(e, UnicodeDecodeError):
                error_log(e)
                break
            if isinstance(e, ConnectionAbortedError):
                error_log(e)
                break

def start_server(host, port):

    th_ping = threading.Thread(target=ping_clients, args=())
    th_ping.start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    while True:

        client_socket, client_address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

