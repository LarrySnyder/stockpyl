.. include:: ../globals.inc

.. _tutorial_sim_page:

Simulation
====================

|sp| contains code to simulate single- or multi-echelon inventory systems. The system being simulated
can include many different features, including:

	* Multiple products, with relationships specified by bill-of-materials (BOM) structures
	* Stochastic demand with a variety of built-in demand distributions, or supply your own
	* Inventory management using a variety of built-in inventory policies, or supply your own
	* Stochastic supply disruptions with various implications
	* Fixed and/or variable costs, or supply your own cost functions
	* Period-by-period, node-by-node state variables output to table or CSV file


.. note:: |node_stage|

.. note:: |fosct_notation|

.. seealso::

	For more details, see the API documentation for the |mod_sim|, |mod_sim_io|, and |mod_supply_chain_product| modules.

.. contents::
    :depth: 3

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
		>>> _ = simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
		>>> write_results(network=network, num_periods=4, columns_to_print='basic')
		  t  | i=0      IO:EXT    OQ:EXT    IS:EXT    OS:EXT    IL
		---  -------  --------  --------  --------  --------  ----
		  0  |              12        12         0        12     1
		  1  |               6         6        12         6     7
		  2  |              11        11         6        11     2
		  3  |              14        14        11        13    -1

Interpreting the results:

	* In period 0, the node has an inbound order (``IO:EXT`` column), i.e., demand, of 12; it places an order
	  of size 12 (``OQ:EXT``), receives no inbound shipment (``IS:EXT``), and sends an outbound shipment of 12 (``IS:EXT``). It ends the period
	  with an inventory level of 1 (``IL``). (At the beginning of period 0, the inventory level was equal to the base-stock level, 13.) 
	* In period 1, the node has a demand of 6; it places an order of size 6; it receives the shipment of size 12 ordered in period 0;
	  it ships 6 units and ends with an inventory level of 7.
	* A backorder occurs in period 3, because the node begins the period with an inventory level of 2, and receives a demand of 14, but
	  only receives a shipment of 11.

(In the column headers, ``EXT`` refers to the external supplier and customer. ``|-1001`` refers to the "dummy" products
at the nodes, which can be ignored in this case. For more details about the columns in the
output produced by :func:`~stockpyl.sim_io.write_results`, see the API documentation for the |mod_sim_io| module.)

.. note:: :func:`~stockpyl.sim.simulation` fills the state variables—the results of the simulation—
	directly into the |class_network| object that is passed in the ``network`` parameter. This object
	can then be passed to :func:`~stockpyl.sim.write_results` to pretty-print the results.


Data Structures
--------------------------------

The simulation code in |sp| makes use of the |class_network| and |class_node| classes, which contain all of 
the data for the system to be simulated. 

.. seealso::

	For more information,
	see the :ref:`tutorial page for multi-echelon inventory optimization (MEIO) <tutorial_meio_page>`, or the
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
	Total cost per period = 1.9906261152138731

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
	...		base_stock_level=264.8,
	...		shipment_lead_time=4,
	...		order_lead_time=1	# to account for difference in SoE
	... )
	>>> T = 1000
	>>> total_cost = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
	>>> print(f"Total cost per period = {total_cost / T}")
	Total cost per period = 4.475292852532866

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


.. _external_suppliers:

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
		>>> _ = simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
		>>> write_results(network=network, num_periods=4, columns_to_print='basic')
		  t  | i=0      IO:1    OQ:EXT    IS:EXT    OS:1    IL  | i=1      IO:EXT    OQ:0    IS:0    OS:EXT    IL
		---  -------  ------  --------  --------  ------  ----  -------  --------  ------  ------  --------  ----
		  0  |            42        50         0      42     8  |              42      42       0        42     8
		  1  |            50        50        50      50     8  |              50      50      42        50     0
		  2  |            37         0        50      37    21  |              37      37      50        37    13
		  3  |            47        50         0      21   -26  |              47      47      37        47     3

.. _sim_output:

Displaying the Results
----------------------

The :func:`~stockpyl.sim_io.write_results` function in the |mod_sim_io| module displays the results of
a simulation. It takes as input the |class_network| object that already has its state variables 
filled by the simulation, and prints a table to the console and/or to a CSV file. The table lists the
values of the state variables for every node and every time period.  
All state variables refer to their values at the end of the period.

