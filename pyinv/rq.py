# ===============================================================================
# PyInv - rq Module
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 04-15-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""The :mod:`rq` module contains code for solving the (r,Q) problem.

Functions in this module are called directly; they are not wrapped in a class.

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory*, 2nd edition
(2019).

"""

from scipy import integrate
from scipy.stats import norm

from pyinv.newsvendor import *
from pyinv.eoq import economic_order_quantity
import pyinv.loss_functions as lf


def r_q_cost(reorder_point, order_quantity, holding_cost, stockout_cost,
			 fixed_cost, annual_demand_mean, annual_demand_standard_deviation,
			 lead_time):
	"""Calculate the exact cost of the given solution for an (r,Q)
	policy with given parameters.

	Parameters
	----------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]
	holding_cost : float
		Holding cost per item per year. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per year. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	annual_demand_mean : float
		Mean demand per year. [:math:`\\lambda']
	annual_demand_standard_deviation : float
		Standard deviation of demand per year. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]

# TODO handle non-normal demand

	Returns
	-------
	cost : float
		Expected cost per year. [:math:`g(r,Q)`]


	**Equations Used** (equation (5.7)):

	.. math::

		g(r,Q) = \\frac{K\\lambda + \\int_r^{r+Q} g(y)dy}{Q}

	where :math:`g(y)` is the newsvendor cost function.

	**Example** (Example 5.1):

	.. testsetup:: *

		from pyinv.rq import *

	.. doctest::

		>>> r_q_cost(126.8, 328.5, 0.225, 7.5, 8, 1300, 150, 1/12)
		78.07116250928294

	"""

	# Check that parameters are positive.
	assert order_quantity > 0, "order_quantity must be positive"
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert annual_demand_mean >= 0, "annual_demand_mean must be non-negative"
	assert annual_demand_standard_deviation >= 0, "annual_demand_standard_deviation must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate mu and sigma (mean and SD of lead-time demand).
	mu = annual_demand_mean * lead_time
	sigma = annual_demand_standard_deviation * np.sqrt(lead_time)

	# Build newsvendor cost function. (Note: lead_time=0 in newsvendor even
	# though LT in (r,Q) <> 0.
	newsvendor_cost = lambda S: newsvendor_normal(holding_cost, stockout_cost,
												  mu, sigma, lead_time=0,
												  base_stock_level=S)[1]

	# Calculate integral of g(.) function.
	g_int = integrate.quad(newsvendor_cost, reorder_point,
						   reorder_point + order_quantity)[0]

	# Calculate (r,Q) cost.
	cost = (fixed_cost * annual_demand_mean + g_int) / order_quantity

	return cost


def r_q_eil_approximation(holding_cost, stockout_cost, fixed_cost,
						  annual_demand_mean, annual_demand_standard_deviation,
			 			  lead_time, tol=1e-6):
	"""Determine r and Q using the "expected-inventory-level" (EIL)
	approximation.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per year. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per year. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	annual_demand_mean : float
		Mean demand per year. [:math:`\\lambda']
	annual_demand_standard_deviation : float
		Standard deviation of demand per year. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]
	tol : float
		Absolute tolerance to use for convergence. The algorithm terminates
		when both ``r`` and ``Q`` are within ``tol`` of their previous values.
		[:math:`\\epsilon`]

# TODO handle non-normal demand

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]
	cost : float
		Approximate expected cost per year. [:math:`g(r,Q)`]


	**Equations Used** (equation (5.7)):

	.. math::

		r = F^{-1}\\left(1 - \\frac{Qh}{p\\lambda}\\right)

		Q = \\sqrt{\\frac{2\\lambda[K + pn(r)]}{h}}

		g(r,Q) = h\\left(r - \\lambda L + \\frac{Q}{2}\\right) + \\frac{K\\lambda}{Q} + \\frac{p\\lambda n(r)}{Q}

	**Algorithm Used:** Iterative algorithm for EIL approximation for :math:`(r,Q)` policy (Algorithm 5.1)

	**Example** (Example 5.2):

	.. testsetup:: *

		from pyinv.rq import *

	.. doctest::

# TODO
		>>> r_q_cost(126.8, 328.5, 0.225, 7.5, 8, 1300, 150, 1/12)
		78.07116250928294

	"""

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert annual_demand_mean >= 0, "annual_demand_mean must be non-negative"
	assert annual_demand_standard_deviation >= 0, "annual_demand_standard_deviation must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate mu and sigma (mean and SD of lead-time demand).
	mu = annual_demand_mean * lead_time
	sigma = annual_demand_standard_deviation * np.sqrt(lead_time)

	# Initialize: Q = EOQ, r = 0.
	Q, _ = economic_order_quantity(fixed_cost, holding_cost, annual_demand_mean)
	r = 0
	Q_prev = float("inf")
	r_prev = float("inf")

	# Loop until Q or r are within tolerance.
	while abs(Q - Q_prev) > tol or abs(r - r_prev) > tol:

		# Remember previous values.
		Q_prev = Q
		r_prev = r

		# Solve for r.
		r = norm.ppf(1 - Q * holding_cost / (stockout_cost * annual_demand_mean),
					 mu, sigma)

		# Solve for Q.
		loss = lf.normal_loss(r, mu, sigma)[0]
		Q = np.sqrt(2 * annual_demand_mean * (fixed_cost + stockout_cost * loss) / holding_cost)

	# Calculate approximate expected annual cost.
	loss = lf.normal_loss(r, mu, sigma)[0]
	cost = holding_cost * (r - mu + Q/2) + fixed_cost * annual_demand_mean / Q \
		+ stockout_cost * annual_demand_mean * loss / Q

	return r, Q, cost

