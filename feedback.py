"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import math
import numpy as np
import instruments


def please_just_give_me_a_simple_loop():
    # control loop setup
    powermeter = instruments.powermeter("Memory")
    okodm = instruments.oko_mirror("Memory")
    tldm = instruments.tl_mirror("Memory")

    feedback = feedback_loop(powermeter, [tldm, okodm])
    feedback.relax_after_execute=False
    #feedback.bind([i for i in range(0,43)])
    #feedback.bind([i for i in range(43,80)])
    return feedback


class feedback_loop():
    def __init__(self, powermeter, mirrors=[], ask_reset=True, relax_after_execute=True):
        if powermeter is not None:
            self.powermeter = powermeter
            print("Current power:", powermeter.read_power())
        else:
            print("[WARNING] No feedback in the loop!")
        self.mirrors = mirrors
        self.chn_mapto_mirror = []
        self.chn_mapto_acturators = []
        self.calls = 0
        self.relax_after_execute = relax_after_execute
        mirror_count = 0
        for mirror in self.mirrors:
            for i in range(mirror.chn):
                self.chn_mapto_mirror.append(mirror_count)
                self.chn_mapto_acturators.append(i)
            mirror_count += 1
        self.bind(clear=ask_reset)
        print("Control loop standby.")
        

    def read(self):
        mirrors_now = []
        for mirror in self.mirrors:
            mirrors_now.append(mirror.now.copy())
        return mirrors_now

    def write(self, mirrors_now):
        # send chn_now
        for i in range(len(self.mirrors)):
            self.mirrors[i].change(
                mirrors_now[i], relax=self.relax_after_execute)

    def bind(self, bindings=None, clear=True):
        if bindings is None:
            self.bindings = [i for i in range(0, len(self.chn_mapto_mirror))]
        else:
            self.bindings = bindings
        self.vchn_max = np.zeros(len(self.bindings))
        self.vchn_min = np.zeros(len(self.bindings))
        self.vchn_default = np.zeros(len(self.bindings))
        self.vchn_num = len(self.bindings)
        for j in range(0, self.vchn_num):
            i = self.bindings[j]

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
            if (input("Do you want to reset? (yes/no)") == "yes"):
                self.execute(self.vchn_default)
                print("======== RESET ======")
                self.print()
                print("======== RESET ======")

    def print(self):
        mirrors_now = self.read()
        for j in range(0, self.vchn_num):
            i = self.bindings[j]
            print("VCHN ", j, " binds to CHN ", i,
                  " maps to ACT ", self.chn_mapto_acturators[i],
                  " on MIRROR ", self.chn_mapto_mirror[i],
                  " max: ", self.vchn_max[j],
                  " min: ", self.vchn_min[j],
                  " typ: ", self.vchn_default[j],
                  " now: ", mirrors_now[self.chn_mapto_mirror[i]][self.chn_mapto_acturators[i]])
        return mirrors_now

    def execute(self, x):
        mirrors_now = self.read()
        # update chn_now
        if sum(np.array(x) > self.vchn_max) + sum(np.array(x) < self.vchn_min) > 0:
            print("control value exceeded.")
            return 0
        for j in range(len(self.bindings)):
            i = self.bindings[j]
            mirrors_now[self.chn_mapto_mirror[i]
                        ][self.chn_mapto_acturators[i]] = x[j]
        self.write(mirrors_now)
        # accumulate call counting
        self.calls += 1
        if (self.calls % 100 == 1):
            print("runs: {}".format(self.calls))

    def get_executed(self):
        mirrors_now = self.read()
        vchn_init = np.zeros(len(self.bindings))
        for j in range(0, len(self.bindings)):
            i = self.bindings[j]
            vchn_init[j] = mirrors_now[self.chn_mapto_mirror[i]
                                       ][self.chn_mapto_acturators[i]]
        return vchn_init

    def f_nm(self, x):
        if sum(np.array(x) > self.vchn_max) + sum(np.array(x) < self.vchn_min) > 0:
            return 0
        return -self.f(x)

    def f(self, x):
        self.execute(x)
        power = self.powermeter.read_power()
        return power

    def fake(self, x):
        self.calls += 1
        return math.sin(x[0]) * math.cos(x[1]) * (1. / (abs(x[2]) + 1))
