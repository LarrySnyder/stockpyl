# ===============================================================================
# stockpyl - DemandSource Class
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 11-22-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
This module contains the ``DemandSource`` class. A ``DemandSource``
object is used to generate demands and to get attributes of the demand distribution.

Notation and equation and section numbers refer to Snyder and Shen,
"Fundamentals of Supply Chain Theory", Wiley, 2019, 2nd ed., except as noted.
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

# TODO: handle Poisson and custom continuous

class DemandSource(object):
	"""
	Attributes
	----------
	_type : str
		The demand type, as a string. Currently supported strings are:
			* None
			* 'N' (normal)
			* 'UD' (uniform discrete)
			* 'UC' (uniform continuous)
			* 'D' (deterministic)
			* 'CD' (custom discrete)
	_round_to_int : bool
		Round demand to nearest integer?
	_mean : float, optional
		Mean of demand per period. Required if ``type`` = 'N'. [:math:`\mu`]
	_standard_deviation : float, optional
		Standard deviation of demand per period. Required if ``type`` =='N'. [:math:`\sigma`]
	_demand_list : list, optional
		List of demand_list, one per period (for deterministic demand types), or list
		of possible demand values (for custom discrete demand types). For deterministic
		demand types, if demand is required in a period beyond the length of the list,
		the list is restarted at the beginning. This also allows ``demand_list`` to be
		a singleton, in which case it is used in every period.
		Required if ``type`` = 'D' or 'CD'. [:math:`d`]
	_probabilities : list, optional
		List of probabilities of each demand value (for custom discrete demand types).
		Required if ``type`` = 'CD'.
	_lo : float, optional
		Low value of demand range (for uniform demand types). Required if
		``type`` = 'UD' or 'UC'.
	_hi : float, optional
		High value of demand range (for uniform demand types). Required if
		``type`` = 'UD' or 'UC'.
	"""

	def __init__(self):
		"""DemandSource constructor method.
		"""
		# Initialize parameters to None. (Relevant parameters will be filled
		# later.)
		self._type = None
		self._mean = None
		self._standard_deviation = None
		self._demand_list = None
		self._probabilities = None
		self._lo = None
		self._hi = None
		self._round_to_int = False

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
		``scipy.stats.rv_discrete`` object.
		"""
		if self.type is None:
			distribution = None
		elif self.type == 'N':
			distribution = scipy.stats.norm(self.mean, self.standard_deviation)
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
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.

		"""
		# Build string of parameters.
		if self.type is None:
			return "DemandSource(None)"
		elif self.type == 'N':
			param_str = "mean={:.2f}, standard_deviation={:.2f}".format(
				self.mean, self.standard_deviation)
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
		Return the full name of the ``DemandSource`` instance.

		Returns
		-------
			The demand_source name.

		"""
		return self.__repr__()

	# DEMAND GENERATION

	def generate_demand(self, period=None):
		"""Generate a demand value using the demand type specified in ``type``.
		If ``type`` is ``None``, returns ``None``.

		Parameters
		----------
		period : int, optional
			The period to generate a demand value for. If ``type`` = 'D' (deterministic),
			this is required if ``demand_list`` is a list of demand_list, one per period. If omitted,
			will return first (or only) demand in list.

		Returns
		-------
		demand : float
			The demand value.

		"""

		if self.type is None:
			return None
		if self.type == 'N':
			demand = self.generate_demand_normal()
		elif self.type == 'UD':
			demand = self.generate_demand_uniform_discrete()
		elif self.type == 'UC':
			demand = self.generate_demand_uniform_continuous()
		elif self.type == 'D':
			demand = self.generate_demand_deterministic(period)
		elif self.type == 'CD':
			demand = self.generate_demand_custom_discrete()
		else:
			demand = None

		if self.round_to_int:
			demand = np.round(demand)

		return demand

	def generate_demand_normal(self):
		"""Generate demand from normal distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return max(0, np.random.normal(self.mean, self.standard_deviation))

	def generate_demand_uniform_discrete(self):
		"""Generate demand from discrete uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.randint(int(self.lo), int(self.hi) + 1)

	def generate_demand_uniform_continuous(self):
		"""Generate demand from continuous uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.uniform(self.lo, self.hi - self.lo)

	def generate_demand_deterministic(self, period=None):
		"""Generate deterministic demand.

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

	def generate_demand_custom_discrete(self):
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
		if self.type not in (None, 'N', 'UD', 'UC', 'D', 'CD'): raise ValueError("Valid type in (None, 'N', 'UD', 'UC', 'D', 'CD') must be provided")

		if self.type == 'N':
			if self.mean is None: raise ValueError("For 'N' (normal) demand, mean must be provided")
			if self.mean < 0: raise ValueError("For 'N' (normal) demand, mean must be non-negative")
			if self.standard_deviation is None: raise ValueError("For 'N' (normal) demand, standard_deviation must be provided")
			if self.standard_deviation < 0: raise ValueError("For 'N' (normal) demand, standard_deviation must be non-negative")
		elif self.type == 'UD':
			if self.lo is None: raise ValueError("For 'UD' (uniform discrete) demand, lo must be provided")
			if self.lo < 0 or not is_integer(self.lo): raise ValueError("For 'UD' (uniform discrete) demand, lo must be a non-negative integer")
			if self.hi is  None: raise ValueError("For 'UD' (uniform discrete) demand, hi must be provided")
			if self.hi < 0 or not is_integer(self.hi): raise ValueError("For 'UD' (uniform discrete) demand, hi must be a non-negative integer")
			if self.lo > self.hi: raise ValueError("For 'UD' (uniform discrete) demand, lo must be <= hi")
		elif self.type == 'UC':
			if self.lo is None: raise ValueError("For 'UC' (uniform continuous) demand, lo must be provided")
			if self.lo < 0: raise ValueError("For 'UC' (uniform continuous) demand, lo must be non-negative")
			if self.hi is None: raise ValueError("For 'UC' (uniform continuous) demand, hi must be provided")
			if self.hi < 0: raise ValueError("For 'UC' (uniform continuous) demand, hi must be non-negative")
			if self.lo > self.hi: raise ValueError("For 'UC' (uniform continuous) demand, lo must be <= hi")
		elif self.type == 'D':
			if self.demand_list is None: raise ValueError("For 'D' (deterministic) demand, demand_list must be provided")
		elif self.type == 'CD':
			if self.demand_list is None: raise ValueError("For 'CD' (custom discrete) demand, demand_list must be provided")
			if self.probabilities is None: raise ValueError("For 'CD' (custom discrete) demand, probabilities must be provided")
			if len(self.demand_list) != len(self.probabilities): raise ValueError("For 'CD' (custom discrete) demand, demand_list and probabilities must have equal lengths")
			if np.sum(self.probabilities) != 1: raise ValueError("For 'CD' (custom discrete) demand, probabilities must sum to 1")

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

		NOTE: For 'UC' and 'UD' demands, this method calculates the lead-time
		demand distribution as the sum of ``lead_time`` uniform random variables.
		Therefore, the method requires ``lead_time`` to be an integer for these
		distributions. If it is not, it raises a ``ValueError``.

		Parameters
		----------
		lead_time : float
			The lead time. [:math:`L`]

		Returns
		-------
		distribution : rv_continuous or rv_discrete
			The lead-time demand distribution object.

		Raises
		------
		ValueError
			If ``type`` is 'UC', 'UD', or 'CD' and ``lead_time`` is not an integer.
		"""

		# TODO: unit tests

		# Check whether lead_time is an integer.
		if self.type in ('UC', 'UD') and not is_integer(lead_time):
			raise ValueError("lead_time must be an integer for 'UC' and 'UD' demand")

		# Get distribution object.
		if self.type == 'N':
			return scipy.stats.norm(self.mean * lead_time, self.standard_deviation * np.sqrt(lead_time))
		elif self.type in ('UC', 'UD'):
			distribution = sum_of_uniforms_distribution(lead_time, self.lo, self.hi)
		elif self.type == 'CD':
			# TODO: handle what happens if demand list is not in the form lo, ..., hi
			distribution = sum_of_discretes_distribution(lead_time, min(self.demand_list), max(self.demand_list), self.probabilities)
		else:
			# TODO: handle 'CD' demands
			# use this: https://stackoverflow.com/a/29236193/3453768
			return None

		return distribution
