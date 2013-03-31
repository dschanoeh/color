from bus import Bus
from time import sleep
from threading import Thread
from datetime import datetime, timedelta
import logging
import random

class Worker(Thread):

    programs = {
            "Black": 0,
            "White": 1,
            "FixedColor": 2,
            "FadeAround": 3,
            "Quit": 255
            }

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        self.interrupt = 0
        self.currentProgram = 1
        self.lastSync = datetime.now()

    def setProgram(self, program):
        self.currentProgram = program
        self.interrupt = 1

    def shutdown(self):
        self.currentProgram = Worker.programs.get("Quit")
        self.interrupt = 1

    def setColorParameter1(self, r, g, b):
        logging.debug("Color parameter 1 set %i %i %i", r, g, b)
        self.r1 = r
        self.g1 = g
        self.b1 = b

    def run(self):
        while 1:
            if self.currentProgram == Worker.programs.get("Black"):
                logging.debug("Worker switching to program Black")
                self.__programBlack()
            elif self.currentProgram == Worker.programs.get("FixedColor"):
                logging.debug("Worker switching to program FixedColor")
                self.__programFixedColor()
            elif self.currentProgram == Worker.programs.get("White"):
                logging.debug("Worker switching to program White")
                self.__programWhite()
            elif self.currentProgram == Worker.programs.get("FadeAround"):
                logging.debug("Worker switching to program FadeAround")
                self.__programFadeAround()
            elif self.currentProgram == Worker.programs.get("Quit"):
                logging.debug("Worker exiting.")
                return

    def __programBlack(self):
        while 1:
            self.bus.fadeRGB(255,0,0,0)
            if self.__mySleep(0.2):
                return

    def __programWhite(self):
        while 1:
            self.bus.fadeRGB(255,255,255,255)
            if self.__mySleep(0.2):
                return

    def __programFixedColor(self):
        while 1:
            self.bus.fadeRGB(255,self.r1,self.g1,self.b1)
            if self.__mySleep(0.2):
                return

    def __programFadeAround(self):
        self.bus.fadeRGB(255,self.r1,self.g1,self.b1)
        while 1:
            for light in range(self.bus.numberOfLights):

                r = self.r1 + (20 * (random.random() - 0.5));
                g = self.g1 + (20 * (random.random() - 0.5));
                b = self.b1 + (20 * (random.random() - 0.5));

                if r < 0:
                    r = 0
                if r > 255:
                    r = 255
                if g < 0:
                    g = 0
                if g > 255:
                    g = 255
                if b < 0:
                    b = 0
                if b > 255:
                    b = 255

                self.bus.fadeRGB(light, r, g, b, step=2, delay=5)
                sleep(0.3)
            if self.__mySleep(5):
                return

    def __mySleep(self, seconds):
        if self.interrupt == 1:
            self.interrupt = 0
            return 1

        sleep(seconds)

        if (datetime.now() - self.lastSync) > timedelta(minutes=1):
            logging.debug("Resyncing...")
            self.bus.sync()
            self.lastSync = datetime.now()


        if self.interrupt == 1:
            self.interrupt = 0
            return 1

        return 0
