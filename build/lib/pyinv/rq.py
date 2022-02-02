# ===============================================================================
# PyInv - rq Module
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 04-15-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""The :mod:`rq` module contains code for solving the :math:`(r,Q)` problem.

Functions in this module are called directly; they are not wrapped in a class.

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory*, 2nd edition
(2019).

"""

from scipy import integrate
from scipy.stats import norm
from scipy.stats import poisson
from scipy.optimize import fsolve

from stockpyl.newsvendor import *
from stockpyl.eoq import *
import stockpyl.loss_functions as lf


def r_q_cost(reorder_point, order_quantity, holding_cost, stockout_cost,
			 fixed_cost, demand_mean, demand_sd,
			 lead_time):
	"""Calculate the exact cost of the given solution for an :math:`(r,Q)`
	policy with given parameters.

	Parameters
	----------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	demand_sd : float
		Standard deviation of demand per unit time. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]

	Returns
	-------
	cost : float
		Expected cost per unit time. [:math:`g(r,Q)`]


	**Equations Used** (equation (5.7)):

	.. math::

		g(r,Q) = \\frac{K\\lambda + \\int_r^{r+Q} g(y)dy}{Q}

	where :math:`g(y)` is the newsvendor cost function.

	**Example** (Example 5.1):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_cost(126.8, 328.5, 0.225, 7.5, 8, 1300, 150, 1/12)
		78.07116250928294

	"""

	# TODO handle non-normal demand

	# Check that parameters are positive.
	assert order_quantity > 0, "order_quantity must be positive"
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert demand_mean >= 0, "mean must be non-negative"
	assert demand_sd >= 0, "demand_sd must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate mu and sigma (mean and SD of lead-time demand).
	mu = demand_mean * lead_time
	sigma = demand_sd * np.sqrt(lead_time)

	# Build newsvendor cost function. (Note: lead_time=0 in newsvendor even
	# though LT in (r,Q) <> 0.
	newsvendor_cost = lambda S: newsvendor_normal_cost(S, holding_cost, stockout_cost,
												  mu, sigma, lead_time=0)

	# Calculate integral of g(.) function.
	g_int = integrate.quad(newsvendor_cost, reorder_point,
						   reorder_point + order_quantity)[0]

	# Calculate (r,Q) cost.
	cost = (fixed_cost * demand_mean + g_int) / order_quantity

	return cost


def r_q_optimal_r_for_q(order_quantity, holding_cost, stockout_cost,
						demand_mean,
						demand_sd, lead_time,
						tol=1e-6):
	"""Calculate optimal :math:`r` for the given :math:`Q`.

	Finds :math:`r` using bisection search.

	Parameters
	----------
	order_quantity : float
		Order quantity. [:math:`Q`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	demand_sd : float
		Standard deviation of demand per unit time. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]
	tol : float
		Absolute tolerance to use for convergence. The algorithm terminates
		when :math:`g(r)` and :math:`g(r+Q)` are within ``tol`` of each other.

	Returns
	-------
	reorder_point : float
		Optimal reorder point for given order quantity. [:math:`r(Q)`]


	**Equation Used** (equation (5.9)):

	.. math::

		g(r) = g(r+Q)

	where :math:`g(y)` is the newsvendor cost function.

	**Example** (Example 5.2):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_optimal_r_for_q(300, 0.225, 7.5, 1300, 150, 1/12)
		129.4272799263067

	"""

	# TODO handle non-normal demand

	# Calculate mu and sigma (mean and SD of lead-time demand).
	mu = demand_mean * lead_time
	sigma = demand_sd * np.sqrt(lead_time)

	# Find S^* (= minimizer of g(.)).
	S, _ = newsvendor_normal(holding_cost, stockout_cost, mu, sigma)

	# Initialize bounds and midpoint for bisection search.
	r_lo = S - 5 * order_quantity  # TODO: better way to do this?
	r_hi = S
	r = (r_lo + r_hi) / 2

	# Calculate g(r) and g(r+Q).
	gr = newsvendor_normal_cost(r, holding_cost, stockout_cost, mu, sigma)
	grQ = newsvendor_normal_cost(r+order_quantity, holding_cost, stockout_cost, mu, sigma)

	# Bisection search.
	while abs(gr - grQ) > tol:

		# Update bounds.
		if gr < grQ:
			r_hi = r
		else:
			r_lo = r

		# Update r.
		r = (r_lo + r_hi) / 2

		# Calculate g(r) and g(r+Q).
		gr = newsvendor_normal_cost(r, holding_cost, stockout_cost, mu, sigma)
		grQ = newsvendor_normal_cost(r+order_quantity, holding_cost, stockout_cost, mu, sigma)

	return r


def r_q_eil_approximation(holding_cost, stockout_cost, fixed_cost,
						  demand_mean, demand_sd,
						  lead_time, tol=1e-6):
	"""Determine :math:`r` and :math:`Q` using the "expected-inventory-level" (EIL)
	approximation.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	demand_sd : float
		Standard deviation of demand per unit time. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]
	tol : float
		Absolute tolerance to use for convergence. The algorithm terminates
		when both :math:`r` and :math:`Q` are within ``tol`` of their previous values.
		[:math:`\\epsilon`]

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]
	cost : float
		Approximate expected cost per unit time. [:math:`g(r,Q)`]


	**Equations Used** (equation (5.17), (5.18), (5.16)):

	.. math::

		r = F^{-1}\\left(1 - \\frac{Qh}{p\\lambda}\\right)

		Q = \\sqrt{\\frac{2\\lambda[K + pn(r)]}{h}}

		g(r,Q) = h\\left(r - \\lambda L + \\frac{Q}{2}\\right) + \\frac{K\\lambda}{Q} + \\frac{p\\lambda n(r)}{Q}

	**Algorithm Used:** Iterative algorithm for EIL approximation for :math:`(r,Q)` policy (Algorithm 5.1)

	**Example** (Example 5.2):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_eil_approximation(0.225, 7.5, 8, 1300, 150, 1/12)
		(213.97044213580244, 318.5901810768729, 95.45114022285196)

	"""

	# TODO handle non-normal demand

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert demand_mean >= 0, "mean must be non-negative"
	assert demand_sd >= 0, "demand_sd must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate mu and sigma (mean and SD of lead-time demand).
	mu = demand_mean * lead_time
	sigma = demand_sd * np.sqrt(lead_time)

	# Initialize: Q = EOQ, r = 0.
	Q, _ = economic_order_quantity(fixed_cost, holding_cost, demand_mean)
	r = 0
	Q_prev = float("inf")
	r_prev = float("inf")

	# Loop until Q and r are within tolerance.
	while abs(Q - Q_prev) > tol or abs(r - r_prev) > tol:

		# Remember previous values.
		Q_prev = Q
		r_prev = r

		# Solve for r.
		r = norm.ppf(1 - Q * holding_cost / (stockout_cost * demand_mean),
					 mu, sigma)

		# Solve for Q.
		loss, _ = lf.normal_loss(r, mu, sigma)
		Q = np.sqrt(2 * demand_mean * (fixed_cost + stockout_cost * loss) / holding_cost)

	# Calculate approximate expected cost per unit time.
	loss, _ = lf.normal_loss(r, mu, sigma)
	cost = holding_cost * (r - mu + Q/2) + fixed_cost * demand_mean / Q \
		   + stockout_cost * demand_mean * loss / Q

	return r, Q, cost


def r_q_eoqb_approximation(holding_cost, stockout_cost, fixed_cost,
						   demand_mean, demand_sd,
						   lead_time):
	"""Determine :math:`r` and :math:`Q` using the "EOQ with backorders" (EOQB)
	approximation.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	demand_sd : float
		Standard deviation of demand per unit time. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]


	**Equations Used** (equations (3.27) and (5.9)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda(h+p)}{hp}}

		g(r) = g(r+Q)

	where :math:`g(y)` is the newsvendor cost function.

	**Example** (Example 5.2):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_eoqb_approximation(0.225, 7.5, 8, 1300, 150, 1/12)
		(128.63781442427097, 308.5737801203754)

	"""

	# TODO handle non-normal demand

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert demand_mean >= 0, "mean must be non-negative"
	assert demand_sd >= 0, "demand_sd must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate EOQB.
	Q, _, _ = economic_order_quantity_with_backorders(fixed_cost, holding_cost,
													  stockout_cost,
													  demand_mean)

	# Calculate r(Q).
	r = r_q_optimal_r_for_q(Q, holding_cost, stockout_cost, demand_mean,
							demand_sd,
							lead_time)

	return r, Q


def r_q_eoqss_approximation(holding_cost, stockout_cost, fixed_cost,
							demand_mean, demand_sd,
							lead_time):
	"""Determine :math:`r` and :math:`Q` using the "EOQ plus safety stock"
	(EOQ+SS) approximation.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	demand_sd : float
		Standard deviation of demand per unit time. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]


	**Equations Used** (equations (3.4) and (5.21)):

	.. math::

		Q^* = \\sqrt{\\frac{2K\\lambda}{h}}

		r = \\mu + z_{\\alpha}\\sigma

	**Example** (Example 5.5):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_eoqss_approximation(0.225, 7.5, 8, 1300, 150, 1/12)
		(190.3369965715624, 304.0467800264368)

	"""

	# TODO handle non-normal demand

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert demand_mean >= 0, "mean must be non-negative"
	assert demand_sd >= 0, "demand_sd must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate mu and sigma (mean and SD of lead-time demand).
	mu = demand_mean * lead_time
	sigma = demand_sd * np.sqrt(lead_time)

	# Calculate EOQ.
	Q, _ = economic_order_quantity(fixed_cost, holding_cost, demand_mean)

	# Calculate r(Q).
	r, _ = newsvendor_normal(holding_cost, stockout_cost, mu, sigma)

	return r, Q


def r_q_loss_function_approximation(holding_cost, stockout_cost, fixed_cost,
									demand_mean, demand_sd,
									lead_time, tol=1e-6):
	"""Determine :math:`r` and :math:`Q` using the "loss function"
	approximation.

	Parameters
	----------
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	demand_sd : float
		Standard deviation of demand per unit time. [:math:`\\tau`]
	lead_time : float
		Lead time. [:math:`L`]
	tol : float
		Absolute tolerance to use for convergence. The algorithm terminates
		when both :math:`r` and :math:`Q` are within ``tol`` of their previous values.
		[:math:`\\epsilon`]

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]


	**Equations Used** (equation (5.28) and (5.29)):

	.. math::

		Q = \\sqrt{\\frac{2\\left[K\\lambda + (h+p)n^{(2)}(r)\\right]}{h}}

		n(r) = \\frac{hQ}{h+p}

	where :math:`n(\\cdot)` and :math:`n^{(2)}(\\cdot)` are the first- and
	second-order loss functions for the lead-time demand distribution.

	**Example** (Example 5.6):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_loss_function_approximation(0.225, 7.5, 8, 1300, 150, 1/12)
		(126.8670634479628, 328.4491421980451)

	"""

	# TODO handle non-normal demand

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert demand_mean >= 0, "mean must be non-negative"
	assert demand_sd >= 0, "demand_sd must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate mu and sigma (mean and SD of lead-time demand).
	mu = demand_mean * lead_time
	sigma = demand_sd * np.sqrt(lead_time)

	# Initialize: Q = EOQ, r = 0.
	Q, _ = economic_order_quantity(fixed_cost, holding_cost, demand_mean)
	r = 0
	Q_prev = float("inf")
	r_prev = float("inf")

	# Loop until Q and r are within tolerance.
	while abs(Q - Q_prev) > tol or abs(r - r_prev) > tol:

		# Remember previous values.
		Q_prev = Q
		r_prev = r

		# Solve for r.
		rhs = holding_cost * Q / (holding_cost + stockout_cost)
		fun = lambda y: lf.normal_loss(y, mu, sigma)[0] - rhs
		r = fsolve(fun, r_prev)[0]

		# Solve for Q.
		loss2, _ = lf.normal_second_loss(r, mu, sigma)
		Q = np.sqrt(2 * (fixed_cost * demand_mean +
						 (holding_cost + stockout_cost) * loss2) / holding_cost)

	return r, Q


def r_q_cost_poisson(reorder_point, order_quantity, holding_cost, stockout_cost,
					 fixed_cost, demand_mean, lead_time):
	"""Calculate the exact cost of the given solution for an :math:`(r,Q)`
	policy with given parameters under Poisson demand.

	Parameters
	----------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	lead_time : float
		Lead time. [:math:`L`]

	Returns
	-------
	cost : float
		Expected cost per unit time. [:math:`g(r,Q)`]


	**Equations Used** (equation (5.48)):

	.. math::

		g(r,Q) = \\frac{K\\lambda + \\sum_{y=r+1}^{r+Q} g(y)}{Q}

	where :math:`g(y)` is the newsvendor cost function.


	**Example** (Example 5.8):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_cost_poisson(3, 5, 20, 150, 100, 1.5, 2)
		107.92358063314975

	"""

	# Check that parameters are positive.
	assert order_quantity > 0 and is_integer(order_quantity), \
		"order_quantity must be a positive integer"
	assert is_integer(reorder_point), "reorder_point must be an integer"
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert demand_mean >= 0, "mean must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate mu (mean lead-time demand).
	mu = demand_mean * lead_time

	# Determine range of y in sum.
	y_range = range(int(reorder_point)+1, int(reorder_point+order_quantity)+1)

	# Calculate cost.
	cost = fixed_cost * demand_mean
	for y in y_range:
		cost += newsvendor_poisson_cost(y, holding_cost, stockout_cost, mu)
	cost /= order_quantity

	return cost


def r_q_poisson_exact(holding_cost, stockout_cost, fixed_cost,
					  demand_mean, lead_time):
	"""Determine optimal :math:`r` and :math:`Q` for Poisson demand_list, using
	algorithm by Federgruen and Zheng (1992).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per unit time. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per unit time. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per unit time. [:math:`\\lambda`]
	lead_time : float
		Lead time. [:math:`L`]

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`r`]
	order_quantity : float
		Order quantity. [:math:`Q`]
	cost : float
		Expected cost per unit time. [:math:`g(r,Q)`]


	**Equations Used** (equation (5.48)):

	.. math::

		g(r,Q) = \\frac{K\\lambda + \\sum_{y=r+1}^{r+Q} g(y)}{Q}

	where :math:`g(y)` is the newsvendor cost function for Poisson demand_list.

	**Example** (Example 5.8):

	.. testsetup:: *

		from rq import *

	.. doctest::

		>>> r_q_poisson_exact(20, 150, 100, 1.5, 2)
		(3, 5, 107.92358063314975)

	"""

	# Check that parameters are positive.
	assert holding_cost > 0, "holding_cost must be positive."
	assert stockout_cost > 0, "stockout_cost must be positive."
	assert fixed_cost > 0, "fixed_cost must be positive."
	assert demand_mean >= 0, "mean must be non-negative"
	assert lead_time >= 0, "lead_time must be non-negative"

	# Calculate alpha.
	alpha = stockout_cost / (stockout_cost + holding_cost)

	# Calculate mu (mean lead-time demand).
	mu = demand_mean * lead_time

	# Find S*.
	S = 0
	while poisson.cdf(S, mu) < alpha:
		S += 1

	# Initialization.
	Q = 1
	r = S - 1
	g = r_q_cost_poisson(r, Q, holding_cost, stockout_cost, fixed_cost,
						 demand_mean, lead_time)

	# Main loop.
	done = False
	while not done:

		# Remember previous cost and r.
		g_prev = g
		r_prev = r

		# Calculate g(r) and g(r+Q+1).
		g_r = newsvendor_poisson_cost(r, holding_cost, stockout_cost, mu)
		g_rQ1 = newsvendor_poisson_cost(r+Q+1, holding_cost, stockout_cost, mu)

		# Determine r(Q+1).
		if g_r < g_rQ1:
			r -= 1
		# (else r = r)

		# Calculate new cost.
		g = r_q_cost_poisson(r, Q + 1, holding_cost, stockout_cost, fixed_cost,
							 demand_mean, lead_time)

		# Termination check.
		if g > g_prev:
			# Done.
			done = True
		else:
			# Increment Q.
			Q += 1

	# Return r_prev, Q, and g_prev.
	r = r_prev
	g = g_prev

	return r, Q, g


