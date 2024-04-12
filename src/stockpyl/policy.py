# ===============================================================================
# stockpyl - Policy Class
# -------------------------------------------------------------------------------
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
	product : |class_product|, optional
		The product the policy refers to. The product must be handled by ``node``. Set to ``None``
		for single-product models.
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

	_DEFAULT_VALUES = {
		'_type': None,
		'_node': None,
		'_product': None,
		'_base_stock_level': None,
		'_order_quantity': None,
		'_reorder_point': None,
		'_order_up_to_level': None
	}

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

		if other is None:
			return False
		else:
			for attr in self._DEFAULT_VALUES.keys():
				if getattr(self, attr) != getattr(other, attr):
					return False
			return True

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
	def product(self):
		return self._product

	@product.setter
	def product(self, value):
		self._product = value

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

	def initialize(self):
		"""Initialize the parameters in the object to their default values. 
		"""
		for attr in self._DEFAULT_VALUES.keys():
			setattr(self, attr, self._DEFAULT_VALUES[attr])

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

	# CONVERTING TO/FROM DICTS

	def to_dict(self):
		"""Convert the |class_policy| object to a dict. The ``node`` and ``product`` attributes are set
		to the indices of the node and product (if any), rather than to the objects.

		Returns
		-------
		dict
			The dict representation of the object.
		"""
		# Initialize dict.
		pol_dict = {}

		# Attributes.
		for attr in self._DEFAULT_VALUES.keys():
			if attr == '_node':
				# Use index only.
				pol_dict['node'] = None if self.node is None else self.node.index
			elif attr == '_product':
				# Use index only.
				pol_dict['product'] = None if self.product is None else self.product.index
			else:
				# Remove leading '_' to get property names.
				prop = attr[1:] if attr[0] == '_' else attr
				pol_dict[prop] = getattr(self, prop)

		return pol_dict

	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_policy| object with attributes copied from the
		values in ``the_dict``. The ``node`` and ``product'' attributes are set to the indices
		of the node and product, like they are in the dict, but should be converted to |class_node|
		and |class_product| objects if this function is called recursively from a |class_node|'s 
		``from_dict()`` method.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_policy|, typically created using ``to_dict()``.

		Returns
		-------
		Policy
			The object converted from the dict.
		"""
		# Build empty Policy.
		pol = cls()
		if the_dict is not None:
			# Fill attributes.
			for attr in cls._DEFAULT_VALUES.keys():
				# Remove leading '_' to get property names.
				prop = attr[1:] if attr[0] == '_' else attr
				if prop in the_dict:
					value = the_dict[prop]
				else:
					value = cls._DEFAULT_VALUES[attr]
				setattr(pol, prop, value)

		return pol

	# ORDER QUANTITY METHODS

	def get_order_quantity(self, predecessor_index=None, predecessor_product_index=None, inventory_position=None,
						   echelon_inventory_position_adjusted=None):
		"""Calculate order quantity using the policy type specified in ``type``.
		If ``type`` is ``None``, return ``None``.

		The method obtains the necessary state variables (typically inventory position,
		and sometimes others) from ``self.node.network``. The order quantity is set using the
		bill of materials structure for the node/product.

		If ``inventory_position`` (and ``echelon_inventory_position_adjusted``, for
		balanced echelon base-stock policies) are provided, they will override the
		values indicated by the node's current state variables. This allows the
		policy to be queried for an order quantity even if no node/product or network are
		provided or have no state variables objects. If ``inventory_position``
		and ``echelon_inventory_position_adjusted`` are omitted
		(which is the typical use case), the current state variables will be used.

		Parameters
		----------
		predecessor_index : int, optional
			The predecessor for which the order quantity should be calculated.
			Use ``None`` for external supplier, or if node has only one predecessor
			(including external supplier).
		predecessor_product_index : int, optional
			The product at the predecessor for which the order quantity should be calculated.
			Use ``None`` if the predecessor is the external supplier. If the predecessor
			has only one product, ``predecessor_product_index`` can be set to ``None`` or to the
			index of that product.
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

		Raises
		------
		AttributeError
			If the policy's ``node`` attribute (or ``product`` attribute, if ``node`` is multi-product)
			is ``None`` and ``inventory_position`` or other required state variables are ``None``.
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
				# Make sure node attribute is set or inventory_position is provided.
				# TODO: adjust error message for multi-product?
				if self.node is None:
					raise AttributeError("You must either provide inventory_position or set the node attribute of the Policy object to the node that it refers to. (Usually this should be done when you first create the Policy object.)")
				if self.node.is_multiproduct and self.product is None:
					raise AttributeError("You must either provide inventory_position or set the product attribute of the Policy object to the product that it refers to (since the node is multi-product). (Usually this shoudl be done when you first creat the Policy object.)")
# TODO: stopped here

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
			# Make sure node attribute is set or inventory_position is provided.
			if self.node is None and echelon_inventory_position_adjusted is None:
				raise AttributeError("You must either provide echelon_inventory_position_adjusted or set the node attribute of the Policy object to the node that it refers to. (Usually this should be done when you first create the Policy object.)")

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

