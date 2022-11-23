import json

def auth_data():
    
    c = open('web/src/auth/auth.json')
    data = json.load(c)

    USERNAME = data['USERNAME']
    BROADCASTER_ID = data['BROADCASTER_ID']
    TOKEN = data['TOKEN']
    CODE = data['CODE']
    REFRESH_TOKEN = data['REFRESH_TOKEN']
    BOTNAME = data['BOTUSERNAME']
    TOKENBOT = data['TOKENBOT']

    
    return USERNAME,BROADCASTER_ID,BOTNAME,CODE,TOKENBOT,TOKEN,REFRESH_TOKEN
