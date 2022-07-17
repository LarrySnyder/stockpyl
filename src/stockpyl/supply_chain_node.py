# ===============================================================================
# stockpyl - SupplyChainNode Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

This module contains the |class_node| class, which is a stage or node
in a supply chain network.

.. note:: |node_stage|

.. note:: |fosct_notation|

A |class_node| is used primarily for :ref:`multi-echelon inventory optimization (MEIO) <meio_page>`
or :ref:`simulation <sim_page>`. |class_node| objects are rarely, if ever, used as standalone objects;
rather, they are included in |class_network| objects, which describe the complete instance 
to be optimized or simulated. 

The node object contains many attributes, and different functions use different sets of attributes.
For example, the :func:`stockpyl.ssm_serial.optimize_base_stock_levels` function takes a
|class_network| whose nodes contain values for ``echelon_holding_cost``, ``lead_time``, ``stockout_cost``,
and ``demand_source`` attributes, while :func:`stockpyl.gsm_serial.optimize_committed_service_times`
uses ``local_holding_cost``, ``processing_time``, etc.
Therefore, to determine which attributes are needed, refer to the documentation for the function 
you are using.


API Reference
-------------


"""

# ===============================================================================
# Imports
# ===============================================================================

import numpy as np
import networkx as nx
from math import isclose
import copy
import math

from stockpyl import policy
from stockpyl import demand_source
from stockpyl import disruption_process
from stockpyl.helpers import change_dict_key, is_integer, is_list

# ===============================================================================
# SupplyChainNode Class
# ===============================================================================

class SupplyChainNode(object):
	"""The |class_node| class contains the data, state variables, and
	performance measures for a supply chain node.

	Attributes
	----------
	network : |class_network|
		The network that contains the node.
	local_holding_cost : float
		Local holding cost, per unit per period. [:math:`h'`]
	echelon_holding_cost : float
		Echelon holding cost, per unit per period. (**Note:** *not currently supported*.) [:math:`h`] 
	local_holding_cost_function : function
		Function that calculates local holding cost per period, as a function
		of ending inventory level. Function must take exactly one argument, the
		ending IL. Function should check that IL > 0.
	in_transit_holding_cost : float
		Holding cost coefficient used to calculate in-transit holding cost for
		shipments en route from the node to its downstream successors, if any.
		If ``in_transit_holding_cost`` is ``None``, then the stage's local_holding_cost
		is used. To ignore in-transit holding costs, set ``in_transit_holding_cost`` = 0.
	stockout_cost : float
		Stockout cost, per unit (per period, if backorders). [:math:`p`]
	stockout_cost_function : function
		Function that calculates stockout cost per period, as a function
		of ending inventory level. Function must take exactly one argument, the
		ending IL. Function should check that IL < 0.
	purchase_cost : float
		Cost incurred per unit. (**Note:** *not currently supported*.)
	revenue : float
		Revenue earned per unit of demand met. (**Note:** *not currently supported*.) [:math:`r`] 
	shipment_lead_time : int
		Shipment lead time. [:math:`L`]
	lead_time : int
		An alias for ``shipment_lead_time``.
	order_lead_time : int
		Order lead time.  (**Note:** *not currently supported*.) 
	demand_source : |class_demand_source|
		Demand source object.
	initial_inventory_level : float
		Initial inventory level.
	initial_orders : float
		Initial outbound order quantity.
	initial shipments : float
		Initial inbound shipment quantity.
	inventory_policy : |class_policy|
		Inventory policy to be used to make inventory decisions.
	supply_type : str
		Supply type , as a string. Currently supported strings are:

			* None
			* 'U': unlimited
			
	disruption_process : |class_disruption_process|
		Disruption process object (if any).
	state_vars : list of |class_state_vars|
		List of |class_state_vars|, one for each period in a simulation.
	problem_specific_data : object
		Placeholder for object that is used to provide data for specific
		problem types.
	"""

	def __init__(self, index, name=None, network=None, **kwargs):
		"""SupplyChainNode constructor method.

		Parameters
		----------
		index : int
			Numeric index to identify node. In a SupplyChainNetwork, each node
			must have a unique index.
		name : str, optional
			String to identify node.
		network : |class_network|
			The network that contains the node.
		kwargs : optional
			Optional keyword arguments to specify node attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match a |class_node| attribute.
		"""
		# Initialize attributes.
		self.initialize()

		# Set named attributes.
		self.index = index
		self.name = name
		self.network = network

		# Set attributes specified by kwargs.
		for key, value in kwargs.items():
			if key not in vars(self):
				raise AttributeError(f"{key} is not an attribute of SupplyChainNode")
			vars(self)[key] = value

	_DEFAULT_VALUES = {
		'index': None,
		'name': None,
		'network': None,
		'_predecessors': [],
		'_successors': [],
		'local_holding_cost': None,
		'echelon_holding_cost': None,
		'local_holding_cost_function': None,
		'in_transit_holding_cost': None,
		'stockout_cost': None,
		'stockout_cost_function': None,
		'revenue': None,
		'shipment_lead_time': None,
		'order_lead_time': None,
		'demand_source': None,
		'initial_inventory_level': None,
		'initial_orders': None,
		'initial_shipments': None,
		'inventory_policy': None,
		'supply_type': None,
		'disruption_process': None,
		'processing_time': None,
		'external_inbound_cst': None,
		'external_outbound_cst': None,
		'demand_bound_constant': None,
		'units_required': None,
		'original_label': None,
		'net_demand_mean': None,
		'net_demand_standard_deviation': None,
		'larger_adjacent_node': None,
		'larger_adjacent_node_is_downstream': None,
		'max_replenishment_time': None,
		'state_vars': []
	}

	# Properties and functions related to network structure.

	def predecessors(self, include_external=False):
		"""Return a list of all predecessors of the node, as |class_node| objects.

		Parameters
		----------
		include_external : bool, optional
			Include the external supplier (if any)? Default = ``False``.

		Returns
		-------
		list
			List of all predecessors, as |class_node| objects.
		"""
		if include_external and self.supply_type is not None:
			return self._predecessors + [None]
		else:
			return self._predecessors

	def successors(self, include_external=False):
		"""Return a list of all successors of the node, as |class_node| objects.

		Parameters
		----------
		include_external : bool, optional
			Include the external customer (if any)? Default = ``False``.

		Returns
		-------
		list
			List of all successors, as |class_node| objects.
		"""
		if include_external and \
				(self.demand_source is not None and self.demand_source.type is not None):
			return self._successors + [None]
		else:
			return self._successors

	def predecessor_indices(self, include_external=False):
		"""Return a list of indices of all predecessors of the node.

		Parameters
		----------
		include_external : bool, optional
			Include the external supplier (if any)? Default = ``False``.

		Returns
		-------
		list
			List of all predecessor indices.
		"""
		return [node.index if node else None for node in self.predecessors(include_external)]

	def successor_indices(self, include_external=False):
		"""Return a list of indices of all successors of the node.

		Parameters
		----------
		include_external : bool, optional
			Include the external customer (if any)? Default = ``False``.

		Returns
		-------
		list
			List of all successor indices.
		"""
		return [node.index if node else None for node in self.successors(include_external)]

	@property
	def descendants(self):
		"""A list of all descendants of the node, as |class_node| objects.
		A descendant is a node that is downstream from the node but not necessarily directly
		adjacent; that is, a node that can be reached from the node via a directed path. Read only.
		"""
		G = self.network.networkx_digraph()
		desc = nx.descendants(G, self.index)
		return [self.network.get_node_from_index(d) for d in desc]

	@property
	def ancestors(self):
		"""A list of all ancestors of the node, as |class_node| objects.
		An ancestor is a node that is upstream from the node but not necessarily directly
		adjacent; that is, a node from which we can reach the node via a directed path.
		Read only.
		"""
		G = self.network.networkx_digraph()
		anc = nx.ancestors(G, self.index)
		return [self.network.get_node_from_index(a) for a in anc]

	@property
	def neighbors(self):
		"""A list of all neighbors (successors and predecessors) of the node, as
		|class_node| objects. Read only.
		"""
		return list(set(self.successors()).union(set(self.predecessors())))

	@property
	def neighbor_indices(self):
		"""A list of indices of all neighbors (successors and predecessors) of the node.
		Read only.
		"""
		return [n.index for n in self.neighbors]

	# Properties related to input parameters.

	@property
	def holding_cost(self):
		"""An alias for ``local_holding_cost``. Read only.
		"""
		return self.local_holding_cost

	@property
	def lead_time(self):
		return self.shipment_lead_time

	@lead_time.setter
	def lead_time(self, value):
		self.shipment_lead_time = value

	@property
	def forward_echelon_lead_time(self):
		"""Total shipment lead time for node and all of its descendants.
		Rosling (1989) calls this :math:`M_i`; Zipkin (2000) calls it :math:`\\underline{L}_j`.
		Some assembly-system algorithms assume that the nodes are indexed
		in order of forward echelon lead time. Read only.
		"""
		return int(self.shipment_lead_time + np.sum([d.shipment_lead_time for d in self.descendants]))

	@property
	def equivalent_lead_time(self):
		"""Difference between forward echelon lead time for the node (node :math:`i`) and
		for node :math:`i-1`, where the nodes are indexed in non-decreasing order of
		forward_echelon_lead_time, consecutively.
		(If nodes are not indexed in this way, results will be unreliable.)
		
		If node is the smallest-indexed node in the network, equivalent lead
		time equals forward echelon lead time, which also equals shipment lead time.
		
		Rosling (1989) calls this :math:`L_i`; Zipkin (2000) calls it :math:`L''_j`.

		Read only.
		"""
		if self.index == np.min(self.network.node_indices):
			return self.forward_echelon_lead_time
		else:
			return self.forward_echelon_lead_time - \
				   self.network.get_node_from_index(self.index-1).forward_echelon_lead_time

	@property
	def derived_demand_mean(self):
		"""
		Mean of derived demand, i.e., external demand at node and all of its descendants.
		Read only.
		"""
		if self.demand_source is not None and self.demand_source.type == 'N':
			DDM = self.demand_source.mean
		else:
			DDM = 0
		for d in self.descendants:
			if d.demand_source is not None and d.demand_source.type == 'N':
				DDM += d.demand_source.mean
		return DDM

	@property
	def derived_demand_standard_deviation(self):
		"""
		Standard deviation of derived demand, i.e., external demand at node and all of its descendants.
		Read only.
		"""
		if self.demand_source is not None and self.demand_source.type == 'N':
			DDV = self.demand_source.standard_deviation ** 2
		else:
			DDV = 0
		for d in self.descendants:
			if d.demand_source is not None and d.demand_source.type == 'N':
				DDV += d.demand_source.standard_deviation ** 2
		return math.sqrt(DDV)

	# Properties related to state variables.

	@property
	def state_vars_current(self):
		"""
		An alias for the most recent set of state variables, i.e., for the
		current period. (Period is determined from ``self.network.period``). Read only.
		"""
		return self.state_vars[self.network.period]

	@property
	def disrupted(self):
		"""Is the node currently disrupted? 
		
		(Works even if the node has no |class_disruption_process| object in its
		``disruption_process`` attribute.)
		"""
		if self.disruption_process is None:
			return False
		else:
			return self.disruption_process.disrupted

	# Special methods.

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to the node. Two nodes are
		considered equal if their indices are equal.

		Parameters
		----------
		other : |class_node|
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
		other : |class_node|
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
		Return a string representation of the |class_node| instance.

		Returns
		-------
			A string representation of the |class_node| instance.

		"""
		return "SupplyChainNode({:s})".format(str(vars(self)))

	# Attribute management.

	def initialize(self):
		"""Initialize the parameters in the object to their default values. 
		Also initializes attributes that are objects (``demand_source``, ``disruption_process``, ``inventory_policy``):
		"""
		# Loop through attributes. Special handling for list and object attributes.
		for attr in self._DEFAULT_VALUES.keys():
			if attr == 'demand_source':
				self.demand_source = demand_source.DemandSource()
			elif attr == 'disruption_process':
				self.disruption_process = disruption_process.DisruptionProcess()
			elif attr == 'inventory_policy':
				self.inventory_policy = policy.Policy(node=self)
			elif is_list(self._DEFAULT_VALUES[attr]):
				setattr(self, attr, copy.deepcopy(self._DEFAULT_VALUES[attr]))
			else:
				setattr(self, attr, self._DEFAULT_VALUES[attr])

	def deep_equal_to(self, other, rel_tol=1e-8):
		"""Check whether node "deeply equals" ``other``, i.e., if all attributes are
		equal, including attributes that are themselves objects.
		
		Note the following caveats:

		* Does not check equality of ``network``. 
		* Checks predecessor and successor equality by index only. 
		* Does not check equality of ``local_holding_cost_function`` or ``stockout_cost_function``.
		* Does not check equality of ``state_vars``.

		Parameters
		----------
		other : |class_node|
			The node to compare this one to.
		rel_tol : float, optional
			Relative tolerance to use when comparing equality of float attributes.

		Returns
		-------
		bool
			``True`` if the two nodes are equal, ``False`` otherwise.
		"""

		# Initialize name of violating attribute (used for debugging) and equality flag.
		viol_attr = None
		eq = True
		
		if other is None:
			eq = False
		else:
			# Special handling for some attributes.
			for attr in self._DEFAULT_VALUES.keys():
				if attr in ('network', 'local_holding_cost_function', 'stockout_cost_function', 'state_vars'):
					# Ignore.
					pass
				elif attr == '_predecessors':
					# Only compare indices.
					if sorted(self.predecessor_indices()) != sorted(other.predecessor_indices()):
						viol_attr = attr
						eq = False
				elif attr == '_successors':
					# Only compare indices.
					if sorted(self.successor_indices()) != sorted(other.successor_indices()):
						viol_attr = attr
						eq = False
				elif attr in ('local_holding_cost', 'echelon_holding_cost', 'in_transit_holding_cost', \
					'stockout_cost', 'revenue', 'initial_inventory_level', 'initial_orders', 'initial_shipments' \
					'demand_bound_constant', 'units_required', 'net_demand_mean', 'net_demand_standard_deviation'):
					# These attributes need approximate comparisons.
					if not isclose(getattr(self, attr) or 0, getattr(other, attr) or 0, rel_tol=rel_tol):
						viol_attr = attr
						eq = False
				elif attr in ('demand_source', 'disruption_process', 'inventory_policy'):
					# Check for None in object or object type.
					if (getattr(self, attr) is None and getattr(other, attr) is not None) or \
						(getattr(self, attr) is not None and getattr(other, attr) is None) or \
						getattr(self, attr) != getattr(other, attr):
						viol_attr = attr
						eq = False
				else:
					if getattr(self, attr) != getattr(other, attr):
						viol_attr = attr
						eq = False

		return eq

	def to_dict(self):
		"""Convert the |class_node| object to a dict. Converts the object recursively,
		calling ``to_dict()`` on each object that is an attribute of the node 
		(|class_demand_source|, etc.).

		Successors and predecessors are stored as their indices only, not |class_node| objects.
		They should be replaced with the node objects if this function is called recursively
		from a |class_network|'s ``from_dict()`` method.

		Similarly, ``network`` object is not filled, but should be filled with the network object if this
		function is called recursively from a |class_network|'s ``from_dict()`` method.

		Returns
		-------
		dict
			The dict representation of the node.
		"""
		# Initialize dict.
		node_dict = {}

		# Attributes.
		for attr in self._DEFAULT_VALUES.keys():
			# A few attributes need special handling.
			if attr == 'network':
				node_dict[attr] = None
			elif attr == '_predecessors':
				node_dict[attr] = copy.deepcopy(self.predecessor_indices(include_external=True))
			elif attr == '_successors':
				node_dict[attr] = copy.deepcopy(self.successor_indices(include_external=True))
			elif attr in ('demand_source', 'disruption_process', 'inventory_policy'):
				node_dict[attr] = None if getattr(self, attr) is None else getattr(self, attr).to_dict()
			elif attr == 'state_vars':
				node_dict[attr] = None if self.state_vars is None else [sv.to_dict() for sv in self.state_vars]
			else:
				node_dict[attr] = getattr(self, attr)

		return node_dict
			
	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_node| object with attributes copied from the
		values in ``the_dict``. List attributes 
		are deep-copied so changes to the original dict do not get propagated to the object.
		
		``_predecessors`` and ``_successors`` attributes are set to the indices of the nodes,
		like they are in the dict, but should be converted to node objects if this
		function is called recursively from a |class_network|'s ``from_dict()`` method.

		Similarly, ``network`` object is not filled, but should be filled with the network object if this
		function is called recursively from a |class_network|'s ``from_dict()`` method.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_node|, typically created using ``to_dict()``.

		Returns
		-------
		SupplyChainNode
			The object converted from the dict.
		"""
		if the_dict is None:
			node = cls()
		else:
			# Build empty SupplyChainNode.
			node = cls(the_dict['index'])
			# Fill attributes.
			for attr in cls._DEFAULT_VALUES.keys():
				# Some attributes require special handling.
				if attr in ('_predecessors', '_successors'):
					if attr in the_dict:
						value = copy.deepcopy(the_dict[attr])
					else:
						value = copy.deepcopy(cls._DEFAULT_VALUES[attr])
				elif attr == 'demand_source':
					if attr in the_dict:
						value = demand_source.DemandSource.from_dict(the_dict[attr])
					else:
						value = demand_source.DemandSource.from_dict(None)
				elif attr == 'disruption_process':
					if attr in the_dict:
						value = disruption_process.DisruptionProcess.from_dict(the_dict[attr])
					else:
						value = disruption_process.DisruptionProcess.from_dict(None)
				elif attr == 'inventory_policy':
					if attr in the_dict:
						value = policy.Policy.from_dict(the_dict[attr])
					else:
						value = policy.Policy.from_dict(None)
					value.node = node
				elif attr == 'state_vars':
					if attr in the_dict:
						if the_dict[attr] is None:
							value = None
						else:
							value = [NodeStateVars.from_dict(sv) for sv in the_dict[attr]]
							for sv in value:
								sv.node = node
					else:
						value = cls._DEFAULT_VALUES[attr]
				else:
					if attr in the_dict:
						value = the_dict[attr]
					else:
						value = cls._DEFAULT_VALUES[attr]
				setattr(node, attr, value)
		
		return node
		
	# Neighbor management.

	def add_successor(self, successor):
		"""Add ``successor`` to the node's list of successors.

		.. important:: This method simply updates the node's list of successors. It does not
			add ``successor`` to the network or add ``self`` as a predecessor of
			``successor``. Typically, this method is called by the network rather
			than directly. Use the :meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.add_successor` method 
			in |class_network| instead.

		Parameters
		----------
		successor : |class_node|
			The node to add as a successor.

		"""
		self._successors.append(successor)

	def add_predecessor(self, predecessor):
		"""Add ``predecessor`` to the node's list of predecessors.

		.. important:: This method simply updates the node's list of predecessors. It does not
			add ``predecessor`` to the network or add ``self`` as a successor of
			``predecessor``. Typically, this method is called by the network rather
			than directly. Use the :meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.add_predecessor` method 
			in |class_network| instead.

		Parameters
		----------
		predecessor : |class_node|
			The node to add as a predecessor.

		"""
		self._predecessors.append(predecessor)

	def remove_successor(self, successor):
		"""Remove ``successor`` from the node's list of successors.

		.. important:: This method simply updates the node's list of successors. It does not
			remove ``successor`` from the network or remove ``self`` as a predecessor of
			``successor``. Typically, this method is called by the 
			:meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.remove_node` method of the 
			|class_network| rather than directly.

		Parameters
		----------
		successor : |class_node|
			The node to remove as a successor.

		"""
		self._successors.remove(successor)

	def remove_predecessor(self, predecessor):
		"""Remove ``predecessor`` from the node's list of predecessors.

		.. important:: This method simply updates the node's list of predecessors. It does not
			remove ``predecessor`` from the network or remove ``self`` as a successor of
			``predecessor``. Typically, this method is called by the 
			:meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.remove_node` method of the 
			|class_network| rather than directly.

		Parameters
		----------
		predecessor : |class_node|
			The node to remove as a predecessor.

		"""
		self._predecessors.remove(predecessor)

	def get_one_successor(self):
		"""Get one successor of the node. If the node has more than one
		successor, return the first in the list. If the node has no
		successors, return ``None``.

		Returns
		-------
		successor : |class_node|
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
		predecessor : |class_node|
			A predecessor of the node.
		"""
		if len(self._predecessors) == 0:
			return None
		else:
			return self._predecessors[0]

	# Attribute management.

	def _get_attribute_total(self, attribute, period, include_external=True):
		"""Return total of ``attribute`` in the node's ``state_vars`` for the period specified, for an
		attribute that is indexed by successor or predecessor, i.e.,
		``inbound_shipment``,`` on_order_by_predecessor``, ``inbound_order``, ``outbound_shipment``, 
		``backorders_by_successor``, ``outbound_disrupted_items``, ``inbound_disrupted_items``. 
		(If another attribute is specified, returns the value of the
		attribute, without any summation.)

		If ``period`` is ``None``, sums the attribute over all periods.

		If ``include_external`` is ``True``, includes the external supply or
		demand node (if any) in the total.

		Example: ``_get_attribute_total(inbound_shipment, 5)`` returns the total
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
		if attribute in ('inbound_shipment', 'on_order_by_predecessor', 'raw_material_inventory', 'inbound_disrupted_items'):
			# These attributes are indexed by predecessor.
			if period is None:
				return float(np.sum([self.state_vars[t].__dict__[attribute][p_index]
							   for t in range(len(self.state_vars))
							   for p_index in self.predecessor_indices(include_external=True)]))
			else:
				return float(np.sum([self.state_vars[period].__dict__[attribute][p_index]
							   for p_index in self.predecessor_indices(include_external=True)]))
		elif attribute in ('inbound_order', 'outbound_shipment', 'backorders_by_successor', 'outbound_disrupted_items'):
			# These attributes are indexed by successor.
			if period is None:
				return float(np.sum([self.state_vars[t].__dict__[attribute][s_index]
							   for t in range(len(self.state_vars))
							   for s_index in self.successor_indices(include_external=True)]))
			else:
				return float(np.sum([self.state_vars[period].__dict__[attribute][s_index]
							   for s_index in self.successor_indices(include_external=True)]))
		else:
			if period is None:
				return np.sum([self.state_vars[:].__dict__[attribute]])
			else:
				return self.state_vars[period].__dict__[attribute]

	def reindex_all_state_variables(self, old_to_new_dict):
		"""Change indices of all keys in all state variables using ``old_to_new_dict``.

		Parameters
		----------
		old_to_new_dict : dict
			Dict in which keys are old indices and values are new indices.

		"""
		for i in range(len(self.state_vars)):
			self.state_vars[i].reindex_state_variables(old_to_new_dict)


