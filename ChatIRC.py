import socket
import os,sys
from datetime import datetime
import time

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

class TwitchBot():
    
    Connected = False

    def __init__(self, callback: None,TOKEN : str,USERNAME: str,CHANNEL: str , parent=None):
        
        """
        :param callback: callback function to be called when the bot receives a message
        :param CHANNEL: Channel name
        :param USERNAME: User nickname
        :param TOKEN: Twitch OAuth
        """
        
        self.callback = callback
        self.SERVER = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.TOKEN = 'oauth:' + TOKEN
        self.USERNAME = USERNAME
        self.CHANNEL = CHANNEL
        self.parent = parent
    
    def connect(self):

        self.Connecting = True

        while self.Connecting:

            try:
        
                self.IRC = socket.socket()
                
                self.IRC.connect((self.SERVER, self.PORT))
                self.IRC.send((
                    "CAP REQ :twitch.tv/commands twitch.tv/tags twitch.tv/membership\n"
                    f"PASS {self.TOKEN}\n"
                    f"NICK {self.USERNAME}\n"
                    f"JOIN #{self.CHANNEL}\n"
                ).encode())

                readbuffer_join = self.IRC.recv(4096).decode()

                if readbuffer_join != '':

                    for line in readbuffer_join.split("\r\n"):

                        if 'Login authentication failed' in line:

                            self.Connected = False
                            self.Connecting = False

                            self.callback(line)
                            self.IRC.close()

                        elif line != ':tmi.twitch.tv CAP * ACK :twitch.tv/commands twitch.tv/tags twitch.tv/membership':
                            
                            self.callback(line)
                            self.Connected = True
                            self.Connecting = False

            except socket.gaierror:
                self.IRC.close()
                self.callback(f"REERRORCONNCHAT | Erro de conexão: 'socket.gaierror connect()'. Tentando novamente em 10 segundos...")
                time.sleep(5)
                continue

            except ConnectionError as e:
                self.IRC.close()
                self.callback(f"REERRORCONNCHAT | Erro de conexão: 'ConnectionError connect()'. Tentando novamente em 10 segundos...")
                time.sleep(5)
                continue
            else:
                self.callback(f"REERRORCONNCHAT | Conectado!")
                break

        self.run()
                
    def send(self, message):
        
        """
        :param message:  Message to send to the channel
        """
        messageTemp = f"PRIVMSG #{self.CHANNEL} :{message}"

        try:
            self.IRC.send((messageTemp + "\n").encode())

        except socket.timeout:

            error_msg = "REERRORCONNCHAT | Erro de conexão: 'socket.timeout send()' O servidor não está respondendo. Verifique a conexão com a internet e tente novamente."
            self.callback(error_msg)

        except socket.error as e:

            error_msg = f"REERRORCONNCHAT | Erro de conexão: 'socket.error send()'. Verifique a conexão com a internet e tente novamente."
            self.callback(error_msg)


        except Exception as e:

            error_log(e)
            error_msg = f"REERRORCONNCHAT | Erro desconhecido: {str(e)}. Verifique o log de erros para mais informações."
            self.callback(error_msg)
        
    def run(self):

        while True:

            try:

                readbuffer = self.IRC.recv(4096).decode()
                
                for line in readbuffer.split("\r\n"):

                    if "PING" in line:
                        message = "PONG tmi.twitch.tv\r\n".encode()
                        self.IRC.send(message)
                        
                    elif line != '':
                        if self.callback:
                            self.callback(line)


            except socket.timeout:

                self.Connected = False
                self.Connecting = False
                self.IRC.close()
                self.callback(f"REERRORCONNCHAT | Erro de conexão: 'socket.timeout run()'. Tentando novamente em 10 segundos...")
                time.sleep(10)
                self.connect()

            except socket.error as e:
                self.Connected = False
                self.Connecting = False
                self.IRC.close()
                self.callback(f"REERRORCONNCHAT | Erro de conexão: 'socket.error run()'. Tentando novamente em 10 segundos...")
                time.sleep(10)
                self.connect()

            except Exception as e:
                error_log(e)
                self.Connected = False
                self.Connecting = False
                self.IRC.close()
                self.callback(F"REERRORCONNCHAT | Erro desconhecido '{str(e)} run()'. Tentando reconectar em 10 segundos...")
                time.sleep(10)
                self.connect()
    
    
