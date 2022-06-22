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

Basic Example
-------------

Simulate a single-node system with Poisson(10) demand, a base-stock policy with a base-stock level of 13, 
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
	...     shipment_lead_time=1
	... )
	>>> simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
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


Data Structures
--------------------------------

The simulation code in |sp| makes use of the |class_network| and |class_node| classes, which contain all of 
the data for the system to be simulated. For more information,
see the "Overview" page for :ref:`multi-echelon inventory optimization (MEIO) <overview_meio_page>`, or the
API pages for |class_network| or |class_node|.


Sequence of Events
------------------------

Simulations in |sp| assume periodic review. In each period :math:`t`, events occur in the following sequence *at each node* :math:`i`:

	1. Inbound orders (i.e., demands) placed :math:`t-L^o_i` periods earlier are received from successor nodes and/or external customers, where :math:`L^o_i`
	   the order lead time for node :math:`i`. 
	2. Outbound orders are placed to predecessor nodes and/or external suppliers.
	3. Inbound shipments sent :math:`t-L^s_i` periods ago are received from predecessor nodes and/or external suppliers, where
	   :math:`L^s_i` is the shipment lead time for node :math:`i`.
	4. Outbound shipments are sent to predecessor nodes and/or external suppliers.
	5. State variables are updated and costs are incurred.

.. note:: This sequence of events (SoE) is somewhat atypical. It is more common to assume that orders are placed *before* demands
	are observed (i.e., SoE steps 1 and 2 are swapped). See, for example, |fosct| §4.3 or Zipkin (2000) §9.3.1. However,
	the two sequences can be made equivalent by adjusting the lead times; see the note in the Lead Times section [HYPERLINK].

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


Lead Times
----------

Each node :math:`i` has both a *shipment lead time* (denoted :math:`L^s_i`) and an
*order lead time* (denoted :math:`L^o_i`). When node :math:`i` places an order, its predecessors and/or external suppliers
receive the order :math:`L^o_i` periods later. And when a node or an external supplier sends a shipment to node :math:`i`, 
node :math:`i` receives it :math:`L^s_i` periods later. Shipment lead times are more commonly discussed in the literature, but order lead times
arise in, for example, papers on the bullwhip effect [REF]. 

The two types of lead times are equivalent if the supplier never runs
out of inventory (e.g., if it is an external supplier, or a predecessor node with a very large base-stock level), since
in that case orders are always shipped as soon as they are received, so the total time between the node placing and receiving 
an order is always :math:`L^o_i + L^s_i`.


.. note:: A system with order lead time :math:`L^o_i` under the
	"order-first" SoE (in which steps 1 and 2 are the reverse of those listed above)
	is equivalent to a system with order lead time :math:`L^o_i+1` under the |sp| SoE.

	The SoE used in |sp| is more flexible, since it allows for the possibility that a node places its outbound order after it already
	knows its demand. Under the "order-first" SoE, this would only be possible by setting :math:`L^o_i = -1`, which does not make sense.