.. note::

	This section assumes that there are no products explicitly added to the network, i.e., the network
	only contains :ref:`dummy products<dummy_products>`. For the simulation output for 
	multiproduct networks, see :ref:`Multiproduct Simulation Output<multiproduct_sim_output>`.

The table has the following format:

	* Each row corresponds to a period in the simulation.
	* Each node is represented by a group of columns. 
	* The columns for each node are as follows:

		- ``i=<node index>``: label for the column group
		- ``DISR``: was the node disrupted in the period? (True/False)
		- ``IO:s``: inbound order received from successor ``s``
		- ``IOPL:s``: inbound order pipeline from successor ``s``: a list of order
		  quantities arriving from succesor ``s`` in ``r`` periods from the
		  period, for ``r`` = 1, ..., ``order_lead_time``
		- ``OQ:p``: order quantity placed to predecessor ``p`` in the period
		- ``OQFG`` : order quantity of finished good (this "order" is never actually
		  placed—only the raw material orders specified in ``OQ`` are placed; but ``OQFG`` can
		  be useful for debugging)
		- ``OO:p``: on-order quantity (items that have been ordered from successor
		  ``p`` but not yet received) 
		- ``IS:p``: inbound shipment received from predecessor ``p`` 
		- ``ISPL:p``: inbound shipment pipeline from predecessor ``p``: a list of
		  shipment quantities arriving from predecessor ``p`` in ``r`` periods from
		  the period, for ``r`` = 1, ..., ``shipment_lead_time``
		- ``IDI:p``: inbound disrupted items: number of items from predecessor ``p``
		  that cannot be received due to a type-RP disruption at the node
		- ``RM|rm``: number of items of raw material ``rm`` in raw-material inventory
		  at node
		- ``PFG``: number of items of the product that are pending, waiting to be
		  processed from raw materials
		- ``OS:s``: outbound shipment to successor ``s``
		- ``DMFS``: demand met from stock at the node in the current period
		- ``FR``: fill rate; cumulative from start of simulation to the current period
		- ``IL``: inventory level (positive, negative, or zero) at node
		- ``BO:s``: backorders owed to successor ``s``
		- ``ODI:s``: outbound disrupted items: number of items held for successor ``s`` due to
		  a type-SP disruption at ``s``
		- ``HC``: holding cost incurred at the node in the period
		- ``SC``: stockout cost incurred at the node in the period
		- ``ITHC``: in-transit holding cost incurred for items in transit to all successors
		  of the node
		- ``REV``: revenue (**Note:** *not currently supported*)
		- ``TC``: total cost incurred at the node (holding, stockout, and in-transit holding)

	* For state variables that are indexed by successor, if ``s`` = ``EXT``, the column
	  refers to the node's external customer
	* For state variables that are indexed by predecessor, if ``p`` = ``EXT``, the column
	  refers to the node's external supplier


**Example:** Consider a 4-node system in which nodes 1 and 2 face external demand; node 3 has
an external supplier and serves nodes 1 and 2; and node 4 has an external customer and serves node 1.
Since node 1 has two predecessors (nodes 3 and 4), node 1 needs one unit from each predecessor in order
to make one unit of its own item.
Demands at nodes 1 and 2 have Poisson distributions with mean 10. The holding cost is 1 at nodes 3 and 4
and 2 at nodes 1 and 2. The stockout cost is 10 at nodes 1 and 2. Node 1 has no order lead time and a
shipment lead time of 2. Node 2 has an order lead time of 1 and a shipment lead time of 1. Nodes 3 and for
each have a shipment lead time of 1. Each stage follows a base-stock policy, with base-stock levels of
12, 12, 20, 12 at nodes 1, ..., 4, respectively. The code below builds this network, simulates it for 10 periods, and 
displays the results.

	.. code-block::
		
		>>> from stockpyl.supply_chain_network import network_from_edges
		>>> from stockpyl.sim import simulation
		>>> from stockpyl.sim_io import write_results
		>>> network = network_from_edges(
		...     edges=[(3, 2), (3, 1), (4, 1)],
		...     node_order_in_lists=[1, 2, 3, 4],
		...     local_holding_cost=[2, 2, 1, 1],
		...     stockout_cost=[10, 10, 0, 0],
		...     order_lead_time=[0, 1, 0, 0],   
		...     shipment_lead_time=[2, 1, 0, 1],
		...     demand_type=['P', 'P', None, None],
		...     mean=[10, 10, None, None],
		...     policy_type=['BS', 'BS', 'BS', 'BS'],
		...     base_stock_level=[30, 25, 10, 10]
		... )
		>>> simulation(network=network, num_periods=10)
		>>> write_results(network, num_periods=10)

