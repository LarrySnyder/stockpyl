import networkx as nx


# Build 2-stage instance.
instance_2_stage = nx.DiGraph()
instance_2_stage.add_node(1, echelon_holding_cost=1,
						     stockout_cost=10,
						  	 lead_time=2,
						  	 demand_mean=100,
						  	 demand_standard_deviation=10)
instance_2_stage.add_node(2, echelon_holding_cost=0.5,
						  	 lead_time=1)
instance_2_stage.add_edge(2, 1)

# Build instance corresponding to Example 6.1.
instance_example_6_1 = nx.DiGraph()
instance_example_6_1.add_node(1, echelon_holding_cost=3,
							  stockout_cost=37.12,
							  lead_time=1,
							  demand_mean=5,
							  demand_standard_deviation=1)
instance_example_6_1.add_node(2, echelon_holding_cost=2,
							  lead_time=1)
instance_example_6_1.add_node(3, echelon_holding_cost=2,
							  lead_time=2)
instance_example_6_1.add_edge(3, 2)
instance_example_6_1.add_edge(2, 1)

# Build instance corresponding to Problem 6.1.
instance_problem_6_1 = nx.DiGraph()
instance_problem_6_1.add_node(1, echelon_holding_cost=1,
							  stockout_cost=15,
							  lead_time=1,
							  demand_mean=100,
							  demand_standard_deviation=15)
instance_problem_6_1.add_node(2, echelon_holding_cost=1,
							  lead_time=1)
instance_problem_6_1.add_edge(2, 1)
