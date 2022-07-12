
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


