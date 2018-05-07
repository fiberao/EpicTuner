"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import feedback,json

if __name__ == "__main__":
    feedback,feedback_znk = feedback.create_loop(prefix="usersetpoint")
    chn = feedback.acturator.chn
    while True:
        try:
            fname = input("set value to all chn:")
            with open(fname + ".txt", 'r') as output:
                if fname.find("znk")>0:
                    print("zernike setpoint")
                    feedback_znk.write(json.load(output))
                if fname.find("raw")>0:
                    print("raw setpoint")
                    feedback.write(json.load(output))
            # print(feedback.mirrors_now)
            print("Power: {} uW".format(feedback.sensor.read()))
        except Exception as e:
            print(e)