The results are shown in the table below. In period 0:

	* Node 1 has a demand of 13 (``IO:EXT`` column),
	  places orders to nodes 3 and 4 of size 13 each (``OQ:3`` and ``OQ:4`` columns), ships 13 units
	  to its customer (``OS:EXT``), and ends the period with an inventory level of 17 (``IL``), incurring
	  a holding cost (``HC``) and a total cost (``TC``) of 34. (Each node begins the
	  simulation with its inventory level equal to its base-stock level.) 
	* Node 2 has a demand of 9, places an order of size 9 to node 3, ships 9 units to its customer, 
	  and ends the period with an inventory level of 16. 
	* Node 3 receives the order of 13 from node 1 (``IO:1`` = 13), but not the order from node 2 (``IO:2`` = 0)
	  since node 2 has an order lead time of 1. Node 2's order is in node 3's inbound order pipeline
	  (``IOPL:2``). Node 3 places an order of size 13 to its supplier (``OQ:EXT``) and receives it immediately
	  as an inbound shipment (``IS:EXT``) because its lead time is 0. It ships 13 units to node 1 (``OS:1``) but no units
	  to node 2 (``OS:2``) since it has not yet received an order from node 2. Its ending inventory level is 10.
	* Node 4 receives the order of size 13 from node 1 (``IO:1``), places an order of size 13 to its supplier (``OQ:EXT``).
	  It does not receive the shipment yet since its shipment lead time is 1, but the shipment appears in its
	  inbound shipment pipeline (``ISPL:EXT``). It began the period with 10 units in inventory, so it ships those
	  10 units to node 1 (``OS:1``), has 3 backorders for node 1 (``BO:1``), and ends with an inventory level of -3 (``IL``).

In period 1:

	* Node 1 receives a demand of 10, orders 10 units from nodes 3 and 4, so it now has 23 units on order from each
	  predecessor (``OO:3`` and ``OO:4``). Node 3 shipped 13 units in period 0 and will ship 10 in period 1, so node 1's
	  inbound shipment pipeline from node 3 (``ISPL:3``) shows 13 units arriving in one period and 10 units arriving in two periods.
	  Node 4 shipped only 10 units in period 0 (because of its insufficient inventory) and 13 in period 1, which
	  is reflected in ``ISPL:4``. Node 1 ships 10 units to its supplier and ends the period with an inventory level of 7.
	* Node 2 receives a demand of 9 again, places an order of size 9, ships 9 units to its customer, and ends
	  with an inventory level of 7.
	* Node 3 receives an order of size 10 from node 1 (``IO:1``), which node 1 placed in period 0, and an order of size
	  9 from node 2 (``IO:2``), which node 2 placed in period 1. It places an order of size 19, receives it immediately,
	  ships 10 units to node 1 and 9 to node 2, and ends with 10 units in inventory.
	* Node 4 receives the order of size 10 from node 1 and places an order of size 10. It receives the order of 13 that
	  it placed to its supplier in node 0 (``IS:EXT``), ships 13 units to node 1 (3 of which were backorders from period 0
	  and 10 of which are for the current demand), and ends with an inventory level of 0.

And so on. Also worth noting is that in period 2, node 1 receives 13 units from node 3 and 10 from node 4. It needs one 
unit from each predecessor to make one unit of its own finished product, so it can only make 10 such units, and
3 units of node 3's product remains in node 1's raw material inventory (``RM:3``). Node 1 began period 2 with an
inventory level of 7, received a demand of 9, and added 10 units to its finished goods inventory, so its ending
inventory level is 8 (``IL``). These 8 units incur a holding cost of 2 each; but the 3 units in raw material inventory
incur node 3's holding cost rate of 1 each. So, the total holding cost (``HC``) at node 1 is 19 in period 2.
	  

.. csv-table:: Simulation Results
   :file: ../aux_files/sim_io_example_instance.csv
   :widths: auto
   :header-rows: 1
   :stub-columns: 1
   
:download:`Download table in CSV format <../aux_files/sim_io_example_instance.csv>`

