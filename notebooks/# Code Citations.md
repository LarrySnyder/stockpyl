# Code Citations

## License: GPL-3.0
https://github.com/LarrySnyder/stockpyl/blob/23355350ebff114f8f04194f066ab8018e3475f0/README.rst

```
service times (CSTs) for a tree network under the guaranteed-service model (GSM) 
using Graves and Willems' (2000) dynamic programming algorithm:

```python
>>> from stockpyl.gsm_tree import optimize_committed_service_times
>>> from stockpyl.instances import load_instance
>>> # Load a named instance, Example 6.5 from FoSCT.
>>> tree = load_instance("example_6_5")
>>> opt_cst, opt_cost = optimize_committed_service_times(tree)
>>> opt_cst
{1: 0, 3: 0, 2: 0, 4: 1}
>>>
```


## License: GPL-3.0
https://github.com/LarrySnyder/stockpyl/blob/23355350ebff114f8f04194f066ab8018e3475f0/README.md

```
service times (CSTs) for a tree network under the guaranteed-service model (GSM) 
using Graves and Willems' (2000) dynamic programming algorithm:

```python
>>> from stockpyl.gsm_tree import optimize_committed_service_times
>>> from stockpyl.instances import load_instance
>>> # Load a named instance, Example 6.5 from FoSCT.
>>> tree = load_instance("example_6_5")
>>> opt_cst, opt_cost = optimize_committed_service_times(tree)
>>> opt_cst
{1: 0, 3: 0, 2: 0, 4: 1}
>>>
```

