# ===============================================================================
# stockpyl - SupplyChainNetwork Class
# -------------------------------------------------------------------------------
# Updated: 03-06-2020
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

This module contains the |class_network| class, which is a network consisting of
one or more nodes. The network and nodes together specify a problem instance.

.. note:: |node_stage|

.. note:: |fosct_notation|

A |class_network| is used primarily for :ref:`multi-echelon inventory optimization (MEIO) <meio_page>`
or :ref:`simulation <sim_page>`. Most data for the problem instance is specified
in the |class_node| objects contained within the |class_network|, rather than in
the network itself.


API Reference
-------------

"""

# ===============================================================================
# Imports
# ===============================================================================

import networkx as nx
import numpy as np
#import json
import copy

#import supply_chain_node
from stockpyl.supply_chain_node import SupplyChainNode
from stockpyl.demand_source import DemandSource
from stockpyl.policy import Policy
from stockpyl.disruption_process import DisruptionProcess
from stockpyl.helpers import is_list, ensure_dict_for_nodes, ensure_list_for_nodes
from stockpyl.helpers import build_node_data_dict

# ===============================================================================
# SupplyChainNetwork Class
# ===============================================================================

class SupplyChainNetwork(object):
	"""The |class_network| class contains one or more nodes, each
	represented by a |class_node| object.

	Attributes
	----------
	period : int
		The current period. Used for simulation.
	problem_specific_data : object
		Placeholder for object that is used to provide data for specific
		problem types.
	max_max_replenishment_time : int
		Largest value of ``max_replenishment_time`` among all nodes in the network.
		Used by |mod_gsm_tree| module.
	"""

	def __init__(self, **kwargs):
		"""SupplyChainNetwork constructor method.

		Parameters
		----------
		kwargs : optional
			Optional keyword arguments to specify network attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match a |class_network| attribute.

		"""
		# Initialize attributes.
		self.initialize()

		# Set attributes specified by kwargs.
		for key, value in kwargs.items():
			if key in vars(self):
				vars(self)[key] = value
			elif f"_{key}" in vars(self):
				vars(self)[f"_{key}"] = value
			else:
				raise AttributeError(f"{key} is not an attribute of SupplyChainNetwork")

	@property
	def nodes(self):
		"""List of all nodes in the network, as |class_node| objects. Read only.
		"""
		if hasattr(self, '_nodes'):
			return self._nodes
		else:
			return []

	@property
	def node_indices(self):
		"""List of indices of all nodes in the network. Read only.
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
		"""List of all source nodes, i.e., all nodes that have no predecessors,
		as |class_node| objects.
		"""
		return [node for node in self.nodes if node.predecessor_indices() == []]

	@property
	def sink_nodes(self):
		"""List of all sink nodes, i.e., all nodes that have no successors,
		as |class_node| objects.
		"""
		return [node for node in self.nodes if node.successor_indices() == []]

	@property
	def edges(self):
		"""List of all edges, as tuples whose elements are the indices of
		the nodes in the edge.
		"""
		edge_list = []
		for n in self.nodes:
			for m in n.successors():
				edge_list.append((n.index, m.index))
		return edge_list

	def has_directed_cycle(self):
		"""Check whether network contains a directed cycle.

		Returns
		-------
		bool
			``True`` if network contains a directed cycle, ``False`` otherwise.
		"""

		# Build networkx representation.
		G = self.networkx_digraph()

		# Count simple cycles.
		num_cycles = len(list(nx.simple_cycles(G)))

		return num_cycles > 0


	# Special members.

	def __repr__(self):
		"""
		Return a string representation of the |class_network| instance.

		Returns
		-------
		str
			A string representation of the |class_network| instance.

		"""
		return "SupplyChainNetwork({:s})".format(str(vars(self)))

	# Attribute management.

	def initialize(self, overwrite=True):
		"""Initialize the parameters in the object to their default values. If ``overwrite`` is ``True``,
		all attributes are reset to their default values, even if they already exist. (This is how the
		method should be called from the object's ``__init()__`` method.) If it is ``False``,
		then missing attributes are added to the object but existing attributes are not overwritten. (This
		is how the method should be called when loading an instance from a file, to make sure that all
		attributes are present.)

		Handles ``_nodes`` list as follows:

			* If ``overwrite`` is ``True``, replaces ``_nodes`` with an empty list.
			* If ``overwrite`` is ``False`` and ``_nodes`` does not exist, creates the ``_nodes`` attribute 
			  and fills it with an empty list.
			* If ``overwrite`` is ``False`` and ``_nodes`` exists but is ``None`` or an empty list, does nothing.
			* If ``overwrite`` is ``False`` and ``_nodes`` exists and contains at least one |class_node| 
			  object, calls the ``initialize()`` method for each node with ``overwrite=False`` to ensure all attributes are present (as well as all attributes in its object attributes such as ``demand_source``, etc.).


		Parameters
		----------
		overwrite : bool, optional
			``True`` to overwrite all attributes to their initial values, ``False`` to initialize
			only those attributes that are missing from the object. Default = ``True``.

		"""

		# NOTE: If the attribute list changes, deep_equal_to() must be updated accordingly.

		# --- Nodes and Period --- #
		if overwrite or not hasattr(self, '_nodes'):
			self._nodes = []
		elif is_list(self._nodes):
			for n in self._nodes:
				n.initialize(overwrite=False)
		if overwrite or not hasattr(self, '_period'):
			self._period = 0

		# --- Intermediate Calculations for GSM Problems --- #
		if overwrite or not hasattr(self, 'max_max_replenishment_time'):
			self.max_max_replenishment_time = None
			
	def deep_equal_to(self, other, rel_tol=1e-8):
		"""Check whether network "deeply equals" ``other``, i.e., if all attributes are
		equal, including attributes that are themselves objects.
		
		Parameters
		----------
		other : |class_network|
			The network to compare this one to.
		rel_tol : float, optional
			Relative tolerance to use when comparing equality of float attributes.

		Returns
		-------
		bool
			``True`` if the two networks are equal, ``False`` otherwise.
		"""

		if sorted(self.node_indices) != sorted(other.node_indices):
			return False

		for n_ind in sorted(self.node_indices):
			other_node = other.get_node_from_index(n_ind)
			if other_node is None:
				return False
			if not self.get_node_from_index(n_ind).deep_equal_to(other_node, rel_tol=rel_tol):
				return False

		return self._period == other._period and \
			self.max_max_replenishment_time == other.max_max_replenishment_time
			
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
		|class_node|
			The node whose index is ``index``, or ``None`` if none.

		"""
		for node in self.nodes:
			if node.index == index:
				return node

		return None

	def reindex_nodes(self, old_to_new_dict, new_names=None):
		"""Change indices of the nodes in the network using ``old_to_new_dict``.
		If ``new_names`` is provided, also updates ``name`` attribute of the nodes.

		Parameters
		----------
		old_to_new_dict : dict
			Dict in which keys are old indices and values are new indices.
		new_names : dict, optional
			Dict in which keys are old indices and values are new names.

		"""
		# Reindex state variables. (This must be done before reindexing nodes.)
		for node in self.nodes:
			node.reindex_all_state_variables(old_to_new_dict)

		# Reindex nodes.
		for node in self.nodes:
			# Reindex node.
			old_index = node.index
			node.index = old_to_new_dict[old_index]
			# Rename node.
			if new_names is not None:
				node.name = new_names[old_index]

	# Methods related to network structure.

	def add_node(self, node):
		"""Add ``node`` to the network. ``node`` will not be connected to other
		nodes that might be in the network already.

		If ``node`` is already in the network (as determined by the index),
		do nothing.

		Parameters
		----------
		node : |class_node|
			The node to add to the network.
		"""

		# Check whether node is already in network.
		if node not in self.nodes:
			self.nodes.append(node)
			node.network = self

	def add_edge(self, from_index, to_index):
		"""Add an edge to the network to and from the nodes with the specified indices.
		If the edge is already in the network, does nothing.
		
		Parameters
		----------
		from_index : int
			Index of "from" node.
		to_index : int
			Index of "to" node.

		Raises
		------
		ValueError
			If either index is not in the network.
		"""

		if (from_index, to_index) not in self.edges:

			# Get nodes.
			from_node = self.get_node_from_index(from_index)
			to_node = self.get_node_from_index(to_index)

			# Do nodes exist?
			if from_node is None:
				raise ValueError(f"No node with index {from_index} in network")
			if to_node is None:
				raise ValueError(f"No node with index {to_index} in network")
			
			# Add edge.
			self.add_successor(from_node, to_node)

	def add_edges_from_list(self, edge_list):
		"""Add multiple edges to the network from a list of index tuples.
		Any edge that is already in the network is ignored.

		Parameters
		----------
		edge_list : list
			List of tuples of indices of nodes in edges.

		Raises
		------
		ValueError
			If any of the nodes are not in the network.
		"""

		# Loop through edges in list.
		for e in edge_list:
			self.add_edge(e[0], e[1])

	def add_successor(self, node, successor_node):
		"""Add ``successor_node`` as a successor to ``node``. ``node`` must
		already be contained in the network.

		The method adds the nodes to each other's lists of _successors and
		_predecessors. If ``successor_node`` is not already contained in the
		network, the method also adds it. (The node is assumed to be contained
		in the network if its index or name match those of a node in the network.)

		Parameters
		----------
		node : |class_node|
			The node to which the successor should be added.
		successor_node : |class_node|
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
		node : |class_node|
			The node to which the successor should be added.
		predecessor_node : |class_node|
			The node to be added as a predecessor.

		"""

		# Add nodes to each other's predecessor and successor lists.
		node.add_predecessor(predecessor_node)
		predecessor_node.add_successor(node)

		# Add node to network (if not already contained in it).
		self.add_node(predecessor_node)

	def remove_node(self, node):
		"""Remove a node from the network. Remove the node from the node list and
		from its predecessors' and successors' successors and predecessors lists.

		If ``node`` is not in the network (as determined by the index), do nothing.

		Parameters
		----------
		node : |class_node|
			The node to remove.
		"""

		# Check whether node is in network.
		if node in self.nodes:
			# Remove from successors' predecessors lists.
			for s in node.successors():
				s.remove_predecessor(node)
			# Remove from predecessors' successors lists.
			for p in node.predecessors():
				p.remove_successor(node)
			# Remove node from network.
			self.nodes.remove(node)

	def networkx_digraph(self):
		"""Build a `NetworkX <https://networkx.org/>`_ ``DiGraph`` object with the same structure as
		the |class_network|.

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

