import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from stockpyl.policy import *


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

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

	def test_s_S(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for (s,S) policy.
		"""
		print_status('TestValidateParameters', 'test_s_S()')

		policy = Policy()
		policy.type = 'sS'
		policy.reorder_point = 10

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

		policy = Policy()
		policy.type = 'sS'
		policy.order_quantity = 10

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

		policy = Policy()
		policy.type = 'sS'
		policy.reorder_point = 20
		policy.order_quantity = 10

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

	def test_r_Q(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for (r,Q) policy.
		"""
		print_status('TestValidateParameters', 'test_r_Q()')

		policy = Policy()
		policy.type = 'rQ'
		policy.reorder_point = 10

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

		policy = Policy()
		policy.type = 'rQ'
		policy.order_quantity = 10

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

	def test_echelon_base_stock(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for echelon base-stock policy.
		"""
		print_status('TestValidateParameters', 'test_echelon_base_stock()')

		policy = Policy()
		policy.type = 'EBS'

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

	def test_balanced_echelon_base_stock(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for balanced echelon base-stock policy.
		"""
		print_status('TestValidateParameters', 'test_balanced_echelon_base_stock()')

		policy = Policy()
		policy.type = 'BEBS'

		with self.assertRaises(AssertionError):
			policy.validate_parameters()

