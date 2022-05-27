import unittest
import math
import random

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from stockpyl.disruption_process import *
from stockpyl.policy import Policy
from stockpyl.instances import load_instance


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_disruption_process   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestDisruptionProcessEq(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDisruptionProcessEq', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDisruptionProcessEq', 'tear_down_class()')

	def test_true(self):
		"""Test that DisruptionProcess.__eq__() correctly returns True when objects are equal.
		"""
		print_status('TestDisruptionProcessEq', 'test_true()')

		dp1 = DisruptionProcess(random_process_type='M', disruption_type='OP', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(random_process_type='M', disruption_type='OP', disruption_probability=0.1, recovery_probability=0.2)
		eq = dp1 == dp2
		self.assertTrue(eq)

		dp1 = DisruptionProcess(random_process_type='E', disruption_state_list=[True, False, False, True, False])
		dp2 = DisruptionProcess(random_process_type='E', disruption_state_list=[True, False, False, True, False])
		eq = dp1 == dp2
		self.assertTrue(eq)

	def test_false(self):
		"""Test that DisruptionProcess.__eq__() correctly returns False when objects are not equal.
		"""
		print_status('TestDisruptionProcessEq', 'test_false()')

		dp1 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.3)
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(random_process_type='M', disruption_probability=0.05, recovery_probability=0.2)
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(random_process_type='M', disruption_type='RP', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(random_process_type='M', disruption_type='OP', disruption_probability=0.1, recovery_probability=0.2)
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(random_process_type='M', disruption_type='RP', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.2)
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(random_process_type='E', disruption_state_list=[True, True, False, True, False])
		dp2 = DisruptionProcess(random_process_type='E', disruption_state_list=[True, False, False, True, False])
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(random_process_type='E', disruption_state_list=[True, True, False, True, False])
		dp2 = DisruptionProcess(random_process_type='E', disruption_state_list=[True, True, False, True, False, False])
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(random_process_type='E', disruption_state_list=[True, True, False, True, False, False])
		eq = dp1 == dp2
		self.assertFalse(eq)


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

		dp1 = DisruptionProcess()
		dp2 = DisruptionProcess()
		dp2.initialize()
		self.assertEqual(dp1, dp2)

		dp1 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess()
		dp1.initialize()
		self.assertEqual(dp1, dp2)

		dp1 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess()
		dp1.initialize(overwrite=False)
		self.assertNotEqual(dp1, dp2)

	def test_missing_values(self):
		"""Test that initialize() correctly leaves attributes in place if object already contains
		those attributes.
		"""
		print_status('TestInitialize', 'test_missing_values()')

		# In this instance, disruption process at node 3 is missing the ``disruption_probability`` attribute.
		# TODO: rename file to test_disruption_process_TestInitialize_data
		network = load_instance("missing_disruption_probability", "tests/additional_files/test_disruption_process_TestCopyFrom_data.json", initialize_missing_attributes=False)
		dp1 = network.get_node_from_index(3).disruption_process
		dp1.initialize(overwrite=False)
		dp2 = DisruptionProcess(random_process_type='M', disruption_type='SP', disruption_probability=None, recovery_probability=0.4)
		self.assertEqual(dp1, dp2)

		network = load_instance("missing_disruption_probability", "tests/additional_files/test_disruption_process_TestCopyFrom_data.json", initialize_missing_attributes=False)
		dp1 = network.get_node_from_index(3).disruption_process
		dp1.initialize(overwrite=True)
		dp2 = DisruptionProcess()
		self.assertEqual(dp1, dp2)

		# In this instance, disruption process at node 1 is missing the ``random_process_type`` attribute.
		network = load_instance("missing_type", "tests/additional_files/test_disruption_process_TestCopyFrom_data.json")
		dp1 = network.get_node_from_index(1).disruption_process
		dp1.initialize(overwrite=False)
		dp2 = DisruptionProcess(random_process_type=None, disruption_type='SP', disruption_probability=0.1, recovery_probability=0.4)
		self.assertEqual(dp1, dp2)


class TestCopyFrom(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCopyFrom', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCopyFrom', 'tear_down_class()')

	def test_copy(self):
		"""Test that copy_from correctly copies from a few different objects.
		"""
		print_status('TestCopyFrom', 'test_copy()')

		dp1 = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.6)
		dp2 = DisruptionProcess()
		dp2.copy_from(dp1)
		self.assertEqual(dp1, dp2)

		dp1 = DisruptionProcess(random_process_type='E', disruption_type='OP', disruption_state_list=[False, True, True, False])
		dp2 = DisruptionProcess()
		dp2.copy_from(dp1)
		self.assertEqual(dp1, dp2)

	def test_missing_values(self):
		"""Test that TestCopyFrom correctly leaves attributes in place if source does
		not contain those attributes.
		"""
		print_status('TestCopyFrom', 'test()')

		# In this instance, disruption process at node 1 is missing the ``disruption_probability`` attribute.
		network = load_instance("missing_base_stock_level", "tests/additional_files/test_policy_TestCopyFrom_data.json")
		dp1 = network.get_node_from_index(1).disruption_process
		dp2 = DisruptionProcess()
		dp2.copy_from(dp1)
		dp1.disruption_probability = None # add attribute back, at default value
		self.assertEqual(dp1, dp2)

		# In this instance, disruption process at node 3 is missing the ``random_process_type`` attribute.
		network = load_instance("missing_type", "tests/additional_files/test_policy_TestCopyFrom_data.json")
		dp1 = network.get_node_from_index(3).disruption_process
		dp2 = DisruptionProcess()
		dp2.copy_from(dp1)
		dp1.random_process_type = None # add attribute back, at default value
		self.assertEqual(dp1, dp2)


