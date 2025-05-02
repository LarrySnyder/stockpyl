# ===============================================================================
# stockpyl - loss_functions Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_loss_functions| module contains code for calculating loss functions.

For a random variable :math:`X`, the loss function, :math:`n(x)`, and the
complementary loss function, :math:`\\bar{n}(x)`, are defined as:

	* :math:`n(x) = E[(X-x)^+]`
	* :math:`\\bar{n}(x) = E[(X-x)^-]`,

where :math:`x^+ = \\max\\{x,0\\}` and :math:`x^- = |\\min\\{x,0\\}|`. The second-order
loss function, :math:`n^{(2)}(x)`, and the second-order complementary loss function,
:math:`\\bar{n}^{(2)}(x)`, are defined as:

	* :math:`n^{(2)}(x) = \\frac{1}{2}E\\left[\\left([X-x]^+\\right)^2\\right]`
	* :math:`\\bar{n}^{(2)}(x) = \\frac{1}{2}E\\left[\\left([X-x]^-\\right)^2\\right]`

.. note:: |fosct_notation|


API Reference
-------------

"""

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import nbinom
from scipy.stats import gamma
#from scipy.integrate import quad
from types import *
import math

from stockpyl.helpers import *


####################################################
# CONTINUOUS DISTRIBUTIONS
####################################################


def standard_normal_loss(z):
	"""
	Return :math:`\\mathscr{L}(z)` and :math:`\\bar{\\mathscr{L}}(z)`, the
	standard normal loss and complementary loss functions.

	Parameters
	----------
	z : float
		Argument of loss function.

	Returns
	-------
	L : float
		Loss function. [:math:`\\mathscr{L}(z)`]
	L_bar : float
		Complementary loss function. [:math:`\\bar{\\mathscr{L}}(z)`]


	**Equations Used** (equations (C.22) and (C.23)):

	.. math::

		\\mathscr{L}(z) = \\phi(z) - z(1 - \\Phi(z))

	.. math::

		\\bar{\\mathscr{L}}(z) = z + \\mathscr{L}(z)

	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> standard_normal_loss(1.3)
		(0.04552796208651397, 1.345527962086514)

	"""

	L = norm.pdf(z) - z * (1 - norm.cdf(z))
	L_bar = z + L

	return L, L_bar


def standard_normal_second_loss(z):
	"""
	Return :math:`\\mathscr{L}^{(2)}(z)` and
	:math:`\\bar{\\mathscr{L}}^{(2)}(z)`, the standard normal second-order loss
	and complementary loss functions.

	Parameters
	----------
	z : float
		Argument of loss function.

	Returns
	-------
	L2 : float
		Loss function. [:math:`\\mathscr{L}^{(2)}(z)`]
	L2_bar : float
		Complementary loss function. [:math:`\\bar{\\mathscr{L}}^{(2)}(z)`]


	**Equations Used** (equations (C.27) and (C.28)):

	.. math::

		\\mathscr{L}^{(2)}(z) = \\frac12\\left[\\left(z^2+1\\right)(1-\\Phi(z)) - z\\phi(z)\\right]

	.. math::

		\\bar{\\mathscr{L}}^{(2)}(z) = \\frac12(z^2 + 1) - \\mathscr{L}^{(2)}(z)

	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> standard_normal_second_loss(1.3)
		(0.01880706693657111, 1.326192933063429)

	"""

	L2 = 0.5 * ((z**2 + 1) * (1 - norm.cdf(z)) - z * norm.pdf(z))
	L2_bar = 0.5 * (z**2 + 1) - L2

	return L2, L2_bar


def normal_loss(x, mean, sd):
	"""
	Return :math:`n(x)` and :math:`\\bar{n}(x)``, the normal loss function and
	complementary loss functions for a :math:`N(\\mu,\\sigma^2)`
	distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	mean : float
		Mean of normal distribution. [:math:`\\mu`]
	sd : float
		Standard deviation of normal distribution. [:math:`\\sigma`]

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]


	**Equations Used** (equations (C.31) and (C.32)):

	.. math::

		n(x) = \\mathscr{L}(z) \\sigma

		\\bar{n}(x) = \\bar{\\mathscr{L}}(z) \\sigma

	where :math:`z = (x-\\mu)/\\sigma` and :math:`\\mathscr{L}(z)` and
	:math:`\\bar{\\mathscr{L}}(z)` are the standard normal loss and complementary
	loss functions.

	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> normal_loss(18.6, 15, 3)
		(0.1683073521514889, 3.7683073521514903)

	"""
	z = (x - mean) / sd

	L, L_bar = standard_normal_loss(z)
	n = sd * L
	n_bar = sd * L_bar

	return n, n_bar


def normal_second_loss(x, mean, sd):
	"""
	Return :math:`n^{(2)}(x)` and :math:`\\bar{n}^{(2)}(x)``, the second-order
	normal loss function and complementary second-order loss function for a
	:math:`N(\\mu,\\sigma^2)` distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	mean : float
		Mean of normal distribution. [:math:`\\mu`]
	sd : float
		Standard deviation of normal distribution. [:math:`\\sigma`]

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n^{(2)}(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}^{(n)}(x)`]


	**Equations Used** (equations (C.33) and (C.34)):

	.. math::

		n^{(2)}(x) = \\mathscr{L}^{(2)}(z) \\sigma^2

		\\bar{n}^{(2)}(x) = \\bar{\\mathscr{L}}^{(2)}(z) \\sigma^2

	where :math:`z = (x-\\mu)/\\sigma` and :math:`\\mathscr{L}^{(2)}(z)` and
	:math:`\\bar{\\mathscr{L}}^{(2)}(z)` are the standard normal second-order
	loss and complementary loss functions.

	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> normal_second_loss(18.6, 15, 3)
		(0.21486028212500707, 10.765139717874998)

	"""
	z = (x - mean) / sd

	L2, L2_bar = standard_normal_second_loss(z)
	n = sd**2 * L2
	n_bar = sd**2 * L2_bar

	return n, n_bar


def standard_normal_loss_dict(start=-4, stop=4, step=0.01, complementary=False):
	"""Return a dictionary whose keys range from ``start`` to ``stop`` in intervals of ``step``, 
	and whose values are the standard normal loss function
	values corresponding to those keys. If going from ``start`` in increments of ``step``
	overshoots ``stop``, ends at the largest value before ``stop``. If ``complementary`` is ``False``,
	the dictionary values are the standard normal complementary loss function.
	
	Default values return :math:`\\mathscr{L}^{(2)}(z)`
	for :math:`z = -4.00, -3.99, -3.98, \ldots, 3.98, 3.99, 4.00`.

	**Note:** Because of how floating point arithmetic works, the dictionary keys will not
	precisely equal the desired values. Therefore, the resulting dictionary is difficult to 
	use by calling it directly. For example, 0.55 is unlikely to be a key in the dictionary 
	returned, even if the input parameters suggest that it should; instead, the key might be
	represented as, say, 0.5499999999999593. Therefore, to determine the value of the loss function
	for 0.55, you must generally search for the nearest key to 0.55 and take the corresponding value.
	(The ``helpers.nearest_dict_value()`` function does just that.)

	Parameters
	----------
	start : float, optional
		The start value to calculate the loss function for, by default -4
	stop : float, optional
		The start value to calculate the loss function for, by default 4
	step : float, optional
		The interval between values to calculate the loss function for, by default 0.01
	complementary : bool, optional
		Set to ``True`` to return the complementary loss function, by default ``False``

	Returns
	-------
	dict
		Dictoinary whose keys range from ``start`` to ``stop`` in intervals of ``step``, 
		and whose values are the standard normal loss function
		values corresponding to those keys.
	"""
	
	# Build list of z values.
	z = start
	z_list = []
	while z < stop:
		z_list.append(z)
		z += step
	
	# Build and return dictionary.
	return {z: standard_normal_loss(z)[1 if complementary else 0] for z in z_list}

	
def lognormal_loss(x, mu, sigma):
	"""
	Return lognormal loss and complementary loss functions for :math:`\\text{lognormal}(\\mu,\\sigma)`
	distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	mu : float
		Mean of distribution of [:math:`\\ln X`].
	sigma : float
		Standard deviation of distribution of [:math:`\\ln X`].

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]


	**Equations Used** (equations (4.102) and (C.14)):

	.. math::

		n(x) = e^{\\mu+\\sigma^2/2} \\Phi((\\mu+\\sigma^2-\\ln x)/\\sigma) - x(1 - \\Phi((\\ln x - \\mu)/\\sigma))

	.. math::

		\\bar{n}(x) = x - E[X] + n(x)


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> lognormal_loss(10, 2, 0.3)
		(0.28364973888106326, 2.5544912009711833)
	"""
	# Calculate E[X].
	E = math.exp(mu + sigma**2/2)

	if x > 0:
		n = E * norm.cdf((mu + sigma**2 - math.log(x)) / sigma) \
			- x * (1 - norm.cdf((math.log(x) - mu) / sigma))
		n_bar = x - E + n
	else:
		n = E - x
		n_bar = 0

	return n, n_bar


def exponential_loss(x, mu):
	"""
	Return exponential loss and complementary loss functions for :math:`\\text{exp}(\\mu)`
	distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	mu : float
		Rate of exponential distribution.

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` < 0.


	**Equations Used** (Zipkin (2000), p. 457 and (C.14)):

	.. math::

		n(x) = \\frac{e^{-\\mu x}}{\\mu}

	.. math::

		\\bar{n}(x) = x - E[X] + n(x)


	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> exponential_loss(1, 0.2)
		(4.0936537653899085, 0.09365376538990855)
	"""
	# Check that x >= 0.
	if x < 0:
		raise ValueError("x must be >= 0.")

	# Calculate E[X].
	E = 1.0 / mu

	n = math.exp(-mu * x) / mu
	n_bar = x - E + n

	return n, n_bar


def exponential_second_loss(x, mu):
	"""
	Return :math:`n^{(2)}(x)` and :math:`\\bar{n}^{(2)}(x)``, the second-order
	exponential loss function and complementary second-order loss function for an
	:math:`\\text{exp}(\\mu)` distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	mu : float
		Rate of exponential distribution.

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n^{(2)}(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}^{(n)}(x)`]

	Raises
	------
	ValueError
		If ``x`` < 0.


	**Equations Used** (Zipkin (2000), p. 457 and (C.19)):

	.. math::

		n^{(2)}(x) = \\frac{e^{-\\mu x}}{\\mu^2}

	.. math::

		\\bar{n}^{(2)}(x) = \\frac12\\left((x-E[X])^2 + \\text{Var}[X]\\right) - n^{(2)}(x)


	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> exponential_second_loss(1, 0.2)
		(20.46826882694954, 0.031731173050459915)

	"""
	# Check that x >= 0.
	if x < 0:
		raise ValueError("x must be >= 0.")

	# Calculate E[X] and Var[X].
	E = 1.0 / mu
	V = 1.0 / mu**2

	n = math.exp(-mu * x) / mu**2
	n_bar = 0.5 * ((x - E)**2 + V) - n

	return n, n_bar


def gamma_loss(x, a, b):
	"""
	Return gamma loss and complementary loss functions for a :math:`\\text{Gamma}(a,b)`
	distribution with shape parameter :math:`a` and scale parameter :math:`b`, i.e.,
	a distribution with pdf

	.. math::

		f(x) = \\frac{x^{a-1}e^{-\\frac{x}{b}}}{\\Gamma(a)b^a},

	where :math:`\\Gamma(\cdot)` is the gamma function.

	Parameters
	----------
	x : float
		Argument of loss function.
	a : float
		Shape parameter of gamma distribution.
	b : float
		Scale parameter of gamma distribution.

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` <= 0.


	**Equations Used** (Zipkin (2000), p. 457 and (C.14)):

	.. math::

		n(x) = \\left[\\left(a - \\frac{x}{b}\\right)(1-F(x)) + xf(x)\\right]b,

	where :math:`f(x)` and :math:`F(x)` are the gamma pdf and cdf, respectively.

	.. math::

		\\bar{n}(x) = x - E[X] + n(x)


	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).

	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> gamma_loss(4, 2, 3)
		(2.635971381157268, 0.635971381157268)
	"""
	# Check that x > 0.
	if x <= 0:
		raise ValueError("x must be > 0.")

	# Calculate f(x), F(x), and E[X].
	f = gamma.pdf(x, a, scale=b)
	F = gamma.cdf(x, a, scale=b)
	E = gamma.mean(a, scale=b)

	n = ((a - x/b) * (1 - F) + x * f) * b
	n_bar = x - E + n

	return n, n_bar


def gamma_second_loss(x, a, b):
	"""
	Return :math:`n^{(2)}(x)` and :math:`\\bar{n}^{(2)}(x)``, the second-order
	loss and complementary loss functions for a
	:math:`\\text{Gamma}(a,b)` distribution with shape parameter :math:`a` and
	scale parameter :math:`b`, i.e., a distribution with pdf

	.. math::

		f(x) = \\frac{x^{a-1}e^{-\\frac{x}{b}}}{\\Gamma(a)b^a},

	where :math:`\\Gamma(\cdot)` is the gamma function.

	Parameters
	----------
	x : float
		Argument of loss function.
	a : float
		Shape parameter of gamma distribution.
	b : float
		Scale parameter of gamma distribution.

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n^{(2)}(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}^{(n)}(x)`]

	Raises
	------
	ValueError
		If ``x`` < 0.


	**Equations Used** (Zipkin (2000), p. 457 and (C.19)):

	.. math::

		n^{(2)}(x) = \\frac{1}{2}\\left[\\left[\\left(a-\\frac{x}{b}\\right)^2 + a\\right](1-F(x)) + \\left(a - \\frac{x}{b} + 1\\right)xf(x)\\right]b^2,

	where :math:`f(x)` and :math:`F(x)` are the gamma pdf and cdf, respectively.

	.. math::

		\\bar{n}^{(2)}(x) = \\frac12\\left((x-E[X])^2 + \\text{Var}[X]\\right) - n^{(2)}(x)

	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> gamma_second_loss(4, 2, 3)
		(10.280288386513346, 0.7197116134866537)

	"""
	# Check that x >= 0.
	if x < 0:
		raise ValueError("x must be >= 0.")

	# Calculate f(x), F(x), and E[X].
	f = gamma.pdf(x, a, scale=b)
	F = gamma.cdf(x, a, scale=b)
	E = a * b
	V = a * b**2

	n = 0.5 * (((a - x/b)**2 + a) * (1 - F) + (a - x/b + 1) * x * f) * b**2
	n_bar = 0.5 * ((x - E)**2 + V) - n

	return n, n_bar


def uniform_loss(x, a, b):
	"""
	Return uniform loss and complementary loss functions for a continuous :math:`U[a,b]`
	distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	a : float
		Lower bound of uniform distribution.
	b : float
		Upper bound of uniform distribution.

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` < ``a`` or > ``b``.


	**Equations Used:**

	.. math::

		n(x) = \\frac{(b-x)^2}{2(b-a)}

		\\bar{n}(x) = \\frac{(x-a)^2}{2(b-a)}


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> uniform_loss(4, 2, 8)
		(1.3333333333333333, 0.3333333333333333)
	"""
	# Check that a <= x <= b.
	if x < a or x > b:
		raise ValueError("x must be >= a and <= b.")

	n = (b - x)**2 / (2 * (b - a))
	n_bar = (x - a)**2 / (2 * (b - a))

	return n, n_bar


def uniform_second_loss(x, a, b):
	"""
	Return :math:`n^{(2)}(x)` and :math:`\\bar{n}^{(2)}(x)``, the second-order
	loss and complementary loss functions for a
	:math:`U[a,b]` distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	a : float
		Lower bound of uniform distribution.
	b : float
		Upper bound of uniform distribution.

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n^{(2)}(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}^{(n)}(x)`]

	Raises
	------
	ValueError
		If ``x`` < ``a`` or > ``b``.


	**Equations Used:**

	.. math::

		n^{(2)}(x) = \\frac{(b-x)^3}{6(b-a)}

		\\bar{n}^{(2)}(x) = \\frac{(x-a)^3}{6(b-a)}


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> uniform_second_loss(4, 2, 8)
		(1.7777777777777777, 0.2222222222222222)

	"""
	# Check that a <= x <= b.
	if x < a or x > b:
		raise ValueError("x must be >= a and <= b.")

	n2 = (b - x)**3 / (6 * (b - a))
	n2_bar = (x - a)**3 / (6 * (b - a))

	return n2, n2_bar


def continuous_loss(x, distrib):
	"""
	Return loss and complementary loss functions for an arbitrary continuous
	distribution, using numerical integration.

	Parameters
	----------
	x : float
		Argument of loss function.
	distrib : rv_continuous
		Desired distribution.

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]


	**Equations Used** (equations (C.12) and (C.13)):

	.. math::

		n(x) = \\int_x^\\infty \\bar{F}(y)dy

		\\bar{n}(x) = \\int_{-\\infty}^x F(y)dy


	**Example**:

	Calculate loss function for :math:`\\exp(10)` distribution, by declaring a
	custom ``rv_continuous`` distribution:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> from scipy import stats
		>>> import math
		>>> class my_exp(stats.rv_continuous):
		...     def _pdf(self, x):
		...         if x >= 0:
		...             return 10 * math.exp(-10 * x)
		...         else:
		...             return 0
		>>> my_dist = my_exp()
		>>> continuous_loss(0.2, my_dist)
		(0.013533528323661264, 0.10522318598177341)

	Or by using a "frozen" built-in exponential distribution:

	.. doctest::

		>>> from scipy.stats import expon
		>>> my_dist = expon(scale=1/10)
		>>> continuous_loss(0.2, my_dist)
		(0.013533528103402742, 0.11353352830366131)

	(The two methods give slightly different results due to differences in the ways the
	two ``rv_continuous`` objects generate the distribution.)

	"""
	# Find values lb and ub such that F(lb) ~ 0 and F(ub) ~ 1.
	# (These will be the ranges for integration.)
	lb = distrib.ppf(1.0e-10)
	ub = distrib.ppf(1.0 - 1.0e-10)

	# Calculate loss functions.
	n = distrib.expect(lambda y: max(y - x, 0), lb=x, ub=ub)
	n_bar = distrib.expect(lambda y: max(x - y, 0), lb=lb, ub=x)

	# Original version; the new version seems to be more accurate (and maybe
	# faster).
#	n = quad(lambda y: 1 - distrib.cdf(y), x, float("inf"))[0]
#	n_bar = quad(lambda y: distrib.cdf(y), -float("inf"), x)[0]

	return n, n_bar


def continuous_second_loss(x, distrib):
	"""
	Return second-order loss and complementary loss functions for an arbitrary continuous
	distribution, using numerical integration.

	Parameters
	----------
	x : float
		Argument of loss function.
	distrib : rv_continuous
		Desired distribution.

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}(x)`]


	**Equations Used** (equations (C.17) and (C.18)):

	.. math::

		n^{(2)}(x) = \\frac12\\int_x^\\infty (y-x)^2 f(y)dy

	.. math::

		n^{(2)}(x) = \\frac12\\int_0^x (x-y)^2 f(y)dy

	**Example**:

	Calculate second-order loss functions for :math:`\\exp(10)` distribution, by declaring a
	custom ``rv_continuous`` distribution:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest:: 

		>>> from scipy import stats
		>>> import math
		>>> class my_exp(stats.rv_continuous):
		...     def _pdf(self, x):
		...         if x >= 0:
		...             return 10 * math.exp(-10 * x)
		...         else:
		...             return 0
		>>> my_dist = my_exp()
		>>> continuous_second_loss(0.2, my_dist)
		(0.0013533528323661267, 0.007824431159359786)

	Or by using a "frozen" built-in exponential distribution:

	.. doctest::

		>>> from scipy.stats import expon
		>>> my_dist = expon(scale=1/10)
		>>> continuous_second_loss(0.2, my_dist)
		(0.001353352589297054, 0.008646647165633875)

	(The two methods give slightly different results due to differences in the ways the
	two ``rv_continuous`` objects generate the distribution.)

	"""
	# Find values lb and ub such that F(lb) ~ 0 and F(ub) ~ 1.
	# (These will be the ranges for integration.)
	lb = distrib.ppf(1.0e-10)
	ub = distrib.ppf(1.0 - 1.0e-10)

	# Find E[X] and Var[X].
#	E, V = distrib.stats(moments='mv')

	# Calculate loss functions.
	n2 = 0.5 * distrib.expect(lambda y: max(y - x, 0)**2, lb=x, ub=ub)
	n2_bar = 0.5 * distrib.expect(lambda y: max(x - y, 0)**2, lb=lb, ub=x)
	#n2_bar = 0.5 * ((x - E)**2 + V) - n2

	# Original version; the new version seems to be more accurate (and maybe
	# faster).
#	n = quad(lambda y: 1 - distrib.cdf(y), x, float("inf"))[0]
#	n_bar = quad(lambda y: distrib.cdf(y), -float("inf"), x)[0]

	return n2, n2_bar


####################################################
# DISCRETE DISTRIBUTIONS
####################################################

def poisson_loss(x, mean):
	"""
	Return Poisson loss and complementary loss functions for :math:`\\text{Pois}` (``mean``)
	distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	mean : float
		Mean of Poisson distribution.

	Returns
	-------
	n : int
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` is not an integer.


	**Equations Used** (equations (C.41) and (C.42)):

	.. math::

		n(x) = -(x - \\mu)(1-F(x)) + \\mu f(x)

	.. math::

		\\bar{n}(x) = (x - \\mu) F(x) + \\mu f(x)


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> poisson_loss(18, 15)
		(0.5176095282584724, 3.5176095282584723)
	"""
	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Calculate f(x) and F(x).
	f = poisson.pmf(x, mean)
	F = poisson.cdf(x, mean)

	n = -(x - mean) * (1 - F) + mean * f
	n_bar = (x - mean) * F + mean * f

	return n, n_bar


def poisson_second_loss(x, mean):
	"""
	Return :math:`n^{(2)}(x)` and :math:`\\bar{n}^{(2)}(x)``, the second-order
	Poisson loss function and complementary second-order loss function for a :math:`\\text{Pois}` (``mean``)
	distribution.

	Parameters
	----------
	x : float
		Argument of loss function.
	mean : float
		Mean of Poisson distribution. [:math:`\\mu`]

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n^{(2)}(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}^{(n)}(x)`]

	Raises
	------
	ValueError
		If ``x`` is not an integer.


	**Equations Used** (equations (C.41) and (C.42)):

	.. math::

		n^{(2)}(x) = \\frac12 \\left[\\left((x-\\mu)^2 + x\\right)(1-F(x)) - \\mu(x-\\mu)f(x)\\right]

	.. math::

		\\bar{n}^{(2)}(x) = \\frac12 \\left[\\left((x-\\mu)^2 + x\\right)F(x) + \\mu(x-\\mu)f(x)\\right]


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> poisson_second_loss(18, 15)
		(0.848340302917789, 12.651659697082211)
	"""
	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Calculate f(x) and F(x).
	f = poisson.pmf(x, mean)
	F = poisson.cdf(x, mean)

	n2 = 0.5 * (((x - mean)**2 + x) * (1 - F) - mean * (x - mean) * f)
	n2_bar = 0.5 * (((x - mean)**2 + x) * F + mean * (x - mean) * f)

	return n2, n2_bar


def geometric_loss(x, p):
	"""
	Return geometric loss and complementary loss functions for :math:`\\text{Geom}` (``p``)
	distribution. Uses the "number of trials" version of the geometric distribution,
	i.e., the pmf is

	.. math::

		f(x) = (1-p)^{x-1}p

	(This is the same version of the distribution used by scipy.)

	Parameters
	----------
	x : float
		Argument of loss function.
	p : float
		Success probability for geometric distribution.

	Returns
	-------
	n : int
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` is not an integer.


	**Equations Used** (Zipkin (2000), Section C.2.3.5, and (C.14)):

	.. math::

		n(x) = \\left(\\frac{1-p}{p}\\right)(1-p)^{x-1}

	.. math::

		\\bar{n}(x) = x - E[X] + n(x)

	(Note that Zipkin (2000) uses the "number of failures" version of the
	geometric distribution and uses :math:`p` to refer to the failure probability rather
	than the success probability. The notation has been adjusted to account for
	the version we use here.)

	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> geometric_loss(7, 0.2)
		(1.0485760000000004, 3.0485760000000006)
	"""
	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Calculate E[X].
	E = 1.0 / p

	n = ((1 - p) / p) * (1 - p)**(x-1)
	n_bar = x - E + n

	return n, n_bar


def geometric_second_loss(x, p):
	"""
	Return :math:`n^{(2)}(x)` and :math:`\\bar{n}^{(2)}(x)``, the second-order
	geometric loss function and complementary second-order loss function for a :math:`\\text{Geom}` (``p``)
	distribution. Uses the "number of trials" version of the geometric distribution,
	i.e., the pmf is

	.. math::

		f(x) = (1-p)^{x-1}p

	(This is the same version of the distribution used by scipy.)

	Parameters
	----------
	x : float
		Argument of loss function.
	p : float
		Success probability for geometric distribution.

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n^{(2)}(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}^{(n)}(x)`]

	Raises
	------
	ValueError
		If ``x`` is not an integer.


	**Equations Used** (Zipkin (2000), Section C.2.3.5, and (C.40)):

	.. math::

		n^{(2)}(x) = \\left(\\frac{1-p}{p}\\right)^2 (1-p)^{x-1}

	.. math::

		\\bar{n}^{(2)}(x) = \\frac12\\left((x-E[X])^2 + (x-E[X]) + \\text{Var}[X]\\right) - n^{(2)}(x)

	(Note that Zipkin (2000) uses the "number of failures" version of the
	geometric distribution and uses :math:`p` to refer to the failure probability rather
	than the success probability. The notation has been adjusted to account for
	the version we use here.)

	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> geometric_second_loss(7, 0.2)
		(4.194304000000002, 8.805695999999998)
	"""
	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Calculate f(x) and F(x).
	E = 1.0 / p
	V = (1.0 - p) / p**2

	n2 = ((1 - p) / p)**2 * (1 - p)**(x - 1)
	n2_bar = 0.5 * ((x - E)**2 + (x - E) + V) - n2

	return n2, n2_bar


def negative_binomial_loss(x, r=None, p = None, mean=None, sd=None):
	"""
	Return negative binomial (NB) loss and complementary loss functions for NB
	distribution with shape parameters :math:`r` and :math:`p`. The pmf of this distribution
	is given by

	.. math::

		f(x) = {x+r-1 \\choose r-1}p^r(1-p)^x

	(See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html.)

	If ``mean`` and ``sd`` are provided instead of ``r`` and ``p``, the function calculates
	:math:`r` and :math:`p` from ``mean`` (:math:`\\mu`) and ``sd``	 (:math:`\\sigma`) using

	.. math::

		r = \\frac{\\mu^2}{\\sigma^2 - \\mu}

	.. math::

		p = 1 - \\frac{\\sigma^2 - \\mu}{\\sigma^2}

	Assumes ``mean < sd**2``; an exception is raised if not.

	Parameters
	----------
	x : int
		Argument of loss function.
	r : int, optional
		Shape parameter of NB distribution representing number of successes until Bernoulli trials stop.
	p : float, optional
		Shape parameter of NB distribution representing success probability for one Bernoulli trial.
	mean : float, optional
		Mean of NB distribution. Ignored if ``r`` and ``p`` are both provided, required otherwise.
	sd : float, optional
		Standard deviation of NB distribution. Ignored if ``r`` and ``p`` are both provided, required otherwise.

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` or ``r`` is not an integer.
	ValueError
		If ``r`` and ``p`` are not both provided and ``mean`` and ``sd`` are also not both provided.
	ValueError
		If ``mean`` is not less than ``sd ** 2``.


	**Equations Used** (Zipkin (2000), Section C.2.3.6, and equation (C.14)):

	.. math::

		n(x) = -(x - r*\\beta)(1-F(x)) + (x + r) * \\beta * f(x),

	where :math:`\\beta = (1-p)/p`.

	.. math::

		\\bar{n}(x) = x - E[X] + n(x)

	(Note that Zipkin (2000) uses a different version of the negative-binomial distribution.
	The notation has been adjusted to account for the version we use here.)

	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> negative_binomial_loss(14, 4, 0.2)
		(4.447304632028364, 2.447304632028364)
		>>> negative_binomial_loss(14, mean=23, sd=8)
		(9.326459980156931, 0.32645998015693145)
	"""

	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Check that correct parameters have been provided.
	if (r is None or p is None) and (mean is None or sd is None):
		raise ValueError("Either r and p or mean and sd must be provided")

	# Calculate mean and sd from r and p, or vice-versa.
	if r is None or p is None:
		r = 1.0 * mean ** 2 / (sd ** 2 - mean)
		p = 1 - (sd ** 2 - mean) / (sd ** 2)
	else:
		mean = (1 - p) * r / p
		sd = math.sqrt((1 - p) * r) / p

	# Check that mean < sigma^2.
	if not mean < sd ** 2:
		raise ValueError("mean must be less than variance")

	beta = (1 - p) / p

	# Calculate f(x) and F(x).
	f = nbinom.pmf(x, r, p)
	F = nbinom.cdf(x, r, p)

	n = -(x - r * beta) * (1 - F) + (x + r) * beta * f
	n_bar = x - mean + n

	return n, n_bar


def negative_binomial_second_loss(x, r=None, p=None, mean=None, sd=None):
	"""
	Return :math:`n^{(2)}(x)` and :math:`\\bar{n}^{(2)}(x)``, the second-order
	exponential loss function and complementary second-order loss function for a
	negative binomial (NB) distribution with shape parameters :math:`r` and :math:`p`.
	The pmf of this distribution is given by

	.. math::

		f(x) = {x+r-1 \\choose r-1}p^r(1-p)^x

	(See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html.)

	If ``mean`` and ``sd`` are provided instead of ``r`` and ``p``, the function calculates
	:math:`r` and :math:`p` from ``mean`` (:math:`\\mu`) and ``sd``	 (:math:`\\sigma`) using

	.. math::

		r = \\frac{\\mu^2}{\\sigma^2 - \\mu}

	.. math::

		p = 1 - \\frac{\\sigma^2 - \\mu}{\\sigma^2}

	Assumes ``mean < sd**2``; an exception is raised if not.

	Parameters
	----------
	x : int
		Argument of loss function.
	r : int, optional
		Shape parameter of NB distribution representing number of successes until Bernoulli trials stop.
	p : float, optional
		Shape parameter of NB distribution representing success probability for one Bernoulli trial.
	mean : float, optional
		Mean of NB distribution. Ignored if `r` and `p` are both provided, required otherwise.
	sd : float, optional
		Standard deviation of NB distribution. Ignored if `r` and `p` are both provided, required otherwise.

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n^{(2)}(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}^{(n)}(x)`]

	Raises
	------
	ValueError
		If ``x`` or ``r`` is not an integer.
	ValueError
		If ``r`` and ``p`` are not both provided and ``mean`` and ``sd`` are also not both provided.
	ValueError
		If ``mean`` is not less than ``sd ** 2``.


	**Equations Used** (Zipkin (2000), Section C.2.3.6, and (C.40)):

	.. math::

		n^{(2)}(x) = \\frac12\\left[\\left[r(r+1)\\beta^2 - 2r\\beta x + x(x+1)\\right](1-F(x))
		+ \\left[(r+1)\\beta - x\\right](x+r)\\beta f(x)\\right],

	where :math:`\\beta = (1-p)/p`.

	.. math::

		\\bar{n}^{(2)}(x) = \\frac12\\left((x-E[X])^2 + (x-E[X]) + \\text{Var}[X]\\right) - n^{(2)}(x)

	(Note that Zipkin (2000) uses a different version of the negative-binomial distribution.
	The notation has been adjusted to account for the version we use here.)

	References
	----------
	P. H. Zipkin, *Foundations of Inventory Management*, Irwin/McGraw-Hill (2000).


	**Example**:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> negative_binomial_second_loss(14, 4, 0.2)
		(30.877804945158942, 10.122195054841043)
		>>> negative_binomial_second_loss(14, mean=23, sd=8)
		(67.10108087745232, 0.8989191225476816)

	"""
	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Check that correct parameters have been provided.
	if (r is None or p is None) and (mean is None or sd is None):
		raise ValueError("Either r and p or mean and sd must be provided")

	# Calculate mean and sd from r and p, or vice-versa.
	if r is None or p is None:
		r = 1.0 * mean ** 2 / (sd ** 2 - mean)
		p = 1 - (sd ** 2 - mean) / (sd ** 2)
	else:
		mean = (1 - p) * r / p
		sd = math.sqrt((1 - p) * r) / p

	# Check that mean < sigma^2.
	if not mean < sd ** 2:
		raise ValueError("mean must be less than variance")

	beta = (1 - p) / p

	# Calculate f(x) and F(x).
	f = nbinom.pmf(x, r, p)
	F = nbinom.cdf(x, r, p)

	n = 0.5 * ((r * (r + 1) * beta**2 - 2 * r * beta * x + x * (x + 1)) * (1 - F) \
		+ ((r + 1) * beta - x) * (x + r) * beta * f)
	n_bar = 0.5 * ((x - mean)**2 + (x - mean) + sd**2) - n

	return n, n_bar


def discrete_loss(x, distrib=None, pmf=None):
	"""
	Return loss and complementary loss function for an arbitrary discrete
	distribution.

	Must provide either ``rv_discrete`` distribution (in ``distrib``) or
	demand pmf (in ``pmf``, as a ``dict``).

	Assumes :math:`F(x) = 0` for :math:`x < 0` (where :math:`F(\\cdot)` is the cdf).

	Parameters
	----------
	x : int
		Argument of loss function.
	distrib : rv_discrete, optional
		Desired distribution.
	pmf : dict, optional
		pmf, as a dict in which keys are the support of the distribution and
		values are their probabilities. Ignored if distrib is not None.

	Returns
	-------
	n : float
		Loss function. [:math:`n(x)`]
	n_bar : float
		Complementary loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` is not an integer.
	ValueError
		If ``distrib`` and ``pmf`` are both ``None``.


	**Equations Used** (equations (C.36) and (C.37)):

	.. math::

		n(x) = \\sum_{y=x}^\\infty (y-x)f(y) = \\sum_{y=x}^\\infty \\bar{F}(y)dy

		\\bar{n}(x) = \\sum_{y=-\\infty}^x (x-y)f(y) = \\sum_{-\\infty}^{x-1} F(y)dy


	**Example**:

	Calculate loss function for :math:`\\text{geom}(0.2)` distribution, by declaring a
	custom ``rv_discrete`` distribution:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> from scipy import stats
		>>> class my_geom(stats.rv_discrete):
		...     def _pmf(self, x):
		...         return np.where(x >= 1, ((1 - 0.2) ** (x - 1)) * 0.2, 0)
		>>> my_dist = my_geom()
		>>> discrete_loss(4, my_dist)
		(2.0479999999999743, 1.048)

	Or by using a "frozen" built-in exponential distribution:

	.. doctest::

		>>> from scipy.stats import geom
		>>> my_dist = geom(0.2)
		>>> discrete_loss(4, my_dist)
		(2.048, 1.048)
	"""
	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Check that either distribution or pmf have been supplied.
	if (distrib is None) and (pmf is None):
		raise ValueError("must provide distrib or pmf")

	if distrib is not None:
		# rv_discrete object has been provided.
		n_bar = float(np.sum([distrib.cdf(range(int(x)))]))
		n = n_bar - x + distrib.mean()

		# Old (slower) method:
		# n = 0.0
		# y = x
		# comp_cdf = 1 - distrib.cdf(y)
		# while comp_cdf > 1.0e-12:
		# 	n += comp_cdf
		# 	y += 1
		# 	comp_cdf = 1 - distrib.cdf(y)
		#
		# n_bar = 0.0
		# for y in range(0, int(x)):
		# 	n_bar += distrib.cdf(y)
	else:
		# pmf dict has been provided.
		x_values = list(pmf.keys())
		x_values.sort()
		n = float(np.sum([(y - x) * pmf[y] for y in x_values if y >= x]))
		n_bar = float(np.sum([(x - y) * pmf[y] for y in x_values if y <= x]))

	return n, n_bar


def discrete_second_loss(x, distrib=None, pmf=None):
	"""
	Return second-order loss and complementary loss function for an arbitrary discrete
	distribution.

	Must provide either ``rv_discrete`` distribution (in ``distrib``) or
	demand pmf (in ``pmf``, as a ``dict``).

	Assumes the random variable cannot take negative values; i.e.,
	:math:`F(x) = 0` for :math:`x < 0` (where :math:`F(\\cdot)` is the cdf).

	Parameters
	----------
	x : int
		Argument of loss function.
	distrib : rv_discrete, optional
		Desired distribution.
	pmf : dict, optional
		pmf, as a dict in which keys are the support of the distribution and
		values are their probabilities. Ignored if distrib is not ``None``.

	Returns
	-------
	n2 : float
		Second-order loss function. [:math:`n(x)`]
	n2_bar : float
		Complementary second-order loss function. [:math:`\\bar{n}(x)`]

	Raises
	------
	ValueError
		If ``x`` is not an integer.
	ValueError
		If ``distrib`` and ``pmf`` are both ``None``.


	**Equations Used** (equations (C.38)-(C.40)):

	.. math::

		n^{(2)}(x) = \\frac12\\sum_{y=x}^\infty (y-x)(y-x-1)f(y) = \\sum_{y=x}^\\infty (y-x)(1-F(y))

		\\bar{n}^{(2)}(x) = \\frac12\\sum_{y=0}^x (x-y)(x+1-y)f(y) = \\sum_{y=0}^x (x-y)F(y)

	.. math::

		\\bar{n}^{(2)}(x) = \\frac12\\left(\\left(x - E[X]\\right)^2 + (x - E[X]) + \\text{Var}[X]\\right) - n^{(2)}(x)

	**Example**:

	Calculate loss function for :math:`\\text{geom}(0.2)` distribution, by declaring a
	custom ``rv_discrete`` distribution:

	.. testsetup:: *

		from stockpyl.loss_functions import *

	.. doctest::

		>>> from scipy import stats
		>>> class my_geom(stats.rv_discrete):
		...     def _pmf(self, x):
		...         return np.where(x >= 1, ((1 - 0.2) ** (x - 1)) * 0.2, 0)
		>>> my_dist = my_geom()
		>>> discrete_loss(4, my_dist)
		(2.0479999999999743, 1.048)

	Or by using a "frozen" built-in exponential distribution:

	.. doctest::

		>>> from scipy.stats import geom
		>>> my_dist = geom(0.2)
		>>> discrete_loss(4, my_dist)
		(2.048, 1.048)
	"""
	# Check for integer x.
	if not is_integer(x):
		raise ValueError("x must be an integer")

	# Check that either distribution or pmf have been supplied.
	if (distrib is None) and (pmf is None):
		raise ValueError("must provide distrib or pmf")

	if distrib is not None:
		# rv_discrete object has been provided.

		# Calculate E[X] and Var[x].
		E, V = distrib.stats(moments='mv')

		# Calculate loss functions.
		n2_bar = float(np.dot([np.subtract(x, range(int(x)))], distrib.cdf(range(int(x)))))
		n2 = 0.5 * ((x - E)**2 + (x - E) + V) - n2_bar

	else:
		# pmf dict has been provided.
		x_values = list(pmf.keys())
		x_values.sort()
		n2 = 0.5 * float(np.sum([(y - x) * (y - x - 1) * pmf[y] for y in x_values if y >= x]))
		n2_bar = 0.5 * float(np.sum([(x - y) * (x + 1 - y) * pmf[y] for y in x_values if y <= x]))

	return n2, n2_bar



