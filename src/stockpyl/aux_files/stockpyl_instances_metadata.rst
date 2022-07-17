
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


.. collapse:: Numerical JRP example on p. 428 of Silver, Pyke, and Peterson (1998)

	| 
	| **Name:** ``spp_jrp``
	| **Description:** Numerical JRP example on p. 428 of Silver, Pyke, and Peterson (1998)
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
			demand_type='N',
			mean=50,
			standard_deviation=8,
			shipment_lead_time=1,
			policy_type='BS',
			base_stock_level=56.6
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
			"fixed_cost": 40,
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



|

**Stochastic Multi-Echelon Inventory Problems**

.. collapse:: Example 6.1 (serial SSM)

	| 
	| **Name:** ``example_6_1``
	| **Description:** Example 6.1 (serial SSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_6_1')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=3,
			node_order_in_system=[3, 2, 1],
			echelon_holding_cost={1: 3, 2: 2, 3: 2},		
			local_holding_cost={1: 7, 2: 4, 3: 2},		
			shipment_lead_time={1: 1, 2: 1, 3: 2},	
			stockout_cost={1: 37.12, 2: 0, 3: 0},
			demand_type='N',
			mean=5,
			standard_deviation=1,
			policy_type='BS',
			base_stock_level={1: 6.49, 2: 5.53, 3: 10.69}
		)


.. collapse:: Problem 6.1 (serial SSM)

	| 
	| **Name:** ``problem_6_1``
	| **Description:** Problem 6.1 (serial SSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_1')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=2,
			node_order_in_system=[2, 1],
			node_order_in_lists=[1, 2],
			local_holding_cost=[2, 1],
			echelon_holding_cost=[1, 1],
			stockout_cost=[15, 0],
			demand_type='N',
			mean=100,
			standard_deviation=15,
			shipment_lead_time=[1, 1],
			policy_type='BS',
			base_stock_level=[100, 94]
		)


.. collapse:: Problem 6.2(a) (serial SSM)

	| 
	| **Name:** ``problem_6_2a``
	| **Description:** Problem 6.2(a) (serial SSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_2a')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=5,
			node_order_in_system=[5, 4, 3, 2, 1],
			node_order_in_lists=[1, 2, 3, 4, 5],
			local_holding_cost=[1, 2, 3, 5, 7],
			echelon_holding_cost=[2, 2, 1, 1, 1],
			stockout_cost=[24, 0, 0, 0, 0],
			demand_type='N',
			mean=64,
			standard_deviation=8,
			shipment_lead_time=[0.5, 0.5, 0.5, 0.5, 0.5],
			policy_type='BS',
			base_stock_level=[40.59, 33.87, 35.14, 33.30, 32.93]
		)


.. collapse:: Problem 6.2(a) (serial SSM with Poisson demand)

	| 
	| **Name:** ``problem_6_2b``
	| **Description:** Problem 6.2(a) (serial SSM with Poisson demand)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_2b')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=5,
			node_order_in_system=[5, 4, 3, 2, 1],
			node_order_in_lists=[1, 2, 3, 4, 5],
			local_holding_cost=[1, 2, 3, 5, 7],
			echelon_holding_cost=[2, 2, 1, 1, 1],
			stockout_cost=[24, 0, 0, 0, 0],
			demand_type='P',
			mean=64,
			shipment_lead_time=[0.5, 0.5, 0.5, 0.5, 0.5],
			policy_type='BS',
			base_stock_level=[40.59, 33.87, 35.14, 33.30, 32.93]
		)


.. collapse:: Problem 6.2(a) (serial SSM), adjusted for periodic review

	| 
	| **Name:** ``problem_6_2a_adj``
	| **Description:** Problem 6.2(a) (serial SSM), adjusted for periodic review
	| **Notes:** Since L=0.5 in Problem 6.2(a), here we treat each period as having length 0.5 in the original problem.
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_2a_adj')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		import numpy as np
		instance = serial_system(
			num_nodes=5,
			node_order_in_system=[5, 4, 3, 2, 1],
			node_order_in_lists=[1, 2, 3, 4, 5],
			local_holding_cost=list(np.array([1, 2, 3, 5, 7]) / 2),
			stockout_cost=list(np.array([24, 0, 0, 0, 0]) / 2),
			demand_type='N',
			mean=64 / 2,
			standard_deviation=8 / math.sqrt(2),
			shipment_lead_time=[1, 1, 1, 1, 1],
			policy_type='BS',
			base_stock_level=[40.59, 33.87, 35.14, 33.30, 32.93]
		)


