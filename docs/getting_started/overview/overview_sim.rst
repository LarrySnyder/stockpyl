.. include:: ../../globals.inc

.. _overview_sim_page:

Simulation
==========

|sp| contains code to simulate single- or multi-echelon inventory systems. The system being simulated
can include many different features, including:

	* Stochastic demand with a variety of built-in demand distributions, or supply your own
	* Inventory management using a variety of built-in inventory policies, or supply your own
	* Stochastic supply disruptions with various implications
	* Fixed and/or variable costs, or supply your own cost functions
	* Period-by-period, node-by-node state variables output to table or CSV file


.. note:: |node_stage|

|fosct_notation|

.. contents::
    :depth: 2

Data Structures
--------------------------------

The simulation code in |sp| makes use of the |class_network| and |class_node| classes, which contain all of 
the data for the system to be simulated. For more information,
see the "Overview" page for :ref:`multi-echelon inventory optimization (MEIO) <overview_meio_page>`, or the
API pages for |class_network| or |class_node|.

Sequence of Events (SoE)
------------------------

Simulations in |sp| assume periodic review. Each node :math:`i` has both a *shipment lead time* (denoted :math:`L^s_i`) and an
*order lead time* (denoted :math:`L^o_i`). When node :math:`i` places an order, its predecessors and/or external suppliers
receive the order :math:`L^o_i` periods later. And when a node or an external supplier sends a shipment to node :math:`i`, 
node :math:`i` receives it :math:`L^s_i` periods later. Shipment lead times are more commonly discussed in the literature, but order lead times
arise in, for example, papers on the bullwhip effect [REF].

In each period :math:`t`, events occur in the following sequence *at each node*:

	1. Inbound orders (i.e., demands) placed :math:`t-L^o` periods earlier are received from successor nodes and/or external customers. 
	2. Outbound orders are placed to predecessor nodes and/or external suppliers.
	3. Inbound shipments sent :math:`t-L^s` periods ago are received from predecessor nodes and/or external suppliers.
	4. Outbound shipments are sent to predecessor nodes and/or external suppliers.
	5. State variables are updated and costs are incurred.

**Example:** Simulate a single-node system with Poisson(10) demand, a base-stock policy with a base-stock level of 13, 
an order lead time of 0, and a shipment lead time of 1.

.. doctest::

	>>> from stockpyl.supply_chain_network import single_stage_system
	>>> from stockpyl.sim import simulation
	>>> from stockpyl.sim_io import write_results
	>>> network = single_stage_system(
	...     demand_type='P',                # Poisson demand
	...     mean=10,
	...     policy_type='BS',               # base-stock policy
	...     base_stock_level=13,
	...     order_lead_time=0,
	...     shipment_lead_time=1
	... )
	>>> total_cost = simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
	>>> write_results(network=network, num_periods=4, columns_to_print='minimal', print_cost_summary=False)
	  t  i=0      IO:EXT    OQ:EXT    IS:EXT    OS:EXT    IL
	---  -----  --------  --------  --------  --------  ----
	  0               12        12         0        12     1
	  1                6         6        12         6     7
	  2               11        11         6        11     2
	  3               14        14        11        13    -1

Interpreting the results:

	* In period 0, the node has an inbound order (``IO:EXT`` column), i.e., demand, of 12; it places an order
	  of size 12 (``OQ:EXT``), receives no inbound shipment (``IS:EXT``), and sends an outbound shipment of 12 (``IS:EXT``). It ends the period
	  with an inventory level of 1 (``IL``). (At the beginning of period 0, the inventory level was equal to the base-stock level, 13.) 
	* In period 1, the node has a demand of 6; it places an order of size 6; it receives the shipment of size 12 ordered in period 0;
	  it ships 6 units and ends with an inventory level of 7.
	* A backorder occurs in period 3, because the node begins the period with an inventory level of 2, and receives a demand of 14, but
	  only receives a shipment of 11.

(In the column headers, ``EXT`` refers to the external supplier and customer.)


.. note:: This sequence of events (SoE) is somewhat atypical. It is more common to assume that orders are placed *before* demands
	are observed (i.e., SoE steps 1 and 2 are swapped). See, for example, |fosct| §4.3 or Zipkin (2000) §9.3.1. However,
	the two sequences can be made equivalent by adjusting the lead times: 
	
	A system with order lead time :math:`L^o_i` under the
	"swapped" SoE is equivalent to a system with order lead time :math:`L^o_i+1` under the |sp| SoE.

	The SoE used in |sp| is more flexible, since it allows for the possibility that a node places its outbound order after it already
	knows its demand. Under the "swapped" SoE, this would only be possible by setting :math:`L^o_i = -1`, which does not make sense.

[EXAMPLE]

In simulations of multi-echelon systems, the sequence of events *among nodes* is also important:

	* Sequence of events steps 1 and 2 first occur, one node at a time, from downstream to upstream: 

		- Sink nodes (nodes with no successor nodes) receive
	  	  their inbound orders (SoE step 1), then they place outbound orders to their predecessors and/or external supplier (SoE step 2). 
	  	- Then those predecessors receive inbound orders and place outbound orders, and so on, moving upstream in the system until
	  	  all nodes have completed SoE steps 1 and 2.

	* Then, SoE steps 3 and 4 occur, one node at a time, from upstream to downstream: 
	
		- Source nodes (nodes with no predecessor nodes)
	  	  receive their inbound shipments (SoE step 3), then they send outbound shipments to their successors and/or external
	  	  customer (SoE step 4). 
		- Then those successors receive inbound shipments and send outbound shipments, and so on, moving
	  	  downstream in the system until all nodes have completed SoE steps 3 and 4.

	* Then, SoE step 5 is completed for all nodes.




External Suppliers
------------------

Advanced Features
-----------------

Disruptions
~~~~~~~~~~~

asdfasdf

Holding and Stockout Cost Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

asdfasdf

Running Multiple Trials
~~~~~~~~~~~~~~~~~~~~~~~





References
----------

P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


