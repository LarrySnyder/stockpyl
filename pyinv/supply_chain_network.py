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

from pyinv.supply_chain_node import *
from pyinv.policy import *
from pyinv.helpers import *

import networkx as nx


# ===============================================================================
# SupplyChainNetwork Class
# ===============================================================================

class SupplyChainNetwork(object):
	"""The ``SupplyChainNetwork`` class contains one or more nodes, each
	represented by a SupplyChainNode object.

	Attributes
	----------
	nodes : list
		A list of all ``SupplyChainNode``s in the network. (Read only.)
	period : int
		The current period. Used for simulation.

	"""

	def __init__(self):
		"""SupplyChainNetwork constructor method.

		"""
		# Initialize attributes.
		self._nodes = []
		self._period = 0

	@property
	def nodes(self):
		return self._nodes

	@property
	def node_indices(self):
		"""Return list of indices of nodes in the network.
		"""
		return [node.index for node in self.nodes]

	@property
	def period(self):
		return self._period

	@period.setter
	def period(self, value):
		self._period = value

	@property
	def source_nodes(self):
		"""List of all source nodes, i.e., all nodes that have no predecessors.
		"""
		return [node for node in self.nodes if node.predecessor_indices == []]

	@property
	def sink_nodes(self):
		"""List of all sink nodes, i.e., all nodes that have no successors.
		"""
		return [node for node in self.nodes if node.successor_indices == []]

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

	# Methods for node handling.

	def get_node_from_index(self, index):
		"""Return node object with the specified index, or ``None`` if no
		matching node is found.

		Parameters
		----------
		index : int
			Index of node to find.

		Returns
		-------
		SupplyChainNode
			The node whose index is ``index``, or ``None`` if none.

		"""
		for node in self.nodes:
			if node.index == index:
				return node

		return None

	def reindex_nodes(self, old_to_new_dict):
		"""Change indices of the nodes in the network using ``old_to_new_dict``.

		Parameters
		----------
		old_to_new_dict : dict
			Dict in which keys are old indices and values are new indices.

		"""
		for node in self.nodes:
			node.index = old_to_new_dict[node.index]

	# Methods related to network structure.

	def add_node(self, node):
		"""Add ``node`` to the network. ``node`` will not be connected to other
		nodes that might be in the network already.

		If ``node`` is already in the network (as determined by the index),
		do nothing.

		Parameters
		----------
		node : SupplyChainNode
			The node to add to the network.

		"""

		# Check whether node is already in network.
		if node not in self.nodes:
			self.nodes.append(node)
			node.network = self

	def add_successor(self, node, successor_node):
		"""Add ``successor_node`` as a successor to ``node``. ``node`` must
		already be contained in the network.

		The method adds the nodes to each other's lists of _successors and
		_predecessors. If ``successor_node`` is not already contained in the
		network, the method also adds it. (The node is assumed to be contained
		in the network if its index or name match those of a node in the network.)

		Parameters
		----------
		node : SupplyChainNode
			The node to which the successor should be added.
		successor_node : SupplyChainNode
			The node to be added as a successor.

		"""

		# Add nodes to each other's predecessor and successor lists.
		node.add_successor(successor_node)
		successor_node.add_predecessor(node)

		# Add node to network (if not already contained in it).
		self.add_node(successor_node)

	def add_predecessor(self, node, predecessor_node):
		"""Add ``predecessor_node`` as a predecessor to ``node``. ``node`` must
		already be contained in the network.

		The method adds the nodes to each other's lists of _successors and
		_predecessors. If ``predecessor_node`` is not already contained in the
		network, the method also adds it. (The node is assumed to be contained
		in the network if its index or name match those of a node in the network.)

		Parameters
		----------
		node : SupplyChainNode
			The node to which the successor should be added.
		predecessor_node : SupplyChainNode
			The node to be added as a predecessor.

		"""

		# Add nodes to each other's predecessor and successor lists.
		node.add_predecessor(predecessor_node)
		predecessor_node.add_successor(node)

		# Add node to network (if not already contained in it).
		self.add_node(predecessor_node)

	def networkx_digraph(self):
		"""Build a ``networkx`` ``digraph`` object with the same structure as
		the ``SupplyChainNetwork``.

		Returns
		-------
		digraph : DiGraph
			The ``networkx`` ``digraph`` object.
		"""

		digraph = nx.DiGraph()
		digraph.add_nodes_from(self.node_indices)
		for n in self.nodes:
			for p in n.predecessors:
				digraph.add_edge(p.index, n.index)

		return digraph


