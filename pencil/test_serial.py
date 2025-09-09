import serial
import time

# Use the correct port
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)  # wait for Arduino reset

print("Sending HOME...")
ser.write(b"HOME\n")

while True:
    line = ser.readline().decode().strip()
    if line:
        print("Arduino:", line)
