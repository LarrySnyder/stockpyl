# ===============================================================================
# stockpyl - meio_general Module
# -------------------------------------------------------------------------------
# Updated: 01-30-2022
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------


For MEIO systems with arbitrary topology (not necessarily serial or tree systems),
the |mod_meio_general| module can optimize base-stock levels approximately using
relatively brute-force approaches—either coordinate descent or enumeration. These
heuristics tend to be quite slow and not particularly accurate, but they are sometimes
the best methods available for complex systems that are not well solved in the literature.

.. note:: |node_stage|

.. note:: |fosct_notation|


The primary data object is the |class_network| and the |class_node| objects
that it contains, which contains all of the data for the optimization instance.



For either the enumeration or the coordinate descent approache, you may provide an objective function that will be used to evaluate
each candidate solution, or you may omit the objective function and the algorithm will
evaluate solutions using simulation. Obviously, evaluating using simulation is typically
much slower than using an objective function.

The :func:`~stockpyl.meio_general.meio_by_enumeration` function allows you to control
how the enumeration is performed (i.e., how the search space is truncated and discretized),
or you can specify the exact base-stock levels to test for each node. 

In the code snippet below, we solve Example 6.1 from |fosct| using enumeration.
We specify upper and lower bounds on the base-stock levels to test for each node and
evaluate each candidate set of base-stock levels using simulation (3 trials, 
100 periods per trial—a very coarse approximation since the simulation runs are very small):

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> from stockpyl.meio_general import meio_by_enumeration
		>>> from stockpyl.instances import load_instance
		>>> example_6_1_network = load_instance("example_6_1")
		>>> best_S, best_cost = meio_by_enumeration(
		...		network=example_6_1_network, 
		...		truncation_lo={1: 5, 2: 4, 3: 10}, 
		...		truncation_hi={1: 7, 2: 7, 3: 12}, 
		...		sim_num_trials=3, 
		...		sim_num_periods=100, 
		...		sim_rand_seed=42
		...	)
		>>> best_S
		{1: 7, 2: 6, 3: 10}
		>>> best_cost
		65.0337132520378

This solution is not good—it is 36.4% worse than the optimal solution—even though we stacked the
deck by giving the function a pretty narrow range of base-stock levels to test. The solution would improve
if we used more simulation trials and more periods per trial, but then 
the execution would be even slower.

Alternately, we can provide an objective function. This is more accurate and faster than
evaluating solutions using simulation, but if the objective function must be evaluated numerically
(as it does for serial SSM systems), speed and accuracy are still non-trivial issues to consider.
In the code below, we first define an objective function using a Python lambda function;
it evaluates each solution by first converting the local base-stock levels to echelon and then 
passing them to the :func:`~stockpyl.ssm_serial.expected_cost` function for serial SSM systems,
which requires echelon base-stock levels as inputs. The discretization settings used below
(``x_num=100, d_num=10``) are relatively coarse, producing inaccurate solutions but pretty quickly.

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> from stockpyl.ssm_serial import expected_cost
		>>> from stockpyl.supply_chain_network import local_to_echelon_base_stock_levels
		>>> obj_fcn = lambda S: expected_cost(local_to_echelon_base_stock_levels(example_6_1_network, S), network=example_6_1_network, x_num=100, d_num=10)
		>>> best_S, best_cost = meio_by_enumeration(
		...     network=example_6_1_network, 
		...     truncation_lo={1: 5, 2: 4, 3: 10},
		...     truncation_hi={1: 7, 2: 7, 3: 12}, 
		...     objective_function=obj_fcn
		... )
		>>> best_S
		{1: 7, 2: 5, 3: 11}
		>>> best_cost
		48.21449789525488

