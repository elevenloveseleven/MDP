import time
import serial
from cache import Rpi_Queue
from message import *

SER_BAUD = 115200
SER_PORT = "/dev/ttyACM"


class ArduinoInterface(object):
    _write_delay = 0.5
    _calib_delay = 1

    def __init__(self):
        self.status = False
        self.ser = None
        self.port_no = 1
        self.writeq = Rpi_Queue()

    def connect(self):
        if self.ser is not None:
            self.ser.close()
            time.sleep(2)
        try:
            self.port_no = self.port_no ^ 1
            self.ser = serial.Serial(SER_PORT + str(self.port_no), SER_BAUD)
            time.sleep(2)
            if self.ser is not None:
                self.status = True
                print("SER--Connected to Arduino!")
            while not self.writeq.is_empty():
                if self.write_from_q(self.writeq.peek()):
                    self.writeq.dequeue()
        except Exception, e:
            print("SER--connection exception: %s" % str(e))
            self.reconnect()

    def disconnect(self):
        if self.ser is not None:
            self.ser.close()
            print("SER--Disconnected to Arduino!")

    def reconnect(self):
        self.disconnect()
        time.sleep(2)
        self.connect()

    def read(self):
        try:
            msg = self.ser.readline()
            if msg != "":
                print("SER--Read from Arduino: %s" % str(msg))
                if len(msg) > 5:
                    if msg[0] != 'T':
                        return msg
                else:
                    msg = msg[0]
                    if msg <= '8':
                        msg = arduino_to_algo(msg)
                        print("SER--After conversion: %s" % str(msg))
                        return msg
        except Exception, e:
            print("SER--read exception: %s" % str(e))
            self.reconnect()

    def write(self, msg):
        try:
            print("SER--Write to Arduino: %s" % str(msg))
            realmsg = algo_to_arduino(msg)
            print("SER--After conversion: %s" % str(realmsg))
            if realmsg:
                self.ser.write(realmsg)
                if realmsg == 'i' or realmsg == 'o':
                    time.sleep(self._calib_delay - self._write_delay)
                time.sleep(self._write_delay)
        except Exception, e:
            print("SER--write exception: %s" % str(e))
            self.writeq.enqueue(msg)
            self.reconnect()

    def write_from_q(self, msg):
        try:
            print("SER--Write to Arduino from Cache: %s" % str(msg))
            realmsg =algo_to_arduino(msg)
            print("SER--After conversion from Cache: %s" % str(msg))
            if realmsg:
                self.ser.write(realmsg)
                if realmsg == 'i' or realmsg == 'o':
                    time.sleep(self._calib_delay - self._write_delay)
                time.sleep(self._write_delay)
            return True
        except Exception, e:
            print("SER--write exception from Cache: %s" % str(e))
            self.reconnect()
            return False
