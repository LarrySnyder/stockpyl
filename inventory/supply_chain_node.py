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
	predecessors : list
		List of immediate predecesssor ``SupplyChainNode``s.
	successors : list
		List of immediate successor ``SupplyChainNode``s.

	# Data/inputs.

	local_holding_cost : float
		Local holding cost, per unit per period. [h']
	echelon_holding_cost : float
		Echelon holding cost, per unit per period. [h] # not currently supported
	stockout_cost : float
		Stockout cost, per unit (per period, if backorders). [p]
	lead_time : int
		Shipment lead time. [L]
	shipment_lead_time : int
		Shipment lead time. [L] # not currently supported # TODO: set as alias for lead_time
	order_lead_time : int
		Order lead time.
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
	initial_IL : float
		Initial inventory level.
	initial_orders : float # TODO: allow list
		Initial outbound order quantity.
	initial shipments : float # TODO: allow list
		Initial inbound shipment quantity.
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

		# Index and name.
		self.index = index
		self.name = name

		# Attributes related to network structure.
		self.network = network
		self._predecessors = []
		self._successors = []

		# Data/inputs.
		self.local_holding_cost = None
		self.echelon_holding_cost = None
		self.stockout_cost = None
		self.lead_time = 0
		self.shipment_lead_time = 0
		self.order_lead_time = 0
		self.demand_type = DemandType.NONE
		self.demand_mean = None
		self.demand_standard_deviation = None
		self.demands = []
		self.demand_probabilities = []
		self.demand_lo = None
		self.demand_hi = None
		self.initial_IL = 0
		self.initial_orders = 0
		self.initial_shipments = 0
		self.inventory_policy = None

	# Properties related to network structure.

	@property
	def predecessors(self):
		return self._predecessors

	@property
	def successors(self):
		return self._successors

	@property
	def predecessor_indices(self):
		return [node.index for node in self._predecessors]

	@property
	def successor_indices(self):
		return [node.index for node in self._successors]

	# Special members.

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to the node. Two nodes are
		considered equal if their indices are equal.

		Parameters
		----------
		other : SupplyChainNode
			The node to compare to.

		Returns
		-------
		bool
			True if the nodes are equal, False otherwise.

		"""
		return self.index == other.index

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to the node. Two nodes are
		considered equal if their indices are equal.

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

	# def __hash__(self):
	# 	"""
	# 	Return the hash for the node, which equals its index.
	#
	# 	"""
	# 	return self.index

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

