from sqlalchemy import create_engine, Column,Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import serial, time, random, os, subprocess,re 
from datetime import datetime
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from itertools import cycle



baudrate = 115200
serial_port = "COM3"                        #bei windows, falls verändern 

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
   

#ser = serial.Serial(serial_port, baudrate, timeout=0.1)        #vorerst off

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
    f"+RXDATA:71,01,{random.randint(0,1)}",
    f"+RXDATA:72,01,{random.randint(0,1)}",
    f"+RXDATA:73,01,{random.randint(0,1)}",
    f"+RXDATA:74,01,{random.randint(0,1)}",
    f"+RXDATA:75,01,{random.randint(0,1)}",
    f"+RXDATA:76,01,{random.randint(0,1)}",
    f"+RXDATA:77,01,{random.randint(0,1)}",
    f"+RXDATA:78,01,{random.randint(0,1)}",

    "CORRUPTED_DATA",   
]

def simulated_uart_generator():
    for random_UART in cycle(SIMULATED_MESSAGES):
        yield random_UART
 


def get_sensor_values():
    uart_stream = simulated_uart_generator()      
    while True:
        #line = ser.readline().decode('ascii', errors='ignore').strip() 
        line = next(uart_stream).strip()        #ist für die simualtion

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

            print("übertragen: ",sensor_values)
        
            yield sensor_values
           
        else:
            yield {}


sensor_reader = get_sensor_values()                 
#extra speicher wo die daten eingespeist werden


