import numpy as np
import cvxpy as cvx

chn_num = 80
mes_num = 100
c0v=cvx.Variable()
c0 = (np.ones(mes_num) * c0v).T
Q = cvx.Variable(chn_num, chn_num)
c1 = cvx.Variable(chn_num)

y = np.random.randn(1, mes_num)

u = np.random.randn(chn_num, mes_num)


# y - (c0 - c1.T * u - cvx.diag(( u.T * Q * u)).T))
objective = cvx.Minimize(cvx.sum_squares(y - (c0 - c1.T * u - cvx.diag(( u.T * Q * u)).T)))
cons = [Q >> 0]
prob = cvx.Problem(objective, cons)
# The optimal objective is returned by prob.solve().
result = prob.solve(solver=cvx.SCS)
# The optimal value for x is stored in x.value.
print(c0v.value)
print(Q.value)
print(c1.value)