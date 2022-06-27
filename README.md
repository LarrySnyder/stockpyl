Stockpyl
========

![PyPI](https://img.shields.io/pypi/v/stockpyl)
[![Documentation Status](https://readthedocs.org/projects/stockpyl/badge/?version=latest)](https://stockpyl.readthedocs.io/en/latest/?badge=latest)
![Coverage](https://raw.githubusercontent.com/LarrySnyder/stockpyl/master/coverage_badge.svg)
![GitHub](https://img.shields.io/github/license/LarrySnyder/stockpyl)
![GitHub issues](https://img.shields.io/github/issues/LarrySnyder/stockpyl)
![Twitter Follow](https://img.shields.io/twitter/follow/LarrySnyder610?style=flat)

Stockpyl is a Python package for inventory optimization. It implements
classical single-node inventory models like the economic order quantity (EOQ), newsvendor,
and Wagner-Whitin problems. It also contains algorithms for multi-echelon inventory optimization
(MEIO) under both stochastic-service model (SSM) and guaranteed-service model (GSM) assumptions. 

Most of the models and algorithms implemented in Stockpyl are discussed in the textbook
*Fundamentals of Supply Chain Theory* (*FoSCT*) by Snyder and Shen, Wiley, 2019, 2nd ed. Most of them
are much older; see *FoSCT* for references to original sources. 

For lots of details, [read the docs](http://stockpyl.readthedocs.io/).

Some Examples
-------------

Solve the newsvendor problem with a holding (overage) cost of 2, a stockout (underage) cost of 18, and 
demands that are normally distributed with a mean of 120 and a standard deviation of 10:

```python
>>> from stockpyl.newsvendor import newsvendor_normal
>>> S, cost = newsvendor_normal(holding_cost=2, stockout_cost=18, demand_mean=120, demand_sd=10)
>>> S
132.815515655446
>>> cost
35.09966638649737
```

Use Chen and Zheng's (1994) algorithm (based on Clark and Scarf (1960)) to optimize a 3-node serial system under
the stochastic-service model (SSM):

```python
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
>>> print(f"S_star = {S_star}, C_star = {C_star}")
S_star = {3: 44.1689463285519, 2: 34.93248526934437, 1: 25.69602421013684}, C_star = 227.15328525645054
```

Simulate the same system using the optimal base-stock levels:

```python
>>> from stockpyl.supply_chain_network import echelon_to_local_base_stock_levels
>>> from stockpyl.sim import simulation
>>> from stockpyl.policy import Policy
>>> # Convert to local base-stock levels and set nodes' inventory policies.
>>> S_star_local = echelon_to_local_base_stock_levels(network, S_star)
>>> for n in network.nodes:
...     n.inventory_policy = Policy(type='BS', base_stock_level=S_star_local[n.index], node=n)
>>> # Simulate the system.
>>> T = 1000
>>> total_cost = simulation(network=network, num_periods=T)
>>> print(f"Average total cost per period = {total_cost/T}")
Average total cost per period = 224.98879893564296
```


Optimize committed service times (CSTs) for a tree network under the guaranteed-service model (GSM) 
using Graves and Willems' (2000) dynamic programming algorithm:

```python
>>> from stockpyl.gsm_tree import optimize_committed_service_times
>>> from stockpyl.instances import load_instance
>>> # Load a named instance, Example 6.5 from FoSCT.
>>> tree = load_instance("example_6_5")
>>> opt_cst, opt_cost = optimize_committed_service_times(tree)
>>> opt_cst
{1: 0, 3: 0, 2: 0, 4: 1}
>>> opt_cost
8.277916867529369
```



Resources
---------

* [PyPI](https://pypi.org/project/stockpyl/)
* [Documentation](http://stockpyl.readthedocs.io/)
* [Issue tracking](https://github.com/LarrySnyder/stockpyl/issues)

Feedback
--------

If you have feedback or encounter problems, please report them on the Stockpyl GitHub
[Issues Page](https://github.com/LarrySnyder/stockpyl/issues). (If you are not comfortable
using GitHub for this purpose, feel free to e-mail me. My contact info is on [my webpage](https://coral.ise.lehigh.edu/larry/).)

License
-------

Stockpyl is open-source and released under the [GPLv3 License](https://choosealicense.com/licenses/gpl-3.0/).

Citation
--------

If you'd like to cite the Stockpyl package, you can use the following BibTeX entry:

```bibtex
@misc{stockpyl,
    title={Stockpyl},
    author={Snyder, Lawrence V.},
    year={2022},
    url={https://github.com/LarrySnyder/stockpyl}
}
```