The :func:`~stockpyl.meio_general.meio_by_coordinate_descent` function optimizes (approximately)
using `coordinate descent <https://en.wikipedia.org/wiki/Coordinate_descent>`_. In principle, 
coordinate descent will find the globally optimal solution if the objective function is
jointly convex in the base-stock levels, but if solutions are evaluated using simulation,
then there are no guarantees. Just as with the :func:`~stockpyl.meio_general.meio_by_enumeration` function,
:func:`~stockpyl.meio_general.meio_by_coordinate_descent` can evaluate solutions based on either
simulation or a provided objective function. And like enumeration, coordinate descent can be quite slow
and not particularly accurate.

	
	.. doctest::
		:skipif: True	# set to False to run the test

		>>> from stockpyl.meio_general import meio_by_coordinate_descent
		>>> from stockpyl.ssm_serial import expected_cost
		>>> from stockpyl.supply_chain_network import local_to_echelon_base_stock_levels
		>>> best_S, best_cost = meio_by_coordinate_descent(
		...		network=example_6_1_network, 
		...		search_lo={1: 5, 2: 4, 3: 10}, 
		...		search_hi={1: 7, 2: 7, 3: 12}, 
		...		sim_num_trials=3, 
		...		sim_num_periods=100, 
		...		sim_rand_seed=762
		...	)
		>>> best_S
		{1: 6.381339837124608, 2: 5.896080179686133, 3: 10.048610642262988}
		>>> best_cost
		65.79707993192646

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> obj_fcn = lambda S: expected_cost(local_to_echelon_base_stock_levels(example_6_1_network, S), network=example_6_1_network, x_num=20, d_num=10)
		>>> best_S, best_cost = meio_by_coordinate_descent(
		...		example_6_1_network, 
		...		search_lo={1: 5, 2: 4, 3: 10},
		...     search_hi={1: 7, 2: 7, 3: 12}, 
		...		objective_function=obj_fcn
		...	)
		>>> best_S
		{1: 5.892036436905893, 2: 5.995771265226075, 3: 11.99995914365099}
		>>> best_cost
		62.33491040676202

