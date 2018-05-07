"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket, time, copy, json, math, pickle
import ws_broadcast
import numpy as np


class Feedback():
    def __init__(self, sensor, acturator, save_file="train_dataset.pkl"):
        self.calls = 0
        self.acturator = acturator
        self.sensor = sensor
        print("Current power:", sensor.read())

        if save_file is not None:
            self.save_file = open(save_file, "a+b")
        else:
            self.save_file = None

        print("Control loop standby.")

    def write(self, list):
        self.acturator.write(list)

    def read(self):
        return self.sensor.read()

    def f(self, x):
        # make a safe copy
        x_copied = []
        for each in x:
            if isinstance(each, float):
                x_copied.append(each)
            else:
                print(x)
                raise ValueError(
                    "Non-float control value is not accepted in the control loop.")

        self.acturator.write(x_copied)
        power = self.sensor.read()
        self.calls += 1
        if (self.calls % 100 == 1):
            print("runs: {}".format(self.calls))
        if self.save_file is not None:
            pickle.dump((x_copied, power), self.save_file, -1)
        return power


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

    def do(self):
        self.powermeter.sendto("r".encode(
            "ascii"), (self.powermeter_IP, self.powermeter_PORT))
        data, addr = self.powermeter.recvfrom(512)  # buffer size is 1024 bytes

        return int(data.decode("ascii"))

    def read(self, size=10):
        last = []
        for i in range(size):
            last.append(self.do())
        power = np.mean(np.array(last)) / 1000000.0
        std = np.std(np.array(last)) / 1000000.0
        if self.aio:
            if (time.time() - self.last_sent >= 2):
                try:
                    self.aio.send('power', power)
                    self.last_sent = time.time()
                except Exception:
                    pass
        return power


class Mirror():
    def __init__(self, mirror_IP, mirror_PORT, prefix):
        self.prefix = prefix
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
            self.range_factor = 200.0
            self.format = "{0:.2f}"
            self.relax = False
            self.mirror_PORT = 9999

        self.mirror_IP = mirror_IP
        if mirror_PORT is not None:
            self.mirror_PORT = mirror_PORT
        if prefix == "oko":
            self.default = [0.0 for i in range(self.chn)]
        else:
            self.default = [0.5 for i in range(self.chn)]
        self.max = [1.0 for i in range(self.chn)]
        self.min = [0.0 for i in range(self.chn)]
        print("{} mirror udp connection:  {}:{}".format(prefix, mirror_IP, self.mirror_PORT))
        self.mirror = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("{} DMVIEW URL:  ws://localhost:{}".format(prefix, self.mirror_PORT - 1))
        self.dmview = ws_broadcast.broadcast(self.mirror_PORT - 1)
        self.initial = self.read()

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
            datalist = [(float(each) - self.range_offset) / self.range_factor for each in datalist]
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

    def get_device_zernike(self, zernike_list):
        zernike_list[0] = zernike_list[0] * 100 + 100
        zernike_list[1] = zernike_list[1] * 100 + 100
        zernike_list[2] = zernike_list[2] * 100 + 100
        command = "6 " + " ".join([self.format.format(x) for x in zernike_list])

        data = self.do(command)

        if data is None:
            raise ValueError("remote mirror returns nothing")
        else:
            datalist = data.split(" ")

            datalist.pop()
            datalist = [float(each) for each in datalist]
            # print(datalist)
            return np.array(datalist, dtype=np.uint32) / 200.0

    def write(self, int_list):
        if self.relax:
            self.device_relax(np.array(int_list.copy()), np.array(self.now.copy()))
        # show change on dmview
        dmview_now = copy.deepcopy(int_list)
        # print(dmview_now)
        if isinstance(dmview_now, list):
            self.dmview.send(json.dumps(dmview_now))
        else:
            self.dmview.send(json.dumps(dmview_now.tolist()))

        # change mirror
        command = "1 " + \
                  " ".join([self.format.format(self.range_offset + x * self.range_factor)
                            for x in int_list])
        self.do(command)
        self.now = copy.deepcopy(int_list)


