import serial
from utils import csv_util as CSV_UTIL
import time
import threading

# USB to TTL port on macos (change based on your PORT)
ser = serial.Serial("/dev/tty.usbserial-B0044FJ3")
ser.baudrate = 115200
print("Serial PORT: ", ser.name)

# AUTHENTICATION code to send STM32 to keep Serial Communication
HEART_BEAT_CODE = "STM32PY"

""" 
COMMUNICATION PROTOCOL:

    1) from SERIAL-SERVER to STM32 
        String Structure: "{CODE}|MSG"
        
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

CSV_UTIL.Initialize_DB()

# deep researche about below code (especially abouy Threads)

serial_lock = threading.Lock()


def heartbeat_thread(ser: serial.Serial):
    while True:
        try:
            with serial_lock:
                heartbeat_str = f"H|{HEART_BEAT_CODE}\n"
                ser.write(heartbeat_str.encode())
            time.sleep(2)
        except Exception as e:
            print(f"Heartbeat thread error: {e}")
            break


# Start heartbeat thread
heartbeat = threading.Thread(target=heartbeat_thread, args=(ser,), daemon=True)
heartbeat.start()


try:
    while True:
        if ser.in_waiting > 0:
            data = ser.read_all().decode("utf-8").strip()
            data_list = data.split(" ")

            if len(data_list) == 0:  # for empty data like "" or " ".
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
                f"Received from STM32: {"SAVE" if rfid_mode == "1" else "READ"} {card_uid_str}")

            if rfid_mode == "1":
                # SAVE
                CSV_UTIL.save_db(ser, card_uid_str, lock=serial_lock)
            elif rfid_mode == "0":
                # READ
                CSV_UTIL.read_db(ser, card_uid_str, lock=serial_lock)
            else:
                pass
            # print(data_list)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    ser.close()
