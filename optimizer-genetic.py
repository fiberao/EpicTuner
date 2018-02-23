"""
The MIT License (MIT)

Copyright (c) 2018 Zuzeng Lin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import feedback
import numpy as np
import pickle


def genetic(f, init, lower_bound, upper_bound, goal=1, initial_trubulance=0.3):
    def evaluate_family(f, parents):
        list_of_goodness = []
        # take measurements of all parents
        #print("Evaluate family...")
        for each in parents:
            result = max(f(each), 0)
            list_of_goodness.append(result)
            #print ("Got " +str(result)+" nW, when measuring with config: "+str(each)+".")
            #print ("Got " +str(result)+" nW")
        return list_of_goodness

    def generate_child(parents, list_of_goodness, n=20, first_iter_overwrite=False, gamma=0.5, rou=3.6 * 10**-6, C=10):
        d = len(parents[0])
        w = []
        a = []
        idd = 0
        for ci in list_of_goodness:
            #print("generate_child based on "+str(ci)+" config:"+str(parents[idd]))
            if first_iter_overwrite is False:
                if (sum(list_of_goodness) == 0):
                    # random jump
                    w.append(1.0 / len(list_of_goodness))
                else:
                    w.append(ci / sum(list_of_goodness))
                if (ci == 0):
                    # jump out
                    a.append(gamma)
                else:
                    a.append(((C / ci)**gamma) * rou)
            else:
                w.append(1.0 / len(list_of_goodness))
                a.append(ci)
            idd += 1
        ret = []
        for repetion in range(0, n):
            sumed = np.zeros(d)
            for i in range(0, len(parents)):
                # sample from the last generations
                max_try = 4
                sample = np.random.multivariate_normal(
                    parents[i], a[i] * np.identity(d), check_valid="raise")
                # resample if out bound

                while (max_try > 0) and (sum(sample > upper_bound) > 0 or sum(sample < lower_bound) > 0):
                    sample = np.random.multivariate_normal(
                        parents[i], a[i] * np.identity(d), check_valid="raise")
                    max_try -= 1

                # hard cut
                sample = np.minimum(sample, upper_bound)
                sample = np.maximum(sample, lower_bound)
                # and add
                #print("sample to "+str(sample))
                sumed += w[i] * sample
            ret.append(sumed)
        return ret

    def select_best_k_childs_as_parents(parents, list_of_goodness, k=10):
        index = np.flip(np.argsort(list_of_goodness), 0)

        ret_child = []
        ret_goodness = []
        for i in range(0, k):
            ret_child.append(parents[index[i]])
            ret_goodness.append(list_of_goodness[index[i]])
            #print("Select "+str(list_of_goodness[index[i]])+" nW config:"+str(parents[index[i]]))

        return ret_child, ret_goodness

    def generate_first_family(grouping=[[0, 7], [8, 15], [16, 23], [24, 31], [32, 39], [40, 42]], fname=".\\genetic_first_family.pkl"):
        def plus_minus_beta(medium, mask, beta):
            ret = []
            for i in range(0, 2**sum(mask)):
                binary_set = format(i, '0' + str(sum(mask)) + 'b')
                j = 0
                generate = medium.copy()
                for k in range(0, len(mask)):
                    if mask[k]:
                        if binary_set[j] == "1":
                            generate[k] += beta
                        else:
                            generate[k] -= beta
                        j += 1
                ret.append(generate)
            return ret

        def generate_grouping(init, gp_start, gp_end, beta):
            mask = []
            for i in range(0, gp_start):
                mask.append(False)
            for i in range(gp_start, gp_end + 1):
                mask.append(True)
            for i in range(gp_end + 1, len(init)):
                mask.append(False)
            #print (mask)
            return (plus_minus_beta(init, mask, beta))

        import os.path
        if os.path.isfile(fname):
            with open(fname, 'rb') as inputf:
                ret = pickle.load(inputf)
                print("[WARNING] using the existing first_family")
        else:
            with open(fname, 'wb') as output:
                initial_family = []
                initial_goodness = []
                for each_group in grouping:
                    print(each_group)
                    group_created_family = generate_grouping(
                        init, each_group[0], each_group[1], beta=initial_trubulance)
                    group_created_family_var = np.std(
                        evaluate_family(f, group_created_family))
                    for each in group_created_family:
                        # print(each)
                        initial_family.append(each)
                        initial_goodness.append(group_created_family_var)
                ret = generate_child(initial_family, initial_goodness,
                                     40, first_iter_overwrite=True, C=goal)
                pickle.dump(ret, output, pickle.HIGHEST_PROTOCOL)
        return ret

    def check_stop(parents, list_of_goodness, iter_id):
        if (iter_id % 5 == 1):
            print("best so far... " + str(list_of_goodness[0]))
            # print(str(parents[0]))
            print(str(iter_id) + " iters...")
        return False

    print("===== initial_family======")
    family = generate_first_family()
    print("====== start genetic_algo ========")
    # main optimization part
    iter_id = 0
    while True:
        iter_id += 1
        goodness = evaluate_family(f, family)
        family, goodness = select_best_k_childs_as_parents(family, goodness)
        if check_stop(family, goodness, iter_id):
            print(family)
        else:
            family = generate_child(family, goodness, C=goal)


if __name__ == "__main__":

    feedback = feedback.please_just_give_me_a_simple_loop()
    input("press any key to start optimzation")
    genetic(feedback.f, feedback.get_executed(),
            feedback.vchn_min, feedback.vchn_max,
            goal=40939, initial_trubulance=0.2)
