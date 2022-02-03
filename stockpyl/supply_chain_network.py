# ===============================================================================
# stockpyl - SupplyChainNetwork Class
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

import networkx as nx
import json

#import supply_chain_node
from stockpyl.demand_source import *
from stockpyl.supply_chain_node import *
from stockpyl.policy import *
from stockpyl.helpers import *


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
		return [node for node in self.nodes if node.predecessor_indices() == []]

	@property
	def sink_nodes(self):
		"""List of all sink nodes, i.e., all nodes that have no successors.
		"""
		return [node for node in self.nodes if node.successor_indices() == []]

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

	def reindex_nodes(self, old_to_new_dict, new_names=None):
		"""Change indices of the nodes in the network using ``old_to_new_dict``.

		Parameters
		----------
		old_to_new_dict : dict
			Dict in which keys are old indices and values are new indices.
		new_names : dict, optional
			Dict in which keys are old indices and values are new names.

		"""
		# Reindex nodes in network.
		for node in self.nodes:
			# Reindex node.
			old_index = node.index
			node.index = old_to_new_dict[old_index]
			# Rename node.
			if new_names is not None:
				node.name = new_names[old_index]
			# Reindex node's state variables.
			node.reindex_all_state_variables(old_to_new_dict)

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
			for p in n.predecessors():
				digraph.add_edge(p.index, n.index)

		return digraph


# ===============================================================================
# Network-Creation Methods
# ===============================================================================

def network_from_edges(edges, node_indices=None, local_holding_cost=None, echelon_holding_cost=None,
					   stockout_cost=None, revenue=None, order_lead_time=None,
					   shipment_lead_time=None, demand_type=None, demand_mean=None,
					   demand_standard_deviation=None, demand_lo=None, demand_hi=None,
					   demand_list=None, probabilities=None, initial_IL=None,
					   initial_orders=None, initial_shipments=None, supply_type=None,
					   inventory_policy_type=None, base_stock_levels=None,
					   reorder_points=None, order_quantities=None,
					   order_up_to_levels=None):
	"""Construct supply chain network with the specified edges.

	Other than ``edges``, all parameters are optional. If they are provided,
	they must be either a dict, a list, or a singleton, with the following
	requirements:
		- If ``node_indices`` is provided, then the parameter may be specified
		either as a dict (with keys equal to the indices in ``node_indices``),
		as a list (whose items are in the same order as ``node_indices``),
		or as a singleton (in which case all nodes will have that parameter
		set to the singleton value).
		- If ``node_indices`` is not provided, then the parameter may be
		specified either as a dict (with keys equal to 0,...,``num_nodes``-1) or
		as a singleton (in which case all nodes will have that
		parameter set to the singleton value). (It cannot be a list.)

	A node's supply type is set to UNLIMITED if it has no predecessors;
	otherwise, its supply type is set to NONE.

	# TODO: allow names instead of indices?

	Parameters
	----------
	edges : list
		List of edges, with each edge specified as a tuple ``(a, b)`` with the
		predecessor node given by ``a`` and the successor node given by ``b``.
	node_indices : list, optional
		List of node indices. These should be the same as the node indices that
		are contained in the edges in ``edges``. The reason to include
		``node_indices`` is to specify the order of nodes if the costs or other
		parameters are provided as lists.
	local_holding_cost
	echelon_holding_cost
	stockout_cost
	revenue
	order_lead_time
	shipment_lead_time
	type # TODO: allow string representation
	demand_mean
	demand_standard_deviation
	demand_lo
	demand_hi
	demand_list
	initial_IL
	initial_orders
	initial_shipments
	inventory_policy_type
	base_stock_levels
	reorder_points
	order_quantities
	order_up_to_levels

	Returns
	-------
	network : SupplyChainNetwork
		The supply chain network, with parameters filled.

	# TODO: if initial_IL not provided, default to BS levels

	# TODO: unit tests
	"""
	# Create network.
	network = SupplyChainNetwork()

	# Add nodes.
	for e in edges:
		if e[0] not in network.node_indices:
			network.add_node(SupplyChainNode(e[0]))
		if e[1] not in network.node_indices:
			network.add_node(SupplyChainNode(e[1]))
	num_nodes = len(network.nodes)

	# Check node_indices; if not provided, build it.
	if node_indices is None:
		# TODO: is this right??
		node_indices = network.node_indices
	else:
		if set(node_indices) != set(network.node_indices):
			raise(ValueError, "node_indices list does not match nodes contained in edge list")

	# Add edges.
	for e in edges:
		source = network.get_node_from_index(e[0])
		sink = network.get_node_from_index(e[1])
		network.add_successor(source, sink)

	# Build vectors of attributes.
	local_holding_cost_list = ensure_dict_for_nodes(local_holding_cost, node_indices, None)
	echelon_holding_cost_list = ensure_dict_for_nodes(echelon_holding_cost, node_indices, None)
	stockout_cost_list = ensure_dict_for_nodes(stockout_cost, node_indices, None)
	revenue_list = ensure_dict_for_nodes(revenue, node_indices, None)
	order_lead_time_list = ensure_dict_for_nodes(order_lead_time, node_indices, None)
	shipment_lead_time_list = ensure_dict_for_nodes(shipment_lead_time, node_indices, None)
	demand_type_list = ensure_dict_for_nodes(demand_type, node_indices, None)
	demand_mean_list = ensure_dict_for_nodes(demand_mean, node_indices, None)
	demand_standard_deviation_list = ensure_dict_for_nodes(demand_standard_deviation, node_indices, None)
	demand_lo_list = ensure_dict_for_nodes(demand_lo, node_indices, None)
	demand_hi_list = ensure_dict_for_nodes(demand_hi, node_indices, None)