You can control which rows and columns are printed using the ``periods_to_print`` and ``columns_to_print`` parameters,
respectively. The code below tells :func:`~stockpyl.sim_io.write_results` to print periods 3-8 and only the ``OQ``, ``IL``, and ``TC``
columns:

	.. testsetup:: col_group

		from stockpyl.supply_chain_network import network_from_edges
		from stockpyl.sim import simulation
		from stockpyl.sim_io import write_results
		network = network_from_edges(
		    edges=[(3, 2), (3, 1), (4, 1)],
		    node_order_in_lists=[1, 2, 3, 4],
		    local_holding_cost=[2, 2, 1, 1],
		    stockout_cost=[10, 10, 0, 0],
		    order_lead_time=[0, 1, 0, 0],   
		    shipment_lead_time=[2, 1, 0, 1],
		    demand_type=['P', 'P', None, None],
		    mean=[10, 10, None, None],
		    policy_type=['BS', 'BS', 'BS', 'BS'],
		    base_stock_level=[30, 25, 10, 10]
		)
		simulation(network=network, num_periods=10, rand_seed=40)
		
	.. doctest:: col_group

		>>> write_results(
		...	network=network, 
		...	num_periods=10,
		...	periods_to_print=list(range(3, 9)), 
		...	columns_to_print=['OQ', 'IL', 'TC']
		...	)
		  t  | i=1      OQ:3    OQ:4    IL    TC  | i=2      OQ:3    IL    TC  | i=3      OQ:EXT    IL    TC  | i=4      OQ:EXT    IL    TC
		---  -------  ------  ------  ----  ----  -------  ------  ----  ----  -------  --------  ----  ----  -------  --------  ----  ----
		  3  |             6       6    15    30  |            14    -2    20  |              19    10    38  |               6     4    19
		  4  |            11      11    13    26  |            14    -3    30  |              25    10    41  |              11    -1    16
		  5  |            11      11     8    16  |             9     2     4  |              25    10    46  |              11    -1    21
		  6  |            10      10     8    17  |             8     8    16  |              19    10    40  |              10     0    22
		  7  |            15      15     4     9  |             9     8    16  |              23    10    43  |              15    -5    21
		  8  |            17      17    -2    20  |            12     4     8  |              26    10    51  |              17    -7    25

Certain strings serve as shortcuts for groups of columns. (See the docstring for :func:`~stockpyl.sim_io.write_results` for a list
of allowable strings.) Shortcuts and column names can be combined in one list:

	.. testsetup:: col_group2
	
		from stockpyl.supply_chain_network import network_from_edges
		from stockpyl.sim import simulation
		from stockpyl.sim_io import write_results
		network = network_from_edges(
		    edges=[(3, 2), (3, 1), (4, 1)],
		    node_order_in_lists=[1, 2, 3, 4],
		    local_holding_cost=[2, 2, 1, 1],
		    stockout_cost=[10, 10, 0, 0],
		    order_lead_time=[0, 1, 0, 0],   
		    shipment_lead_time=[2, 1, 0, 1],
		    demand_type=['P', 'P', None, None],
		    mean=[10, 10, None, None],
		    policy_type=['BS', 'BS', 'BS', 'BS'],
		    base_stock_level=[30, 25, 10, 10]
		)
		simulation(network=network, num_periods=10, rand_seed=40)
		
	.. doctest:: col_group2

		>>> write_results(
		...	network=network, 
		...	num_periods=10,
		...	periods_to_print=list(range(3, 9)), 
		...	columns_to_print=['OQ', 'IL', 'costs']
		...	)
		  t  | i=1      OQ:3    OQ:4    IL    HC    SC    TC  | i=2      OQ:3    IL    HC    SC    TC  | i=3      OQ:EXT    IL    HC    SC    TC  | i=4      OQ:EXT    IL    HC    SC    TC
		---  -------  ------  ------  ----  ----  ----  ----  -------  ------  ----  ----  ----  ----  -------  --------  ----  ----  ----  ----  -------  --------  ----  ----  ----  ----
		  3  |             6       6    15    30     0    30  |            14    -2     0    20    20  |              19    10    10     0    38  |               6     4     4     0    19
		  4  |            11      11    13    26     0    26  |            14    -3     0    30    30  |              25    10    10     0    41  |              11    -1     0     0    16
		  5  |            11      11     8    16     0    16  |             9     2     4     0     4  |              25    10    10     0    46  |              11    -1     0     0    21
		  6  |            10      10     8    17     0    17  |             8     8    16     0    16  |              19    10    10     0    40  |              10     0     0     0    22
		  7  |            15      15     4     9     0     9  |             9     8    16     0    16  |              23    10    10     0    43  |              15    -5     0     0    21
		  8  |            17      17    -2     0    20    20  |            12     4     8     0     8  |              26    10    10     0    51  |              17    -7     0     0    25


