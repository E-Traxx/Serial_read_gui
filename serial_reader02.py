import serial, time,re, random



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
#ser = serial.Serial(serial_port, baudrate, timeout=0.3)  


ID_LENGHTS = {
    '1': {'total_length': 16, 'infos': [(8, "apps_speed"), (8, "apps_accel")
        ]},
    '2': {'total_length': 8, 'infos': [(1, "error_current"), (7, "temperature_inverter")
        ]},
    '5': {'total_length': 32, 'infos': [
        (8, "brake"),
        (8, "temperature_battery"),
        (8, "temperature_motor"),
        (8, "power")
        ]},
    '6': {'total_length': 32, 'infos': [
        (16, "current_sensor"),
        (16, "voltage_1")
        ]},
    '7': {'total_length': 32, 'infos': [
        (8, "suspension_fl"),
        (8, "suspension_rr"),
        (8, "suspension_fr"),
        (8, "suspension_rl")
        ]},
    '8': {'total_length': 48, 'infos': [
        (16, "x_gyro"),
        (16, "y_gyro"),
        (16, "z_gyro")
        ]},
    'B': {'total_length': 16, 'infos': [
        (16, "battery_status")
        ]},
    '9': {'total_length': 16, 'infos': [
        (8, "soc1"),
        (7, "soc2"),
        (1, "error_soc")
        ]},
    'C': {'total_length': 8, 'infos': [
        (1, "error_soc"),
        (1, "bspd"),
        (1, "error_current"),
        (1, "error_voltage"),
        (1, "error_undervoltage"),
        (1, "error_temperature_motor"),
        (1, "error_temperature_battery"),
        (1, "error_temperature_inverter")
        ]
    }
}

# verarbeitet die ID und jeweilige message in abhängikeit der jeweiligen länge

def process_data(pieces_of_hexa,id_str, signal):           

    temp_position = pieces_of_hexa   #einzelne nachricht in hexa
    details = ID_LENGHTS.get(id_str)    #komplette nachrichten
    messages = details.get('infos')   #infos von länge und art
    
    result = {'signal':signal}

    index = 0
    for info_lenght, value_description in messages:
        total_bits = len(temp_position) * 4                                         # gibt nochmal die total_length der bits aus
        binary_string = format(int(temp_position, 16), f'0{total_bits}b')           #wandelt die den string von hexa in binär um 

        each_value_bits = binary_string[index: index + info_lenght]                 #selbes schema wie in der unteren funktion über indexing nimmt der sich die werte

        index += info_lenght

        each_value = int(each_value_bits, 2)

        print(f"ID: {id_str} - {value_description}: {each_value} (vollständige Hex value: {temp_position})")

        result[value_description] = each_value 



    global latest_data
    latest_data = {**latest_data, **result}         

  
#zerlegt die eingegangene message nach komma in 4 teile und wichtig sind 3(message) und 4(id)
def seperating_data(message):

    parts = message.split(',')
    if len(parts) < 4:
        raise ValueError("Die Nachricht entspricht nicht dem erwarteten Format")
    hexa_message = parts[2] 
   #hexa_message = parts[-1]                #muss noch geändert werden wenn echte aten kommen
    ids = parts[3]                      # muss überprüft werden
    signal = parts[1]
    #decode again
    #hexa_message = hexa_message.encode('ascii')    !!!! muss dringend geprüft werden

    index = 0
    for id_data in ids:
        if id_data in ID_LENGHTS:
            message = ID_LENGHTS[id_data]
            total_length_hexa = message['total_length'] // 4        # teilt die bit länge durch 4 um die anzahl an hexa zeichen zu bekommen die er rausfiltern soll
            
            seperated_info = hexa_message[index:index + total_length_hexa]      #durch den index bekommt der den bereich der zeichen 
            process_data(seperated_info, id_data, signal)                               # hier gibt er den string ab zusammen mit der id

            index+=total_length_hexa
            


#hauptfunktion am lesen, lesen, lesen....
def main():

    while True:
       # message = ser.readline().strip()
       # decoded_message = message.decode(encodeing ='ascii', errors ='ignore')
        rand_hex_str = ''.join(f"{randint(0, 15):X}" for _ in range(80))        #random data
        test_message = f"2,100,{rand_hex_str},123A49B5678C"                       #random
       
        seperating_data(test_message)
        push_to_db()
        time.sleep(3)



