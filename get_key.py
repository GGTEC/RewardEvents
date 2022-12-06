import akeyless
import os ,sys
from dotenv import load_dotenv

extDataDir = os.getcwd()

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS

load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))


def start_apikey():
    
    configuration = akeyless.Configuration(
            host = "https://api.akeyless.io"
    )


    api_client = akeyless.ApiClient(configuration)
    api = akeyless.V2Api(api_client)

    body = akeyless.Auth(access_id=os.getenv('AccessID'), access_key=os.getenv('AccessKey'))
    res = api.auth(body)

    tokenakey = res.token

    body = akeyless.GetSecretValue(names=['REWARDEVENTS'], token=tokenakey)
    res = api.get_secret_value(body)
    
    ClientSecret = res['REWARDEVENTS']
    
    return ClientSecret