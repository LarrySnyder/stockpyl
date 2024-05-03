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

For multi-product models, most attributes may be either at the node level (by setting the attribute
in the |class_node| object), or at the product level (by setting the attribute in the |class_product| object), 
or at the node-product level (by setting the |class_node|'s attribute to a dict whose keys are product
indices and whose values are the attribute values). In particular:

	* If the attribute is a dict, the node will first attempt to access the value of ``<attribute>[<product id>]``.
	* Else, if the attribute is a dict but does not contain a value for a given product, the product's value
	for the attribute is used, if it exists.
	* Else the node's value of the attribute is used. (It should be a singleton in this case.)

To add a product to the node, use :func:`add_product`. To retrieve the products at the node, use
the ``products`` property, which is a dict whose keys are product indices and whose values are the
corresponding |class_product| objects. (For example, ``node.products[4]`` is the product at ``node`` with index 4.)


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

from stockpyl.node_state_vars import NodeStateVars
from stockpyl import policy
from stockpyl.supply_chain_product import SupplyChainProduct
from stockpyl import demand_source
from stockpyl import disruption_process
from stockpyl.helpers import change_dict_key, is_integer, is_list, is_dict, replace_dict_null_keys, replace_dict_numeric_string_keys

# This number gets added to product indices to avoid conflicts.
_INDEX_BUMP = 1000

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
	order_capacity : float
		Maximum size of an order.
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
			A numeric value to identify the node. In a |class_network|, each node
			must have a unique index.
		name : str, optional
			A string to identify the node.
		network : |class_network|, optional
			The network that contains the node.
		kwargs : optional
			Optional keyword arguments to specify node attributes. These arguments may be
            dicts to specify product-specific value of the attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match a |class_node| attribute.
		"""
		# Initialize attributes; set index; add dummy product.
		self.initialize(index)

		# Set other named attributes.
		self.name = name
		self.network = network

		# Set attributes specified by kwargs.
		for key, value in kwargs.items():
			if key in vars(self):
				# The key refers to an attribute of the object.
				setattr(self, key, value)
			elif key in dir(self.__class__) and isinstance(getattr(self.__class__, key), property):
				# The key refers to a property of the object. (We can still set it using setattr().)
				setattr(self, key, value)
			elif f"_{key}" in vars(self):
				# The key refers to an attribute that has "_" prepended to it.
				setattr(self, f"_{key}", value)
			else:
				raise AttributeError(f"{key} is not an attribute of SupplyChainNode")

	_DEFAULT_VALUES = {
		'_index': None,
		'name': None,
		'network': None,
		'_products_by_index': {},
		'_dummy_product': None,
		'_external_supplier_dummy_product': None,
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
		'_inventory_policy': None,
		'supply_type': None,
		'disruption_process': None,
		'order_capacity': None,
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

	@property
	def index(self):
		return self._index
	
	@index.setter
	def index(self, value):
		# Raise error if index is not a non-negative integer.
		if not is_integer(value) or value < 0:
			raise ValueError('Node index must be a non-negative integer.')
		self._index = value

		# If node has a dummy product, replace it with a new one to update its index.
		if self._dummy_product:
			self._remove_dummy_product()
			self._add_dummy_product()
			self._external_supplier_dummy_product = SupplyChainProduct(self._dummy_product.index - 1, is_dummy=True)
		# Replace external supplier dummy product.
		self._external_supplier_dummy_product = \
			SupplyChainProduct(SupplyChainNode._external_supplier_dummy_product_index_from_node_index(self.index), is_dummy=True)

	

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
	def inventory_policy(self):
		return self._inventory_policy

	@inventory_policy.setter
	def inventory_policy(self, value):
		# Set ``_inventory_policy``, and also set ``_inventory_policy``'s ``node`` attribute to self.
		# If ``value`` is a dict (for multi-product), set ``node`` and ``product`` attributes of the policy 
		# for each product in the dict.
		self._inventory_policy = value
		if self._inventory_policy is not None:
			if is_dict(value):
				for prod, _ in value.items():
					self._inventory_policy[prod].node = self
					self._inventory_policy[prod].product = prod
			else:
				self._inventory_policy.node = self

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
		# Set supply_type to not None if the node or any products have it set to not None.
		# TODO: handle this more elegantly (node supply_type property sets based on products too)
		supply_type = self.supply_type
		if not supply_type:
			for prod in self.products:
				if prod is not None and not is_integer(prod) and prod.supply_type is not None:
					supply_type = prod.supply_type
		# Include external supplier if include_external and supply_type is not None.
		if include_external and supply_type is not None:
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
	
	# Properties and functions related to products and bill of materials.

	@property
	def products(self):
		"""A list containing products handled by the node. Read only. """
		return list(self._products_by_index.values())

	@property
	def products_by_index(self):
		"""A dict containing products handled by the node. The keys of the dict are
		product indices and the values are the corresponding |class_product| objects.
		For example, ``self.products_by_index[4]`` returns a |class_product| object for the product 
		with index 4. Read only. """
		return self._products_by_index

	@property
	def is_multiproduct(self):
		"""Returns ``True`` if the node handles multiple products, ``False`` otherwise. Read only."""
		return len(self.products) > 1

	@property
	def is_singleproduct(self):
		"""Returns ``True`` if the node handles a single product, ``False`` otherwise. Read only."""
		return not self.is_multiproduct

	@property
	def product_indices(self):
		"""A list of indices of all products handled at the node. Read only."""
		return list(self._products_by_index.keys())
	
	def add_product(self, product):
		"""Add ``product`` to the node. If ``product`` is already in the node (as determined by the index),
		do nothing.

		Parameters
		----------
		product : |class_product|
			The product to add to the node.
		"""

		product.network = self.network
		if product not in self.products:
			self._products_by_index[product.index] = product
			if not product.is_dummy:
				# Remove dummy product. (This also sets `dummy_product` to None.)
				self._remove_dummy_product()

	def add_products(self, list_of_products):
		"""Add each product in ``list_of_products`` to the node. If a given product is already in the 
		node (as determined by the index), do not add it.

		Parameters
		----------
		list_of_products : list of |class_product| objects
			The list of products to add to the node.
		"""

		for prod in list_of_products:
			self.add_product(prod)

	def remove_product(self, product):
		"""Remove ``product`` from the node. ``product`` may be either a |class_product| object or
		the index of the product. If ``product`` is not in the node (as determined by the index),
		do nothing.

		Parameters
		----------
		product : |class_product| or int
			The product to remove from the node.
		"""
		if isinstance(product, SupplyChainProduct):
			self._products_by_index.pop(product.index, None)
		else:
			self._products_by_index.pop(product, None)
	
		if len(self._products_by_index) == 0:
			# No real products in the node. Add dummy product.
			self._add_dummy_product()

	def remove_products(self, list_of_products):
		"""Remove each product in ``list_of_products`` from the node. Products in ``list_of_products``
		may be either |class_product| objects or product indices, or a mix. Alternatively, set ``list_of_products`` to
		the string ``'all'`` to remove all products. If a given product is not in the 
		node (as determined by the index), do not remove it.

		Parameters
		----------
		list_of_products : list of |class_product| objects, or string
			The list of products to remove from the node, or ``'all'`` to remove all products.
		"""

		if list_of_products == 'all':
			for prod in self.products:
				self.remove_product(prod)
		else:
			for prod in list_of_products:
				self.remove_product(prod)

	def _add_dummy_product(self):
		"""Add a dummy product to the node. Typically this happens when the node is initialized and/or
		when all "real" products are removed from the node.
		"""
		prod_ind = self._dummy_product_index_from_node_index(self.index)
		dummy = SupplyChainProduct(index=prod_ind, is_dummy=True)
		self.add_product(dummy)
		self._dummy_product = dummy
		
	def _remove_dummy_product(self):
		"""Remove the dummy product from the node. Typically this happens when a "real" product is added
		to the node.
		"""
		self.remove_product(self._dummy_product)
		self._dummy_product = None

	@classmethod
	def _dummy_product_index_from_node_index(cls, node_index):
		"""Return index of dummy product for a given node index. This is called when a dummy product is
		added to a node, to determine its index, but also can be called at other times (e.g., when nodes are
		being reindexed), to predict what the new dummy product index will be.

		Parameters
		----------
		node_index : int
			The index of the node.
		"""
		if node_index > 0:
			return -2 * node_index
		else:
			return -_INDEX_BUMP - 2 * node_index

	@classmethod
	def _external_supplier_dummy_product_index_from_node_index(cls, node_index):
		"""Return index of external supplier dummy product for a given node index. This is called when an
		external supplier dummy product is
		added to a node, to determine its index, but also can be called at other times (e.g., when nodes are
		being reindexed), to predict what the new external supplier dummy product index will be.

		Parameters
		----------
		node_index : int
			The index of the node.
		"""
		return SupplyChainNode._dummy_product_index_from_node_index(node_index) - 1
		
	def get_network_bill_of_materials(self, product=None, predecessor=None, raw_material=None):
		"""Return the "network bill of materials" (NBOM) i.e., the number of units of ``raw_material`` 
		from ``predecessor`` that are required to make one unit of ``product`` at this node,
		accounting for network structure. In particular, if _no_ raw materials at the predecessor
		have a BOM relationship with _any_ product at the node, then _every_ raw material at the predecessor is assigned a BOM
		number of 1 for _every_ product at the node. (In particular, this allows single-product networks to
		be constructed without adding any products to the network.)

		``product``, ``predecessor``, and ``raw_material`` may be indices or objects. Set ``predecessor`` to ``None`` to
		determine the predecessor automatically: Either the external supplier (if ``raw_material`` is
		``None`` or the index of the dummy product at the external supplier) or the unique predecessor that provides a given
		dummy product (if ``raw_material`` is a dummy product), or an arbitrary predecessor (if ``raw_material`` is not a
		dummy product, because in this case the NBOM equals the BOM--it is product-specific, not node-specific, so
		the predecessor is irrelevant). 
			
		Raises a ``ValueError`` if ``product`` is not a product at the node, ``raw_material`` is
		not a product at ``predecessor``, or ``predecessor`` is not a predecessor of the node.

		:func:`NBOM` is a shortcut to this function.

		Parameters
		----------
		product : |class_product| or int, optional
			The product to get the BOM for, as a |class_object| or index. Set to ``None`` (the default) for
			the dummy product.
		predecessor : |class_node| or int, optional
			The predecessor to get the BOM for, as a |class_node| object or index. Set to
			``None`` (the default) to determine the predecessor automatically.
		raw_material : |class_product| or int, optional
			The raw material to get the BOM for, as a |class_object| or index. Set to ``None`` (the default) for
			the dummy product at the external supplier.

		Returns
		-------
		int
			The network BOM number for the (raw material, product) pair at these nodes.

		Raises
		------
		ValueError
			If ``product`` is not a product at the node or ``raw_material`` is
			not a product at ``predecessor``.
		ValueError
			If ``predecessor`` is not a predecessor of the node.
		"""

		# TODO: would be better to pre-build this, plus raw_materials, raw_material_suppliers, etc.,
		# in SCNode and SCProduct. Rebuild it each time the product or node structure changes.

		# Get objects and indices for parameters.
		if isinstance(product, SupplyChainProduct):
			prod = product
			prod_ind = product.index
		elif product is None:
			prod = self._dummy_product
			prod_ind = self._dummy_product.index
		else:
			prod = self.network.products_by_index[product]
			prod_ind = product

		if isinstance(raw_material, SupplyChainProduct):
#			rm = raw_material
			rm_ind = raw_material.index
		else:
#			rm = None if raw_material is None else self.network.products_by_index[raw_material]
			rm_ind = raw_material

		if isinstance(predecessor, SupplyChainNode):
			pred = predecessor
			pred_ind = predecessor.index
		elif predecessor is None:
			if rm_ind == self._external_supplier_dummy_product.index:
				pred = None
				pred_ind = None
			else:
				# This works for the case in which rm is a dummy product or a regular product.
				pred = self.raw_material_suppliers_by_raw_material(rm_ind, network_BOM=True)[0]
				pred_ind = pred.index if pred is not None else None
		else:
			pred = self.network.get_node_from_index(predecessor)
			pred_ind = predecessor

		# Validate parameters.
		if prod_ind not in self.product_indices:
			raise ValueError(f'Product {prod_ind} is not a product in node {self.index}.')
		if pred is not None and rm_ind not in pred.product_indices:
			raise ValueError(f'Product {rm_ind} is not a product in node {pred_ind}.')
		if pred_ind not in self.predecessor_indices(include_external=True):
			raise ValueError(f'Node {pred_ind} is not a predecessor of node {self.index}.')
		
		# Do any raw materials at predecessor have a BOM relationship with any products at the node?
		found = False
		for prod1 in self.products:
			for prod2 in prod1.raw_materials:
				if prod2 in (pred.products if pred is not None else [self._external_supplier_dummy_product.index]):
					found = True
					break
		
		# Were any BOM relationships found?
		if found:
			# Yes--return BOM relationship for this (product, raw material) pair (even if it's 0).
			return prod.BOM(rm_ind)
		else:
			# No--return 1, regardless of the product and raw material.
			return 1
		
	def NBOM(self, product=None, predecessor=None, raw_material=None):
		"""A shortcut to :func:`~get_network_bill_of_materials`."""
		return self.get_network_bill_of_materials(product, predecessor, raw_material)

	def raw_materials_by_product(self, product_index=None, network_BOM=True):
		"""A list of all raw materials required to make product with index ``product_index``
		at the node, as as |class_prod| objects. If the node is single-product, either set 
		``product_index`` to the index of the single product, or to ``None``
		and the function will determine the index automatically. Set ``product_index`` to ``'all'``
		to include all raw materials required to make all products at the node.
 
		If ``network_BOM`` is ``True``, includes raw materials that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.

		Parameters
		----------
		product_index : int, optional
			The product index, or ``None`` if the node is single-product, or ``'all'`` to 
			get raw materials for all products.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all raw materials required to make the product at the node.

		Raises
		------
		ValueError
			If ``product_index`` is not found among the node's products, and it's not the case that ``product_index is None`` and
			this is a single-product node with no |class_product| added.
		"""
		# If product index is not in product indices for node, AND it's not the case that this is a single-product node
		# and product_index is None, raise exception.
		if not (self.is_singleproduct and product_index is None) \
			and product_index != 'all' and product_index not in self.product_indices:
			raise ValueError(f'{product_index} is not a product index in this SupplyChainNode')

		# Determine which products to get raw materials for.
		if product_index == 'all':
			products = self.products
		elif product_index == None:
			products = [self.products[0]]
		else:
			products = [self.products_by_index[product_index]]

		rms = set()
		for prod in products:
			if network_BOM:
				for pred in self.predecessors(include_external=True):
					for rm in pred.products if pred is not None else [self._external_supplier_dummy_product]:
						if self.NBOM(product=prod, predecessor=pred, raw_material=rm) > 0:
							rms.add(rm)
			else:
				rms |= set(prod.raw_materials)
		return list(rms)

	def raw_material_indices_by_product(self, product_index=None, network_BOM=True):
		"""A list of indices of all raw materials required to make product with index ``product_index``
		at the node, as as |class_prod| objects. If the node is single-product, either set 
		``product_index`` to the index of the single product, or to ``None``
		and the function will determine the index automatically. Set ``product_index`` to ``'all'``
		to include all raw materials required to make all products at the node.

		If ``network_BOM`` is ``True``, includes raw materials that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.

		Parameters
		----------
		product_index : int, optional
			The product index, or ``None`` if node is single-product, or ``'all'`` to 
			get raw materials for all products.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of indices of all raw materials required to make the product at the node.

		Raises
		------
		ValueError
			If ``product_index`` is not found among the node's products, and it's not the case that ``product_index is None`` and
			this is a single-product node with no |class_product| added.
		"""
		return [rm.index for rm in self.raw_materials_by_product(product_index=product_index, network_BOM=network_BOM)]

	def raw_material_suppliers_by_product(self, product_index=None, network_BOM=True):
		"""Return a list of all predecessors from which a raw material must be ordered in order to
		make ``product_index`` at this node, according to the bill of materials. 
		If the node is single-product, either set 
		``product_index`` to the index of the single product, or to ``None``
		and the function will determine the index automatically. 

		If ``network_BOM`` is ``True``, includes raw material suppliers that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.
			
		Suppliers in list are
		|class_node| objects, plus ``None`` for the external supplier, if appropriate. 

		Parameters
		----------
		product_index : int, optional
			The product index, or ``None`` if node is single-product.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all predecessors, as |class_node| objects, from which a raw material must be ordered in order to
			make ``product_index`` at this node, according to the bill of materials, including ``None`` for
			the external supplier, if appropriate.

		Raises
		------
		ValueError
			If ``product_index`` is not found among the node's products, and it's not the case that ``product_index is None`` and
			this is a single-product node with no |class_product| added.
		"""
		# If product index is not in product indices for node, AND it's not the case that this is a single-product node
		# and product_index is None, raise exception.
		if not (self.is_singleproduct and product_index is None) and product_index not in self.product_indices:
			raise ValueError(f'{product_index} is not a product index in this SupplyChainNode')
		
		if product_index is None:
			if len(self.products) == 0:
				return []
			else:
				prod = self.products[0]
		else:
			prod = self.products_by_index[product_index]
		suppliers = []
		# Only include external supplier if network_BOM is True.
		for p in self.predecessors(include_external=network_BOM):
			# Determine whether p provides a raw material for the product.
			provides_rm = False
			if p is None:
				provides_rm = True
			else:
				for rm in p.products:
					if (network_BOM and self.NBOM(product=prod, predecessor=p, raw_material=rm) > 0) \
					or (not network_BOM and prod.BOM(rm.index if rm is not None else None) > 0):
						provides_rm = True
						break

			# Add p to list if it provides a raw material.
			if provides_rm:
				suppliers.append(p)
		
		return suppliers

	def raw_material_supplier_indices_by_product(self, product_index=None, network_BOM=True):
		"""Return a list of all indices of predecessors from which a raw material must be ordered in order to
		make ``product_index`` at this node, according to the bill of materials. 
		If the node is single-product, either set 
		``product_index`` to the index of the single product, or to ``None``
		and the function will determine the index automatically. 

		If ``network_BOM`` is ``True``, includes raw material suppliers that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.
			
		Parameters
		----------
		product_index : int, optional
			The product index, or ``None`` if ``predecessor`` is single-product.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all indices of predecessors from which a raw material must be ordered in order to
			make ``product_index`` at this node, according to the bill of materials.

		Raises
		------
		ValueError
			If ``product_index`` is not found among the node's products, and it's not the case that this is a single-product
			node with no |class_product| added.
		"""
		return [(s.index if s is not None else None) for s in self.raw_material_suppliers_by_product(product_index=product_index, network_BOM=network_BOM)]

	def raw_material_suppliers_by_raw_material(self, rm_index=None, network_BOM=True):
		"""Return a list of all predecessors that supply the node with the raw material
		with index ``rm_index``. Every predecessor that _can_ supply the raw material, including
		the external supplier, is included in the list, regardless of whether the BOM
		requires it, and regardless of whether the node actually orders the raw material
		from the supplier.

		If the node has only a single raw material that is required according to its
		BOM, ``rm_index`` can be set to the index of that raw material, or to ``None`` and
		the function will determine th eindex automatically.

		If ``network_BOM`` is ``True``, includes raw material suppliers that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.
			
		Suppliers in list are
		|class_node| objects, plus ``None`` for the external supplier, if appropriate. 

		Parameters
		----------
		rm_index : int, optional
			The raw material index, or ``None`` if the node requires a single raw material.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all predecessors, as |class_node| objects, that can supply the node
			with the raw material with index ``rm_index``, according to the bill of materials, 
			including ``None`` for the external supplier, if appropriate.

		Raises
		------
		ValueError
			If ``rm_index`` is not found among the node's raw materials (and is not ``None``).
		ValueError
			If ``rm_index is None`` and the node requires more than one raw material.
		"""
		rms = self.raw_materials_by_product('all', network_BOM=network_BOM)
		rm_indices = self.raw_material_indices_by_product('all', network_BOM=network_BOM)
		# If rm_index is None and the node requires more than one raw material, raise exception.
		if len(rms) > 1 and rm_index is None:
			raise ValueError(f'rm_index cannot be None if node requires more than 1 raw material.')
		# If rm_index is not in product indices for node and is not None, raise exception.
		if rm_index is not None and rm_index not in rm_indices:
			raise ValueError(f'{rm_index} is not a raw material required by this SupplyChainNode')
		
		if rm_index is None:
			# rm_index is None and there is at most a single raw material at this node (otherwise an exception
   			# would have been raised).
			if len(rms) == 0:
				return []
			else:
				rm = rms[0]
		elif rm_index == self._external_supplier_dummy_product.index:
			rm = self._external_supplier_dummy_product
		else:
			rm = self.network.products_by_index[rm_index]

		suppliers = []
		# Only include external supplier if network_BOM is True.
		for p in self.predecessors(include_external=network_BOM):
			if p is None and rm.index == self._external_supplier_dummy_product.index:
				# This is the external supplier, and rm_index matches the index of the
				# external supplier dummy product.
				suppliers.append(p)
			elif p is not None and rm.index in p.product_indices:
				# This is a "real" supplier, and it handles rm_index.
				suppliers.append(p)
		
		return suppliers

	def raw_material_supplier_indices_by_raw_material(self, rm_index=None, network_BOM=True):
		"""Return a list of indices of all predecessors that supply the node with the raw material
		with index ``rm_index``. Every predecessor that _can_ supply the raw material, including
		the external supplier, is included in the list, regardless of whether the BOM
		requires it, and regardless of whether the node actually orders the raw material
		from the supplier.

		If the node has only a single raw material that is required according to its
		BOM, ``rm_index`` can be set to the index of that raw material, or to ``None`` and
		the function will determine the index automatically.

		If ``network_BOM`` is ``True``, includes raw material suppliers that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.
			
		Parameters
		----------
		rm_index : int, optional
			The raw material index, or ``None`` if the node requires a single raw material.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of indicies of all predecessors that can supply the node
			with the raw material with index ``rm_index``, according to the bill of materials, 
			including ``None`` for the external supplier, if appropriate.

		Raises
		------
		ValueError
			If ``rm_index`` is not found among the node's raw materials (and is not ``None``).
		ValueError
			If ``rm_index is None`` and the node requires more than one raw material.
		"""
		return [(s.index if s is not None else None) for s in self.raw_material_suppliers_by_raw_material(rm_index=rm_index, network_BOM=network_BOM)]

	def products_by_raw_material(self, rm_index=None):
		"""A list of all products that use raw material with index ``rm_index`` at the node, 
		as as |class_prod| objects. If the node has a single raw material (either dummy or real), either set
		``rm_index`` to the index of the single raw material, or to ``None`` and the function
		will determine the index automatically. 
 
		If ``network_BOM`` is ``True``, includes products that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.

		Parameters
		----------
		rm_index : int, optional
			The raw material index, or ``None`` if the node has a single raw material.

		Returns
		-------
		list
			List of all products that use the raw material at the node.

		Raises
		------
		ValueError
			If ``rm_index`` is not found among the node's raw materials, and it's not the case that ``rm_index is None`` and
			this node has a single raw material.
		"""
		# If rm_index is not in raw material indices for node, AND it's not the case that this node has a single raw material
		# and rm_index is None, raise exception.
		all_rms = self.raw_material_indices_by_product('all', network_BOM=True)
		if not (len(all_rms) == 1 and rm_index is None) and rm_index not in all_rms:
			raise ValueError(f'{rm_index} is not a raw material index in this SupplyChainNode')

		# If rm_index is None, determine which rm_index to use.
		if rm_index is None:
			rm_index = all_rms[0]
		
		return [prod for prod in self.products if self.NBOM(product=prod, predecessor=None, raw_material=rm_index) > 0]
	
	def product_indices_by_raw_material(self, rm_index=None):
		"""A list of indices of all products that use raw material with index ``rm_index`` at the node, 
		as as |class_prod| objects. If the node has a single raw material (either dummy or real), either set
		``rm_index`` to the index of the single raw material, or to ``None`` and the function
		will determine the index automatically. 
 
		If ``network_BOM`` is ``True``, includes products that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) Read only.

		Parameters
		----------
		rm_index : int, optional
			The raw material index, or ``None`` if the node has a single raw material.

		Returns
		-------
		list
			List of indices of all products that use the raw material at the node.

		Raises
		------
		ValueError
			If ``rm_index`` is not found among the node's raw materials, and it's not the case that ``rm_index is None`` and
			this node has a single raw material.
		"""
		return [prod.index for prod in self.products_by_raw_material(rm_index=rm_index)]

	# Properties related to lead times.

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
				self.network.get_node_from_index(self.index - 1).forward_echelon_lead_time

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
		return other is not None and self.index == other.index

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

	def initialize(self, index=None):
		"""Initialize the parameters in the object to their default values and sets index attribute.
		Initializes attributes that are objects (``demand_source``, ``disruption_process``, ``_inventory_policy``).
		Adds dummy product and sets external supplier dummy product index, both of which are used in simulations.

		Set ``index`` to ``None`` to keep the current index, if any. If index is already ``None``,
		a ``ValueError`` is raised.

		Parameters
		----------
		index : int, optional
			The index for the node, or ``None`` (default) to keep the current index.

		Raises
		------
		ValueError
			If ``index`` and ``self.index`` are both ``None``, or if ``index`` is not an integer.
		"""

		# Raise error if index is None and current index is None.
		if index is None and (not hasattr(self, 'index') or self.index is None):
			raise ValueError('index parameter can only be set to None if node index is already set.')
		# Raise error if index is not an integer.
		if index is not None and not is_integer(index):
			raise ValueError('Node index must be an integer.')
		
		# Remember current index. (Make sure it exists. If this is first initialization, it does not.)
		if hasattr(self, 'index'):
			curr_index = self.index
		else:
			curr_index = None

		# Loop through attributes. Special handling for list and object attributes.
		for attr in self._DEFAULT_VALUES.keys():
			if attr == 'demand_source':
				self.demand_source = demand_source.DemandSource()
			elif attr == 'disruption_process':
				self.disruption_process = disruption_process.DisruptionProcess()
			elif attr == '_inventory_policy':
				self.inventory_policy = policy.Policy(node=self)
			elif is_list(self._DEFAULT_VALUES[attr]) or is_dict(self._DEFAULT_VALUES[attr]):
				setattr(self, attr, copy.deepcopy(self._DEFAULT_VALUES[attr]))
			else:
				setattr(self, attr, self._DEFAULT_VALUES[attr])

		# Set node index. This must be done after the 'for attr' loop, because default value
		# of index is None in self._DEFAULT_VALUES.
		if index is None:
			self.index = curr_index
		else:
			self.index = index

		# Add dummy product.
		self._add_dummy_product()
		
		# Set external supplier dummy product. (This is set even if the node does not and
  		# never will have an external supplier.)
		self._external_supplier_dummy_product = \
			SupplyChainProduct(SupplyChainNode._external_supplier_dummy_product_index_from_node_index(self.index), is_dummy=True)

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
				elif attr == '_inventory_policy':
					# Compare inventory policies.
					if self.inventory_policy != other.inventory_policy:
						viol_attr = attr
						eq = False
				elif attr in ('local_holding_cost', 'echelon_holding_cost', 'in_transit_holding_cost', 
							  'stockout_cost', 'revenue', 'initial_inventory_level', 'initial_orders',
							  'initial_shipments','demand_bound_constant', 'units_required', 'net_demand_mean',
							  'net_demand_standard_deviation', 'order_capacity'):
					# These attributes need approximate comparisons.
					if not isclose(getattr(self, attr) or 0, getattr(other, attr) or 0, rel_tol=rel_tol):
						viol_attr = attr
						eq = False
				elif attr in ('demand_source', 'disruption_process'):
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

		The following substitutions are made:

		* Successors and predecessors are stored as their indices only, not |class_node| objects.
		* Values in ``_products_by_index`` dict are replaced with indices only, not |class_product| objects.
			(This means that the keys and values in the dict are the same.)
		* Dummy product attributes are replaced with indices only, not |class_product| objects.
		* ``network`` object is not filled.

		These should be replaced with the corresponding node objects if this function is called
		recursively from a |class_network|'s ``from_dict()`` method.

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
			elif attr == '_products_by_index':
				# Replace product objects with their indices.
				node_dict[attr] = {prod_ind: prod_ind for prod_ind in self._products_by_index.keys()}
			elif attr in ('_dummy_product', '_external_supplier_dummy_product'):
				# Replace dummy products with their indices.
				node_dict[attr] = None if getattr(self, attr) is None else getattr(self, attr).index
			elif attr == '_predecessors':
				node_dict[attr] = copy.deepcopy(self.predecessor_indices(include_external=True))
			elif attr == '_successors':
				node_dict[attr] = copy.deepcopy(self.successor_indices(include_external=True))
			elif attr == '_products_by_index':
				node_dict[attr] = {prod.index: prod.to_dict() for prod in self.products}
			elif attr in ('demand_source', 'disruption_process', '_inventory_policy'):
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

		``_products_by_index`` is set to a dict in which the keys and values are both product indices, 
		like they are in the dict, but should be converted to |class_product| objects if this function is 
		called recursively from a |class_network|'s ``from_dict()`` method. 
		``_dummy_product`` and ``_external_supplier_dummy_product`` are set to indices, like they are
		in the dict, but should be converted to |class_product| objects if this function is called recursively.

		Similarly, ``network`` object is not filled, but should be filled with the network object if this
		function is called recursively from a |class_network|'s ``from_dict()`` method.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_node|, typically created using ``to_dict()``.

		Returns
		-------
		|class_product|
			The object converted from the dict.
		"""
		if the_dict is None:
			node = cls()
		else:
			# Determine index for new node. The attribute could be stored in the dict as 
			# index or _index: Older saved files use index, but the attribute was changed
			# to _index subsequently. Allow exception to be raised if neither is in the dict.
			index = the_dict['index'] if 'index' in the_dict else the_dict['_index']
			# Build empty SupplyChainNode.
			node = cls(index)
			# Fill attributes.
			for attr in cls._DEFAULT_VALUES.keys():
				# Some attributes require special handling.
				if attr == '_index':
					# This has no effect--we already set the index--but is needed for setattr() below.
					value = index
				elif attr in ('_products_by_index', '_predecessors', '_successors'):
					if attr in the_dict:
						value = copy.deepcopy(the_dict[attr])
					else:
						value = copy.deepcopy(cls._DEFAULT_VALUES[attr])
				# elif attr == '_products_by_index':
				# 	if attr not in the_dict:
				# 		value = copy.deepcopy(cls._DEFAULT_VALUES['_products_by_index'])
				# 	else:
				# 		value = copy.
				# 		for prod_dict in (the_dict['_products_by_index'].values() or []):
				# 			value[prod_dict['index']] = SupplyChainProduct.from_dict(prod_dict)
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
				elif attr == '_inventory_policy':
					if attr in the_dict:
						value = policy.Policy.from_dict(the_dict[attr])
					else:
						value = policy.Policy.from_dict(None)
					value.node = node
					# Remove "_" from attr so we are setting the property, not the attribute.
					attr = 'inventory_policy'
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

	def get_attribute(self, attr, product=None):
		"""Return the value of the attribute ``attr`` for ``product``. This is a way to
		easily access an attribute without knowing ahead of time whether it is a singleton
		or a product-keyed dict. ``product`` may be either a |class_product| object or the index of the product.
		
			* If ``self.attr`` is a dict and contains the key ``product``, returns ``self.attr[product]``. 
			``product`` must be the product index, in this case.
			(This returns a (node, product)-specific value of the attribute.) 
			* Else if ``self.attr`` equals its default value (e.g., ``None``), 
			or is a dict but does not contain the key ``product``, returns
			``self.products[product].attr``. (This returns a product-specific value of the attribute.)
			* Else (``self.attr`` is a singleton), returns ``self.attr``. (This returns a node-specific value
			of the attribute.)

		(Here, we are assuming ``product`` is an index. If it is a |class_product| object, replace ``product``
		with ``product.index``.)

		Parameters
		----------
		attr : str
			The name of the attribute to get.
		product : |class_product| or int, optional
			The product to get the attribute for, either as a |class_product| object or as an index.
			If the node has a single product, set ``product`` to its index, or to ``None`` (or omit it)
			to determine the index automatically.
		
		Returns
		-------
		any
			The value of the attribute for the product (if any).
		
		Raises
		------
		ValueError
			If ``product`` is ``None`` but the node has multiple products.
		"""
		if product is None and len(self.products) > 1:
			raise ValueError(f'You cannot set product = None for a node that has multiple products (node = {self.index}).')
  
		# Get self.attr and the product and index.
		self_attr = getattr(self, attr)
		if product is None:
			product_obj = self.products[0]
			product_ind = self.products[0].index
		elif isinstance(product, SupplyChainProduct):
			product_obj = product
			product_ind = product.index
		else:
			product_obj = self.products_by_index[product]
			product_ind = product

		# Is self.attr a dict?
		if is_dict(self_attr):
			if product_ind in self_attr:
				return self_attr[product_ind]
			else:
				return getattr(product_obj, attr)
		elif attr == 'inventory_policy':
			# inventory_policy needs to be handled separately because both None and Policy(None)
			# trigger using the product's attribute.
			if product_obj is not None and \
				(self_attr is None or self_attr == self._DEFAULT_VALUES['_inventory_policy'] or \
				 (isinstance(self_attr, policy.Policy) and self_attr.type is None)):
				return getattr(product_obj, attr)
			else:
				return self_attr
		else:
			# Determine whether attr is set to its default value; if so, try to use product attribute.
			# Properties that are aliases for attributes require special handling since there's no
			# default value for properties.
			if attr == 'holding_cost':
				default_val = self._DEFAULT_VALUES['local_holding_cost']
			elif attr == 'lead_time':
				default_val = self._DEFAULT_VALUES['shipment_lead_time']
			else:
				default_val = self._DEFAULT_VALUES[attr]
			if product_obj is not None and ((default_val is None and self_attr is None) or (self_attr == default_val)):
				# Product exists and attr at node is set to default value--use attr at product.
				return getattr(product_obj, attr)
			else:
				return self_attr

	def _get_state_var_total(self, attribute, period, product_index=None, include_external=True):
		"""Return total (over all successors/predecessors) of ``attribute`` in the node's ``state_vars`` 
		for the period and product specified, for an
		attribute that is indexed by successor or predecessor, i.e.,
		``inbound_shipment``,`` on_order_by_predecessor``, ``inbound_order``, ``outbound_shipment``,
		``backorders_by_successor``, ``outbound_disrupted_items``, ``inbound_disrupted_items``.
		(If another attribute is specified, returns the value of the
		attribute, without any summation.) 

		If ``period`` is ``None``, sums the attribute over all periods.

		If node is multi-product, ``product_index`` must be set to the index of the product for which
		the attribute is being requested.

		If ``include_external`` is ``True``, includes the external supply or
		demand node (if any) in the total.

		Example: ``_get_state_var_total('inbound_shipment', 5)`` returns the total
		inbound shipment, from all predecessor nodes (including the external
		supply, if any), in period 5.

		Parameters
		----------
		attribute : str
			Attribute to be totalled. Error occurs if attribute is not present.
		period : int
			Time period. Set to ``None`` to sum over all periods.
		product_index : int
			Index of product for which the attribute is being requested. May set to ``None`` for
			single-product nodes.
		include_external : bool
			Include the external supply or demand node (if any) in the total?

		Returns
		-------
		float
			The total value of the attribute.

		Raises
		------
		ValueError
			If ``product_index is None`` and the node is not single-product.

		"""
		if product_index is None and self.is_multiproduct:
			raise ValueError('product_index cannot be None for multi-product nodes.')
		
		# Reset product_index to index of (possibly dummy) product if this is a single-product node.
		if product_index is None:
			product_index = self.product_indices[0]

		if attribute in ('inbound_shipment', 'on_order_by_predecessor', 'raw_material_inventory', 'inbound_disrupted_items'):
			# These attributes are indexed by predecessor.
			if period is None:
				return float(np.sum([self.state_vars[t].__dict__[attribute][p_index][product_index]
									 for t in range(len(self.state_vars))
									 for p_index in self.predecessor_indices(include_external=include_external)]))
			else:
				return float(np.sum([self.state_vars[period].__dict__[attribute][p_index][product_index]
									 for p_index in self.predecessor_indices(include_external=include_external)]))
		elif attribute in ('inbound_order', 'outbound_shipment', 'backorders_by_successor', 'outbound_disrupted_items'):
			# These attributes are indexed by successor.
			if period is None:
				return float(np.sum([self.state_vars[t].__dict__[attribute][s_index][product_index]
									 for t in range(len(self.state_vars))
									 for s_index in self.successor_indices(include_external=include_external)]))
			else:
				return float(np.sum([self.state_vars[period].__dict__[attribute][s_index][product_index]
									 for s_index in self.successor_indices(include_external=include_external)]))
		elif attribute in ('disrupted', 'holding_cost_incurred', 'stockout_cost_incurred', 'in_transit_holding_cost_incurred',
			'revenue_earned', 'total_cost_incurred'):
			# These attributes are not indexed by product.
			if period is None:
				return np.sum([self.state_vars[:].__dict__[attribute]])
			else:
				return self.state_vars[period].__dict__[attribute]
		else:
			if period is None:
				return np.sum([self.state_vars[:].__dict__[attribute][product_index]])
			else:
				return self.state_vars[period].__dict__[attribute][product_index]

	def reindex_all_state_variables(self, old_to_new_dict, old_to_new_prod_dict):
		"""Change indices of all node-based keys in all state variables using ``old_to_new_dict``
		and all product-based keys using ``old_to_new_prod_dict``.

		Parameters
		----------
		old_to_new_dict : dict
			Dict in which keys are old node indices and values are new node indices.
		old_to_new_prod_dict : dict
			Dict in which keys are old product indices and values are new product indices.

		"""
		for i in range(len(self.state_vars)):
			self.state_vars[i].reindex_state_variables(old_to_new_dict, old_to_new_prod_dict)

