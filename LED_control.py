import serial
import time
import struct

ser = serial.Serial('COM15', 115200)

time.sleep(5)

raw_input("Press any key to turn on LEFT LED")
ser.write(struct.pack('B',1)) #left

raw_input("Press any key to turn on FP LED")
ser.write(struct.pack('B',0)) #fp

raw_input("Press any key to turn on RIGHT LED")
ser.write(struct.pack('B',2)) #right

raw_input("Press any key to turn OFF all LEDs")
ser.write(struct.pack('B',3)) #All OFF

raw_input("Press any key to turn on LEFT LED")
ser.write(struct.pack('B',1)) #left

raw_input("Press any key to turn on FP LED")
ser.write(struct.pack('B',0)) #fp

raw_input("Press any key to turn on RIGHT LED")
ser.write(struct.pack('B',2)) #right

raw_input("Press any key to turn OFF all LEDs")
ser.write(struct.pack('B',3)) #All OFF

ser.close()