# wird von GUI_tele parallel aufgerufen
@app.route('/incoming_data', methods=['GET'])
def transfer_data():
    return jsonify(latest_data)

    
def push_to_db():
    session = Session()
    try:
        current_time = int(time.time())
        for key, value in latest_data.items():
            if key in table_mapping:
                table_name = table_mapping[key]
                each_dict = table_name(time=current_time)
                setattr(each_dict, key, value)
                session.add(each_dict)
                print("ausgeführt")
        session.commit()
    except Exception as e:
        session.rollback()
        print("Fehler", e)
    finally:
        session.close()



# klassen aus der alten datei 
class Apps(Base):
    __tablename__ = 'Apps'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    apps_accel = Column("apps_accel", Integer)
    apps_brake = Column("apps_brake", Integer)

#class WheelSpeed(Base):
#    __tablename__ = 'wheel_speed'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    time = Column(Integer)
#    speed = Column("speed", Integer)

class Soc(Base):
    __tablename__ = 'soc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    soc1 = Column("soc1", Integer)
    soc2 = Column("soc2", Integer)

class SteeringAngle(Base):
    __tablename__ = 'steering_angle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    steering_angle = Column("steering_angle", Integer)

class CurrentSensor(Base):
    __tablename__ = 'current_sensor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    current_sensor = Column("current_sensor", Integer)
    voltage_1 = Column("voltage_1", Integer)

class Suspension(Base):
    __tablename__ = 'suspension'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    suspension_fr = Column("suspension_fr", Integer)
    suspension_fl = Column("suspension_fl", Integer)
    suspension_rr = Column("suspension_rr", Integer)
    suspension_rl = Column("suspension_rl", Integer)

class Gyro(Base):
    __tablename__ = 'gyro'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    sbg_roll = Column("sbg_roll", Float)
    sbg_pitch = Column("sbg_pitch", Float)
    sbg_yaw = Column("sbg_yaw", Float)

class Temperature(Base):
    __tablename__ = 'temperature'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    temperature_motor = Column("temperature_motor", Integer)
    temperature_inverter = Column("temperature_inverter", Integer)
    temperature_battery = Column("temperature_battery", Integer)

class Inverter(Base):
    __tablename__ = 'inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    inverter_power = Column("inverter_power", Integer)

class Errors(Base):
    __tablename__ = 'errors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    error_undervoltage = Column("error_undervoltage", Integer)
    error_current = Column("error_current", Integer)
    error_voltage = Column("error_voltage", Integer)
    error_bspd = Column("error_bspd", Integer)
    error_soc = Column("error_soc", Integer)
    error_temperature_motor = Column("error_temperature_motor", Integer)
    error_temperature_battery = Column("error_temperature_battery", Integer)
    error_temperature_inverter = Column("error_temperature_inverter", Integer)

table_mapping = {
    "apps_speed": Apps,
    "apps_accel": Apps,
    "temperature_inverter": Temperature,
    "brake": Apps,
    "temperature_battery": Temperature,
    "temperature_motor": Temperature,
    "power": Inverter,
    "current_sensor": CurrentSensor,
    "voltage_1": CurrentSensor,
    "suspension_fl": Suspension,
    "suspension_rr": Suspension,
    "suspension_fr": Suspension,
    "suspension_rl": Suspension,
    "x_gyro": Gyro,
    "y_gyro": Gyro,
    "z_gyro": Gyro,
    "battery_status": Errors,   # battery status treated as error status
    "error_current": Errors,
    "error_voltage": Errors,
    "error_undervoltage": Errors,
    "error_bspd": Errors,
    "error_soc": Errors,
    "error_temperature_motor": Errors,
    "error_temperature_battery": Errors,
    "error_temperature_inverter": Errors,
    "soc1": Soc,
    "soc2": Soc,
}


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    Thread(target=lambda: app.run(host='127.0.0.1', port=8024, debug=False)).start()        # wurde mir vorgeschlagen habs nicht besser hinbekommen
    main()
    
        
