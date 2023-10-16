import copy

from stockpyl.supply_chain_network import *


def get_mohammad_instance(instance_name):
	"""Return the named instance specified by ``instance_name``. Return
	variables depend on the instance.

	Parameters
	----------
	instance_name : str
		The instance name. See method code for allowable strings.

	"""

	if instance_name == "assembly_1_instance_1":
#		base_stock_levels = {1: 26.91, 2: 26.8, 3: 26.86, 4: 26.85, 5: 13.56, 6: 13.57, 7: 14.64} # DNN
		base_stock_levels = {1: 6.0848, 2: 27.32172, 3: 21.77163, 4: 26.89778, 5: 13.47768, 6: 14.109565, 7: 14.439935} # DFO

		network = network_from_edges(
			edges=[(1, 5), (2, 5), (3, 6), (4, 6), (5, 7), (6, 7)],
			local_holding_cost={1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25, 5: 0.8, 6: 0.8, 7: 1.9},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 10},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=13,
			demand_standard_deviation=1.2,
			shipment_lead_time={1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_1_instance_2":
#		base_stock_levels = {1: 10.08, 2: 10.08, 3: 10.13, 4: 10.13, 5: 5.42, 6: 5.36, 7: 6.56} # DNN
		base_stock_levels = {1: 10.19997, 2: 11.83357, 3: 1.00973, 4: 11.15087, 5: 4.65895, 6: 3.04472, 7: 6.902135} # DFO

		network = network_from_edges(
			edges=[(1, 5), (2, 5), (3, 6), (4, 6), (5, 7), (6, 7)],
			local_holding_cost={1: 2, 2: 2, 3: 2, 4: 2, 5: 4, 6: 4, 7: 7},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 37.12},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time={1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_1_instance_3":
#		base_stock_levels = {1: 40.98, 2: 40.99, 3: 41.03, 4: 41.07, 5: 42.5, 6: 43.22, 7: 46.16} # DNN
		base_stock_levels = {1: 39.66654, 2: 22.78782, 3: 12.47249, 4: 46.63012, 5: 40.811065, 6: 41.23119, 7: 47.927315}  # DFO
		network = network_from_edges(
			edges=[(1, 5), (2, 5), (3, 6), (4, 6), (5, 7), (6, 7)],
			local_holding_cost={1: 0.4, 2: 0.4, 3: 0.4, 4: 0.4, 5: 0.9, 6: 0.9, 7: 2.1},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 15},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=20,
			demand_standard_deviation=3,
			shipment_lead_time={1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_1_instance_4":
		#base_stock_levels = {1: 10.12, 2: 10.19, 3: 10.73, 4: 10.21, 5: 12.56, 6: 12.38, 7: 12.25}  # DNN
		base_stock_levels = {1: 1.26966, 2: 7.59656, 3: 9.89732, 4: 1.60905, 5: 7.66552, 6: 6.609325, 7: 14.66896}  # DFO
		network = network_from_edges(
			edges=[(1, 5), (2, 5), (3, 6), (4, 6), (5, 7), (6, 7)],
			local_holding_cost={1: 0.3, 2: 0.3, 3: 0.3, 4: 0.3, 5: 0.8, 6: 0.8, 7: 2},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 15},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time={1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_1_instance_5":
		#base_stock_levels = {1: 5.01, 2: 5.02, 3: 5.11, 4: 5.06, 5: 7.05, 6: 6.95, 7: 6.28} # DNN
		base_stock_levels = {1: 8.79276, 2: 7.35225, 3: 8.91924, 4: 5.23825, 5: 4.39524, 6: 4.41465, 7: 6.069885}  # DFO
		network = network_from_edges(
			edges=[(1, 5), (2, 5), (3, 6), (4, 6), (5, 7), (6, 7)],
			local_holding_cost={1: 0.5, 2: 0.5, 3: 0.5, 4: 0.5, 5: 1, 6: 1, 7: 3},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 16},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time={1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network

	if instance_name == "assembly_2_instance_1":
		#base_stock_levels = {1: 5.23, 2: 5.01, 3: 5.22, 4: 4.96, 5: 4.92, 6: 6.11, 7: 6.25} # DNN
		base_stock_levels = {1: 6.76884, 2: 6.53439, 3: 6.80622, 4: 6.80622, 5: 3.367885, 6: 6.283875, 7: 5.93438}  # DFO
		network = network_from_edges(
			edges=[(4, 6), (5, 6), (1, 7), (2, 7), (3, 7), (6, 7)],
			local_holding_cost={1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 4, 7: 7},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 40},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time={1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_2_instance_2":
		#base_stock_levels = {1: 9.93, 2: 9.89, 3: 9.98, 4: 9.86, 5: 9.87, 6: 11.19, 7: 12.28} # DNN
		base_stock_levels = {1: 10.89048, 2: 10.49692, 3: 11.01343, 4: 11.2439, 5: 8.19415, 6: 10.676975, 7: 11.18709}  # DFO
		network = network_from_edges(
			edges=[(4, 6), (5, 6), (1, 7), (2, 7), (3, 7), (6, 7)],
			local_holding_cost={1: 0.3, 2: 0.3, 3: 0.3, 4: 0.3, 5: 0.3, 6: 0.5, 7: 0.9},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 3.5},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=10,
			demand_standard_deviation=1,
			shipment_lead_time={1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_2_instance_3":
		#base_stock_levels = {1: 10.7, 2: 10.43, 3: 10.71, 4: 10.27, 5: 10.24, 6: 11.06, 7: 11.49}  # DNN
		base_stock_levels = {1: 11.57266, 2: 19.27623, 3: 11.59136, 4: 13.77751, 5: 9.67496, 6: 11.690005, 7: 11.77895}  # DFO
		network = network_from_edges(
			edges=[(4, 6), (5, 6), (1, 7), (2, 7), (3, 7), (6, 7)],
			local_holding_cost={1: 0.5, 2: 0.5, 3: 0.5, 4: 0.5, 5: 0.5, 6: 3, 7: 6},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 25},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=10,
			demand_standard_deviation=2,
			shipment_lead_time={1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_2_instance_4":
		#base_stock_levels = {1: 7.26, 2: 7.16, 3: 7.1, 4: 6.93, 5: 6.88, 6: 7.87, 7: 7.81}  # DNN
		base_stock_levels = {1: 7.47658, 2: 7.95378, 3: 6.10077, 4: 5.57228, 5: 9.1448, 6: 6.51286, 7: 8.0289}  # DFO
		network = network_from_edges(
			edges=[(4, 6), (5, 6), (1, 7), (2, 7), (3, 7), (6, 7)],
			local_holding_cost={1: 0.6, 2: 0.6, 3: 0.6, 4: 0.6, 5: 0.6, 6: 1.1, 7: 2.5},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 5.4},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=7,
			demand_standard_deviation=1,
			shipment_lead_time={1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
	elif instance_name == "assembly_2_instance_5":
		#base_stock_levels = {1: 12.11, 2: 11.97, 3: 11.9, 4: 11.5, 5: 11.59, 6: 13.56, 7: 14.54}  # DNN
		base_stock_levels = {1: 14.88273, 2: 14.55826, 3: 14.48443, 4: 4.95442, 5: 8.154495, 6: 14.92147, 7: 14.80215}  # DFO
		network = network_from_edges(
			edges=[(4, 6), (5, 6), (1, 7), (2, 7), (3, 7), (6, 7)],
			local_holding_cost={1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25, 5: 0.25, 6: 0.59, 7: 0.88},
			stockout_cost={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 49.7},
			demand_type={1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: 'N'},
			demand_mean=11,
			demand_standard_deviation=2,
			shipment_lead_time={1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1},
			inventory_policy_type='BS',
			base_stock_levels=base_stock_levels,
			initial_IL=base_stock_levels
		)
		return network
