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

For a tutorial, see Snyder, L. V., "[Stockpyl: A Python Package for Inventory Optimization and Simulation](https://pubsonline.informs.org/doi/10.1287/educ.2023.0256)," in: Bish, E. K. and H. Balasubramanian, INFORMS TutORials in Operations Research, 156–197, 2023. The associated Jupyter notebooks are at [`notebooks/`](https://github.com/LarrySnyder/stockpyl/blob/c41103ca2055138f8f9844d29b3ab8ac67c847d5/notebooks).

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
>>> from stockpyl.ssm_serial import optimize_base_stock_levels
>>> S_star, C_star = optimize_base_stock_levels(
...     num_nodes=3,
...     echelon_holding_cost=[4, 3, 1],
...     lead_time=[1, 1, 2],
...     stockout_cost=40,
...     demand_mean=10,
...     demand_standard_deviation=2
... )
>>> S_star
{1: 12.764978727246302, 2: 23.49686681508743, 3: 46.28013742779933}
>>> C_star
86.02533221942987
```

Simulate the same system using the optimal base-stock levels:



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

Stockpyl is open-source and released under the [MIT License](https://choosealicense.com/licenses/mit/).

Citation
--------

If you'd like to cite the Stockpyl package, you can use the following BibTeX entry:

```bibtex
@misc{stockpyl,
    title={Stockpyl},
    author={Snyder, Lawrence V.},
    year={2023},
    url={https://github.com/LarrySnyder/stockpyl}
}
```

