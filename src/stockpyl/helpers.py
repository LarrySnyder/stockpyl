"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_helpers| module contains helper functions that are used by functions throughout the 
|sp| package.

API Reference
-------------


"""

import math
from scipy import stats
from scipy.special import comb
from scipy.stats import rv_discrete, rv_continuous
from math import factorial
import numpy as np
from itertools import product
from collections import defaultdict


### CONSTANTS ###

BIG_INT = 1e100
BIG_FLOAT = 1.0e100


### UTILITY FUNCTIONS ###

def min_of_dict(d):
	"""Determine min value of a dict and return min and argmin (key).

	Values must be numeric.

	Parameters
	----------
	d : dict
		The dict.

	Returns
	-------
	min_value : float
		Minimum value in dict.
	min_key : any
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
	unless ``require_presence`` is ``True``, in which case the dict must have the
	key to count as a match.

	Parameters
	----------
	d1 : node
		First dict for comparison.
	d2 : node
		Second dict for comparison.
	require_presence : bool, optional
		Set to ``True`` to require dicts to have the same keys, or ``False``
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
	"""Determine whether ``x`` is an iterable or a singleton.

	Parameters
	----------
	x : any
		Object to test for iterable vs. singleton.

	Returns
	-------
	bool
		``True`` if ``x`` is iterable, ``False`` if it is a singleton.

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
	x : any
		Object to test for list-ness.

	Returns
	-------
	bool
		``True`` if ``x`` is a list, ``False`` otherwise.

	"""
	return isinstance(x, list)


def is_set(x):
	"""Determine whether x is a set.
	
	Parameters
	----------
	x : any
		Object to test for set-ness.

	Returns
	-------
	bool
		``True`` if ``x`` is a set, ``False`` otherwise.

	"""
	return isinstance(x, set)


def is_dict(x):
	"""Determine whether x is a dict.

	Parameters
	----------
	x : any
		Object to test for dict-ness.

	Returns
	-------
	bool
		``True`` if ``x`` is a dict, ``False`` otherwise.

	"""
	return isinstance(x, dict)


def is_integer(x):
	"""Determine whether ``x`` is an integer. Return ``True`` if ``x`` is an int,
	or a float that evaluates to an integer, ``False`` otherwise.

	Parameters
	----------
	x : float
		Number to check for integrality.

	Returns
	-------
	bool
		``True`` if ``x`` is an integer, ``False`` otherwise.

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


def is_numeric_string(s):
	"""Determine whether ``s`` is a string that represents a number. 

	Parameters
	----------
	s : str
		String to check for integrality.

	Returns
	-------
	bool
		``True`` if ``s`` represents a number, ``False`` otherwise.

	"""
	if not isinstance(s, str):
		return False
	else:
		# https://stackoverflow.com/q/354038/3453768
		try:
			float(s)
			return True
		except ValueError:
			return False


def is_discrete_distribution(distribution):
	"""Check whether the given distribution object is discrete.

	Works both for ``rv_frozen`` objects and for custom distributions (i.e., subclasses of
	``rv_continuous`` and ``rv_discrete``).

	See https://stackoverflow.com/a/61530461/3453768.

	Parameters
	----------
	distribution : rv_frozen, rv_continuous, or rv_discrete
		The distribution object to check.

	Returns
	-------
	bool
		``True`` if the distribution is discrete, ``False`` otherwise.


	.. note:: Not reliable if ``distribution`` is not an ``rv_frozen``, ``rv_discrete``,
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

	Works both for ``rv_frozen`` objects and for custom distributions (i.e., subclasses of
	``rv_continuous`` and ``rv_discrete``).

	See https://stackoverflow.com/a/61530461/3453768.

	Parameters
	----------
	distribution : rv_frozen, rv_continuous, or rv_discrete
		The distribution object to check.

	Returns
	-------
	bool
		``True`` if the distribution is continuous, ``False`` otherwise.


	.. note:: Not reliable if ``distribution`` is not an ``rv_frozen``, ``rv_discrete``,
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


