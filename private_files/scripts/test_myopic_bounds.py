from stockpyl.instances import load_instance
from stockpyl.finite_horizon import *

if __name__ == "__main__":

	instance = load_instance("problem_4_29")

	num_periods = 6
	# holding_cost = [1, 1, 1, 1, 2, 2]
	# stockout_cost = [20, 20, 10, 15, 10, 10]
	# terminal_holding_cost = 4
	# terminal_stockout_cost = 50
	# purchase_cost = [0.2, 0.8, 0.5, 0.5, 0.2, 0.8]
	# fixed_cost = 100
	# demand_mean = [20, 60, 110, 200, 200, 40]
	# demand_sd = [4.6000, 11.9000, 26.4000, 32.8000, 1.8000, 8.5000]
	# discount_factor = 0.98
	# initial_inventory_level = 0

	S_underbar, S_overbar, s_underbar, s_overbar = myopic_bounds(
				instance['num_periods'], 
				instance['holding_cost'], 
				instance['stockout_cost'], 
				instance['terminal_holding_cost'], 
				instance['terminal_stockout_cost'], 
				instance['purchase_cost'], 
				instance['fixed_cost'], 
				instance['demand_mean'], 
				instance['demand_sd'], 
				instance['discount_factor']
		)

	# Solve problem.
	reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
		x_range = finite_horizon_dp(				
				instance['num_periods'], 
				instance['holding_cost'], 
				instance['stockout_cost'], 
				instance['terminal_holding_cost'], 
				instance['terminal_stockout_cost'], 
				instance['purchase_cost'], 
				instance['fixed_cost'], 
				instance['demand_mean'], 
				instance['demand_sd'], 
				instance['discount_factor'], 
				instance['initial_inventory_level']
		)

	results = []
	for t in range(1, num_periods+1):
		results.append([t, reorder_points[t], order_up_to_levels[t], S_underbar[t], S_overbar[t],
					   s_underbar[t], s_overbar[t]])

	print(tabulate(results, headers=["t", "s", "S", "S_underbar", "S_overbar", "s_underbar", "s_overbar"]))

	print(S_underbar, S_overbar, s_underbar, s_overbar)

	# S_underbar, S_overbar, s_underbar, s_overbar = myopic_bounds(5, 1, 20, 1, 20, 2, 50, 100, 20)
	# print(S_underbar[1], S_overbar[1], s_underbar[1], s_overbar[1])