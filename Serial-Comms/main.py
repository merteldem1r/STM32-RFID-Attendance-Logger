import serial

ser = serial.Serial('/dev/cu.usbserial-10')
ser.baudrate = 115200
print(ser.name)


try:
    while True:

        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print(f"Received: {data}")
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    ser.close()