def network_from_edges(edges, node_order_in_lists=None, **kwargs):
	"""Construct a supply chain network with the specified edges.

	The ``kwargs`` parameters specify the attributes (data) for the nodes in the network.
	If they are provided, they must be either a dict, a list, or a singleton,
	with the following requirements:

		* If the parameter is a dict, then the keys must contain the node indices
		  and the values must contain the corresponding attribute values. If a given
		  node index is contained in the list of edges but is not a key in the dict,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a singleton, then the attribute is set to that value
		  for all nodes.
		* If the parameter is a list and ``node_order_in_lists`` is provided, ``node_order_in_lists``
		  must contain the same indices as the nodes in the edges in ``edges`` (otherwise a ``ValueError``
		  is raised). The values in the list are
		  assumed to correspond to the node indices in the order they are specified in 
		  ``node_order_in_lists``. That is, the value in slot ``k`` in the parameter list is
		  assigned to the node with index ``node_order_in_lists[k]``. If a given
		  node index is contained in the list of edges but is not in ``node_order_in_lists``,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a list and ``node_order_in_lists`` is not provided, the values 
		  in the list are assumed to correspond to the sorted list of node indices in 
		  the edge list. That is, the value in slot ``k`` in the parameter list is assigned
		  to the node in slot ``k`` when the nodes in the edge list are sorted.

	If ``edges`` is ``None`` or ``[]``, a single-node network is returned. The index of the node
	is set to 0, unless ``node_order_in_lists`` is provided, in which case the node's index is set to
	``node_order_in_lists[0]``. The rules for ``kwargs`` above also apply to the single-node case.

	``supply_type`` attribute is set to 'U' at all nodes that have no predecessors and to
	 ``None`` at all other nodes, no matter how (or whether) the corresponding parameter is set.

	For the ``demand_source`` attribute, you may pass a |class_demand_source| object
	*or* the individual attributes of the demand source (``mean``, ``round_to_int``, etc.).
	In the latter case, a ``DemandSource`` object will be constructed with the specified
	attributes and filled into the ``demand_source`` attribute of the node. **Note:** If providing
	individual demand source attributes, the ``type`` attribute must be called ``demand_type``
	to avoid ambiguity with other objects.

	Similarly, you may pass |class_policy| and |class_disruption_process| objects for
	the ``inventory_policy`` and ``disruption_process`` attributes, or you may pass
	the individual attributes for these objects. **Note:** If providing individual inventory policy
	attributes, the ``type`` attribute must be called ``policy_type`` to avoid
	ambiguity with other objects.

	If ``kwargs`` contains a parameter that is not an attribute of |class_node| or one of
	its attribute objects (|class_demand_source|, |class_policy|, or |class_disruption_process|), 
	an ``AttributeError`` is raised. (Exception: ``demand_type`` and ``policy_type`` are allowed
	even though they are not attributes of |class_node|; see above.)


	.. note:: This function does not check that valid attributes have been provided for
		``demand_source``, ``inventory_policy``, and ``disruption_process``. For example,
		it does not check that a ``base_stock_level`` has been provided if the policy type
		is set to ``BS``.


	Parameters
	----------
	edges : list
		List of edges, with each edge specified as a tuple ``(a, b)``, where ``a``
		is the index of the predecessor and ``b`` is the index of the successor node.
		If ``None`` or empty, a single-node network is created.
	node_order_in_lists : list, optional
		List of node indices in the order in which the nodes are listed in any
		attributes that are lists. (``node_order_in_lists[k]`` is the index of the ``k`` th node.)
	kwargs : optional
		Optional keyword arguments to specify node attributes.


	Raises
	------
	AttributeError
		If ``kwargs`` contains a parameter that is not an attribute of |class_node|.

	"""

	# Create network.
	network = SupplyChainNetwork()

	# Is the edge list non-empty?
	if edges:
		# Add nodes from edge list.
		for e in edges:
			if e[0] not in network.node_indices:
				network.add_node(SupplyChainNode(e[0]))
			if e[1] not in network.node_indices:
				network.add_node(SupplyChainNode(e[1]))
	else:
		# Add single node.
		if node_order_in_lists is not None:
			ind = node_order_in_lists[0]
		else:
			ind = 0
		network.add_node(SupplyChainNode(ind))

	# Check attributes in kwargs.
	for a in kwargs.keys():
		if not hasattr(network.nodes[0], a) and \
			not hasattr(network.nodes[0].demand_source, a) and \
			not hasattr(network.nodes[0].inventory_policy, a) and \
			not hasattr(network.nodes[0].disruption_process, a) and \
			a not in ('demand_type', 'policy_type'):
			raise AttributeError(f"{a} is not an attribute of SupplyChainNode")

	# Check node_order_in_lists; if not provided, build it.
	if node_order_in_lists is None:
		node_order_in_lists = sorted(network.node_indices)
	else:
		if set(node_order_in_lists) != set(network.node_indices):
			raise ValueError("node_order_in_lists does not match nodes contained in edge list")

	# Add edges.
	for e in edges:
		source = network.get_node_from_index(e[0])
		sink = network.get_node_from_index(e[1])
		network.add_successor(source, sink)

	# Build data dict.
	data_dict = build_node_data_dict(attribute_dict=kwargs, node_order_in_lists=node_order_in_lists)

	# Set node attributes. (The code below uses the get() function to access the
	# dictionaries within data_dict; get() returns None if the requested key is not
	# in the dict.)
	for n in network.nodes:

		# Costs and lead times. 
		if data_dict[n.index].get('local_holding_cost') is not None:
			n.local_holding_cost 		= data_dict[n.index].get('local_holding_cost') 
		else:
			n.local_holding_cost 		= data_dict[n.index].get('holding_cost')
		n.echelon_holding_cost			= data_dict[n.index].get('echelon_holding_cost')
		n.local_holding_cost_function	= data_dict[n.index].get('local_holding_cost_function')
		n.in_transit_holding_cost		= data_dict[n.index].get('in_transit_holding_cost')
		n.stockout_cost					= data_dict[n.index].get('stockout_cost')
		n.stockout_cost_function		= data_dict[n.index].get('stockout_cost_function')
		n.purchase_cost					= data_dict[n.index].get('purchase_cost')
		n.revenue						= data_dict[n.index].get('revenue')
		if data_dict[n.index].get('shipment_lead_time') is not None:
			n.shipment_lead_time		= data_dict[n.index].get('shipment_lead_time')
		else:
			n.shipment_lead_time		= data_dict[n.index].get('lead_time')
		n.order_lead_time				= data_dict[n.index].get('order_lead_time')

		# Demand source.
		if data_dict[n.index].get('demand_source') is not None:
			n.demand_source = data_dict[n.index]['demand_source']
		else:
			# Create DemandSource object. (Don't override default value for round_to_int 
			# with None.)
			ds = DemandSource()
			ds.type 				= data_dict[n.index].get('demand_type')
			if data_dict[n.index].get('round_to_int') is not None:
				ds.round_to_int		= data_dict[n.index].get('round_to_int')
			ds.mean					= data_dict[n.index].get('mean')
			ds.standard_deviation	= data_dict[n.index].get('standard_deviation')
			ds.demand_list			= data_dict[n.index].get('demand_list')
			ds.probabilities		= data_dict[n.index].get('probabilities')
			ds.lo					= data_dict[n.index].get('lo')
			ds.hi					= data_dict[n.index].get('hi')
			n.demand_source = ds

		# Inventory policy.
		if data_dict[n.index].get('inventory_policy') is not None:
			n.inventory_policy = data_dict[n.index]['inventory_policy']
		else:
			# Create Policy object.
			pol = Policy()
			pol.type				= data_dict[n.index].get('policy_type')
			pol.node				= n
			pol.base_stock_level	= data_dict[n.index].get('base_stock_level')
			pol.order_quantity		= data_dict[n.index].get('order_quantity')
			pol.reorder_point		= data_dict[n.index].get('reorder_point')
			pol.order_up_to_level	= data_dict[n.index].get('order_up_to_level')
			n.inventory_policy = pol

		# Disruption process.
		if data_dict[n.index].get('disruption_process') is not None:
			n.disruption_process = data_dict[n.index]['disruption_process']
		else:
			# Create DisruptionProcess object. (Don't override default values for disruption_type
			# or disrupted with None.)
			dp = DisruptionProcess()
			dp.random_process_type		= data_dict[n.index].get('random_process_type')
			if data_dict[n.index].get('disruption_type') is not None:
				dp.disruption_type		= data_dict[n.index].get('disruption_type')
			dp.disruption_probability	= data_dict[n.index].get('disruption_probability')
			dp.recovery_probability		= data_dict[n.index].get('recovery_probability')
			dp.disruption_state_list	= data_dict[n.index].get('disruption_state_list')
			if data_dict[n.index].get('disrupted') is not None:
				dp.disrupted			= data_dict[n.index].get('disrupted')
			n.disruption_process = dp

		# Supply type.
		if not n.predecessors():
			n.supply_type			= 'U'

		# Initial quantities.
		n.initial_inventory_level	= data_dict[n.index].get('initial_inventory_level')
		n.initial_orders			= data_dict[n.index].get('initial_orders')
		n.initial_shipments			= data_dict[n.index].get('initial_shipments')

		# GSM parameters.
		n.processing_time			= data_dict[n.index].get('processing_time')
		n.external_inbound_cst		= data_dict[n.index].get('external_inbound_cst')
		n.external_outbound_cst		= data_dict[n.index].get('external_outbound_cst')
		n.demand_bound_constant		= data_dict[n.index].get('demand_bound_constant')
		n.units_required			= data_dict[n.index].get('units_required')

		# Problem-specific data.
		n.problem_specific_data		= data_dict[n.index].get('problem_specific_data')

	return network


