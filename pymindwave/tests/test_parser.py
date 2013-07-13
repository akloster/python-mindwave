#!/usr/bin/env python
# -*- coding:utf-8 -*-

import StringIO
from pymindwave import parser

standby_test_stream = StringIO.StringIO(
    '\xaa\xaa' + # [SYNC] sync packets
    '\x03' + # [PLENGTH] payload length
    '\xd4\x01\x00' + # in standby mode
    '\x2a' # [CHKSUM]
)

sync_test_stream1 = StringIO.StringIO(
    '\x00\x12\x71\xaa' +
    '\xaa\xaa' + # [SYNC] sync packets
    '\x03' + # [PLENGTH] payload length
    '\xd4\x01\x00' + # in standby mode
    '\x2a' # [CHKSUM]
)

sync_test_stream2 = StringIO.StringIO(
    '\x00\x12\x71' +
    '\xaa\xaa' + # [SYNC] sync packets
    '\x03' + # [PLENGTH] payload length
    '\xd4\x01\x00' + # in standby mode
    '\x2a' # [CHKSUM]
)

disconnected_test_stream = StringIO.StringIO(
    '\xaa\xaa' + # [SYNC] sync packets
    '\x04' + # [PLENGTH] payload length
    '\xd2' + # headset disconnected
    '\x02' + # data len
    '\xa1\x6c' + # headset global ID: 0xa16c
    '\x1e' # [CHKSUM]
)

raw_data_test_stream = StringIO.StringIO(
    '\x65\x02\x00\x64\x61' +
    '\xaa\xaa' +
    '\x04' +
    '\x80' +
    '\x02' +
    '\x00\x28' +
    '\x55'
)

official_test_stream = StringIO.StringIO(
    '\xaa\xaa' + # [SYNC] sync packets
    '\x20' + # [PLENGTH] payload length
    '\x02' + # [POOR_SIGNAL] quality
    '\x00' + # No poor signal detected (0/200)
    '\x83' + # [ASIC_EEG_POWER_INT]
    '\x18' + # [VLENGTH] 24 bytes
    '\x00' + # (1/3) Begin Delta bytes
    '\x00' + # (2/3)
    '\x94' + # (3/3) End Delta bytes
    '\x00' + # (1/3) Begin Theta bytes
    '\x00' + # (2/3)
    '\x42' + # (3/3) End Theta bytes
    '\x00' + # (1/3) Begin Low-alpha bytes
    '\x00' + # (2/3)
    '\x0b' + # (3/3) End Low-alpha bytes
    '\x00' + # (1/3) Begin High-alpha bytes
    '\x00' + # (2/3)
    '\x64' + # (3/3) End High-alpha bytes
    '\x00' + # (1/3) Begin Low-beta bytes
    '\x00' + # (2/3)
    '\x4d' + # (3/3) End Low-beta bytes
    '\x00' + # (1/3) Begin High-beta bytes
    '\x00' + # (2/3)
    '\x3d' + # (3/3) End High-beta bytes
    '\x00' + # (1/3) Begin Low-gamma bytes
    '\x00' + # (2/3)
    '\x07' + # (3/3) End Low-gamma bytes
    '\x00' + # (1/3) Begin Mid-gamma bytes
    '\x00' + # (2/3)
    '\x05' + # (3/3) End Mid-gamma bytes
    '\x04' + # [ATTENTION] eSense
    '\x0d' + # eSense Attention level of 13
    '\x05' + # [MEDITATION] eSense
    '\x3d' + # eSense Meditation level of 61
    '\x34' # [CHKSUM] (1's comp inverse of 8-bit Payload sum of 0xCB)
)


def test_standby_mode():
    p = parser.VirtualParser(standby_test_stream)
    p.update()
    assert (p.dongle_state == 'standby')

def test_sync():
    p = parser.VirtualParser(sync_test_stream1)
    p.update()
    assert (p.dongle_state == 'standby')
    p = parser.VirtualParser(sync_test_stream2)
    p.update()
    assert (p.dongle_state == 'standby')

def test_official_test_stream():
    p = parser.VirtualParser(official_test_stream)
    p.update()
    assert (p.sending_data)
    assert (p.current_attention == 13)
    assert (p.current_meditation == 61)
    assert (p.current_vector == [148, 66, 11, 100, 77, 61, 7, 5])

def test_disconnected_mode():
    p = parser.VirtualParser(disconnected_test_stream)
    p.update()
    assert (p.dongle_state == 'disconnected')

def test_rawdata_test():
    p = parser.VirtualParser(raw_data_test_stream)
    p.update()
    print p.raw_values
    assert (p.raw_values == [0x28])