Accessing the State Variables
--------------------------------

In addition to viewing the results in tabular form, you can also query a |class_state_vars| object
using methods such as 
:meth:`~stockpyl.node_state_vars.NodeStateVars.get_inventory_level`, 
:meth:`~stockpyl.node_state_vars.NodeStateVars.get_order_quantity`, etc., to get values of 
individual state variables. The arguments of these
methods are the relevant nodes/products, but these arguments can be omitted if they are inferrable
(e.g., if the node has a single predecessor, or a single product, etc.).

	.. doctest:: col_group2

		>>> network.nodes_by_index[1].state_vars[3].get_inventory_level()
		15.0
		>>> network.nodes_by_index[1].state_vars[3].get_order_quantity(predecessor=3)
		6.0
		>>> network.nodes_by_index[2].state_vars[4].get_inbound_shipment()
		13.0
		>>> network.nodes_by_index[2].state_vars[6].get_inbound_order()
		8
		>>> network.nodes_by_index[3].state_vars[6].get_inbound_order(successor=2)
		9.0

Some state variables, in particular those that are not indexed by any node or product,
are accessed by using the attribute directly:

	.. doctest:: col_group2

		>>> network.nodes_by_index[1].state_vars[3].holding_cost_incurred
		30.0
		>>> network.nodes_by_index[3].state_vars[5].total_cost_incurred
		46.0



Advanced Features
-----------------

Supply Disruptions
~~~~~~~~~~~~~~~~~~

|sp| can simulate supply disruptions, typically generated by a 2-state Markov process. 
To specify that a node is subject to disruptions, set its ``disruption_process`` attribute
to a |class_disruption_process| object whose ``random_process_type`` attribute is not ``None``. 

**Example::** The following code simulates the instance in Example 9.3, in which the demand
is deterministic at 2000 per period and disruptions follow a 2-state Markov process with
disruption probability 0.04 and recovery probability 0.25:

.. testsetup:: *

	from stockpyl.supply_chain_network import single_stage_system
	from stockpyl.sim import simulation

.. doctest::

	>>> from stockpyl.disruption_process import DisruptionProcess
	>>> network = single_stage_system(
	...     holding_cost=0.25,
	...     stockout_cost=3,
	...     demand_type='D',                # deterministic demand
	...     demand_list=2000,
	...     disruption_process=DisruptionProcess(random_process_type='M', disruption_probability=0.04, recovery_probability=0.25),
	...     policy_type='BS',               
	...     base_stock_level=8000
	... )
	>>> T = 10000
	>>> total_cost = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
	>>> print(f"Total cost per period = {total_cost / T}")
	Total cost per period = 2831.9


|sp| supports four types of disruptions, which differ by how the system "pauses" when a disruption occurs:

	* ``'OP'`` (order-pausing: the stage cannot place orders during disruptions) (default)
	* ``'SP'`` (shipment-pausing: the stage can place orders during disruptions but its supplier(s) cannot ship them)
	* ``'TP'`` (transit-pausing: items in transit to the stage are paused during disruptions)
	* ``'RP'`` (receipt-pausing: items cannot be received by the disrupted stage; they accumulate 
	  just before the stage and are received when the disruption ends)


**Example:** The code below simulates a 2-node serial system in which the downstream node (node 2) is subject to
disruptions. First, type-OP disruptions:

	.. testsetup:: *

		from stockpyl.supply_chain_network import serial_system
		from stockpyl.sim import simulation
		from stockpyl.sim_io import write_results

	.. doctest::

		>>> from stockpyl.disruption_process import DisruptionProcess
		>>> network = serial_system(
		...     num_nodes=2,
		...     node_order_in_system=[1, 2],
		...     shipment_lead_time=1,
		...     demand_type='P',
		...     mean=20,
		...     policy_type='BS',
		...     base_stock_level=[25, 25]
		... )
		>>> network.nodes_by_index[2].disruption_process = DisruptionProcess(
		...     random_process_type='M',
		...     disruption_type='OP',
		...     disruption_probability=0.1,
		...     recovery_probability=0.4
		... )
		>>> T = 100
		>>> _ = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
		>>> write_results(network=network, num_periods=T, periods_to_print=list(range(7, 16)), columns_to_print=['DISR', 'IO', 'OQ', 'IS', 'OS', 'IL'])
		  t  | i=1    DISR      IO:2    OQ:EXT    IS:EXT    OS:2    IL  | i=2    DISR      IO:EXT    OQ:1    IS:1    OS:EXT    IL
		---  -------  ------  ------  --------  --------  ------  ----  -------  ------  --------  ------  ------  --------  ----
		  7  |        False       19        19        14      19     6  |        False         19      19      14        19     6
		  8  |        False       20        20        19      20     5  |        False         20      20      19        20     5
		  9  |        False        0         0        20       0    25  |        True          21       0      20        21     4
		 10  |        False        0         0         0       0    25  |        True          24       0       0         4   -20
		 11  |        False        0         0         0       0    25  |        True          22       0       0         0   -42
		 12  |        False        0         0         0       0    25  |        True          20       0       0         0   -62
		 13  |        False      104       104         0      25   -79  |        False         17     104       0         0   -79
		 14  |        False       20        20       104      99     5  |        False         20      20      25        25   -74
		 15  |        False       21        21        20      21     4  |        False         21      21      99        95     4