.. collapse:: Problem 6.2(b) (serial SSM with Poisson demand), adjusted for periodic review

	| 
	| **Name:** ``problem_6_2b_adj``
	| **Description:** Problem 6.2(b) (serial SSM with Poisson demand), adjusted for periodic review
	| **Notes:** Since L=0.5 in Problem 6.2(b), here we treat each period as having length 0.5 in the original problem.
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_2b_adj')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		import numpy as np
		instance = serial_system(
			num_nodes=5,
			node_order_in_system=[5, 4, 3, 2, 1],
			node_order_in_lists=[1, 2, 3, 4, 5],
			local_holding_cost=list(np.array([1, 2, 3, 5, 7]) / 2),
			stockout_cost=list(np.array([24, 0, 0, 0, 0]) / 2),
			demand_type='P',
			mean=64 / 2,
			shipment_lead_time=[1, 1, 1, 1, 1],
			policy_type='BS',
			base_stock_level=[40.59, 33.87, 35.14, 33.30, 32.93]
		)


.. collapse:: Problem 6.16 (serial SSM)

	| 
	| **Name:** ``problem_6_16``
	| **Description:** Problem 6.16 (serial SSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_16')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=2,
			node_order_in_system=[2, 1],
			node_order_in_lists=[1, 2],
			local_holding_cost=[7, 2],
			echelon_holding_cost=[5, 2],
			stockout_cost=[24, 0],
			demand_type='N',
			mean=20,
			standard_deviation=4,
			shipment_lead_time=[8, 3],
			policy_type='BS',
			base_stock_level=[171.1912, 57.7257],
			initial_inventory_level=20,
			initial_orders=20,
			initial_shipments=20
		)


.. collapse:: Serial SSM system in Shang and Song (2003), Table 1, row 1

	| 
	| **Name:** ``shang_song_1``
	| **Description:** Serial SSM system in Shang and Song (2003), Table 1, row 1
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('shang_song_1')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=4,
			node_order_in_system=[4, 3, 2, 1],
			echelon_holding_cost=0.25,
			shipment_lead_time=0.25,
			stockout_cost={1: 9},
			demand_type='P',
			mean=16,
			policy_type='BS'
		)


.. collapse:: Serial SSM system in Shang and Song (2003), Table 1, row 9

	| 
	| **Name:** ``shang_song_9``
	| **Description:** Serial SSM system in Shang and Song (2003), Table 1, row 9
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('shang_song_9')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=4,
			node_order_in_system=[4, 3, 2, 1],
			node_order_in_lists=[1, 2, 3, 4],
			echelon_holding_cost=[0.25, 2.5, 2.5, 0.25],
			shipment_lead_time=0.25,
			stockout_cost={1: 9},
			demand_type='P',
			mean=16,
			policy_type='BS'
		)


.. collapse:: Serial SSM system in Shang and Song (2003), Table 1, row 17

	| 
	| **Name:** ``shang_song_17``
	| **Description:** Serial SSM system in Shang and Song (2003), Table 1, row 17
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('shang_song_17')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=4,
			node_order_in_system=[4, 3, 2, 1],
			echelon_holding_cost=0.25,
			shipment_lead_time=0.25,
			stockout_cost={1: 99},
			demand_type='P',
			mean=16,
			policy_type='BS'
		)


.. collapse:: Serial SSM system in Shang and Song (2003), Table 1, row 25

	| 
	| **Name:** ``shang_song_25``
	| **Description:** Serial SSM system in Shang and Song (2003), Table 1, row 25
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('shang_song_25')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import serial_system
		instance = serial_system(
			num_nodes=4,
			node_order_in_system=[4, 3, 2, 1],
			node_order_in_lists=[1, 2, 3, 4],
			echelon_holding_cost=[0.25, 2.5, 2.5, 0.25],
			shipment_lead_time=0.25,
			stockout_cost={1: 99},
			demand_type='P',
			mean=16,
			policy_type='BS'
		)


