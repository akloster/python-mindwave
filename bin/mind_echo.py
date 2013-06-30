#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform

from pymindwave.parser import Parser
from pymindwave.pyeeg import bin_power


if __name__ == "__main__":
	if platform.system() == 'Darwin':
		p = Parser('/dev/tty.MindWave')
	else:
		p = Parser('/dev/ttyUSB0')
	while True:
		p.update()
		if p.sending_data:
			print 'Attention: {0}, Meditation: {1}'.format(
					p.current_attention, p.current_meditation)

