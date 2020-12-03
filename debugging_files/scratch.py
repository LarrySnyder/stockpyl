from pyinv.sim import *


T = 100

network = get_named_instance("rosling_figure_1")
# Make the BS levels a little smaller so there are some stockouts.
network.get_node_from_index(1).inventory_policy.base_stock_level = 6
network.get_node_from_index(2).inventory_policy.base_stock_level = 20
network.get_node_from_index(3).inventory_policy.base_stock_level = 35
network.get_node_from_index(4).inventory_policy.base_stock_level = 58
network.get_node_from_index(5).inventory_policy.base_stock_level = 45
network.get_node_from_index(6).inventory_policy.base_stock_level = 65
network.get_node_from_index(7).inventory_policy.base_stock_level = 75

total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

# #	write_results(network, T, total_cost, write_csv=False)
write_results(network, T, total_cost, write_csv=True, csv_filename='temp.csv')

