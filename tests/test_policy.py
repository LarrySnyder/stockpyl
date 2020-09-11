import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from pyinv.policy import *


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

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.BASE_STOCK,
											 base_stock_level=105.3)

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(BASE_STOCK: base_stock_level=105.30)")

	def test_r_Q(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_r_Q()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.r_Q,
											 reorder_point=45.3,
											 order_quantity=17.4)

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(r_Q: reorder_point=45.30, order_quantity=17.40)")

	def test_s_S(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_s_S()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.s_S,
											 reorder_point=45.3,
											 order_up_to_level=117.4)

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(s_S: reorder_point=45.30, order_up_to_level=117.40)")

	def test_fixed_quantity(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		fixed-quantity policy.
		"""
		print_status('TestPolicyRepr', 'test_fixed_quantity()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.FIXED_QUANTITY,
											 order_quantity=17.4)

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(FIXED_QUANTITY: order_quantity=17.40)")

	def test_echelon_base_stock(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		echelon base-stock policy.
		"""
		print_status('TestPolicyRepr', 'test_echelon_base_stock()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.ECHELON_BASE_STOCK,
											 base_stock_level=105.3)

		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(ECHELON_BASE_STOCK: echelon_base_stock_level=105.30)")


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

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.BASE_STOCK,
											 base_stock_level=100)

		q1 = policy.get_order_quantity(85)
		self.assertEqual(q1, 15)
		q2 = policy.get_order_quantity(-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity(140)
		self.assertEqual(q3, 0)

	def test_r_Q(self):
		"""Test that get_order_quantity() returns correct order quantity
		under an (r,Q) policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_r_Q()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.r_Q,
											 reorder_point=100,
											 order_quantity=200)

		q1 = policy.get_order_quantity(75)
		self.assertEqual(q1, 200)
		q2 = policy.get_order_quantity(-20)
		self.assertEqual(q2, 200)
		q3 = policy.get_order_quantity(140)
		self.assertEqual(q3, 0)

	def test_s_S(self):
		"""Test that get_order_quantity() returns correct order quantity
		under an (s,S) policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_s_S()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.s_S,
											 reorder_point=50,
											 order_up_to_level=100)

		q1 = policy.get_order_quantity(15)
		self.assertEqual(q1, 85)
		q2 = policy.get_order_quantity(-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity(70)
		self.assertEqual(q3, 0)

	def test_fixed_quantity(self):
		"""Test that get_order_quantity() returns correct order quantity
		under a fixed-quantity policy.
		"""
		print_status('TestGetOrderQuantity', 'test_fixed_quantity()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.FIXED_QUANTITY,
											 order_quantity=100)

		q1 = policy.get_order_quantity()
		self.assertEqual(q1, 100)

	def test_echelon_base_stock(self):
		"""Test that get_order_quantity() returns correct order quantity
		under an echelon base-stock policy for a few instances.
		"""
		print_status('TestGetOrderQuantity', 'test_echelon_base_stock()')

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.ECHELON_BASE_STOCK,
											 base_stock_level=100)

		q1 = policy.get_order_quantity(85)
		self.assertEqual(q1, 15)
		q2 = policy.get_order_quantity(-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity(140)
		self.assertEqual(q3, 0)

