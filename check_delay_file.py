from datetime import datetime, timedelta
import json

mesages_file = open('src/mesages/mesages_file.json', "r", encoding='utf-8') 
mesages_data = json.load(mesages_file) 

message_error = mesages_data['response_delay_error']

def check_delay():
    
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    time_delay_file = open('src/config/prefix_tts.json')
    time_delay_data = json.load(time_delay_file)

    delay = time_delay_data['delay_date']

    delay_compare = time_delay_data['delay_config']

    t1 = datetime.strptime(delay, "%d/%m/%Y %H:%M:%S")
    t2 = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

    if t1 > t2:
        
        diff = t1 - t2
        
        message = message_error.replace('{seconds}', str(diff.seconds))
        value = False
        
        return message,value
        
    else:

        datetime_object = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

        time_delay_file = open('src/config/prefix_tts.json')
        time_delay_data = json.load(time_delay_file)
        delay_compare = time_delay_data['delay_config']

        future_date = datetime_object + timedelta(seconds= int(delay_compare))
        delay_save = future_date.strftime("%d/%m/%Y %H:%M:%S")

        time_delay_data['delay_date'] = delay_save

        time_delay_write = open('src/config/prefix_tts.json' , 'w', encoding='utf-8') 
        json.dump(time_delay_data, time_delay_write, indent = 4, ensure_ascii=False)
        
        message = 'OK'
        value = True
        
        return message,value


def check_global_delay():
    
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    time_delay_file = open('src/config/commands_config.json')
    time_delay_data = json.load(time_delay_file)

    delay = time_delay_data['delay_date']

    delay_compare = time_delay_data['delay_config'] 

    t1 = datetime.strptime(delay, "%d/%m/%Y %H:%M:%S")
    t2 = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

    if t1 > t2:
        
        diff = t1 - t2
        

        message = message_error.replace('{seconds}', str(diff.seconds))
        value = False
        
        return message,value
        
    else:

        datetime_object = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

        time_delay_file = open('src/config/commands_config.json')
        time_delay_data = json.load(time_delay_file)
        delay_compare = time_delay_data['delay_config']

        future_date = datetime_object + timedelta(seconds= int(delay_compare))
        delay_save = future_date.strftime("%d/%m/%Y %H:%M:%S")

        time_delay_data['delay_date'] = delay_save

        time_delay_write = open('src/config/commands_config.json' , 'w', encoding='utf-8') 
        json.dump(time_delay_data, time_delay_write, indent = 4, ensure_ascii=False)
        
        message = 'OK'
        value = True
        
        return message,value
