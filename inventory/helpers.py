"""Helper functions for inventory package.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import math

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
	#		_ = iter(x)
			_ = (y for y in x)
		except TypeError:
			return False
		else:
			return True


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


def ensure_list_for_time_periods(x, num_periods):
	"""Ensure that x is a list suitable for time-period indexing; if not, create
	such a list and return it.

	"Suitable for time-period indexing" means that it has length num_periods+1,
	and element [0] is ignored.

	If x is a singleton, return a list consisting of 'length' copies of x.
	If x is a list of length 'length', return x.
	If x is a list of length 'length'-1, shift elements to the right by 1 slot,
		fill [0] element with 0, and return new list.
	Otherwise, raise a ValueError.

	Examples:
		- ensure_list_of_length(5, 3) returns [5, 5, 5]
		- ensure_list_of_length([0, 5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_of_length([5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_of_length([0, 5, 2, 1], 3) rasies a ValueError.

	Parameters
	----------
	x : float or list
		Object to time-period-ify.
	num_periods : int
		Number of time periods.

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
			raise ValueError('x must be a singleton or a list of length num_periods or num_periods+1')
	else:
		return [0] + [x] * num_periods