Node 2 is disrupted starting in period 9 (``DISR`` column). Since these are order-pausing disruptions, the node cannot place orders, so its
order quantity for orders to node 1 (``OQ:1``) is 0, starting in period 9 and continuing until the disruption ends in period 13,
at which point a large order is placed. At first, that order is mostly backordered upstream at node 1, since node 1 was not aware of the
upcoming large order. 

Next, type-SP disruptions:

	.. doctest::

		>>> network.nodes_by_index[2].disruption_process.disruption_type='SP'
		>>> _ = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
		>>> write_results(network=network, num_periods=T, periods_to_print=list(range(7, 16)), columns_to_print=['DISR', 'IO', 'OQ', 'IS', 'OS', 'IL', 'ODI'])
		  t  | i=1    DISR      IO:2    OQ:EXT    IS:EXT    OS:2    IL    ODI:2  | i=2    DISR      IO:EXT    OQ:1    IS:1    OS:EXT    IL    ODI:EXT
		---  -------  ------  ------  --------  --------  ------  ----  -------  -------  ------  --------  ------  ------  --------  ----  ---------
		  7  |        False       19        19        14      19     6        0  |        False         19      19      14        19     6          0
		  8  |        False       20        20        19      20     5        0  |        False         20      20      19        20     5          0
		  9  |        False       21        21        20       0     4       21  |        True          21      21      20        21     4          0
		 10  |        False       24        24        21       0     1       45  |        True          24      24       0         4   -20          0
		 11  |        False       22        22        24       0     3       67  |        True          22      22       0         0   -42          0
		 12  |        False       20        20        22       0     5       87  |        True          20      20       0         0   -62          0
		 13  |        False       17        17        20     104     8        0  |        False         17      17       0         0   -79          0
		 14  |        False       20        20        17      20     5        0  |        False         20      20     104        99     5          0
		 15  |        False       21        21        20      21     4        0  |        False         21      21      20        21     4          0

In this case, node 2 can still place orders during the disruption, but node 1 cannot ship them. Instead, the items are moved to
node 1's "outbound disrupted items" category (``ODI:2``). When the disruption ends in period 13, node 1 ships those accumulated items (``OS:2``).

Next, type-TP disruptions:

	.. doctest::

		>>> network.nodes_by_index[2].disruption_process.disruption_type='TP'
		>>> _ = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
		>>> write_results(network=network, num_periods=T, periods_to_print=list(range(7, 16)), columns_to_print=['DISR', 'IO', 'OQ', 'IS', 'ISPL', 'OS', 'IL'])
		  t  | i=1    DISR      IO:2    OQ:EXT    IS:EXT  ISPL:EXT      OS:2    IL  | i=2    DISR      IO:EXT    OQ:1    IS:1  ISPL:1      OS:EXT    IL
		---  -------  ------  ------  --------  --------  ----------  ------  ----  -------  ------  --------  ------  ------  --------  --------  ----
		  7  |        False       19        19        14  [19.0]          19     6  |        False         19      19      14  [19.0]          19     6
		  8  |        False       20        20        19  [20.0]          20     5  |        False         20      20      19  [20.0]          20     5
		  9  |        False       21        21        20  [21.0]          21     4  |        True          21      21      20  [21.0]          21     4
		 10  |        False       24        24        21  [24.0]          24     1  |        True          24      24       0  [45.0]           4   -20
		 11  |        False       22        22        24  [22.0]          22     3  |        True          22      22       0  [67.0]           0   -42
		 12  |        False       20        20        22  [20.0]          20     5  |        True          20      20       0  [87.0]           0   -62
		 13  |        False       17        17        20  [17.0]          17     8  |        False         17      17       0  [104.0]          0   -79
		 14  |        False       20        20        17  [20.0]          20     5  |        False         20      20     104  [20.0]          99     5
		 15  |        False       21        21        20  [21.0]          21     4  |        False         21      21      20  [21.0]          21     4
				