# ===============================================================================
# Methods to Create Specific Network Structures
# ===============================================================================

def single_stage_system(index=0, **kwargs):
	"""Generate a single-stage network.

	The ``kwargs`` parameters specify the attributes (data) for the node.

	For the ``demand_source`` attribute, you may pass a |class_demand_source| object
	*or* the individual attributes of the demand source (``mean``, ``round_to_int``, etc.).
	In the latter case, a ``DemandSource`` object will be constructed with the specified
	attributes and filled into the ``demand_source`` attribute of the node. **Note:** If providing
	individual demand source attributes, the ``type`` attribute must be called ``demand_type``
	to avoid ambiguity with other objects.

	Similarly, you may pass |class_policy| and |class_disruption_process| objects for
	the ``inventory_policy`` and ``disruption_process`` attributes, or you may pass
	the individual attributes for these objects. **Note:** If providing individual inventory policy
	attributes, the ``type`` attribute must be called ``policy_type`` to avoid
	ambiguity with other objects.

	If ``kwargs`` contains a parameter that is not an attribute of |class_node| or one of
	its attribute objects (|class_demand_source|, |class_policy|, or |class_disruption_process|), 
	an ``AttributeError`` is raised. (Exception: ``demand_type`` and ``policy_type`` are allowed
	even though they are not attributes of |class_node|; see above.)


	.. note:: This function does not check that valid attributes have been provided for
		``demand_source``, ``inventory_policy``, and ``disruption_process``. For example,
		it does not check that a ``base_stock_level`` has been provided if the policy type
		is set to ``BS``.
	

	Parameters
	----------
	index : int, optional
		Index to use for the node. Default = 0.
	kwargs : optional
		Optional keyword arguments to specify node attributes.

	Returns
	-------
	network : |class_network|
		The single-stage network, with parameters filled.

	Raises
	------
	AttributeError
		If ``kwargs`` contains a parameter that is not an attribute of |class_node|.

	"""

	return network_from_edges(
		edges=[],
		node_order_in_lists=[index],
		**kwargs
	)


