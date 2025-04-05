import serial, time,re 
from flask import Flask, jsonify
from datetime import datetime


baudrate = 115200
serial_port = "COM3"  

#ser = serial.Serial(serial_port, baudrate, timeout=0.3)  


ID_LENGHTS = {
    '1': {'total_length': 12,
        'infos': [
            (8, "Leistung"),
            (4, "error_power")
        ]},
    '2':{ 'total_length': 24,
        'infos': [
            (16, "error"),
            (8, "OINK OINK")
        ]},
    '3': {'total_length': 16,
        'infos': [
            (12, "i_dont_know"),
            (4, "voltage ")
        ]},
    '4': {'total_length': 12,
        'infos': [
            (4, "notio"),
            (8, "hallo")
        ]},
    'A': {'total_length': 20,
        'infos': [
            (12, "time"),
            (8, "car")
        ]}
}

def flask_server(data):

    current_time = int(datetime.now().strftime('%H%M%S'))
    


    return






def process_data(pieces_of_hexa,id_str):           # bekommt die daten aus seperating_data

    temp = pieces_of_hexa   #einzelne nachricht
    details = ID_LENGHTS.get(id_str)    #komplette nachrichten
    fields = details.get('infos')   #infos 
    
    result = {}

    index = 0
    for info_lenght, value_description in fields:
        message_hexa_lenght = info_lenght // 4            #info_lenght in bit: 4 bit = 1 hexa, 1 byte = 8 bit = 2 hexa
        each_value_in_hexa = temp[index: index + message_hexa_lenght]
        index+=message_hexa_lenght

        each_value = int(each_value_in_hexa,16)

        print(f"ID: {id_str} - {value_description}: {each_value} (Hex: {each_value_in_hexa})")

        result[value_description] = each_value 

    flask_server(result)
    print(result)




def seperating_data(message):

    parts = message.split(',')
    if len(parts) < 4:
        
        raise ValueError("Die Nachricht entspricht nicht dem erwarteten Format")

    hexa_message = parts[2] 
    ids = parts[3]

    
    index = 0
    for id_data in ids:
        if id_data in ID_LENGHTS:
            message = ID_LENGHTS[id_data]
            total_length_hexa = message['total_length'] // 4
            
            seperated_info = hexa_message[index:index + total_length_hexa]
            process_data(seperated_info, id_data)

            index+=total_length_hexa
    print("Fertig mit der erhaltenen Nachricht")
        



def main():

    #kommt noch ein loop
    #message = ser.readline('utf-8', errors='ignore').strip()

    test_message = "2,n,FA110832A34F7BCDE83FA83C23BCD321DE21985F3421AB234C2321DB8896AFF12312,123A4"
    seperating_data(test_message)
    print("hier startet was")


if __name__ == "__main__":
    main()
        

