#!/usr/bin/env python
# -*- coding:utf-8 -*-

from distutils.core import setup

setup(name="pymindwave",
    verseion='0.9',
    description='python library to interface with Neurosky Mindwave haedset',
    author='Andreas Klostermann',
    url='https://github.com/akloster/python-mindwave',
    packages=['pymindwave'],
    scripts=['bin/feedback.py', 'bin/sdl_viewer.py'],
    )
