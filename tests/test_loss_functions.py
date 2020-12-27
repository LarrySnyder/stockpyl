import unittest

import numpy as np
from scipy.stats import norm
from scipy.stats import lognorm
from scipy.stats import poisson
from scipy.stats import geom
from scipy.stats import expon
from scipy.stats import gamma
from scipy.stats import nbinom

from pyinv import loss_functions

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_loss_functions   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestStandardNormalLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestStandardNormalLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestStandardNormalLoss', 'tear_down_class()')

	def test(self):
		"""Test that standard_normal_loss function correctly calculates L and
		L_bar for a few instances.
		"""
		print_status('TestStandardNormalLoss', 'test()')

		z1 = -1.4
		L1, L_bar1 = loss_functions.standard_normal_loss(z1)
		self.assertAlmostEqual(L1, 1.436668142708465)
		self.assertAlmostEqual(L_bar1, 0.036668142708465)

		z2 = 0.3
		L2, L_bar2 = loss_functions.standard_normal_loss(z2)
		self.assertAlmostEqual(L2, 0.266761242117210)
		self.assertAlmostEqual(L_bar2, 0.566761242117210)

		z3 = 3.1
		L3, L_bar3 = loss_functions.standard_normal_loss(z3)
		self.assertAlmostEqual(L3, 2.672490952231408e-04)
		self.assertAlmostEqual(L_bar3, 3.100267249095223)


class TestStandardNormalSecondLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestStandardNormalSecondLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestStandardNormalSecondLoss', 'tear_down_class()')

	def test(self):
		"""Test that standard_normal_loss function correctly calculates L2 and
		L2_bar for a few instances.
		"""
		print_status('TestStandardNormalSecondLoss', 'test()')

		z = -1.4
		L2, L2_bar = loss_functions.standard_normal_second_loss(z)
		self.assertAlmostEqual(L2, 1.465289370279040)
		self.assertAlmostEqual(L2_bar, 0.014710629720960)

		z = 0.3
		L2, L2_bar = loss_functions.standard_normal_second_loss(z)
		self.assertAlmostEqual(L2, 0.151030102587942)
		self.assertAlmostEqual(L2_bar, 0.393969897412058)

		z = 3.1
		L2, L2_bar = loss_functions.standard_normal_second_loss(z)
		self.assertAlmostEqual(L2, 6.956550901328958e-05)
		self.assertAlmostEqual(L2_bar, 5.304930434490987)


class TestNormalLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNormalLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNormalLoss', 'tear_down_class()')

	def test(self):
		"""Test that normal_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestNormalLoss', 'test()')

		x1 = -1.4
		mean1 = 0
		sd1 = 1
		n1, n_bar1 = loss_functions.normal_loss(x1, mean1, sd1)
		self.assertAlmostEqual(n1, 1.436668142708465)
		self.assertAlmostEqual(n_bar1, 0.036668142708465)

		x2 = 11.0
		mean2 = 8
		sd2 = 3
		n2, n_bar2 = loss_functions.normal_loss(x2, mean2, sd2)
		self.assertAlmostEqual(n2, 0.249946411763059)
		self.assertAlmostEqual(n_bar2, 3.249946411763059)

		x3 = 10.5
		mean3 = 15
		sd3 = 5
		n3, n_bar3 = loss_functions.normal_loss(x3, mean3, sd3)
		self.assertAlmostEqual(n3, 5.002155685433356)
		self.assertAlmostEqual(n_bar3, 0.502155685433356)


class TestNormalSecondLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNormalSecondLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNormalSecondLoss', 'tear_down_class()')

	def test(self):
		"""Test that normal_second_loss function correctly calculates n2 and
		n2_bar for a few instances.
		"""
		print_status('TestNormalSecondLoss', 'test()')

		x = -1.4
		mean = 0
		sd = 1
		n2, n2_bar = loss_functions.normal_second_loss(x, mean, sd)
		self.assertAlmostEqual(n2, 1.465289370279040)
		self.assertAlmostEqual(n2_bar, 0.014710629720960)

		x = 11.0
		mean = 8
		sd = 3
		n2, n2_bar = loss_functions.normal_second_loss(x, mean, sd)
		self.assertAlmostEqual(n2, 0.339029025046969)
		self.assertAlmostEqual(n2_bar, 8.660970974953031)

		x = 10.5
		mean = 15
		sd = 5
		n2, n2_bar = loss_functions.normal_second_loss(x, mean, sd)
		self.assertAlmostEqual(n2, 21.454098725390558)
		self.assertAlmostEqual(n2_bar, 1.170901274609442)


class TestLognormalLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestLognormalLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestLognormalLoss', 'tear_down_class()')

	def test(self):
		"""Test that lognormal_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestLognormalLoss', 'test()')

		x1 = 10
		mu1 = 2
		sigma1 = 0.3
		n1, n_bar1 = loss_functions.lognormal_loss(x1, mu1, sigma1)
		self.assertAlmostEqual(n1, 0.283649738881062)
		self.assertAlmostEqual(n_bar1, 2.554491200971182)

		x2 = 2.5
		mu2 = 1
		sigma2 = 0.5
		n2, n_bar2 = loss_functions.lognormal_loss(x2, mu2, sigma2)
		self.assertAlmostEqual(n2, 0.887025638033385)
		self.assertAlmostEqual(n_bar2, 0.306808789115353)

		x3 = 0.5
		mu3 = 0.2
		sigma3 = 0.1
		n3, n_bar3 = loss_functions.lognormal_loss(x3, mu3, sigma3)
		self.assertAlmostEqual(n3, 0.727525064963178)
		self.assertAlmostEqual(n_bar3, 0)


class TestExponentialLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestExponentialLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestExponentialLoss', 'tear_down_class()')

	def test(self):
		"""Test that exponential_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestExponentialLoss', 'test()')

		x1 = 1
		mu1 = 0.2
		n1, n_bar1 = loss_functions.exponential_loss(x1, mu1)
		self.assertAlmostEqual(n1, 4.093653765389909)
		self.assertAlmostEqual(n_bar1, 0.093653765389909)

		x2 = 2.5
		mu2 = 1
		n2, n_bar2 = loss_functions.exponential_loss(x2, mu2)
		self.assertAlmostEqual(n2, 0.082084998623899)
		self.assertAlmostEqual(n_bar2, 1.582084998623899)

		x3 = 0.5
		mu3 = 2
		n3, n_bar3 = loss_functions.exponential_loss(x3, mu3)
		self.assertAlmostEqual(n3, 0.183939720585721)
		self.assertAlmostEqual(n_bar3, 0.183939720585721)

		# Test using continuous_loss, too, just as a triple-check.

		dist1 = expon(scale=1/mu1)
		n1a, n_bar1a = loss_functions.continuous_loss(x1, dist1)
		self.assertAlmostEqual(n1a, 4.093653765389909)
		self.assertAlmostEqual(n_bar1a, 0.093653765389909)

		dist2 = expon(scale=1/mu2)
		n2a, n_bar2a = loss_functions.continuous_loss(x2, dist2)
		self.assertAlmostEqual(n2a, 0.082084998623899)
		self.assertAlmostEqual(n_bar2a, 1.582084998623899)

		dist3 = expon(scale=1/mu3)
		n3a, n_bar3a = loss_functions.continuous_loss(x3, dist3)
		self.assertAlmostEqual(n3a, 0.183939720585721)
		self.assertAlmostEqual(n_bar3a, 0.183939720585721)

	def test_negative_x(self):
		"""Test that exponential_loss correctly raises exception if x < 0."""
		print_status('TestExponentialLoss', 'test_negative_x()')

		x = -2
		mu = 2
		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.exponential_loss(x, mu)


class TestExponentialSecondLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestExponentialSecondLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestExponentialSecondLoss', 'tear_down_class()')

	def test(self):
		"""Test that exponential_second_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestExponentialSecondLoss', 'test()')

		x1 = 1
		mu1 = 0.2
		n1, n_bar1 = loss_functions.exponential_second_loss(x1, mu1)
		self.assertAlmostEqual(n1, 20.468268826949540)
		self.assertAlmostEqual(n_bar1, 0.031731173050460)

		x2 = 2.5
		mu2 = 1
		n2, n_bar2 = loss_functions.exponential_second_loss(x2, mu2)
		self.assertAlmostEqual(n2, 0.082084998623899)
		self.assertAlmostEqual(n_bar2, 1.542915001376101)

		x3 = 0.5
		mu3 = 2
		n3, n_bar3 = loss_functions.exponential_second_loss(x3, mu3)
		self.assertAlmostEqual(n3, 0.091969860292861)
		self.assertAlmostEqual(n_bar3, 0.033030139707139)

		# # Test using continuous_loss, too, just as a triple-check.
		#
		# dist1 = expon(scale=1/mu1)
		# n1a, n_bar1a = loss_functions.continuous_second_loss(x1, dist1)
		# self.assertAlmostEqual(n1a, 20.468268826949540)
		# self.assertAlmostEqual(n_bar1a, 0.031731173050460)
		#
		# dist2 = expon(scale=1/mu2)
		# n2a, n_bar2a = loss_functions.continuous_second_loss(x2, dist2)
		# self.assertAlmostEqual(n2a, 0.082084998623899)
		# self.assertAlmostEqual(n_bar2a, 1.542915001376101)
		#
		# dist3 = expon(scale=1/mu3)
		# n3a, n_bar3a = loss_functions.continuous_second_loss(x3, dist3)
		# self.assertAlmostEqual(n3a, 0.091969860292861)
		# self.assertAlmostEqual(n_bar3a, 0.033030139707139)

	def test_negative_x(self):
		"""Test that exponential_second_loss correctly raises exception if x < 0."""
		print_status('TestExponentialSecondLoss', 'test_negative_x()')

		x = -2
		mu = 2
		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.exponential_second_loss(x, mu)


class TestGammaLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGammaLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGammaLoss', 'tear_down_class()')

	def test(self):
		"""Test that gamma_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestGammaLoss', 'test()')

		x1 = 4
		a1 = 2
		b1 = 3
		n1, n_bar1 = loss_functions.gamma_loss(x1, a1, b1)
		self.assertAlmostEqual(n1, 2.635971381157268)
		self.assertAlmostEqual(n_bar1, 0.635971381157268)

		x2 = 0.4
		a2 = 0.5
		b2 = 1.0
		n2, n_bar2 = loss_functions.gamma_loss(x2, a2, b2)
		self.assertAlmostEqual(n2, 0.276296168886834)
		self.assertAlmostEqual(n_bar2, 0.176296168886834)

		x3 = 7
		a3 = 9
		b3 = 0.5
		n3, n_bar3 = loss_functions.gamma_loss(x3, a3, b3)
		self.assertAlmostEqual(n3, 0.057910792089881)
		self.assertAlmostEqual(n_bar3, 2.557910792089881)

		# Test using continuous_loss, too, just as a triple-check.

		dist1 = gamma(a1, scale=b1)
		n1a, n_bar1a = loss_functions.continuous_loss(x1, dist1)
		self.assertAlmostEqual(n1a, 2.635971381157268)
		self.assertAlmostEqual(n_bar1a, 0.635971381157268)

		dist2 = gamma(a2, scale=b2)
		n2a, n_bar2a = loss_functions.continuous_loss(x2, dist2)
		self.assertAlmostEqual(n2a, 0.276296168886834)
		self.assertAlmostEqual(n_bar2a, 0.176296168886834)

		dist3 = gamma(a3, scale=b3)
		n3a, n_bar3a = loss_functions.continuous_loss(x3, dist3)
		self.assertAlmostEqual(n3a, 0.057910792089881)
		self.assertAlmostEqual(n_bar3a, 2.557910792089881)

	def test_negative_x(self):
		"""Test that exponential_loss correctly raises exception if x < 0."""
		print_status('TestExponentialLoss', 'test_negative_x()')

		x = -2
		a = 2
		b = 1
		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.gamma_loss(x, a, b)


class TestGammaSecondLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGammaSecondLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGammaSecondLoss', 'tear_down_class()')

	def test(self):
		"""Test that gamma_second_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestGammaSecondLoss', 'test()')

		x1 = 4
		a1 = 2
		b1 = 3
		n1, n_bar1 = loss_functions.gamma_second_loss(x1, a1, b1)
		self.assertAlmostEqual(n1, 10.280288386513346)
		self.assertAlmostEqual(n_bar1, 0.7197116134866537)

		x2 = 0.4
		a2 = 0.5
		b2 = 1.0
		n2, n_bar2 = loss_functions.gamma_second_loss(x2, a2, b2)
		self.assertAlmostEqual(n2, 0.226181566792298)
		self.assertAlmostEqual(n_bar2, 0.028818433207702)

		x3 = 7
		a3 = 9
		b3 = 0.5
		n3, n_bar3 = loss_functions.gamma_second_loss(x3, a3, b3)
		self.assertAlmostEqual(n3, 0.050685800735730)
		self.assertAlmostEqual(n_bar3, 4.199314199264270)

		# TODO:
		# # Test using continuous_loss, too, just as a triple-check.
		#
		# dist1 = expon(scale=1/mu1)
		# n1a, n_bar1a = loss_functions.continuous_second_loss(x1, dist1)
		# self.assertAlmostEqual(n1a, 20.468268826949540)
		# self.assertAlmostEqual(n_bar1a, 0.031731173050460)
		#
		# dist2 = expon(scale=1/mu2)
		# n2a, n_bar2a = loss_functions.continuous_second_loss(x2, dist2)
		# self.assertAlmostEqual(n2a, 0.082084998623899)
		# self.assertAlmostEqual(n_bar2a, 1.542915001376101)
		#
		# dist3 = expon(scale=1/mu3)
		# n3a, n_bar3a = loss_functions.continuous_second_loss(x3, dist3)
		# self.assertAlmostEqual(n3a, 0.091969860292861)
		# self.assertAlmostEqual(n_bar3a, 0.033030139707139)

	def test_negative_x(self):
		"""Test that gamma_second_loss correctly raises exception if x < 0."""
		print_status('TestGammaSecondLoss', 'test_negative_x()')

		x = -2
		a = 2
		b = 1
		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.gamma_second_loss(x, a, b)


class TestContinuousLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestContinuousLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestContinuousLoss', 'tear_down_class()')

	def test_normal(self):
		"""Test that continuous_loss function correctly calculates n and n_bar
		for a normally distributed instance.
		"""
		print_status('TestContinuousLoss', 'test_normal()')

		x1 = -1.4
		mean1 = 0
		sd1 = 1
		n1, n_bar1 = loss_functions.continuous_loss(x1, norm(mean1, sd1))
		self.assertAlmostEqual(n1, 1.436668142708465)
		self.assertAlmostEqual(n_bar1, 0.036668142708465)

		x2 = 11.0
		mean2 = 8
		sd2 = 3
		n2, n_bar2 = loss_functions.continuous_loss(x2, norm(mean2, sd2))
		self.assertAlmostEqual(n2, 0.249946411763059)
		self.assertAlmostEqual(n_bar2, 3.249946411763059)

	def test_lognormal(self):
		"""Test that continuous_loss function correctly calculates n and n_bar
		for a lognormally distributed instance.
		"""
		print_status('TestContinuousLoss', 'test_lognormal()')

		x1 = 10
		mu1 = 2
		sigma1 = 0.3
		# lognorm arguments: shape, loc, scale; setting shape = sigma, loc = 0,
		# scale = exp(mu) is equivalent to a lognormal distribution with
		# parameters mu, sigma
		n1, n_bar1 = loss_functions.continuous_loss(x1, lognorm(sigma1, 0, np.exp(mu1)))
		self.assertAlmostEqual(n1, 0.283649738881062)
		self.assertAlmostEqual(n_bar1, 2.554491200971182)

		x2 = 2.5
		mu2 = 1.0
		sigma2 = 0.5
		n2, n_bar2 = loss_functions.continuous_loss(x2, lognorm(sigma2, 0, np.exp(mu2)))
		self.assertAlmostEqual(n2, 0.887025638033385, places=4)
		self.assertAlmostEqual(n_bar2, 0.306808789115353, places=4)


class TestPoissonLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPoissonLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPoissonLoss', 'tear_down_class()')

	def test(self):
		"""Test that poisson_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestPoissonLoss', 'test()')

		x1 = 220
		mean1 = 200
		n1, n_bar1 = loss_functions.discrete_loss(x1, poisson(mean1))
		self.assertAlmostEqual(n1, 0.536005857158494)
		self.assertAlmostEqual(n_bar1, 20.536005857158482)

		x2 = 5
		mean2 = 7
		n2, n_bar2 = loss_functions.discrete_loss(x2, poisson(mean1))
		self.assertAlmostEqual(n1, 0.536005857158494)
		self.assertAlmostEqual(n_bar1, 20.536005857158482)

	def test_non_integer(self):
		"""Test that poisson_loss function raises exception on non-integer x.
		"""
		print_status('TestPoissonLoss', 'test_non_integer()')

		x = 0.3
		mean = 0.5
		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.poisson_loss(x, mean)

	def test_non_numeric(self):
		"""Test that poisson_loss function raises exception on non-numeric x.
		"""
		print_status('TestPoissonLoss', 'test_non_numeric()')

		x = "foo"
		mean = 5
		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.poisson_loss(x, mean)


class TestNegativeBinomialLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNegativeBinomialLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNegativeBinomialLoss', 'tear_down_class()')

	def test(self):
		"""Test that negative_binomial_loss function correctly calculates n and n_bar for
		a few instances.
		"""
		print_status('TestNegativeBinomialLoss', 'test()')

		x1 = 14
		mean1 = 23.333333333333336
		sd1 = 8.819171036881968
		n1, n_bar1 = loss_functions.negative_binomial_loss(x1, mean1, sd1)
		self.assertAlmostEqual(n1, 9.740089476453932, places=4)
		self.assertAlmostEqual(n_bar1, 0.406758474515445, places=4)

		x2 = 28
		mean2 = 23.333333333333336
		sd2 = 8.819171036881968
		n2, n_bar2 = loss_functions.negative_binomial_loss(x2, mean2, sd2)
		self.assertAlmostEqual(n2, 1.805485505752903, places=4)
		self.assertAlmostEqual(n_bar2, 6.472154141707762, places=4)

		x3 = 10
		mean3 = 15
		sd3 = 6.123724356957944
		n3, n_bar3 = loss_functions.negative_binomial_loss(x3, mean3, sd3)
		self.assertAlmostEqual(n3, 5.533809274622726, places=4)
		self.assertAlmostEqual(n_bar3, 0.533809274627819, places=4)

		# Test using discrete_loss, as a triple-check.
		r1 = 1.0 * mean1 ** 2 / (sd1 ** 2 - mean1)
		p1 = 1 - (sd1 ** 2 - mean1) / (sd1 ** 2)
		n1a, n_bar1a = loss_functions.discrete_loss(x1, nbinom(r1, p1))
		self.assertAlmostEqual(n1, n1a, places=4)
		self.assertAlmostEqual(n_bar1, n_bar1a, places=4)

		r2 = 1.0 * mean2 ** 2 / (sd2 ** 2 - mean2)
		p2 = 1 - (sd2 ** 2 - mean2) / (sd2 ** 2)
		n2a, n_bar2a = loss_functions.discrete_loss(x2, nbinom(r2, p2))
		self.assertAlmostEqual(n2, n2a, places=4)
		self.assertAlmostEqual(n_bar2, n_bar2a, places=4)

		r3 = 1.0 * mean3 ** 2 / (sd3 ** 2 - mean3)
		p3 = 1 - (sd3 ** 2 - mean3) / (sd3 ** 2)
		n3a, n_bar3a = loss_functions.discrete_loss(x3, nbinom(r3, p3))
		self.assertAlmostEqual(n3, n3a, places=4)
		self.assertAlmostEqual(n_bar3, n_bar3a, places=4)

	def test_non_integer(self):
		"""Test that poisson_loss function raises exception on non-integer x.
		"""
		print_status('TestPoissonLoss', 'test_non_integer()')

		x = 0.3
		mean = 0.5
		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.poisson_loss(x, mean)


class TestDiscreteLoss(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDiscreteLoss', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDiscreteLoss', 'tear_down_class()')

	def test_poisson(self):
		"""Test that discrete_loss function correctly calculates n and n_bar
		for a Poisson distributed instance.
		"""
		print_status('TestDiscreteLoss', 'test_poisson()')

		x1 = 220
		mean1 = 200
		n1, n_bar1 = loss_functions.discrete_loss(x1, poisson(mean1))
		self.assertAlmostEqual(n1, 0.536005857158494, places=4)
		self.assertAlmostEqual(n_bar1, 20.536005857158482, places=4)

		x2 = 5
		mean2 = 7
		n2, n_bar2 = loss_functions.discrete_loss(x2, poisson(mean2))
		self.assertAlmostEqual(n2, 2.292599516747219, places=4)
		self.assertAlmostEqual(n_bar2, 0.292600125697305, places=4)

	def test_geometric(self):
		"""Test that discrete_loss function correctly calculates n and n_bar
		for a geometric distributed instance.
		"""
		print_status('TestDiscreteLoss', 'test_geometric()')

		x1 = 5
		p1 = 0.2
		# Setting loc=-1 changes geom to "# failures" form.
		n1, n_bar1 = loss_functions.discrete_loss(x1, geom(p1, -1))
		self.assertAlmostEqual(n1, 1.310646440214040, places=3)
		self.assertAlmostEqual(n_bar1, 2.310720000000000, places=3)

		x2 = 3
		p2 = 0.7
		n2, n_bar2 = loss_functions.discrete_loss(x2, geom(p2, -1))
		self.assertAlmostEqual(n2, 0.011571370765832, places=3)
		self.assertAlmostEqual(n_bar2, 2.583000000000000, places=3)

	def test_pmf(self):
		"""Test that discrete_loss function correctly calculates n and n_bar
		if provided with a pmf instead of a distribution object.
		"""
		print_status('TestDiscreteLoss', 'test_pmf()')

		d1 = range(1, 11)
		f1 = [.13, .15, .02, .15, .10, .02, .04, .09, .15, .15]
		pmf1 = dict(zip(d1, f1))
		x1 = 6
		n1, n_bar1 = loss_functions.discrete_loss(x1, None, pmf1)
		self.assertAlmostEqual(n1, 1.27)
		self.assertAlmostEqual(n_bar1, 1.71)

		d2 = range(0, 41)
		f2 = [poisson.pmf(d, 7) for d in d2]
		pmf2 = dict(zip(d2, f2))
		x2 = 11
		n2, n_bar2 = loss_functions.discrete_loss(x2, None, pmf2)
		self.assertAlmostEqual(n2, 0.102799704109245)
		self.assertAlmostEqual(n_bar2, 4.102799704109247)

	def test_no_distrib(self):
		"""Test that discrete_loss function correctly raises exception if
		both distrib and pmf are None.
		"""
		print_status('TestDiscreteLoss', 'test_pmf()')

		with self.assertRaises(ValueError):
			n, n_bar = loss_functions.discrete_loss(0, None, None)



