import mysql.connector, random
from mysql.connector import errorcode
import serial,time
from flask import Flask, jsonify


DB_NAME = 'test_01'    


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
    

if __name__ == '__main__':
    app.run(host = '127.0.0.1',port = 8024)






data_base = mysql.connector.connect(user = 'root', password = 'Etraxx_25',host = 'localhost', database ='test_01')

if data_base.is_connected():
    print("connected with: " + DB_NAME)
else:
    print("Error, not connected")

cursor = data_base.cursor()

TABLES = {}
TABLES['APPS'] = (
    "CREATE TABLE `APPS` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['wheel_speed']=(
     "CREATE TABLE `wheel_speed` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"

)

TABLES['soc'] = (
     "CREATE TABLE `soc` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)


TABLES['brake_pressure'] = (
     "CREATE TABLE `brake_pressure` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "`time` int,"
    "`values` int"
    ") ENGINE=InnoDB"
)

TABLES['brake_throttle'] = (
     "CREATE TABLE `brake_throttle` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['steering_angle'] = (
     "CREATE TABLE `steering_angle` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['current_sensor'] = (
     "CREATE TABLE `current_sensor` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['suspension'] = (
     "CREATE TABLE `suspension` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['gyro'] = (
     "CREATE TABLE `gyro` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['disciplines'] = (
     "CREATE TABLE `disciplines` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['torque_slipcontroll'] = (
     "CREATE TABLE `torque_slipcontroll` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['mecanical_power'] = (
     "CREATE TABLE `mecanical_power` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

TABLES['errors'] = (
     "CREATE TABLE `errors` ("
    "id INT PRIMARY KEY AUTO_INCREMENT,"
    "  `time` int,"
    "  `values` int"
    ") ENGINE=InnoDB"
)

# erstellt die tables
for table_name in TABLES:
    table_description = TABLES[table_name]
    cursor.execute(table_description)
    
cursor.close()
data_base.close()





