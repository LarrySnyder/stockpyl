from loss_functions import *

from scipy.stats import *

p = 0.3
k = 3

class my_geom(rv_discrete):
	def _pmf(self, x):
		return np.where(x >= 1, ((1 - p) ** (x - 1)) * p, 0)
my_dist = my_geom()

# xk = np.arange(1000)
# pk = ((1-p)**(xk-1))*p
# my_dist = rv_discrete(name='custm', values=(xk,pk))

print(my_dist.pmf(k))
print(geom.pmf(k, p))

print(my_dist.cdf(k))
print(geom.cdf(k, p))
print(1 - (1-p)**k)

print('------')

#
# from scipy.stats import rv_discrete
# from numpy import exp
# class poisson_gen(rv_discrete):
#     "Poisson distribution"
#     def _pmf(self, j, mu):
#         return exp(-mu) * mu**j / factorial(j)
#
# my_poisson = poisson_gen(name="poisson")
#
# print(my_poisson.pmf(12, 10))
# print(poisson.pmf(12, 10))
#
# print(my_poisson.cdf(12, 10))
# print(poisson.cdf(12, 10))