def get_data(): 
    data = next(sensor_reader,{})
    print("!!!! attention !!!: ", data)
    current_time = int(datetime.now().strftime('%H%M%S'))
    

    apps_accel= data.get("accel", 0)
    apps_brake = data.get("brake",0)
    apps_speed = data.get("speed",0)


    temp_inverter = data.get("temp_inverter",0)
    temp_battery = data.get("temp_battery",0)
    temp_motor = data.get("temp_motor",0)

    power = data.get("power",0)
    current = data.get("current",0)

    voltage_1 = data.get("soc_1",0)       #SOC_1
    voltage_2 = data.get("soc_2",0)         #soc_2

    suspension_FL = data.get("FL",0)
    suspension_RR = data.get("RR",0)
    suspension_FR = data.get("FR",0)
    suspension_RL = data.get("RL",0)

    x_gyro = data.get("x_gyro",0)
    y_gyro = data.get("y_gyro",0)
    z_gyro = data.get("z_gyro",0)

    battery_status = data.get("battery_status",0)
    
    #errors in 0/1
    error_temperature_inverter = data.get("error", {}).get("inverter",1)
    error_temperature_Battery = data.get("error", {}).get("battery",1)
    error_temperature_motor = data.get("error", {}).get("motor", 1)
    error_soc = data.get("error", {}).get("soc", 1)
    error_BSPD = data.get("error", {}).get("BSPD", 1)
    error_current = data.get("error", {}).get("error_current", 1)
    error_voltage = data.get("error", {}).get("error_voltage", 1)
    error_inverter_undervoltage = data.get("error", {}).get("error_inverter_undervoltage", 1)
    error_test = data.get("error", {}).get("error_test", 1)


    return {
        "current_time": current_time,

        "speed":apps_speed,
        "ACCEL":apps_accel,
        "BRAKE":apps_brake,

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
        time_value = int(datetime.now().strftime('%H%M%S'))
        new_obj = None

    
        if sensor_id == "01":
            new_obj = AppsAccel(
                time=time_value, 
                accel=data.get("accel", 0)  
            )
        elif sensor_id == "02":
            new_obj = WheelSpeed(
                time=time_value, 
                speed=data.get("speed", 0)
            )
        elif sensor_id == "03":
            new_obj = AppsBrake(
                time=time_value, 
                brake=data.get("brake", 0)
            )
        elif sensor_id == "10":
            new_obj = TemperatureInverter(
                time=time_value, 
                value=data.get("temp_inverter", 0)
            )
        elif sensor_id == "11":
            new_obj = TemperatureBattery(
                time=time_value, 
                value=data.get("temp_battery", 0)
            )
        elif sensor_id == "12":
            new_obj = TemperatureMotor(
                time=time_value, 
                value=data.get("temp_motor", 0)
            )
        elif sensor_id == "15":
            new_obj = SteeringAngle(
                time=time_value, 
                steering_angle=data.get("steering_value", 0)
            )
        elif sensor_id == "20":
            new_obj = Inverter(
                time=time_value, 
                inverter_power=data.get("power", 0)
            )
        elif sensor_id == "21":
            new_obj = CurrentSensor(
                time=time_value, 
                current_sensor=data.get("current", 0.0)
            )
        elif sensor_id == "30":
            new_obj = SuspensionFL(
                time=time_value, 
                value=data.get("FL", 0)
            )
        elif sensor_id == "31":
            new_obj = SuspensionRR(
                time=time_value, 
                value=data.get("RR", 0)
            )
        elif sensor_id == "32":
            new_obj = SuspensionFR(
                time=time_value, 
                value=data.get("FR", 0)
            )
        elif sensor_id == "33":
            new_obj = SuspensionRL(
                time=time_value, 
                value=data.get("RL", 0)
            )
        elif sensor_id == "40":
            new_obj = Soc1(
                time=time_value, 
                soc1=data.get("soc_1", 0)
            )
        elif sensor_id == "41":
            new_obj = Soc2(
                time=time_value, 
                soc2=data.get("soc_2", 0)
            )
        elif sensor_id == "50":
            new_obj = GyroRoll(
                time=time_value, 
                value=float(data.get("x_gyro", 0.0))
            )
        elif sensor_id == "51":
            new_obj = GyroPitch(
                time=time_value, 
                value=float(data.get("y_gyro", 0.0))
            )
        elif sensor_id == "52":
            new_obj = GyroYaw(
                time=time_value, 
                value=float(data.get("z_gyro", 0.0))
            )
        elif sensor_id == "60":
            new_obj = BatteryStatus(
                time=time_value, 
                value=data.get("battery_status", 0)
            )

        elif sensor_id == "70":
            new_obj = ErrorBattery(
                time=time_value, 
                value=data.get("error", {}).get("battery", 0)
            )
        elif sensor_id == "71":
            new_obj = ErrorInverter(
                time=time_value, 
                value=data.get("error", {}).get("inverter", 0)
            )
        elif sensor_id == "72":
            new_obj = ErrorMotor(
                time=time_value, 
                value=data.get("error", {}).get("motor", 0)
            )
        elif sensor_id == "73":
            new_obj = ErrorSOC(
                time=time_value, 
                value=data.get("error", {}).get("soc", 0)
            )
        elif sensor_id == "74":
            new_obj = ErrorBSPD(
                time=time_value, 
                value=data.get("error", {}).get("BSPD", 0)
            )
        elif sensor_id == "75":
            new_obj = ErrorCurrent(
                time=time_value, 
                value=data.get("error", {}).get("error_current", 0)
            )
        elif sensor_id == "76":
            new_obj = ErrorVoltage(
                time=time_value, 
                value=data.get("error", {}).get("error_voltage", 0)
            )
        elif sensor_id == "77":
            new_obj = ErrorUndervoltage(
                time=time_value, 
                value=data.get("error", {}).get("error_inverter_undervoltage", 0)
            )
        elif sensor_id == "78":
            new_obj = ErrorTest(
                time=time_value, 
                value=data.get("error", {}).get("error_test", 0)
            )
        else:
            print(f"unbekannte id: {sensor_id}")
            return

        if new_obj:
            session.add(new_obj)
            session.commit()
            print(f"gespeichert: ID: {sensor_id} (Zeit: {time_value})")
        else:
            print("Konnte keine Daten erstellen")

    except Exception as e:
        session.rollback()
        print(f"Fehler bei sensor_id {sensor_id}: {str(e)}")
    finally:
        session.close()



class AppsAccel(Base):
    __tablename__ = 'apps_accel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    accel = Column(Integer)

class AppsBrake(Base):
    __tablename__ = 'apps_brake'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    brake = Column(Integer)

class WheelSpeed(Base):
    __tablename__ = 'wheel_speed'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    speed = Column(Integer)

class BatteryStatus(Base):
    __tablename__ = 'battery_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class Soc1(Base):
    __tablename__ = 'soc_1'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    soc1 = Column(Integer)

class Soc2(Base):
    __tablename__ = 'soc_2'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    soc2 = Column(Integer)

class SteeringAngle(Base):
    __tablename__ = 'steering_angle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    steering_angle = Column(Integer)

class CurrentSensor(Base):
    __tablename__ = 'current_sensor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    current_sensor = Column(Integer)

class SuspensionFL(Base):
    __tablename__ = 'suspension_fl'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class SuspensionRR(Base):
    __tablename__ = 'suspension_rr'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class SuspensionFR(Base):
    __tablename__ = 'suspension_fr'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class SuspensionRL(Base):
    __tablename__ = 'suspension_rl'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class GyroRoll(Base):
    __tablename__ = 'gyro_roll'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Float)

class GyroPitch(Base):
    __tablename__ = 'gyro_pitch'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Float)

class GyroYaw(Base):
    __tablename__ = 'gyro_yaw'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Float)

class TemperatureMotor(Base):
    __tablename__ = 'temperature_motor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class TemperatureInverter(Base):
    __tablename__ = 'temperature_inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class TemperatureBattery(Base):
    __tablename__ = 'temperature_battery'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class Inverter(Base):
    __tablename__ = 'inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    inverter_power = Column(Integer)

class ErrorBattery(Base):
    __tablename__ = 'error_battery'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class ErrorInverter(Base):
    __tablename__ = 'error_inverter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class ErrorMotor(Base):
    __tablename__ = 'error_motor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class ErrorTest(Base):
    __tablename__ = 'error_test'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)


class ErrorSOC(Base):
    __tablename__ = 'error_soc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class ErrorBSPD(Base):
    __tablename__ = 'error_bspd'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class ErrorCurrent(Base):
    __tablename__ = 'error_current'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class ErrorVoltage(Base):
    __tablename__ = 'error_voltage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)

class ErrorUndervoltage(Base):
    __tablename__ = 'error_undervoltage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Integer)
    value = Column(Integer)





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
scheduler.add_job(give_data_to_database, 'interval', seconds=0.3,coalesce=True)
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

