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


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestPolicyInit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPolicyInit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPolicyInit', 'tear_down_class()')

	def test_init(self):
		"""Test that Policy.__init__() correctly raises errors on incorrect parameters.
		"""
		print_status('TestPolicyInit', 'test_init()')

		# Negative order quantities.
		with self.assertRaises(AssertionError):
			_ = Policy(InventoryPolicyType.r_Q, 100, -5)
		with self.assertRaises(AssertionError):
			_ = Policy(InventoryPolicyType.FIXED_QUANTITY, -100)

		# s > S.
		with self.assertRaises(AssertionError):
			_ = Policy(InventoryPolicyType.s_S, 50, 40)


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

		policy = Policy(InventoryPolicyType.BASE_STOCK, 105.3)
		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(BASE_STOCK: base_stock_level=105.30)")

	def test_r_Q(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_r_Q()')

		policy = Policy(InventoryPolicyType.r_Q, 45.3, 17.4)
		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(r_Q: reorder_point=45.30, order_quantity=17.40)")

	def test_s_S(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyRepr', 'test_s_S()')

		policy = Policy(InventoryPolicyType.s_S, 45.3, 117.4)
		policy_str = policy.__repr__()
		self.assertEqual(policy_str, "Policy(s_S: reorder_point=45.30, order_up_to_level=117.40)")


class TestPolicyStr(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPolicyStr', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPolicyStr', 'tear_down_class()')

	def test_base_stock(self):
		"""Test that Policy.__str__() correctly returns policy string for
		base-stock policy.
		"""
		print_status('TestPolicyStr', 'test_base_stock()')

		policy = Policy(InventoryPolicyType.BASE_STOCK, 105.3)
		policy_str = policy.__str__()
		self.assertEqual(policy_str, "Policy(BASE_STOCK: base_stock_level=105.30)")

	def test_r_Q(self):
		"""Test that Policy.__str__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyStr', 'test_r_Q()')

		policy = Policy(InventoryPolicyType.r_Q, 45.3, 17.4)
		policy_str = policy.__str__()
		self.assertEqual(policy_str, "Policy(r_Q: reorder_point=45.30, order_quantity=17.40)")

	def test_s_S(self):
		"""Test that Policy.__repr__() correctly returns policy string for
		(r,Q) policy.
		"""
		print_status('TestPolicyStr', 'test_s_S()')

		policy = Policy(InventoryPolicyType.s_S, 45.3, 117.4)
		policy_str = policy.__str__()
		self.assertEqual(policy_str, "Policy(s_S: reorder_point=45.30, order_up_to_level=117.40)")


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

		policy = Policy(InventoryPolicyType.BASE_STOCK, 100)
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

		policy = Policy(InventoryPolicyType.r_Q, 100, 200)
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

		policy = Policy(InventoryPolicyType.s_S, 50, 100)
		q1 = policy.get_order_quantity_s_S(15)
		self.assertEqual(q1, 85)
		q2 = policy.get_order_quantity_s_S(-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity_s_S(70)
		self.assertEqual(q3, 0)

	def test_fixed_quantity(self):
		"""Test that get_order_quantity() returns correct order quantity
		under a fixed-quantity policy.
		"""
		print_status('TestGetOrderQuantity', 'test_fixed_quantity()')

		policy = Policy(InventoryPolicyType.FIXED_QUANTITY, 100)
		q1 = policy.get_order_quantity_fixed_quantity()
		self.assertEqual(q1, 100)


class TestGetOrderQuantityBaseStock(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetOrderQuantityBaseStock', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetOrderQuantityBaseStock', 'tear_down_class()')

	def test(self):
		"""Test that get_order_quantity_base_stock() returns correct order
		quantity for a few instances.
		"""
		print_status('TestGetOrderQuantityBaseStock', 'test()')

		policy = Policy(InventoryPolicyType.BASE_STOCK, 100)
		q1 = policy.get_order_quantity_base_stock(85)
		self.assertEqual(q1, 15)
		q2 = policy.get_order_quantity_base_stock(-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity_base_stock(140)
		self.assertEqual(q3, 0)


class TestGetOrderQuantityrQ(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetOrderQuantityrQ', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetOrderQuantityrQ', 'tear_down_class()')

	def test(self):
		"""Test that get_order_quantity_r_Q() returns correct order
		quantity for a few instances.
		"""
		print_status('TestGetOrderQuantityrQ', 'test()')

		policy = Policy(InventoryPolicyType.r_Q, 100, 200)
		q1 = policy.get_order_quantity_r_Q(75)
		self.assertEqual(q1, 200)
		q2 = policy.get_order_quantity_r_Q(-20)
		self.assertEqual(q2, 200)
		q3 = policy.get_order_quantity_r_Q(140)
		self.assertEqual(q3, 0)


class TestGetOrderQuantitysS(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetOrderQuantitysS', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetOrderQuantitysS', 'tear_down_class()')

	def test(self):
		"""Test that get_order_quantity_s_S() returns correct order
		quantity for a few instances.
		"""
		print_status('TestGetOrderQuantitysS', 'test()')

		policy = Policy(InventoryPolicyType.s_S, 50, 100)
		q1 = policy.get_order_quantity_s_S(15)
		self.assertEqual(q1, 85)
		q2 = policy.get_order_quantity_s_S(-20)
		self.assertEqual(q2, 120)
		q3 = policy.get_order_quantity_s_S(70)
		self.assertEqual(q3, 0)


class TestGetOrderQuantityFixedQuantity(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetOrderQuantityFixedQuantity', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetOrderQuantityFixedQuantity', 'tear_down_class()')

	def test(self):
		"""Test that get_order_quantity_fixed_quantity() returns correct order
		quantity.
		"""
		print_status('TestGetOrderQuantityFixedQuantity', 'test()')

		policy = Policy(InventoryPolicyType.FIXED_QUANTITY, 100)
		q1 = policy.get_order_quantity_fixed_quantity()
		self.assertEqual(q1, 100)

