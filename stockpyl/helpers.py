"""Helper functions for stockpyl package.

(c) Lawrence V. Snyder
Lehigh University

"""

import math
from scipy import stats
from scipy.special import comb
from scipy.stats import uniform
from scipy.stats import rv_discrete, rv_continuous
from math import factorial
import numpy as np

#from datatypes import *


### CONSTANTS ###

BIG_INT = 1e100
BIG_FLOAT = 1.0e100


### UTILITY FUNCTIONS ###

def min_of_dict(d):
	"""Determine min value of dict and return min and argmin (key).

	Values must be numeric.

	Parameters
	----------
	d : dict
		The dict.

	Returns
	-------
	min_value : float
		Minimum value in dict.
	min_key
		Key that attains minimum value.

	Raises
	------
	TypeError
		If dict contains a non-numeric value.
	"""
	min_key = min(d, key=d.get)
	min_value = d[min_key]

	return min_value, min_key


def dict_match(d1, d2, require_presence=False, rel_tol=1e-9, abs_tol=0.0):
	"""Check whether two dicts have equal keys and values.

	A missing key is treated as 0 if the key is present in the other dict,
	unless require_presence is True, in which case the dict must have the
	key to count as a match.

	Parameters
	----------
	d1 : node
		First dict for comparison.
	d2 : node
		Second dict for comparison.
	require_presence : bool, optional
		Set to True to require dicts to have the same keys, or False
		(default) to treat missing keys as 0s.
	rel_tol : float
		Relative tolerance.
	abs_tol : float
		Absolute tolerance.
	"""

	match = True

	# Check d1 against d2.
	for key in d1.keys():
		if key in d2:
			if not math.isclose(d1[key], d2[key], rel_tol=rel_tol, abs_tol=abs_tol):
				match = False
		else:
			if not math.isclose(d1[key], 0, rel_tol=rel_tol, abs_tol=abs_tol) \
					or require_presence:
				match = False

	# Check d2 against d1.
	for key in d2.keys():
		if key in d2:
			# We already checked in this case.
			pass
		else:
			if not math.isclose(d2[key], 0, rel_tol=rel_tol, abs_tol=abs_tol) \
					or require_presence:
				match = False

	return match


def is_iterable(x):
	"""Determine whether x is an iterable or a singleton.

	Parameters
	----------
	x
		Object to test for iterable vs. singleton.

	Returns
	-------
	True if x is iterable, False if it is a singleton.

	"""
	# First check whether x is a string (because strings act like iterables).
	if isinstance(x, str):
		return False
	else:
		try:
			_ = iter(x)
	#		_ = (y for y in x)
		except TypeError:
			return False
		else:
			return True


def is_list(x):
	"""Determine whether x is a list.

	Parameters
	----------
	x
		Object to test for list-ness.

	Returns
	-------
	True if x is a list, False otherwise.

	"""
	return isinstance(x, list)


def is_integer(x):
	"""Determine whether x is an integer. Return False if x is not a float,
	or is a non-integer float, or is an int.

	Parameters
	----------
	x : float
		Number to check for integrality.

	Returns
	-------
	is_int : bool
		True if x is an integer, False otherwise.

	"""
	# Check whether x is an int.
	if isinstance(x, int):
		return True
	# Check whether x is a float.
	elif isinstance(x, float):
		# Check whether x is an integer.
		if x.is_integer():
			return True
		else:
			return False
	else:
		return False


def is_discrete_distribution(distribution):
	"""Check whether the given distribution object is discrete.

	Works both for ``rv_frozen`` objects (i.e., `frozen distributions
	<https://docs.scipy.org/doc/scipy/reference/tutorial/stats.html#freezing-a
	-distribution>`_) and for custom distribution (i.e., subclasses of
	``rv_continuous`` and ``rv_discrete``).

	See https://stackoverflow.com/a/61530461/3453768.

	Parameters
	----------
	distribution : rv_frozen, rv_continuous, or rv_discrete
		The distribution object to check.

	Returns
	-------
	``True`` if the distribution is discrete, ``False`` otherwise.

	Notes
	-----
	Not reliable if ``distribution`` is not an ``rv_frozen``, ``rv_discrete``,
	or ``rv_continuous`` object.

	"""
	# First check whether distribution is a frozen distribution (in which case
	# it has a .dist attribute which must be checked).
	if hasattr(distribution, 'dist'):
		# Check .dist attribute to determine type.
		return isinstance(distribution.dist, rv_discrete)
	else:
		# Check the object itself for type.
		return isinstance(distribution, rv_discrete)


