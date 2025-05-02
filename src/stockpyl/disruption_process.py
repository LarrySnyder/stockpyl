# ===============================================================================
# stockpyl - DisruptionProcess Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

This module contains the |class_disruption_process| class. A |class_disruption_process|
object represents a disruption process that a node is subject to. Attributes specify the type of 
random process governing the disruption, as well as the type of disruption itself (i.e., its effects).
The object keeps track of the current disruption state and generates new states according
to the random process.

.. note:: |fosct_notation|

**Example:** Create a |class_disruption_process| object representing disruptions that follow a 2-state
Markov process with a disruption probability of 0.1 and a recovery probability of 0.3. 
Disruptions are "order-pausing" (a disrupted node cannot place orders). Generate a new
disruption state assuming the current state is ``True`` (disrupted).

	.. testsetup:: *

		from stockpyl.disruption_process import *

	.. doctest::

		>>> dp = DisruptionProcess(
		...     random_process_type='M',        # 2-state Markovian
		...     disruption_type='OP',           # order-pausing disruptions
		...     disruption_probability=0.1,
		...     recovery_probability=0.3
		... )
		>>> dp.disrupted = True
		>>> dp.update_disruption_state()
		>>> dp.disrupted	# doctest: +SKIP
		True
		>>> dp.update_disruption_state()
		>>> dp.disrupted	# doctest: +SKIP
		False
		>>> # Calculate steady-state probabilities of being up and down.
		>>> pi_up, pi_down = dp.steady_state_probabilities()
		>>> pi_up, pi_down
		(0.7499999999999999, 0.25)

API Reference
-------------

