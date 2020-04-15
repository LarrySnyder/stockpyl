# ===============================================================================
# PyInv - eoq Module
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 04-15-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""The :mod:`eoq` module contains code for solving the economic order quantity
(EOQ) problem and some of its variants.

Functions in this class are called directly; they are not wrapped in a class.

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory*, 2nd edition
(2019).

"""

import numpy as np


def economic_order_quantity(fixed_cost, holding_cost, demand_rate):
	"""Solve the economic order quantity (EOQ) problem.

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	demand_rate : float
		Demand (items) per unit time. [:math:`\\lambda`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (items). [:math:`Q^*`]
	cost : float
		Optimal cost per unit time. [:math:`g^*`]


	**Equations Used** (equations (3.4) and (3.5)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda}{h}}

		g^* = \\sqrt{2K\\lambda h}

	**Example** (Example 3.1):

	.. testsetup:: *

		from inventory.eoq import *

	.. doctest::

		>>> economic_order_quantity(8, 0.225, 1300)
		(304.0467800264368, 68.41052550594829)

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
	"""Solve the economic order quantity with backorders (EOQB) problem.

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	demand_rate : float
		Demand (items) per unit time. [:math:`\\lambda`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (items). [:math:`Q^*`]
	stockout_fraction : float
		Optimal stockout fraction (items). [:math:`x^*`]
	cost : float
		Optimal cost per unit time. [:math:`g^*`]


	**Equations Used** (equations (3.27)--(3.29)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda(h+p)}{hp}}

		x^* = \\frac{h}{h+p}

		g^* = \\sqrt{\\frac{2K\\lambda hp}{h+p}}

	**Example** (Example 3.8):

	.. testsetup:: *

		from inventory.eoq import *

	.. doctest::

		>>> economic_order_quantity_with_backorders(8, 0.225, 5, 1300)
		(310.81255515896464, 0.0430622009569378, 66.92136355097325)

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


def economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate):
	"""Solve the economic production quantity (EPQ) problem.

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	demand_rate : float
		Demand (items) per unit time. [:math:`\\lambda`]
	production_rate : float
		Production quantity (items) per unit time. [:math:`\\mu`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (items). [:math:`Q^*`]
	cost : float
		Optimal cost per unit time. [:math:`g^*`]


	**Equations Used** (equations (3.31) and (3.32)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda}{h(1-\\rho)}}

		g^* = \\sqrt{2K\\lambda h(1-\\rho)}

	where :math:`\\rho = \\lambda/\\mu`.

	**Example**:

	.. testsetup:: *

		from inventory.eoq import *

	.. doctest::

		>>> economic_production_quantity(8, 0.225, 1300, 1700)
		(626.8084945889684, 33.183979125298336)

	"""

	# Check that parameters are positive.
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert holding_cost > 0, "holding_cost must be positive."
	assert demand_rate > 0, "demand_rate must be positive."
	assert production_rate > 0, "production_rate must be positive."

	# Calculate rho.
	rho = demand_rate / production_rate

	# Calculate optimal order quantity and cost.
	order_quantity = np.sqrt(
		2 * fixed_cost * demand_rate / (holding_cost * (1 - rho)))
	cost = order_quantity * holding_cost * (1 - rho)

	return order_quantity, cost

