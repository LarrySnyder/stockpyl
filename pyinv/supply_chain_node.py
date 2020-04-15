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

import numpy as np

from pyinv.datatypes import *
from pyinv.policy import *
from pyinv.demand_source import *


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
	demand_source : DemandSource
		Demand source object.
	initial_inventory_level : float
		Initial pyinv level.
	initial_orders : float # TODO: allow list
		Initial outbound order quantity.
	initial shipments : float # TODO: allow list
		Initial inbound shipment quantity.
	inventory_policy : Policy
		Inventory policy to be used to make pyinv decisions.
	supply_type : SupplyType
		Supply type (unlimited, etc.).
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

		# --- Index and Name --- #
		self.index = index
		self.name = name

		# --- Attributes Related to Network Structure --- #
		self.network = network
		self._predecessors = []
		self._successors = []

		# --- Data/Inputs --- #
		self.local_holding_cost = None
		self.echelon_holding_cost = None
		self.stockout_cost = None
#		self.lead_time = 0
		self.shipment_lead_time = 0
		self.order_lead_time = 0
		self.demand_source = None
		self.initial_inventory_level = 0
		self.initial_orders = 0
		self.initial_shipments = 0
		self.inventory_policy = None
		self.supply_type = SupplyType.NONE

		# --- State Variables/Performance Measures --- #

		# inbound_shipment[p][t] = shipment quantity arriving at node from
		# predecessor node p in period t. If p is None, refers to external supply.
		self.inbound_shipment = None

		# inbound_order[s][t] = order quantity arriving at node from successor
		# node s in period t. If s is None, refers to external demand.
		self.inbound_order = None

		# outbound_shipment[s][t] = outbound shipment to node s in period t.
		# If s is None, refers to external demand.
		self.outbound_shipment = None

		# on_order[p][t] = on-order quantity (items that have been ordered from
		# p but not yet received) at node at the beginning of period t. If p
		# is None, refers to external supply.
		self.on_order = None

		# inventory_level[t] = pyinv level (positive, negative, or zero) at
		# node at the beginning of period t.
		self.inventory_level = None

		# backorders[s][t] = number of backorders for successor s at the
		# beginning of period t. If s is None, refers to external demand.
		# Sum over all successors should always equal max{0, -inventory_level}.
		self.backorders = None

		# ending_inventory_level[t] = pyinv level (positive, negative, or
		# zero) at node at the end of period t.
		# NOTE: This is just for convenience, since EIL[t] = IL[t+1].
		self.ending_inventory_level = None

		# Costs: each refers to a component of the cost (or the total cost)
		# incurred at the node in period t.
		self.holding_cost_incurred = None
		self.stockout_cost_incurred = None
		self.in_transit_holding_cost_incurred = None
		self.total_cost_incurred = None

		# demand_met_from_stock[t] = demands met from stock at the node in
		# period t
		self.demand_met_from_stock = None

		# fill_rate[t] = cumulative fill rate in periods 0, ..., t.
		self.fill_rate = None

		# --- Decision Variables --- #

		# order_quantity[p][t] = order quantity placed by the node to
		# predecessor p in period t. If p is None, refers to external supply.
		self.order_quantity = None

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

	# Properties related to input parameters.

	@property
	def holding_cost(self):
		# An alias for ``local_holding_cost``. Read only.
		return self.local_holding_cost

	@property
	def lead_time(self):
		# An alias for ``shipment_lead_time``. Read only.
		return self.shipment_lead_time

	# Special methods.

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

	def __hash__(self):
		"""
		Return the hash for the node, which equals its index.

		"""
		return self.index

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

	def get_one_successor(self):
		"""Get one successor of the node. If the node has more than one
		successor, return the first in the list. If the node has no
		successors, return ``None``.

		Returns
		-------
		successor : SupplyChainNode
			A successor of the node.
		"""
		if len(self._successors) == 0:
			return None
		else:
			return self._successors[0]

	def get_one_predecessor(self):
		"""Get one predecessor of the node. If the node has more than one
		predecessor, return the first in the list. If the node has no
		predecessor, return ``None``.

		Returns
		-------
		predecessor : SupplyChainNode
			A predecessor of the node.
		"""
		if len(self._predecessors) == 0:
			return None
		else:
			return self._predecessors[0]

	# Attribute management.

	def get_attribute_total(self, attribute, period, include_external=True):
		"""Return total of attribute for the period specified, for an
		attribute that is indexed by successor or predecessor, i.e.,
		inbound_shipment, on_order, inbound_order, outbound_shipment, or
		backorders. (If another attribute is specified, returns the value of the
		attribute, without any summation.)

		If ``period`` is ``None``, sums the attribute over all periods.

		If ``include_external`` is ``True``, includes the external supply or
		demand node (if any) in the total.

		Example: get_attribute_total(inbound_shipment, 5) returns the total
		inbound shipment, from all predecessor nodes (including the external
		supply, if any), in period 5.

		Parameters
		----------
		attribute : str
			Attribute to be totalled. Error occurs if attribute is not present.
		period : int
			Time period. Set to ``None`` to sum over all periods.
		include_external : bool
			Include the external supply or demand node (if any) in the total?

		Returns
		-------
		float
			The total value of the attribute.

		"""
		if attribute in ('inbound_shipment', 'on_order'):
			# These attributes are indexed by predecessor.
			if include_external and self.supply_type != SupplyType.NONE:
				pred_indices = self.predecessor_indices + [None]
			else:
				pred_indices = self.predecessor_indices
			if period is None:
				return np.sum([self.__dict__[attribute][p_index][:]
							   for p_index in pred_indices])
			else:
				return np.sum([self.__dict__[attribute][p_index][period]
							   for p_index in pred_indices])
		elif attribute in ('inbound_order', 'outbound_shipment', 'backorders'):
			# These attributes are indexed by successor.
			if include_external and self.demand_source.type != DemandType.NONE:
				succ_indices = self.successor_indices + [None]
			else:
				succ_indices = self.successor_indices
			if period is None:
				return np.sum([self.__dict__[attribute][s_index][:]
						   for s_index in succ_indices])
			else:
				return np.sum([self.__dict__[attribute][s_index][period]
							   for s_index in succ_indices])
		else:
			if period is None:
				return np.sum([self.__dict__[attribute][:]])
			else:
				return self.__dict__[attribute][period]



