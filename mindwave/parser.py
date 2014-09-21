import bluetooth
import struct
import time
import pandas as pd
from datetime import datetime


"""

    This interface library is designed to be used from very different contexts.
    The general idea is that the Mindwave modules in the headset (and other devices)
    talk a common binary protocol, which is entirely one-sided from headset to device/
    computer, with one exception (explained later). The means of transport however
    does vary. The original MindWave headset had 2.4Ghz wireless connection, using a
    proprietary USB dongle/receiver. This receiver is mounted as a serial console in
    Linux. It also requires extra commands to connect and disconnect.
    
    The MindWave mobile uses bluetooth, which I would recommend over the 2.4Ghz version.
    
    There have been hacks with arduinos hooked up to the Thinkgear AM modules directly.
    
    Not only are the technical means of data transport different, your application needs
    one of several possible means of regularly reading the data.
    
    In the EuroPython 2014 talk "Brainwaves for Hackers" I demonstrated a way to do this
    in the IPython Notebook, and that only involved a blocking read from a bluetooth socket at
    certain intervals. Pygame works the same way.
    
    There are more sophisticated event loops out there, like in Kivy, Gevent or Tornado.
    
    That are the reasons why there is a parser module that can be fed a stream of bytes.
    You can add recorders to the parser, which take care of analyzing the parsed data.
    
    There is for example one recorder which converts the parsed data into Pandas
    Timeseries. But doing that dozens of times per second is too much work for weak
    processors, like in the Raspberry Pi, so there you would probably derive your own
    parser.
"""
def queue_to_series(a, freq="s"):
    t = pd.date_range(end=datetime.now(), freq=freq, periods=len(a))
    return pd.TimeSeries(a, index=t)

class ThinkGearParser(object):
    def __init__(self, recorders=None):
        self.recorders = []
        if recorders is not None:
            self.recorders += recorders
        self.input_data = ""
        self.parser = self.parse()
        self.parser.next()

    def feed(self, data):
        for c in data:
            self.parser.send(ord(c))
        for recorder in self.recorders:
            recorder.finish_chunk()
        self.input_data += data
    def dispatch_data(self, key, value):
        for recorder in self.recorders:
            recorder.dispatch_data(key, value)

    def parse(self):
        """
            This generator parses one byte at a time.
        """
        i = 1
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
                        self.state = "standby"
                    elif packet_code == 0xd0:
                        self.state = "connected"
                    elif packet_code == 0xd2:
                        data_len = yield
                        headset_id = yield
                        headset_id += yield
                        self.dongle_state = "disconnected"
                    else:
                        self.sending_data = True
                        left = packet_length - 2
                        while left>0:
                            if packet_code ==0x80: # raw value
                                row_length = yield
                                a = yield
                                b = yield
                                value = struct.unpack("<h",chr(b)+chr(a))[0]
                                self.dispatch_data("raw", value)
                                left -= 2
                            elif packet_code == 0x02: # Poor signal
                                a = yield

                                left -= 1
                            elif packet_code == 0x04: # Attention (eSense)
                                a = yield
                                if a>0:
                                    v = struct.unpack("b",chr(a))[0]
                                    if 0 < v <= 100:
                                        self.dispatch_data("attention", v)
                                left-=1
                            elif packet_code == 0x05: # Meditation (eSense)
                                a = yield
                                if a>0:
                                    v = struct.unpack("b",chr(a))[0]
                                    if 0 < v <= 100:
                                        self.dispatch_data("meditation", v)
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
                                    value = a*255*255+b*255+c
                                left -= vlength
                                self.dispatch_data("bands", self.current_vector)
                            packet_code = yield
                else:
                    pass # sync failed
            else:
                pass # sync failed

class TimeSeriesRecorder:
    def __init__(self, file_name=None):
        self.meditation = pd.TimeSeries()
        self.attention = pd.TimeSeries()
        self.raw = pd.TimeSeries()
        self.blink = pd.TimeSeries()
        self.poor_signal = pd.TimeSeries()
        self.attention_queue = []
        self.meditation_queue = []
        self.poor_signal_queue = []
        self.blink_queue = []
        self.raw_queue = []
        if file_name is not None:
            self.store = pd.HDFStore(file_name)
        else:
            self.store = None
 
    def dispatch_data(self, key, value):
        if key == "attention":
            self.attention_queue.append(value)
            # Blink and "poor signal" is only sent when a blink or poor signal is detected
            # So fake continuous signal as zeros.
            
            self.blink_queue.append(0)
            self.poor_signal_queue.append(0)
            
        elif key == "meditation":
            self.meditation_queue.append(value)
        elif key == "raw":
            self.raw_queue.append(value)
        elif key == "blink":
            self.blink_queue.append(value)
            if len(self.blink_queue)>0:
                self.blink_queue[-1] = self.current_blink_strength
 
        elif key == "poor_signal":
            if len(self.poor_signal_queue)>0:
                self.poor_signal_queue[-1] = a

        
    def record_meditation(self, attention):
        self.meditation_queue.append()
        
    def record_blink(self, attention):
        self.blink_queue.append()
    
    def finish_chunk(self):
        """ called periodically to update the timeseries """
        self.meditation = pd.concat([self.meditation, queue_to_series(self.meditation_queue, freq="s")])
        
        self.attention = pd.concat([self.attention, queue_to_series(self.attention_queue, freq="s")])
        self.blink = pd.concat([self.blink, queue_to_series(self.blink_queue, freq="s")])
        self.raw = pd.concat([self.raw, queue_to_series(self.raw_queue, freq="1953U")])
        self.poor_signal = pd.concat([self.poor_signal, queue_to_series(self.poor_signal_queue)])

        self.attention_queue = []
        self.meditation_queue = []
        self.poor_signal_queue = []
        self.blink_queue = []
        self.raw_queue = []
        if self.store is not None:
            self.store['attention'] = self.attention
            self.store['meditation'] = self.meditation
            self.store['raw'] = self.raw

