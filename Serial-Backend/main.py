import serial

ser = serial.Serial('/dev/cu.usbserial-10')
ser.baudrate = 9600
print(ser.name)

# TO DO:
# 1- when the programme first run check if db excel file exist (if not create db excel file)
# 2- create serial communication with microcontroller
# 3- create interval (2 seconds) of heartbeat to mq
# connected. errorhandling
# 4- wait messages from STM32:
#       4.1- SAVE: save the card UID to db.csv, send "OK " message to STM32
#       4.2- READ: chech from db if user exist, if exist send user info (e.g. "Mert Eldemir-220201019") 
#                                if NOT exist send "ERR" message to STM32

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            data_list = data.split(" ")
            
            if data_list[0] == 1:
                pass
                # WRITE
            else:
                # READ
                pass
                
            
        
            print(data_list)
            print(f"{data}")
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    ser.close()
