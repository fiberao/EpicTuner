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
import pickle

def load_experiment_record(filename="train_dataset.pkl",sample_rate=1,trunc=None):
    # fetch file form disk
    power = []
    x = []
    experiment_record = open(filename, "rb")
    i = 0
    while True:
        try:
            ret = pickle.load(experiment_record)
            i +=1
            if trunc is not None:
                if i>trunc:
                    break
            if (i%sample_rate ==0 ):
                x.append(ret[0])
                power.append(ret[1])
        except EOFError:
            break
    experiment_record.close()
    return x,power
def please_just_give_me_a_simple_loop(host="localhost"):
    # control loop setup
    powermeter = instruments.powermeter(host)
    #okodm = instruments.oko_mirror(host)
    #tldm = instruments.tl_mirror(host)
    alpaodm = instruments.alpao_mirror(host)
    feedback = feedback_loop(powermeter, [alpaodm])#tldm, okodm
    feedback.relax_after_execute = False
    #feedback.bind([i for i in range(0,43)])
    #feedback.bind([i for i in range(43,80)])
    return feedback


class feedback_loop():
    def __init__(self, powermeter, mirrors=[], ask_reset=True, relax_after_execute=True, save_file="train_dataset.pkl"):
        self.calls = 0
        if save_file is not None:
            self.save_file = open(save_file, "a+b")
        else:
            self.save_file = None

        if powermeter is not None:
            self.powermeter = powermeter
            print("Current power:", powermeter.read_power())
        else:
            print("[WARNING] No feedback in the loop!")

        if mirrors is None:
            print("[WARNING] Running in simulation mode!")
            self.simulate = True
            self.vchn_num = 5
            self.vchn_max = np.ones(self.vchn_num)
            self.vchn_min = np.zeros(self.vchn_num)
            self.vchn_default = np.ones(self.vchn_num) * 0.5
        else:
            self.simulate = False
            self.mirrors = mirrors

            self.chn_mapto_mirror = []
            self.chn_mapto_acturators = []

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
        self.vchn_num = len(self.bindings)
        self.vchn_max = np.zeros(self.vchn_num)
        self.vchn_min = np.zeros(self.vchn_num)
        self.vchn_default = np.zeros(self.vchn_num)

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
        if self.simulate:
            return self.vchn_default.copy()
        else:
            mirrors_now = self.read()
            vchn_init = np.zeros(len(self.bindings))
            for j in range(0, len(self.bindings)):
                i = self.bindings[j]
                vchn_init[j] = mirrors_now[self.chn_mapto_mirror[i]
                                           ][self.chn_mapto_acturators[i]]
            return vchn_init

    def f_nm(self, x, repeat=1):
        if sum(np.array(x) > self.vchn_max) + sum(np.array(x) < self.vchn_min) > 0:
            print("out of range")
            return 0
        ret = self.f(x, repeat)
        if repeat > 1:
            ret[0] *= -1.0
        else:
            ret *= -1.0
        return ret

    def f(self, x, repeat=1,record=True):
        # make a safe copy
        x_copied = []
        for each in x:
            if isinstance(each, float):
                x_copied.append(each)
            else:
                print(x)
                raise ValueError(
                    "Non-float control value is not accepted in the control loop.")
        if self.simulate:
            power = (20.0 * 1000.0 * math.sin(x_copied[0] + 1) * math.cos(x_copied[1] - 0.3)
                     * (1. / (abs(x_copied[2] - 0.5) + 1))
                     * (1. / (abs(x_copied[3] - 0.1) + 1))
                     * (1. / (abs(x_copied[4] - 0.3) + 1)))
        else:
            self.execute(x_copied)
            power = self.powermeter.read_power(repeat)
        if record and (self.save_file is not None):
            pickle.dump((x_copied, power), self.save_file, -1)
        return power
