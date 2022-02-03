import sys

sys.path.append('/Users/larry/Documents/GitHub/stockpyl')
# print(sys.path)

#from ...stockpyl.instances import *

# import os

# print(os.getcwd())

from stockpyl.instances import *

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

# network = get_named_instance("example_4_1_network")
# #network.nodes[0].to_dict()
# save_instance("example_4_1", network, "Example 4.1 (as SupplyChainNetwork)")

# import jsonpickle

# network_json = jsonpickle.encode(network)

# pass

#instance = load_instance("scmo_jrp_hw_3")
instance = load_instance("example_4_1_network")
print(instance)
