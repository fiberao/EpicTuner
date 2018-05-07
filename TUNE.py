"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from optimizer import genetic, nm
import feedback

if __name__ == "__main__":
    feedback_raw, feedback_znk = feedback.create_loop()
    if input("znk/raw?:").find("znk") >= 0:
        print("znk optimization running...")
        feedback = feedback_znk
    else:
        print("raw optimization running...")
        feedback = feedback_raw
    if (input("Do you want to reset? (yes/no)") == "yes"):
        feedback.acturator.reset()

    if input("ga/nm?:").find("nm") >= 0:
        print("optimization started with Nelder_mead")
        final = nm.nelder_mead(feedback.f, feedback.acturator.read(), max_iter=10000)
        feedback.f(final[0])
    else:
        initial_trubulance = float(input("initial_trubulance(0.1):"))
        print("optimization started with Genetic algorithm")
        genetic.genetic(feedback.f, feedback.acturator.read().tolist(),
                        feedback.acturator.min.tolist(), feedback.acturator.max.tolist(),
                        goal=80000, initial_trubulance=initial_trubulance)
