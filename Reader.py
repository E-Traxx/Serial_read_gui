import serial,time,re,random,os,json
import pandas as pd
from flask import Flask, jsonify
from random import randint
from threading import Thread
from sqlalchemy.orm import declarative_base  
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, String, MetaData, Float 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

baudrate        = 9600
serial_port     = "COM4"  
user            = 'Exxe25'
password        = 'Etraxx_25'
host            = 'localhost'
database        = 'database_etraxx'
port            = "3306"
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))                #erstell die file im Ordner wo Reader.py liegt
LOG_PATH        = os.path.join(BASE_DIR, "logs", "telemetry.log")

connection_url  = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
engine          = create_engine(connection_url, echo=True)
Base            = declarative_base()
Session         = sessionmaker(bind=engine)
app             = Flask(__name__)

latest_data     = {}                                                                        #GUI bezieht daraus die Daten
logged_snapshot = {}                                                                        #zusätzliches Dictionary, um doppelte Einträge zu vermeiden. Deswegen NULL-Werte wenn doppelte auftauchen, blöd bei den errors :(


log_dir = os.path.dirname(LOG_PATH)
if log_dir:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


CSV_ID = {
    #"4240": "electrical_msg_can.csv",
    "1F10": "electrical_msg_can.csv",
    #"4210": "info_msg_can.csv",
    "1A00": "info_msg_can.csv",
    "4230": "driver_input_msg_can.csv",
    #"00670": "driver_input_msg_can.csv",
    #"4200": "error_msg_can.csv",
    "0640": "error_msg_can.csv",
    #"4220": "temperature_msg_can.csv",}
    "41D0": "temperature_msg_can.csv",}


if not os.path.exists(LOG_PATH):
    print("Log file will be created on first write.\n")
else:
    print("Log file exists. Appending new data.\n")


def append_to_log(name, value):
    object_to_log = {
        "name": name,
        "value": value,
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "timestamp": time.time()
    }
    print(object_to_log)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(object_to_log) + "\n")




def process_information(frame,signal):
    frame = frame.strip()
    if len(frame) <= 4:
        return

    id_hex      = frame[:4]               
    ID          = id_hex.lstrip("0").upper() or "0"   
    payload_hex = frame[4:]      
    
    latest_data['signal_info'] = int(signal)                                                 # Signal Information
    
    binary_message = format(int(payload_hex, 16), f'0{len(payload_hex)*4}b')
    
  
    ID_file  = CSV_ID.get(ID)
    if not ID_file:
        return        

    try:
        csv_file = pd.read_csv(ID_file, sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        csv_file = pd.read_csv(ID_file, sep=";", encoding="latin1")

    for _, row in csv_file.iterrows():

        name              = row["Name"]
        start             = int(row["Startbit"])
        length            = int(row["Length [Bit]"])
        factor            = float(row["Factor"])

        binary_value      = binary_message[start:start+length]                                     
        decimal_value     = int(binary_value, 2)                                                       #kann man maybe durch in(value,16) ersetzen, aber läuft so auch
        computed_value    = decimal_value * factor

        latest_data[name] =  f"{computed_value:.2f}"                                                #übergibt namen aus CSV und Wert in latest_data, damit GUI die Daten bekommt
        append_to_log(name, computed_value)                                                          #Loggen der Daten in


def main():
    ser = serial.Serial(serial_port, baudrate, timeout=1)

    while True:
        raw = ser.readline().decode('ascii', errors='ignore').rstrip('\r\n')

        if not raw:         
            continue

        payload = raw.split(',')[-1]
        signal  = raw.split(',')[1] 

        process_information(payload,signal)
        push_to_db()

        print(latest_data)                                                                   #For debugging purposes, can be removed later
        #time.sleep(1)



@app.route('/incoming_data', methods=['GET'])
def transfer_data():
    return jsonify(latest_data) 




def push_to_db():
    session = Session()

    try:
        ts = int(time.time())
        row_cache: dict[type, Base] = {}
        #row_cache = {}
        for key, val_str in latest_data.items():

            
            try:
                numeric_val = float(val_str)
            except ValueError:
                numeric_val = None

            if numeric_val not in (0.0, 1.0) and logged_snapshot.get(key) == val_str:                               #klappt nicht bei den errors, da die immer 0 oder 1 sind
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
        print("DB-Fehler:", exc)
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
    time                           = Column(Integer)
    speed                          = Column(Float)                            
    info_soc                       = Column(Float)
    info_ing                       = Column(Integer)

class Temperature(Base):
    __tablename__ = 'temperature'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    temperature_u1_motor           = Column(Float)
    temperature_u2_motor           = Column(Float)
    temperature_u1_inverter        = Column(Float)
    temperature_u2_inverter        = Column(Float)
    temperature_highest_bms        = Column(Float)

class Inverter(Base):
    __tablename__ = 'inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    voltage_left_inverter          = Column(Float)           # V
    voltage_right_inverter         = Column(Float)           # V
    current_bms                    = Column(Float)           # A
    charge_bms                     = Column(Float)           # Ah


class Errors(Base):
    __tablename__ = 'errors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    error_bspd_software            = Column(Integer)
    error_can_bus                  = Column(Integer)
    error_general                  = Column(Integer)
    error_imd                      = Column(Integer)
    error_u2_inverter              = Column(Integer)
    error_latching                 = Column(Integer)
    error_temperature              = Column(Integer)
    error_undervoltage             = Column(Integer)
    bms_error                      = Column(Integer)
    error_u1_inverter              = Column(Integer)



table_mapping = {
    
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
