import json

class auth_data:
    def __init__(self, filename):
        with open(filename) as f:
            self.data = json.load(f)

    def USERNAME(self):
        return self.data['USERNAME']

    def BOTUSERNAME(self):
        return self.data['BOTUSERNAME']

    def BROADCASTER_ID(self):
        return self.data['BROADCASTER_ID']
    
    def BOT_ID(self):
        return self.data['BOT_ID']

    def TOKEN(self):
        return self.data['TOKEN']

    def TOKENBOT(self):
        return self.data['TOKENBOT']