**Example:** Example 4.1 in |fosct| assumes a lead time of 0, but it also assumes the "order-first" sequence of events.
Therefore, to simulate this system in |sp|, we must set the order lead time (or, equivalentlly, the shipment lead time, since
the node's supplier never runs out of inventory):


.. testsetup:: *

	from stockpyl.supply_chain_network import single_stage_system
	from stockpyl.sim import simulation

.. doctest::

	>>> network = single_stage_system(
	...		holding_cost=0.18,
	...		stockout_cost=0.70,
	...		demand_type='N',
	...		mean=50,
	...		standard_deviation=8,
	...		policy_type='BS',
	...		base_stock_level=57,
	...		order_lead_time=1	# to account for difference in SoE
	... )
	>>> T = 1000
	>>> total_cost = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
	>>> print(f"Total cost per period = {total_cost / T}")
	1.9906261152138731

The total cost per period is very close to the value predicted by the theory (2.0000) in Example 4.1. 

**Example:** In Example 4.4 in |fosct|, the lead time is 4. To account for the difference in SoE, we set
the order lead time to 1 and the shipment lead time to 4. (Setting the shipment or order lead time to 5
and the other to 0 would have the same effect.)

.. testsetup:: *

	from stockpyl.supply_chain_network import single_stage_system
	from stockpyl.sim import simulation

.. doctest::

	>>> network = single_stage_system(
	...		holding_cost=0.18,
	...		stockout_cost=0.70,
	...		demand_type='N',
	...		mean=50,
	...		standard_deviation=8,
	...		policy_type='BS',
	...		base_stock_level=57,
	...		shipment_lead_time=4,
	...		order_lead_time=1	# to account for difference in SoE
	... )
	>>> T = 1000
	>>> total_cost = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
	>>> print(f"Total cost per period = {total_cost / T}")
	4.475292852532866

Again this matches the cost of 4.47 predicted by the theory.

Supply and Demand
-----------------

External Customers
~~~~~~~~~~~~~~~~~~~~
Any node can have an **external customer**—a customer that is not a node that is modeled explicitly
in the system. External customers are the only source of exogenous demand in the system. If there are
no external customers, there is no demand. A node can have both an external customer and one or
more successor nodes.

To specify that a node has an external customer, set its ``demand_source`` attribute
to a |class_demand_source| object whose ``type`` attribute is not ``None``. The network-creation
functions in the |mod_supply_chain_network| module set this attribute for you at the relevant node(s),
or you can do it manually.

External customers always have an order lead time of 0 and a shipment lead time of 0.


External Suppliers
~~~~~~~~~~~~~~~~~~~
Any node can have an **external supplier**—a supplier that is not a node that is modeled explicitly
in the system. External suppliers are the only source of exogenous supply in the system. If there are 
no external suppliers, there is no supply. A node can have both an external supplier and one or 
more predecessor nodes.

To specify that a node has an external supplier, set its ``supply_type`` attribute
to something other than ``None``. (See |class_node| for a list of valid supply types.) The network-creation
functions in |mod_supply_chain_network| module set this attribute for you at the relevant node(s),
or you can do it manually.

External suppliers always have sufficient supply; they never have stockouts.


Inventory Policies
------------------
Each node in the system must have an inventory policy, specified as a |class_policy| object.
Different nodes may have different types of policies. 

**Example:** Simulate a 2-stage serial system in which the upstream node (node 0) uses
an :math:`(r,Q)` policy with :math:`r=10` and :math:`Q=50`, and the downstream node (node 1) uses
a base-stock policy with :math:`S=50`. The demand has a Poisson distribution with mean 45. 
Both nodes have a (shipment) lead time of 1.

.. testsetup:: *

	from stockpyl.sim import simulation

.. doctest::

	>>> from stockpyl.supply_chain_network import serial_system
	>>> network = serial_system(
	...     num_nodes=2,
	...     demand_type='P',
	...     mean=45,
	...     policy_type=['rQ', 'BS'],
	...     reorder_point=[10, None],
	...     order_quantity=[50, None],
	...     base_stock_level=[None, 50],
	...     shipment_lead_time=[1, 1]
	... )
	>>> simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
	>>> write_results(network=network, num_periods=4, columns_to_print='minimal', print_cost_summary=False)
	  t  i=0      IO:1    OQ:EXT    IS:EXT    OS:1    IL  i=1      IO:EXT    OQ:0    IS:0    OS:EXT    IL
	---  -----  ------  --------  --------  ------  ----  -----  --------  ------  ------  --------  ----
	  0             42        50         0      42     8               42      42       0        42     8
	  1             50        50        50      50     8               50      50      42        50     0
	  2             37         0        50      37    21               37      37      50        37    13
	  3             47        50         0      21   -26               47      47      37        47     3
	  4              0         0         0       0   -26                0       0       0         0     3




Advanced Features
-----------------

Supply Disruptions
~~~~~~~~~~~~~~~~~~

|sp| can simulate supply disruptions, typically generated by a 2-state Markov process. 
To specify that a node is subject to disruptions, set its ``disruption_process`` attribute
to a |class_disruption_process| object whose ``random_process_type`` attribute is not ``None``. 



Converting from Continuous Review
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A continuous-review system can often be approximated by a periodic-review system in |sp|. The sequence of events [HYPERLINK]
used by |sp| means that the lead times in the continuous-review system should be kept the same when modeling
as a periodic-review system in |sp|. 

**Example:** Example 6.1 consists of a 3-node serial system with downstream node 1. The code below simulates this sytem
in |sp|. Note that the average cost per period reported by the simulation is close to the expected cost of 47.65 predicted by the theory.

.. testsetup:: *

	from stockpyl.sim import simulation
	from stockpyl.supply_chain_network import serial_system

.. doctest::

	>>> network = serial_system(
	...     num_nodes=3,
	...     node_order_in_system=[3, 2, 1],
	...     local_holding_cost={1: 7, 2: 4, 3: 2},          
	...     shipment_lead_time={1: 1, 2: 1, 3: 2},
	...     stockout_cost=37.12,
	...     demand_type='N',
	...     mean=5,
	...     standard_deviation=1,
	...     policy_type='EBS',      # echelon base-stock policy
	...     base_stock_level={1: 6.49, 2: 12.02, 3: 22.71}
	... )
	>>> T = 1000
	>>> total_cost = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
	>>> print(f"Total cost per period = {total_cost / T}")
	47.259837154163556



Holding and Stockout Cost Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

asdfasdf

Running Multiple Trials
~~~~~~~~~~~~~~~~~~~~~~~





References
----------

P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


