import socket
import time

class TwitchBot():
    
    Connected = False

    def __init__(self, callback: None,TOKEN : str,USERNAME: str,CHANNEL: str ):
        
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
    
    def connect(self):
        
        self.IRC = socket.socket()

        Connecting = True

        self.IRC.connect((self.SERVER, self.PORT))
        self.IRC.send(
            (   
                "CAP REQ :twitch.tv/commands twitch.tv/tags twitch.tv/membership" + "\n" + 
                "PASS " + self.TOKEN + "\n" +
                "NICK " + self.USERNAME + "\n" +
                "JOIN #" + self.CHANNEL + "\n"
            )
            .encode()
        )

        while Connecting:

            try:
                readbuffer_join = self.IRC.recv(4096)
                readbuffer_join = readbuffer_join.decode("UTF-8").strip('\n\r')

                if readbuffer_join != '':
                    
                    if 'Login authentication failed' in readbuffer_join:

                        self.Connected = False
                        Connecting = False

                        self.callback(readbuffer_join)
                        self.IRC.close()

                    elif readbuffer_join != ':tmi.twitch.tv CAP * ACK :twitch.tv/commands twitch.tv/tags twitch.tv/membership':
                        
                        self.callback(readbuffer_join)
                        self.Connected = True
                        Connecting = False
                    
            except ConnectionAbortedError:
                
                self.Connected = False
                Connecting = False
                
                self.callback(readbuffer_join)
                self.IRC.close()
                
                


    def send(self, message):
        
        """
        :param message:  Message to send to the channel
        """
        
        messageTemp = "PRIVMSG #" + self.CHANNEL + " :" + message
        self.IRC.send((messageTemp + "\n").encode())

    def run(self):

        while True:
            try:
                readbuffer = self.IRC.recv(4096).decode()
            except:
                readbuffer = ""
            for line in readbuffer.split("\r\n"):
                if "PING" in line:
                    message = "PONG tmi.twitch.tv\r\n".encode()
                    self.IRC.send(message)
                elif line != '':
                    if self.callback:
                        self.callback(line)
    
    