class ZNKAdapter():
    def __init__(self, mirror):
        self.real_mirror = mirror
        # load zernike controller
        if self.real_mirror.prefix == "alpao":
            self.chn = 14
            self.normolization = 100.0
            self.wf_offset = 0
            self.get_device_zernike = False
        elif self.real_mirror.prefix == "oko":
            self.chn = 14
            self.normolization = 2e-7
            self.wf_offset = 1e-8
            self.get_device_zernike = False
        elif self.real_mirror.prefix == "thorlabs":
            self.chn = 12 + 3
            self.get_device_zernike = True
            self.format = "{0:.6f}"
        else:
            raise ValueError("unsupported mirror!!!")
        self.max = np.ones(self.chn)
        self.min = -np.ones(self.chn)
        self.default = np.zeros(self.chn)
        self.initial = np.zeros(self.chn)

        with open("mirrors/{prefix}/{prefix}_fit.json".format(prefix=self.real_mirror.prefix)) as file:
            loaded = json.loads(file.read())
            self.mesh_to_act = np.asarray(loaded["inv"])
            self.wf_min = np.min(self.mesh_to_act)
            self.wf_max = np.max(self.mesh_to_act)

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
            q[z] -= mean
        q *= self.normolization
        q -= self.wf_offset
        return q

    def calc_arbitrary(self, arbi):
        p = np.dot(arbi, self.mesh_to_act)
        return p

    def read(self):
        raise ValueError("can not read in zernike")

    def write(self, int_list):
        if self.get_device_zernike:
            ret = self.real_mirror.get_device_zernike(int_list)
        else:
            ret = self.calc_zernike(int_list)
            # print("wf gap {}, min {}, max {}".format(np.min(ret)-np.max(ret), np.min(ret), np.max(ret)))
            ret = self.calc_arbitrary(ret)
            # print("cmd gap {}, min {}, max {}".format(np.min(ret) - np.max(ret), np.min(ret), np.max(ret)))
        ret = np.maximum(np.array(self.real_mirror.min),
                         np.minimum(ret + 0.5, np.array(self.real_mirror.max)))
        # print("write zernike", ret)
        self.real_mirror.write(ret)


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
        self.bind()

    def read_all_initial(self):
        mirrors_now = []
        for mirror in self.mirrors:
            mirrors_now.append(mirror.inital.copy())
        return mirrors_now

    def write_all(self, mirrors_now):
        # send chn_now
        for i in range(len(self.mirrors)):
            self.mirrors[i].write(mirrors_now[i])

    def bind(self, bindings=None):
        if bindings is None:
            self.bindings = [i for i in range(0, len(self.chn_mapto_mirror))]
        else:
            self.bindings = bindings
        self.chn = len(self.bindings)
        self.max = np.zeros(self.chn)
        self.min = np.zeros(self.chn)
        self.default = np.zeros(self.chn)

        for j in range(0, self.chn):
            i = self.bindings[j]

            self.max[j] = self.mirrors[self.chn_mapto_mirror[i]
            ].max[self.chn_mapto_acturators[i]]
            self.min[j] = self.mirrors[self.chn_mapto_mirror[i]
            ].min[self.chn_mapto_acturators[i]]
            self.default[j] = self.mirrors[self.chn_mapto_mirror[i]
            ].default[self.chn_mapto_acturators[i]]

    def reset(self):
        self.write(self.default)
        self.print()

    def print(self):
        mirrors_now = self.read_all_initial()
        for j in range(0, self.chn):
            i = self.bindings[j]
            print("CHN ", j, " (#", i,
                  ") maps to ACT ", self.chn_mapto_acturators[i],
                  " on MIRROR ", self.chn_mapto_mirror[i],
                  " max: ", self.max[j],
                  " min: ", self.min[j],
                  " typ: ", self.default[j],
                  " init: ", mirrors_now[self.chn_mapto_mirror[i]][self.chn_mapto_acturators[i]])

    def write(self, x):
        mirrors_now = self.read_all_initial()
        # update chn_now
        if sum(np.array(x) > self.max) + sum(np.array(x) < self.min) > 0:
            print("control value exceeded.", np.array(x))
            return 0
        for j in range(len(self.bindings)):
            i = self.bindings[j]
            mirrors_now[self.chn_mapto_mirror[i]
            ][self.chn_mapto_acturators[i]] = x[j]
        self.write_all(mirrors_now)

    def read(self):

        mirrors_now = self.read_all_initial()
        vchn_init = np.zeros(len(self.bindings))
        for j in range(0, len(self.bindings)):
            i = self.bindings[j]
            vchn_init[j] = mirrors_now[self.chn_mapto_mirror[i]][self.chn_mapto_acturators[i]]
        print("======== Control loop status ======")
        self.print()
        print("========     END status      ======")
        return vchn_init