def nearest_dict_value(key_to_search, the_dict):
	"""Return the value in ``the_dict`` corresponding to the key that is closest
	to ``key_to_search``.

	Parameters
	----------
	key_to_search : float
		The number to search for among the keys.
	the_dict : dict
		The dictionary to search.
	"""

	# https://stackoverflow.com/a/7934624/3453768
	return the_dict.get(key_to_search, the_dict[min(the_dict.keys(), key=lambda k: abs(k-key_to_search))])


def find_nearest(array, values, sorted=False, index=dict()):
	"""Determine entries in ``array`` that are closest to each of the
	entries in ``values`` and return their indices. Neither array needs to be sorted,
	but if ``array`` is sorted and ``sorted`` is set to ``True``, execution will be faster. In dictionary ``index`` a
	map to desired indices can be provided, in which case execution will be even faster for specified values. ``array``
	and ``values`` need not be the same length.

	Parameters
	----------
	array : ndarray
		The array to search for values in.
	values : ndarray
		The array whose values should be searched for in the other array.
	sorted : bool, optional
		If ``True``, treats array as sorted, which will make the function execute faster.
	index : dict, optional
		A dictionary from values to indices, which will make the function execute even faster for
		given values.

	Returns
	-------
	ind : ndarray
		Array of indices.
	"""
	array = np.asarray(array)
	values = np.array(values, ndmin=1, copy=False)
	ind = np.zeros(values.shape)
	for v in range(values.size):
		ind[v] = index.get(values[v])
		if np.isnan(ind[v]):
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
	"""Check whether ``iterable_list`` is a list in which every item is an iterable of the
	same size *or* a singleton.

	**Examples:**

	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> check_iterable_sizes([[5, 3, 1], ('a', 'b', 'c'), 7])
		True
		>>> check_iterable_sizes([[5, 3, 1], ('a', 'b'), 7])
		False

	Parameters
	----------
	iterable_list : list
		List to check.

	Returns
	-------
	bool
		``True`` if ``iterable_list`` is a list in which every item is an iterable of the
		same size *or* a singleton, ``False`` otherwise.

	"""
	# Build set of lengths of items in list, excluding singletons.
	lengths = {len(i) for i in iterable_list if is_iterable(i) and len(i) != 1}

	# Check whether lengths contains at most one element.
	return len(lengths) <= 1


