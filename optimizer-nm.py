"""
The MIT License (MIT)

Copyright (c) 2017 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket
import copy
import threading
powermeter_val = "no signal"
#init_mirror
mirror_IP = "memory"
mirror_PORT = 8888
print ("mirror IP:"+str(mirror_IP))
print ("mirror port:"+str(mirror_PORT))
mirror = socket.socket(socket.AF_INET, # Internet
	                     socket.SOCK_DGRAM) # UDP
#init powermeter
def rec_UDP():
	print ("powermeter port:"+str(7777))
	powermeter = socket.socket(socket.AF_INET, # Internet
	                     socket.SOCK_DGRAM) # UDP
	powermeter.bind(("0.0.0.0",7777))
	global powermeter_val
	while True:
		data, addr = powermeter.recvfrom(512) # buffer size is 1024 bytes
		powermeter_val=-int(data.decode("ascii"))		
listen_UDP = threading.Thread(target=rec_UDP)
listen_UDP.start()
input()
def change_mirror(int_list=[0.0]):
	# change mirror
	mirror.sendto((" ".join([str(int(x*4096)) for x in int_list])).encode("ascii"), (mirror_IP, mirror_PORT))
	data, addr = mirror.recvfrom(512) # buffer size is 1024 bytes
	#print ("mirro config:", data.decode("ascii"))
def close_mirror():
	mirror.sendto("9999 ".encode("ascii"), (mirror_IP, mirror_PORT))

def nelder_mead(f, x_start,
                step=0.3, no_improve_thr=10,
                no_improv_break=1000, max_iter=0,
                alpha=1., gamma=2., rho=-0.5, sigma=0.5):
    '''
        @param f (function): function to optimize, must return a scalar score
            and operate over a numpy array of the same dimensions as x_start
        @param x_start (numpy array): initial position
        @param step (float): look-around radius in initial step
        @no_improv_thr,  no_improv_break (float, int): break after no_improv_break iterations with
            an improvement lower than no_improv_thr
        @max_iter (int): always break after this number of iterations.
            Set it to 0 to loop indefinitely.
        @alpha, gamma, rho, sigma (floats): parameters of the algorithm
            (see Wikipedia page for reference)

        return: tuple (best parameter array, best score)
    '''

    # init
    print(x_start)
    dim = len(x_start)
    prev_best = f(x_start)
    no_improv = 0
    res = [[x_start, prev_best]]

    for i in range(dim):
        x = copy.copy(x_start)
        x[i] = x[i] + step
        score = f(x)
        res.append([x, score])

    # simplex iter
    iters = 0
    while 1:
        # order
        res.sort(key=lambda x: x[1])
        #print([each[1] for each in res])
        best = res[0][1]

        # break after max_iter
        if max_iter and iters >= max_iter:
            return res[0]
        iters += 1

        # break after no_improv_break iterations with no improvement
        print ('...best so far:', best)

        if best < prev_best - no_improve_thr:
            no_improv = 0
            prev_best = best
        else:
            no_improv += 1

        if no_improv >= no_improv_break:
            return res[0]

        # centroid
        x0 = [0.] * dim
        for tup in res[:-1]:
            for i, c in enumerate(tup[0]):
                x0[i] += c / (len(res)-1)

        # reflection
        xr = x0 + alpha*(x0 - res[-1][0])
        rscore = f(xr)
        if res[0][1] <= rscore < res[-2][1]:
            del res[-1]
            res.append([xr, rscore])
            continue

        # expansion
        if rscore < res[0][1]:
            xe = x0 + gamma*(x0 - res[-1][0])
            escore = f(xe)
            if escore < rscore:
                del res[-1]
                res.append([xe, escore])
                continue
            else:
                del res[-1]
                res.append([xr, rscore])
                continue

        # contraction
        xc = x0 + rho*(x0 - res[-1][0])
        cscore = f(xc)
        if cscore < res[-1][1]:
            del res[-1]
            res.append([xc, cscore])
            continue

        # reduction
        x1 = res[0][0]
        nres = []
        for tup in res:
            redx = x1 + sigma*(tup[0] - x1)
            score = f(redx)
            nres.append([redx, score])
        res = nres


if __name__ == "__main__":
    import math
    import numpy as np
    import time
    def f(x):
    	for each in x:
    		if (each >1) or (each <0):
    			return 0
    	change_mirror(x)
    	time.sleep(0.2)
    	print (powermeter_val)
    	return powermeter_val
    final=nelder_mead(f, np.ones(37)*0.5)
    print (final[0])
    change_mirror(final[0])
    
    
