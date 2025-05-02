# ===============================================================================
# stockpyl - eoq Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_eoq| module contains code for solving the economic order quantity
(EOQ) problem and some of its variants.

.. note:: |fosct_notation|

.. seealso::

	For an overview of single-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for single-echelon inventory optimization<tutorial_seio_page>`.


API Reference
-------------
"""

import numpy as np
import math


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
		order_quantity = math.sqrt(2 * fixed_cost * demand_rate / holding_cost)
		cost = order_quantity * holding_cost
	else:
		# Calculate cost.
		cost = fixed_cost * demand_rate / order_quantity + holding_cost * order_quantity / 2

	return order_quantity, cost


def economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs):
    """Solve the economic order quantity (EOQ) problem with all-units quantity discounts.

    In the EOQ problem with all-units quantity discounts, the unit cost of all items in an order is discounted based on the order quantity, 
    according to a piecewise constant function defined by the breakpoints and unit costs.

    Parameters
    ----------
    fixed_cost : float
        Fixed cost per order. [:math:`K`]
    holding_cost_rate : float
        Holding cost rate per item per unit time as a percentage of the purchase cost. [:math:`i`]
    demand_rate : float
        Demand (items) per unit time. [:math:`\\lambda`]
    breakpoints : list of float
        Breakpoints for quantity discounts, in increasing order starting with 0. [:math:`[b_0, b_1, \\ldots, b_n]` where :math:`b_0 = 0`]
    unit_costs : list of float
        Unit cost for each discount region. [:math:`[c_0, c_1, \\ldots, c_n]`]

    Returns
    -------
    order_quantity : float
        Optimal order quantity (items). [:math:`Q^*`]
    region : int
        The index of the discount region used (i.e., the index :math:`j` such that :math:`b_j \\leq Q^* < b_{j+1}`). [:math:`j^*`]
    cost : float
        Cost per unit time attained by ``order_quantity`` in the chosen region. [:math:`g^*`]

        
    **Notes**:
    
    1. For each region :math:`j`, computes the EOQ assuming the unit cost :math:`c_j`: :math:`Q^*_j = \\sqrt{\\frac{2K\\lambda}{i c_j}}`.
    2. Identifies candidates, which include:
     	- Each :math:`Q^*_j` that is *realizable* (i.e., falls within its region’s bounds: :math:`b_j \\leq Q^*_j < b_{j+1}` for :math:`j < n`, or :math:`Q^*_j \\geq b_j` for :math:`j = n`).
        - Each breakpoint :math:`b_k` for :math:`k \\geq 1`, evaluated in region :math:`k`.
    3. Evaluates the total cost at each candidate and selects the one with the lowest cost.

    **Equations Used** (equations (3.18) and (3.19)):
    
    For each region :math:`j`, the unconstrained EOQ is:

    .. math::

        Q^*_j = \\sqrt{\\frac{2K\\lambda}{i c_j}}

    The total cost for an order quantity :math:`Q` in region :math:`j` is:

    .. math::

        g_j(Q) = c_j \\lambda + \\frac{K \\lambda}{Q} + \\frac{i c_j Q}{2}

    **Example**:
    
    .. testsetup:: *

        from stockpyl.eoq import *

    .. doctest::

        >>> fixed_cost = 200
        >>> holding_cost_rate = 0.20
        >>> demand_rate = 1000
        >>> breakpoints = [0, 200, 500]
        >>> unit_costs = [500, 475, 450]
        >>> economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)
        (500, 2, 472900.0)
    """
    # Input validation
    if fixed_cost < 0:
        raise ValueError("fixed_cost must be non-negative.")
    if holding_cost_rate <= 0:
        raise ValueError("holding_cost_rate must be positive.")
    if demand_rate < 0:
        raise ValueError("demand_rate must be non-negative.")
    if not isinstance(breakpoints, list) or len(breakpoints) < 1 or breakpoints[0] != 0:
        raise ValueError("breakpoints must be a list starting with 0.")
    if not all(isinstance(b, (int, float)) and b >= 0 for b in breakpoints):
        raise ValueError("breakpoints must contain non-negative numbers.")
    if not all(breakpoints[i] < breakpoints[i + 1] for i in range(len(breakpoints) - 1)):
        raise ValueError("breakpoints must be strictly increasing.")
    if not isinstance(unit_costs, list) or len(unit_costs) != len(breakpoints):
        raise ValueError("unit_costs must be a list with the same length as breakpoints.")
    if not all(isinstance(c, (int, float)) and c > 0 for c in unit_costs):
        raise ValueError("unit_costs must contain positive numbers.")

    # Define the cost function for a given Q in region j.
    def g(Q, j):
        return unit_costs[j] * demand_rate + fixed_cost * demand_rate / Q + holding_cost_rate * unit_costs[j] * Q / 2

    # Calculate unconstrained EOQ for each region.
    Q_star = [math.sqrt(2 * fixed_cost * demand_rate / (holding_cost_rate * unit_costs[j])) for j in range(len(unit_costs))]

    # Collect candidates: realizable Q*_j and breakpoints.
    candidates = []
    n = len(breakpoints) - 1  # Index of the last region
    for j in range(len(unit_costs)):
        Q_j = Q_star[j]
        # Check if Q*_j is realizable.
        is_realizable = (j == n and Q_j >= breakpoints[j]) or (j < n and breakpoints[j] <= Q_j < breakpoints[j + 1])
        if is_realizable:
            cost = g(Q_j, j)
            candidates.append((Q_j, j, cost))
    # Add breakpoints b_k for k >= 1 as candidates.
    for k in range(1, len(breakpoints)):
        Q = breakpoints[k]
        cost = g(Q, k)  # Q = b_k falls in region k since intervals are [b_k, b_{k+1})
        candidates.append((Q, k, cost))

    # Ensure there are candidates (should always be true since breakpoints >= 1 exist).
    if not candidates:
        raise ValueError("No feasible order quantity found.")

    # Select the candidate with the lowest cost.
    order_quantity, region, cost = min(candidates, key=lambda x: x[2])

    return order_quantity, region, cost


def economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs):
    """Solve the economic order quantity (EOQ) problem with incremental quantity discounts.

    In the EOQ problem with incremental quantity discounts, the unit cost decreases incrementally for units above each breakpoint. 
    For an order quantity :math:`Q` in region :math:`j` (i.e., :math:`b_j \\leq Q < b_{j+1}`), the purchase cost is the sum of the 
    costs of units up to :math:`b_j` plus the cost of additional units at :math:`c_j`.

    Parameters
    ----------
    fixed_cost : float
        Fixed cost per order. [:math:`K`]
    holding_cost_rate : float
        Holding cost rate per item per unit time as a percentage of the purchase cost. [:math:`i`]
    demand_rate : float
        Demand (items) per unit time. [:math:`\\lambda`]
    breakpoints : list of float
        Breakpoints for quantity discounts, in increasing order starting with 0. [:math:`[b_0, b_1, \\ldots, b_n]` where :math:`b_0 = 0`]
    unit_costs : list of float
        Unit cost for incremental units in each discount region. [:math:`[c_0, c_1, \\ldots, c_n]`]

    Returns
    -------
    order_quantity : float
        Optimal order quantity (items). [:math:`Q^*`]
    region : int
        The index of the discount region used (i.e., the index :math:`j` such that :math:`b_j \\leq Q^* < b_{j+1}`). [:math:`j^*`]
    cost : float
        Cost per unit time attained by ``order_quantity`` in the chosen region. [:math:`g^*`]


	**Notes**:
    
    1. For each region :math:`j`, computes a modified EOQ based on the incremental cost structure: :math:`Q^*_j = \\sqrt{\\frac{2(K + \\bar{c}_j)\\lambda}{i c_j}}`, where :math:`\\bar{c}_j` accounts for the fixed cost offset due to incremental discounts.
    2. Checks if each :math:`Q^*_j` is *realizable* (i.e., :math:`b_j \\leq Q^*_j < b_{j+1}` for :math:`j < n`, or :math:`Q^*_j \\geq b_j` for :math:`j = n`).
    3. Among realizable :math:`Q^*_j`, selects the one with the lowest total cost.

    **Equations Used** (equations (3.20), (3.21) and (3.22)):
    
    For :math:`Q` in region :math:`j`, the purchase cost is:

    .. math::

        C(Q) = \\sum_{i=0}^{j-1} c_i (b_{i+1} - b_i) + c_j (Q - b_j) = \\bar{c}_j + c_j Q

    where:

    .. math::

        \\bar{c}_j = \\sum_{i=0}^{j-1} c_i (b_{i+1} - b_i) - c_j b_j \\text{ if } j > 0, \\text{ else } 0

    The unconstrained EOQ for region :math:`j` is:

    .. math::

        Q^*_j = \\sqrt{\\frac{2(K + \\bar{c}_j)\\lambda}{i c_j}}

    The total cost is:

    .. math::
    
    	g_j\\left(Q_j^*\\right) = c_j \\lambda + \\frac{i \\bar{c}_j}{2} + \\sqrt{2\\left(K+\\bar{c}_j\\right) \\lambda i c_j}
 
    or
    
    .. math::
    
    	g_j(Q) = c_j \\lambda + \\frac{i \\bar{c}_j}{2} + \\frac{(K + \\bar{c}_j)\\lambda}{Q} + \\frac{i c_j Q}{2}

    **Example**:
    
    .. testsetup:: *

        from stockpyl.eoq import *

    .. doctest::

        >>> fixed_cost = 150
        >>> holding_cost_rate = 0.25
        >>> demand_rate = 2400
        >>> breakpoints = [0, 300, 600]
        >>> unit_costs = [100, 90, 80]
        >>> economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)
        (1481.8906842274164, 2, 222762.8136845483)
    """
    # Input validation
    if fixed_cost < 0:
        raise ValueError("fixed_cost must be non-negative.")
    if holding_cost_rate <= 0:
        raise ValueError("holding_cost_rate must be positive.")
    if demand_rate < 0:
        raise ValueError("demand_rate must be non-negative.")
    if not isinstance(breakpoints, list) or len(breakpoints) < 1 or breakpoints[0] != 0:
        raise ValueError("breakpoints must be a list starting with 0.")
    if not all(isinstance(b, (int, float)) and b >= 0 for b in breakpoints):
        raise ValueError("breakpoints must contain non-negative numbers.")
    if not all(breakpoints[i] < breakpoints[i + 1] for i in range(len(breakpoints) - 1)):
        raise ValueError("breakpoints must be strictly increasing.")
    if not isinstance(unit_costs, list) or len(unit_costs) != len(breakpoints):
        raise ValueError("unit_costs must be a list with the same length as breakpoints.")
    if not all(isinstance(c, (int, float)) and c > 0 for c in unit_costs):
        raise ValueError("unit_costs must contain positive numbers.")

    # Define helper functions.
    def c_bar(j):
        """Calculate the fixed cost offset for region j."""
        if j == 0:
            return 0
        return sum(unit_costs[i] * (breakpoints[i + 1] - breakpoints[i]) for i in range(j)) - unit_costs[j] * breakpoints[j]

    def g(Q, j):
        """Calculate total cost for Q in region j."""
        cb = c_bar(j)
        return unit_costs[j] * demand_rate + holding_cost_rate * cb / 2 + (fixed_cost + cb) * demand_rate / Q + holding_cost_rate * unit_costs[j] * Q / 2

    # Calculate modified EOQ for each region.
    Q_star = [math.sqrt(2 * (fixed_cost + c_bar(j)) * demand_rate / (holding_cost_rate * unit_costs[j])) for j in range(len(unit_costs))]

    # Collect realizable Q*_j.
    candidates = []
    n = len(breakpoints) - 1  # Index of the last region
    for j in range(len(unit_costs)):
        Q_j = Q_star[j]
        # Check if Q*_j is realizable
        is_realizable = (j == n and Q_j >= breakpoints[j]) or (j < n and breakpoints[j] <= Q_j < breakpoints[j + 1])
        if is_realizable:
            cost = g(Q_j, j)
            candidates.append((Q_j, j, cost))

    # Check if there are any realizable solutions.
    if not candidates:
        raise ValueError("No realizable order quantity found.")

    # Select the candidate with the lowest cost.
    order_quantity, region, cost = min(candidates, key=lambda x: x[2])

    return order_quantity, region, cost


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
		order_quantity = math.sqrt(2 * fixed_cost * demand_rate * (holding_cost + stockout_cost)
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
		order_quantity = math.sqrt(
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
			m = math.sqrt((individual_fixed_costs[n] / (holding_costs[n] * demand_rates[n])) * const)
			m = max(1, int(round(m)))

		order_multiples.append(m)

	# Calculate a few terms we'll need below.
	term1 = shared_fixed_cost + float(np.sum(np.divide(individual_fixed_costs, order_multiples)))
	term2 = float(np.sum([holding_costs[n] * order_multiples[n] * demand_rates[n] for n in range(num_prod)]))

	# Calculate base cycle time.
	numer = 2 * term1
	denom = term2
	base_cycle_time = math.sqrt(numer / denom)

	# Calculate order quantities.
	order_quantities = [base_cycle_time * order_multiples[n] * demand_rates[n] for n in range(num_prod)]

	# Calculate average cost.
	avg_fixed_cost = term1 / base_cycle_time
	avg_holding_cost = (base_cycle_time / 2) * term2
	cost = avg_fixed_cost + avg_holding_cost

	return order_quantities, base_cycle_time, order_multiples, cost

