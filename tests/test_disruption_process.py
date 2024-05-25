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


class TestToDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestToDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestToDict', 'tear_down_class()')

	def test_markovian(self):
		"""Test that to_dict() correctly converts a Markovian DisruptionProcess
		object to dict.
		"""
		print_status('TestToDict', 'test_markovian()')

		disruption_process = DisruptionProcess()
		disruption_process.random_process_type = 'M'
		disruption_process.disruption_probability = 0.1
		disruption_process.recovery_probability = 0.25
		disruption_process.disrupted = True
		dp_dict = disruption_process.to_dict()
		correct_dict = {
			'random_process_type': 'M',
			'disruption_type': 'OP',
			'disruption_probability': 0.1,
			'recovery_probability': 0.25,
			'disruption_state_list': None,
			'disrupted': True
		}
		self.assertDictEqual(dp_dict, correct_dict)

	def test_explicit(self):
		"""Test that to_dict() correctly converts an explicit DisruptionProcess 
		object to dict.
		"""
		print_status('TestToDict', 'test_explicit()')

		disruption_state_list = [True, False, False, True, False]

		disruption_process = DisruptionProcess()
		disruption_process.random_process_type = 'E'
		disruption_process.disruption_type = 'RP'
		disruption_process.disruption_state_list = disruption_state_list
		dp_dict = disruption_process.to_dict()
		correct_dict = {
			'random_process_type': 'E',
			'disruption_type': 'RP',
			'disruption_probability': None,
			'recovery_probability': None,
			'disruption_state_list': [True, False, False, True, False],
			'disrupted': False
		}
		self.assertDictEqual(dp_dict, correct_dict)

		# Modify original list to make sure the dict doesn't change.
		disruption_state_list.append(True)
		self.assertDictEqual(dp_dict, correct_dict)


class TestFromDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestFromDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestFromDict', 'tear_down_class()')

	def test_markovian(self):
		"""Test that from_dict() correctly converts a Markovian DisruptionProcess
		object from a dict.
		"""
		print_status('TestFromDict', 'test_markovian()')

		the_dict = {
			'random_process_type': 'M',
			'disruption_type': 'OP',
			'disruption_probability': 0.1,
			'recovery_probability': 0.25,
			'disruption_state_list': None,
			'disrupted': True
		}
		dp = DisruptionProcess.from_dict(the_dict)

		correct_dp = DisruptionProcess()
		correct_dp.random_process_type = 'M'
		correct_dp.disruption_probability = 0.1
		correct_dp.recovery_probability = 0.25
		correct_dp.disrupted = True

		self.assertEqual(dp, correct_dp)

	def test_explicit(self):
		"""Test that from_dict() correctly converts an explicit DisruptionProcess 
		object from a dict.
		"""
		print_status('TestFromDict', 'test_explicit()')

		disruption_state_list = [True, False, False, True, False]

		the_dict = {
			'random_process_type': 'E',
			'disruption_type': 'RP',
			'disruption_probability': None,
			'recovery_probability': None,
			'disruption_state_list': disruption_state_list,
			'disrupted': False
		}
		dp = DisruptionProcess.from_dict(the_dict)

		correct_dp = DisruptionProcess()
		correct_dp.random_process_type = 'E'
		correct_dp.disruption_type = 'RP'
		correct_dp.disruption_state_list = [True, False, False, True, False]
		
		self.assertEqual(dp, correct_dp)

		# Modify original list to make sure the dict doesn't change.
		disruption_state_list.append(True)
		self.assertEqual(dp, correct_dp)

	def test_missing_values(self):
		"""Test that from_dict() correctly fills attributes with defaults if missing.
		"""
		print_status('TestFromDict', 'test_missing_values()')

		# In this instance, disruption process at node 1 is missing the ``disruption_probability`` attribute.
		network1 = load_instance("missing_disruption_probability", "tests/additional_files/test_disruption_process_TestFromDict_data.json")
		network2 = load_instance("example_6_1")
		dp1 = network1.nodes_by_index[1].disruption_process
		dp2 = network2.nodes_by_index[1].disruption_process
		dp2.disruption_probability = DisruptionProcess._DEFAULT_VALUES['_disruption_probability']
		self.assertEqual(dp1, dp2)

		# In this instance, disruption process at node 1 is missing the ``disruption_state_list`` attribute.
		network1 = load_instance("missing_disruption_state_list", "tests/additional_files/test_disruption_process_TestFromDict_data.json")
		network2 = load_instance("example_6_1")
		dp1 = network1.nodes_by_index[1].disruption_process
		dp2 = network2.nodes_by_index[1].disruption_process
		dp2.disruption_probability = DisruptionProcess._DEFAULT_VALUES['_disruption_state_list']
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

