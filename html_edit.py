from bs4 import BeautifulSoup as bs

  
def update_notif(redeem,user,artist,type_not):

    html = open('web/src/html/notification.html')
    
    soup = bs(html, 'html.parser')

    redeem_block = soup.find("div", {"class": "redem_block"})
    music_block = soup.find("div", {"class": "music_block"})

    if type_not == 'redeem':
        
        music_block['style'] = 'display: none;'
        redeem_block['style'] = 'display: block;'
        
        redeem_name_tag = soup.find("span", {"class": "redem_name"})
        redeem_user_tag = soup.find("span", {"class": "redem_user"})

        redeem_name_tag.string = redeem
        redeem_user_tag.string = user
        
        
        # Alter HTML file to see the changes done
        with open("web/src/html/notification.html", "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))

    elif type_not == 'music':

        music_block['style'] = 'display: block;'
        redeem_block['style'] = 'display: none;'

        music_name_tag = soup.find("span", {"class": "music_name"})
        artist_name_tag = soup.find("span", {"class": "artist_name"})
        redeem_user_tag = soup.find("span", {"class": "redem_user"})

        music_name_tag.string = redeem
        artist_name_tag.string = artist
        redeem_user_tag.string = user
        
        # Alter HTML file to see the changes done
        with open("web/src/html/notification.html", "wb") as f_output:
            f_output.write(soup.prettify("utf-8"))


