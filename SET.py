"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import instruments
import feedback
import pickle
import numpy as np
if __name__ == "__main__":
    # control loop setup
    powermeter = instruments.powermeter()
    if False:
        mirror = instruments.oko_mirror()
    else:
        mirror = instruments.tl_mirror()
    feedback = feedback.feedback_loop(powermeter, [mirror], False)
    chn = len(feedback.bindings)
    while True:
        fname = input("set value to all chn:")
        try:
            if (fname.replace('.', '', 1).isdigit()):
                feedback.execute(np.ones(chn) * min(float(fname), 1.0))
            else:
                with open(fname + ".pkl", 'rb') as output:
                    feedback.mirrors_now = pickle.load(output)
                feedback.write()
        except Exception as r:
            print(str(r))
        # print(feedback.mirrors_now)
        print("Power: {} uW".format(powermeter.read_power()/(1000.0*1000.0)))
