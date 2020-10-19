"""Code for optimizing multi-echelon inventory systems using a variety of
generic methods.

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the ``SupplyChainNetwork`` and the ``SupplyChainNode``s
that it contains, which contains all of the data for the optimization instance.

(c) Lawrence V. Snyder
Lehigh University

"""

import numpy as np
from itertools import product
from tqdm import tqdm				# progress bar

from pyinv.supply_chain_network import *
from pyinv.helpers import *
from pyinv.sim import *
from pyinv.ssm_serial import *
from pyinv.instances import *
from pyinv import optimization


# -------------------

# HELPER FUNCTIONS

def truncate_and_discretize(network, values=None, truncation_lo=None,
						truncation_hi=None, discretization_step=None,
						discretization_num=None):
	"""Determine truncated and discretized set of values for each node in network.

	* If ``values`` is provided, it is assumed to be a dictionary of truncated
	and discretized values, and it is returned without modification.
	* If ``truncation_lo``, ``truncation_hi``, and ``discretization_step`` or
	``discretization_num`` are provided, these are used to determine the set of values.
	* ``truncation_lo``, ``truncation_hi``, ``discretization_step``, and
	``discretization_num`` may each either be a dictionary (with keys equal to
	node indices) or a singleton. If a singleton, the same value will be used for all nodes.
	* If any or all of ``truncation_lo``, ``truncation_hi``, ``discretization_step``,
	and ``discretization_num`` are omitted, they will be set automatically:
		- ``truncation_lo'' is set to 0.
		- ``truncation_hi`` is set to 100.
		- ``discretization_step`` is set to 1 and ``discretization_num`` is set to
		(``truncation_hi`` - ``truncation_lo``) / ``discretization_step``.
		# TODO: use demand distribution to set lo and hi, even at upstream nodes

	Parameters
	----------
	network : SupplyChainNetwork
	values : dict, optional
		Dictionary in which keys are node indices and values are lists of
		truncated, discretized values; if provided, it is returned without modification.
	truncation_lo : float or dict, optional
		A float or dictionary indicating, for each node index, the low end of the
		truncation range for values to test for that node. If float,
		the same value is used for every node. If omitted, it is set automatically.
	truncation_hi : float or dict, optional
		A dictionary indicating, for each node index, the high end of the
		truncation range for values levels to test for that node. If float,
		the same value is used for every node. If omitted, it is set automatically.
	discretization_step : float or dict, optional
		A dictionary indicating, for each node index, the interval width to use
		for discretization of the values to test for that node. If float,
		the same value is used for every node. If omitted, it is set automatically.
	discretization_num : int or dict, optional
		A dictionary indicating, for each node index, the number of intervals to use
		for discretization of the values to test for that node. If int,
		the same value is used for every node. If omitted, it is set automatically.
		Ignored if ``discretization_step`` is provided.

	Returns
	-------
	truncated_discretized_values : dict
		Dictionary indicating a list of truncated, discretized values for each
		node index.
	"""

	# Define constants for default truncation and discretization settings.
	DEFAULT_LO = 0
	DEFAULT_HI = 100
	DEFAULT_STEP = 1

	# Were values already provided?
	if values is not None:
		truncated_discretized_values = values
	else:
		# Determine lo, hi, step, and num.
		lo_dict = ensure_dict_for_nodes(truncation_lo, network.node_indices)
		hi_dict = ensure_dict_for_nodes(truncation_hi, network.node_indices)
		step_dict = ensure_dict_for_nodes(discretization_step, network.node_indices)
		num_dict = ensure_dict_for_nodes(discretization_num, network.node_indices)

		# Initialize output dict.
		truncated_discretized_values = {}

		# Loop through nodes.
		for n in network.nodes:

			# Determine lo, hi, step/num for each node. If not provided,
			# use default settings.
			# TODO: what if lead_time_demand_distribution is not provided by demand_source object?
			lo = lo_dict[n.index] or DEFAULT_LO
			hi = hi_dict[n.index] or DEFAULT_HI
			if step_dict[n.index] is not None:
				step = step_dict[n.index]
			elif num_dict[n.index] is not None:
				num = num_dict[n.index]
				step = (hi - lo) / (num - 1)
			else:
				step = DEFAULT_STEP

			truncated_discretized_values[n.index] = np.arange(lo, hi+step, step).tolist()

	return truncated_discretized_values


