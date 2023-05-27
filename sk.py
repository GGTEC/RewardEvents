import socket
import threading
import hashlib
import base64
import os
import time
from datetime import datetime

clients = []
ping_interval = 5

appdata_path = os.getenv('APPDATA')

def error_log(ex):

    now = datetime.now()
    time_error = now.strftime("%d/%m/%Y %H:%M:%S")

    trace = []
    tb = ex.__traceback__

    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "lineno": tb.tb_lineno
        })
        tb = tb.tb_next

    error = str(f'Erro = type: {type(ex).__name__} | message: {str(ex)} | trace: {trace} | time: {time_error} \n')

    with open(f"{appdata_path}/rewardevents/web/src/error_log.txt", "a+", encoding='utf-8') as log_file_r:
        log_file_r.write(error)

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

def send_ping(client_socket):
    while True:
        try:
            client_socket.send(encode_websocket_frame('ping'))
            time.sleep(ping_interval)

            # Espera pela resposta do cliente (pong)
            response = client_socket.recv(4048)

            decoded_response = decode_websocket_frame(response)

            if str('pong') in str(decoded_response):
                continue
            else:
                break

        except:
            break

    # Encerra a conexão com o cliente
    client_socket.close()
    clients.remove(client_socket)

def handle_client(client_socket):
    handshake(client_socket)
    clients.append(client_socket)

    threading.Thread(target=send_ping, args=(client_socket,)).start()

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

def broadcast_message(message):

    for client in clients:

        client.send(encode_websocket_frame(message))


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print('Servidor WebSocket iniciado em', host, 'na porta', port)

    while True:
        client_socket, address = server_socket.accept()
        print('Novo cliente conectado:', address)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

