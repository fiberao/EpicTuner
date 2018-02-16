"""
The MIT License (MIT)

Copyright (c) 2017 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import instruments
import time
import numpy as np

if False:
        mirror=instruments.oko_mirror()
        chn=37
else:
        mirror=instruments.tl_mirror()
        chn=43
        print(mirror.read())
init=np.ones(chn)/2.0
step=50
chn_max=1.0
chn_min=0.0
while True:
        for ch in range(30,chn):
                print(ch)
                #middle to max
                x=init.copy()
                for i in range(0,step):
                        x[ch]=init[ch]+(chn_max-init[ch])*(i/(1.0*step))
                        print(x)
                        mirror.change(x)
                        time.sleep(0.005)
                for i in range(0,step):
                        x[ch]=chn_max+(chn_min-chn_max)*(i/(1.0*step))
                        print(x)
                        mirror.change(x)
                        time.sleep(0.005)
                for i in range(0,step):
                        x[ch]=chn_min+(init[ch]-chn_min)*(i/(1.0*step))
                        print(x)
                        mirror.change(x)
                        time.sleep(0.005)