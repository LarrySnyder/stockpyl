Stockpyl
========

Stockpyl is a Python package for inventory optimization. It contains implementation for
classical single-node inventory models like the economic order quantity (EOQ), newsvendor,
and Wagner-Whitin problems. It also contains algorithms for multi-echelon inventory optimization
(MEIO). 

Most of the models and algorithms implemented in Stockpyl are discussed in the textbook
*Fundamentals of Supply Chain Theory* (*FoSCT*) by Snyder and Shen, Wiley, 2019, 2nd ed. Most of them
are much older, and *FoSCT* provides references to original sources. 



Some Examples
-------------

Solve the EOQ problem with :math:`K=8`, :math:`h=0.225`, and :math:`\lambda=1300` (Example 3.1 in *FoSCT*):

.. doctest::
    
    >>> from stockpyl.eoq import economic_order_quantity
    >>> Q, cost = economic_order_quantity(fixed_cost=8, holding_cost=0.225, demand_rate=1300)
    >>> Q
    304.0467800264368
    >>> cost
    68.41052550594829

Or the newsvendor problem with :math:`h=0.18`, :math:`p=0.70`, and :math:`D\sim N(50, 8^2)` (Example 4.3 in *FoSCT*):

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

The ``ssm_serial`` module includes the Clark and Scarf (1960) algorithm for stochastic serial systems (more precisely,
Chen-Zheng's (1994) reworking of it):

.. doctest::

    >>> from stockpyl.ssm_serial import optimize_base_stock_levels
    >>> S_star, C_star = optimize_base_stock_levels(
    ...     num_nodes=3,
    ...     echelon_holding_cost=[3, 2, 2],
    ...     lead_time=[1, 1, 2],
    ...     stockout_cost=37.12,
    ...     demand_mean=5,
    ...     demand_standard_deviation=1
    ... )
    >>> S_star
    {1: 6.5144388073261155, 2: 12.012332294949644, 3: 22.700237234889784}
    >>> C_star
    47.668653127136345

And the ``gsm_tree`` module implements Graves and Willems' (2000) the dynamic programming algorithm for optimizing committed service times (CSTs)
in acyclical guaranteed-service model (GSM) systems:

.. doctest::

    >>> from stockpyl.gsm_tree import optimize_committed_service_times
    >>> from stockpyl.instances import load_instance
    >>> # Load a named instance, Example 6.5 from FoSCT
    >>> tree = load_instance("example_6_5")
    >>> opt_cst, opt_cost = optimize_committed_service_times(tree)
    >>> opt_cst
    {1: 0, 3: 0, 2: 0, 4: 1}
    >>> opt_cost
    8.277916867529369