# -------------------

# ENUMERATION

def meio_by_enumeration(network, base_stock_levels=None, truncation_lo=None,
						truncation_hi=None, discretization_step=None,
						discretization_num=None, objective_function=None,
						sim_num_trials=10, sim_num_periods=1000, sim_rand_seed=None,
						progress_bar=True, print_solutions=False):
	"""Optimize the MEIO instance by enumerating the combinations of values of the
	base-stock levels. Evaluate each combination using the provided objective
	function, or simulation if not provided.

	# TODO: generalize to allow parameters other than BSL

	Parameters
	----------
	network : SupplyChainNetwork
		The network to optimize.
	base_stock_levels : dict, optional
		A dictionary indicating, for each node index, the base-stock levels to
		test in the enumeration. Example: {0: [0, 5, 10, 15], 1: [0, 2, 4, 6]}.
	truncation_lo : float or dict, optional
		A float or dictionary indicating, for each node index, the low end of the
		truncation range for values to test for that node. If float,
		the same value is used for every node. If omitted, it is set automatically.
	truncation_hi : float or dict, optional
		A dictionary indicating, for each node index, the high end of the
		truncation range for values levels to test for that node. If float,
		the same value is used for every node. If omitted, it is set automatically.
	discretization_step : float or dict, optional
		A dictionary indicating, for each node index, the interval width to use
		for discretization of the values to test for that node. If float,
		the same value is used for every node. If omitted, it is set automatically.
	discretization_num : int or dict, optional
		A dictionary indicating, for each node index, the number of intervals to use
		for discretization of the values to test for that node. If int,
		the same value is used for every node. If omitted, it is set automatically.
		Ignored if ``discretization_step`` is provided.
	objective_function : function, optional
		The function to use to evaluate a given solution. The function must take
		a single argument, the dictionary of base-stock levels, and return a
		single output, the expected cost per period. If omitted, simulation
		will be used.
	sim_num_trials : int, optional
		Number of trials to run in each simulation. Ignored if ``objective_function``
		is provided.
	sim_num_periods : int, optional
		Number of periods per trial in each simulation. Ignored if ``objective_function''
		is provided.
	sim_rand_seed : int, optional
		Rand seed to use for simulation. Ignored if ``objective_function'' is provided.
	progress_bar : bool, optional
		Display a progress bar? Ignored if ``print_solutions`` is True.
	print_solutions : bool, optional
		Print each solution and its cost?

	Returns
	-------
	best_S : dict
		Dict of best base-stock levels found.
	best_cost : float
		Best cost found.

	"""

	# Determine base-stock levels to test by truncating and discretizing
	# according to preferences specified.
	# (If base_stock_levels is not None, these will simply be returned.)
	S_dict = truncate_and_discretize(network, base_stock_levels, truncation_lo,
								truncation_hi, discretization_step, discretization_num)

	# Get Cartesian product of all base-stock levels. The line below creates a
	# list of dicts, each of which is one of the enumerated solutions and gives
	# the base-stock levels for each node.
	# See https://stackoverflow.com/a/40623158/3453768.
	enumerated_solutions = list((dict(zip(S_dict, x)) for x in product(*S_dict.values())))

	# Do progress bar?
	do_bar = progress_bar and not print_solutions

	# Initialize progress bar. (If not requested, then this will disable it.)
	pbar = tqdm(total=len(enumerated_solutions), disable=not do_bar)

	# Initialize best-solution tracker.
	best_cost = np.inf

	# Loop through enumerated solutions.
	for S in enumerated_solutions:

		# Update progress bar.
		pbar.update()

		# Was an objective function provided?
		if objective_function is not None:
			mean_cost = objective_function(S)
		else:
			# Set base-stock levels for all nodes.
			for n in network.nodes:
				n.inventory_policy.base_stock_level = S[n.index]
			# Run multiple trials of simulation to evaluate solution.
			mean_cost, _ = run_multiple_trials(network, sim_num_trials, sim_num_periods,
											   sim_rand_seed, progress_bar=False)

		# Compare to best solution found so far.
		# TODO: do something with sem?
		if mean_cost < best_cost:
			best_cost = mean_cost
			best_S = S

		# Print solution, if requested.
		if print_solutions:
			print_str = "S = {} cost = {}".format(S, mean_cost)
			if mean_cost < best_cost:
				print_str += ' *'
			print(print_str)

	# Close progress bar.
	pbar.close()

	return best_S, best_cost