def is_continuous_distribution(distribution):
	"""Check whether the given distribution object is continuous.

	Works both for ``rv_frozen`` objects (i.e., `frozen distributions
	<https://docs.scipy.org/doc/scipy/reference/tutorial/stats.html#freezing-a
	-distribution>`_) and for custom distribution (i.e., subclasses of
	``rv_continuous`` and ``rv_discrete``).

	See https://stackoverflow.com/a/61530461/3453768.

	Parameters
	----------
	distribution : rv_frozen, rv_continuous, or rv_discrete
		The distribution object to check.

	Returns
	-------
	``True`` if the distribution is continuous, ``False`` otherwise.

	Notes
	-----
	Not reliable if ``distribution`` is not an ``rv_frozen``, ``rv_discrete``,
	or ``rv_continuous`` object.

	"""
	# First check whether distribution is a frozen distribution (in which case
	# it has a .dist attribute which must be checked).
	if hasattr(distribution, 'dist'):
		# Check .dist attribute to determine type.
		return isinstance(distribution.dist, rv_continuous)
	else:
		# Check the object itself for type.
		return isinstance(distribution, rv_continuous)


def find_nearest(array, values, sorted=False):
	"""Determine entries in ``array` that are closest to each of the
	entries in ``values`` and return their indices. Neither array needs to be sorted,
	but if ``array`` is sorted and ``sorted`` is set to ``True``, execution will be faster.
	``array`` and ``values`` need not be the same length.

	Parameters
	----------
	array : ndarray
		The array to search for values in.
	values : ndarray
		The array whose values should be searched for in the other array.
	sorted : Boolean
		If ``True``, treats array as sorted, which will make the function execute
		faster.

	Returns
	-------
	ind : ndarray
		Array of indices.
	"""
	array = np.asarray(array)
	values = np.array(values, ndmin=1, copy=False)
	ind = np.zeros(values.shape)
	for v in range(values.size):
		if sorted:
			# https://stackoverflow.com/a/26026189/3453768
			idx = np.searchsorted(array, values[v], side="left")
			if idx > 0 and (idx == len(array) or math.fabs(values[v] - array[idx-1])
					< math.fabs(values[v] - array[idx])):
				ind[v] = idx-1
			else:
				ind[v] = idx
		else:
			# https://stackoverflow.com/a/2566508/3453768
			idx = (np.abs(array - values[v])).argmin()
			ind[v] = idx

	return ind.astype(int)


### LIST-HANDLING FUNCTIONS ###

def check_iterable_sizes(iterable_list):
	"""Check whether `iterable_list` is a list in which every item is an iterable of the
	same size _or_ a singleton.

	Examples:
		- ensure_iterable_sizes([[5, 3, 1], ('a', 'b', 'c'), 7]) returns True
		- ensure_iterable_sizes([[5, 3, 1], ('a, 'b'), 7]) returns False

	Parameters
	----------
	iterable_list : list
		List to check.

	Returns
	-------
	True if `iterable_list` is a list in which every item is an iterable of the
	same size _or_ a singleton, False otherwise.
	"""
	# Build set of lengths of items in list, excluding singletons.
	lengths = {len(i) for i in iterable_list if is_iterable(i) and len(i) != 1}

	# Check whether lengths contains at most one element.
	return len(lengths) <= 1


def ensure_list_for_time_periods(x, num_periods, var_name=None):
	"""Ensure that `x` is a list suitable for time-period indexing; if not, create
	such a list and return it.

	"Suitable for time-period indexing" means that it has length num_periods+1,
	and element [0] is ignored.

	If x is a singleton, return a list consisting of `num_periods` copies of x.
	If x is a list of length `num_periods`, return x.
	If x is a list of length `num_periods`-1, shift elements to the right by 1 slot,
		fill [0] element with 0, and return new list.
	Otherwise, raise a ValueError.

	Examples:
		- ensure_list_for_time_periods(5, 3) returns [5, 5, 5]
		- ensure_list_for_time_periods([0, 5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_for_time_periods([5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_for_time_periods([0, 5, 2, 1], 3) raises a ValueError.

	Parameters
	----------
	x : float or list
		Object to time-period-ify.
	num_periods : int
		Number of time periods.
	var_name : str, optional
		Variable name to use in generating error messages, if desired.
		Useful for offloading the type-checking to this function rather than
		doing it in the calling function.

	Returns
	-------
	x_new : list
		Time-period-ified list.
	"""
	# Determine whether x is singleton or iterable.
	if is_iterable(x):
		if len(x) == num_periods+1:
			return x
		elif len(x) == num_periods:
			return [0] + x
		else:
			if var_name is None:
				vname = 'x'
			else:
				vname = var_name
			raise ValueError('{:s} must be a singleton or a list of length num_periods or num_periods+1'.format(vname))
	else:
		return [0] + [x] * num_periods


