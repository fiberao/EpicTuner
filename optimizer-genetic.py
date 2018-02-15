"""
The MIT License (MIT)

Copyright (c) 2017 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import copy
import instruments
import math
import numpy as np
import time

def genetic(f, x_start,
               ):
    pass

if __name__ == "__main__":
    if False:
        mirror=instruments.oko_mirror()
        chn=37
        init=np.zeros(chn)/2.0
    else:
        mirror=instruments.tl_mirror()
        chn=43
        init=np.ones(chn)/2.0
        print(mirror.read())
    mirror.change(init)
    #print("countdown 3 secs...")
    input("press any key to start optimzation")
    print("optimization start!")
    def f(x):
        for each in x:
            if (each >1) or (each <0):
                return 0
        mirror.change(x)
        acc=0.0
        for each in range(0,10):
            acc+=instruments.read_power()
        return acc/10.0
    final=nelder_mead(f, init)
    print (final[0])
    instruments.change(final[0])
    
    
