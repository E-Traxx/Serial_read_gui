import serial,time,re,random
import pandas as pd
from flask import Flask, jsonify
from random import randint



baudrate = 115200
serial_port = "COM3"  



latest_data = { }

logged_snapshot = {}

CSV_ID ={
    "424": "electrical_msg_can.csv",
    "421": "info_msg_can.csv",
    "423": "driver_input_msg_can.csv",
    "420": "error_msg_can.csv",
    "422": "temperature_msg_can.csv",}


def process_information(frame):
    frame = frame.strip()

  
    id_hex      = frame[:4]               
    ID          = id_hex.lstrip("0").upper() or "0"   
    payload_hex = frame[4:]                

    

    binary_message = format(int(payload_hex, 16), f'0{len(payload_hex)*4}b')
    
    csv_information = {}
    ID_file = CSV_ID.get(ID)
            
    try:
        csv_file = pd.read_csv(ID_file, sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        csv_file = pd.read_csv(ID_file, sep=";", encoding="latin1")

    for _, row in csv_file.iterrows():

        name   = row["Name"]
        start  = int(row["Startbit"])
        length = int(row["Length [Bit]"])
        factor = float(row["Factor"])

        binary_value = binary_message[start:start+length]
        decimal_value = int(binary_value, 2)
        computed_value = decimal_value * factor

        latest_data[name] =  f"{computed_value:.2f}"



def main():

    while True:

        raw = ser.readline().decode('ascii', errors='ignore').rstrip('\r\n')
        payload = raw.split(',')[-1]       
        process_information(payload)
        print(latest_data)
        push_to_db()
        time.sleep(1)

if __name__ == "__main__":
    main()