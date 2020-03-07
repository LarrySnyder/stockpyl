# ===============================================================================
# PyInv - SupplyChainNetwork Class
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 03-06-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
This module contains the ``SupplyChainNetwork`` class.

"""

# ===============================================================================
# Imports
# ===============================================================================

from inventory.datatypes import *
from inventory.policy import *


# ===============================================================================
# SupplyChainNetwork Class
# ===============================================================================

class SupplyChainNetwork(object):
	"""The ``SupplyChainNetwork`` class contains one or more nodes, each
	represented by a SupplyChainNode object.

	Attributes
	----------
	nodes : list
		A list of all nodes in the network. (Read only.)

	"""

	def __init__(self):
		"""SupplyChainNetwork constructor method.

		"""
		# Initialize attributes.
		self._nodes = []

	@property
	def nodes(self):
		return self._nodes

	# Special members.

	def __repr__(self):
		"""
		Return a string representation of the ``SupplyChainNetwork`` instance.

		Returns
		-------
		str
			A string representation of the ``SupplyChainNetwork`` instance.

		"""
		return "SupplyChainNetwork({:s})".format(str(vars(self)))

