# ===============================================================================
# stockpyl - SupplyChainNetwork Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview
--------

This module contains the |class_network| class, which is a network consisting of
one or more nodes and, optionally, one or more products. The network, nodes, and
products together specify a problem instance.

.. note:: |node_stage|

.. note:: |fosct_notation|

A |class_network| is used primarily for :ref:`multi-echelon inventory optimization (MEIO) <meio_page>`
or :ref:`simulation <sim_page>`. Most data for the problem instance is specified
in the |class_node| and |class_product| objects contained within the |class_network|, rather than in
the network itself.


API Reference
-------------

"""

# ===============================================================================
# Imports
# ===============================================================================

import networkx as nx
import numpy as np
# import json
import copy
from collections import Counter
import warnings


#import supply_chain_node
from stockpyl.supply_chain_node import SupplyChainNode
from stockpyl.supply_chain_product import SupplyChainProduct
from stockpyl.demand_source import DemandSource
from stockpyl.policy import Policy
from stockpyl.disruption_process import DisruptionProcess
from stockpyl.helpers import is_list, is_dict, is_integer, is_iterable, is_set, ensure_dict_for_nodes, ensure_list_for_nodes
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

	_DEFAULT_VALUES = {
		'_nodes': [], # TODO: remove this, just use _nodes_by_index.values()
		'_products': [],					# all products (loaded directly or into nodes) 
		'_local_product_indices': [],		# only includes products that are loaded directly into the network; they may or may not also be loaded into nodes
		'_period': 0,
		'max_max_replenishment_time': None
	}

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
	def nodes_by_index(self):
		"""A dict containing nodes in the network. The keys of the dict are
		node indices and the values are the corresponding |class_node| objects.
		For example, ``self.nodes_by_index[4]`` is a |class_node| object 
		with index 4. Read only."""
		return self._nodes_by_index

	@property
	def products(self):
		"""List of all products in the network, as |class_product| objects. Includes products
		that have been explicitly added to the network via :func:`add_product` as well as products
		that are handled by the nodes in the network. Read only.
		"""
		return self._products

	@property
	def product_indices(self):
		"""List of indices of all products in the network. Includes products
		that have been explicitly added to the network via :func:`add_product` as well as products
		that are handled by the nodes in the network. Read only.
		"""
		return self._product_indices

	@property
	def products_by_index(self):
		"""A dict containing products in the network. Includes products that have been explicitly
		added to the network via :func:`add_product` as well as products that are handled by the nodes
		in the network.
		
		The keys of the dict are
		product indices and the values are the corresponding |class_product| objects.
		For example, ``self.products_by_index[4]`` returns a |class_product| object for the product 
		with index 4. 

		Includes "dummy products" that are added internally to nodes that do not have a |class_product|
		object added. Dummy products are identifiable as such by their index, which is always negative.
	
		Read only. 
		"""
		return self._products_by_index

	@property
	def period(self):
		return self._period

	@period.setter
	def period(self, value):
		self._period = value

	@property
	def source_nodes(self):
		"""List of all source nodes, i.e., all nodes that have no predecessors,
		as |class_node| objects. Read only.
		"""
		return [node for node in self.nodes if len(node.predecessor_indices()) == 0]

	@property
	def sink_nodes(self):
		"""List of all sink nodes, i.e., all nodes that have no successors,
		as |class_node| objects. Read only.
		"""
		return [node for node in self.nodes if len(node.successor_indices()) == 0]

	@property
	def edges(self):
		"""List of all edges, as tuples whose elements are the indices of
		the nodes in the edge. Read only.
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
		return f'SupplyChainNetwork(nodes={self.node_indices}, products={self.product_indices})'