class TestValidateParameters(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestValidateParameters', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestValidateParameters', 'tear_down_class()')

	def test_markovian(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for Markovian disruptions.
		"""
		print_status('TestValidateParameters', 'test_markovian()')

		dp = DisruptionProcess()
		dp.random_process_type = 'M'
		dp.disruption_probability = -3
		dp.recovery_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.random_process_type = 'M'
		dp.disruption_probability = 1.5
		dp.recovery_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.random_process_type = 'M'
		dp.disruption_probability = 0.5
		dp.recovery_probability = -3
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.random_process_type = 'M'
		dp.disruption_probability = 0.5
		dp.recovery_probability = 1.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.random_process_type = 'M'
		dp.disruption_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.random_process_type = 'M'
		dp.recovery_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

	def test_explicit(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for explicit disruptions.
		"""
		print_status('TestValidateParameters', 'test_explicit()')

		dp = DisruptionProcess()
		dp.random_process_type = 'E'
		dp.disruption_state_list = None
		with self.assertRaises(AttributeError):
			dp.validate_parameters()


class TestDisruptionProcessRepr(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDisruptionProcessRepr', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDisruptionProcessRepr', 'tear_down_class()')

	def test_none(self):
		"""Test that DisruptionProcess.__repr__() correctly returns disruption process string
		when random_process_type is None.
		"""
		print_status('TestDisruptionProcessRepr', 'test_none()')

		dp = DisruptionProcess()
		dp.random_process_type = None

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(None)")

	def test_markovian(self):
		"""Test that DisruptionProcess.__repr__() correctly returns disruption process string
		when random_process_type is 'M'.
		"""
		print_status('TestDisruptionProcessRepr', 'test_markovian()')

		dp = DisruptionProcess()
		dp.random_process_type = 'M'
		dp.disruption_type = 'OP'
		dp.disruption_probability = 0.1
		dp.recovery_probability = 0.2

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(OP, M: disruption_probability=0.100000, recovery_probability=0.200000)")

	def test_explicit(self):
		"""Test that DisruptionProcess.__repr__() correctly returns disruption process string
		when random_process_type is 'E'.
		"""
		print_status('TestDisruptionProcessRepr', 'test_explicit()')

		dp = DisruptionProcess()
		dp.random_process_type = 'E'
		dp.disruption_type = 'SP'
		dp.disruption_state_list = False

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(SP, E: disruption_state_list=False)")

		dp = DisruptionProcess()
		dp.random_process_type = 'E'
		dp.disruption_type = 'SP'
		dp.disruption_state_list = [False, True, True, False]

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(SP, E: disruption_state_list=[False, True, True, False])")

		dp = DisruptionProcess()
		dp.random_process_type = 'E'
		dp.disruption_type = 'SP'
		dp.disruption_state_list = 5 * [False, True, True, False]

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(SP, E: disruption_state_list=[False, True, True, False, False, True, True, False]...)")


class TestUpdateDisruptionState(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestUpdateDisruptionState', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestUpdateDisruptionState', 'tear_down_class()')

	def test_markovian(self):
		"""Test that update_disruption_state() produces correct disruption states on average for 
		Markovian disruptions.
		"""
		print_status('TestUpdateDisruptionState', 'test_explicit()')

		NUM_TRIALS = 1000

		np.random.seed(42)

		disruption_probability = 0.1
		recovery_probability = 0.2
		z = 1.96

		dp = DisruptionProcess(random_process_type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
		num_disrupted = 0
		for _ in range(NUM_TRIALS):
			dp.disrupted = False
			dp.update_disruption_state()
			if dp.disrupted:
				num_disrupted += 1
		p_hat = num_disrupted / NUM_TRIALS
		ci_lo = p_hat - z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		ci_hi = p_hat + z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		self.assertTrue(ci_lo <= dp.disruption_probability <= ci_hi)

		dp = DisruptionProcess(random_process_type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
		num_disrupted = 0
		for _ in range(NUM_TRIALS):
			dp.disrupted = True
			dp.update_disruption_state()
			if dp.disrupted:
				num_disrupted += 1
		p_hat = 1 - num_disrupted / NUM_TRIALS
		ci_lo = p_hat - z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		ci_hi = p_hat + z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		self.assertTrue(ci_lo <= dp.recovery_probability <= ci_hi)

		disruption_probability = 0.005
		recovery_probability = 0.4
		z = 1.96

		dp = DisruptionProcess(random_process_type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
		num_disrupted = 0
		for _ in range(NUM_TRIALS):
			dp.disrupted = False
			dp.update_disruption_state()
			if dp.disrupted:
				num_disrupted += 1
		p_hat = num_disrupted / NUM_TRIALS
		ci_lo = p_hat - z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		ci_hi = p_hat + z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		self.assertTrue(ci_lo <= dp.disruption_probability <= ci_hi)

		dp = DisruptionProcess(random_process_type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
		num_disrupted = 0
		for _ in range(NUM_TRIALS):
			dp.disrupted = True
			dp.update_disruption_state()
			if dp.disrupted:
				num_disrupted += 1
		p_hat = 1 - num_disrupted / NUM_TRIALS
		ci_lo = p_hat - z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		ci_hi = p_hat + z * math.sqrt(p_hat * (1 - p_hat) / NUM_TRIALS)
		self.assertTrue(ci_lo <= dp.recovery_probability <= ci_hi)

	def test_explicit(self):
		"""Test that update_disruption_state() produces correct disruption states for explicit disruptions.
		"""
		print_status('TestUpdateDisruptionState', 'test_explicit()')

		dp = DisruptionProcess()
		dp.random_process_type = 'E'
		dp.disruption_state_list = False
		dp.update_disruption_state()
		self.assertFalse(dp.disrupted)

		dp = DisruptionProcess()
		dp.random_process_type = 'E'
		dp.disruption_state_list = [False, True, True, False]
		dp.update_disruption_state(period=5)
		self.assertTrue(dp.disrupted)

		dp = DisruptionProcess()
		dp.random_process_type = 'E'
		dp.disruption_state_list = [False, True, True, False]
		dp.update_disruption_state(period=3)
		self.assertFalse(dp.disrupted)


class TestSteadyStateProbabilities(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSteadyStateProbabilities', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSteadyStateProbabilities', 'tear_down_class()')

	def test_markovian(self):
		"""Test stead_state_probabilities() for Markovian disruptions.
		"""
		print_status('TestSteadyStateProbabilities', 'test_markovian()')

		dp = DisruptionProcess(random_process_type='M', disruption_probability=0.1, recovery_probability=0.2)
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 0.2 / 0.3)
		self.assertAlmostEqual(pi_d, 0.1 / 0.3)

		dp = DisruptionProcess(random_process_type='M', disruption_probability=0.005, recovery_probability=0.4)
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 0.4 / 0.405)
		self.assertAlmostEqual(pi_d, 0.005 / 0.405)

	def test_explicit(self):
		"""Test stead_state_probabilities() for explicit disruptions.
		"""
		print_status('TestSteadyStateProbabilities', 'test_explicit()')

		dp = DisruptionProcess(random_process_type='E', disruption_state_list=[False, True, True, False, False, True, False])
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 4/7)
		self.assertAlmostEqual(pi_d, 3/7)

		dp = DisruptionProcess(random_process_type='E', disruption_state_list=[False, True, True, False, False, True, False, False, False, False, True, True, True, False])
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 8/14)
		self.assertAlmostEqual(pi_d, 6/14)