#	demands_list = ensure_list_for_time_periods(demand_list, node_indices, None)
	probabilities_list = ensure_dict_for_nodes(probabilities, node_indices, None)
	initial_IL_list = ensure_dict_for_nodes(initial_IL, node_indices, None)
	initial_orders_list = ensure_dict_for_nodes(initial_orders, node_indices, None)
	initial_shipments_list = ensure_dict_for_nodes(initial_shipments, node_indices, None)
	supply_type_list = ensure_dict_for_nodes(supply_type, node_indices, None)
	inventory_policy_type_list = ensure_dict_for_nodes(inventory_policy_type, node_indices, None)
	base_stock_levels_list = ensure_dict_for_nodes(base_stock_levels, node_indices, None)
	reorder_points_list = ensure_dict_for_nodes(reorder_points, node_indices, None)
	order_quantities_list = ensure_dict_for_nodes(order_quantities, node_indices, None)
	order_up_to_levels_list = ensure_dict_for_nodes(order_up_to_levels, node_indices, None)

	# Check that valid demand info has been provided.
	for n in network.nodes:
		if demand_type_list[n.index] == 'N' and (demand_mean_list[n.index] is None or demand_standard_deviation_list[n.index] is None):
			raise ValueError("Demand type was specified as normal but mean and/or SD were not provided")
		elif (demand_type_list[n.index] == 'UD' or
			  demand_type_list[n.index] == 'UC') and \
			(demand_lo_list[n.index] is None or demand_hi_list[n.index] is None):
			raise ValueError("Demand type was specified as uniform but lo and/or hi were not provided")
		elif demand_type_list[n.index] == 'D' and demand_list is None:
			raise ValueError("Demand type was specified as deterministic but demand_list were not provided")
		elif demand_type_list[n.index] == 'CD' and (demand_list is None or probabilities_list is None):
			raise ValueError("Demand type was specified as discrete explicit but demand_list and/or probabilities were not provided")

	# Check that valid inventory policy has been provided.
	for n in network.nodes:
		# Check parameters for inventory policy type.
		if inventory_policy_type_list[n.index] is None:
			raise ValueError("Valid inventory_policy_type has not been provided")
		elif inventory_policy_type_list[n.index] in ('BS', 'EBS', 'BEBS') and base_stock_levels_list[n.index] is None:
			raise ValueError("Policy type was specified as base-stock but base-stock level was not provided")
		elif inventory_policy_type_list[n.index] == 'rQ' \
			and (reorder_points_list[n.index] is None or order_quantities_list[n.index] is None):
			raise ValueError("Policy type was specified as (r,Q) but reorder point and/or order quantity were not "
							 "provided")
		elif inventory_policy_type_list[n.index] == 'sS' \
			and (reorder_points_list[n.index] is None or order_up_to_levels_list[n.index] is None):
			raise ValueError("Policy type was specified as (s,S) but reorder point and/or order-up-to level were not "
							 "provided")
		elif inventory_policy_type_list[n.index] == 'FQ' \
			and order_quantities_list[n.index] is None:
			raise ValueError("Policy type was specified as fixed-quantity but order quantity was not provided")

	# Set parameters.
	for n in network.nodes:

		# Set costs and lead times.
		n.local_holding_cost = local_holding_cost_list[n.index]
		n.echelon_holding_cost = echelon_holding_cost_list[n.index]
		n.stockout_cost = stockout_cost_list[n.index]
		n.revenue = revenue_list[n.index]
