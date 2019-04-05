import networkx as nx


# Build instance corresponding to network in Figure 6.12.
instance_2_stage = nx.DiGraph()
instance_2_stage.add_node(1, echelon_holding_cost=1,
						     stockout_cost=10,
						  	 lead_time=2,
						  	 demand_mean=100,
						  	 demand_standard_deviation=10)
instance_2_stage.add_node(2, echelon_holding_cost=0.5,
						  	 lead_time=1)
instance_2_stage.add_edge(2, 1)

