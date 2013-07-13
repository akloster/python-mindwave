import struct
from time import time
from time import sleep
from numpy import mean
import serial

"""
This is a Driver Class for the Neurosky Mindwave. The Mindwave consists of a
headset and an usb dongle.  The dongle communicates with the mindwave headset
wirelessly and can relay the data to a program that opens its usb serial port.

Some clarification on the Neurosky docs: The Neurosky Chip/Board is used in
several devices, for example the Neurosky Mindset, the Neurosky Mindwave,
Mattel MindFlex and several others. These chips all use the same protocol over
a serial connection, but depending on the device, some kind of middleware is
used. The Mindset uses bluetooth to communicate with the computer, the Mindwave
has its own proprietary dongle, and the MindFlex uses a dumbed down RF protocol
to communicate with the "main" board of the game.

However, all of these devices speak essentially the same protocol. I also had
the impression, before reading the docs, that only the Mindset provides raw
values, which is obviously not the case.

The Mindwave ships with a TCP/IP server to provide apps a relatively easy way
to access the data. Maybe I will write a substitute in Python in the future,
but for now I am satisfied with using Python only.
"""

class VirtualParser(object):
    def __init__(self, input_fstream):
        self.parser = self.run()
        self.parser.next()
        self.current_vector  =[]
        self.raw_values =  []
        self.current_meditation = 0
        self.current_attention= 0
        self.current_blink_strength = 0
        self.current_spectrum = []
        self.sending_data = False
        self.dongle_state ="initializing"
        self.raw_file = None
        self.esense_file = None
        self.input_fstream = input_fstream

    def update(self):
        input_stream = self.input_fstream.read(1000)
        #for b in input_stream:
            #print '{0:x}'.format(ord(b))
        for b in input_stream:
            self.parser.send(ord(b))	# Send each byte to the generator

    def write_serial(self, string):
        self.input_fstream.write(string)

    def start_raw_recording(self, file_name):
        self.raw_file = file(file_name, "wt")
        self.raw_start_time = time()

    def start_esense_recording(self, file_name):
        self.esense_file = file(file_name, "wt")
        self.esense_start_time = time()

    def stop_raw_recording(self):
        if self.raw_file:
            self.raw_file.close()
            self.raw_file = None

    def stop_esense_recording(self):
        if self.esense_file:
            self.esense_file.close()
            self.esense_file = None

    def run(self):
        """
            This generator parses one byte at a time.
        """
        last = time()
        i = 1
        self.buffer_len = 512*3
        times = []
        while 1:
            byte = yield
            if byte== 0xaa:
                byte = yield # This byte should be "\aa" too
                if byte== 0xaa:
                    # packet synced by 0xaa 0xaa
                    packet_length = yield
                    packet_code = yield
                    if packet_code == 0xd4:
                        # standing by
                        self.dongle_state= "standby"
                    elif packet_code == 0xd0:
                        self.dongle_state = "connected"
                    elif packet_code == 0xd2:
                        data_len = yield
                        headset_id = yield
                        headset_id += yield
                        self.dongle_state = "disconnected"
                    else:
                        self.sending_data = True
                        left = packet_length-2
                        while left>0:
                            if packet_code ==0x80: # raw value
                                row_length = yield
                                a = yield
                                b = yield
                                value = struct.unpack("<h",chr(a)+chr(b))[0]
                                self.raw_values.append(value)
                                if len(self.raw_values)>self.buffer_len:
                                    self.raw_values = self.raw_values[-self.buffer_len:]
                                left-=2

                                if self.raw_file:
                                    t = time()-self.raw_start_time
                                    self.raw_file.write("%.4f,%i\n" %(t, value))
                            elif packet_code == 0x02: # Poor signal
                                a = yield
                                self.poor_signal = a
                                if a>0:
                                    pass
                                left-=1
                            elif packet_code == 0x04: # Attention (eSense)
                                a = yield
                                if a>0:
                                    v = struct.unpack("b",chr(a))[0]
                                    if v>0:
                                        self.current_attention = v
                                        if self.esense_file:
                                            self.esense_file.write("%.2f,,%i\n" % (time()-self.esense_start_time, v))
                                left-=1
                            elif packet_code == 0x05: # Meditation (eSense)
                                a = yield
                                if a>0:
                                    v = struct.unpack("b",chr(a))[0]
                                    if v>0:
                                        self.current_meditation = v
                                        if self.esense_file:
                                            self.esense_file.write("%.2f,%i,\n" % (time()-self.esense_start_time, v))

                                left-=1
                            elif packet_code == 0x16: # Blink Strength
                                self.current_blink_strength = yield
                                left-=1
                            elif packet_code == 0x83:
                                vlength = yield
                                self.current_vector = []
                                for row in range(8):
                                    a = yield
                                    b = yield
                                    c = yield
                                    #value = a*255*255+b*255+c
                                    value = c*255*255+b*255+a
                                    self.current_vector.append(value)
                                left -= vlength
                            packet_code = yield
                else:
                    pass # sync failed
            else:
                pass # sync failed


class Parser(VirtualParser):
    def __init__(self, serial_dev='/dev/ttyUSB0'):
        self.dongle = serial.Serial(serial_dev,  115200, timeout=0.001)
        VirtualParser.__init__(self, self.dongle)



