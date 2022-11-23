
def removestring(value):
    try:
        simbolos = [['[', ']'], ['(', ')'], ['"', '"']]
        for simbolo in simbolos:
            if value.find(simbolo[0]) and value.find(simbolo[1]):
                value = value.replace(value[(indice := value.find(simbolo[0])):value.find(simbolo[1], indice + 1) + 1],
                                    '').strip()
                
        return value
    except:
        return value


