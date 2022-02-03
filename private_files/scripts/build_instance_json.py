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

# h, p, mu, sigma = get_named_instance("example_4_1")
# save_instance("example_4_1", {"holding_cost": h, "stockout_cost": p, "demand_mean": mu, "demand_sd": sigma}, "Example 4.1 (newsvendor)")

# network = get_named_instance("example_4_1_network")
# save_instance("example_4_1_network", network, "Example 4.1 (newsvendor) (as SupplyChainNetwork)")

# r, c, v, mu, sigma = get_named_instance("example_4_2")
# save_instance("example_4_2", {"selling_revenue": r, "purchase_cost": c, "salvage_value": v, "demand_mean": mu, "demand_sd": sigma}, "Example 4.2 (newsvendor explicit)")

# network = get_named_instance("example_4_2_network")
# save_instance("example_4_2_network", network, "Example 4.2 (newsvendor explicit) (as SupplyChainNetwork)")

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

h, p, pmf = get_named_instance("problem_4_7b")
save_instance("problem_4_7b", {"holding_cost": h, "stockout_cost": p, "demand_pmf": pmf}, "Problem 4.7(b) (newsvendor with discrete demand)")

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

# CHAPTER 9

# h, p, K, d, lambdaa, mu = get_named_instance("example_9_1")
# save_instance("example_9_1", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_rate": d, "disruption_rate": lambdaa, "recovery_rate": mu}, "Example 9.1 (EOQB)")

# h, p, K, d, lambdaa, mu = get_named_instance("problem_9_8")
# save_instance("problem_9_8", {"holding_cost": h, "stockout_cost": p, "fixed_cost": K, "demand_rate": d, "disruption_rate": lambdaa, "recovery_rate": mu}, "Problem 9.8 (EOQB)")

# h, p, d, alpha, beta = get_named_instance("example_9_3")
# save_instance("example_9_3", {"holding_cost": h, "stockout_cost": p, "demand": d, "disruption_prob": alpha, "recovery_prob": beta}, "Example 9.3 (base-stock with disruptions)")

# K, h, d, mu, sigma = get_named_instance("example_9_4")
# save_instance("example_9_4", {"holding_cost": h, "fixed_cost": K, "demand_rate": d, "yield_mean": mu, "yield_sd": sigma}, "Example 9.4 (EOQ with additive yield uncertainty")

# K, h, d, mu, sigma = get_named_instance("problem_9_4a")
# save_instance("problem_9_4a", {"holding_cost": h, "fixed_cost": K, "demand_rate": d, "yield_mean": mu, "yield_sd": sigma}, "Problem 9.4(a) (EOQ with additive yield uncertainty")

# K, h, d, mu, sigma = get_named_instance("example_9_5")
# save_instance("example_9_3", {"holding_cost": h, "fixed_cost": K, "demand_rate": d, "yield_mean": mu, "yield_sd": sigma}, "Problem 9.5 (EOQ with multiplicative yield uncertainty")

# h, p, d, lo, hi = get_named_instance("example_9_6")
# save_instance("example_9_6", {"holding_cost": h, "stockout_cost": p, "demand": d, "yield_lo": lo, "yield_hi": hi}, "Example 9.6 (newsvendor with additive yield uncertainty")

# h, p, d, lo, hi = get_named_instance("problem_9_5")
# save_instance("problem_9_5", {"holding_cost": h, "stockout_cost": p, "demand": d, "yield_lo": lo, "yield_hi": hi}, "Problem 9.5 (newsvendor with additive yield uncertainty")

# OTHER INSTANCES

# network = get_named_instance("assembly_3_stage")
# save_instance("assembly_3_stage", network, "3-stage assembly system (2 warehouses, 1 retailer)")

# network = get_named_instance("rosling_figure_1")
# save_instance("rosling_figure_1", network, "assembly system from Figure 1 in Rosling (1989) (structure and lead times are from Rosling; all other parameters are made up)")

# network = get_named_instance("rong_atan_snyder_figure_1a")
# save_instance("rong_atan_snyder_figure_1a", network, "distribution system from Figure 1 in Rong, Atan, and Snyder (2017)) (using normal demand instead of Poisson)")

