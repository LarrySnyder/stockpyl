# ===============================================================================
# stockpyl - DemandSource Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

This module contains the |class_demand_source| class. A |class_demand_source|
object represents external demand observed by a node.
The demand can be random or deterministic. Attributes specify the type of demand
distribution and its parameters. The object can generate demands from the specified distribution.

.. note:: |fosct_notation|

**Example:** Create a |class_demand_source| object representing demand that has a normal
distribution with a mean of 50 and a standard deviation of 10. Generate a random demand from the distribution.

	.. testsetup:: *

		from stockpyl.demand_source import *

	.. doctest::

		>>> ds = DemandSource(type='N', mean=50, standard_deviation=10)
		>>> ds.generate_demand()	# doctest: +SKIP
		46.75370030596123
		>>> # Tell object to round demands to integers.
		>>> ds.round_to_int = True
		>>> ds.generate_demand()	# doctest: +SKIP
		63

API Reference
-------------

"""


# ===============================================================================
# Imports
# ===============================================================================

import numpy as np
import scipy.stats 

from stockpyl.helpers import *

# ===============================================================================
# DemandSource Class
# ===============================================================================

ALLOWABLE_TYPES = ('N', 'P', 'UD', 'UC', 'NB', 'D', 'CD', None)
class DemandSource(object):
	"""
	A |class_demand_source| object represents external demand observed by a node.
	The demand can be random or deterministic. Attributes specify the type of demand
	distribution and its parameters. The object can generate demands from the specified distribution.

	Parameters
	----------
	**kwargs 
		Keyword arguments specifying values of one or more attributes of the |class_demand_source|, 
		e.g., ``type='N'``.

	Attributes
	----------
	type : str
		The demand type, as a string. Currently supported strings are:

			* None
			* 'N' (normal)
			* 'P' (Poisson)
			* 'UD' (uniform discrete)
			* 'UC' (uniform continuous)
			* 'NB' (negative binomial)
			* 'D' (deterministic)
			* 'CD' (custom discrete)
			
	round_to_int : bool
		Round demand to nearest integer?
	demand_list : list, optional
		List of demands, one per period (for deterministic demand types), or list
		of possible demand values (for custom discrete demand types). For deterministic
		demand types, if demand is required in a period beyond the length of the list,
		the list is restarted at the beginning. This also allows ``demand_list`` to be
		a singleton, in which case it is used in every period.
		Required if ``type`` == 'D' or 'CD'. [:math:`d`]
	probabilities : list, optional
		List of probabilities of each demand value (for custom discrete demand types).
		Required if ``type`` == 'CD'.
	lo : float, optional
		Low value of demand range (for uniform demand types). Required if
		``type`` == 'UD' or 'UC'.
	hi : float, optional
		High value of demand range (for uniform demand types). Required if
		``type`` == 'UD' or 'UC'.
	n : int, optional
		Parameter for negative binomial distribution indicating number of trial successes. 
		Required if ``type`` == 'NB'. [:math:`n`]
	p : float, optional
		Parameter for negative binomial distribution indicating probability of success for each trial. 
		Required if ``type`` == 'NB'. [:math:`p`]
	"""

	def __init__(self, **kwargs):
		"""DemandSource constructor method.

		Parameters
		----------
		kwargs : optional
			Optional keyword arguments to specify |class_demand_source| attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match class_demand_source| attribute.
		"""
		# Initialize parameters.
		self.initialize()

		# Set attributes specified by kwargs.
		for key, value in kwargs.items():
			if key in vars(self):
				vars(self)[key] = value
			elif f"_{key}" in vars(self):
				vars(self)[f"_{key}"] = value
			else:
				raise AttributeError(f"{key} is not an attribute of DemandSource")

	_DEFAULT_VALUES = {
		'_type': None,
		'_mean': None,
		'_standard_deviation': None,
		'_demand_list': None,
		'_probabilities': None,
		'_lo': None,
		'_hi': None,
		'_n': None,
		'_p': None,
		'_round_to_int': None
	}

	# SPECIAL METHODS

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to this demand source object. 
		Two demand source objects are considered equal if all of their attributes 
		are equal.

		Parameters
		----------
		other : |class_demand_source|
			The demand source object to compare to.

		Returns
		-------
		bool
			True if the demand source objects are equal, False otherwise.

		"""
		if other is None:
			return False
		else:
			for attr in self._DEFAULT_VALUES.keys():
				if getattr(self, attr) != getattr(other, attr):
					return False
			return True

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to this demand source object. 
		Two demand source objects are considered equal if all of their attributes 
		are equal.

		Parameters
		----------
		other : |class_demand_source|
			The demand source object to compare to.

		Returns
		-------
		bool
			True if the demand source objects are not equal, False otherwise.
		"""
		return not self.__eq__(other)

	# PROPERTY GETTERS AND SETTERS

	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value):
		self._type = value

	@property
	def mean(self):
		"""Return mean set by user, if any; or, for distributions whose mean is not
		set but is calculated from other parameters, returns the calculated mean.
		If neither is true, return ``None``.
		"""
		if self._mean is not None:
			return self._mean
		elif self.type in ('UC', 'UD', 'NB', 'CD'):
			return self.demand_distribution.mean()
		else:
			return None

	@mean.setter
	def mean(self, value):
		self._mean = value

	@property
	def standard_deviation(self):
		"""Return standard deviation set by user, if any; or, for distributions whose standard deviation is not
		set but is calculated from other parameters, returns the calculated standard deviation.
		If neither is true, return ``None``.
		"""
		if self._standard_deviation is not None:
			return self._standard_deviation
		elif self.type in ('P', 'UC', 'UD', 'NB', 'CD'):
			return self.demand_distribution.std()
		else:
			return None

	@standard_deviation.setter
	def standard_deviation(self, value):
		self._standard_deviation = value

	@property
	def demand_list(self):
		return self._demand_list

	@demand_list.setter
	def demand_list(self, value):
		self._demand_list = value

	@property
	def probabilities(self):
		return self._probabilities

	@probabilities.setter
	def probabilities(self, value):
		self._probabilities = value

	@property
	def lo(self):
		return self._lo

	@lo.setter
	def lo(self, value):
		self._lo = value

	@property
	def hi(self):
		return self._hi

	@hi.setter
	def hi(self, value):
		self._hi = value

	@property
	def n(self):
		return self._n

	@n.setter
	def n(self, value):
		self._n = value

	@property
	def p(self):
		return self._p

	@p.setter
	def p(self, value):
		self._p = value

	@property
	def round_to_int(self):
		return self._round_to_int

	@round_to_int.setter
	def round_to_int(self, value):
		self._round_to_int = value

	# READ-ONLY PROPERTIES
	@property
	def demand_distribution(self):
		"""Demand distribution, as a ``scipy.stats.rv_continuous`` or
		``scipy.stats.rv_discrete`` object. Returns ``None`` if demand source ``type`` is ``'D'``.
		Read only.
		"""
		# Check that the appropriate parameters have been set. If not, raise an exception.
		self.validate_parameters()

		if self.type is None:
			distribution = None
		elif self.type == 'N':
			distribution = scipy.stats.norm(self.mean, self.standard_deviation)
		elif self.type == 'P':
			distribution = scipy.stats.poisson(self.mean)
		elif self.type == 'UD':
			distribution = scipy.stats.randint(self.lo, self.hi+1)
		elif self.type == 'UC':
			distribution = scipy.stats.uniform(self.lo, self.hi - self.lo)
		elif self.type == 'NB':
			distribution = scipy.stats.nbinom(self.n, self.p)
		elif self.type == 'CD':
			distribution = scipy.stats.rv_discrete(name='custom',
												   values=(self.demand_list, self.probabilities))
		else:
			distribution = None

		return distribution
	
	@property
	def is_discrete(self):
		"""``True`` if the distribution is discrete, ``False`` if it is continuous. Read only.

		The distribution is discrete if ``self.type`` is 'P', 'UD', 'CD', 'NB', or 'D'.

		Returns
		-------
		bool
			``True`` if the distribution is discrete, ``False`` if it is continuous.
		"""
		return self.type in ('P', 'UD', 'CD', 'NB', 'D')
	

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the |class_demand_source| instance.

		Returns
		-------
			A string representation of the |class_demand_source| instance.

		"""
		# Build string of parameters.
		if self.type is None:
			return "DemandSource(None)"
		elif self.type == 'N':
			param_str = "mean={:.2f}, standard_deviation={:.2f}".format(
				self.mean, self.standard_deviation)
		elif self.type == 'P':
			param_str = "mean={:.2f}".format(self.mean)
		elif self.type in ('UD', 'UC'):
			param_str = "lo={:.2f}, hi={:.2f}".format(
				self.lo, self.hi)
		elif self.type == 'D':
			if not is_list(self.demand_list) or len(self.demand_list) <= 8:
				param_str = "demand_list={}".format(self.demand_list)
			else:
				param_str = "demand_list={}...".format(self.demand_list[0:8])
		elif self.type == 'NB':
			param_str = "n={:d}, p={:.2f}".format(self.n, self.p)
		elif self.type == 'CD':
			if len(self.demand_list) <= 8:
				param_str = "demand_list={}, probabilities={}".format(
					self.demand_list, self.probabilities)
			else:
				param_str = "demand_list={}..., probabilities={}...".format(
					self.demand_list[0:8], self.probabilities[0:8])
		else:
			param_str = ""

		return "DemandSource({:s}: {:s})".format(self.type, param_str)

	def __str__(self):
		"""
		Return the full name of the |class_demand_source| instance.

		Returns
		-------
			The demand_source name.

		"""
		return self.__repr__()

	# ATTRIBUTE HANDLING

	def initialize(self):
		"""Initialize the parameters in the object to their default values. 
		"""
		for attr in self._DEFAULT_VALUES.keys():
			setattr(self, attr, self._DEFAULT_VALUES[attr])

	def validate_parameters(self):
		"""Check that appropriate parameters have been provided for the given
		demand type. Raise an exception if not.
		"""
		if self.type not in ALLOWABLE_TYPES: raise AttributeError(f"Valid type in {ALLOWABLE_TYPES} must be provided")

		# Note: Importane to use the '_' attributes here, rather than associated properties,
		# to avoid infinite recursion. (For example, if self._mean is None, calling self.mean calls
  		# self.demand_distribution(), which calls self.mean.) Plus, these attributes have to be set by
		# user, not just calculated.
		if self.type == 'N':
			if self._mean is None: raise AttributeError("For 'N' (normal) demand, mean must be provided")
			if self._mean < 0: raise AttributeError("For 'N' (normal) demand, mean must be non-negative")
			if self._standard_deviation is None: raise AttributeError("For 'N' (normal) demand, standard_deviation must be provided")
			if self._standard_deviation < 0: raise AttributeError("For 'N' (normal) demand, standard_deviation must be non-negative")
		elif self.type == 'P':
			if self._mean is None: raise AttributeError("For 'P' (Poisson) demand, mean must be provided")
			if self._mean < 0: raise AttributeError("For 'P' (Poisson) demand, mean must be non-negative")
		elif self.type == 'UD':
			if self._lo is None: raise AttributeError("For 'UD' (uniform discrete) demand, lo must be provided")
			if self._lo < 0 or not is_integer(self._lo): raise AttributeError("For 'UD' (uniform discrete) demand, lo must be a non-negative integer")
			if self._hi is  None: raise AttributeError("For 'UD' (uniform discrete) demand, hi must be provided")
			if self._hi < 0 or not is_integer(self._hi): raise AttributeError("For 'UD' (uniform discrete) demand, hi must be a non-negative integer")
			if self._lo > self._hi: raise AttributeError("For 'UD' (uniform discrete) demand, lo must be <= hi")
		elif self.type == 'UC':
			if self._lo is None: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be provided")
			if self._lo < 0: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be non-negative")
			if self._hi is None: raise AttributeError("For 'UC' (uniform continuous) demand, hi must be provided")
			if self._hi < 0: raise AttributeError("For 'UC' (uniform continuous) demand, hi must be non-negative")
			if self._lo > self._hi: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be <= hi")
		elif self.type == 'NB':
			if self._n is None: raise AttributeError("For 'NB' (negative binomial) demand, n must be provided")
			if self._n <= 0: raise AttributeError("For 'NB' (negative binomial) demand, n must be positive")
			if self._p is None: raise AttributeError("For 'NB' (negative binomial) demand, p must be provided")
			if self._p < 0 or self._p > 1: raise AttributeError("For 'NB' (negative binomial) demand, p must be in [0, 1]")
		elif self.type == 'D':
			if self._demand_list is None: raise AttributeError("For 'D' (deterministic) demand, demand_list must be provided")
		elif self.type == 'CD':
			if self._demand_list is None: raise AttributeError("For 'CD' (custom discrete) demand, demand_list must be provided")
			if self._probabilities is None: raise AttributeError("For 'CD' (custom discrete) demand, probabilities must be provided")
			if len(self._demand_list) != len(self._probabilities): raise AttributeError("For 'CD' (custom discrete) demand, demand_list and probabilities must have equal lengths")
			if np.sum(self._probabilities) != 1: raise AttributeError("For 'CD' (custom discrete) demand, probabilities must sum to 1")

	# CONVERSION TO/FROM DICTS

	def to_dict(self):
		"""Convert the |class_demand_source| object to a dict. List attributes
		(``demand_list``, ``probabilities``) are deep-copied so changes to the original
		object do not get propagated to the dict.

		Returns
		-------
		dict
			The dict representation of the object.
		"""
		# Initialize dict.
		ds_dict = {}

		# Attributes.
		for attr in self._DEFAULT_VALUES.keys():
			# Remove leading '_' to get property names.
			prop = attr[1:] if attr[0] == '_' else attr
			ds_dict[prop] = getattr(self, prop)

		return ds_dict

	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_demand_source| object with attributes copied from the
		values in ``the_dict``. List attributes (``demand_list``, ``probabilities``) 
		are deep-copied so changes to the original dict do not get propagated to the object.
		Any missing attributes are set to their default values.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_demand_source|, typically created using ``to_dict()``.

		Returns
		-------
		DemandSource
			The object converted from the dict.
		"""
		if the_dict is None:
			ds = cls()
		else:
			# Build empty DemandSource.
			ds = cls()
			# Fill attributes.
			for attr in cls._DEFAULT_VALUES.keys():
				# Remove leading '_' to get property names.
				prop = attr[1:] if attr[0] == '_' else attr

				# Some attributes require special handling.
				if prop == 'demand_list':
					if prop not in the_dict or the_dict[prop] is None:
						value = None
					elif the_dict[prop] is not None:
						# If elements of demand_list are dicts (keys = products, values = demands),
	  					# replace string keys with integers.
						value = [{int(k): v for k, v in d.items()} if is_dict(d) else d for d in the_dict[prop]]
				else:
					if prop in the_dict:
						value = the_dict[prop]
					else:
						value = cls._DEFAULT_VALUES[attr]

				# Set the property/attribute.
				setattr(ds, prop, value)
	
		return ds

	# DEMAND GENERATION

	def generate_demand(self, period=None):
		"""Generate a demand value using the demand type specified in ``type``.
		If ``type`` is ``None``, returns ``None``.

		Parameters
		----------
		period : int, optional
			The period to generate a demand value for. If ``type`` = 'D' (deterministic),
			this is required if ``demand_list`` is a list of demands, one per period. If omitted,
			will return first (or only) demand in list.

		Returns
		-------
		demand : float
			The demand value.

		"""

		if self.type is None:
			return None
		if self.type == 'N':
			demand = self._generate_demand_normal()
		elif self.type == 'P':
			demand = self._generate_demand_poisson()
		elif self.type == 'UD':
			demand = self._generate_demand_uniform_discrete()
		elif self.type == 'UC':
			demand = self._generate_demand_uniform_continuous()
		elif self.type == 'NB':
			demand = self._generate_demand_negative_binomial()
		elif self.type == 'D':
			demand = self._generate_demand_deterministic(period)
		elif self.type == 'CD':
			demand = self._generate_demand_custom_discrete()
		else:
			demand = None

		if self.round_to_int:
			demand = int(np.round(demand))

		return demand

	def _generate_demand_normal(self):
		"""Generate demand from normal distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return max(0, float(np.random.normal(self.mean, self.standard_deviation)))

	def _generate_demand_poisson(self):
		"""Generate demand from Poisson distribution.

		Returns
		-------
		demand : int
			The demand value.

		"""
		return int(np.random.poisson(self.mean))

	def _generate_demand_uniform_discrete(self):
		"""Generate demand from discrete uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return int(np.random.randint(int(self.lo), int(self.hi) + 1))

	def _generate_demand_uniform_continuous(self):
		"""Generate demand from continuous uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return float(np.random.uniform(self.lo, self.hi - self.lo))

	def _generate_demand_negative_binomial(self):
		"""Generate demand from negative binomial distribution.

		Returns
		-------
		demand : int
			The demand value.

		"""
		return float(np.random.negative_binomial(self.n, self.p))
	
	def _generate_demand_deterministic(self, period=None):
		"""Generate deterministic demand.

		Parameters
		----------
		period : int, optional
			The period to generate a demand value for. This is required if ``demand_list`` is a 
			list of demands, one per period. If omitted, will return first (or only) demand in list.

		Returns
		-------
		demand : float
			The demand value.

		"""
		if is_iterable(self.demand_list):
			if period is None:
				# Return first demand in demand_list list.
				return self.demand_list[0]
			else:
				# Get demand for period mod (# periods in demand_list list), i.e.,
				# if we are past the end of the demand_list list, loop back to the beginning.
				return self.demand_list[period % len(self.demand_list)]
		else:
			# Return demand_list singleton.
			return self.demand_list

	def _generate_demand_custom_discrete(self):
		"""Generate demand from custom discrete distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.choice(self.demand_list, p=self.probabilities)

	# OTHER METHODS

	def cdf(self, x):
		"""Cumulative distribution function of demand distribution.

		In some cases, this is just a wrapper around ``cdf()`` function
		of ``scipy.stats.rv_continuous`` or ``scipy.stats.rv_discrete`` object.

		Parameters
		----------
		x : float
			Value to calculate cdf for.

		Returns
		-------
		F : float
			cdf of ``x``.

		"""

		if self.type in (None, 'D'):
			return None
		else:
			distribution = self.demand_distribution
			return distribution.cdf(x)


	def lead_time_demand_distribution(self, lead_time):
		"""Return lead-time demand distribution, as a
		``scipy.stats.rv_continuous`` or ``scipy.stats.rv_discrete`` object.

		.. note:: If ``lead_time`` equals 0, this method returns an ``rv_discrete`` object
			with a single value (0) and a single probability (1).

		.. note:: For 'UC', 'UD', 'NB', and 'CD' demands, this method calculates the lead-time
			demand distribution as the sum of ``lead_time`` independent random variables.
			Therefore, the method requires ``lead_time`` to be an integer for these
			distributions. If it is not, it raises a ``ValueError``.

		Parameters
		----------
		lead_time : float or int
			The lead time. [:math:`L`]

		Returns
		-------
		distribution : rv_continuous or rv_discrete
			The lead-time demand distribution object.

		Raises
		------
		ValueError
			If ``type`` is 'UC', 'UD', 'NB', or 'CD' and ``lead_time`` is not an integer.
		"""

		# Check whether lead_time is an integer.
		if self.type in ('UC', 'UD', 'NB', 'CD') and not is_integer(lead_time):
			raise ValueError("lead_time must be an integer for 'UC', 'UD', 'NB', or 'CD' demand")

		# Get distribution object.
		if lead_time == 0:
			# Return singleton.
			return scipy.stats.rv_discrete(name='custom', values=([0], [1]))
		elif self.type == 'N':
			return scipy.stats.norm(self.mean * lead_time, self.standard_deviation * math.sqrt(lead_time))
		elif self.type == 'P':
			return scipy.stats.poisson(self.mean * lead_time)
		elif self.type == 'UC':
			distribution = sum_of_continuous_uniforms_distribution(lead_time, self.lo, self.hi)
		elif self.type == 'UD':
			distribution = sum_of_discrete_uniforms_distribution(lead_time, self.lo, self.hi)
		elif self.type == 'NB':
			# Build probability list.
			min_demand = 0
			max_demand = int(self.demand_distribution.ppf(0.9999))
			prob = [self.demand_distribution.pmf(d) for d in range(min_demand, max_demand + 1)]
			prob = [prob[d] / sum(prob) for d in range(min_demand, max_demand + 1)]
			distribution = sum_of_discretes_distribution(lead_time, min_demand, max_demand, prob)
		elif self.type == 'CD':
			# Convert probability list to a list with 0 values for x values not in support.
			min_demand = min(self.demand_list)
			max_demand = max(self.demand_list)
			prob = []
			for x in range(min_demand, max_demand + 1):
				if x in self.demand_list:
					prob.append(self.probabilities[self.demand_list.index(x)])
				else:
					prob.append(0)
			distribution = sum_of_discretes_distribution(lead_time, min_demand, max_demand, prob)
		else:
			return None

		return distribution
