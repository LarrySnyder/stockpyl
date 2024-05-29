import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from stockpyl.policy import *
from stockpyl.instances import load_instance
from stockpyl.supply_chain_node import SupplyChainNode


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_policy   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestPolicyEq(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPolicyEq', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPolicyEq', 'tear_down_class()')

	def test_true(self):
		"""Test that Policy.__eq__() correctly returns True when objects are equal.
		"""
		print_status('TestPolicyEq', 'test_true()')

		pol1 = Policy(type='rQ', reorder_point=45.3, order_quantity=17.4)
		pol2 = Policy(type='rQ', reorder_point=45.3, order_quantity=17.4)
		eq = pol1 == pol2
		self.assertTrue(eq)

		pol1 = Policy(type='BS', base_stock_level=60)
		pol2 = Policy(type='BS', base_stock_level=60)
		eq = pol1 == pol2
		self.assertTrue(eq)

	def test_false(self):
		"""Test that Policy.__eq__() correctly returns False when objects are not equal.
		"""
		print_status('TestPolicyEq', 'test_false()')

		pol1 = Policy(type='rQ', reorder_point=45.3, order_quantity=17.4)
		pol2 = Policy(type='rQ', reorder_point=45.3, order_quantity=12)
		eq = pol1 == pol2
		self.assertFalse(eq)

		pol1 = Policy(type='rQ', reorder_point=45.3, order_quantity=17.4)
		pol2 = Policy(type='rQ', reorder_point=45.3)
		eq = pol1 == pol2
		self.assertFalse(eq)

		pol1 = Policy(type='BS', base_stock_level=60)
		pol2 = Policy(type='BS', base_stock_level=50)
		eq = pol1 == pol2
		self.assertFalse(eq)

		pol1 = Policy(type='BS', base_stock_level=60)
		pol2 = Policy(type='BS')
		eq = pol1 == pol2
		self.assertFalse(eq)

		pol1 = Policy(type='BS', base_stock_level=60)
		pol2 = Policy(type='BS', reorder_point=40)
		eq = pol1 == pol2
		self.assertFalse(eq)
		
