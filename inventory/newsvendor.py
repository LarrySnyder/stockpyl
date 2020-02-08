"""Code for solving newsvendor_normal problem.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np
from scipy import stats

import inventory.loss_functions as lf


def newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd,
					  base_stock_level=None):
	"""Solve newsvendor problem with normal distribution, or (if
	base_stock_level is supplied) calculate cost of given solution.

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [h]
	stockout_cost : float
		Stockout cost per item per period. [p]
	demand_mean : float
		Mean demand per period. [mu]
	demand_sd : float
		Standard deviation of demand per period. [sigma]
	base_stock_level : float
		Base-stock level to evaluate cost of (optional). If supplied, no
		optimization will be performed. [S]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [S^*]
	cost : float
		Cost per period attained by base_stock_level. [g^*]
	"""

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert demand_mean > 0, "demand_mean must be positive."
	assert demand_sd > 0, "demand_sd must be positive."

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = stockout_cost / (stockout_cost + holding_cost)

		# Calculate optimal order quantity and cost.
		base_stock_level = stats.norm.ppf(alpha, demand_mean, demand_sd)
		cost = (holding_cost + stockout_cost) * stats.norm.pdf(stats.norm.ppf(alpha, 0, 1)) * demand_sd
	else:
		# Calculate loss functions.
		n, n_bar = lf.normal_loss(base_stock_level, demand_mean, demand_sd)

		# Calculate cost.
		cost = holding_cost * n_bar + stockout_cost * n

	return base_stock_level, cost