def ensure_list_for_time_periods(x, num_periods, var_name=None):
	"""Ensure that ``x`` is a list suitable for time-period indexing; if not, create
	such a list and return it.

	"Suitable for time-period indexing" means that it has length ``num_periods`` + 1,
	and the 0th element is ignored.

	* If ``x`` is a singleton, return a list consisting of ``num_periods`` copies of ``x`` plus
	  a ``0`` in the 0th element.
	* If ``x`` is a list of length ``num_periods``+1, return ``x``.
	* If ``x`` is a list of length ``num_periods``, shift elements to the right by 1 slot, 
	  fill the 0th element with 0, and return new list.
	* If ``x`` is a numpy array, convert to list first, then follow above rules.
	* Otherwise, raise a ``ValueError``.

	**Examples:**
	
	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> ensure_list_for_time_periods(5, 3)
		[0, 5, 5, 5]
		>>> ensure_list_for_time_periods([0, 5, 2, 1], 4)
		[0, 0, 5, 2, 1]
		>>> ensure_list_for_time_periods([5, 2, 1, 3, 2], 4)
		[5, 2, 1, 3, 2]
		>>> ensure_list_for_time_periods([0, 5, 2, 1, 5], 3)
		Traceback (most recent call last):
			...
		ValueError: x must be a singleton or a list of length num_periods or num_periods+1


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

	Raises
	------
	ValueError
		If ``x`` is not a singleton or a list of length ``num_periods`` or ``num_periods`` + 1.
	"""
	# If numpy array, convert to list.
	if isinstance(x, np.ndarray):
		x = x.tolist()

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
	"""Ensure that ``x`` is a list suitable for node indexing; if not, create
	such a list and return it.

	"Suitable for node indexing" means that it has length ``num_nodes``.

	* If ``x`` is a singleton, return a list consisting of ``num_nodes`` copies of ``x``.
	* If ``x`` is a list of length ``num_nodes``, return ``x``.
	* If ``x`` is ``None`` and ``default`` is provided, return a list consisting of
	  ``num_nodes`` copies of ``default``.
	* If ``x`` is ``None`` and ``default`` is not provided, a list consisting of 
	  ``num_nodes`` copies of ``None``.
	* Otherwise, raise a ``ValueError``.

	**Examples:**
	
	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> ensure_list_for_nodes(5, 3)
		[5, 5, 5]
		>>> ensure_list_for_nodes([0, 5, 2, 1], 4)
		[0, 5, 2, 1]
		>>> ensure_list_for_nodes([0, 5, 2, 1], 3)
		Traceback (most recent call last):
			...
		ValueError: x must be a singleton, a list of length num_nodes, or None


	Parameters
	----------
	x : float or list
		Object to node-ify.
	num_nodes : int
		Number of nodes.
	default : float, optional
		Value to use if ``x`` is ``None``.

	Returns
	-------
	x_new : list
		Node-ified list.

	Raises
	------
	ValueError
		If ``x`` is not a singleton, a list of length ``num_nodes``, or ``None``.
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
				raise ValueError('x must be a singleton, a list of length num_nodes, or None')
		else:
			return [x] * num_nodes


def build_node_data_dict(attribute_dict, node_order_in_lists, default_values={}):
	"""Build a dict of dicts containing data for all nodes and for one or more attributes.
	The dict returned, ``data_dict``, is keyed by the node indices. 
	``data_dict[n]`` is a dict of data for the node with index ``n``, and 
	``data_dict[n][a]`` is the value of attribute ``a``, where ``a`` is in a key
	in ``attribute_dict``.

	:func:`~build_node_data_dict` is similar to calling :func:`~ensure_dict_for_nodes` for multiple
	attributes simultaneously.

	For each attribute ``a`` in ``attribute_dict`` keys, ``attribute_dict[a]`` 
	may take one of several forms. For a given node index ``n`` and attribute ``a``:

		* If ``attribute_dict[a]`` is a dict, then ``data_dict[n][a]`` is set to
		  ``attribute_dict[a][n]``. If ``n`` is not a key in ``attribute_dict[a]``
		  then ``data_dict[n][a]`` is set to ``default_values[a]`` if it exists
		  and to ``None`` otherwise.
		* If ``attribute_dict[a]`` is a singleton, then ``data_dict[n][a]`` is set to
		  ``attribute_dict[a]``.
		* If ``attribute_dict[a]`` is a list with the same length as ``node_order_in_lists``,
		  then the values in the list are assumed to correspond to the node indices in the
		  order they are specified in ``node_order_in_lists``. That is, ``attribute_dict[a][k]`` 
		  is placed in ``data_dict[node_order_in_lists[k]][a]``, for ``k`` in ``range(len(node_order_in_lists))``.
		* If ``attribute_dict[a]`` is ``None`` and ``default_values[a]`` is provided, 
		  ``data_dict[n][a]`` is set to ``default_values[a]``. 
		  (This is useful for setting default values for attributes that are passed without knowing 
		  whether data is provided for them.)
		* If ``attribute_dict[a]`` is ``None`` and ``default_values[a]`` is not provided, 
		  ``data_dict[n][a]`` is set to ``None``.
		* If ``attribute_dict[a]`` is a list that does *not* have the same length as ``node_order_in_lists``, a ``ValueError`` is raised.

	(Exception: The ``demand_list`` and ``probabilities`` attributes of |class_demand_source| are lists,
	and are treated as singletons for the purposes of the rules above, unless they contain other lists, in which 
	case they are treated as normal. For example, ``attribute_dict['demand_list'] = [0, 1, 2, 3]`` will set the ``demand_list`` to
	``[0, 1, 2, 3]`` for all nodes. But ``demand_list=[[0, 1, 2, 3], [0, 1, 2, 3], None, None]`` will set the ``demand_list`` to 
	``[0, 1, 2, 3]`` for nodes 0 and 1 but to ``None`` for nodes 2 and 3.)


	Parameters
	----------
	attribute_dict : dict
		Dict whose keys are strings (representing node attributes) and whose values
		are dicts, lists, and/or singletons specifying the values of the attributes for the nodes.
	node_order_in_lists : list
		List of node indices in the order in which the nodes are listed in any
		attributes that are lists. (``node_order_in_lists[k]`` is the index of the ``k`` th node.)
	default_values : dict
		Dict whose keys are strings (in ``attribute_dict.keys()`` ) and whose values
		are the default values to use if the attribute is not provided.


	Returns
	-------
	data_dict : dict
		The data dict.

	Raises
	------
	ValueError
		If ``attribute_dict[a]`` is a list whose length does not equal that of ``node_order_in_lists``.


	**Example:**
	
	.. testsetup:: *

		from stockpyl.helpers import build_node_data_dict

	.. doctest::

		>>> attribute_dict = {}
		>>> attribute_dict['local_holding_cost'] = 1
		>>> attribute_dict['stockout_cost'] = [10, 8, 0]
		>>> attribute_dict['demand_mean'] = {1: 0, 3: 50}
		>>> attribute_dict['lead_time'] = None
		>>> attribute_dict['processing_time'] = None
		>>> node_order_in_lists = [3, 2, 1]
		>>> default_values = {'lead_time': 0, 'demand_mean': 99}
		>>> data_dict = build_node_data_dict(attribute_dict, node_order_in_lists, default_values)
		>>> data_dict[1]
		{'local_holding_cost': 1, 'stockout_cost': 0, 'demand_mean': 0, 'lead_time': 0, 'processing_time': None}
		>>> data_dict[2]
		{'local_holding_cost': 1, 'stockout_cost': 8, 'demand_mean': 99, 'lead_time': 0, 'processing_time': None}
		>>> data_dict[3]
		{'local_holding_cost': 1, 'stockout_cost': 10, 'demand_mean': 50, 'lead_time': 0, 'processing_time': None}

	"""

	# Initialize data_dict.
	data_dict = {n: {} for n in node_order_in_lists}

	# Loop through attributes in attribute_names.
	for a in attribute_dict:

		# What type is ``attribute_dict[a]``?
		if attribute_dict[a] is None:
			
			# Use default (if any).
			for n in node_order_in_lists:
				if a in default_values:
					data_dict[n][a] = default_values[a]
				else:
					data_dict[n][a] = None

		elif type(attribute_dict[a]) == dict:

			for n in node_order_in_lists:
				# Is n a key in attribute_dict[a]?
				if n in attribute_dict[a]:
					# Yes: use it.
					data_dict[n][a] = attribute_dict[a][n]
				elif a in default_values:
					# No, but default value is provided; use it instead.
					data_dict[n][a] = default_values[a]
				else:
					# No, and no default value is provided; use None.
					data_dict[n][a] = None
		
		# If it's a list and a = 'demand_list' or 'probabilities', treat it as a list if any of its elements
		# and as a singleton othwerwise.
		elif is_iterable(attribute_dict[a]) and \
			(a not in ('demand_list', 'probabilities') or any([is_iterable(e) for e in attribute_dict[a]])):

			# attribute_dict[a] is a list; check its length.
			if len(list(attribute_dict[a])) == len(node_order_in_lists):
				for k in range(len(node_order_in_lists)):
					data_dict[node_order_in_lists[k]][a] = attribute_dict[a][k]
			else:
				raise ValueError('attribute_dict[a] must be a singleton, dict, list with the same length as node_indices, or None for all a in attribute_names')

		else:

			# attribute_dict[a] is a singleton (or is a list-type attribute). 
			for n in node_order_in_lists:
				data_dict[n][a] = attribute_dict[a]

	return data_dict


def ensure_dict_for_nodes(x, node_indices, default=None):
	"""Ensure that ``x`` is a dict with node indices as ``keys``; if not, create
	such a dict and return it.

	* If ``x`` is a dict, return ``x``.
	* If ``x`` is a singleton, return a dict with keys equal to ``node_indices``
	  and values all equal to ``x``.
	* If ``x`` is a list with the same length as ``node_indices``, return a dict
	  with keys equal to ``node_indices`` and values equal to ``x``.
	* If ``x`` is ``None`` and ``default`` is provided, return a dict with keys
	  equal to ``node_indices`` and values all equal to ``default``.
	* If ``x`` is ``None`` and ``default`` is not provided, return a dict with
	  keys equal to ``node_indices`` and values all equal to ``None``.
	* Otherwise, raise a ``ValueError``.


	Parameters
	----------
	x : dict, float, or list
		Object to node-ify.
	node_indices : list
		List of node indices. (``node_indices[k]`` is the index of the ``k`` th node.)
	default : float, optional
		Value to use if ``x`` is ``None``.

	Returns
	-------
	x_new : dict
		Node-ified dict.

	Raises
	------
	ValueError
		If ``x`` is not a dict, a singleton, a list with the same length as ``node_indices``, or ``None``.


	**Examples:**
	
	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> ensure_dict_for_nodes(5, [0, 1, 2])
		{0: 5, 1: 5, 2: 5}
		>>> ensure_dict_for_nodes([0, 5, 2], [0, 1, 2])
		{0: 0, 1: 5, 2: 2}
		>>> ensure_list_for_nodes([0, 5, 2, 1], [0, 1, 2])
		Traceback (most recent call last):
			...
		ValueError: x must be a singleton, dict, list with the same length as node_indices, or None

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
				raise ValueError('x must be a singleton, dict, list with the same length as node_indices, or None')
		else:
			return {node_indices[i]: x for i in range(len(node_indices))}


