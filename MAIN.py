"""
The MIT License (MIT)

Copyright (c) 2016 Single Quantum B. V. and Andreas Fognini
Copyright (c) 2017 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


from WebSQControl import WebSQControl

import socket
UDP_IP = "127.0.0.1"
UDP_PORT = 7777


print ("UDP target IP:"+str(UDP_IP))
print ("UDP target port:"+str(UDP_PORT))

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


#TCP IP Address of your system (default 192.168.1.1)
tcp_ip_address = '192.168.35.236'#"192.168.1.1"
#The control port (default 12000)
control_port = 12000
#and the port emitting the photon Counts (default 12345)
counts_port = 12345

websq = WebSQControl(TCP_IP_ADR = tcp_ip_address, CONTROL_PORT = control_port, COUNTS_PORT = counts_port)
websq.connect()
"""
print("Automatically finding bias current, avoid Light exposure")
found_bias_current = websq.auto_bias_calibration(DarkCounts=[100,100,100,100])
print("Bias current: " + str(found_bias_current))
"""

#Aquire number of detectors in the system
number_of_detectors =  websq.get_number_of_detectors()
print("Your system has " + str(number_of_detectors) + ' detectors\n')

print("Set integration time\n")
websq.set_measurement_periode(100)   #time in ms

print("Enable detectors\n")
websq.enable_detectors(True)
print("Read back set values")
print("====================\n")
print("Measurement Periode (ms): \t" + str(websq.get_measurement_periode()))
print("Bias Currents in uA: \t\t" +    str(websq.get_bias_current()))
print("Trigger Levels in mV: \t\t" +   str(websq.get_trigger_level()))
print("============================\n")

while True:
	#get the counts
	counts = websq.aquire_cnts(1)

	d1=counts[0][1]
	print(d1)
	sock.sendto((str(int(d1)).encode("utf-8")), (UDP_IP, UDP_PORT))
	
#Close connection
websq.close()
