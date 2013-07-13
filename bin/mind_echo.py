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

    hs.disconnect()

    while hs.get_state() != 'connected':
        print hs.get_state()
        time.sleep(1)
        if (hs.get_state() == 'standby'):
            print 'trying to connect...'
            hs.connect()

    while True:
        print 'connected, wait 1s to collect data'
        time.sleep(1)
        print hs.get('attention')
        print hs.get('meditation')
        #print hs.get('rawdata')
        print hs.get('alpha_waves')
        print hs.get('blink_strength')

    print 'disconnecting...'
    hs.disconnect()
    hs.destroy()
    sys.exit(0)
