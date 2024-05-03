# ===============================================================================
# stockpyl - SupplyChainProduct Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview
--------

This module contains the |class_product| class, which is a product handled by a node
in a supply chain network.

.. note:: |fosct_notation|

A |class_product| is used primarily for :ref:`multi-echelon inventory optimization (MEIO) <meio_page>`
or :ref:`simulation <sim_page>`. |class_product| objects are ... TODO: info here about including these 
objects in nodes or nodeproducts.

TODO: update:
The product object contains many attributes, and different functions use different sets of attributes.
For example, the :func:`stockpyl.ssm_serial.optimize_base_stock_levels` function takes a
|class_network| whose nodes contain values for ``echelon_holding_cost``, ``lead_time``, ``stockout_cost``,
and ``demand_source`` attributes, while :func:`stockpyl.gsm_serial.optimize_committed_service_times`
uses ``local_holding_cost``, ``processing_time``, etc.
Therefore, to determine which attributes are needed, refer to the documentation for the function
you are using.


Game plan for BOM:
# TODO: delete this later
- BOM lives at product level, and does not indicate node for either product or raw material
- Every node has a dummy product with negative index when it is created. When a product is loaded into the 
	node, the dummy product is removed. If all "real" products are unloaded, a dummy product is added back.
	Indices are generated automatically on the fly. Dummy products have their ``is_dummy`` attribute set to ``True``.
- A dummy product is always assumed to have a BOM number of 1 with every product at every predecessor and
	successor, including both dummy and real products. product.get_bill_of_materials(rm_ind) returns 1 if rm_ind < 0, 
	and product.get_bill_of_materials(rm_index) returns 1 if product is a dummy product, regardless of what 
	rm_index is.
- If a node and a predecessor have no BOM relationship specified for all (rm, product) pairs,
	a BOM number of 1 is assumed for every product/RM pair. 
	This is true whether the node or predecessor have an actual product loaded, or a dummy product. 
- To set the BOM number to something other than 1, both the product and the RM must be actual products, 
	not dummy.
