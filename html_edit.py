from bs4 import BeautifulSoup as bs

  
def update_notif(redeem,user):

    html = open('src/html/notification.html')
    
    soup = bs(html, 'html.parser')
    
    redeem_name_tag = soup.find("span", {"class": "redem_name"})
    redeem_user_tag = soup.find("span", {"class": "redem_user"})

    redeem_name_tag.string = redeem
    redeem_user_tag.string = user
    
    # Alter HTML file to see the changes done
    with open("src/html/notification.html", "wb") as f_output:
        f_output.write(soup.prettify("utf-8"))