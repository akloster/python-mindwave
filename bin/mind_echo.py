#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import sys, time
from pymindwave import headset


if __name__ == "__main__":
    if platform.system() == 'Darwin':
        hs = headset.Headset('/dev/tty.MindWave')
    else:
        hs = headset.Headset('/dev/ttyUSB0')

    while 1:
        print hs.get_state()
        time.sleep(1)
        if (hs.get_state() == 'standby'):
            print 'trying to connect...'
            hs.connect()
        if (hs.get_state() == 'connected'):
            print 'connected, wait 3s to collect data'
            time.sleep(3)
            print hs.get('attention')
            print hs.get('meditation')
            print hs.get('rawdata')
            print 'disconnecting...'
            hs.disconnect()
            hs.destroy()
            sys.exit(0)