def serial_system(num_nodes, node_order_in_system=None, node_order_in_lists=None, **kwargs):
	"""Generate a serial system with the specified number of nodes. By default, node 0
	is upstream and node ``num_nodes`` - 1 is downstream, but this can be changed by
	setting ``node_order_in_system``. 

	The ``kwargs`` parameters specify the attributes (data) for the nodes in the network.
	If they are provided, they must be either a dict, a list, or a singleton,
	with the following requirements:

		* If the parameter is a dict, then the keys must contain the node indices
		  and the values must contain the corresponding attribute values. If a given
		  node index is contained in ``node_order_in_system`` (or in ``range(num_nodes)``,
		  if ``node_order_in_system`` is not provided) but is not a key in the dict,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a singleton, then the attribute is set to that value
		  for all nodes.
		* If the parameter is a list and ``node_order_in_lists`` is provided, ``node_order_in_lists``
		  must contain the same indices as the nodes in the edges in ``edges`` (otherwise a ``ValueError``
		  is raised). The values in the list are
		  assumed to correspond to the node indices in the order they are specified in 
		  ``node_order_in_lists``. That is, the value in slot ``k`` in the parameter list is
		  assigned to the node with index ``node_order_in_lists[k]``. If a given
		  node index is contained in the list of edges but is not in ``node_order_in_lists``,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a list and ``node_order_in_lists`` is not provided, the values 
		  in the list are assumed to correspond to nodes in the same order as ``node_order_in_system`` 
		  (or in ``range(num_nodes)``, if ``node_order_in_system`` is not provided).

	``demand_source`` attribute is only set at the downstream-most node,
	no matter how (or whether) the corresponding parameter is set. ``supply_type`` attribute is set to 'U'
	at the upstream-most node and to ``None`` at all other nodes, no matter how (or whether) the
	corresponding parameter is set.

	For the ``demand_source`` attribute, you may pass a |class_demand_source| object
	*or* the individual attributes of the demand source (``mean``, ``round_to_int``, etc.).
	In the latter case, a ``DemandSource`` object will be constructed with the specified
	attributes and filled into the ``demand_source`` attribute of the node. **Note:** If providing
	individual demand source attributes, the ``type`` attribute must be called ``demand_type``
	to avoid ambiguity with other objects.

	Similarly, you may pass |class_policy| and |class_disruption_process| objects for
	the ``inventory_policy`` and ``disruption_process`` attributes, or you may pass
	the individual attributes for these objects. **Note:** If providing individual inventory policy
	attributes, the ``type`` attribute must be called ``policy_type`` to avoid
	ambiguity with other objects.

	If ``kwargs`` contains a parameter that is not an attribute of |class_node| or one of
	its attribute objects (|class_demand_source|, |class_policy|, or |class_disruption_process|), 
	an ``AttributeError`` is raised. (Exception: ``demand_type`` and ``policy_type`` are allowed
	even though they are not attributes of |class_node|; see above.)


	.. note:: This function does not check that valid attributes have been provided for
		``demand_source``, ``inventory_policy``, and ``disruption_process``. For example,
		it does not check that a ``base_stock_level`` has been provided if the policy type
		is set to ``BS``.


	Parameters
	----------
	num_nodes : int
		Number of nodes in the serial system.
	node_order_in_system : list, optional
		List of node indices in the order that they appear in the serial system,
		with upstream-most node listed first. If omitted, the system will be indexed
		0, ..., ``num_nodes`` - 1.
	node_order_in_lists : list, optional
		List of node indices in the order in which the nodes are listed in any
		attributes that are lists. (``node_order_in_lists[k]`` is the index of the ``k`` th node.)
	kwargs : optional
		Optional keyword arguments to specify node attributes.


	Raises
	------
	AttributeError
		If ``kwargs`` contains a parameter that is not an attribute of |class_node|.
	"""

	# Determine edges of network.
	if node_order_in_system is None:
		node_order_in_system = list(range(num_nodes))
	edges = [(node_order_in_system[k], node_order_in_system[k+1]) for k in range(len(node_order_in_system)-1)]
	
	# Make local copy of kwarg dict.
	local_kwargs = copy.deepcopy(kwargs)
	# Determine sink node.
	sink_node = node_order_in_system[-1]
	# Set demand_source parameter so it only occurs at sink node.
	if 'demand_source' not in local_kwargs:
		local_kwargs['demand_source'] = {}
	for n in node_order_in_system:
		if n != sink_node:
			local_kwargs['demand_source'][n] = DemandSource()

	# Determine node_order_in_lists.
	if node_order_in_lists is None:
		node_order_in_lists = node_order_in_system

	# Build network.
	return network_from_edges(
		edges=edges, 
		node_order_in_lists=node_order_in_lists, 
		**local_kwargs
	)


