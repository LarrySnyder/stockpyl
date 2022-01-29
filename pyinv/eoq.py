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

Functions in this module are called directly; they are not wrapped in a class.

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory*, 2nd edition
(2019).

"""

# TODO: allow these functions to take lists or ndarrays

#from instances import *

import numpy as np

from pyinv.helpers import check_iterable_sizes


def economic_order_quantity(fixed_cost, holding_cost, demand_rate):
	"""Solve the economic order quantity (EOQ) problem.

	Input parameters may be singletons or list-like objects, or a combination.
	All list-like objects must have the same dimensions. Return values will
	be singletons if all input parameters are singletons and will be ndarrays otherwise.

	Parameters
	----------
	fixed_cost : float or list-like of floats
		Fixed cost per order. [:math:`K`]
	holding_cost : float or list-like of floats
		Holding cost per item per unit time. [:math:`h`]
	demand_rate : float or list-like of floats
		Demand (items) per unit time. [:math:`\\lambda`]

	Returns
	-------
	order_quantity : float or ndarray
		Optimal order quantity (items). [:math:`Q^*`]
	cost : float or ndarray
		Optimal cost per unit time. [:math:`g^*`]


	**Equations Used** (equations (3.4) and (3.5)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda}{h}}

		g^* = \\sqrt{2K\\lambda h}

	**Example** (Example 3.1):

	.. testsetup:: *

		from pyinv.eoq import *

	.. doctest::

		>>> economic_order_quantity(8, 0.225, 1300)
		(304.0467800264368, 68.41052550594829)

	**Example** (Example 3.1 and an example with :math:`K=20`, :math:`h=1`, :math:`\\lambda=100`):

	.. testsetup:: *

		from pyinv.eoq import *

	.. doctest::

		>>> economic_order_quantity([8, 20], [0.225, 1], [1300, 100])
		(array([304.04678003,  63.2455532 ]), array([68.41052551, 63.2455532 ]))

	"""

	# Convert input parameters to numpy arrays.
	fixed_cost = np.array(fixed_cost)
	holding_cost = np.array(holding_cost)
	demand_rate = np.array(demand_rate)

	# Check that parameters are non-negative/positive.
	if not np.all(fixed_cost >= 0): raise ValueError("fixed_cost must be non-negative.")
	if not np.all(holding_cost > 0): raise ValueError( "holding_cost must be positive.")
	if not np.all(demand_rate >= 0): raise ValueError( "demand_rate must be non-negative.")

	# Check that parameters are singletons or same-size iterables.
	if not check_iterable_sizes([fixed_cost, holding_cost, demand_rate]): raise ValueError("Input parameters must singletons or list-like objects of the same size.")

	# Calculate optimal order quantity and cost.
	order_quantity = np.sqrt(2 * fixed_cost * demand_rate / holding_cost)
	cost = order_quantity * holding_cost

	return order_quantity, cost


# TODO: need an eoq_cost() function, or an order_quantity parameter in eoq()

def economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate):
	"""Solve the economic order quantity with backorders (EOQB) problem.

	Input parameters may be singletons or list-like objects, or a combination.
	All list-like objects must have the same dimensions. Return values will
	be singletons if all input parameters are singletons and will be ndarrays otherwise.

	Parameters
	----------
	fixed_cost : float or list-like of floats
		Fixed cost per order. [:math:`K`]
	holding_cost : float or list-like of floats
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float or list-like of floats
		Stockout cost per item per unit time. [:math:`p`]
	demand_rate : float or list-like of floats
		Demand (items) per unit time. [:math:`\\lambda`]

	Returns
	-------
	order_quantity : float or ndarray
		Optimal order quantity (items). [:math:`Q^*`]
	stockout_fraction : float or ndarray
		Optimal stockout fraction (items). [:math:`x^*`]
	cost : float or ndarray
		Optimal cost per unit time. [:math:`g^*`]


	**Equations Used** (equations (3.27)--(3.29)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda(h+p)}{hp}}

		x^* = \\frac{h}{h+p}

		g^* = \\sqrt{\\frac{2K\\lambda hp}{h+p}}

	**Example** (Example 3.8):

	.. testsetup:: *

		from pyinv.eoq import *

	.. doctest::

		>>> economic_order_quantity_with_backorders(8, 0.225, 5, 1300)
		(310.81255515896464, 0.0430622009569378, 66.92136355097325)

	**Example** (Example 3.8 and an example with :math:`K=20`, :math:`h=1`, :math:`p=10`, :math:`\\lambda=100`):

	.. testsetup:: *

		from pyinv.eoq import *

	.. doctest::

		>>> economic_order_quantity_with_backorders([8, 20], [0.225, 1], [5, 10], [1300, 100])
		(array([310.81255516,  66.33249581]), array([0.0430622 , 0.09090909]), array([66.92136355, 60.30226892]))

	"""

	# Convert input parameters to numpy arrays.
	fixed_cost = np.array(fixed_cost)
	holding_cost = np.array(holding_cost)
	stockout_cost = np.array(stockout_cost)
	demand_rate = np.array(demand_rate)
	
	# Check that parameters are positive.
	if not np.all(fixed_cost >= 0): raise ValueError("fixed_cost must be non-negative.")
	if not np.all(holding_cost > 0): raise ValueError( "holding_cost must be positive.")
	if not np.all(stockout_cost > 0): raise ValueError( "stockout_cost must be positive.")
	if not np.all(demand_rate >= 0): raise ValueError( "demand_rate must be non-negative.")

	# Check that parameters are singletons or same-size iterables.
	if not check_iterable_sizes([fixed_cost, holding_cost, stockout_cost, demand_rate]): raise ValueError("Input parameters must singletons or list-like objects of the same size.")

	# Calculate optimal order quantity and cost.
	order_quantity = np.sqrt(2 * fixed_cost * demand_rate * (holding_cost + stockout_cost)
								/ (holding_cost * stockout_cost))
	stockout_fraction = holding_cost / (holding_cost + stockout_cost)
	cost = order_quantity * (holding_cost * stockout_cost) / (holding_cost + stockout_cost)

	return order_quantity, stockout_fraction, cost


def economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate):
	"""Solve the economic production quantity (EPQ) problem.

	Input parameters may be singletons or list-like objects, or a combination.
	All list-like objects must have the same dimensions. Return values will
	be singletons if all input parameters are singletons and will be ndarrays otherwise.

	Parameters
	----------
	fixed_cost : float or list-like of floats
		Fixed cost per order. [:math:`K`]
	holding_cost : float or list-like of floats
		Holding cost per item per unit time. [:math:`h`]
	demand_rate : float or list-like of floats
		Demand (items) per unit time. [:math:`\\lambda`]
	production_rate : float or list-like of floats
		Production quantity (items) per unit time. [:math:`\\mu`]

	Returns
	-------
	order_quantity : float or ndarray
		Optimal order quantity (items). [:math:`Q^*`]
	cost : float or ndarray
		Optimal cost per unit time. [:math:`g^*`]


	**Equations Used** (equations (3.31) and (3.32)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda}{h(1-\\rho)}}

		g^* = \\sqrt{2K\\lambda h(1-\\rho)}

	where :math:`\\rho = \\lambda/\\mu`.

	**Example**:

	.. testsetup:: *

		from pyinv.eoq import *

	.. doctest::

		>>> economic_production_quantity(8, 0.225, 1300, 1700)
		(626.8084945889684, 33.183979125298336)

	**Example**:

	.. testsetup:: *

		from pyinv.eoq import *

	.. doctest::

		>>> economic_production_quantity([8, 20], [0.225, 1], [1300, 100], [1700, 200])
		(array([626.80849459,  89.4427191 ]), array([33.18397913, 44.72135955]))

	"""

	# Convert input parameters to numpy arrays.
	fixed_cost = np.array(fixed_cost)
	holding_cost = np.array(holding_cost)
	demand_rate = np.array(demand_rate)
	production_rate = np.array(production_rate)

	# Check that parameters are non-negative/positive.
	if not np.all(fixed_cost >= 0): raise ValueError("fixed_cost must be non-negative.")
	if not np.all(holding_cost > 0): raise ValueError( "holding_cost must be positive.")
	if not np.all(demand_rate >= 0): raise ValueError( "demand_rate must be non-negative.")
	if not np.all(production_rate > 0): raise ValueError( "production_rate must be positive.")

	# Check that parameters are singletons or same-size iterables.
	if not check_iterable_sizes([fixed_cost, holding_cost, demand_rate, production_rate]): raise ValueError("Input parameters must singletons or list-like objects of the same size.")

	# Check that demand rate < production rate.
	if not np.all(demand_rate < production_rate): raise ValueError("demand_rate must be less than production_rate.")

	# Calculate rho.
	rho = demand_rate / production_rate

	# Calculate optimal order quantity and cost.
	order_quantity = np.sqrt(
		2 * fixed_cost * demand_rate / (holding_cost * (1 - rho)))
	cost = order_quantity * holding_cost * (1 - rho)

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

		from pyinv.eoq import *

	.. doctest::

		>>> shared_fixed_cost = 600
		>>> individual_fixed_costs = [120, 840, 300]
		>>> holding_costs = [160, 20, 50]
		>>> demand_rates = [1, 1, 1]
		>>> joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)
		([3.103164454170876, 9.309493362512628, 3.103164454170876], 3.103164454170876, [1, 3, 1], 837.8544026261366)
	"""

	# TODO: unit tests

	# Check that parameters are positive.
	assert shared_fixed_cost >= 0, "shared_fixed_cost must be non-negative"
	assert np.all(np.array(individual_fixed_costs) >= 0), "individual_fixed_costs must be non-negative."
	assert np.all(np.array(holding_costs) > 0), "holding_costs must be non-negative."
	assert np.all(np.array(demand_rates) > 0), "demand_rates must be non-negative."
	assert len(individual_fixed_costs) == len(holding_costs) and len(holding_costs) == len(demand_rates), \
		"all lists must have the same length"

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