#		return "SupplyChainNetwork({:s})".format(str(vars(self)))

	# Attribute management.

	def initialize(self):
		"""Initialize the parameters in the object to their default values.
		"""
		# Loop through attributes. Special handling for list and dict attributes.
		for attr in self._DEFAULT_VALUES.keys():
			if is_list(self._DEFAULT_VALUES[attr]) or is_dict(self._DEFAULT_VALUES[attr]) \
				or is_set(self._DEFAULT_VALUES[attr]):
				setattr(self, attr, copy.deepcopy(self._DEFAULT_VALUES[attr]))
			else:
				setattr(self, attr, self._DEFAULT_VALUES[attr])

		# Set _currently_building flag. (This indicates whether we are currently building
 		# a network, e.g., using from_dict(), in which case we should pause buidling product attributes.)
		self._currently_building = False

		# Initialize node- and product-related attributes that are derived from others.
		self._build_node_attributes()
		self._build_product_attributes()

	# # --- Nodes and Period --- #
	# if overwrite or not hasattr(self, '_nodes'):
	# 	self._nodes = []
	# elif is_list(self._nodes):
	# 	for n in self._nodes:
	# 		n.initialize(overwrite=False)
	# if overwrite or not hasattr(self, '_period'):
	# 	self._period = 0

	# # --- Intermediate Calculations for GSM Problems --- #
	# if overwrite or not hasattr(self, 'max_max_replenishment_time'):
	# 	self.max_max_replenishment_time = None

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

		eq = True

		if sorted(self.node_indices) != sorted(other.node_indices):
			eq = False
		else:
			# # Replace None with -1 in both node's product indices because None can't be sorted.
			# self_indices = [prod_ind if prod_ind is not None else -1 for prod_ind in self.product_indices]
			if set(self.product_indices) != set(other.product_indices):
				eq = False
			else:
				# Special handling for some attributes.
				for attr in self._DEFAULT_VALUES.keys():
					if attr == '_nodes':
						for n_ind in sorted(self.node_indices):
							other_node = other.nodes_by_index[n_ind]
							if other_node is None:
								eq = False
							elif not self.nodes_by_index[n_ind].deep_equal_to(other_node, rel_tol=rel_tol):
								eq = False
					elif attr == '_products':
						# Check that lists of indices are equal (ignoring order).
						if Counter([prod.index for prod in self._products]) != Counter([prod.index for prod in other._products]):
							eq = False
						for prod in self._products:
							other_prod = other.products_by_index[prod.index]
							if not prod.deep_equal_to(other_prod, rel_tol=rel_tol):
								eq = False
					elif attr == '_local_product_indices':
						# Check that lists of indices are equal (ignoring order).
						if Counter([prod_ind for prod_ind in self._local_product_indices]) != Counter([prod_ind for prod_ind in other._local_product_indices]):
							eq = False
						# for prod in self._local_products:
						# 	other_prod = other.products_by_index[prod.index]
						# 	if not prod.deep_equal_to(other_prod, rel_tol=rel_tol):
						# 		eq = False
						# for prod in self._local_products:						
						# 	other_prod = other.products_by_index[prod.index]
						# 	if other_prod is None:
						# 		eq = False
						# 	elif not self.products_by_index[prod.index].deep_equal_to(other_prod, rel_tol=rel_tol):
						# 		eq = False
					else:
						if getattr(self, attr) != getattr(other, attr):
							eq = False

		return eq

	def to_dict(self):
		"""Convert the |class_network| object to a dict. Converts the object recursively,
		calling ``to_dict()`` on each |class_node| in the network.

		Returns
		-------
		dict
			The dict representation of the network.
		"""
		# Initialize dict.
		network_dict = {}

		# Attributes.
		for attr in self._DEFAULT_VALUES.keys():
			# Remove leading '_' to get property names.
