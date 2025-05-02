# ===============================================================================
# stockpyl - wagner_whitin Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_wagner_whitin| module contains code for solving the Wagner-Whitin
problem using dynamic programming.

.. note:: |fosct_notation|

.. seealso::

	For an overview of single-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for single-echelon inventory optimization<tutorial_seio_page>`.



API Reference
-------------

"""

import numpy as np

from stockpyl.helpers import *


def wagner_whitin(num_periods, holding_cost, fixed_cost, demand, purchase_cost=0):
	"""Solve the Wagner-Whitin problem using dynamic programming (DP).

	The time periods are indexed 1, ..., ``num_periods``. Lists given in
	outputs use the same indexing, which means that element 0
	will usually be ignored. (In some cases, element 0 is used to represent
	initial conditions.)

	Most parameters may be given as a singleton or a list. If given as a
	singleton, the parameter will be assumed to be the same in every time
	period. If given as a list, the list must be of length ``num_periods`` or
	``num_periods``\+1.

	*	In the former case, the list is assumed to contain values for periods
		1, ..., ``num_periods`` in elements 0, ..., ``num_periods``-1.
	*	In the latter case, the list is assumed to contain values for periods
		1, ..., ``num_periods`` in elements 1, ..., ``num_periods``, and the
		0th element is ignored.

	The parameters may be mixed, some singletons and some lists.

	Parameters
	----------
	num_periods : int
		Number of periods in time horizon. [:math:`T`]
	holding_cost : float or list
		Holding cost per item per period. [:math:`h`]
	fixed_cost : float or list
		Fixed cost per order. [:math:`K`]
	demand : float or list
		Demand in each time period. [:math:`d`]
	purchase_cost : float or list, optional
		Purchase cost per item. [:math:`c`]

	Returns
	-------
	order_quantities : list
		List of order quantities in each time period. [:math:`Q^*`]
	cost : float
		Optimal cost for entire horizon. [:math:`\\theta_1`]
	costs_to_go : list
		List of "costs to go". [:math:`\\theta`]
	next_order_periods : list
		List of "next order" period. [:math:`s`]

	Raises
	------
	ValueError
		If ``holding_cost``, ``fixed_cost``, ``demand``, or ``purchase_cost`` <= 0 for any time period.


	**Equation Used** (modified from equation (3.39)):

	.. math::

		\\theta_t = \\min_{t < s \le T+1} \\left\\{K + c_t\sum_{i=1}^{s-1}d_i + h\\sum_{i=t}^{s-1}(i-t)d_i + \\theta_s \\right\\}

	**Algorithm Used:** Wagner-Whitin algorithm (Algorithm 3.1)

	**Example** (a Example 3.9):

	.. testsetup:: *

		from stockpyl.wagner_whitin import *

	.. doctest::

		>>> Q, cost, theta, s = wagner_whitin(4, 2, 500, [90, 120, 80, 70])
		>>> Q
		[0, 210, 0, 150, 0]
		>>> cost
		1380.0
		>>> theta
		array([   0., 1380.,  940.,  640.,  500.,    0.])
		>>> s
		[0, 3, 5, 5, 5]

	"""
	# Check that parameters are non-negative.
	if not np.all(np.array(holding_cost) >= 0): raise ValueError("holding_cost must be non-negative")
	if not np.all(np.array(fixed_cost) >= 0): raise ValueError("fixed_cost must be non-negative")
	if not np.all(np.array(demand) >= 0): raise ValueError("demand must be non-negative")
	if not np.all(np.array(purchase_cost) >= 0): raise ValueError("purchase_cost must be non-negative")

	# Replace scalar parameters with lists (multiple copies of scalar).
	holding_cost = ensure_list_for_time_periods(holding_cost, num_periods)
	fixed_cost = ensure_list_for_time_periods(fixed_cost, num_periods)
	demand = ensure_list_for_time_periods(demand, num_periods)
	purchase_cost = ensure_list_for_time_periods(purchase_cost, num_periods)

	# Allocate solution arrays.
	theta = np.zeros(num_periods+2)
	next_order_periods = [0] * (num_periods+1)

	# Loop backwards through periods.
	for t in range(num_periods, 0, -1):

		# Loop through possible next order periods.
		best_cost = BIG_FLOAT
		for ss in range(t+1, num_periods+2):
			# Calculate cost if next order is in period ss.
			cost = fixed_cost[t] * (sum(demand[i] for i in range(t, ss)) > 0) # 0 fixed/setup cost if demand is 0
			for i in range(t, ss):
				cost += purchase_cost[t] * demand[i] + holding_cost[t] * (i - t) * demand[i]
			cost += theta[ss]

			# Compare to best cost.
			if cost < best_cost:
				best_cost = cost
				best_s = ss

		# Set theta and next_order_periods.
		theta[t] = best_cost
		next_order_periods[t] = best_s

	# Determine optimal order quantities.
	order_quantities = [0] * (num_periods+1)
	t = 1
	while t <= num_periods:
		order_quantities[t] = np.sum(demand[t:next_order_periods[t]])
		t = next_order_periods[t]
	cost = theta[1]

	return order_quantities, cost, theta, next_order_periods


