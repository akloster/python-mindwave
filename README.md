
python-mindwave
===============

This is a set of simple scripts that interface with the Neurosky Mindwave.

The Mindwave is a kind of Headset that can record EEG brain waves.

These scripts have been tested under Linux(Ubuntu) and OSX, so there might be
some adaptation to do for other platforms. The USB device is hardcoded but is
trivial to change in parser.py.


Dependencies
------------

Install following packages from your packing system:

* python-numpy
* python-game
* python-scipy
* pyserial

If you want to install dependencies using pip, you will also need to install
following dev dependencies:

* gfortran
* libopenblas-dev
* liblapack-dev


Usage
-----
You might not have the neccessary permissions to open the serial connection. If
that is the case, please drop me a note what you did to make it work. For
example it might be enough to add your user account to the group "dialout".

```
python sdl_viewer.py
```


Misc
----
But, for what might you use an EEG?

* Neurofeedback training
  * Better concentration
  * Help treat Depression and ADHD
  * Potentially other protocols
* Help with meditation and measure progress and endurance
* Use Brainwaves to control games


Please message me, if you have suggestions for improvements/bugs etc. or if you
are interested to develop more features/games for the Mindwave.

If you want to use the Mindwave with some kind of physical computing platform
(arduino, BeagleBoard, BeagleBone, Rasperry Pi), the manufacturer recommends
that you solder some wires into the headset for direct communication. That
means that you risk completely ruining the device and having to attach the
Arduino (or similar) to the headset itself. Instead it's probably cheaper and
easier to use the USB Host capabilities of an Arduino shield or the native USB
Ports of the other platform for the dongle, retaining full functionality and
"wirelessness".