.. collapse:: 3-stage assembly system (2 warehouses, 1 retailer)

	| 
	| **Name:** ``assembly_3_stage``
	| **Description:** 3-stage assembly system (2 warehouses, 1 retailer)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('assembly_3_stage')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import mwor_system
		instance = mwor_system(
			num_warehouses=2,
			node_order_in_lists=[0, 1, 2],
			local_holding_cost=[2, 1, 1],
			stockout_cost=[20, 0, 0],
			demand_type='N',
			mean=5,
			standard_deviation=1,
			shipment_lead_time=[1, 2, 2],
			policy_type='BS',
			base_stock_level=[7, 13, 11],
			initial_inventory_level=[7, 13, 11]
		)
		instance.get_node_from_index(0).demand_source.round_to_int = True


.. collapse:: Assembly system from Figure 1 in Rosling (1989)

	| 
	| **Name:** ``rosling_figure_1``
	| **Description:** Assembly system from Figure 1 in Rosling (1989)
	| **Notes:** Structure and lead times are from Rosling; all other parameters are made up.
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('rosling_figure_1')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import SupplyChainNetwork
		from stockpyl.supply_chain_node import SupplyChainNode
		from stockpyl.demand_source import DemandSource
		instance = SupplyChainNetwork()
		nodes = {i: SupplyChainNode(index=i) for i in range(1, 8)}
		# Inventory policies (balanced echelon base-stock).
		for n in nodes.values():
			n.inventory_policy.type = 'BEBS'
			n.inventory_policy.base_stock_level = None
		# Node 1.
		nodes[1].shipment_lead_time = 1
		nodes[1].demand_source = DemandSource(type='UD', lo=0, hi=10)
		nodes[1].supply_type = None
		nodes[1].inventory_policy.base_stock_level = 8
		nodes[1].initial_inventory_level = 8
		instance.add_node(nodes[1])
		# Node 2.
		nodes[2].shipment_lead_time = 1
		nodes[2].supply_type = None
		nodes[2].inventory_policy.base_stock_level = 24
		nodes[2].initial_inventory_level = 8
		instance.add_predecessor(nodes[1], nodes[2])
		# Node 3.
		nodes[3].shipment_lead_time = 3
		nodes[3].supply_type = None
		nodes[3].inventory_policy.base_stock_level = 40
		nodes[3].initial_inventory_level = 24
		instance.add_predecessor(nodes[1], nodes[3])
		# Node 4.
		nodes[4].shipment_lead_time = 2
		nodes[4].supply_type = None
		nodes[4].inventory_policy.base_stock_level = 76
		nodes[4].initial_inventory_level = 16
		instance.add_predecessor(nodes[3], nodes[4])
		# Node 5.
		nodes[5].shipment_lead_time = 4
		nodes[5].inventory_policy.base_stock_level = 62
		nodes[5].initial_inventory_level = 32
		nodes[5].supply_type = 'U'
		instance.add_predecessor(nodes[2], nodes[5])
		# Node 6.
		nodes[6].shipment_lead_time = 1
		nodes[6].supply_type = 'U'
		nodes[6].inventory_policy.base_stock_level = 84
		nodes[6].initial_inventory_level = 8
		instance.add_predecessor(nodes[4], nodes[6])
		# Node 7.
		nodes[7].shipment_lead_time = 2
		nodes[7].supply_type = 'U'
		nodes[7].inventory_policy.base_stock_level = 92
		nodes[7].initial_inventory_level = 16
		instance.add_predecessor(nodes[4], nodes[7])


.. collapse:: Distribution system from Figure 1(a) in Rong, Atan, and Snyder (2017)

	| 
	| **Name:** ``rong_atan_snyder_figure_1a``
	| **Description:** Distribution system from Figure 1(a) in Rong, Atan, and Snyder (2017)
	| **Notes:** Uses normal demand instead of Poisson.
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('rong_atan_snyder_figure_1a')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import network_from_edges
		from math import sqrt
		instance = network_from_edges(
			edges=[(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)],
			demand_type={0: None, 1: None, 2: None, 3: 'N', 4: 'N', 5: 'N', 6: 'N'},
			mean=8,
			standard_deviation=sqrt(8),
			local_holding_cost={0: 1/3, 1: 2/3, 2: 2/3, 3: 1, 4: 1, 5: 1, 6: 1},
			stockout_cost=20,
			shipment_lead_time=1,
			policy_type='BS',
			base_stock_level={i: 0 for i in range(0, 7)}
		)


