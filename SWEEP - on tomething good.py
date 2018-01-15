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
while True:
        for ch in range(0,37):
                print(ch)
                for i in range(0,50):
                        x=[ 0.08243495,0.11290853,0.01320357,0.5610874, 0.37928419,0.36383452,0.12653611,0.36106641,0.31070294,0.65827922,0.55790878,0.75869671,0.41379684,0.54693251,0.313424,0.69806012,0.66996935,0.25862084,0.1678645, 0.52571725,0.70222249,0.72651944,0.51168345,0.63146174,0.83053895,0.98572477,0.77767956,0.44044176,0.65840676,0.75685873,0.69704646,0.36414569,0.45923254,0.27972951,0.51759203,0.36345417,0.63121994]
                        x[ch]=i/50.0
                        instruments.change_mirror(x,False)
                        time.sleep(0.007)
                for i in range(0,50):
                        x=[ 0.08243495,0.11290853,0.01320357,0.5610874, 0.37928419,0.36383452,0.12653611,0.36106641,0.31070294,0.65827922,0.55790878,0.75869671,0.41379684,0.54693251,0.313424,0.69806012,0.66996935,0.25862084,0.1678645, 0.52571725,0.70222249,0.72651944,0.51168345,0.63146174,0.83053895,0.98572477,0.77767956,0.44044176,0.65840676,0.75685873,0.69704646,0.36414569,0.45923254,0.27972951,0.51759203,0.36345417,0.63121994]
                        x[ch]=i/50.0
                        instruments.change_mirror(x,False)
                        time.sleep(0.007)
