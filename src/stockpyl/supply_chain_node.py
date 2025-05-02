# ===============================================================================
# stockpyl - SupplyChainNode Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
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
from stockpyl.helpers import is_integer, is_list, is_dict, is_set, replace_dict_numeric_string_keys

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
		# Set network. (This must be done before initialize() because initialize() uses it.)
		self.network = network

		# Initialize other attributes; set index; add dummy product.
		self.initialize(index)

		# Set name. (This must be done after initialize() because initialize() will reset it to None.)
		self.name = name

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
		'_products': [],
		'_product_indices': [],	
		'_products_by_index': {},
		'_dummy_product': None,
		'_external_supplier_dummy_product': None,
		'_predecessor_indices': [],
		'_successor_indices': [],
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
		
		# Rebuild node- and product-related attributes in network.
		if self.network is not None:
			self.network._build_node_attributes()
			self.network._build_product_attributes()

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
 
	@property
	def has_external_supplier(self):
		"""``True`` if the node has an external supplier (i.e., if its ``supply_type`` is not ``None``),
		``False`` otherwise.
		"""
		has_ext_supp = False
		for prod_ind in self.product_indices:
			if self.get_attribute('supply_type', product=prod_ind) is not None:
				has_ext_supp = True
				break
		
		return has_ext_supp

	@property
	def has_external_customer(self):
		"""``True`` if the node has an external customer (i.e., if its ``demand_source`` is not ``None``),
		``False`` otherwise.
		"""
		has_ext_cust = False
		for prod_ind in self.product_indices:
			ds = self.get_attribute('demand_source', product=prod_ind)
			if ds is not None and ds.type is not None:
				has_ext_cust = True
				break
		
		return has_ext_cust

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
		
		Raises
		------
		AttributeError
			If ``network`` attribute is ``None``.
		"""
		if self.network is None:
			raise ValueError('predecessors() cannot be called if network attribute is None. Use predecessor_indices() instead.')
		return [self.network.nodes_by_index[pred_ind] for pred_ind in self.predecessor_indices(include_external=include_external)]

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

		Raises
		------
		AttributeError
			If ``network`` attribute is ``None``.
		"""
		if self.network is None:
			raise ValueError('successors() cannot be called if network attribute is None. Use successor_indices() instead.')
		return [self.network.nodes_by_index[pred_ind] for pred_ind in self.successor_indices(include_external=include_external)]

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
		if include_external and self.has_external_supplier:
			return self._predecessor_indices + [None]
		else:
			return self._predecessor_indices

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
		if include_external and self.has_external_customer:
			return self._successor_indices + [None]
		else:
			return self._successor_indices

	@property
	def descendants(self):
		"""A list of all descendants of the node, as |class_node| objects.
		A descendant is a node that is downstream from the node but not necessarily directly
		adjacent; that is, a node that can be reached from the node via a directed path. Read only.
		"""
		G = self.network.networkx_digraph()
		desc = nx.descendants(G, self.index)
		return [self.network.nodes_by_index[d] for d in desc]

	@property
	def ancestors(self):
		"""A list of all ancestors of the node, as |class_node| objects.
		An ancestor is a node that is upstream from the node but not necessarily directly
		adjacent; that is, a node from which we can reach the node via a directed path.
		Read only.
		"""
		G = self.network.networkx_digraph()
		anc = nx.ancestors(G, self.index)
		return [self.network.nodes_by_index[a] for a in anc]

	@property
	def neighbors(self):
		"""A list of all neighbors (successors and predecessors) of the node, as
		|class_node| objects. Read only.

		Raises
		------
		AttributeError
			If ``network`` attribute is ``None``.
		"""
		if self.network is None:
			raise ValueError('neighbors() cannot be called if network attribute is None. Use neighbor_indices() instead.')

		return [self.network.nodes_by_index[n_index] for n_index in self.neighbor_indices]

	@property
	def neighbor_indices(self):
		"""A list of indices of all neighbors (successors and predecessors) of the node.
		Read only.
		"""
		neighbor_indices = copy.deepcopy(self.successor_indices())
		neighbor_indices += copy.deepcopy(self.predecessor_indices()) # this assumes no predecessor can also be a successor
	
		return neighbor_indices

	def validate_predecessor(self, predecessor, raw_material=None, network_BOM=True, err_on_multiple_preds=True):
		"""Confirm that ``predecessor`` is a valid predecessor of node:

			* If ``predecessor`` is a |class_node| object, confirms that it is a 
				predecessor of the node, and returns the predecessor node and its index.
			* If ``predecessor`` is an int, confirms that it is the index of a predecessor
				of the node, and returns the predecessor node and its index.
			* If ``predecessor`` is ``None`` and the node has a single predecessor node
				(regardless of whether it also has an external supplier), returns the predecessor node and its index.
			* If ``predecessor`` is ``None`` and the node has 0 or more than 1 predecessor node and has
				an external supplier, returns ``None, None``. (This represents the external supplier.)
			* Raises a ``ValueError`` in most other cases.
			* If ``raw_material`` is not ``None``, also checks that the predecessor provides that raw
				material, and raises an exception if not. (This only works if ``preecessor`` is not ``None``.)

		Parameters
		----------
		predecessor : |class_node|, int, or ``None``
			The predecessor to validate.
		raw_material : |class_product| or int, optional
			If not ``None`` and ``predecessor`` is not ``None``, the function will check that
			``raw_material`` is provided by ``predecessor`` and raise an exception if not.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.
		err_on_multiple_preds : bool, optional
			If ``True`` (default), raises an exception if ``predecessor`` is ``None`` and the
			node has multiple predecessors (or multiple predecessors that provide ``raw_material``).
		
		Returns
		-------
		|class_node|
			The node object.
		int
			The node index.
	
		Raises
		------
		TypeError
			If ``predecessor`` is not a |class_node|, int, or ``None``.
		ValueError
			If ``predecessor`` is not a predecessor of the node.
		ValueError
			If ``predecessor`` is ``None`` and the node has no external supplier 
			and has 0 or >1 predecessor nodes.
		ValueError
			If ``predecessor`` and ``raw_material`` are both not ``None`` and ``predecessor``
			does not supply this node with ``raw_material``.
		"""

		if raw_material is None:
			pred_indices = self.predecessor_indices(include_external=False)
		else:
			rm_obj, rm_ind = self.network.parse_product(raw_material)
			pred_indices = [pred_ind for pred_ind in self.predecessor_indices(include_external=False) 
				if rm_ind in self.network.nodes_by_index[pred_ind].product_indices]
			if rm_ind == self._external_supplier_dummy_product.index:
				pred_indices.append(None)
		
		if predecessor is None:
			if len(pred_indices) == 1:
				return self.network.parse_node(pred_indices[0])
			elif None in self.predecessor_indices(include_external=True):
				return None, None
			# Now len(preds) = 0 or >1 and node does not have an external supplier.
			elif len(pred_indices) == 0 or err_on_multiple_preds:
				if raw_material is None:
					raise ValueError(f'predecessor cannot be None if the node has no external supplier and has 0 or >1 predecessor nodes.')
				else:
					raise ValueError(f'predecessor cannot be None if raw_material is not None and the node has 0 or >1 suppliers of raw_material')
			else:
				# len(preds) > 1 but error was suppressed.
				return None, None
		else:
			pred_node, pred_ind = self.network.parse_node(predecessor) # raises TypeError on bad type
			if pred_ind not in pred_indices:
				raise ValueError(f'Node {pred_ind} is not a predecessor of node {self.index}.')
			else:
				return pred_node, pred_ind

	def validate_successor(self, successor):
		"""Confirm that ``successor`` is a valid successor of node:

			* If ``successor`` is a |class_node| object, confirms that it is a 
				successor of the node, and returns the successor node and its index.
			* If ``successor`` is an int, confirms that it is the index of a successor
				of the node, and returns the successor node and its index.
			* If ``successor`` is ``None`` and the node has a single successor node
				(regardless of whether it also has an external customer), returns the successor node and its index.
			* If ``successor`` is ``None`` and the node has 0 or more than 1 successor node and has
				an external customer, returns ``None, None``. (This represents the external customer.)
			* Raises a ``ValueError`` in most other cases.

		Parameters
		----------
		successor : |class_node|, int, or ``None``
			The successor to validate.
		
		Returns
		-------
		|class_node|
			The node object.
		int
			The node index.
	
		Raises
		------
		TypeError
			If ``successor`` is not a |class_node|, int, or ``None``.
		ValueError
			If ``successor`` is not a successor of the node.
		ValueError
			If ``successor`` is ``None`` and the node has no external customer 
			and has 0 or >1 successor nodes.
		"""

		succ_indices = self.successor_indices(include_external=False)
		if successor is None:
			if len(succ_indices) == 1:
				return self.network.parse_node(succ_indices[0])
			elif None in self.successor_indices(include_external=True):
				return None, None
			else:
				raise ValueError(f'successor cannot be None if the node has no external customer and has 0 or >1 successor nodes.')
		else:
			succ_node, succ_ind = self.network.parse_node(successor) # raises TypeError on bad type
			if succ_ind not in succ_indices:
				raise ValueError(f'Node {succ_ind} is not a successor of node {self.index}.')
			else:
				return succ_node, succ_ind
		
	# Properties and functions related to products and bill of materials.

	@property
	def products(self):
		"""A list containing products handled by the node. Read only."""			
		return self._products

	@property
	def product_indices(self):
		"""A list of indices of all products handled at the node. Read only."""
		return self._product_indices
	
	@property
	def products_by_index(self):
		"""A dict containing products handled by the node. The keys of the dict are
		product indices and the values are the corresponding |class_product| objects.
		For example, ``self.products_by_index[4]`` is a |class_product| object for the product 
		with index 4. Read only. """
		return self._products_by_index

	@property
	def is_multiproduct(self):
		"""Returns ``True`` if the node handles multiple products, ``False`` otherwise. Read only."""
		return len(self.product_indices) > 1

	@property
	def is_singleproduct(self):
		"""Returns ``True`` if the node handles a single product, ``False`` otherwise. Read only."""
		return not self.is_multiproduct

	def _build_product_attributes(self):
		"""Build product-related attributes that are derived from other attributes,
		at the network and the nodes in it.
		These attributes are built each time the nodes or products in the network change, rather than 
		deriving them live during a simulation.

		Does nothing if self._currently_building is True. (This is to avoid building
  		product attributes when network is currently being built and not all product/node
		info is in place yet.)
		"""
		if self.network is not None and not self.network._currently_building:
			self._build_network_bill_of_materials()
			self._build_supplier_raw_material_pairs()
						
	def _build_supplier_raw_material_pairs(self):
		"""Build two product-indexed dicts of (supplier, raw material) pairs -- one based on pure BOM
   		and one based on NBOM -- and store them in _supplier_raw_material_pairs_by_product_BOM and
   		_supplier_raw_material_pairs_by_product_NBOM attributes. Suppliers and raw materials are
		stored as indices.
		These attributes are built each time the nodes or products change, rather than 
		deriving them live during a simulation.

		Does nothing if ``self.network`` is ``None`` or ``self.network._currently_building`` is ``True``. 
		(This is to avoid building
  		product attributes when network is currently being built and not all product/node
		info is in place yet.)
		"""
		# This function relies on :func:`get_network_bill_of_materials` but not other functions
		# that list suppliers/raw materials. Therefore, those functions can call this one without
		# triggering an infinite recursion.

		if self.network and not self.network._currently_building:

			# Initialize attributes.
			self._supplier_raw_material_pairs_by_product_BOM = {prod_ind: [] for prod_ind in self.product_indices}
			self._supplier_raw_material_pairs_by_product_NBOM = {prod_ind: [] for prod_ind in self.product_indices}

			for prod in self.products:
				pairs_BOM = []
				pairs_NBOM = []
				for pred in self.predecessors(include_external=True):
					for rm in pred.products if pred is not None else [self._external_supplier_dummy_product]:
						if prod.BOM(raw_material=rm.index) > 0:
							pairs_BOM.append((pred.index if pred else None, rm.index))
						if self.NBOM(product=prod, predecessor=pred, raw_material=rm) > 0:
							pairs_NBOM.append((pred.index if pred else None, rm.index))

				self._supplier_raw_material_pairs_by_product_BOM[prod.index] = pairs_BOM
				self._supplier_raw_material_pairs_by_product_NBOM[prod.index] = pairs_NBOM
						
	def _build_network_bill_of_materials(self):
		"""Build the network bill of materials and store it in _network_bill_of_materials attribute.
		This attribute is built each time the nodes or products change, rather than 
		deriving it live during a simulation.

		Does nothing if ``self.network`` is ``None`` or ``self.network._currently_building`` is ``True``. 
		(This is to avoid building
  		product attributes when network is currently being built and not all product/node
		info is in place yet.)
		"""
		if self.network is not None and not self.network._currently_building:
			# Initialize NBOM.
			self._network_bill_of_materials = \
				{prod_ind: {pred_ind: {} for pred_ind in self.predecessor_indices(include_external=True)} for prod_ind in self.product_indices}

			# Loop through predecessors.
			for pred in self.predecessors(include_external=True):
				pred_ind = pred.index if pred is not None else None
				# Do any raw materials at predecessor have a BOM relationship with any products at the node?
				BOM_found = False
				for prod1 in self.products:
					for prod2_ind in prod1.raw_material_indices:
						if prod2_ind in (pred.product_indices if pred is not None else [self._external_supplier_dummy_product.index]):
							BOM_found = True
							break
				
				# Loop through products at node and predecessor.
				for prod1 in self.products:
					for prod2_ind in (pred.product_indices if pred is not None else [self._external_supplier_dummy_product.index]):
						# If any BOM relationships were found, use product BOM; otherwise, NBOM = 1.
						if BOM_found:
							NBOM = prod1.BOM(prod2_ind)
						else:
							NBOM = 1

						# Set NBOM.
						self._network_bill_of_materials[prod1.index][pred_ind][prod2_ind] = NBOM
			
	def add_product(self, product):
		"""Add ``product`` to the node. If ``product`` is already in the node (as determined by the index),
		do nothing.

		Parameters
		----------
		product : |class_product|
			The product to add to the node.
		"""

		product.network = self.network

		# Remember value of _currently_building flag, and turn it on to avoid building product attributes prematurely.
		if self.network is not None:
			old_currently_building = self.network._currently_building
			self.network._currently_building = True
				
		if product.index not in self.product_indices:
			self._product_indices.append(product.index)
			self._products.append(product)
			self._products_by_index[product.index] = product
			if not product.is_dummy:
				# Remove dummy product. (This also sets `dummy_product` to None.)
				self._remove_dummy_product()

		# Rebuild node- and product-related attributes in network.
		if self.network is not None:
			self.network._currently_building = old_currently_building
			self.network._build_node_attributes()
			self.network._build_product_attributes()

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
		# Parse product. (Can't use network.parse_product() because network might be None.)
		if isinstance(product, SupplyChainProduct):
			prod_ind = product.index
			prod_obj = product
		else:
			prod_ind = product
			if product in self._products_by_index: 
				prod_obj = self._products_by_index[product]
			elif self.network and product in self.network.products_by_index:
				prod_obj = self.network.products_by_index[product]
			else:
				prod_obj = None

		# Remove items from lists/dict carefully; it's possible that not all of them exist
		# (if we are in the middle of loading/building a network.)
		changed = False
		if prod_ind in self._product_indices:
			self._product_indices.remove(prod_ind)
			changed = True
		if prod_obj in self._products:
			self._products.remove(prod_obj)
			changed = True
		if prod_ind in self._products_by_index:
			self._products_by_index.pop(prod_ind, None)
			changed = True

		# If anything changed, rebuild node and product attributes.
		if changed:	
			# Remember value of _currently_building flag, and turn it on to avoid building product attributes prematurely.
			if self.network is not None:
				old_currently_building = self.network._currently_building
				self.network._currently_building = True
					
			if len(self._product_indices) == 0:
				# No real products in the node. Add dummy product.
				self._add_dummy_product()

			# Rebuild node- and product-related attributes in network.
			if self.network is not None:
				self.network._currently_building = old_currently_building
				self.network._build_node_attributes()
				self.network._build_product_attributes()

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
			# Make static copy to avoid changing list while iterating over it.
			product_indices = copy.deepcopy(self.product_indices)
			for prod_ind in product_indices:
				self.remove_product(prod_ind)
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

		# Rebuild node- and product-related attributes in network.
		if self.network is not None:
			self.network._build_node_attributes()
			self.network._build_product_attributes()
		
	def _remove_dummy_product(self):
		"""Remove the dummy product from the node. Typically this happens when a "real" product is added
		to the node. Does nothing if node has no dummy product, i.e., ``self._dummy_product`` is ``None``.
		"""
		self.remove_product(self._dummy_product)
		self._dummy_product = None

		# Rebuild node- and product-related attributes in network.
		if self.network is not None:
			self.network._build_node_attributes()
			self.network._build_product_attributes()

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
		``None`` or the dummy product at the external supplier) or the unique predecessor that provides a given
		dummy product (if ``raw_material`` is a dummy product), or an arbitrary predecessor (if ``raw_material`` is not a
		dummy product, because in this case the NBOM equals the BOM--it is product-specific, not node-specific, so
		the predecessor is irrelevant). 
			
		Returns a ``ValueError`` if ``product`` is not a product at the node, ``raw_material`` is
		not a product at ``predecessor``, or ``predecessor`` is not a predecessor of the node.

		:func:`NBOM` is a shortcut to this function.

		Parameters
		----------
		product : |class_product| or int, optional
			The product to get the BOM for, as a |class_product| or index. Set to ``None`` (the default) for
			the dummy product.
		predecessor : |class_node| or int, optional
			The predecessor to get the BOM for, as a |class_node| object or index. Set to
			``None`` (the default) to determine the predecessor automatically.
		raw_material : |class_product| or int, optional
			The raw material to get the BOM for, as a |class_product| or index. Set to ``None`` (the default) for
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

		_, prod_ind = self.validate_product(product)
		pred_obj, pred_ind = self.validate_predecessor(predecessor, raw_material=raw_material, err_on_multiple_preds=False)
		if pred_obj:
			# Make sure raw material is a product at pred.
			_, rm_ind = pred_obj.validate_product(raw_material) # can't use self.validate_raw_material here because it calls NBOM() ==> infinite recursion
		else:
			# Pred is external supplier. Just parse the raw material.
			rm_obj, rm_ind = self.network.parse_product(raw_material)
			# If raw material is a non-dummy product, replace pred with an arbitrary predecessor. (See docstring.)
			if rm_obj is not None and not rm_obj.is_dummy:
				for pred_ind in self.predecessor_indices(include_external=False):
					pred_obj = self.network.nodes_by_index[pred_ind]
					if rm_ind in pred_obj.product_indices:
						break
				# pred_obj = [pred for pred in self.predecessors(include_external=False) if rm_ind in pred.product_indices][0]
				# pred_ind = pred_obj.index

			# If raw material is None, replace it with external supplier dummy product.
			if rm_ind is None:
				rm_ind = self._external_supplier_dummy_product.index

		return self._network_bill_of_materials[prod_ind][pred_ind][rm_ind]

	def NBOM(self, product=None, predecessor=None, raw_material=None):
		"""A shortcut to :func:`~get_network_bill_of_materials`."""
		return self.get_network_bill_of_materials(product, predecessor, raw_material)

	def raw_materials_by_product(self, product=None, return_indices=False, network_BOM=True):
		"""Return a list of all raw materials required to make ``product``
		at the node. If the node is single-product, either set 
		``product`` to the single product, or to ``None``
		and the function will determine it automatically. Set ``product`` to ``'all'``
		to include all raw materials required to make all products at the node.
 
		If ``return_indices`` is ``False``, returns the raw materials as |class_product| objects,
		otherwise returns their indices.

		If ``network_BOM`` is ``True``, includes raw materials that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) 

		Parameters
		----------
		product : |class_product|, int, or string, optional
			The product (as a |class_product| object or index), ``None`` if the node is single-product, 
			or ``'all'`` to get raw materials for all products.
		return_indices : bool, optional
			Set to ``False`` (the default) to return product objects, ``True`` to return product indices.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all raw materials required to make the product at the node.

		Raises
		------
		ValueError
			If ``product`` is not found among the node's products, and it's not the case that ``product is None`` and
			this is a single-product node.
		"""
		# Validate parameters.
		if product != 'all':
			prod_obj, prod_ind = self.validate_product(product)

		# Determine which products to get raw materials for.
		if product == 'all':
			prod_inds = self.product_indices
		elif product is None:
			if len(self.product_indices) != 1:
				raise ValueError('product cannot be None unless node has exactly 1 product.')
			prod_inds = self.product_indices
		else:
			prod_inds = [prod_ind]

		rms = []
		for prod_ind in prod_inds:
			for _, rm in self.supplier_raw_material_pairs_by_product(product=prod_ind, \
										return_indices=return_indices, network_BOM=network_BOM):
				if rm not in rms:
					rms.append(rm)
			
		return rms

	def raw_material_suppliers_by_product(self, product=None, return_indices=False, network_BOM=True):
		"""Return a list of all predecessors from which a raw material must be ordered in order to
		make ``product`` at this node, according to the bill of materials. 
		If the node is single-product, either set 
		``product`` to the single product, or to ``None``
		and the function will determine it automatically. 

		If ``return_indices`` is ``False``, returns the suppliers as |class_node| objects,
		otherwise returns their indices.

		If ``network_BOM`` is ``True``, includes raw material suppliers that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.)

		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index), or ``None`` if the node is single-product.
		return_indices : bool, optional
			Set to ``False`` (the default) to return node objects, ``True`` to return node indices.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all predecessors from which a raw material must be ordered in order to
			make ``product`` at this node, according to the bill of materials, including ``None`` for
			the external supplier, if appropriate.

		Raises
		------
		ValueError
			If ``product`` is not found among the node's products, and it's not the case that ``product is None`` and
			this is a single-product node.
		"""
		# Validate parameters.
		prod_obj, _ = self.validate_product(product)

		suppliers = []
		for pred, rm in self.supplier_raw_material_pairs_by_product(product=prod_obj, \
									return_indices=return_indices, network_BOM=network_BOM):
			if pred not in suppliers:	
				suppliers.append(pred)
		
		return suppliers

	def raw_material_suppliers_by_raw_material(self, raw_material=None, return_indices=False, network_BOM=True):
		"""Return a list of all predecessors that supply the node with ``raw_material``.
		Every predecessor that _can_ supply the raw material, including
		the external supplier, is included in the list, regardless of whether the node actually orders the raw material
		from the supplier. If the node has a single raw material, either set ``raw_material`` to the
		single raw material, or to ``None`` and the function will determine it automatically.

		If ``return_indices`` is ``False``, returns the suppliers as |class_node| objects,
		otherwise returns their indices.

		If ``network_BOM`` is ``True``, includes raw material suppliers that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) 
			
		Parameters
		----------
		raw_material : |class_product| or int, optional
			The raw material (as a |class_product| object or index), or ``None`` if the node 
			requires a single raw material.
		return_indices : bool, optional
			Set to ``False`` (the default) to return product objects, ``True`` to return product indices.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all predecessors that can supply the node
			with ``raw_material``, according to the bill of materials, 
			including ``None`` for the external supplier, if appropriate.

		Raises
		------
		ValueError
			If ``raw_material`` is not found among the node's raw materials, and it's not the case
			that ``raw_material is None`` and this node has a single raw material.
		"""
		# Validate parameters.
		rm_obj, _ = self.validate_raw_material(raw_material, network_BOM=network_BOM)

		suppliers = []
		for pred, rm in self.supplier_raw_material_pairs_by_product(product='all', 
   										return_indices=False, network_BOM=network_BOM):
			if pred not in suppliers:
				if rm == rm_obj:
					if return_indices:
						suppliers.append(pred.index if pred is not None else None)
					else:
						suppliers.append(pred)
	
		return suppliers

	def products_by_raw_material(self, raw_material=None, return_indices=False, network_BOM=True):
		"""Return a list of all products that use ``raw_material`` at the node. 
		If the node has a single raw material (either dummy or real), either set
		``raw_material`` to the single raw material, or to ``None`` and the function
		will determine it automatically. 

		Parameters
		----------
		raw_material : |class_product| or int, optional
			The raw material (as a |class_product| object or index), or ``None`` if the node 
			requires a single raw material.
		return_indices : bool, optional
			Set to ``False`` (the default) to return product objects, ``True`` to return product indices.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.

		Returns
		-------
		list
			List of all products that use the raw material at the node, according to the bill of materials.

		Raises
		------
		ValueError
			If ``raw_material`` is not found among the node's raw materials, and it's not the case that ``raw_material is None`` and
			this node has a single raw material.
		"""
		# Validate parameters.
		_, rm_ind = self.validate_raw_material(raw_material, network_BOM=network_BOM)
  
		if network_BOM:
			prod_inds = []
			for prod_ind in self.product_indices:
				if prod_ind not in prod_inds:
					for pred in self.raw_material_suppliers_by_raw_material(rm_ind, return_indices=False, network_BOM=True):
						if self.NBOM(product=prod_ind, predecessor=pred, raw_material=rm_ind) > 0:
							prod_inds.append(prod_ind)
							break
		else:
			prod_inds = [prod.index for prod in self.products if prod.BOM(raw_material=rm_ind) > 0]
		
		if return_indices:
			return prod_inds
		else:
			return [self.network.parse_product(prod_ind)[0] for prod_ind in prod_inds]
	
	def supplier_raw_material_pairs_by_product(self, product=None, return_indices=False, network_BOM=True):
		"""A list of all predecessors and raw materials for ``product``, as tuples ``(pred, rm)``.
		Set ``product`` to ``'all'`` to get predecessors and raw materials for all products at the node.
		If the node has a single product (either dummy or real), either set ``product`` to the single product,
		or to ``None`` and the function will determine it automatically. 

		If ``return_indices`` is ``False``, returns a list with the predecessors as |class_node| objects (or ``None`` for the
		external supplier) and the products as |class_product| objects. Otherwise, returns a list with 
		the predecessor and product indices.

		If ``network_BOM`` is ``True``, includes predecessors and raw materials that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) 

		Parameters
		----------
		product : |class_product|, int, or string, optional
			The product (as a |class_product| object or index), ``None`` if the node is single-product,
			or ``'all'`` to get predecessors and raw materials for all products.
		return_indices : bool, optional
			Set to ``False`` (the default) to return node and product objects, ``True`` to return node and product indices.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.
		
		Returns
		-------
		list
			List of (predecessor, raw material) tuples.

		Raises
		------
		ValueError
			If ``product`` is not found among the node's products, and it's not the case that ``product is None`` and
			this is a single-product node.
		"""
		# This function relies on :func:`get_network_bill_of_materials` but not other functions
		# that list suppliers/raw materials. Therefore, those functions can call this one without
		# triggering an infinite recursion.

   		# Validate parameters.
		if product != 'all':
			prod_obj, prod_ind = self.validate_product(product)

			# If product is not in products for node, AND it's not the case that this is a single-product node
			# and product is None, raise exception.
			if not (self.is_singleproduct and product is None) \
				and prod_ind not in self.product_indices:
				raise ValueError(f'{prod_ind} is not a product index at node {self.index}.')

		# Determine which products to consider.
		if product == 'all':
			prod_inds = self.product_indices
		elif product is None:
			if len(self.product_indices) != 1:
				raise ValueError('product cannot be None unless node has exactly 1 product.')
			prod_inds = self.product_indices
		else:
			prod_inds = [prod_ind]

		pairs = []
		for prod_ind in prod_inds:
			if network_BOM:
				pairs += self._supplier_raw_material_pairs_by_product_NBOM[prod_ind]
			else:
				pairs += self._supplier_raw_material_pairs_by_product_BOM[prod_ind]
		# Remove duplicates.
		pairs = list(set(pairs))
		
		# Convert indices to objects, if requested.
		if not return_indices:
			pairs = [(self.network.nodes_by_index[pred_ind], self.network.products_by_index[rm_ind]) for pred_ind, rm_ind in pairs]

		return pairs

	def customers_by_product(self, product=None, return_indices=False, network_BOM=True):
		"""A list of customers that order ``product`` from the node. If the node has a single product
		(either dummy or real), either set ``product`` to the single product, or to ``None`` and the function
		will determine it automatically. 
				
		If ``return_indices`` is ``False``, returns the customers as |class_node| objects (or ``None`` for the
		external customer), otherwise returns customer indices.

		If ``network_BOM`` is ``True``, includes customers that don't have a 
		BOM relationship specified but are implied by the network structure. 
		(See :func:`get_network_bill_of_materials`.) 

		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index), or ``None`` if the node has a single product.
		return_indices : bool, optional
			Set to ``False`` (the default) to return node objects, ``True`` to return node indices.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.
		"""
		prod_obj, prod_ind = self.validate_product(product)
	
		# Customer nodes.
		custs = [n for n in self.successors(include_external=False) \
			if prod_obj in n.raw_materials_by_product('all', network_BOM=network_BOM) and \
				self in n.raw_material_suppliers_by_raw_material(prod_ind, network_BOM=network_BOM)]
		
		# Convert to indices, if desired.
		if return_indices:
			custs = [n.index for n in custs]
		
		# External customer.
		ds = self.get_attribute('demand_source', product=product)
		if ds is not None and ds.type is not None:
			custs.append(None)
		
		return custs

	def validate_product(self, product):
		"""Confirm that ``product`` is a valid product of node:

			* If ``product`` is a |class_product| object, confirms that it is a 
				product of the node, and returns the product object and its index.
			* If ``product`` is an int, confirms that it is the index of a product
				of the node, and returns the product object and its index.
			* If ``product`` is ``None`` and the node has a single product
				(including a dummy product), returns the product node and its index.
			* Raises a ``ValueError`` in most other cases.

		Parameters
		----------
		product : |class_product|, int, or ``None``
			The product to validate.
		
		Returns
		-------
		|class_product|
			The product object.
		int
			The product index.
	
		Raises
		------
		TypeError
			If ``product`` is not a |class_product|, int, or ``None``.
		ValueError
			If ``product`` is not a product of the node.
		ValueError
			If ``product`` is ``None`` and the node has more than 1 product (including
			the dummy product).
		"""

		prod_indices = self.product_indices
		if product is None:
			if len(prod_indices) == 1:
				return self.network.parse_product(prod_indices[0])
			else:
				raise ValueError(f'product cannot be None if the node has more than 1 product.')
		else:
			prod_obj, prod_ind = self.network.parse_product(product) # raises TypeError on bad type
			if prod_ind not in prod_indices:
				raise ValueError(f'Product {prod_ind} is not a product of node {self.index}.')
			else:
				return prod_obj, prod_ind
		
	def validate_raw_material(self, raw_material, predecessor=None, network_BOM=True):
		"""Confirm that ``raw_material`` is a valid raw material used by the node:

			* If ``raw_material`` is a |class_product| object, confirms that it is a 
				raw material of the node, and returns the raw material's |class_product| object and its index.
			* If ``raw_material`` is an int, confirms that it is the index of a raw material
				of the node, and returns the raw material's |class_product| object and its index.
			* If ``raw_material`` is ``None`` and the node has a single raw material
				(including an external supplier dummy raw material), returns the raw material node and its index.
			* Raises a ``ValueError`` in most other cases.
			* If ``predecessor`` is not ``None``, also checks that the raw material is provided by that
				predecessor, and raises an exception if not. (This only works if ``raw_material`` is not ``None``.)
	
		Parameters
		----------
		raw_material : |class_product|, int, or ``None``
			The raw material to validate.
		predecessor : |class_node| or int, optional
			If not ``None`` and ``raw_material`` is not ``None``, the function will check that
			``raw_material`` is provided by ``predecessor`` and raise an exception if not.
		network_BOM : bool, optional
			If ``True`` (default), function uses network BOM instead of product-only BOM.
		
		Returns
		-------
		|class_product|
			The raw material as an object.
		int
			The raw material index.
	
		Raises
		------
		TypeError
			If ``raw_material`` is not a |class_product|, int, or ``None``.
		ValueError
			If ``raw_material`` is not a raw material of the node.
		ValueError
			If ``raw_material`` is ``None`` and either ``predecessor`` is supplied and the node receives more than 1 raw
			material from ``predecessor`` or ``predecesor`` is ``None`` and the node has more than 1 raw material (including
			the dummy raw materials).
		ValueError
			If ``raw_material`` and ``predecessor`` are both not ``None`` and ``predecessor``
			does not supply this node with ``raw_material``.
		"""

		rm_inds = self.raw_materials_by_product(product='all', return_indices=True, network_BOM=network_BOM)
		if raw_material is None:
			if predecessor is None:
				if len(rm_inds) == 1:
					return self.network.parse_product(rm_inds[0])
				else:
					raise ValueError(f'raw_material and predecessor cannot both be None if the node has more than 1 raw material.')
			else:
				_, pred_ind = self.network.parse_node(predecessor)
				rms_from_pred = [rm_ind for (p_ind, rm_ind) in \
									self.supplier_raw_material_pairs_by_product(product='all', return_indices=True, network_BOM=True) \
									if p_ind == pred_ind]
				if len(rms_from_pred) == 1:
					return self.network.parse_product(rms_from_pred[0])
				else:
					raise ValueError(f'raw_material cannot be None if the predecessor provides more than 1 raw material to the node.')
		else:
			rm_obj, rm_ind = self.network.parse_product(raw_material) # raises TypeError on bad type
			_, pred_ind = self.network.parse_node(predecessor)
			if rm_ind not in rm_inds:
				raise ValueError(f'Product {rm_ind} is not a raw material of node {self.index}.')
			elif pred_ind is not None and (pred_ind, rm_ind) not in \
				self.supplier_raw_material_pairs_by_product(product='all', return_indices=True, network_BOM=True):
				raise ValueError(f'Node {pred_ind} does not provide product {rm_ind} as a raw material to node {self.index}')
			else:
				return rm_obj, rm_ind
		
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
				self.network.nodes_by_index[self.index - 1].forward_echelon_lead_time

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
		considered equal if their indices are equal. Returns ``False`` if ``other`` 
		is not a |class_node|.

		Parameters
		----------
		other : |class_node|
			The node to compare to.

		Returns
		-------
		bool
			True if the nodes are equal, False otherwise.

		"""
		if not isinstance(other, SupplyChainNode):
			return False
		else:
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

	def __repr__(self):
		"""
		Return a string representation of the |class_node| instance.

		Returns
		-------
			A string representation of the |class_node| instance.

		"""
		return f'SupplyChainNode(index={self.index})'

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
		
		# Remember current index, if any. (If this is first initialization, it doesn't exist yet.)
		curr_index = self.index if hasattr(self, 'index') else None

		# Loop through attributes. Special handling for list/dict/set and object attributes.
		for attr in self._DEFAULT_VALUES.keys():
			if attr == 'demand_source':
				self.demand_source = demand_source.DemandSource()
			elif attr == 'disruption_process':
				self.disruption_process = disruption_process.DisruptionProcess()
			elif attr == '_inventory_policy':
				self.inventory_policy = policy.Policy(node=self)
			elif is_list(self._DEFAULT_VALUES[attr]) or is_dict(self._DEFAULT_VALUES[attr]) or \
				is_set(self._DEFAULT_VALUES[attr]):
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
	
		# Build product-related attributes.
		self._build_product_attributes()

	def deep_equal_to(self, other, rel_tol=1e-8):
		"""Check whether node "deeply equals" ``other``, i.e., if all attributes are
		equal, including attributes that are themselves objects.

		Note the following caveats:

		* Does not check equality of ``network``.
		* Checks predecessor and successor equality by index only.
		* Checks product equality by index only, i.e., checks ``_product_indices`` but not
		  ``_products`` or ``_products_by_index``.
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
				elif attr == '_product_indices':
					if set(self.product_indices) != set(other.product_indices):
						viol_attr = attr
						eq = False
				elif attr in ('_products', '_products_by_index'):
					# Do nothing.
					pass
				elif attr == '_predecessor_indices':
					if set(self.predecessor_indices()) != set(other.predecessor_indices()):
						viol_attr = attr
						eq = False
				elif attr == '_successor_indices':
					if set(self.successor_indices()) != set(other.successor_indices()):
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
					# These attributes need approximate comparisons. Check first whether it's a dict or singleton.
					self_attr = getattr(self, attr)
					other_attr = getattr(other, attr)
					if (is_dict(self_attr) and not is_dict(other_attr)) or (not is_dict(self_attr) and is_dict(other_attr)) \
						or (is_dict(self_attr) and set(self_attr.keys()) != set(other_attr.keys())):
						viol_attr = attr
						eq = False
					elif is_dict(self_attr):
						for k, v in self_attr.items():
							if not isclose(v or 0, other_attr[k] or 0, rel_tol=rel_tol):
								viol_attr = attr
								eq = False
					elif not isclose(self_attr or 0, other_attr or 0, rel_tol=rel_tol):
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

		* ``_products`` and ``_products_by_index`` attributes are not converted; only ``_product_indices``.
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
			elif attr == '_product_indices':
				node_dict[attr] = copy.deepcopy(self.product_indices)
			# elif attr == '_products_by_index':
			# 	# Replace product objects with their indices.
			# 	node_dict[attr] = {prod_ind: prod_ind for prod_ind in self._products_by_index.keys()}
			elif attr in ('_products', '_products_by_index'):
				# Do nothing.
				pass
			elif attr in ('_dummy_product', '_external_supplier_dummy_product'):
				# Replace dummy products with their indices.
				node_dict[attr] = None if getattr(self, attr) is None else getattr(self, attr).index
			elif attr == '_predecessor_indices':
				node_dict[attr] = copy.deepcopy(self.predecessor_indices(include_external=False))
			elif attr == '_successor_indices':
				node_dict[attr] = copy.deepcopy(self.successor_indices(include_external=False))
			elif attr in ('demand_source', 'disruption_process', '_inventory_policy'):
				# Determine whether attr is a singleton or a dict (for node-product-level attribute).
				# Leave a note to the decoder indicating which type of dict this is.
				the_attr = None if getattr(self, attr) is None else getattr(self, attr)
				if is_dict(the_attr):
					node_dict[attr] = {k: v.to_dict() for k, v in the_attr.items()}
					node_dict[attr]['dict_type'] = 'product_keyed_attribute'
				elif the_attr is None:
					node_dict[attr] = None
				else:
					node_dict[attr] = the_attr.to_dict()
					node_dict[attr]['dict_type'] = 'singleton_attribute'
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

		Note that:

		* ``_product_indices`` attribute is loaded into the product, but ``_products`` and ``_products_by_index``
		  attributes are not. (They are set to their default values.) These should be filled by the |class_network|'s ``from_dict()`` method. 
		* ``_dummy_product`` and ``_external_supplier_dummy_product`` are set to indices, like they are
		  in the dict.
		* ``network`` object is not filled.

		These attributes should be completed (i.e., indices replaced by objects, etc.) by the network object if this 
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
			for attr_name in cls._DEFAULT_VALUES.keys():
				# Some attributes require special handling. For attributes that are objects (which will have
				# been saved as dicts), read 'dict_type' to determine whether this is a product-keyed dict
				# or a singleton; also, don't include 'dict_type' in the decoded object.
				if attr_name == '_index':
					# This has no effect--we already set the index--but is needed for setattr() below.
					value = index
				# TODO: remove this and next after test instance files are rebuilt -- or maybe add warning but keep it?
				# - _predecessor_indices instead of _predecessors (and same for succ)
				# - None (nil) in preds/succs
				# - lists instead of sets
				# elif attr_name == '_predecessor_indices':
				# 	if '_predecessors' in the_dict:
				# 		value = list(copy.deepcopy(the_dict['_predecessors']))
				# 	else:
				# 		value = list(copy.deepcopy(the_dict['_predecessor_indices']))
				# 	# Remove any None values. (Older versions saved external supplier as None.)
				# 	if None in value:
				# 		value.remove(None)
				# elif attr_name == '_successor_indices':
				# 	if '_successors' in the_dict:
				# 		value = list(copy.deepcopy(the_dict['_successors']))
				# 	else:
				# 		value = list(copy.deepcopy(the_dict['_successor_indices']))
				# 	# Remove any None values. (Older versions saved external customer as None.)
				# 	if None in value:
				# 		value.remove(None)	
				# elif attr_name == '_products_by_index':
				# 	if '_products_by_index' in the_dict:
				# 		# Convert keys to int (they were probably saved as strings). 
				# 		# Do not yet convert values to objects. (This will be done in network from_dict().)
				# 		value = {int(k): int(k) for k in the_dict['_products_by_index'].keys()}
				# 	else:
				# 		value = copy.deepcopy(cls._DEFAULT_VALUES[attr_name])
				elif attr_name in ('_product_indices', '_predecessor_indices', '_successor_indices'):
					if attr_name in the_dict:
						value = copy.deepcopy(the_dict[attr_name])
					else:
						value = copy.deepcopy(cls._DEFAULT_VALUES[attr_name])
				elif attr_name in ('_products', '_products_by_index'):
					# Reset to default values.
					value = copy.deepcopy(cls._DEFAULT_VALUES[attr_name])
				elif attr_name == 'demand_source':
					if attr_name in the_dict:
						if 'dict_type' in the_dict[attr_name] and the_dict[attr_name]['dict_type'] == 'product_keyed_attribute':
							# Attribute is product-keyed dict; convert keys to int (they were probably
							# saved as strings) and undictify objects.
							value = {int(k): demand_source.DemandSource.from_dict(v) for k, v in the_dict[attr_name].items() if k != 'dict_type'}
						else:
							value = demand_source.DemandSource.from_dict(the_dict[attr_name])
					else:
						value = demand_source.DemandSource.from_dict(None)
				elif attr_name == 'disruption_process':
					if attr_name in the_dict:
						if 'dict_type' in the_dict[attr_name] and the_dict[attr_name]['dict_type'] == 'product_keyed_attribute':
							value = {int(k): disruption_process.DisruptionProcess.from_dict(v) for k, v in the_dict[attr_name].items() if k != 'dict_type'}
						else:
							value = disruption_process.DisruptionProcess.from_dict(the_dict[attr_name])
					else:
						value = disruption_process.DisruptionProcess.from_dict(None)
				elif attr_name == '_inventory_policy':
					if attr_name in the_dict:
						if 'dict_type' in the_dict[attr_name] and the_dict[attr_name]['dict_type'] == 'product_keyed_attribute':
							value = {int(k): policy.Policy.from_dict(v) for k, v in the_dict[attr_name].items() if k != 'dict_type'}
							for k in value:
								value[k].node = node
						else:
							value = policy.Policy.from_dict(the_dict[attr_name])
							value.node = node
					else:
						value = policy.Policy.from_dict(None)
						value.node = node
					# Remove "_" from attr_name so we are setting the property, not the attribute.
					attr_name = 'inventory_policy'
				elif attr_name == 'state_vars':
					if attr_name in the_dict:
						if the_dict[attr_name] is None:
							value = None
						else:
							value = [NodeStateVars.from_dict(sv) for sv in the_dict[attr_name]]
							for sv in value:
								sv.node = node
					else:
						value = cls._DEFAULT_VALUES[attr_name]
				else:
					if attr_name in the_dict:
						value = the_dict[attr_name]
						if is_dict(the_dict[attr_name]) and 'dict_type' in the_dict[attr_name]:
							if the_dict[attr_name]['dict_type'] == 'product_keyed_attribute':
								# Keys (products) may have been saved as strings -- replace with ints.
								value = replace_dict_numeric_string_keys(value)
							del the_dict[attr_name]['dict_type']
					else:
						value = cls._DEFAULT_VALUES[attr_name]
				setattr(node, attr_name, value)

		return node

	# Neighbor management.

	def add_successor(self, successor):
		"""Add ``successor`` to the node's set of successors.

		.. important:: This method simply updates the node's set of successors. It does not
			add ``successor`` to the network or add ``self`` as a predecessor of
			``successor``. Typically, this method is called by the network rather
			than directly. Use the :meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.add_successor` method
			in |class_network| instead.

		Parameters
		----------
		successor : |class_node|
			The node to add as a successor.

		"""
		self._successor_indices.append(successor.index)

	def add_predecessor(self, predecessor):
		"""Add ``predecessor`` to the node's set of predecessors.

		.. important:: This method simply updates the node's set of predecessors. It does not
			add ``predecessor`` to the network or add ``self`` as a successor of
			``predecessor``. Typically, this method is called by the network rather
			than directly. Use the :meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.add_predecessor` method
			in |class_network| instead.

		Parameters
		----------
		predecessor : |class_node|
			The node to add as a predecessor.

		"""
		self._predecessor_indices.append(predecessor.index)

	def remove_successor(self, successor):
		"""Remove ``successor`` from the node's set of successors. ``successor`` may
		be a |class_node| or its index. Does nothing if ``successor`` is not a successor of the node

		.. important:: This method simply updates the node's set of successors. It does not
			remove ``successor`` from the network or remove ``self`` as a predecessor of
			``successor``. Typically, this method is called by the
			:meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.remove_node` method of the
			|class_network| rather than directly.

		Parameters
		----------
		successor : |class_node| or int
			The node to remove as a successor.

		"""
		if isinstance(successor, SupplyChainNode):
			succ_ind = successor.index
		else:
			succ_ind = successor

		self._successor_indices.remove(succ_ind)

	def remove_predecessor(self, predecessor):
		"""Remove ``predecessor`` from the node's set of predecessors. ``predecessor`` may
		be a |class_node| or its index. Does nothing if ``predecessor`` is not a predecessor of the node

		.. important:: This method simply updates the node's set of predecessors. It does not
			remove ``predecessor`` from the network or remove ``self`` as a successor of
			``predecessor``. Typically, this method is called by the
			:meth:`~stockpyl.supply_chain_network.SupplyChainNetwork.remove_node` method of the
			|class_network| rather than directly.

		Parameters
		----------
		predecessor : |class_node| or int
			The node to remove as a predecessor.

		"""
		if isinstance(predecessor, SupplyChainNode):
			pred_ind = predecessor.index
		else:
			pred_ind = predecessor

		self._predecessor_indices.remove(pred_ind)

	def get_one_successor(self):
		"""Get one successor of the node. If the node has more than one
		successor, return the first in the list. If the node has no
		successors, return ``None``.

		Returns
		-------
		successor : |class_node|
			A successor of the node.
		"""
		if len(self.successor_indices()) == 0:
			return None
		else:
			return self.network.nodes_by_index[self.successor_indices()[0]]
