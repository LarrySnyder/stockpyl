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

.. image:: https://raw.githubusercontent.com/LarrySnyder/stockpyl-testing/ac4f0ca30993c53f5e53743a77f4f2d7ae55d05e/intro_to_products_diagram.png
   :scale: 100 %
   :alt: 3-node network diagram
   :align: center

In the diagram:

	* The squares represent nodes. The number in the top-left corner of a node is its index.
	* The circles represent products. The number in a product is its index.
	* The lines from products 20 and 30 to product 10 indicate that products 20 and 30 are
	  raw materials that are used to make product 10. To make 1 unit of product 10 requires
	  5 units of product 20 and 2 units of product 30, as indicated by `x5` and `x3` on the lines.
	* The arrow from node 2 to node 1 indicates that node 2 ships items to node 1. The lead
	  time for these shipments is 1 period, as indicated by `L=1` on the arrow.
	* The arrow from node 1 represents the external demand, which follows a uniform discrete
	  distribution on [1,5].
	* The arrow into node 2 represents the external supplier. The lead time for shipments
	  from the external supplier is 2 periods, as indicated by `L=2` on the arrow.

We'll start building this network using the :func:`~stockpyl.supply_chain_network.serial_system` function:

.. doctest::

	>>> from stockpyl.supply_chain_network import serial_system
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
	>>> # Build a dict for easier access to the nodes.
	>>> nodes = {n.index: n for n in network.nodes}

Next, we'll create the three products and add them to a dict whose keys are product indices
and whose values are products, for easy access to the product objects. We'll also set the BOM.

.. doctest::

	>>> from stockpyl.supply_chain_product import SupplyChainProduct
	>>> products = {10: SupplyChainProduct(index=10), 20: SupplyChainProduct(index=20), 30: SupplyChainProduct(index=30)}
	>>> products[10].set_bill_of_materials(raw_material=20, num_needed=5)
	>>> products[10].set_bill_of_materials(raw_material=30, num_needed=3)

To add the products to the nodes, we use :py:meth:`~stockpyl.supply_chain_network.SupplyChainProduct.add_product` and 
:py:meth:`~stockpyl.supply_chain_network.SupplyChainProduct.add_products`:

.. doctest::

	>>> nodes[1].add_product(products[10])
	>>> nodes[2].add_products([products[20], products[30]])


Specifying Attributes
---------------------------

Most attributes that apply to nodes also apply to products. For example, 