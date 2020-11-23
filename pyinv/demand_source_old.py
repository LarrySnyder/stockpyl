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
object is used to generate demands.

Notation and equation and section numbers refer to Snyder and Shen,
"Fundamentals of Supply Chain Theory", Wiley, 2019, 2nd ed., except as noted.
"""


# ===============================================================================
# Imports
# ===============================================================================

from enum import Enum
import numpy as np
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
	DETERMINISTIC = 4			# must supply 'demands' parameter
	DISCRETE_EXPLICIT = 5		# must supply 'demands' and 'demand_probs' parameters


# ===============================================================================
# DemandSource Class
# ===============================================================================

class DemandSource(ABC):
	"""The ``DemandSource`` class is used to encapsulate demand generation.
	This is an abstract class, so it must be subclassed. Subclasses define the
	actual demand generation.

	"""

	@abstractmethod
	def generate_demand(self):
		pass
	



class DemandSourceOld(object):
	"""
	Attributes
	----------
	demand_type : DemandType
		The demand type.
	round : bool
		Round demand to nearest integer?
	demand_mean : float
		Mean of demand per period. Required if ``type`` == ``NORMAL``,
		ignored otherwise. [mu]
	demand_standard_deviation : float
		Standard deviation of demand per period. Required if ``type`` ==
		``NORMAL``, ignored otherwise. [sigma]
	demands : list
		List of demands, one per period (if ``type`` == ``DETERMINISTIC``),
		or list of possible demand values (if ``type`` ==
		``DISCRETE_EXPLICIT``). Required if ``type`` == ``DETERMINISTIC``
		or ``DISCRETE_EXPLICIT``, ignored otherwise. [d]
	demand_probabilities : list
		List of probabilities of each demand value. Required if ``type``
		== ``DISCRETE_EXPLICIT``, ignored otherwise.
	demand_lo : float
		Low value of demand range. Required if ``type`` ==
		``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
	demand_hi : float
		High value of demand range. Required if ``type`` ==
		``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
	"""

	def __init__(
			self,
			demand_type=None,
			round=False,
			demand_mean=None,
			demand_standard_deviation=None,
			demands=None,
			demand_probabilities=None,
			demand_lo=None,
			demand_hi=None
	):
		"""DemandSource constructor method.

		Parameters
		----------
		demand_type : DemandType
			The demand type.
		demand_mean : float
			Mean of demand per period. Required if ``type`` == ``NORMAL``,
			ignored otherwise. [mu]
		demand_standard_deviation : float
			Standard deviation of demand per period. Required if ``type`` ==
			``NORMAL``, ignored otherwise. [sigma]
		demands : list
			List of demands, one per period (if ``type`` == ``DETERMINISTIC``),
			or list of possible demand values (if ``type`` ==
			``DISCRETE_EXPLICIT``). Required if ``type`` == ``DETERMINISTIC``
			or ``DISCRETE_EXPLICIT``, ignored otherwise. [d]
		demand_probabilities : list
			List of probabilities of each demand value. Required if ``type``
			== ``DISCRETE_EXPLICIT``, ignored otherwise.
		demand_lo : float
			Low value of demand range. Required if ``type`` ==
			``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
		demand_hi : float
			High value of demand range. Required if ``type`` ==
			``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
		"""
		# Set type.
		self.demand_type = demand_type

		# Set round_to_int.
		self.round = round

		# Initialize parameters to None. (Relevant parameters will be filled
		# below.)
		self.demand_mean = None
		self.demand_standard_deviation = None
		self.demands = None
		self.demand_probabilities = None
		self.demand_lo = None
		self.demand_hi = None

		# Set (and validate) demand parameters.
		# TODO: change this so that all of this can be set after __init__
		if demand_type == DemandType.NORMAL:
			assert demand_mean is not None, "For NORMAL demand, mean must be provided"
			assert demand_mean >= 0, "For NORMAL demand, mean must be non-negative"
			assert demand_standard_deviation is not None, "For NORMAL demand, standard_deviation must be provided"
			assert demand_standard_deviation >= 0, "For NORMAL demand, standard_deviation must be non-negative"
			self.demand_mean = demand_mean
			self.demand_standard_deviation = demand_standard_deviation
		elif demand_type == DemandType.UNIFORM_DISCRETE:
			assert demand_lo is not None, "For UNIFORM_DISCRETE demand, lo must be provided"
			assert demand_lo >= 0 and is_integer(demand_lo), \
				"For UNIFORM_DISCRETE demand, lo must be a non-negative integer"
			assert demand_hi is not None, "For UNIFORM_DISCRETE demand, hi must be provided"
			assert demand_hi >= 0 and is_integer(demand_hi), \
				"For UNIFORM_DISCRETE demand, hi must be a non-negative integer"
			assert demand_lo <= demand_hi, "For UNIFORM_DISCRETE demand, lo must be <= hi"
			self.demand_lo = demand_lo
			self.demand_hi = demand_hi
		elif demand_type == DemandType.UNIFORM_CONTINUOUS:
			assert demand_lo is not None, "For UNIFORM_CONTINUOUS demand, lo must be provided"
			assert demand_lo >= 0, "For UNIFORM_CONTINUOUS demand, lo must be non-negative"
			assert demand_hi is not None, "For UNIFORM_CONTINUOUS demand, hi must be provided"
			assert demand_hi >= 0, "For UNIFORM_CONTINUOUS demand, hi must be non-negative"
			assert demand_lo <= demand_hi, "For UNIFORM_CONTINUOUS demand, lo must be <= hi"
			self.demand_lo = demand_lo
			self.demand_hi = demand_hi
		elif demand_type == DemandType.DETERMINISTIC:
			assert demands is not None, "For DETERMINISTIC demand, demands must be provided"
			self.demands = demands
		elif demand_type == DemandType.DISCRETE_EXPLICIT:
			assert demands is not None, "For DISCRETE_EXPLICIT demand, demands must be provided"
			assert demand_probabilities is not None, "For DISCRETE_EXPLICIT demand, probabilities must be provided"
			assert len(demands) == len(demand_probabilities), \
				"For DISCRETE_EXPLICIT demand, demands and probabilities must have equal lengths"
			assert np.sum(demand_probabilities) == 1, "For DISCRETE_EXPLICIT demand, probabilities must sum to 1"
			self.demands = demands
			self.demand_probabilities = demand_probabilities

	# Special members.

	def __repr__(self):
		"""
		Return a string representation of the ``DemandSource`` instance.

		Returns
		-------
			A string representation of the ``DemandSource`` instance.

		"""
		# Build string of parameters.
		if self.demand_type == DemandType.NONE:
			param_str = ""
		elif self.demand_type == DemandType.NORMAL:
			param_str = \
				"mean={:.2f}, standard_deviation={:.2f}".format(self.demand_mean, self.demand_standard_deviation)
		elif self.demand_type in (DemandType.UNIFORM_DISCRETE, DemandType.UNIFORM_CONTINUOUS):
			param_str = \
				"lo={:.2f}, hi={:.2f}".format(self.demand_lo, self.demand_hi)
		elif self.demand_type == DemandType.DETERMINISTIC:
			param_str = "demands={}".format(self.demands)
		elif self.demand_type == DemandType.DISCRETE_EXPLICIT:
			param_str = "demands={}, probabilities={}".format(self.demands, self.demand_probabilities)

		return "DemandSource({:s}: {:s})".format(self.demand_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``DemandSource`` instance.

		Returns
		-------
			The demand source name.

		"""
		return self.__repr__()

	def generate_demand(self, period=None):
		"""Generate a demand value using the demand type specified in
		type.

		Parameters
		----------
		period : int, optional
			The period to generate a demand value for. If ``type`` ==
			``DETERMINISTIC``, this is required if ``demands`` is a list of
			demands, on per period. If omitted, will return first (or only)
			demand in list. Ignored if ``type`` != ``DETERMINISTIC``.

		Returns
		-------
		demand : float
			The demand value.

		"""

		if self.demand_type == DemandType.NORMAL:
			demand = self.generate_demand_normal()
		elif self.demand_type == DemandType.UNIFORM_DISCRETE:
			demand = self.generate_demand_uniform_discrete()
		elif self.demand_type == DemandType.UNIFORM_CONTINUOUS:
			demand = self.generate_demand_uniform_continuous()
		elif self.demand_type == DemandType.DETERMINISTIC:
			demand = self.generate_demand_deterministic(period)
		elif self.demand_type == DemandType.DISCRETE_EXPLICIT:
			demand = self.generate_demand_discrete_explicit()

		if self.round:
			demand = np.round(demand)

		return demand

	def generate_demand_normal(self):
		"""Generate demand from normal distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.normal(self.demand_mean, self.demand_standard_deviation)

	def generate_demand_uniform_discrete(self):
		"""Generate demand from discrete uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.randint(int(self.demand_lo), int(self.demand_hi) + 1)

	def generate_demand_uniform_continuous(self):
		"""Generate demand from continuous uniform distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.uniform(self.demand_lo, self.demand_hi)

	def generate_demand_deterministic(self, period=None):
		"""Generate deterministic demand.

		Returns
		-------
		demand : float
			The demand value.

		"""
		if is_iterable(self.demands):
			if period is None:
				# Return first demand in demands list.
				return self.demands[0]
			else:
				# Get demand for period mod (# periods in demands list), i.e.,
				# if we are past the end of the demands list, loop back to the beginning.
				return self.demands[period % len(self.demands)]
		else:
			# Return demands singleton.
			return self.demands

	def generate_demand_discrete_explicit(self):
		"""Generate demand from discrete explicit distribution.

		Returns
		-------
		demand : float
			The demand value.

		"""
		return np.random.choice(self.demands, p=self.demand_probabilities)

