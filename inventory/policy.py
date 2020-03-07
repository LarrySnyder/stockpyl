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


# ===============================================================================
# Data types
# ===============================================================================

class InventoryPolicyType(Enum):
	BASE_STOCK = 0
	r_Q = 1
	s_S = 2
	FIXED_QUANTITY = 3
#	STERMAN = 3
#	RANDOM = 4


# ===============================================================================
# Policy Class
# ===============================================================================

class Policy(object):
	"""The ``Policy`` class is used to encapsulate inventory policy calculations.

	Attributes
	----------
	policy_type : InventoryPolicyType
		The inventory policy type.
	param1 : float
		First inventory parameter; usage depends on policy_type.
	param2 : float
		Second inventory parameter; usage depends on policy_type.
	"""

	def __init__(self, policy_type=None, param1=None, param2=None):
		"""Policy constructor method.

		Parameters
		----------
		policy_type : InventoryPolicyType
			The inventory policy type.
		param1 : float
			First inventory parameter; usage depends on policy_type.
		param2 : float
			Second inventory parameter; usage depends on policy_type.
		"""
		# Initialize parameters to None. (Relevant parameters will be filled
		# below.)
		self.base_stock_level = None
		self.reorder_point = None
		self.order_quantity = None
		self.order_up_to_level = None

		# Set policy_type.
		self.policy_type = policy_type

		# Set (and validate) policy parameters.
		if policy_type == InventoryPolicyType.BASE_STOCK:
			self.base_stock_level = param1
		elif policy_type == InventoryPolicyType.r_Q:
			self.reorder_point = param1
			self.order_quantity = param2
			assert param2 >= 0, "For r_Q policy, param2 (order quantity) must be non-negative"
		elif policy_type == InventoryPolicyType.s_S:
			self.reorder_point = param1
			self.order_up_to_level = param2
			assert param1 <= param2, "For s_S policy, param1 (reorder point) must be <= param2 (order-up-to level)"
		elif policy_type == InventoryPolicyType.FIXED_QUANTITY:
			self.order_quantity = param1
			assert param1 >= 0, "for FIXED_QUANTITY policy, param1 (order quantity) must be non-negative"

	# # Properties.
	#
	# @property
	# def base_stock_level(self):
	# 	return self._base_stock_level
	#
	# @base_stock_level.setter
	# def base_stock_level(self, value):
	# 	self._base_stock_level = value
	#
	# @property
	# def reorder_point(self):
	# 	return self._reorder_point
	#
	# @reorder_point.setter
	# def reorder_point(self, value):
	# 	self._reorder_point = value
	#
	# @property
	# def order_quantity(self):
	# 	return self._order_quantity
	#
	# @order_quantity.setter
	# def order_quantity(self, value):
	# 	self._order_quantity = value
	#
	# @property
	# def order_up_to_level(self):
	# 	return self._order_up_to_level
	#
	# @order_up_to_level.setter
	# def order_up_to_level(self, value):
	# 	self._order_up_to_level = value

	# Special members.

	def __repr__(self):
		"""
		Return a string representation of the ``Policy`` instance.

		Returns
		-------
			A string representation of the ``Policy`` instance.

		"""
		# Build string of parameters.
		param_str = ""
		if self.base_stock_level is not None:
			param_str += "base_stock_level={:.2f}, ".format(self.base_stock_level)
		if self.reorder_point is not None:
			param_str += "reorder_point={:.2f}, ".format(self.reorder_point)
		if self.order_quantity is not None:
			param_str += "order_quantity={:.2f}, ".format(self.order_quantity)
		if self.order_up_to_level is not None:
			param_str += "order_up_to_level={:.2f}, ".format(self.order_up_to_level)
		if len(param_str) > 0:
			# Delete trailing comma and space.
			param_str = param_str[0:len(param_str)-2]

		return "Policy({:s}: {:s})".format(self.policy_type.name, param_str)

	def __str__(self):
		"""
		Return the full name of the ``Policy`` instance.

		Returns
		-------
			The policy name.

		"""
		return self.__repr__()

	def get_order_quantity(self, inventory_position=None):
		"""Calculate order quantity using the inventory policy type specified
		in policy_type. The following parameters must be specified:
			- BASE_STOCK: inventory_position
			- r_Q: inventory_position
			- s_S: inventory_position

		Returns
		-------
		order_quantity : float
			The order quantity.

		"""

		if self.policy_type == InventoryPolicyType.BASE_STOCK:
			return self.get_order_quantity_base_stock(inventory_position)
		elif self.policy_type == InventoryPolicyType.r_Q:
			return self.get_order_quantity_r_Q(inventory_position)
		elif self.policy_type == InventoryPolicyType.s_S:
			return self.get_order_quantity_s_S(inventory_position)
		elif self.policy_type == InventoryPolicyType.FIXED_QUANTITY:
			return self.get_order_quantity_fixed_quantity()

	def get_order_quantity_base_stock(self, inventory_position):
		"""Calculate order quantity using a base-stock policy.

		Parameters
		----------
		inventory_position : float
			Inventory position immediately before order is placed.

		Returns
		-------
		order_quantity : float
			The order quantity.

		"""
		return max(0.0, self.base_stock_level - inventory_position)

	def get_order_quantity_r_Q(self, inventory_position):
		"""Calculate order quantity using an (r,Q) policy.

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

	def get_order_quantity_s_S(self, inventory_position):
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
			return self.order_up_to_level - inventory_position
		else:
			return 0

	def get_order_quantity_fixed_quantity(self):
		"""Calculate order quantity using a fixed-quantity policy.

		Parameters
		----------

		Returns
		-------
		order_quantity : float
			The order quantity.

		"""
		return self.order_quantity

