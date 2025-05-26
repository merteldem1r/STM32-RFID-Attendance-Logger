# Developed by Ahsen Yenisey
# GitHub: https://github.com/ahsenyenisey

import sys
import serial
from utils import csv_util as CSV_UTIL
import time
import threading

# USB to TTL port on macos (change based on your PORT)
SERIAL_PORT: str = "/dev/tty.usbserial-B0044FJ3"

# HEARTBEAT_CODE used as Handshake mechanism between STM32 and Serial-Server
# this code is just an example and also it definitely should be stored in .env 
HEARTBEAT_CODE = "STM32PY"

ser = None

def Start_Serial():
    global ser
    try:
        ser = serial.Serial()
        ser.port = SERIAL_PORT
        ser.baudrate = 115200
        ser.open()
        print("Serial PORT:", ser.name)
    except serial.SerialException as e:
        print(f"Error opening serial port {SERIAL_PORT}: {e}")
        sys.exit(1)

Start_Serial()

CSV_UTIL.Initialize_DB()
serial_lock = threading.Lock()


def heartbeat_thread(ser: serial.Serial):
    while True:
        try:
            with serial_lock:
                heartbeat_str = f"H|{HEARTBEAT_CODE}\n"
                ser.write(heartbeat_str.encode())
            time.sleep(2)
        except Exception as e:
            print(f"Heartbeat thread error: {e}")
            break


# Start heartbeat thread
heartbeat = threading.Thread(target=heartbeat_thread, args=(ser,), daemon=True)
heartbeat.start()

print(f"Heartbeat thread started: sending '{HEARTBEAT_CODE}' code to STM32\n")

""" 
COMMUNICATION PROTOCOL:

    1) from SERIAL-SERVER to STM32 
        String Structure: "{CODE}|{MSG}"
        
            CODE:
                Definition:
                    Code to clarify the response. Either Hearbeat, Read or Save.

                Types:
                    H: Hearbeat (Every 2 seconds to keep Serial Communication) 
                    R: Read Response
                    S: Save Response
                        

            MSG:
                Definition:
                    Message from Serial Server.

                Types:
                    For Read:
                        ERR: User not found
                        {USER_INFO}: Found user inormaion (e.g. "Mert Eldemir-220201019")
                            
                    For Save: 
                        ERR: Saving failed
                        DUP: Duplicate. UID already saved
                        OK: UID saved to database
        Examples: 
            "H|STM32PY" (Auth code to keep serial connectino)
            
            "R|Ahsen Yenisey-220201019" (UID information response)
            "R|ERR" (UID not found)
            
            "S|ERR" Saving failed
                etc.
                
            
    2) from STM32 to SERIAL-SERVER
        String Structure: "{CODE} {UID}"
        
            CODE:
                Definition:
                    Code to clarify to the Serial Server what should be done with received UID. Either Read and send back information or Save to the database

                Types:
                    0: Read (to read UID and send response of user information)
                    1: Save (to save UID to database)
            UID: 
                Definiton:
                    4 byte UID information from RFID card
                    
        Examples:
            "0 D6 97 71 AF" (Save UID to database)
            "1 D6 97 71 AF" (Read card from database and response with info)
"""

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.read_all().decode("utf-8").strip()
            data_list = data.split(" ")

            if len(data_list) == 0: 
                continue

            if data == "HB":
                continue

            rfid_mode = data_list[0]
            card_uid_list = data_list[1:]
            card_uid_str = ' '.join(card_uid_list)

            # if card_uid_str == "HB":
            #     continue

            if not card_uid_str or card_uid_str == "HB":
                continue

            print(
                f"<- Received from STM32:  {data}")

            if rfid_mode == "1":
                # SAVE Request
                CSV_UTIL.save_db(ser, card_uid_str, lock=serial_lock)
            elif rfid_mode == "0":
                # READ Request
                CSV_UTIL.read_db(ser, card_uid_str, lock=serial_lock)
            else:
                pass
            # print(data_list)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    ser.close()
