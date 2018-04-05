"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket, time, copy, json, math
import ws_broadcast
import numpy as np


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

    def read_raw(self):
        self.powermeter.sendto("r".encode(
            "ascii"), (self.powermeter_IP, self.powermeter_PORT))
        data, addr = self.powermeter.recvfrom(512)  # buffer size is 1024 bytes

        return int(data.decode("ascii"))

    def read(self, size=1):
        last = []
        for i in range(size):
            last.append(self.read_raw())
        power = np.mean(np.array(last)) / 1000000.0
        std = np.std(np.array(last)) / 1000000.0
        if self.aio:
            if (time.time() - self.last_sent >= 2):
                try:
                    self.aio.send('power', power)
                    self.last_sent = time.time()
                except Exception:
                    pass
        if size > 1:
            return [power, std]
        else:
            return power


class Mirror():
    def __init__(self, mirror_IP, mirror_PORT, prefix):
        if prefix == "alpao":
            self.chn = 97
            self.range_offset = -1.0
            self.range_factor = 2.0
            self.format = "{0:.6f}"
            self.relax = False
            self.mirror_PORT = 5555
        elif prefix == "oko":
            self.chn = 37
            self.range_offset = 0.0
            self.range_factor = 4095.0
            self.format = "{0:.0f}"
            self.relax = False
            self.mirror_PORT = 8888
        elif prefix == "thorlabs":
            self.chn = 43
            self.range_offset = 0.0
            self.range_factor = 199.0
            self.format = "{0:.6f}"
            self.relax = True
            self.mirror_PORT = 9999

        self.mirror_IP = mirror_IP
        if mirror_PORT is not None:
            self.mirror_PORT = mirror_PORT

        self.default = [0.5 for i in range(self.chn)]
        self.max = [1.0 for i in range(self.chn)]
        self.min = [0.0 for i in range(self.chn)]
        print("{} mirror udp connection:  {}:{}".format(prefix, mirror_IP, self.mirror_PORT))
        self.mirror = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("{} DMVIEW URL:  ws://{}:{}".format(prefix, mirror_IP, self.mirror_PORT - 1))
        self.dmview = ws_broadcast.broadcast(self.mirror_PORT - 1)
        self.now = self.read()

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
        if data is None:
            raise ValueError("remote mirror returns nothing")
        else:
            datalist = data.split(" ")
            datalist.pop()
            datalist = [(float(each)-self.range_offset) / self.range_factor for each in datalist]
            return datalist

    def device_relax(self, setpoint, prev, reset_all=True, sleep=0.3):
        mask_for_relax = abs(prev - setpoint) > (1.0 / 2000.0)
        if sum(mask_for_relax) > 0:

            if reset_all:
                int_list = [-1 for each in mask_for_relax]
            else:
                int_list = (-1) * mask_for_relax + \
                           (1 - mask_for_relax) * setpoint

            command = "4 " + \
                      " ".join([self.format.format(x * self.range_factor)
                                for x in int_list])
            self.do(command)
            time.sleep(sleep)

    def write(self, int_list):
        if self.relax:
            self.device_relax(np.array(int_list.copy()), np.array(self.now.copy()))
        # show change on dmview
        dmview_now = copy.deepcopy(int_list)
        self.dmview.send(str(dmview_now))
        # change mirror
        command = "1 " + \
                  " ".join([self.format.format(self.range_offset + x * self.range_factor)
                            for x in int_list])
        self.do(command)
        self.now = copy.deepcopy(int_list)