def sort_dict_by_keys(d, ascending=True, return_values=True):
	"""Sort dict by keys and return sorted list of values or keys, depending
	on the value of ``return_values``.

	Keys must all be comparable to one another, i.e., all numbers or all strings,
	with the exception that ``None`` keys are allowed.
	Special handling is included to handle keys that are ``None``.
	(``None`` is assumed to come before any other element when sorting in
	ascending order.)

	**Example:**

	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> the_dict = {'a': 5, None: 14, 'b': 7}
		>>> sort_dict_by_keys(the_dict)
		[14, 5, 7]
		>>> sort_dict_by_keys(the_dict, return_values=False)
		[None, 'a', 'b']

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

	
def sort_nested_dict_by_keys(d, ascending=True, return_values=True):
	"""Sort nested dict by its first two levels of keys and return sorted 
	list of values or keys, depending on the value of ``return_values``.
	If ``return_values`` is ``False``, the list returned
	contains tuples ``(key1, key2)``, where ``key1`` is the key from the
	outer dict and ``key2`` is the key from the inner dict.

	Keys must all be comparable to one another, i.e., all numbers or all strings,
	with the exception that ``None`` keys are allowed.
	Special handling is included to handle keys that are ``None``.
	(``None`` is assumed to come before any other element when sorting in
	ascending order.)

	**Example:**

	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> the_dict = {'a': 5, None: 14, 'b': 7}
		>>> sort_dict_by_keys(the_dict)
		[14, 5, 7]
		>>> sort_dict_by_keys(the_dict, return_values=False)
		[None, 'a', 'b']

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
	# Replace nested dict with one in which the first two levels are replaced by a tuple.
	# Also replace any None keys with -inf so they will always be sorted first (if ascending order).
	flattened_dict = {(key1 if key1 is not None else float('-inf'), key2 if key2 is not None else float('-inf')): \
							d[key1][key2] for key1 in d.keys() for key2 in d[key1].keys()}

	if return_values:
		# Build sorted list of values (sorted by keys) in flattened_dict.
		return_list = [value for _, value in sorted(flattened_dict.items(), reverse=not ascending)]
	else:
		# Build sorted list of keys in flattened_dict.
		return_list = [key for key, _ in sorted(flattened_dict.items(), reverse=not ascending)]

		# Replace -inf with None.
		return_list = [(None if key1 == -float('inf') else key1, None if key2 == -float('inf') else key2) \
						for key1, key2 in return_list]

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
	KeyError
		If ``dict_to_change[old_key]`` is undefined.
	"""
	# Change key.
	# See https://stackoverflow.com/a/4406521/3453768.
	dict_to_change[new_key] = dict_to_change.pop(old_key)


def replace_dict_numeric_string_keys(dict_to_change):
	"""Replace any key in ``dict_to_change`` that is a string representing an integer with 
	the integer itself. Return a new dict.
	Works recursively to replace numeric-string keys in any values in ``dict_to_change``, etc.

	Parameters
	----------
	dict_to_change : dict
		The dict.

	Returns
	-------
	dict
		The new dict.
	"""
	new_dict = {}
	for old_key, v in dict_to_change.items():

		# If v is a dict, call this function recursively on it.
		if is_dict(v):
			v = replace_dict_numeric_string_keys(v)
			
		# Determine new key, if any.
		if is_numeric_string(old_key):
			# Change key.
			new_key = float(old_key)
			if is_integer(new_key):
				new_key = int(old_key)
		else:
			new_key = old_key
		# Add item to dict.
		new_dict[new_key] = v

	return new_dict


def replace_dict_null_keys(dict_to_change):
	"""Replace any key in ``dict_to_change`` that equals the string ``'null'`` with ``None``.
	Return a new dict.
	Works recursively to replace ``'null'``'`` keys in any values in ``dict_to_change``, etc.

	Parameters
	----------
	dict_to_change : dict
		The dict.

	Returns
	-------
	dict
		The new dict.
	"""
	new_dict = {}
	for old_key, v in dict_to_change.items():

		# If v is a dict, call this function recursively on it.
		if is_dict(v):
			v = replace_dict_null_keys(v)
			
		# Determine new key, if any.
		if old_key == 'null':
			new_key = None
		else:
			new_key = old_key
		# Add item to dict.
		new_dict[new_key] = v

	return new_dict

def compare_unhashable_lists(list1, list2):
	"""Determine whether ``list1`` and ``list2`` have the same elements, with the same
	counts, not necessarily in the same order. Return ``True`` if they do, ``False`` otherwise.

	.. note:: Only use this function for lists of unhashable objects (such as |class_node|
		and |class_product|). For hashable objects, ``collections.Counter`` is faster, e.g.,
		``Counter(list1) == Counter(list2)``.

	Parameters
	----------
	list1 : list
		The first list to compare.
	list2 : list
		The second list to compare.

	Returns
	-------
	bool
		``True`` if the two lists have the same elements, with the same counts, not 
		neceessarily in the same order, ``False`` otherwise.
	"""
	# https://stackoverflow.com/a/7829388/3453768

	if len(list1) != len(list2):
		return False
		
	list1 = list(list1)   # make a mutable copy
    
	try:
		for elem in list2:
			list1.remove(elem)
	except ValueError:
		return False
    
	return not list1


### STATS FUNCTIONS ###

def convolve_many(arrays):
	"""Convolve a list of 1-dimensional float arrays together, using 
	fast Fourier transforms (FFTs).
	The arrays need not have the same length, but each array should
	have length at least 1.

	If the arrays represent pmfs of discrete random variables
	:math:`X_1,\\ldots,X_n`, then the output represents the pmf of
	:math:`X_1+\\cdots+X_n`. Assuming the possible values of all of the random
	variables are equally spaced with spacing :math:`s`, the possible values of
	:math:`X_1+\\cdots+X_n` corresponding to the output are
	:math:`\\sum_i\\min X_i,\\ldots,\\sum_i \\max X_i`, with spacing :math:`s`.

	Code is adapted from https://stackoverflow.com/a/29236193/3453768.

	Parameters
	----------
	arrays : list of 1-dimensional float arrays
		The arrays to convolve.

	Returns
	-------
	convolution : array
		Array of elements in the convolution.


	**Example:**
	Let :math:`X_1 = \\{0, 1, 2\\}` with probabilities :math:`[0.6, 0.3, 0.1]`,
	:math:`X_2 = \\{0, 1, 2\\}` with probabilities :math:`[0.5, 0.4, 0.1]`,
	:math:`X_3 = \\{0, 1\\}` with probabilities :math:`[0.3, 0.7]`, and
	:math:`X_4 = 0` with probability :math:`1`.

	.. testsetup:: *

		from stockpyl.helpers import *

	.. doctest::

		>>> convolve_many([[0.6, 0.3, 0.1], [0.5, 0.4, 0.1], [0.3, 0.7], [1.0]])
		array([0.09 , 0.327, 0.342, 0.182, 0.052, 0.007])

	In other words, :math:`X_1+\\cdots+X_4 = \\{0, 1, \\ldots, 5\\}` with
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
	convolution = convolution.real

	# Ensure values in convolution are >= 0. Sometimes ifft will produce slightly
	# negative values due to rounding error.
	ROUNDING_TOL = 1.0e-10
	for i in range(len(convolution)):
		if convolution[i] < -ROUNDING_TOL:
			raise ValueError("np.fft.ifft returned negative results in convolve_many()")
		elif -ROUNDING_TOL <= convolution[i] < 0:
			convolution[i] = 0

	return convolution


