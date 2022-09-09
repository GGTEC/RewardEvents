#!/usr/bin/python
#    You would receive a notification when the channel you followed in 
#  Twitch had braodcasting
from tkinter import *
import webview
import json
import requests
from requests.structures import CaseInsensitiveDict
import apitoken

REDIRECT_URI ="http://localhost:5555"
TWITCH_PREFIX = "https://api.twitch.tv/kraken/"
SCOPE = "clips:edit+user:read:email+chat:edit+chat:read+channel:read:redemptions+channel:manage:redemptions"
OAUTH_URI = TWITCH_PREFIX + "oauth2/authorize?response_type=token&force_verify=true&client_id="+apitoken.CLIENTID+"&redirect_uri="+REDIRECT_URI+"&scope="+ SCOPE



class Webview_Auth:
    def __init__(self):
        self.window = webview.create_window('OAuth', '')
        self.window.events.loaded += self.on_loaded
        webview.start(self.get_current_url, self.window)
    
    
    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
                
    def get_current_url(self,window):
        window.load_url(OAUTH_URI)


    def save_access_token(self,access_token):
        
        out_file1 = open("src/auth/auth.json") 
        data1 = json.load(out_file1)
        
        username = data1['USERNAME']
    
        url = "https://api.twitch.tv/helix/users?login=" + username

        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer " + access_token
        headers["Client-Id"] = apitoken.CLIENTID

        resp = requests.get(url, headers=headers)
        user_id = json.loads(resp.text)
        
        try:
            user_id_resp = user_id['data'][0]['id']
            data = {}
            data['USERNAME'] = username
            data['USERID'] = user_id_resp
            data['TOKEN'] = access_token
            data['TOKENBOT'] = ''
            data['BOTUSERNAME'] = ''
            
            out_file = open("src/auth/auth.json", "w") 
            json.dump(data, out_file, indent = 6)  
            out_file.close()
            
            self.window.load_html("<!DOCTYPE html>\n"
                                    "<html lang='pt'>\n"
                                    "<head>\n"
                                    "<script type='text/javascript'>window.history.pushState('', '', '/');</script>"
                                    "<meta charset='UTF-8'>\n"
                                    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                                    "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css'>\n"
                                    "<title>Document</title>\n"
                                    "</head>\n"
                                    "<style>"
                                    "html, body {height: 100%;}\n"
                                    ".container {height: 100%;}\n"
                                    "</style>\n"
                                    "<body style='background-color: #191919;'>"
                                    "<div class='container'>\n<div class='row h-100'>\n"
                                    "<div class='col-sm-12 my-auto'>\n"
                                    "<div class='card card-block w-50 mx-auto text-center' style='background-color: #4b1a6a;color:azure'>\n"
                                    "<div class='card-body'>\n<h1 class='card-title'>Sucesso!</h5>\n<p class='card-text'>Pode fechar esta pagina.</p>\n"
                                    "</div>\n</div>\n</div>\n</div>\n</div>\n</body>\n</html>")
            
        except:
            pass


    def on_loaded(self):
        uri = self.window.get_current_url()
        try:
            access_token = self.find_between(uri,'#access_token=','&')

            if access_token:
                self.save_access_token(access_token)
        except:
            pass