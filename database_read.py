from sqlalchemy import create_engine, Column,Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import serial, time, random, os, subprocess,re 
from datetime import datetime
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from itertools import cycle
import threading
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
    "+RXDATA:15,01,230",
    "+RXDATA:02,01,230",
    "+RXDATA:03,01,231",
    "+RXDATA:10,01,313",
    "+RXDATA:11,01,131",
    "+RXDATA:12,01,245",
    "+RXDATA:20,01,34",
    "+RXDATA:21,01,1",
    "+RXDATA:30,01,2",
    "+RXDATA:31,01,20",
    "+RXDATA:32,01,23",
    "+RXDATA:33,01,14",
    "+RXDATA:40,01,35",
    "+RXDATA:41,01,20",
    "+RXDATA:50,01,23",
    "+RXDATA:51,01,3",
    "+RXDATA:60,01,2",
    "+RXDATA:70,01,1",
    "+RXDATA:71,01,1",
    "+RXDATA:72,01,0",
    "+RXDATA:73,01,1",
    "+RXDATA:74,01,0",
    "+RXDATA:75,01,1",
    "+RXDATA:76,01,0",
    "+RXDATA:77,01,1",
    "+RXDATA:78,01,1",
    "+RXDATA:02,01,1",


    "CORRUPTED_DATA",   
]

def simulated_uart_generator():
    for random_UART in cycle(SIMULATED_MESSAGES):
        yield random_UART
        time.sleep(0.00001)


def get_sensor_values():

    uart_stream = simulated_uart_generator()      

    while True:
        #line = ser.readline().decode('ascii', errors='ignore').strip()
        line = next(uart_stream).strip()
        if not "RXDATA" in line:
            print("HALLO!!!!!!keine RXDATA Nachricht!!!!!")
            yield {}
            continue
        numbers = re.findall(r'\d+', line) 

        if len(numbers) >= 3:
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

   # data = next(sensor_reader,{})

    current_time = int(datetime.now().strftime('%H%M%S'))


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

        "speed": sensor_data.get("speed",0),
        "ACCEL":sensor_data.get("accel",0),
        "BRAKE":sensor_data.get("brake",0),

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



def save_to_database(data):
    
    session = Session()
    
    try:
        sensor_id = data.get("sensor_id")
        if sensor_id is None:
            return

        if sensor_id in ("01", "03"):
            apps_data = Apps(
                time = int(datetime.now().strftime('%H%M%S')),
                apps_accel = data.get("accel"),
                apps_brake = data.get("brake")
        )
            session.add(apps_data)

        if sensor_id == "02":
            wheel_data = WheelSpeed(
                time = int(datetime.now().strftime('%H%M%S')),
                speed = data.get("speed")
        )
            session.add(wheel_data)

        if sensor_id in ("40", "41"):
            soc_data = Soc(
                time =int(datetime.now().strftime('%H%M%S')),
                soc1 = data.get("soc_1"),
                soc2 = data.get("soc_2")
        )
            session.add(soc_data)

        if sensor_id == "15":
            steering_data = SteeringAngle(
                time = int(datetime.now().strftime('%H%M%S')),
                steering_angle = data.get("steering_value")  
        )
            session.add(steering_data)

        if sensor_id == "21":
            current_sensor_data = CurrentSensor(
                time = int(datetime.now().strftime('%H%M%S')),
                current_sensor = data.get("current")  
        )
            session.add(current_sensor_data)

        if sensor_id in ("30", "31", "32", "33"):
            suspension_data = Suspension(
                time = int(datetime.now().strftime('%H%M%S')),
                suspension_fr = data.get("FR"),
                suspension_fl = data.get("FL"),
                suspension_rr = data.get("RR"),
                suspension_rl = data.get("RL")
        )
            session.add(suspension_data)

        if sensor_id in ("50", "51"):
            gyro_data = Gyro(
                time = int(datetime.now().strftime('%H%M%S')),
                sbg_roll = data.get("x_gyro"),
                sbg_pitch = data.get("y_gyro"),
                #sbg_yaw = data["z_gyro"]               # Muss ich noch hinzufügen, grad kein bock
        )
            session.add(gyro_data)

        if sensor_id in ("10", "11", "12"):
            temperature_data = Temperature(
                time = int(datetime.now().strftime('%H%M%S')),
                temperature_motor = data.get("temp_motor"),
                temperature_inverter = data.get("temp_inverter"),
                temperature_battery = data.get("temp_battery")
        )
            session.add(temperature_data)

        if sensor_id == "20":
            inverter_data = Inverter(
                time = int(datetime.now().strftime('%H%M%S')),
                input_inverter_power = data.get("power")
        )
            session.add(inverter_data)

        if sensor_id in ("70", "71", "72", "73","74", "75", "76", "77","78"):
            error_data = Errors(
                time=int(datetime.now().strftime('%H%M%S')),  

                error_undervoltage=data.get("error", {}).get("error_inverter_undervoltage", None),
                error_voltage=data.get("error", {}).get("error_voltage", None),
                error_bspd=data.get("error", {}).get("BSPD", None),
                error_soc=data.get("error", {}).get("soc", None),
                error_temperature_motor=data.get("error", {}).get("motor", None),
                error_temperature_battery=data.get("error", {}).get("battery", None),
                error_temperature_inverter=data.get("error", {}).get("inverter", None),
    )

            session.add(error_data)

        session.commit()

    except Exception as e:
        session.rollback()  
        print(f"Datenbankfehler: {e}")

    finally:
        session.close() 




