# This is necessary in order to make the import statements work.
import sys

sys.path.append('../stockpyl')

from stockpyl import sim
from stockpyl import sim_io
from stockpyl.instances import load_instance
from stockpyl.disruption_process import DisruptionProcess


# Number of periods.
T = 1000

# --------- EXAMPLE 6.1 (serial) --------- #

# Load instance.
network = load_instance("example_6_1")

# Add shipment-pausing disruptions at node 2.
network.get_node_from_index(2).disruption_process = DisruptionProcess(
	random_process_type='M',	# Markovian
	disruption_type='SP',		# shipment-pausing
	disruption_probability=0.1,
	recovery_probability=0.3
)

# Simulate the system.
total_cost = sim.simulation(network=network, num_periods=T, rand_seed=42)

# Write results to CSV file.
sim_io.write_results(
	network=network,
	num_periods=T,
	write_csv=True,
	csv_filename='aux_files/sim_results_example_6_1.csv'
)

# --------- ROSLING FIGURE 1 (assembly) --------- #

# Load instance. 
network = load_instance("rosling_figure_1")

# Add shipment-pausing disruptions at node 4.
network.get_node_from_index(4).disruption_process = DisruptionProcess(
	random_process_type='M',	# Markovian
	disruption_type='SP',		# shipment-pausing
	disruption_probability=0.05,
	recovery_probability=0.2
)

# Simulate the system.
total_cost = sim.simulation(network=network, num_periods=T, rand_seed=42)

# Write results to CSV file.
sim_io.write_results(
	network=network,
	num_periods=T,
	write_csv=True,
	csv_filename='aux_files/sim_results_rosling_figure_1.csv'
)


# --------- RONG, ATAN, SNYDER FIGURE 1a (distribution) --------- #

# Load instance. 
network = load_instance("rong_atan_snyder_figure_1a")

# Add shipment-pausing disruptions at node 0 and 5.
# NOTE: If your simulation can't handle independent disruptions at two different nodes,
# comment out one of them below.
network.get_node_from_index(0).disruption_process = DisruptionProcess(
	random_process_type='M',	# Markovian
	disruption_type='SP',		# shipment-pausing
	disruption_probability=0.05,
	recovery_probability=0.3
)
network.get_node_from_index(5).disruption_process = DisruptionProcess(
	random_process_type='M',	# Markovian
	disruption_type='SP',		# shipment-pausing
	disruption_probability=0.2,
	recovery_probability=0.5
)

# Simulate the system.
total_cost = sim.simulation(network=network, num_periods=T, rand_seed=42)

# Write results to CSV file.
sim_io.write_results(
	network=network,
	num_periods=T,
	write_csv=True,
	csv_filename='aux_files/sim_results_rong_atan_snyder_figure_1a.csv'
)

