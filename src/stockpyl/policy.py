# ===============================================================================
# stockpyl - Policy Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
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
	product_index : int, optional
		The index of the product the policy refers to. The product must be handled by ``node``. May set to ``None``
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
		"""Convert the |class_policy| object to a dict. The ``node`` attribute is set
		to the indices of the node, rather than to the object.

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
			else:
				# Remove leading '_' to get property names.
				prop = attr[1:] if attr[0] == '_' else attr
				pol_dict[prop] = getattr(self, prop)

		return pol_dict

	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_policy| object with attributes copied from the
		values in ``the_dict``. The ``node`` attribute is set to the index
		of the node, like it is in the dict, but should be converted to |class_node|
		objecs if this function is called recursively from a |class_node|'s 
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

	def get_order_quantity(self, product=None, order_capacity=None, include_raw_materials=False,
		inventory_position=None, echelon_inventory_position_adjusted=None):
		"""Calculate order quantity for the product using the policy type specified in ``type``.
		If the node is single-product, ``product`` may be set to ``None`` and the function will determine
		the product automatically. If ``type`` is ``None``, returns ``None``. 
		
		If ``include_raw_materials`` is ``False`` (the default), returns a singleton that equals the order
		quantity for ``product``. If ``include_raw_materials`` is ``True``, returns 
		a nested dict such that ``get_order_quantity[p][rm]`` is the order
		quantity to place to predecessor ``p`` for raw material product ``rm``, expressed in units of ``rm``. 
		The dict includes an entry in which ``pred`` and ``rm`` are both ``None``, which corresponds to the order quantity 
		of the product itself, expressed in units of the product.

		If ``order_capacity`` is provided, the FG order quantity returned will not exceed this capacity,
		and the RM order quantities will be scaled accordingly.

		If there are multiple predecessors that supply the same raw material, this function will, in general,
		order all required units of that raw material from a single supplier. The function can be overloaded to
		specify an allocation rule. 
		
		The method obtains the necessary state variables (typically inventory position,
		and sometimes others) from ``self.node.network``. The order quantities are set using the
		bill of materials structure for the node/product.

		If the policy's ``node`` attribute is ``None``, the returned dict only contains ``product`` itself,
		no raw materials.

		If ``inventory_position`` (and ``echelon_inventory_position_adjusted``, for
		balanced echelon base-stock policies) are provided, they will override the
		values indicated by the node's current state variables. This allows the
		policy to be queried for an order quantity even if no node/product or network are
		provided or have no state variables objects. If ``inventory_position``
		and ``echelon_inventory_position_adjusted`` are ``None``
		(which is the typical use case), the current state variables will be used.

		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index) for which the order quantity should be calculated.
			If the node is single-product, either set ``product`` to the index of the single product, 
			or to ``None`` and the function will determine the index automatically. 
		order_capacity : float, optional
			Maximum number of units of ``product`` that can be ordered in the current period.
		include_raw_materials : bool, optional
			If ``False``, the function will return the order quantity for ``product``, as a 
			singleton float. If ``True``, the function will return a dict indicating the order quantities
			for all raw materials and predecessors.
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
		order_quantity : float or dict
			The order quantity for ``product`` if ``include_raw_materials`` is ``False``; or, if 
			``include_raw_materials`` is ``True``, a nested
			dict such that ``get_order_quantity[p][rm]`` is the order quantity to place to predecessor ``p`` 
			for raw material product ``rm``, expressed in units of ``rm``. The dict includes an entry in which ``pred`` and ``rm`` 
			are both ``None``, which corresponds to the order quantity of the product itself, expressed in units of the product.

		Raises
		------
		AttributeError
			If the policy's ``node`` attribute (or ``product`` attribute, if ``node`` is multi-product)
			is ``None`` and ``inventory_position`` or other required state variables are ``None``.
		"""
		if self.type is None:
			return None
		
		# Calculate IP.
		if inventory_position is not None:
			# inventory_position was provided -- use it.
			IP = inventory_position
		else:
			if self.type == 'FQ':
				# Fixed-quantity policy does not need inventory position.
				IP = None
			else:
				# Make sure node attribute is set or inventory_position is provided.
				if self.node is None:
					raise AttributeError("You must either provide inventory_position or set the node attribute of the Policy object to the node that it refers to. (Usually this should be done when you first create the Policy object.)")
				if self.node.is_multiproduct and self.product is None:
					raise AttributeError("You must either provide inventory_position or set the product attribute of the Policy object to the product that it refers to (since the node is multi-product). (Usually this shoudl be done when you first creat the Policy object.)")

				# Validate product.
				_, prod_ind = self.node.validate_product(product)
				
				# Calculate total demand (inbound orders), including successor nodes and
				# external demand, in FG units.
				demand = self.node._get_state_var_total('inbound_order', self.node.network.period, product=prod_ind)

				# Calculate (local or echelon) inventory position, before demand is subtracted. Exclude from pipeline
				# RM units that are "earmarked" for other products at this node.
				if self.type in ('EBS', 'BEBS'):
					IP_before_demand = \
						self.node.state_vars_current.echelon_inventory_position(product=prod_ind, predecessor=None, raw_material=None)
				else:
					IP_before_demand = \
						self.node.state_vars_current.inventory_position(product=prod_ind, exclude_earmarked_units=True)

				# Calculate current inventory position, after demand is subtracted.
				IP = IP_before_demand - demand
 
		# Determine order quantity based on policy. This order quantity is in units of the product.
		if self.type == 'BS':
			OQ = self._get_order_quantity_base_stock(IP)
		elif self.type == 'sS':
			OQ = self._get_order_quantity_s_S(IP)
		elif self.type == 'rQ':
			OQ = self._get_order_quantity_r_Q(IP)
		elif self.type == 'FQ':
			OQ = self._get_order_quantity_fixed_quantity()
		elif self.type == 'EBS':
			OQ = self._get_order_quantity_echelon_base_stock(IP)
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
					partner_node = self.node.network.nodes_by_index[self.node.index + 1]
					EIPA = partner_node.state_vars_current._echelon_inventory_position_adjusted()

			OQ = self._get_order_quantity_balanced_echelon_base_stock(IP, EIPA)
		else:
			OQ = None
		
		# Adjust OQ to account for capacity, if provided.
		if order_capacity is not None:
			OQ = min(OQ, order_capacity)
	
		# Include raw materials?
		if not include_raw_materials:
			return OQ
		else:
			# Initialize returned dict with FG order quantity.
			OQ_dict = {None: {None: OQ}}

			# Keep track of how much is left to order for each raw material (to avoid double-ordering
			# if there are multiple suppliers). Use raw material units.
			still_to_order = {rm_index: OQ * self.node.NBOM(product=prod_ind, predecessor=None, raw_material=rm_index) \
								for rm_index in self.node.raw_materials_by_product(prod_ind, return_indices=True)}

			# Loop through raw materials and predecessors, and calculate order quantities for each.
			if OQ is not None:
				for rm_index in self.node.raw_materials_by_product(prod_ind, return_indices=True):
					for pred_index in self.node.raw_material_suppliers_by_raw_material(rm_index, return_indices=True):

						# Create key for pred in outer level of dict, if it doesn't already exist.
						if pred_index not in OQ_dict:
							OQ_dict[pred_index] = {}

						# Order still_to_order, which just equals the order quantity, or 0
						# if we have already ordered this RM from a different supplier.
						# (This may change in the future if we introduce policies or supplier-specific ordering capacities.)
						OQ_dict[pred_index][rm_index] = still_to_order[rm_index]
		
						# Subtract order from still_to_order.
						still_to_order[rm_index] -= OQ_dict[pred_index][rm_index]

			return OQ_dict

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

