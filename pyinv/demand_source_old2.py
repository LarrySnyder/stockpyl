# ===============================================================================
# PyInv - DemandSource Class
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 04-12-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
This module contains the ``DemandSource`` class. A ``DemandSource``
object is used to generate demand_list.

Notation and equation and section numbers refer to Snyder and Shen,
"Fundamentals of Supply Chain Theory", Wiley, 2019, 2nd ed., except as noted.
"""


# ===============================================================================
# Imports
# ===============================================================================

from enum import Enum
import numpy as np
from scipy.stats import norm
from scipy.stats import uniform
from abc import ABC, abstractmethod			# abstract base class

from pyinv.helpers import *


# ===============================================================================
# Data Types
# ===============================================================================

class DemandType(Enum):
	NONE = 0					# no external demand
	NORMAL = 1
	UNIFORM_DISCRETE = 2
	UNIFORM_CONTINUOUS = 3
	DETERMINISTIC = 4			# must supply 'demand_list' parameter
	DISCRETE_EXPLICIT = 5		# must supply 'demand_list' and 'demand_probs' parameters


# ===============================================================================
# DemandSource Class and Subclasses
# ===============================================================================

class DemandSource(ABC):
	"""The ``DemandSource`` class is used to encapsulate demand generation.
	This is an abstract class, so it must be subclassed. Subclasses define the
	actual demand generation.
	"""

	@abstractmethod
	def generate_demand(self, period=None):
		pass


class DemandSourceNone(DemandSource):
	"""The ``DemandSourceNone`` class is used for nodes that have no external
	demand source.

	Attributes
	----------
	_type : DemandType
		The demand type.
	"""

	def __init__(self):
		self._type = DemandType.NONE

	# PROPERTIES

	@property
	def type(self):
		# Read-only property.
		return self._type

	# SPECIAL METHODS

	def __repr__(self):
		"""
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.
		"""
		return "DemandSource({:s})".format(self._type.name)

	# METHODS

	def generate_demand(self, period=None):
		"""Return None.

		Parameters
		----------
		period : int
			Ignored.

		Returns
		-------
		demand : float
			The demand value. Equals None.
		"""
		demand = None

		return demand


class DemandSourceNormal(DemandSource):
	"""The ``DemandSourceNormal`` class is used to encapsulate demand generation
	for demand_list with normal distribution.

	Attributes
	----------
	_type : DemandType
		The demand type.
	_mean : float
		Mean of demand per period. [mu]
	_standard_deviation : float
		Standard deviation of demand per period. [sigma]
	_round_to_int : bool
		Round demand to nearest integer?
	"""

	def __init__(self):
		self._type = DemandType.NORMAL
		self._mean = None
		self._standard_deviation = None
		self._round_to_int = False

	# PROPERTIES

	@property
	def type(self):
		# Read-only property.
		return self._type

	@property
	def mean(self):
		return self._mean

	@mean.setter
	def mean(self, mean):
		assert mean >= 0, "For NORMAL demand, mean must be non-negative"
		self._mean = mean

	@property
	def standard_deviation(self):
		return self._standard_deviation

	@standard_deviation.setter
	def standard_deviation(self, standard_deviation):
		assert standard_deviation >= 0, "For NORMAL demand, standard_deviation must be non-negative"
		self._standard_deviation = standard_deviation

	@property
	def round_to_int(self):
		return self._round_to_int

	@round_to_int.setter
	def round_to_int(self, round_to_int):
		self._round_to_int = round_to_int

	# SPECIAL METHODS

	def __repr__(self):
		"""
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.
		"""
		# Build string of parameters.
		param_str = \
			"mean={:.2f}, standard_deviation={:.2f}".format(self._mean, self._standard_deviation)

		return "DemandSource({:s}: {:s})".format(self._type.name, param_str)

	# METHODS

	def generate_demand(self, period=None):
		"""Generate demand from normal distribution.

		Parameters
		----------
		period : int, optional
			Ignored for this demand source type.

		Returns
		-------
		demand : float
			The demand value.
		"""
		# Check parameters.
		assert self._mean is not None, "For NORMAL demand, mean must be provided"
		assert self._standard_deviation is not None, "For NORMAL demand, mean must be provided"

		# Generate random demand.
		demand = max(0, np.random.normal(self._mean, self._standard_deviation))

		# Round demand, if requested.
		if self._round_to_int:
			demand = np.round(demand)

		return demand

	def demand_distribution(self):
		"""Return demand distribution, as a ``scipy.stats.rv_continuous`` object.

		Returns
		-------
		distribution : rv_continuous
			The demand distribution object.
		"""
		return norm(self._mean, self._standard_deviation)

	def lead_time_demand_distribution(self, lead_time):
		"""Return lead-time demand distribution, as a
		``scipy.stats.rv_continuous`` object.

		Parameters
		----------
		lead_time : float
			The lead time. [:math:`L`]

		Returns
		-------
		distribution : rv_continuous
			The lead-time demand distribution object.
		"""
		return norm(self._mean * lead_time,
					self._standard_deviation * np.sqrt(lead_time))

	def cdf(self, x):
		"""Cumulative distribution function of demand distribution.

		For normal distribution, this is simply a wrapper around
		``scipy.stats.norm.cdf()``.

		Parameters
		----------
		x : float
			Value to calculate cdf for.

		Returns
		-------
		F : float
			cdf of ``x``.

		"""

		distrib = norm(self._mean, self._standard_deviation)

		return distrib.cdf(x)


class DemandSourceUniformDiscrete(DemandSource):
	"""The ``DemandSourceUniformDiscrete`` class is used to encapsulate demand
	generation for demand_list with discrete uniform distribution.

	Attributes
	----------
	_type : DemandType
		The demand type.
	_lo : float
		Low value of demand range.
	_hi : float
		High value of demand range.
	"""

	def __init__(self):
		self._type = DemandType.UNIFORM_DISCRETE
		self._lo = None
		self._hi = None

	# PROPERTIES

	@property
	def type(self):
		# Read-only property.
		return self._type

	@property
	def lo(self):
		return self._lo

	@lo.setter
	def lo(self, lo):
		assert lo >= 0 and is_integer(lo), "For UNIFORM_DISCRETE demand, lo must be a non-negative integer"
		self._lo = lo

	@property
	def hi(self):
		return self._hi

	@hi.setter
	def hi(self, hi):
		assert hi >= 0 and is_integer(hi), "For UNIFORM_DISCRETE demand, hi must be a non-negative integer"
		self._hi = hi

	# SPECIAL METHODS

	def __repr__(self):
		"""
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.
		"""
		# Build string of parameters.
		param_str = \
			"lo={:.2f}, hi={:.2f}".format(self._lo, self._hi)

		return "DemandSource({:s}: {:s})".format(self._type.name, param_str)

	# METHODS

	def generate_demand(self, period=None):
		"""Generate demand from discrete uniform distribution.

		Parameters
		----------
		period : int, optional
			Ignored for this demand source type.

		Returns
		-------
		demand : float
			The demand value.
		"""
		# Check parameters.
		assert self._lo is not None, "For UNIFORM_DISCRETE demand, lo must be provided"
		assert self._hi is not None, "For UNIFORM_DISCRETE demand, hi must be provided"
		assert self._lo <= self._hi, "For UNIFORM_DISCRETE demand, lo must be <= hi"

		# Generate random demand.
		demand = np.random.randint(int(self._lo), int(self._hi) + 1)

		return demand


class DemandSourceUniformContinuous(DemandSource):
	"""The ``DemandSourceUniformContinuous`` class is used to encapsulate demand
	generation for demand_list with continuous uniform distribution.

	Attributes
	----------
	_type : DemandType
		The demand type.
	_lo : float
		Low value of demand range.
	_hi : float
		High value of demand range.
	_round_to_int : bool
		Round demand to nearest integer?
	"""

	def __init__(self):
		self._type = DemandType.UNIFORM_CONTINUOUS
		self._lo = None
		self._hi = None
		self._round_to_int = False

	# PROPERTIES

	@property
	def type(self):
		# Read-only property.
		return self._type

	@property
	def lo(self):
		return self._lo

	@lo.setter
	def lo(self, lo):
		assert lo >= 0, "For UNIFORM_DISCRETE demand, lo must be non-negative"
		self._lo = lo

	@property
	def hi(self):
		return self._hi

	@hi.setter
	def hi(self, hi):
		assert hi >= 0, "For UNIFORM_DISCRETE demand, hi must be non-negative"
		self._hi = hi

	@property
	def round_to_int(self):
		return self._round_to_int

	@round_to_int.setter
	def round_to_int(self, round):
		self._round_to_int = round

	# SPECIAL METHODS

	def __repr__(self):
		"""
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.
		"""
		# Build string of parameters.
		param_str = \
			"lo={:.2f}, hi={:.2f}".format(self._lo, self._hi)

		return "DemandSource({:s}: {:s})".format(self._type.name, param_str)

	# METHODS

	def generate_demand(self, period=None):
		"""Generate demand from continuous uniform distribution.

		Parameters
		----------
		period : int, optional
			Ignored for this demand source type.

		Returns
		-------
		demand : float
			The demand value.
		"""
		# Check parameters.
		assert self._lo is not None, "For UNIFORM_CONTINUOUS demand, lo must be provided"
		assert self._hi is not None, "For UNIFORM_DISCRETE demand, hi must be provided"
		assert self._lo <= self._hi, "For UNIFORM_DISCRETE demand, lo must be <= hi"

		# Generate random demand.
		demand = np.random.uniform(self._lo, self._hi)

		# Round demand, if requested.
		if self._round_to_int:
			demand = np.round(demand)

		return demand

	def demand_distribution(self):
		"""Return demand distribution, as a ``scipy.stats.rv_continuous`` object.

		Returns
		-------
		distribution : rv_continuous
			The demand distribution object.
		"""
		# Uniform loc = lo, scale = hi - lo.
		return uniform(self._lo, self._hi - self._lo)

	def lead_time_demand_distribution(self, lead_time):
		"""Return lead-time demand distribution, as a
		``scipy.stats.rv_continuous`` object.

		NOTE: This method calculates the lead-time demand distribution as the
		sum of ``lead_time`` uniform random variables. Therefore, the method
		requires ``lead_time`` to be an integer. If it is not, it raises an
		value error.

		Parameters
		----------
		lead_time : int
			The lead time. [:math:`L`]

		Returns
		-------
		distribution : rv_continuous
			The lead-time demand distribution object.

		Raises
		------
		ValueError
			If ``lead_time`` is not an integer.
		"""

		# Check whether lead_time is an integer.
		if not is_integer(lead_time):
			raise(ValueError, "lead_time must be an integer")

		# Get distribution object.
		distribution = sum_of_uniforms_distribution(lead_time, self._lo, self._hi)

		return distribution

	def cdf(self, x):
		"""Cumulative distribution function of demand distribution.

		For normal distribution, this is simply a wrapper around
		``scipy.stats.unif.cdf()``.

		Parameters
		----------
		x : float
			Value to calculate cdf for.

		Returns
		-------
		F : float
			cdf of ``x``.

		"""

		# Uniform loc = lo, scale = hi - lo.
		distrib = uniform(self._lo, self._hi - self._lo)

		return distrib.cdf(x)


class DemandSourceDeterministic(DemandSource):
	"""The ``DemandSourceDeterministic`` class is used to encapsulate demand
	generation for deterministic demand_list.

	Attributes
	----------
	_type : DemandType
		The demand type.
	_demands : list
		List of demand_list, one per period. [d]
	"""

	def __init__(self):
		self._type = DemandType.DETERMINISTIC
		self._demands = None

	# PROPERTIES

	@property
	def type(self):
		# Read-only property.
		return self._type

	@property
	def demands(self):
		return self._demands

	@demands.setter
	def demands(self, demands):
		self._demands = demands

	# SPECIAL METHODS

	def __repr__(self):
		"""
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.
		"""
		# Build string of parameters.
		param_str = "demand_list={}".format(self.demands)

		return "DemandSource({:s}: {:s})".format(self._type.name, param_str)

	# METHODS

	def generate_demand(self, period=None):
		"""Generate demand from deterministic demand source.

		Parameters
		----------
		period : int, optional
			The period to generate a demand value for. If omitted, will return
			the first (or only) demand in _demands list.

		Returns
		-------
		demand : float
			The demand value.
		"""
		# Check parameters.
		assert self._demands is not None, "For DETERMINISTIC demand, demand_list must be provided"

		if is_iterable(self._demands):
			if period is None:
				# Return first demand in demand_list list.
				demand = self._demands[0]
			else:
				# Get demand for period mod (# periods in demand_list list), i.e.,
				# if we are past the end of the demand_list list, loop back to the beginning.
				demand = self._demands[period % len(self._demands)]
		else:
			# Return demand_list singleton.
			demand = self._demands

		return demand


class DemandSourceDiscreteExplicit(DemandSource):
	"""The ``DemandSourceDiscreteExplicit`` class is used to encapsulate demand
	generation for discrete explicit demand_list.

	Attributes
	----------
	_type : DemandType
		The demand type.
	_demands : list
		List of possible demand values.
	_probabilities : list
		List of probabilities of each demand value.
	"""

	def __init__(self):
		self._type = DemandType.DISCRETE_EXPLICIT
		self._demands = None
		self._probabilities = None

	# PROPERTIES

	@property
	def type(self):
		# Read-only property.
		return self._type

	@property
	def demands(self):
		return self._demands

	@demands.setter
	def demands(self, demands):
		self._demands = demands

	@property
	def probabilities(self):
		return self._probabilities

	@probabilities.setter
	def probabilities(self, probabilities):
		assert np.sum(probabilities) == 1, "For DISCRETE_EXPLICIT demand, probabilities must sum to 1"
		self._probabilities = probabilities

	# SPECIAL METHODS

	def __repr__(self):
		"""
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.
		"""
		# Build string of parameters.
		param_str = "demand_list={}, probabilities={}".format(self._demands, self._probabilities)

		return "DemandSource({:s}: {:s})".format(self._type.name, param_str)

	# METHODS

	def generate_demand(self, period=None):
		"""Generate demand from deterministic demand source.

		Parameters
		----------
		period : int, optional
			Ignored for this demand source type.

		Returns
		-------
		demand : float
			The demand value.
		"""
		# Check parameters.
		assert self._demands is not None, "For DISCRETE_EXPLICIT demand, demand_list must be provided"
		assert self._probabilities is not None, "For DISCRETE_EXPLICIT demand, probabilities must be provided"
		assert len(self._demands) == len(self._probabilities), \
			"For DISCRETE_EXPLICIT demand, demand_list and probabilities must have equal lengths"

		demand = np.random.choice(self.demands, p=self.probabilities)

		return demand


# ===============================================================================
# DemandSourceFactory Class
# ===============================================================================

class DemandSourceFactory(object):
	"""The ``DemandSourceFactory`` class is used to build ``DemandSource``
	objects.

	Example
	-------
	To build a ``DemandSourceNormal`` object:

		demand_source_factory = DemandSourceFactory()
		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)

	It is also possible to create the subclass object directly, e.g.,

		demand_source = DemandSourceNormal()

	"""

	def build_demand_source(self, demand_type):
		"""Build and return a DemandSource object of the specified type.

		Parameters
		----------
		demand_type : DemandType
			The desired demand type.

		Returns
		-------
		demand_source : DemandSource
			The DemandSource object.

		"""
		if demand_type == DemandType.NONE:
			demand_source = DemandSourceNone()
		elif demand_type == DemandType.NORMAL:
			demand_source = DemandSourceNormal()
		elif demand_type == DemandType.UNIFORM_DISCRETE:
			demand_source = DemandSourceUniformDiscrete()
		elif demand_type == DemandType.UNIFORM_CONTINUOUS:
			demand_source = DemandSourceUniformContinuous()
		elif demand_type == DemandType.DETERMINISTIC:
			demand_source = DemandSourceDeterministic()
		elif demand_type == DemandType.DISCRETE_EXPLICIT:
			demand_source = DemandSourceDiscreteExplicit()
		else:
			raise(ValueError, "Unknown demand source type")

		return demand_source