# -------------------

# COORDINATE DESCENT

def base_stock_level_bisection_search(network, node_to_optimize, lo=None, hi=None,
						objective_function=None,
						sim_num_trials=10, sim_num_periods=1000, sim_rand_seed=None,
						tolerance=1e-2):
	"""Optimize the base-stock level for one node using bisection search.
	Evaluate each solution using the provided objective function, or simulation if not provided.

	Parameters
	----------
	network : SupplyChainNetwork
		The supply chain network.
	node_to_optimize : SupplyChainNode
		The supply chain node to optimize.
	lo : float, optional
		The low end of the search range. If omitted, it is set automatically.
	hi : float, optional
		The high end of the search range. If omitted, it is set automatically.
	objective_function : function, optional
		The function to use to evaluate a given solution. If omitted, simulation
		will be used.
	sim_num_trials : int, optional
		Number of trials to run in each simulation. Ignored if ``objective_function``
		is provided.
	sim_num_periods : int, optional
		Number of periods per trial in each simulation. Ignored if ``objective_function''
		is provided.
	sim_rand_seed : int, optional
		Rand seed to use for simulation. Ignored if ``objective_function'' is provided.
	tolerance : float, optional
		Absolute tolerance to use for convergence. The algorithm terminates when
		the absolute difference between the current bounds is less than the tolerance.

	Returns
	-------
	base_stock_level : float
		Best base-stock level found for the node.
	cost : float
		Cost of best solution found.
	"""

	# Determine bounds, if not provided.
	# TODO: do this better
	if lo is None:
		lo = 0
	if hi is None:
		hi = 3 * np.sum([s.demand_source.mean for s in network.sink_nodes])

	# Determine initial lo, hi, and midpoint for bisection search.
	S_lo = lo
	S_hi = hi
	S = (S_lo + S_hi) / 2

	# Calculate cost at


