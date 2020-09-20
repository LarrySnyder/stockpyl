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
	_predecessors : list
		List of immediate predecesssor ``SupplyChainNode``s.
	_successors : list
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
	state_vars : list of NodeStateVars
		List of NodeStateVars, one for each period in a simulation.
	state_vars_current : NodeStateVars
		Shortcut to most recent set of state variables. (Period is determined
		from ``self.network.period``.
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
		self.shipment_lead_time = 0
		self.order_lead_time = 0
		self.demand_source = None
		self.initial_inventory_level = 0
		self.initial_orders = 0
		self.initial_shipments = 0
		self.inventory_policy = None
		self.supply_type = SupplyType.NONE

		# --- State Variables --- #
		self.state_vars = []

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

	# Properties related to input parameters and state variables.

	@property
	def holding_cost(self):
		# An alias for ``local_holding_cost``. Read only.
		return self.local_holding_cost

	@property
	def lead_time(self):
		# An alias for ``shipment_lead_time``. Read only.
		return self.shipment_lead_time

	@property
	def state_vars_current(self):
		# An alias for the most recent set of state variables. Read only.
		return self.state_vars[self.network.period]

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
				return np.sum([self.state_vars[t].__dict__[attribute][p_index]
							   for t in range(len(self.state_vars)) for p_index in pred_indices])
			else:
				return np.sum([self.state_vars[period].__dict__[attribute][p_index]
							   for p_index in pred_indices])
		elif attribute in ('inbound_order', 'outbound_shipment', 'backorders_by_successor'):
			# These attributes are indexed by successor.
			if include_external and self.demand_source.type != DemandType.NONE:
				succ_indices = self.successor_indices + [None]
			else:
				succ_indices = self.successor_indices
			if period is None:
				return np.sum([self.state_vars[t].__dict__[attribute][s_index]
							   for t in range(len(self.state_vars)) for s_index in succ_indices])
			else:
				return np.sum([self.state_vars[period].__dict__[attribute][s_index]
							   for s_index in succ_indices])
		else:
			if period is None:
				return np.sum([self.state_vars[:].__dict__[attribute]])
			else:
				return self.state_vars[period].__dict__[attribute]


# ===============================================================================
# NodeStateVars Class
# ===============================================================================

class NodeStateVars(object):
	"""The ``NodeStateVars`` class contains values of the state variables
	for a supply chain node.

	Notation below in brackets [...] is from Snyder and Shen (2019).

	Attributes
	----------
	node : SupplyChainNode
		The node the state variables refer to.
	period : int
		The period of the simulation that the state variables refer to.
	inbound_shipment_pipeline : dict
		``inbound_shipment_pipeline[p][r]`` = shipment quantity arriving
		from predecessor node ``p`` in ``r`` periods from the current period.
		If ``p`` is ``None``, refers to external supply.
	inbound_shipment : dict
		``inbound_shipment[p]`` = shipment quantity arriving at node from
		predecessor node ``p`` in the current period. If ``p`` is ``None``,
		refers to external supply.
	inbound_order_pipeline : dict
		``inbound_order_pipeline[s][r]`` = order quantity arriving from
		successor node ``s`` in ``r`` periods from the current period.
		If ``s`` is ``None``, refers to external demand.
	inbound_order : dict
		``inbound_order[s]`` = order quantity arriving at node from successor
		node ``s`` in the current period. If ``s`` is ``None``, refers to
		external demand.
	outbound_shipment : dict
		``outbound_shipment[s]`` = outbound shipment to successor node ``s``.
		If ``s`` is ``None``, refers to external demand.
	on_order_by_predecessor : dict
		``on_order_by_predecessor[p]`` = on-order quantity (items that have been
		ordered from successor node ``p`` but not yet received) at node at the
		beginning of period. If ``p`` is ``None``, refers to external supply.
	inventory_level : float
		Inventory level (positive, negative, or zero) at node at the beginning
		of period.
	backorders_by_successor : dict
		``backorders_by_successor[s]`` = number of backorders for successor
		``s`` at the beginning of period. If ``s`` is ``None``, refers to
		external demand.
		Sum over all successors should always equal max{0, -inventory_level}.
	ending_inventory_level : float
		Inventory level (positive, negative, or zero) at node at the end of period.
		NOTE: This is just for convenience, since EIL[t] = IL[t+1].
	holding_cost_incurred : float
		Holding cost incurred at the node in the period.
	stockout_cost_incurred : float
		Stockout cost incurred at the node in the period.
	in_transit_holding_cost_incurred : float
		In-transit holding cost incurred at the node in the period.
	total_cost_incurred : float
		Total cost incurred at the node in the period.
	demand_met_from_stock : float
		Demands met from stock at the node in the period.
	fill_rate : float
		Cumulative fill rate in periods 0, ..., period.
	order_quantity : dict
		``order_quantity[p]`` = order quantity placed by the node to
		predecessor ``p`` in period. If ``p`` is ``None``, refers to external supply.
		# TODO: rename to outbound_order
	"""

	def __init__(self, node=None, period=None):
		"""NodeStateVars constructor method.

		If ``node`` is provided, the state variable dicts (``inbound_shipment``,
		``inbound_order``, etc.) are initialized with the appropriate keys.
		Otherwise, they are set to empty dicts and must be initialized before
		using.

		Parameters
		----------
		node : SupplyChainNode, optional
			The node to which these state variables refer.
		period : int, optional
			The period to which these state variables refer.
		"""
		# --- Node --- #
		self.node = node
		self.period = period

		# --- Primary State Variables --- #
		# These are set explicitly during the simulation.

		if node:

			# Build lists of predecessor and successor indices, including external
			# supply and demand, if any.
			# TODO: build this feature into the node object.
			if node.supply_type != SupplyType.NONE:
				predecessor_indices = node.predecessor_indices + [None]
			else:
				predecessor_indices = node.predecessor_indices
				# TODO: shouldn't this be "is not None and ..." ? (a few lines down too)
			if node.demand_source is None or node.demand_source.type != DemandType.NONE:
				successor_indices = node.successor_indices + [None]
			else:
				successor_indices = node.successor_indices

			# Initialize dicts with appropriate keys.
			self.inbound_shipment_pipeline = {p_index:
				[0] * (self.node.shipment_lead_time+self.node.shipment_lead_time+1)
											for p_index in predecessor_indices}
			self.inbound_shipment = {p_index: 0 for p_index in predecessor_indices}
			self.inbound_order_pipeline = {s_index:
				[0] * (self.node.network.nodes[s_index].order_lead_time+1)
										   for s_index in node.successor_indices}
			# Add external customer to inbound_order_pipeline. (Must be done
			# separately since external customer does not have its own node,
			# or its own order lead time.)
			if node.demand_source is None or node.demand_source.type != DemandType.NONE:
				self.inbound_order_pipeline[None] = [0]
			self.inbound_order = {s_index: 0 for s_index in successor_indices}
			self.outbound_shipment = {s_index: 0 for s_index in successor_indices}
			self.on_order_by_predecessor = {p_index: 0 for p_index in predecessor_indices}
			self.backorders_by_successor = {s_index: 0 for s_index in successor_indices}
			self.order_quantity = {p_index: 0 for p_index in predecessor_indices}

		else:

			# Initialize dicts to empty dicts.
			self.inbound_shipment_pipeline = {}
			self.inbound_shipment = {}
			self.inbound_order_pipeline = {}
			self.inbound_order = {}
			self.outbound_shipment = {}
			self.on_order_by_predecessor = {}
			self.backorders_by_successor = {}
			self.order_quantity = {}

		# Remaining state variables.
		self.inventory_level = 0
		self.ending_inventory_level = 0

		# Costs: each refers to a component of the cost (or the total cost)
		# incurred at the node in the period.
		self.holding_cost_incurred = 0
		self.stockout_cost_incurred = 0
		self.in_transit_holding_cost_incurred = 0
		self.total_cost_incurred = 0

		# Fill rate quantities.
		self.demand_met_from_stock = 0
		self.fill_rate = 0

	# --- Calculated State Variables --- #
	# These are calculated based on the primary state variables.

	# on_hand = current on-hand inventory.
	@property
	def on_hand(self):
		return max(0, self.inventory_level)

	# backorders = current backorders. Should always equal sum over all successors
	# of backorders_by_successor[s].
	@property
	def backorders(self):
		return max(0, -self.inventory_level)

	def in_transit_to(self, successor):
		"""Return current total inventory in transit to a given successor.
		(Declared as a function, not a property, because needs to take an argument.)
		Includes items that will be/have been delivered during the current period.

		Parameters
		----------
		successor : SupplyChainNode
			The successor node.

		Returns
		-------
			The current inventory in transit to the successor.
		"""
		return np.sum([successor.state_vars[self.period].inbound_shipment_pipeline[self.node.index][:]])

#		return np.sum([successor.state_vars[self.period + t].inbound_shipment[self.node.index]
#				for t in range(successor.shipment_lead_time)])

	def in_transit_from(self, predecessor):
		"""Return current total inventory in transit from a given predecessor.
		(Declared as a function, not a property, because needs to take an argument.)
		Includes items that will be/have been delivered during the current period
		(``self.network.period``).

		Parameters
		----------
		predecessor : SupplyChainNode
			The predecessor node (or ``None`` for external supplier).

		Returns
		-------
			The current inventory in transit from the predecessor.
		"""
		if predecessor is None:
			p = None
		else:
			p = predecessor.index

		return np.sum(self.inbound_shipment_pipeline[p][:])

#		return np.sum([self.node.state_vars[self.period + t].inbound_shipment[p]
#				for t in range(self.node.shipment_lead_time)])

	# in_transit = current total inventory in transit to the node. If node has
	# more than 1 predecessor (it is an assembly node), including external supplier,
	# in-transit items are counted using the "units" of the node itself.
	# That is, they are divided by the total number of predecessors.
	# TODO: handle BOM
	@property
	def in_transit(self):
		total_in_transit = np.sum([self.in_transit_from(p) for p in self.node.predecessors])
		if self.node.supply_type == SupplyType.NONE:
			if total_in_transit == 0:
				return 0
			else:
				return total_in_transit / len(self.node.predecessors)
		else:
			total_in_transit += self.in_transit_from(None)
			return total_in_transit / (len(self.node.predecessors) + 1)

	# on_order = current total on-order quantity. If node has more than 1
	# predecessor (it is an assembly node), including external supplier,
	# on-order items are counted using the "units" of the node itself.
	# That is, they are divided by the total number of predecessors.
	# TODO: handle BOM
	@property
	def on_order(self):
		total_on_order = self.node.get_attribute_total('on_order_by_predecessor',
												  self.period,
												  include_external=True)
		if total_on_order == 0:
			return 0
		else:
			if self.node.supply_type == SupplyType.NONE:
				return total_on_order / len(self.node.predecessors)
			else:
				return total_on_order / (len(self.node.predecessors) + 1)

	# inventory_position = current local inventory position at node
	# = IL + OO.
	@property
	def inventory_position(self):
		return self.inventory_level + self.on_order

	# echelon_on_hand_inventory = current echelon on-hand inventory at node
	# = on-hand inventory at node and at or in transit to all of its
	# downstream nodes.
	@property
	def echelon_on_hand_inventory(self):
		EOHI = self.on_hand
		for d in self.node.descendants:
			EOHI += d.state_vars[self.period].on_hand
			# Add in-transit quantity from predecessors that are descendents
			# of self (or equal to self).
			for p in d.predecessors:
				if p.index == self.node.index or p in self.node.descendants:
					EOHI += d.state_vars[self.period].in_transit_from(p)
		return EOHI

	# echelon_inventory_level = current echelon inventory level at node
	# = echelon on-hand inventory minus backorders at terminal node(s)
	# downstream from node.
	@property
	def echelon_inventory_level(self):
		EIL = self.echelon_on_hand_inventory
		for d in self.node.descendants + [self.node]:
			if d in self.node.network.sink_nodes:
				EIL -= d.state_vars[self.period].backorders
		return EIL

	# echelon_inventory_position = current echelon inventory position at node
	# = echelon inventory level + on order.
	@property
	def echelon_inventory_position(self):
		return self.echelon_inventory_level + self.on_order