class Apps(Base):
    __tablename__ = 'APPS'  
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer,nullable=False)
    apps_accel = Column("APPS ACCEL", Integer,nullable=True) 
    apps_brake = Column("APPS BRAKE", Integer,nullable=True)  


class WheelSpeed(Base):
    __tablename__ = 'wheel_speed'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer,nullable=False)
    speed = Column(Integer,nullable=True)

class Soc(Base):
    __tablename__ = 'soc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer,nullable=False)
    soc1 = Column("SOC 1", Integer, nullable=True)
    soc2 = Column("SOC 2", Integer, nullable=True)

class SteeringAngle(Base):
    __tablename__ = 'steering_angle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer, nullable=False)
    steering_angle = Column("Steering angle", Integer, nullable=True)

class CurrentSensor(Base):
    __tablename__ = 'current_sensor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer, nullable=False)
    current_sensor = Column("current sensor", Integer, nullable=True)

class Suspension(Base):
    __tablename__ = 'suspension'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer, nullable=False)
    suspension_fr = Column("suspension FR", Integer, nullable=True)
    suspension_fl = Column("suspension FL", Integer, nullable=True)
    suspension_rr = Column("suspension RR", Integer, nullable=True)
    suspension_rl = Column("suspension RL", Integer, nullable=True)

class Gyro(Base):
    __tablename__ = 'gyro'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer, nullable=False)
    sbg_roll = Column("SBG-roll", Float, nullable=True)  
    sbg_pitch = Column("SBG-pitch", Float, nullable=True)
    sbg_yaw = Column("SBG-yaw", Float, nullable=True)

class Temperature(Base):
    __tablename__ = 'Temperature'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer, nullable=False)
    temperature_motor = Column("TEMPERATURE Motor", Integer, nullable=True)
    temperature_inverter = Column("TEMPERATURE Inverter", Integer, nullable=True)
    temperature_battery = Column("TEMPERATURE Battery", Integer, nullable=True)


class Inverter(Base):
    __tablename__ = 'Inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer, nullable=False)
    input_inverter_power = Column("Input/Inverter power", Integer, nullable=True)

class Errors(Base):
    __tablename__ = 'errors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer, nullable=False)
    error_undervoltage = Column("error undervotlage", Integer, nullable=True)
    error_current = Column("error current", Integer, nullable=True)
    error_voltage = Column("error voltage", Integer, nullable=True)
    error_bspd = Column("error BSPD", Integer, nullable=True)
    error_soc = Column("error soc", Integer, nullable=True)
    error_temperature_motor = Column("error Temperature motor", Integer, nullable=True)
    error_temperature_battery = Column("error Temperature battery", Integer, nullable=True)
    error_temperature_inverter = Column("error Temperature inverter", Integer, nullable=True)


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
scheduler.add_job(give_data_to_database, 'interval', seconds=1)
scheduler.add_job(backup, 'interval', seconds=200, coalesce=True)
scheduler.start()


@app.route('/incoming_data', methods=['GET'])
def transfer_data():
    data = get_data()
    
    return jsonify(data)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host = '127.0.0.1',port = 8024, debug = True)

