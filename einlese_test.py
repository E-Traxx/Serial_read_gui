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

       # raw = ser.readline().decode('ascii', errors='ignore').rstrip('\r\n')
#
       # if not raw.upper().startswith("AT+P2PUNICASTTX="):
       #     continue
#
       # stored_frame = raw
       # status = ser.readline().decode('ascii', errors='ignore').rstrip('\r\n')
#
       # if status.upper() == "OK":
       #     
       #     payload = stored_frame.split('=', 1)[1]            
       #     process_information(payload)
       #     push_to_db()
#
       # elif status == "AT_DUTYCYCLE_RESTRICTED":
       #     ser.write(b"ATZ\r\n")
       #     time.sleep(1.5)
#
       # else:
       #     print("unerwartet komisch hmm... Neustart")
       #     ser.write(b"ATZ\r\n")
       #     time.sleep(1.5)
            
        id_hex_raw = random.choice(list(CSV_ID.keys()))   
        id_hex     = f"{int(id_hex_raw, 16):04X}"         
        rand_hex_str = ''.join(f"{randint(0, 15):X}" for _ in range(80))

        test_message = f"AT+P2PUNICASTTX={id_hex}{rand_hex_str}"
    
        payload = test_message.split('=', 1)[1]            
        process_information(payload)

        print(latest_data)


        time.sleep(0.5)

if __name__ == "__main__":
    main()