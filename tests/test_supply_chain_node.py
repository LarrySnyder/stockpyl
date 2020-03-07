import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from inventory.supply_chain_node import *

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_supply_chain_node   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestSupplyChainNodeInit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainNodeInit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainNodeInit', 'tear_down_class()')

	# def test_init(self):
	# 	"""Test that SupplyChainNode.__init__() correctly raises errors on
	# 	incorrect parameters.
	# 	"""
	# 	print_status('TestPolicyInit', 'test_init()')


class TestSupplyChainNodeRepr(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainNodeRepr', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainNodeRepr', 'tear_down_class()')

	def test(self):
		"""Test that SupplyChainNode.__repr__() correctly returns node string.
		"""
		print_status('TestSupplyChainNodeRepr', 'test()')

		node1 = SupplyChainNode(index=1, name="foo")
		node_str1 = node1.__repr__()
		self.assertEqual(node_str1, "SupplyChainNode(index=1, name=foo)")

		node2 = SupplyChainNode(index=2)
		node_str2 = node2.__repr__()
		self.assertEqual(node_str2, "SupplyChainNode(index=2, name=None)")

		node3 = SupplyChainNode(name="bar")
		node_str3 = node3.__repr__()
		self.assertEqual(node_str3, "SupplyChainNode(index=None, name=bar)")

		node4 = SupplyChainNode()
		node_str4 = node4.__repr__()
		self.assertEqual(node_str4, "SupplyChainNode(index=None, name=None)")


class TestSupplyChainNodeStr(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainNodeStr', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainNodeStr', 'tear_down_class()')

	def test(self):
		"""Test that SupplyChainNode.__str__() correctly returns node string.
		"""
		print_status('TestSupplyChainNodeStr', 'test()')

		node1 = SupplyChainNode(index=1, name="foo")
		node_str1 = node1.__str__()
		self.assertEqual(node_str1, "SupplyChainNode(index=1, name=foo)")

		node2 = SupplyChainNode(index=2)
		node_str2 = node2.__str__()
		self.assertEqual(node_str2, "SupplyChainNode(index=2, name=None)")

		node3 = SupplyChainNode(name="bar")
		node_str3 = node3.__str__()
		self.assertEqual(node_str3, "SupplyChainNode(index=None, name=bar)")

		node4 = SupplyChainNode()
		node_str4 = node4.__str__()
		self.assertEqual(node_str4, "SupplyChainNode(index=None, name=None)")


