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

latest_data = {}

CSV_ID ={

    "1": "electrical_msg_can.csv",
    "2": "info_msg_can.csv",
    "3": "driver_input_msg_can.csv",
    "4": "error_msg_can.csv",
    "5": "temperature_msg_can.csv",
}


def process_information(message):
    global latest_data
    parts = message.split(",")
    ID = parts[3].strip()
    hexa_message = parts[-1]
    binary_message = format(int(hexa_message, 16), f'0{len(hexa_message)*4}b')
    
    csv_information = {}
    ID_file = CSV_ID.get(ID)
        
    if ID_file is None:
        print("ID nicht bekannt:", ID)
        return      

    try:
        # Zuerst mit UTF-8 einlesen
        csv_file = pd.read_csv(ID_file, sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback auf Latin-1, um Sonderzeichen wie ° zu lesen
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

#hauptfunktion am lesen, lesen, lesen....
def main():

    while True:
       # message = ser.readline().strip()
       # decoded_message = message.decode(encodeing ='ascii', errors ='ignore')
        # Wähle zufällige Frame-ID basierend auf den verfügbaren IDs
        id_ = random.choice(list(CSV_ID.keys()))
        # Bestimme die benötigte Hex-Länge aus total_length (Bits → Nibbles)
        
        # Erzeuge einen Zufalls-Hex-String in der korrekten Länge
        rand_hex_str = ''.join(f"{randint(0, 15):X}" for _ in range(50))
        test_message = f"2,100,2,{id_},{rand_hex_str}"
        print(test_message)
        process_information(test_message)
        #print(latest_data)
       # push_to_db()
        time.sleep(0.5)



# wird von GUI_tele parallel aufgerufen
@app.route('/incoming_data', methods=['GET'])
def transfer_data():
    return jsonify(latest_data)
#
#    
#def push_to_db():
#    session = Session()
#    try:
#        current_time = int(time.time())
#        for key, value in latest_data.items():
#            if key in table_mapping:
#                table_name = table_mapping[key]
#                each_dict = table_name(time=current_time)
#                setattr(each_dict, key, value)
#                session.add(each_dict)
#                print("ausgeführt")
#        session.commit()
#    except Exception as e:
#        session.rollback()
#        print("Fehler", e)
#    finally:
#        session.close()
#
#
#
## klassen aus der alten datei 
#class Apps(Base):
#    __tablename__ = 'Apps'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    apps_accel = Column("apps_accel", Integer)
#    apps_brake = Column("apps_brake", Integer)
#
##class WheelSpeed(Base):
##    __tablename__ = 'wheel_speed'
##    id = Column(Integer, primary_key=True, autoincrement=True)
##    time = Column(Integer)
##    speed = Column("speed", Integer)
#
#class Soc(Base):
#    __tablename__ = 'soc'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    soc1 = Column("soc1", Integer)
#    soc2 = Column("soc2", Integer)
#
#class SteeringAngle(Base):
#    __tablename__ = 'steering_angle'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    steering_angle = Column("steering_angle", Integer)
#
#class CurrentSensor(Base):
#    __tablename__ = 'current_sensor'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    current_sensor = Column("current_sensor", Integer)
#    voltage_1 = Column("voltage_1", Integer)
#
#class Suspension(Base):
#    __tablename__ = 'suspension'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    suspension_fr = Column("suspension_fr", Integer)
#    suspension_fl = Column("suspension_fl", Integer)
#    suspension_rr = Column("suspension_rr", Integer)
#    suspension_rl = Column("suspension_rl", Integer)
#
#class Gyro(Base):
#    __tablename__ = 'gyro'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    sbg_roll = Column("sbg_roll", Float)
#    sbg_pitch = Column("sbg_pitch", Float)
#    sbg_yaw = Column("sbg_yaw", Float)
#
#class Temperature(Base):
#    __tablename__ = 'temperature'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    temperature_motor = Column("temperature_motor", Integer)
#    temperature_inverter = Column("temperature_inverter", Integer)
#    temperature_battery = Column("temperature_battery", Integer)
#
#class Inverter(Base):
#    __tablename__ = 'inverter'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    inverter_power = Column("inverter_power", Integer)
#
#class Errors(Base):
#    __tablename__ = 'errors'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    error_undervoltage = Column("error_undervoltage", Integer)
#    error_current = Column("error_current", Integer)
#    error_voltage = Column("error_voltage", Integer)
#    error_bspd = Column("error_bspd", Integer)
#    error_soc = Column("error_soc", Integer)
#    error_temperature_motor = Column("error_temperature_motor", Integer)
#    error_temperature_battery = Column("error_temperature_battery", Integer)
#    error_temperature_inverter = Column("error_temperature_inverter", Integer)
#
#table_mapping = {
#    "speed": Apps,
#    "apps_accel": Apps,
#    "temperature_inverter": Temperature,
#    "brake": Apps,
#    "temperature_battery": Temperature,
#    "temperature_motor": Temperature,
#    "power": Inverter,
#    "current_sensor": CurrentSensor,
#    "voltage_1": CurrentSensor,
#    "suspension_fl": Suspension,
#    "suspension_rr": Suspension,
#    "suspension_fr": Suspension,
#    "suspension_rl": Suspension,
#    "x_gyro": Gyro,
#    "y_gyro": Gyro,
#    "z_gyro": Gyro,
#    "battery_status": Errors,   # battery status treated as error status
#    "error_current": Errors,
#    "error_voltage": Errors,
#    "error_undervoltage": Errors,
#    "error_bspd": Errors,
#    "error_soc": Errors,
#    "error_temperature_motor": Errors,
#    "error_temperature_battery": Errors,
#    "error_temperature_inverter": Errors,
#    "soc1": Soc,
#    "soc2": Soc,
#}


if __name__ == "__main__":
#    Base.metadata.create_all(engine)
    Thread(target=lambda: app.run(host='127.0.0.1', port=8024, debug=False)).start()        # wurde mir vorgeschlagen habs nicht besser hinbekommen
    main()
    
        
