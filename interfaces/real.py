
"""
set of real device communication interfaces
"""
import time

import serial
from bluetooth import *
from base import Interface
from common.pmessage import PMessage,ValidationException
from common.debug import debug,DEBUG_INTERFACE,DEBUG_VALIDATION
from interfaces.config import *

TO_SER = dict({PMessage.M_MOVE_FORWARD: "0", PMessage.M_TURN_RIGHT: "1", PMessage.M_TURN_LEFT: "2",
               PMessage.M_TURN_BACK: "3", PMessage.M_START_EXPLORE: "4", PMessage.M_START_FASTRUN: "5",
               PMessage.M_CALLIBRATE_FRONT: "i", PMessage.M_CALLIBRATE_RIGHT:"o",PMessage.M_END_EXPLORE:"8"})

FROM_SER = {value:key for key,value in TO_SER.items()}
current_milli_time = lambda: int(round(time.time() * 1000))


class ArduinoInterface(Interface):
    name = ARDUINO_LABEL
    _write_delay = 0.5
    _calib_delay = 1

    def __init__(self):
        super(ArduinoInterface,self).__init__()
        self.status = False
        self.ser = None
        self.port_no = 1

    def connect(self):
        if self.ser is not None:
            self.ser.close()
            time.sleep(2)
        try:
            self.port_no = self.port_no ^ 1
            self.ser = serial.Serial(SER_PORT+str(self.port_no), SER_BAUD)
            time.sleep(2)
            if self.ser is not None:
                self.set_ready()
                self.status = True
                debug("SER--Connected to Arduino!",DEBUG_INTERFACE)
        except Exception, e:
            debug("SER--connection exception: %s" % str(e),DEBUG_INTERFACE)
            self.reconnect()

    def disconnect(self):
        if self.ser is not None:
            self.ser.close()
            self.set_not_ready()
            debug("SER--Disconnected to Arduino!",DEBUG_INTERFACE)

    def reconnect(self):
        self.disconnect()
        time.sleep(3)
        self.connect()

    def read(self):
        try:
            msg = self.ser.readline().rstrip()
            if msg != "":
                debug(str(current_milli_time()) + "SER--Read from Arduino: %s" % str(msg), DEBUG_INTERFACE)
                if msg[0] != 'T' and len(msg.split(',')) == 6:
                    realmsg = PMessage(type=PMessage.T_MAP_UPDATE, msg=msg)
                    debug(str(current_milli_time()) + "SER--Read from Arduino after1: %s" % str(realmsg), DEBUG_INTERFACE)
                    return realmsg
                elif msg[0] != 'T' and msg in FROM_SER:
                    if msg[0] <= '8':
                        realmsg = PMessage(type=PMessage.T_ROBOT_MOVE, msg=FROM_SER.get(msg[0]))
                        debug(str(current_milli_time()) + "SER--Read from Arduino after2: %s" % str(realmsg), DEBUG_INTERFACE)
                        return realmsg
                elif msg[0] != 'T' and len(msg) > 1:
                    tmp = ord(msg[1]) - 96
                    if tmp > 1:
                        msg = FROM_SER.get(msg[0]) + "*" + str(tmp)
                    else:
                        msg = FROM_SER.get(msg[0])
                    realmsg = PMessage(type=PMessage.T_ROBOT_MOVE, msg=msg)
                    debug(str(current_milli_time()) + "SER--Read from Arduino after3: %s" % str(realmsg), DEBUG_INTERFACE)
                    return realmsg

        except ValidationException as e:
            debug(str(current_milli_time()) + "validation exception: {}".format(e.message),DEBUG_VALIDATION)
        except Exception, e:
            debug(str(current_milli_time()) + "SER--read exception: %s" % str(e),DEBUG_INTERFACE)
            self.reconnect()

    def write(self, msg):
        try:
            msg = msg.get_msg()
            debug(str(current_milli_time()) + "SER--Write to Arduino b4: %s" % str(msg), DEBUG_INTERFACE)       
            realmsg = ""
            if msg in TO_SER:
                realmsg = TO_SER.get(msg)
                if realmsg == "0":
                    realmsg = "0a"
            elif len(msg.split('*')) == 2:
                msg = msg.split('*')
                tmp = int(msg[1]) + 96
                realmsg = TO_SER.get(msg[0]) + chr(tmp)

            if realmsg:
                debug(str(current_milli_time()) + "SER--Write to Arduino: %s" % str(realmsg),DEBUG_INTERFACE)
                self.ser.write(realmsg)
                if realmsg == 'i' or realmsg == 'o':
                    time.sleep(self._calib_delay - self._write_delay)
                time.sleep(self._write_delay)
        except Exception, e:
            debug(str(current_milli_time()) + "SER--write exception: %s" % str(e),DEBUG_INTERFACE)
            self.reconnect()


class AndroidInterface(Interface):

    name = ANDROID_LABEL
    _write_delay = 0.1

    def __init__(self):
        super(AndroidInterface,self).__init__()
        self.status = False

    def connect(self):
        connected = False
        while(not connected):
            try:
                self.server_sock = BluetoothSocket(RFCOMM)
                self.server_sock.bind(("", BT_PORT))
                self.server_sock.listen(2)
                port = self.server_sock.getsockname()[1]
                advertise_service(self.server_sock, "SampleServer",
                                  service_id=BT_UUID,
                                  service_classes=[BT_UUID, SERIAL_PORT_CLASS],
                                  profiles=[SERIAL_PORT_PROFILE],
                )
                self.client_sock, client_info = self.server_sock.accept()
                debug("BT--Connected to %s on channel %s" % (str(client_info), str(port)),DEBUG_INTERFACE)
                self.set_ready()
                return True
            except Exception, e:
                debug("BT--connection exception: %s" % str(e),DEBUG_INTERFACE)

    def disconnect(self):
        try:
            self.client_sock.close()
            self.server_sock.close()
            self.set_not_ready()
            debug("BT--Disconnected to Android!",DEBUG_INTERFACE)
        except Exception, e:
            debug("BT--disconnection exception: %s" % str(e),DEBUG_INTERFACE)

    def read(self):
        if (not self._msg_buffer.is_empty()):
            return self._msg_buffer.dequeue()
        try:
            msg = self.client_sock.recv(2048)
            debug("BT--Read from Android: %s" % str(msg),DEBUG_INTERFACE)
            pmsgs = PMessage.load_messages_from_json(json_str=msg)
            if (pmsgs):
                for msg in pmsgs:
                    self._msg_buffer.enqueue(msg)
                return self._msg_buffer.dequeue()
        except ValidationException as e:
            debug("Validation exception: {}".format(e.message),DEBUG_VALIDATION)
        except Exception, e:
            debug("BT--read exception: %s" % str(e),DEBUG_INTERFACE)

    def write(self, msg):
        try:
            msg = msg.render_msg()
            self.client_sock.send(msg)
            time.sleep(self._write_delay)
            debug("BT--Write to Android: %s" % str(msg),DEBUG_INTERFACE)
        except Exception, e:
            debug("BT--write exception: %s" % str(e),DEBUG_INTERFACE)
