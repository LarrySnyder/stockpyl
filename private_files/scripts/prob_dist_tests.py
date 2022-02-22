import sys
from scipy.stats import uniform, randint
import matplotlib.pyplot as plt

sys.path.append('/Users/larry/Documents/GitHub/stockpyl')

from stockpyl.helpers import *


def run_irwin_hall_cdf_test():
	"""Test ``helpers.irwin_hall_cdf()``. This is not a unit test; it must be
	run manually. It simulates many sums of uniform distributions and plots
	their empirical cdf against the calculated cdf.

	"""

	n = 4
	T = 100000
	nbins = 100

	sums = []
	for t in range(T):
		sums.append(np.sum(uniform.rvs(size=n)))

	x = np.arange(0, n, n * 1.0/nbins)
	F_empirical = np.zeros(np.size(x))
	F_calc = np.zeros(np.size(x))
	for b in range(nbins):
		F_empirical[b] = np.sum(1 if sums[t] < x[b] else 0 for t in range(T)) / T
		F_calc[b] = irwin_hall_cdf(x[b], n)

	plt.plot(x, F_empirical, 'r')
	plt.plot(x, F_calc, 'b')
	plt.show()


def run_sum_of_continuous_uniforms_distribution_test():
	"""Test ``helpers.sum_of_continuous_uniforms_distribution()``. This is not a unit test;
	it must be run manually. It simulates many sums of uniform distributions and
	plots their empirical cdf against the calculated cdf.

	"""

	n = 4
	lo = 20
	hi = 60
	T = 10000
	nbins = 100

	sums = []
	for t in range(T):
		sums.append(np.sum(uniform.rvs(lo, hi-lo, size=n)))

	dist = sum_of_continuous_uniforms_distribution(n, lo, hi)

	x = np.arange(n*lo, n*hi, n * (hi-lo)/nbins)
	F_empirical = np.zeros(np.size(x))
	F_calc = np.zeros(np.size(x))
	for b in range(nbins):
		F_empirical[b] = np.sum(1 if sums[t] < x[b] else 0 for t in range(T)) / T
		F_calc[b] = dist.cdf(x[b])

	plt.plot(x, F_empirical, 'r')
	plt.plot(x, F_calc, 'b')
	plt.show()


def run_sum_of_discrete_uniforms_distribution_test():
	"""Test ``helpers.sum_of_discrete_uniforms_distribution()``. This is not a unit test;
	it must be run manually. It simulates many sums of uniform distributions and
	plots their empirical cdf against the calculated cdf.

	"""

	n = 4
	lo = 20
	hi = 60
	T = 10000
	nbins = 100

	sums = []
	for t in range(T):
		sums.append(np.sum(randint.rvs(lo, hi + 1, size=n)))

	dist = sum_of_discrete_uniforms_distribution(n, lo, hi)

	x = np.arange(n*lo, n*hi, n * (hi-lo)/nbins)
	F_empirical = np.zeros(np.size(x))
	F_calc = np.zeros(np.size(x))
	for b in range(nbins):
		F_empirical[b] = np.sum(1 if sums[t] < x[b] else 0 for t in range(T)) / T
		F_calc[b] = dist.cdf(x[b])

	plt.plot(x, F_empirical, 'r')
	plt.plot(x, F_calc, 'b')
	plt.show()


#test_irwin_hall_cdf()
#run_sum_of_continuous_uniforms_distribution_test()
run_sum_of_discrete_uniforms_distribution_test()

#dist = sum_of_discrete_uniforms_distribution(2, 5, 10)
#print(dist.pmf(18))