#		node.lead_time = shipment_lead_time_list[n]
		n.shipment_lead_time = shipment_lead_time_list[n.index]
		n.order_lead_time = order_lead_time_list[n.index]

		# Build and set demand source.
		demand_source = DemandSource()
		demand_type = demand_type_list[n.index]
		demand_source.type = demand_type
		if demand_type == 'N':
			demand_source.mean = demand_mean_list[n.index]
			demand_source.standard_deviation = demand_standard_deviation_list[n.index]
		elif demand_type in ('UC', 'UD'):
			demand_source.lo = demand_lo_list[n.index]
			demand_source.hi = demand_hi_list[n.index]
		elif demand_type == 'D':
			demand_source.demand_list = demand_list[n.index]
		elif demand_type == 'CD':
			demand_source.demand_list = demand_list[n.index]
			demand_source.probabilities = probabilities_list[n.index]
		n.demand_source = demand_source

		# Set initial quantities.
		n.initial_inventory_level = initial_IL_list[n.index]
		n.initial_orders = initial_orders_list[n.index]
		n.initial_shipments = initial_shipments_list[n.index]

		# Set inventory policy.
		n.inventory_policy.type = inventory_policy_type_list[n.index]
		if inventory_policy_type_list[n.index] in ('BS', 'EBS', 'BEBS'):
			n.inventory_policy.base_stock_level = base_stock_levels_list[n.index]
		elif inventory_policy_type_list[n.index] == 'rQ':
			n.inventory_policy.reorder_point = reorder_points_list[n.index]
			n.inventory_policy.order_quantity = order_quantities_list[n.index]
		elif inventory_policy_type_list[n.index] == 'sS':
			n.inventory_policy.reorder_point = reorder_points_list[n.index]
			n.inventory_policy.order_up_to_level = order_up_to_levels_list[n.index]
		elif inventory_policy_type_list[n.index] == 'FQ':
			n.inventory_policy.order_quantity=order_quantities_list[n.index]

		# Set supply type.
		if len(n.predecessors()) == 0:
			n.supply_type = 'U'
		else:
			n.supply_type = None

	return network


# ===============================================================================
# Methods to Create Specific Network Structures
# ===============================================================================

def single_stage(holding_cost=0, stockout_cost=0, revenue=0, order_lead_time=0,
				 shipment_lead_time=0, demand_type=None, demand_mean=0,
				 demand_standard_deviation=0, demand_lo=0, demand_hi=0,
				 demand_list=None, probabilities=None, initial_IL=0,
				 initial_orders=0, initial_shipments=0, supply_type=None,
				 inventory_policy_type=None, base_stock_level=None,
				 reorder_point=None, order_quantity=None,
				 order_up_to_level=None):
	"""Generate single-stage system.

	All parameters are optional.

	Parameters
	----------
	holding_cost
	holding_cost
	stockout_cost
	revenue
	order_lead_time
	shipment_lead_time
	demand_type
	demand_mean
	demand_standard_deviation
	demand_lo
	demand_hi
	demand_list
	initial_IL
	initial_orders
	initial_shipments
	supply_type
	inventory_policy_type
	base_stock_level
	reorder_point
	order_quantity
	order_up_to_level

	Returns
	-------
	network : SupplyChainNetwork
		The single-stage network, with parameters filled.

	# TODO: if initial_IL not provided, default to BS levels
	"""

	# Check that valid demand info has been provided.
	if demand_type == 'N' and (demand_mean is None or demand_standard_deviation is None):
		raise ValueError("Demand type was specified as normal but mean and/or SD were not provided")
	elif (demand_type == 'UD' or
		  demand_type == 'UC') and \
		(demand_lo is None or demand_hi is None):
		raise ValueError("Demand type was specified as uniform but lo and/or hi were not provided")
	elif demand_type == 'D' and demand_list is None:
		raise ValueError("Demand type was specified as deterministic but demand_list were not provided")
	elif demand_type == 'CD' and (demand_list is None or probabilities is None):
		raise ValueError("Demand type was specified as discrete explicit but demand_list and/or probabilities were not provided")

	# Check that valid inventory policy has been provided.
	if inventory_policy_type is None:
		raise ValueError("Valid inventory_policy_type has not been provided")
	elif inventory_policy_type in ('BS', 'EBS', 'BEBS') \
		and base_stock_level is None:
		raise ValueError("Policy type was specified as base-stock but base-stock level was not provided")
	elif inventory_policy_type == 'rQ' \
		and (reorder_point is None or order_quantity is None):
		raise ValueError("Policy type was specified as (r,Q) but reorder point and/or order quantity were not "
						 "provided")
	elif inventory_policy_type == 'sS' \
		and (reorder_point is None or order_up_to_level is None):
		raise ValueError("Policy type was specified as (s,S) but reorder point and/or order-up-to level were not "
						 "provided")
	elif inventory_policy_type == 'FQ' \
		and order_quantity is None:
		raise ValueError("Policy type was specified as fixed-quantity but order quantity was not provided")

	# Build network.
	network = SupplyChainNetwork()

	# Create node.
	node = SupplyChainNode(index=0)

	# Set parameters.

	# Set costs and lead times.
	node.local_holding_cost = holding_cost
	node.echelon_holding_cost = holding_cost
	node.stockout_cost = stockout_cost
	node.revenue = revenue
