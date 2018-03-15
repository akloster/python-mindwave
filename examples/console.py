#!/usr/bin/python
# -*- coding: utf-8 -*-

from mindwave.parser import ThinkGearParser, TimeSeriesRecorder
import bluetooth
import time
import sys
import argparse


from mindwave.bluetooth_headset import connect_magic, connect_bluetooth_addr
from mindwave.bluetooth_headset import BluetoothError
from example_startup import mindwave_startup

description = """Simple Neurofeedback console application.

Make sure you paired the Mindwave to your computer. You need to
do that pairing for every operating system/user profile you run
seperately.

If you don't know the address, leave it out, and this program will
figure it out, but you need to put the MindWave Mobile headset into
pairing mode first.

"""
if __name__ == '__main__':
    extra_args=[dict(name='measure', type=str, nargs='?',
            const="attention", default="attention",
            help="""Measure you want feedback on. Either "meditation"
            or "attention\"""")]
    socket, args = mindwave_startup(description=description,
                              extra_args=extra_args)

    if args.measure not in ["attention", "meditation"]:
        print("Unknown measure %s" % repr(args.measure))
        sys.exit(-1)
    recorder = TimeSeriesRecorder()
    parser = ThinkGearParser(recorders=[recorder])

    if args.measure== 'attention':
        measure_name = 'Attention'
    else:
        measure_name = 'Meditation'

    while 1:
        time.sleep(0.25)
        data = socket.recv(20000)
        parser.feed(data)
        v = 0
        if args.measure == 'attention':
            if len(recorder.attention)>0:
                v = recorder.attention[-1]
        if args.measure == 'meditation':
            if len(recorder.meditation)>0:
                v = recorder.meditation[-1]
        if v>0:
            print("BALABLA:",v)
