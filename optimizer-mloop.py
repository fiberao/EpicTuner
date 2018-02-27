"""
The MIT License (MIT)

Copyright (c) 2017 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import feedback




# Imports for M-LOOP
import mloop.interfaces as mli
import mloop.controllers as mlc
import mloop.visualizations as mlv

# Other imports
import numpy as np



# Declare your custom class that inherits from the Interface class


class CustomInterface(mli.Interface):

    # Initialization of the interface, including this method is optional
    def __init__(self):
        # You must include the super command to call the parent class, Interface, constructor
        super(CustomInterface, self).__init__()
        self.feedback = feedback.please_just_give_me_a_simple_loop()
        # Attributes of the interface can be added here
        # If you want to pre-calculate any variables etc. this is the place to do it
        # In this example we will just define the location of the minimum

    # You must include the get_next_cost_dict method in your class
    # this method is called whenever M-LOOP wants to run an experiment
    def get_next_cost_dict(self, params_dict):
        x = params_dict['params']
        for each in x:
            if (each > 1) or (each < 0):
                return {'cost': 0, 'uncer': 3, 'bad': True}
        ret = self.feedback.f_nm(x,5)
        ret = {'cost': ret[0], 'uncer': ret[1], 'bad': False}
        return ret


def main():
    # M-LOOP can be run with three commands

    # First create your interface
    interface = CustomInterface()
    # Next create the controller, provide it with your controller and any options you want to set
    chn = 80
    controller = mlc.create_controller(interface, controller_type='gaussian_process', no_delay=False,
                                       training_type='nelder_mead', initial_simplex_corner=np.ones(chn)*0.5,
                                       initial_simplex_displacements=np.ones(
                                           chn) * 0.4,
                                       max_num_runs=10000, target_cost=-50000000,
                                       num_params=chn, min_boundary=np.ones(chn)*0.0,
                                       max_boundary=np.ones(chn)*1.0,
                                       first_params=np.ones(chn)*0.5)
    print('init okay.')
    controller.optimize()

    print('Best parameters found:')
    print(controller.best_params)
    feedback.execute(controller.best_params)

    # mlv.show_all_default_visualizations(controller)


# Ensures main is run when this code is run as a script
if __name__ == '__main__':
    main()
