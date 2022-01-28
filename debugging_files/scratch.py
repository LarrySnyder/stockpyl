from sim import *


# T = 100
#
# network = get_named_instance("example_4_1_network")
#
# total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)
#
# # #	write_results(network, T, total_cost, write_csv=False)
# write_results(network, T, total_cost, write_csv=False, csv_filename='temp.csv')
#

from wagner_whitin import *

# T = 4
# h = 1
# K = 20
# d = [25, 15, 15, 30]

# T = 5
# h = 0.1
# K = 100
# d = [730, 580, 445, 650, 880]

# T = 8
# h = 3
# K = 600
# d = [75, 95, 40, 120, 50, 70, 35, 80]

T = 4
h = 10
K = 2000
d = [100, 400, 150, 300]

Q, C, theta, s = wagner_whitin(T, h, K, d)

print(C)
print(Q)
print(theta)
print (s)