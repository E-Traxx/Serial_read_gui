import serial, time,re, random
import pandas as pd


from flask import Flask, jsonify
from datetime import datetime
from random import randint
from threading import Thread

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, String, MetaData, Float 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATA_BASE = 'telemetry.db'
baudrate = 115200
serial_port = "COM3"  


user = 'root'
password = 'Etraxx_25'
host = 'localhost'
database = 'test_01'
port = "3306"  



connection_url= f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
engine = create_engine(connection_url, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

app = Flask(__name__)




latest_data = { }

logged_snapshot = {}

CSV_ID ={
    "1": "electrical_msg_can.csv",
    "2": "info_msg_can.csv",
    "3": "driver_input_msg_can.csv",
    "4": "error_msg_can.csv",
    "5": "temperature_msg_can.csv",}


def process_information(message):
    global latest_data
    parts = message.split(",")
    ID = parts[3].strip()
    hexa_message = parts[-1]
    binary_message = format(int(hexa_message, 16), f'0{len(hexa_message)*4}b')
    
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
       # message = ser.readline().strip()
       # decoded_message = message.decode(encodeing ='ascii', errors ='ignore')
        # Wähle zufällige Frame-ID basierend auf den verfügbaren IDs
        id_ = random.choice(list(CSV_ID.keys()))
        # Bestimme die benötigte Hex-Länge aus total_length (Bits → Nibbles)
        
        # Erzeuge einen Zufalls-Hex-String in der korrekten Länge
        rand_hex_str = ''.join(f"{randint(0, 15):X}" for _ in range(80))
        test_message = f"2,100,2,4,{rand_hex_str}"
    
        process_information(test_message)
        print(latest_data)
        #print(latest_data)
        push_to_db()
        time.sleep(0.5)


@app.route('/incoming_data', methods=['GET'])
def transfer_data():
    return jsonify(latest_data)

    
def push_to_db():
  
    session = Session()
    try:
        ts = int(time.time())
        row_cache: dict[type, Base] = {}

        for key, val_str in latest_data.items():

            # Skip unchanged values, except when the value is 0 or 1
            try:
                numeric_val = float(val_str)
            except ValueError:
                numeric_val = None

            if numeric_val not in (0.0, 1.0) and logged_snapshot.get(key) == val_str:
                continue
            logged_snapshot[key] = val_str

            TableCls = table_mapping.get(key)
            if not TableCls:
                continue  

            if TableCls not in row_cache:
                row_cache[TableCls] = TableCls(time=ts)

            try:
                val = float(val_str)
            except ValueError:
                val = None

            setattr(row_cache[TableCls], key, val)

        if not row_cache:
            return  

   
        session.add_all(row_cache.values())
        session.commit()

    except Exception as exc:
        session.rollback()
        print("DB‑Fehler:", exc)
    finally:
        session.close()




class Apps(Base):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    driver_input_demanded_throttle = Column(Float)   # %
    driver_input_break             = Column(Float)   # %
    driver_input_steering_angle    = Column(Float)   # %

class Speed(Base):
    __tablename__ = 'info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time  = Column(Integer)
    speed = Column(Float)                            
    info_soc = Column(Float)
    info_ing = Column(Integer)

class Temperature(Base):
    __tablename__ = 'temperature'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    temperature_u1_motor    = Column(Float)
    temperature_u2_motor    = Column(Float)
    temperature_u1_inverter = Column(Float)
    temperature_u2_inverter = Column(Float)
    temperature_highest_bms = Column(Float)

class Inverter(Base):
    __tablename__ = 'inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    voltage_left_inverter  = Column(Float)           # V
    voltage_right_inverter = Column(Float)           # V
    current_bms            = Column(Float)           # A
    charge_bms             = Column(Float)           # Ah


class Errors(Base):
    __tablename__ = 'errors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    error_bspd_software   = Column(Integer)
    error_can_bus         = Column(Integer)
    error_general         = Column(Integer)
    error_imd             = Column(Integer)
    error_u2_inverter     = Column(Integer)
    error_latching        = Column(Integer)
    error_temperature     = Column(Integer)
    error_undervoltage    = Column(Integer)
    bms_error             = Column(Integer)
    error_u1_inverter     = Column(Integer)



table_mapping: dict[str, Base] = {
    
    "driver_input_demanded_throttle": Apps,
    "driver_input_break": Apps,
    "driver_input_steering_angle": Apps,

    
    "info_soc": Speed,
    "speed": Speed,
    "info_ing": Speed,

   
    "temperature_u1_motor": Temperature,
    "temperature_u2_motor": Temperature,
    "temperature_u1_inverter": Temperature,
    "temperature_u2_inverter": Temperature,
    "temperature_highest_bms": Temperature,


    "voltage_left_inverter": Inverter,
    "voltage_right_inverter": Inverter,
    "current_bms": Inverter,
    "charge_bms": Inverter,


    "error_bspd_software": Errors,
    "error_can_bus": Errors,
    "error_general": Errors,
    "error_imd": Errors,
    "error_u2_inverter": Errors,
    "error_latching": Errors,
    "error_temperature": Errors,
    "error_undervoltage": Errors,
    "bms_error": Errors,
    "error_u1_inverter": Errors,
}

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    Thread(target=lambda: app.run(host='127.0.0.1', port=8024, debug=False)).start()        
    main()
    
        