.. collapse:: Distribution system from Figure 1(b) in Rong, Atan, and Snyder (2017)

	| 
	| **Name:** ``rong_atan_snyder_figure_1b``
	| **Description:** Distribution system from Figure 1(b) in Rong, Atan, and Snyder (2017)
	| **Notes:** Uses normal demand instead of Poisson. Cost and lead times are omitted.
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('rong_atan_snyder_figure_1b')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import network_from_edges
		from math import sqrt
		demand_type = {i: 'N' if i >= 3 else None for i in range(11)}
		instance = network_from_edges(
			edges=[(0, 1), (0, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, 8), (2, 9), (2, 10)],
			demand_type=demand_type,
			mean=8,
			standard_deviation=sqrt(8),
			policy_type='BS',
			base_stock_level={i: 0 for i in range(0, 11)}
		)


.. collapse:: Distribution system from Figure 1(c) in Rong, Atan, and Snyder (2017)

	| 
	| **Name:** ``rong_atan_snyder_figure_1c``
	| **Description:** Distribution system from Figure 1(c) in Rong, Atan, and Snyder (2017)
	| **Notes:** Uses normal demand instead of Poisson. Cost and lead times are omitted.
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('rong_atan_snyder_figure_1c')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import network_from_edges
		from math import sqrt
		instance = network_from_edges(
			edges=[(0, 1), (0, 2), (2, 3), (2, 4), (2, 5)],
			demand_type={0: None, 1: 'N', 2: None, 3: 'N', 4: 'N', 5: 'N'},
			mean=8,
			standard_deviation=sqrt(8),
			policy_type='BS',
			base_stock_level={i: 0 for i in range(0, 6)}
		)


