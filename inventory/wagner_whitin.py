"""Code for solving Wagner-Whitin problem.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np

from inventory.helpers import *

def wagner_whitin(num_periods, holding_cost, fixed_cost, demand):
	"""Solve Wagner-Whitin problem using dynamic programming (DP).

	The time periods are indexed 1, ..., num_periods. Lists given in
	outputs will use the same indexing, which means that item [0]
	will usually be ignored. (In some cases, item [0] is used to represent
	initial conditions.)

	Most parameters may be given as a singleton or a list. If given as a
	singleton, the parameter will be assumed to be the same in every time
	period. If given as a list, the list must be of length num_periods or
	num_periods+1.
		- In the former case, the list is assumed to contain values
			for periods 1, ..., num_periods in elements 0, ..., num_periods-1.
		- In the latter case, the list is assumed to contain values
			for periods 1, ..., num_periods in elements 1, ..., num_periods,
			and the [0] element is ignored.

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	num_periods : int
		Number of periods in time horizon. [T]
	holding_cost : float or list
		Holding cost per item per period. If list, length must equal
		num_periods. [h]
	fixed_cost : float or list
		Fixed cost per order. If list, length must equal num_periods. [K]
	demand : float or list
		Demand in each time period. If list, length must equal num_periods. [d]

	Returns
	-------
	order_quantities : list
		List of order quantities in each time period. [Q^*]
	next_order_periods : list
		List of "next order" period. [next_order_periods]
	cost : float
		Optimal cost for entire horizon. [g^*]
	"""
	# Check that parameters are non-negative.
	assert np.all(np.array(holding_cost) >= 0), "holding_cost must be non-negative."
	assert np.all(np.array(fixed_cost) >= 0), "fixed_cost must be non-negative."
	assert np.all(np.array(demand) >= 0), "demand must be non-negative."

	# Replace scalar parameters with lists (multiple copies of scalar).
	holding_cost = ensure_list_for_time_periods(holding_cost, num_periods)
	fixed_cost = ensure_list_for_time_periods(fixed_cost, num_periods)
	demand = ensure_list_for_time_periods(demand, num_periods)

	# Allocate solution arrays.
	theta = np.zeros(num_periods+2)
	next_order_periods = [0] * (num_periods+1)

	# Loop backwards through periods.
	for t in range(num_periods, 0, -1):

		# Loop through possible next order periods.
		best_cost = BIG_FLOAT
		for ss in range(t+1, num_periods+2):
			# Calculate cost if next order is in period ss.
			cost = fixed_cost[t]
			for i in range(t, ss):
				# TODO: vectorize this
				cost += holding_cost[t] * (i - t) * demand[i]
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

	return order_quantities, next_order_periods, cost



