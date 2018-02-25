"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import feedback
from scipy.optimize import basinhopping

if __name__ == "__main__":
    feedback = feedback.please_just_give_me_a_simple_loop()

    if (input("optimzation for tl & oko? (yes/no)")) == "yes":

        # rewrite the bounds in the way required by L-BFGS-B
        bounds = [(low + .000001, high - .000001)
                  for low, high in zip(feedback.vchn_min, feedback.vchn_max)]
        print(bounds)
        minimizer_kwargs = dict(method="L-BFGS-B", bounds=bounds)
        final = basinhopping(feedback.f_nm, feedback.get_executed(),
                             minimizer_kwargs=minimizer_kwargs)
        print(final)
        feedback.execute(final)
        print("optimization for tl & oko finished!")
