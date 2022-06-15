.. include:: ../../globals.inc

.. _overview_meio_page:

Multi-Echelon Inventory Optimization
====================================

|sp| contains code to solve the following types of multi-echelon inventory optimization (MEIO) problems:

* Serial systems under the stochastic-service model (SSM) (|mod_ssm_serial| module)
* Serial or tree systems under the guaranteed-service model (GSM) (|mod_gsm_serial| and |mod_gsm_tree| modules)
* Systems with arbitrary topology<overview_meio:General MEIO Systems, optimized using enumeration or coordinate descent (|mod_meio_general| module)

.. note:: |node_stage|

|fosct_notation|

.. contents::
    :depth: 2



The |class_network| Class
--------------------------------

All of the MEIO code in |sp| makes use of the |class_network| class, which contains all of the data for 
an MEIO instance. For some functions, you provide data in the form of lists, dicts, or singletons and the
function builds the |class_network| object for you, while other functions require you to pass an |class_network| 
object directly.

A |class_network|, in turn, consists of one or more |class_node| objects. When you create a |class_node|,
you provide an index and any parameters you wish. (The list of available parameters is in the documentation
for the |class_node| class.) For example:

.. doctest::

	>>> from stockpyl.supply_chain_node import SupplyChainNode
	>>> my_node = SupplyChainNode(index=1, local_holding_cost=3, stockout_cost=20, shipment_lead_time=2)
	>>> my_other_node = SupplyChainNode(index=2, name="other_node", echelon_holding_cost=1.5)

You can then add these nodes to a |class_network|:

.. doctest::

	>>> from stockpyl.supply_chain_network import SupplyChainNetwork
	>>> network = SupplyChainNetwork()
	>>> network.add_node(my_node)
	>>> network.add_successor(my_node, my_other_node)

