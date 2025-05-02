# ===============================================================================
# stockpyl - ssm_serial Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_ssm_serial| module contains code to solve serial systems under the stochastic service
model (SSM), either exactly, using the :func:`~stockpyl.ssm_serial.optimize_base_stock_levels` function
(which implements the algorithm by Chen and Zheng (1994), which in turn is
based on the algorithm by Clark and Scarf (1960)), or approximately, using the :func:`~stockpyl.ssm_serial.newsvendor_heuristic` 
function (which implements the newsvendor heuristic by Shang and Song (2003)).

.. note:: |node_stage|

.. note:: |fosct_notation|


.. seealso::

	For an overview of multi-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for multi-echelon inventory optimization<tutorial_meio_page>`.


References
----------
F. Chen and Y. S. Zheng. Lower bounds for multiechelon stochastic inventory systems. *Management Science*, 40(11):1426–1443, 1994.

A. J. Clark and H. Scarf. Optimal policies for a multiechelon inventory problem. *Management Science*, 6(4):475–490, 1960.

K. H. Shang and J.-S. Song. Newsvendor bounds and heuristic for optimal policies in serial supply chains. *Management Science*, 49(5):618-638, 2003.


API Reference
-------------

"""

import numpy as np
from scipy import stats
#import math
import matplotlib.pyplot as plt
import copy

from stockpyl.demand_source import DemandSource
from stockpyl.helpers import round_dict_values
from stockpyl.newsvendor import *
from stockpyl.supply_chain_network import serial_system


### OPTIMIZATION ###

def optimize_base_stock_levels(num_nodes=None, node_order_in_system=None, node_order_in_lists=None,
								echelon_holding_cost=None, lead_time=None, stockout_cost=None, 
								demand_mean=None, demand_standard_deviation=None,
								demand_source=None, network=None,
								S=None, plots=False, x=None,
								x_num=1000, d_num=100,
								ltd_lower_tail_prob=1-stats.norm.cdf(4),
								ltd_upper_tail_prob=1-stats.norm.cdf(4),
								sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
								sum_ltd_upper_tail_prob=1-stats.norm.cdf(4)):
	"""Chen-Zheng (1994) algorithm for stochastic serial systems under the stochastic service model (SSM), which in 
	turn is based on Clark and Scarf (1960). 

	Problem instance may either be provided in the individual parameters ``num_nodes``, ..., ``demand_source``,
	or as a |class_network| in the ``network`` parameter.

	By default, the nodes in the system are assumed to be indexed
	``num_nodes``, ..., 1, with node 1 at the downstream end, but this can be changed by
	providing either the ``node_order_in_system`` or ``network`` parameter.

	The node-specific parameters (``echelon_holding_cost``, ``lead_time``)
	must be either a dict, a list, or a singleton, with the following requirements:
	
	* If the parameter is a dict, then the keys must contain the node indices and the values
	  must contain the corresponding attribute values. If a given node index is contained in
	  ``node_order_in_system`` (or in 1, ..., ``num_nodes``, if ``node_order_in_system`` is not
	  provided) but is not a key in the dict, the attribute value is set to ``None`` for that node.
	* If the parameter is a singleton, then the attribute is set to that value for all nodes.
	* If the parameter is a list and ``node_order_in_lists`` is provided, ``node_order_in_lists`` 
	  must contain the same indices as ``node_order_in_system`` (if it is provided) or 1, ..., ``num_nodes``
	  (if it is not), otherwise a ``ValueError`` is raised. The values in the list are assumed
	  to correpond to the node indices in the order they are specified in ``node_order_in_lists``.
	  That is, the value in slot ``k`` in the parameter list is assigned to the node with index
	  ``node_order_in_lists[k]``. 
	* If the parameter is a list and ``node_order_in_lists`` is not provided, the values
	  in the list are assumed to correspond to nodes in the same order as ``node_order_in_system``
	  (or in ``num_nodes``, ..., 1, if ``node_order_in_system`` is not provided).
	
	(These are the same requirements as in :func:`stockpyl.supply_chain_network.serial_system`, except
	that the default node numbering is ``num_nodes``, ..., 1 here.)

	Either ``demand_mean`` and ``demand_standard_deviation`` must be
	provided (in which case the demand will be assumed to be normally distributed),
	or ``demand_source`` must be provided, or ``network`` must be provided.

	If ``demand_source`` is provided and has all-integer support, this is accounted for
	in the discretization, and the solutions returned will also be integer.

	Parameters
	----------
	num_nodes : int, optional
		Number of nodes in serial system. [:math:`N`]
	node_order_in_system : list, optional
		List of node indices in the order that they appear in the serial system,
		with upstream-most node listed first. If omitted, the system will be indexed
		``num_nodes``, ..., 1. Ignored if ``network`` is provided.
	node_order_in_lists : list, optional
		List of node indices in the order in which the nodes are listed in any
		attributes that are lists. (``node_order_in_lists[k]`` is the index of the ``k`` th node.)
		Ignored if ``network`` is provided.
	echelon_holding_cost : float, list, or dict, optional
		Echelon holding cost at each node. [:math:`h`]
	lead_time : float, list, or dict, optional
		(Shipment) lead time at each node. [:math:`L`]
	stockout_cost : float, optional
		Stockout cost per item per unit time at node 1. [:math:`p`]
	demand_mean : float, optional
		Mean demand per unit time at node 1. Ignored if ``demand_source`` is not ``None``. [:math:`\\mu`]
	demand_standard_deviation : float, optional
		Standard deviation of demand per unit time at node 1. Ignored if ``demand_source`` is not ``None``. [:math:`\\sigma`]
	demand_source : |class_demand_source|, optional
		A |class_demand_source| object describing the demand distribution. Required if
		``demand_mean`` and ``demand_standard_deviation`` are ``None``.
	network : |class_network|, optional
		A |class_network| object that provides all of the necessary data. If provided,
		``num_nodes``, ..., ``demand_source`` are ignored.
	S : dict, optional
		Dict of echelon base-stock levels to evaluate. If present, no
		optimization is performed and the function just returns the cost
		under base-stock levels ``S``; to optimize instead, set ``S`` = ``None``
		(the default). [:math:`S`]
	plots : bool, optional
		``True`` for the function to generate plots of :math:`C(\\cdot)` functions,
		``False`` otherwise.
	x : ndarray, optional
		x-array to use for truncation and discretization, or ``None`` (the default)
		to determine automatically.
	x_num : int, optional
		Number of discretization intervals to use for ``x`` range. Ignored if
		``x`` is provided. Ignored if a discrete distribution is provided in
		``demand_source`` (since in that case ``x`` range is discretized to integers).
	d_num : int, optional
		Number of discretization intervals to use for ``d`` range. 
		Ignored if a discrete distribution is provided in
		``demand_source`` (since in that case ``d`` range is discretized to integers).
	ltd_lower_tail_prob : float, optional
		Lower tail probability to use when truncating lead-time demand
		distribution.
	ltd_upper_tail_prob : float, optional
		Upper tail probability to use when truncating lead-time demand
		distribution.
	sum_ltd_lower_tail_prob : float, optional
		Lower tail probability to use when truncating "sum-of-lead-times"
		demand distribution.
	sum_ltd_upper_tail_prob : float, optional
		Upper tail probability to use when truncating "sum-of-lead-times"
		demand distribution.

	Returns
	-------
	S_star : dict
		Dict of optimal echelon base-stock levels. [:math:`S^*`]
	C_star : float
		Optimal expected cost. [:math:`C^*`]

	Raises
	------
	ValueError
		If ``network`` is ``None`` and ``num_nodes``, ..., ``stockout_cost`` are ``None``.
	ValueError
		If ``network``, ``node_order_in_system``, and ``num_nodes`` are all ``None``.
	ValueError
		If ``stockout_cost`` is ``None`` or if ``echelon_holding_cost`` or
		``lead_time`` is ``None`` for any node.
	ValueError
		If ``demand_mean`` or ``demand_standard_deviation`` is ``None`` and 
		``demand_source`` is ``None``.
	ValueError
		If ``stockout_cost`` < 0 or if ``lead_time`` < 0 for any node.
		

	**Equations Used**: 

	.. math::

		\\underline{g}_0(x) = (p+h'_1)x^-
	
	For :math:`j=1,\\ldots,N`:

	.. math::

		\\begin{gather*}
		\\hat{g}_j(x) = h_jx + \\underline{g}_{j-1}(x) \\\\
		g_j(y) = E\left[\hat{g}_j(y-D_j)\\right] \\\\
		S^*_j = \\mathrm{argmin} \\{g_j(y)\\} \\\\
		\\underline{g}_j(x) = g_j(\\min\\{S_j^*,x\\})
		\\end{gather*}


	The range of :math:`x` values considered is discretized and truncated. 
	The :math:`\\hat{g}_j(x)` functions sometimes need to be evaluated for :math:`x`
	values outside this range. For those values, the following limits provide linear 
	approximations that are used instead (see Problem 6.13):

	.. math::

		\\begin{gather*}
		\\lim_{x \\rightarrow -\\infty} \\hat{g}_j(x) = \\sum_{i=1}^j h_i\\left(x - \\sum_{k=i}^{j-1} E[D_k]\\right) - (p+h'_1)\\left(x - \\sum_{k=1}^{j-1} E[D_k]\\right) \\\\
		\\lim_{x \\rightarrow +\\infty} \\hat{g}_j(x) = \\begin{cases} h_jx + g_{j-1}(S^*_{j-1}), & \\text{if $j>1$} \\\\
															h_jx, & \\text{if $j=1$} \\end{cases}
		\\end{gather*}


	References
	----------
	F. Chen and Y. S. Zheng. Lower bounds for multiechelon stochastic inventory systems. *Management Science*, 40(11):1426–1443, 1994.

	A. J. Clark and H. Scarf. Optimal policies for a multiechelon inventory problem. *Management Science*, 6(4):475–490, 1960.


	**Example** (Example 6.1):

	.. testsetup:: *

		from stockpyl.ssm_serial import *

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> S_star, C_star = optimize_base_stock_levels(
		... 	num_nodes=3, 
		... 	echelon_holding_cost=[2, 2, 3], 
		... 	lead_time=[2, 1, 1], 
		... 	stockout_cost=37.12, 
		... 	demand_mean=5, 
		... 	demand_standard_deviation=1
		...	)
		>>> S_star
		{3: 22.700237234889784, 2: 12.012332294949644, 1: 6.5144388073261155}
		>>> C_star
		47.668653127136345
	"""

	# Validate data and re-index to N, ..., 1.
	old_to_new_dict, num_nodes, echelon_holding_cost_dict, lead_time_dict, stockout_cost, demand_source \
		= _preprocess_parameters(num_nodes, node_order_in_system, node_order_in_lists, echelon_holding_cost,
		lead_time, stockout_cost, demand_mean, demand_standard_deviation, demand_source, network)

	# Get shortcuts to some parameters (for convenience).
	N = num_nodes
	mu = demand_source.demand_distribution.mean()
	L = [0] + [lead_time_dict[j] for j in range(1, N+1)]
	h = [0] + [echelon_holding_cost_dict[j] for j in range(1, N+1)]
	p = stockout_cost

	# Build "sum of lead-time demand" distribution (LTD distribution in
	# which L = sum of all lead times)
	sum_ltd_dist = demand_source.lead_time_demand_distribution(sum(L))

	# Get truncation bounds for sum-of-lead-time demand distribution.
	# If support is finite, use support; otherwise, use F^{-1}(.).
	if sum_ltd_dist.a == float("-inf"):
		sum_ltd_lo = sum_ltd_dist.ppf(sum_ltd_lower_tail_prob)
	else:
		# interval(1) gives lo and hi end of interval that contains 100% of
		# probability area, i.e., 0th and 100th percentile, which for uniform
		# distribution is the entire support.
		sum_ltd_lo = sum_ltd_dist.interval(1)[0]
	if sum_ltd_dist.b == float("inf"):
		sum_ltd_hi = sum_ltd_dist.ppf(1 - sum_ltd_upper_tail_prob)
	else:
		sum_ltd_hi = sum_ltd_dist.interval(1)[1]

	# Is demand distribution discrete (integer)?
	if demand_source.type in ('P', 'UD'):
		discrete_distribution = True
	elif demand_source.type == 'CD' and np.all([is_integer(d) for d in demand_source.demand_list]):
		discrete_distribution = True
	else:
		discrete_distribution = False

	# Determine x (inventory level) array (truncated and discretized).
	# If demand distribution is discrete, discretize to integers; otherwise,
	# use x_num to determine granularity.
	if x is None:
		# x-range = [sum_ltd_lo-sum_ltd_mean, sum_ltd_hi].
		x_lo = sum_ltd_lo - sum_ltd_hi # originally used sum_ltd_dist.mean() here but I think sum_ltd_hi is more accurate
		x_hi = sum_ltd_hi
		# Ensure x >= largest echelon BS level, if provided.
		if S is not None:
			x_hi = max(x_hi, max(S.values()))
		# Build x range. Is demand distribution discrete?
		if discrete_distribution:
			# x_lo and h_hi should already be integers, but cast them anyway.
			x_lo    = round(x_lo)
			x_delta = int(1)
			x_num   = round(x_hi-x_lo)
		elif x_num and x_hi > x_lo:
			x_lo    = float(x_lo)
			x_delta = float((x_hi-x_lo)/x_num)
		else:
			x_lo    = float((x_lo+x_hi)*0.5)
			x_delta = float(1)
			x_num   = int()
		x_hi = x_num*x_delta+x_lo
		x = np.array([x_ind*x_delta+x_lo for x_ind in range(x_num+1)])
	elif x.size > 1:
		x_lo    = np.min(x)
		x_hi    = np.max(x)
		x_delta = abs(x[1]-x[0])
		x_num   = int((x_hi-x_lo)/x_delta)
	else:
		x_lo    = x[0]
		x_hi    = x_lo
		x_delta = int(1)
		x_num   = int()

	# Extended x array (used for approximate C-hat function).
	x_ext_num = math.ceil(sum_ltd_hi/x_delta)
	# x_ext_lo = np.min(x) - (mu * sum(L) +
	# 						d.max() * sigma * np.sqrt(sum(L)))
	# x_ext_hi = np.max(x) + (mu * sum(L) +
	# 						d.max() * sigma * np.sqrt(sum(L)))
	x_ext = np.array([x_ext_ind*x_delta+x_lo for x_ext_ind in range(-x_ext_num, x_num+x_ext_num+1)])

	# Index dictionaries to find nearest entry for matching value faster
	index_x     = {x    [ind]: ind for ind in range(x    .size)}
	index_x_ext = {x_ext[ind]: ind for ind in range(x_ext.size)}

	# Initialize arrays. (0th element is ignored since we are assuming stages
	# are numbered starting at 1. C_bar is an exception since C_bar[0] is
	# meaningful.)
	C_hat = np.zeros((N+1, len(x)))
	C = np.zeros((N+1, len(x)))
	S_star = {}
	C_star = np.zeros(N+1)
	C_bar = np.zeros((N+1, len(x)))

	# Initialize arrays containing approximation for C (mainly for debugging).
	C_hat_lim1 = np.zeros((N+1, len(x_ext)))
	C_hat_lim2 = np.zeros((N+1, len(x_ext)))

	# Calculate C_bar[0, :].
	C_bar[0, :] = (p + sum(h)) * np.maximum(-x, 0)

	# Loop through stages.
	for j in range(1, N+1):

		# Calculate C_hat.
		C_hat[j, :] = h[j] * x + C_bar[j-1, :]

		# Calculate approximate C-hat function.
		C_hat_lim1[j, :] = -(p + sum(h)) * (x_ext - mu * sum(L[1:j]))
		for i in range(1, j+1):
			C_hat_lim1[j, :] += h[i] * (x_ext - mu * sum(L[i:j]))
		# C_hat_lim2 is never used since y-d is never greater than the y range;
		# however, it is here so it can be plotted.
		if j > 1:
			C_hat_lim2[j, :] = h[j] * x_ext + C[j-1, find_nearest(x, S_star[j-1], True, index_x)]
		else:
			C_hat_lim2[j, :] = h[j] * x_ext

		# Get lead-time demand distribution.
		ltd_dist = demand_source.lead_time_demand_distribution(L[j])

		# Get truncation bounds for lead-time demand distribution.
		# If support is finite, use support; otherwise, use F^{-1}(.).
		if ltd_dist.a == float("-inf"):
			d_lo = max(ltd_dist.ppf(ltd_lower_tail_prob), float())
		else:
			d_lo = max(ltd_dist.interval(1)[0], float())
		if ltd_dist.b == float("inf"):
			d_hi = max(ltd_dist.ppf(float(1)-ltd_upper_tail_prob), d_lo)
		else:
			d_hi = max(ltd_dist.interval(1)[1], d_lo)

		# Determine d (lead-time demand) array (truncated and discretized).
		if discrete_distribution:
			d_lo    = round(d_lo)
			d_delta = int(1)
			num     = round(d_hi-d_lo)
		elif d_num and d_hi > d_lo:
			d_lo    = float(d_lo)
			d_delta = float((d_hi-d_lo)/d_num)
			num     = d_num
		else:
			d_lo    = float((d_lo+d_hi)*0.5)
			d_delta = float(1)
			num     = int()
		d_hi = num*d_delta+d_lo
		d = np.array([d_ind*d_delta+d_lo for d_ind in range(num+1) if (ltd_dist.cdf((d_ind+0.5)*d_delta+d_lo) if d_ind != num else float(1)) > (ltd_dist.cdf((d_ind-0.5)*d_delta+d_lo) if d_ind else float())])

		# Calculate discretized cdf array.
		fd = np.array([(ltd_dist.cdf(d[ind]+d_delta*float(0.5)) if ind+1 != d.size else float(1))-(ltd_dist.cdf(d[ind]-d_delta*float(0.5)) if ind else float()) for ind in range(d.size)])
		#fd = ltd_dist.cdf(d+d_delta/2) - ltd_dist.cdf(d-d_delta/2)

		# Calculate C.
		for y in x:

			# Get index of closest element of x to y.
			the_x = index_x[y]

			# Loop through demands and calculate expected cost.
			# This method uses the following result (see Problem 6.13):
			# lim_{y -> -infty} C_j(y) = -(p + h'_{j+1})(y - sum_{i=1}^j E[D_i])
			# lim_{y -> +infty} C_j(y) = h_j(y - E[D_j]) + C_{j-1}(S*_{j-1})

			the_cost = np.zeros(d.size)

			for d_ind in range(d.size):
				# Calculate y - d.
				y_minus_d = y - d[d_ind]

				# Calculate cost -- use approximate value of C-hat if y-d is
				# outside of x-range.
				if y_minus_d < x_lo:
					the_cost[d_ind] = \
						C_hat_lim1[j, find_nearest(x_ext, y_minus_d, True, index_x_ext)]
				elif y_minus_d > x_hi: # THIS SHOULD NEVER HAPPEN
					print('WARNING: y > x + d', flush=True)
					the_cost[d_ind] = \
						C_hat_lim2[j, find_nearest(x_ext, y_minus_d, True, index_x_ext)]
				else:
					the_cost[d_ind] = \
						C_hat[j, find_nearest(x, y_minus_d, True, index_x)]

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
		C_star[j] = C[j, find_nearest(x, S_star[j], True, index_x)]

		# Calculate C_bar
		C_bar[j, :] = C[j, find_nearest(x, np.minimum(S_star[j], x), True, index_x)]

	# Plot functions.
	if plots:
		fig, axes = plt.subplots(2, 2)
		# C_hat.
		axes[0, 0].plot(x, np.transpose(C_hat[1:N+1, :]))
		axes[0, 0].set_title('C-hat')
		axes[0, 0].legend(list(map(str, range(1, N+1))))
		k = N
		axes[0, 0].plot(x, C_hat_lim1[k, find_nearest(x_ext, x, True, index_x_ext)], ':')
		axes[0, 0].plot(x, C_hat_lim2[k, find_nearest(x_ext, x, True, index_x_ext)], ':')
		# C_bar.
		axes[0, 1].plot(x, np.transpose(C_bar))
		axes[0, 1].set_title('C-bar')
		axes[0, 1].legend(list(map(str, range(N+1))))
		# C.
		axes[1, 0].plot(x, np.transpose(C[1:N+1, :]))
		axes[1, 0].set_title('C')
		axes[1, 0].legend(list(map(str, range(1, N+1))))

		plt.show()

	# Revert to original node indexing.
	temp_S_star = {n_ind: S_star[old_to_new_dict[n_ind]] for n_ind in old_to_new_dict.keys()}
	S_star = temp_S_star

	return S_star, C_star[N]	


def newsvendor_heuristic(num_nodes=None, node_order_in_system=None, node_order_in_lists=None,
								echelon_holding_cost=None, lead_time=None,
								stockout_cost=None, demand_mean=None, demand_standard_deviation=None,
								demand_source=None, network=None, weight=0.5, round_type=None):
	"""Shang-Song (2003) heuristic for stochastic serial systems under
	stochastic service model (SSM), as described in |fosct|.

	Problem instance may either be provided in the individual parameters ``num_nodes``, ..., ``demand_source``,
	or as a |class_network| in the ``network`` parameter.

	By default, the nodes in the system are assumed to be indexed
	``num_nodes``, ..., 1, with node 1 at the downstream end, but this can be changed by
	providing either the ``node_order_in_system`` or ``network`` parameter.

	The node-specific parameters (``echelon_holding_cost``, ``lead_time``)
	must be either a dict, a list, or a singleton, with the following requirements:
	
	* If the parameter is a dict, then the keys must contain the node indices and the values
	  must contain the corresponding attribute values. If a given node index is contained in
	  ``node_order_in_system`` (or in 1, ..., ``num_nodes``, if ``node_order_in_system`` is not
	  provided) but is not a key in the dict, the attribute value is set to ``None`` for that node.
	* If the parameter is a singleton, then the attribute is set to that value for all nodes.
	* If the parameter is a list and ``node_order_in_lists`` is provided, ``node_order_in_lists`` 
	  must contain the same indices as ``node_order_in_system`` (if it is provided) or 1, ..., ``num_nodes``
	  (if it is not), otherwise a ``ValueError`` is raised. The values in the list are assumed
	  to correpond to the node indices in the order they are specified in ``node_order_in_lists``.
	  That is, the value in slot ``k`` in the parameter list is assigned to the node with index
	  ``node_order_in_lists[k]``. 
	* If the parameter is a list and ``node_order_in_lists`` is not provided, the values
	  in the list are assumed to correspond to nodes in the same order as ``node_order_in_system``
	  (or in  ``num_nodes``, ..., 1, if ``node_order_in_system`` is not provided).
	
	(These are the same requirements as in :func:`stockpyl.supply_chain_network.serial_system`, except
	that the default node numbering is  ``num_nodes``, ..., 1 here.)

	Either ``demand_mean`` and ``demand_standard_deviation`` must be
	provided (in which case the demand will be assumed to be normally distributed),
	or ``demand_source`` must be provided, or ``network`` must be provided.

	Rounding is discussed in Shang and Song (2003), p. 625.


	Parameters
	----------
	num_nodes : int, optional
		Number of nodes in serial system. [:math:`N`]
	node_order_in_system : list, optional
		List of node indices in the order that they appear in the serial system,
		with upstream-most node listed first. If omitted, the system will be indexed
		``num_nodes``, ..., 1. Ignored if ``network`` is provided.
	node_order_in_lists : list, optional
		List of node indices in the order in which the nodes are listed in any
		attributes that are lists. (``node_order_in_lists[k]`` is the index of the ``k`` th node.)
		Ignored if ``network`` is provided.
	echelon_holding_cost : float, list, or dict, optional
		Echelon holding cost at each node. [:math:`h`]
	lead_time : float, list, or dict, optional
		(Shipment) lead time at each node. [:math:`L`]
	stockout_cost : float, optional
		Stockout cost per item per unit time at node 1. [:math:`p`]
	demand_mean : float, optional
		Mean demand per unit time at node 1. Ignored if ``demand_source`` is not ``None``. [:math:`\\mu`]
	demand_standard_deviation : float, optional
		Standard deviation of demand per unit time at node 1. Ignored if ``demand_source`` is not ``None``. [:math:`\\mu`]
	demand_source : |class_demand_source|, optional
		A |class_demand_source| object describing the demand distribution. Required if
		``demand_mean`` and ``demand_standard_deviation`` are ``None``.
	network : |class_network|, optional
		A |class_network| object that provides all of the necessary data. If provided,
		``num_nodes``, ..., ``demand_source`` are ignored.
	weight : float, optional
		Weight to use in weighted sum of lower- and upper-bound base-stock levels. 
	round_type : string, optional
		Set to 'up' to always round base-stock levels up to next larger integer, 'down' to 
		always round down, 'nearest' to round to nearest integer, or ``None`` to not round at all.

	Returns
	-------
	S_heur : dict
		Dict of heuristic echelon base-stock levels. [:math:`\\tilde{S}`]

	Raises
	------
	ValueError
		If ``network`` is ``None`` and ``num_nodes``, ..., ``stockout_cost`` are ``None``.
	ValueError
		If ``stockout_cost`` is ``None`` or if ``echelon_holding_cost`` or
		``lead_time`` is ``None`` for any node.
	ValueError
		If ``demand_mean`` or ``demand_standard_deviation`` is ``None`` and 
		``demand_source`` is ``None``.
	ValueError
		If ``stockout_cost`` < 0 or if ``lead_time`` < 0 for any node.
		

	References
	----------
	K. H. Shang and J.-S. Song. Newsvendor bounds and heuristic for optimal policies in serial supply chains. *Management Science*, 49(5):618-638, 2003.
	

	**Equation Used** (equation (6.32)): 

	.. math::

		\\tilde{S}_j = \\texttt{weight}\\tilde{F}_j^{-1}\\left(\\frac{p+\\sum_{i=j+1}^N h_i}{p+\\sum_{i=j}^N h_i}\\right) + (1-\\texttt{weight})\\tilde{F}_j^{-1}\\left(\\frac{p+\\sum_{i=j+1}^N h_i}{p+\\sum_{i=1}^N h_i}\\right)
	
	for :math:`j=1,\\ldots,N`.


	**Example** (Example 6.1):

	.. testsetup:: *

		from stockpyl.ssm_serial import *

	.. doctest::

		>>> S_heur = newsvendor_heuristic(
		...		num_nodes=3, 
		...		echelon_holding_cost=[2, 2, 3], 
		...		lead_time=[2, 1, 1], 
		...		stockout_cost=37.12, 
		...		demand_mean=5, 
		...		demand_standard_deviation=1
		...		)
		>>> S_heur # (optimal is {3: 22.700237234889784, 2: 12.012332294949644, 1: 6.5144388073261155})
		{3: 22.634032391786285, 2: 12.027434723327854, 1: 6.490880975286938}
		>>> # Calculate expected cost of heuristic solution. (optimal is 47.668653127136345)
		>>> expected_cost(
		...		echelon_S=S_heur,
		...		num_nodes=3, 
		...		echelon_holding_cost=[2, 2, 3], 
		...		lead_time=[2, 1, 1], 
		...		stockout_cost=37.12, 
		...		demand_mean=5, 
		...		demand_standard_deviation=1
		...		)
		47.65465421619295
	"""

	# Validate data and re-index to N, ..., 1.
	old_to_new_dict, num_nodes, echelon_holding_cost_dict, lead_time_dict, stockout_cost, demand_source \
		= _preprocess_parameters(num_nodes, node_order_in_system, node_order_in_lists, echelon_holding_cost,
		lead_time, stockout_cost, demand_mean, demand_standard_deviation, demand_source, network)

	# Get shortcuts to some parameters (for convenience).
	N = num_nodes
	indices = list(range(1, num_nodes+1))
	# demand_source is filled by _preprocess_parameters() if not specified as parameters.
	mu = demand_source.demand_distribution.mean()
	sigma = demand_source.demand_distribution.std()
	L = [0] + [lead_time_dict[j] for j in range(1, N+1)]
	h = [0] + [echelon_holding_cost_dict[j] for j in range(1, N+1)]
	p = stockout_cost

	# Build "sum of lead-time demand" distributions (LTD distribution in
	# which L = sum of lead times of stages 1, ..., j) for j = 1, ..., N.
	sum_ltd_dist = {}
	for j in indices:
		sum_ltd_dist[j] = demand_source.lead_time_demand_distribution(float(np.sum(L[1:(j+1)])))
	
	# Solve newsvendor problems.
	S_heur = {}
	for j in indices:
		# Calculate effective holding and stockout costs.
		p_eff = p + np.sum(h[j+1:])
		h_eff_u = h[j]
		h_eff_l = np.sum(h[1:j+1])
		if demand_source.type == 'N':
			# Normal.
			# Calculate parameters of LTD distribution.
			mu_ltd = mu * np.sum(L[1:j+1])
			sigma_ltd = sigma * math.sqrt(np.sum(L[1:j+1]))
			# Calculate newsvendor quantities.
			S_u, _ = newsvendor_normal(h_eff_u, p_eff, mu_ltd, sigma_ltd)
			S_l, _ = newsvendor_normal(h_eff_l, p_eff, mu_ltd, sigma_ltd)
		elif demand_source.type == 'P':
			# Poisson.
			# Calculate parameters of LTD distribution.
			mu_ltd = mu * np.sum(L[1:j+1])
			# Calculate newsvendor quantities.
			S_u, _ = newsvendor_poisson(h_eff_u, p_eff, mu_ltd)
			S_l, _ = newsvendor_poisson(h_eff_l, p_eff, mu_ltd)
		elif demand_source.type == 'UC':
			# Uniform continuous.
			# Build LTD distribution.
			ltd_distrib = demand_source.lead_time_demand_distribution(float(np.sum(L[1:(j+1)])))
			# Calculate newsvendor quantities.
			S_u, _ = newsvendor_continuous(h_eff_u, stockout_cost, ltd_distrib)
			S_l, _ = newsvendor_continuous(h_eff_l, stockout_cost, ltd_distrib)
		elif demand_source.type in ('UD', 'CD'):
			# Discrete.
			# Build LTD distribution.
			ltd_distrib = demand_source.lead_time_demand_distribution(float(np.sum(L[1:(j+1)])))
			# Calculate newsvendor quantities.
			S_u, _ = newsvendor_discrete(h_eff_u, stockout_cost, ltd_distrib)
			S_l, _ = newsvendor_discrete(h_eff_l, stockout_cost, ltd_distrib)
		else:
			raise ValueError(f"demand_source.type '{demand_source.type}' is not supported")
		
		# Take weighted average.
		S_heur[j] = weight * S_l + (1 - weight) * S_u

	# Revert to original node indexing.
	temp_S_heur = {n_ind: S_heur[old_to_new_dict[n_ind]] for n_ind in old_to_new_dict.keys()}
	S_heur = temp_S_heur

	return round_dict_values(S_heur, round_type)


### COST-RELATED FUNCTIONS ###

def expected_cost(echelon_S, 
					num_nodes=None, echelon_holding_cost=None, lead_time=None,
					stockout_cost=None, demand_mean=None, demand_standard_deviation=None,
					demand_source=None, network=None,
					x_num=1000, d_num=100,
					ltd_lower_tail_prob=1-stats.norm.cdf(4),
					ltd_upper_tail_prob=1-stats.norm.cdf(4),
					sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
					sum_ltd_upper_tail_prob=1-stats.norm.cdf(8)):
	"""Calculate expected cost of given solution.

	This is a wrapper function that calls :func:`~stockpyl.ssm_serial.optimize_base_stock_levels`
	without doing any optimization.

	For parameter descriptions, see docstring for :func:`~stockpyl.ssm_serial.optimize_base_stock_levels`.

	Parameters
	----------
	echelon_S : dict
		Dict of echelon base-stock levels to be evaluated.
	other parameters :
		See :func:`~stockpyl.ssm_serial.optimize_base_stock_levels`.

	Returns
	-------
	cost : float
		Expected cost of system.


	Raises
	------
	ValueError
		If ``stockout_cost`` is ``None`` or if ``echelon_S``, ``echelon_holding_cost``,
		or ``lead_time`` is ``None`` for any node.
	ValueError
		If ``demand_mean`` or ``demand_standard_deviation`` is ``None`` and 
		``demand_source`` is ``None``.
	ValueError
		If ``stockout_cost`` < 0 or if ``lead_time`` < 0 for any node.
		

	**Equations Used**: See :func:`optimize_base_stock_levels`.


	**Example** (Example 6.1):

	.. testsetup:: *

		from stockpyl.ssm_serial import *

	.. doctest::

		>>> expected_cost(
		...		echelon_S={1: 6.5144388073261155, 2: 12.012332294949644, 3: 22.700237234889784},
		... 	num_nodes=3, 
		... 	echelon_holding_cost=[2, 2, 3], 
		... 	lead_time=[2, 1, 1], 
		... 	stockout_cost=37.12, 
		... 	demand_mean=5, 
		... 	demand_standard_deviation=1
		...	)
		47.641099926743415
	"""

	# Validate echelon_S. (Other parameters will be validated in optimize_base_stock_levels().)
	if not all(echelon_S.values()): raise ValueError("echelon_S cannot be None for any node")

	_, cost = optimize_base_stock_levels(num_nodes=num_nodes, echelon_holding_cost=echelon_holding_cost,
										lead_time=lead_time, stockout_cost=stockout_cost,
										demand_mean=demand_mean, demand_standard_deviation=demand_standard_deviation,
										demand_source=demand_source, network=network,
										S=echelon_S, plots=False,
										 x=None, x_num=x_num, d_num=d_num,
										 ltd_lower_tail_prob=ltd_lower_tail_prob,
										 ltd_upper_tail_prob=ltd_upper_tail_prob,
										 sum_ltd_lower_tail_prob=sum_ltd_lower_tail_prob,
										 sum_ltd_upper_tail_prob=sum_ltd_upper_tail_prob)

	return cost


def expected_holding_cost(echelon_S, 
							num_nodes=None, echelon_holding_cost=None, lead_time=None,
							stockout_cost=None, demand_mean=None, demand_standard_deviation=None,
							demand_source=None, network=None,
							x_num=1000, d_num=100,
							ltd_lower_tail_prob=1-stats.norm.cdf(4),
							ltd_upper_tail_prob=1-stats.norm.cdf(4),
							sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
							sum_ltd_upper_tail_prob=1-stats.norm.cdf(8)):
	"""Calculate expected holding cost of given solution.

	The basic idea is to set the stockout cost to 0 and call 
	:func:`optimize_base_stock_levels` without doing any optimization.

	For parameter descriptions, see docstring for :func:`~stockpyl.ssm_serial.optimize_base_stock_levels`.

	Parameters
	----------
	echelon_S : dict
		Dict of echelon base-stock levels to be evaluated.
	other parameters :
		See :func:`~stockpyl.ssm_serial.optimize_base_stock_levels`.

	Returns
	-------
	holding_cost : float
		Expected holding cost of system.


	Raises
	------
	ValueError
		If ``stockout_cost`` is ``None`` or if ``echelon_S``, ``echelon_holding_cost``,
		or ``lead_time`` is ``None`` for any node.
	ValueError
		If ``demand_mean`` or ``demand_standard_deviation`` is ``None`` and 
		``demand_source`` is ``None``.
	ValueError
		If ``stockout_cost`` < 0 or if ``lead_time`` < 0 for any node.
		

	**Equations Used**: See :func:`optimize_base_stock_levels`.


	**Example** (Example 6.1):

	.. testsetup:: *

		from stockpyl.ssm_serial import *

	.. doctest::

		>>> expected_holding_cost(
		...		echelon_S={1: 6.5144388073261155, 2: 12.012332294949644, 3: 22.700237234889784},
		... 	num_nodes=3, 
		... 	echelon_holding_cost=[2, 2, 3], 
		... 	lead_time=[2, 1, 1], 
		... 	stockout_cost=37.12, 
		... 	demand_mean=5, 
		... 	demand_standard_deviation=1
		...	)
		43.10006605241919
	"""

	# Validate echelon_S. (Other parameters will be validated in optimize_base_stock_levels().)
	if not all(echelon_S.values()): raise ValueError("echelon_S cannot be None for any node")

	# Make copy of network and set stockout cost to 0.
	if network:
		network2 = copy.deepcopy(network)
		for node in network2.nodes:
			node.stockout_cost = 0
	else:
		stockout_cost = 0
		network2 = None

	_, holding_cost = optimize_base_stock_levels(num_nodes=num_nodes, echelon_holding_cost=echelon_holding_cost,
										lead_time=lead_time, stockout_cost=stockout_cost,
										demand_mean=demand_mean, demand_standard_deviation=demand_standard_deviation,
										demand_source=demand_source, network=network2,
										S=echelon_S, plots=False, x=None, x_num=x_num, d_num=d_num,
										ltd_lower_tail_prob=ltd_lower_tail_prob,
										ltd_upper_tail_prob=ltd_upper_tail_prob,
										sum_ltd_lower_tail_prob=sum_ltd_lower_tail_prob,
										sum_ltd_upper_tail_prob=sum_ltd_upper_tail_prob)

	return holding_cost


### HELPER FUNCTIONS ###

def _preprocess_parameters(num_nodes=None, node_order_in_system=None, node_order_in_lists=None,
								echelon_holding_cost=None, lead_time=None, stockout_cost=None, 
								demand_mean=None, demand_standard_deviation=None,
								demand_source=None, network=None):
	"""Check that appropriate parameters are provided, validate their values, convert to N, ..., 1
	indexing, and return dict-ified parameters.

	Parameters
	----------
	see optimize_base_stock_levels()

	Returns
	-------
	old_to_new_dict
		dict in which keys are old indices of nodes and values are new indices
	num_nodes
		Number of nodes in system
	echelon_holding_cost_dict
		Dict of echelon holding costs, under new indexing
	lead_time_dict
		Dict of lead times, under new indexing
	stockout_cost
		Stockout cost
	demand_source
		Demand source
	"""

	# Check for presence of data.
	if network is None:
		if (num_nodes is None or echelon_holding_cost is None or \
			lead_time is None or stockout_cost is None):
			raise ValueError("You must provide either network or num_nodes, ..., stockout_cost")
	if network is None and (demand_mean is None or demand_standard_deviation is None) and demand_source is None:
		raise ValueError("You must provide either demand_mean and demand_standard_deviation, or demand_source")

	# Standardize parameters: Convert node indexing to N, ..., 1 and put all attributes in
	# separate parameter dicts (if they are not already).
	if network:
		# Make local copy.
		num_nodes = len(network.nodes)
		local_network = copy.deepcopy(network)
	else:
		# Build a network with the specified node order.
		if node_order_in_system is None:
			# Make sure num_nodes is provided.
			if num_nodes is None:
				raise ValueError("Either num_nodes, node_order_in_system, or network must be provided")
			node_order_in_system = list(range(num_nodes, 0, -1))
		else:
			num_nodes = len(node_order_in_system)
		if node_order_in_lists is None:
			# Build node_order_in_lists.
			node_order_in_lists = node_order_in_system 
		# Build demand_source, if not provided.
		if demand_source is None:
			demand_source = DemandSource(type='N', mean=demand_mean, standard_deviation=demand_standard_deviation)
		# Build serial system.
		local_network = serial_system(num_nodes=num_nodes, 
			node_order_in_system=node_order_in_system,
			node_order_in_lists=node_order_in_lists,
			echelon_holding_cost=echelon_holding_cost,
			shipment_lead_time=lead_time,
			stockout_cost=stockout_cost,
			demand_source=demand_source
		)
	# Reindex nodes to N, ..., 1.
	old_to_new_dict = {}
	k = num_nodes
	n = local_network.source_nodes[0]
	for _ in range(num_nodes):
		old_to_new_dict[n.index] = k
		k -= 1
		n = n.get_one_successor()
	local_network.reindex_nodes(old_to_new_dict)
	# Build dicts and singletons of parameters.
	echelon_holding_cost_dict = {node.index: node.echelon_holding_cost for node in local_network.nodes}
	lead_time_dict = {node.index: node.lead_time for node in local_network.nodes}
	stockout_cost = local_network.nodes_by_index[1].stockout_cost
	demand_source = local_network.nodes_by_index[1].demand_source
	
	# Validate more parameters.
	if any(c is None for c in echelon_holding_cost_dict.values()): raise ValueError("echelon_holding_cost cannot be None for any node")
	if stockout_cost < 0: raise ValueError("stockout_cost must be non-negative")
	if any(L is None for L in lead_time_dict.values()): raise ValueError("lead_time cannot be None for any node")
	if any(l < 0 for l in lead_time_dict.values()): raise ValueError("lead_time must be non-negative for every node")
	
	return old_to_new_dict, num_nodes, echelon_holding_cost_dict, lead_time_dict, stockout_cost, demand_source