#		node.lead_time = shipment_lead_time
	node.shipment_lead_time = shipment_lead_time
	node.order_lead_time = order_lead_time

	# Build and set demand source.
	demand_type = demand_type
	demand_source = DemandSource()
	demand_source.type = demand_type
	if demand_type == 'N':
		demand_source.mean = demand_mean
		demand_source.standard_deviation = demand_standard_deviation
	elif demand_type in ('UC', 'UD'):
		demand_source.lo = demand_lo
		demand_source.hi = demand_hi
	elif demand_type == 'D':
		demand_source.demand_list = demand_list
	elif demand_type == 'CD':
		demand_source.demand_list = demand_list
		demand_source.probabilities = probabilities
	node.demand_source = demand_source

	# Set initial quantities.
	node.initial_inventory_level = initial_IL
	node.initial_orders = initial_orders
	node.initial_shipments = initial_shipments

	# Set inventory policy.
	node.inventory_policy.type = inventory_policy_type
	if inventory_policy_type in ('BS', 'EBS', 'BEBS'):
		node.inventory_policy.base_stock_level = base_stock_level
	elif inventory_policy_type == 'rQ':
		node.inventory_policy.reorder_point = reorder_point
		node.inventory_policy.order_quantity = order_quantity
	elif inventory_policy_type == 'sS':
		node.inventory_policy.reorder_point = reorder_point
		node.inventory_policy.order_up_to_level = order_up_to_level
	elif inventory_policy_type == 'FQ':
		node.inventory_policy.order_quantity = order_quantity

	# Set supply type.
	node.supply_type = 'U'

	# Add node to network.
	network.add_node(node)

	return network


