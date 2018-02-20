"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket
import ws_broadcast
dmview = ws_broadcast.broadcast()
# POWER METER

class powermeter():
    def __init__(self, powermeter_IP="localhost", powermeter_PORT=7777):
        self.powermeter_IP = powermeter_IP
        self.powermeter_PORT = powermeter_PORT
        print("powermeter IP:" + str(powermeter_IP))
        print("powermeter port:" + str(powermeter_PORT))
        self.powermeter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def read_power(self):
        self.powermeter.sendto("r".encode(
            "ascii"), (self.powermeter_IP, self.powermeter_PORT))
        data, addr = self.powermeter.recvfrom(512)  # buffer size is 1024 bytes
        return int(data.decode("ascii"))


class oko_mirror():
    def __init__(self, mirror_IP="localhost", mirror_PORT=8888):
        self.mirror_IP = mirror_IP
        self.mirror_PORT = mirror_PORT
        print("mirror IP:" + str(mirror_IP))
        print("mirror port:" + str(mirror_PORT))
        self.mirror = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def change(self, int_list, wait=True):
        max_v = 40
        forbidden_area_v = 40
        dmview_now = [forbidden_area_v]
        for each in int_list:
            dmview_now.append((1.0 - each) * max_v)
        dmview.send(str(dmview_now))
        # change mirror
        try:
            self.mirror.sendto((" ".join([str(int(x * 4095)) for x in int_list])).encode(
                "ascii"), (self.mirror_IP, self.mirror_PORT))
            if (wait):
                data, addr = self.mirror.recvfrom(
                    512)  # buffer size is 1024 bytes
                #print ("mirro config:", data.decode("ascii"))
        except ConnectionResetError as e:
            print(str(e))
            return None

    def close(self):
        self.mirror.sendto("9999 ".encode("ascii"),
                           (self.mirror_IP, self.mirror_PORT))


class tl_mirror():
    def __init__(self, mirror_IP="localhost", mirror_PORT=9999):
        self.mirror_IP = mirror_IP
        self.mirror_PORT = mirror_PORT
        print("mirror IP:" + str(mirror_IP))
        print("mirror port:" + str(mirror_PORT))
        self.mirror = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def change(self, int_list, wait=True):
        max_v = 40
        forbidden_area_v = 20
        dmview_now = [forbidden_area_v]
        for each in int_list:
            dmview_now.append((each) * max_v)
        dmview.send(str(dmview_now))
        # change mirror
        try:
            command = (
                "1 " + " ".join(["{0:.6f}".format(x * 200.0) for x in int_list])).encode("ascii")
            # print(command)
            self.mirror.sendto(command, (self.mirror_IP, self.mirror_PORT))
            if (wait):
                #print("started waiting...")
                data, addr = self.mirror.recvfrom(1024)
                #print ("mirro config:", data.decode("ascii"))
        except ConnectionResetError as e:
            print(str(e))
            return None

    def close(self):
        self.mirror.sendto("9999 ".encode("ascii"),
                           (self.mirror_IP, self.mirror_PORT))

    def read(self):
        try:
            self.mirror.sendto("3 1".encode("ascii"),
                               (self.mirror_IP, self.mirror_PORT))
            data, addr = self.mirror.recvfrom(512)
        except ConnectionResetError as e:
            print(str(e))
            return None
        datalist = data.decode("ascii").split(" ")
        datalist.pop()
        return datalist
