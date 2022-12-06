import time,re
from rx.subject import Subject
import simple_chat as chat_res

class Chat(Subject):

    def __init__(self, channel: str, nickname: str, oauth: str):
        """
        :param channel: Channel name
        :param nickname: User nickname
        :param oauth: Twitch OAuth
        """
        super().__init__()

        self.irc = chat_res.IRC(nickname, password=oauth)
        self.irc.incoming.subscribe(self._message_handler)
        self.irc.start()

        self.channel = channel.lstrip('#')
        self.joined: bool = False

    def _message_handler(self, data: bytes) -> None:

        if not self.joined:
            self.irc.join_channel(self.channel)
            self.joined = True
            
        text = data.decode("UTF-8").strip('\n\r')
        
        self.on_next(
            chat_res.Message(text=text))

    def send(self, message: str) -> None:
        while not self.joined:
            time.sleep(0.01)
        self.irc.send_message(message=message, channel=self.channel)

    def __del__(self):
        self.irc.active = False
        self.dispose()
