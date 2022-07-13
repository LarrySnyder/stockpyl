
|

**Deterministic Single-Echelon Inventory Problems**

.. collapse:: Example 3.1 (EOQ)

	| 
	| **Name:** ``example_3_1``
	| **Description:** Example 3.1 (EOQ)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_3_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			'fixed_cost': 8,
			'holding_cost': 0.225,
			'demand_rate': 1300
		}


.. collapse:: Problem 3.1 (EOQ)

	| 
	| **Name:** ``problem_3_1``
	| **Description:** Problem 3.1 (EOQ)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_3_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			'fixed_cost': 2250,
			'holding_cost': 275,
			'demand_rate': 182500
		}


.. collapse:: Example 3.8 (EOQB)

	| 
	| **Name:** ``example_3_8``
	| **Description:** Example 3.8 (EOQB)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_3_8')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			'fixed_cost': 8,
			'holding_cost': 0.225,
			'stockout_cost': 5,
			'demand_rate': 1300
		}


.. collapse:: Problem 3.2(b) (EOQB)

	| 
	| **Name:** ``problem_3_2b``
	| **Description:** Problem 3.2(b) (EOQB)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_3_2b')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			'fixed_cost': 40,
			'holding_cost': 40.05,
			'stockout_cost': 60,
			'demand_rate': 2080
		}


.. collapse:: Problem 3.22 (EPQ)

	| 
	| **Name:** ``problem_3_22``
	| **Description:** Problem 3.22 (EPQ)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_3_22')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			'fixed_cost': 4,
			'holding_cost': 0.08,
			'demand_rate': 80,
			'production_rate': 110
		}


.. collapse:: Example 3.9 (Wagner-Whitin)

	| 
	| **Name:** ``example_3_9``
	| **Description:** Example 3.9 (Wagner-Whitin)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_3_9')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"num_periods": 4,
			"holding_cost": 2,
			"fixed_cost": 500,
			"demand": [
				90,
				120,
				80,
				70
			]
		}


.. collapse:: Problem 3.27 (Wagner-Whitin)

	| 
	| **Name:** ``problem_3_27``
	| **Description:** Problem 3.27 (Wagner-Whitin)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_3_27')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"num_periods": 4,
			"holding_cost": 0.8,
			"fixed_cost": 120,
			"demand": [
				150,
				100,
				80,
				200
			]
		}


.. collapse:: Problem 3.29 (Wagner-Whitin)

	| 
	| **Name:** ``problem_3_29``
	| **Description:** Problem 3.29 (Wagner-Whitin)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_3_29')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"num_periods": 5,
			"holding_cost": 0.1,
			"fixed_cost": 100,
			"demand": [
				730,
				580,
				445,
				650,
				880
			]
		}


.. collapse:: SCMO (Wagner-Whitin with nonstationary purchase cost)

	| 
	| **Name:** ``scmo_ww_hw_c``
	| **Description:** SCMO (Wagner-Whitin with nonstationary purchase cost)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('scmo_ww_hw_c')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"num_periods": 5,
			"holding_cost": 0.1,
			"fixed_cost": 100,
			"demand": [
				400,
				500,
				500,
				1100,
				900
			],
			"purchase_cost": [
				3,
				1,
				4,
				6,
				6
			]
		}


.. collapse:: SCMO (JRP example)

	| 
	| **Name:** ``scmo_jrp_ex``
	| **Description:** SCMO (JRP example)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('scmo_jrp_ex')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"shared_fixed_cost": 600,
			"individual_fixed_costs": [
				120,
				840,
				300
			],
			"holding_costs": [
				160,
				20,
				50
			],
			"demand_rates": [
				1,
				1,
				1
			]
		}


.. collapse:: Numerical JRP on p. 428 of Silver, Pyke, and Peterson (1998)

	| 
	| **Name:** ``spp_jrp``
	| **Description:** Numerical JRP on p. 428 of Silver, Pyke, and Peterson (1998)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('spp_jrp')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"shared_fixed_cost": 40,
			"individual_fixed_costs": [
				15,
				15,
				15,
				15
			],
			"holding_costs": [
				0.24,
				0.24,
				0.24,
				0.24
			],
			"demand_rates": [
				86000,
				12500,
				1400,
				3000
			]
		}


.. collapse:: SCMO (JRP problem 1)

	| 
	| **Name:** ``scmo_jrp_hw_1``
	| **Description:** SCMO (JRP problem 1)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('scmo_jrp_hw_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"shared_fixed_cost": 20000,
			"individual_fixed_costs": [
				36000,
				46000,
				34000,
				38000
			],
			"holding_costs": [
				1000,
				900,
				1200,
				1000
			],
			"demand_rates": [
				1780,
				445,
				920,
				175
			]
		}


