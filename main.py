from time import sleep
from bus import Bus
from worker import Worker
import logging
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

############### Configuration ###############
SERVER_PORT = 8001
IP_ADRESS = '192.168.0.1'
SERIAL_DEVICE = "/dev/ttyU0"
#SERIAL_DEVICE = "/dev/tty.usbserial-ftDW2LR5"
NUMBER_OF_LIGHTS = 6
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#############################################

bus = Bus(SERIAL_DEVICE, NUMBER_OF_LIGHTS)
worker = Worker(bus)
worker.start()
sleep(1)

class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        action = self.path.strip("/")
        logging.debug("Path: %s" % action)
        commands = action.split("/")
        try:
            if commands[0] == "default.css":
                self.serveFile("web/default.css")
            elif commands[0] == "apple-touch-icon.png":
                self.serveFile("web/apple-touch-icon.png")
            elif commands[0] == "":
                self.sendHTMLUI()
            else:
                logging.debug(commands)
                if len(commands) > 1 and commands[1] != "":
                    value = commands[1]
                    lv = len(value)
                    r = int(value[0], 16)*16 + int(value[1], 16)
                    g = int(value[2], 16)*16 + int(value[3], 16)
                    b = int(value[4], 16)*16 + int(value[5], 16)
                    worker.setColorParameter1(r,g,b)

                worker.setProgram(Worker.programs.get(commands[0]))
                self.sendHTMLUI()
        except IndexError:
            self.sendHTMLUI("Error: Invalid parameters")


    def sendHTMLUI(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.generateHTMLUI())
    
    def serveFile(self, filename):
        file = open(filename, 'r')
        self.send_response(200)
        self.send_header('Content-type', self.getContentType(filename))
        self.end_headers()
        self.wfile.write(file.read())
        file.close()

    def getContentType(self, filename):
        type = "application/octet-stream"
        if filename.lower().endswith("png"):
            type = 'image/png'
        return type
    
    def generateHTMLUI(self):
        body = ""
        filename = "web/index.html"
        file = open(filename, 'r')
        for line in file.readlines():
            body += line
        file.close()
        return body

try:
    server = HTTPServer((IP_ADRESS, SERVER_PORT), Server)
    server.serve_forever()

except KeyboardInterrupt:
    worker.shutdown()
    server.socket.close()

