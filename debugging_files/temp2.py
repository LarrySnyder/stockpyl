from ss import *
import cProfile
import re
from scipy.stats import poisson
from loss_functions import *
import timeit

h = 1
p = 9
K = 64
mu = 64

cProfile.run('s_s_discrete_exact(h, p, K, True, mu)')

# def lots_of_losses():
# 	for mu in range(1, 100):
# 		dist = poisson(mu)
# 		for x in range(0, 3*mu, int(np.ceil(3*mu/10))):
# 			_, _ = discrete_loss(x, dist)

# cProfile.run('lots_of_losses()')


# def temp():
# 	for _ in range(1000):
# 		dist = poisson(50)
#
# cProfile.run('temp()')