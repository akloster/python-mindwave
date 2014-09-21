#!/usr/bin/python
# -*- coding: utf-8 -*-

from mindwave.parser import ThinkGearParser, TimeSeriesRecorder
import bluetooth
import time
import sys
import argparse
from progressbar import ProgressBar, Bar, Percentage


from mindwave.bluetooth_headset import connect_magic, connect_bluetooth_addr
from mindwave.bluetooth_headset import BluetoothError
from example_startup import mindwave_startup

description = """Simple commandline application to record EEG.

Make sure you paired the Mindwave to your computer. You need to
do that pairing for every operating system/user profile you run
seperately.

If you don't know the address, leave it out, and this program will
figure it out, but you need to put the MindWave Mobile headset into
pairing mode first, otherwise it can't be found.

"""
if __name__ == '__main__':
    extra_args = [dict(name='filename', type=str, nargs=1, help="File to write data to (HDF5 format)."), dict(name='frequency', type=int, nargs='?',
            const=10, default=10,
            help="""Frequency of recording, in iterations per second.
            This doesn't affect the sampling accuracy, but rather how
            often the parser is translating the data from the device
            into Timeseries data.
            """)]

    socket, args = mindwave_startup(description=description,
                              extra_args=extra_args)

    recorder = TimeSeriesRecorder(args.filename[0])
    parser = ThinkGearParser(recorders=[recorder])
    loop_time = 1.0 / float(args.frequency)
    last_message = time.time()
    start = last_message
    while 1:
        t = time.time()
        try:
            data = socket.recv(20000)
        except BluetoothError, e:
            print e
            time.sleep(0.5)
            continue
        parser.feed(data)
        elapsed = time.time()-t
        time.sleep(max(0.01, loop_time-elapsed))
        if (time.time()-last_message)>=5:
            print("%.2f" % (time.time()-start))
            last_message = time.time()