def irwin_hall_cdf(x, n):
	"""Return cdf of Irwin-Hall distribution, i.e., distribution of sum of ``n``
	:math:`U[0,1]` random variables.

	See https://en.wikipedia.org/wiki/Irwin%E2%80%93Hall_distribution.

	Parameters
	----------
	x : float
		Argument of cdf function.
	n : int
		Number of :math:`U[0,1]` random variables in the sum.

	Returns
	-------
	F : float
		The cdf of ``x``.
	"""

	F = 0
	for k in range(int(np.floor(x)) + 1):
		F += ((-1) ** k) * comb(n, k) * (x - k) ** n
	F /= factorial(n)

	return F


def sum_of_continuous_uniforms_distribution(n, lo=0, hi=1):
	"""Return distribution of sum of ``n`` identical continuous uniform random variables as an
	``rv_continuous`` object.

	If ``lo`` = 0 and ``hi`` = 1, this distribution is the Irwin-Hall distribution.

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
		The ``rv_continuous`` object.

	Raises
	------
	ValueError
		If ``n`` is not an integer.

	"""

	class sum_of_continuous_uniforms_rv(stats.rv_continuous):

		def _cdf(self, x):
			# P(X <= x) = P(Y <= (y - n * lo) / (hi - lo)), where Y is the sum of
			# n U[0,1] r.v.s and therefore has an Irwin-Hall distribution.
			if x < n * lo:
				return 0
			elif x > n * hi:
				return 1
			else:
				return irwin_hall_cdf((x - n * lo) / (hi - lo), n)

	# Check whether n is an integer.
	if not is_integer(n):
		raise ValueError("n must be an integer")

	distribution = sum_of_continuous_uniforms_rv()

	return distribution


