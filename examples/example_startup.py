import time
import sys
import argparse
import bluetooth

from mindwave.bluetooth_headset import connect_magic, connect_bluetooth_addr
from mindwave.bluetooth_headset import BluetoothError

def mindwave_startup(description="", extra_args=[]):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('address', type=str, nargs='?',
            const=None, default=None,
            help="""Bluetooth Address of device. Use this
            if you have multiple headsets nearby or you want
            to save a few seconds during startup.""")
    for params in extra_args:
        name = params['name']
        del params['name']
        parser.add_argument(name, **params)
    args = parser.parse_args(sys.argv[1:])
    if args.address is None:
        socket, socket_addr = connect_magic()
        if socket is None:
            print "No MindWave Mobile found."
            sys.exit(-1)
    else:
        socket = connect_bluetooth_addr(args.address)
        if socket is None:
            print "Connection failed."
            sys.exit(-1)
        socket_addr = args.address
    print "Connected with MindWave Mobile at %s" % socket_addr
    for i in range(5):
        try:
            if i>0:
                print "Retrying..."
            time.sleep(2)
            len(socket.recv(10))
            break
        except BluetoothError, e:
            print e
        if i == 5:
            print "Connection failed."
            sys.exit(-1)
    return socket, args
