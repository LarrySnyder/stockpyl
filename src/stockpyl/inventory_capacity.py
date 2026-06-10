# ===============================================================================
# stockpyl - InventoryCapacity Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

This module contains the |class_inventory_capacity| class. A |class_inventory_capacity|
object represents the type of capacity each node is subject to (i.e., its effects).
The object keeps track of the current capacity state.

.. note:: |fosct_notation|

**Example:** 

"""


# ===============================================================================
# Imports
# ===============================================================================

import numpy as np
import copy

from stockpyl.helpers import *


# ===============================================================================
#InventoryCapacity Class
# ===============================================================================

class InventoryCapacity(object):
	"""
	A |class_inventory_capacity| object represents the type of capacity each node is subject to (i.e., its effects).
	The object keeps track of the current capacity state.

	Parameters
	----------
	**kwargs 
		Keyword arguments specifying values of one or more attributes of the |class_disruption_process|, 
		e.g., ``inventory_capacity_type='HC'``.

	Attributes
	----------
	inventory_capacity : float
		Maximum on-hand inventory.

	inventory_capacity_type : str
		The type of capacity, as a string. Currently supported strings are:
			* 'HC' (holding-cost: additional holding cost charged on excess_inventory) (default)
			* 'PP' (production-pausing: triggers shutdown for consequtive periods until inventory_level drops below inventory_capacity)
		
	additional_holding_cost: float
		Holidng cost charged when inventory_level > inventory_capacity, per unit per period.

	over_capacity : bool
		``True`` if the inventory_level > inventory_capacity, ``False`` otherwise.
	
	shutdown : bool
		``True`` if inventory_capacity_type = 'PP' and and inventory_level is over capacity, ``False`` otherwise
	"""

	def __init__(self, **kwargs):
		"""InventoryCapacity constructor method.

		Parameters
		----------
		kwargs : optional
			Optional keyword arguments to specify |class_inventory_capacity| attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match a |class_inventory_capacity| attribute.
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
				raise AttributeError(f"{key} is not an attribute of InventoryCapacity")
		
		#validate parameters
		self.validate_parameters()
			


	_DEFAULT_VALUES = {
		'_inventory_capacity': None,
		'_inventory_capacity_type': None,
		'_over_capacity': False,
		'_additional_holding_cost': None
	}

	# SPECIAL METHODS

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to this |class_inventory_capacity| object. 
		Two |class_invnetory_capacity| objects are considered equal if all of their attributes 
		(*except* ``_over_capacity``, the state variable) are equal.

		Parameters
		----------
		other : |class_inventory_capacity|
			The |class_inventory_capacity| object to compare to.

		Returns
		-------
		bool
			``True`` if the |class_inventory_capacity| objects are equal, ``False`` otherwise.
		"""
		if other is None:
			return False
		else:
			for attr in self._DEFAULT_VALUES.keys():
				if getattr(self, attr) != getattr(other, attr):
					return False
			return True

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to this |class_inventory_capacity| object. 
		Two |class_invnetory_capacity| objects are considered equal if all of their attributes 
		(*except* ``_over_capacity``, the state variable) are equal.

		Parameters
		----------
		other : |class_invnetory_capacity|
			The |class_invnetory_capacity| object to compare to.

		Returns
		-------
		bool
			True if the |class_invnetory_capacity| objects are not equal, False otherwise.
		"""
		return not self.__eq__(other)

	# PROPERTY GETTERS AND SETTERS

	@property
	def inventory_capacity_type(self):
		return self._inventory_capacity_type

	@inventory_capacity_type.setter
	def inventory_capacity_type(self, value):
		self._inventory_capacity_type = value

	@property
	def inventory_capacity(self):
		return self._inventory_capacity

	@inventory_capacity.setter
	def inventory_capacity(self, value):
		self._inventory_capacity = value
	
	@property
	def additional_holding_cost(self):
		return self._additional_holding_cost

	@additional_holding_cost.setter
	def additional_holding_cost(self, value):
		self._additional_holding_cost = value

	@property
	def over_capacity(self):
		return self._over_capacity

	@over_capacity.setter
	def over_capacity(self, value):
		self._over_capacity = value

	@property
	def shutdown(self):
		return self._shutdown

	@shutdown.setter
	def shutdown(self, value):
		self._shutdown = value
		
	# READ-ONLY PROPERTIES

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the |class_invnetory_capacity| instance.

		Returns
		-------
			A string representation of the |class_invnetory_capacity| instance.

		"""
		# Build string of parameters.
		if self.inventory_capacity_type is None:
			return "InventoryCapacity(None)"
		elif self.inventory_capacity_type == 'HC':
			param_str = "additional_holding_cost={:.6f}".format(self.addiitonal_holding_cost)
		elif self.inventory_capacity_type == 'PP':
			param_str = "shutdown={:.6f}".format(self.shutdown)
		else:
			param_str = ""

		return "InventoryCapacity({:s}, {:s}: {:s})".format(self.inventory_capacity_type, self.inventory_capacity, param_str)

	def __str__(self):
		"""
		Return the full name of the |class_invnetory_capacity| instance.

		Returns
		-------
			The |class_invnetory_capacity| name.

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
		capacity type. Raise an exception if not.
		"""
		if self.inventory_capacity_type not in (None, 'HC', 'PP'): raise AttributeError("Valid random_process_type in (None, 'HC', 'PP') must be provided")
		if self.inventory_capacity_type == 'HC' and self.additional_holding_cost is None: raise AttributeError("additional_holding_cost not provided")

	# CONVERTING TO/FROM DICTS

	def to_dict(self):
		"""Convert the |class_invnetory_capacity| object to a dict. List attributes
		are deep-copied so changes to the original
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
		"""Return a new |class_invnetory_capacity| object with attributes copied from the
		values in ``the_dict``. List attributes 
		are deep-copied so changes to the original dict do not get propagated to the object.
		Any missing attributes are set to their default values.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_invnetory_capacity|, typically created using ``to_dict()``.

		Returns
		-------
		InventoryCapacity
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

	# CAPACITY STATE MANAGEMENT

	def update_capacity_state(self, period=None):
		"""Update the capacity state by setting the ``over_capacity`` attribute accordingly. 

		If ``inventory_capacity_type`` is ``PP``and over_capacity = ``True``, sets ``shutdown`` to ``True``.

		Parameters
		----------
		period : int, optional
			The period to update the disruption state for. If ``inventory_capacity_type`` = 'PP'.
		"""

		if self.inventory_capacity_type is None:
			over_capacity = False
			shutdown = False

		self.over_capacity = over_capacity
		self.shutdown = shutdown




