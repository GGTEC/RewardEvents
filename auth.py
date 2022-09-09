import json

def auth_data():
    
    c = open('src/auth/auth.json')
    data = json.load(c)

    USERNAME = data['USERNAME']
    USERID = data['USERID']
    BOTNAME = data['BOTUSERNAME']
    TOKENBOT = data['TOKENBOT']
    TOKEN = data['TOKEN']
    
    return USERNAME,USERID,BOTNAME,TOKENBOT,TOKEN
