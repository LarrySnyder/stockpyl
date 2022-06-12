# ===============================================================================
# stockpyl - DemandSource Class
# -------------------------------------------------------------------------------
# Updated: 11-22-2020
# Author: Larry Snyder
# License: GPLv3
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
			* 'D' (deterministic)
			* 'CD' (custom discrete)
			
	round_to_int : bool
		Round demand to nearest integer?
	mean : float, optional
		Mean of demand per period. Required if ``type`` == 'N' or 'P'. [:math:`\mu`]
	standard_deviation : float, optional
		Standard deviation of demand per period. Required if ``type`` == 'N'. [:math:`\sigma`]
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

		return self._type == other._type and \
			self._mean == other._mean and \
			self._standard_deviation == other._standard_deviation and \
			self._demand_list == other._demand_list and \
			self._probabilities == other._probabilities and \
			self._lo == other._lo and \
			self._hi == other._hi and \
			self._round_to_int == other._round_to_int

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
		return self._mean

	@mean.setter
	def mean(self, value):
		self._mean = value

	@property
	def standard_deviation(self):
		return self._standard_deviation

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
	def round_to_int(self):
		return self._round_to_int

	@round_to_int.setter
	def round_to_int(self, value):
		self._round_to_int = value
		
	# READ-ONLY PROPERTIES
	@property
	def demand_distribution(self):
		"""Demand distribution, as a ``scipy.stats.rv_continuous`` or
		``scipy.stats.rv_discrete`` object. Read only.
		"""
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
		elif self.type == 'CD':
			distribution = scipy.stats.rv_discrete(name='custom',
												   values=(self.demand_list, self.probabilities))
		else:
			distribution = None

		return distribution

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

	def initialize(self, overwrite=True):
		"""Initialize the parameters in the object to their default values. If ``overwrite`` is ``True``,
		all attributes are reset to their default values, even if they already exist. (This is how the
		method should be called from the object's ``__init()__`` method.) If it is ``False``,
		then missing attributes are added to the object but existing attributes are not overwritten. (This
		is how the method should be called when loading an instance from a file, to make sure that all
		attributes are present.)

		Parameters
		----------
		overwrite : bool, optional
			``True`` to overwrite all attributes to their initial values, ``False`` to initialize
			only those attributes that are missing from the object. Default = ``True``.
		"""
		if overwrite or not hasattr(self, '_type'):
			self._type = None
		if overwrite or not hasattr(self, '_mean'):
			self._mean = None
		if overwrite or not hasattr(self, '_standard_deviation'):
			self._standard_deviation = None
		if overwrite or not hasattr(self, '_demand_list'):
			self._demand_list = None
		if overwrite or not hasattr(self, '_probabilities'):
			self._probabilities = None
		if overwrite or not hasattr(self, '_lo'):
			self._lo = None
		if overwrite or not hasattr(self, '_hi'):
			self._hi = None
		if overwrite or not hasattr(self, '_round_to_int'):
			self._round_to_int = False

	def validate_parameters(self):
		"""Check that appropriate parameters have been provided for the given
		demand type. Raise an exception if not.
		"""
		if self.type not in (None, 'N', 'UD', 'UC', 'D', 'CD'): raise AttributeError("Valid type in (None, 'N', 'UD', 'UC', 'D', 'CD') must be provided")

		if self.type == 'N':
			if self.mean is None: raise AttributeError("For 'N' (normal) demand, mean must be provided")
			if self.mean < 0: raise AttributeError("For 'N' (normal) demand, mean must be non-negative")
			if self.standard_deviation is None: raise AttributeError("For 'N' (normal) demand, standard_deviation must be provided")
			if self.standard_deviation < 0: raise AttributeError("For 'N' (normal) demand, standard_deviation must be non-negative")
		elif self.type == 'P':
			if self.mean is None: raise AttributeError("For 'P' (Poisson) demand, mean must be provided")
			if self.mean < 0: raise AttributeError("For 'P' (Poisson) demand, mean must be non-negative")
		elif self.type == 'UD':
			if self.lo is None: raise AttributeError("For 'UD' (uniform discrete) demand, lo must be provided")
			if self.lo < 0 or not is_integer(self.lo): raise AttributeError("For 'UD' (uniform discrete) demand, lo must be a non-negative integer")
			if self.hi is  None: raise AttributeError("For 'UD' (uniform discrete) demand, hi must be provided")
			if self.hi < 0 or not is_integer(self.hi): raise AttributeError("For 'UD' (uniform discrete) demand, hi must be a non-negative integer")
			if self.lo > self.hi: raise AttributeError("For 'UD' (uniform discrete) demand, lo must be <= hi")
		elif self.type == 'UC':
			if self.lo is None: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be provided")
			if self.lo < 0: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be non-negative")
			if self.hi is None: raise AttributeError("For 'UC' (uniform continuous) demand, hi must be provided")
			if self.hi < 0: raise AttributeError("For 'UC' (uniform continuous) demand, hi must be non-negative")
			if self.lo > self.hi: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be <= hi")
		elif self.type == 'D':
			if self.demand_list is None: raise AttributeError("For 'D' (deterministic) demand, demand_list must be provided")
		elif self.type == 'CD':
			if self.demand_list is None: raise AttributeError("For 'CD' (custom discrete) demand, demand_list must be provided")
			if self.probabilities is None: raise AttributeError("For 'CD' (custom discrete) demand, probabilities must be provided")
			if len(self.demand_list) != len(self.probabilities): raise AttributeError("For 'CD' (custom discrete) demand, demand_list and probabilities must have equal lengths")
			if np.sum(self.probabilities) != 1: raise AttributeError("For 'CD' (custom discrete) demand, probabilities must sum to 1")

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
		return max(0, np.random.normal(self.mean, self.standard_deviation))

	def _generate_demand_poisson(self):
		"""Generate demand from Poisson distribution.

		Returns
		-------
		demand : int
			The demand value.

		"""
		return np.random.poisson(self.mean)

	def _generate_demand_uniform_discrete(self):
		"""Generate demand from discrete uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.randint(int(self.lo), int(self.hi) + 1)

	def _generate_demand_uniform_continuous(self):
		"""Generate demand from continuous uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.uniform(self.lo, self.hi - self.lo)

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

	def validate_parameters(self):
		"""Check that appropriate parameters have been provided for the given
		demand type. Raise an exception if not.
		"""
		if self.type not in (None, 'N', 'UD', 'UC', 'D', 'CD'): raise AttributeError("Valid type in (None, 'N', 'UD', 'UC', 'D', 'CD') must be provided")

		if self.type == 'N':
			if self.mean is None: raise AttributeError("For 'N' (normal) demand, mean must be provided")
			if self.mean < 0: raise AttributeError("For 'N' (normal) demand, mean must be non-negative")
			if self.standard_deviation is None: raise AttributeError("For 'N' (normal) demand, standard_deviation must be provided")
			if self.standard_deviation < 0: raise AttributeError("For 'N' (normal) demand, standard_deviation must be non-negative")
		elif self.type == 'P':
			if self.mean is None: raise AttributeError("For 'P' (Poisson) demand, mean must be provided")
			if self.mean < 0: raise AttributeError("For 'P' (Poisson) demand, mean must be non-negative")
		elif self.type == 'UD':
			if self.lo is None: raise AttributeError("For 'UD' (uniform discrete) demand, lo must be provided")
			if self.lo < 0 or not is_integer(self.lo): raise AttributeError("For 'UD' (uniform discrete) demand, lo must be a non-negative integer")
			if self.hi is  None: raise AttributeError("For 'UD' (uniform discrete) demand, hi must be provided")
			if self.hi < 0 or not is_integer(self.hi): raise AttributeError("For 'UD' (uniform discrete) demand, hi must be a non-negative integer")
			if self.lo > self.hi: raise AttributeError("For 'UD' (uniform discrete) demand, lo must be <= hi")
		elif self.type == 'UC':
			if self.lo is None: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be provided")
			if self.lo < 0: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be non-negative")
			if self.hi is None: raise AttributeError("For 'UC' (uniform continuous) demand, hi must be provided")
			if self.hi < 0: raise AttributeError("For 'UC' (uniform continuous) demand, hi must be non-negative")
			if self.lo > self.hi: raise AttributeError("For 'UC' (uniform continuous) demand, lo must be <= hi")
		elif self.type == 'D':
			if self.demand_list is None: raise AttributeError("For 'D' (deterministic) demand, demand_list must be provided")
		elif self.type == 'CD':
			if self.demand_list is None: raise AttributeError("For 'CD' (custom discrete) demand, demand_list must be provided")
			if self.probabilities is None: raise AttributeError("For 'CD' (custom discrete) demand, probabilities must be provided")
			if len(self.demand_list) != len(self.probabilities): raise AttributeError("For 'CD' (custom discrete) demand, demand_list and probabilities must have equal lengths")
			if np.sum(self.probabilities) != 1: raise AttributeError("For 'CD' (custom discrete) demand, probabilities must sum to 1")

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

		.. note:: For 'P', 'UC', 'UD', and 'CD' demands, this method calculates the lead-time
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
			If ``type`` is 'P', 'UC', 'UD', or 'CD' and ``lead_time`` is not an integer.
		"""

		# Check whether lead_time is an integer.
		if self.type in ('P', 'UC', 'UD', 'CD') and not is_integer(lead_time):
			raise ValueError("lead_time must be an integer for 'P', 'UC', 'UD', or 'CD' demand")

		# Get distribution object.
		if self.type == 'N':
			return scipy.stats.norm(self.mean * lead_time, self.standard_deviation * np.sqrt(lead_time))
		elif self.type == 'P':
			return scipy.stats.poisson(self.mean * lead_time)
		elif self.type == 'UC':
			distribution = sum_of_continuous_uniforms_distribution(lead_time, self.lo, self.hi)
		elif self.type == 'UD':
			distribution = sum_of_discrete_uniforms_distribution(lead_time, self.lo, self.hi)
		elif self.type == 'CD':
			# Convert probability list to a list with 0 values for x values not in support.
			min_demand = min(self.demand_list)
			max_demand = max(self.demand_list)
			p = []
			for x in range(min_demand, max_demand + 1):
				if x in self.demand_list:
					p.append(self.probabilities[self.demand_list.index(x)])
				else:
					p.append(0)
			distribution = sum_of_discretes_distribution(lead_time, min_demand, max_demand, p)
		else:
			return None

		return distribution