def ensure_list_for_nodes(x, num_nodes, default=None):
	"""Ensure that x is a list suitable for node indexing; if not, create
	such a list and return it.

	"Suitable for node indexing" means that it has length num_nodes.

	If x is a singleton, return a list consisting of `num_nodes` copies of x.
	If x is a list of length `num_nodes`, return x.
	If x is None and `default` is provided, return a list consisting of
		`num_nodes` copies of `default`.
	If x is None and `default` is not provided, a list consisting of
	 	`num_nodes` copies of None.
	Otherwise, raise a ValueError.

	Examples:
		- ensure_list_for_nodes(5, 3) returns [5, 5, 5]
		- ensure_list_for_nodes([0, 5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_for_nodes([0, 5, 2, 1], 3) raises a ValueError.

	Parameters
	----------
	x : float or list
		Object to node-ify.
	num_nodes : int
		Number of nodes.
	default : float, optional
		Value to use if x is None.

	Returns
	-------
	x_new : list
		Node-ified list.
	"""
	# Is x None?
	if x is None:
		return [default] * num_nodes
	else:
		# Determine whether x is singleton or iterable.
		if is_iterable(x):
			if len(list(x)) == num_nodes:
				return list(x)
			else:
				raise ValueError('x must be a singleton or a list of length num_nodes')
		else:
			return [x] * num_nodes


def ensure_dict_for_nodes(x, node_indices, default=None):
	"""Ensure that x is a dict suitable with node indices as keys(); if not, create
	such a dict and return it.

	If ``x`` is a dict, return ``x``.
	If ``x`` is a singleton, return a dict with keys equal to ``node_indices``
		and values all equal to ``x``.
	If ``x`` is a list with the same length as ``node_indices``, return a dict
		with keys equal to ``node_indices`` and values equal to ``x``.
	If ``x`` is ``None`` and ``default`` is provided, return a dict with keys
		equal to ``node_indices`` and values all equal to ``default``.
	If ``x`` is ``None`` and ``default`` is not provided, return a dict with
		keys equal to ``node_indices`` and values all equal to ``None``.
	Otherwise, raise a ``ValueError``.

	Examples:
		- ensure_dict_for_nodes(5, [0, 1, 2]) returns {0: 5, 1: 5, 2:5}.
		- ensure_dict_for_nodes([0, 5, 2], [0, 1, 2]) returns {0: 0, 1: 5, 2: 2}.
		- ensure_list_for_nodes([0, 5, 2, 1], [0, 1, 2]) raises a ValueError.

	Parameters
	----------
	x : dict, float, or list
		Object to node-ify.
	node_indices : list
		List of node indices.
	default : float, optional
		Value to use if ``x`` is ``None``.

	Returns
	-------
	x_new : dict
		Node-ified dict.
	"""
	# Is x None?
	if type(x) == dict:
		return x
	elif x is None:
		return {n_ind: default for n_ind in node_indices}
	else:
		# Determine whether x is singleton or iterable.
		if is_iterable(x):
			if len(list(x)) == len(node_indices):
				return {node_indices[i]: x[i] for i in range(len(x))}
			else:
				raise ValueError('x must be a singleton, dict, or list with the same length as node_indices')
		else:
			return {node_indices[i]: x for i in range(len(node_indices))}


