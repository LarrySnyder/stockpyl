.. include:: globals.inc

Multi-Echelon Inventory Optimization
====================================

|sp| contains code to solve the following types of multi-echelon inventory optimization (MEIO) problems:

* :ref:`Serial systems under the stochastic-service model (SSM)<overview_meio:Serial SSM Systems>` (|mod_ssm_serial| module)
* Serial or tree systems under the guaranteed-service model (GSM) (|mod_gsm_serial| and |mod_gsm_tree| modules)
* Systems with arbitrary topology, optimized using enumeration or coordinate descent

The terms "node" and "stage" are used interchangeably in the documentation.

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory* (|fosct|), 2nd edition
(2019).

|copy| Lawrence V. Snyder, Lehigh University

The |class_network| Class
-------------------------

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
	...     local_holding_cost=[8, 4, 2],
	...     stockout_cost=[40, 0, 0],
	...     shipment_lead_time=[1, 1, 2],
	...     demand_type='N', # normally distributed demand
	...     demand_mean=5,
	...     demand_standard_deviation=1,
	...     inventory_policy_type='BS', # base-stock policy
	...     base_stock_levels=[6, 8, 12],
	...     downstream_0=True
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
		...     node_indices=[1, 2, 3],
		...     echelon_holding_cost={1: 3, 2: 2, 3: 2},
		...     shipment_lead_time={1: 1, 2: 1, 3: 2},
		...     stockout_cost={1: 37.12, 2: 0, 3: 0},
		...     demand_type='N',
		...     demand_mean=5,
		...     demand_standard_deviation=1,
		...     inventory_policy_type='BS',
		...     base_stock_levels=0,
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
		>>> example_6_1_network = load_instance("example_6_1")
		>>> S_star, C_star = optimize_base_stock_levels(network=example_6_1_network)
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
