from serial import Serial, EIGHTBITS, STOPBITS_ONE
import random
from time import sleep
import logging

class Bus:

    ALL = 255

    def __init__(self, serialPort, numberOfLights):
       self.con = Serial(
            port=serialPort,
            baudrate=19200,
            bytesize=EIGHTBITS,
            stopbits=STOPBITS_ONE
        )

       self.numberOfLights = numberOfLights
       self.sync()
       self.stop()

    def flush(self):
        self.con.flushInput()
        self.con.flushOutput()

    def sync(self, addr = 0):
        for x in range(15):
            self.con.write( chr(27) )
        self.con.write( chr( int(addr) ) )
        self.flush()

    def fadeRGB(self, addr, r, g, b, step = 5, delay = 0):
        logging.debug("fadeRGB %i, %i, %i, %i",addr, r, g, b)
# Reverse colors for transmission
        r = 255 - r
        g = 255 - g
        b = 255 - b

        self.con.write( chr( int(addr) ) )
        self.con.write(chr(1) )
        self.con.write( chr( int(step) ) )
        self.con.write( chr( int(delay) ) )
        self.con.write( chr( int(r) ) )
        self.con.write( chr( int(g) ) )
        self.con.write( chr( int(b) ) )
        self.zeros()
        self.flush()

    def zeros(self, count = 8):
        for x in range( int(count) ):
            self.con.write( chr(0) )

    def stop(self, addr = 255, fading = 1):
        self.con.write( chr( int(addr) ) )
        self.con.write( chr(8) )
        self.con.write( chr( int(fading) ) )
        self.zeros(12)
