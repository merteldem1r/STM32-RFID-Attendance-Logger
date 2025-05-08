import serial
from utils import csv_util as CSV_UTIL

ser = serial.Serial("/dev/cu.usbserial-10")
ser.baudrate = 9600
print(ser.name)

# TO DO:
# 1- when the programme first run check if db excel file exist (if not create db excel file)
# 2- create serial communication with microcontroller
# 3- create interval (2 seconds) of heartbeat to STM32
# connected. errorhandling
# 4- wait messages from STM32:
#       4.1- SAVE: save the card UID to db.csv, send "OK " message to STM32 (is it longer than 4 bytes)
#       4.2- READ: check from db if user exist, if exist send user info (e.g. "Mert Eldemir-220201019")
#                                if NOT exist send "ERR" message to STM32

CSV_UTIL.Initialize_DB()


try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode("utf-8").strip()
            data_list = data.split(" ")
            # print(data_list)

            rfid_mode = data_list[0]
            card_uid_list = data_list[1:]
            card_uid_str = ' '.join(card_uid_list)
            
            if rfid_mode == "1":
                # SAVE
                CSV_UTIL.save_db(ser, card_uid_str)
                
            elif rfid_mode == "0":
                # READ
                CSV_UTIL.read_db(ser, card_uid_str)
                
            else:
                pass

            # print(data_list)
            print(f"{data}")
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    ser.close()
