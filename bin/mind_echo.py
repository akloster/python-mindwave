#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import sys, time
from pymindwave import headset
from pymindwave.pyeeg import bin_power

def raw_to_spectrum(rawdata):
    flen = 50
    spectrum, relative_spectrum = bin_power(rawdata, range(flen), 512)
    #print spectrum
    #print relative_spectrum
    return spectrum


if __name__ == "__main__":
    if platform.system() == 'Darwin':
        hs = headset.Headset('/dev/tty.MindWave')
    else:
        hs = headset.Headset('/dev/ttyUSB0')

    # wait some time for parser to udpate state so we might be able
    # to reuse last opened connection.
    time.sleep(1)
    if hs.get_state() != 'connected':
        hs.disconnect()

    while hs.get_state() != 'connected':
        time.sleep(1)
        print 'current state: {0}'.format(hs.get_state())
        if (hs.get_state() == 'standby'):
            print 'trying to connect...'
            hs.connect()

    print 'now connected!'
    while True:
        print 'wait 1s to collect data...'
        time.sleep(1)
        print 'attention {0}, meditation {1}'.format(hs.get('attention'), hs.get('meditation'))
        print 'alpha_waves {0}'.format(hs.get('alpha_waves'))
        print 'blink_strength {0}'.format(hs.get('blink_strength'))
        print 'raw data:'
        print hs.get('rawdata')
        #print raw_to_spectrum(hs.get('rawdata'))

    print 'disconnecting...'
    hs.disconnect()
    hs.destroy()
    sys.exit(0)
