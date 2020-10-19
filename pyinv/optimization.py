"""Optimization-related functions.

(c) Lawrence V. Snyder
Lehigh University

"""

import math


def golden_section_search(f, a, b, tol=1e-5):
	"""Golden-section search. Adapted from https://en.wikipedia.org/wiki/Golden-section_search.
	This implementation reuses function evaluations, saving 1/2 of the evaluations
	per iteration, and returns a bounding interval.

	Given a function ``f`` with a single local minimum in the interval [``a``,``b``],
	returns a point within ``tol`` of the minimizer.

	**Example**:

	.. testsetup:: *

		from pyinv.optimization import *

	.. doctest::

		>>> f = lambda x: (x-2)**2
		>>> a = 1
		>>> b = 5
		>>> tol = 1e-5
		>>> x = golden_section_search(f, a, b, tol)
		>>> print(x)
		2.0000005374905

	Parameters
	----------
	f : function
		Function to optimize.
	a : float
		Lower end of interval to optimize over.
	b : float
		Upper end of interval to optimize over.
	tol : float, optional
		Tolerance. Algorithm terminates when the interval being considered has
		width less than or equal to ``tol``.

	Returns
	-------
	x_star : float
		Optimizer of ``f``.
	f_star : float
		Optimal value of ``f``.

	"""
	# TODO: comment this better

	# Calculate golden-section quantities.
	invphi = (math.sqrt(5) - 1) / 2  # 1 / phi
	invphi2 = (3 - math.sqrt(5)) / 2  # 1 / phi^2

	(a, b) = (min(a, b), max(a, b))
	h = b - a
	if h <= tol:
		return (a, b)

	# Calculate required number of steps to achieve tolerance.
	n = int(math.ceil(math.log(tol / h) / math.log(invphi)))

	c = a + invphi2 * h
	d = a + invphi * h
	yc = f(c)
	yd = f(d)

	for k in range(n-1):
		if yc < yd:
			b = d
			d = c
			yd = yc
			h = invphi * h
			c = a + invphi2 * h
			yc = f(c)
		else:
			a = c
			c = d
			yc = yd
			h = invphi * h
			d = a + invphi * h
			yd = f(d)

	if yc < yd:
		x_star = (a + d) / 2
	else:
		x_star = (c + b) / 2

	f_star = f(x_star)

	return x_star, f_star
