# ===============================================================================
# stockpyl - eoq Module
# -------------------------------------------------------------------------------
# Updated: 01-30-2022
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_eoq| module contains code for solving the economic order quantity
(EOQ) problem and some of its variants.

.. note:: |fosct_notation|




The :func:`stockpyl.eoq.economic_order_quantity` function
implements the basic EOQ model; it returns both the optimal order quantity and the corresponding
optimal cost:

.. doctest::
    
    >>> from stockpyl.eoq import economic_order_quantity
    >>> Q, cost = economic_order_quantity(fixed_cost=8, holding_cost=0.225, demand_rate=1300)
    >>> Q
    304.0467800264368
    >>> cost
    68.41052550594829

The module also contains functions for the EOQ with backorders (EOQB) and the economic production quantity (EPQ). 

The :func:`stockpyl.eoq.joint_replenishment_problem_silver_heuristic` function implements 
Silver's (1976) heuristic for the joint replenishment problem (JRP):

.. doctest::

	>>> from stockpyl.eoq import joint_replenishment_problem_silver_heuristic
	>>> shared_fixed_cost = 600
	>>> individual_fixed_costs = [120, 840, 300]
	>>> holding_costs = [160, 20, 50]
	>>> demand_rates = [1, 1, 1]
	>>> Q, T, m, cost = joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)
	>>> Q # order quantities
	[3.103164454170876, 9.309493362512628, 3.103164454170876]
	>>> T # base cycle time
	3.103164454170876
	>>> m # order multiples
	[1, 3, 1]
	>>> cost
	837.8544026261366