The disruption means that items in transit to node 2 are paused. This is evident from the inbound shipment pipeline at node 2 from node 1 (``ISPL:1``),
which increases as the disruption continues and then is cleared when the disruption ends. 

Finally, type-RP disruptions:

	.. doctest::

		>>> network.nodes_by_index[2].disruption_process.disruption_type='RP'
		>>> _ = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
		>>> write_results(network=network, num_periods=T, periods_to_print=list(range(7, 16)), columns_to_print=['DISR', 'IO', 'OQ', 'IS', 'OS', 'IL', 'ISPL', 'IDI'])
		  t  | i=1    DISR      IO:2    OQ:EXT    IS:EXT  ISPL:EXT      IDI:EXT    OS:2    IL  | i=2    DISR      IO:EXT    OQ:1    IS:1  ISPL:1      IDI:1    OS:EXT    IL
		---  -------  ------  ------  --------  --------  ----------  ---------  ------  ----  -------  ------  --------  ------  ------  --------  -------  --------  ----
		  7  |        False       19        19        14  [19.0]              0      19     6  |        False         19      19      14  [19.0]          0        19     6
		  8  |        False       20        20        19  [20.0]              0      20     5  |        False         20      20      19  [20.0]          0        20     5
		  9  |        False       21        21        20  [21.0]              0      21     4  |        True          21      21       0  [21.0]         20         5   -16
		 10  |        False       24        24        21  [24.0]              0      24     1  |        True          24      24       0  [24.0]         41         0   -40
		 11  |        False       22        22        24  [22.0]              0      22     3  |        True          22      22       0  [22.0]         65         0   -62
		 12  |        False       20        20        22  [20.0]              0      20     5  |        True          20      20       0  [20.0]         87         0   -82
		 13  |        False       17        17        20  [17.0]              0      17     8  |        False         17      17     107  [17.0]          0        99     8
		 14  |        False       20        20        17  [20.0]              0      20     5  |        False         20      20      17  [20.0]          0        20     5
		 15  |        False       21        21        20  [21.0]              0      21     4  |        False         21      21      20  [21.0]          0        21     4

In this case, the disruptions prevent node 2 from receiving items. During the disruption, items that would otherwise have been 
received by node 2 from node 1 are instead moved to node 2's "inbound disrupted items" category (``IDI:1``). They remain there
until the disruption ends, at which point they are included in the node's inbound shipment (``IS:1``). 

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
	Total cost per period = 47.25983715416357



Holding and Stockout Cost Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As an alternative to using linear holding and stockout cost functions using coefficients that you provide,
|sp| allows you to provide arbitrary functions that are used to calculate the holding and stockout costs
based on the current inventory level. The functions can be standalone functions or lambda functions. 

**Example:** Simulate a single-stage system with Poisson(15) demand, a base-stock level of 17, and
holding and stockout cost functions given by

.. math::

	h(x) = 0.5(x^+)^2 

	p(x) = 10\sqrt{x^+},

where :math:`a^+ \equiv \max\{a,0\}` and :math:`x` is the inventory level (so :math:`x^+` is the on-hand inventory
and :math:`(-x)^+` is the backorders).

	.. doctest::

		>>> from stockpyl.supply_chain_network import single_stage_system
		>>> from stockpyl.sim import simulation
		>>> from stockpyl.sim_io import write_results
		>>> import math
		>>> def holding_cost(x):
		...	return 0.5 * max(x, 0)**2
		>>> network = single_stage_system(
		...	local_holding_cost_function=holding_cost,
		...	stockout_cost_function=lambda x: 10 * math.sqrt(max(-x, 0)),
		...	demand_type='P',	
		...	mean=15,
		...	policy_type='BS',		
		...	base_stock_level=17,
		...	lead_time=1
		...	)
		>>> T = 100
		>>> _ = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
		>>> write_results(network=network, num_periods=T, periods_to_print=list(range(6)), columns_to_print=['basic', 'costs'])
		  t  | i=0      IO:EXT    OQ:EXT    IS:EXT    OS:EXT    IL    HC       SC       TC
		---  -------  --------  --------  --------  --------  ----  ----  -------  -------
		  0  |              18        18         0        17    -1   0    10       10
		  1  |              10        10        18        11     7  24.5   0       24.5
		  2  |              16        16        10        16     1   0.5   0        0.5
		  3  |              19        19        16        17    -2   0    14.1421  14.1421
		  4  |              11        11        19        13     6  18     0       18
		  5  |              13        13        11        13     4   8     0        8