.. collapse:: Example 6.3 (serial GSM)

	| 
	| **Name:** ``example_6_3``
	| **Description:** Example 6.3 (serial GSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_6_3')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import network_from_edges
		instance = network_from_edges(
			edges=[(3, 2), (2, 1)], 
			node_order_in_lists=[1, 2, 3],
			processing_time=[1, 0, 1],
			external_inbound_cst=[None, None, 1],
			local_holding_cost=[7, 4, 2],
			demand_bound_constant=1,
			external_outbound_cst=[1, None, None],
			demand_type=['N', None, None],
			mean=0,
			standard_deviation=[1, 0, 0]
		)


.. collapse:: Problem 6.7 (serial GSM)

	| 
	| **Name:** ``problem_6_7``
	| **Description:** Problem 6.7 (serial GSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_7')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import SupplyChainNetwork
		from stockpyl.supply_chain_node import SupplyChainNode
		from stockpyl.demand_source import DemandSource
		instance = SupplyChainNetwork()
		instance.add_node(SupplyChainNode(3, name='Forming', network=instance, processing_time=1, local_holding_cost=2, external_inbound_cst=1, demand_bound_constant=4))
		instance.add_node(SupplyChainNode(2, name='Firing', network=instance, processing_time=1, local_holding_cost=3, demand_bound_constant=4))
		instance.add_node(SupplyChainNode(1, name='Glazing', network=instance, processing_time=2, local_holding_cost=4, external_outbound_cst=0, demand_source=DemandSource(type='N', mean=45, standard_deviation=10), demand_bound_constant=4))
		instance.add_edges_from_list([(3, 2), (2, 1)])


.. collapse:: Problem 6.8 (serial GSM)

	| 
	| **Name:** ``problem_6_8``
	| **Description:** Problem 6.8 (serial GSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_8')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import network_from_edges
		from scipy import stats
		instance = network_from_edges(
			[(n+1, n) for n in range(1, 10)], 
			node_order_in_lists=list(range(1, 11)),
			processing_time=[5, 10, 2, 15, 8, 5, 9, 5, 1, 5],
			external_inbound_cst=[None] * 9 + [7],
			local_holding_cost=[5.73, 4.56, 3.04, 2.93, 2.47, 2.37, 1.15, 1.1, 0.98, 0.87],
			demand_bound_constant=stats.norm.ppf(0.98),
			external_outbound_cst=[3] + [None] * 9,
			demand_type=['N'] + [None] * 9,
			mean=0,
			standard_deviation=[15.8] + [None] * 9
		)


.. collapse:: Problem 6.9 (tree GSM)

	| 
	| **Name:** ``problem_6_9``
	| **Description:** Problem 6.9 (tree GSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_6_9')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import SupplyChainNetwork
		from stockpyl.supply_chain_node import SupplyChainNode
		from stockpyl.demand_source import DemandSource
		instance = SupplyChainNetwork()
		instance.add_node(SupplyChainNode(1, network=instance, processing_time=7, local_holding_cost=220*0.2/365, external_outbound_cst=3, demand_source=DemandSource(type='N', mean=22.0, standard_deviation=4.1), demand_bound_constant=4))
		instance.add_node(SupplyChainNode(2, network=instance, processing_time=7, local_holding_cost=140*0.2/365, external_outbound_cst=3, demand_source=DemandSource(type='N', mean=15.3, standard_deviation=6.2), demand_bound_constant=4))
		instance.add_node(SupplyChainNode(3, network=instance, processing_time=21, local_holding_cost=90*0.2/365, demand_bound_constant=4))
		instance.add_node(SupplyChainNode(4, network=instance, processing_time=3, local_holding_cost=5*0.2/365, demand_bound_constant=4))
		instance.add_node(SupplyChainNode(5, network=instance, processing_time=8, local_holding_cost=20*0.2/365, demand_bound_constant=4))
		instance.add_node(SupplyChainNode(6, network=instance, processing_time=2, local_holding_cost=7.5*0.2/365, demand_bound_constant=4))
		instance.add_edges_from_list([(6, 5), (4, 3), (5, 3), (3, 1), (3, 2)])


.. collapse:: Example 6.5 (tree GSM)

	| 
	| **Name:** ``example_6_5``
	| **Description:** Example 6.5 (tree GSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_6_5')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import network_from_edges
		instance = network_from_edges(
			edges=[(1, 3), (3, 2), (3, 4)], 
			node_order_in_lists=[1, 2, 3, 4],
			processing_time=[2, 1, 1, 1],
			external_inbound_cst=[1, None, None, None],
			local_holding_cost=[1, 3, 2, 3],
			demand_bound_constant=[1, 1, 1, 1],
			external_outbound_cst=[None, 0, None, 1],
			demand_type=[None, 'N', None, 'N'],
			mean=[None, 0, None, 0],
			standard_deviation=[None, 1, None, 1]
		)


.. collapse:: Figure 6.12 (tree GSM)

	| 
	| **Name:** ``figure_6_12``
	| **Description:** Figure 6.12 (tree GSM)
	| **Notes:** This instance only consists of the network structure, no costs or other parameters.
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('figure_6_12')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import network_from_edges
		instance = network_from_edges(
			edges=[(1, 2), (1, 3), (3, 5), (4, 5), (5, 6), (5, 7)]
		)


.. collapse:: Figure 6.14 (tree GSM)

	| 
	| **Name:** ``figure_6_14``
	| **Description:** Figure 6.14 (tree GSM)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('figure_6_14')

	| **Code to Build Manually:**

	.. code-block:: python

		from stockpyl.supply_chain_network import SupplyChainNetwork
		from stockpyl.supply_chain_node import SupplyChainNode
		from stockpyl.demand_source import DemandSource
		from scipy import stats
		instance = SupplyChainNetwork()
		instance.add_node(SupplyChainNode(1, 'Raw_Material', instance, processing_time=2, local_holding_cost=0.01))
		instance.add_node(SupplyChainNode(2, 'Process_Wafers', instance, processing_time=3, local_holding_cost=0.03))
		instance.add_node(SupplyChainNode(3, 'Package_Test_Wafers', instance, processing_time=2, local_holding_cost=0.04))
		instance.add_node(SupplyChainNode(4, 'Imager_Base', instance, processing_time=4, local_holding_cost=0.06))
		instance.add_node(SupplyChainNode(5, 'Imager_Assembly', instance, processing_time=2, local_holding_cost=0.12))
		instance.add_node(SupplyChainNode(6, 'Ship_to_Final_Assembly', instance, processing_time=3, local_holding_cost=0.13))
		instance.add_node(SupplyChainNode(7, 'Camera', instance, processing_time=6, local_holding_cost=0.20))
		instance.add_node(SupplyChainNode(8, 'Circuit_Board', instance, processing_time=4, local_holding_cost=0.08))
		instance.add_node(SupplyChainNode(9, 'Other_Parts', instance, processing_time=3, local_holding_cost=0.04))
		instance.add_node(SupplyChainNode(10, 'Build_Test_Pack', instance, processing_time=2, local_holding_cost=0.50, \
			external_outbound_cst=2, demand_source=DemandSource(type='N', mean=0, standard_deviation=10)))
		for n in instance.nodes:
			n.demand_bound_constant = stats.norm.ppf(0.95)
		instance.add_edges_from_list([(1, 2), (2, 3), (3, 5), (4, 5), (5, 6), (7, 10), (6, 10), (8, 10), (9, 10)])



|

**Single-Echelon Inventory Problems with Supply Uncertainty**

.. collapse:: Example 9.1 (EOQD)

	| 
	| **Name:** ``example_9_1``
	| **Description:** Example 9.1 (EOQD)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_9_1')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.225,
			"stockout_cost": 5,
			"fixed_cost": 8,
			"demand_rate": 1300,
			"disruption_rate": 1.5,
			"recovery_rate": 14
		}


.. collapse:: Problem 9.8 (EOQD)

	| 
	| **Name:** ``problem_9_8``
	| **Description:** Problem 9.8 (EOQD)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_9_8')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 4,
			"stockout_cost": 22,
			"fixed_cost": 35,
			"demand_rate": 30,
			"disruption_rate": 1,
			"recovery_rate": 12
		}


.. collapse:: Example 9.3 (base-stock with disruptions)

	| 
	| **Name:** ``example_9_3``
	| **Description:** Example 9.3 (base-stock with disruptions)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_9_3')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.25,
			"stockout_cost": 3,
			"demand": 2000,
			"disruption_prob": 0.04,
			"recovery_prob": 0.25
		}


.. collapse:: Example 9.4 (EOQ with additive yield uncertainty)

	| 
	| **Name:** ``example_9_4``
	| **Description:** Example 9.4 (EOQ with additive yield uncertainty)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_9_4')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.06,
			"fixed_cost": 18500,
			"demand_rate": 75000,
			"yield_mean": -15000,
			"yield_sd": 9000
		}


.. collapse:: Example 9.5 (EOQ with multiplicative yield uncertainty)

	| 
	| **Name:** ``example_9_5``
	| **Description:** Example 9.5 (EOQ with multiplicative yield uncertainty)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_9_5')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 0.06,
			"fixed_cost": 18500,
			"demand_rate": 75000,
			"yield_mean": 0.8333333333333334,
			"yield_sd": 0.14085904245475275
		}


