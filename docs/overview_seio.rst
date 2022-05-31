.. include:: globals.inc

Single-Echelon Inventory Optimization
=====================================

|sp| contains code to solve the following types of single-echelon inventory optimization problems:

* The :ref:`economic order quantity (EOQ) problem<overview_seio:The EOQ Problem>` (|mod_eoq| module)
* The :ref:`newsvendor problem<overview_seio:The Newsvendor Problem>` (|mod_newsvendor| module)
* The :ref:`(r,Q) optimization problem<overview_seio:The |rq| Optimization Problem>` (|mod_rq| module)
* The :ref:`(s,S) optimization problem<overview_seio:The |ss| Optimization Problem>` (|mod_ss| module)
* The :ref:`Wagner-Whitin problem<overview_seio:The Wagner-Whitin Problem>` (|mod_wagner_whitin| module)
* :ref:`Finite-horizon stochastic problems<overview_seio:Finite-Horizon Stochastic Problems>` with or without fixed costs (|mod_finite_horizon| module)
* Plus a number of single-echelon problems with :ref:`supply uncertainty<overview_su:Supply Uncertainty>`

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory* (|fosct|), 2nd edition
(2019).



The EOQ Problem
---------------

The |mod_eoq| module contains code for solving the economic order quantity
(EOQ) problem and some of its variants. The :func:`stockpyl.eoq.economic_order_quantity` function
implements the basic EOQ model; it returns both the optimal order quantity and the corresponding
optimal cost:

.. doctest::
    
    >>> from stockpyl.eoq import economic_order_quantity
    >>> Q, cost = economic_order_quantity(fixed_cost=8, holding_cost=0.225, demand_rate=1300)
    >>> Q
    304.0467800264368
    >>> cost
    68.41052550594829

The module also contains functions for the EOQ with backorders (EOQB) and the economic production quantity (EPQ). 

The :func:`stockpyl.eoq.joint_replenishment_problem_silver_heuristic` function implements 
Silver's (1976) heuristic for the joint replenishment problem (JRP):

.. doctest::

	>>> from stockpyl.eoq import joint_replenishment_problem_silver_heuristic
	>>> shared_fixed_cost = 600
	>>> individual_fixed_costs = [120, 840, 300]
	>>> holding_costs = [160, 20, 50]
	>>> demand_rates = [1, 1, 1]
	>>> Q, T, m, cost = joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)
	>>> Q # order quantities
	[3.103164454170876, 9.309493362512628, 3.103164454170876]
	>>> T # base cycle time
	3.103164454170876
	>>> m # order multiples
	[1, 3, 1]
	>>> cost
	837.8544026261366


The Newsvendor Problem
----------------------

The |mod_newsvendor| module contains code for solving the newsvendor problem and some of its variants. 
The :func:`stockpyl.newsvendor.newsvendor_normal` function 
implements the basic newsvendor model for normally distributed demands; it returns both the optimal base-stock level (i.e., order quantity)
and the corresponding expected optimal cost:

.. doctest::
    
    >>> from stockpyl.newsvendor import newsvendor_normal
    >>> S, cost = newsvendor_normal(holding_cost=0.18, stockout_cost=0.70, demand_mean=50, demand_sd=8)
    >>> S
    56.60395592743389
    >>> cost
    1.9976051931766445

If you only want to calculate the expected cost of a given base-stock level, you can either call
:func:`stockpyl.newsvendor.newsvendor_normal`, passing it the optional ``base_stock_level`` parameter, or
call the :func:`stockpyl.newsvendor.newsvendor_normal_cost` function:

.. doctest::

	>>> from stockpyl.newsvendor import newsvendor_normal, newsvendor_normal_cost
	>>> newsvendor_normal(holding_cost=0.18, stockout_cost=0.70, demand_mean=50, demand_sd=8, base_stock_level=53)
	(53, 2.223748044859164)
	>>> newsvendor_normal_cost(53, holding_cost=0.18, stockout_cost=0.70, demand_mean=50, demand_sd=8)
	2.223748044859164

These functions use the version of the newsvendor problem based on holding and stockout (overage and
underage) costs. The :func:`stockpyl.newsvendor.newsvendor_normal_explicit` function uses the "explicit" (or profit-maximization)
form of the newsvendor problem, whose parameters are the selling revenue, purchase cost, and salvage value:

.. doctest::

	>>> from stockpyl.newsvendor import newsvendor_normal_explicit
	>>> newsvendor_normal_explicit(selling_revenue=1.00, purchase_cost=0.30, salvage_value=0.12, demand_mean=50, demand_sd=8)
	(56.60395592743389, 33.002394806823354)

The module supports probability distributions other than normal; for example, Poisson:

.. doctest::

	>>> from stockpyl.newsvendor import newsvendor_poisson
	>>> h, p, mu = 0.18, 0.70, 50
	>>> newsvendor_poisson(h, p, mu)
	(56.0, 1.797235211809178)

You can also solve newsvendor problems for arbitrary continuous distributions specified as ``scipy.stats.rv_continuous`` 
objects:

.. doctest::

	>>> from stockpyl.newsvendor import newsvendor_continuous
	>>> from scipy.stats import lognorm
	>>> from math import exp
	>>> demand_distrib = lognorm(0.3, 0, exp(6))
	>>> newsvendor_continuous(holding_cost=1, stockout_cost=4, demand_distrib=demand_distrib)
	(519.3023987673176, 198.42277610622506)

Or arbitrary discrete distributions specified as either a ``scipy.stats.rv_discrete`` object or
as a dictionary containing the pmf:

.. doctest::

	>>> from stockpyl.newsvendor import newsvendor_discrete
	>>> from scipy.stats import geom
	>>> demand_distrib = geom(0.2)
	>>> newsvendor_discrete(holding_cost=1, stockout_cost=4, demand_distrib=demand_distrib)
	(8.0, 7.194304)
	>>> # or ...
	>>> d = range(0, 50)
	>>> f = [geom.pmf(d_val, 0.2) for d_val in d]
	>>> demand_pmf = dict(zip(d, f))
	>>> newsvendor_discrete(holding_cost=1, stockout_cost=4, demand_pmf=demand_pmf)
	(8, 7.19102133030678)


The |rq| Optimization Problem
-----------------------------

The |mod_rq| module contains code for solving the |rq| optimization problem, including
a number of approximations.
The :func:`stockpyl.rq.r_q_poisson_exact` function implements Federgruen and Zheng's (1992)
exact algorithm for the |rq| problem with Poisson demands:

.. doctest::
    
	>>> from stockpyl.rq import r_q_poisson_exact
	>>> r, Q, cost = r_q_poisson_exact(holding_cost=20, stockout_cost=150, fixed_cost=100, demand_mean=1.5, lead_time=2)
	>>> r
	3
	>>> Q
	5
	>>> cost
	107.92358063314975

For normally distributed demands, the module implements the expected-inventory-level (EIL) approximation
(Whitin (1953), Hadley and Whitin (1963)), the EOQ with backorders (EOQB) approximation (see Zheng (1992)),
the EOQ plus safety stock (EOQ+SS) approximation, and the loss-function approximation (Hadley and Whitin (1963)):

.. doctest::

	>>> from stockpyl.rq import r_q_eil_approximation, r_q_eoqb_approximation, r_q_eoqss_approximation, r_q_loss_function_approximation
	>>> h = 0.225
	>>> p = 7.5
	>>> K = 8
	>>> demand_mean = 1300
	>>> demand_sd = 150
	>>> L = 1/12
	>>> r_eil, Q_eil, _ = r_q_eil_approximation(h, p, K, demand_mean, demand_sd, L)
	>>> r_eil, Q_eil
	(213.97044213580244, 318.5901810768729)
	>>> r_eoqb, Q_eoqb = r_q_eoqb_approximation(h, p, K, demand_mean, demand_sd, L)
	>>> r_eoqb, Q_eoqb
	(128.63781442427097, 308.5737801203754)
	>>> r_eoqss, Q_eoqss = r_q_eoqss_approximation(h, p, K, demand_mean, demand_sd, L)
	>>> r_eoqss, Q_eoqss
	(190.3369965715624, 304.0467800264368)
	>>> r_lf, Q_lf = r_q_loss_function_approximation(h, p, K, demand_mean, demand_sd, L)
	>>> r_lf, Q_lf
	(126.8670634479628, 328.4491421980451)

