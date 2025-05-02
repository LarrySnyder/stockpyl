# ===============================================================================
# stockpyl - NodeStateVars Class
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview
--------

This module contains the |class_state_vars| class, which keeps track of the state variables
for a node during a simulation.

.. note:: |node_stage|

.. note:: |fosct_notation|


API Reference
-------------


"""

# ===============================================================================
# Imports
# ===============================================================================

import numpy as np
import copy

from stockpyl.helpers import change_dict_key, is_integer


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
		``inbound_shipment_pipeline[p][rm][r]`` = shipment quantity of raw material ``rm`` 
		arriving from predecessor node ``p`` in ``r`` periods from the current period.
		If ``p`` is ``None``, refers to external supplier.
	inbound_shipment : dict
		``inbound_shipment[p][rm]`` = shipment quantity of raw material ``rm`` arriving at node from
		predecessor node ``p`` in the current period. If ``p`` is ``None``,
		refers to external supplier. 
	inbound_order_pipeline : dict
		``inbound_order_pipeline[s][prod][r]`` = order quantity for product ``prod`` arriving from
		successor node ``s`` in ``r`` periods from the current period.
		If ``s`` is ``None``, refers to external demand. If ``s`` is single-product or external
		demand, ``prod=None``.
	inbound_order : dict
		``inbound_order[s][prod]`` = order quantity for product ``prod`` arriving at node from successor
		node ``s`` in the current period. If ``s`` is ``None``, refers to
		external demand. If ``s`` is single-product or external
		demand, ``prod=None``.
	demand_cumul : float
		``demand_cumul[prod]`` = cumulative demand (from all sources, internal and external) for product ``prod``
		from period 0 through the current period. If node is single-product, ``prod=None``. 
		(Used for ``fill_rate`` calculation.)
	outbound_shipment : dict
		``outbound_shipment[s][prod]`` = outbound shipment of product ``prod`` to successor node ``s``.
		If ``s`` is ``None``, refers to external demand. If node is single-product, ``prod=None``.
	on_order_by_predecessor : dict
		``on_order_by_predecessor[p][rm]`` = on-order quantity (items that have been
		ordered from predecessor node ``p`` but not yet received) for raw material ``rm`` at node. If ``p`` is ``None``, 
		refers to external supply.
	inventory_level : float
		``inventory_level[prod]`` = inventory level (positive, negative, or zero) of product ``prod`` at node.
	backorders_by_successor : dict
		``backorders_by_successor[s][prod]`` = number of backorders of product ``prod`` for successor
		``s``. If ``s`` is ``None``, refers to external demand. 
	outbound_disrupted_items : dict
		``outbound_disrupted_items[s][prod]`` = number of items of product ``prod`` held for successor ``s``
		due to a type-SP disruption at ``s``. (Since external demand cannot be
		disrupted, ``outbound_disrupted_items[None][prod]`` always = 0.) 
		Items held for successor are not included in ``backorders_by_successor``.
		Sum over all successors of ``backorders_by_successor + outbound_disrupted_items``
		should always equal max{0, -``inventory_level``}.
	inbound_disrupted_items : dict
		``inbound_disrupted_items[p][rm]`` = number of items of raw material ``rm`` from predecessor ``p`` that are
		being held before receipt due to a type-RP disruption at the node.
	raw_material_inventory : dict
		``raw_material_inventory[rm]`` = number of units of raw material ``rm`` from _all_ predecessors 
		in raw-material inventory at node. 
	pending_finished_goods : dict
		``pending_finished_goods[prod]`` = number of units of product ``prod`` that are waiting to be
		produced from raw materials. (This is used internally to ensure that raw materials are used to produce
		the finished goods that they were originally ordered for.)
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
		``demand_met_from_stock[prod]`` = demand for product ``prod`` met from stock at the node in the period.
		If node is single-product, ``prod=None``.
	demand_met_from_stock_cumul : float
		``demand_met_from_stock_cumul[prod]`` = cumulative demand for product ``prod`` met from stock from 
		period 0 through the current period. If node is single-product, ``prod=None``.
		(Used for ``fill_rate`` calculation.)
	fill_rate : float
		``fill_rate[prod]`` = cumulative fill rate for product ``prod`` in periods 0, ..., period.
		If node is single product, ``prod=None``.
	order_quantity : dict
		``order_quantity[p][rm]`` = order quantity for raw material ``rm`` placed by the node to
		predecessor ``p`` in period. If ``p`` is ``None``, refers to external supplier. 
	order_quantity_fg : dict
		``order_quantity_fg[prod]`` = finished-goods order quantity for product ``prod`` at the 
		node in period.
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

			# Build some shortcuts.
			rm_indices = {p.index if p else None: (p.product_indices if p else [node._external_supplier_dummy_product.index]) \
				   for p in self.node.predecessors(include_external=True)}

			# Initialize dicts with appropriate keys. (inbound_shipment_pipeline gets
			# order_lead_time+shipment_lead_time slots for orders to external supplier)
			self.inventory_level = {prod_index: 0 for prod_index in self.node.product_indices}
			self.inbound_shipment_pipeline = {}
			for p_index in self.node.predecessor_indices(include_external=True):
				self.inbound_shipment_pipeline[p_index] = {}
				for rm_index in self.node.raw_materials_by_product(product='all', return_indices=True, network_BOM=True):
					# Find a product at this node that uses raw material rm_index from predecessor p_index,
					# and use its lead times. If there is more than one such product, use the last one found.
					for prod_index in self.node.product_indices:
						if rm_index in self.node.raw_materials_by_product(product=prod_index, return_indices=True, network_BOM=True) and \
							p_index in self.node.raw_material_suppliers_by_raw_material(raw_material=rm_index, return_indices=True, network_BOM=True):
							# Get lead times for this product. 
							order_lead_time = (self.node.get_attribute('order_lead_time', product=prod_index) or 0)
							shipment_lead_time = (self.node.get_attribute('shipment_lead_time', product=prod_index) or 0)
							self.inbound_shipment_pipeline[p_index][rm_index] = [0] * (order_lead_time + shipment_lead_time + 1)			  
			self.inbound_shipment = {p_index: {prod_index: 0 for prod_index in rm_indices[p_index]}
		   							 for p_index in self.node.predecessor_indices(include_external=True)}
			self.inbound_order = {s_index: {prod_index: 0 for prod_index in node.product_indices} 
												for s_index in self.node.successor_indices(include_external=True)}
			self.outbound_shipment = {s_index: {prod_index: 0 for prod_index in node.product_indices} 
								   				for s_index in self.node.successor_indices(include_external=True)}
			self.on_order_by_predecessor = {p_index: {prod_index: 0 for prod_index in rm_indices[p_index]}
												for p_index in self.node.predecessor_indices(include_external=True)}
			self.backorders_by_successor = {s_index: {prod_index: 0 for prod_index in node.product_indices}
												for s_index in self.node.successor_indices(include_external=True)}
			self.outbound_disrupted_items = {s_index: {prod_index: 0 for prod_index in node.product_indices}
												for s_index in self.node.successor_indices(include_external=True)}
			self.inbound_disrupted_items = {p_index: {prod_index: 0 for prod_index in rm_indices[p_index]}
												for p_index in self.node.predecessor_indices(include_external=True)}
			self.order_quantity = {p_index: {prod_index: 0 for prod_index in rm_indices[p_index]}
												for p_index in self.node.predecessor_indices(include_external=True)}
			self.raw_material_inventory = {prod_index: 0 for prod_index \
				in self.node.raw_materials_by_product(product='all', return_indices=True, network_BOM=True)}
			self.order_quantity_fg = {prod_index: 0 for prod_index in self.node.product_indices}
			self.pending_finished_goods = {prod_index: 0 for prod_index in self.node.product_indices}

			# inbound_order_pipeline needs some special handling -- external customer must be added
			# separately since it does not have its own node, or its own order lead time.
			self.inbound_order_pipeline = {}
			for s in self.node.successors(include_external=False):
				s_index = s.index
				self.inbound_order_pipeline[s_index] = {}
				for prod_index in self.node.product_indices:
					# Does s order prod_index from node?
					if prod_index in s.raw_materials_by_product(product='all', return_indices=True, network_BOM=True) \
						and node.index in s.raw_material_suppliers_by_raw_material(raw_material=prod_index, return_indices=True, network_BOM=True):
						# Find a product at s that orders this raw material at node, to get its order_lead_time.
						downstream_prod_index = s.products_by_raw_material(prod_index)[0]
						order_lead_time = s.get_attribute('order_lead_time', product=downstream_prod_index) or 0
					else:
						order_lead_time = 0
					self.inbound_order_pipeline[s_index][prod_index] = [0] * (order_lead_time + 1)
			for prod_index in node.product_indices:
				ds = node.get_attribute('demand_source', prod_index)
				if ds is not None and ds.type is not None:
					if None not in self.inbound_order_pipeline:
						self.inbound_order_pipeline[None] = {}
					self.inbound_order_pipeline[None][prod_index] = [0]

			# Fill rate quantities.
			self.demand_cumul = {prod_index: 0 for prod_index in self.node.product_indices}
			self.demand_met_from_stock = {prod_index: 0 for prod_index in self.node.product_indices}
			self.demand_met_from_stock_cumul = {prod_index: 0 for prod_index in self.node.product_indices}
			self.fill_rate = {prod_index: 0 for prod_index in self.node.product_indices}

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
			self.order_quantity_fg = {}
			self.pending_finished_goods = {}

		# Remaining state variables.
		self.disrupted = False

		# Costs: each refers to a component of the cost (or the total cost)
		# incurred at the node in the period.
		self.holding_cost_incurred = 0
		self.stockout_cost_incurred = 0
		self.in_transit_holding_cost_incurred = 0
		self.revenue_earned = 0
		self.total_cost_incurred = 0

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

	# --- State Variable Functions --- #
	# These are basically shortcuts to the individual attributes that offer more flexibility
	# in how products are specified (or not).
 
	def get_inbound_shipment_pipeline(self, periods_from_now, predecessor=None, raw_material=None):
		"""Shortcut to ``self.inbound_shipment_pipeline[predecessor][raw_material][periods_from_now]``
		that does not require ``predecessor`` or ``raw_material`` to be specified if they are inferrable.

		Parameters
		----------
		periods_from_now : int
			Get pipeline inventory arriving this many periods into the future.
		predecessor : |class_node| or int, optional
			Predecessor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect predecessor automatically for a single-predecessor node. If node has
			both an external supplier and a predecessor node and ``predecessor`` is ``None``,
			returns the external supplier.
		raw_material : |class_product| or int, optional
			Raw material (as a |class_product|) or its index, or ``None`` (the default) to detect 
			raw material automatically for a single-raw material node (including a dummy product).

		Returns
		-------
		float
			Inbound shipment pipeline.
		"""
		_, pred_ind = self.node.validate_predecessor(predecessor)
		_, rm_ind = self.node.validate_raw_material(raw_material=raw_material, predecessor=predecessor)
			
		return self.inbound_shipment_pipeline[pred_ind][rm_ind][periods_from_now] 
	
	def get_inbound_shipment(self, predecessor=None, raw_material=None):
		"""Shortcut to ``self.inbound_shipment[predecessor][raw_material]``
		that does not require ``predecessor`` or ``raw_material`` to be specified if they are inferrable.

		Parameters
		----------
		predecessor : |class_node| or int, optional
			Predecessor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect predecessor automatically for a single-predecessor node. If node has
			both an external supplier and a predecessor node and ``predecessor`` is ``None``,
			returns the external supplier.
		raw_material : |class_product| or int, optional
			Raw material (as a |class_product|) or its index, or ``None`` (the default) to detect 
			raw material automatically for a single-raw material node (including a dummy product).

		Returns
		-------
		float
			Inbound shipment.
		"""
		_, pred_ind = self.node.validate_predecessor(predecessor)
		_, rm_ind = self.node.validate_raw_material(raw_material=raw_material, predecessor=predecessor)
			
		return self.inbound_shipment[pred_ind][rm_ind] 
	
	def get_inbound_order_pipeline(self, periods_from_now, successor=None, product=None):
		"""Shortcut to ``self.inbound_order_pipeline[successor][product][periods_from_now]``
		that does not require ``successor`` or ``product`` to be specified if they are inferrable.

		Parameters
		----------
		periods_from_now : int
			Get pipeline order arriving this many periods into the future.
		successor : |class_node| or int, optional
			Successor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect successor automatically for a single-successor node. If node has
			both an external customer and a successor node and ``successor`` is ``None``,
			returns the external customer.
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Inbound order pipeline.
		"""
		_, succ_ind = self.node.validate_successor(successor)
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.inbound_order_pipeline[succ_ind][prod_ind][periods_from_now] 
	
	def get_inbound_order(self, successor=None, product=None):
		"""Shortcut to ``self.inbound_order[successor][product]``
		that does not require ``successor`` or ``product`` to be specified if they are inferrable.

		Parameters
		----------
		successor : |class_node| or int, optional
			Successor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect successor automatically for a single-successor node. If node has
			both an external customer and a successor node and ``successor`` is ``None``,
			returns the external customer.
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Inbound order.
		"""
		_, succ_ind = self.node.validate_successor(successor)
		_, rm_ind = self.node.validate_product(product=product)
			
		return self.inbound_order[succ_ind][rm_ind] 
	
	def get_demand_cumul(self, product=None):
		"""Shortcut to ``self.demand_cumul[product]``
		that does not require ``product`` to be specified if it is inferrable.

		Parameters
		----------
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Cumulative demand.
		"""
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.demand_cumul[prod_ind]

	def get_outbound_shipment(self, successor=None, product=None):
		"""Shortcut to ``self.outbound_shipment[successor][product]``
		that does not require ``successor`` or ``product`` to be specified if they are inferrable.

		Parameters
		----------
		successor : |class_node| or int, optional
			Successor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect successor automatically for a single-successor node. If node has
			both an external customer and a successor node and ``successor`` is ``None``,
			returns the external customer.
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Outbound shipment.
		"""
		_, succ_ind = self.node.validate_successor(successor)
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.outbound_shipment[succ_ind][prod_ind] 

	def get_on_order_by_predecessor(self, predecessor=None, raw_material=None):
		"""Shortcut to ``self.on_order_by_predecessor[predecessor][raw_material]``
		that does not require ``predecessor`` or ``raw_material`` to be specified if they are inferrable.

		Parameters
		----------
		predecessor : |class_node| or int, optional
			Predecessor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect predecessor automatically for a single-predecessor node. If node has
			both an external supplier and a predecessor node and ``predecessor`` is ``None``,
			returns the external supplier.
		raw_material : |class_product| or int, optional
			Raw material (as a |class_product|) or its index, or ``None`` (the default) to detect 
			raw material automatically for a single-raw material node (including a dummy product).

		Returns
		-------
		float
			On order by predecessor.
		"""
		_, pred_ind = self.node.validate_predecessor(predecessor)
		_, rm_ind = self.node.validate_raw_material(raw_material=raw_material, predecessor=predecessor)
			
		return self.on_order_by_predecessor[pred_ind][rm_ind] 

	def get_inventory_level(self, product=None):
		"""Shortcut to ``self.inventory_level[product]``
		that does not require ``product`` to be specified if it is inferrable.

		Parameters
		----------
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Inventory level.
		"""
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.inventory_level[prod_ind]

	def get_backorders_by_successor(self, successor=None, product=None):
		"""Shortcut to ``self.backorders_by_successor[successor][product]``
		that does not require ``successor`` or ``product`` to be specified if they are inferrable.

		Parameters
		----------
		successor : |class_node| or int, optional
			Successor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect successor automatically for a single-successor node. If node has
			both an external customer and a successor node and ``successor`` is ``None``,
			returns the external customer.
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Backorders by successor.
		"""
		_, succ_ind = self.node.validate_successor(successor)
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.backorders_by_successor[succ_ind][prod_ind] 

	def get_outbound_disrupted_items(self, successor=None, product=None):
		"""Shortcut to ``self.outbound_disrupted_items[successor][product]``
		that does not require ``successor`` or ``product`` to be specified if they are inferrable.

		Parameters
		----------
		successor : |class_node| or int, optional
			Successor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect successor automatically for a single-successor node. If node has
			both an external customer and a successor node and ``successor`` is ``None``,
			returns the external customer.
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Outbound disrupted items.
		"""
		_, succ_ind = self.node.validate_successor(successor)
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.outbound_disrupted_items[succ_ind][prod_ind] 

	def get_inbound_disrupted_items(self, predecessor=None, raw_material=None):
		"""Shortcut to ``self.inbound_disrupted_items[predecessor][raw_material]``
		that does not require ``predecessor`` or ``raw_material`` to be specified if they are inferrable.

		Parameters
		----------
		predecessor : |class_node| or int, optional
			Predecessor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect predecessor automatically for a single-predecessor node. If node has
			both an external supplier and a predecessor node and ``predecessor`` is ``None``,
			returns the external supplier.
		raw_material : |class_product| or int, optional
			Raw material (as a |class_product|) or its index, or ``None`` (the default) to detect 
			raw material automatically for a single-raw material node (including a dummy product).

		Returns
		-------
		float
			Inbound disrupted items.
		"""
		_, pred_ind = self.node.validate_predecessor(predecessor)
		_, rm_ind = self.node.validate_raw_material(raw_material=raw_material, predecessor=predecessor)
			
		return self.inbound_disrupted_items[pred_ind][rm_ind] 

	def get_raw_material_inventory(self, raw_material=None):
		"""Shortcut to ``self.raw_material_inventory[raw_material]``
		that does not require ``raw_material`` to be specified if it is inferrable.

		Parameters
		----------
		raw_material : |class_product| or int, optional
			Raw material (as a |class_product|) or its index, or ``None`` (the default) to detect 
			raw material automatically for a single-raw material node (including a dummy product).

		Returns
		-------
		float
			Raw material inventory.
		"""
		_, rm_ind = self.node.validate_raw_material(raw_material=raw_material)
			
		return self.raw_material_inventory[rm_ind]

	def get_pending_finished_goods(self, product=None):
		"""Shortcut to ``self.pending_finished_goods[product]``
		that does not require ``product`` to be specified if it is inferrable.

		Parameters
		----------
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Pending finished goods.
		"""
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.pending_finished_goods[prod_ind]

	def get_demand_met_from_stock(self, product=None):
		"""Shortcut to ``self.demand_met_from_stock[product]``
		that does not require ``product`` to be specified if it is inferrable.

		Parameters
		----------
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Demand met from stock.
		"""
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.demand_met_from_stock[prod_ind]

	def get_demand_met_from_stock_cumul(self, product=None):
		"""Shortcut to ``self.demand_met_from_stock_cumul[product]``
		that does not require ``product`` to be specified if it is inferrable.

		Parameters
		----------
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Cumulative demand met from stock.
		"""
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.demand_met_from_stock_cumul[prod_ind]

	def get_fill_rate(self, product=None):
		"""Shortcut to ``self.fill_rate[product]``
		that does not require ``product`` to be specified if it is inferrable.

		Parameters
		----------
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Fill rate.
		"""
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.fill_rate[prod_ind]

	def get_order_quantity(self, predecessor=None, raw_material=None):
		"""Shortcut to ``self.order_quantity[predecessor][raw_material]``
		that does not require ``predecessor`` or ``raw_material`` to be specified if they are inferrable.

		Parameters
		----------
		predecessor : |class_node| or int, optional
			Predecessor node (as a |class_node|) or its index, or ``None`` (the default)
			to detect predecessor automatically for a single-predecessor node. If node has
			both an external supplier and a predecessor node and ``predecessor`` is ``None``,
			returns the external supplier.
		raw_material : |class_product| or int, optional
			Raw material (as a |class_product|) or its index, or ``None`` (the default) to detect 
			raw material automatically for a single-raw material node (including a dummy product).

		Returns
		-------
		float
			Order quantity.
		"""
		_, pred_ind = self.node.validate_predecessor(predecessor)
		_, rm_ind = self.node.validate_raw_material(raw_material=raw_material, predecessor=predecessor)
			
		return self.order_quantity[pred_ind][rm_ind] 

	def get_order_quantity_fg(self, product=None):
		"""Shortcut to ``self.order_quantity_fg[product]``
		that does not require ``product`` to be specified if it is inferrable.

		Parameters
		----------
		product : |class_product| or int, optional
			Product (as a |class_product|) or its index, or ``None`` (the default) to detect 
			product automatically for a single-product node (including a dummy product).

		Returns
		-------
		float
			Finished-goods order quantity.
		"""
		_, prod_ind = self.node.validate_product(product=product)
			
		return self.order_quantity_fg[prod_ind]




	# --- Calculated State Variables --- #
	# These are calculated based on the primary state variables.

	@property
	def on_hand(self):
		"""Current on-hand inventory at node. If node is single-product, returns the on-hand inventory as a singleton. 
		If node is multi-product, returns dict whose 
		keys are product indices and whose values are the corresponding on-hand inventory levels. Read only.
		"""
		if self.node.is_multiproduct:
			return {prod_index: max(0, self.inventory_level[prod_index]) for prod_index in self.node.product_indices}
		else:
			return max(0, self.inventory_level[self.node._dummy_product.index])

	@property
	def backorders(self):
		"""Current number of backorders. Should always equal sum over all successors ``s``
		of ``backorders_by_successor[s]`` + ``outbound_disrupted_items[s]``. If node is single-product, 
		returns the backorders as a singleton. If node is 
		multi-product, returns dict whose keys are product indices and whose values are the
		corresponding numbers of backorders. Read only.
		"""
		if self.node.is_multiproduct:
			return {prod_index: max(0, -self.inventory_level[prod_index]) for prod_index in self.node.product_indices}
		else:
			return max(0, -self.inventory_level[self.node._dummy_product.index])

	def in_transit_to(self, successor, product=None):
		"""Return current total inventory of ``product`` in transit to ``successor``.
		Includes items that will be/have been delivered during the current period.

		If the node is single-product, either set ``product`` to the single product, or to ``None``
		and the function will determine the product automatically.

		Parameters
		----------
		successor : |class_node|
			The successor node.
		product : |class_product| or int, optional
			The outbound product (as a |class_product| object or index), or 
			``None`` if ``successor`` is single-product.

		Returns
		-------
		float
			The current inventory in transit to the successor.
		"""
		# Validate parameters.
		_, prod_ind = self.node.validate_product(product)
		# if prod_index is not None and prod_index not in self.node.product_indices:
		# 	raise ValueError(f'{prod_index} is not a product at node {self.node.index}.')
		if prod_ind is not None and (self.node.index, prod_ind) not in \
			successor.supplier_raw_material_pairs_by_product(product='all', return_indices=True, network_BOM=True):
			raise ValueError(f'Node {self.node.index} does not provide product {prod_ind} to node {successor.index}.')
		
		return np.sum([successor.state_vars[self.period].inbound_shipment_pipeline[self.node.index][prod_ind][:]])

	def in_transit_from(self, predecessor=None, raw_material=None):
		"""Return current total inventory of ``raw_material`` in transit from a given predecessor.
		Includes items that will be/have been delivered during the current period.

		Set ``predecessor`` to ``None`` if the predecessor is the external supplier.
		If the node has a single raw material, either set ``raw_material`` to the single raw material, or to ``None``
		and the function will determine the raw material automatically.

		Parameters
		----------
		predecessor : |class_node|
			The predecessor node.
		raw_material : |class_product| or int, optional
			The inbound raw_material (as a |class_product| object or index), or ``None`` if 
			``predecessor`` has a single product or external supplier.

		Returns
		-------
		float
			The current inventory in transit from the predecessor.
		"""
		# Validate parameters.
		_, rm_ind = self.node.validate_raw_material(raw_material, predecessor)
		# if rm_ind is None:
		# 	rm_ind = self.node._external_supplier_dummy_product.index
		_, pred_ind = self.node.validate_predecessor(predecessor, rm_ind)
			
		# 					Get predecessor index. Also get prod_index if it's None.
		# if predecessor is None:
		# 	p_ind = None
		# 	if prod_index is None:
		# 		prod_index = self.node._external_supplier_dummy_product.index
		# else:
		# 	p_ind = predecessor.index
		# 	if prod_index is None:
		# 		prod_index = predecessor.products[0].index

		# # Validate parameters.
		# if prod_index is not None and prod_index not in self.inbound_shipment_pipeline[p_ind].keys():
		# 	raise ValueError(f'{prod_index} is not a product at node {p_ind}.')

		return np.sum(self.inbound_shipment_pipeline[pred_ind][rm_ind][:])

	def in_transit(self, product=None):
		"""Current inventory of raw materials for ``product`` that is in transit to the node.  Read only.
		
		In-transit items are counted using the "units" of the node (or node-product pair) itself.
		That is, each in-transit quantity is divided by the number of units of the inbound item
		required to make one unit of ``product`` at this node, according to the bill of materials; and then 
		the sum of those quantities is divided by the total number of raw materials required for this node (or node-product pair). 

		For example, if the bill of materials specifies that to make one unit at the node requires
		2 units from predecessor node A and 6 units from predecessor node B, and if there are 
		10 in-transit units from A and 18 from B, then ``in_transit`` equals 

		.. math::

			\\frac{\\frac{10}{2} + \\frac{18}{6}}{2} = 4

		If the node is single-product, either set ``product`` to the single product, or to ``None``
		and the function will determine the product automatically. 
		
		If the node has multiple products that use the same raw material, this function includes all units of that
		raw material, even though some of them may wind up being used to make products other than ``product``.

		To get the number of units in transit by predecessor and/or product, use :func:`in_transit_from`.
		
		.. versionchanged:: 1.0	
			This was previously a property and is now a function.
		
							
		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index), or ``None`` to set the product 
			automatically if node is single-product.

		Returns
		-------
		float
			The current inventory in transit from predecessors.
		"""
		# Validate parameters.
		_, prod_ind = self.node.validate_product(product)
		# if prod_index is not None and prod_index not in self.node.product_indices:
		# 	raise ValueError(f'{prod_index} is not a product at node {self.node.index}.')
		
		# # Determine product index.
		# prod_index = prod_index or self.node.product_indices[0]

		total_in_transit = np.sum([
				self.in_transit_from(p, rm_index) 
				* self.node.NBOM(product=prod_ind, predecessor=p.index if p is not None else None, raw_material=rm_index)
			for rm_index in self.node.raw_materials_by_product(product=prod_ind, return_indices=True, network_BOM=True)
			for p in self.node.raw_material_suppliers_by_raw_material(raw_material=rm_index, network_BOM=True)
		])

		if total_in_transit == 0:
			return 0
		else:
			return total_in_transit / len(self.node.raw_materials_by_product(product=prod_ind, network_BOM=True))

	def on_order(self, product=None):
		"""Current inventory of raw materials for ``product`` that is on order to the node. Read only.
		
		On-order items are counted using the "units" of the node (or node-product pair) itself.
		That is, each on-order quantity is divided by the number of units of the inbound item
		required to make one unit of product ``product`` at this node, according to the bill of materials; and then 
		the sum of those quantities is divided by the total number of raw materials required for this node (or node-product pair). 

		For example, if the bill of materials specifies that to make one unit at the node requires
		2 units from predecessor node A and 6 units from predecessor node B, and if there are 
		10 on-order units from A and 18 from B, then ``on_order`` equals 

		.. math::

		\\frac{\\frac{10}{2} + \\frac{18}{6}}{2} = 4

		If the node is single-product, either set ``product`` to the single product, or to ``None``
		and the function will determine the product automatically. 
		
		If the node has multiple products that use the same raw material, this function includes all units of that
		raw material, even though some of them may wind up being used to make products other than ``product``.

		.. versionchanged:: 1.0	
			This was previously a property and is now a function.
		
		
		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index), or ``None`` to set the product 
			automatically if node is single-product.

		Returns
		-------
		float
			The current inventory on order from predecessors.
		"""
		# Validate parameters.
		_, prod_ind = self.node.validate_product(product)
		# if prod_index is not None and prod_index not in self.node.product_indices:
		# 	raise ValueError(f'{prod_index} is not a product at node {self.node.index}.')
		
		# # Determine product index. 
		# prod_index = prod_index or self.node.product_indices[0]

		total_on_order = np.sum([
				self.on_order_by_predecessor[p][rm_index]
				/ self.node.NBOM(product=prod_ind, predecessor=p, raw_material=rm_index)
			for rm_index in self.node.raw_materials_by_product(product=prod_ind, return_indices=True, network_BOM=True)
			for p in self.node.raw_material_suppliers_by_raw_material(raw_material=rm_index, return_indices=True, network_BOM=True)
		])

		if total_on_order == 0:
			return 0
		else:
			return total_on_order / len(self.node.raw_materials_by_product(product=prod_ind, network_BOM=True))

	def raw_material_aggregate(self, product=None):
		"""Current raw materials for ``product`` that are in raw-material inventory at the node. Read only.
		
		Raw materials are counted using the "units" of the node (or node-product pair) itself.
		That is, each raw material quantity is divided by the number of units of the raw material
		required to make one unit of product ``product`` at this node, according to the bill of materials; and then 
		the sum of those quantities is divided by the total number of raw materials required for this node (or node-product pair). 

		For example, if the bill of materials specifies that to make one unit at the node requires
		2 units from predecessor node A and 6 units from predecessor node B, and if there are 
		10 node-A units and 18 node-B units in raw material inventory at the node, then ``raw_material_aggregate`` equals 

		.. math::

		\\frac{\\frac{10}{2} + \\frac{18}{6}}{2} = 4

		If the node is single-product, either set ``product`` to the single product, or to ``None``
		and the function will determine the product automatically. 
		
		If the node has multiple products that use the same raw material, this function includes all units of that
		raw material, even though some of them may wind up being used to make products other than ``product``.

		.. versionchanged:: 1.0	
			This was previously a property and is now a function.
		
		
		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index), or ``None`` to set the product 
			automatically if node is single-product.

		Returns
		-------
		float
			The current raw material inventory.
		"""
		# Validate parameters.
		prod_obj, prod_ind = self.node.validate_product(product)
		# if prod_index is not None and prod_index not in self.node.product_indices:
		# 	raise ValueError(f'{prod_index} is not a product at node {self.node.index}.')
		
		# # Determine product index.
		# prod_index = prod_index or self.node.product_indices[0]
		# prod = self.node.products_by_index[prod_index]

		total_raw_material = 0
		for rm_index in self.node.raw_materials_by_product(product=prod_ind, return_indices=True, network_BOM=True):
			BOM = prod_obj.BOM(rm_index) 
			if BOM == 0:
				# rm_index has no BOM relationship, so it is only in the network BOM; therefore,
				# its BOM number is 1.
				BOM = 1

			total_raw_material += self.raw_material_inventory[rm_index] * BOM

		if total_raw_material == 0:
			return 0
		else:
			return total_raw_material / len(self.node.raw_materials_by_product(product=prod_ind, network_BOM=True))

	def inbound_disrupted_items_aggregate(self, product=None):
		"""Current total inbound disrupted inventory of raw materials for ``product``. Read only.
		
		Inbound items are counted using the "units" of the node (or node-product pair) itself.
		That is, each inbound quantity is divided by the number of units of the inbound item
		required to make one unit of ``product`` at this node, according to the bill of materials; and then 
		the sum of those quantities is divided by the total number of raw materials required for this node (or node-product pair). 

		For example, if the bill of materials specifies that to make one unit at the node requires
		2 units from predecessor node A and 6 units from predecessor node B, and if there are 
		10 inbound disrupted units from A and 18 from B, then ``inbound_disrupted_items_aggregate`` equals 

		.. math::

		\\frac{\\frac{10}{2} + \\frac{18}{6}}{2} = 4

		If the node is single-product, either set ``product`` to the single product, or to ``None``
		and the function will determine the product automatically. 
		
		If the node has multiple products that use the same raw material, this function includes all disrupted units of that
		raw material, even though some of them may wind up being used to make products other than ``product``.

		.. versionchanged:: 1.0	
			This was previously a property and is now a function.
		
		
		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index), or ``None`` to set the product 
			automatically if node is single-product.

		Returns
		-------
		float
			The current disrupted inventory from predecessors.
		"""
		# Validate parameters.
		_, prod_ind = self.node.validate_product(product)
		# if prod_index is not None and prod_index not in self.node.product_indices:
		# 	raise ValueError(f'{prod_index} is not a product at node {self.node.index}.')
		
		# # Determine product index. 
		# prod_index = prod_index or self.node.product_indices[0]

		total_disrupted_items = np.sum([
				self.inbound_disrupted_items[p][rm_index]
				* self.node.NBOM(product=prod_ind, predecessor=p, raw_material=rm_index)
			for rm_index in self.node.raw_materials_by_product(product=prod_ind, return_indices=True, network_BOM=True)
			for p in self.node.raw_material_suppliers_by_raw_material(raw_material=rm_index, return_indices=True, network_BOM=True)
		])

		if total_disrupted_items == 0:
			return 0
		else:
			return total_disrupted_items / len(self.node.raw_materials_by_product(product=prod_ind, network_BOM=True))

	def inventory_position(self, product=None, exclude_earmarked_units=False):
		"""Current (local) inventory position at node for ``product``. 
		Equals inventory level plus pipeline inventory. (Pipeline inventory equals on-order inventory of the raw material,
		raw material inventory that has not yet been processed, and inbound disrupted items of the
		raw material due to type-RP disruptions). Inventory position is expressed in the units of the product
		(not the raw materials).

		If the product uses multiple raw materials, the pipeline inventory is the maximum number
		of units of the product that can be produced, given the quantities of raw materials in the pipeline.
		For example, suppose product A requires 10 units of product B and 5 units of product C; there are
		4 units of product A on hand; and there are 20 units of product B and 15 units of product C in the pipeline.
		The the inventory level is 4, and the pipeline inventory contains enough raw materials to make 2 units 
		of product A. So, the inventory position is 6.

		If ``exclude_earmarked_units`` is ``True``, raw materials that are already "earmarked" for a different 
		product at this node are excluded from the pipeline inventory. In particular, the pipeline of a given
		raw material is reduced by the sum, over all _other_ products at the node, of the number of units
		of that product that are pending times the NBOM for that product/raw material.

		If the node is single-product, either set ``product`` to the single product, or to ``None``
		and the function will determine the product automatically. If the node is multi-product, ``product`` must be
		set to a single product at the node.

		If the node has multiple products that use the same raw material, the inventory position returned by this function includes all units of that
		raw material, even though some of them may wind up being used to make products other than ``product``.

		Parameters
		----------
		product : |class_product| or int, optional
			The product (as a |class_product| object or index), or ``None`` to set the product 
			automatically if node is single-product.

		Returns
		-------
		float
			The inventory position.
		"""

		# Validate parameters.
		_, prod_ind = self.node.validate_product(product)
		# if prod_index is not None and prod_index not in self.node.product_indices:
		# 	raise ValueError(f'{prod_index} is not a product at node {self.node.index}.')
		
		# # Determine product index.
		# prod_index = prod_index or self.node.product_indices[0]

		# Determine total units of each RM in the pipeline, converted to units of the downstream product.
		pipeline = {}
		for rm_index in self.node.raw_materials_by_product(product=prod_ind, return_indices=True, network_BOM=True):
			# Calculate pipeline, in upstream units.
			pipeline[rm_index] = self.raw_material_inventory[rm_index]
			for pred_index in self.node.raw_material_suppliers_by_raw_material(raw_material=rm_index, return_indices=True, network_BOM=True):
				pipeline[rm_index] += (self.on_order_by_predecessor[pred_index][rm_index] \
										+ self.inbound_disrupted_items[pred_index][rm_index])
			
			# Subtract earmarked units, if requested.
			if exclude_earmarked_units:
				for other_prod_ind in self.node.product_indices:
					if other_prod_ind != prod_ind:
						# Calculate number of earmarked units.
						earmarked_units = self.node.state_vars_current.pending_finished_goods[other_prod_ind] \
											* self.node.NBOM(product=other_prod_ind, predecessor=None, raw_material=rm_index)
						# Subtract earmarked units from pipeline.
						pipeline[rm_index] = max(0, pipeline[rm_index] - earmarked_units)

			# Convert to downstream units.
			pipeline[rm_index] /= self.node.NBOM(product=prod_ind, predecessor=None, raw_material=rm_index)

		# Determine number of units of FG that can be made from pipeline inventory.
		units_from_pipeline = min(pipeline.values())

		return self.inventory_level[prod_ind] + units_from_pipeline
	
	@property
	def echelon_on_hand_inventory(self):
		"""Current echelon on-hand inventory at node. Equals on-hand inventory at node
		and at or in transit to all of its downstream nodes. If node is single-product,
		returns the echelon on-hand inventory as a singleton. If node is multi-product, returns dict
		whose keys are product indices and whose values are the corresponding echelon on-hand inventory levels. Read only.
		"""
		EOHI = self.on_hand

		if self.node.is_singleproduct:
			for d in self.node.descendants:
				# Add on-hand inventory at descendant.
				EOHI += d.state_vars[self.period].on_hand
				# Add in-transit quantity from predecessors that are descendents
				# of self (or equal to self).
				for p in d.predecessors():
					if p.index == self.node.index or p in self.node.descendants:
						EOHI += d.state_vars[self.period].in_transit_from(predecessor=p, raw_material=None)
		else:
			for d in self.node.descendants:
				# Add on-hand inventory at descendant.
				on_hand = d.state_vars[self.period].on_hand
				for prod_index in self.node.product_indices:
					EOHI[prod_index] += on_hand[prod_index]
					# Add in-transit quantity from predecessors that are descendants
					# of self (or equal to self).
					for p in d.predecessors():
						if p.index == self.node.index or p in self.node.descendants:
							EOHI[prod_index] += d.state_vars[self.period].in_transit_from(predecessor=p, raw_material=prod_index)

		return EOHI

	@property
	def echelon_inventory_level(self):
		"""Current echelon inventory level at node. Equals echelon on-hand inventory
		minus backorders at terminal node(s) downstream from node. If node is single-product,
		returns the echelon inventory level as a singleton. If node is multi-product, returns dict
		whose keys are product indices and whose values are the corresponding echelon inventory levels. Read only.
		"""
		EIL = self.echelon_on_hand_inventory

		if self.node.is_singleproduct:
			for d in self.node.descendants + [self.node]:
				if d in self.node.network.sink_nodes:
					EIL -= d.state_vars[self.period].backorders
		else:
			for d in self.node.descendants + [self.node]:
				backorders = d.state_vars[self.periods].backorders
				for prod_index in self.node.product_indices:
					if d in self.node.network.sink_nodes:
						EIL[prod_index] -= backorders[prod_index]

		return EIL

	def echelon_inventory_position(self, product=None, predecessor=None, raw_material=None):
		"""Current echelon inventory position at node for product with index ``product``. 
		Equals echelon inventory level plus on order items. 
		
		On-order includes raw material inventory that has not yet been processed, as well as
		inbound disrupted items due to type-RP disruptions.

		If the node is single-product, either set ``product`` to the single product, or to ``None``
		and the function will determine the product automatically. If the node is multi-product, ``product`` must be
		set to a single product at the node.

		If the node has a single predecessor, which provides a single raw material, either set ``predecessor`` 
		and ``raw_material`` to the appropriate indicies, or set them to ``None`` and the function will determine them
		automatically.
		If the node has multiple predecessors and/or raw materials, either set ``predecessor`` and ``raw_material``
		to the indices of a single predecessor and raw material (to get the raw-material-specific inventory position)
		or set both to ``None`` to use the aggregate on-order and raw material inventory for all predecessors and
		raw materials (counting such items using the "units" of the node itself; see documentation for :func:`on_order` for more details).
		``predecessor`` and ``raw_material`` must both either be ``None`` or not ``None``. 

		If the node has multiple products that use the same raw material, this function includes all units of that
		raw material, even though some of them may wind up being used to make products other than ``product``.

		Parameters
		----------
		product : |class_product| or int, optional
			The product (as |class_product| object or index), or ``None`` to set the product 
			automatically if node is single-product.
		predecessor : |class_node| or int, optional
			Predecessor (as |class_node| object or index) to consider in inventory position 
			calculation (including all others), or ``None`` to include all predecessors.
		raw_material : |class_product| or int, optional
			Raw material (as |class_product| or index) to consider in inventory position
			calculation (excluding all others), or ``None`` to include all raw materials.

		Returns
		-------
		float
			The echelon inventory position.

		Raises
		------
		ValueError
			If ``predecessor is None`` and ``raw_material is not None``, or vice-versa.
		"""
		# Validate parameters. 
		if not (predecessor is None and raw_material is None):
			_, pred_ind = self.node.validate_predecessor(predecessor, raw_material=raw_material)
			_, rm_ind = self.node.validate_raw_material(raw_material, predecessor=predecessor)
		_, prod_ind = self.node.validate_product(product)

		# Calculate echelon inventory level.
		if self.node.is_singleproduct:
			EIL = self.echelon_inventory_level
		else:
			EIL = self.echelon_inventory_level[prod_ind]
		# Calculate on-order, raw material inventory, and inbound disrupted items.
		if raw_material is not None:
			OO = self.on_order_by_predecessor[pred_ind][rm_ind]
			RMI = self.raw_material_inventory[rm_ind]
			IDI = self.inbound_disrupted_items[pred_ind][rm_ind]
		else:
			# Note: If <=1 predecessor, raw_material_inventory should always = 0
   			# (because raw materials are processed right away).
			OO = self.on_order(product=prod_ind)
			RMI = self.raw_material_aggregate(product=prod_ind)
			IDI = self.inbound_disrupted_items_aggregate(product=prod_ind)
		
		return EIL + OO + RMI + IDI
		
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

		.. warning:: This function has not yet been updated to handle multi-product nodes.

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
			rm_index = self.node._external_supplier_dummy_product.index
		else:
			pred_index = pred.index
			rm_index = next(iter(pred.product_indices))
#			rm_index = pred.product_indices[0]
		for t in range(self.node.equivalent_lead_time, self.node.shipment_lead_time):
			if self.node.network.period - t >= 0:
				in_transit_adjusted += self.node.state_vars[self.node.network.period - t].order_quantity[pred_index][rm_index]
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
		sv_dict['node'] = self.node.index
		sv_dict['period'] = self.period
		sv_dict['inbound_shipment_pipeline'] = copy.deepcopy(self.inbound_shipment_pipeline)
		sv_dict['inbound_shipment'] = copy.deepcopy(self.inbound_shipment)
		sv_dict['inbound_order_pipeline'] = copy.deepcopy(self.inbound_order_pipeline)
		sv_dict['inbound_order'] = copy.deepcopy(self.inbound_order)
		sv_dict['outbound_shipment'] = copy.deepcopy(self.outbound_shipment)
		sv_dict['on_order_by_predecessor'] = copy.deepcopy(self.on_order_by_predecessor)
		sv_dict['backorders_by_successor'] = copy.deepcopy(self.backorders_by_successor)
		sv_dict['outbound_disrupted_items'] = copy.deepcopy(self.outbound_disrupted_items)
		sv_dict['inbound_disrupted_items'] = copy.deepcopy(self.inbound_disrupted_items)
		sv_dict['order_quantity'] = copy.deepcopy(self.order_quantity)
		sv_dict['order_quantity_fg'] = copy.deepcopy(self.order_quantity_fg)
		sv_dict['raw_material_inventory'] = copy.deepcopy(self.raw_material_inventory)
		sv_dict['pending_finished_goods'] = copy.deepcopy(self.pending_finished_goods)
		sv_dict['inventory_level'] = self.inventory_level
		sv_dict['disrupted'] = self.disrupted
		sv_dict['holding_cost_incurred'] = self.holding_cost_incurred
		sv_dict['stockout_cost_incurred'] = self.stockout_cost_incurred
		sv_dict['in_transit_holding_cost_incurred'] = self.in_transit_holding_cost_incurred
		sv_dict['revenue_earned'] = self.revenue_earned
		sv_dict['total_cost_incurred'] = self.total_cost_incurred
		sv_dict['demand_cumul'] = self.demand_cumul
		sv_dict['demand_met_from_stock'] = self.demand_met_from_stock
		sv_dict['demand_met_from_stock_cumul'] = self.demand_met_from_stock_cumul
		sv_dict['fill_rate'] = self.fill_rate

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

			nsv.node = the_dict['node']
			nsv.period = the_dict['period']
			nsv.inbound_shipment_pipeline = copy.deepcopy(the_dict['inbound_shipment_pipeline'])
			nsv.inbound_shipment = copy.deepcopy(the_dict['inbound_shipment'])
			nsv.inbound_order_pipeline = copy.deepcopy(the_dict['inbound_order_pipeline'])
			nsv.inbound_order = copy.deepcopy(the_dict['inbound_order'])
			nsv.outbound_shipment = copy.deepcopy(the_dict['outbound_shipment'])
			nsv.on_order_by_predecessor = copy.deepcopy(the_dict['on_order_by_predecessor'])
			nsv.backorders_by_successor = copy.deepcopy(the_dict['backorders_by_successor'])
			nsv.outbound_disrupted_items = copy.deepcopy(the_dict['outbound_disrupted_items'])
			nsv.inbound_disrupted_items = copy.deepcopy(the_dict['inbound_disrupted_items'])
			nsv.order_quantity = copy.deepcopy(the_dict['order_quantity'])
			nsv.order_quantity_fg = copy.deepcopy(the_dict['order_quantity_fg'])
			nsv.raw_material_inventory = copy.deepcopy(the_dict['raw_material_inventory'])
			nsv.pending_finished_goods = copy.deepcopy(the_dict['pending_finished_goods'])
			nsv.inventory_level = the_dict['inventory_level']
			nsv.disrupted = the_dict['disrupted']
			nsv.holding_cost_incurred = the_dict['holding_cost_incurred']
			nsv.stockout_cost_incurred = the_dict['stockout_cost_incurred']
			nsv.in_transit_holding_cost_incurred = the_dict['in_transit_holding_cost_incurred']
			nsv.revenue_earned = the_dict['revenue_earned']
			nsv.total_cost_incurred = the_dict['total_cost_incurred']
			nsv.demand_cumul = the_dict['demand_cumul']
			nsv.demand_met_from_stock = the_dict['demand_met_from_stock']
			nsv.demand_met_from_stock_cumul = the_dict['demand_met_from_stock_cumul']
			nsv.fill_rate = the_dict['fill_rate']

		return nsv

	# --- Utility Functions --- #

	def reindex_state_variables(self, old_to_new_dict, old_to_new_prod_dict):
		"""Change indices of node-based state variable dict keys using ``old_to_new_dict``
		and indices of product-based state variable dict keys using ``old_to_new_prod_dict``.

		Parameters
		----------
		old_to_new_dict : dict
			Dict in which keys are old node indices and values are new node indices.
		old_to_new_prod_dict : dict
			Dict in which keys are old product indices and values are new product indices.

		"""
		# State variables indexed by product only.
		for prod in self.node.products:
			change_dict_key(self.demand_cumul, prod.index, old_to_new_prod_dict[prod.index])
			change_dict_key(self.inventory_level, prod.index, old_to_new_prod_dict[prod.index])
			change_dict_key(self.demand_met_from_stock, prod.index, old_to_new_prod_dict[prod.index])
			change_dict_key(self.demand_met_from_stock_cumul, prod.index, old_to_new_prod_dict[prod.index])
			change_dict_key(self.fill_rate, prod.index, old_to_new_prod_dict[prod.index])
			old_rm_indices = list(self.raw_material_inventory.keys())
			for rm_index in old_rm_indices:
				change_dict_key(self.raw_material_inventory, rm_index, old_to_new_prod_dict[rm_index])
			change_dict_key(self.order_quantity_fg, prod.index, old_to_new_prod_dict[prod.index])
			change_dict_key(self.pending_finished_goods, prod.index, old_to_new_prod_dict[prod.index])

		# State variables indexed by predecessor.
		for p in self.node.predecessors(include_external=True):
			p_index = p.index if p is not None else None
			rm_indices = p.product_indices if p is not None else [self.node._external_supplier_dummy_product.index]
			# Change rm index (inner level of nested dict).
			for rm_index in rm_indices:
				change_dict_key(self.inbound_shipment_pipeline[p_index], rm_index, old_to_new_prod_dict[rm_index])
				change_dict_key(self.inbound_shipment[p_index], rm_index, old_to_new_prod_dict[rm_index])
				change_dict_key(self.on_order_by_predecessor[p_index], rm_index, old_to_new_prod_dict[rm_index])
				change_dict_key(self.order_quantity[p_index], rm_index, old_to_new_prod_dict[rm_index])
				change_dict_key(self.inbound_disrupted_items[p_index], rm_index, old_to_new_prod_dict[rm_index])
			# Change predecessor index (outer level of nested dict).
			if p is not None:
				# We don't need to change the node index for external supplier (only the rm index).
				change_dict_key(self.inbound_shipment_pipeline, p_index, old_to_new_dict[p_index])
				change_dict_key(self.inbound_shipment, p_index, old_to_new_dict[p_index])
				change_dict_key(self.on_order_by_predecessor, p_index, old_to_new_dict[p_index])
				change_dict_key(self.order_quantity, p_index, old_to_new_dict[p_index])
				change_dict_key(self.inbound_disrupted_items, p_index, old_to_new_dict[p_index])

		# State variables indexed by successor.
		for s in self.node.successors(include_external=False):
			# Change prod index (inner level of nested dict).
			for prod_index in self.node.product_indices:
				change_dict_key(self.inbound_order_pipeline[s.index], prod_index, old_to_new_prod_dict[prod_index])
				change_dict_key(self.inbound_order[s.index], prod_index, old_to_new_prod_dict[prod_index])
				change_dict_key(self.outbound_shipment[s.index], prod_index, old_to_new_prod_dict[prod_index])
				change_dict_key(self.backorders_by_successor[s.index], prod_index, old_to_new_prod_dict[prod_index])
				change_dict_key(self.outbound_disrupted_items[s.index], prod_index, old_to_new_prod_dict[prod_index])
			# Change successor index (outer level of nested dict).
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

		if (self.node is not None and other.node is None) or (
				self.node is None and other.node is not None): return False
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
		if self.order_quantity_fg != other.order_quantity_fg: return False
		if self.raw_material_inventory != other.raw_material_inventory: return False
		if self.pending_finished_goods != other.pending_finished_goods: return False
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

