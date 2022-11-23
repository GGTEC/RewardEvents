import coverpy
import requests
import validators
from removesimbols import removestring
from pytube import YouTube, Search
from PIL import Image
from bs4 import BeautifulSoup as bs
import sys
from datetime import datetime, timedelta
from dateutil import tz
import yt_dlp

coverpy = coverpy.CoverPy()

def error_log(ex):

    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    trace = []
    tb = ex.__traceback__

    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "lineno": tb.tb_lineno
        })
        tb = tb.tb_next

    error = str(f'Erro = type:{type(ex).__name__} | message: {str(ex)} | trace: {trace} | time: {time} \n')

    print(error)

    with open("web/src/config/error_log.txt", "a+",encoding='utf-8') as log_file_r:
            log_file_r.write(error)


def album_search(user_input, redem_by_user):
    
    music = '0'
    artist = '0'
    url_youtube = "0"
    success = 0

    try:

        if validators.url(user_input):
            
            yt = YouTube(user_input)
            url_youtube = user_input
            video_title = yt.title
            rep_input = removestring(video_title)

        else:

            search_youtube = Search(user_input)
            result_search = search_youtube.results[0].__dict__
            url_youtube = result_search['watch_url']

            yt = YouTube(url_youtube)
            video_title = yt.title
            rep_input = user_input 

        try:
            
            result = coverpy.get_cover(rep_input, 1)
            album_art = result.artwork(625)
            artist = result.artist
            music = result.name

            img_data = requests.get(album_art).content

            album_art_mei = open(sys._MEIPASS + '/web/src/player/images/album.png', 'wb')
            album_art_mei.write(img_data)
            album_art_mei.close()

            album_art_local = open('web/src/player/images/album.png', 'wb')
            album_art_local.write(img_data)
            album_art_local.close()
        
        except:

            ydl_opts={
                'skip_download' : True,
                'noplaylist': True,
                'quiet' : True,
                'no_color': True,
                'write_thumbnails' : True,
                'outtmpl': 'web/src/player/images/album.%(ext)s',
                'force-write-archive' : True
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_youtube])

            img_webp = Image.open('web/src/player/images/album.webp').convert("RGB")
            img_webp.save('web/src/player/images/album.png','png')

            try:
                
                title_split = video_title.split(' - ')
                artist = title_split[0]
                music = title_split[1]
            
            except Exception as e:

                music = video_title
                artist = '0'

        success = 1

    except Exception as e:
        error_log(e)

        success = 0


    response_albumart = {
        
        "music" : music,
        "artist" : artist,
        "link" : url_youtube,
        "success" : success
    }

    return response_albumart
