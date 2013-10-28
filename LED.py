import serial
import time
import struct
import pygame

#as opposed to LED_control.py, this one allows you to press the arrows to turn on the LEDs

result = pygame.init()

if not result[1] == 0:
    print "PyGame initialization failed"
    exit(1)

screen = pygame.display.set_mode((320, 240))

ser = serial.Serial('COM15', 115200)

time.sleep(5)

while 1:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ser.write(struct.pack('B',1)) #left
                print "left"
            if event.key == pygame.K_DOWN:
                ser.write(struct.pack('B',3)) #ALL OFF
                print "ALL OFF"
            if event.key == pygame.K_RIGHT:
                ser.write(struct.pack('B',2)) #right
                print "right"
            if event.key == pygame.K_UP:
                ser.write(struct.pack('B',0)) #fp
                print "Fixation Point"
            if event.key == pygame.K_ESCAPE:
                ser.close()
                print "esc"
                quit()