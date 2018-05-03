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


def please_just_give_me_a_simple_loop(host="Memory", znk=True):
    # control loop setup
    powermeter = instruments.powermeter(host)
    if not znk:
        oko = instruments.Mirror(host, None, "oko")
        alpao = instruments.Mirror(host, None, "alpao")
        router = instruments.Router([oko, alpao])
    else:
        # oko_znk = instruments.ZNKMirror(host, None, "oko")
        # alpao_znk = instruments.ZNKMirror(host, None, "alpao")
        tl_znk = instruments.ZNKThrolabs(host,None,"thorlabs")
        router = instruments.Router([tl_znk])
    feedback = feedback_raw(powermeter, router)

    return feedback


def load_experiment_record(filename="train_dataset.pkl", sample_rate=1, trunc=None):
    # fetch file form disk
    power = []
    x = []
    experiment_record = open(filename, "rb")
    i = 0
    while True:
        try:
            ret = pickle.load(experiment_record)
            i += 1
            if trunc is not None:
                if i > trunc:
                    break
            if (i % sample_rate == 0):
                x.append(ret[0])
                power.append(ret[1])
        except EOFError:
            break
    experiment_record.close()
    return x, power


class feedback_raw():
    def __init__(self, sensor, acturator, save_file="train_dataset.pkl"):
        self.calls = 0
        self.acturator = acturator
        self.sensor = sensor
        print("Current power:", sensor.read())

        if save_file is not None:
            self.save_file = open(save_file, "a+b")
        else:
            self.save_file = None

        print("Control loop standby.")

    def write(self, list):
        self.acturator.write(list)

    def read(self):
        return self.sensor.read()

    def f(self, x, record=True):
        # make a safe copy
        x_copied = []
        for each in x:
            if isinstance(each, float):
                x_copied.append(each)
            else:
                print(x)
                raise ValueError(
                    "Non-float control value is not accepted in the control loop.")

        self.acturator.write(x_copied)
        power = self.sensor.read()
        self.calls += 1
        if (self.calls % 100 == 1):
            print("runs: {}".format(self.calls))
        if record and (self.save_file is not None):
            pickle.dump((x_copied, power), self.save_file, -1)
        return power
