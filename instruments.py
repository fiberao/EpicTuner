"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket
import ws_broadcast
import numpy as np
import time

# POWER METER


class powermeter():
    def __init__(self, powermeter_IP="localhost", powermeter_PORT=7777, online='6ddea3a7998b483183641022b542826d'):
        self.powermeter_IP = powermeter_IP
        self.powermeter_PORT = powermeter_PORT
        print("powermeter IP:" + str(powermeter_IP))
        print("powermeter port:" + str(powermeter_PORT))
        self.powermeter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if online:
            from Adafruit_IO import Client
            self.last_sent = time.time()
            self.aio = Client(online)

    def read(self):
        self.powermeter.sendto("r".encode(
            "ascii"), (self.powermeter_IP, self.powermeter_PORT))
        data, addr = self.powermeter.recvfrom(512)  # buffer size is 1024 bytes
        
        return int(data.decode("ascii"))

    def read_power(self, size=1):
        last = []
        for i in range(size):
            last.append(self.read())
        power = np.mean(np.array(last)) / 1000000.0
        std = np.std(np.array(last)) / 1000000.0
        if self.aio:
            if (time.time() - self.last_sent >= 2):
                try:
                    self.aio.send('power', power)
                    self.last_sent = time.time()
                except Exception:
                    pass
        if size>1:
            return [power,std]
        else:
            return power

class mirror():
    def do(self, code, wait=True):
        try:
            self.mirror.sendto(code.encode("ascii"),
                               (self.mirror_IP, self.mirror_PORT))
            if (wait):
                data, addr = self.mirror.recvfrom(1024)
        except ConnectionResetError as e:
            print(str(e))
            return None
        return data.decode("ascii")

    def close(self):
        self.do("9999 ")

    def read(self):
        data = self.do("3 ")
        datalist = data.split(" ")
        datalist.pop()
        datalist = [float(each) / self.range_factor for each in datalist]
        return datalist

    def write(self, int_list, wait=True):
        dmview_now = [self.dmv_forbidden_area_v]
        for each in int_list:
            dmview_now.append((each) * self.dmv_max_v)
        self.dmview.send(str(dmview_now))
        # change mirror

        command = "1 " + \
            " ".join([self.format.format(self.range_offset+ x * self.range_factor)
                      for x in int_list])
        self.do(command)


class alpao_mirror(mirror):
    def __init__(self, mirror_IP="localhost", mirror_PORT=5555):
        self.mirror_IP = mirror_IP
        self.mirror_PORT = mirror_PORT
        print("Alpao mirror IP:" + str(mirror_IP))
        print("Alpao mirror port:" + str(mirror_PORT))
        self.mirror = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.chn = 97
        self.default = [0.5 for i in range(self.chn)]
        self.max = [1.0 for i in range(self.chn)]
        self.min = [0.0 for i in range(self.chn)]
        self.range_offset = -1.0
        self.range_factor = 2.0
        self.format = "{0:.6f}"
        self.dmv_max_v = 1
        self.dmv_forbidden_area_v = 0
        self.now = self.read()
        self.dmview = ws_broadcast.broadcast(mirror_PORT - 1)

    def change(self, int_list, relax=False):
        self.write(int_list)
        self.now = int_list

class oko_mirror(mirror):
    def __init__(self, mirror_IP="localhost", mirror_PORT=8888):
        self.mirror_IP = mirror_IP
        self.mirror_PORT = mirror_PORT
        print("OKO mirror IP:" + str(mirror_IP))
        print("OKO mirror port:" + str(mirror_PORT))
        self.mirror = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.chn = 37
        self.default = [0.5 for i in range(self.chn)]
        self.max = [1.0 for i in range(self.chn)]
        self.min = [0.0 for i in range(self.chn)]
        self.range_offset = 0.0
        self.range_factor = 4095.0
        self.format = "{0:.0f}"
        self.dmv_max_v = 1
        self.dmv_forbidden_area_v = 0
        self.now = self.read()
        self.dmview = ws_broadcast.broadcast(mirror_PORT - 1)

    def change(self, int_list, relax=False):
        self.write(int_list)
        self.now = int_list


class tl_mirror(mirror):
    def __init__(self, mirror_IP="localhost", mirror_PORT=9999):
        self.mirror_IP = mirror_IP
        self.mirror_PORT = mirror_PORT
        print("TL mirror IP:" + str(mirror_IP))
        print("TL mirror port:" + str(mirror_PORT))
        self.mirror = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.chn = 43
        self.default = [0.43 for i in range(self.chn)]
        self.max = [1.0 for i in range(self.chn)]
        self.min = [0.0 for i in range(self.chn)]
        self.range_offset = 0.0
        self.range_factor = 199.0
        self.format = "{0:.6f}"
        self.dmv_max_v = 40
        self.dmv_forbidden_area_v = 20
        self.now = self.read()
        self.dmview = ws_broadcast.broadcast(mirror_PORT - 1)

    def oscillate(self, setpoint, compose_relaxer, damp=-0.9, stop_cond=(1.0 / (200.0 * 10))):
        time_damp = 0.3
        while max(np.abs(compose_relaxer)) > stop_cond:
            compose_relaxer *= damp
            time_damp *= damp
            relaxed_pattern = setpoint + compose_relaxer
            relaxed_pattern = np.minimum(self.max, relaxed_pattern)
            relaxed_pattern = np.maximum(self.min, relaxed_pattern)
            self.write(relaxed_pattern)
            time.sleep(time_damp)
            relaxed_pattern = setpoint - compose_relaxer
            relaxed_pattern = np.minimum(self.max, relaxed_pattern)
            relaxed_pattern = np.maximum(self.min, relaxed_pattern)
            self.write(relaxed_pattern)
            time.sleep(time_damp)
        self.write(setpoint)
        # print("END RELAXING")

    def remote_relax(self, setpoint, prev):
        onefourth = np.array(self.default)
        # erase history
        # self.relax(np.array(self.max) - onefourth, onefourth, damp=0.9)
        # self.relax(np.array(self.min), onefourth, damp=0.9)
        # time.sleep(0.01)
        self.oscillate(setpoint, onefourth, damp=0.5)
        # rebuilt voltage
        self.oscillate(setpoint, onefourth / 4.0,
                       damp=0.95, stop_cond=(1.0 / (200.0 * 800.0)))

    def device_relax(self, setpoint, prev, reset_all=True):
        mask_for_relax = abs(prev - setpoint) > (1.0 / 2000.0)
        if sum(mask_for_relax) > 0:
            self.write(setpoint)
            if reset_all:
                int_list = [-1 for each in mask_for_relax]
            else:
                int_list = (-1) * mask_for_relax + \
                    (1 - mask_for_relax) * setpoint

            command = "4 " + \
                " ".join([self.format.format(x * self.range_factor)
                          for x in int_list])
            self.do(command)
            time.sleep(0.3)

    def change(self, int_list, relax=True):
        prev = np.array(self.now.copy())
        setpoint = np.array(int_list.copy())
        if relax:
            self.device_relax(setpoint, prev)
        self.write(int_list)
        self.now = int_list.copy()
