import serial, time,re 


baudrate = 115200
serial_port = "COM3"  

ser = serial.Serial(serial_port, baudrate, timeout=0.3)  


ID_LENGHTS = {
    '1':2,
    '2':3,
    '3':2,
    '4':1,
    '5':2
}

def process_data():           # bekommt die daten aus seperating_data

    print()



def seperating_data(message):

    parts = message.split(',')

    if len(parts) < 4:
        print("zu wenig Nachrichten")
        continue

    hexa_message = parts[2] 
    ids = parts[3]

    i = 0
    while i <len(ids):
        id_data = ids[i]

        if id_data in ID_LENGHTS:
            lenght_in_bytes = ID_LENGHTS(id_data)
            lenght_in_hexa = lenght_in_bytes * 2
            #abhängig wie groß habe ihc jetzt die größe rus jeweiliger id erstmal




    process_data()
    print("star")



def main():

    #kommt noch ein loop
    message = ser.readline('utf-8', errors='ignore').strip()

    seperating_data(message)

    print("hier startet was")


        
        

