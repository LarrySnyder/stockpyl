import networkx as nx

from pyinv.datatypes import *
from pyinv.demand_source import *


# Build 2-stage instance.
instance_2_stage = nx.DiGraph()
instance_2_stage.add_node(1, echelon_holding_cost=1,
						     stockout_cost=10,
						  	 lead_time=1,
						  	 demand_mean=10,
						  	 demand_standard_deviation=2,
						  	 initial_IL=0,
						  	 initial_orders=0,
						  	 initial_shipments=0,
						  	 order_lead_time=0,
						  	 shipment_lead_time=0,
						  	 demand_type='N',
						  	 supply_type=SupplyType.NONE)
instance_2_stage.add_node(2, echelon_holding_cost=1,
						  	 lead_time=1,
						  	 initial_IL=0,
						  	 initial_orders=0,
						  	 initial_shipments=0,
						  	 order_lead_time=0,
						  	 shipment_lead_time=0,
						  	 demand_type='N',
						  	 supply_type=SupplyType.UNLIMITED)
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