# ===============================================================================
# Methods to Create Specific Network Structures
# ===============================================================================

def serial_system(num_nodes, node_indices=None, downstream_0=True,
				  local_holding_cost=0, echelon_holding_cost=0,
				  stockout_cost=0, order_lead_time=0,
				  shipment_lead_time=0, demand_type=None, demand_mean=0,
				  demand_standard_deviation=0, demand_lo=0, demand_hi=0,
				  demands=None, demand_probabilities=None, initial_IL=0,
				  initial_orders=0, initial_shipments=0, supply_type=None,
				  inventory_policy_type=None, local_base_stock_levels=None,
				  echelon_base_stock_levels=None,
				  reorder_points=None, order_quantities=None,
				  order_up_to_levels=None):
	"""Generate serial system with specified number of nodes.

	Other than ``num_nodes``, all parameters are optional. If they are provided,
	they must be either a dict, a list, or a singleton, with the following
	requirements:
		- If ``node_indices`` is provided, then the parameter may be specified
		either as a dict (with keys equal to the indices in ``node_indices``)
		or as a singleton (in which case all nodes will have that parameter
		set to the singleton value).
		- If ``node_indices`` is not provided, then the parameter may be
		specified either as a dict (with keys equal to 0,...,``num_nodes``-1),
		as a list, or as a singleton (in which case all nodes will have that
		parameter set to the singleton value). If the parameter is specified as
		a dict or list, then the keys or list indices must correspond to the
		actual indexing of the nodes; that is, if ``downstream_0`` is ``True``,
		then key/index ``0`` should refer to the downstream-most node, and if
		``downstream_0`` is ``False``, then key/index ``0`` should refer to the
		upstream-most node.

	Parameters
	----------
	num_nodes : int
		Number of nodes in serial system.
	node_indices : list, optional
		List of node indices, with downstream-most node listed first.
	downstream_0 : bool, optional
		If True, node 0 is downstream; if False, node 0 is upstream. Ignored if
		``node_labels`` is provided.
	local_holding_cost
	echelon_holding_cost
	stockout_cost
	order_lead_time
	shipment_lead_time
	demand_type
	demand_mean
	demand_standard_deviation
	demand_lo
	demand_hi
	demands
	initial_IL
	initial_orders
	initial_shipments
	supply_type
	inventory_policy_type
	local_base_stock_levels
	echelon_base_stock_levels
	reorder_points
	order_quantities
	order_up_to_levels

	Returns
	-------
	network : SupplyChainNetwork
		The serial system network, with parameters filled.

	# TODO: if initial_IL not provided, default to BS levels
	"""

#	print('hello')

	# Build list of node indices.
	if node_indices is not None:
		indices = node_indices
	elif downstream_0:
		indices = list(range(num_nodes))
	else:
		indices = list(range(num_nodes-1, -1, -1))

	# Build vectors of attributes.
	local_holding_cost_list = ensure_list_for_nodes(local_holding_cost, num_nodes, 0.0)
	echelon_holding_cost_list = ensure_list_for_nodes(echelon_holding_cost, num_nodes, 0.0)
	stockout_cost_list = ensure_list_for_nodes(stockout_cost, num_nodes, 0.0)
	order_lead_time_list = ensure_list_for_nodes(order_lead_time, num_nodes, 0)
	shipment_lead_time_list = ensure_list_for_nodes(shipment_lead_time, num_nodes, 0)
	demand_type_list = ensure_list_for_nodes(demand_type, num_nodes, None)
	demand_mean_list = ensure_list_for_nodes(demand_mean, num_nodes, None)
	demand_standard_deviation_list = ensure_list_for_nodes(demand_standard_deviation, num_nodes, None)
	demand_lo_list = ensure_list_for_nodes(demand_lo, num_nodes, None)
	demand_hi_list = ensure_list_for_nodes(demand_hi, num_nodes, None)