"""


# ===============================================================================
# Imports
# ===============================================================================

import numpy as np
import copy

from stockpyl.helpers import *


# ===============================================================================
# DisruptionProcess Class
# ===============================================================================

class DisruptionProcess(object):
	"""
	A |class_disruption_process| object represents a disruption process that a node is subject to. Attributes specify the type of 
	random process governing the disruption, as well as the type of disruption itself (i.e., its effects).
	The object keeps track of the current disruption state and generates new states according
	to the random process.

	Parameters
	----------
	**kwargs 
		Keyword arguments specifying values of one or more attributes of the |class_disruption_process|, 
		e.g., ``random_process_type='M'``.

	Attributes
	----------
	random_process_type : str
		The type of random process governing the disruptions, as a string. Currently supported strings are:
			
			* None
			* 'M' (2-state Markovian)
			* 'E' (explicit: disruption state for each period is provided explicitly)

	disruption_type : str
		The type of disruption, as a string. Currently supported strings are:

			* 'OP' (order-pausing: the stage cannot place orders during disruptions) (default)
			* 'SP' (shipment-pausing: the stage can place orders during disruptions but its supplier(s) cannot ship them)
			* 'TP' (transit-pausing: items in transit to the stage are paused during disruptions)
			* 'RP' (receipt-pausing: items cannot be received by the disrupted stage; they accumulate 
			  just before the stage and are received when the disruption ends)

	disruption_probability : float
		The probability that the node is disrupted in period :math:`t+1` given that 
		it is not disrupted in period `t`. Required if ``random_process_type`` = 'M'. [:math:`\\alpha`]
	recovery_probability : float
		The probability that the node is not disrupted in period :math:`t+1` given that 
		it is disrupted in period `t`. Required if ``random_process_type`` = 'M'. [:math:`\\beta`]
	disruption_state_list : list, optional
		List of disruption states (``True``/``False``, one per period), if ``random_process_type`` = ``'E'``. If 
		disruption state is required in a period beyond the length of the list,
		the list is restarted at the beginning. 
		Required if ``random_process_type`` = 'E'.
	disrupted : bool
		``True`` if the node is currently disrupted, ``False`` otherwise.
	"""

	def __init__(self, **kwargs):
		"""DisruptionProcess constructor method.

		Parameters
		----------
		kwargs : optional
			Optional keyword arguments to specify |class_disruption_process| attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match a |class_disruption_process| attribute.
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
				raise AttributeError(f"{key} is not an attribute of DisruptionProcess")

	_DEFAULT_VALUES = {
		'_random_process_type': None,
		'_disruption_type': 'OP',
		'_disruption_probability': None,
		'_recovery_probability': None,
		'_disruption_state_list': None,
		'_disrupted': False
	}

	# SPECIAL METHODS

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to this |class_disruption_process| object. 
		Two |class_disruption_process| objects are considered equal if all of their attributes 
		(*except* ``_disrupted``, the state variable) are equal.

		Parameters
		----------
		other : |class_disruption_process|
			The |class_disruption_process| object to compare to.

		Returns
		-------
		bool
			``True`` if the |class_disruption_process| objects are equal, ``False`` otherwise.
		"""
		if other is None:
			return False
		else:
			for attr in self._DEFAULT_VALUES.keys():
				if getattr(self, attr) != getattr(other, attr):
					return False
			return True

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to this |class_disruption_process| object. 
		Two |class_disruption_process| objects are considered equal if all of their attributes 
		(*except* ``_disrupted``, the state variable) are equal.

		Parameters
		----------
		other : |class_disruption_process|
			The |class_disruption_process| object to compare to.

		Returns
		-------
		bool
			True if the |class_disruption_process| objects are not equal, False otherwise.
		"""
		return not self.__eq__(other)

	# PROPERTY GETTERS AND SETTERS

	@property
	def random_process_type(self):
		return self._random_process_type

	@random_process_type.setter
	def random_process_type(self, value):
		self._random_process_type = value

	@property
	def disruption_type(self):
		return self._disruption_type

	@disruption_type.setter
	def disruption_type(self, value):
		self._disruption_type = value

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
		Return a string representation of the |class_disruption_process| instance.

		Returns
		-------
			A string representation of the |class_disruption_process| instance.

		"""
		# Build string of parameters.
		if self.random_process_type is None:
			return "DisruptionProcess(None)"
		elif self.random_process_type == 'M':
			param_str = "disruption_probability={:.6f}, recovery_probability={:.6f}".format(
				self.disruption_probability, self.recovery_probability)
		elif self.random_process_type == 'E':
			if not is_list(self.disruption_state_list) or len(self.disruption_state_list) <= 8:
				param_str = "disruption_state_list={}".format(self.disruption_state_list)
			else:
				param_str = "disruption_state_list={}...".format(self.disruption_state_list[0:8])
		else:
			param_str = ""

		return "DisruptionProcess({:s}, {:s}: {:s})".format(self.disruption_type, self.random_process_type, param_str)

	def __str__(self):
		"""
		Return the full name of the |class_disruption_process| instance.

		Returns
		-------
			The |class_disruption_process| name.

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
		random process type. Raise an exception if not.
		"""
		if self.random_process_type not in (None, 'M', 'E'): raise AttributeError("Valid random_process_type in (None, 'M', 'E') must be provided")
		if self.disruption_type not in (None, 'SP', 'OP', 'TP', 'RP'): raise AttributeError("Valid disruption_type in (None, 'SP', 'OP', 'TP', 'RP') must be provided")

		if self.random_process_type == 'M':
			if self.disruption_probability is None: raise AttributeError("For 'M' (Markovian) disruptions, disruption_probability must be provided")
			if self.disruption_probability < 0 or self.disruption_probability > 1: raise AttributeError("For 'M' (Markovian) disruptions, disruption_probability must be in [0,1]")
			if self.recovery_probability is None: raise AttributeError("For 'M' (Markovian) disruptions, recovery_probability must be provided")
			if self.recovery_probability < 0 or self.recovery_probability > 1: raise AttributeError("For 'M' (Markovian) disruptions, recovery_probability must be in [0,1]")
		elif self.random_process_type == 'E':
			if self.disruption_state_list is None: raise AttributeError("For 'E' (explicit) disruptions, disruption_probability_list must be provided")

	# CONVERTING TO/FROM DICTS

	def to_dict(self):
		"""Convert the |class_disruption_process| object to a dict. List attributes
		(``disruption_state_list``) are deep-copied so changes to the original
		object do not get propagated to the dict.

		Returns
		-------
		dict
			The dict representation of the object.
		"""
		# Initialize dict.
		dp_dict = {}

		# Attributes.
		for attr in self._DEFAULT_VALUES.keys():
			# Remove leading '_' to get property names.
			prop = attr[1:] if attr[0] == '_' else attr
			if is_list(getattr(self, prop)):
				dp_dict[prop] = copy.deepcopy(getattr(self, prop))
			else:
				dp_dict[prop] = getattr(self, prop)

		return dp_dict

	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_disruption_process| object with attributes copied from the
		values in ``the_dict``. List attributes (``disruption_state_list``) 
		are deep-copied so changes to the original dict do not get propagated to the object.
		Any missing attributes are set to their default values.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_disruption_process|, typically created using ``to_dict()``.

		Returns
		-------
		DisruptionProcess
			The object converted from the dict.
		"""
		if the_dict is None:
			dp = cls()
		else:
			# Build empty DisruptionProcess.
			dp = cls()
			# Fill attributes.
			for attr in cls._DEFAULT_VALUES.keys():
				# Remove leading '_' to get property names.
				prop = attr[1:] if attr[0] == '_' else attr
				if prop in the_dict:
					if is_list(the_dict[prop]):
						value = copy.deepcopy(the_dict[prop])
					else:
						value = the_dict[prop]
				else:
					value = cls._DEFAULT_VALUES[attr]
				setattr(dp, prop, value)

		return dp

	# DISRUPTION STATE MANAGEMENT

	def update_disruption_state(self, period=None):
		"""Update the disruption state using the type specified in ``random_process_type`` and
		set the ``disrupted`` attribute accordingly. 

		If ``random_process_type`` is ``None``, sets ``disrupted`` to ``False``.

		Parameters
		----------
		period : int, optional
			The period to update the disruption state for. If ``random_process_type`` = 'E' (explicit), this is required
			if ``disruption_state_list`` is a list of disruption states, one per period. If omitted,
			will return first (or only) disruption state in list.
		"""

		if self.random_process_type is None:
			disrupted = False
		if self.random_process_type == 'M':
			disrupted = self._generate_disruption_state_markovian()
		elif self.random_process_type == 'E':
			disrupted = self._generate_disruption_state_explicit(period)
		else:
			disrupted = False

		self.disrupted = disrupted

	def _generate_disruption_state_markovian(self):
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

	def _generate_disruption_state_explicit(self, period=None):
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

	def steady_state_probabilities(self):
		"""Return the steady-state probabilities of the node being up (not disrupted) or down (disrupted).

		Returns
		-------
		pi_up : float
			The steady-state probability of non-disruption.
		pi_down : float
			The steady-state probability of disruption.
		"""

		if self.random_process_type == 'M':
			pi_up = self.recovery_probability / (self.disruption_probability + self.recovery_probability)
			pi_down = self.disruption_probability / (self.disruption_probability + self.recovery_probability)
		elif self.random_process_type == 'E':
			pi_down = sum(self.disruption_state_list) / len(self.disruption_state_list)
			pi_up = 1 - pi_down
		else:
			pi_up = None
			pi_down = None

		return pi_up, pi_down
