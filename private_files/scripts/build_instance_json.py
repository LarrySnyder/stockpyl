import sys
import copy

sys.path.append('/Users/larry/Documents/GitHub/stockpyl')
# print(sys.path)

#from ...stockpyl.instances import *

# import os

# print(os.getcwd())

from stockpyl.instances import *


def get_named_instance(instance_name):
	"""Return the named instance specified by ``instance_name``. Return
	variables depend on the instance.

	Parameters
	----------
	instance_name : str
		The instance name. See method code for allowable strings.

	"""

	# CHAPTER 3
	if instance_name == "example_3_1":
		# Example 3.1.
		fixed_cost = 8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		return fixed_cost, holding_cost, demand_rate
	elif instance_name == "problem_3_1":
		# Problem 3.1.
		fixed_cost = 2250
		holding_cost = 275
		demand_rate = 500 * 365
		return fixed_cost, holding_cost, demand_rate
	elif instance_name == "example_3_8":
		# Example 3.8.
		fixed_cost = 8
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		return fixed_cost, holding_cost, stockout_cost, demand_rate
	elif instance_name == "problem_3_2b":
		# Problem 3.2(b).
		fixed_cost = 40
		holding_cost = (165 * 0.17 + 12)
		stockout_cost = 60
		demand_rate = 40 * 52
		return fixed_cost, holding_cost, stockout_cost, demand_rate
	elif instance_name == "problem_3_22":
		# Problem 3.22.
		fixed_cost = 4
		holding_cost = 0.08
		demand_rate = 80
		production_rate = 110
		return fixed_cost, holding_cost, demand_rate, production_rate
	elif instance_name == "example_3_9":
		# Example 3.9 (Wagner-Whitin).
		num_periods = 4
		holding_cost = 2
		fixed_cost = 500
		demand = [90, 120, 80, 70]
		return num_periods, holding_cost, fixed_cost, demand
	elif instance_name == "problem_3_27":
		# Problem 3.27.
		num_periods = 4
		holding_cost = 0.8
		fixed_cost = 120
		demand = [150, 100, 80, 200]
		return num_periods, holding_cost, fixed_cost, demand
	elif instance_name == "problem_3_29":
		# Problem 3.29.
		num_periods = 5
		holding_cost = 0.1
		fixed_cost = 100
		demand = [730, 580, 445, 650, 880]
		return num_periods, holding_cost, fixed_cost, demand
	elif instance_name == "ww_hw_c":
		# SCMO HW problem for WW with nonstationary purchase cost.
		num_periods = 5
		holding_cost = 0.1
		fixed_cost = 100
		demand = [400, 500, 500, 1100, 900]
		purchase_cost = [3, 1, 4, 6, 6]
		return num_periods, holding_cost, fixed_cost, demand, purchase_cost
	elif instance_name == "jrp_ex":
		# JRP example in SCMO.
		shared_fixed_cost = 600
		individual_fixed_costs = [120, 840, 300]
		holding_costs = [160, 20, 50]
		demand_rates = [1, 1, 1]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_hw_1":
		# JRP HW 1 (paper)
		shared_fixed_cost = 20000
		individual_fixed_costs = [36000, 46000, 34000, 38000]
		holding_costs = [1000, 900, 1200, 1000]
		demand_rates = [1780, 445, 920, 175]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_hw_2":
		# JRP HW 2 (construction)
		shared_fixed_cost = 1500
		individual_fixed_costs = [4000, 1000, 2000]
		holding_costs = [300, 200, 200]
		demand_rates_week = [175, 1600, 400]
		demand_rates = (52 * np.array(demand_rates_week)).tolist()
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_hw_3":
		# JRP HW 3 (books)
		shared_fixed_cost = 180
		individual_fixed_costs = [60, 100, 180, 115, 135]
		purchase_costs = [19, 14, 17, 14, 12]
		holding_costs = (0.28 * np.array(purchase_costs)).tolist()
		demand_rates = [6200, 1300, 400, 4400, 1800]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_silver":
		# Numerical example in Silver (1976).
		shared_fixed_cost = 10
		individual_fixed_costs = [1.87, 5.27, 7.94, 8.19, 8.87]
		holding_costs = [0.2] * 5
		demand_rates = [1736, 656, 558, 170, 142]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_spp":
		# Example on p. 428 of Silver, Pyke, and Peterson (1998).
		shared_fixed_cost = 40
		individual_fixed_costs = [15, 15, 15, 15]
		holding_costs = [0.24] * 4
		demand_rates = [86000, 12500, 1400, 3000]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates



	# CHAPTER 4
	if instance_name == "example_4_1_network":
		# Example 4.1 (newsvendor), as SupplyChainNetwork object.
		example_4_1_network = serial_system(
			num_nodes=1,
			local_holding_cost=[0.18],
			stockout_cost=[0.70],
			demand_type='N',
			demand_mean=50,
			demand_standard_deviation=8,
			shipment_lead_time=[1],
			inventory_policy_type='BS',
			base_stock_levels=[56.6]
		)
		return example_4_1_network
	elif instance_name == "example_4_1":
		# Example 4.1 (newsvendor).
		holding_cost = 0.18
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		return holding_cost, stockout_cost, demand_mean, demand_sd
	elif instance_name == "example_4_2":
		# Example 4.2 (newsvendor explicit).
		selling_revenue = 1
		purchase_cost = 0.3
		salvage_value = 0.12
		demand_mean = 50
		demand_sd = 8
		return selling_revenue, purchase_cost, salvage_value, demand_mean, demand_sd
	elif instance_name == "example_4_2_network":
		# Example 4.2 (newsvendo rexplicit), as SupplyChainNetwork object.
		example_4_2_network = serial_system(
			num_nodes=1,
			local_holding_cost=[0.18],
			stockout_cost=[0.70],
			demand_type='N',
			demand_mean=50,
			demand_standard_deviation=8,
			shipment_lead_time=[1],
			inventory_policy_type='BS',
			base_stock_levels=[56.6])
		return example_4_2_network
	elif instance_name == "example_4_3":
		# Example 4.3 (= Example 4.1).
		return get_named_instance("example_4_1")
	elif instance_name == "problem_4_1":
		# Problem 4.1.
		holding_cost = 65-22
		stockout_cost = 129-65+15
		demand_mean = 900
		demand_sd = 60
		return holding_cost, stockout_cost, demand_mean, demand_sd
	elif instance_name == "problem_4_3b":
		# Problem 4.3(b) (newsvendor explicit -- In-Flight Meals).
		selling_revenue = 7
		purchase_cost = 2.5
		salvage_value = 1.5
		demand_mean = 50
		demand_sd = 10
		return selling_revenue, purchase_cost, salvage_value, demand_mean, demand_sd
	elif instance_name == "example_4_4":
		# Example 4.4.
		holding_cost = 0.18
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		lead_time = 4
		return holding_cost, stockout_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "example_4_7":
		# Example 4.7 (Poisson).
		holding_cost = 1
		stockout_cost = 4
		demand_mean = 6
		fixed_cost = 5
		return holding_cost, stockout_cost, fixed_cost, demand_mean
	elif instance_name == "problem_4_8a":
		# Problem 4.8(a).
		holding_cost = 200
		stockout_cost = 270
		demand_mean = 18
		return holding_cost, stockout_cost, demand_mean
	elif instance_name == "problem_4_7b":
		# Problem 4.7(b).
		holding_cost = 500000
		stockout_cost = 1000000
		demand_pmf = {1: 0.25, 2: 0.05, 3: 0.1, 4: 0.2, 5: 0.15, 6: 0.10, 7: 0.10, 8: 0.05}
		return holding_cost, stockout_cost, demand_pmf
	elif instance_name == "problem_4_8b":
		# Problem 4.8(b) -- lognormal newsvendor.
		holding_cost = 1
		stockout_cost = 0.1765
		mu = 6
		sigma = 0.3
		return holding_cost, stockout_cost, mu, sigma
	elif instance_name == "problem_4_31":
		# Problem 4.31.
		holding_cost = 40
		stockout_cost = 125
		fixed_cost = 150
		demand_mean = 4
		return holding_cost, stockout_cost, fixed_cost, demand_mean
	elif instance_name == "example_4_8":
		# Example 4.8 (= Example 4.4 + K = 2.5).
		holding_cost, stockout_cost, demand_mean, demand_sd, _ = \
			get_named_instance("example_4_4")
		fixed_cost = 2.5
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd
	elif instance_name == "problem_4_32":
		# Problem 4.32.
		holding_cost = 2
		stockout_cost = 36
		fixed_cost = 60
		demand_mean = 190
		demand_sd = 48
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd
	elif instance_name == "problem_4_29":
		# Problem 4.29.
		num_periods = 10
		holding_cost = 1
		stockout_cost = 25
		terminal_holding_cost = holding_cost
		terminal_stockout_cost = stockout_cost
		purchase_cost = 1
		fixed_cost = 0
		demand_mean = 18
		demand_sd = 3
		discount_factor = 0.98
		initial_inventory_level = 0
		return num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level
	elif instance_name == "problem_4_30":
		# Problem 4.30 (= Problem 4.29 + fixed_cost = 40).
		num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, _, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level = \
			get_named_instance("problem_4_29")
		fixed_cost = 40
		return num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level

	# CHAPTER 5
	if instance_name == "example_5_1":
		# Example 5.1 (plus 5.2-5.6).
		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		demand_mean = 1300
		demand_sd = 150
		lead_time = 1/12
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "problem_5_1":
		# Problem 5.1.
		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		demand_mean = 800
		demand_sd = 40
		lead_time = 4/365
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "problem_5_3":
		# Problem 5.3.
		holding_cost = 1.5 / 7
		stockout_cost = 40
		fixed_cost = 85
		demand_mean = 192
		demand_sd = 17.4
		lead_time = 3
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "example_5_8":
		# Example 5.8 (Poisson).
		holding_cost = 20
		stockout_cost = 150
		fixed_cost = 100
		demand_mean = 1.5
		lead_time = 2
		return holding_cost, stockout_cost, fixed_cost, demand_mean, lead_time
	elif instance_name == "problem_5_2":
		# Problem 5.2.
		holding_cost = 4
		stockout_cost = 28
		fixed_cost = 4
		demand_mean = 12
		lead_time = 0.5
		return holding_cost, stockout_cost, fixed_cost, demand_mean, lead_time

	# CHAPTER 6
	if instance_name == "example_6_1":
		# Example 6.1.
		example_6_1_network = serial_system(
			num_nodes=3,
			local_holding_cost=[7, 4, 2],
			echelon_holding_cost=[3, 2, 2],
			stockout_cost=[37.12, 0, 0],
			demand_type='N',
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time=[1, 1, 2],
			inventory_policy_type='BS',
			base_stock_levels=[6.49, 5.53, 10.69],
			downstream_0=True
		)
		return example_6_1_network
	elif instance_name == "problem_6_1":
		# Problem 6.1.
		problem_6_1_network = serial_system(
			num_nodes=2,
			local_holding_cost=[2, 1],
			echelon_holding_cost=[1, 1],
			stockout_cost=[15, 0],
			demand_type='N',
			demand_mean=100,
			demand_standard_deviation=15,
			shipment_lead_time=[1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[100, 94],
			downstream_0=True
		)
		return problem_6_1_network
	elif instance_name == "problem_6_2a":
		# Problem 6.2a.
		problem_6_2a_network = serial_system(
			num_nodes=5,
			local_holding_cost=[1, 2, 3, 5, 7],
			echelon_holding_cost=[2, 2, 1, 1, 1],
			stockout_cost=[24, 0, 0, 0, 0],
			demand_type='N',
			demand_mean=64,
			demand_standard_deviation=8,
			shipment_lead_time=[0.5, 0.5, 0.5, 0.5, 0.5],
			inventory_policy_type='BS',
			base_stock_levels=[40.59, 33.87, 35.14, 33.30, 32.93],
			downstream_0=True
		)
		return problem_6_2a_network
	elif instance_name == "problem_6_2a_adj":
		# Problem 6.2a, adjusted for periodic review.
		# (Since L=0.5 in that problem, here we treat each period as
		# having length 0.5 in the original problem.)
		problem_6_2a_network_adj = serial_system(
			num_nodes=5,
			local_holding_cost=list(np.array([1, 2, 3, 5, 7]) / 2),
			stockout_cost=list(np.array([24, 0, 0, 0, 0]) / 2),
			demand_type='N',
			demand_mean=64 / 2,
			demand_standard_deviation=8 / np.sqrt(2),
			shipment_lead_time=[1, 1, 1, 1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[40.59, 33.87, 35.14, 33.30, 32.93],
			downstream_0=True
		)
		return problem_6_2a_network_adj
	elif instance_name == "problem_6_2b_adj":
		# Problem 6.2b, adjusted for periodic review.
		# (Since L=0.5 in that problem, here we treat each period as
		# having length 0.5 in the original problem.)
		problem_6_2a_network_adj = get_named_instance('problem_6_2a_adj')
		problem_6_2b_network_adjusted = copy.deepcopy(problem_6_2a_network_adj)
		# TODO: build this instance - -need to add Poisson demand capability
		return problem_6_2b_network_adjusted
	elif instance_name == "problem_6_16":
		# Problem 6.16.
		problem_6_16_network = serial_system(
			num_nodes=2,
			local_holding_cost=[7, 2],
			stockout_cost=[24, 0],
			demand_type='N',
			demand_mean=20,
			demand_standard_deviation=4,
			shipment_lead_time=[8, 3],
			inventory_policy_type='BS',
			base_stock_levels=[171.1912, 57.7257],
			initial_IL=20,
			initial_orders=20,
			initial_shipments=20,
			downstream_0=True
		)
		return problem_6_16_network

	# CHAPTER 9
	if instance_name == "example_9_1":
		# Example 9.1.
		holding_cost = 0.225
		stockout_cost = 5
		fixed_cost = 8
		demand_rate = 1300
		disruption_rate = 1.5
		recovery_rate = 14
		return holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate
	elif instance_name == "problem_9_8":
		# Problem 9.8.
		holding_cost = 4
		stockout_cost = 22
		fixed_cost = 35
		demand_rate = 30
		disruption_rate = 1
		recovery_rate = 12
		return holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate
	elif instance_name == "example_9_3":
		# Example 9.3.
		holding_cost = 0.25
		stockout_cost = 3
		disruption_prob = 0.04
		recovery_prob = 0.25
		demand = 2000
		return holding_cost, stockout_cost, demand, disruption_prob, recovery_prob
	elif instance_name == "example_9_4":
		# Example 9.4.
		fixed_cost = 18500
		holding_cost = 0.06
		demand_rate = 75000
		yield_mean = -15000
		yield_sd = 9000
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "problem_9_4a":
		# Problem 9.4a.
		fixed_cost, holding_cost, demand_rate = get_named_instance("problem_3_1")
		yield_mean = -1/0.02
		yield_sd = 0.02
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "problem_9_4b":
		# Problem 9.4b.
		fixed_cost, holding_cost, demand_rate = get_named_instance("problem_3_1")
		yield_mean = 0.9
		yield_sd = 0.2 / np.sqrt(12)
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "example_9_5":
		# Example 9.5.
		fixed_cost = 18500
		holding_cost = 0.06
		demand_rate = 75000
		yield_mean = 5.0/6
		yield_sd = np.sqrt(5.0/(36*7))
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "example_9_6":
		# Example 9.6.
		holding_cost = 15000000
		stockout_cost = 75000000
		demand = 1.5
		yield_lo = -0.5
		yield_hi = 0.5
		return holding_cost, stockout_cost, demand, yield_lo, yield_hi
	elif instance_name == "problem_9_5":
		# Problem 9.5.
		holding_cost = 150
		stockout_cost = 1200
		demand = 25
		yield_lo = -5
		yield_hi = 0
		return holding_cost, stockout_cost, demand, yield_lo, yield_hi

	# INSTANCES NOT FROM TEXTBOOK
	if instance_name == "assembly_3_stage":
		assembly_3_stage_network = mwor_system(
			num_warehouses=2,
			local_holding_cost=[2, 1, 1],
			stockout_cost=[20, 0, 0],
			demand_type='N',
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time=[1, 2, 2],
			inventory_policy_type='BS',
			base_stock_levels=[7, 13, 11],
			initial_IL=[7, 13, 11],
			downstream_0=True
		)
		assembly_3_stage_network.nodes[0].demand_source.round_to_int = True
		return assembly_3_stage_network
	elif instance_name == "assembly_3_stage_2":
			assembly_3_stage_2_network = network_from_edges(
				edges=[(1, 3), (2, 3)],
				local_holding_cost={1: 1, 2: 1, 3: 2},
				stockout_cost={1: 0, 2: 0, 3: 20},
				demand_type={1: None, 2: None, 3: 'N'},
				demand_mean=20,
				demand_standard_deviation=5,
				shipment_lead_time={1: 2, 2: 2, 3: 1},
				inventory_policy_type='BS',
				base_stock_levels={1: 44, 2: 52, 3: 28},
				initial_IL={1: 44, 2: 52, 3: 28}
			)
			# assembly_3_stage_2_network = mwor_system(
			# 	num_warehouses=2,
			# 	local_holding_cost=[2, 1, 1],
			# 	stockout_cost=[20, 0, 0],
			# 	type='D',
			# 	mean=20,
			# 	standard_deviation=5,
			# 	shipment_lead_time=[1, 2, 2],
			# 	inventory_policy_type='BS',
			# 	base_stock_levels=[28, 52, 44],
			# 	initial_IL=[28, 52, 44],
			# 	downstream_0=True)
			assembly_3_stage_2_network.get_node_from_index(3).demand_source.round_to_int = True
			return assembly_3_stage_2_network
	elif instance_name == "rosling_figure_1":
		# Figure 1 from Rosling (1989).
		# Note: Other than the structure and lead times, none of the remaining parameters are from Rosling's paper.
		rosling_figure_1_network = SupplyChainNetwork()
		nodes = {i: SupplyChainNode(index=i) for i in range(1, 8)}
		# Inventory policies.
		for n in nodes.values():
			n.inventory_policy.type = 'BEBS'
			n.inventory_policy.base_stock_level = None
		# Node 1.
		nodes[1].shipment_lead_time = 1
		demand_source = DemandSource() # TODO: create this in the constructor (like policy)
		demand_source.type = 'UD'
		demand_source.lo = 0
		demand_source.hi = 10
		nodes[1].demand_source = demand_source
		nodes[1].supply_type = None
		nodes[1].inventory_policy.base_stock_level = 8
		nodes[1].initial_inventory_level = 8
		rosling_figure_1_network.add_node(nodes[1])
		# Node 2.
		nodes[2].shipment_lead_time = 1
		nodes[2].supply_type = None
		nodes[2].inventory_policy.base_stock_level = 24
		nodes[2].initial_inventory_level = 8
		rosling_figure_1_network.add_predecessor(nodes[1], nodes[2])
		# Node 3.
		nodes[3].shipment_lead_time = 3
		nodes[3].supply_type = None
		nodes[3].inventory_policy.base_stock_level = 40
		nodes[3].initial_inventory_level = 24
		rosling_figure_1_network.add_predecessor(nodes[1], nodes[3])
		# Node 4.
		nodes[4].shipment_lead_time = 2
		nodes[4].supply_type = None
		nodes[4].inventory_policy.base_stock_level = 76
		nodes[4].initial_inventory_level = 16
		rosling_figure_1_network.add_predecessor(nodes[3], nodes[4])
		# Node 5.
		nodes[5].shipment_lead_time = 4
		nodes[5].inventory_policy.base_stock_level = 62
		nodes[5].initial_inventory_level = 32
		nodes[5].supply_type = 'U'
		rosling_figure_1_network.add_predecessor(nodes[2], nodes[5])
		# Node 6.
		nodes[6].shipment_lead_time = 1
		nodes[6].supply_type = 'U'
		nodes[6].inventory_policy.base_stock_level = 84
		nodes[6].initial_inventory_level = 8
		rosling_figure_1_network.add_predecessor(nodes[4], nodes[6])
		# Node 7.
		nodes[7].shipment_lead_time = 2
		nodes[7].supply_type = 'U'
		nodes[7].inventory_policy.base_stock_level = 92
		nodes[7].initial_inventory_level = 16
		rosling_figure_1_network.add_predecessor(nodes[4], nodes[7])
		return rosling_figure_1_network
	elif instance_name == "kangye_4_stage":
		kangye_4_stage = mwor_system(
			num_warehouses=3,
			demand_type='N',
			demand_mean=20,
			demand_standard_deviation=4,
			shipment_lead_time=[1, 1, 2, 3],
			inventory_policy_type='BEBS',
			base_stock_levels=[30, 50, 70, 90],
			downstream_0=True
		)
		return kangye_4_stage
	elif instance_name == "kangye_3_stage_serial":
		kangye_3_stage_serial = serial_system(
			num_nodes=3,
			local_holding_cost=[1, 5, 10],
			stockout_cost=[0, 0, 100],
			demand_type='N',
			demand_mean=5,
			demand_standard_deviation=np.sqrt(5),
			shipment_lead_time=[1, 1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[7, 7, 7],
			initial_IL=[7, 7, 7],
			downstream_0=False
		)
		for i in range(2):
			kangye_3_stage_serial.get_node_from_index(i).in_transit_holding_cost = 0
		kangye_3_stage_serial.get_node_from_index(2).demand_source.round_to_int = True
		return kangye_3_stage_serial
	elif instance_name == "michelle_sean_3_stage":
		michelle_sean_3_stage = mwor_system(
			num_warehouses=2,
			demand_type='N',
			demand_mean=50,
			demand_standard_deviation=10,
			local_holding_cost=[10, 10, 10],
			stockout_cost=[10, 10, 10],
			shipment_lead_time=[1, 1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[60, 50, 60],
			downstream_0=True,
			initial_IL=[60, 50, 60]
		)
		return michelle_sean_3_stage
	elif instance_name == "rong_atan_snyder_figure_1a":
		# Uses normal demand instead of Poisson.
		rong_atan_snyder_figure_1a = network_from_edges(
			edges=[(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)],
			demand_type={0: None, 1: None, 2: None, 3: 'N', 4: 'N', 5: 'N', 6: 'N'},
			demand_mean=8,
			demand_standard_deviation=np.sqrt(8),
			local_holding_cost={0: 1/3, 1: 2/3, 2: 2/3, 3: 1, 4: 1, 5: 1, 6: 1},
			stockout_cost=20,
			shipment_lead_time=1,
			inventory_policy_type='BS',
			base_stock_levels={i: 0 for i in range(0, 7)}
		)
		return rong_atan_snyder_figure_1a
	elif instance_name == "rong_atan_snyder_figure_1b":
		# Uses normal demand instead of Poisson.
		# TODO: add costs and lead times
		demand_type = {i: 'N' if i >= 3 else None for i in range(11)}
		rong_atan_snyder_figure_1b = network_from_edges(
			edges=[(0, 1), (0, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, 8), (2, 9), (2, 10)],
			demand_type=demand_type,
			demand_mean=8,
			demand_standard_deviation=np.sqrt(8),
			inventory_policy_type='BS',
			base_stock_levels={i: 0 for i in range(0, 11)}
		)
		return rong_atan_snyder_figure_1b
	elif instance_name == "rong_atan_snyder_figure_1c":
		# Uses normal demand instead of Poisson.
		# TODO: add costs and lead times
		rong_atan_snyder_figure_1c = network_from_edges(
			edges=[(0, 1), (0, 2), (2, 3), (2, 4), (2, 5)],
			demand_type={0: None, 1: 'N', 2: None, 3: 'N', 4: 'N', 5: 'N'},
			demand_mean=8,
			demand_standard_deviation=np.sqrt(8),
			inventory_policy_type='BS',
			base_stock_levels={i: 0 for i in range(0, 6)}
		)
		return rong_atan_snyder_figure_1c


# CHAPTER 3

# save_instance("example_3_1", {"fixed_cost": 8, "holding_cost": 0.75 * 0.3, "demand_rate": 1300}, "Example 3.1")
# save_instance("problem_3_1", {"fixed_cost": 2250, "holding_cost": 275, "demand_rate": 500 * 365}, "Problem 3.1")
# save_instance("example_3_8", {"fixed_cost": 8, "holding_cost": 0.75 * 0.3, "stockout_cost": 5, "demand_rate": 1300}, "Example 3.8")
# save_instance("problem_3_2b", {"fixed_cost": 40, "holding_cost": (165 * 0.17 + 12), "stockout_cost": 60, "demand_rate": 40 * 52}, "Problem 3.2(b)")
# save_instance("problem_3_22", {"fixed_cost": 4, "holding_cost": 0.08, "demand_rate": 80, "production_rate": 110}, "Problem 3.22")
# save_instance("example_3_9", {"num_periods": 4, "holding_cost": 2, "fixed_cost": 500, "demand": [90, 120, 80, 70]}, "Example 3.9")

# N, h, K, d = get_named_instance("problem_3_29")
# save_instance("problem_3_29", {"num_periods": N, "holding_cost": h, "fixed_cost": K, "demand": d}, "Problem 3.29 (Wagner-Whitin)")

# N, h, K, d, c = get_named_instance("ww_hw_c")
# save_instance("scmo_ww_hw_c", {"num_periods": N, "holding_cost": h, "fixed_cost": K, "demand": d, "purchase_cost": c}, "(SCMO, Wagner-Whitin with nonstationary purchase cost)")

# K, k, h, d = get_named_instance("jrp_hw_3")
# save_instance("scmo_jrp_hw_3", {"shared_fixed_cost": K, "individual_fixed_costs": k, "holding_costs": h, "demand_rates": d}, "SCMO (JRP problem 3)")

# CHAPTER 4

# h, p, mu, sigma = get_named_instance("example_4_1")
# save_instance("example_4_1", {"holding_cost": h, "stockout_cost": p, "demand_mean": mu, "demand_sd": sigma}, "Example 4.1 (newsvendor)")

# network = get_named_instance("example_4_1_network")
# save_instance("example_4_1_network", network, "Example 4.1 (newsvendor) (as ``SupplyChainNetwork``)")

# r, c, v, mu, sigma = get_named_instance("example_4_2")
# save_instance("example_4_2", {"selling_revenue": r, "purchase_cost": c, "salvage_value": v, "demand_mean": mu, "demand_sd": sigma}, "Example 4.2 (newsvendor explicit)")

# network = get_named_instance("example_4_2_network")
# save_instance("example_4_2_network", network, "Example 4.2 (newsvendor explicit) (as ``SupplyChainNetwork``)")

# h, p, mu, sigma = get_named_instance("example_4_3")
# save_instance("example_4_3", {"holding_cost": h, "stockout_cost": p, "demand_mean": mu, "demand_sd": sigma}, "Example 4.3 (newsvendor) (= Example 4.1)")

# h, p, mu, sigma = get_named_instance("problem_4_1")
# save_instance("problem_4_1", {"holding_cost": h, "stockout_cost": p, "demand_mean": mu, "demand_sd": sigma}, "Problem 4.1 (newsvendor)")

# r, c, v, mu, sigma = get_named_instance("problem_4_3b")
# save_instance("problem_4_3b", {"selling_revenue": r, "purchase_cost": c, "salvage_value": v, "demand_mean": mu, "demand_sd": sigma}, "Problem 4.3(b) (newsvendor explicit)")

# h, p, mu, sigma, L = get_named_instance("example_4_4")
# save_instance("example_4_4", {"holding_cost": h, "stockout_cost": p, "demand_mean": mu, "demand_sd": sigma, "lead_time": L}, "Example 4.4 (base-stock optimization)")

# h, p, K, mu = get_named_instance("example_4_7")
# save_instance("example_4_7", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu}, "Example 4.7 ((s,S) with Poisson demand)")

#h, p, pmf = get_named_instance("problem_4_7b")
#save_instance("problem_4_7b", {"holding_cost": h, "stockout_cost": p, "demand_pmf": pmf}, "Problem 4.7(b) (newsvendor with discrete demand)")

# h, p, mu = get_named_instance("problem_4_8a")
# save_instance("problem_4_8a", {"holding_cost": h, "stockout_cost": p, "demand_mean": mu}, "Problem 4.8(a) (newsvendor with Poisson demand)")

# h, p, mu, sigma = get_named_instance("problem_4_8b")
# save_instance("problem_4_8b", {"holding_cost": h, "stockout_cost": p, "mu": mu, "sigma": sigma}, "Problem 4.8(b) (newsvendor with lognormal demand)")

# h, p, K, mu = get_named_instance("problem_4_31")
# save_instance("problem_4_31", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu}, "Problem 4.31 ((s,S) with Poisson demand)")

# h, p, K, mu, sigma = get_named_instance("example_4_8")
# save_instance("example_4_8", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu, "demand_sd": sigma}, "Example 4.8 ((s,S))")

# h, p, K, mu, sigma = get_named_instance("problem_4_32")
# save_instance("problem_4_32", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu, "demand_sd": sigma}, "Problem 4.32 ((s,S))")

# N, h, p, hT, pT, c, K, mu, sigma, gamma, iIL = get_named_instance("problem_4_29")
# save_instance("problem_4_29", {"num_periods": N, "holding_cost": h, "stockout_cost": p, "terminal_holding_cost": hT, "terminal_stockout_cost": pT, "purchase_cost": c, "fixed_cost": K, "demand_mean": mu, "demand_sd": sigma, "discount_factor": gamma, "initial_inventory_level": iIL}, "Problem 4.29 (finite-horizon)")

# N, h, p, hT, pT, c, K, mu, sigma, gamma, iIL = get_named_instance("problem_4_30")
# save_instance("problem_4_30", {"num_periods": N, "holding_cost": h, "stockout_cost": p, "terminal_holding_cost": hT, "terminal_stockout_cost": pT, "purchase_cost": c, "fixed_cost": K, "demand_mean": mu, "demand_sd": sigma, "discount_factor": gamma, "initial_inventory_level": iIL}, "Problem 4.30 (finite-horizon)")

# CHAPTER 5

# h, p, K, mu, sigma, L = get_named_instance("example_5_1")
# save_instance("example_5_1", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu, "demand_sd": sigma, "lead_time": L}, "Example 5.1 ((r,Q))")

# h, p, K, mu, sigma, L = get_named_instance("problem_5_1")
# save_instance("problem_5_1", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu, "demand_sd": sigma, "lead_time": L}, "Problem 5.1 ((r,Q))")

# h, p, K, mu, L = get_named_instance("problem_5_2")
# save_instance("problem_5_2", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu, "lead_time": L}, "Problem 5.2 ((r,Q) with Poisson demand)")

# h, p, K, mu, sigma, L = get_named_instance("problem_5_3")
# save_instance("problem_5_3", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu, "demand_sd": sigma, "lead_time": L}, "Problem 5.3 ((r,Q))")

# h, p, K, mu, L = get_named_instance("example_5_8")
# save_instance("example_5_8", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_mean": mu, "lead_time": L}, "Example 5.8 ((r,Q) with Poisson demand)")

# CHAPTER 6

# network = get_named_instance("example_6_1")
# save_instance("example_6_1", network, "Example 6.1 (serial SSM)")

# network = get_named_instance("problem_6_1")
# save_instance("problem_6_1", network, "Problem 6.1 (serial SSM)")

# network = get_named_instance("problem_6_2a")
# save_instance("problem_6_2a", network, "Problem 6.2(a) (serial SSM)")

# network = get_named_instance("problem_6_2a_adj")
# save_instance("problem_6_2a_adj", network, "Problem 6.2(a) (serial SSM), adjusted for periodic review (since L=0.5 in that problem, here we treat each period as having length 0.5 in the original problem.)")

# network = get_named_instance("problem_6_2b_adj")
# save_instance("problem_6_2b_adj", network, "Problem 6.2(b) (serial SSM), adjusted for periodic review (since L=0.5 in that problem, here we treat each period as having length 0.5 in the original problem.)")

# network = get_named_instance("problem_6_16")
# save_instance("problem_6_16", network, "Problem 6.16 (serial SSM)")

# network = network_from_edges(
# 	[(1, 3), (3, 2), (3, 4)], node_indices=[1, 2, 3, 4],
# 	processing_times=[2, 1, 1, 1],
# 	external_inbound_csts=[1, None, None, None],
# 	local_holding_cost=[1, 3, 2, 3],
# 	demand_bound_constants=[1, 1, 1, 1],
# 	external_outbound_csts=[None, 0, None, 1],
# 	demand_type=[None, 'N', None, 'N'],
# 	demand_mean=0,
# 	demand_standard_deviation=[None, 1, None, 1]
# )
# save_instance("example_6_5", network, 'Example 6.5 (tree GSM)')

# network = SupplyChainNetwork()
# network.add_node(SupplyChainNode(1, 'Raw_Material', network, processing_time=2, local_holding_cost=0.01))
# network.add_node(SupplyChainNode(2, 'Process_Wafers', network, processing_time=3, local_holding_cost=0.03))
# network.add_node(SupplyChainNode(3, 'Package_Test_Wafers', network, processing_time=2, local_holding_cost=0.04))
# network.add_node(SupplyChainNode(4, 'Imager_Base', network, processing_time=4, local_holding_cost=0.06))
# network.add_node(SupplyChainNode(5, 'Imager_Assembly', network, processing_time=2, local_holding_cost=0.12))
# network.add_node(SupplyChainNode(6, 'Ship_to_Final_Assembly', network, processing_time=3, local_holding_cost=0.13))
# network.add_node(SupplyChainNode(7, 'Camera', network, processing_time=6, local_holding_cost=0.20))
# network.add_node(SupplyChainNode(8, 'Circuit_Board', network, processing_time=4, local_holding_cost=0.08))
# network.add_node(SupplyChainNode(9, 'Other_Parts', network, processing_time=3, local_holding_cost=0.04))
# network.add_node(SupplyChainNode(10, 'Build_Test_Pack', network, processing_time=2, local_holding_cost=0.50, \
# 	external_outbound_cst=2, demand_source=DemandSource(type='N', mean=0, standard_deviation=10),
# 	demand_bound_constant=stats.norm.ppf(0.95)))
# network.add_edges_from_list([(1, 2), (2, 3), (3, 5), (4, 5), (5, 6), (7, 10), (6, 10), (8, 10), (9, 10)])
# save_instance("figure_6_14", network, 'Figure 6.14 (tree GSM)')

# network = network_from_edges([(1, 2), (1, 3), (3, 5), (4, 5), (5, 6), (5, 7)])
# save_instance("figure_6_12", network, 'Figure 6.12 (tree GSM')

# network = SupplyChainNetwork()
# network.add_node(SupplyChainNode(3, name='Forming', network=network, processing_time=1, local_holding_cost=2, external_inbound_cst=1))
# network.add_node(SupplyChainNode(2, name='Firing', network=network, processing_time=1, local_holding_cost=3))
# network.add_node(SupplyChainNode(1, name='Glazing', network=network, processing_time=2, local_holding_cost=4, external_outbound_cst=0, demand_source=DemandSource(type='N', mean=45, standard_deviation=10), demand_bound_constant=4))
# network.add_edges_from_list([(3, 2), (2, 1)])
# save_instance("problem_6_7", network, 'Problem 6.7 (tree GSM)')

network = SupplyChainNetwork()
network.add_node(SupplyChainNode(1, network=network, processing_time=7, local_holding_cost=220*0.2/365, external_outbound_cst=3, demand_source=DemandSource(type='N', mean=22.0, standard_deviation=4.1), demand_bound_constant=4))
network.add_node(SupplyChainNode(2, network=network, processing_time=7, local_holding_cost=140*0.2/365, external_outbound_cst=3, demand_source=DemandSource(type='N', mean=15.3, standard_deviation=6.2), demand_bound_constant=4))
network.add_node(SupplyChainNode(3, network=network, processing_time=21, local_holding_cost=90*0.2/365))
network.add_node(SupplyChainNode(4, network=network, processing_time=3, local_holding_cost=5*0.2/365))
network.add_node(SupplyChainNode(5, network=network, processing_time=8, local_holding_cost=20*0.2/365))
network.add_node(SupplyChainNode(6, network=network, processing_time=2, local_holding_cost=7.5*0.2/365))
network.add_edges_from_list([(6, 5), (4, 3), (5, 3), (3, 1), (3, 2)])
save_instance("problem_6_9", network, 'Problem 6.9 (tree GSM)')

# CHAPTER 9

# h, p, K, d, lambdaa, mu = get_named_instance("example_9_1")
# save_instance("example_9_1", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_rate": d, "disruption_rate": lambdaa, "recovery_rate": mu}, "Example 9.1 (EOQB)")

# h, p, K, d, lambdaa, mu = get_named_instance("problem_9_8")
# save_instance("problem_9_8", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_rate": d, "disruption_rate": lambdaa, "recovery_rate": mu}, "Problem 9.8 (EOQB)")

# h, p, d, alpha, beta = get_named_instance("example_9_3")
# save_instance("example_9_3", {"holding_cost": h, "stockout_cost": p, "demand": d, "disruption_prob": alpha, "recovery_prob": beta}, "Example 9.3 (base-stock with disruptions)")

# K, h, d, mu, sigma = get_named_instance("example_9_4")
# save_instance("example_9_4", {"holding_cost": h, "fixed_cost": K, "demand_rate": d, "yield_mean": mu, "yield_sd": sigma}, "Example 9.4 (EOQ with additive yield uncertainty)")

# K, h, d, mu, sigma = get_named_instance("problem_9_4a")
# save_instance("problem_9_4a", {"holding_cost": h, "fixed_cost": K, "demand_rate": d, "yield_mean": mu, "yield_sd": sigma}, "Problem 9.4(a) (EOQ with additive yield uncertainty)")

# K, h, d, mu, sigma = get_named_instance("problem_9_4b")
# save_instance("problem_9_4b", {"holding_cost": h, "fixed_cost": K, "demand_rate": d, "yield_mean": mu, "yield_sd": sigma}, "Problem 9.4(b) (EOQ with multiplicative yield uncertainty)")

# K, h, d, mu, sigma = get_named_instance("example_9_5")
# save_instance("example_9_5", {"holding_cost": h, "fixed_cost": K, "demand_rate": d, "yield_mean": mu, "yield_sd": sigma}, "Problem 9.5 (EOQ with multiplicative yield uncertainty)")

# h, p, d, lo, hi = get_named_instance("example_9_6")
# save_instance("example_9_6", {"holding_cost": h, "stockout_cost": p, "demand": d, "yield_lo": lo, "yield_hi": hi}, "Example 9.6 (newsvendor with additive yield uncertainty)")

# h, p, d, lo, hi = get_named_instance("problem_9_5")
# save_instance("problem_9_5", {"holding_cost": h, "stockout_cost": p, "demand": d, "yield_lo": lo, "yield_hi": hi}, "Problem 9.5 (newsvendor with additive yield uncertainty)")

# OTHER INSTANCES

# network = get_named_instance("assembly_3_stage")
# save_instance("assembly_3_stage", network, "3-stage assembly system (2 warehouses, 1 retailer)")

# network = get_named_instance("rosling_figure_1")
# save_instance("rosling_figure_1", network, "assembly system from Figure 1 in Rosling (1989) (structure and lead times are from Rosling; all other parameters are made up)")

# network = get_named_instance("rong_atan_snyder_figure_1a")
# save_instance("rong_atan_snyder_figure_1a", network, "distribution system from Figure 1(a) in Rong, Atan, and Snyder (2017)) (using normal demand instead of Poisson)")

# network = get_named_instance("rong_atan_snyder_figure_1b")
# save_instance("rong_atan_snyder_figure_1b", network, "distribution system from Figure 1(b) in Rong, Atan, and Snyder (2017)) (using normal demand instead of Poisson, and with costs and lead times omitted)")

# network = get_named_instance("rong_atan_snyder_figure_1c")
# save_instance("rong_atan_snyder_figure_1c", network, "distribution system from Figure 1(c) in Rong, Atan, and Snyder (2017)) (using normal demand instead of Poisson, and with costs and lead times omitted)")
