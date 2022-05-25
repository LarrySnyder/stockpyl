# ===============================================================================
# stockpyl - DisruptionProcess Class
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 5-24-22
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
This module contains the ``DisruptionProcess`` class. A ``DisruptionProcess``
object is used to keep track of a given node's disruption state.

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
# DisruptionProcess Class
# ===============================================================================

class DisruptionProcess(object):
	"""
	Attributes
	----------
	_type : str
		The disruption process type, as a string. Currently supported strings are:
			* None
			* 'M' (2-state Markovian)
			* 'E' (explicit: disruption state for each period is provided explicitly)
	_disruption_probability : float
		The probability that the node is disrupted in period :math:`t+1` given that 
		it is not disrupted in period `t`. [:math:`\\alpha`]
	_recovery_probability : float
		The probability that the node is not disrupted in period :math:`t+1` given that 
		it is disrupted in period `t`. [:math:`\\beta`]
	_disruption_state_list : list, optional
		List of disruption states (``True``/``False``, one per period), if ``_type`` = ``'E'``. If 
		disruption state is required in a period beyond the length of the list,
		the list is restarted at the beginning. 
		Required if ``type`` = 'E'.
	_disrupted : bool
		``True`` if the node is currently disrupted, ``False`` otherwise.
	"""

	def __init__(self, **kwargs):
		"""DisruptionProcess constructor method.

		Parameters
		----------
		kwargs : optional
			Optional keyword arguments to specify ``DisruptionProcess`` attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match a ``DisruptionProcess`` attribute.
		"""
		# Initialize parameters to None. (Relevant parameters will be filled later.)
		self._type = None
		self._disruption_probability = None
		self._recovery_probability = None
		self._disruption_state_list = None

		# Initialize state variable to False.
		self._disrupted = False

		# Set attributes specified by kwargs.
		for key, value in kwargs.items():
			if key in vars(self):
				vars(self)[key] = value
			elif f"_{key}" in vars(self):
				vars(self)[f"_{key}"] = value
			else:
				raise AttributeError(f"{key} is not an attribute of DisruptionProcess")

			vars(self)[key] = value

	# SPECIAL METHODS

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to this ``DisruptionProcess`` object. 
		Two ``DisruptionProcess`` objects are considered equal if all of their attributes 
		(*except* ``_disrupted``, the state variable) are equal.

		Parameters
		----------
		other : DisruptionProcess
			The ``DisruptionProcess`` object to compare to.

		Returns
		-------
		bool
			``True`` if the ``DisruptionProcess`` objects are equal, ``False`` otherwise.
		"""

		return self._type == other._type and \
			self._disruption_probability == other._disruption_probability and \
			self._recovery_probability == other._recovery_probability and \
			self._disruption_state_list == other._disruption_state_list

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to this ``DisruptionProcess`` object. 
		Two ``DisruptionProcess`` objects are considered equal if all of their attributes 
		(*except* ``_disrupted``, the state variable) are equal.

		Parameters
		----------
		other : DisruptionProcess
			The ``DisruptionProcess`` object to compare to.

		Returns
		-------
		bool
			True if the ``DisruptionProcess`` objects are not equal, False otherwise.
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
	def disruption_probability(self):
		return self._disruption_probability

	@disruption_probability.setter
	def disruption_probability(self, value):
		self._disruption_probability = value

	@property
	def recovery_probability(self):
		return self._recovery_probability

	@recovery_probability.setter
	def recovery_probability(self, value):
		self._recovery_probability = value

	@property
	def disruption_state_list(self):
		return self._disruption_state_list

	@disruption_state_list.setter
	def disruption_state_list(self, value):
		self._disruption_state_list = value

	@property
	def disrupted(self):
		return self._disrupted

	@disrupted.setter
	def disrupted(self, value):
		self._disrupted = value
		
	# READ-ONLY PROPERTIES

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the ``DisruptionProcess`` instance.

		Returns
		-------
			A string representation of the ``DisruptionProcess`` instance.

		"""
		# Build string of parameters.
		if self.type is None:
			return "DisruptionProcess(None)"
		elif self.type == 'M':
			param_str = "disruption_probability={:.6f}, recovery_probability={:.6f}".format(
				self.disruption_probability, self.recovery_probability)
		elif self.type == 'E':
			if not is_list(self.disruption_state_list) or len(self.disruption_state_list) <= 8:
				param_str = "disruption_state_list={}".format(self.disruption_state_list)
			else:
				param_str = "disruption_state_list={}...".format(self.disruption_state_list[0:8])
		else:
			param_str = ""

		return "DisruptionProcess({:s}: {:s})".format(self.type, param_str)

	def __str__(self):
		"""
		Return the full name of the ``DisruptionProcess`` instance.

		Returns
		-------
			The ``DisruptionProcess`` name.

		"""
		return self.__repr__()

	# DISRUPTION STATE MANAGEMENT

	def update_disruption_state(self, period=None):
		"""Update the disruption state using the disruption type specified in ``type`` and
		set the ``disrupted`` attribute accordingly. 

		If ``type`` is ``None``, sets ``disrupted`` to ``False``.

		Parameters
		----------
		period : int, optional
			The period to update the disruption state for. If ``type`` = 'E' (explicit), this is required
			if ``disruption_state_list`` is a list of disruption states, one per period. If omitted,
			will return first (or only) disruption state in list.
		"""

		if self.type is None:
			disrupted = False
		if self.type == 'M':
			disrupted = self.generate_disruption_state_markovian()
		elif self.type == 'E':
			disrupted = self.generate_disruption_state_explicit(period)
		else:
			disrupted = False

		self.disrupted = disrupted

	def generate_disruption_state_markovian(self):
		"""Generate new disruption state for a Markovian disruption process.

		Returns
		-------
		disrupted : bool
			``True`` if the new disruption state is disrupted, ``False`` otherwise.

		"""
		if self.disrupted:
			return np.random.rand() <= 1 - self.recovery_probability
		else:
			return np.random.rand() <= self.disruption_probability

	def generate_disruption_state_explicit(self, period=None):
		"""Generate explicit disruption state.

		Returns
		-------
		disrupted : bool
			``True`` if the new disruption state is disrupted, ``False`` otherwise.

		"""
		if is_iterable(self.disruption_state_list):
			if period is None:
				# Return first demand in disruption_state_list.
				return self.disruption_state_list[0]
			else:
				# Get disruption state for period mod (# periods in disruption_state_list), i.e.,
				# if we are past the end of the disruption_state_list, loop back to the beginning.
				return self.disruption_state_list[period % len(self.disruption_state_list)]
		else:
			# Return disruption_state_list singleton.
			return self.disruption_state_list

	# OTHER METHODS

	def validate_parameters(self):
		"""Check that appropriate parameters have been provided for the given
		disruption type. Raise an exception if not.
		"""
		if self.type not in (None, 'M', 'E'): raise AttributeError("Valid type in (None, 'M', 'E') must be provided")

		if self.type == 'M':
			if self.disruption_probability is None: raise AttributeError("For 'M' (Markovian) disruptions, disruption_probability must be provided")
			if self.disruption_probability < 0 or self.disruption_probability > 1: raise AttributeError("For 'M' (Markovian) disruptions, disruption_probability must be in [0,1]")
			if self.recovery_probability is None: raise AttributeError("For 'M' (Markovian) disruptions, recovery_probability must be provided")
			if self.recovery_probability < 0 or self.recovery_probability > 1: raise AttributeError("For 'M' (Markovian) disruptions, recovery_probability must be in [0,1]")
		elif self.type == 'E':
			if self.disruption_state_list is None: raise AttributeError("For 'E' (explicit) disruptions, disruption_probability_list must be provided")

	def steady_state_probabilities(self):
		"""Return the steady-state probabilities of the node being up (not disrupted) or down (disrupted).

		Returns
		-------
		pi_up : float
			The steady-state probability of non-disruption.
		pi_down : float
			The steady-state probability of disruption.
		"""

		if self.type == 'M':
			pi_up = self.recovery_probability / (self.disruption_probability + self.recovery_probability)
			pi_down = self.disruption_probability / (self.disruption_probability + self.recovery_probability)
		elif self.type == 'E':
			pi_down = sum(self.disruption_state_list) / len(self.disruption_state_list)
			pi_up = 1 - pi_down
		else:
			pi_up = None
			pi_down = None

		return pi_up, pi_down
