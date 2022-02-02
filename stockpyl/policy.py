# ===============================================================================
# stockpyl - Policy Class
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 11-25-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
This module contains the ``Policy`` class. A ``Policy`` object is used to make
order quantity calculations.

Notation and equation and section numbers refer to Snyder and Shen,
"Fundamentals of Supply Chain Theory", Wiley, 2019, 2nd ed., except as noted.
"""

# ===============================================================================
# Imports
# ===============================================================================

import numpy as np


# ===============================================================================
# Data Types
# ===============================================================================

# class InventoryPolicyType(Enum):
# 	CUSTOM = 0
# 	BASE_STOCK = 1
# 	r_Q = 2
# 	s_S = 3
# 	FIXED_QUANTITY = 4
# 	ECHELON_BASE_STOCK = 5
# 	BALANCED_ECHELON_BASE_STOCK = 6
# 	LOCAL_BASE_STOCK = 7
# #	STERMAN = 3
# #	RANDOM = 4
#

# ===============================================================================
# Policy Class
# ===============================================================================

class Policy(object):
	"""The ``Policy`` class is used to encapsulate inventory policy calculations.

	Attributes
	----------
	_type : str
		The policy type, as a string. Currently supported strings are:
			* None
			* 'BS' (base stock)
			* 'sS' (s, S)
			* 'rQ' (r, Q)
			* 'FQ' (fixed quantity)
			* 'EBS' (echelon base-stock)
			* 'BEBS' (balanced echelon base-stock)
	_node : SupplyChainNode
		The node the policy refers to.
	_base_stock_level : float
		The base-stock level used by the policy, if applicable.
	_order_quantity : float
		The order quantity used by the policy, if applicable.
	_reorder_point : float
		The reorder point used by the policy, if applicable.
	_order_up_to_level : float
		The order-up-to level used by the policy, if applicable.

	"""

	# TODO: handle predecessor-specific order quantities

	def __init__(self, type=None, node=None):
		"""Policy constructor method.
		"""
		# Initialize parameters to None. (Relevant parameters will be filled later.)
		self._type = type
		self._node = node
		self._base_stock_level = None
		self._order_quantity = None
		self._reorder_point = None
		self._order_up_to_level = None

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
		Return a string representation of the ``Policy`` instance.

		Returns
		-------
			A string representation of the ``Policy`` instance.

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
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	# METHODS

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
			Use ``None'' for external supplier, or if node has only one predecessor
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
				demand = self.node.get_attribute_total('inbound_order', self.node.network.period)

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
			return self.get_order_quantity_base_stock(IP)
		elif self.type == 'sS':
			return self.get_order_quantity_s_S(IP)
		elif self.type == 'rQ':
			return self.get_order_quantity_r_Q(IP)
		elif self.type == 'FQ':
			return self.get_order_quantity_fixed_quantity()
		elif self.type == 'EBS':
			return self.get_order_quantity_echelon_base_stock(IP)
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
					EIPA = partner_node.state_vars_current.echelon_inventory_position_adjusted()

			return self.get_order_quantity_balanced_echelon_base_stock(IP, EIPA)
		else:
			return None

	def get_order_quantity_base_stock(self, inventory_position):
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

	def get_order_quantity_s_S(self, inventory_position):
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

	def get_order_quantity_r_Q(self, inventory_position):
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

	def get_order_quantity_fixed_quantity(self):
		"""Calculate order quantity using fixed-quantity policy.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return self.order_quantity

	def get_order_quantity_echelon_base_stock(self, echelon_inventory_position):
		"""Calculate order quantity using echelon base-stock policy.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return max(0.0, self.base_stock_level - echelon_inventory_position)

	def get_order_quantity_balanced_echelon_base_stock(self, echelon_inventory_position,
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

		# TODO: unit tests

		# Determine target inventory position.
		target_IP = min(self.base_stock_level, echelon_inventory_position_adjusted)
		order_quantity = max(0.0, target_IP - echelon_inventory_position)

		return max(0.0, order_quantity)

	# OTHER METHODS

	def validate_parameters(self):
		"""Check that appropriate parameters have been provided for the given
		policy type. Raise an exception if not.
		"""
		assert self.type in (None, 'BS', 'sS', 'rQ', 'EBS', 'BEBS'), "Valid type in (None, 'BS', 'sS', 'rQ', 'EBS', 'BEBS') must be provided"

		if self.type == 'BS':
			assert self.base_stock_level is not None, "For 'BS' (base-stock) policy, base_stock_level must be provided"
		elif self.type == 'sS':
			assert self.reorder_point is not None, "For 'sS' (s,S) policy, reorder_point must be provided"
			assert self.order_up_to_level is not None, "For 'sS' (s,S) policy, order_up_to_level must be provided"
			assert self.reorder_point <= self.order_up_to_level, "For 'sS' (s,S) policy, reorder_point must be <= order_up_to_level"
		elif self.type == 'rQ':
			assert self.reorder_point is not None, "For 'rQ' (r,Q) policy, reorder_point must be provided"
			assert self.order_quantity is not None, "For 'rQ' (r,Q) policy, order_quantity must be provided"
		if self.type == 'EBS':
			assert self.base_stock_level is not None, "For 'EBS' (echelon base-stock) policy, base_stock_level must be provided"
		if self.type == 'BEBS':
			assert self.base_stock_level is not None, "For 'BEBS' (balanced echelon base-stock) policy, base_stock_level must be provided"