Running Multiple Trials
~~~~~~~~~~~~~~~~~~~~~~~

The :func:`~stockpyl.sim.run_multiple_trials` function will run the simulation multiple for multiple trials. For each trial,
the function calculates the average cost per period; it then returns the mean and standard error of the mean (SEM) 
of the average costs. An :math:`\\alpha`-confidence interval can be constructed using
``mean_cost`` :math:`\\pm z_{1-(1-\\alpha)/2} \\times` ``sem_cost``.
This is useful for, e.g., comparing two systems to see whether their costs are statistically different
according to the simulation.

**Example:** Optimize the serial system in Example 6.1 of |fosct| using both the exact algorithm by Chen and Zheng (1994) and
the newsvendor heuristic by Shang and Song (2003). Simulate both solutions for 10 trials, 1000 periods per trial, and
determine whether the heuristic solution is statistically worse than the optimal solution.

.. doctest::

	>>> from stockpyl.ssm_serial import optimize_base_stock_levels, newsvendor_heuristic
	>>> from stockpyl.supply_chain_network import echelon_to_local_base_stock_levels
	>>> from stockpyl.sim import run_multiple_trials
	>>> from stockpyl.instances import load_instance
	>>> # Load network.
	>>> network = load_instance("example_6_1")
	>>> # Set base-stock levels according to optimal solution.
	>>> S_opt, _ = optimize_base_stock_levels(network=network)
	>>> S_opt_local = echelon_to_local_base_stock_levels(network, S_opt)
	>>> for n in network.nodes:
	...	n.inventory_policy.base_stock_level = S_opt_local[n.index]
	>>> mean_opt, sem_opt = run_multiple_trials(network=network, num_trials=10, num_periods=1000, rand_seed=42, progress_bar=False)
	>>> print(f"Optimal solution has simulated average cost per period with mean {mean_opt} and SEM {sem_opt}")
	Optimal solution has simulated average cost per period with mean 47.78805396416774 and SEM 0.258285462809664
	>>> # Set base-stock levels according to heuristic solution.
	>>> S_heur = newsvendor_heuristic(network=network)
	>>> S_heur_local = echelon_to_local_base_stock_levels(network, S_heur)
	>>> for n in network.nodes:
	...	n.inventory_policy.base_stock_level = S_heur_local[n.index]
	>>> mean_heur, sem_heur = run_multiple_trials(network=network, num_trials=10, num_periods=1000, rand_seed=42, progress_bar=False)
	>>> print(f"Heuristic solution has simulated average cost per period with mean {mean_heur} and SEM {sem_heur}")
	Heuristic solution has simulated average cost per period with mean 47.789138050714946 and SEM 0.270398146817947
	>>> ## Calculate confidence intervals.
	>>> from scipy.stats import norm
	>>> z = norm.ppf(1 - (1 - 0.95)/2)
	>>> lo_opt, hi_opt = mean_opt - z * sem_opt, mean_opt + z * sem_opt
	>>> lo_heur, hi_heur = mean_heur - z * sem_heur, mean_heur + z * sem_heur
	>>> print(f"Optimal solution CI = [{lo_opt}, {hi_opt}], heuristic solution CI = [{lo_heur}, {hi_heur}]")
	Optimal solution CI = [47.281823759330535, 48.29428416900494], heuristic solution CI = [47.2591674214654, 48.31910867996449]

Because the two confidence intervals overlap, we cannot say that the two solutions have statistically different
average costs. (Of course, the theory tells us that the true expected costs for the two solutions are different.)


References
----------

F. Chen and Y. S. Zheng. Lower bounds for multiechelon stochastic inventory systems. *Management Science*, 40(11):1426–1443, 1994.

K. H. Shang and J.-S. Song. Newsvendor bounds and heuristic for optimal policies in serial supply chains. *Management Science*, 49(5):618-638, 2003.

P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


