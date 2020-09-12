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
import networkx as nx

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
	local_holding_cost_function : function
		Function that calculates local holding cost per period, as a function
		of ending inventory level. Function must take exactly one argument, the
		ending IL. Function should check that IL > 0.
	stockout_cost : float
		Stockout cost, per unit (per period, if backorders). [p]
	stockout_cost_function : function
		Function that calculates stockout cost per period, as a function
		of ending inventory level. Function must take exactly one argument, the
		ending IL. Function should check that IL < 0.
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
		# TODO: when set local or echelon h.c., update the other
		self.local_holding_cost = None
		self.echelon_holding_cost = None
		self.local_holding_cost_function = None
		self.stockout_cost = None
		self.stockout_cost_function = None
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

		# The following state variables are updated explicitly by sim.py.

		# inbound_shipment[p][t] = shipment quantity arriving at node from
		# predecessor node p in period t. If p is None, refers to external supply.
		self.inbound_shipment = None

		# inbound_order[s][t] = order quantity arriving at node from successor
		# node s in period t. If s is None, refers to external demand.
		self.inbound_order = None

		# outbound_shipment[s][t] = outbound shipment to node s in period t.
		# If s is None, refers to external demand.
		self.outbound_shipment = None

		# on_order_by_predecessor[p][t] = on-order quantity (items that have been ordered from
		# p but not yet received) at node at the beginning of period t. If p
		# is None, refers to external supply.
		self.on_order_by_predecessor = None

		# inventory_level[t] = inventory level (positive, negative, or zero) at
		# node at the beginning of period t.
		self.inventory_level = None

		# backorders_by_successor[s][t] = number of backorders for successor s at the
		# beginning of period t. If s is None, refers to external demand.
		# Sum over all successors should always equal max{0, -inventory_level}.
		self.backorders_by_successor = None

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

	@property
	def descendants(self):
		# TODO: build the digraph at the network level, keep it static, and update it when network structure updates
		G = self.network.networkx_digraph()
		desc = nx.descendants(G, self.index)
		return [self.network.get_node_from_index(d) for d in desc]

	@property
	def ancestors(self):
		G = self.network.networkx_digraph()
		anc = nx.ancestors(G, self.index)
		return [self.network.get_node_from_index(a) for a in anc]

	# Properties related to input parameters.

	@property
	def holding_cost(self):
		# An alias for ``local_holding_cost``. Read only.
		return self.local_holding_cost

	@property
	def lead_time(self):
		# An alias for ``shipment_lead_time``. Read only.
		return self.shipment_lead_time

	# Properties related to state variables.
	# TODO: write unit tests for these properties

	# on_hand = current on-hand inventory.
	@property
	def on_hand(self):
		return max(0, self.inventory_level[self.network.period])

	# backorders = current backorders. Should always equal sum over all successors
	# of backorders_by_successor[s][t].
	@property
	def backorders(self):
		return max(0, -self.inventory_level[self.network.period])

	def in_transit_to(self, successor):
		"""Return current total inventory in transit to a given successor.
		(Declared as a function, not a property, because needs to take an argument.)

		Parameters
		----------
		successor : SupplyChainNode
			The successor node.

		Returns
		-------
			The current inventory in transit to the successor.
		"""
		return np.sum([successor.inbound_shipment[self.index][self.network.period+t]
				for t in range(successor.shipment_lead_time)])

	def in_transit_from(self, predecessor):
		"""Return current total inventory in transit from a given predecessor.
		(Declared as a function, not a property, because needs to take an argument.)

		Parameters
		----------
		predecessor : SupplyChainNode
			The predecessor node (or ``None`` for external supplier).

		Returns
		-------
			The current inventory in transit from the predecessor.
		"""
		return np.sum([self.inbound_shipment[predecessor.index][self.network.period+t]
				for t in range(self.shipment_lead_time)])

	# in_transit = current total inventory in transit to the node. If node has
	# more than 1 predecessor (it is an assembly node), including external supplier,
	# in-transit items are counted using the "units" of the node itself.
	# That is, they are divided by the total number of predecessors.
	# TODO: handle BOM
	@property
	def in_transit(self):
		total_in_transit = np.sum([self.in_transit_from(p) for p in self.predecessors])
		if total_in_transit == 0:
			return 0
		else:
			if self.supply_type == SupplyType.NONE:
				return total_in_transit / len(self.predecessors)
			else:
				return total_in_transit / (len(self.predecessors) + 1)

	# on_order = current total on-order quantity. If node has more than 1
	# predecessor (it is an assembly node), including external supplier,
	# on-order items are counted using the "units" of the node itself.
	# That is, they are divided by the total number of predecessors.
	# TODO: handle BOM
	@property
	def on_order(self):
		total_on_order = self.get_attribute_total('on_order_by_predecessor',
												  self.network.period,
												  include_external=True)
		if total_on_order == 0:
			return 0
		else:
			if self.supply_type == SupplyType.NONE:
				return total_on_order / len(self.predecessors)
			else:
				return total_on_order / (len(self.predecessors) + 1)

	# inventory_position = current local inventory position at node
	# = IL + OO.
	@property
	def inventory_position(self):
		return self.inventory_level[self.network.period] + self.on_order

	# echelon_on_hand_inventory = current echelon on-hand inventory at node
	# = on-hand inventory at node and at or in transit to all of its
	# downstream nodes.
	@property
	def echelon_on_hand_inventory(self):
		EOHI = self.on_hand
		for d in self.descendants:
			EOHI += d.on_hand
			# Add in-transit quantity from predecessors that are descendents
			# of self (or equal to self).
			for p in d.predecessors:
				if p.index == self.index or p in self.descendants:
					EOHI += d.in_transit_from(p)
		return EOHI

	# echelon_inventory_level = current echelon inventory level at node
	# = echelon on-hand inventory minus backorders at terminal node(s)
	# downstream from node.
	@property
	def echelon_inventory_level(self):
		EIL = self.echelon_on_hand_inventory
		for d in self.descendants + [self]:
			if d in self.network.sink_nodes:
				EIL -= d.backorders
		return EIL

	# echelon_inventory_position = current echelon inventory position at node
	# = echelon inventory level + on order.
	@property
	def echelon_inventory_position(self):
		return self.echelon_inventory_level + self.on_order

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
		inbound_shipment, on_order_by_predecessor, inbound_order, outbound_shipment, or
		backorders_by_successor. (If another attribute is specified, returns the value of the
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
		if attribute in ('inbound_shipment', 'on_order_by_predecessor'):
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
		elif attribute in ('inbound_order', 'outbound_shipment', 'backorders_by_successor'):
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



