.. include:: ../globals.inc

.. _tutorial_su_page:

Supply Uncertainty
============================

|sp| contains code to solve the following types of single-echelon inventory optimization problems
in the |mod_supply_uncertainty| module:

- Economic order quantity (EOQ)-based models
	- with disruptions
	- with additive and multiplicative yield uncertainty
- Newsvendor-based models
	- with disruptions
	- with additive yield uncertainty

The notation and references (equations, sections, examples, etc.) used below
refer to Snyder and Shen, *Fundamentals of Supply Chain Theory* (|fosct|), 2nd edition
(2019).

.. contents::
    :depth: 2

The EOQ Problem with Disruptions
--------------------------------

The EOQ problem with disruptions (EOQD) assumes that the supplier can be disrupted
randomly, following a 2-state Markov process. The :func:`eoq_with_disruptions` function
solves the EOQD either exactly (using models by Parlar and Berkin (1991) and Berk and Arreola-Risa (1994)
and optimizing numerically) or heuristically (using an approximation by Snyder (2014)).

.. doctest::

	>>> from stockpyl.supply_uncertainty import eoq_with_disruptions
	>>> K = 8
	>>> h = 0.225
	>>> p = 5
	>>> demand_rate = 1300
	>>> disruption_rate = 1.5
	>>> recovery_rate = 14
	>>> Q, cost = eoq_with_disruptions(K, h, p, demand_rate, disruption_rate, recovery_rate)
	>>> Q
	772.8110739983106
	>>> cost
	173.95000257319708
	>>> Q, cost = eoq_with_disruptions(K, h, p, demand_rate, disruption_rate, recovery_rate, approximate=True)
	>>> Q
	773.1432417118889
	>>> cost
	173.957229385175


The EOQ Problem with Yield Uncertainty
--------------------------------------

In EOQ problems with yield uncertainty, the supplier can always provide inventory, but
the quantity delivered differs randomly from the quantity ordered. |sp| supports both 
additive yield uncertainty:

.. doctest::

	>>> from stockpyl.supply_uncertainty import eoq_with_additive_yield_uncertainty
	>>> K = 18500
	>>> h = 0.06
	>>> demand_rate = 75000
	>>> yield_mean = -15000
	>>> yield_sd = 9000
	>>> Q, cost = eoq_with_additive_yield_uncertainty(K, h, demand_rate, yield_mean, yield_sd)
	>>> Q
	230246.37046881882
	>>> cost
	12914.78222812913

and multiplicative yield uncertainty:

.. doctest::

	>>> from stockpyl.supply_uncertainty import eoq_with_multiplicative_yield_uncertainty
	>>> from math import sqrt
	>>> yield_mean = 0.8333
	>>> yield_sd = sqrt(0.0198)
	>>> Q, cost = eoq_with_multiplicative_yield_uncertainty(K, h, demand_rate, yield_mean, yield_sd)
	>>> Q
	254477.46130342316
	>>> cost
	13086.16169098594


The Newsvendor Problem with Disruptions
---------------------------------------

In the newsvendor (or base-stock) problem with disruptions, the demand is deterministic but the supply
can be disrupted, following a 2-state Markov process. The :func:`newsvendor_with_disruptions` function
returns both the optimal base-stock level and the optimal expected cost.

.. doctest::

	>>> from stockpyl.supply_uncertainty import newsvendor_with_disruptions
	>>> h = 0.25
	>>> p = 3
	>>> d = 2000
	>>> alpha = 0.04
	>>> beta = 0.25
	>>> S, cost = newsvendor_with_disruptions(h, p, d, alpha, beta)
	>>> S
	8000
	>>> cost
	2737.0689302470355


The Newsvendor Problem with Yield Uncertainty
---------------------------------------------

In newsvendor problems with yield uncertainty, the supplier can always provide inventory, but
the quantity delivered differs randomly from the quantity ordered. |sp| currently supports only 
additive yield uncertainty:

.. doctest::

	>>> from stockpyl.supply_uncertainty import newsvendor_with_additive_yield_uncertainty
	>>> h = 15
	>>> p = 75
	>>> d = 1500000
	>>> yield_mean = 250000
	>>> yield_sd = 200000
	>>> S, cost = newsvendor_with_additive_yield_uncertainty(h, p, d, yield_mean, yield_sd)
	>>> S
	1443484.3132203403
	>>> cost
	4497316.9310527835

If the yield mean and standard deviation are provided, as in the code above, the
yield is assumed to have a normal distribution. Alternately, you can provide an arbitrary
distribution as a ``scipy.stats.rv_continuous`` or ``scipy.stats.rv_discrete`` object:

.. doctest::

	>>> from scipy.stats import uniform
	>>> newsvendor_with_additive_yield_uncertainty(h, p, d, yield_distribution=uniform(-500000, 1000000))
	(1833333.3333333335, 6249999.997499999)