def meio_by_coordinate_descent(network, initial_solution=None,
							   search_lo=None, search_hi=None,
							   objective_function=None,
							   sim_num_trials=10, sim_num_periods=1000, sim_rand_seed=None,
							   tol=1e-2, line_search_tol=1e-4, verbose=False):
	"""Optimize the MEIO instance by coordinate descent on the
	base-stock levels. Evaluate each solution using the provided objective
	function, or simulation if not provided.

	# TODO: generalize to allow parameters other than BSL

	Parameters
	----------
	network : SupplyChainNetwork
		The network to optimize.
	initial_solution : dict, optional
		The starting solution, as a dict. If omitted, initial solution will be set
		automatically.
	search_lo : float or dict, optional
		A float or dictionary indicating, for each node index, the low end of the
		search range for that node. If float, the same value is used for every node.
		If omitted, it is set automatically.
	search_hi : float or dict, optional
		A dictionary indicating, for each node index, the high end of the
		search range for that node. If float, the same value is used for every node.
		If omitted, it is set automatically.
	objective_function : function, optional
		The function to use to evaluate a given solution. If omitted, simulation
		will be used.
	sim_num_trials : int, optional
		Number of trials to run in each simulation. Ignored if ``objective_function``
		is provided.
	sim_num_periods : int, optional
		Number of periods per trial in each simulation. Ignored if ``objective_function''
		is provided.
	sim_rand_seed : int, optional
		Rand seed to use for simulation. Ignored if ``objective_function'' is provided.
	tol : float, optional
		Algorithm terminates when iteration fails to improve objective function by
		more than tol.
	line_search_tol : float, optional
		Tolerance to use for line search (golden section search) component of algorithm.
	verbose: bool, optional
		Set to True to print messages at each iteration.
	Returns
	-------
	best_S : dict
		Dict of best base-stock levels found.
	best_cost : float
		Best cost found.

	"""

	# Determine initial solution.
	if initial_solution is None:
		# TODO: do this better -- set to mean implied demand
		initial_solution = {}
		for n in network.nodes:
			initial_solution[n.index] = np.sum([s.demand_source.mean for s in network.sink_nodes])

	# Determine bounds for search, if not provided.
	lo = ensure_dict_for_nodes(search_lo, network.node_indices)
	hi = ensure_dict_for_nodes(search_hi, network.node_indices)
	# TODO: do this better
	for n in network.nodes:
		if lo[n.index] is None:
			lo[n.index] = 0
		if hi[n.index] is None:
			hi[n.index] = 3 * np.sum([s.demand_source.mean for s in network.sink_nodes])

	# Shortcut to objective function.
	def obj_fcn(S):
		if objective_function is not None:
			return objective_function(S)
		else:
			# Set base-stock levels for all nodes.
			for n in network.nodes:
				n.inventory_policy.base_stock_level = S[n.index]
			# Run multiple trials of simulation to evaluate solution.
			cost, _ = run_multiple_trials(network, sim_num_trials, sim_num_periods, sim_rand_seed,
												  progress_bar=False)
			return cost

	# Initialize current solution and cost.
	current_soln = initial_solution
	current_cost = obj_fcn(current_soln)

	# Print message, if requested.
	if verbose:
		print("Initial solution = {} initial cost = {}".format(current_soln, current_cost))

	# Initialize done flag.
	done = False
	t = 0

	# Loop until cost does not improve by more than tol.
	while not done:

		# Loop through all nodes, optimizing base-stock level for each in turn.
		for n in network.nodes:

			# Optimize base-stock level for node using golden-section search.
			f = lambda Sn: obj_fcn({i.index: Sn if i.index == n.index else current_soln[i.index] for i in network.nodes})
			best_Sn, best_cost = optimization.golden_section_search(f, lo[n.index], hi[n.index], tol=line_search_tol, verbose=False)

			# Replace base-stock level in current_solution with new value.
			current_soln[n.index] = best_Sn

			# Print message, if requested.
			if verbose:
				print("Iteration {} node {} best_S[n] = {} best_cost = {} current_soln = {}".format(t, n.index, best_Sn, best_cost, current_soln))

		# Check improvement since last iteration.
		if best_cost >= current_cost - tol:
			# Terminate.
			done = True
		else:
			current_cost = best_cost
			t += 1

	return current_soln, best_cost


#
# network = get_named_instance("example_6_1")
#
# # reindex nodes N, ..., 1 (ssm_serial.expected_cost() requires it)
# network.reindex_nodes({0: 1, 1: 2, 2: 3})
# obj_fcn = lambda S: expected_cost(network, local_to_echelon_base_stock_levels(network, S), x_num=100, d_num=10)
# best_S, best_cost = meio_by_coordinate_descent(network,
# 										initial_solution=echelon_to_local_base_stock_levels(network, {1: 6.49, 2: 12.02, 3: 22.71}),
# 										objective_function=obj_fcn, verbose=True)
# best_S, best_cost = meio_by_enumeration(network,
# 										truncation_lo={1: 5, 2: 4, 3: 10},
#  										truncation_hi={1: 7, 2: 7, 3: 12},
# 										objective_function=obj_fcn)

#
# # T = 1000
# # total_cost = simulation(network, T)
# # print(total_cost / T)
#
# best_S, best_cost = meio_by_enumeration(network,
# 										truncation_lo={0: 5, 1: 4, 2: 10},
# 										truncation_hi={0: 7, 1: 7, 2: 12},
# 										sim_num_trials=5, sim_num_periods=500,
# 										sim_rand_seed=762,
# 										print_solutions=True)
# best_S, best_cost = meio_by_enumeration(network,
# 										truncation_lo=55,
# 										truncation_hi=58,
# 										discretization_step=0.1,
# 										sim_num_trials=5, sim_num_periods=500,
# 										sim_rand_seed=762,
# 										print_solutions=True)
#
#print("best_S = {}, best_cost = {}".format(best_S, best_cost))