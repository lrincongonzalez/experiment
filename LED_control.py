import serial
import time
import struct

ser = serial.Serial('COM15', 115200)

time.sleep(5)
print "ready"

while 1:
    ri = raw_input("Press 1:Left, 2:FP, 3:Right, 5:OFF, 8:esc")

    if ri == '1':
        ser.write(struct.pack('B',1)) #left
        print "LEFT LED ON"
    if ri == '2':
        ser.write(struct.pack('B',0)) #fp
        print "FP LED ON"
    if ri == '3':
        ser.write(struct.pack('B',2)) #right
        print "RIGHT LED ON"
    if ri == '5':
        ser.write(struct.pack('B',3)) #All OFF
        print "all LED OFF"
    if ri == '8':
        break;

ser.close()