def sort_dict_by_keys(d, ascending=True, return_values=True):
	"""Sort dict by keys and return sorted list of values or keys, depending
	on the value of ``return_values``.
	Special handling is included to handle keys that might be ``None``.
	(``None`` is assumed to come before any other element when sorting in
	ascending order.)

	Parameters
	----------
	d : dict
		The dict to sort.
	ascending : bool, optional
		Sort order.
	return_values : bool, optional
		Set to ``True`` to return a list of the dict's values, ``False`` to
		return its keys.

	Returns
	-------
	return_list : list
		List of values or keys of ``d``, sorted in order of keys of ``d``.

	"""
	# Create dict equal to d but without None key.
	dict_without_none = {key: d[key] for key in d.keys() if key is not None}

	if return_values:
		# Build sorted list of values in dict_without_none.
		return_list = [value for _, value in sorted(dict_without_none.items(), reverse=not ascending)]

		# If original dict had None key, add it back.
		if None in d.keys():
			if ascending:
				return_list.insert(0, d[None])
			else:
				return_list.append(d[None])
	else:
		# Build sorted list of keys in dict_without_none.
		return_list = [key for key, _ in sorted(dict_without_none.items(), reverse=not ascending)]

		# If original dict had None key, add it back.
		if None in d.keys():
			if ascending:
				return_list.insert(0, None)
			else:
				return_list.append(None)

	return return_list


def change_dict_key(dict_to_change, old_key, new_key):
	"""Change ``old_key`` to ``new_key`` in ``dict_to_change`` (in place).
	New key/value pair will appear at end of dict.

	Parameters
	----------
	dict_to_change : dict
		The dict.
	old_key :
		The key to be changed.
	new_key :
		The key to change to.

	Raises
	------
	KeyError : if dict_to_change[old_key] is undefined.
	"""
	# Change key.
	# See https://stackoverflow.com/a/4406521/3453768.
	dict_to_change[new_key] = dict_to_change.pop(old_key)


### STATS FUNCTIONS ###

def convolve_many(arrays):
	"""Convolve a list of 1-dimensional float arrays together, using FFTs.
	The arrays need not have the same length, but each array should
	have length at least 1.

	If the arrays represent pmfs of discrete random variables
	:math:`X_1,\\ldots,X_n`, then the output represents the pmf of
	:math:`X_1+\\cdots+X_n`. Assuming the possible values of all of the random
	variables are equally spaced with spacing :math:`s`, the possible values of
	:math:`X_1+\\cdots+X_n` corresponding to the output are
	:math:`\\min_i\\{\\min X_i\\},\\ldots,\\sum_i \\max X_i`, with spacing :math:`s`.

	Code is adapted from https://stackoverflow.com/a/29236193/3453768.

	Parameters
	----------
	arrays : list of 1-dimensional float arrays
		The arrays to convolve.

	Returns
	-------
	convolution : array
		Array of elements in the convolution.

	**Example**
	Let :math:`X_1 = \\{0, 1, 2\\}` with probabilities :math:`[0.6, 0.3, 0.1]`,
	:math:`X_2 = \\{0, 1, 2\\}` with probabilities :math:`[0.5, 0.4, 0.1]`,
	:math:`X_3 = \\{0, 1\\}` with probabilities :math:`[0.3, 0.7]`, and
	:math:`X_4 = 0` with probability :math:`1`.

	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> convolve_many([[0.6, 0.3, 0.1], [0.5, 0.4, 0.1], [0.3, 0.7], [1.0]])
		array([0.09 , 0.327, 0.342, 0.182, 0.052, 0.007])

	In other words, :math:`X_1+\\cdots+X_4 = \\{0, 1, \\ldots, 5\\}`: with
	probabilities :math:`[0.09 , 0.327, 0.342, 0.182, 0.052, 0.007]`.

	"""
	result_length = 1 + sum((len(a) - 1) for a in arrays)

	# Copy each array into a 2d array of the appropriate shape.
	rows = np.zeros((len(arrays), result_length))
	for i, a in enumerate(arrays):
		rows[i, :len(a)] = a

	# Transform, take the product, and do the inverse transform
	# to get the convolution.
	fft_of_rows = np.fft.fft(rows)
	fft_of_convolution = fft_of_rows.prod(axis=0)
	convolution = np.fft.ifft(fft_of_convolution)

	# Assuming real inputs, the imaginary part of the output can be ignored.
	return convolution.real


def irwin_hall_cdf(x, n):
	"""Return cdf of Irwin-Hall distribution, i.e., distribution of sum of ``n``
	U[0,1] random variables.

	See https://en.wikipedia.org/wiki/Irwin%E2%80%93Hall_distribution.

	Parameters
	----------
	x : float
		Argument of cdf function.
	n : int
		Number of U[0,1] random variables in the sum.

	Returns
	-------
	F : float
		The cdf of ``x``.
	"""

	# TODO vectorize this
	F = 0
	for k in range(int(np.floor(x)) + 1):
		F += ((-1) ** k) * comb(n, k) * (x - k) ** n
	F /= factorial(n)

	return F


