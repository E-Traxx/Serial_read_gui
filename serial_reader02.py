import serial, time,re 


baudrate = 115200
serial_port = "COM3"  

#ser = serial.Serial(serial_port, baudrate, timeout=0.3)  


ID_LENGHTS = {
    '1':2,      # erhält werte von 
    '2':4,
    '3':6,
    '4':10,
    'A':5
}

def process_data(pieces_of_hexa,id_str):           # bekommt die daten aus seperating_data

    print(f"ID: {id_str}, processed piece: {pieces_of_hexa}")



def seperating_data(message):

    parts = message.split(',')
    if len(parts) < 4:
        
        raise ValueError("Die Nachricht entspricht nicht dem erwarteten Format")

    hexa_message = parts[2] 
    ids = parts[3]

    
    j = 0
    for id_data in ids:
        if id_data in ID_LENGHTS:
            lenght_in_bytes = ID_LENGHTS[id_data]
            lenght_in_hexa = lenght_in_bytes * 2

            
            seperated_info = hexa_message[j:j+lenght_in_hexa]
            process_data(seperated_info, id_data)

            j+=lenght_in_hexa
    print("Fertig mit der erhaltenen Nachricht")
        



def main():

    #kommt noch ein loop
    #message = ser.readline('utf-8', errors='ignore').strip()

    test_message = "2,n,FA20C832A34F7BCDE83FA83C23BCD321DE21985F3421AB234C2321DB8896AFF12,123A4"
    seperating_data(test_message)
    print("hier startet was")


if __name__ == "__main__":
    main()
        

