"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import math
import numpy as np


class feedback_loop():
    def __init__(self, powermeter, mirrors=[], ask_reset=True):
        if powermeter is not None:
            self.powermeter = powermeter
            print("Current power:", powermeter.read_power())
        else:
            print("[WARNING] No feedback in the loop!")
        self.mirrors = mirrors
        self.chn_mapto_mirror = []
        self.chn_mapto_acturators = []
        mirror_count = 0
        for mirror in self.mirrors:
            for i in range(mirror.chn):
                self.chn_mapto_mirror.append(mirror_count)
                self.chn_mapto_acturators.append(i)
            mirror_count += 1
        self.bind(clear=ask_reset)
        print("Control loop standby.")
        self.calls = 0

    def read(self):
        self.mirrors_now = []
        for mirror in self.mirrors:
            self.mirrors_now.append(mirror.read())

    def bind(self, bindings=None, clear=True):
        if bindings is None:
            self.bindings = [i for i in range(0, len(self.chn_mapto_mirror))]
        else:
            self.bindings = bindings
        self.vchn_max = np.zeros(len(self.bindings))
        self.vchn_min = np.zeros(len(self.bindings))
        self.vchn_init = np.zeros(len(self.bindings))
        self.vchn_default = np.zeros(len(self.bindings))
        self.read()
        for j in range(0, len(self.bindings)):
            i = self.bindings[j]
            self.vchn_init[j] = self.mirrors_now[self.chn_mapto_mirror[i]
                                                 ][self.chn_mapto_acturators[i]]
            self.vchn_max[j] = self.mirrors[self.chn_mapto_mirror[i]
                                            ].max[self.chn_mapto_acturators[i]]
            self.vchn_min[j] = self.mirrors[self.chn_mapto_mirror[i]
                                            ].min[self.chn_mapto_acturators[i]]
            self.vchn_default[j] = self.mirrors[self.chn_mapto_mirror[i]
                                                ].default[self.chn_mapto_acturators[i]]

        print("======== Control loop status ======")
        self.print()
        print("========     END status      ======")
        if clear:
            if (len(input("Do you want to reset? (yes/no)")) > 1):
                self.execute(self.vchn_default)
                print("======== RESET ======")
                self.print()
                print("======== RESET ======")

    def print(self):
        self.read()
        for j in range(0, len(self.bindings)):
            i = self.bindings[j]
            print("VCHN ", j, " binds to CHN ", i,
                  " maps to ACT ", self.chn_mapto_acturators[i],
                  " on MIRROR ", self.chn_mapto_mirror[i],
                  " max: ", self.vchn_max[j],
                  " min: ", self.vchn_min[j],
                  " typ: ", self.vchn_default[j],
                  " now: ", self.mirrors_now[self.chn_mapto_mirror[i]][self.chn_mapto_acturators[i]])

    def execute(self, x):
        # update chn_now
        for j in range(len(self.bindings)):
            i = self.bindings[j]
            self.mirrors_now[self.chn_mapto_mirror[i]
                             ][self.chn_mapto_acturators[i]] = x[j]
        self.write()

    def write(self):
        # send chn_now
        for i in range(len(self.mirrors)):
            self.mirrors[i].change(self.mirrors_now[i])

    def f_nm(self, x):
        if sum(np.array(x) > self.vchn_max) + sum(np.array(x) < self.vchn_min) > 0:
            return 0
        return -self.f(x)

    def f(self, x):
        if sum(np.array(x) > self.vchn_max) + sum(np.array(x) < self.vchn_min) > 0:
            print("control value exceeded.")
            return 0
        self.execute(x)
        self.calls += 1
        if (self.calls % 100 == 1):
            print("runs:{}".format(self.calls))
        acc = 0.0
        integration = 2
        for each in range(0, integration):
            acc += self.powermeter.read_power()
        power = acc / float(integration)
        return power / (1000.0 * 1000.0)

    def fake(self, x):
        self.calls += 1
        return math.sin(x[0]) * math.cos(x[1]) * (1. / (abs(x[2]) + 1))
