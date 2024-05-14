.. include:: globals.inc


Stockpyl
========

|sp| is a Python package for inventory optimization and simulation. It implements
classical single-node inventory models like the economic order quantity (EOQ), newsvendor,
and Wagner-Whitin problems. It also contains algorithms for multi-echelon inventory optimization
(MEIO) under both stochastic-service model (SSM) and guaranteed-service model (GSM) assumptions. 
And, it has extensive features for simulating multi-echelon inventory systems.

.. note:: |fosct_notation|

----

Some Examples
-------------

Solve the EOQ problem with a fixed cost of 8, a holding cost of 0.225, and a demand rate of 1300 (Example 3.1 in *FoSCT*):

.. doctest::
    
    >>> from stockpyl.eoq import economic_order_quantity
    >>> Q, cost = economic_order_quantity(fixed_cost=8, holding_cost=0.225, demand_rate=1300)
    >>> Q
    304.0467800264368
    >>> cost
    68.41052550594829

Or the newsvendor problem with a holding cost of 0.18, a stockout cost of 0.70, and demand that is normally
distributed with mean 50 and standard deviation 8 (Example 4.3 in *FoSCT*):

.. doctest::
    
    >>> from stockpyl.newsvendor import newsvendor_normal
    >>> S, cost = newsvendor_normal(holding_cost=0.18, stockout_cost=0.70, demand_mean=50, demand_sd=8)
    >>> S
    56.60395592743389
    >>> cost
    1.9976051931766445

Note that most functions in Stockpyl use longer, more descriptive parameter names (``holding_cost``, ``fixed_cost``, etc.)
rather than the shorter notation assigned to them in textbooks and articles (``h``, ``K``). 

Stockpyl can solve the Wagner-Whitin model using dynamic programming: 

.. doctest::

    >>> from stockpyl.wagner_whitin import wagner_whitin
    >>> T = 4
    >>> h = 2
    >>> K = 500
    >>> d = [90, 120, 80, 70]
    >>> Q, cost, theta, s = wagner_whitin(T, h, K, d)
    >>> Q # Optimal order quantities
    [0, 210, 0, 150, 0]
    >>> cost # Optimal cost
    1380.0
    >>> theta # Cost-to-go function
    array([   0., 1380.,  940.,  640.,  500.,    0.])
    >>> s # Optimal next period to order in
    [0, 3, 5, 5, 5]

And finite-horizon stochastic inventory problems:

.. doctest::

    >>> from stockpyl.finite_horizon import finite_horizon_dp
    >>> T = 5
    >>> h = 1
    >>> p = 20
    >>> h_terminal = 1
    >>> p_terminal = 20
    >>> c = 2
    >>> K = 50
    >>> mu = 100
    >>> sigma = 20
    >>> s, S, cost, _, _, _ = finite_horizon_dp(T, h, p, h_terminal, p_terminal, c, K, mu, sigma)
    >>> s # Reorder points
    [0, 110, 110, 110, 110, 111]
    >>> S # Order-up-to levels
    [0, 133.0, 133.0, 133.0, 133.0, 126.0]

Stockpyl includes an implementation of the Clark and Scarf (1960) algorithm for stochastic serial systems (more precisely,
Chen-Zheng's (1994) reworking of it):

.. doctest::

    >>> from stockpyl.supply_chain_network import serial_system
    >>> from stockpyl.ssm_serial import optimize_base_stock_levels
    >>> # Build network.
    >>> network = serial_system(
    ...     num_nodes=3,
    ...     node_order_in_system=[3, 2, 1],
    ...     echelon_holding_cost=[4, 3, 1],
    ...     local_holding_cost=[4, 7, 8],
    ...     shipment_lead_time=[1, 1, 2],
    ...     stockout_cost=40,
    ...     demand_type='N',
    ...     mean=10,
    ...     standard_deviation=2
    ... )
    >>> # Optimize echelon base-stock levels.
    >>> S_star, C_star = optimize_base_stock_levels(network=network)
    >>> print(f"Optimal echelon base-stock levels = {S_star}")
    Optimal echelon base-stock levels = {3: 44.11999999999999, 2: 34.879999999999995, 1: 25.727999999999994}
    >>> print(f"Optimal expected cost per period = {C_star}")
    Optimal expected cost per period = 227.14074094530974

Stockpyl has extensive features for simulating multi-echelon inventory systems. Below, we simulate
the same serial system, obtaining an average cost per period that is similar to what the theoretical
model predicted above.

.. doctest::

    >>> from stockpyl.supply_chain_network import echelon_to_local_base_stock_levels
    >>> from stockpyl.sim import simulation
    >>> from stockpyl.policy import Policy
    >>> # Convert to local base-stock levels and set nodes' inventory policies.
    >>> S_star_local = echelon_to_local_base_stock_levels(network, S_star)
    >>> for n in network.nodes:
    ...     n.inventory_policy = Policy(type='BS', base_stock_level=S_star_local[n.index], node=n)
    >>> # Simulate the system.
    >>> T = 1000
    >>> total_cost = simulation(network=network, num_periods=T, rand_seed=42)
    >>> print(f"Average total cost per period = {total_cost/T}")
    Average total cost per period = 226.19159620574135


Stockpyl also implements Graves and Willems' (2000) dynamic programming algorithm for optimizing 
committed service times (CSTs) in acyclical guaranteed-service model (GSM) systems:

.. doctest::

    >>> from stockpyl.gsm_tree import optimize_committed_service_times
    >>> from stockpyl.instances import load_instance
    >>> # Load a named instance, Example 6.5 from FoSCT.
    >>> tree = load_instance("example_6_5")
    >>> # Optimize committed service times.
    >>> opt_cst, opt_cost = optimize_committed_service_times(tree)
    >>> print(f"Optimal CSTs = {opt_cst}")
    Optimal CSTs = {1: 0, 3: 0, 2: 0, 4: 1}
    >>> print(f"Optimal expected cost per period = {opt_cost}")
    Optimal expected cost per period = 8.277916867529369

----



.. toctree::
    :maxdepth: 3
    :caption: Documentation Contents

    install
    tutorial/tutorial
    api/api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`


.. sidebar-links::
    :github:
    :pypi: stockpyl