#	demands_list = ensure_list_for_time_periods(demands, num_nodes, None)
	demand_probabilities_list = ensure_list_for_nodes(demand_probabilities, num_nodes, None)
	initial_IL_list = ensure_list_for_nodes(initial_IL, num_nodes, None)
	initial_orders_list = ensure_list_for_nodes(initial_orders, num_nodes, None)
	initial_shipments_list = ensure_list_for_nodes(initial_shipments, num_nodes, None)
	supply_type_list = ensure_list_for_nodes(supply_type, num_nodes, None)
	inventory_policy_type_list = ensure_list_for_nodes(inventory_policy_type, num_nodes, None)
	local_base_stock_levels_list = ensure_list_for_nodes(local_base_stock_levels, num_nodes, None)
	echelon_base_stock_levels_list = ensure_list_for_nodes(echelon_base_stock_levels, num_nodes, None)
	reorder_points_list = ensure_list_for_nodes(reorder_points, num_nodes, None)
	order_quantities_list = ensure_list_for_nodes(order_quantities, num_nodes, None)
	order_up_to_levels_list = ensure_list_for_nodes(order_up_to_levels, num_nodes, None)

	# Check that valid demand info has been provided.
	if demand_type_list[0] is None or demand_type_list[0] == DemandType.NONE:
		raise ValueError("Valid demand_type has not been provided")
	elif demand_type_list[0] == DemandType.NORMAL and (demand_mean_list[0] is None or demand_standard_deviation_list[0] is None):
		raise ValueError("Demand type was specified as normal but mean and/or SD were not provided")
	elif (demand_type_list[0] == DemandType.UNIFORM_DISCRETE or
		  demand_type_list[0] == DemandType.UNIFORM_CONTINUOUS) and \
		(demand_lo_list[0] is None or demand_hi_list[0] is None):
		raise ValueError("Demand type was specified as uniform but lo and/or hi were not provided")
	elif demand_type_list[0] == DemandType.DETERMINISTIC and demands is None:
		raise ValueError("Demand type was specified as deterministic but demands were not provided")
	elif demand_type_list[0] == DemandType.DISCRETE_EXPLICIT and (demands is None or demand_probabilities_list is None):
		raise ValueError("Demand type was specified as discrete explicit but demands and/or probabilities were not provided")

	# Check that valid inventory policy has been provided.
	for n_index in range(num_nodes):
		# Check parameters for inventory policy type.
		if inventory_policy_type_list[n_index] is None:
			raise ValueError("Valid inventory_policy_type has not been provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.BASE_STOCK \
			and local_base_stock_levels_list[n_index] is None:
			raise ValueError("Policy type was specified as base-stock but base-stock level was not provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.r_Q \
			and (reorder_points_list[n_index] is None or order_quantities_list[n_index] is None):
			raise ValueError("Policy type was specified as (r,Q) but reorder point and/or order quantity were not "
							 "provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.s_S \
			and (reorder_points_list[n_index] is None or order_up_to_levels_list[n_index] is None):
			raise ValueError("Policy type was specified as (s,S) but reorder point and/or order-up-to level were not "
							 "provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.FIXED_QUANTITY \
			and order_quantities_list[n_index] is None:
			raise ValueError("Policy type was specified as fixed-quantity but order quantity was not provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.ECHELON_BASE_STOCK \
			and echelon_base_stock_levels[n_index] is None:
			raise ValueError("Policy type was specified as echelon base-stock but echelon base-stock level was not "
							 "provided")

	# TODO: I don't think the indexing is right for the parameters.
	# Build network, in order from downstream to upstream.
	network = SupplyChainNetwork()
	for n in range(num_nodes):

		# Create node. (n is the position of the node, 0..num_nodes-1, with 0
		# as the downstream-most node. indices[n] is the label of node n.)
		node = SupplyChainNode(index=indices[n])

		# Set parameters.

		# Set costs and lead times.
		node.local_holding_cost = local_holding_cost_list[n]
		node.echelon_holding_cost = echelon_holding_cost_list[n]
		node.stockout_cost = stockout_cost_list[n]
#		node.lead_time = shipment_lead_time_list[n]
		node.shipment_lead_time = shipment_lead_time_list[n]
		node.order_lead_time = order_lead_time_list[n]

		# Build and set demand source.
		demand_source_factory = DemandSourceFactory()
		demand_type = demand_type_list[n]
		if n == 0:
			demand_source = demand_source_factory.build_demand_source(demand_type)
			if demand_type == DemandType.NORMAL:
				demand_source.mean = demand_mean_list[n]
				demand_source.standard_deviation = demand_standard_deviation_list[n]
			elif demand_type in (DemandType.UNIFORM_CONTINUOUS, DemandType.UNIFORM_DISCRETE):
				demand_source.lo = demand_lo_list[n]
				demand_source.hi = demand_hi_list[n]
			elif demand_type == DemandType.DETERMINISTIC:
				demand_source.demands = demands[n]
			elif demand_type == DemandType.DISCRETE_EXPLICIT:
				demand_source.demands = demands[n]
				demand_source.probabilities = demand_probabilities_list[n]
		else:
			demand_source = demand_source_factory.build_demand_source(DemandType.NONE)
		node.demand_source = demand_source

		# Set initial quantities.
		node.initial_inventory_level = initial_IL_list[n]
		node.initial_orders = initial_orders_list[n]
		node.initial_shipments = initial_shipments_list[n]

		# Set inventory policy.
		policy_factory = PolicyFactory()
		if inventory_policy_type_list[n] == InventoryPolicyType.BASE_STOCK:
			policy = policy_factory.build_policy(InventoryPolicyType.BASE_STOCK,
												 base_stock_level=local_base_stock_levels_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.r_Q:
			policy = policy_factory.build_policy(InventoryPolicyType.r_Q,
												 reorder_point=reorder_points_list[n],
												 order_quantity=order_quantities_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.s_S:
			policy = policy_factory.build_policy(InventoryPolicyType.s_S,
												 reorder_point=reorder_points_list[n],
												 order_up_to_level=order_up_to_levels_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.FIXED_QUANTITY:
			policy = policy_factory.build_policy(InventoryPolicyType.FIXED_QUANTITY,
												 order_quantity=order_quantities_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.ECHELON_BASE_STOCK:
			policy = policy_factory.build_policy(InventoryPolicyType.ECHELON_BASE_STOCK,
												 echelon_base_stock_level=echelon_base_stock_levels_list[n])
		else:
			policy = None
		node.inventory_policy = policy

		# Set supply type.
		if n == num_nodes-1:
			node.supply_type = SupplyType.UNLIMITED
		else:
			node.supply_type = SupplyType.NONE

		# Add node to network.
		if n == 0:
			network.add_node(node)
		else:
			network.add_predecessor(network.get_node_from_index(prev_node), node)
		prev_node = node.index

	return network


def mwor_system(num_retailers, node_indices=None, downstream_0=True,
				  local_holding_cost=None, echelon_holding_cost=None,
				  stockout_cost=None, order_lead_time=None,
				  shipment_lead_time=None, demand_type=None, demand_mean=None,
				  demand_standard_deviation=None, demand_lo=None, demand_hi=None,
				  demands=None, demand_probabilities=None, initial_IL=None,
				  initial_orders=None, initial_shipments=None, supply_type=None,
				  inventory_policy_type=None, local_base_stock_levels=None,
				  echelon_base_stock_levels=None,
				  reorder_points=None, order_quantities=None,
				  order_up_to_levels=None):
	"""Generate multiple-warehouse, one-retailer (MWOR) (i.e., 2-echelon assembly)
	system with specified number of retailers.

	Other than ``num_nodes``, all parameters are optional. If they are provided,
	they must be either a dict, a list, or a singleton, with the following
	requirements:
		- If ``node_indices`` is provided, then the parameter may be specified
		either as a dict (with keys equal to the indices in ``node_indices``)
		or as a singleton (in which case all nodes will have that parameter
		set to the singleton value).
		- If ``node_indices`` is not provided, then the parameter may be
		specified either as a dict (with keys equal to 0,...,``num_nodes``-1),
		as a list, or as a singleton (in which case all nodes will have that
		parameter set to the singleton value). If the parameter is specified as
		a dict or list, then the keys or list indices must correspond to the
		actual indexing of the nodes; that is, if ``downstream_0`` is ``True``,
		then key/index ``0`` should refer to the downstream-most node, and if
		``downstream_0`` is ``False``, then the largest key/index should refer
		to the downstream-most node.

	Parameters
	----------
	num_retailers : int
		Number of nodes in MWOR system.
	node_indices : list, optional
		List of node indices, with the single downstream node listed first.
	downstream_0 : bool, optional
		If True, node 0 is the single downstream node; if False, node
		``num_retailers`` is the single downstream node. Ignored if
		``node_labels`` is provided.
	local_holding_cost
	echelon_holding_cost
	stockout_cost
	order_lead_time
	shipment_lead_time
	demand_type
	demand_mean
	demand_standard_deviation
	demand_lo
	demand_hi
	demands
	initial_IL
	initial_orders
	initial_shipments
	supply_type
	inventory_policy_type
	local_base_stock_levels
	echelon_base_stock_levels
	reorder_points
	order_quantities
	order_up_to_levels

	Returns
	-------
	network : SupplyChainNetwork
		The MWOR network, with parameters filled.

	# TODO: if initial_IL not provided, default to BS levels
	"""

	# Calculate total # of nodes (= # retailers + 1)
	num_nodes = num_retailers + 1

	# Build list of node indices.
	if node_indices is not None:
		indices = node_indices
	elif downstream_0:
		indices = list(range(num_nodes))
	else:
		indices = list(range(num_nodes-1, -1, -1))

	# Build vectors of attributes.
	local_holding_cost_list = ensure_list_for_nodes(local_holding_cost, num_nodes, 0.0)
	echelon_holding_cost_list = ensure_list_for_nodes(echelon_holding_cost, num_nodes, 0.0)
	stockout_cost_list = ensure_list_for_nodes(stockout_cost, num_nodes, 0.0)
	order_lead_time_list = ensure_list_for_nodes(order_lead_time, num_nodes, 0)
	shipment_lead_time_list = ensure_list_for_nodes(shipment_lead_time, num_nodes, 0)
	demand_type_list = ensure_list_for_nodes(demand_type, num_nodes, None)
	demand_mean_list = ensure_list_for_nodes(demand_mean, num_nodes, None)
	demand_standard_deviation_list = ensure_list_for_nodes(demand_standard_deviation, num_nodes, None)
	demand_lo_list = ensure_list_for_nodes(demand_lo, num_nodes, None)
	demand_hi_list = ensure_list_for_nodes(demand_hi, num_nodes, None)
#	demands_list = ensure_list_for_time_periods(demands, num_nodes, None)
	demand_probabilities_list = ensure_list_for_nodes(demand_probabilities, num_nodes, None)
	initial_IL_list = ensure_list_for_nodes(initial_IL, num_nodes, None)
	initial_orders_list = ensure_list_for_nodes(initial_orders, num_nodes, None)
	initial_shipments_list = ensure_list_for_nodes(initial_shipments, num_nodes, None)
	supply_type_list = ensure_list_for_nodes(supply_type, num_nodes, None)
	inventory_policy_type_list = ensure_list_for_nodes(inventory_policy_type, num_nodes, None)
	local_base_stock_levels_list = ensure_list_for_nodes(local_base_stock_levels, num_nodes, None)
	echelon_base_stock_levels_list = ensure_list_for_nodes(echelon_base_stock_levels, num_nodes, None)
	reorder_points_list = ensure_list_for_nodes(reorder_points, num_nodes, None)
	order_quantities_list = ensure_list_for_nodes(order_quantities, num_nodes, None)
	order_up_to_levels_list = ensure_list_for_nodes(order_up_to_levels, num_nodes, None)

	# TODO: write separate functions to do these type/input checks
	# Check that valid demand info has been provided.
	if demand_type_list[0] is None or demand_type_list[0] == DemandType.NONE:
		raise ValueError("Valid demand_type has not been provided")
	elif demand_type_list[0] == DemandType.NORMAL and (demand_mean_list[0] is None or demand_standard_deviation_list[0] is None):
		raise ValueError("Demand type was specified as normal but mean and/or SD were not provided")
	elif (demand_type_list[0] == DemandType.UNIFORM_DISCRETE or
		  demand_type_list[0] == DemandType.UNIFORM_CONTINUOUS) and \
		(demand_lo_list[0] is None or demand_hi_list[0] is None):
		raise ValueError("Demand type was specified as uniform but lo and/or hi were not provided")
	elif demand_type_list[0] == DemandType.DETERMINISTIC and demands is None:
		raise ValueError("Demand type was specified as deterministic but demands were not provided")
	elif demand_type_list[0] == DemandType.DISCRETE_EXPLICIT and (demands is None or demand_probabilities_list is None):
		raise ValueError("Demand type was specified as discrete explicit but demands and/or probabilities were not provided")

	# Check that valid inventory policy has been provided.
	for n_index in range(num_nodes):
		# Check parameters for inventory policy type.
		if inventory_policy_type_list[n_index] is None:
			raise ValueError("Valid inventory_policy_type has not been provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.BASE_STOCK \
			and local_base_stock_levels_list[n_index] is None:
			raise ValueError("Policy type was specified as base-stock but base-stock level was not provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.r_Q \
			and (reorder_points_list[n_index] is None or order_quantities_list[n_index] is None):
			raise ValueError("Policy type was specified as (r,Q) but reorder point and/or order quantity were not "
							 "provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.s_S \
			and (reorder_points_list[n_index] is None or order_up_to_levels_list[n_index] is None):
			raise ValueError("Policy type was specified as (s,S) but reorder point and/or order-up-to level were not "
							 "provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.FIXED_QUANTITY \
			and order_quantities_list[n_index] is None:
			raise ValueError("Policy type was specified as fixed-quantity but order quantity was not provided")
		elif inventory_policy_type_list[n_index] == InventoryPolicyType.ECHELON_BASE_STOCK \
			and echelon_base_stock_levels[n_index] is None:
			raise ValueError("Policy type was specified as echelon base-stock but echelon base-stock level was not "
							 "provided")

	# TODO: I don't think the indexing is right for the parameters.
	# Build network, in order from downstream to upstream.
	network = SupplyChainNetwork()
	for n in range(num_nodes):

		# Create node. (n is the position of the node, 0..num_nodes-1, with 0
		# as the downstream-most node. indices[n] is the label of node n.)
		node = SupplyChainNode(index=indices[n])

		# Set parameters.

		# Set costs and lead times.
		node.local_holding_cost = local_holding_cost_list[n]
		node.echelon_holding_cost = echelon_holding_cost_list[n]
		node.stockout_cost = stockout_cost_list[n]
#		node.lead_time = shipment_lead_time_list[n]
		node.shipment_lead_time = shipment_lead_time_list[n]
		node.order_lead_time = order_lead_time_list[n]

		# Build and set demand source.
		demand_source_factory = DemandSourceFactory()
		demand_type = demand_type_list[n]
		if n == 0:
			demand_source = demand_source_factory.build_demand_source(demand_type)
			if demand_type == DemandType.NORMAL:
				demand_source.mean = demand_mean_list[n]
				demand_source.standard_deviation = demand_standard_deviation_list[n]
			elif demand_type in (DemandType.UNIFORM_CONTINUOUS, DemandType.UNIFORM_DISCRETE):
				demand_source.lo = demand_lo_list[n]
				demand_source.hi = demand_hi_list[n]
			elif demand_type == DemandType.DETERMINISTIC:
				demand_source.demands = demands[n]
			elif demand_type == DemandType.DISCRETE_EXPLICIT:
				demand_source.demands = demands[n]
				demand_source.probabilities = demand_probabilities_list[n]
		else:
			demand_source = demand_source_factory.build_demand_source(DemandType.NONE)
		node.demand_source = demand_source

		# Set initial quantities.
		node.initial_inventory_level = initial_IL_list[n]
		node.initial_orders = initial_orders_list[n]
		node.initial_shipments = initial_shipments_list[n]

		# Set inventory policy.
		policy_factory = PolicyFactory()
		if inventory_policy_type_list[n] == InventoryPolicyType.BASE_STOCK:
			policy = policy_factory.build_policy(InventoryPolicyType.BASE_STOCK,
												 base_stock_level=local_base_stock_levels_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.r_Q:
			policy = policy_factory.build_policy(InventoryPolicyType.r_Q,
												 reorder_point=reorder_points_list[n],
												 order_quantity=order_quantities_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.s_S:
			policy = policy_factory.build_policy(InventoryPolicyType.s_S,
												 reorder_point=reorder_points_list[n],
												 order_up_to_level=order_up_to_levels_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.FIXED_QUANTITY:
			policy = policy_factory.build_policy(InventoryPolicyType.FIXED_QUANTITY,
												 order_quantity=order_quantities_list[n])
		elif inventory_policy_type_list[n] == InventoryPolicyType.ECHELON_BASE_STOCK:
			policy = policy_factory.build_policy(InventoryPolicyType.ECHELON_BASE_STOCK,
												 echelon_base_stock_level=echelon_base_stock_levels_list[n])
		else:
			policy = None
		node.inventory_policy = policy

		# Set supply type.
		if n == num_nodes-1:
			node.supply_type = SupplyType.UNLIMITED
		else:
			node.supply_type = SupplyType.NONE

		# Add node to network.
		if n == 0:
			network.add_node(node)
			retailer_node = node
		else:
			network.add_predecessor(retailer_node, node)

	return network
