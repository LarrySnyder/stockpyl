# ===============================================================================
# stockpyl - ss Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_ss| module contains code for solving the |ss| optimization problem.

.. note:: |fosct_notation|

.. seealso::

	For an overview of single-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for single-echelon inventory optimization<tutorial_seio_page>`.


API Reference
-------------

"""

from scipy import integrate
from scipy.stats import norm
from scipy.stats import poisson
from scipy.optimize import fsolve

from stockpyl.newsvendor import *
from stockpyl.eoq import *
#import stockpyl.loss_functions as lf


def s_s_cost_discrete(reorder_point, order_up_to_level, holding_cost,
					  stockout_cost, fixed_cost, use_poisson, demand_mean=None,
					  demand_hi=None, demand_pmf=None):
	"""Calculate the exact cost of the given solution for an |ss|
	policy with given parameters under a discrete (Poisson or custom) demand
	distribution.

	Uses method introduced in Zheng and Federgruen (1991).

	Parameters
	----------
	reorder_point : float
		Reorder point. [:math:`s`]
	order_up_to_level : float
		Order-up-to level. [:math:`S`]
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	use_poisson : bool
		Set to ``True`` to use Poisson distribution, ``False`` to use custom
		discrete distribution. If ``True``, then ``mean`` must be
		provided; if ``False``, then ``hi`` and ``demand_pdf`` must
		be provied.
	demand_mean : float, optional
		Mean demand per period. Required if ``use_poisson`` is ``True``,
		ignored otherwise. [:math:`\\mu`]
	demand_hi : int, optional
		Upper limit of support of demand per period (lower limit is assumed to
		be 0). Required if ``use_poisson`` is ``False``, ignored otherwise.
	demand_pmf : list, optional
		List of pmf values for demand values 0, ..., ``hi``. Required
		if ``use_poisson`` is ``False``, ignored otherwise.

	Returns
	-------
	cost : float
		Expected cost per period. [:math:`g(s,S)`]

	Raises
	------
	ValueError
		If ``reorder_point`` or ``order_up_to_level`` is not an integer.
	ValueError
		If ``holding_cost``, ``stockout_cost``, or ``fixed_cost`` <= 0.
	ValueError
		If ``demand_mean`` < 0, or if ``demand_hi`` is not a non-negative integer.
	ValueError
		If ``demand_pmf`` is not a list of length ``demand_hi`` + 1.


	**Equations Used** (equation (5.7)):

	.. math::

		g(s,S) = \\frac{K + \\sum_{d=0}^{S-s-1} m(d)g(S-d)}{M(S-s)},

	where :math:`g(\cdot)` is the newsvendor cost function and :math:`M(\\cdot)`
	and :math:`m(\\cdot)` are as described in equations (4.71)--(4.75).


	References
	----------
	Y.-S. Zheng and A. Federgruen, Finding Optimal |ss| Policies is About as Simple
	as Evaluating a Single Policy, *Operations Research* 39(4), 654-665 (1991).


	**Example** (Example 4.7):

	.. testsetup:: *

		from stockpyl.ss import *

	.. doctest::

		>>> s_s_cost_discrete(4, 10, 1, 4, 5, True, 6)
		8.034111561471642

	"""

	# Check parameters.
	if not is_integer(reorder_point): raise ValueError("reorder_point must be an integer")
	if not is_integer(order_up_to_level): raise ValueError("order_up_to_level must be an integer")
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if fixed_cost <= 0: raise ValueError("fixed_cost must be positive")
	if demand_mean is not None and demand_mean < 0: raise ValueError("demand_mean must be non-negative (or None)")
	if demand_hi is not None and (demand_hi < 0 or not is_integer(demand_hi)):
		raise ValueError("demand_hi must be a non-negative integer (or None)")
	if demand_pmf is not None and \
		(not is_list(demand_pmf) or len(demand_pmf) != demand_hi+1):
		raise ValueError("demand_pmf must be a list of length demand_hi+1 (or None)")

	# Determine demand pmf to use based on use_poisson.
	if use_poisson:
		# We only need values up through S-s.
		pmf = poisson.pmf(range(int(order_up_to_level) - int(reorder_point)), demand_mean)
	else:
		pmf = demand_pmf

	# Calculate m(.) function.
	m = np.zeros(int(order_up_to_level) - int(reorder_point))
	m[0] = 1.0 / (1 - pmf[0])
	for j in range(1, int(order_up_to_level) - int(reorder_point)):
		m[j] = m[0] * np.sum([pmf[l] * m[j-l] for l in range(1, j+1)])
		# old (incorrect) method:
		# m[j] = np.sum([pmf[d] * m[j-d] for d in range(j+1)])

	# Calculate M(.) function.
	M = np.zeros(int(order_up_to_level) - int(reorder_point) + 1)
	M[0] = 0
	for j in range(1, int(order_up_to_level) - int(reorder_point) + 1):
		M[j] = M[j-1] + m[j-1]

	# Calculate g(s,S).
	cost = fixed_cost
	for d in range(int(order_up_to_level) - int(reorder_point)):
		if use_poisson:
			cost += m[d] * newsvendor_poisson_cost(order_up_to_level - d,
				holding_cost=holding_cost,
				stockout_cost=stockout_cost,
				demand_mean=demand_mean)
		else:
			cost += m[d] * newsvendor_discrete(
				holding_cost=holding_cost,
				stockout_cost=stockout_cost,
				demand_distrib=None,
				demand_pmf={n: demand_pmf[n] for n in range(demand_hi)},
				base_stock_level=order_up_to_level - d)[1]
	cost /= M[int(order_up_to_level)-int(reorder_point)]

	return cost


def s_s_discrete_exact(holding_cost, stockout_cost, fixed_cost, use_poisson,
					   demand_mean=None, demand_hi=None, demand_pmf=None):
	"""Determine optimal :math:`s` and :math:`S` for an |ss|
	policy under a discrete (Poisson or custom) demand distribution.

	Uses method introduced in Zheng and Federgruen (1991).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	use_poisson : bool
		Set to ``True`` to use Poisson distribution, ``False`` to use custom
		discrete distribution. If ``True``, then ``demand_mean`` must be
		provided; if ``False``, then ``demand_hi`` and ``demand_pdf`` must
		be provied.
	demand_mean : float, optional
		Mean demand per period. Required if ``use_poisson`` is ``True``,
		ignored otherwise. [:math:`\\mu`]
	demand_hi : int, optional
		Upper limit of support of demand per period (lower limit is assumed to
		be 0). Required if ``use_poisson`` is ``False``, ignored otherwise.
	demand_pmf : list, optional
		List of pmf values for demand values 0, ..., ``demand_hi``. Required
		if ``use_poisson`` is ``False``, ignored otherwise.

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`s`]
	order_up_to_level : float
		Order-up-to level. [:math:`S`]
	cost : float
		Expected cost per period. [:math:`g(s,S)`]

	Raises
	------
	ValueError
		If ``holding_cost``, ``stockout_cost``, or ``fixed_cost`` <= 0.
	ValueError
		If ``demand_mean`` < 0, or if ``demand_hi`` is not a non-negative integer.
	ValueError
		If ``demand_pmf`` is not a list of length ``demand_hi`` + 1.


	**Algorithm Used:** Exact algorithm for periodic-review |ss|
	policies with discrete demand distribution (Algorithm 4.2)


	References
	----------
	Y.-S. Zheng and A. Federgruen, Finding Optimal |ss| Policies is About as Simple
	as Evaluating a Single Policy, *Operations Research* 39(4), 654-665 (1991).


	**Example** (Example 4.7):

	.. testsetup:: *

		from stockpyl.ss import *

	.. doctest::

		>>> s_s_discrete_exact(1, 4, 5, True, 6)
		(4.0, 10.0, 8.034111561471642)

	"""

	# Check parameters.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if fixed_cost <= 0: raise ValueError("fixed_cost must be positive")
	if demand_mean is not None and demand_mean < 0: raise ValueError("demand_mean must be non-negative (or None)")
	if demand_hi is not None and (demand_hi < 0 or not is_integer(demand_hi)):
		raise ValueError("demand_hi must be a non-negative integer (or None)")
	if demand_pmf is not None and \
		(not is_list(demand_pmf) or len(demand_pmf) != demand_hi+1):
		raise ValueError("demand_pmf must be a list of length demand_hi+1 (or None)")

	# Determine y^*.
	if use_poisson:
		demand_pmf_dict = None
		y_star, _ = newsvendor_poisson(holding_cost, stockout_cost, demand_mean)
	else:
		demand_pmf_dict = {d: demand_pmf[d] for d in range(demand_hi+1)}
		y_star, _ = newsvendor_discrete(holding_cost, stockout_cost,
										demand_pmf=demand_pmf_dict)

	# Initialize.
	S0 = y_star
	s = y_star

	# Find s(S0).
	done = False
	while not done:
		s -= 1
		if use_poisson:
			gs = newsvendor_poisson_cost(s, holding_cost, stockout_cost, demand_mean)
		else:
			gs = newsvendor_discrete(holding_cost, stockout_cost,
									 demand_pmf=demand_pmf_dict,
									 base_stock_level=s)[1]
		gsS0 = s_s_cost_discrete(s, S0, holding_cost, stockout_cost, fixed_cost,
							 use_poisson, demand_mean, demand_hi, demand_pmf)
		if gsS0 <= gs:
			done = True

	# Set s0.
	s0 = s

	# Initialize incumbent and cost.
	S_hat = S0
	s_hat = s0
	g_hat = s_s_cost_discrete(s_hat, S_hat, holding_cost, stockout_cost,
							  fixed_cost, use_poisson, demand_mean, demand_hi,
							  demand_pmf)

	# Choose next order-up-to level to consider.
	S = S_hat + 1

	# Loop through S values.
	if use_poisson:
		gS = newsvendor_poisson_cost(S, holding_cost, stockout_cost, demand_mean)
	else:
		gS = newsvendor_discrete(holding_cost, stockout_cost,
								 demand_pmf=demand_pmf_dict,
								 base_stock_level=S)[1]
	while gS <= g_hat:

		# Check for improvement.
		gsS = s_s_cost_discrete(s_hat, S, holding_cost, stockout_cost, fixed_cost,
							 use_poisson, demand_mean, demand_hi, demand_pmf)
		if gsS < g_hat:

			# Update incumbent S.
			S_hat = S
			if use_poisson:
				gs = newsvendor_poisson_cost(s+1, holding_cost, stockout_cost,
											 demand_mean)
			else:
				gs = newsvendor_discrete(holding_cost, stockout_cost,
										 demand_pmf=demand_pmf_dict,
										 base_stock_level=s+1)[1]
			while s_s_cost_discrete(s, S_hat, holding_cost, stockout_cost,
									fixed_cost, use_poisson, demand_mean,
									demand_hi, demand_pmf) <= gs:
				s += 1
				if use_poisson:
					gs = newsvendor_poisson_cost(s + 1, holding_cost, stockout_cost,
												 demand_mean)
				else:
					gs = newsvendor_discrete(holding_cost, stockout_cost,
											 demand_pmf=demand_pmf_dict,
											 base_stock_level=s+1)[1]

			# Update incumbent s and g.
			s_hat = s
			g_hat = s_s_cost_discrete(s_hat, S_hat, holding_cost, stockout_cost,
									  fixed_cost, use_poisson, demand_mean,
									  demand_hi, demand_pmf)

		# Try next order-up-to level.
		S += 1
		if use_poisson:
			gS = newsvendor_poisson_cost(S, holding_cost, stockout_cost,
										 demand_mean)
		else:
			gS = newsvendor_discrete(holding_cost, stockout_cost,
									 demand_pmf=demand_pmf_dict,
									 base_stock_level=S)[1]

	s = s_hat
	S = S_hat
	g = g_hat

	return s, S, g


def s_s_power_approximation(holding_cost, stockout_cost, fixed_cost,
					   demand_mean, demand_sd):
	"""Determine heuristic :math:`s` and :math:`S` for an |ss|
	policy under a normal demand distribution.

	Uses the power approximation by Ehrhardt and Mosier (1984).

	Parameters
	----------
	holding_cost : float
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float
		Stockout cost per item per period. [:math:`p`]
	fixed_cost : float
		Fixed cost per order. [:math:`K`]
	demand_mean : float
		Mean demand per period. [:math:`\\mu`]
	demand_sd : float
		Standard deviation of demand per period. [:math:`\\sigma`]

	Returns
	-------
	reorder_point : float
		Reorder point. [:math:`s`]
	order_up_to_level : float
		Order-up-to level. [:math:`S`]

	Raises
	------
	ValueError
		If ``holding_cost``, ``stockout_cost``, or ``fixed_cost`` <= 0.
	ValueError
		If ``demand_mean`` or ``demand_sd`` < 0.


	References
	----------
	R. Ehrhardt and C. Mosier, A Revision of the Power Approximation for
	Computing |ss| Policies, *Management Science* 30, 618-622 (1984).


	**Equations Used** (equations (4.77)-(4.80)):

	.. math::

		Q  = 1.30 \\mu^{0.494} \\left(\\frac{K}{h}\\right)^{0.506} \\left(1 + \\frac{\\sigma_L^2}{\\mu^2}\\right)^{
		0.116}

		z  = \\sqrt{\\frac{Q}{\\sigma_L} \\frac{h}{p}}

		s  = 0.973\\mu_L + \\sigma_L\\left(\\frac{0.183}{z} + 1.063 - 2.192z\\right) \\label{eq:sS_power_approx3}

		S  = s + Q

	where :math:`\\mu_L = \\mu L` and :math:`\\sigma^2_L = \\sigma^2L` are the
	mean and standard deviation of the lead-time demand.

	**Example** (Example 4.7):

	.. testsetup:: *

		from stockpyl.ss import *

	.. doctest::

		>>> s_s_power_approximation(0.18, 0.70, 2.5, 50, 8)
		(40.19461695647407, 74.29017010980579)

	"""

	# Check that parameters are positive/non-negative.
	if holding_cost <= 0: raise ValueError("holding_cost must be positive")
	if stockout_cost <= 0: raise ValueError("stockout_cost must be positive")
	if fixed_cost <= 0: raise ValueError("fixed_cost must be positive")
	if demand_mean < 0: raise ValueError("mean must be non-negative")
	if demand_sd < 0: raise ValueError("demand_sd must be non-negative")

	# Calculate Q and z.
	Q = 1.30 * (demand_mean**0.494) * (fixed_cost / holding_cost)**0.506 \
		* (1 + (demand_sd / demand_mean)**2)**0.116
	z = math.sqrt((Q / demand_sd) * (holding_cost / stockout_cost))

	# Calculate s and S.
	s = 0.973 * demand_mean + demand_sd * ((0.183 / z) + 1.063 - 2.192*z)
	S = s + Q

	return s, S
