"""Code to implement Chen-Zheng (1994) algorithm for stochastic serial systems
under stochastic service model (SSM), as described in Snyder and Shen (2019).

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the SSM instance.

The following attributes are used to specify input data:
	* Node-level attributes
		- echelon_holding_cost [h]
		- stockout_cost [p]
		- lead_time [L]
		- demand_mean [mu]
		- demand_standard_deviation [sigma]
	* Edge-level attributes
		(None.)

The following attributes are used to store outputs and intermediate values:
	* Graph-level attributes
		(None.)
	* Node-level attributes:
		(None.)

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import networkx as nx
import numpy as np
from scipy import stats
import math
import matplotlib.pyplot as plt

#from tests.instances_ssm_serial import *


### NETWORK-HANDLING FUNCTIONS ###

def local_to_echelon_base_stock_levels(network, S_local):
	"""Convert local base-stock levels to echelon base-stock levels.

	Assumes network is serial system but does not assume anything about the
	labeling of the nodes.

	Parameters
	----------
	network : graph
		NetworkX directed graph representing the multi-echelon serial network.
	S_local : dict
		Dict of local base-stock levels.

	Returns
	-------
	S_echelon : dict
		Dict of echelon base-stock levels.

	"""
	S_echelon = {}
	for n in network.nodes:
		S_echelon[n] = S_local[n] + \
					   np.sum([S_local[k] for k in nx.descendants(network, n)])

	return S_echelon

# TODO: write echelon_to_local_base_stock_levels()


def expected_cost(network, echelon_S, x_num=1000, d_num=100):
	"""Calculate expected cost of given solution.

	This is a convenience function that calls optimize_base_stock_levels()
	without doing any optimization.

	Parameters
	----------
	network : graph
		NetworkX directed graph representing the multi-echelon serial network.
	echelon_S : dict
		Dict of echelon base-stock levels to be evaluated.
	x_num : int, optional
		Number of discretization intervals to use for x range. Ignored if
		x is provided.
	d_num : int, optional
		Number of discretization intervals to use for d range.

	Returns
	-------
	cost : float
		Expected cost of system.
	"""
	_, cost = optimize_base_stock_levels(network, S=echelon_S, plots=False,
										 x=None, x_num=x_num, d_num=d_num)

	return cost


def expected_holding_cost(network, echelon_S, x_num=1000, d_num=100):
	"""Calculate expected holding cost of given solution.

	Basic idea: set stockout cost to 0 and call optimize_base_stock_levels()
	without doing any optimization.

	Parameters
	----------
	network : graph
		NetworkX directed graph representing the multi-echelon serial network.
	echelon_S : dict
		Dict of echelon base-stock levels to be evaluated.
	x_num : int, optional
		Number of discretization intervals to use for x range. Ignored if
		x is provided.
	d_num : int, optional
		Number of discretization intervals to use for d range.

	Returns
	-------
	holding_cost : float
		Expected holding cost of system.
	"""

	# Make copy of network and set stockout cost to 0.
	network2 = network.copy()
	for n in network2.nodes:
		network2.nodes[n]['stockout_cost'] = 0

	_, holding_cost = optimize_base_stock_levels(network2, S=echelon_S,
								plots=False, x=None, x_num=x_num, d_num=d_num)

	return holding_cost


### UTILITY FUNCTIONS ###

def find_nearest(array, values, sorted=False):
	"""Determine entries in array that are closest to each of the
	entries in values and return their indices. Neither array needs to be sorted,
	but if array is sorted and sorted is set to True, execution will be faster.
	array and values need not be the same length.

	Parameters
	----------
	array : ndarray
		The array to search for values in
	values : ndarray
		The array whose values should be searched for in the other array
	sorted : Boolean
		If True, treats array as sorted, which will make the function execute
		faster

	Returns
	-------
	ind : ndarray
		Array of indices.
	"""
	array = np.asarray(array)
	values = np.array(values, ndmin=1, copy=False)
	ind = np.zeros(values.shape)
	for v in range(values.size):
		if sorted:
			# https://stackoverflow.com/a/26026189/3453768
			idx = np.searchsorted(array, values[v], side="left")
			if idx > 0 and (idx == len(array) or math.fabs(values[v] - array[idx-1])
					< math.fabs(values[v] - array[idx])):
				ind[v] = idx-1
			else:
				ind[v] = idx
		else:
			# https://stackoverflow.com/a/2566508/3453768
			idx = (np.abs(array - values[v])).argmin()
			ind[v] = idx

	return ind.astype(int)


### OPTIMIZATION ###

def optimize_base_stock_levels(network, S=None, plots=False, x=None,
							   x_num=1000, d_num=100):
	"""Chen-Zheng (1994) algorithm for stochastic serial systems under
	stochastic service model (SSM), as described in Snyder and Shen (2019).

	Stages are assumed to be indexed N, ..., 1. Demands are assumed to be
	normally distributed.

	Parameters
	----------
	network : graph
		NetworkX directed graph representing the multi-echelon serial network.
	S : dict, optional
		Dict of echelon base-stock levels to evaluate. If present, no
		optimization is performed and the function just returns the cost
		under base-stock levels S; to optimize instead, set S=None (the default).
	plots : Boolean
		True for the function to generate plots of C(.) functions, False o/w.
	x : ndarray, optional
		x-array to use for truncation and discretization, or None (the default)
		to determine automatically.
	x_num : int, optional
		Number of discretization intervals to use for x range. Ignored if
		x is provided.
	d_num : int, optional
		Number of discretization intervals to use for d range.

	Returns
	-------
	S_star : ndarray
		array of optimal base-stock levels
	C_star : float
		optimal expected cost
	"""

	# Get shortcuts to parameters (for convenience).
	N = len(network.nodes)
	mu = network.nodes[1]['demand_mean']
	sigma = network.nodes[1]['demand_standard_deviation']
	L = np.zeros(N+1)
	h = np.zeros(N+1)
	for j in network.nodes:
		if 'lead_time' in network.nodes[j]:
			L[j] = network.nodes[j]['lead_time']
		else:
			L[j] = 0
		h[j] = network.nodes[j]['echelon_holding_cost']
	if 'stockout_cost' in network.nodes[1]:
		p = network.nodes[1]['stockout_cost']
	else:
		p = 0

	# Determine x array (truncated and discretized).
	# TODO: handle this better
	if x is None:
		x_lo = -4 * sigma * np.sqrt(sum(L))
		x_hi = mu * sum(L) + 8 * sigma * np.sqrt(sum(L))
		x_delta = (x_hi - x_lo) / x_num
		# Ensure x >= largest echelon BS level, if provided.
		if S is not None:
			x_hi = max(x_hi, max(S, key=S.get))
		# Build x range.
		x = np.arange(x_lo, x_hi + x_delta, x_delta)
	else:
		x_delta = x[1] - x[0]

	# Standard normal demand array (truncated and discretized).
	# (Use mu + d * sigma to get distribution-specific demands).
	d_lo = -4
	d_hi = 4
	d_delta = (d_hi - d_lo) / d_num
	d = np.arange(d_lo, d_hi + d_delta, d_delta)
	# Probability array.
	fd = stats.norm.cdf(d+d_delta/2) - stats.norm.cdf(d-d_delta/2)

	# Extended x array (used for approximate C-hat function).
	x_ext_lo = np.min(x) - (mu * sum(L) +
							d.max() * sigma * np.sqrt(sum(L)))
	x_ext_hi = np.max(x) + (mu * sum(L) +
							d.max() * sigma * np.sqrt(sum(L)))
	x_ext = np.arange(x_ext_lo, x_ext_hi, x_delta)

	# Initialize arrays. (0th element is ignored since we are assuming stages
	# are numbered starting at 1. C_bar is an exception since C_bar[0] is
	# meaningful.)
	C_hat = np.zeros((N+1, len(x)))
	C = np.zeros((N+1, len(x)))
	S_star = np.zeros(N+1)
	C_star = np.zeros(N+1)
	C_bar = np.zeros((N+1, len(x)))

	# Initialize arrays containing approximation for C (mainly for deubugging).
	C_hat_lim1 = np.zeros((N+1, len(x_ext)))
	C_hat_lim2 = np.zeros((N+1, len(x_ext)))

	# Calculate C_bar[0, :].
	C_bar[0, :] = (p + sum(h)) * np.maximum(-x, 0)

	# Loop through stages.
	for j in range(1, N+1):

#		print(str(j))

		# Calculate C_hat.
		C_hat[j, :] = h[j] * x + C_bar[j-1, :]

		# Calculate approximate C-hat function.
		C_hat_lim1[j, :] = -(p + sum(h)) * (x_ext - mu * sum(L[1:j]))
		for i in range(1, j+1):
			C_hat_lim1[j, :] += h[i] * (x_ext - mu * sum(L[i:j]))
		# C_hat_lim2 is never used since y-d is never greater than the y range;
		# however, I'm leaving it here so it can be plotted.
		if j > 1:
			C_hat_lim2[j, :] = h[j] * x_ext + C[j-1, find_nearest(x, S_star[j-1], True)]
		else:
			C_hat_lim2[j, :] = h[j] * x_ext

		# Calculate C.
		for y in x:

			# Get index of closest element of x to y.
			the_x = find_nearest(x, y, True)

			# Loop through demands and calculate expected cost.
			# This method uses the following result (see Problem X.X):
			# TODO: supply problem number
			# lim_{y -> -infty} C_j(y) = -(p + h'_{j+1})(y - sum_{i=1}^j E[D_i])
			# lim_{y -> +infty} C_j(y) = h_j(y - E[D_j]) + C_{j-1}(S*_{j-1})
			# TODO: this can probably be vectorized and be much faster

			the_cost = np.zeros(d.size)

			for d_ind in range(d.size):
				# Calculate y - d.
				y_minus_d = y - (mu * L[j] + d[d_ind] * sigma * np.sqrt(L[j]))

				# Calculate cost -- use approximate value of C-hat if y-d is
				# outside of x-range.
				if y_minus_d < np.min(x):
					the_cost[d_ind] = \
						C_hat_lim1[j, find_nearest(x_ext, y_minus_d, True)]
				elif y_minus_d > np.max(x): # THIS SHOULD NEVER HAPPEN
					the_cost[d_ind] = \
						C_hat_lim2[j, find_nearest(x_ext, y_minus_d, True)]
				else:
					the_cost[d_ind] = \
						C_hat[j, find_nearest(x, y_minus_d, True)]

			# Calculate expected cost.
			C[j, the_x] = np.dot(fd, the_cost)

		# Did user specify S?
		if S is None:
			# No -- determine S*.
			opt_S_index = np.argmin(C[j, :])
			S_star[j] = x[opt_S_index]
		else:
			# Yes -- use specified S.
			S_star[j] = S[j]
		C_star[j] = C[j, find_nearest(x, S_star[j], True)]

		# Calculate C_bar
		C_bar[j, :] = C[j, find_nearest(x, np.minimum(S_star[j], x), True)]

	# Plot functions.
	if plots:
		fig, axes = plt.subplots(2, 2)
		# C_hat.
		axes[0, 0].plot(x, np.transpose(C_hat[1:N+1, :]))
		axes[0, 0].set_title('C-hat')
		axes[0, 0].legend(list(map(str, range(1, N+1))))
		k = N
		axes[0, 0].plot(x, C_hat_lim1[k, find_nearest(x_ext, x)], ':')
		axes[0, 0].plot(x, C_hat_lim2[k, find_nearest(x_ext, x)], ':')
		# C_bar.
		axes[0, 1].plot(x, np.transpose(C_bar))
		axes[0, 1].set_title('C-bar')
		axes[0, 1].legend(list(map(str, range(N+1))))
		# C.
		axes[1, 0].plot(x, np.transpose(C[1:N+1, :]))
		axes[1, 0].set_title('C')
		axes[1, 0].legend(list(map(str, range(1, N+1))))

		plt.show()

	return S_star, C_star[N]


#S_star, C_star = optimize_base_stock_levels(instance_2_stage, plots=False)
#print('S_star = {}, C_star = {}'.format(S_star, C_star))


# TODO: write unit tests