.. collapse:: SCMO (JRP problem 2)

	| 
	| **Name:** ``scmo_jrp_hw_2``
	| **Description:** SCMO (JRP problem 2)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('scmo_jrp_hw_2')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"shared_fixed_cost": 1500,
			"individual_fixed_costs": [
				4000,
				1000,
				2000
			],
			"holding_costs": [
				300,
				200,
				200
			],
			"demand_rates": [
				9100,
				83200,
				20800
			]
		}


.. collapse:: SCMO (JRP problem 3)

	| 
	| **Name:** ``scmo_jrp_hw_3``
	| **Description:** SCMO (JRP problem 3)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('scmo_jrp_hw_3')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"shared_fixed_cost": 180,
			"individual_fixed_costs": [
				60,
				100,
				180,
				115,
				135
			],
			"holding_costs": [
				5.32,
				3.9200000000000004,
				4.760000000000001,
				3.9200000000000004,
				3.3600000000000003
			],
			"demand_rates": [
				6200,
				1300,
				400,
				4400,
				1800
			]
		}


.. collapse:: Numerical JRP example in Silver (1976)

	| 
	| **Name:** ``silver_jrp``
	| **Description:** Numerical JRP example in Silver (1976)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('silver_jrp')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"shared_fixed_cost": 10,
			"individual_fixed_costs": [
				1.87,
				5.27,
				7.94,
				8.19,
				8.87
			],
			"holding_costs": [
				0.2,
				0.2,
				0.2,
				0.2,
				0.2
			],
			"demand_rates": [
				1736,
				656,
				558,
				170,
				142
			]
		}



|

**Stochastic Single-Echelon Inventory Problems**

.. collapse:: Example 4.1 (newsvendor)

	| 
	| **Name:** ``example_4_1``
	| **Description:** Example 4.1 (newsvendor)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_4_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.18,
			"stockout_cost": 0.7,
			"demand_mean": 50,
			"demand_sd": 8
		}


.. collapse:: Example 4.1 (newsvendor) (as SupplyChainNetwork object)

	| 
	| **Name:** ``example_4_1_network``
	| **Description:** Example 4.1 (newsvendor) (as SupplyChainNetwork object)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_4_1_network')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import single_stage_system
		instance = single_stage_system(
			holding_cost=0.18,
			stockout_cost=0.7,
			mean=50,
			standard_deviation=8
		)


.. collapse:: Example 4.2 (newsvendor explicit)

	| 
	| **Name:** ``example_4_2``
	| **Description:** Example 4.2 (newsvendor explicit)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_4_2')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"revenue": 1,
			"purchase_cost": 0.3,
			"salvage_value": 0.12,
			"demand_mean": 50,
			"demand_sd": 8
		}


.. collapse:: Example 4.3 (newsvendor) (= Example 4.1)

	| 
	| **Name:** ``example_4_3``
	| **Description:** Example 4.3 (newsvendor) (= Example 4.1)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_4_3')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.18,
			"stockout_cost": 0.7,
			"demand_mean": 50,
			"demand_sd": 8
		}


.. collapse:: Problem 4.1 (newsvendor)

	| 
	| **Name:** ``problem_4_1``
	| **Description:** Problem 4.1 (newsvendor)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 43,
			"stockout_cost": 79,
			"demand_mean": 900,
			"demand_sd": 60
		}


.. collapse:: Problem 4.3(b) (newsvendor explicit)

	| 
	| **Name:** ``problem_4_3b``
	| **Description:** Problem 4.3(b) (newsvendor explicit)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_3b')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"revenue": 7,
			"purchase_cost": 2.5,
			"salvage_value": 1.5,
			"demand_mean": 50,
			"demand_sd": 10
		}


.. collapse:: Example 4.4 (base-stock optimization)

	| 
	| **Name:** ``example_4_4``
	| **Description:** Example 4.4 (base-stock optimization)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_4_4')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.18,
			"stockout_cost": 0.7,
			"demand_mean": 50,
			"demand_sd": 8,
			"lead_time": 4
		}


.. collapse:: Example 4.7 ((s,S) with Poisson demand)

	| 
	| **Name:** ``example_4_7``
	| **Description:** Example 4.7 ((s,S) with Poisson demand)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_4_7')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 1,
			"stockout_cost": 4,
			"fixed_cost": 5,
			"demand_mean": 6
		}


.. collapse:: Problem 4.7(b) (newsvendor with discrete demand)

	| 
	| **Name:** ``problem_4_7b``
	| **Description:** Problem 4.7(b) (newsvendor with discrete demand)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_7b')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 500000,
			"stockout_cost": 1000000,
			"demand_pmf": {
				"1": 0.25,
				"2": 0.05,
				"3": 0.1,
				"4": 0.2,
				"5": 0.15,
				"6": 0.1,
				"7": 0.1,
				"8": 0.05
			}
		}


