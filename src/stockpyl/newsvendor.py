# ===============================================================================
# stockpyl - newsvendor Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc


Overview 
--------


The |mod_newsvendor| module contains code for solving the newsvendor
problem and some of its variants.

.. note:: |fosct_notation|

.. seealso::

	For an overview of single-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for single-echelon inventory optimization<tutorial_seio_page>`.


API Reference
-------------
"""


from scipy import stats
from scipy.optimize import brentq
import numpy as np

import stockpyl.loss_functions as lf
from stockpyl.helpers import *


def newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd,
					  lead_time=0, base_stock_level=None):
	"""Solve the newsvendor problem with normal distribution, or (if
	``base_stock_level`` is supplied) calculate expected cost of given solution.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand_mean : float
		Mean demand per period. [:math:`\\mu`]
	demand_sd : float
		Standard deviation of demand per period. [:math:`\\sigma`]
	lead_time : int, optional
		Lead time. Default = 0. [:math:`L`]
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
		If ``holding_cost`` <= 0 or ``stockout_cost`` <= 0.
	ValueError
		If ``demand_mean`` <= 0 or ``demand_sd`` <= 0.


	**Equations Used** (equations (4.30), (4.37), and (4.24), modified for non-zero
	lead time):

	.. math::

		S^* = \\mu + z_{\\alpha}\\sigma

		g^* = (h+p)\phi(z_{\\alpha})\\sigma

	where :math:`\\mu` and :math:`\\sigma` are the lead-time demand mean
	and standard deviation, and :math:`\\alpha = p/(h+p)`,

	or

	.. math::

		g(S) = h\\bar{n}(S) + pn(S),

	where :math:`n(\cdot)` and :math:`\\bar{n}(\cdot)` are the lead-time demand
	loss and complementary loss functions.

	**Example** (Example 4.3):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> newsvendor_normal(0.18, 0.70, 50, 8)
		(56.60395592743389, 1.9976051931766445)

	"""

	# Check that parameters are positive.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand_mean <= 0: raise ValueError("mean must be positive")
	if demand_sd <= 0: raise ValueError("demand_sd must be positive")

	# Calculate lead-time demand parameters.
	ltd_mean = demand_mean * (lead_time + 1)
	ltd_sd = demand_sd * math.sqrt(lead_time + 1)

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


def newsvendor_normal_cost(base_stock_level, holding_cost, stockout_cost,
						   demand_mean, demand_sd, lead_time=0):
	"""Calculate the cost of using ``base_stock_level`` as the solution to the
	newsvendor problem with normal distribution.

	Parameters
	----------
	base_stock_level : float
		Base-stock level for cost evaluation. [:math:`S`]
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand_mean : float
		Mean demand per period. [:math:`\\mu`]
	demand_sd : float
		Standard deviation of demand per period. [:math:`\\sigma`]
	lead_time : int, optional
		Lead time. Default = 0. [:math:`L`]

	Returns
	-------
	cost : float
		Cost per period attained by ``base_stock_level``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``holding_cost`` <= 0 or ``stockout_cost`` <= 0.
	ValueError
		If ``demand_mean`` <= 0 or ``demand_sd`` <= 0.


	**Equations Used** (equation (4.24)):

	.. math::

		g(S) = h\\bar{n}(S) + pn(S),

	where :math:`n(\cdot)` and :math:`\\bar{n}(\cdot)` are the lead-time demand
	loss and complementary loss functions.

	**Example** (Example 4.1):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> newsvendor_normal_cost(60, 0.18, 0.70, 50, 8)
		2.156131552870387

	"""

	# Check that parameters are positive.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand_mean <= 0: raise ValueError("mean must be positive")
	if demand_sd <= 0: raise ValueError("demand_sd must be positive")

	# Calculate lead-time demand parameters.
	ltd_mean = demand_mean * (lead_time + 1)
	ltd_sd = demand_sd * math.sqrt(lead_time + 1)

	# Calculate loss functions.
	n, n_bar = lf.normal_loss(base_stock_level, ltd_mean, ltd_sd)

	# Calculate cost.
	cost = holding_cost * n_bar + stockout_cost * n

	return cost


def newsvendor_poisson(holding_cost, stockout_cost, demand_mean,
					  base_stock_level=None):
	"""Solve the newsvendor problem with Poisson distribution, or (if
	``base_stock_level`` is supplied) calculate cost of given solution.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand_mean : float
		Mean demand per period. [:math:`\\mu`]
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [:math:`S^*`]
	cost : float
		Cost per period attained by ``base_stock_level``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``holding_cost`` <= 0 or ``stockout_cost`` <= 0.
	ValueError
		If ``demand_mean`` <= 0.
	ValueError
		If ``base_stock_level`` is supplied and is not an integer.


	**Equations Used**:

	.. math::

		S^* = \\text{smallest } S \\text{ such that } F(S) \\ge \\frac{p}{h+p}

		g(S^*) = h\\bar{n}(S^*) + pn(S^*)

	or

	.. math::

		g(S) = h\\bar{n}(S) + pn(S),

	where :math:`F(\\cdot)`, :math:`n(\\cdot)`, and :math:`\\bar{n}(\\cdot)` are
	the Poisson cdf, loss function, and complementary loss function,
	respectively.

	**Example**:

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> newsvendor_poisson(0.18, 0.70, 50)
		(56.0, 1.797235211809178)

	"""

	# Check that parameters are positive.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand_mean <= 0: raise ValueError("mean must be positive")
	if base_stock_level is not None and not is_integer(base_stock_level):
		raise ValueError("base_stock_level must be an integer (or None)")

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = stockout_cost / (stockout_cost + holding_cost)

		# Calculate optimal order quantity and cost.
		base_stock_level = stats.poisson.ppf(alpha, demand_mean)

	# Calculate loss functions.
	n, n_bar = lf.poisson_loss(base_stock_level, demand_mean)

	# Calculate cost.
	cost = holding_cost * n_bar + stockout_cost * n

	return base_stock_level, cost


def newsvendor_poisson_cost(base_stock_level, holding_cost, stockout_cost,
						   demand_mean):
	"""Calculate the cost of using ``base_stock_level`` as the solution to the
	newsvendor problem with Poisson distribution.

	Parameters
	----------
	base_stock_level : float
		Base-stock level for cost evaluation. [:math:`S`]
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand_mean : float
		Mean demand per period. [:math:`\\mu`]
	lead_time : int, optional
		Lead time. Default = 0. [:math:`L`]

	Returns
	-------
	cost : float
		Cost per period attained by ``base_stock_level``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``holding_cost`` <= 0 or ``stockout_cost`` <= 0.
	ValueError
		If ``demand_mean`` <= 0.
	ValueError
		If ``base_stock_level`` is not an integer.


	**Equations Used** (equation (4.6)):

	.. math::

		g(S) = h\\bar{n}(S) + pn(S),

	where :math:`n(\cdot)` and :math:`\\bar{n}(\cdot)` are the lead-time demand
	loss and complementary loss functions.


	**Example** (Example 4.1):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> newsvendor_poisson_cost(56, 0.18, 0.70, 50)
		1.797235211809178

	"""

	# Check that parameters are positive.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if demand_mean <= 0: raise ValueError("mean must be positive")
	if not is_integer(base_stock_level): raise ValueError("base_stock_level must be an integer")

	# Calculate loss functions.
	n, n_bar = lf.poisson_loss(base_stock_level, demand_mean)

	# Calculate cost.
	cost = holding_cost * n_bar + stockout_cost * n

	return cost


def newsvendor_continuous(holding_cost, stockout_cost, demand_distrib=None,
						  demand_pdf=None, base_stock_level=None):
	"""Solve the newsvendor problem with generic continuous distribution, or (if
	``base_stock_level`` is supplied) calculate cost of given solution.

	Must provide either ``rv_continuous`` distribution (in ``demand_distrib``) or
	demand pdf (in ``demand_pdf``, as a function).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand_distrib : rv_continuous, optional
		Demand distribution object.
	demand_pdf : function, optional
		Demand pdf, as a function. Ignored if ``demand_distrib`` is not
		``None``. [:math:`f(\\cdot)`]
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [:math:`S^*`]
	cost : float
		Cost per period attained by ``base_stock_level``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``holding_cost`` <= 0 or ``stockout_cost`` <= 0.
	ValueError
		If ``demand_distrib`` and ``demand_pdf`` are both ``None``.


	**Equations Used** (equations (4.27) and (4.24)):

	.. math::

		S^* = F^{-1}\\left(\\frac{p}{h+p}\\right)

		g(S) = h\\bar{n}(S^*) + pn(S)

	where :math:`F(\\cdot)`, :math:`n(\\cdot)`, and :math:`\\bar{n}(\\cdot)` are
	the demand cdf, loss function, and complementary loss function,
	respectively.

	**Example** (Example 4.3):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> from scipy.stats import norm
		>>> demand_distrib = norm(50, 8)
		>>> newsvendor_continuous(0.18, 0.70, demand_distrib)
		(56.60395592743389, 1.997605188935892)
		>>> newsvendor_continuous(0.18, 0.70, demand_distrib, base_stock_level=40)
		(40, 7.35613154776623)

	**Example** (Problem 4.8(b)):

	.. doctest::

		>>> from scipy.stats import lognorm
		>>> demand_distrib = lognorm(0.3, 0, np.exp(6))
		>>> newsvendor_continuous(1, 0.1765, demand_distrib)
		(295.6266448071368, 29.44254351324322)

	"""

	# Check that parameters are positive.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")

	# Check that either distribution or pmf have been supplied.
	if demand_distrib is None and demand_pdf is None: raise ValueError("must provide demand_distrib or demand_pdf")

	# For now, raise error if only demand_pdf is provided. TODO: (Need to add this
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
	"""Solve the newsvendor problem with generic discrete distribution, or (if
	``base_stock_level`` is supplied) calculate cost of given solution.

	Must provide either ``rv_discrete`` distribution (in ``demand_distrib``) or
	demand pmf (in ``demand_pmf``, as a dict).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	demand_distrib : rv_discrete, optional
		Demand distribution object.
	demand_pmf : dict, optional
		Demand pmf, as a dict in which keys are possible demand values and
		values are their probabilities. Ignored if ``demand_distrib`` is
		not ``None``. [:math:`f(\\cdot)`]
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [:math:`S^*`]
	cost : float
		Cost per period attained by ``base_stock_level``. [:math:`g^*`]

	Raises
	------
	ValueError
		If ``holding_cost`` <= 0 or ``stockout_cost`` <= 0.
	ValueError
		If ``demand_distrib`` and ``demand_pdf`` are both ``None``.


	**Equations Used**:

	.. math::

		S^* = \\text{smallest } S \\text{ such that } F(S) \\ge \\frac{p}{h+p}

		g(S) = h\\bar{n}(S^*) + pn(S)

	where :math:`F(\\cdot)`, :math:`n(\\cdot)`, and :math:`\\bar{n}(\\cdot)` are
	the demand cdf, loss function, and complementary loss function,
	respectively.

	**Example** (Example 4.7):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

			>>> from scipy.stats import poisson
			>>> demand_distrib = poisson(6)
			>>> newsvendor_discrete(1, 4, demand_distrib)
			(8.0, 3.5701069457709416)
			>>> newsvendor_discrete(1, 4, demand_distrib, base_stock_level=5)
			(5, 6.590296024616343)

	.. doctest::

		>>> from scipy.stats import poisson
		>>> d = range(0, 41)
		>>> f = [poisson.pmf(d_val, 6) for d_val in d]
		>>> demand_pmf = dict(zip(d, f))
		>>> newsvendor_discrete(1, 4, demand_pmf=demand_pmf)
		(8, 3.570106945770941)

	"""

	# Check that parameters are positive.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost < 0: raise ValueError("stockout_cost must be non-negative")

	# Check that either distribution or pmf have been supplied.
	if demand_distrib is None and demand_pmf is None: raise ValueError("must provide demand_distrib or demand_pmf")

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
		if not is_integer(base_stock_level): raise ValueError("base_stock_level must be an integer")

	# Calculate loss functions.
	n, n_bar = lf.discrete_loss(base_stock_level, demand_distrib, demand_pmf)

	# Calculate cost.
	cost = holding_cost * n_bar + stockout_cost * n

	return base_stock_level, cost


def myopic(
		holding_cost,
		stockout_cost,
		purchase_cost,
		purchase_cost_next_per,
		demand_mean,
		demand_sd,
		discount_factor=1.0,
		base_stock_level=None):
	"""Find the optimizer of the myopic cost function, or (if ``base_stock_level``
	is supplied) calculate the cost of given solution. Assumes demand is normally distributed.

	The myopic cost function is denoted :math:`G_i(y)` in Veinott (1966) and
	as :math:`C^+(t,y)` in Zipkin (2000). It is not used in |fosct|, 
	but the function is given in terms of Snyder-Shen notation below.

	Parameters are singleton values for the current period, not arrays.

	Parameters
	----------
	holding_cost : float
		Holding cost in the current period. [:math:`h`]
	stockout_cost : float
		Stockout cost in the current period. [:math:`p`]
	purchase_cost : float
		Purchase cost in the current period. [:math:`c`]
	purchase_cost_next_per : float
		Purchase cost in the next period. [:math:`c_{t+1}`]
	demand_mean : float
		Mean demand in the current period. [:math:`\\mu`]
	demand_sd : float
		Standard deviation of demand in the current period. [:math:`\\sigma`]
	discount_factor : float, optional
		Discount factor in the current period, in :math:`(0,1]`.
		Default = 1. [:math:`\\gamma`]
	base_stock_level : float, optional
		Base-stock level for cost evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock-level (or base-stock level supplied). [:math:`S^*`]
	cost : float
		The myopic cost attained by ``base_stock_level``. [:math:`G_t(S^*)`]

	Raises
	------
	ValueError
		If :math:`-h_t > c_t - \\gamma c_{t+1}` or :math:`c_t - \\gamma c_{t+1} > p_t`.


	**Equation Used**:

	.. math::

		S^* = F^{-1}\\left(\\frac{p - c^+}{p + h}\\right)

		c^+ = c_t - \\gamma c_{t+1}

		G_t(y) = c_ty + g_t(y) - \\gamma_tc_{t+1}(y - E[D_t]),

	where :math:`g_t(\\cdot)` is the newsvendor cost function for period :math:`t`.


	References
	----------
	A. F. Veinott, Jr., On the Optimality of :math:`(s,S)` Inventory Policies:
	New Conditions and a New Proof, *J. SIAM Appl. Math* 14(5), 1067-1083 (1966).

	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example** (Example 4.1):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> myopic(0.18, 0.70, 0.3, 0.35, 50, 8, 0.98)
		(58.09891883213067, 16.682411764618777)
		>>> myopic(0.18, 0.70, 0.3, 0.35, 50, 8, 0.98, base_stock_level=62)
		(62, 16.850319828088736)

	"""

	# Calculate c_plus.
	c_plus = purchase_cost - discount_factor * purchase_cost_next_per

	# Validate c_plus.
	if c_plus < -holding_cost or c_plus > stockout_cost:
		raise ValueError("myopic() requires -h_t <= c_t - gamma * c_{t+1} <= p_t")

	# Is S provided?
	if base_stock_level is None:
		# Set critical ratio.
		critical_ratio = (stockout_cost - c_plus) / (stockout_cost + holding_cost)

		# Set base_stock_level to minimizer of G_t(y). (It could be found numerically
		# using myopic_cost(), but it's faster to find it this way.)
		base_stock_level = stats.norm.ppf(critical_ratio, demand_mean, demand_sd)

	# Calculate G_t(base_stock_level).
	cost = myopic_cost(base_stock_level, holding_cost, stockout_cost,
		purchase_cost, purchase_cost_next_per, demand_mean, demand_sd, discount_factor)

	return base_stock_level, cost


def myopic_cost(
		base_stock_level,
		holding_cost,
		stockout_cost,
		purchase_cost,
		purchase_cost_next_per,
		demand_mean,
		demand_sd,
		discount_factor=1.0):
	"""Calculate "myopic" cost function. Assumes demand is normally distributed.

	The myopic cost function is denoted :math:`G_i(y)` in Veinott (1966) and
	as :math:`C^+(t,y)` in Zipkin (2000). It is not used in |fosct|, 
	but the function is given in terms of Snyder-Shen notation below.

	Parameters are singleton values for the current period, not arrays.

	Parameters
	----------
	base_stock_level : float
		Base-stock level to calculate cost for. [:math:`S`]
	holding_cost : float
		Holding cost in the current period. [:math:`h`]
	stockout_cost : float
		Stockout cost in the current period. [:math:`p`]
	purchase_cost : float
		Purchase cost in the current period. [:math:`c`]
	purchase_cost_next_per : float
		Purchase cost in the next period. [:math:`c_{t+1}`]
	demand_mean : float
		Mean demand in the current period. [:math:`\\mu`]
	demand_sd : float
		Standard deviation of demand in the current period. [:math:`\\sigma`]
	discount_factor : float, optional
		Discount factor in the current period, in :math:`(0,1]`.
		Default = 1. [:math:`\\gamma`]

	Returns
	-------
	cost : float
		The myopic cost.


	**Equation Used**:

	.. math::

		G_t(y) = c_ty + g_t(y) - \\gamma_tc_{t+1}(y - E[D_t]),

	where :math:`g_t(\\cdot)` is the newsvendor cost function for period :math:`t`.


	References
	----------
	A. F. Veinott, Jr., On the Optimality of :math:`(s,S)` Inventory Policies:
	New Conditions and a New Proof, *J. SIAM Appl. Math* 14(5), 1067-1083 (1966).

	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example** (Example 4.1):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> myopic_cost(60, 0.18, 0.70, 0.3, 0.35, 50, 8, 0.98)
		16.726131552870388

	"""

	# Calculate newsvendor cost.
	g = newsvendor_normal_cost(base_stock_level, holding_cost, stockout_cost,
			demand_mean, demand_sd)

	return purchase_cost * base_stock_level + g \
		- discount_factor * purchase_cost_next_per * (base_stock_level - demand_mean)


def set_myopic_cost_to(
		cost,
		holding_cost,
		stockout_cost,
		purchase_cost,
		purchase_cost_next_per,
		demand_mean,
		demand_sd,
		discount_factor=1.0,
		left_half=True):
	"""Find the value of :math:`y` such that :math:`G_t(y)`
	equals ``cost``, where :math:`G_t(\\cdot)` is the myopic cost function
	for the current period, given by ``myopic_cost()``. Assumes demand is normally distrbuted.

	If ``left_half`` is ``True``, requires :math:`y \\le \\underline{S}_t`,
	where :math:`\\underline{S}_t` is the minimizer of :math:`G_t(\\cdot)`.
	Otherwise, requires :math:`S \\ge \\underline{S}_t`.

	Parameters
	----------
	cost : float
		The cost to set ``myopic_cost()`` equal to.
	holding_cost : float
		Holding cost in the current period. [:math:`h`]
	stockout_cost : float
		Stockout cost in the current period. [:math:`p`]
	purchase_cost : float
		Purchase cost in the current period. [:math:`c`]
	purchase_cost_next_per : float
		Purchase cost in the next period. [:math:`c_{t+1}`]
	demand_mean : float
		Mean demand in the current period. [:math:`\\mu`]
	demand_sd : float
		Standard deviation of demand in the current period. [:math:`\\sigma`]
	discount_factor : float, optional
		Discount factor in the current period, in :math:`(0,1]`.
		Default = 1. [:math:`\\gamma`]
	left_half : bool, optional
		If ``True``, requires :math:`y \\le \\underline{S}_t`; otherwise,
		requires :math:`y \\ge \\underline{S}_t`. Default = ``True``.

	Returns
	-------
	base_stock_level : float
		The :math:`y` so that ``myopic_cost(y)`` equals ``cost``.

	Raises
	------
	ValueError
		If :math:`-h_t > c_t - \\gamma c_{t+1}` or :math:`c_t - \\gamma c_{t+1} > p_t`.
	ValueError
		If ``cost`` is less than :math:`G_t(\\underline{S}_t)`.


	**Example** (Example 4.1):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> set_myopic_cost_to(18, 0.18, 0.70, 0.3, 0.35, 50, 8, 0.98, left_half=True)
		49.394684658734164
		>>> myopic_cost(49.394684658734164, 0.18, 0.70, 0.3, 0.35, 50, 8, 0.98)
		17.999999999999996
		>>> set_myopic_cost_to(18, 0.18, 0.70, 0.3, 0.35, 50, 8, 0.98, left_half=False)
		71.84861989932769
		>>> myopic_cost(71.84861989932769, 0.18, 0.70, 0.3, 0.35, 50, 8, 0.98)
		18.0

	"""

	# Calculate c_plus.
	c_plus = purchase_cost - discount_factor * purchase_cost_next_per

	# Validate c_plus.
	if c_plus < -holding_cost or c_plus > stockout_cost:
		raise ValueError("set_myopic_cost_to() requires -h_t <= c_t - gamma * c_{t+1} <= p_t")

	# Set critical ratio.
	critical_ratio = (stockout_cost - c_plus) / (stockout_cost + holding_cost)

	# Set S_underbar to minimizer of G_t(y). (It could be found numerically
	# using myopic_cost(), but it's faster to find it this way.)
	S_underbar = stats.norm.ppf(critical_ratio, demand_mean, demand_sd)

	# Calculate G_t(S_underbar).
	G_S_underbar = myopic_cost(S_underbar, holding_cost, stockout_cost,
		purchase_cost, purchase_cost_next_per, demand_mean, demand_sd, discount_factor)

	# Check that cost >= G_S_underbar.
	if cost < G_S_underbar:
		raise ValueError("cost < G_t(S_underbar), so there is no y s.t. G_t(y) = cost")

	# Determine bounds for brentq() function.
	delta = max(demand_mean, 10)
	if left_half:
		a = S_underbar - delta
		while myopic_cost(a, holding_cost, stockout_cost, purchase_cost,
						  purchase_cost_next_per, demand_mean, demand_sd,
						  discount_factor) < cost:
			a -= delta
		b = S_underbar
	else:
		a = S_underbar
		b = S_underbar + delta
		while myopic_cost(b, holding_cost, stockout_cost, purchase_cost,
						  purchase_cost_next_per, demand_mean, demand_sd,
						  discount_factor) < cost:
			b += delta

	# Set up lambda function for G_t(y) - cost.
	fun = lambda y: myopic_cost(y, holding_cost, stockout_cost, purchase_cost,
								purchase_cost_next_per, demand_mean, demand_sd,
								discount_factor) - cost

	# Use Brent method to find zero of G_t(y) - cost.
	base_stock_level = brentq(fun, a, b)

	return base_stock_level


def newsvendor_normal_explicit(revenue, purchase_cost, salvage_value,
							   demand_mean, demand_sd, holding_cost=0, stockout_cost=0, 
					  		   lead_time=0, base_stock_level=None):
	"""Solve the "explicit", profit-maximization version of the newsvendor
	problem with normal distribution, or (if ``base_stock_level`` is supplied)
	calculate profit of given solution.

	Assumes ``salvage_value`` < ``purchase_cost`` < ``revenue``
	(otherwise the solution is not well-defined).

	Parameters
	----------
	revenue : float
		Revenue per unit sold. [:math:`r`]
	purchase_cost : float
		Cost per unit purchased. [:math:`c`]
	salvage_value : float
		Revenue per unit unsold. [:math:`v`]
	demand_mean : float
		Mean demand per period. [:math:`\\mu`]
	demand_sd : float
		Standard deviation of demand per period. [:math:`\\sigma`]
	holding_cost : float, optional
		Holding cost per item per period, over and above any costs and revenues from
		buying, selling, or salvaging items. [:math:`h`]
	stockout_cost : float, optional
		Stockout cost per item per period, over and above any costs and revenues from
		buying, selling, or salvaging items. [:math:`p`]
	lead_time : int, optional
		Lead time. Default = 0. [:math:`L`]
	base_stock_level : float, optional
		Base-stock level for profit evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [:math:`S^*`]
	profit : float
		Profit per period attained by ``base_stock_level``. [:math:`\\pi^*`]

	Raises
	------
	ValueError
		If ``r`` < ``c`` or ``c`` < ``v``.
	ValueError
		If ``holding_cost`` < 0 or ``stockout_cost`` < 0.
	ValueError
		If ``demand_mean`` <= 0 or ``demand_sd`` <= 0.


	**Equations Used**:

	.. math::

		S^* = \\mu + z_{\\alpha}\\sigma

		\\pi^* = (r-c)\\mu - (r-v+h+p)\phi(z_{\\alpha})\\sigma

		\\pi(S) = (r-c+p)S - p\\mu + (v-r-h-p)\\bar{n}(S),

	where :math:`\\mu` and :math:`\\sigma` are the lead-time demand mean
	and standard deviation, :math:`\\alpha = (p+r-c)/(h+p+r-v)`,
	and :math:`\\bar{n}(\\cdot)` is the normal complementary loss function.

	**Example** (Example 4.2):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> newsvendor_normal_explicit(1, 0.3, 0.12, 50, 8)
		(56.60395592743389, 33.002394806823354)

	"""

	# Check that parameters are positive/non-negative.
	if holding_cost < 0: raise ValueError("holding_cost must be non-negative")
	if stockout_cost < 0: raise ValueError("stockout_cost must be non-negative")
	if demand_mean <= 0: raise ValueError("mean must be positive")
	if demand_sd <= 0: raise ValueError("demand_sd must be positive")
	if revenue <= purchase_cost: raise ValueError("revenue must be > purchase_cost")
	if purchase_cost <= salvage_value: raise ValueError("purchase_cost must be > salvage_value")

	# Calculate lead-time demand parameters.
	ltd_mean = demand_mean * (lead_time + 1)
	ltd_sd = demand_sd * math.sqrt(lead_time + 1)

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = (stockout_cost + revenue - purchase_cost) \
				/ (stockout_cost + holding_cost + revenue - salvage_value)

		# Calculate optimal order quantity and cost.
		base_stock_level = stats.norm.ppf(alpha, ltd_mean, ltd_sd)
		profit = (revenue - purchase_cost) * ltd_mean \
			- (revenue - salvage_value + holding_cost + stockout_cost) \
			   * stats.norm.pdf(stats.norm.ppf(alpha, 0, 1)) * ltd_sd
	else:
		# Calculate loss functions.
		_, n_bar = lf.normal_loss(base_stock_level, ltd_mean, ltd_sd)

		# Calculate profit.
		profit = (revenue - purchase_cost + stockout_cost) * base_stock_level \
			- stockout_cost * ltd_mean \
			+ (salvage_value - revenue - holding_cost - stockout_cost) * n_bar

	return base_stock_level, profit


def newsvendor_poisson_explicit(revenue, purchase_cost, salvage_value,
							   demand_mean, holding_cost=0, stockout_cost=0, 
					  		   lead_time=0, base_stock_level=None):
	"""Solve the "explicit", profit-maximization version of the newsvendor
	problem with Poisson distribution, or (if ``base_stock_level`` is supplied)
	calculate profit of given solution.

	Assumes ``salvage_value`` < ``purchase_cost`` < ``revenue``
	(otherwise the solution is not well-defined).

	Parameters
	----------
	revenue : float
		Revenue per unit sold. [:math:`r`]
	purchase_cost : float
		Cost per unit purchased. [:math:`c`]
	salvage_value : float
		Revenue per unit unsold. [:math:`v`]
	demand_mean : float
		Mean demand per period. [:math:`\\mu`]
	holding_cost : float, optional
		Holding cost per item per period, over and above any costs and revenues from
		buying, selling, or salvaging items. [:math:`h`]
	stockout_cost : float, optional
		Stockout cost per item per period, over and above any costs and revenues from
		buying, selling, or salvaging items. [:math:`p`]
	lead_time : int, optional
		Lead time. Default = 0. [:math:`L`]
	base_stock_level : float, optional
		Base-stock level for profit evaluation. If supplied, no
		optimization will be performed. [:math:`S`]

	Returns
	-------
	base_stock_level : float
		Optimal base-stock level (or base-stock level supplied). [:math:`S^*`]
	profit : float
		Profit per period attained by ``base_stock_level``. [:math:`\\pi^*`]

	Raises
	------
	ValueError
		If ``r`` < ``c`` or ``c`` < ``v``.
	ValueError
		If ``holding_cost`` < 0 or ``stockout_cost`` < 0.


	**Equations Used**:

	.. math::

		S^* = \\text{smallest } S \\text{ such that } F(S) \\ge \\frac{p+r-c}{h+p+r-v}

		\\pi(S) = (r-c+p)S - p\\mu + (v-r-h-p)\\bar{n}(S),

	where :math:`\\mu` is the lead-time demand mean
	and :math:`\\bar{n}(\\cdot)` is the Poisson complementary loss function.

	**Example** (Example 4.2 but with Poisson demand):

	.. testsetup:: *

		from stockpyl.newsvendor import *

	.. doctest::

		>>> newsvendor_poisson_explicit(1, 0.3, 0.12, 50)
		(56.0, 33.20276478819082)

	"""

	# Check that parameters are positive/non-negative.
	if holding_cost < 0: raise ValueError("holding_cost must be non-negative")
	if stockout_cost < 0: raise ValueError("stockout_cost must be non-negative")
	if demand_mean <= 0: raise ValueError("mean must be positive")
	if revenue <= purchase_cost: raise ValueError("revenue must be > purchase_cost")
	if purchase_cost <= salvage_value: raise ValueError("purchase_cost must be > salvage_value")

	# Calculate lead-time demand parameters.
	ltd_mean = demand_mean * (lead_time + 1)

	# Is S provided?
	if base_stock_level is None:
		# Calculate alpha.
		alpha = (stockout_cost + revenue - purchase_cost) \
				/ (stockout_cost + holding_cost + revenue - salvage_value)

		# Calculate optimal order quantity.
		base_stock_level = stats.poisson.ppf(alpha, ltd_mean)

	# Calculate loss functions.
	_, n_bar = lf.poisson_loss(base_stock_level, ltd_mean)

	# Calculate profit.
	profit = (revenue - purchase_cost + stockout_cost) * base_stock_level \
		- stockout_cost * ltd_mean \
		+ (salvage_value - revenue - holding_cost - stockout_cost) * n_bar

	return base_stock_level, profit