API Reference
-------------
"""

import numpy as np


def economic_order_quantity(fixed_cost, holding_cost, demand_rate, order_quantity=None):
	"""Solve the economic order quantity (EOQ) problem, or (if
	``order_quantity`` is supplied) calculate cost of given solution.

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	demand_rate : float
		Demand (items) per unit time. [:math:`\\lambda`]
	order_quantity : float, optional
		Order quantity for cost evaluation. If supplied, no
		optimization will be performed. [:math:`Q`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (or order quantity supplied) (items). [:math:`Q^*`]
	cost : float
		Cost per unit time attained by ``order_quantity``. [:math:`g^*`]


	**Equations Used** (equations (3.4) and (3.5)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda}{h}}

		g^* = \\sqrt{2K\\lambda h}

	or

	.. math::

		g(Q) = \\frac{K\\lambda}{Q} + \\frac{hQ}{2}

	**Example** (Example 3.1):

	.. testsetup:: *

		from stockpyl.eoq import *

	.. doctest::

		>>> economic_order_quantity(8, 0.225, 1300)
		(304.0467800264368, 68.41052550594829)

	"""

	# Check that parameters are non-negative/positive.
	if fixed_cost < 0: raise ValueError("fixed_cost must be non-negative.")
	if holding_cost <= 0: raise ValueError( "holding_cost must be positive.")
	if demand_rate < 0: raise ValueError( "demand_rate must be non-negative.")
	if order_quantity is not None and order_quantity <= 0: raise ValueError("order_quantity must be positive.")

	# Is Q provided?
	if order_quantity is None:
		# Calculate optimal order quantity and cost.
		order_quantity = np.sqrt(2 * fixed_cost * demand_rate / holding_cost)
		cost = order_quantity * holding_cost
	else:
		# Calculate cost.
		cost = fixed_cost * demand_rate / order_quantity + holding_cost * order_quantity / 2

	return order_quantity, cost


def economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate, order_quantity=None, stockout_fraction=None):
	"""Solve the economic order quantity with backorders (EOQB) problem, or (if ``order_quantity`` and ``stockout_fraction`` are supplied) calculate cost of given solution.

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
	order_quantity : float, optional
		Order quantity for cost evaluation. If supplied, no
		optimization will be performed. [:math:`Q`]
	stockout_fraction : float, optional
		Stockout fraction for cost evaluation. If supplied, no
		optimization will be performed. [:math:`x`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (or order quantity supplied) (items). [:math:`Q^*`]
	stockout_fraction : float
		Optimal stockout fraction (or stockout fraction supplied) (items). [:math:`x^*`]
	cost : float
		Cost per unit time attained by ``order_quantity`` and ``stockout_fraction``. [:math:`g^*`]


	**Equations Used** (equations (3.27)--(3.29)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda(h+p)}{hp}}

		x^* = \\frac{h}{h+p}

		g^* = \\sqrt{\\frac{2K\\lambda hp}{h+p}}

	or

	.. math::

		g(Q,x) = \\frac{hQ(1-x)^2}{2} + \\frac{pQx^2}{2} + \\frac{K\lambda}{Q}

	**Example** (Example 3.8):

	.. testsetup:: *

		from stockpyl.eoq import *

	.. doctest::

		>>> economic_order_quantity_with_backorders(8, 0.225, 5, 1300)
		(310.81255515896464, 0.0430622009569378, 66.92136355097325)

	"""

	# Check that parameters are positive.
	if fixed_cost < 0: raise ValueError("fixed_cost must be non-negative.")
	if holding_cost <= 0: raise ValueError( "holding_cost must be positive.")
	if stockout_cost <= 0: raise ValueError( "stockout_cost must be positive.")
	if demand_rate < 0: raise ValueError( "demand_rate must be non-negative.")
	if order_quantity is not None and order_quantity <= 0: raise ValueError("order_quantity must be positive.")
	if stockout_fraction is not None and (stockout_fraction < 0 or stockout_fraction > 1): raise ValueError("stockout_fraction must be between 0 and 1.")

	# Check that both or neither order_quantity and stockout_fraction are  provided.
	if (order_quantity is None and stockout_fraction is not None) or (order_quantity is not None and stockout_fraction is None): raise ValueError("You must provide both order_quantity and stockout_fraction or neither.")

	# Is Q provided?
	if order_quantity is None:
		# Calculate optimal order quantity, stockout fraction, and cost.
		order_quantity = np.sqrt(2 * fixed_cost * demand_rate * (holding_cost + stockout_cost)
									/ (holding_cost * stockout_cost))
		stockout_fraction = holding_cost / (holding_cost + stockout_cost)
		cost = order_quantity * (holding_cost * stockout_cost) / (holding_cost + stockout_cost)
	else:
		# Caclulate cost.
		cost = holding_cost * order_quantity * (1 - stockout_fraction) ** 2 / 2 \
			+ stockout_cost * order_quantity * stockout_fraction ** 2 / 2 \
			+ fixed_cost * demand_rate / order_quantity

	return order_quantity, stockout_fraction, cost


def economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate, order_quantity=None):
	"""Solve the economic production quantity (EPQ) problem, or (if ``order_quantity`` is supplied) calculate cost of given solution.

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
	order_quantity : float, optional
		Order quantity for cost evaluation. If supplied, no optimization will be performed. [:math:`Q`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (or order quantity supplied) (items). [:math:`Q^*`]
	cost : float
		Cost per unit time attained by ``order_quantity``. [:math:`g^*`]


	**Equations Used** (equations (3.31) and (3.32)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda}{h(1-\\rho)}}

		g^* = \\sqrt{2K\\lambda h(1-\\rho)}

	or

	.. math::

		g(Q) = \\frac{K\\lambda}{Q} + \\frac{h(1 - \\rho)Q}{2}

	where :math:`\\rho = \\lambda/\\mu`.

	**Example**:

	.. testsetup:: *

		from stockpyl.eoq import *

	.. doctest::

		>>> economic_production_quantity(8, 0.225, 1300, 1700)
		(626.8084945889684, 33.183979125298336)

	"""

	# Check that parameters are non-negative/positive.
	if fixed_cost < 0: raise ValueError("fixed_cost must be non-negative.")
	if holding_cost <= 0: raise ValueError( "holding_cost must be positive.")
	if demand_rate < 0: raise ValueError( "demand_rate must be non-negative.")
	if production_rate <= 0: raise ValueError( "production_rate must be positive.")
	if order_quantity is not None and order_quantity <= 0: raise ValueError("order_quantity must be positive.")

	# Check that demand rate < production rate.
	if demand_rate >= production_rate: raise ValueError("demand_rate must be less than production_rate.")

	# Calculate rho.
	rho = demand_rate / production_rate

	# Is Q provided?
	if order_quantity is None:
		# Calculate optimal order quantity and cost.
		order_quantity = np.sqrt(
			2 * fixed_cost * demand_rate / (holding_cost * (1 - rho)))
		cost = order_quantity * holding_cost * (1 - rho)
	else:
		# Calculate cost.
		cost = fixed_cost * demand_rate / order_quantity + holding_cost * (1 - rho) * order_quantity / 2

	return order_quantity, cost


def joint_replenishment_problem_silver_heuristic(shared_fixed_cost,
												 individual_fixed_costs,
												 holding_costs,
												 demand_rates):
	"""Solve the joint replenishment problem (JRP) using Silver's (1976) heuristic.

	Parameters
	----------
	shared_fixed_cost : float
		Shared fixed cost per order. [:math:`K`]
	individual_fixed_costs : list of floats
		Individual fixed cost if product ``n`` is included in order. [:math:`k_n`]
	holding_costs : list of floats
		Holding cost per item per unit time for product ``n``. [:math:`h_n`]
	demand_rates : list of floats
		Demand (items) per unit time for product ``n``. [:math:`\\lambda_n`]

	Returns
	-------
	order_quantities : list of floats
		Order quantities (items). [:math:`Q_n`]
	base_cycle_time : float
		Interval between consecutive orders. [:math:`T`]
	order_multiples : list of ints
		Product ``n`` is included in every ``order_multiples[n]`` orders. [:math:`m_n`]
	cost : float
		Cost per unit time. [:math:`g`]


	**Equations Used**:

	.. math::

		\\hat{n} = n \\text{ that minimizes } k_n / h_n\\lambda_n

		m_{\\hat{n}} = 1

		m_n = \\sqrt{\\frac{k_n}{h_n\\lambda_n} \\times \\frac{h_{\\hat{n}}\\lambda_{\\hat{n}}}{K+k_{\\hat{n}}}} \\text{ (rounded)}

		T = \\sqrt{\\frac{2(K+\\sum_{n=1}^N \\frac{k_n}{m_n}}{\\sum_{n=1}^N h_nm_n\\lambda_n}}

		Q_n = Tm_n\\lambda_n

		g = \\frac{K + \\sum_{n=1}^N \\frac{k_n}{m_n}}{T} + \\frac{T}{2}\\sum_{n=1}^N h_nm_n\\lambda_n

	**Example**:

	.. testsetup:: *

		from stockpyl.eoq import *

	.. doctest::

		>>> shared_fixed_cost = 600
		>>> individual_fixed_costs = [120, 840, 300]
		>>> holding_costs = [160, 20, 50]
		>>> demand_rates = [1, 1, 1]
		>>> joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)
		([3.103164454170876, 9.309493362512628, 3.103164454170876], 3.103164454170876, [1, 3, 1], 837.8544026261366)
	"""

	# Check that parameters are non-negative/positive.
	if shared_fixed_cost < 0: raise ValueError("shared_fixed_cost must be non-negative")
	if not np.all(np.array(individual_fixed_costs) >= 0): raise ValueError("individual_fixed_costs must be non-negative.")
	if not np.all(np.array(holding_costs) > 0): raise ValueError("holding_costs must be non-negative.")
	if not np.all(np.array(demand_rates) > 0): raise ValueError("demand_rates must be non-negative.")
	if len(individual_fixed_costs) != len(holding_costs) or len(holding_costs) != len(demand_rates): raise ValueError("all lists must have the same length")

	# Determine number of products.
	num_prod = len(individual_fixed_costs)

	# Calculate ratios.
	ratio = [individual_fixed_costs[n] / (holding_costs[n] * demand_rates[n]) for n in range(num_prod)]

	# Determine product with min ratio.
	min_ratio_prod = np.argmin(ratio)

	# Calculate constant for min_ratio_prod.
	const = holding_costs[min_ratio_prod] * demand_rates[min_ratio_prod] / \
		(shared_fixed_cost + individual_fixed_costs[min_ratio_prod])

	# Calculate order frequencies.
	order_multiples = []
	for n in range(num_prod):

		if n == min_ratio_prod:
			m = 1
		else:
			m = np.sqrt((individual_fixed_costs[n] / (holding_costs[n] * demand_rates[n])) * const)
			m = max(1, int(round(m)))

		order_multiples.append(m)

	# Calculate a few terms we'll need below.
	term1 = shared_fixed_cost + np.sum(np.divide(individual_fixed_costs, order_multiples))
	term2 = np.sum([holding_costs[n] * order_multiples[n] * demand_rates[n] for n in range(num_prod)])

	# Calculate base cycle time.
	numer = 2 * term1
	denom = term2
	base_cycle_time = np.sqrt(numer / denom)

	# Calculate order quantities.
	order_quantities = [base_cycle_time * order_multiples[n] * demand_rates[n] for n in range(num_prod)]

	# Calculate average cost.
	avg_fixed_cost = term1 / base_cycle_time
	avg_holding_cost = (base_cycle_time / 2) * term2
	cost = avg_fixed_cost + avg_holding_cost

	return order_quantities, base_cycle_time, order_multiples, cost