.. collapse:: Problem 4.8(a) (newsvendor with Poisson demand)

	| 
	| **Name:** ``problem_4_8a``
	| **Description:** Problem 4.8(a) (newsvendor with Poisson demand)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_8a')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 200,
			"stockout_cost": 270,
			"demand_mean": 18
		}


.. collapse:: Problem 4.8(b) (newsvendor with lognormal demand)

	| 
	| **Name:** ``problem_4_8b``
	| **Description:** Problem 4.8(b) (newsvendor with lognormal demand)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_8b')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 1,
			"stockout_cost": 0.1765,
			"mu": 6,
			"sigma": 0.3
		}


.. collapse:: Problem 4.31 ((s,S) with Poisson demand)

	| 
	| **Name:** ``problem_4_31``
	| **Description:** Problem 4.31 ((s,S) with Poisson demand)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_31')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 40,
			"stockout_cost": 125,
			"fixed_cost": 150,
			"demand_mean": 4
		}


.. collapse:: Example 4.8 ((s,S))

	| 
	| **Name:** ``example_4_8``
	| **Description:** Example 4.8 ((s,S))
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_4_8')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.18,
			"stockout_cost": 0.7,
			"fixed_cost": 2.5,
			"demand_mean": 50,
			"demand_sd": 8
		}


.. collapse:: Problem 4.32 ((s,S))

	| 
	| **Name:** ``problem_4_32``
	| **Description:** Problem 4.32 ((s,S))
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_32')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 2,
			"stockout_cost": 36,
			"fixed_cost": 60,
			"demand_mean": 190,
			"demand_sd": 48
		}


.. collapse:: Problem 4.29 (finite-horizon)

	| 
	| **Name:** ``problem_4_29``
	| **Description:** Problem 4.29 (finite-horizon)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_29')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"num_periods": 10,
			"holding_cost": 1,
			"stockout_cost": 25,
			"terminal_holding_cost": 1,
			"terminal_stockout_cost": 25,
			"purchase_cost": 1,
			"fixed_cost": 0,
			"demand_mean": 18,
			"demand_sd": 3,
			"discount_factor": 0.98,
			"initial_inventory_level": 0
		}


.. collapse:: Problem 4.30 (finite-horizon)

	| 
	| **Name:** ``problem_4_30``
	| **Description:** Problem 4.30 (finite-horizon)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_4_30')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"num_periods": 10,
			"holding_cost": 1,
			"stockout_cost": 25,
			"terminal_holding_cost": 1,
			"terminal_stockout_cost": 25,
			"purchase_cost": 1,
			"fixed_cost": 0,
			"demand_mean": 18,
			"demand_sd": 3,
			"discount_factor": 0.98,
			"initial_inventory_level": 0
		}


.. collapse:: Example 5.1 ((r,Q))

	| 
	| **Name:** ``example_5_1``
	| **Description:** Example 5.1 ((r,Q))
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_5_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.225,
			"stockout_cost": 7.5,
			"fixed_cost": 8,
			"demand_mean": 1300,
			"demand_sd": 150,
			"lead_time": 0.08333333333333333
		}


.. collapse:: Problem 5.1 ((r,Q))

	| 
	| **Name:** ``problem_5_1``
	| **Description:** Problem 5.1 ((r,Q))
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_5_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 3.1,
			"stockout_cost": 45,
			"fixed_cost": 50,
			"demand_mean": 800,
			"demand_sd": 40,
			"lead_time": 0.010958904109589041
		}


.. collapse:: Problem 5.2 ((r,Q) with Poisson demand)

	| 
	| **Name:** ``problem_5_2``
	| **Description:** Problem 5.2 ((r,Q) with Poisson demand)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_5_2')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 4,
			"stockout_cost": 28,
			"fixed_cost": 4,
			"demand_mean": 12,
			"lead_time": 0.5
		}


.. collapse:: Problem 5.3 ((r,Q))

	| 
	| **Name:** ``problem_5_3``
	| **Description:** Problem 5.3 ((r,Q))
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_5_3')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.21428571428571427,
			"stockout_cost": 40,
			"fixed_cost": 85,
			"demand_mean": 192,
			"demand_sd": 17.4,
			"lead_time": 3
		}


.. collapse:: Example 5.8 ((r,Q) with Poisson demand))

	| 
	| **Name:** ``example_5_8``
	| **Description:** Example 5.8 ((r,Q) with Poisson demand))
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_5_8')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 20,
			"stockout_cost": 150,
			"fixed_cost": 100,
			"demand_mean": 1.5,
			"lead_time": 2
		}