def owmr_system(num_retailers, node_order_in_system=None, node_order_in_lists=None, **kwargs):
	"""Generate a one-warehouse, multiple-retailer (OWMR) (i.e., 2-echelon distribution)
	system with the specified number of retailers. By default, node 0 is the warehouse
	and nodes 1, ..., ``num_retailers`` are the retailers, but this can be changed 
	by setting ``node_order_in_system``.

	The ``kwargs`` parameters specify the attributes (data) for the nodes in the network.
	If they are provided, they must be either a dict, a list, or a singleton,
	with the following requirements:

		* If the parameter is a dict, then the keys must contain the node indices
		  and the values must contain the corresponding attribute values. If a given
		  node index is contained in ``node_order_in_system`` (or in ``range(num_nodes)``,
		  if ``node_order_in_system`` is not provided) but is not a key in the dict,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a singleton, then the attribute is set to that value
		  for all nodes.
		* If the parameter is a list and ``node_order_in_lists`` is provided, ``node_order_in_lists``
		  must contain the same indices as the nodes in the edges in ``edges`` (otherwise a ``ValueError``
		  is raised). The values in the list are
		  assumed to correspond to the node indices in the order they are specified in 
		  ``node_order_in_lists``. That is, the value in slot ``k`` in the parameter list is
		  assigned to the node with index ``node_order_in_lists[k]``. If a given
		  node index is contained in the list of edges but is not in ``node_order_in_lists``,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a list and ``node_order_in_lists`` is not provided, the values 
		  in the list are assumed to correspond to nodes in the same order as ``node_order_in_system`` 
		  (or in ``range(num_retailers+1)``, if ``node_order_in_system`` is not provided).

	``demand_source`` attribute is not set at the warehouse node,
	no matter how (or whether) the corresponding parameter is set.``supply_type`` attribute is set to 'U'
	at the warehouse node and to ``None`` at all other nodes, no matter how (or whether) the
	corresponding parameter is set.

	For the ``demand_source`` attribute, you may pass a |class_demand_source| object
	*or* the individual attributes of the demand source (``mean``, ``round_to_int``, etc.).
	In the latter case, a ``DemandSource`` object will be constructed with the specified
	attributes and filled into the ``demand_source`` attribute of the node. **Note:** If providing
	individual demand source attributes, the ``type`` attribute must be called ``demand_type``
	to avoid ambiguity with other objects.

	Similarly, you may pass |class_policy| and |class_disruption_process| objects for
	the ``inventory_policy`` and ``disruption_process`` attributes, or you may pass
	the individual attributes for these objects. **Note:** If providing individual inventory policy
	attributes, the ``type`` attribute must be called ``policy_type`` to avoid
	ambiguity with other objects.

	If ``kwargs`` contains a parameter that is not an attribute of |class_node| or one of
	its attribute objects (|class_demand_source|, |class_policy|, or |class_disruption_process|), 
	an ``AttributeError`` is raised. (Exception: ``demand_type`` and ``policy_type`` are allowed
	even though they are not attributes of |class_node|; see above.)


	.. note:: This function does not check that valid attributes have been provided for
		``demand_source``, ``inventory_policy``, and ``disruption_process``. For example,
		it does not check that a ``base_stock_level`` has been provided if the policy type
		is set to ``BS``.


	Parameters
	----------
	num_retailers : int
		Number of retailers in OWMR system.
	node_order_in_system : list, optional
		List of node indices in the order that they appear in the OWMR system,
		with warehouse node first and retailer nodes last. If omitted, the warehouse
		will have index 0 and the retailers will have indices 1, ..., ``num_retailers``.
	node_order_in_lists : list, optional
		List of node indices in the order in which the nodes are listed in any
		attributes that are lists. (``node_order_in_lists[k]`` is the index of the ``k`` th node.)
	kwargs : optional
		Optional keyword arguments to specify node attributes.

	Raises
	------
	AttributeError
		If ``kwargs`` contains a parameter that is not an attribute of |class_node|.
	"""

	# Determine edges of network.
	if node_order_in_system is None:
		node_order_in_system = list(range(0, num_retailers+1))
	edges = [(node_order_in_system[0], node_order_in_system[k]) for k in range(1, num_retailers+1)]

	# Make local copy of kwarg dict.
	local_kwargs = copy.deepcopy(kwargs)
	# Set demand_source parameter so it only occurs at retailer nodes.
	if 'demand_source' not in local_kwargs:
		local_kwargs['demand_source'] = {}
	local_kwargs['demand_source'][node_order_in_system[-1]] = DemandSource()

	# Determine node_order_in_lists.
	if node_order_in_lists is None:
		node_order_in_lists = node_order_in_system

	# Build network.
	return network_from_edges(
		edges=edges,
		node_order_in_lists=node_order_in_lists,
		**local_kwargs
	)