# ===============================================================================
# NodeStateVars Class
# ===============================================================================

class NodeStateVars(object):
	"""The |class_state_vars| class contains values of the state variables
	for a supply chain node during a :ref:`simulation <sim_page>`.
	All state variables refer to their values at the
	end of a period (except during the period itself, in which case the
	values might be intermediate until the period is complete).


	Attributes
	----------
	node : |class_node|
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
	demand_cumul : float
		Cumulative demand (from all sources, internal and external)
		from period 0 through the current period. (Used for ``fill_rate`` calculation.)
	outbound_shipment : dict
		``outbound_shipment[s]`` = outbound shipment to successor node ``s``.
		If ``s`` is ``None``, refers to external demand.
	on_order_by_predecessor : dict
		``on_order_by_predecessor[p]`` = on-order quantity (items that have been
		ordered from successor node ``p`` but not yet received) at node. If ``p`` is ``None``, refers to external supply.
	inventory_level : float
		Inventory level (positive, negative, or zero) at node 
	backorders_by_successor : dict
		``backorders_by_successor[s]`` = number of backorders for successor
		``s``. If ``s`` is ``None``, refers to external demand.
	outbound_disrupted_items : dict
		``outbound_disrupted_items[s]`` = number of items held for successor ``s``
		due to a type-SP disruption at ``s``. (Since external demand cannot be
		disrupted, ``outbound_disrupted_items[None]`` always = 0.) Items held for successor
		are not included in ``backorders_by_successor``.
		Sum over all successors of ``backorders_by_successor + outbound_disrupted_items``
		should always equal max{0, -``inventory_level``}. 
	inbound_disrupted_items : dict
		``inbound_disrupted_items[p]`` = number of items from predecessor ``p`` that are
		being held before receipt due to a type-RP disruption at the node. 
	raw_material_inventory : dict
		``raw_material_inventory[p]`` = number of units of predecessor ``p``'s
		product in raw-material inventory at node. If ``p`` is ``None``, refers
		to external supply.
	disrupted : bool
		``True`` if the node was disrupted in the period, ``False`` otherwise.
	holding_cost_incurred : float
		Holding cost incurred at the node in the period.
	stockout_cost_incurred : float
		Stockout cost incurred at the node in the period.
	in_transit_holding_cost_incurred : float
		In-transit holding cost incurred at the node in the period.
	revenue_earned : float
		Revenue earned at the node in the period.
	total_cost_incurred : float
		Total cost (less revenue) incurred at the node in the period.
	demand_met_from_stock : float
		Demands met from stock at the node in the period.
	demand_met_from_stock_cumul : float
		Cumulative demands met from stock from period 0 through the current period.
		(Used for ``fill_rate`` calculation.)
	fill_rate : float
		Cumulative fill rate in periods 0, ..., period.
	order_quantity : dict
		``order_quantity[p]`` = order quantity placed by the node to
		predecessor ``p`` in period. If ``p`` is ``None``, refers to external supply.
	"""

	def __init__(self, node=None, period=None):
		"""NodeStateVars constructor method.

		If ``node`` is provided, the state variable dicts (``inbound_shipment``,
		``inbound_order``, etc.) are initialized with the appropriate keys.
		Otherwise, they are set to empty dicts and must be initialized before
		using.

		Parameters
		----------
		node : |class_node|, optional
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

			# Initialize dicts with appropriate keys. (inbound_shipment_pipeline gets
			# order_lead_time+shipment_lead_time slots for orders to external supplier)
			self.inbound_shipment_pipeline = {p_index:
				[0] * ((self.node.order_lead_time or 0) + (self.node.shipment_lead_time or 0) + 1)
											for p_index in self.node.predecessor_indices(include_external=True)}
			self.inbound_shipment = {p_index: 0 for p_index in self.node.predecessor_indices(include_external=True)}
			self.inbound_order_pipeline = {s_index:
				[0] * ((self.node.network.get_node_from_index(s_index).order_lead_time or 0) + 1)
										   for s_index in node.successor_indices()}
			# Add external customer to inbound_order_pipeline. (Must be done
			# separately since external customer does not have its own node,
			# or its own order lead time.)
			if node.demand_source is not None and node.demand_source.type is not None:
				self.inbound_order_pipeline[None] = [0]
			self.inbound_order = {s_index: 0 for s_index in self.node.successor_indices(include_external=True)}
			self.outbound_shipment = {s_index: 0 for s_index in self.node.successor_indices(include_external=True)}
			self.on_order_by_predecessor = {p_index: 0 for p_index in self.node.predecessor_indices(include_external=True)}
			self.backorders_by_successor = {s_index: 0 for s_index in self.node.successor_indices(include_external=True)}
			self.outbound_disrupted_items = {s_index: 0 for s_index in self.node.successor_indices(include_external=True)}
			self.inbound_disrupted_items = {p_index: 0 for p_index in self.node.predecessor_indices(include_external=True)}
			self.order_quantity = {p_index: 0 for p_index in self.node.predecessor_indices(include_external=True)}
			self.raw_material_inventory = {p_index: 0 for p_index in self.node.predecessor_indices(include_external=True)}

		else:

			# Initialize dicts to empty dicts.
			self.inbound_shipment_pipeline = {}
			self.inbound_shipment = {}
			self.inbound_order_pipeline = {}
			self.inbound_order = {}
			self.outbound_shipment = {}
			self.on_order_by_predecessor = {}
			self.backorders_by_successor = {}
			self.outbound_disrupted_items = {}
			self.inbound_disrupted_items = {}
			self.order_quantity = {}
			self.raw_material_inventory = {}

		# Remaining state variables.
		self.inventory_level = 0
		self.disrupted = False

		# Costs: each refers to a component of the cost (or the total cost)
		# incurred at the node in the period.
		self.holding_cost_incurred = 0
		self.stockout_cost_incurred = 0
		self.in_transit_holding_cost_incurred = 0
		self.revenue_earned = 0
		self.total_cost_incurred = 0

		# Fill rate quantities.
		self.demand_cumul = 0
		self.demand_met_from_stock = 0
		self.demand_met_from_stock_cumul = 0
		self.fill_rate = 0

	# --- Special Methods --- #

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to the state variables object. Two objects are
		considered equal if they are deeply-equal to each other.

		Parameters
		----------
		other : |class_state_vars|
			The state variables object to compare to.

		Returns
		-------
		bool
			True if the state variables objects are equal, False otherwise.

		"""
		return self.deep_equal_to(other)

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to the state variables object. Two objects are
		considered equal if they are deeply-equal to each other.

		Parameters
		----------
		other : |class_state_vars|
			The state variables object to compare to.

		Returns
		-------
		bool
			True if the state variables objects are not equal, False otherwise.

		"""
		return not self.__eq__(other)

	# --- Calculated State Variables --- #
	# These are calculated based on the primary state variables.

	@property
	def on_hand(self):
		"""Current on-hand inventory. Read only.
		"""
		return max(0, self.inventory_level)

	@property
	def backorders(self):
		"""Current number of backorders. Should always equal sum over all successors ``s``
		of ``backorders_by_successor[s]`` + ``outbound_disrupted_items[s]``.  Read only.
		"""
		return max(0, -self.inventory_level)

	def in_transit_to(self, successor):
		"""Return current total inventory in transit to a given successor.
		(Declared as a function, not a property, because needs to take an argument.)
		Includes items that will be/have been delivered during the current period.

		Parameters
		----------
		successor : |class_node|
			The successor node.

		Returns
		-------
			The current inventory in transit to the successor.
		"""
		return np.sum([successor.state_vars[self.period].inbound_shipment_pipeline[self.node.index][:]])

	def in_transit_from(self, predecessor):
		"""Return current total inventory in transit from a given predecessor.
		(Declared as a function, not a property, because needs to take an argument.)
		Includes items that will be/have been delivered during the current period
		(``self.network.period``).

		Parameters
		----------
		predecessor : |class_node|
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

	@property
	def in_transit(self):
		"""Current total inventory in transit to the node. If node has
		more than 1 predecessor (it is an assembly node), including external supplier,
		in-transit items are counted using the "units" of the node itself.
		That is, they are divided by the total number of predecessors. Read only.
		"""
		total_in_transit = np.sum([self.in_transit_from(p)
								   for p in self.node.predecessors(include_external=True)])
		if total_in_transit == 0:
			return 0
		else:
			return total_in_transit / len(self.node.predecessors(include_external=True))

	@property
	def on_order(self):
		"""Current total on-order quantity. If node has more than 1
		predecessor (it is an assembly node), including external supplier,
		on-order items are counted using the "units" of the node itself.
		That is, they are divided by the total number of predecessors. Read only.
		"""
		total_on_order = self.node._get_attribute_total('on_order_by_predecessor',
												  self.period,
												  include_external=True)
		if total_on_order == 0:
			return 0
		else:
			return total_on_order / len(self.node.predecessors(include_external=True))

	@property
	def raw_material_aggregate(self):
		"""Total raw materials at the node. Raw materials
		are counted using the "units" of the node itself. That is, they are
		divided by the total number of predecessors. Read only.
		"""
		total_raw_material = self.node._get_attribute_total('raw_material_inventory',
															self.period,
															include_external=True)
		if total_raw_material == 0:
			return 0
		else:
			return total_raw_material / len(self.node.predecessors(include_external=True))

	@property
	def inbound_disrupted_items_aggregate(self):
		"""Total inbound disrupted items at the node. Inbound disrupted items
		are counted using the "units" of the node itself. That is, they are
		divided by the total number of predecessors. Read only.
		"""
		total_raw_material = self.node._get_attribute_total('inbound_disrupted_items',
															self.period,
															include_external=True)
		if total_raw_material == 0:
			return 0
		else:
			return total_raw_material / len(self.node.predecessors(include_external=True))

	def inventory_position(self, predecessor_index=None):
		"""Current local inventory position at node. Equals inventory level plus
		on-order inventory. 
		On-order includes raw material inventory that has not yet been processed, as
		well as inbound disrupted items due to type-RP disruptions.
		If the node has more than one predecessor (including external supplier),
		set ``predecessor_index`` for predecessor-specific inventory position, or set to ``None``
		to use aggregate on-order and raw material inventory (counting such
		items using the "units" of the node itself).

		Parameters
		----------
		predecessor_index : int, optional
			Predecessor to consider in inventory position calculation (excluding all others),
			or ``None`` to include all predecessors.

		Returns
		-------
		float
			The inventory position.		
		"""
		if predecessor_index is not None:
			return self.inventory_level \
					+ self.on_order_by_predecessor[predecessor_index] \
					+ self.raw_material_inventory[predecessor_index] \
					+ self.inbound_disrupted_items[predecessor_index]
		else:
			# Note: If <=1 predecessor, raw_material_inventory should always = 0.
			return self.inventory_level + self.on_order + self.raw_material_aggregate \
					+ self.inbound_disrupted_items_aggregate

	@property
	def echelon_on_hand_inventory(self):
		"""Current echelon on-hand inventory at node. Equals on-hand inventory at node 
		and at or in transit to all of its downstream nodes. Read only.
		"""
		EOHI = self.on_hand
		for d in self.node.descendants:
			EOHI += d.state_vars[self.period].on_hand
			# Add in-transit quantity from predecessors that are descendents
			# of self (or equal to self).
			for p in d.predecessors():
				if p.index == self.node.index or p in self.node.descendants:
					EOHI += d.state_vars[self.period].in_transit_from(p)
		return EOHI

	@property
	def echelon_inventory_level(self):
		"""Current echelon inventory level at node. Equals echelon on-hand inventory 
		minus backorders at terminal node(s) downstream from node. Read only.
		"""
		EIL = self.echelon_on_hand_inventory
		for d in self.node.descendants + [self.node]:
			if d in self.node.network.sink_nodes:
				EIL -= d.state_vars[self.period].backorders
		return EIL

	def echelon_inventory_position(self, predecessor_index=None):
		"""Current echelon inventory position at node. Equals echelon inventory level plus
		on order items. On-order includes raw material inventory that has not yet been processed.
		If the node has more than one predecessor (including external supplier),
		set ``predecessor_index`` for predecessor-specific inventory position, or set to ``None``
		to use aggregate on-order and raw material inventory (counting such
		items using the "units" of the node itself).

		Parameters
		----------
		predecessor_index : int, optional
			Predecessor to consider in inventory position calculation (excluding all others),
			or ``None`` to include all predecessors.

		Returns
		-------
		float
			The echelon inventory position.
		"""
		if predecessor_index is not None:
			return self.echelon_inventory_level \
					+ self.on_order_by_predecessor[predecessor_index] \
					+ self.raw_material_inventory[predecessor_index]
		else:
			# Note: If <=1 predecessor, raw_material_inventory should always = 0.
			return self.echelon_inventory_level + self.on_order + self.raw_material_aggregate

	def _echelon_inventory_position_adjusted(self):
		"""Calculate the adjusted echelon inventory position. Equals the current echelon inventory position
		including only items ordered :math:`L_i` periods ago or earlier, where :math:`L_i` is the
		forward echelon lead time for the node. That is, equals current echelon inventory level
		plus items ordered :math:`L_i` periods ago or earlier.

		Rosling (1989) calls this :math:`X^L_{it}`; Zipkin (2000) calls it :math:`IN^+_j(t)`.

		Assumes there are no order lead times.

		This quantity is used (only?) for balanced echelon base-stock policies.
		Nodes are assumed to be indexed consecutively in non-decreasing order of
		forward echelon lead time.
	
		Note: Balanced echelon base-stock policy assumes a node never orders
		more than its predecessor can ship; therefore, # of items shipped in a
		given interval is the same as # of items ordered. In addition, there
		are no raw-material inventories.

		Returns
		-------
		float
			The adjusted echelon inventory position.
		"""
		# Calculate portion of in-transit inventory that was ordered L_i periods
		# ago or earlier.
		# Since order quantity to all predecessors is the same, choose one arbitrarily
		# and get order quantities for that predecessor.
		in_transit_adjusted = 0
		pred = self.node.get_one_predecessor()
		if pred is None:
			pred_index = None
		else:
			pred_index = pred.index
		for t in range(self.node.equivalent_lead_time, self.node.shipment_lead_time):
			if self.node.network.period - t >= 0:
				in_transit_adjusted += self.node.state_vars[self.node.network.period-t].order_quantity[pred_index]
			# np.sum([self.node.state_vars[self.node.network.period-t].order_quantity[predecessor_index]
			# 		for t in range(self.node.equivalent_lead_time, self.node.shipment_lead_time)])
		# Calculate adjusted echelon inventory position.
		return self.echelon_inventory_level + in_transit_adjusted

	# --- Conversion to/from Dicts --- #

	def to_dict(self):
		"""Convert the |class_state_vars| object to a dict. List and dict attributes
		are deep-copied so changes to the original object do not get propagated to the dict.
 		The ``node`` attribute is set to the index of the node (if any), rather than to the object.

		Returns
		-------
		dict
			The dict representation of the object.
		"""
		# Initialize dict.
		sv_dict = {}

		# Attributes.
		sv_dict['node'] 							= self.node.index
		sv_dict['period']							= self.period
		sv_dict['inbound_shipment_pipeline']		= copy.deepcopy(self.inbound_shipment_pipeline)
		sv_dict['inbound_shipment']					= copy.deepcopy(self.inbound_shipment)
		sv_dict['inbound_order_pipeline']			= copy.deepcopy(self.inbound_order_pipeline)
		sv_dict['inbound_order']					= copy.deepcopy(self.inbound_order)
		sv_dict['outbound_shipment']				= copy.deepcopy(self.outbound_shipment)
		sv_dict['on_order_by_predecessor']			= copy.deepcopy(self.on_order_by_predecessor)
		sv_dict['backorders_by_successor']			= copy.deepcopy(self.backorders_by_successor)
		sv_dict['outbound_disrupted_items']			= copy.deepcopy(self.outbound_disrupted_items)
		sv_dict['inbound_disrupted_items']			= copy.deepcopy(self.inbound_disrupted_items)
		sv_dict['order_quantity']					= copy.deepcopy(self.order_quantity)
		sv_dict['raw_material_inventory']			= copy.deepcopy(self.raw_material_inventory)
		sv_dict['inventory_level'] 					= self.inventory_level
		sv_dict['disrupted'] 						= self.disrupted
		sv_dict['holding_cost_incurred'] 			= self.holding_cost_incurred
		sv_dict['stockout_cost_incurred'] 			= self.stockout_cost_incurred
		sv_dict['in_transit_holding_cost_incurred']	= self.in_transit_holding_cost_incurred
		sv_dict['revenue_earned'] 					= self.revenue_earned
		sv_dict['total_cost_incurred'] 				= self.total_cost_incurred
		sv_dict['demand_cumul'] 					= self.demand_cumul
		sv_dict['demand_met_from_stock'] 			= self.demand_met_from_stock
		sv_dict['demand_met_from_stock_cumul'] 		= self.demand_met_from_stock_cumul
		sv_dict['fill_rate'] 						= self.fill_rate

		return sv_dict

	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_state_vars| object with attributes copied from the
		values in ``the_dict``. List and dict attributes 
		are deep-copied so changes to the original dict do not get propagated to the object.
		
		The ``node`` attribute is set to the index of the node,
		like it is in the dict, but should be converted to a node object if this
		function is called recursively from a |class_node|'s ``from_dict()`` method.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_state_vars|, typically created using ``to_dict()``.

		Returns
		-------
		NodeStateVars
			The object converted from the dict.
		"""
		if the_dict is None:
			nsv = None
		else:
			nsv = NodeStateVars()

			nsv.node 								= the_dict['node']
			nsv.period								= the_dict['period']
			nsv.inbound_shipment_pipeline			= copy.deepcopy(the_dict['inbound_shipment_pipeline'])
			nsv.inbound_shipment					= copy.deepcopy(the_dict['inbound_shipment'])
			nsv.inbound_order_pipeline				= copy.deepcopy(the_dict['inbound_order_pipeline'])
			nsv.inbound_order						= copy.deepcopy(the_dict['inbound_order'])
			nsv.outbound_shipment					= copy.deepcopy(the_dict['outbound_shipment'])
			nsv.on_order_by_predecessor				= copy.deepcopy(the_dict['on_order_by_predecessor'])
			nsv.backorders_by_successor				= copy.deepcopy(the_dict['backorders_by_successor'])
			nsv.outbound_disrupted_items			= copy.deepcopy(the_dict['outbound_disrupted_items'])
			nsv.inbound_disrupted_items				= copy.deepcopy(the_dict['inbound_disrupted_items'])
			nsv.order_quantity						= copy.deepcopy(the_dict['order_quantity'])
			nsv.raw_material_inventory				= copy.deepcopy(the_dict['raw_material_inventory'])
			nsv.inventory_level						= the_dict['inventory_level']
			nsv.disrupted							= the_dict['disrupted']
			nsv.holding_cost_incurred				= the_dict['holding_cost_incurred']
			nsv.stockout_cost_incurred				= the_dict['stockout_cost_incurred']
			nsv.in_transit_holding_cost_incurred	= the_dict['in_transit_holding_cost_incurred']
			nsv.revenue_earned						= the_dict['revenue_earned']
			nsv.total_cost_incurred					= the_dict['total_cost_incurred']
			nsv.demand_cumul						= the_dict['demand_cumul']
			nsv.demand_met_from_stock				= the_dict['demand_met_from_stock']
			nsv.demand_met_from_stock_cumul			= the_dict['demand_met_from_stock_cumul']
			nsv.fill_rate							= the_dict['fill_rate']

		return nsv


	# --- Utility Functions --- #

	def reindex_state_variables(self, old_to_new_dict):
		"""Change indices of state variable dict keys using ``old_to_new_dict``.

		Parameters
		----------
		old_to_new_dict : dict
			Dict in which keys are old indices and values are new indices.

		"""
		# State variables indexed by predecessor.
		for p in self.node.predecessors(include_external=False):
			change_dict_key(self.inbound_shipment_pipeline, p.index, old_to_new_dict[p.index])
			change_dict_key(self.inbound_shipment, p.index, old_to_new_dict[p.index])
			change_dict_key(self.on_order_by_predecessor, p.index, old_to_new_dict[p.index])
			change_dict_key(self.raw_material_inventory, p.index, old_to_new_dict[p.index])
			change_dict_key(self.order_quantity, p.index, old_to_new_dict[p.index])
			change_dict_key(self.inbound_disrupted_items, p.index, old_to_new_dict[p.index])

		# State variables indexed by successor.
		for s in self.node.successors(include_external=False):
			change_dict_key(self.inbound_order_pipeline, s.index, old_to_new_dict[s.index])
			change_dict_key(self.inbound_order, s.index, old_to_new_dict[s.index])
			change_dict_key(self.outbound_shipment, s.index, old_to_new_dict[s.index])
			change_dict_key(self.backorders_by_successor, s.index, old_to_new_dict[s.index])
			change_dict_key(self.outbound_disrupted_items, s.index, old_to_new_dict[s.index])

	def deep_equal_to(self, other, rel_tol=1e-8):
		"""Check whether object "deeply equals" ``other``, i.e., if all attributes are
		equal, including attributes that are lists or dicts.
		
		Note the following caveats:

		* Checks the equality of ``node.index`` but not the entire ``node`` object.

		Parameters
		----------
		other : |class_state_vars|
			The state variables to compare this one to.
		rel_tol : float, optional
			Relative tolerance to use when comparing equality of float attributes.

		Returns
		-------
		bool
			``True`` if the two state variables objects are equal, ``False`` otherwise.
		"""

		if (self.node is not None and other.node is None) or (self.node is None and other.node is not None): return False
		if self.node is not None and other.node is not None:
			if is_integer(self.node) and is_integer(other.node):
				if self.node != other.node: return False
			elif not is_integer(self.node) and not is_integer(other.node):
				if self.node.index != other.node.index: return False
			else: 
				return False
		if self.period != other.period: return False
		if self.inbound_shipment_pipeline != other.inbound_shipment_pipeline: return False
		if self.inbound_shipment != other.inbound_shipment: return False
		if self.inbound_order_pipeline != other.inbound_order_pipeline: return False
		if self.inbound_order != other.inbound_order: return False
		if self.outbound_shipment != other.outbound_shipment: return False
		if self.on_order_by_predecessor != other.on_order_by_predecessor: return False
		if self.backorders_by_successor != other.backorders_by_successor: return False
		if self.outbound_disrupted_items != other.outbound_disrupted_items: return False
		if self.inbound_disrupted_items != other.inbound_disrupted_items: return False
		if self.order_quantity != other.order_quantity: return False
		if self.raw_material_inventory != other.raw_material_inventory: return False
		if self.inventory_level != other.inventory_level: return False
		if self.disrupted != other.disrupted: return False
		if self.holding_cost_incurred != other.holding_cost_incurred: return False
		if self.stockout_cost_incurred != other.stockout_cost_incurred: return False
		if self.in_transit_holding_cost_incurred != other.in_transit_holding_cost_incurred: return False
		if self.revenue_earned != other.revenue_earned: return False
		if self.total_cost_incurred != other.total_cost_incurred: return False
		if self.demand_cumul != other.demand_cumul: return False
		if self.demand_met_from_stock != other.demand_met_from_stock: return False
		if self.demand_met_from_stock_cumul != other.demand_met_from_stock_cumul: return False
		if self.fill_rate != other.fill_rate: return False

		return True

