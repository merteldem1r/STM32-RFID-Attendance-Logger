import serial
import time

ser = serial.Serial('/dev/tty.debug-console')
ser.baudrate = 115200

print("Serial at port: ", ser.name)

while True:
    val = ser.readline()
    val_str = str(val, "UTF-8")
    print(val_str)
    time.sleep(3)