We can evaluate these approximate solutions under the exact expected cost function:

.. doctest::

	>>> from stockpyl.rq import r_q_cost
	>>> r_q_cost(r_eil, Q_eil, h, p, K, demand_mean, demand_sd, L)
	92.28687665608078
	>>> r_q_cost(r_eoqb, Q_eoqb, h, p, K, demand_mean, demand_sd, L)
	78.20243187688158
	>>> r_q_cost(r_eoqss, Q_eoqss, h, p, K, demand_mean, demand_sd, L)
	87.04837003438256
	>>> r_q_cost(r_lf, Q_lf, h, p, K, demand_mean, demand_sd, L)
	78.07114627035178


The |ss| Optimization Problem
-----------------------------

The |mod_ss| module contains code for solving the |ss| optimization problem. 

The exact problem with Poisson (or other discrete) demands can be solved using 
the :func:`stockpyl.ss.s_s_discrete_exact` function, which implements Zheng and Federgruen's (1991)
algorithm:

.. doctest::
    
	>>> from stockpyl.ss import s_s_discrete_exact
	>>> h = 1
	>>> p = 4
	>>> K = 5
	>>> demand_mean = 6
	>>> r, Q, cost = s_s_discrete_exact(h, p, K, use_poisson=True, demand_mean=demand_mean)
	>>> r
	4.0
	>>> Q
	10.0
	>>> cost
	8.034111561471642

The :func:`stockpyl.ss.s_s_power_approximation` function implements the power approximation
for normal demands by Ehrhardt and Mosier (1984):

.. doctest::

	>>> from stockpyl.ss import s_s_power_approximation
	>>> h = 0.18
	>>> p = 0.70
	>>> K = 2.5
	>>> demand_mean = 50
	>>> demand_sd = 8
	>>> r, Q = s_s_power_approximation(h, p, K, demand_mean, demand_sd)
	>>> r
	40.19461695647407
	>>> Q
	74.29017010980579


The Wagner-Whitin Problem
-------------------------

The |mod_wagner_whitin| module contains code for solving the Wagner-Whitin problem using dynamic programming: 

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

The cost parameters may also vary from period to period:

.. doctest::

	>>> h = [5, 1, 1, 2]
	>>> K = [300, 500, 300, 500]
	>>> Q, cost, _, _ = wagner_whitin(T, h, K, d)
	>>> Q
	[0, 90, 270, 0, 0]
	>>> cost
	1020.0


Finite-Horizon Stochastic Problems
----------------------------------

The |mod_finite_horizon| module contains code for solving finite-horizon, stochastic
inventory optimization problems, with or without fixed costs, using dynamic programming (DP).

If the fixed costs are 0, then a base-stock policy is optimal and the results of the demand_pmf
indicate the optimal base-stock levels, i.e., order-up-to levels (:math:`S`) in each time period:

.. doctest::

	>>> from stockpyl.finite_horizon import finite_horizon_dp
	>>> T = 5
	>>> h = 1
	>>> p = 20
	>>> h_terminal = 1
	>>> p_terminal = 20
	>>> c = 2
	>>> K = 0
	>>> mu = 100
	>>> sigma = 20
	>>> s, S, cost, _, _, _ = finite_horizon_dp(T, h, p, h_terminal, p_terminal, c, K, mu, sigma)
	>>> S # Order-up-to levels
	[0, 133.0, 133.0, 133.0, 133.0, 126.0]
	>>> s # Reorder points equal order-up-to levels in a base-stock policy
	[0, 133, 133, 133, 133, 126]

If the fixed costs are non-zero, then an |ss| policy is optimal, and the results
give both the reorder points (:math:`s`) and the order-up-to levels (:math:`S`)

.. doctest::

    >>> K = 50
    >>> s, S, cost, _, _, _ = finite_horizon_dp(T, h, p, h_terminal, p_terminal, c, K, mu, sigma)
    >>> s # Reorder points
    [0, 110, 110, 110, 110, 111]
    >>> S # Order-up-to levels
    [0, 133.0, 133.0, 133.0, 133.0, 126.0]