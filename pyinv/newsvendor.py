# ===============================================================================
# PyInv - newsvendor Module
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 04-15-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""The :mod:`newsvendor` module contains code for solving the newsvendor
problem and some of its variants.

Functions in this module are called directly; they are not wrapped in a class.

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory*, 2nd edition
(2019).

"""

from scipy import stats
import numpy as np

import pyinv.loss_functions as lf
from pyinv.helpers import *


def newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd,
					  lead_time=0, base_stock_level=None):
	"""Solve the newsvendor problem with normal distribution, or (if
	``base_stock_level`` is supplied) calculate cost of given solution.

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
		Cost per period attained by ``base_stock_level``. [:math:`g^*`]


	**Equations Used** (equations (4.24) and (4.30), modified for non-zero
	lead time):

	.. math::

		S^* = \\mu + z_{\\alpha}\\sigma

		g^* = (h+p)\phi(z_{\\alpha})\\sigma

	where :math:`\\mu` and :math:`\\sigma` are the lead-time demand mean
	and standard deviation, and :math:`\\alpha = p/(h+p)`.

	**Example** (Example 4.3):

	.. testsetup:: *

		from pyinv.newsvendor import *

	.. doctest::

		>>> newsvendor_normal(0.18, 0.70, 50, 8)
		(56.60395592743389, 1.9976051931766445)

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


	**Equations Used** (equation (4.6)):

	.. math::

		g(S) = h\\bar{n}(S) + pn(S),

	where :math:`n(\cdot)` and :math:`\\bar{n}(\cdot)` are the lead-time demand
	loss and complementary loss functions.

	**Example** (Example 4.1):

	.. testsetup:: *

		from pyinv.newsvendor import *

	.. doctest::

		>>> newsvendor_normal_cost(60, 0.18, 0.70, 50, 8)
		2.156131552870387

	"""

	# TODO: allow base_stock_level to be an array (for other _cost functions too)

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert demand_mean > 0, "demand_mean must be positive."
	assert demand_sd > 0, "demand_sd must be positive."

	# Calculate lead-time demand parameters.
	ltd_mean = demand_mean * (lead_time + 1)
	ltd_sd = demand_sd * np.sqrt(lead_time + 1)

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


	**Equations Used** (equations (4.35), (4.32)-(4.34)):

	.. math::

		S^* = \\text{smallest } S \\text{ such that } F(S) \\ge \\frac{p}{h+p}

		g(S^*) = h\\bar{n}(S^*) + pn(S^*)

	where :math:`F(\\cdot)`, :math:`n(\\cdot)`, and :math:`\\bar{n}(\\cdot)` are
	the Poisson cdf, loss function, and complementary loss function,
	respectively.

	**Example**:

	.. testsetup:: *

		from pyinv.newsvendor import *

	.. doctest::

		>>> newsvendor_poisson(0.18, 0.70, 50)
		(56.0, 1.797235211809178)

	"""

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert demand_mean > 0, "demand_mean must be positive."
	if base_stock_level is not None:
		assert is_integer(base_stock_level), "base_stock_level must be an integer (or None)"

	# TODO: handle lead time

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


	**Equations Used** (equation (4.6)):

	.. math::

		g(S) = h\\bar{n}(S) + pn(S),

	where :math:`n(\cdot)` and :math:`\\bar{n}(\cdot)` are the lead-time demand
	loss and complementary loss functions.


	**Example** (Example 4.1):

	.. testsetup:: *

		from pyinv.newsvendor import *

	.. doctest::

		>>> newsvendor_poisson_cost(56, 0.18, 0.70, 50)
		1.797235211809178

	"""

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert demand_mean > 0, "demand_mean must be positive."
	if base_stock_level is not None:
		assert is_integer(base_stock_level), "base_stock_level must be an integer (or None)"

	# TODO: handle lead time

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


	**Equations Used** (equations (4.35), (4.32)-(4.34)):

	.. math::

		S^* = F^{-1}\\left(\\frac{p}{h+p}\\right)

		g(S^*) = h\\bar{n}(S^*) + pn(S^*)

	where :math:`F(\\cdot)`, :math:`n(\\cdot)`, and :math:`\\bar{n}(\\cdot)` are
	the demand cdf, loss function, and complementary loss function,
	respectively.

	**Example** (Example 4.3):

	.. testsetup:: *

		from pyinv.newsvendor import *

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
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."

	# Check that either distribution or pmf have been supplied.
	assert (demand_distrib is not None) or (demand_pdf is not None), \
		"must provide demand_distrib or demand_pdf"

	# TODO: handle lead time
	# TODO: handle demand_pdf as function

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


	**Equations Used** (equations (4.35), (4.32)-(4.34)):

	.. math::

		S^* = \\text{smallest } S \\text{ such that } F(S) \\ge \\frac{p}{h+p}

		g(S^*) = h\\bar{n}(S^*) + pn(S^*)

	where :math:`F(\\cdot)`, :math:`n(\\cdot)`, and :math:`\\bar{n}(\\cdot)` are
	the demand cdf, loss function, and complementary loss function,
	respectively.

	**Example** (Example 4.7):

	.. testsetup:: *

		from pyinv.newsvendor import *

	.. doctest::

		>>> from scipy.stats import poisson
		>>> demand_distrib = poisson(6)
		>>> newsvendor_discrete(1, 4, demand_distrib)
		(8.0, 3.570106945768532)
		>>> newsvendor_discrete(1, 4, demand_distrib, base_stock_level=5)
		(5, 6.590296024613934)

	.. doctest::

		>>> from scipy.stats import poisson
		>>> d = range(0, 41)
		>>> f = [poisson.pmf(d_val, 6) for d_val in d]
		>>> demand_pmf = dict(zip(d, f))
		>>> newsvendor_discrete(1, 4, demand_pmf=demand_pmf)
		(8, 3.570106945770941)

	"""

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."

	# Check that either distribution or pmf have been supplied.
	assert (demand_distrib is not None) or (demand_pmf is not None), \
		"must provide demand_distrib or demand_pmf"

	# TODO: handle lead time

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

