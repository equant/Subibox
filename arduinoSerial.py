import serial

class ArduinoSerial:

    serialPorts = [
                 '/dev/ttyUSB0',
                 '/dev/ttyUSB1',
                 '/dev/ttyUSB2',
                 '/dev/ttyUSB3'
    ]

    def connect(self):

        for port in ArduinoSerial.serialPorts:
            try:
                arduino = serial.Serial(port, 28800, timeout=0)
            except:
                pass
                #print "Failed to connect on: ", port

        if arduino:
            self.arduino = arduino
            return arduino

        return 0
