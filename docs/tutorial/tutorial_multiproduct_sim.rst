.. include:: ../globals.inc

.. _tutorial_multiproduct_sim_page:

Multi-Product Simulation
========================

|sp| supports simulating systems with multiple products. This page describes how to create and manage
products, as well as simulate multi-product systems. If you haven't already read the
the :ref:`tutorial page for simulation<tutorial_sim_page>`, read that first.


.. note:: |node_stage|

.. note:: |fosct_notation|

.. admonition:: See Also

	For more details, see the API documentation for the |mod_sim|, |mod_sim_io|, and |mod_supply_chain_product| modules.

.. contents::
    :depth: 3


Products
--------

The primary class for handling products is the |class_product|. A |class_product| object
is typically added to one or more |class_node| objects; those nodes are then said to
"handle" the product. Most attributes (``echelon_holding_cost``, ``lead_time``, ``stockout_cost``,
``demand_source``, ``inventory_policy``, etc.) may be specified either at the node level
(same value for all products at the node), at the product level (same value for all nodes that handle
the product), or at the node-product level (separate value for the node-product pair). 

Products are related to each other via a **bill of materials (BOM).** The BOM specifies
the number of units of an upstream product (*raw material*) that are required to make 
one unit of a downstream product (*finished goods*). For example, the BOM might specify that
5 units of product A and 2 units of product B are required to make 1 unit of product C at a downstream node.
The raw materials are products A and B, and the finished good is product C. 

.. note:: "Raw materials" and "finished goods" are |class_product| objects. They are not separate
	classes. Moreover, a finished good at one node may be a raw material at another node; for example,
	node 1 might produce product A as its finished good, which it then ships to node 2, where it is
	used as a raw material to product product B.

Every node has at least one product. If your code does not explicltly create products or
add them to nodes, |sp| automatically creates and manages "dummy" products at each node.
This means that you can ignore products entirely if you do not need them, and any code written
for versions of |sp| prior to v1.0 (when products were introduced) should still work without
being adapted to handle products. # TODO: is this true? are there caveats?


Basic Multi-Product Example
---------------------------

This tutorial will use the following network:

![3-node diagram](https://github.com/LarrySnyder/stockpyl-testing/blob/main/intro_to_products_diagram.png)

We'll start building this network using the :func:`~stockpyl.supply_chain_network.serial_system` function:

.. testsetup:: *

	from stockpyl.supply_chain_network import serial_system

.. doctest::

	>>> network = serial_system(
	...		num_nodes=2,
	...		node_order_in_system=[2, 1],
	...		node_order_in_lists=[1, 2],
	...		local_holding_cost=[5, None],	# holding cost at node 2 will be product-specific, so leave it unspecified here
	...		stockout_cost=[20, 0],
	...		demand_type='UD',				# discrete uniform distribution, for easier debugging
	...		lo=1,
	...		hi=5,
	...		shipment_lead_time=[1, 2]
	...	)

Next, we'll create three products, w