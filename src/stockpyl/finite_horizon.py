# ===============================================================================
# stockpyl - finite_horizon Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_finite_horizon| module contains code for solving finite-horizon, stochastic
inventory optimization problems, with or without fixed costs, using dynamic programming (DP).

.. note:: |fosct_notation|

.. seealso::

	For an overview of single-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for single-echelon inventory optimization<tutorial_seio_page>`.


API Reference
-------------
"""

import numpy as np
from scipy.stats import norm
import warnings

from stockpyl.helpers import *
from stockpyl.newsvendor import *
from stockpyl.eoq import *
import stockpyl.loss_functions as lf
from stockpyl.instances import *


def finite_horizon_dp(
		num_periods,
		holding_cost,
		stockout_cost,
		terminal_holding_cost,
		terminal_stockout_cost,
		purchase_cost,
		fixed_cost,
		demand_mean=None,
		demand_sd=None,
		demand_source=None,
		discount_factor=1.0,
		initial_inventory_level=0.0,
		trunc_tol=0.02,
		d_spread=4,
		s_spread=5,
		oul_matrix=None,
		x_range=None):
	"""
	Solve the finite-horizon inventory optimization problem, with or without
	fixed costs, minimizing the expected discounted cost over the time horizon,
	using dynamic programming (DP).

	See Sections 4.3.3 and 4.4.3 of |fosct| for discussion and
	notation.

	Returns :math:`s^*_t` and :math:`S^*_t` in the output lists ``reorder_points``
	and ``order_up_to_levels``, respectively. If ``fixed_cost`` = 0,
	then ``reorder_points[t]`` = ``order_up_to_levels[t]`` for all ``t``.

	Also returns the optimal cost and action matrices. The optimal total
	expected discounted cost over the entire horizon is given by
	``cost_matrix[1,initial_inventory_level]``, and is also returned in ``total_cost``.
	``x_range`` gives the range of :math:`x` values for which :math:`\\theta_t(x)`
	is calculated, i.e., the indices for the columns of ``cost_matrix`` and
	``oul_matrix``.

	The terminal cost function is assumed to be given by

	.. math::

		\\theta_{T+1}(x) = h_T x^+ + p_T x^-,

	where :math:`h_T` = ``terminal_holding_cost``, :math:`p_T` =
	``terminal_stockout_cost``, :math:`x^+ = \\max\\{x,0\\}`, and
	:math:`x^- = \\max\\{-x,0\\}`.

	Either ``demand_mean`` and ``demand_sd`` must be
	provided (in which case the demand will be assumed to be normally distributed),
	or ``demand_source`` must be provided (in which case the demand will follow the
	distribution specified in ``demand_source``).

	Most parameters may be given as a singleton or a list. If given as a
	singleton, the parameter will be assumed to be the same in every time
	period. If given as a list, the list must be of length ``num_periods`` or
	``num_periods``\+1.

	*	In the former case, the list is assumed to contain values for periods
		1, ..., ``num_periods`` in elements 0, ..., ``num_periods``-1.
	*	In the latter case, the list is assumed to contain values for periods
		1, ..., ``num_periods`` in elements 1, ..., ``num_periods``, and the
		0th element is ignored.

	The parameters may be mixed, some scalars and some lists.

	Output arrays are all 1-indexed; for example, ``reorder_point[5]`` gives
	:math:`s^*_5`, the reorder point for period 5.

	Discretization is done at the integer level, i.e., all demands and
	inventory positions are rounded to the nearest integer. The state space
	(range of possible inventory positions) is truncated using settings
	specified in the code.

	Raises warnings if the discretization and truncation settings are likely to
	lead to suboptimal results. (See details in the code.)
		
	If ``oul_matrix`` is provided as an input, the function uses it (with discretization 
	specified by ``x_range`` input) instead of optimizing over the order-up-to levels.
	If ``oul_matrix`` is provided, then ``x_range`` must be provided as well.

	.. note:: This function executes faster than straightforward implementation because it calculates
		:math:`H_t(y)` (as defined in (4.87)) for each :math:`t` and :math:`y`,
		and then uses this when calculating :math:`\\theta_t(x)` for each :math:`x`.
		This avoids having to recalculate the terms that don't depend on :math:`x`
		(which are computationally expensive).

	Parameters
	----------
	num_periods : int
		Number of periods in time horizon. [:math:`T`]
	holding_cost : float or list
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float or list
		Stockout cost per item per period. [:math:`p`]
	terminal_holding_cost : float
		Terminal holding cost per item. [:math:`h_T`]
	terminal_stockout_cost : float
		Terminal stockout cost per item. [:math:`p_T`]
	purchase_cost : float or list
		Purchase cost per item. [:math:`c`]
	fixed_cost : float or list
		Fixed cost per order. [:math:`K`]
	demand_mean : float or list, optional
		Demand mean per period. Ignored if ``demand_source`` is not ``None``. [:math:`\\mu`]
	demand_sd : float or list, optional
		Demand standard deviation per period. Ignored if ``demand_source`` is not ``None``. [:math:`\\sigma`]
	demand_source : |class_demand_source|, optional
		A |class_demand_source| object describing the demand distribution. Required if
		``demand_mean`` and ``demand_standard_deviation`` are ``None``.
	discount_factor : float or list
		Discount factor, in :math:`(0,1]`. Default = 1. [:math:`\\gamma`]
	initial_inventory_level : float
		Initial inventory level at the start of period 1. [:math:`x_1`]
	trunc_tol : float
		Truncation tolerance; a warning is raised if *either* total probability of 
		demand outside of ``d_range`` > ``trunc_tol`` for any time period, *or*
		:math:`P(s_t - D < x_{min})` > ``trunc_tol``, where :math:`x_{min}` is the 
		minimum value of :math:`x` after truncation.
	d_spread : float
		Number of standard deviations around mean to consider for demand truncation.
	s_spread : float
		Number of (demand) standard deviations around :math:`(s,S)` estimates to consider.
	oul_matrix : ndarray, optional
		User-specified matrix of order-up-to levels; ``oul_matrix[t,x]`` = optimal
		order-up-to level in period :math:`t` if we begin period :math:`t`
		with :math:`IL_t = x`. ``t=0`` is ignored. If provided, then ``x_range`` must also be provided.
	x_range : ndarray, optional
		User-specified list of :math:`x`-values used in the discretization, i.e.,
		indices of the columns of ``cost_matrix`` and ``oul_matrix``. 

	Returns
	-------
	reorder_points : list
		List of reorder points in each time period. [:math:`s^*_t`]
	order_up_to_levels : list
		List of order-up-to levels in each time period. [:math:`S^*_t`]
	total_cost : float
		Optimal total expected discounted cost over the horizon, assuming IL in
		period 1 equals ``initial_inventory_level``. [:math:`\\theta_1(x_1)`]
	cost_matrix : ndarray
		Matrix of DP costs; ``cost_matrix[t,x]`` = optimal expected cost
		in periods :math:`t,\\ldots,T` if we begin period :math:`t` with
		:math:`IL_t = x` (and act optimally thereafter). [:math:`\\theta_t(x)`]
	oul_matrix : ndarray
		Matrix of order-up-to levels; ``oul_matrix[t,x]`` = optimal
		order-up-to level in period :math:`t` if we begin period :math:`t`
		with :math:`IL_t = x`. ``t=0`` is ignored.
	x_range : list
		List of :math:`x`-values used in the discretization, i.e.,
		indices of the columns of ``cost_matrix`` and ``oul_matrix``.

	Raises
	------
	ValueError
		If ``num_periods`` <= 0 or is non-integer.
	ValueError
		If ``holding_cost``, ``stockout_cost``, ``purchase_cost``, ``fixed_cost``,
		``demand_mean``, or ``demand_sd`` < 0 for any time period.
	ValueError
		If ``demand_mean`` or ``demand_standard_deviation`` is ``None`` and 
		``demand_source`` is ``None``.
	ValueError
		If ``discount_factor`` <= 0 or > 1 for any time period.
	ValueError
		If ``terminal_holding_cost`` < 0 or ``terminal_stockout_cost`` < 0.
	ValueError
		If ``oul_matrix`` is provided but ``x_range`` is not, or ``x_range`` does not contain all
		values in ``oul_matrix``.


	**Equation Used** (equation (4.66)):

	.. math::

		\\theta_t(x) = \\min_{y \\ge x} \\{K\\delta(y-x) + c(y-x) + g(y) +
		\\gamma \\mathbb{E}_D[\\theta_{t+1}(y-D)]\\},

	where :math:`\\delta(z) = 1` if :math:`z>0` and :math:`0` otherwise,
	and where :math:`g(\\cdot)` is the newsvendor cost function.

	**Algorithm Used:** DP for finite-horizon inventory problem (Algorithm 4.1)

	**Truncation and Discretization** are performed as follows:

		1. Range of demand values is truncated at :math:`\\mu \pm` ``d_spread``:math:`\\sigma`,
		where :math:`\\mu` and :math:`\\sigma` are the mean and 
		standard deviation of the demand, truncating also at 0, and accounting conservatively
		for the variations in demand parameters across periods.

		2. If the total probability of demand outside the demand range in any time period
		is greater than ``trunc_tol``, a warning is issued.

		3. :math:`s` is estimated as the newsvendor solution and
		:math:`S` is estimated as :math:`s + Q_{EOQB}`, where :math:`Q_{EOQB}` is the
		order quantity from the EOQB problem. 

		4. ``s_spread``:math:`\\sigma` is subtracted from :math:`s` and added to :math:`S`
		to provide desired buffer, and :math:`\\mu + \\sigma` ``d_spread`` is subtracted 
		from :math:`s` to account for demand, accounting conservatively for the 
		variations in demand parameters across periods, and adjusting the final period
		to account for terminal costs.

		5. Range of :math:`x` values is set using these two bounds.

		6. When calculating :math:`H_t(y)`, the demand range is further truncated to avoid
		:math:`y-d` falling below the smallest value in the :math:`x`-range. 

		7. If, at any point in the optimization, the optimal order-up-to level for any :math:`x`
		and :math:`t` is the largest value in the :math:`x`-range, suggesting that the uppper end
		of the range is too low and that the optimal order-up-to level may be greater than it, the
		optimization is terminated, the upper end of the :math:`x`-range is doubled,
		and the optimization is restarted.

		8. If, at any point in the optimization, the total probability of demand values
		that could bring the inventory level below the smallest value in the :math:`x`-range is
		greater than ``trunc_tol``, suggesting that the lower end of the range is too high
		and that reasonable demand values could bump up against it, a warning is generated. 
		The optimization is not terminated, but the user may wish to try again with 
		a larger value of ``s_spread`` and/or ``d_spread``.

	**Example**:

	.. testsetup:: *

		from stockpyl.finite_horizon import *

	.. doctest::

		>>> s, S, cost, _, _, _ = finite_horizon_dp(5, 1, 20, 1, 20, 2, 50, 100, 20)
		>>> s
		[0, 110, 110, 110, 110, 111]
		>>> S
		[0, 133.0, 133.0, 133.0, 133.0, 126.0]
		>>> cost
		1558.6946467384012
	"""

	# Validate singleton parameters.
	if num_periods <= 0 or not is_integer(num_periods): raise ValueError("num_periods must be a positive integer")
	if terminal_holding_cost < 0: raise ValueError("terminal_holding_cost must be non-negative")
	if terminal_stockout_cost < 0: raise ValueError("terminal_stockout_cost must be non-negative")

	# Replace scalar parameters with lists (multiple copies of scalar).
	holding_cost = np.array(ensure_list_for_time_periods(holding_cost, num_periods, var_name="holding_cost"))
	stockout_cost = np.array(ensure_list_for_time_periods(stockout_cost, num_periods, var_name="stockout_cost"))
	purchase_cost = np.array(ensure_list_for_time_periods(purchase_cost, num_periods, var_name="purchase_cost"))
	fixed_cost = np.array(ensure_list_for_time_periods(fixed_cost, num_periods, var_name="fixed_cost"))
	discount_factor = np.array(ensure_list_for_time_periods(discount_factor, num_periods, var_name="discount_factor"))
	demand_mean = np.array(ensure_list_for_time_periods(demand_mean, num_periods, var_name="mean"))
	demand_sd = np.array(ensure_list_for_time_periods(demand_sd, num_periods, var_name="demand_sd"))
	demand_source = np.array(ensure_list_for_time_periods(demand_source, num_periods, var_name="demand_source"))

	# Build demand_source, if not provided; and get mean and SD, if demand_source is provided.
	# After this step, demand_mean[t], demand_sd[t], and demand_source[t] will be reliably set for all t.
	for t in range(1, num_periods + 1):
		if demand_source[t] is None:
			demand_source[t] = DemandSource(type='N', mean=demand_mean[t], standard_deviation=demand_sd[t])
		else:
			demand_mean[t] = demand_source[t].mean or demand_source[t].demand_distribution.mean()
			demand_sd[t] = demand_source[t].standard_deviation or demand_source[t].demand_distribution.std()

	# Validate other parameters.
	if not np.all(np.array(holding_cost[1:]) >= 0): raise ValueError("holding_cost must be non-negative")
	if not np.all(np.array(stockout_cost[1:]) >= 0): raise ValueError("stockout_cost must be non-negative")
	if not np.all(np.array(purchase_cost[1:]) >= 0): raise ValueError("purchase_cost must be non-negative")
	if not np.all(np.array(fixed_cost[1:]) >= 0): raise ValueError("fixed_cost must be non-negative")
	if not np.all(np.array(discount_factor[1:]) > 0) or \
		not np.all(np.array(discount_factor[1:]) <= 1): raise ValueError("discount_factor must be <0 and <=1")
	if not np.all(np.array(demand_mean[1:]) >= 0): raise ValueError("demand_mean must be non-negative")
	if not np.all(np.array(demand_sd[1:]) >= 0): raise ValueError("demand_sd must be non-negative")
	if (demand_mean is None or demand_sd is None) and demand_source is None:
		raise ValueError("You must provide either demand_mean and demand_standard_deviation, or demand_source")
	
	# Determine truncation for D: mu +/- d_spread * sigma (but no negative values)
	# (accounting appropriately for variations among periods)
	d_min = int(max(0, round(np.min(demand_mean[1:]) - d_spread * np.max(demand_sd[1:]))))
	d_max = int(round(np.max(demand_mean[1:]) + d_spread * np.max(demand_sd[1:])))
	d_range = np.array(range(d_min, d_max + 1))

	# Calculate total probability of demand outside d_range for each t, and
	# raise warning if > trunc_tol for any t. (prob is an array.)
	# Ignore entry 0 (o/w divide-by-0) but then add back an entry for 0 to keep
	# things consistent.
	prob = [demand_source[t].demand_distribution.cdf(d_min) + \
		    (1 - demand_source[t].demand_distribution.cdf(d_max)) for t in range(1, num_periods + 1)]
	# prob = norm.cdf(d_min, demand_mean[1:], demand_sd[1:]) + \
	# 	   (1 - norm.cdf(d_max, demand_mean[1:], demand_sd[1:]))
	prob = np.append([0], prob)
	if np.any(prob > trunc_tol):
		warnings.warn("Total probability of demand outside demand-truncation range exceeds trunc_tol for at least one period.")

	# Calculate alpha (= p/(p+h)) in each period.
	alpha = np.zeros(num_periods+1)
	alpha[0] = 0
	alpha[1:num_periods] = np.divide(stockout_cost[1:num_periods],
									 (stockout_cost[1:num_periods] + holding_cost[1:num_periods]))
	# Include terminal costs in alpha[T].
	alpha[num_periods] = \
		np.divide((stockout_cost[num_periods] + terminal_stockout_cost),
				  (stockout_cost[num_periods] + terminal_stockout_cost +
				   holding_cost[num_periods] + terminal_holding_cost))

	# Calculate newsvendor solution for each period, or use mu if sigma = 0.
	nv = np.zeros(num_periods+1)
	for t in range(1, num_periods+1):
		nv[t] = demand_mean[t]
#		if demand_sd[t] == 0:
#			nv[t] = mean[t]
#		else:
#			nv[t] = norm.ppf(alpha[t], mean[t], demand_sd[t])

	# Calculate EOQB.
	Q = [economic_order_quantity_with_backorders(fixed_cost[t], holding_cost[t],
			stockout_cost[t], demand_mean[t])[0] for t in range(1, num_periods+1)]

	# Determine initial truncation for x.
	# Did user specify oul_matrix?
	if oul_matrix is not None:
		user_provided_oul_matrix = True
		# Make sure x_range is also provided and contains all OULs.
		if x_range is None:
			raise ValueError('If oul_matrix is provided, then x_range must also be provided.')
		elif (np.amax(np.amax(oul_matrix)) not in x_range) or \
			(np.amin(np.amin(oul_matrix)) not in x_range):
			raise ValueError('x_range must contain all oul_matrix values.')
		else:
			x_min = int(np.amin(x_range))
			x_max = int(np.amax(x_range))
	elif x_range is not None:
		user_provided_oul_matrix = False
		x_min = int(np.amin(x_range))
		x_max = int(np.amax(x_range))
	else:
		user_provided_oul_matrix = False
		# - estimate s = newsvendor solution, S = s + EOQB
		# - then subtract s_spread * sigma from s and add s_spread * sigma to S
		# - then, subtract mu + d_spread * sigma from s to account for demand
		# (accounting appropriately for variations among periods, and adjusting
		# period T to include terminal costs)
		x_min = int(round(np.min(nv[1:]) - np.max(demand_mean[1:]) - np.max(demand_sd[1:]) * (s_spread + d_spread)))
		x_max = int(round(np.max(nv[1:]) + np.max(Q[1:]) + np.max(demand_sd[1:]) * s_spread))
		x_range = np.array(range(x_min, x_max+1))

	# Note:
	# - to get x value from index i, use x_range[i]
	# - to get index from x value, use x - x_min
	# Example: x_range = 10:20; then x_range[3] = 13 and 13 - x_min = 3.

	# Start with initial truncation range; abort, expand, and re-try if necessary.
	done = False
	while not done:

		# Allocate arrays.
		reorder_points = [0] * (num_periods+1)
		order_up_to_levels = [0] * (num_periods+1)
		cost_matrix = np.zeros((num_periods+2, len(x_range)))
		if not user_provided_oul_matrix:
			oul_matrix = np.zeros((num_periods+1, len(x_range)))
		H = np.zeros((num_periods+1, len(x_range)))

		# Initialize abort (will be set to true if range is not large enough)
		abort = False

		# Initialize warning flags (will be set to True when warnings are
		# issued to avoid duplication).
#		opt_warning = False

		# Calculate terminal costs.
		cost_matrix[num_periods+1, :] \
			= terminal_holding_cost * np.maximum(x_range, 0) + \
			  terminal_stockout_cost * np.maximum(-x_range, 0)

		# Loop backwards through periods.
		for t in range(num_periods, 0, -1):

			# Calculate probability vector for demand.
			if demand_source[t].is_discrete:
				prob = [demand_source[t].demand_distribution.pmf(d) for d in d_range]
			else:
				prob = [demand_source[t].demand_distribution.cdf(d + 0.5) - \
						demand_source[t].demand_distribution.cdf(d - 0.5) for d in d_range]
			# prob = norm.cdf(d_range + 0.5, demand_mean[t], demand_sd[t]) - \
			# 	   norm.cdf(d_range - 0.5, demand_mean[t], demand_sd[t])

			# Calculate H_t(y).
			for y in range(x_min, x_max + 1):

				# Initialize cost.
				cost = 0.0

				# Calculate n(y) and \bar{n}(y). 
				n, n_bar = lf.normal_loss(y, demand_mean[t], demand_sd[t])

				# Calculate current-period (newsvendor) cost.
				cost += holding_cost[t] * n_bar + stockout_cost[t] * n

				# Truncate demand range to avoid y-d exceeding x bounds.
				# Need x_min <= y - d <= x_max.
				# Therefore d_eff (d effective) must be between y - x_max
				# and y - x_min.
				d_eff = np.maximum(np.minimum(d_range, y - x_min), y - x_max)

				# Calculate amount of demand probability that was truncated
				# and issue warning if truncprob > trunc_tol
				#truncprob = np.dot(prob, d_range != d_eff)
				#if truncprob > trunc_tol:
				#	warnings.warn('Total probability of truncated demand exceeds trunc_tol: t = {:d}, y = {:d}, truncprob = {:f}'.format(t, y, truncprob))

				# Calculate future cost for this y.
				future_cost = discount_factor[t] * np.dot(prob,
								cost_matrix[t+1, y - d_eff - x_min])

				# Add future cost.
				cost += future_cost

				# Set H.
				H[t, y - x_min] = cost

			# Loop through possible x values.
			for x in range(x_min, x_max + 1):

				# Initialize best_cost to something big (keeps track of best
				# cost found for this t and x).
				best_cost = float("inf")

				# Did user provide oul_matrix? 
				if user_provided_oul_matrix:
					# Only consider y equal to value specified in oul_matrix.
					y_range = [oul_matrix[t, x - x_min]]
				else:
					# Consider y = x, ..., x_max.
					y_range = list(range(x, x_max + 1))

				# Loop through possible y values.
				for y in y_range:

					# Initialize cost.
					cost = 0.0

					# Calculate ordering cost.
					if y > x:
						cost += purchase_cost[t] * (y - x) + fixed_cost[t]

					# Add H_t(y).
					cost += H[t, int(y - x_min)]

					# Compare cost to current best.
					if cost < best_cost:
						best_cost = cost
						best_y = y

						# If this is the largest y in range (and range has more
						# than one element), abort and increase upper range.
						if y == x_max and x < x_max:
							if user_provided_oul_matrix:
								warnings.warn('Cost is still decreasing at upper end of y range; did not increase upper range '
					 						'because oul_matrix was provided: t = {:d}, x = {:d}, y = {:d}.'.format(t, x, y))
							else:
								warnings.warn('Cost is still decreasing at upper end of y range; increasing upper range '
											'and retrying: t = {:d}, x = {:d}, y = {:d}.'.format(t, x, y))
								abort = True
								x_max = x_max * 2
								x_range = np.array(range(x_min, x_max + 1))
								break

				# If abort flag was set in for-y loop, exit for-x loop.
				if abort:
					break

				# Store best cost and best action for this t, x.
				cost_matrix[t, x - x_min] = best_cost
				oul_matrix[t, x - x_min] = best_y

			# If abort flag was set in for-y loop, exit for-t loop.
			if abort:
				break
			else:
				# Determine s^*_t and S^*_t.
				# S^*_t = OUL for first x-value in range.
				order_up_to_levels[t] = oul_matrix[t, 0]
				# s^*_t = largest x s.t. y_t[x] = S^*_t
				reorder_points[t] = x_range[0]
				while oul_matrix[t, reorder_points[t] + 1 - x_min] \
					== order_up_to_levels[t] and reorder_points[t] < x_max:
					reorder_points[t] += 1

			# Raise warning if truncation makes it so that probability of
			# demand bringing IL below x_range > trunc_tol (i.e., if
			# P(s - D < x_min) > trunc_tol). (Issue warning in each period
			# in which there is a violation.)
			prob_demand_below_range = 1 - \
				demand_source[t].demand_distribution.cdf(reorder_points[t] - x_min)
			# prob_demand_below_range = 1 - \
			# 	norm.cdf(reorder_points[t] - x_min, demand_mean[t], demand_sd[t])
			if prob_demand_below_range > trunc_tol:
				warnings.warn('Probability that demand brings IL below x-truncation range exceeds trunc_tol: t = {:d}, prob = {:f}'.format(t, prob_demand_below_range))

		# If made it through all t without abort flag, set done = True.
		if not abort:
			done = True

	# Calculate expected total cost.
	total_cost = cost_matrix[1, int(initial_inventory_level) - x_min]

	return reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, x_range


def myopic_bounds(
		num_periods,
		holding_cost,
		stockout_cost,
		terminal_holding_cost,
		terminal_stockout_cost,
		purchase_cost,
		fixed_cost,
		demand_mean,
		demand_sd,
		discount_factor=1.0):
	"""
	Calculate the "myopic" bounds for the finite-horizon inventory optimization problem,
	with or without fixed costs. 

	See Sections 4.3.3 and 4.4.3 of |fosct| for discussion and
	notation.

	The myopic bounds :math:`\\bar{s}_t`, :math:`\\underline{S}_t`,
	and :math:`\\bar{S}_t` are denoted :math:`r^+(t)`, :math:`s^+(t)`, and :math:`s^++(t)`,
	respectively, in Zipkin (2000). (Zipkin does not have an analogous quantity
	to :math:`\\underline{s}_t`.) They are not used in |fosct|, 
	but the bounds are given in terms of |fosct| notation below.

	Demands are assumed to be normally distributed.

	Most parameters may be given as a singleton or a list. If given as a
	singleton, the parameter will be assumed to be the same in every time
	period. If given as a list, the list must be of length ``num_periods`` or
	``num_periods``\+1.

	*	In the former case, the list is assumed to contain values for periods
		1, ..., ``num_periods`` in elements 0, ..., ``num_periods``-1.
	*	In the latter case, the list is assumed to contain values for periods
		1, ..., ``num_periods`` in elements 1, ..., ``num_periods``, and the
		0th element is ignored.

	The parameters may be mixed, some scalars and some lists.

	Output arrays are all 1-indexed; for example, ``S_underbar[5]`` gives
	:math:`\\underline{s}_5`, the lower bound on :math:`s_5`.

	Parameters
	----------
	num_periods : int
		Number of periods in time horizon. [:math:`T`]
	holding_cost : float or list
		Holding cost per item per period. [:math:`h`]
	stockout_cost : float or list
		Stockout cost per item per period. [:math:`p`]
	terminal_holding_cost : float
		Terminal holding cost per item. [:math:`h_T`]
	terminal_stockout_cost : float
		Terminal stockout cost per item. [:math:`p_T`]
	purchase_cost : float or list
		Purchase cost per item. [:math:`c`]
	fixed_cost : float or list
		Fixed cost per order. [:math:`K`]
	demand_mean : float or list
		Demand mean per period. [:math:`\\mu`]
	demand_sd : float or list
		Demand standard deviation per period. [:math:`\\sigma`]
	discount_factor : float or list
		Discount factor, in :math:`(0,1]`. Default = 1. [:math:`\\gamma`]

	Returns
	-------
	S_underbar : ndarray
		List of myopic lower bounds on :math:`S_t`. [:math:`\\underline{S}_t`]
	S_overbar : ndarray
		List of myopic upper bounds on :math:`S_t`. [:math:`\\bar{S}_t`]
	s_underbar : ndarray
		List of myopic lower bounds on :math:`s_t`. [:math:`\\underline{s}_t`]
	s_overbar : ndarray
		List of myopic upper bounds on :math:`s_t`. For periods ``t`` in which
		``fixed_cost[t] - discount_factor[t] * fixed_cost[t+1] < 0``,
		``s_overbar[t] = None``. (``s_overbar`` is invalid in these cases.) [:math:`\\bar{s}_t`]

	Raises
	------
	ValueError
		If ``num_periods`` <= 0 or is non-integer.
	ValueError
		If ``holding_cost``, ``stockout_cost``, ``purchase_cost``, ``fixed_cost``,
		``demand_mean``, or ``demand_sd`` < 0 for any time period.
	ValueError
		If ``discount_factor`` <= 0 or > 1 for any time period.
	ValueError
		If ``purchase_cost[t] - discount_factor[t] * purchase_cost[t+1]`` is
		less than ``-holding_cost[t]`` or greater than ``stockout_cost[t]``
		for some ``t``. (This is required for myopic policy to be valid.)


	**Equations Used:**

	.. math::

		\\underline{S}_t = \\text{optimizer of } G_t(y)

	.. math::

		\\bar{S}_t = \\text{the value of } y > \\underline{S}_t \\text{ such that } G_t(y) = G_t(\\underline{S}_t) + \\gamma_tK_{t+1}

	.. math::

		\\underline{s}_t = \\text{the value of } y \\le \\underline{S}_t \\text{ such that } G_t(y) = G_t(\\underline{S}_t) + K_t

	.. math::

		\\bar{s}_t = \\text{the value of } y \\le \\underline{S}_t \\text{ such that } G_t(y) = G_t(\\underline{S}_t) + K_t - \\gamma_tK_{t+1},

	where :math:`G_t(y)` is the myopic newsvendor cost function in period :math:`t`,
	denoted :math:`G_i(y)` in Veinott (1966) and
	as :math:`C^+(t,y)` in Zipkin (2000), and is implemented in :func:`stockpyl.newsvendor.myopic`.)

	In the fourth equation, if :math:`K_t - \\gamma_tK_{t+1} < 0`, then :math:`\\bar{s}_t` is invalid and
	``s_overbar[t]`` is set to ``None``.


	References
	----------
	A. F. Veinott, Jr., On the Optimality of :math:`(s,S)` Inventory Policies:
	New Conditions and a New Proof, *J. SIAM Appl. Math* 14(5), 1067-1083 (1966).

	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.finite_horizon import *

	.. doctest::

		>>> S_underbar, S_overbar, s_underbar, s_overbar = myopic_bounds(5, 1, 20, 1, 20, 2, 50, 100, 20)
		>>> S_underbar[1], S_overbar[1], s_underbar[1], s_overbar[1]
		(133.36782387894158, 191.66022942788436, 110.26036848597217, 133.36782387894158)

	"""

	# Validate singleton parameters.
	assert num_periods > 0 and is_integer(num_periods), "num_periods must be a positive integer."
	assert terminal_holding_cost >= 0, "terminal_holding_cost must be non-negative"
	assert terminal_stockout_cost >= 0, "terminal_stockout_cost must be non-negative"

	# Replace scalar parameters with lists (multiple copies of scalar).
	holding_cost = np.array(ensure_list_for_time_periods(holding_cost, num_periods, var_name="holding_cost"))
	stockout_cost = np.array(ensure_list_for_time_periods(stockout_cost, num_periods, var_name="stockout_cost"))
	purchase_cost = np.array(ensure_list_for_time_periods(purchase_cost, num_periods, var_name="purchase_cost"))
	fixed_cost = np.array(ensure_list_for_time_periods(fixed_cost, num_periods, var_name="fixed_cost"))
	discount_factor = np.array(ensure_list_for_time_periods(discount_factor, num_periods, var_name="discount_factor"))
	demand_mean = np.array(ensure_list_for_time_periods(demand_mean, num_periods, var_name="mean"))
	demand_sd = np.array(ensure_list_for_time_periods(demand_sd, num_periods, var_name="demand_sd"))

	# Validate other parameters.
	assert np.all(np.array(holding_cost[1:]) >= 0), "holding_cost must be non-negative."
	assert np.all(np.array(stockout_cost[1:]) >= 0), "stockout_cost must be non-negative."
	assert np.all(np.array(purchase_cost[1:]) >= 0), "purchase_cost must be non-negative."
	assert np.all(np.array(fixed_cost[1:]) >= 0), "fixed_cost must be non-negative."
	assert np.all(np.array(discount_factor[1:]) > 0) and \
		   np.all(np.array(discount_factor[1:]) <= 1), "discount_factor must be <0 and <=1."
	assert np.all(np.array(demand_mean[1:]) >= 0), "mean must be non-negative."
	assert np.all(np.array(demand_sd[1:]) >= 0), "demand_sd must be non-negative."

	# Redefine holding and stockout costs in last period to include terminal
	# costs, and set c_{T+1} = K_{T+1} = 0.
	h = holding_cost.copy()
	h[num_periods] += terminal_holding_cost
	p = stockout_cost.copy()
	p[num_periods] += terminal_stockout_cost
	c = list(purchase_cost.copy())
	c.append(0)
	K = list(fixed_cost.copy())
	K.append(0)

	# Calculate c_plus (c^+_t = c_t - gamma * c_{t+1}) and check that it is
	# nonegative for every t. (Otherwise, the costs increase too quickly and
	# the myopic policy is not valid.)
	c_plus = np.zeros(num_periods+1)
	for t in range(1, num_periods):
		c_plus[t] = c[t] \
					- discount_factor[t] * c[t+1]
		if c_plus[t] < -h[t] or c_plus[t] > p[t]:
			raise ValueError("myopic policy requires -h_t <= c_t - gamma * c_{t+1} <= p_t for all t")

	# Initialize output arrays.
	S_underbar = np.zeros(num_periods+1)
	S_overbar = np.zeros(num_periods+1)
	s_underbar = np.zeros(num_periods+1)
	s_overbar = np.zeros(num_periods+1)

	# Loop through periods.
	for t in range(1, num_periods+1):

		# Calculate S_underbar (= optimizer of G_t(.)).
		S_underbar[t], G_S_underbar = myopic(h[t], p[t], c[t], c[t+1], demand_mean[t], demand_sd[t], discount_factor[t])

		# Set S_overbar to y >= S_underbar s.t. G_t(y) = G_t(S_underbar) + gamma_t * K_{t+1}.
		S_overbar[t] = set_myopic_cost_to(G_S_underbar + discount_factor[t] * K[t+1],
										  h[t], p[t], c[t], c[t+1], demand_mean[t],
										  demand_sd[t], discount_factor[t], left_half=False)

		# Set s_underbar to y <= S_underbar s.t. G_t(y) = G_t(S_underbar) + K_t.
		s_underbar[t] = set_myopic_cost_to(G_S_underbar + K[t],
										   h[t], p[t], c[t], c[t+1], demand_mean[t],
										   demand_sd[t], discount_factor[t], left_half=True)

		# Set s_overbar to y <= S_underbar s.t. G_t(y) = G_t(S_underbar) + K_t - gamma_t * K_{t+1},
		# unless K_t - gamma_t * K_{t+1} < 0, in which case set to None.
		if K[t] - discount_factor[t] * K[t+1] >= 0:
			s_overbar[t] = set_myopic_cost_to(G_S_underbar + K[t] - discount_factor[t] * K[t+1],
											  h[t], p[t], c[t], c[t+1], demand_mean[t],
											  demand_sd[t], discount_factor[t], left_half=True)
		else:
			s_overbar[t] = None

	return S_underbar, S_overbar, s_underbar, s_overbar