The network now contains both nodes, and a (directed) edge from ``my_node`` to ``my_other_node``. Nodes can
be accessed either from a |class_network| object's :attr:`~stockpyl.supply_chain_network.SupplyChainNetwork.nodes` 
attribute (a list of nodes), or using its member function :meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.get_node_from_index`:
 
.. doctest::

	>>> n1 = network.nodes[0]
	>>> n1.index
	1
	>>> n1.local_holding_cost
	3
	>>> n2 = network.get_node_from_index(2)
	>>> n2.index
	2
	>>> n2.echelon_holding_cost
	1.5

The |mod_supply_chain_network| module contains functions for quickly building certain types
of multi-echelon networks; for example:

.. doctest::

	>>> from stockpyl.supply_chain_network import serial_system
	>>> serial_3 = serial_system(
	...     num_nodes=3,
	...     local_holding_cost=[2, 4, 8],
	...     stockout_cost=[0, 0, 40],
	...     shipment_lead_time=[2, 1, 1],
	...     demand_type='N', # normally distributed demand
	...     mean=5,
	...     standard_deviation=1,
	...     policy_type='BS', # base-stock policy
	...     base_stock_level=[12, 8, 6]
	... )
	>>> serial_3.nodes[1].local_holding_cost
	4

There are several other ways to build |class_network| objects; see the documentation for the
object for more information.

Serial SSM Systems
------------------

The |mod_ssm_serial| module contains code to solve serial systems under the stochastic service
model (SSM), either exactly, using the :func:`~stockpyl.ssm_serial.optimize_base_stock_levels` function
(which implements the algorithm by Chen and Zheng (1994), which in turn is
based on the algorithm by Clark and Scarf (1960)), or approximately, using the :func:`~stockpyl.ssm_serial.newsvendor_heuristic`
function (which implements the newsvendor heuristic by Shang and Song (1996)).

For either function, you may pass the instance data as individual parameters (costs, demand distribution, etc.) 
or a |class_network|. Here is Example 6.1 from |fosct| with the data passed as individual parameters:

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> from stockpyl.ssm_serial import optimize_base_stock_levels
		>>> S_star, C_star = optimize_base_stock_levels(
		... 	num_nodes=3, 
		... 	echelon_holding_cost=[3, 2, 2], 
		... 	lead_time=[1, 1, 2], 
		... 	stockout_cost=37.12, 
		... 	demand_mean=5, 
		... 	demand_standard_deviation=1
		...	)
		>>> S_star
		{1: 6.5144388073261155, 2: 12.012332294949644, 3: 22.700237234889784}
		>>> C_star
		47.668653127136345

Here is the same example, first building a |class_network| and then passing that instead:

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> from stockpyl.ssm_serial import optimize_base_stock_levels
		>>> from stockpyl.supply_chain_network import serial_system
		>>> example_6_1_network = serial_system(
		...     num_nodes=3,
		...     node_order_in_system=[3, 2, 1],
		...     echelon_holding_cost={1: 3, 2: 2, 3: 2},
		...     shipment_lead_time={1: 1, 2: 1, 3: 2},
		...     stockout_cost={1: 37.12, 2: 0, 3: 0},
		...     demand_type='N',
		...     mean=5,
		...     standard_deviation=1,
		...     policy_type='BS',
		...     base_stock_level=0,
		... )
		>>> S_star, C_star = optimize_base_stock_levels(network=example_6_1_network)
		>>> S_star
		{1: 6.5144388073261155, 2: 12.012332294949644, 3: 22.700237234889784}
		>>> C_star
		47.668653127136345

Example 6.1 is also a built-in instance in |sp|, so you can load it directly:

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> from stockpyl.ssm_serial import optimize_base_stock_levels
		>>> from stockpyl.instances import load_instance
		>>> S_star, C_star = optimize_base_stock_levels(network=load_instance("example_6_1"))
		>>> S_star
		{1: 6.5144388073261155, 2: 12.012332294949644, 3: 22.700237234889784}
		>>> C_star
		47.668653127136345

To solve the instance using the newsvendor heuristic:

	.. doctest::
		:skipif: True	# set to False to run the test

		>>> from stockpyl.ssm_serial import newsvendor_heuristic
		>>> S_heur = newsvendor_heuristic(network=example_6_1_network)
		>>> S_heur
		{1: 6.490880975286938, 2: 12.027434723327854, 3: 22.634032391786285}
		>>> # Evaluate the (exact) expected cost of the heuristic solution.
		>>> from stockpyl.ssm_serial import expected_cost
		>>> expected_cost(S_heur, network=example_6_1_network)
		47.680099140842174


Serial or Tree GSM Systems
--------------------------

|sp| contains functions to optimize committed service times (CSTs) in either serial or
general tree systems under the guaranteed-service model (GSM). 

For serial GSM systems, the |mod_gsm_serial| module implements the dynamic programming (DP)
algorithm of Inderfurth (1991). Here is Example 6.3 from |fosct|, passing the data as individual
parameters:

	.. doctest::

		>>> from stockpyl.gsm_serial import optimize_committed_service_times
		>>> opt_cst, opt_cost = optimize_committed_service_times(
		...		num_nodes=3,
		...		local_holding_cost=[7, 4, 2],
		...		processing_time=[1, 0, 1],
		...		demand_bound_constant=1,
		...		external_outbound_cst=1,
		...		external_inbound_cst=1,
		...		demand_mean=0,
		...		demand_standard_deviation=1
		...	)
		>>> opt_cst
		{3: 0, 2: 0, 1: 1}
		>>> opt_cost
		2.8284271247461903

Or passing a |class_network|:

	.. doctest::

		>>> from stockpyl.gsm_serial import optimize_committed_service_times
		>>> from stockpyl.supply_chain_network import network_from_edges
		>>> example_6_3_network = network_from_edges(
		...     edges=[(3, 2), (2, 1)],
		...     node_order_in_lists=[1, 2, 3],
		...     processing_time=[1, 0, 1],
		...     external_inbound_cst=[None, None, 1],
		...     local_holding_cost=[7, 4, 2],
		...     demand_bound_constant=1,
		...     external_outbound_cst=[1, None, None],
		...     demand_type=['N', None, None],
		...     mean=0,
		...     standard_deviation=[1, 0, 0]
		... )
		>>> optimize_committed_service_times(network=example_6_3_network)
		({3: 0, 2: 0, 1: 1}, 2.8284271247461903)

Or loading the instance directly:

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> optimize_committed_service_times(network=load_instance("example_6_3"))
		({3: 0, 2: 0, 1: 1}, 2.8284271247461903)

The |mod_gsm_tree| module implements Graves and Willems's (2000) dynamic programming (DP)
algorithm for multi-echelon inventory systems with tree structures. The 
:func:`~stockpyl.gsm_tree.optimize_committed_service_times` function requires
a |class_network| containing all of the instance data to be passed as an argument. 
The code snippet below solves Example 6.5 in |fosct|.

	.. doctest::

		>>> from stockpyl.gsm_tree import optimize_committed_service_times
		>>> from stockpyl.supply_chain_network import network_from_edges
		>>> example_6_5_network = network_from_edges(
		... 	edges=[(1, 3), (3, 2), (3, 4)],
		... 	node_order_in_lists=[1, 2, 3, 4],
		... 	processing_time=[2, 1, 1, 1],
		... 	external_inbound_cst=[1, None, None, None],
		... 	local_holding_cost=[1, 3, 2, 3],
		... 	demand_bound_constant=[1, 1, 1, 1],
		... 	external_outbound_cst=[None, 0, None, 1],
		... 	demand_type=[None, 'N', None, 'N'],
		... 	mean=0,
		... 	standard_deviation=[None, 1, None, 1]
		... )
		>>> opt_cst, opt_cost = optimize_committed_service_times(tree=example_6_5_network)
		>>> opt_cst
		{1: 0, 3: 0, 2: 0, 4: 1}
		>>> opt_cost
		8.277916867529369

Example 6.5 is a built-in instance in |sp|, so it can be loaded directly instead:

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> optimize_committed_service_times(tree=load_instance("example_6_5"))
		({1: 0, 3: 0, 2: 0, 4: 1}, 8.277916867529369)


General MEIO Systems
--------------------

For MEIO systems with arbitrary topology (not necessarily serial or tree systems),
the |mod_meio_general| module can optimize base-stock levels approximately using
relatively brute-force approaches—either coordinate descent or enumeration. These
heuristics tend to be quite slow and not particularly accurate, but they are sometimes
the best methods available for complex systems that are not well solved in the literature.

For both approaches, you may provide an objective function that will be used to evaluate
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