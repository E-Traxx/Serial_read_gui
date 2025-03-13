import random
from mysql.connector import errorcode
from sqlalchemy import create_engine,text
import serial,time
from flask import Flask, jsonify


   


app = Flask(__name__)

@app.route('/incoming_data', methods=['GET'])
def get_data(): 
    speed = random.randint(0,115)
    accel = random.randint(0,100)
    brake = random.randint(0,100) 

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

    battery_status = random.uniform(0,100)
    

    #errors in 0/1
    error_temperature_inverter = random.randint(0,1)
    error_temperature_Battery = random.randint(0,1)
    error_temperature_motor = random.randint(0,1)
    error_soc = random.randint(0,1)
    error_BSPD = random.randint(0,1)
    error_current = random.randint(0,1)
    error_votlage = random.randint(0,1)
    error_inverter_undervoltage = random.randint(0,1)
    error_test = random.randint(0,1)


    return jsonify({
        "speed": speed,
        "ACCEL":accel,
        "BRAKE": brake,

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
            "error_voltage":error_votlage,
            "error_undervotlage":error_inverter_undervoltage,
            "error_test":error_test
        }
    })



user = 'root'
password = 'Etraxx_25'
host = 'localhost'
database = 'test_01'

connection_url= f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
engine = create_engine(connection_url, echo=True)



TABLES = {}
TABLES['APPS'] = (
    "CREATE TABLE IF NOT EXISTS `APPS` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `APPS ACCEL` int,"
    "  `APPS BRAKE` int"
    ") ENGINE=InnoDB"
)

TABLES['wheel_speed']=(
     "CREATE TABLE IF NOT EXISTS `wheel_speed` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `speed` int"
    ") ENGINE=InnoDB"

)

TABLES['soc'] = (
     "CREATE TABLE IF NOT EXISTS `soc` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `SOC 1` int,"
    "  `SOC 2` int"
    ") ENGINE=InnoDB"
)


#TABLES['brake_pressure'] = (
#     "CREATE TABLE `brake_pressure` ("
#    "id INT PRIMARY KEY AUTO_INCREMENT,"
#    "`time` int,"
#    "`values` int"
#    ") ENGINE=InnoDB"
#
#
#TABLES['brake_throttle'] = (
#   "CREATE TABLE `brake_throttle` ("
#  "id INT PRIMARY KEY AUTO_INCREMENT,"
#  "  `time` int,"
#  "  `values` int"
#  ") ENGINE=InnoDB"
#
#
TABLES['steering_angle'] = (
     "CREATE TABLE IF NOT EXISTS `steering_angle` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `Steering angle` int"
    ") ENGINE=InnoDB"
)

TABLES['current_sensor'] = (
     "CREATE TABLE IF NOT EXISTS `current_sensor` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `current sensor` int"
    ") ENGINE=InnoDB"
)

TABLES['suspension'] = (
     "CREATE TABLE IF NOT EXISTS `suspension` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `suspension FR` int,"
    "  `suspension FL` int,"
    "  `suspension RR` int,"
    "  `suspension RL` int"
    ") ENGINE=InnoDB"
)

TABLES['gyro'] = (
     "CREATE TABLE IF NOT EXISTS `gyro` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `SBG-roll` int,"
    "  `SBG-pitch` int,"
    "  `SBG-yaw` int"
    ") ENGINE=InnoDB"
)

TABLES['Temperature'] = (
     "CREATE TABLE IF NOT EXISTS `Temperature` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `TEMPERATURE Motor` int,"
    "  `TEMPERATURE Inverter` int,"
    "  `TEMPERATURE Battery` int"
    ") ENGINE=InnoDB"
)

#TABLES['torque_slipcontroll'] = (
#     "CREATE TABLE `torque_slipcontroll` ("
#    "id INT PRIMARY KEY AUTO_INCREMENT,"
#    "  `time` int,"
#    "  `values` int"
#    ") ENGINE=InnoDB"
#)

TABLES['Inverter'] = (
     "CREATE TABLE IF NOT EXISTS `Inverter` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `Input/Inverter power` int"
    ") ENGINE=InnoDB"
)

TABLES['errors'] = (
     "CREATE TABLE IF NOT EXISTS `errors` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `error undervotlage` int,"
    "  `error current` int,"
    "  `error voltage` int,"
    "  `error BSPD` int,"
    "  `error soc` int,"
    "  `error Temperature motor` int,"
    "  `error Temperature battery` int,"
    "  `error Temperature inverter` int"
    ") ENGINE=InnoDB"
)

# erstellt die tables
with engine.connect() as connection:
    for table_name in TABLES:
        table_description = TABLES[table_name]
        connection.execute(text(table_description))






if __name__ == '__main__':
    app.run(host = '127.0.0.1',port = 8024)