def sum_of_discrete_uniforms_pmf(n, lo, hi):
	"""Calculate pmf of sum of ``n`` identical discrete uniform random variables. 
	Return values as dict.

	Adapted from https://stackoverflow.com/a/69842911/3453768.

	Parameters
	----------
	n : int
		Number of uniform random variables in the sum.
	lo : int
		Lower bound of uniform distribution.
	hi : int
		Upper bound of uniform distribution.

	Returns
	-------
	dict
		Dictionary of pmf values.

	Raises
	------
	ValueError
		If ``n`` is not an integer.
	"""
	# Check whether n is an integer.
	if not is_integer(n):
		raise ValueError("n must be an integer")

	du_pmf = {i: 1/(hi-lo+1) for i in range(lo, hi+1)}
	du_sum_pmf = {0: 1}

	for i in range(n):
		new_sum_pmf = defaultdict(float)
		for prev_sum, dice in product(du_sum_pmf, du_pmf):
			new_sum_pmf[prev_sum + dice] += du_sum_pmf[prev_sum] * du_pmf[dice]
		du_sum_pmf = new_sum_pmf

	return du_sum_pmf
				

def sum_of_discrete_uniforms_distribution(n, lo, hi):
	"""Return distribution of sum of ``n`` identical discrete uniform random variables as an
	``rv_continuous`` object.

	Parameters
	----------
	n : int
		Number of uniform random variables in the sum.
	lo : int
		Lower bound of uniform distribution.
	hi : int
		Upper bound of uniform distribution.

	Returns
	-------
	distribution : rv_discrete
		The ``rv_discrete`` object.

	Raises
	------
	ValueError
		If ``n`` is not an integer.

	"""
	
	# Check whether n is an integer.
	if not is_integer(n):
		raise ValueError("n must be an integer")

	pmf = sum_of_discrete_uniforms_pmf(n, lo, hi)

	distribution = stats.rv_discrete(name='sum_of_discrete_uniforms', values=(list(pmf.keys()), list(pmf.values())))

	return distribution
	
	