API Reference
-------------
"""

import numpy as np
from itertools import product
from tqdm import tqdm				# progress bar

from stockpyl.supply_chain_network import *
from stockpyl.helpers import *
from stockpyl.sim import *
from stockpyl.ssm_serial import *
from stockpyl.instances import *
import stockpyl.optimization as optimization


# -------------------

# ENUMERATION

def meio_by_enumeration(network, base_stock_levels=None, truncation_lo=None,
						truncation_hi=None, discretization_step=None,
						discretization_num=None, groups=None, objective_function=None,
						sim_num_trials=10, sim_num_periods=1000, sim_rand_seed=None,
						progress_bar=True, print_solutions=False):
	"""Optimize the MEIO instance by enumerating the combinations of values of the
	base-stock levels. Evaluate each combination using the provided objective
	function, or simulation if not provided.

	Parameters
	----------
	network : |class_network|
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
	groups : list of sets, optional
		A list of sets, each of which contains indices of nodes that should have the
		same base-stock level. This speeds the optimization since the base-stock
		levels for the nodes in a given group do not have to be optimized individually.
		Any nodes not contained in any set in the list are optimized individually.
		If omitted, all nodes are optimized individually.
	objective_function : function, optional
		The function to use to evaluate a given solution. The function must take
		a single argument, the dictionary of base-stock levels, and return a
		single output, the expected cost per period. If omitted, simulation
		will be used.
	sim_num_trials : int, optional
		Number of trials to run in each simulation. Ignored if ``objective_function``
		is provided.
	sim_num_periods : int, optional
		Number of periods per trial in each simulation. Ignored if ``objective_function``
		is provided.
	sim_rand_seed : int, optional
		Rand seed to use for simulation. Ignored if ``objective_function`` is provided.
	progress_bar : bool, optional
		Display a progress bar? Ignored if ``print_solutions`` is ``True``.
	print_solutions : bool, optional
		Print each solution and its cost?

	Returns
	-------
	best_S : dict
		Dict of best base-stock levels found.
	best_cost : float
		Best cost found.

	"""

	# Build dictionary indicating which optimization group each node is assigned to.
	# (Group indices will not be consecutive; some will be empty.)
	# Note that every set contains a node with the same index as the set.
	opt_group, _ = _base_stock_group_assignments(network.node_indices, groups=groups)

	# Determine list of nodes to optimize, based on groups. Nodes that are not
	# in the list will have their base-stock level set to the level from their group.
	nodes_to_optimize = {opt_group[n_ind] for n_ind in network.node_indices}

	# Build lists needed for truncation and discretization, based on nodes_to_optimize.
	dict_base_stock_levels = ensure_dict_for_nodes(base_stock_levels, network.node_indices)
	dict_truncation_lo = ensure_dict_for_nodes(truncation_lo, network.node_indices)
	dict_truncation_hi = ensure_dict_for_nodes(truncation_hi, network.node_indices)
	dict_discretization_step = ensure_dict_for_nodes(discretization_step, network.node_indices)
	dict_discretization_num = ensure_dict_for_nodes(discretization_num, network.node_indices)
	nto_base_stock_levels = {n_ind: dict_base_stock_levels[n_ind] for n_ind in nodes_to_optimize}
	nto_truncation_lo = {n_ind: dict_truncation_lo[n_ind] for n_ind in nodes_to_optimize}
	nto_truncation_hi = {n_ind: dict_truncation_hi[n_ind] for n_ind in nodes_to_optimize}
	nto_discretization_step = {n_ind: dict_discretization_step[n_ind] for n_ind in nodes_to_optimize}
	nto_discretization_num = {n_ind: dict_discretization_num[n_ind] for n_ind in nodes_to_optimize}

	# Determine base-stock levels to test by truncating and discretizing
	# according to preferences specified.
	# (If base_stock_levels is not None, these will simply be returned.)
	S_dict = truncate_and_discretize(nodes_to_optimize, nto_base_stock_levels, nto_truncation_lo,
								nto_truncation_hi, nto_discretization_step, nto_discretization_num)

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

	# Loop through enumerated solutions. (Each one only contains nodes in nodes_to_optimize.)
	for S in enumerated_solutions:

		# Update progress bar.
		pbar.update()

		# Determine complete dict of base-stock levels (not just for nodes_to_optimize).
		S_complete = {n_ind: S[opt_group[n_ind]] for n_ind in network.node_indices}
		# for n_ind in network.node_indices:
		# 	if n_ind in nodes_to_optimize:
		# 		S_complete[n_ind] = S[n_ind]
		# 	else:
		# 		S_complete[n_ind] = S[opt_group[n_ind]]

		# Was an objective function provided?
		if objective_function is not None:
			mean_cost = objective_function(S_complete)
		else:
			# Set base-stock levels for all nodes.
			for n in network.nodes:
				if n.inventory_policy.type == 'BS':
					n.inventory_policy.base_stock_level = S_complete[n.index]
				else:
					n.inventory_policy.local_base_stock_level = S_complete[n.index]
			# Run multiple trials of simulation to evaluate solution.
			mean_cost, _ = run_multiple_trials(network, sim_num_trials, sim_num_periods,
											   sim_rand_seed, progress_bar=False)

		# Compare to best solution found so far.
		if mean_cost < best_cost:
			best_cost = mean_cost
			best_S = S_complete

		# Print solution, if requested.
		if print_solutions:
			print_str = "S = {} cost = {}".format(S_complete, mean_cost)
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
	Can be called as a standalone function, but usually used as a subroutine for
	:func:`stockpyl.meio_general.meio_by_coordinate_descent`.
	
	Parameters
	----------
	network : |class_network|
		The supply chain network.
	node_to_optimize : |class_node|
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
		Number of periods per trial in each simulation. Ignored if ``objective_function``
		is provided.
	sim_rand_seed : int, optional
		Rand seed to use for simulation. Ignored if ``objective_function`` is provided.
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
							   groups=None, objective_function=None,
							   sim_num_trials=10, sim_num_periods=1000, sim_rand_seed=None,
							   tol=1e-2, line_search_tol=1e-4, verbose=False):
	"""Optimize the MEIO instance by coordinate descent on the
	base-stock levels. Evaluate each solution using the provided objective
	function, or simulation if not provided.

	Parameters
	----------
	network : |class_network|
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
	groups : list of sets, optional
		A list of sets, each of which contains indices of nodes that should have the
		same base-stock level. This speeds the optimization since the base-stock
		levels for the nodes in a given group do not have to be optimized individually.
		Any nodes not contained in any set in the list are optimized individually.
		If omitted, all nodes are optimized individually.
	objective_function : function, optional
		The function to use to evaluate a given solution. If omitted, simulation
		will be used.
	sim_num_trials : int, optional
		Number of trials to run in each simulation. Ignored if ``objective_function``
		is provided.
	sim_num_periods : int, optional
		Number of periods per trial in each simulation. Ignored if ``objective_function``
		is provided.
	sim_rand_seed : int, optional
		Rand seed to use for simulation. Ignored if ``objective_function`` is provided.
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

	# Build dictionary indicating which optimization group each node is assigned to.
	# (Group indices will not be consecutive; some will be empty.)
	# Note that every set contains a node with the same index as the set.
	opt_group, group_list = _base_stock_group_assignments(network.node_indices, groups=groups)

	# Determine list of nodes to optimize, based on groups. Nodes that are not
	# in the list will have their base-stock level set to the level from their group.
	nodes_to_optimize = {opt_group[n_ind] for n_ind in network.node_indices}

	# Determine bounds for search, if not provided, based on nodes_to_optimize.
	dict_lo = ensure_dict_for_nodes(search_lo, network.node_indices)
	dict_hi = ensure_dict_for_nodes(search_hi, network.node_indices)
	nto_lo = {n_ind: dict_lo[n_ind] for n_ind in nodes_to_optimize}
	nto_hi = {n_ind: dict_hi[n_ind] for n_ind in nodes_to_optimize}
	for n_ind in nodes_to_optimize:
		if nto_lo[n_ind] is None:
			nto_lo[n_ind] = 0
		if nto_hi[n_ind] is None:
			n = network.get_node_from_index(n_ind)
			nto_hi[n_ind] = 3 * n.lead_time * np.sum([s.demand_source.mean for s in network.sink_nodes])

	# Determine initial solution.
	if initial_solution is None:
		nto_initial_solution = {}
		for n in nodes_to_optimize:
			nto_initial_solution[n] = np.sum([s.demand_source.mean for s in network.sink_nodes])
	else:
		nto_initial_solution = {n_ind: initial_solution[n_ind] for n_ind in nodes_to_optimize}

	# Shortcut to objective function.
	def obj_fcn(S):
		if objective_function is not None:
			return objective_function(S)
		else:
			# Set base-stock levels for all nodes.
			for n in network.nodes:
				if n.inventory_policy.type == 'BS':
					n.inventory_policy.base_stock_level = S[n.index]
				else:
					n.inventory_policy.local_base_stock_level = S[n.index]
			# Run multiple trials of simulation to evaluate solution.
			cost, _ = run_multiple_trials(network, sim_num_trials, sim_num_periods, sim_rand_seed,
												  progress_bar=False)
			return cost

	# Initialize current solution and cost.
	current_soln_complete = {n_ind: nto_initial_solution[opt_group[n_ind]] for n_ind in network.node_indices}
	current_cost = obj_fcn(current_soln_complete)

	# Print message, if requested.
	if verbose:
		print("Initial solution = {} initial cost = {}".format(current_soln_complete, current_cost))

	# Initialize done flag.
	done = False
	t = 0

	# Loop until cost does not improve by more than tol.
	while not done:

		# Loop through all groups, optimizing base-stock level for each in turn.
		for g in group_list:

			# Optimize base-stock level for group using golden-section search.
			def f(Sn):
				S = current_soln_complete.copy()
				for n_ind in g:
					S[n_ind] = Sn
				return obj_fcn(S)
