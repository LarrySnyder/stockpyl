# ===============================================================================
# PyInv - Policy Class
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 03-06-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
This module contains the ``Policy`` class. A ``Policy`` object is used to make
order quantity calculations.

"""

# ===============================================================================
# Imports
# ===============================================================================

from enum import Enum
from abc import ABC, abstractmethod


# ===============================================================================
# Data Types
# ===============================================================================

class InventoryPolicyType(Enum):
	CUSTOM = 0
	BASE_STOCK = 1
	r_Q = 2
	s_S = 3
	FIXED_QUANTITY = 4
	ECHELON_BASE_STOCK = 5
	BALANCED_ECHELON_BASE_STOCK = 6
#	STERMAN = 3
#	RANDOM = 4


# ===============================================================================
# Policy Class and Subclasses
# ===============================================================================

class Policy(ABC):
	"""The ``Policy`` class is used to encapsulate inventory policy calculations.
	This is an abstract class, so it must be subclassed. Subclasses define the
	actual policy.
	"""

	@abstractmethod
	def get_order_quantity(self, predecessor_index=None):
		pass


class PolicyBaseStock(Policy):
	"""The ``PolicyBaseStock`` class is used for base-stock policies.

	Attributes
	----------
	_policy_type : InventoryPolicyType
		The inventory policy type.
	_base_stock_level : float
		The base-stock level. [:math:`S`]
	"""

	def __init__(self, base_stock_level):
		"""Policy constructor method.
		"""
		# Set policy_type.
		self._policy_type = InventoryPolicyType.BASE_STOCK

		# Set policy parameter(s).
		self._base_stock_level = base_stock_level

	# PROPERTIES

	@property
	def policy_type(self):
		# Read only.
		return self._policy_type

	@property
	def base_stock_level(self):
		return self._base_stock_level

	@base_stock_level.setter
	def base_stock_level(self, value):
		self._base_stock_level = value

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the ``Policy`` instance.

		Returns
		-------
			A string representation of the ``Policy`` instance.

		"""
		# Build string of parameters.
		param_str = "base_stock_level={:.2f}".format(self.base_stock_level)

		return "Policy({:s}: {:s})".format(self.policy_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	# METHODS

	def get_order_quantity(self, inventory_position=None, predecessor_index=None):
		# TODO: doesn't currently make use of predecessor_index -- this will be needed when BS levels are pred-specific
		"""Calculate order quantity.

		Parameters
		----------
		inventory_position : float
			Inventory position immediately before order is placed.
		predecessor_index : int, optional
			The predecessor for which the order quantity should be calculated.
			Use ``None'' for external supplier, or if node has only one predecessor
			(including external supplier).

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return max(0.0, self._base_stock_level - inventory_position)


class PolicysS(Policy):
	"""The ``PolicysS`` class is used for (s,S) policies.

	Attributes
	----------
	_policy_type : InventoryPolicyType
		The inventory policy type.
	_reorder_point : float
		The reorder point. [:math:`s`]
	_order_up_to_level : float
		The order-up-to level. [:math:`S`]
	"""

	def __init__(self, reorder_point, order_up_to_level):
		"""Policy constructor method.
		"""
		# Set policy_type.
		self._policy_type = InventoryPolicyType.s_S

		# Set policy parameter(s).
		self._reorder_point = reorder_point
		self._order_up_to_level = order_up_to_level

	# PROPERTIES

	@property
	def policy_type(self):
		# Read only.
		return self._policy_type

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
		param_str = "reorder_point={:.2f}, order_up_to_level={:.2f}".format(self._reorder_point, self._order_up_to_level)

		return "Policy({:s}: {:s})".format(self.policy_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	# METHODS

	def get_order_quantity(self, inventory_position=None, predecessor_index=None):
		"""Calculate order quantity using an (s,S) policy.

		Parameters
		----------
		inventory_position : float
			Inventory position immediately before order is placed.
		predecessor_index : int, optional
			The predecessor for which the order quantity should be calculated.
			Use ``None'' for external supplier, or if node has only one predecessor
			(including external supplier).

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		if inventory_position <= self._reorder_point:
			return self._order_up_to_level - inventory_position
		else:
			return 0


class PolicyrQ(Policy):
	"""The ``PolicyrQ`` class is used for (r,Q) policies.

	Attributes
	----------
	_policy_type : InventoryPolicyType
		The inventory policy type.
	_reorder_point : float
		The reorder point. [:math:`r`]
	_order_quantity : float
		The order quantity. [:math:`Q`]
	"""

	def __init__(self, reorder_point, order_quantity):
		"""Policy constructor method.
		"""
		# Set policy_type.
		self._policy_type = InventoryPolicyType.r_Q

		# Set policy parameter(s).
		self._reorder_point = reorder_point
		self._order_quantity = order_quantity

	# PROPERTIES

	@property
	def policy_type(self):
		# Read only.
		return self._policy_type

	@property
	def reorder_point(self):
		return self._reorder_point

	@reorder_point.setter
	def reorder_point(self, value):
		self._reorder_point = value

	@property
	def order_quantity(self):
		return self._order_quantity

	@order_quantity.setter
	def order_quantity(self, value):
		self._order_quantity = value

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the ``Policy`` instance.

		Returns
		-------
			A string representation of the ``Policy`` instance.

		"""
		# Build string of parameters.
		param_str = "reorder_point={:.2f}, order_quantity={:.2f}".format(self._reorder_point,
																			self._order_quantity)

		return "Policy({:s}: {:s})".format(self.policy_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	# METHODS

	def get_order_quantity(self, inventory_position=None, predecessor_index=None):
		"""Calculate order quantity using an (s,S) policy.

		Parameters
		----------
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


class PolicyFixedQuantity(Policy):
	"""The ``PolicyrQ`` class is used for fixed-quantity policies.

	Attributes
	----------
	_policy_type : InventoryPolicyType
		The inventory policy type.
	_order_quantity : float
		The order quantity. [:math:`Q`]
	"""

	def __init__(self, order_quantity):
		"""Policy constructor method.
		"""
		# Set policy_type.
		self._policy_type = InventoryPolicyType.FIXED_QUANTITY

		# Set policy parameter(s).
		self._order_quantity = order_quantity

	# PROPERTIES

	@property
	def policy_type(self):
		# Read only.
		return self._policy_type

	@property
	def order_quantity(self):
		return self._order_quantity

	@order_quantity.setter
	def order_quantity(self, value):
		self._order_quantity = value

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the ``Policy`` instance.

		Returns
		-------
			A string representation of the ``Policy`` instance.

		"""
		# Build string of parameters.
		param_str = "order_quantity={:.2f}".format(self._order_quantity)

		return "Policy({:s}: {:s})".format(self.policy_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	# METHODS

	def get_order_quantity(self, inventory_position=None, predecessor_index=None):
		"""Calculate order quantity using a fixed-quantity policy.

		Parameters
		----------
		inventory_position : float
			Inventory position immediately before order is placed.
			(Ignored for this inventory policy type.)

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return self.order_quantity


class PolicyEchelonBaseStock(Policy):
	"""The ``PolicyEchelonBaseStock`` class is used for echelon base-stock
	policies.

	Attributes
	----------
	_policy_type : InventoryPolicyType
		The inventory policy type.
	_echelon_base_stock_level : float
		The echelon base-stock level. [:math:`S`]
	"""

	def __init__(self, echelon_base_stock_level):
		"""Policy constructor method.
		"""
		# Set policy_type.
		self._policy_type = InventoryPolicyType.ECHELON_BASE_STOCK

		# Set policy parameter(s).
		self._echelon_base_stock_level = echelon_base_stock_level

	# PROPERTIES

	@property
	def policy_type(self):
		# Read only.
		return self._policy_type

	@property
	def echelon_base_stock_level(self):
		return self._echelon_base_stock_level

	@echelon_base_stock_level.setter
	def echelon_base_stock_level(self, value):
		self._echelon_base_stock_level = value

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the ``Policy`` instance.

		Returns
		-------
			A string representation of the ``Policy`` instance.

		"""
		# Build string of parameters.
		param_str = "echelon_base_stock_level={:.2f}".format(self.echelon_base_stock_level)

		return "Policy({:s}: {:s})".format(self.policy_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	# METHODS

	def get_order_quantity(self, echelon_inventory_position=None, predecessor_index=None):
		"""Calculate order quantity.

		Parameters
		----------
		echelon_inventory_position : float
			Echelon inventory position immediately before order is placed.
			Echelon IP at stage i = sum of on-hand inventories at i and at or
			in transit to all of its downstream stages, minus backorders at
			downstream-most stage, plus on-order inventory at stage i.

		Returns
		-------
		order_quantity : float
			The order quantity.
		"""

		return max(0.0, self._echelon_base_stock_level - echelon_inventory_position)


class PolicyBalancedEchelonBaseStock(Policy):
	"""The ``PolicyBalancedEchelonBaseStock`` class is used for balanced echelon
	base-stock policies.

	Attributes
	----------
	_policy_type : InventoryPolicyType
		The inventory policy type.
	_echelon_base_stock_level : float
		The echelon base-stock level. [:math:`S`]
	"""

	def __init__(self, echelon_base_stock_level):
		"""Policy constructor method.
		"""
		# Set policy_type.
		self._policy_type = InventoryPolicyType.BALANCED_ECHELON_BASE_STOCK

		# Set policy parameter(s).
		self._echelon_base_stock_level = echelon_base_stock_level

	# PROPERTIES

	@property
	def policy_type(self):
		# Read only.
		return self._policy_type

	@property
	def echelon_base_stock_level(self):
		return self._echelon_base_stock_level

	@echelon_base_stock_level.setter
	def echelon_base_stock_level(self, value):
		self._echelon_base_stock_level = value

	# SPECIAL MEMBERS

	def __repr__(self):
		"""
		Return a string representation of the ``Policy`` instance.

		Returns
		-------
			A string representation of the ``Policy`` instance.

		"""
		# Build string of parameters.
		param_str = "echelon_base_stock_level={:.2f}".format(self.echelon_base_stock_level)

		return "Policy({:s}: {:s})".format(self.policy_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	# METHODS

	def get_order_quantity(self, echelon_inventory_position, echelon_inventory_position_adjusted, predecessor_index):
		"""Calculate order quantity.
		Follows a balanced echelon base-stock policy, i.e., order up to min{S_i, IN^+_{i+1}}, where
		S_i is the echelon base-stock level and IN^+_{i+1} is the adjusted echelon inventory position
		for node i+1.
		A balanced echelon base-stock policy is optimal for assembly systems (see Rosling (1989)), but
		only if the system is in long-run balance (again, see Rosling). If the system
		is not in long-run balance, the policy also requires checking that the predecessor
		nodes have sufficient inventory, which this function does not do. The system may
		begin in long-run balance for certain initial conditions, but no matter the initial
		conditions, it will eventually reach long-run balance; see Rosling.

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
		target_IP = min(self.echelon_base_stock_level, echelon_inventory_position_adjusted)
		order_quantity = max(0.0, target_IP - echelon_inventory_position)

		return max(0.0, order_quantity)


# ===============================================================================
# PolicyFactory Class
# ===============================================================================

class PolicyFactory(object):
	"""The ``PolicyFactory`` class is used to build ``Policy`` objects.

	Example
	-------
	To build a ``PolicyBaseStock`` object:

		policy_factory = PolicyFactory()
		policy = policy_factory.build_policy(InventoryPolicyType.BASE_STOCK, base_stock_level=100)

	It is also possible to create the subclass object directly, e.g.,

		policy = PolicyBaseStock(base_stock_level=100)

	"""

	def build_policy(self, policy_type, base_stock_level=None,
					 reorder_point=None, order_up_to_level=None,
					 order_quantity=None):
		"""
		Build and return a Policy object of the specified type.

		Parameters
		----------
		policy_type : InventoryPolicyType
			The desired inventory policy type.
		base_stock_level : float, optional
			The base-stock level. Required for BASE_STOCK policies.
		reorder_point : float, optional
			The reorder point. Required for r_Q and s_S policies.
		order_up_to_level : float, optional
			The order-up-to level. Required for s_S policies.
		order_quantity : float, optional
			The order quantity. Required for r_Q and FIXED_QUANTITY policies.

		Returns
		-------
		policy : Policy
			The Policy object.

		"""
		if policy_type == InventoryPolicyType.BASE_STOCK:
			policy = PolicyBaseStock(base_stock_level=base_stock_level)
		elif policy_type == InventoryPolicyType.r_Q:
			policy = PolicyrQ(reorder_point=reorder_point, order_quantity=order_quantity)
		elif policy_type == InventoryPolicyType.s_S:
			policy = PolicysS(reorder_point=reorder_point, order_up_to_level=order_up_to_level)
		elif policy_type == InventoryPolicyType.FIXED_QUANTITY:
			policy = PolicyFixedQuantity(order_quantity=order_quantity)
		elif policy_type == InventoryPolicyType.ECHELON_BASE_STOCK:
			policy = PolicyEchelonBaseStock(echelon_base_stock_level=base_stock_level)
		elif policy_type == InventoryPolicyType.BALANCED_ECHELON_BASE_STOCK:
			policy = PolicyBalancedEchelonBaseStock(echelon_base_stock_level=base_stock_level)
		else:
			raise(ValueError, "Unknown inventory policy type")

		return policy
