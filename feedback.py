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


def create_loop(host="Memory",prefix="tuningrec"):
    # control loop setup
    powermeter = instruments.powermeter(host)
    oko = instruments.Mirror(host, None, "oko")
    #alpao = instruments.Mirror(host, None, "alpao")
    thorlabs = instruments.Mirror(host, None, "thorlabs")
    router = instruments.Router([oko,thorlabs])
    feedback = instruments.Feedback(powermeter, router,prefix+"_raw.pkl")

    oko_znk = instruments.ZNKAdapter(oko)
    # alpao = instruments.ZNKAdapter(alpao)
    thorlabs_znk = instruments.ZNKAdapter(thorlabs)
    router_znk = instruments.Router([oko_znk,thorlabs_znk],False)
    feedback_znk = instruments.Feedback(powermeter, router_znk,prefix+"_znk.pkl")
    return feedback, feedback_znk


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

