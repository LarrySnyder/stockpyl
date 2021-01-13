# ===============================================================================
# PyInv - supply_uncertainty Module
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 01-12-2021
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""The :mod:`supply_uncertainty` module contains code for solving inventory
problems with supply uncertainty.

Functions in this module are called directly; they are not wrapped in a class.

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory*, 2nd edition
(2019).

"""

import numpy as np

from pyinv import optimization


def economic_order_quantity_with_disruptions(fixed_cost, holding_cost, stockout_cost, demand_rate,
											 disruption_rate, recovery_rate, approximate=False):
	"""Solve the economic order quantity problem with disruptions (EOQD) as
	presented by Parlar and Berkin (1991) and Berk and Arreola-Risa (1994).
	Problem is solved numerically using golden section search.

	Set ``approximate`` to ``True`` to use the approximation by Snyder (2014).

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item. [:math:`p`]
	demand_rate : float
		Demand (items) per unit time. [:math:`d`]
	disruption_rate : float
		Parameter of exponential distribution governing length of "up" intervals. [:math:`\\lambda`]
	recovery_rate : float
		Parameter of exponential distribution governing length of "down" intervals. [:math:`\\mu`]
	approximate : bool, optional
		Use approximate cost function?
	Returns
	-------
	order_quantity : float
		Optimal order quantity (items). [:math:`Q^*`]
	cost : float
		Optimal cost per unit time. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``fixed_cost`` or ``demand_rate`` < 0, or if ``holding_cost`` or
		``stockout_cost`` <= 0.
	ValueError
		If ``disruption_rate`` <= 0 or ``recovery_rate`` <= 0.


	**Equations Used** (equation (9.5)):

	.. math::

		g(Q) = \\frac{K + hQ^2/2d + pd\\psi/\\mu}{Q/d + \\psi/\\mu},

	where

	.. math::

		\\psi = \\frac{\\lambda}{\\lambda+\\mu} \\left(1 - e^{-\\frac{(\\lambda+\\mu)Q}{d}}\\right)

	if ``approximate`` is ``False``. If ``approximate`` is ``True``, then

	.. math::

		Q^* = \\frac{\\sqrt{(\\psi d h)^2 + 2h\\mu(Kd\\mu + d^2p\\psi)} - \\psi dh}{h\\mu},

	where

	.. math::

		\\psi = \\frac{\\lambda}{\\lambda+\\mu},

	and

	.. math::

		g(Q^*) = hQ^*.

	(See Snyder (2014).)

	**Example** (Example 3.1):

	.. testsetup:: *

		from pyinv.eoq import *

	.. doctest::

		>>> economic_order_quantity(8, 0.225, 1300)
		(304.0467800264368, 68.41052550594829)

	"""

	# Check that parameters are positive.
	assert fixed_cost >= 0, "fixed_cost must be non-negative."
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert demand_rate >= 0, "demand_rate must be non-negative."
	assert disruption_rate > 0, "disruption_rate must be positive"
	assert recovery_rate > 0, "recovery_rate must be positive"

	# Calculate approximate order quantity. Even if exact order quantity is
	# requested, approximate quantity will be used for search bounds.
	psi_approx = (disruption_rate / (disruption_rate + recovery_rate))

	# Calculate approximate Q^*.
	order_quantity_approx = (np.sqrt((psi_approx * demand_rate * holding_cost) ** 2 + 2 * holding_cost * recovery_rate * (
				fixed_cost * demand_rate * recovery_rate + demand_rate ** 2 * stockout_cost * psi_approx)) - psi_approx * demand_rate * holding_cost) / (
								 holding_cost * recovery_rate)

	# Approximate?
	if approximate:

		# Set Q.
		order_quantity = order_quantity_approx

		# Calculate g(Q).
		cost = holding_cost * order_quantity

	else:

		# Use golden section search to find Q*.
		f = lambda Q: economic_order_quantity_with_disruptions_cost(Q, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		lo = order_quantity_approx / 10
		hi = order_quantity_approx * 10
		order_quantity, cost = optimization.golden_section_search(f, lo, hi, verbose=False)

	return order_quantity, cost


def economic_order_quantity_with_disruptions_cost(order_quantity, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate,
											approximate=False):
	"""Calculate the cost of using ``order_quantity`` as the solution to
	the economic order quantity problem with disruptions (EOQD) as
	presented by Parlar and Berkin (1991) and Berk and Arreola-Risa (1994).

	Set ``approximate`` to ``True`` to use the approximation by Snyder (2014).

	Parameters
	----------
	order_quantity : float
		Order quantity for cost evaluation. [:math:`Q`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item. [:math:`p`]
	demand_rate : float
		Demand (items) per unit time. [:math:`d`]
	disruption_rate : float
		Parameter of exponential distribution governing length of "up" intervals. [:math:`\\lambda`]
	recovery_rate : float
		Parameter of exponential distribution governing length of "down" intervals. [:math:`\\mu`]
	approximate : bool, optional
		Use approximate cost function?

	Returns
	-------
	cost : float
		Optimal cost per unit time. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``fixed_cost`` or ``demand_rate`` < 0, or if ``holding_cost``,
		``stockout_cost``, or ``order_quantity`` <= 0.
	ValueError
		If ``disruption_rate`` <= 0 or ``recovery_rate`` <= 0.


	**Equations Used** (equation (9.5)):

	.. math::

		g(Q) = \\frac{K + hQ^2/2d + pd\\psi/\\mu}{Q/d + \\psi/\\mu},

	where

	.. math::

		\\psi = \\frac{\\lambda}{\\lambda+\\mu} \\left(1 - e^{-\\frac{(\\lambda+\\mu)Q}{d}}\\right)

	if ``approximate`` is ``False`` and

	.. math::

		\\psi = \\frac{\\lambda}{\\lambda+\\mu}

	if ``approximate`` is ``True``.

	**Example** (Example 9.1):

	.. testsetup:: *

		from pyinv.supply_uncertainty import *

	.. doctest::

		>>> economic_order_quantity_with_disruptions_cost(700, 8, 0.225, 5, 1300, 1.5, 14)
		174.78711738886236

		>>> economic_order_quantity_with_disruptions_cost(700, 8, 0.225, 5, 1300, 1.5, 14, approximate=True)
		174.80614234644133
	"""

	# TODO: allow base_stock_level to be an array (for other _cost functions too)

	# Check that parameters are positive.
	assert fixed_cost >= 0, "fixed_cost must be non-negative."
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert demand_rate >= 0, "demand_rate must be non-negative."
	assert order_quantity > 0, "order_quantity must be positive"
	assert disruption_rate > 0, "disruption_rate must be positive"
	assert recovery_rate > 0, "recovery_rate must be positive"

	# Calculate psi.
	if approximate:
		psi = (disruption_rate / (disruption_rate + recovery_rate))
	else:
		psi = (disruption_rate / (disruption_rate + recovery_rate)) \
			* (1 - np.exp(-(disruption_rate+recovery_rate) * order_quantity / demand_rate))

	# Calculate cost.
	numer = (fixed_cost + holding_cost * order_quantity**2 / (2 * demand_rate)
			+ stockout_cost * demand_rate * psi / recovery_rate)
	denom = order_quantity / demand_rate + psi / recovery_rate
	cost = numer / denom

	return cost






