"""
The MIT License (MIT)

Copyright (c) 2017 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket
import ws_broadcast
#init_mirror
mirror_IP = "memory"
mirror_PORT = 8888
print ("mirror IP:"+str(mirror_IP))
print ("mirror port:"+str(mirror_PORT))
mirror = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#init powermeter
powermeter_IP = "memory"
powermeter_PORT = 7777
print ("powermeter IP:"+str(powermeter_IP))
print ("powermeter port:"+str(powermeter_PORT))
powermeter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def read_power():
	# change mirror
	powermeter.sendto("r".encode("ascii"), (powermeter_IP, powermeter_PORT))
	data, addr = powermeter.recvfrom(512) # buffer size is 1024 bytes
	return -int(data.decode("ascii"))
def change_mirror(int_list,wait=True):
	max_v=40
	forbidden_area_v=60
	dmview_now=[forbidden_area_v]
	for each in int_list:
		dmview_now.append((1.0-each)*max_v)
	ws_broadcast.send_dmview(str(dmview_now))
	# change mirror
	mirror.sendto((" ".join([str(int(x*4095)) for x in int_list])).encode("ascii"), (mirror_IP, mirror_PORT))
	if (wait):
		data, addr = mirror.recvfrom(512) # buffer size is 1024 bytes
		#print ("mirro config:", data.decode("ascii"))
def close_mirror():
	mirror.sendto("9999 ".encode("ascii"), (mirror_IP, mirror_PORT))