def sum_of_discretes_distribution(n, lo, hi, p):
	"""Return distribution of convolution of ``n`` identical discrete random variables as an
	``rv_discrete`` object.

	The random variables must have support ``lo``, ``lo`` + 1, ..., ``hi``.
	(The convolution will have support ``n * lo``, ``n * lo`` + 1, ..., ``n * hi``).


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
		The ``rv_discrete`` object.

	Raises
	------
	ValueError
		If ``n``, ``lo``, or ``hi`` are not integers.
	ValueError
		If ``p`` does not have length ``hi - lo + 1``.

	"""


	# Check whether n, lo, and hi are integers.
	if not is_integer(n):
		raise ValueError("n must be an integer")
	if not is_integer(lo):
		raise ValueError("lo must be an integer")
	if not is_integer(hi):
		raise ValueError("hi must be an integer")

	# Check that p has length hi - lo + 1. (If not, it probably means the calling
	# function did not add 0s for values that are not part of the support.)
	if len(p) != hi - lo + 1:
		raise ValueError("p must have length hi - lo + 1. (If the support of the discrete distribution \
			is not consecutive integers, you must add zeroes to p for the integers that are not part of the support)")

	xk = np.arange(n * lo, n * hi + 1)
	pk = convolve_many([p for _ in range(n)])

	distribution = stats.rv_discrete(name='sum_of_discretes', values=(xk, pk))

	return distribution