def serial_system(num_nodes, node_indices=None, downstream_0=True,
				  local_holding_cost=None, echelon_holding_cost=None,
				  stockout_cost=None, revenue=None, order_lead_time=None,
				  shipment_lead_time=None, demand_type=None, demand_mean=None,
				  demand_standard_deviation=None, demand_lo=None, demand_hi=None,
				  demand_list=None, probabilities=None, initial_IL=None,
				  initial_orders=None, initial_shipments=None, supply_type=None,
				  inventory_policy_type=None, base_stock_levels=None,
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
	revenue
	order_lead_time
	shipment_lead_time
	demand_type
	demand_mean
	demand_standard_deviation
	demand_lo
	demand_hi
	demand_list
	initial_IL
	initial_orders
	initial_shipments
	supply_type
	inventory_policy_type
	base_stock_levels
	reorder_points
	order_quantities
	order_up_to_levels

	Returns
	-------
	network : SupplyChainNetwork
		The serial system network, with parameters filled.

	# TODO: if initial_IL not provided, default to BS levels
	"""

	# Build list of node indices.
	if node_indices is not None:
		indices = node_indices
		downstream_node = node_indices[0]
	elif downstream_0:
		indices = list(range(num_nodes))
		downstream_node = 0
	else:
		indices = list(range(num_nodes-1, -1, -1))
		downstream_node = num_nodes-1

	# Build dicts of attributes.
	local_holding_cost_dict = ensure_dict_for_nodes(local_holding_cost, indices, None)
	echelon_holding_cost_dict = ensure_dict_for_nodes(echelon_holding_cost, indices, None)
	stockout_cost_dict = ensure_dict_for_nodes(stockout_cost, indices, None)
	revenue_dict = ensure_dict_for_nodes(revenue, indices, None)
	order_lead_time_dict = ensure_dict_for_nodes(order_lead_time, indices, None)
	shipment_lead_time_dict = ensure_dict_for_nodes(shipment_lead_time, indices, None)
	demand_type_dict = ensure_dict_for_nodes(demand_type, indices, None)
	demand_mean_dict = ensure_dict_for_nodes(demand_mean, indices, None)
	demand_standard_deviation_dict = ensure_dict_for_nodes(demand_standard_deviation, indices, None)
	demand_lo_dict = ensure_dict_for_nodes(demand_lo, indices, None)
	demand_hi_dict = ensure_dict_for_nodes(demand_hi, indices, None)
#	demands_dict = ensure_dict_for_time_periods(demand_list, indices, None)
	probabilities_dict = ensure_dict_for_nodes(probabilities, indices, None)
	initial_IL_dict = ensure_dict_for_nodes(initial_IL, indices, None)
	initial_orders_dict = ensure_dict_for_nodes(initial_orders, indices, None)
	initial_shipments_dict = ensure_dict_for_nodes(initial_shipments, indices, None)
	supply_type_dict = ensure_dict_for_nodes(supply_type, indices, None)
	inventory_policy_type_dict = ensure_dict_for_nodes(inventory_policy_type, indices, None)
	base_stock_levels_dict = ensure_dict_for_nodes(base_stock_levels, indices, None)
	reorder_points_dict = ensure_dict_for_nodes(reorder_points, indices, None)
	order_quantities_dict = ensure_dict_for_nodes(order_quantities, indices, None)
	order_up_to_levels_dict = ensure_dict_for_nodes(order_up_to_levels, indices, None)

	# Check that valid demand info has been provided.
	if demand_type_dict[downstream_node] is None:
		raise ValueError("Valid type has not been provided")
	elif demand_type_dict[downstream_node] == 'N' and (demand_mean_dict[downstream_node] is None or demand_standard_deviation_dict[downstream_node] is None):
		raise ValueError("Demand type was specified as normal but mean and/or SD were not provided")
	elif (demand_type_dict[downstream_node] == 'UD' or
		  demand_type_dict[downstream_node] == 'UC') and \
		(demand_lo_dict[downstream_node] is None or demand_hi_dict[downstream_node] is None):
		raise ValueError("Demand type was specified as uniform but lo and/or hi were not provided")
	elif demand_type_dict[downstream_node] == 'D' and demand_list is None:
		raise ValueError("Demand type was specified as deterministic but demand_list were not provided")
	elif demand_type_dict[downstream_node] == 'CD' and (demand_list is None or probabilities_dict is None):
		raise ValueError("Demand type was specified as discrete explicit but demand_list and/or probabilities were not provided")

	# Check that valid inventory policy has been provided.
	for n_index in indices:
		# Check parameters for inventory policy type.
		if inventory_policy_type_dict[n_index] is None:
			raise ValueError("Valid inventory_policy_type has not been provided")
		elif inventory_policy_type_dict[n_index] in ('BS', 'EBS', 'BEBS') \
			and base_stock_levels_dict[n_index] is None:
			raise ValueError("Policy type was specified as base-stock but base-stock level was not provided")
		elif inventory_policy_type_dict[n_index] == 'rQ' \
			and (reorder_points_dict[n_index] is None or order_quantities_dict[n_index] is None):
			raise ValueError("Policy type was specified as (r,Q) but reorder point and/or order quantity were not "
							 "provided")
		elif inventory_policy_type_dict[n_index] == 'sS' \
			and (reorder_points_dict[n_index] is None or order_up_to_levels_dict[n_index] is None):
			raise ValueError("Policy type was specified as (s,S) but reorder point and/or order-up-to level were not "
							 "provided")
		elif inventory_policy_type_dict[n_index] == 'FQ' \
			and order_quantities_dict[n_index] is None:
			raise ValueError("Policy type was specified as fixed-quantity but order quantity was not provided")

	# TODO: I don't think the indexing is right for the parameters.
	# Build network, in order from downstream to upstream.
	network = SupplyChainNetwork()
	for n in range(num_nodes):

		# Create node. (n is the position of the node, 0..num_nodes-1, with 0
		# as the downstream-most node. indices[n] is the label of node n.)
		n_ind = indices[n]
		node = SupplyChainNode(index=n_ind)

		# Set parameters.

		# Set costs and lead times.
		node.local_holding_cost = local_holding_cost_dict[n_ind]
		node.echelon_holding_cost = echelon_holding_cost_dict[n_ind]
		node.stockout_cost = stockout_cost_dict[n_ind]
		node.revenue = revenue_dict[n_ind]
#		node.lead_time = shipment_lead_time_dict[n_ind]
		node.shipment_lead_time = shipment_lead_time_dict[n_ind]
		node.order_lead_time = order_lead_time_dict[n_ind]

		# Build and set demand source.
		demand_type = demand_type_dict[n_ind]
		if n == 0:
			demand_source = DemandSource()
			demand_source.type = demand_type
			if demand_type == 'N':
				demand_source.mean = demand_mean_dict[n_ind]
				demand_source.standard_deviation = demand_standard_deviation_dict[n_ind]
			elif demand_type in ('UC', 'UD'):
				demand_source.lo = demand_lo_dict[n_ind]
				demand_source.hi = demand_hi_dict[n_ind]
			elif demand_type == 'D':
				demand_source.demand_list = demand_list[n_ind]
			elif demand_type == 'CD':
				demand_source.demand_list = demand_list[n_ind]
				demand_source.probabilities = probabilities_dict[n_ind]
		else:
			demand_source = None
		node.demand_source = demand_source

		# Set initial quantities.
		node.initial_inventory_level = initial_IL_dict[n_ind]
		node.initial_orders = initial_orders_dict[n_ind]
		node.initial_shipments = initial_shipments_dict[n_ind]

		# Set inventory policy.
		node.inventory_policy.type = inventory_policy_type_dict[n_ind]
		if inventory_policy_type_dict[n_ind] in ('BS', 'EBS', 'BEBS'):
			node.inventory_policy.base_stock_level = base_stock_levels_dict[n_ind]
		elif inventory_policy_type_dict[n_ind] == 'rQ':
			node.inventory_policy.reorder_point = reorder_points_dict[n_ind]
			node.inventory_policy.order_quantity = order_quantities_dict[n_ind]
		elif inventory_policy_type_dict[n_ind] == 'sS':
			node.inventory_policy.reorder_point = reorder_points_dict[n_ind]
			node.inventory_policy.order_up_to_level = order_up_to_levels_dict[n_ind]
		elif inventory_policy_type_dict[n_ind] == 'FQ':
			node.inventory_policy.order_quantity=order_quantities_dict[n_ind]

		# Set supply type.
		if n == num_nodes-1:
			node.supply_type = 'U'
		else:
			node.supply_type = None

		# Add node to network.
		if n == 0:
			network.add_node(node)
		else:
			network.add_predecessor(network.get_node_from_index(prev_node), node)
		prev_node = node.index

	return network


def mwor_system(num_warehouses, node_indices=None, downstream_0=True,
				local_holding_cost=None, echelon_holding_cost=None,
				stockout_cost=None, revenue=None, order_lead_time=None,
				shipment_lead_time=None, demand_type=None, demand_mean=None,
				demand_standard_deviation=None, demand_lo=None, demand_hi=None,
				demand_list=None, probabilities=None, initial_IL=None,
				initial_orders=None, initial_shipments=None, supply_type=None,
				inventory_policy_type=None, base_stock_levels=None,
				reorder_points=None, order_quantities=None,
				order_up_to_levels=None):
	"""Generate multiple-warehouse, one-retailer (MWOR) (i.e., 2-echelon assembly)
	system with specified number of warehouses.

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
	num_warehouses : int
		Number of nodes in MWOR system.
	node_indices : list, optional
		List of node indices, with the single downstream node listed first.
	downstream_0 : bool, optional
		If True, node 0 is the single downstream node; if False, node
		``num_warehouses`` is the single downstream node. Ignored if
		``node_labels`` is provided.
	local_holding_cost
	echelon_holding_cost
	stockout_cost
	revenue
	order_lead_time
	shipment_lead_time
	demand_type
	demand_mean
	demand_standard_deviation
	demand_lo
	demand_hi
	demand_list
	initial_IL
	initial_orders
	initial_shipments
	supply_type
	inventory_policy_type
	base_stock_levels
	reorder_points
	order_quantities
	order_up_to_levels

	Returns
	-------
	network : SupplyChainNetwork
		The MWOR network, with parameters filled.

	# TODO: if initial_IL not provided, default to BS levels
	"""

	# Calculate total # of nodes (= # warehouses + 1)
	num_nodes = num_warehouses + 1

	# Build list of node indices.
	if node_indices is not None:
		indices = node_indices
	elif downstream_0:
		indices = list(range(num_nodes))
	else:
		indices = list(range(num_nodes-1, -1, -1))

	# Build vectors of attributes.
	local_holding_cost_list = ensure_list_for_nodes(local_holding_cost, num_nodes, None)
	echelon_holding_cost_list = ensure_list_for_nodes(echelon_holding_cost, num_nodes, None)
	stockout_cost_list = ensure_list_for_nodes(stockout_cost, num_nodes, None)
	revenue_list = ensure_list_for_nodes(revenue, num_nodes, None)
	order_lead_time_list = ensure_list_for_nodes(order_lead_time, num_nodes, None)
	shipment_lead_time_list = ensure_list_for_nodes(shipment_lead_time, num_nodes, None)
	demand_type_list = ensure_list_for_nodes(demand_type, num_nodes, None)
	demand_mean_list = ensure_list_for_nodes(demand_mean, num_nodes, None)
	demand_standard_deviation_list = ensure_list_for_nodes(demand_standard_deviation, num_nodes, None)
	demand_lo_list = ensure_list_for_nodes(demand_lo, num_nodes, None)
	demand_hi_list = ensure_list_for_nodes(demand_hi, num_nodes, None)
#	demands_list = ensure_list_for_time_periods(demand_list, num_nodes, None)
	probabilities_list = ensure_list_for_nodes(probabilities, num_nodes, None)
	initial_IL_list = ensure_list_for_nodes(initial_IL, num_nodes, None)
	initial_orders_list = ensure_list_for_nodes(initial_orders, num_nodes, None)
	initial_shipments_list = ensure_list_for_nodes(initial_shipments, num_nodes, None)
	supply_type_list = ensure_list_for_nodes(supply_type, num_nodes, None)
	inventory_policy_type_list = ensure_list_for_nodes(inventory_policy_type, num_nodes, None)
	base_stock_levels_list = ensure_list_for_nodes(base_stock_levels, num_nodes, None)
	reorder_points_list = ensure_list_for_nodes(reorder_points, num_nodes, None)
	order_quantities_list = ensure_list_for_nodes(order_quantities, num_nodes, None)
	order_up_to_levels_list = ensure_list_for_nodes(order_up_to_levels, num_nodes, None)

	# TODO: write separate functions to do these type/input checks
	# Check that valid demand info has been provided.
	if demand_type_list[0] is None or demand_type_list[0] == None:
		raise ValueError("Valid type has not been provided")
	elif demand_type_list[0] == 'N' and (demand_mean_list[0] is None or demand_standard_deviation_list[0] is None):
		raise ValueError("Demand type was specified as normal but mean and/or SD were not provided")
	elif (demand_type_list[0] == 'UD' or
		  demand_type_list[0] == 'UC') and \
		(demand_lo_list[0] is None or demand_hi_list[0] is None):
		raise ValueError("Demand type was specified as uniform but lo and/or hi were not provided")
	elif demand_type_list[0] == 'D' and demand_list is None:
		raise ValueError("Demand type was specified as deterministic but demand_list were not provided")
	elif demand_type_list[0] == 'CD' and (demand_list is None or probabilities_list is None):
		raise ValueError("Demand type was specified as discrete explicit but demand_list and/or probabilities were not provided")

	# Check that valid inventory policy has been provided.
	for n_index in range(num_nodes):
		# Check parameters for inventory policy type.
		if inventory_policy_type_list[n_index] is None:
			raise ValueError("Valid inventory_policy_type has not been provided")
		elif inventory_policy_type_list[n_index] in ('BS', 'EBS', 'BEBS') \
			and base_stock_levels_list[n_index] is None:
			raise ValueError("Policy type was specified as base-stock but base-stock level was not provided")
		elif inventory_policy_type_list[n_index] == 'rQ' \
			and (reorder_points_list[n_index] is None or order_quantities_list[n_index] is None):
			raise ValueError("Policy type was specified as (r,Q) but reorder point and/or order quantity were not "
							 "provided")
		elif inventory_policy_type_list[n_index] == 'sS' \
			and (reorder_points_list[n_index] is None or order_up_to_levels_list[n_index] is None):
			raise ValueError("Policy type was specified as (s,S) but reorder point and/or order-up-to level were not "
							 "provided")
		elif inventory_policy_type_list[n_index] == 'FQ' \
			and order_quantities_list[n_index] is None:
			raise ValueError("Policy type was specified as fixed-quantity but order quantity was not provided")

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
		node.revenue = revenue_list[n]
#		node.lead_time = shipment_lead_time_list[n]
		node.shipment_lead_time = shipment_lead_time_list[n]
		node.order_lead_time = order_lead_time_list[n]

		# Build and set demand source.
		# TODO: make a one-line way to create demand source -- this is way too cumbersome
		demand_type = demand_type_list[n]
		if n == 0:
			demand_source = DemandSource()
			demand_source.type = demand_type
			if demand_type == 'N':
				demand_source.mean = demand_mean_list[n]
				demand_source.standard_deviation = demand_standard_deviation_list[n]
			elif demand_type in ('UC', 'UD'):
				demand_source.lo = demand_lo_list[n]
				demand_source.hi = demand_hi_list[n]
			elif demand_type == 'D':
				demand_source.demand_list = demand_list[n]
			elif demand_type == 'CD':
				demand_source.demand_list = demand_list[n]
				demand_source.probabilities = probabilities_list[n]
		else:
			demand_source = None
		node.demand_source = demand_source

		# Set initial quantities.
		node.initial_inventory_level = initial_IL_list[n]
		node.initial_orders = initial_orders_list[n]
		node.initial_shipments = initial_shipments_list[n]

		# Set inventory policy.
		policy = Policy(inventory_policy_type_list[n], node)
		if inventory_policy_type_list[n] in ('BS', 'EBS', 'BEBS'):
			policy.base_stock_level = base_stock_levels_list[n]
		elif inventory_policy_type_list[n] == 'rQ':
			policy.reorder_point = reorder_points_list[n]
			policy.order_quantity = order_quantities_list[n]
		elif inventory_policy_type_list[n] == 'sS':
			policy.reorder_point = reorder_points_list[n]
			policy.order_up_to_level = order_up_to_levels_list[n]
		elif inventory_policy_type_list[n] == 'FQ':
			policy.order_quantity=order_quantities_list[n]
		else:
			policy = None
		node.inventory_policy = policy

		# Set supply type.
		if n == 0:
			node.supply_type = None
		else:
			node.supply_type = 'U'

		# Add node to network.
		if n == 0:
			network.add_node(node)
			retailer_node = node
		else:
			network.add_predecessor(retailer_node, node)

	return network


# ===============================================================================
# Local vs. Echelon Methods
# ===============================================================================

def local_to_echelon_base_stock_levels(network, S_local):
	"""Convert local base-stock levels to echelon base-stock levels for a serial system.

	Assumes network is serial system but does not assume anything about the
	labeling of the nodes.

	Parameters
	----------
	network : SupplyChainNetwork
		The serial inventory network.
	S_local : dict
		Dict of local base-stock levels.

	Returns
	-------
	S_echelon : dict
		Dict of echelon base-stock levels.

	"""
	# TODO: allow more general topologies.

	S_echelon = {}
	for n in network.nodes:
		S_echelon[n.index] = S_local[n.index]
		k = n.get_one_successor()
		while k is not None:
			S_echelon[n.index] += S_local[k.index]
			k = k.get_one_successor()

	return S_echelon


def echelon_to_local_base_stock_levels(network, S_echelon):
	"""Convert echelon base-stock levels to local base-stock levels for a serial system.

	Assumes network is serial system but does not assume anything about the
	labeling of the nodes.

	Parameters
	----------
	network : SupplyChainNetwork
		The serial inventory network.
	S_echelon : dict
		Dict of echelon base-stock levels.

	Returns
	-------
	S_local : dict
		Dict of local base-stock levels.

	"""
	# TODO: allow more general topologies.

	S_local = {}

	# Determine indexing of nodes. (node_list[i] = index of i'th node, where
	# i = 0 means sink node and i = N-1 means source node.)
	node_list = []
	n = network.sink_nodes[0]
	while n is not None:
		node_list.append(n.index)
		n = n.get_one_predecessor()

	# Calculate S-minus.
	S_minus = {}
	j = 0
	for n in network.nodes:
		S_minus[n.index] = np.min([S_echelon[node_list[i]]
							 for i in range(j, len(S_echelon))])
		j += 1

	# Calculate S_local.
	for n in network.nodes:
		# Get successor.
		k = n.get_one_successor()
		if k is None:
			S_local[n.index] = S_minus[n.index]
		else:
			S_local[n.index] = S_minus[n.index] - S_minus[k.index]

	return S_local


