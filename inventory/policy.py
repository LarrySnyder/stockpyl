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
#	STERMAN = 3
#	RANDOM = 4


# ===============================================================================
# Policy Class
# ===============================================================================

class Policy(object):
	"""
	The ``Policy`` class.

	:arg InventoryPolicyType policy_type:
		The inventory policy type.
	:arg float param1:
		First inventory parameter; usage depends on policy_type.
	:arg float param2:
		Second inventory parameter; usage depends on policy_type.

	"""
	def __init__(self, policy_type=None, param1=None, param2=None):
		"""
		Card constructor method.

		:arg InventoryPolicyType policy_type:
			The inventory policy type.
		:arg float param1:
			First inventory parameter; usage depends on policy_type.
		:arg float param2:
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

		# Set policy parameters.
		if policy_type == InventoryPolicyType.BASE_STOCK:
			self.base_stock_level = param1
		elif policy_type == InventoryPolicyType.r_Q:
			self.reorder_point = param1
			self.order_quantity = param2
		elif policy_type == InventoryPolicyType.s_S:
			self.reorder_point = param1
			self.order_up_to_level = param2

	def __repr__(self):
		"""
		Returns a string representation of the ``Policy`` instance.

		:returns:
			A string representation of the Policy instance.

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
		Returns the full name of the ``Policy`` instance.

		:returns:
			The policy name.

		"""
		return self.__repr__()



