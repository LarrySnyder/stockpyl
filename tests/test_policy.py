import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from inventory.policy import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_policy   class : {:30s} function : {:30s}".format(class_name, function_name))


def setUpModule():
	"""Called once, before anything else in this module."""
	print_status('---', 'setUpModule()')


def tearDownModule():
	"""Called once, after everything else in this module."""
	print_status('---', 'tearDownModule()')


class TestPolicyRepr(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestPolicyRepr', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestPolicyRepr', 'tearDownClass()')

	def test_base_stock(self):
		"""Test that policy.__repr__() correctly displays policy string for
		base-stock policy.
		"""
		print_status('TestPolicyRepr', 'test_base_stock()')

		policy = Policy(InventoryPolicyType.BASE_STOCK, 105.3)
		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(BASE_STOCK: base_stock_level=105.30)")

	def test_r_Q(self):
		"""Test that policy.__repr__() correctly displays policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_r_Q()')

		policy = Policy(InventoryPolicyType.r_Q, 45.3, 17.4)
		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(r_Q: reorder_point=45.30, order_quantity=17.40)")

	def test_s_S(self):
		"""Test that policy.__repr__() correctly displays policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_s_S()')

		policy = Policy(InventoryPolicyType.s_S, 45.3, 117.4)
		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(s_S: reorder_point=45.30, order_up_to_level=117.40)")


class TestPolicyStr(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestPolicyStr', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestPolicyStr', 'tearDownClass()')

	def test_base_stock(self):
		"""Test that policy.__str__() correctly displays policy string for
		base-stock policy.
		"""
		print_status('TestPolicyStr', 'test_base_stock()')

		policy = Policy(InventoryPolicyType.BASE_STOCK, 105.3)
		policy_str = policy.__str__()
		self.assertEqual(policy_str, "Policy(BASE_STOCK: base_stock_level=105.30)")

	def test_r_Q(self):
		"""Test that policy.__str__() correctly displays policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyStr', 'test_r_Q()')

		policy = Policy(InventoryPolicyType.r_Q, 45.3, 17.4)
		policy_str = policy.__str__()
		self.assertEqual(policy_str, "Policy(r_Q: reorder_point=45.30, order_quantity=17.40)")

	def test_s_S(self):
		"""Test that policy.__repr__() correctly displays policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyStr', 'test_s_S()')

		policy = Policy(InventoryPolicyType.s_S, 45.3, 117.4)
		policy_str = policy.__str__()
		self.assertEqual(policy_str, "Policy(s_S: reorder_point=45.30, order_up_to_level=117.40)")

