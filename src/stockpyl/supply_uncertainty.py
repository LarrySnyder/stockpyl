# ===============================================================================
# stockpyl - supply_uncertainty Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

|sp| contains code to solve the following types of single-echelon inventory optimization problems
in the |mod_supply_uncertainty| module:

* Economic order quantity (EOQ)-based models
	- with disruptions
	- with yield uncertainty
* Newsvendor-based models
	- with disruptions
	- with yield uncertainty

.. note:: |fosct_notation|

.. seealso::

	For an overview of supply uncertainty in |sp|,
	see the :ref:`tutorial page for supply uncertainty<tutorial_su_page>`.



API Reference
-------------

"""

import numpy as np
from math import log
from scipy.stats import *

from stockpyl.optimization import golden_section_search
from stockpyl.loss_functions import *
from stockpyl.helpers import is_discrete_distribution


def eoq_with_disruptions(fixed_cost, holding_cost, stockout_cost, demand_rate,
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

	References
	----------
	M. Parlar and D. Berkin. Future supply uncertainty in EOQ models. *Naval Research Logistics*, 38 (1):107–121, 1991.

	E. Berk and A. Arreola-Risa. Note on “Future supply uncertainty in EOQ models”. *Naval Research Logistics*, 41(1):129–132, 1994.

	L. V. Snyder. A tight approximation for a continuousreview inventory model with supplier disruptions. *International Journal of Production Economics*, 155:91–108, 2014.

	**Example** (Example 9.1-9.2):

	.. testsetup:: *

		from stockpyl.supply_uncertainty import *

	.. doctest::

		>>> eoq_with_disruptions(8, 0.225, 5, 1300, 1.5, 14)
		(772.8110739983106, 173.95000257319708)

		>>> eoq_with_disruptions(8, 0.225, 5, 1300, 1.5, 14, approximate=True)
		(773.1432417118889, 173.957229385175)

	"""

	# Check parameters.
	if fixed_cost < 0: raise ValueError("fixed_cost must be non-negative")
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand_rate < 0: raise ValueError("demand_rate must be non-negative")
	if disruption_rate <= 0: raise ValueError("disruption_rate must be positive")
	if recovery_rate <= 0: raise ValueError("recovery_rate must be positive")

	# Calculate approximate order quantity. Even if exact order quantity is
	# requested, approximate quantity will be used for search bounds.
	psi_approx = (disruption_rate / (disruption_rate + recovery_rate))

	# Calculate approximate Q^*.
	order_quantity_approx = (math.sqrt((psi_approx * demand_rate * holding_cost) ** 2 + 2 * holding_cost * recovery_rate * (
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
		f = lambda Q: eoq_with_disruptions_cost(Q, fixed_cost,
												holding_cost, stockout_cost, demand_rate,
												disruption_rate, recovery_rate)
		lo = order_quantity_approx / 10
		hi = order_quantity_approx * 10
		order_quantity, cost = golden_section_search(f, lo, hi, verbose=False)

	return order_quantity, cost


def eoq_with_disruptions_cost(order_quantity, fixed_cost,
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

	References
	----------
	M. Parlar and D. Berkin. Future supply uncertainty in EOQ models. *Naval Research Logistics*, 38 (1):107–121, 1991.

	E. Berk and A. Arreola-Risa. Note on “Future supply uncertainty in EOQ models”. *Naval Research Logistics*, 41(1):129–132, 1994.

	L. V. Snyder. A tight approximation for a continuousreview inventory model with supplier disruptions. *International Journal of Production Economics*, 155:91–108, 2014.

	**Example** (Example 9.1):

	.. testsetup:: *

		from stockpyl.supply_uncertainty import *

	.. doctest::

		>>> eoq_with_disruptions_cost(700, 8, 0.225, 5, 1300, 1.5, 14)
		174.78711738886236

		>>> eoq_with_disruptions_cost(700, 8, 0.225, 5, 1300, 1.5, 14, approximate=True)
		174.80614234644133
	"""

	# Check that parameters are positive.
	if fixed_cost < 0: raise ValueError("fixed_cost must be non-negative")
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand_rate < 0: raise ValueError("demand_rate must be non-negative")
	if order_quantity <= 0: raise ValueError("order_quantity must be positive")
	if disruption_rate <= 0: raise ValueError("disruption_rate must be positive")
	if recovery_rate <= 0: raise ValueError("recovery_rate must be positive")

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


def newsvendor_with_disruptions(holding_cost, stockout_cost, demand, disruption_prob,
					  recovery_prob, base_stock_level=None):
	"""Solve the newsvendor problem with disruptions and deterministic demand, or (if
	``base_stock_level`` is supplied) calculate expected cost of given solution.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand : float
		Demand per period. [:math:`d`]
	disruption_prob : float
		Probability of disruption in period :math:`t+1` given that there is no
		disruption in period :math:`t`. [:math:`\\alpha`]
	recovery_prob : float
		Probability of no disruption in period :math:`t+1` given that there is a
		disruption in period :math:`t`. [:math:`\\beta`]
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [:math:`S^*`]
	cost : float
		Expected cost per period attained by ``base_stock_level``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``holding_cost``, ``stockout_cost``, or ``demand`` <= 0.
	ValueError
		If ``disruption_prob`` or ``recovery_prob`` is not in (0,1).


	**Equations Used** ((9.18), (9.14), and Lemma 9.2):

	.. math::

		S^* = d + dF^{-1}\\left(\\frac{p}{p+h}\\right)

	.. math::

		g(S) = \\sum_{n=0}^\\infty \\pi_n \\left[h\\left[S-(n+1)d\\right]^+ + p\\left[(n+1)d-S\\right]^+\\right],

	where

	.. math::

		\\pi_0 = \\frac{\\beta}{\\alpha+\\beta}

	.. math::

		\\pi_n = \\frac{\\alpha\\beta}{\\alpha+\\beta}(1-\\beta)^{n-1}, \\quad n \ge 1

	.. math::

		F(n) = 1 - \\frac{\\alpha}{\\alpha+\\beta}(1-\\beta)^n.

	**Example** (Example 9.3):

	.. testsetup:: *

		from stockpyl.supply_uncertainty import *

	.. doctest::

		>>> newsvendor_with_disruptions(0.25, 3, 2000, 0.04, 0.25)
		(8000, 2737.0689302470355)
		>>> newsvendor_with_disruptions(0.25, 3, 2000, 0.04, 0.25, base_stock_level=1200)
		(1200, 5710.344790717086)

	"""

	# Check parameters.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand <= 0: raise ValueError("demand must be positive")
	if disruption_prob <= 0 or disruption_prob >= 1: raise ValueError("disruption_prob must be between 0 and 1")
	if recovery_prob <= 0 or recovery_prob >= 1: raise ValueError("recovery_prob must be between 0 and 1")

	# Calculate gamma.
	gamma = stockout_cost / (stockout_cost + holding_cost)

	# Choose sufficiently large n that F(n) is close to 1 (and larger than gamma).
	max_gamma = max(1-1.0e-10, gamma)
	max_n = int(np.ceil(log((1 - max_gamma) *
							(disruption_prob + recovery_prob) / disruption_prob, 1 - recovery_prob)))

	# Calculate probability distribution.
	pi = np.zeros(max_n+1)
	F = np.zeros(max_n+1)
	pi[0] = recovery_prob / (disruption_prob + recovery_prob)
	F[0] = pi[0]
	for n in range(1, max_n+1):
		pi[n] = (disruption_prob * recovery_prob / (disruption_prob + recovery_prob)) * \
			(1 - recovery_prob)**(n-1)
		F[n] = 1 - (disruption_prob / (disruption_prob + recovery_prob)) * \
			(1 - recovery_prob)**n

	# Is S provided?
	if base_stock_level is None:
		# Calculate gamma.
		gamma = stockout_cost / (stockout_cost + holding_cost)

		# Calculate optimal base-stock level.
		n = 0
		while F[n] < gamma:
			n += 1
		base_stock_level = demand * (1 + n)

	# Calculate cost.
	cost = np.sum([pi[n] * (holding_cost * max(0, base_stock_level - (n+1) * demand)
						+ stockout_cost * max(0, (n+1) * demand - base_stock_level))
				   for n in range(max_n+1)])

	return base_stock_level, cost


def eoq_with_additive_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean,
					  yield_sd, order_quantity=None):
	"""Solve the EOQ problem with additive yield uncertainty and deterministic demand, or (if
	``order_quantity`` is supplied) calculate expected cost of given solution.

	Note that the optimal solution depends only on the mean and standard deviation
	of the yield distribution, not the distribution itself.

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	demand_rate : float
		Demand (items) per unit time. [:math:`d`]
	yield_mean : float
		Mean of yield distribution. [:math:`E[Y]`]
	yield_sd : float
		Standard deviation of yield distribution. [:math:`\\text{SD}[Y]`]
	order_quantity : float, optional
		Order quantity for cost evaluation. If supplied, no
		optimization will be performed. [:math:`Q`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (or order quantity supplied). [:math:`Q^*`]
	cost : float
		Expected cost per unit time attained by ``order_quantity``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``fixed_cost`` or ``demand_rate``, or if ``holding_cost`` <= 0.
	ValueError
		If ``yield_sd`` < 0.


	**Equations Used** ((9.23) and (9.22)):

	.. math::

		Q^* = \\sqrt{\\frac{2Kd}{h} + \\text{Var}[Y]} - E[Y]

	.. math::

		g(Q) = \\frac{2Kd + h\\text{Var}[Y]}{2(Q+E[Y])} + \\frac{h(Q+E[Y])}{2}

	**Example** (Example 9.4):

	.. testsetup:: *

		from stockpyl.supply_uncertainty import *

	.. doctest::

		>>> eoq_with_additive_yield_uncertainty(18500, 0.06, 75000, -15000, 9000)
		(230246.37046881882, 12914.78222812913)
		>>> eoq_with_additive_yield_uncertainty(18500, 0.06, 75000, -15000, 9000, order_quantity=300000)
		(300000, 13426.947368421053)
	"""

	# Check parameters.
	if fixed_cost < 0: raise ValueError("fixed_cost must be non-negative")
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if demand_rate < 0: raise ValueError("demand_rate must be non-negative")
	if yield_sd < 0: raise ValueError("yield_sd must be non-negative")

	# Is Q provided?
	if order_quantity is None:
		order_quantity = math.sqrt((2 * fixed_cost * demand_rate / holding_cost) + yield_sd**2) - yield_mean

	# Calculate cost.
	term1 = (2 * fixed_cost * demand_rate + holding_cost * yield_sd**2) / (2 * (order_quantity + yield_mean))
	term2 = holding_cost * (order_quantity + yield_mean) / 2
	cost = term1 + term2

	return order_quantity, cost


def eoq_with_multiplicative_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean,
					  yield_sd, order_quantity=None):
	"""Solve the EOQ problem with multiplicative yield uncertainty and deterministic demand, or (if
	``order_quantity`` is supplied) calculate expected cost of given solution.

	Note that the optimal solution depends only on the mean and standard deviation
	of the yield distribution, not the distribution itself.

	Parameters
	----------
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	demand_rate : float
		Demand (items) per unit time. [:math:`d`]
	yield_mean : float
		Mean of yield distribution. [:math:`E[Z]`]
	yield_sd : float
		Standard deviation of yield distribution. [:math:`\\text{SD}[Z]`]
	order_quantity : float, optional
		Order quantity for cost evaluation. If supplied, no
		optimization will be performed. [:math:`Q`]

	Returns
	-------
	order_quantity : float
		Optimal order quantity (or order quantity supplied). [:math:`Q^*`]
	cost : float
		Expected cost per unit time attained by ``order_quantity``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``fixed_cost`` or ``demand_rate``, or if ``holding_cost`` <= 0.
	ValueError
		If ``yield_sd`` < 0.


	**Equations Used** ((9.25) and (9.24)):

	.. math::

		Q^* = \\sqrt{\\frac{2Kd}{h(\\text{Var}[Z] + E[Z]^2)}}

	.. math::

		g(Q) = \\frac{Kd}{QE[Z]} + \\frac{hQ(\\text{Var}[Z] + E[Z]^2)}{2E[Z]}

	**Example** (Example 9.5):

	.. testsetup:: *

		from stockpyl.supply_uncertainty import *

	.. doctest::

		>>> eoq_with_multiplicative_yield_uncertainty(18500, 0.06, 75000, 0.8333, math.sqrt(0.0198))
		(254477.46130342316, 13086.16169098594)
		>>> eoq_with_multiplicative_yield_uncertainty(18500, 0.06, 75000, 0.8333, math.sqrt(0.0198), order_quantity=300000)
		(300000, 13263.770562822512)
	"""

	# Check parameters.
	if fixed_cost < 0: raise ValueError("fixed_cost must be non-negative")
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if demand_rate < 0: raise ValueError("demand_rate must be non-negative")
	if yield_sd < 0: raise ValueError("yield_sd must be non-negative")

	# Is Q provided?
	if order_quantity is None:
		order_quantity = math.sqrt((2 * fixed_cost * demand_rate) / (holding_cost * (yield_sd**2 + yield_mean**2)))

	# Calculate cost.
	term1 = fixed_cost * demand_rate / (order_quantity * yield_mean)
	term2 = holding_cost * order_quantity * (yield_sd**2 + yield_mean**2) / (2 * yield_mean)
	cost = term1 + term2

	return order_quantity, cost


def newsvendor_with_additive_yield_uncertainty(holding_cost, stockout_cost, demand,
											   yield_mean=None, yield_sd=None,
											   yield_distribution=None, loss_function=None,
											   base_stock_level=None):
	"""Solve the newsvendor problem with additive yield uncertainty and deterministic demand, or (if
	``base_stock_level`` is supplied) calculate expected cost of given solution.

	Either provide ``yield_mean`` and ``yield_sd`` to use a normal yield distribution,
	or provide ``yield_distribution`` as a frozen ``rv_continuous`` or ``rv_discrete`` object.
	If ``yield_distribution`` is provided, then loss functions are calculated using
	``loss_functions.continuous_loss()`` or ``loss_functions.discrete_loss()``,
	unless ``loss_function`` is provided. (Loss functions are used in expected-cost calculation.)

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand : float
		Demand per period. [:math:`d`]
	yield_mean : float, optional
		Mean of yield distribution. [:math:`E[Y]`]
	yield_sd : float, optional
		Standard deviation of yield distribution. [:math:`\\text{SD}[Y]`]
	yield_distribution : rv_continuous or rv_discrete, optional
		Yield distribution. Required if ``yield_mean`` or ``yield_sd`` is ``None``.
	loss_function : function, optional
		Function that takes a single argument and returns a tuple consisting
		of the loss function and complementary loss function value of that argument.
		Ignored if ``yield_distribution`` is ``None``.
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [:math:`S^*`]
	cost : float
		Expected cost per unit time attained by ``base_stock_level``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``holding_cost``, ``stockout_cost``, or ``demand`` <= 0.
	ValueError
		If ``yield_sd`` <= 0.
	ValueError
		If (``yield_mean`` is ``None`` or ``yield_sd`` is ``None``) and
		``yield_distribution`` is ``None``.


	**Equations Used** ((9.28) and (9.27)):

	.. math::

		S^* = d - F_Y^{-1}\\left(\\frac{h}{h+p}\\right)

	.. math::

		g(S) = p\\bar{n}(d-S) + hn(d-S),

	where :math:`n(\\cdot)` and :math:`\\bar{n}(\\cdot)` are the loss function
	and complementary loss function, respectively, of the yield distribution.

	**Example** (Example 9.6):

	.. testsetup:: *

		from stockpyl.supply_uncertainty import *

	Using generic function to calculate loss functions:

	.. doctest::

		>>> from scipy.stats import uniform
		>>> newsvendor_with_additive_yield_uncertainty(15, 75, 1.5e6, yield_distribution=uniform(-500000, 1000000))
		(1833333.3333333335, 6249999.997499999)

	Using ``uniform_loss()`` to calculate loss functions, which is more accurate:

	.. doctest::

		>>> from stockpyl.loss_functions import uniform_loss
		>>> loss_function = lambda x: uniform_loss(x, -500000, 500000)
		>>> newsvendor_with_additive_yield_uncertainty(15, 75, 1.5e6, yield_distribution=uniform(-500000, 1000000), loss_function=loss_function)
		(1833333.3333333335, 6250000.000000001)
	"""

	# Check parameters.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand <= 0: raise ValueError("demand must be positive")
	if (yield_sd or 0) < 0: raise ValueError("yield_sd must be non-negative")
	if (yield_mean is None or yield_sd is None) and yield_distribution is None: \
		raise ValueError("Must provide either yield_mean and yield_sd or yield_distribution")

	# Is S provided?
	if base_stock_level is None:
		# Calculate critical ratio.
		crit_ratio = holding_cost / (holding_cost + stockout_cost)

		# Determine base-stock level.
		if yield_mean is not None and yield_sd is not None:
			# Normal yield.
			base_stock_level = demand - norm.ppf(crit_ratio, yield_mean, yield_sd)
		else:
			# Other yield distribution.
			base_stock_level = demand - yield_distribution.ppf(crit_ratio)

		# Calculate R.
		R = demand - base_stock_level

		# Calculate loss functions.
		if yield_mean is not None and yield_sd is not None:
			n, n_bar = normal_loss(R, yield_mean, yield_sd)
		else:
			# Is loss function provided?
			if loss_function is not None:
				n, n_bar = loss_function(R)
			else:
				if is_discrete_distribution(yield_distribution):
					n, n_bar = discrete_loss(R, yield_distribution)
				else:
					n, n_bar = continuous_loss(R, yield_distribution)

	# Calculate cost.
	cost = stockout_cost * n_bar + holding_cost * n

	return base_stock_level, cost