- If a node has supply_type 'U', the external supplier is assumed to provide a dummy raw material,
	which is not loaded into the external supplier (since a node doesn't exist for that supplier),
	but raw material inventory is allocated at the node for the external supplier's dummy product at 
	the start of the simulation. 
	The BOM number is 1 in this case. If there are multiple products at the node, they each order
	1 unit of the dummy product. The dummy product at an external supplier also has a negative
	index that is generated on the fly.
- To have an external supplier with a BOM number other than 1, you have to create a node to represent
	the external supplier. It can have zero costs and LT, etc., but must have the RM product loaded.
- In some functions, setting a product parameter to None is a shortcut for setting it to the index
	of the dummy product.
- _bill_of_materials[rm_index] = # of units of raw material rm_index required to make 1 unit of product.
- In general, I'm ensuring that everything works if _all_ nodes have products loaded or _no_ nodes have
	products loaded, but I'm less sure about the case in which some do and some don't.


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
from stockpyl.helpers import is_list, is_dict, is_integer


# ===============================================================================
# SupplyChainProduct Class
# ===============================================================================

class SupplyChainProduct(object):
	"""The |class_product| class contains the data for a product within a supply chain.
	
	All attributes except ``name``, ``id``, and ``network`` may be overridden at the node level
	by a |class_node| that handles the product. 
	TODO: update?
	
	TODO: note that GSM and SSM modules can't handle multi-product; only sim.

	Attributes
	----------
	index : int
		A numeric identifier for the product. Must be a non-negative integer.
	name : str
		A string to identify the product.
	network : |class_network|
		The network that contains this product.
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
		shipments en route from a node to its downstream successors, if any.
		If ``in_transit_holding_cost`` is ``None``, then the product's local_holding_cost
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
	TODO: decide whether disruptions are at node or product level
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
		"""SupplyChainProduct constructor method.

		Parameters
		----------
		index : int
			A numeric value to identify the product. In a |class_network|, each product
			must have a unique index.
		name : str, optional
			A string to identify the product.
		network : |class_network|, optional
			The network that contains this product.
		kwargs : optional
			Optional keyword arguments to specify node attributes.

		Raises
		------
		AttributeError
			If an optional keyword argument does not match a |class_product| attribute.
		"""
		# Initialize attributes.
		self.initialize()

		# If is_dummy is True, set this first to avoid an error when setting index to a negative number.
		if 'is_dummy' in kwargs.keys() and kwargs['is_dummy']:
			self.is_dummy = True

		# Set named attributes.
		self.index = index
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
				raise AttributeError(f"{key} is not an attribute of SupplyChainProduct")

	_DEFAULT_VALUES = {
		'_index': 0,
		'name': None,
		'network': None,
		'is_dummy': False,
		'_bill_of_materials': {},
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
#		'disruption_process': None,
		'order_capacity': None,
		'state_vars': []
	}
	
	@property
	def index(self):
		return self._index

	@index.setter
	def index(self, value):
		# Raise error if index is non-integer, or if it is negative and this is not a dummy product.
		if not is_integer(value) or (value < 0 and not self.is_dummy):
			raise ValueError('Product index must be a non-negative integer.')
		self._index = value

	# Properties and functions related to bill of materials.

	def set_bill_of_materials(self, rm_index, num_needed=1.0):
		"""Specify that ``num_needed`` units of raw material product ``rm_index`` are required in order
		to make one unit of this product.
		
		To remove a BOM relationship, call this function again, setting ``num_needed = 0`` or ``num_needed = None``.
		If ``num_needed = 0`` or ``None`` and a BOM relationship does not already exist for the specified product 
		and raw material, does nothing.

		Raises an exception if the product's index or ``rm_index`` is negative. (Negative indices are reserved for
		"dummy products" established by a simulation, and such products always have a BOM number of 1 with every
		other product.)

		Parameters
		----------
		rm_index : int
			Index of raw material product.
		num_needed : float, optional
			The number of units required, by default 1.0. Set to 0 or ``None`` to remove the BOM relationship.
		
		Raises
		------
		ValueError
			If ``self.index is None`` or ``rm_index is None``.
		"""

		if self.index < 0 or rm_index < 0:
			raise ValueError('You cannot set the BOM for dummy products (products with index < 0).')
		
		# Are we adding a BOM relationship?
		if num_needed:
			# Set self._bill_of_materials[rm_index].
			self._bill_of_materials[rm_index] = num_needed
		else:
			# We are removing a BOM relationship.
			self._bill_of_materials.pop(rm_index, None)
	
	def get_bill_of_materials(self, rm_index):
		"""Return the number of units of raw material product ``rm_index`` that are required in order
		to make one unit of this product. Returns 0 if there is no BOM relationship for this product and ``rm_index``.

		:func:`BOM` is a shortcut to this function.
		
		Parameters
		----------
		rm_index : int
			Index of raw material product.
		
		Returns
		-------
		int
			The BOM number for the (raw material, product) pair.
		"""
		# if self.index < 0 or rm_index < 0:
		# 	return 1
   
		try:
			# Return BOM number, if BOM entry exists.
			return self._bill_of_materials[rm_index]
		except:
			# No BOM relationship exists; return 0.
			return 0
		
	def BOM(self, rm_index):
		"""A shortcut to :func:`~get_bill_of_materials`."""
		return self.get_bill_of_materials(rm_index)

	@property
	def bill_of_materials_dict(self):
		"""A dict containing all non-zero bill-of-materials relationships for this product.
		``bill_of_materials_dict[rm_index]`` is the number of units of raw material ``rm_index`` 
		required to make one unit of this product.

		It is normally easier to access the bill of materials using :func:`get_bill_of_materials` 
		(or the shortcut :func:`BOM`).

		Dummy products (products with index < 0) always have a BOM number of 1 with every other product, but this is not
		reflected in the dict returned; the dict does not have entries for dummy products.

		Read only.
		"""
		return self._bill_of_materials

	@property
	def raw_materials(self):
		"""A list of all raw materials required to make this product, as |class_prod| objects. Read only."""
		if self.network is None:
			raise ValueError('self.network cannot be None when calling raw_materials.')
		return [self.network.products_by_index[rm_index] for rm_index in self.bill_of_materials_dict.keys() if self.BOM(rm_index) > 0 ]

	@property
	def raw_material_indices(self):
		"""A list of the indices of all raw materials required to make this product. Read only."""
		return [rm.index for rm in self.raw_materials]

	# Properties and functions related to network structure.

	@property
	def handling_nodes(self):
		"""A list of all nodes in the network that handle this product, 
		as |class_node| objects. Read only.
		"""		
		# TODO: unit tests
		return [node for node in self.network.nodes if self in node.products]
	
	@property
	def handling_node_indices(self):
		"""A list of indices of all nodes in the network that handle this product.
		Read only.
		"""
		return [node.index for node in self.handling_nodes()]

	# Properties related to input parameters.
	@property
	def holding_cost(self):
		"""An alias for ``local_holding_cost``. Read only.
		"""
		return self.local_holding_cost
	
	@property
	def lead_time(self):
		"""An alias for ``shipment_lead_time``."""
		return self.shipment_lead_time

	@lead_time.setter
	def lead_time(self, value):
		"""An alias for ``shipment_lead_time``."""
		self.shipment_lead_time = value

	@property
	def inventory_policy(self):
		return self._inventory_policy
	
	@inventory_policy.setter
	def inventory_policy(self, value):
		# Set _inventory_policy, and also set _inventory_policy's product
		self._inventory_policy = value
		# TODO: handle setting product and node attributes


	# Special methods.

	def __eq__(self, other):
		"""Determine whether ``other`` is equal to the product. Two products are
		considered equal if their indices are equal.

		Parameters
		----------
		other : |class_product|
			The product to compare to.

		Returns
		-------
		bool
			True if the products are equal, False otherwise.

		"""
		return self.index == (other.index if other is not None else None)

	def __ne__(self, other):
		"""Determine whether ``other`` is not equal to the product. Two products are
		considered equal if their indices are equal.

		Parameters
		----------
		other : |class_product|
			The product to compare to.

		Returns
		-------
		bool
			True if the products are not equal, False otherwise.

		"""
		return not self.__eq__(other)

	def __hash__(self):
		"""
		Return the hash for the product, which equals its index, or -1 if its index is ``None``.

		"""
		return self.index or -1

	def __repr__(self):
		"""
		Return a string representation of the |class_product| instance.

		Returns
		-------
			A string representation of the |class_product| instance.

		"""
		return "SupplyChainProduct({:s})".format(str(vars(self)))

	# Attribute management.

	def initialize(self):
		"""Initialize the parameters in the object to their default values.
		Also initializes attributes that are objects (``demand_source``, ``disruption_process``, ``_inventory_policy``):
		"""
		
		# Loop through attributes. Special handling for list and object attributes.
		for attr in self._DEFAULT_VALUES.keys():
			if attr == 'demand_source':
				self.demand_source = demand_source.DemandSource()
			elif attr == 'disruption_process':
				self.disruption_process = disruption_process.DisruptionProcess()
			elif attr == '_inventory_policy':
				self.inventory_policy = policy.Policy()
			elif is_list(self._DEFAULT_VALUES[attr]) or is_dict(self._DEFAULT_VALUES[attr]):
				setattr(self, attr, copy.deepcopy(self._DEFAULT_VALUES[attr]))
			else:
				setattr(self, attr, self._DEFAULT_VALUES[attr])

	def deep_equal_to(self, other, rel_tol=1e-8):
		"""Check whether product "deeply equals" ``other``, i.e., if all attributes are
		equal, including attributes that are themselves objects.

		Note the following caveats:

		* Does not check equality of ``network``.
		* Does not check equality of ``local_holding_cost_function`` or ``stockout_cost_function``.

		Parameters
		----------
		other : |class_product|
			The product to compare this one to.
		rel_tol : float, optional
			Relative tolerance to use when comparing equality of float attributes.

		Returns
		-------
		bool
			``True`` if the two products are equal, ``False`` otherwise.
		"""

		# Initialize name of violating attribute (used for debugging) and equality flag.
		viol_attr = None
		eq = True

		if other is None:
			eq = False
		else:
			# Special handling for some attributes.
			for attr in self._DEFAULT_VALUES.keys():
				if attr in ('network', 'local_holding_cost_function', 'stockout_cost_function'):
					# Ignore.
					pass
				elif attr == '_inventory_policy':
					# Compare inventory policies.
					if self.inventory_policy != other.inventory_policy:
						viol_attr = attr
						eq = False
				elif attr in ('local_holding_cost', 'echelon_holding_cost', 'in_transit_holding_cost', \
							  'stockout_cost', 'revenue', 'initial_inventory_level', 'initial_orders',
							  'initial_shipments', 'order_capacity'):
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
		"""Convert the |class_product| object to a dict. Converts the object recursively,
		calling ``to_dict()`` on each object that is an attribute of the product
		(|class_demand_source|, etc.).

		``network`` object is not filled, but should be filled with the network object if this
		function is called recursively from a |class_network|'s ``from_dict()`` method.

		Returns
		-------
		dict
			The dict representation of the product.
		"""
		# Initialize dict.
		product_dict = {}

		# Attributes.
		for attr in self._DEFAULT_VALUES.keys():
			# A few attributes need special handling.
			if attr == 'network':
				product_dict[attr] = None
			elif attr in ('demand_source', 'disruption_process', '_inventory_policy'):
				product_dict[attr] = None if getattr(self, attr) is None else getattr(self, attr).to_dict()
			else:
				product_dict[attr] = getattr(self, attr)

		return product_dict

	@classmethod
	def from_dict(cls, the_dict):
		"""Return a new |class_product| object with attributes copied from the
		values in ``the_dict``. List attributes are deep-copied so changes to the original dict do 
		not get propagated to the object.

		``network`` object is not filled, but should be filled with the network object if this
		function is called recursively from a |class_network|'s ``from_dict()`` method.
		 ``node`` attribute is not filled in the product's ``inventory_policy`` attribute.

		Parameters
		----------
		the_dict : dict
			Dict representation of a |class_product|, typically created using ``to_dict()``.

		Returns
		-------
		|class_product|
			The object converted from the dict.
		"""
		if the_dict is None:
			product = cls()
		else:
			# Build empty SupplyChainProduct.
			product = cls(the_dict['_index'], is_dummy=the_dict['is_dummy'])
			# Fill attributes.
			for attr in cls._DEFAULT_VALUES.keys():
				# Some attributes require special handling.
				if attr == 'demand_source':
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
						# Set policy's node to None.
						value.node = None
					else:
						value = policy.Policy.from_dict(None)
					# Remove "_" from attr so we are setting the property, not the attribute.
					attr = 'inventory_policy'
				elif attr == '_bill_of_materials':
					# If keys are integers as strings (this happens if loading from a file), replace with integers.
					if attr in the_dict:
						value = {int(k): v for k, v in the_dict[attr].items()}
					else:
						value = copy.deepcopy(cls._DEFAULT_VALUES[attr])
				else:
					if attr in the_dict:
						value = the_dict[attr]
					else:
						value = cls._DEFAULT_VALUES[attr]
				setattr(product, attr, value)

		return product


	@classmethod
	def from_node(cls, the_node):
		"""Return a new |class_product| object with attributes copied from the
		corresponding attributes in ``the_node``. (This is useful mostly for debugging.)
		List attributes are deep-copied so changes to the original node do not get propagated to the product.

		Only copies attributes that are present in both classes.

		``network`` attribute is copied from the node (not deep-copied). ``node`` attribute
		is not filled in the product's ``inventory_policy`` attribute.

		Parameters
		----------
		the_node : |class_node|
			Node object whose attributes are to be copied to the product.

		Returns
		-------
		|class_product|
			The product object converted from the node.
		"""
		if the_node is None:
			product = cls()
		else:
			# Build empty SupplyChainProduct.
			product = cls(the_node.index)
			# Fill attributes.
			for attr in cls._DEFAULT_VALUES.keys():
				# Some attributes require special handling.
				if attr in ('demand_source', 'disruption_process'):
					value = copy.deepcopy(getattr(the_node, attr))
				elif attr == '_inventory_policy':
					value = copy.deepcopy(getattr(the_node, attr))
					# Set policy's node to None.
					value.node = None
					# Remove "_" from attr so we are setting the property, not the attribute.
					attr = 'inventory_policy'
				else:
					if hasattr(the_node, attr):
						value = getattr(the_node, attr)
					else:
						value = cls._DEFAULT_VALUES[attr]
				setattr(product, attr, value)

		return product