class ZNKMirror(Mirror):

    def __init__(self, mirror_IP, mirror_PORT, prefix):
        self.chn = 14
        self.real_mirror = Mirror(mirror_IP, mirror_PORT, prefix)

        # load zernike controller
        with open("mirrors/{prefix}/{prefix}_fit.json".format(prefix=prefix)) as file:
            loaded = json.loads(file.read())
            self.mesh_to_act = np.asarray(loaded["inv"])
            self.wavefront_x = loaded["wfx"]
            self.wavefront_y = loaded["wfy"]
        g = np.zeros((len(self.wavefront_x), 14))
        for w in range(len(self.wavefront_x)):
            v = self.wavefront_x[w]
            z = self.wavefront_y[w]
            R = math.sqrt(v * v + z * z)
            T = math.atan2(z, v)
            g[w][0] = 2 * R * math.cos(T)
            g[w][1] = 2 * R * math.sin(T)
            g[w][2] = math.sqrt(3) * (2 * R * R - 1)
            g[w][3] = math.sqrt(6) * R * R * math.sin(2 * T)
            g[w][4] = math.sqrt(6) * R * R * math.cos(2 * T)
            g[w][5] = math.sqrt(8) * (3 * R * R * R - 2 * R) * math.sin(T)
            g[w][6] = math.sqrt(8) * (3 * R * R * R - 2 * R) * math.cos(T)
            g[w][7] = math.sqrt(8) * (R * R * R) * math.sin(3 * T)
            g[w][8] = math.sqrt(8) * (R * R * R) * math.cos(3 * T)
            g[w][9] = math.sqrt(5) * (6 * R * R * R * R - 6 * R * R + 1)
            g[w][10] = math.sqrt(10) * (4 * R * R * R * R - 3 * R * R) * math.cos(2 * T)
            g[w][11] = math.sqrt(10) * (4 * R * R * R * R - 3 * R * R) * math.sin(2 * T)
            g[w][12] = math.sqrt(10) * R * R * R * R * math.cos(4 * T)
            g[w][13] = math.sqrt(10) * R * R * R * R * math.sin(4 * T)
        self.zernike_modes_to_mesh = g

    def calc_zernike(self, zernike_list):
        q = np.zeros(len(self.wavefront_x))
        mean = 0
        for z in range(len(self.wavefront_x)):
            for mode_zernike in range(len(zernike_list)):
                q[z] += zernike_list[mode_zernike] * self.zernike_modes_to_mesh[z][mode_zernike]
                mean += q[z]
        mean /= len(self.wavefront_x)
        for z in range(len(self.wavefront_x)):
            q[z] /= mean
        return self.calc_arbitrary(q)

    def calc_arbitrary(self, arbi):
        p = np.dot(arbi, self.mesh_to_act)
        return p

    def read(self):
        raise ValueError("can not read in zernike")

    def write(self, int_list):
        print("write zernike")
        self.real_mirror.write(self.calc_arbitrary(int_list))


class Router():
    def __init__(self, mirrors=[], ask_reset=True):
        if mirrors is None:
            raise ValueError("[WARNING] Running in simulation mode!")
        self.mirrors = mirrors
        self.chn_mapto_mirror = []
        self.chn_mapto_acturators = []

        mirror_count = 0
        for mirror in self.mirrors:
            for i in range(mirror.chn):
                self.chn_mapto_mirror.append(mirror_count)
                self.chn_mapto_acturators.append(i)
            mirror_count += 1
        self.bind(clear=ask_reset)

    def read_all(self):
        mirrors_now = []
        for mirror in self.mirrors:
            mirrors_now.append(mirror.now.copy())
        return mirrors_now

    def write_all(self, mirrors_now):
        # send chn_now
        for i in range(len(self.mirrors)):
            self.mirrors[i].write(
                mirrors_now[i])

    def bind(self, bindings=None, clear=True):
        if bindings is None:
            self.bindings = [i for i in range(0, len(self.chn_mapto_mirror))]
        else:
            self.bindings = bindings
        self.chn = len(self.bindings)
        self.max = np.zeros(self.chn)
        self.min = np.zeros(self.chn)
        self.vchn_default = np.zeros(self.chn)

        for j in range(0, self.chn):
            i = self.bindings[j]

            self.max[j] = self.mirrors[self.chn_mapto_mirror[i]
            ].max[self.chn_mapto_acturators[i]]
            self.min[j] = self.mirrors[self.chn_mapto_mirror[i]
            ].min[self.chn_mapto_acturators[i]]
            self.vchn_default[j] = self.mirrors[self.chn_mapto_mirror[i]
            ].default[self.chn_mapto_acturators[i]]

        print("======== Control loop status ======")
        self.print()
        print("========     END status      ======")
        if clear:
            if (input("Do you want to reset? (yes/no)") == "yes"):
                self.write(self.vchn_default)
                print("======== RESET ======")
                self.print()
                print("======== RESET ======")

    def print(self):
        mirrors_now = self.read_all()
        for j in range(0, self.chn):
            i = self.bindings[j]
            print("VCHN ", j, " binds to CHN ", i,
                  " maps to ACT ", self.chn_mapto_acturators[i],
                  " on MIRROR ", self.chn_mapto_mirror[i],
                  " max: ", self.max[j],
                  " min: ", self.min[j],
                  " typ: ", self.vchn_default[j],
                  " now: ", mirrors_now[self.chn_mapto_mirror[i]][self.chn_mapto_acturators[i]])
        return mirrors_now

    def write(self, x):
        mirrors_now = self.read_all()
        # update chn_now
        if sum(np.array(x) > self.max) + sum(np.array(x) < self.min) > 0:
            print("control value exceeded.")
            return 0
        for j in range(len(self.bindings)):
            i = self.bindings[j]
            mirrors_now[self.chn_mapto_mirror[i]
            ][self.chn_mapto_acturators[i]] = x[j]
        self.write_all(mirrors_now)

    def read(self):
        mirrors_now = self.read_all()
        vchn_init = np.zeros(len(self.bindings))
        for j in range(0, len(self.bindings)):
            i = self.bindings[j]
            vchn_init[j] = mirrors_now[self.chn_mapto_mirror[i]][self.chn_mapto_acturators[i]]
        return vchn_init
