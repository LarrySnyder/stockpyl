import networkx as nx
from scipy import stats


# Build instance corresponding to network in Figure 6.12.
instance_figure_6_12 = nx.DiGraph()
instance_figure_6_12.add_nodes_from(range(1, 8))
instance_figure_6_12.add_edge(1, 2)
instance_figure_6_12.add_edge(1, 3)
instance_figure_6_12.add_edge(3, 5)
instance_figure_6_12.add_edge(4, 5)
instance_figure_6_12.add_edge(5, 6)
instance_figure_6_12.add_edge(5, 7)

# Build instance corresponding to Example 6.5.
instance_example_6_5 = nx.DiGraph()
instance_example_6_5.add_node(1, processing_time=2,
							  external_inbound_cst=1,
							  holding_cost=1,
							  demand_bound_constant=1)
instance_example_6_5.add_node(2, processing_time=1,
							  external_outbound_cst=0,
							  holding_cost=3,
							  demand_bound_constant=1,
							  external_demand_standard_deviation=1)
instance_example_6_5.add_node(3, processing_time=1,
							  holding_cost=2,
							  demand_bound_constant=1)
instance_example_6_5.add_node(4, processing_time=1,
							  external_outbound_cst=1,
							  holding_cost=3,
							  demand_bound_constant=1,
							  external_demand_standard_deviation=1)
instance_example_6_5.add_edge(1, 3)
instance_example_6_5.add_edge(3, 2)
instance_example_6_5.add_edge(3, 4)

# Build instance corresponding to Figure 6.14.
# Must be relabeled before used.
instance_figure_6_14 = nx.DiGraph()
instance_figure_6_14.add_node('Raw_Material', processing_time=2,
							  holding_cost=0.01)
instance_figure_6_14.add_node('Process_Wafers', processing_time=3,
							  holding_cost=0.03)
instance_figure_6_14.add_node('Package_Test_Wafers', processing_time=2,
							  holding_cost=0.04)
instance_figure_6_14.add_node('Imager_Base', processing_time=4,
							  holding_cost=0.06)
instance_figure_6_14.add_node('Imager_Assembly', processing_time=2,
							  holding_cost=0.12)
instance_figure_6_14.add_node('Ship_to_Final_Assembly', processing_time=3,
							  holding_cost=0.13)
instance_figure_6_14.add_node('Camera', processing_time=6,
							  holding_cost=0.20)
instance_figure_6_14.add_node('Circuit_Board', processing_time=4,
							  holding_cost=0.08)
instance_figure_6_14.add_node('Other_Parts', processing_time=3,
							  holding_cost=0.04)
instance_figure_6_14.add_node('Build_Test_Pack', processing_time=2,
							  holding_cost=0.50,
							  external_outbound_cst=2,
							  external_demand_standard_deviation=10,
							  demand_bound_constant=stats.norm.ppf(0.95))
instance_figure_6_14.add_edge('Raw_Material', 'Process_Wafers')
instance_figure_6_14.add_edge('Process_Wafers', 'Package_Test_Wafers')
instance_figure_6_14.add_edge('Package_Test_Wafers', 'Imager_Assembly')
instance_figure_6_14.add_edge('Imager_Base', 'Imager_Assembly')
instance_figure_6_14.add_edge('Imager_Assembly', 'Ship_to_Final_Assembly')
instance_figure_6_14.add_edge('Camera', 'Build_Test_Pack')
instance_figure_6_14.add_edge('Ship_to_Final_Assembly', 'Build_Test_Pack')
instance_figure_6_14.add_edge('Circuit_Board', 'Build_Test_Pack')
instance_figure_6_14.add_edge('Other_Parts', 'Build_Test_Pack')

# Build instance corresponding to Problem 6.7.
# Must be relabeled before used.
instance_problem_6_7 = nx.DiGraph()
instance_problem_6_7.add_node(3, processing_time=1,  # Forming
							  external_inbound_cst=1,
							  holding_cost=2)
instance_problem_6_7.add_node(2, processing_time=1,  # Firing
							  holding_cost=3)
instance_problem_6_7.add_node(1, processing_time=2,  # Glazing
							  external_demand_mean=45,
							  external_demand_standard_deviation=10,
							  external_outbound_cst=0,
							  demand_bound_constant=4,
							  holding_cost=4)
instance_problem_6_7.add_edge(3, 2)
instance_problem_6_7.add_edge(2, 1)

# Build instance corresponding to Problem 6.9.
# Must be relabeled before used.
instance_problem_6_9 = nx.DiGraph()
instance_problem_6_9.add_node(1, processing_time=7,
							  holding_cost=220 * 0.2 / 365,
							  demand_bound_constant=4,
							  external_outbound_cst=3,
							  external_demand_mean=22.0,
							  external_demand_standard_deviation=4.1)
instance_problem_6_9.add_node(2, processing_time=7,
							  holding_cost=140 * 0.2 / 365,
							  demand_bound_constant=4,
							  external_outbound_cst=3,
							  external_demand_mean=15.3,
							  external_demand_standard_deviation=6.2)
instance_problem_6_9.add_node(3, processing_time=21,
							  holding_cost=90 * 0.2 / 365,
							  demand_bound_constant=4)
instance_problem_6_9.add_node(4, processing_time=3,
							  holding_cost=5 * 0.2 / 365,
							  demand_bound_constant=4)
instance_problem_6_9.add_node(5, processing_time=8,
							  holding_cost=20 * 0.2 / 365,
							  demand_bound_constant=4)
instance_problem_6_9.add_node(6, processing_time=2,
							  holding_cost=7.5 * 0.2 / 365,
							  demand_bound_constant=4)
instance_problem_6_9.add_edge(6, 5)
instance_problem_6_9.add_edge(4, 3)
instance_problem_6_9.add_edge(5, 3)
instance_problem_6_9.add_edge(3, 1)
instance_problem_6_9.add_edge(3, 2)


# Build single-stage instance.
instance_single_stage = nx.DiGraph()
instance_single_stage.add_node(1, processing_time=1,
                     external_inbound_cst=0,
					 external_outbound_cst=0,
                     holding_cost=1,
                     demand_bound_constant=2,
                     external_demand_standard_deviation=1)
