# ===============================================================================
# PyInv - SupplyChainNode Class
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 03-06-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
This module contains the ``SupplyChainNode`` class, which is a stage or node
in a supply chain network.

"""

# ===============================================================================
# Imports
# ===============================================================================

from inventory.datatypes import *
from inventory.policy import *


# ===============================================================================
# SupplyChainNode Class
# ===============================================================================

class SupplyChainNode(object):
	"""The ``SupplyChainNode`` class contains the data, state variables, and
	performance measures for a supply chain node.

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Attributes
	----------
	# Attributes related to parent network.

	network : SupplyChainNetwork
		The network that contains the node.
	_predecessors : list
		List of immediate predecesssor ``SupplyChainNode``s.
	_successors : list
		List of immediate successor ``SupplyChainNode``s.

	# Data/inputs.

	local_holding_cost : float
		Local holding cost, per unit per period. [h'] # TODO: allow echelon holding costs
	stockout_cost : float
		Stockout cost, per unit (per period, if backorders). [p]
	lead_time : int
		Shipment lead time. [L] # TODO: create "alias" shipment_lead_time
	demand_type : DemandType
		Demand type (normal, deterministic, etc.).
	demand_mean : float
		Mean of demand per period. Required if ``demand_type`` == ``NORMAL``,
		ignored otherwise. [mu]
	demand_standard_deviation : float
		Standard deviation of demand per period. Required if ``demand_type`` ==
		``NORMAL``, ignored otherwise. [sigma]
	demands : list
		List of demands, one per period (if ``demand_type`` == ``DETERMINISTIC``),
		or list of possible demand values (if ``demand_type`` ==
		``DISCRETE_EXPLICIT``). Required if ``demand_type`` == ``DETERMINISTIC``
		or ``DISCRETE_EXPLICIT``, ignored otherwise. [d]
	demand_probabilities : list
		List of probabilities of each demand value. Required if ``demand_type``
		== ``DISCRETE_EXPLICIT``, ignored otherwise.
	demand_lo : float
		Low value of demand range. Required if ``demand_type`` ==
		``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
	demand_hi : float
		High value of demand range. Required if ``demand_type`` ==
		``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
	inventory_policy : Policy
		Inventory policy to be used to make inventory decisions.
	"""

	def __init__(self, index, name=None, network=None):
		"""SupplyChainNode constructor method.

		Parameters
		----------
		index : int
			Numeric index to identify node. In a SupplyChainNetwork, each node
			must have a unique index.
		name : str, optional
			String to identify node.
		network : SupplyChainNetwork
			The network that contains the node.
		"""
		# Initialize attributes.

		# Attributes related to network structure.
		self.network = network
		self._predecessors = []
		self._successors = []

		# Index and name.
		self.index = index
		self.name = name

		# Data/inputs.
		self.local_holding_cost = None
		self.stockout_cost = None
		self.lead_time = 0
		self.demand_type = DemandType.NONE
		self.demand_mean = None
		self.demand_standard_deviation = None
		self.demands = []
		self.demand_probabilities = []
		self.demand_lo = None
		self.demand_hi = None
		self.inventory_policy = None

	# Special members.

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to the node. Two nodes are
		considered equal if their names or indices are equal.

		Parameters
		----------
		other : SupplyChainNode
			The node to compare to.

		Returns
		-------
		bool
			True if the nodes are equal, False otherwise.

		"""
		return self.index == other.index or self.name == other.name

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to the node. Two nodes are
		considered equal if their names or indices are equal.

		Parameters
		----------
		other : SupplyChainNode
			The node to compare to.

		Returns
		-------
		bool
			True if the nodes are not equal, False otherwise.

		"""
		return not self.__eq__(other)

	def __repr__(self):
		"""
		Return a string representation of the ``SupplyChainNode`` instance.

		Returns
		-------
			A string representation of the ``SupplyChainNode`` instance.

		"""
		return "SupplyChainNode({:s})".format(str(vars(self)))

	# Neighbor management.

	def add_successor(self, successor):
		"""Add ``successor`` to the node's list of successors.

		Notes
		-----
		This method simply updates the node's list of successors. It does not
		add ``successor`` to the network. Typically, this method is called by
		the network.

		Parameters
		----------
		successor : SupplyChainNode
			The node to add as a successor.

		"""
		self._successors.append(successor)

	def add_predecessor(self, predecessor):
		"""Add ``predecessor`` to the node's list of predecessors.

		Notes
		-----
		This method simply updates the node's list of predecessors. It does not
		add ``predecessor`` to the network. Typically, this method is called by
		the network.

		Parameters
		----------
		predecessor : SupplyChainNode
			The node to add as a predecessor.

		"""
		self._predecessors.append(predecessor)

# # Methods to add and remove neighbors.
	#
	# def add_successor(self, successor):
	# 	"""Add a successor to the node.
	#
	# 	Parameters
	# 	----------
	# 	successor : SupplyChainNode
	# 		The node to add as a successor.
	#
	# 	"""
	#
	# 	# Add the successor to the node's list of _successors.
	# 	self._successors.append(successor)
	#
	# 	# Add the node to the successor's list of _predecessors.
	# 	successor._predecessors.append(self)
	#
	# 	# Add

