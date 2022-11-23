import json
import random
from random import randint
import time
import smt
import auth
from smt import send_message
from datetime import datetime

def error_log(message):

    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")


    error = f"erro = {message} horario = {time} \n"

    with open("web/src/config/error_log.txt", "a+",encoding='utf-8') as log_file_r:
            log_file_r.write(error)


def timer(tid):
    
    print('Modulo timer iniciado')

    while True:

        USERNAME,BROADCASTER_ID,BOTNAME,CODE,TOKENBOT,TOKEN,REFRESH_TOKEN = auth.auth_data()

        if CODE and TOKENBOT:

            try:

                timer_data_file = open('web/src/config/timer.json' , 'r', encoding='utf-8')
                timer_data = json.load(timer_data_file)

                timer_int = timer_data['TIME']
                timer_max_int = timer_data['TIME_MAX']
                
                next_timer = randint(timer_int,timer_max_int)

                if smt.value == True:

                    timer_status_file = open('web/src/config/commands_config.json' , 'r', encoding='utf-8')
                    timer_status = json.load(timer_status_file)
                    
                    status = timer_status['STATUS_TIMER']
                    
                    
                    if status == 1:
                        
                        timer_message = timer_data['MESSAGES']
                        last_key = timer_data['LAST']
                        
                        key_value = timer_message.keys()


                        try:
                            message_key = random.choice(list(key_value))
                            
                            if message_key == last_key:
                                
                                time.sleep(1)
                                
                            else:
                                
                                timer_data['LAST'] = message_key
                                
                                update_last_file = open('web/src/config/timer.json' , 'w', encoding='utf-8') 
                                json.dump(timer_data, update_last_file, indent = 4,ensure_ascii=False)
                                
                                update_last_file.close()
                            
                                send_message(timer_message[message_key],'TIMER') 

                                time.sleep(next_timer) 

                        except Exception as e:

                            pass

                            time.sleep(10)

                    else:
                        time.sleep(10)
                else:
                    time.sleep(10)
            except:
                time.sleep(5)
        else:
            time.sleep(10) 

        