def mwor_system(num_warehouses, node_order_in_system=None, node_order_in_lists=None, **kwargs):
	"""Generate a multiple-warehouse, one-retailer (MWOR) (i.e., 2-echelon assembly)
	system with the specified number of warehouses. By default, node 0 is the retailer
	and nodes 1, ..., ``num_warehouses`` are the warehouses, but this can be changed 
	by setting ``node_order_in_system``.

	The ``kwargs`` parameters specify the attributes (data) for the nodes in the network.
	If they are provided, they must be either a dict, a list, or a singleton,
	with the following requirements:

		* If the parameter is a dict, then the keys must contain the node indices
		  and the values must contain the corresponding attribute values. If a given
		  node index is contained in ``node_order_in_system`` (or in ``range(num_nodes)``,
		  if ``node_order_in_system`` is not provided) but is not a key in the dict,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a singleton, then the attribute is set to that value
		  for all nodes.
		* If the parameter is a list and ``node_order_in_lists`` is provided, ``node_order_in_lists``
		  must contain the same indices as the nodes in the edges in ``edges`` (otherwise a ``ValueError``
		  is raised). The values in the list are
		  assumed to correspond to the node indices in the order they are specified in 
		  ``node_order_in_lists``. That is, the value in slot ``k`` in the parameter list is
		  assigned to the node with index ``node_order_in_lists[k]``. If a given
		  node index is contained in the list of edges but is not in ``node_order_in_lists``,
		  the attribute value is set to ``None`` for that node.
		* If the parameter is a list and ``node_order_in_lists`` is not provided, the values 
		  in the list are assumed to correspond to nodes in the same order as ``node_order_in_system`` 
		  (or in ``range(num_warehouses+1)``, if ``node_order_in_system`` is not provided).

	``demand_source`` attribute is only set at the retailer node,
	no matter how (or whether) the corresponding parameter is set. ``supply_type`` attribute is set to 'U'
	at the warehouse nodes and to ``None`` at the retailer node, no matter how (or whether) the
	corresponding parameter is set.

	For the ``demand_source`` attribute, you may pass a |class_demand_source| object
	*or* the individual attributes of the demand source (``mean``, ``round_to_int``, etc.).
	In the latter case, a ``DemandSource`` object will be constructed with the specified
	attributes and filled into the ``demand_source`` attribute of the node. **Note:** If providing
	individual demand source attributes, the ``type`` attribute must be called ``demand_type``
	to avoid ambiguity with other objects.

	Similarly, you may pass |class_policy| and |class_disruption_process| objects for
	the ``inventory_policy`` and ``disruption_process`` attributes, or you may pass
	the individual attributes for these objects. **Note:** If providing individual inventory policy
	attributes, the ``type`` attribute must be called ``policy_type`` to avoid
	ambiguity with other objects.

	If ``kwargs`` contains a parameter that is not an attribute of |class_node| or one of
	its attribute objects (|class_demand_source|, |class_policy|, or |class_disruption_process|), 
	an ``AttributeError`` is raised. (Exception: ``demand_type`` and ``policy_type`` are allowed
	even though they are not attributes of |class_node|; see above.)


	.. note:: This function does not check that valid attributes have been provided for
		``demand_source``, ``inventory_policy``, and ``disruption_process``. For example,
		it does not check that a ``base_stock_level`` has been provided if the policy type
		is set to ``BS``.


	Parameters
	----------
	num_warehouses : int
		Number of warehouses in MWOR system.
	node_order_in_system : list, optional
		List of node indices in the order that they appear in the MWOR system,
		with warehouse nodes first and retailer node last. If omitted, the retailer
		will have index 0 and the warehouses will have indices 1, ..., ``num_warehouses``.
	node_order_in_lists : list, optional
		List of node indices in the order in which the nodes are listed in any
		attributes that are lists. (``node_order_in_lists[k]`` is the index of the ``k`` th node.)
	kwargs : optional
		Optional keyword arguments to specify node attributes.

	Raises
	------
	AttributeError
		If ``kwargs`` contains a parameter that is not an attribute of |class_node|.
	"""

	# Determine edges of network.
	if node_order_in_system is None:
		node_order_in_system = list(range(1, num_warehouses+1)) + [0]
	edges = [(node_order_in_system[k], node_order_in_system[-1]) for k in range(0, num_warehouses)]

	# Make local copy of kwarg dict.
	local_kwargs = copy.deepcopy(kwargs)
	# Set demand_source parameter so it only occurs at retailer node.
	if 'demand_source' not in local_kwargs:
		local_kwargs['demand_source'] = {}
	for n in node_order_in_system[0:-1]:
		local_kwargs['demand_source'][n] = DemandSource()

	# Determine node_order_in_lists.
	if node_order_in_lists is None:
		node_order_in_lists = node_order_in_system

	# Build network.
	return network_from_edges(
		edges=edges,
		node_order_in_lists=node_order_in_lists,
		**local_kwargs
	)


# ===============================================================================
# Local vs. Echelon Methods
# ===============================================================================

def local_to_echelon_base_stock_levels(network, S_local):
	"""Convert local base-stock levels to echelon base-stock levels for a serial system.

	Assumes network is serial system but does not assume anything about the
	labeling of the nodes.

	Parameters
	----------
	network : |class_network|
		The serial inventory network.
	S_local : dict
		Dict of local base-stock levels.

	Returns
	-------
	S_echelon : dict
		Dict of echelon base-stock levels.

	"""

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
	network : |class_network|
		The serial inventory network.
	S_echelon : dict
		Dict of echelon base-stock levels.

	Returns
	-------
	S_local : dict
		Dict of local base-stock levels.

	"""

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


