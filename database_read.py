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
   
    "+RXDATA:02,01,230",
    "CORRUPTED_DATA",   
]

def simulated_uart_generator():
    for random_UART in cycle(SIMULATED_MESSAGES):
        yield random_UART
        time.sleep(0.1)


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
            try:
                value = int(numbers[2])
            except ValueError:
                print("ungültiger Wert")
                continue
            
                         
            

            sensor_id = numbers[0]    
            sensor_values = {}

            match sensor_id:
                  case "01":
                      sensor_values["accel"] = value                          
                  case "02":
                     sensor_values["speed"] = value
                  case "03":
                      sensor_values["brake"] = value
                  case _:
                      print("zu faul für den rest")

            print("!!!!!!!!!!!",sensor_values)
            yield sensor_values


sensor_reader = get_sensor_values()                 #so ne kacke, wie soll ich darauf kommen es global aufzurufen, kotz


def get_data(): 
    sensor_data = next(sensor_reader)
    

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
        data = get_data()
        save_to_database(data)



def save_to_database(data):
    session = Session()

    try:

        apps_data = Apps(
            time = data["current_time"],
            apps_accel = data["ACCEL"],
            apps_brake = data["BRAKE"]
        )
        session.add(apps_data)

        # Tabelle WheelSpeed
        wheel_data = WheelSpeed(
            time = data["current_time"],
            speed = data["speed"]
        )
        session.add(wheel_data)

        # Tabelle Soc
        soc_data = Soc(
            time =data["current_time"],
            soc1 = data["soc_1"],
            soc2 = data["soc_2"]
        )
        session.add(soc_data)

        # Tabelle SteeringAngle
        steering_data = SteeringAngle(
            time = data["current_time"],
            steering_angle = random.randint(0, 720)  # Beispielwert
        )
        session.add(steering_data)

        # Tabelle CurrentSensor
        current_sensor_data = CurrentSensor(
            time = data["current_time"],
            current_sensor = data["current"]  
        )
        session.add(current_sensor_data)

        # Tabelle Suspension
        suspension_data = Suspension(
            time = data["current_time"],
            suspension_fr = data["FR"],
            suspension_fl = data["FL"],
            suspension_rr = data["RR"],
            suspension_rl = data["RL"]
        )
        session.add(suspension_data)

        # Tabelle Gyro
        gyro_data = Gyro(
            time = data["current_time"],
            sbg_roll = data["x_gyro"],
            sbg_pitch = data["y_gyro"],
            #sbg_yaw = data["z_gyro"]               # Muss ich noch hinzufügen, grad kein bock
        )
        session.add(gyro_data)

        # Tabelle Temperature
        temperature_data = Temperature(
            temperature_motor = data["temp_motor"],
            temperature_inverter = data["temp_inverter"],
            temperature_battery = data["temp_battery"]
        )
        session.add(temperature_data)

        #Tabelle Inverter
        inverter_data = Inverter(
            time = data["current_time"],
            input_inverter_power = data["power"]
        )
        session.add(inverter_data)

        # Tabelle Erros
        error_data= Errors(

            error_undervoltage=data["error"]["error_undervoltage"],  
            error_voltage=data["error"]["error_voltage"],
            error_bspd=data["error"]["BSPD"],
            error_soc=data["error"]["soc"],
            error_temperature_motor=data["error"]["motor"],
            error_temperature_battery=data["error"]["battery"],
            error_temperature_inverter=data["error"]["inverter"]
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
    temperature_motor = Column("TEMPERATURE Motor", Integer)
    temperature_inverter = Column("TEMPERATURE Inverter", Integer)
    temperature_battery = Column("TEMPERATURE Battery", Integer)


class Inverter(Base):
    __tablename__ = 'Inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    input_inverter_power = Column("Input/Inverter power", Integer)

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


#startet seperat  give_data_to_database mit interval
scheduler = BackgroundScheduler()
scheduler.add_job(give_data_to_database,'interval',seconds=2,coalesce=True,max_instances=3)
scheduler.start()




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


scheduler = BackgroundScheduler()
scheduler.add_job(backup, 'interval', seconds = 200,coalesce=True)
scheduler.start()



@app.route('/incoming_data', methods=['GET'])
def transfer_data():
    data = get_data()
    
    return jsonify(data)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host = '127.0.0.1',port = 8024, debug = False)

