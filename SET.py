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
mirror_IP = "127.0.0.1"
mirror_PORT = 8888
print ("mirror IP:"+str(mirror_IP))
print ("mirror port:"+str(mirror_PORT))
mirror = socket.socket(socket.AF_INET, # Internet
	                     socket.SOCK_DGRAM) # UDP
#init powermeter
def rec_UDP():
	print ("powermeter IP:"+str("127.0.0.1"))
	print ("powermeter port:"+str(7777))
	powermeter = socket.socket(socket.AF_INET, # Internet
	                     socket.SOCK_DGRAM) # UDP
	powermeter.bind(("127.0.0.1",7777))
	global powermeter_val
	while True:
		data, addr = powermeter.recvfrom(512) # buffer size is 1024 bytes
		powermeter_val=-int(data.decode("ascii"))		
listen_UDP = threading.Thread(target=rec_UDP)
listen_UDP.start()

def change_mirror(int_list=[0.0]):
	# change mirror
	mirror.sendto((" ".join([str(int(x*4096)) for x in int_list])).encode("ascii"), (mirror_IP, mirror_PORT))
	data, addr = mirror.recvfrom(512) # buffer size is 1024 bytes
	print ("mirro config:", data.decode("ascii"))
def close_mirror():
	mirror.sendto("9999 ".encode("ascii"), (mirror_IP, mirror_PORT))
import time
import numpy as np
while True:     
 x=np.ones(37)*min(float(input("set value to all chn: ")),1.0)
 print(x)
 change_mirror(x)
 time.sleep(0.3)

