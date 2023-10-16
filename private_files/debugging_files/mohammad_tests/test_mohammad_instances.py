import time

from sim import *
from meio import *

from mohammad_tests.mohammad_instances import *

def main():
	# What to do.
	EVALUATE_MP = True
	OPTIMIZE_CD = False
	OPTIMIZE_E = False

	# Settings for optimization simulation and full simulation evaluation.
	OPT_NUM_PERIODS = 200
	OPT_NUM_TRIALS = 3
	EVAL_NUM_PERIODS = 10000
	EVAL_NUM_TRIALS = 10
	SEED = 762

	network = get_mohammad_instance("assembly_2_instance_5")
#	groups = [{1, 2, 3, 4, 5, 6, 7}]
	groups = [{1, 2, 3, 4, 5}, {6}, {7}]

	if EVALUATE_MP:
		# Evaluate Mohammad's solution.
		print("Evaluating Mohammad's solution...")
		S_mp = {n.index: n.inventory_policy.base_stock_level for n in network.nodes}
		for n in network.nodes:
			n.inventory_policy.base_stock_level = S_mp[n.index]
		mean_cost_mp, sem_cost_mp = run_multiple_trials(network, rand_seed=SEED, num_trials=EVAL_NUM_TRIALS, num_periods=EVAL_NUM_PERIODS)
	else:
		S_mp = {n_ind: None for n_ind in network.node_indices}
		mean_cost_mp = None
		sem_cost_mp = None

	# Get range for optimization.
	lo = {n.index: n.derived_demand_mean * n.lead_time * 0.75 for n in network.nodes}
	hi = {n.index: n.derived_demand_mean * n.lead_time * 2 for n in network.nodes}

	if OPTIMIZE_CD:
		# Optimize by coordinate descent.
		print("\nOptimizing by coordinate descent...")
		initial_solution = {n.index: n.derived_demand_mean * n.lead_time for n in network.nodes}
		tic = time.perf_counter()
		best_S_cd, best_cost_cd = meio_by_coordinate_descent(network, groups=groups,
											initial_solution=initial_solution,
											search_lo=lo, search_hi=hi,
											sim_num_trials=OPT_NUM_TRIALS, sim_num_periods=OPT_NUM_PERIODS,
											sim_rand_seed=SEED,
											verbose=True)
		toc = time.perf_counter()
		time_cd = toc - tic
		# Evaluate coordinate descent solution.
		print("\nEvaluating coordinate descent solution...")
		for n in network.nodes:
			n.inventory_policy.base_stock_level = best_S_cd[n.index]
		mean_cost_cd, sem_cost_cd = run_multiple_trials(network, num_trials=EVAL_NUM_TRIALS, num_periods=EVAL_NUM_PERIODS)
	else:
		best_S_cd = {n_ind: None for n_ind in network.node_indices}
		best_cost_cd = None
		mean_cost_cd = None
		sem_cost_cd = None
		time_cd = None

	if OPTIMIZE_E:
		# Optimize by enumeration.
		print("\nOptimizing by enumeration...")
		tic = time.perf_counter()
		best_S_e, best_cost_e = meio_by_enumeration(network,
												groups=groups,
												truncation_lo=lo,
												truncation_hi=hi,
												discretization_num=10,
												sim_num_trials=OPT_NUM_TRIALS, sim_num_periods=OPT_NUM_PERIODS,
												sim_rand_seed=SEED,
												print_solutions=False,
												progress_bar=True)
		toc = time.perf_counter()
		time_e = toc - tic
		# Evaluate enumeration solution.
		print("\nEvaluating enumeration solution...")
		for n in network.nodes:
			n.inventory_policy.base_stock_level = best_S_e[n.index]
		mean_cost_e, sem_cost_e = run_multiple_trials(network, num_trials=EVAL_NUM_TRIALS, num_periods=EVAL_NUM_PERIODS)
	else:
		best_S_e = {n_ind: None for n_ind in network.node_indices}
		best_cost_e = None
		mean_cost_e = None
		sem_cost_e = None
		time_e = None

	# Build output table.
	results = []
	headers = [None, "MP Solution", "CD Solution", "Enum Solution"]
	ind = network.node_indices
	ind.sort()
	for n_ind in ind:
		results.append(["S_{}".format(n_ind), S_mp[n_ind], best_S_cd[n_ind], best_S_e[n_ind]])
	results.append(["Cost reported by optimization:", None, best_cost_cd, best_cost_e])
	results.append(["Cost evaluated by simulation, mean:", mean_cost_mp, mean_cost_cd, mean_cost_e])
	results.append(["Cost evaluated by simulation, SEM:", sem_cost_mp, sem_cost_cd, sem_cost_e])
	results.append(["Time (sec):", None, time_cd, time_e])

	print(tabulate(results, headers=headers))

if __name__ == "__main__":
	main()
