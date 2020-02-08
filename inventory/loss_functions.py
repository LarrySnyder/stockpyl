"""Code for solving newsvendor_normal problem.

Equation and section numbers refer to Snyder and Shen, "Fundamentals of Supply
Chain Theory", Wiley, 2019, 2nd ed., except as noted.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import nbinom
from scipy.integrate import quad
from types import *
from numbers import Number
from numbers import Integral

from inventory.helpers import *


####################################################
# CONTINUOUS DISTRIBUTIONS
####################################################


def standard_normal_loss(z):
	"""
	Return standard normal loss and complementary loss functions.

	Identities used:
		- L(z) = phi(z) - z(1 - Phi(z)); see equation (C.22).
		- \bar{L}(z) = z + L(z); see equation (C.23).

	Parameters
	----------
	z : float
		Argument of loss function.

	Returns
	-------
	L : float
		Loss function. [L(z)]
	L_bar : float
		Complementary loss function. [\bar{L}(z)]
	"""

	L = norm.pdf(z) - z * (1 - norm.cdf(z))
	L_bar = z + L

	return L, L_bar


def normal_loss(x, mean, sd):
	"""
	Return normal loss and complementary loss functions for N(mu,sigma^2)
	distribution.

	Identities used:
		- n(x) = sigma * L(z); see equation (C.31).
		- \bar{n}(x) = sigma * \bar{L}(z); see equation (C.32)

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	x : float
		Argument of loss function.
	mean : float
		Mean of normal distribution. [mu]
	sd : float
		Standard deviation of normal distribution. [sigma]

	Returns
	-------
	n : float
		Loss function. [n(x)]
	n_bar : float
		Complementary loss function. [\bar{n}(x)]
	"""
	z = (x - mean) / sd

	L, L_bar = standard_normal_loss(z)
	n = sd * L
	n_bar = sd * L_bar

	return n, n_bar


def lognormal_loss(x, mu, sigma):
	"""
	Return lognormal loss and complementary loss functions for logN(mu,sigma)
	distribution.

	Identities used:
		- n(x) = e^{mu+sigma^2/2} * Phi((mu+sigma^2-ln x)/sigma) -
			x(1 - Phi((ln x - mu)/sigma)); see equation (4.102)
		- \bar{n}(x) = x - E[X] + n(x); see equation (C.14)

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Parameters
	----------
	x : float
		Argument of loss function.
	mu : float
		Mean of distribution of ln X.
	sigma : float
		Standard deviation of distribution of ln X.

	Returns
	-------
	n : float
		Loss function. [n(x)]
	n_bar : float
		Complementary loss function. [\bar{n}(x)]
	"""
	# Calculate E[X].
	E = np.exp(mu + sigma**2/2)

	if x > 0:
		n = E * norm.cdf((mu + sigma**2 - np.log(x)) / sigma) \
			- x * (1 - norm.cdf((np.log(x) - mu) / sigma))
		n_bar = x - E + n
	else:
		n = E - x
		n_bar = 0

	return n, n_bar


def continuous_loss(x, distrib):
	"""
	Return loss and complementary loss functions for an arbitrary continuous
	distribution.

	Identities used:
		- n(x) = \int_x^\infty \bar{F}(y)dy; see equation (C.12)
		- \bar{n}(x) = \int_{-\infty}^x F(y)dy; see equation (C.13)

	Calculates integrals using numerical integration.

	Parameters
	----------
	x : float
		Argument of loss function.
	distrib : rv_continuous
		Desired distribution.

	Returns
	-------
	n : float
		Loss function. [n(x)]
	n_bar : float
		Complementary loss function. [\bar{n}(x)]
	"""
	n = distrib.expect(lambda y: max(y - x, 0))
	n_bar = distrib.expect(lambda y: max(x - y, 0))

	# Original version; the new version seems to be more accurate (and maybe
	# faster).
#	n = quad(lambda y: 1 - distrib.cdf(y), x, float("inf"))[0]
#	n_bar = quad(lambda y: distrib.cdf(y), -float("inf"), x)[0]

	return n, n_bar


####################################################
# DISCRETE DISTRIBUTIONS
####################################################

def poisson_loss(x, mean):
	"""
	Return Poisson loss and complementary loss functions for Pois(mu)
	distribution.

	Identities used:
		- n(x) = -(x - mu)\bar{F}(x) + mu * f(x); see equation (C.41)
		- \bar{n}(x) = (x - mu) * F(x) + mu * f(x); see equation (C.42)

	Raises ValueError if x is not an integer.

	Parameters
	----------
	x : float
		Argument of loss function.
	mean : float
		Mean of Poisson distribution.

	Returns
	-------
	n : int
		Loss function. [n(x)]
	n_bar : float
		Complementary loss function. [\bar{n}(x)]
	"""
	# Check for integer x.
	assert is_integer(x), "x must be an integer"

	n = -(x - mean) * (1 - poisson.cdf(x, mean)) + mean * poisson.pmf(x, mean)
	n_bar = (x - mean) * poisson.cdf(x, mean) + mean * poisson.pmf(x, mean)

	return n, n_bar


def negative_binomial_loss(x, mean, sd):
	"""
	Return negative binomial loss and complementary loss functions for NB
	distribution with given mean and standard deviation.

	(Function calculates n and p, the NB parameters.) Assumes mu < sigma^2.

	Identities used:
		- n(x) = -(x - n*beta)\bar{F}(x) + (x + n) * beta * f(x), where
			beta = p/(1-p); see Zipkin (2000), Section C.2.3.6.
		- \bar{n}(x) = x - E[X] + n(x); see equation (C.14)

	Raises ValueError if x is not an integer.

	Parameters
	----------
	x : float
		Argument of loss function.
	mean : float
		Mean of NB distribution.
	sd : float
		Standard deviation of NB distribution.

	Returns
	-------
	n : int
		Loss function. [n(x)]
	n_bar : float
		Complementary loss function. [\bar{n}(x)]
	"""
	# Check for integer x.
	assert is_integer(x), "x must be an integer"

	r = 1.0 * mean ** 2 / (sd ** 2 - mean)
	p = 1 - (sd ** 2 - mean) / (sd ** 2)
	beta = p / (1 - p)

#	return discrete_loss(x, nbinom(r, p))
#	n = -(x - r * beta) * (1 - nbinom.cdf(x, r, p)) + (x + r) * beta * nbinom.pmf(x, r, p)
#	n_bar = x - mean + n
	# formula above does not seem to be working (e.g., if r = 6, p = 0.4, then
	# returns negative value for n(10). So for now, using generic function:
	n, n_bar = discrete_loss(x, nbinom(r, p))

	return n, n_bar


def discrete_loss(x, distrib):
	"""
	Return loss and complementary loss function for an arbitrary discrete
	distribution.

	Assumes cdf(x) = 0 for x < 0.

	Identities used:
		- n(x) = \sum_x^\infty \bar{F}(y); see equation (C.35)
		- \bar{n}(x) = \sum_0^{x-1}; see equation (C.36)
	Terminates sums when \bar{F}(y) < 1e-12.

	Raises ValueError if x is not an integer.

	Parameters
	----------
	x : int
		Argument of loss function.
	distrib : rv_discrete
		Desired distribution.

	Returns
	-------
	n : float
		Loss function. [n(x)]
	n_bar : float
		Complementary loss function. [\bar{n}(x)]
	"""
	# Check for integer x.
	assert is_integer(x), "x must be an integer"

	n = 0.0
	y = x
	comp_cdf = 1 - distrib.cdf(y)
	while comp_cdf > 1.0e-12:
		n += comp_cdf
		y += 1
		comp_cdf = 1 - distrib.cdf(y)

	n_bar = 0.0
	for y in range(0, int(x)):
		n_bar += distrib.cdf(y)

	return n, n_bar

