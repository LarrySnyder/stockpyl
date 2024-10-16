# Misc. unit tests based on issues posted at https://github.com/LarrySnyder/stockpyl/issues.

import unittest

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import lognorm

from stockpyl.supply_chain_network import network_from_edges
from stockpyl.supply_chain_product import SupplyChainProduct
from stockpyl.policy import Policy
from stockpyl.sim import simulation
from stockpyl.sim_io import write_results

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_issues   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestIssue171(unittest.TestCase):
	# https://github.com/LarrySnyder/stockpyl/issues/171 

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIssue171', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIssue171', 'tear_down_class()')

	def test_multisource_orders(self):
		"""Test that total order quantity is correct across suppliers. 
		(Issue 171 reported that order was duplicated rather than split or assigned to one supplier.)
		"""
		print_status('TestIssue171', 'test_multisource_orders()')

		network = network_from_edges(
			edges=[(2, 1), (3, 1)],
			node_order_in_lists=[1, 2, 3],
			local_holding_cost=[2,4,2],
			stockout_cost=[50, 25, 25],
			demand_type='UD',
			lo=1,
			hi=5,
			shipment_lead_time=[0, 0, 0],
			order_lead_time=[0, 0, 0]
		)

		nodes = {n.index: n for n in network.nodes}

		products = {10: SupplyChainProduct(index=10), 20: SupplyChainProduct(index=20)}
		products[10].set_bill_of_materials(raw_material=20, num_needed=3)

		nodes[1].add_product(products[10])
		nodes[2].add_product(products[20])
		nodes[3].add_product(products[20])

		products[10].inventory_policy = Policy(type='BS', base_stock_level=10, node=nodes[1], product=products[10])
		nodes[2].inventory_policy = {20: Policy(type='BS', base_stock_level=12, node=nodes[2], product=products[20])}
		nodes[3].inventory_policy = {20: Policy(type='BS', base_stock_level=22, node=nodes[3], product=products[20])}

		_ = simulation(network, 100, rand_seed=17)

		self.assertEqual(nodes[1].state_vars[0].order_quantity[2][20], 6)
		self.assertEqual(nodes[1].state_vars[0].order_quantity[3][20], 0)
		self.assertEqual(nodes[1].state_vars[3].order_quantity[2][20], 15)
		self.assertEqual(nodes[1].state_vars[3].order_quantity[3][20], 0)

	def test_multisource_IS(self):
		"""Test that inbound shipments are recorded in the correct period from both suppliers. 
		(Issue 171 reported that one supplier had IS in the correct period and one had it 1 period late.)
		"""
		print_status('TestIssue171', 'test_multisource_IS()')

		network = network_from_edges(
		edges=[(2, 1), (3, 1)],
		node_order_in_lists=[1, 2, 3],
		local_holding_cost=[2,4,2],
		stockout_cost=[50, 25, 25],
		demand_type='UD', # discrete uniform distribution, for easier debugging
		lo=1,
		hi=5,
		shipment_lead_time=[0, 0, 0],
		order_lead_time=[0, 0, 0]
		)

		nodes = {n.index: n for n in network.nodes}

		products = {10: SupplyChainProduct(index=10), 20: SupplyChainProduct(index=20)}
		products[10].set_bill_of_materials(raw_material=20, num_needed=3)

		nodes[1].add_product(products[10])
		nodes[2].add_product(products[20])
		nodes[3].add_product(products[20])

		class MultisourcePolicy(Policy):
			def __init__(self, **kwargs):
				super().__init__(**kwargs)

			def get_order_quantity(self, product=None, order_capacity=None, include_raw_materials=False, inventory_position=None, echelon_inventory_position_adjusted=None):
				OQ_dict = super().get_order_quantity(product, order_capacity, include_raw_materials, inventory_position, echelon_inventory_position_adjusted)
				if isinstance(OQ_dict, dict):
					for rm_ind in self.node.raw_materials_by_product(product=None, return_indices=True, network_BOM=False):
						# Shortcut to suppliers for this RM.
						supp_inds = self.node.raw_material_suppliers_by_raw_material(raw_material=rm_ind, return_indices=True, network_BOM=False)
						# Get total order quantity for this RM.
						total_OQ = sum([OQ_dict[supp_ind][rm_ind] for supp_ind in supp_inds])
						# Split order evenly across suppliers.
						for supp_ind in supp_inds:
							OQ_dict[supp_ind][rm_ind] = total_OQ / len(supp_inds)
				return OQ_dict

		products[10].inventory_policy = MultisourcePolicy(type='BS', base_stock_level=10, node=nodes[1], product=products[10])
		nodes[2].inventory_policy = {20: Policy(type='BS', base_stock_level=12, node=nodes[2], product=products[20])}
		nodes[3].inventory_policy = {20: Policy(type='BS', base_stock_level=22, node=nodes[3], product=products[20])}

		_ = simulation(network, 100, rand_seed=17)

		self.assertEqual(nodes[1].state_vars[0].order_quantity[2][20], 3)
		self.assertEqual(nodes[1].state_vars[0].order_quantity[3][20], 3)
		self.assertEqual(nodes[1].state_vars[0].inbound_shipment[2][20], 3)
		self.assertEqual(nodes[1].state_vars[0].inbound_shipment[3][20], 3)
		self.assertEqual(nodes[1].state_vars[3].order_quantity[2][20], 7.5)
		self.assertEqual(nodes[1].state_vars[3].order_quantity[3][20], 7.5)
		self.assertEqual(nodes[1].state_vars[3].inbound_shipment[2][20], 7.5)
		self.assertEqual(nodes[1].state_vars[3].inbound_shipment[3][20], 7.5)