def sum_of_uniforms_distribution(n, lo=0, hi=1):
	"""Return distribution of sum of ``n`` identical uniform random variables as
	``rv_continuous`` object.

	If ``lo`` = 0 and ``hi`` = 1, this distribution is the Irwin-Hall
	distribution.

	Parameters
	----------
	n : int
		Number of uniform random variables in the sum.
	lo : float, optional
		Lower bound of uniform distribution. Default = 0.
	hi : float, optional
		Upper bound of uniform distribution. Default = 1.

	Returns
	-------
	distribution : rv_continuous
		The rv_continuous object.

	"""

	class sum_of_uniforms_rv(stats.rv_continuous):
		def _cdf(self, x):
			# P(X <= x) = P(Y <= (y - n * lo) / (hi - lo)), where Y is the sum of
			# n U[0,1] r.v.s and therefore has an Irwin-Hall distribution.
			if x < n * lo:
				return 0
			elif x > n * hi:
				return 1
			else:
				return irwin_hall_cdf((x - n * lo) / (hi - lo), n)

	distribution = sum_of_uniforms_rv()

	return distribution


def sum_of_discretes_distribution(n, lo, hi, p):
	"""Return distribution of convolution of ``n`` identical discrete random variables as
	``rv_discrete`` object.

	The random variables must have support ``lo``, ``lo``+1, ..., ``hi``.
	(The convolution will have support ``n * lo``, ``n * lo``+1, ..., ``n * hi``.


	Parameters
	----------
	n : int
		Number of uniform random variables in the sum.
	lo : int
		Smallest value of the support of the random variable.
	hi : int
		Largest value of the support of the random variable.
	p : list
		Probabilities of each of the values.

	Returns
	-------
	distribution : rv_discrete
		The rv_discrete object.

	"""

	xk = np.arange(n * lo, n * hi + 1)
	pk = convolve_many([p for _ in range(n)])

	distribution = stats.rv_discrete(name='sum_of_discretes', values=(xk, pk))

	return distribution


def run_irwin_hall_cdf_test():
	"""Test ``helpers.irwin_hall_cdf()``. This is not a unit test; it must be
	run manually. It simulates many sums of uniform distributions and plots
	their empirical cdf against the calculated cdf.

	"""

	n = 4
	T = 100000
	nbins = 100

	sums = []
	for t in range(T):
		sums.append(np.sum(uniform.rvs(size=n)))

	x = np.arange(0, n, n * 1.0/nbins)
	F_empirical = np.zeros(np.size(x))
	F_calc = np.zeros(np.size(x))
	for b in range(nbins):
		F_empirical[b] = np.sum(1 if sums[t] < x[b] else 0 for t in range(T)) / T
		F_calc[b] = irwin_hall_cdf(x[b], n)

	import matplotlib.pyplot as plt

	plt.plot(x, F_empirical, 'r')
	plt.plot(x, F_calc, 'b')
	plt.show()


def run_sum_of_uniforms_distribution_test():
	"""Test ``helpers.sum_of_uniforms_distribution()``. This is not a unit test;
	it must be run manually. It simulates many sums of uniform distributions and
	plots their empirical cdf against the calculated cdf.

	"""

	n = 4
	lo = 20
	hi = 60
	T = 10000
	nbins = 100

	sums = []
	for t in range(T):
		sums.append(np.sum(uniform.rvs(lo, hi-lo, size=n)))

	dist = sum_of_uniforms_distribution(n, lo, hi)

	x = np.arange(n*lo, n*hi, n * (hi-lo)/nbins)
	F_empirical = np.zeros(np.size(x))
	F_calc = np.zeros(np.size(x))
	for b in range(nbins):
		F_empirical[b] = np.sum(1 if sums[t] < x[b] else 0 for t in range(T)) / T
		F_calc[b] = dist.cdf(x[b])

	import matplotlib.pyplot as plt

	plt.plot(x, F_empirical, 'r')
	plt.plot(x, F_calc, 'b')
	plt.show()



#test_irwin_hall_cdf()
#test_sum_of_uniforms_distribution()

