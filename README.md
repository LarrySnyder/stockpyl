Stockpyl
========

![PyPI](https://img.shields.io/pypi/v/stockpyl)
[![Documentation Status](https://readthedocs.org/projects/stockpyl/badge/?version=latest)](https://stockpyl.readthedocs.io/en/latest/?badge=latest)<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="99" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="99" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="#97CA00" d="M63 0h36v20H63z"/>
        <path fill="url(#b)" d="M0 0h99v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="31.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
        <text x="31.5" y="14">coverage</text>
        <text x="80" y="15" fill="#010101" fill-opacity=".3">91%</text>
        <text x="80" y="14">91%</text>
    </g>
</svg>
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

