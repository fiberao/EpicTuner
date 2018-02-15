"""
The MIT License (MIT)

Copyright (c) 2017 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import instruments

#Imports for M-LOOP
import mloop.interfaces as mli
import mloop.controllers as mlc
import mloop.visualizations as mlv

#Other imports
import numpy as np
import time
import math
if False:
        mirror=instruments.oko_mirror()
        chn=37
        init=np.zeros(chn)/2.0
else:
        mirror=instruments.tl_mirror()
        chn=43
        init=np.ones(chn)/2.0
        print(mirror.read())
#Declare your custom class that inherits from the Interface class
class CustomInterface(mli.Interface):

        #Initialization of the interface, including this method is optional
        def __init__(self):
                #You must include the super command to call the parent class, Interface, constructor
                super(CustomInterface,self).__init__()

                #Attributes of the interface can be added here
                #If you want to pre-calculate any variables etc. this is the place to do it
                #In this example we will just define the location of the minimum
                

        #You must include the get_next_cost_dict method in your class
        #this method is called whenever M-LOOP wants to run an experiment
        def get_next_cost_dict(self,params_dict):
                x = params_dict['params']
                for each in x:
                	if (each >1) or (each <0):
                		return {'cost':powermeter_val, 'uncer':3, 'bad':True}
                mirror.change(x)
                ret= {'cost':instruments.read_power(), 'uncer':3, 'bad':False}
                return ret
def main():
        #M-LOOP can be run with three commands

        #First create your interface
        interface = CustomInterface()
        #Next create the controller, provide it with your controller and any options you want to set
        #                                                                                  
        controller = mlc.create_controller(interface,controller_type = 'gaussian_process', no_delay = False, 
        	training_type = 'nelder_mead' , initial_simplex_corner= np.ones(37)*0.5,initial_simplex_displacements= np.ones(37)*0.2,
        	max_num_runs = 10000, target_cost = -50000000, num_params = 37, min_boundary = np.zeros(37), max_boundary = np.ones(37),
        	first_params=init)
        controller.optimize()

        print('Best parameters found:')
        print(controller.best_params)
        mirror.change(controller.best_params)
        #mlv.show_all_default_visualizations(controller)


#Ensures main is run when this code is run as a script
if __name__ == '__main__':
        main()
