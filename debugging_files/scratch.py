from pyinv.sim import *


T = 100

network = get_named_instance("example_4_1_network")

total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

# #	write_results(network, T, total_cost, write_csv=False)
write_results(network, T, total_cost, write_csv=False, csv_filename='temp.csv')

