"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import instruments
import math
import numpy as np
powermeter = instruments.powermeter("labtop1")
print(powermeter.read_power())
if False:
    mirror = instruments.oko_mirror()
    chn = 37
    default = np.zeros(chn)
else:
    mirror = instruments.tl_mirror("labtop1")
    chn = 43
    default = np.ones(chn) * 0.42
print(mirror.read())
if (len(input("Previous values are those above. Do you want to reset (yes for reset)?")) > 1):
    mirror.change(default)
init = np.array(mirror.read())
print(init)
print("Control loop standby.")
calls = 0


def tl_tiptilt(x):
    pass


def f_nm(x):
    if sum(x > 1) + sum(x < 0) > 0:
        return 0
    return -f(x)


def f(x):
    global calls
    if sum(x > 1) + sum(x < 0) > 0:
        print("control value exceeded.")
        return 0
    mirror.change(x, True)
    calls += 1
    if (calls % 100 == 1):
        print("runs:{}".format(calls))
    acc = 0.0
    integration = 2
    for each in range(0, integration):
        acc += powermeter.read_power()
    power = acc / float(integration)
    return power / (1000.0 * 1000.0)


def fake(x):
    global calls
    calls += 1
    return math.sin(x[0]) * math.cos(x[1]) * (1. / (abs(x[2]) + 1))