def round_dict_values(the_dict, round_type=None):
	"""Round the values in a dict. Return a new dict.

	Parameters
	----------
	the_dict : dict
		The dict to round
	round_type : string, optional
		Set to 'up' to round all values up to next larger integer, 'down' to 
		round down, 'nearest' to round to nearest integer, or ``None`` to not round at all.
	"""

	new_dict = {}

	for key, value in the_dict.items():
		if round_type == 'up':
			new_dict[key] = math.ceil(value)
		elif round_type == 'down':
			new_dict[key] = math.floor(value)
		elif round_type == 'nearest':
			new_dict[key] = round(value)
		else:
			new_dict[key] = value

	return new_dict
	

### JSON-RELATED FUNCTIONS ###

def serialize_set(obj):
	"""Serialize a set by converting it to a dict of the form
	``{'type': 'set', 'elements': elements}``, where ``elements`` are
	the elements of the set.

	This is used for serializing objects so they can be saved in JSON format. 
	To use: ``json.dump(json_contents, file, default=serialize_set)``.

	Parameters
	----------
	obj : Any
		The object to serialize.

	Returns
	-------
	dict
		Dictionary representation of ``obj``, if ``obj`` is a set.
	"""
	if is_set(obj):
		return {
			'type': 'set',
			'elements': list(obj)
		}


def deserialize_set(obj):
	"""Deserialize a set of the form ``{'type': 'set', 'elements': elements}``
	by converting it to a set of the form ``{elements}``.
		
	This is used for deserializing objects to they can be loaded from JSON format.
	To use: ``json.load(file, object_hook=deserialize_set)``.

	Parameters
	----------
	obj : Any
		The object to deserialize.

	Returns
	-------
	set
		Set representation of ``obj``, if ``obj`` is a dict of the appropriate form.
	"""
	# https://realpython.com/python-serialize-data/
	if is_dict(obj) and 'type' in obj and obj['type'] == 'set' and 'elements' in obj:
		return set(obj['elements'])
	else:
		return obj
			