.. collapse:: Problem 9.4(a) (EOQ with additive yield uncertainty)

	| 
	| **Name:** ``problem_9_4a``
	| **Description:** Problem 9.4(a) (EOQ with additive yield uncertainty)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_9_4a')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 275,
			"fixed_cost": 2250,
			"demand_rate": 182500,
			"yield_mean": -50.0,
			"yield_sd": 0.02
		}


.. collapse:: Problem 9.4(b) (EOQ with multiplicative yield uncertainty)

	| 
	| **Name:** ``problem_9_4b``
	| **Description:** Problem 9.4(b) (EOQ with multiplicative yield uncertainty)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_9_4b')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 275,
			"fixed_cost": 2250,
			"demand_rate": 182500,
			"yield_mean": 0.9,
			"yield_sd": 0.05773502691896258	
		}


.. collapse:: Example 9.6 (newsvendor with additive yield uncertainty)

	| 
	| **Name:** ``example_9_6``
	| **Description:** Example 9.6 (newsvendor with additive yield uncertainty)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('example_9_6')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 15000000,
			"stockout_cost": 75000000,
			"demand": 1.5,
			"yield_lo": -0.5,
			"yield_hi": 0.5
		}


.. collapse:: Problem 9.5 (newsvendor with additive yield uncertainty)

	| 
	| **Name:** ``problem_9_5``
	| **Description:** Problem 9.5 (newsvendor with additive yield uncertainty)
	| **Code to Load Instance:**

	.. code-block:: python

		instance = load_instance('problem_9_5')

	| **Code to Build Manually:**

	.. code-block:: python

		instance = {
			"holding_cost": 150,
			"stockout_cost": 1200,
			"demand": 25,
			"yield_lo": -5,
			"yield_hi": 0
		}


