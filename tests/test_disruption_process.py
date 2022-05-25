import unittest
import math
import random

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from stockpyl.disruption_process import *


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

		dp1 = DisruptionProcess(type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(type='M', disruption_probability=0.1, recovery_probability=0.2)
		eq = dp1 == dp2
		self.assertTrue(eq)

		dp1 = DisruptionProcess(type='E', disruption_state_list=[True, False, False, True, False])
		dp2 = DisruptionProcess(type='E', disruption_state_list=[True, False, False, True, False])
		eq = dp1 == dp2
		self.assertTrue(eq)

	def test_false(self):
		"""Test that DisruptionProcess.__eq__() correctly returns False when objects are not equal.
		"""
		print_status('TestDisruptionProcessEq', 'test_false()')

		dp1 = DisruptionProcess(type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(type='M', disruption_probability=0.1, recovery_probability=0.3)
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(type='M', disruption_probability=0.05, recovery_probability=0.2)
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(type='E', disruption_state_list=[True, True, False, True, False])
		dp2 = DisruptionProcess(type='E', disruption_state_list=[True, False, False, True, False])
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(type='E', disruption_state_list=[True, True, False, True, False])
		dp2 = DisruptionProcess(type='E', disruption_state_list=[True, True, False, True, False, False])
		eq = dp1 == dp2
		self.assertFalse(eq)

		dp1 = DisruptionProcess(type='M', disruption_probability=0.1, recovery_probability=0.2)
		dp2 = DisruptionProcess(type='E', disruption_state_list=[True, True, False, True, False, False])
		eq = dp1 == dp2
		self.assertFalse(eq)


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
		dp.type = 'M'
		dp.disruption_probability = -3
		dp.recovery_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.type = 'M'
		dp.disruption_probability = 1.5
		dp.recovery_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.type = 'M'
		dp.disruption_probability = 0.5
		dp.recovery_probability = -3
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.type = 'M'
		dp.disruption_probability = 0.5
		dp.recovery_probability = 1.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.type = 'M'
		dp.disruption_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

		dp = DisruptionProcess()
		dp.type = 'M'
		dp.recovery_probability = 0.5
		with self.assertRaises(AttributeError):
			dp.validate_parameters()

	def test_explicit(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for explicit disruptions.
		"""
		print_status('TestValidateParameters', 'test_explicit()')

		dp = DisruptionProcess()
		dp.type = 'E'
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
		when type is None.
		"""
		print_status('TestDisruptionProcessRepr', 'test_none()')

		dp = DisruptionProcess()
		dp.type = None

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(None)")

	def test_markovian(self):
		"""Test that DisruptionProcess.__repr__() correctly returns disruption process string
		when type is 'M'.
		"""
		print_status('TestDisruptionProcessRepr', 'test_markovian()')

		dp = DisruptionProcess()
		dp.type = 'M'
		dp.disruption_probability = 0.1
		dp.recovery_probability = 0.2

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(M: disruption_probability=0.100000, recovery_probability=0.200000)")

	def test_explicit(self):
		"""Test that DisruptionProcess.__repr__() correctly returns disruption process string
		when type is 'E'.
		"""
		print_status('TestDisruptionProcessRepr', 'test_explicit()')

		dp = DisruptionProcess()
		dp.type = 'E'
		dp.disruption_state_list = False

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(E: disruption_state_list=False)")

		dp = DisruptionProcess()
		dp.type = 'E'
		dp.disruption_state_list = [False, True, True, False]

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(E: disruption_state_list=[False, True, True, False])")

		dp = DisruptionProcess()
		dp.type = 'E'
		dp.disruption_state_list = 5 * [False, True, True, False]

		dp_str = dp.__repr__()
		self.assertEqual(dp_str, "DisruptionProcess(E: disruption_state_list=[False, True, True, False, False, True, True, False]...)")


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

		dp = DisruptionProcess(type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
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

		dp = DisruptionProcess(type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
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

		dp = DisruptionProcess(type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
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

		dp = DisruptionProcess(type='M', disruption_probability=disruption_probability, recovery_probability=recovery_probability)
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
		dp.type = 'E'
		dp.disruption_state_list = False
		dp.update_disruption_state()
		self.assertFalse(dp.disrupted)

		dp = DisruptionProcess()
		dp.type = 'E'
		dp.disruption_state_list = [False, True, True, False]
		dp.update_disruption_state(period=5)
		self.assertTrue(dp.disrupted)

		dp = DisruptionProcess()
		dp.type = 'E'
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

		dp = DisruptionProcess(type='M', disruption_probability=0.1, recovery_probability=0.2)
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 0.2 / 0.3)
		self.assertAlmostEqual(pi_d, 0.1 / 0.3)

		dp = DisruptionProcess(type='M', disruption_probability=0.005, recovery_probability=0.4)
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 0.4 / 0.405)
		self.assertAlmostEqual(pi_d, 0.005 / 0.405)

	def test_explicit(self):
		"""Test stead_state_probabilities() for explicit disruptions.
		"""
		print_status('TestSteadyStateProbabilities', 'test_explicit()')

		dp = DisruptionProcess(type='E', disruption_state_list=[False, True, True, False, False, True, False])
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 4/7)
		self.assertAlmostEqual(pi_d, 3/7)

		dp = DisruptionProcess(type='E', disruption_state_list=[False, True, True, False, False, True, False, False, False, False, True, True, True, False])
		pi_u, pi_d = dp.steady_state_probabilities()
		self.assertAlmostEqual(pi_u, 8/14)
		self.assertAlmostEqual(pi_d, 6/14)