#			return self.successors()[0]

	def get_one_predecessor(self):
		"""Get one predecessor of the node. If the node has more than one
		predecessor, return the first in the list. If the node has no
		predecessor, return ``None``.

		Returns
		-------
		predecessor : |class_node|
			A predecessor of the node.
		"""
		if len(self.predecessor_indices()) == 0:
			return None
		else:
			return self.network.nodes_by_index[self.predecessor_indices()[0]]
#			return self()[0]

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
		if product is None and len(self.product_indices) > 1:
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
			if product in self.products_by_index:
				product_obj = self.products_by_index[product]
			else:
				product_obj = self.network.products_by_index[product]
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

	def _get_state_var_total(self, attribute, period, product=None, include_external=True):
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
		_, prod_ind = self.validate_product(product)
		
		# if product_index is None and self.is_multiproduct:
		# 	raise ValueError('product_index cannot be None for multi-product nodes.')
		
		# # Reset product_index to index of (possibly dummy) product if this is a single-product node.
		# if product_index is None:
		# 	product_index = self.product_indices[0]

		if attribute in ('inbound_shipment', 'on_order_by_predecessor', 'raw_material_inventory', 'inbound_disrupted_items'):
			# These attributes are indexed by predecessor.
			if period is None:
				return float(np.sum([self.state_vars[t].__dict__[attribute][p_index][prod_ind]
									 for t in range(len(self.state_vars))
									 for p_index in self.predecessor_indices(include_external=include_external)]))
			else:
				return float(np.sum([self.state_vars[period].__dict__[attribute][p_index][prod_ind]
									 for p_index in self.predecessor_indices(include_external=include_external)]))
		elif attribute in ('inbound_order', 'outbound_shipment', 'backorders_by_successor', 'outbound_disrupted_items'):
			# These attributes are indexed by successor.
			if period is None:
				return float(np.sum([self.state_vars[t].__dict__[attribute][s_index][prod_ind]
									 for t in range(len(self.state_vars))
									 for s_index in self.successor_indices(include_external=include_external)]))
			else:
				return float(np.sum([self.state_vars[period].__dict__[attribute][s_index][prod_ind]
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
				return np.sum([self.state_vars[:].__dict__[attribute][prod_ind]])
			else:
				return self.state_vars[period].__dict__[attribute][prod_ind]

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

