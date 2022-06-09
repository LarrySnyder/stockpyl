# ===============================================================================
# stockpyl - Policy Class
# -------------------------------------------------------------------------------
# Updated: 11-25-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

This module contains the |class_policy| class. A |class_policy| object is used to 
encapsulate inventory policy calculations and to make order quantity calculations.

.. note:: |fosct_notation|

**Example:** Create a |class_policy| object representing a base-stock policy with
base-stock level 60. Calculate the order quantity if the current inventory position
is 52.5.

	.. testsetup:: *

		from stockpyl.policy import *

	.. doctest::

		>>> pol = Policy(type='BS', base_stock_level=60)
		>>> pol.get_order_quantity(inventory_position=52.5)
		7.5

API Reference
-------------

"""

# ===============================================================================
# Imports
# ===============================================================================

import numpy as np

# ===============================================================================
# Policy Class
# ===============================================================================

class Policy(object):
	"""A |class_policy| object is used to encapsulate inventory policy calculations and to make
	order quantity calculations.

	Parameters
	----------
	**kwargs 
		Keyword arguments specifying values of one or more attributes of the |class_demand_source|, 
		e.g., ``type='BS'``.

	Attributes
	----------
	type : str
		The policy type, as a string. Currently supported strings are:

			* None
			* 'BS' (base stock)
			* 'sS' (s, S)
			* 'rQ' (r, Q)
			* 'FQ' (fixed quantity)
			* 'EBS' (echelon base-stock)
			* 'BEBS' (balanced echelon base-stock)

	node : |class_node|
		The node the policy refers to.
	base_stock_level : float, optional
		The base-stock level used by the policy, if applicable. Required if ``type`` == 'BS',
		'EBS', or 'BEBS'.
	order_quantity : float, optional
		The order quantity used by the policy, if applicable. Required if ``type`` == 'FQ' or 'rQ'.
	reorder_point : float, optional
		The reorder point used by the policy, if applicable. Required if ``type`` == 'sS' or 'rQ'.
	order_up_to_level : float, optional
		The order-up-to level used by the policy, if applicable. Required if ``type`` == 'sS'.

	"""

	def __init__(self, **kwargs):
		"""Policy constructor method.

		kwargs : optional
			Optional keyword arguments to specify node attributes.
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
				raise AttributeError(f"{key} is not an attribute of Policy")

	# SPECIAL METHODS

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to this policy object. 
		Two policy objects are considered equal if all of their attributes 
		are equal. ``node`` attribute is compared using memory address.

		Note the following caveat:

		* Does not check equality of ``_node``. 

		Parameters
		----------
		other : |class_policy|
			The |class_policy| object to compare to.

		Returns
		-------
		bool
			True if the policy objects are equal, False otherwise.

		"""

		return self._type == other._type and \
			self._base_stock_level == other._base_stock_level and \
			self._order_quantity == other._order_quantity and \
			self._reorder_point == other._reorder_point and \
			self._order_up_to_level == other._order_up_to_level

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to this policy object. 
		Two policy objects are considered equal if all of their attributes 
		are equal.

		Parameters
		----------
		other : |class_demand_source|
			The policy object to compare to.

		Returns
		-------
		bool
			True if the policy objects are not equal, False otherwise.
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
	def node(self):
		return self._node

	@node.setter
	def node(self, value):
		self._node = value

	@property
	def base_stock_level(self):
		return self._base_stock_level

	@base_stock_level.setter
	def base_stock_level(self, value):
		self._base_stock_level = value

	@property
	def order_quantity(self):
		return self._order_quantity

	@order_quantity.setter
	def order_quantity(self, value):
		self._order_quantity = value

	@property
	def reorder_point(self):
		return self._reorder_point

	@reorder_point.setter
	def reorder_point(self, value):
		self._reorder_point = value

	@property
	def order_up_to_level(self):
		return self._order_up_to_level

	@order_up_to_level.setter
	def order_up_to_level(self, value):
		self._order_up_to_level = value

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the |class_policy| instance.

		Returns
		-------
			A string representation of the |class_policy| instance.

		"""
		# Build string of parameters.
		if self.type is None:
			return "Policy(None)"
		elif self.type in ('BS', 'EBS', 'BEBS'):
			param_str = "base_stock_level={:.2f}".format(self.base_stock_level)
		elif self.type == 'sS':
			param_str = "reorder_point={:.2f}, order_up_to_level={:.2f}".format(self.reorder_point,
																				self.order_up_to_level)
		elif self.type == 'rQ':
			param_str = "reorder_point={:.2f}, order_quantity={:.2f}".format(self.reorder_point, self.order_quantity)
		elif self.type == 'FQ':
			param_str = "order_quantity={:.2f}".format(self.order_quantity)
		else:
			param_str = ""

		return "Policy({:s}: {:s})".format(self.type, param_str)

	def __str__(self):
		"""
		Return the full name of the |class_policy| instance.

		Returns
		-------
			The policy name.

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
		if overwrite or not hasattr(self, '_node'):
			self._node = None
		if overwrite or not hasattr(self, '_base_stock_level'):
			self._base_stock_level = None
		if overwrite or not hasattr(self, '_order_quantity'):
			self._order_quantity = None
		if overwrite or not hasattr(self, '_reorder_point'):
			self._reorder_point = None
		if overwrite or not hasattr(self, '_order_up_to_level'):
			self._order_up_to_level = None

	def validate_parameters(self):
		"""Check that appropriate parameters have been provided for the given
		policy type. Raise an exception if not.
		"""
		if self.type not in (None, 'BS', 'sS', 'rQ', 'EBS', 'BEBS'): raise AttributeError("Valid type in (None, 'BS', 'sS', 'rQ', 'EBS', 'BEBS') must be provided")

		if self.type == 'BS':
			if self.base_stock_level is None: raise AttributeError("For 'BS' (base-stock) policy, base_stock_level must be provided")
		elif self.type == 'sS':
			if self.reorder_point is None: raise AttributeError("For 'sS' (s,S) policy, reorder_point must be provided")
			if self.order_up_to_level is None: raise AttributeError("For 'sS' (s,S) policy, order_up_to_level must be provided")
			if self.reorder_point <= self.order_up_to_level: raise AttributeError("For 'sS' (s,S) policy, reorder_point must be <= order_up_to_level")
		elif self.type == 'rQ':
			if self.reorder_point is None: raise AttributeError("For 'rQ' (r,Q) policy, reorder_point must be provided")
			if self.order_quantity is None: raise AttributeError("For 'rQ' (r,Q) policy, order_quantity must be provided")
		if self.type == 'EBS':
			if self.base_stock_level is None: raise AttributeError("For 'EBS' (echelon base-stock) policy, base_stock_level must be provided")
		if self.type == 'BEBS':
			if self.base_stock_level is None: raise AttributeError("For 'BEBS' (balanced echelon base-stock) policy, base_stock_level must be provided")

	# ORDER QUANTITY METHODS

	def get_order_quantity(self, predecessor_index=None, inventory_position=None,
						   echelon_inventory_position_adjusted=None):
		"""Calculate order quantity using the policy type specified in ``type``.
		If ``type`` is ``None``, return ``None``.

		The method obtains the necessary state variables (typically inventory position,
		and sometimes others) from ``self.node.network``.

		If ``inventory_position`` (and ``echelon_inventory_position_adjusted``, for
		balanced echelon base-stock policies) are provided, they will override the
		values indicated by the node's current state variables. This allows the
		policy to be queried for an order quantity even if no node or network are
		provided or have no state variables objects. If ``inventory_position``
		and ``echelon_inventory_position_adjusted`` are omitted
		(which is the typical use case), the current state variables will be used.

		Parameters
		----------
		predecessor_index : int, optional
			The predecessor for which the order quantity should be calculated.
			Use ``None`` for external supplier, or if node has only one predecessor
			(including external supplier).
		inventory_position : float, optional
			Inventory position immediately before order is placed (after demand is subtracted).
			If provided, the policy will use this IP instead of the IP indicated by the
			current state variables.
		echelon_inventory_position_adjusted : float, optional
			Adjusted echelon inventory position at node i+1, where i is the current node.
			If provided, the policy will use this EIPA instead of the EIPA indicated by
			current state variables. Used only for balanced echelon base-stock policies.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""
		if self.type is None:
			return None

		# Was inventory_position provided?
		if inventory_position is not None:
			IP = inventory_position
		else:
			if self.type == 'FQ':
				# Fixed-quantity policy does not need inventory position.
				IP = None
			else:
				# Calculate total demand (inbound orders), including successor nodes and
				# external demand.
				demand = self.node._get_attribute_total('inbound_order', self.node.network.period)

				# Calculate (local or echelon) inventory position, before demand is subtracted.
				if self.type in ('EBS', 'BEBS'):
					IP_before_demand = \
						self.node.state_vars_current.echelon_inventory_position(predecessor_index=predecessor_index)
				else:
					IP_before_demand = \
						self.node.state_vars_current.inventory_position(predecessor_index=predecessor_index)

				# Calculate current inventory position, after demand is subtracted.
				IP = IP_before_demand - demand

		# Determine order quantity based on policy.
		if self.type == 'BS':
			return self._get_order_quantity_base_stock(IP)
		elif self.type == 'sS':
			return self._get_order_quantity_s_S(IP)
		elif self.type == 'rQ':
			return self._get_order_quantity_r_Q(IP)
		elif self.type == 'FQ':
			return self._get_order_quantity_fixed_quantity()
		elif self.type == 'EBS':
			return self._get_order_quantity_echelon_base_stock(IP)
		elif self.type == 'BEBS':
			# Was EIPA provided?
			if echelon_inventory_position_adjusted is not None:
				EIPA = echelon_inventory_position_adjusted
			else:
				# Determine partner node and adjusted echelon inventory position.
				if self.node.index == max(self.node.network.node_indices):
					EIPA = np.inf
				else:
					partner_node = self.node.network.get_node_from_index(self.node.index + 1)
					EIPA = partner_node.state_vars_current._echelon_inventory_position_adjusted()

			return self._get_order_quantity_balanced_echelon_base_stock(IP, EIPA)
		else:
			return None

	def _get_order_quantity_base_stock(self, inventory_position):
		"""Calculate order quantity using base-stock policy.

		Parameters
		-------
		inventory_position : float
			Inventory position immediately before order is placed.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return max(0.0, self.base_stock_level - inventory_position)

	def _get_order_quantity_s_S(self, inventory_position):
		"""Calculate order quantity using (s,S) policy.

		Parameters
		-------
		inventory_position : float
			Inventory position immediately before order is placed.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		if inventory_position <= self.reorder_point:
			return self.order_up_to_level - inventory_position
		else:
			return 0

	def _get_order_quantity_r_Q(self, inventory_position):
		"""Calculate order quantity using (r,Q) policy.

		Parameters
		-------
		inventory_position : float
			Inventory position immediately before order is placed.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		if inventory_position <= self.reorder_point:
			return self.order_quantity
		else:
			return 0.0

	def _get_order_quantity_fixed_quantity(self):
		"""Calculate order quantity using fixed-quantity policy.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return self.order_quantity

	def _get_order_quantity_echelon_base_stock(self, echelon_inventory_position):
		"""Calculate order quantity using echelon base-stock policy.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return max(0.0, self.base_stock_level - echelon_inventory_position)

	def _get_order_quantity_balanced_echelon_base_stock(self, echelon_inventory_position,
													   echelon_inventory_position_adjusted):
		"""Calculate order quantity.
		Follows a balanced echelon base-stock policy, i.e., order up to :math:`min{S_i, IN^+_{i+1}}`, where
		:math:`S_i` is the echelon base-stock level and :math:`IN^+_{i+1}` is the adjusted echelon inventory position
		for node :math:`i+1`.
		A balanced echelon base-stock policy is optimal for assembly systems (see Rosling (1989)), but
		only if the system is in long-run balance (again, see Rosling). If the system
		is not in long-run balance, the policy also requires checking that the predecessor
		nodes have sufficient inventory, which this function does not do. The system may
		begin in long-run balance for certain initial conditions, but no matter the initial
		conditions, it will eventually reach long-run balance; see Rosling.

		Obtains the state variables it needs from ``self.node.network``.

		Parameters
		----------
		echelon_inventory_position : float
			Echelon inventory position immediately before order is placed.
			Echelon IP at stage i = sum of on-hand inventories at i and at or
			in transit to all of its downstream stages, minus backorders at
			downstream-most stage, plus on-order inventory at stage i.
		echelon_inventory_position_adjusted : float
			Adjusted echelon inventory position at node i+1, where i is the current node.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		# Determine target inventory position.
		target_IP = min(self.base_stock_level, echelon_inventory_position_adjusted)
		order_quantity = max(0.0, target_IP - echelon_inventory_position)

		return max(0.0, order_quantity)