#			f = lambda Sn: obj_fcn({i.index: Sn if i.index == n.index else current_soln[i.index] for i in network.nodes})
			best_Sn, best_cost = optimization.golden_section_search(f, nto_lo[min(g)], nto_hi[min(g)], tol=line_search_tol, verbose=False)

			# Replace group base-stock levels in current_solution with new values.
			for n_ind in g:
				current_soln_complete[n_ind] = best_Sn

			# Print message, if requested.
			if verbose:
				print("Iteration {} nodes {} best_S[n] = {} best_cost = {} current_soln = {}".format(t, g, best_Sn, best_cost, current_soln_complete))

		# Check improvement since last iteration.
		if best_cost >= current_cost - tol:
			# Terminate.
			done = True
		else:
			current_cost = best_cost
			t += 1

	return current_soln_complete, best_cost


# -------------------

# HELPER FUNCTIONS

def truncate_and_discretize(node_indices, values=None, truncation_lo=None,
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

		- ``truncation_lo`` is set to 0.
		- ``truncation_hi`` is set to 100.
		- ``discretization_step`` is set to 1 and ``discretization_num`` is set to
		  (``truncation_hi`` - ``truncation_lo``) / ``discretization_step``.
		
	Parameters
	----------
	node_indices : list
		List of indices of all nodes in the network.
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
	if values is None:
		values_provided = False
	else:
		values_provided = False
		for v in values.values():
			if v is not None:
				values_provided = True

	if values_provided:
		truncated_discretized_values = values
	else:
		# Determine lo, hi, step, and num.
		lo_dict = ensure_dict_for_nodes(truncation_lo, node_indices)
		hi_dict = ensure_dict_for_nodes(truncation_hi, node_indices)
		step_dict = ensure_dict_for_nodes(discretization_step, node_indices)
		num_dict = ensure_dict_for_nodes(discretization_num, node_indices)

		# Initialize output dict.
		truncated_discretized_values = {}

		# Loop through nodes.
		for n_ind in node_indices:

			# Determine lo, hi, step/num for each node. If not provided,
			# use default settings.
			lo = lo_dict[n_ind] or DEFAULT_LO
			hi = hi_dict[n_ind] or DEFAULT_HI
			if step_dict[n_ind] is not None:
				step = step_dict[n_ind]
			elif num_dict[n_ind] is not None:
				num = num_dict[n_ind]
				step = (hi - lo) / (num - 1)
			else:
				step = DEFAULT_STEP

			truncated_discretized_values[n_ind] = np.arange(lo, hi+1, step).tolist()

	return truncated_discretized_values


def _base_stock_group_assignments(node_indices, groups=None):
	"""Build dict indicating, for each node index, the group that the node is
	assigned to for the purposes of base-stock-level optimization.

	Grouping nodes that should have the same base-stock level speeds the optimization
	since the base-stock levels for the nodes in a given group do not have to be
	optimized individually.

	Group indices will not be consecutive; some group indices will have no members.

	Parameters
	----------
	node_indices : list
		List of indices of all nodes in the network.
	groups : list of sets, optional
		A list of sets, each of which contains indices of nodes that should have the
		same base-stock level. Any nodes not contained in any set in the list are
		optimized individually. If omitted, all nodes are optimized individually.

	Returns
	-------
	opt_group : dict
		A dict in which each key is the index of a node in ``network`` and each
		value is the index of the optimization group the node is assigned to.
	group_list : list
		A list in which each item is a list of node indices corresponding to one
		group. This is the same as the ``groups`` list provided, but with
		singletons filled in.
	"""

	# Initialize dict.
	opt_group = {}

	# Were any groups provided?
	if groups is None:
		opt_group = {n_ind: n_ind for n_ind in node_indices}
	else:
		# For each node, look for it in a group.
		for n_ind in node_indices:
			for node_set in groups:
				if n_ind in node_set:
					# Assign group in dict.
					opt_group[n_ind] = min(node_set)

			# Check whether we already assigned node; if not, assign it to its own
			# group.
			if n_ind not in opt_group:
				opt_group[n_ind] = n_ind

	# Build group_list.
	group_list = []
	for i in node_indices:
		g = [n_ind for n_ind in node_indices if opt_group[n_ind] == i]
		if g:
			group_list.append(g)

	return opt_group, group_list


