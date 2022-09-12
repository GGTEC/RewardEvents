import json
import random
from random import randint
import time
from smt import send_message
import _thread


def timer():
    
    while True:
        
        timer_data_file = open('src/config/timer.json' , 'r', encoding='utf-8')
        timer_data = json.load(timer_data_file)
        
        timer_int = timer_data['TIME']
        timer_max_int = timer_data['TIME_MAX']
        next_timer = randint(timer_int,timer_max_int)
        
        timer_message = timer_data['MESSAGES']
        last_key = timer_data['LAST']
        
        
        if "1" in timer_message.keys():
            
            key_value = timer_message.keys()
            message_key = random.choice(list(key_value))
            
            if message_key == last_key:
                
                time.sleep(1)
                
            else:
                
                timer_data['LAST'] = message_key
                
                update_last_file = open('src/config/timer.json' , 'w', encoding='utf-8') 
                json.dump(timer_data, update_last_file, indent = 4,ensure_ascii=False)
                
                update_last_file.close()
            
                send_message(timer_message[message_key],'TIMER')  
        else:
            
            time.sleep(10)
            
        time.sleep(next_timer)

_thread.start_new_thread(timer, (2,))