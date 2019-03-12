"""Code for solving newsvendor problem.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np


def newsvendor(holding_cost, stockout_cost, demand_mean, demand_sd):
	"""Solve newsvendor problem.

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [K]
	holding_cost : float
		Holding cost per item per unit time. [h]
	demand_rate : float
		Demand (items) per unit time. [lambda]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (items). [Q^*]
	cost : float
		Optimal cost per unit time. [g^*]
	"""

	# Check that parameters are positive.
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert holding_cost > 0, "holding_cost must be positive."
	assert demand_rate > 0, "demand_rate must be positive."

	# Calculate optimal order quantity and cost.
	order_quantity = np.sqrt(2 * fixed_cost * demand_rate / holding_cost)
	cost = order_quantity * holding_cost

	return order_quantity, cost


def economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate):
	"""Solve economic order quantity with backorders (EOQB) problem.

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [K]
	holding_cost : float
		Holding cost per item per unit time. [h]
	stockout_cost : float
		Stockout cost per item per unit time. [p]
	demand_rate : float
		Demand (items) per unit time. [lambda]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (items). [Q^*]
	stockout_fraction : float
		Optimal stockout fraction (items). [x^*]
	cost : float
		Optimal cost per unit time. [g^*]
	"""

	# Check that parameters are positive.
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert demand_rate > 0, "demand_rate must be positive."

	# Calculate optimal order quantity and cost.
	order_quantity = np.sqrt(2 * fixed_cost * demand_rate * (holding_cost + stockout_cost)
								/ (holding_cost * stockout_cost))
	stockout_fraction = holding_cost / (holding_cost + stockout_cost)
	cost = order_quantity * (holding_cost * stockout_cost) / (holding_cost + stockout_cost)

	return order_quantity, stockout_fraction, cost


