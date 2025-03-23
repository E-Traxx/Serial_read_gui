from sqlalchemy import create_engine, Column,Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import serial, time, random, os, subprocess,re 
from datetime import datetime
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from itertools import cycle

#//// wie übergibt der zahlen? 001,01 oder 1 wie wird das dargestellt \\\\

baudrate = 115200
serial_port = "COM3"

user = 'root'
password = 'Etraxx_25'
host = 'localhost'
database = 'test_01'
port = "3306"  
path = '/Users/imagine_losing/Desktop/Backup_files'


connection_url= f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
engine = create_engine(connection_url, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

app = Flask(__name__)
   

#ser = serial.Serial(serial_port, baudrate, timeout=0.1)

SIMULATED_MESSAGES = [

    f"+RXDATA:03,01,{random.randint(100,500)}",
    f"+RXDATA:01,01,{random.randint(100,500)}",
    f"+RXDATA:02,01,{random.randint(100,500)}",
    f"+RXDATA:10,01,{random.randint(100,500)}",
    f"+RXDATA:11,01,{random.randint(100,500)}",
    f"+RXDATA:12,01,{random.randint(100,500)}",
    f"+RXDATA:20,01,{random.randint(100,500)}",
    f"+RXDATA:31,01,{random.randint(100,500)}",
    f"+RXDATA:15,01,{random.randint(100,500)}",
    f"+RXDATA:21,01,{random.randint(100,500)}",
    f"+RXDATA:30,01,{random.randint(100,500)}",
    f"+RXDATA:33,01,{random.randint(100,500)}",
    f"+RXDATA:32,01,{random.randint(100,500)}",
    f"+RXDATA:40,01,{random.randint(100,500)}",
    f"+RXDATA:41,01,{random.randint(100,500)}",
    f"+RXDATA:50,01,{random.randint(100,500)}",
    f"+RXDATA:51,01,{random.randint(100,500)}",
    f"+RXDATA:52,01,{random.randint(100,500)}",
    f"+RXDATA:60,01,{random.randint(100,500)}",
    f"+RXDATA:71,01,{random.randint(100,500)}",
    f"+RXDATA:72,01,{random.randint(100,500)}",
    f"+RXDATA:73,01,{random.randint(100,500)}",
    f"+RXDATA:74,01,{random.randint(100,500)}",
    f"+RXDATA:75,01,{random.randint(100,500)}",
    f"+RXDATA:76,01,{random.randint(100,500)}",
    f"+RXDATA:77,01,{random.randint(100,500)}",
    f"+RXDATA:78,01,{random.randint(100,500)}",

    "CORRUPTED_DATA",   
]

def simulated_uart_generator():
    for random_UART in cycle(SIMULATED_MESSAGES):
        yield random_UART
 


def get_sensor_values():

    uart_stream = simulated_uart_generator()      

    while True:
        #line = ser.readline().decode('ascii', errors='ignore').strip() #eigentlich diese aber das müssen wir anpassen weil keine einzelnen daten kommen
        line = next(uart_stream).strip()

        if not "RXDATA" in line:
            print("HALLO!!!!!!keine RXDATA Nachricht!!!!!")
            yield {}
            continue
        numbers = re.findall(r'\d+', line) 

        #schaut, ob die decoded nachricht mind. 3 teile hat

        if len(numbers) == 3:
            value = numbers[2]
            current_time = int(datetime.now().strftime('%H%M%S'))
            
            

            try:
                value = int(numbers[2])
            except ValueError:
                print("ungültiger Wert")
                continue

            sensor_id = numbers[0]    
            sensor_values = {
            "sensor_id": sensor_id,
            "error":{}
            }

            #habe die ports so mal gesetzt
            match sensor_id:
                case "01":
                    sensor_values["accel"] = value
                 
                case "02":
                    sensor_values["speed"] = value
        
                case "03":
                    sensor_values["brake"] = value
                    

                # Temperaturen
                case "10":
                    sensor_values["temp_inverter"] = value
         
                case "11":
                    sensor_values["temp_battery"] = value

                case "12":
                    sensor_values["temp_motor"] = value

                case "15":
                    sensor_values["steering_value"] = value  

                # Leistung und Strom
                case "20":
                    sensor_values["power"] = value
                
                case "21":
                    sensor_values["current"] = value
                   
                # Fahrwerk/Federwege
                case "30":
                    sensor_values["FL"] = value
              
                case "31":
                    sensor_values["RR"] = value
                    
                case "32":
                    sensor_values["FR"] = value
                  
                case "33":
                    sensor_values["RL"] = value
                # SOC
                case "40":
                    sensor_values["soc_1"] = value
                case "41":
                    sensor_values["soc_2"] = value

                #Gyro
                case "50":
                    sensor_values["x_gyro"] = float(value)
                case "51":
                    sensor_values["y_gyro"] = float(value)
                case "52":
                    sensor_values["z_gyro"] = float(value)

                #Batteriestatus
                case "60":
                    sensor_values["battery_status"] = value

                #error
                case "70":
                    sensor_values["error"]["battery"] = value
                case "71":
                    sensor_values["error"]["inverter"] = value
                case "72":
                    sensor_values["error"]["motor"] = value
                case "73":
                   
                    sensor_values["error"]["soc"] = value
                case "74":
                    
                    sensor_values["error"]["BSPD"] = value
                case "75":
                    
                    sensor_values["error"]["error_current"] = value
                case "76":
                    
                    sensor_values["error"]["error_voltage"] = value
                case "77":
                 
                    sensor_values["error"]["error_inverter_undervoltage"] = value
                case "78":
                    sensor_values["error"]["error_test"] = value

                case _:
                    print("Unbekannt, ew, whats that???!!!", sensor_id)

            print("!!!!!!!!!!!",sensor_values)
            yield sensor_values
        else:
            yield {}


sensor_reader = get_sensor_values()                 #so ne kacke, wie soll ich darauf kommen es global aufzurufen, kotz


def get_data(): 

    #daten  von da oben sollen hier einegragen werde


    current_time = int(datetime.now().strftime('%H%M%S'))

    #war vorher da, um an die GUI zu übertagen und die Datenbank, aber ändern wir ja 
    temp_inverter = random.randint(80, 128)
    temp_battery = random.randint(50, 64)
    temp_motor = random.randint(60, 100)

    power = random.randint(300, 500)
    current = random.uniform(90,120)

    voltage_1 = random.randint(0, 100)        #SOC_1
    voltage_2 = random.randint(0, 588)         #soc_2

    suspension_FL = random.randint(0,100)
    suspension_RR = random.randint(0,100)
    suspension_FR = random.randint(0,100)
    suspension_RL  = random.randint(0,100)

    x_gyro = random.uniform(-1, 1)
    y_gyro = random.uniform(-1, 1)
    z_gyro = random.uniform(-1, 1)

    battery_status = random.uniform(0,100)
    

    #errors in 0/1
    error_temperature_inverter = random.randint(0,1)
    error_temperature_Battery = random.randint(0,1)
    error_temperature_motor = random.randint(0,1)
    error_soc = random.randint(0,1)
    error_BSPD = random.randint(0,1)
    error_current = random.randint(0,1)
    error_voltage = random.randint(0,1)
    error_inverter_undervoltage = random.randint(0,1)
    error_test = random.randint(0,1)


    return {
        "current_time": current_time,

        "speed": latest_data.apps_accel,
        "ACCEL":latest_data.apps_accel,
        "BRAKE":latest_data.apps_brake,

        "temp_inverter": temp_inverter,
        "temp_battery":temp_battery,
        "temp_motor":temp_motor,

        "power": power,
        "current": current,

        "FL":suspension_FL,
        "RR":suspension_RR,
        "FR":suspension_FR,
        "RL":suspension_RL,

        "soc_1": voltage_1,
        "soc_2": voltage_2,

        "x_gyro": x_gyro,
        "y_gyro": y_gyro,
        "battery_status":battery_status,

        "error":{
            "battery":error_temperature_Battery,
            "inverter":error_temperature_inverter,
            "motor":error_temperature_motor,
            "soc":error_soc,
            "error_current":error_current,
            "BSPD": error_BSPD,
            "error_voltage":error_voltage,
            "error_undervoltage":error_inverter_undervoltage,
            "error_test":error_test
        }
    }



def give_data_to_database():
    data = next(sensor_reader,{})
    save_to_database(data)



def save_to_database():
    

    session = Session()
    try:
       #wollte mir eine neue logik zum eintragen in die Datenbank überlegen, 
       #wenn du bock hast änder das einfach wie du die datenbank am liebsten machen möchtest,
       #ich würde das so machen, dass wir die daten immer an ein dict. geben was global ist und was wir dann immer wenn es eine neuen wert gibt jeweils,
       #das aus dem dict. holen und wieder leeren, 

       #
         


        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Datenbankfehler: {e}")
    finally:
        session.close()




class Apps(Base):
    __tablename__ = 'APPS'  
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    apps_accel = Column("APPS ACCEL", Integer) 
    apps_brake = Column("APPS BRAKE", Integer)  


class WheelSpeed(Base):
    __tablename__ = 'wheel_speed'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    speed = Column(Integer)

class Soc(Base):
    __tablename__ = 'soc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    soc1 = Column("SOC 1", Integer)
    soc2 = Column("SOC 2", Integer)

class SteeringAngle(Base):
    __tablename__ = 'steering_angle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    steering_angle = Column("Steering angle", Integer)

class CurrentSensor(Base):
    __tablename__ = 'current_sensor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    current_sensor = Column("current sensor", Integer)

class Suspension(Base):
    __tablename__ = 'suspension'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    suspension_fr = Column("suspension FR", Integer)
    suspension_fl = Column("suspension FL", Integer)
    suspension_rr = Column("suspension RR", Integer)
    suspension_rl = Column("suspension RL", Integer)

class Gyro(Base):
    __tablename__ = 'gyro'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    sbg_roll = Column("SBG-roll", Float)  
    sbg_pitch = Column("SBG-pitch", Float)
    sbg_yaw = Column("SBG-yaw", Float)

class Temperature(Base):
    __tablename__ = 'Temperature'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    temperature_motor = Column("TEMPERATURE Motor", Integer)
    temperature_inverter = Column("TEMPERATURE Inverter", Integer)
    temperature_battery = Column("TEMPERATURE Battery", Integer)


class Inverter(Base):
    __tablename__ = 'Inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    inverter_power = Column("Input/Inverter power", Integer)

class Errors(Base):
    __tablename__ = 'errors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    error_undervoltage = Column("error undervotlage", Integer)
    error_current = Column("error current", Integer)
    error_voltage = Column("error voltage", Integer)
    error_bspd = Column("error BSPD", Integer)
    error_soc = Column("error soc", Integer)
    error_temperature_motor = Column("error Temperature motor", Integer)
    error_temperature_battery = Column("error Temperature battery", Integer)
    error_temperature_inverter = Column("error Temperature inverter", Integer)

#falls wir benötigen
def backup():

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(path, f"backup_{current_time}.sql")

    if not os.path.exists(path):
        os.makedirs(path)

    command = (
        f"mysqldump --no-tablespaces "
        f"--host={host} --port={port} --user={user} --password={password} {database} "
        f"> \"{backup_file}\" 2>/dev/null"
    )

    try:
        subprocess.run(command, shell=True)
        print(f"Backup erfolgreich: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Backup fehlgeschlagen: {e}")



#startet seperat  give_data_to_database mit interval
scheduler = BackgroundScheduler()
scheduler.add_job(give_data_to_database, 'interval', seconds=0.01)
scheduler.add_job(backup, 'interval', seconds=200, coalesce=True)
scheduler.start()



#ist vom server
@app.route('/incoming_data', methods=['GET'])
def transfer_data():
    data = get_data()
    
    return jsonify(data)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host = '127.0.0.1',port = 8024, debug = True)

