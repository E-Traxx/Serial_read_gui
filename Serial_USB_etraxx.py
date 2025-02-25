import serial
import struct


SERIAL_PORT = ''
BAUDRATE = 9600
TIMEOUT = 1
error= 'ignore'


ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUDRATE, timeout=TIMEOUT)

while True:
    raw_data = ser.readline()                           #liest die rohdaten wenn CAN ID 
    if not line:                                    #wenn keine daten vorhanden sind veruscht er es erneut
            continue

line = ser.decode(encoding ='UTF-8', errors = error)

print(line)





