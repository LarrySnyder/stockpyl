"""Code for solving newsvendor_normal problem.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

from scipy import stats
import numpy as np

import inventory.loss_functions as lf
from inventory.helpers import *


def newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd,
					  lead_time=0, base_stock_level=None):
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
	lead_time : int, optional
		Lead time. Optional; default = 0. [L]
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
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

	# Calculate lead-time demand parameters.
	ltd_mean = demand_mean * (lead_time + 1)
	ltd_sd = demand_sd * np.sqrt(lead_time + 1)

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = stockout_cost / (stockout_cost + holding_cost)

		# Calculate optimal order quantity and cost.
		base_stock_level = stats.norm.ppf(alpha, ltd_mean, ltd_sd)
		cost = (holding_cost + stockout_cost) * stats.norm.pdf(stats.norm.ppf(alpha, 0, 1)) * ltd_sd
	else:
		# Calculate loss functions.
		n, n_bar = lf.normal_loss(base_stock_level, ltd_mean, ltd_sd)

		# Calculate cost.
		cost = holding_cost * n_bar + stockout_cost * n

	return base_stock_level, cost


def newsvendor_poisson(holding_cost, stockout_cost, demand_mean,
					  base_stock_level=None):
	"""Solve newsvendor problem with Poisson distribution, or (if
	base_stock_level is supplied) calculate cost of given solution.

	Notation below in brackets [...] is from Snyder and Shen (2019).

	TODO: handle lead time

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [h]
	stockout_cost : float
		Stockout cost per item per period. [p]
	demand_mean : float
		Mean demand per period. [mu]
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
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

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = stockout_cost / (stockout_cost + holding_cost)

		# Calculate optimal order quantity and cost.
		base_stock_level = stats.poisson.ppf(alpha, demand_mean)
	else:
		# Check for integer x.
		assert is_integer(base_stock_level), "x must be an integer"

	# Calculate loss functions.
	n, n_bar = lf.poisson_loss(base_stock_level, demand_mean)

	# Calculate cost.
	cost = holding_cost * n_bar + stockout_cost * n

	return base_stock_level, cost


def newsvendor_continuous(holding_cost, stockout_cost, demand_distrib=None,
						demand_pdf=None, base_stock_level=None):
	"""Solve newsvendor problem with generic continuous distribution, or (if
	base_stock_level is supplied) calculate cost of given solution.

	Must provide rv_continuous distribution (in demand_distrib) or
	demand pdf (in demand_pdf, as a function).

	TODO: handle lead time
	TODO: handle demand_pdf as function

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [h]
	stockout_cost : float
		Stockout cost per item per period. [p]
	demand_distrib : rv_continuous, optional
		Demand distribution object.
	demand_pdf : function, optional
		Demand pdf, as a function. Ignored if demand_distrib is not None.
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
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

	# Check that either distribution or pmf have been supplied.
	assert (demand_distrib is not None) or (demand_pdf is not None), \
		"must provide demand_distrib or demand_pdf"

	# For now, raise error if only demand_pdf is provided. (Need to add this
	# capability.)
	assert demand_distrib is not None, "newsvendor_continuous() does not yet support demand distributions passed as pdf functions"

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = stockout_cost / (stockout_cost + holding_cost)

		# Was distribution provided?
		if demand_distrib is not None:
			# Use built-in ppf (F-inverse) function.
			base_stock_level = demand_distrib.ppf(alpha)
		else:
			# NEED TO HANDLE THIS CASE
			pass

	# Calculate loss functions.
	n, n_bar = lf.continuous_loss(base_stock_level, demand_distrib)

	# Calculate cost.
	cost = holding_cost * n_bar + stockout_cost * n

	return base_stock_level, cost


def newsvendor_discrete(holding_cost, stockout_cost, demand_distrib=None,
						demand_pmf=None, base_stock_level=None):
	"""Solve newsvendor problem with generic discrete distribution, or (if
	base_stock_level is supplied) calculate cost of given solution.

	Must provide either rv_discrete distribution (in demand_distrib) or
	demand pmf (in demand_pmf, as a dict).

	TODO: handle lead time

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [h]
	stockout_cost : float
		Stockout cost per item per period. [p]
	demand_distrib : rv_discrete, optional
		Demand distribution object.
	demand_pmf : dict, optional
		Demand pmf, as a dict in which keys are possible demand values and
		values are their probabilities. Ignored if demand_distrib is not None.
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
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

	# Check that either distribution or pmf have been supplied.
	assert (demand_distrib is not None) or (demand_pmf is not None), \
		"must provide demand_distrib or demand_pmf"

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = stockout_cost / (stockout_cost + holding_cost)

		# Was distribution provided?
		if demand_distrib is not None:
			# Use built-in ppf (F-inverse) function.
			base_stock_level = demand_distrib.ppf(alpha)
		else:
			# Build sorted list of demand values.
			demand_values = list(demand_pmf.keys())
			demand_values.sort()
			# Loop through demands until cdf exceeds alpha.
			i = 0
			F = 0
			while F < alpha:
				F += demand_pmf[demand_values[i]]
				i += 1
				if i >= len(demand_pmf):
					break
			# Set base-stock level.
			base_stock_level = demand_values[i-1]
	else:
		# Check for integer base_stock_level
		assert is_integer(base_stock_level), "base_stock_level must be an integer"

	# Calculate loss functions.
	n, n_bar = lf.discrete_loss(base_stock_level, demand_distrib, demand_pmf)

	# Calculate cost.
	cost = holding_cost * n_bar + stockout_cost * n

	return base_stock_level, cost