#			prop = attr[1:] if attr[0] == '_' else attr
			if attr == '_nodes':
				network_dict['_nodes'] = [node.to_dict() for node in self.nodes]
			elif attr == '_products':
				network_dict[attr] = [prod.to_dict() for prod in self.products]
			elif attr == '_local_product_indices':
				network_dict[attr] = copy.deepcopy(self._local_product_indices)
			else:
				network_dict[attr] = getattr(self, attr)

		return network_dict

	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_network| object with attributes copied from the
		values in ``the_dict``.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_network|, typically created using ``to_dict()``.

		Returns
		-------
		SupplyChainNetwork
			The object converted from the dict.
		"""
		if the_dict is None:
			network = cls()
		else:
			# Build empty SupplyChainNetwork.
			network = cls()

			# Fill product info first.
			if '_products' not in the_dict:
				network._products = copy.deepcopy(cls._DEFAULT_VALUES['_products'])
			else:
				for prod_dict in the_dict['_products']:
					network.add_product(SupplyChainProduct.from_dict(prod_dict))
			# 	network._products = [SupplyChainProduct.from_dict(prod_dict) for prod_dict in the_dict['_products']]
			# network._product_indices = [prod.index for prod in network._products]
			# network._products_by_index = {prod.index: prod for prod in network._products}

			# Set _currently_building flag so we don't re-build product attributes in the next step.
			network._currently_building = True

   			# Fill attributes. 
			for attr in cls._DEFAULT_VALUES.keys():
				if attr == '_nodes':
					if '_nodes' not in the_dict:
						network._nodes = copy.deepcopy(cls._DEFAULT_VALUES['_nodes'])
					else:
						for n_dict in the_dict['_nodes']:
							# Create node. 
							node = SupplyChainNode.from_dict(n_dict)
							# Add node to network.
							network.add_node(node)
							# Get list of product indices at the node.
							prod_indices = copy.deepcopy(node._product_indices)
							# Remove all products from node and add them according to prod_indices. 
							node.remove_products('all')
							for prod_ind in prod_indices:
								node.add_product(network._products_by_index[prod_ind])
							# Replace external supplier dummy-product index with product object.
							if node._external_supplier_dummy_product is not None:
								node._external_supplier_dummy_product = network._products_by_index[node._external_supplier_dummy_product]
				elif attr == '_products':
					# We already handled this.
					pass
				else:
					if attr in the_dict:
						if is_dict(the_dict[attr]) or is_set(the_dict[attr]) or is_list(the_dict[attr]):
							value = copy.deepcopy(the_dict[attr])
						else:
							value = the_dict[attr]
					else:
						if attr in the_dict:
							value = copy.deepcopy(cls._DEFAULT_VALUES[attr])
						else:
							value = cls._DEFAULT_VALUES[attr]

					# # Remove leading '_' to get property names.
					# prop = attr[1:] if attr[0] == '_' else attr
					# if prop in the_dict:
					# 	value = the_dict[prop]
					# else:
					# 	value = cls._DEFAULT_VALUES[attr]
					setattr(network, attr, value)

		# Turn off _currently_building flag and build product-related attributes.
		network._currently_building = False
		network._build_node_attributes()
		network._build_product_attributes()

		return network

	# Methods for node handling.

	def get_node_from_index(self, index):
		"""Return |class_node| object with the specified index, or ``None`` if no
		matching node is found.

		.. deprecated:: 1.1
			Use ``node_from_index`` instead.

		Parameters
		----------
		index : int
			Index of node to find.

		Returns
		-------
		|class_node|
			The node whose index is ``index``, or ``None`` if none.

		"""
		warnings.warn('SupplyChainNetwork.get_node_from_index() is deprecated. Use SupplyChainNetwork.nodes_by_index instead.', DeprecationWarning, stacklevel=2)
			
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
		# Remember value of _currently_building flag, and turn it on to avoid building product attributes prematurely.
		old_currently_building = self._currently_building
		self._currently_building = True
		
		# Build product mapping. (Real products keep their indices. Dummy products change
  		# because their nodes change.)
		old_to_new_prod_dict = {}
		for node in self.nodes:
			for prod in node.products:
				if prod.is_dummy:
					old_to_new_prod_dict[prod.index] = \
						SupplyChainNode._dummy_product_index_from_node_index(old_to_new_dict[node.index])
				else:
					old_to_new_prod_dict[prod.index] = prod.index
			old_to_new_prod_dict[node._external_supplier_dummy_product.index] = \
				SupplyChainNode._external_supplier_dummy_product_index_from_node_index(old_to_new_dict[node.index])
	
		# Reindex state variables. (This must be done before reindexing nodes.)
		for node in self.nodes:
			node.reindex_all_state_variables(old_to_new_dict, old_to_new_prod_dict)

		# Reindex nodes.
		for node in self.nodes:
			# Reindex node.
			old_index = node.index
			node.index = old_to_new_dict[old_index]
			# Reindex predecessors and successors.
			node._predecessor_indices = [old_to_new_dict[p] for p in node._predecessor_indices]
			node._successor_indices = [old_to_new_dict[s] for s in node._successor_indices]
			# Rename node.
			if new_names is not None:
				node.name = new_names[old_index]

		# Rebuild product attributes.
		self._currently_building = old_currently_building
		self._build_node_attributes()
		self._build_product_attributes()

	# Methods related to network structure.

	def _build_node_attributes(self):
		"""Build node-related attributes that are derived from other attributes.
		These attributes are built each time the nodes or products change, rather than 
		deriving them live during a simulation.

		Does nothing if self._currently_building is True. (This is to avoid building
  		node attributes when network is currently being built and not all product/node
		info is in place yet.)
		"""
		if not self._currently_building:
			# Build _nodes_by_index.
			self._nodes_by_index = {n.index: n for n in self.nodes}
			# Add None: None.
			self._nodes_by_index.update({None: None})

	def add_node(self, node):
		"""Add ``node`` to the network. ``node`` will not be connected to other
		nodes that might be in the network already unless it has already been set as
		a predecessor or successor to another node in the network.

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
			for prod in node.products:
				# Fill network attribute, unless prod is an integer. 
				# (This can happen when building a network using from_dict(), because
				# _product_by_index values are replaced with ints in to_dict().)
				if not is_integer(prod):		
					prod.network = self

			# Rebuild node and product attributes.
			self._build_node_attributes()
			self._build_product_attributes()

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
			from_node = self.nodes_by_index[from_index]
			to_node = self.nodes_by_index[to_index]

			# Do nodes exist?
			if from_node is None:
				raise ValueError(f"No node with index {from_index} in network")
			if to_node is None:
				raise ValueError(f"No node with index {to_index} in network")

			# Add edge.
			self.add_successor(from_node, to_node)

			# Rebuild node and product attributes.
			self._build_node_attributes()
			self._build_product_attributes()

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

		The method adds the nodes to each other's lists of successors and
		predecessors. If ``successor_node`` is not already contained in the
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

		# Rebuild node and product attributes.
		self._build_node_attributes()
		self._build_product_attributes()

	def add_predecessor(self, node, predecessor_node):
		"""Add ``predecessor_node`` as a predecessor to ``node``. ``node`` must
		already be contained in the network.

		The method adds the nodes to each other's lists of successors and
		predecessors. If ``predecessor_node`` is not already contained in the
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

		# Rebuild node and product attributes.
		self._build_node_attributes()
		self._build_product_attributes()

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
			# Rebuild node and product attributes.
			self._build_node_attributes()
			self._build_product_attributes()

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
			for p_index in n.predecessor_indices():
				digraph.add_edge(p_index, n.index)

		return digraph
	
	# Functions related to product management.
 
	def _build_product_attributes(self):
		"""Build product-related attributes that are derived from other attributes,
		at the network and the nodes in it.
		These attributes are built each time the nodes or products change, rather than 
		deriving them live during a simulation.

		Does nothing if self._currently_building is True. (This is to avoid building
  		product attributes when network is currently being built and not all product/node
		info is in place yet.)
		"""
		if not self._currently_building:
			# Build product lists at nodes.
			# for node in self.nodes:
			# 	node._build_product_lists()

			# Build _products.
			# Add any products from nodes that are not in network product list.
#			products = [prod for prod in self._local_products]
			for node in self.nodes:
				for prod in node.products:
					if prod not in self._products:
						self._products.append(prod)
				if node._external_supplier_dummy_product is not None:
					if node._external_supplier_dummy_product not in self._products:
						self._products.append(node._external_supplier_dummy_product)
			# Remove any products that are not in local products or nodes. (This can happen, e.g.,
			# during node reindexing.)
			products = copy.deepcopy(self._products) # static copy to avoid changing list while we loop over it
			for prod in products:
				found = (prod.index in self._local_product_indices) or \
					any([prod.index in node.product_indices for node in self.nodes]) or \
					any([prod.index == node._external_supplier_dummy_product.index for node in self.nodes])
				if not found:
					self._products.remove(prod)					
			# Build _product_indices.
			self._product_indices = [prod.index for prod in self._products]
			
			# Build _products_by_index. Includes all products in network (including in nodes).
			self._products_by_index = {prod.index: prod for prod in self._products}
			# Add external supplier dummy products.
			self._products_by_index.update({node._external_supplier_dummy_product.index: node._external_supplier_dummy_product \
						for node in self.nodes if node._external_supplier_dummy_product is not None})

			# Build product attributes for all nodes.
			for node in self.nodes:
				node._build_product_attributes()

	def add_product(self, product):
		"""Add ``product`` to the network. ``product`` will not automatically be contained in any
		nodes that might be in the network already. 
		If ``product`` is already in the network (as determined by the index),
		do nothing.

		It is not necessary to add products using this function if they are handled by nodes
		in the network. The only reason to use this function is to add a product to a network
		that is not handled by any node in the network, which is not typical, or when loading
		a network from a file..

		Parameters
		----------
		product : |class_product|
			The product to add locally to the network.
		"""

		# Check whether product is already in network.
		product.network = self
		if product.index not in self._local_product_indices:
			self._local_product_indices.append(product.index)
			if product not in self._products:
				self._products.append(product)

			# Rebuild node and product attributes.
			self._build_node_attributes()
			self._build_product_attributes()

	def remove_product(self, product):
		"""Remove a product from the network. If ``product`` is not in the network (as 
		determined by the index), do nothing. ``product`` may be either a |class_product| object or
		the index of the product. 
				
		The product is removed locally from the network itself
		but is not removed from any nodes within the network. If the product is handled by
		any of those nodes, it will still be included in ``self.products``.

		Parameters
		----------
		product : |class_product| or int
			The product to remove locally from the network.
		"""
		_, prod_ind = self.parse_product(product)

		# Check whether product is in network.
		if prod_ind in self._local_product_indices:
			# Remove product from network. (If it's not in any nodes, it will be removed
			# from self._products by _build_node_attributes() below.)
			self._local_product_indices.remove(prod_ind)

			# Rebuild node and product attributes.
			self._build_node_attributes()
			self._build_product_attributes()

	# Utility functions.

	def parse_node(self, node, allow_none=True):
		"""Return the node and node index as a tuple, whether ``node`` is a |class_node|
		object or an int.

		Parameters
		----------
		node : |class_node| or int
			The node itself (as a |class_node|) or its index (as an int).
		allow_none : bool, optional
			If ``True`` (the default), ``node`` may be ``None``, in which case the
			function returns ``None, None``. If ``False``, raises an exception.

		Returns
		-------
		|class_node| 
			The node object.
		int
			The node index.

		Raises
		------
		TypeError
			If ``node`` is not a |class_node| or an int.
		ValueError
			if ``node`` is not a node in the network.
		"""

		if node is None:
			if allow_none:
				node_obj = None
				node_ind = None
			else:
				raise ValueError('node may not be None if allow_none is False.')
		elif is_integer(node):
			try:
				node_obj = self.nodes_by_index[node]
			except:
				raise ValueError(f'Node {node} is not a node in the network.')
			node_ind = node
		elif isinstance(node, SupplyChainNode):
			node_obj = node
			node_ind = node.index
			if node_ind not in self.node_indices:
				raise ValueError(f'Node {node_ind} is not a node in the network.')
		else:
			raise TypeError('node must be a SupplyChainNode or an int.')

		return node_obj, node_ind

	def parse_product(self, product, allow_none=True):
		"""Return the product and product index as a tuple, whether ``product`` is a |class_product|
		object or an int.

		Parameters
		----------
		product : |class_product| or int
			The product itself (as a |class_product|) or its index (as an int).
		allow_none : bool, optional
			If ``True`` (the default), ``product`` may be ``None``, in which case the
			function returns ``None, None``. If ``False``, raises an exception.

		Returns
		-------
		|class_product| 
			The product object.
		int
			The product index.

		Raises
		------
		TypeError
			If ``product`` is not a |class_product| or an int.
		ValueError
			if ``product`` is not a product in the network.
		"""

		if product is None:
			if allow_none:
				product_obj = None
				product_ind = None
			else:
				raise TypeError('product may not be None if allow_none is False.')
		elif is_integer(product):
			try:
				product_obj = self.products_by_index[product]
			except:
				raise ValueError(f'product {product} is not a product in the network.')
			product_ind = product
		elif isinstance(product, SupplyChainProduct):
			product_obj = product
			product_ind = product.index
			if product_ind not in self.product_indices:
				raise ValueError(f'Product {product_ind} is not a product in the network.')
		else:
			raise TypeError('product must be a SupplyChainProduct or an int.')

		return product_obj, product_ind

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

	The ``supply_type`` attribute is set to 'U' at all nodes that have no predecessors and to
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

	# (Exception: ``demand_list`` and ``probabilities`` attributes of |class_demand_source| may be
	# lists; these lists are treated as singletons for the purpose of the rules above.)

	# Create network.
	network = SupplyChainNetwork()

	# Set _currently_building flag so we don't re-build product attributes in the next step.
	network._currently_building = True

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

	# Temporarily turn _currently_building off and build node structure.
	network._currently_building = False
	network._build_node_attributes()
	network._currently_building = True

	# Check attributes in kwargs.
	for a in kwargs.keys():
		if not hasattr(network.nodes[0], a) and \
				not hasattr(network.nodes[0].demand_source, a) and \
				not hasattr(network.nodes[0].inventory_policy, a) and \
				not hasattr(network.nodes[0].disruption_process, a) and \
				a not in ('demand_type', 'policy_type', 'order_capacity'):
			raise AttributeError(f"{a} is not an attribute of SupplyChainNode")

	# Check node_order_in_lists; if not provided, build it.
	if node_order_in_lists is None:
		node_order_in_lists = sorted(network.node_indices)
	else:
		if set(node_order_in_lists) != set(network.node_indices):
			raise ValueError("node_order_in_lists does not match nodes contained in edge list")

	# Add edges.
	for e in edges:
		source = network.nodes_by_index[e[0]]
		sink = network.nodes_by_index[e[1]]
		network.add_successor(source, sink)

	# Build data dict.
	data_dict = build_node_data_dict(attribute_dict=kwargs, node_order_in_lists=node_order_in_lists)

	# Set node attributes. (The code below uses the get() function to access the
	# dictionaries within data_dict; get() returns None if the requested key is not
	# in the dict.)
	for n in network.nodes:

		# Costs and lead times.
		if data_dict[n.index].get('local_holding_cost') is not None:
			n.local_holding_cost = data_dict[n.index].get('local_holding_cost')
		else:
			n.local_holding_cost = data_dict[n.index].get('holding_cost')
		n.echelon_holding_cost = data_dict[n.index].get('echelon_holding_cost')
		n.order_capacity = data_dict[n.index].get('order_capacity')
		n.local_holding_cost_function = data_dict[n.index].get('local_holding_cost_function')
		n.in_transit_holding_cost = data_dict[n.index].get('in_transit_holding_cost')
		n.stockout_cost = data_dict[n.index].get('stockout_cost')
		n.stockout_cost_function = data_dict[n.index].get('stockout_cost_function')
		n.purchase_cost = data_dict[n.index].get('purchase_cost')
		n.revenue = data_dict[n.index].get('revenue')
		if data_dict[n.index].get('shipment_lead_time') is not None:
			n.shipment_lead_time = data_dict[n.index].get('shipment_lead_time')
		else:
			n.shipment_lead_time = data_dict[n.index].get('lead_time')
		n.order_lead_time = data_dict[n.index].get('order_lead_time')

		# Demand source. If this is a sink node OR if demand_source or demand_type were
		# provided as a dict or list (not a singleton) and node was included in it, 
		# build demand_source as specified by kwargs. Otherwise (it's not a sink node
		# and demand_source and demand_type are singletons or do not include node), 
		# create DemandSource of type None.
		if n in network.sink_nodes or \
			(is_iterable(kwargs.get('demand_source')) and data_dict[n.index].get('demand_source') is not None) or \
			(is_iterable(kwargs.get('demand_type')) and data_dict[n.index].get('demand_type') is not None):

			if data_dict[n.index].get('demand_source') is not None:
				n.demand_source = data_dict[n.index]['demand_source']
			else:
				# Create DemandSource object. (Don't override default value for round_to_int
				# with None.)
				ds = DemandSource()
				ds.type = data_dict[n.index].get('demand_type')
				if data_dict[n.index].get('round_to_int') is not None:
					ds.round_to_int = data_dict[n.index].get('round_to_int')
				ds.mean = data_dict[n.index].get('mean')
				ds.standard_deviation = data_dict[n.index].get('standard_deviation')
				ds.demand_list = data_dict[n.index].get('demand_list')
				ds.probabilities = data_dict[n.index].get('probabilities')
				ds.lo = data_dict[n.index].get('lo')
				ds.hi = data_dict[n.index].get('hi')
				n.demand_source = ds
		else:
			n.demand_source = DemandSource()

		# Inventory policy.
		if data_dict[n.index].get('inventory_policy') is not None:
			n.inventory_policy = data_dict[n.index]['inventory_policy']
			n.inventory_policy.node = n
		else:
			# Create Policy object.
			pol = Policy()
			pol.type = data_dict[n.index].get('policy_type')
			pol.node = n
			pol.base_stock_level = data_dict[n.index].get('base_stock_level')
			pol.order_quantity = data_dict[n.index].get('order_quantity')
			pol.reorder_point = data_dict[n.index].get('reorder_point')
			pol.order_up_to_level = data_dict[n.index].get('order_up_to_level')
			n.inventory_policy = pol

		# Disruption process.
		if data_dict[n.index].get('disruption_process') is not None:
			n.disruption_process = data_dict[n.index]['disruption_process']
		else:
			# Create DisruptionProcess object. (Don't override default values for disruption_type
			# or disrupted with None.)
			dp = DisruptionProcess()
			dp.random_process_type = data_dict[n.index].get('random_process_type')
			if data_dict[n.index].get('disruption_type') is not None:
				dp.disruption_type = data_dict[n.index].get('disruption_type')
			dp.disruption_probability = data_dict[n.index].get('disruption_probability')
			dp.recovery_probability = data_dict[n.index].get('recovery_probability')
			dp.disruption_state_list = data_dict[n.index].get('disruption_state_list')
			if data_dict[n.index].get('disrupted') is not None:
				dp.disrupted = data_dict[n.index].get('disrupted')
			n.disruption_process = dp

		# Supply type.
		if not n.predecessors():
			n.supply_type = 'U'

		# Initial quantities.
		n.initial_inventory_level = data_dict[n.index].get('initial_inventory_level')
		n.initial_orders = data_dict[n.index].get('initial_orders')
		n.initial_shipments = data_dict[n.index].get('initial_shipments')

		# GSM parameters.
		n.processing_time = data_dict[n.index].get('processing_time')
		n.external_inbound_cst = data_dict[n.index].get('external_inbound_cst')
		n.external_outbound_cst = data_dict[n.index].get('external_outbound_cst')
		n.demand_bound_constant = data_dict[n.index].get('demand_bound_constant')
		n.units_required = data_dict[n.index].get('units_required')

		# Problem-specific data.
		n.problem_specific_data = data_dict[n.index].get('problem_specific_data')

	# Turn off _currently_building flag and build node- and product-related attributes.
	network._currently_building = False
	network._build_node_attributes()
	network._build_product_attributes()

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


	**Example** (a |class_network| object containing the data from Example 4.1):

	.. testsetup:: *

		from stockpyl.supply_chain_network import *

	.. doctest::

		>>> network = single_stage_system(holding_cost=0.18,
		... stockout_cost=0.70,
		... demand_type='N',
		... mean=50, standard_deviation=8,
		... policy_type='BS',
		... base_stock_level=56.6)
		>>> network.nodes[0].stockout_cost
		0.7

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
		  must contain the same indices as ``node_order_in_system`` (if it is provided) or
		  0, ..., ``num_nodes`` - 1 (if it is not), otherwise a ``ValueError``
		  is raised. The values in the list are
		  assumed to correspond to the node indices in the order they are specified in
		  ``node_order_in_lists``. That is, the value in slot ``k`` in the parameter list is
		  assigned to the node with index ``node_order_in_lists[k]``.
		* If the parameter is a list and ``node_order_in_lists`` is not provided, the values
		  in the list are assumed to correspond to nodes in the same order as ``node_order_in_system``
		  (or in ``range(num_nodes)``, if ``node_order_in_system`` is not provided).

	``demand_source`` and ``stockout_cost`` attributes are only set at the downstream-most node,
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


	**Example** (a |class_network| object containing the data from Example 4.1):

	.. testsetup:: *

		from stockpyl.supply_chain_network import *

	.. doctest::

		>>> network = single_stage_system(holding_cost=0.18,
		... stockout_cost=0.70,
		... demand_type='N',
		... mean=50, standard_deviation=8,
		... policy_type='BS',
		... base_stock_level=56.6)
		>>> network.nodes[0].stockout_cost
		0.7

	"""

	# (Exception: ``demand_list`` and ``probabilities`` attributes of |class_demand_source| may be
	# lists; these lists are treated as singletons for the purpose of the rules above.)

	# Determine edges of network.
	if node_order_in_system is None:
		node_order_in_system = list(range(num_nodes))
	edges = [(node_order_in_system[k], node_order_in_system[k + 1]) for k in range(len(node_order_in_system) - 1)]

	# Make local copy of kwarg dict.
	local_kwargs = copy.deepcopy(kwargs)

	# Determine node_order_in_lists.
	if node_order_in_lists is None:
		node_order_in_lists = node_order_in_system

	# Build network.
	network = network_from_edges(
		edges=edges,
		node_order_in_lists=node_order_in_lists,
		**local_kwargs
	)

	# Determine sink node.
	sink_node = node_order_in_system[-1]
	# Set demand_source and stockout_cost parameters so they only occur at sink node.
	for node in network.nodes:
		if node.index != sink_node:
			node.demand_source = DemandSource()
			node.stockout_cost = 0
			node.stockout_cost_function = None

	return network


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
		node_order_in_system = list(range(0, num_retailers + 1))
	edges = [(node_order_in_system[0], node_order_in_system[k]) for k in range(1, num_retailers + 1)]

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
		node_order_in_system = list(range(1, num_warehouses + 1)) + [0]
	edges = [(node_order_in_system[k], node_order_in_system[-1]) for k in range(0, num_warehouses)]

	# Make local copy of kwarg dict.
	local_kwargs = copy.deepcopy(kwargs)
	# Set demand_source parameter so it only occurs at retailer node.
	if 'demand_source' not in local_kwargs:
		local_kwargs['demand_source'] = {}
	elif isinstance(local_kwargs['demand_source'], DemandSource):
		# demand_source provided as singleton; convert to dict.
		local_kwargs['demand_source'] = {n: DemandSource() for n in node_order_in_system[0:-1]}
		local_kwargs['demand_source'].update({node_order_in_system[-1]: kwargs['demand_source']})
	else:
		# demand_source provided as list; overwrite all except retailer node.
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
	num_nodes = len(network.nodes)

	# Determine indexing of nodes. (node_list[i] = index of i'th node, where
	# i = 0 means sink node and i = N-1 means source node.)
	node_list = []
	n = network.sink_nodes[0]
	while n is not None:
		node_list.append(n.index)
		n = n.get_one_predecessor()

	# Calculate S-minus.
	S_minus = {}
	for j in range(num_nodes):
		S_minus[node_list[j]] = np.min([S_echelon[node_list[i]] for i in range(j, num_nodes)])

	# Calculate S_local.
	for n in network.nodes:
		# Get successor.
		k = n.get_one_successor()
		if k is None:
			S_local[n.index] = S_minus[n.index]
		else:
			S_local[n.index] = S_minus[n.index] - S_minus[k.index]

	return S_local