class TestPolicyRepr(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPolicyRepr', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPolicyRepr', 'tear_down_class()')

	def test_base_stock(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		base-stock policy.
		"""
		print_status('TestPolicyRepr', 'test_base_stock()')

		policy = Policy()
		policy.type = 'BS'
		policy.base_stock_level = 105.3

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(BS: base_stock_level=105.30)")

	def test_r_Q(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_r_Q()')

		policy = Policy()
		policy.type = 'rQ'
		policy.reorder_point = 45.3
		policy.order_quantity = 17.4

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(rQ: reorder_point=45.30, order_quantity=17.40)")

	def test_s_S(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_s_S()')

		policy = Policy()
		policy.type = 'sS'
		policy.reorder_point = 45.3
		policy.order_up_to_level = 117.4

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(sS: reorder_point=45.30, order_up_to_level=117.40)")

	def test_fixed_quantity(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		fixed-quantity policy.
		"""
		print_status('TestPolicyRepr', 'test_fixed_quantity()')

		policy = Policy()
		policy.type = 'FQ'
		policy.order_quantity = 17.4

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(FQ: order_quantity=17.40)")

	def test_echelon_base_stock(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		echelon base-stock policy.
		"""
		print_status('TestPolicyRepr', 'test_echelon_base_stock()')

		policy = Policy()
		policy.type = 'EBS'
		policy.base_stock_level = 105.3

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(EBS: base_stock_level=105.30)")


class TestGetOrderQuantity(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetOrderQuantity', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetOrderQuantity', 'tear_down_class()')

	def test_base_stock(self):
		"""Test that get_order_quantity() returns correct order quantity
		under a base-stock policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_base_stock()')

		policy = Policy()
		policy.type = 'BS'
		policy.base_stock_level = 100

		q1 = policy.get_order_quantity(inventory_position=85)
		self.assertEqual(q1, 15)
		q2 = policy.get_order_quantity(inventory_position=-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity(inventory_position=140)
		self.assertEqual(q3, 0)

	def test_r_Q(self):
		"""Test that get_order_quantity() returns correct order quantity
		under an (r,Q) policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_r_Q()')

		policy = Policy()
		policy.type = 'rQ'
		policy.reorder_point = 100
		policy.order_quantity = 200

		q1 = policy.get_order_quantity(inventory_position=75)
		self.assertEqual(q1, 200)
		q2 = policy.get_order_quantity(inventory_position=-20)
		self.assertEqual(q2, 200)
		q3 = policy.get_order_quantity(inventory_position=140)
		self.assertEqual(q3, 0)

	def test_s_S(self):
		"""Test that get_order_quantity() returns correct order quantity
		under an (s,S) policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_s_S()')

		policy = Policy()
		policy.type = 'sS'
		policy.reorder_point = 50
		policy.order_up_to_level = 100

		q1 = policy.get_order_quantity(inventory_position=15)
		self.assertEqual(q1, 85)
		q2 = policy.get_order_quantity(inventory_position=-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity(inventory_position=70)
		self.assertEqual(q3, 0)

	def test_fixed_quantity(self):
		"""Test that get_order_quantity() returns correct order quantity
		under a fixed-quantity policy.
		"""
		print_status('TestGetOrderQuantity', 'test_fixed_quantity()')

		policy = Policy()
		policy.type = 'FQ'
		policy.order_quantity = 100

		q1 = policy.get_order_quantity()
		self.assertEqual(q1, 100)

	def test_echelon_base_stock(self):
		"""Test that get_order_quantity() returns correct order quantity
		under an echelon base-stock policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_echelon_base_stock()')

		policy = Policy()
		policy.type = 'EBS'
		policy.base_stock_level = 100

		q1 = policy.get_order_quantity(inventory_position=85)
		self.assertEqual(q1, 15)
		q2 = policy.get_order_quantity(inventory_position=-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity(inventory_position=140)
		self.assertEqual(q3, 0)

	def test_balanced_echelon_base_stock(self):
		"""Test that get_order_quantity() returns correct order quantity
		under a balanced echelon base-stock policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_balanced_echelon_base_stock()')

		policy = Policy()
		policy.type = 'BEBS'
		policy.base_stock_level = 100

		q = policy.get_order_quantity(inventory_position=85, echelon_inventory_position_adjusted=40)
		self.assertEqual(q, 0)
		q = policy.get_order_quantity(inventory_position=45, echelon_inventory_position_adjusted=200)
		self.assertEqual(q, 55)
		q = policy.get_order_quantity(inventory_position=-20, echelon_inventory_position_adjusted=80)
		self.assertEqual(q, 100)
		q = policy.get_order_quantity(inventory_position=140, echelon_inventory_position_adjusted=200)
		self.assertEqual(q, 0)


class TestInitialize(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestInitialize', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestInitialize', 'tear_down_class()')

	def test_initialize(self):
		"""Test that initialize() correctly initializes.
		"""
		print_status('TestInitialize', 'test_copy()')

		pol1 = Policy()
		pol2 = Policy()
		pol1.initialize()
		self.assertEqual(pol1, pol2)

		pol1 = Policy(type='BS', base_stock_level=25)
		pol2 = Policy()
		pol1.initialize()
		self.assertEqual(pol1, pol2)

class TestToDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestToDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestToDict', 'tear_down_class()')

	def test_base_stock(self):
		"""Test that to_dict() correctly converts a base-stock Policy object to dict.
		"""
		print_status('TestToDict', 'test_base_stock()')

		pol = Policy()
		pol.type = 'BS'
		pol.base_stock_level = 100
		pol_dict = pol.to_dict()
		correct_dict = {
			'type': 'BS',
			'node': None,
			'product': None,
			'base_stock_level': 100,
			'order_quantity': None,
			'reorder_point': None,
			'order_up_to_level': None
		}
		self.assertDictEqual(pol_dict, correct_dict)

	def test_base_stock_with_node(self):
		"""Test that to_dict() correctly converts a base-stock Policy object to dict
		when its node attribute is set to a node object.
		"""
		print_status('TestToDict', 'test_base_stock_with_node()')

		node = SupplyChainNode(index=5, local_holding_cost=1, stockout_cost=10)

		pol = Policy()
		pol.type = 'BS'
		pol.node = node
		pol.base_stock_level = 100
		pol_dict = pol.to_dict()
		correct_dict = {
			'type': 'BS',
			'node': 5,
			'product': None,
			'base_stock_level': 100,
			'order_quantity': None,
			'reorder_point': None,
			'order_up_to_level': None
		}
		self.assertDictEqual(pol_dict, correct_dict)

	def test_s_S(self):
		"""Test that to_dict() correctly converts an (s,S) Policy object to dict.
		"""
		print_status('TestToDict', 'test_s_S()')

		pol = Policy()
		pol.type = 'sS'
		pol.node = None
		pol.reorder_point = 100
		pol.order_up_to_level = 500
		pol_dict = pol.to_dict()
		correct_dict = {
			'type': 'sS',
			'node': None,
			'product': None,
			'base_stock_level': None,
			'order_quantity': None,
			'reorder_point': 100,
			'order_up_to_level': 500
		}
		self.assertDictEqual(pol_dict, correct_dict)


class TestFromDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestFromDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestFromDict', 'tear_down_class()')

	def test_base_stock(self):
		"""Test that from_dict() correctly converts a base-stock Policy object from a dict.
		"""
		print_status('TestFromDict', 'test_base_stock()')

		the_dict = {
			'type': 'BS',
			'node': None,
			'base_stock_level': 100,
			'order_quantity': None,
			'reorder_point': None,
			'order_up_to_level': None
		}
		pol = Policy.from_dict(the_dict)

		correct_pol = Policy()
		correct_pol.type = 'BS'
		correct_pol.base_stock_level = 100

		self.assertEqual(pol, correct_pol)

	def test_s_S(self):
		"""Test that from_dict() correctly converts an (s,S) Policy object from a dict.
		"""
		print_status('TestFromDict', 'test_s_S()')

		the_dict = {
			'type': 'sS',
			'node': None,
			'base_stock_level': None,
			'order_quantity': None,
			'reorder_point': 100,
			'order_up_to_level': 500
		}
		pol = Policy.from_dict(the_dict)

		correct_pol = Policy()
		correct_pol.type = 'sS'
		correct_pol.node = None
		correct_pol.reorder_point = 100
		correct_pol.order_up_to_level = 500

		self.assertEqual(pol, correct_pol)

	def test_missing_values(self):
		"""Test that from_dict() correctly fills attributes with defaults if missing.
		"""
		print_status('TestFromDict', 'test_missing_values()')

		# In this instance, policy at node 3 is missing the ``base_stock_level`` attribute.
		network1 = load_instance("missing_base_stock_level", "tests/additional_files/test_policy_TestFromDict_data.json")
		network2 = load_instance("example_6_1")
		pol1 = network1.nodes_by_index[3].inventory_policy
		pol2 = network2.nodes_by_index[3].inventory_policy
		pol2.base_stock_level = Policy._DEFAULT_VALUES['_base_stock_level']
		self.assertEqual(pol1, pol2)

		# In this instance, policy at node 1 is missing the ``type`` attribute.
		network1 = load_instance("missing_type", "tests/additional_files/test_policy_TestFromDict_data.json")
		network2 = load_instance("example_6_1")
		pol1 = network1.nodes_by_index[1].inventory_policy
		pol2 = network2.nodes_by_index[1].inventory_policy
		pol2.type = Policy._DEFAULT_VALUES['_type']
		self.assertEqual(pol1, pol2)



class TestValidateParameters(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestValidateParameters', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestValidateParameters', 'tear_down_class()')

	def test_base_stock(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for base-stock policy.
		"""
		print_status('TestValidateParameters', 'test_base_stock()')

		policy = Policy()
		policy.type = 'BS'

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

	def test_s_S(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for (s,S) policy.
		"""
		print_status('TestValidateParameters', 'test_s_S()')

		policy = Policy()
		policy.type = 'sS'
		policy.reorder_point = 10

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

		policy = Policy()
		policy.type = 'sS'
		policy.order_quantity = 10

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

		policy = Policy()
		policy.type = 'sS'
		policy.reorder_point = 20
		policy.order_quantity = 10

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

	def test_r_Q(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for (r,Q) policy.
		"""
		print_status('TestValidateParameters', 'test_r_Q()')

		policy = Policy()
		policy.type = 'rQ'
		policy.reorder_point = 10

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

		policy = Policy()
		policy.type = 'rQ'
		policy.order_quantity = 10

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

	def test_echelon_base_stock(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for echelon base-stock policy.
		"""
		print_status('TestValidateParameters', 'test_echelon_base_stock()')

		policy = Policy()
		policy.type = 'EBS'

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

	def test_balanced_echelon_base_stock(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for balanced echelon base-stock policy.
		"""
		print_status('TestValidateParameters', 'test_balanced_echelon_base_stock()')

		policy = Policy()
		policy.type = 'BEBS'

		with self.assertRaises(AttributeError):
			policy.validate_parameters()

