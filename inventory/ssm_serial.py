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

from tests.instances_ssm_serial import *


def get_indices(array, values):
	"""Determine smallest entries in array that are larger than each of the
	entries in values and return their indices. Neither array needs to be sorted.
	array and values need not be the same length.

	Parameters
	----------
	array : ndarray
		The array to search for values in
	values : ndarray
		The array whose values should be searched for in the other array

	Returns
	-------
	ind : ndarray
		Array of indices.
	"""
	values = np.array(values, ndmin=1, copy=False)
	ind = np.zeros(values.shape)
	for v in range(values.size):
		ind[v] = np.argmax(array > values[v])
	# TODO: handle vector of values without looping?
	# TODO: speed this up if array is sorted?

	return ind


def optimize_base_stock_levels(network, x=None, S=None, plots=False):
	"""Chen-Zheng (1994) algorithm for stochastic serial systems under
	stochastic service model (SSM), as described in Snyder and Shen (2019).

	Stages are assumed to be indexed N, ..., 1. Demands are assumed to be
	normally distributed.

	Parameters
	----------
	network : graph
		NetworkX directed graph representing the multi-echelon serial network.
	x : ndarray, optional
		x-array to use for truncation and discretization, or None (the default)
		to determine automatically
	S : ndarray, optional
		array of echelon base-stock levels to evaluate. If present, no
		optimization is performed and the function just returns the cost
		under base-stock levels S; to optimize instead, set S=None (the default)
	plots : Boolean
		True for the function to generate plots of C(.) functions, False o/w

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
	p = network.nodes[1]['stockout_cost']

	# Determine x array (truncated and discretized)
	# TODO: handle this better
	if x is None:
		x_num = 1000
		x_lo = -4 * sigma * np.sqrt(sum(L))
		x_hi = mu * sum(L) + 8 * sigma * np.sqrt(sum(L))
		x_delta = (x_hi - x_lo) / x_num
		# Ensure x >= largest echelon BS level, if provided.
		if S is not None:
			x_hi = max(x_hi, np.max(S))
		# Build x range.
		x = np.arange(x_lo, x_hi + x_delta, x_delta)
	else:
		x_delta = x[1] - x[0]

	# Standard normal demand array (truncated and discretized).
	# (Use mu + d * sigma to get distribution-specific demands).
	d_lo = -4
	d_hi = 4
	d_delta = (d_hi - d_lo) / 100
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
	C_bar = np.zeros((N+1, len(x)))

	# Initialize arrays containing approximation for C (mainly for deubugging).
	C_hat_lim1 = np.zeros((N+1, len(x_ext)))
	C_hat_lim2 = np.zeros((N+1, len(x_ext)))

	# Calculate C_bar[0, :].
	C_bar[0, :] = (p + sum(h)) * np.maximum(-x, 0)

	# Loop through stages.
	for j in range(1, N+1):

		print(str(j))

		# Calculate C_hat.
		C_hat[j, :] = h[j] * x + C_bar[j-1, :]

		# Calculate approximate C-hat function.
		C_hat_lim1[j, :] = -(p + sum(h)) * (x_ext - mu * sum(L[1:j]))
		for i in range(1, j+1):
			C_hat_lim1[j, :] += h[i] * (x_ext - mu * sum(L[i:j]))
		# C_hat_lim2 is never used since y-d is never greater than the y range;
		# however, I'm leaving it here so it can be plotted.
		if j > 1:
			C_hat_lim2[j, :] = h[j] * x_ext + C[j-1, get_indices(x, S_star[j-1])]
		else:
			C_hat_lim2[j, :] = h[j] * x_ext

	pass

optimize_base_stock_levels(instance_2_stage)