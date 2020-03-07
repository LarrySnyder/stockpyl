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

from inventory.datatypes import *
from inventory.policy import *


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
	predecessors : list
		List of immediate predecesssor nodes.
	successors : list
		List of immediate successor nodes.

	# Data/inputs.

	local_holding_cost : float
		Local holding cost, per unit per period. [h'] # TODO: allow echelon holding costs
	stockout_cost : float
		Stockout cost, per unit (per period, if backorders). [p]
	lead_time : int
		Shipment lead time. [L] # TODO: create "alias" shipment_lead_time
	demand_type : DemandType
		Demand type (normal, deterministic, etc.).
	demand_mean : float
		Mean of demand per period. Required if ``demand_type`` == ``NORMAL``,
		ignored otherwise. [mu]
	demand_standard_deviation : float
		Standard deviation of demand per period. Required if ``demand_type`` ==
		``NORMAL``, ignored otherwise. [sigma]
	demands : list
		List of demands, one per period (if ``demand_type`` == ``DETERMINISTIC``),
		or list of possible demand values (if ``demand_type`` ==
		``DISCRETE_EXPLICIT``). Required if ``demand_type`` == ``DETERMINISTIC``
		or ``DISCRETE_EXPLICIT``, ignored otherwise. [d]
	demand_probabilities : list
		List of probabilities of each demand value. Required if ``demand_type``
		== ``DISCRETE_EXPLICIT``, ignored otherwise.
	demand_lo : float
		Low value of demand range. Required if ``demand_type`` ==
		``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
	demand_hi : float
		High value of demand range. Required if ``demand_type`` ==
		``UNIFORM_DISCRETE`` or ``UNIFORM_CONTINUOUS``, ignored otherwise.
	inventory_policy : Policy
		Inventory policy to be used to make inventory decisions.
	"""

	def __init__(self, index=None, name=None, network=None):
		"""SupplyChainStage constructor method.

		Parameters
		----------
		index : int, optional
			Numeric index to identify node.
		name : str, optional
			String to identify node.
		network : SupplyChainNetwork
			The network that contains the node.
		"""
		# Initialize attributes.

		# Attributes related to parent network.
		self.network = network
		self._predecessors = []
		self._successors = []

		# Index and name.
		self.index = index
		self.name = name

		# Data/inputs.
		local_holding_cost = None
		stockout_cost = None
		lead_time = 0
		demand_type = DemandType.NONE
		demand_mean = None
		demand_standard_deviation = None
		demands = []
		demand_probabilities = []
		demand_lo = None
		demand_hi = None
		inventory_policy = None

	# Special members.

	def __repr__(self):
		"""
		Return a string representation of the ``SupplyChainNode`` instance.

		Returns
		-------
			A string representation of the ``SupplyChainNode`` instance.

		"""
		return "SupplyChainNode(index={:}, name={:})".format(self.index, self.name)

	def __str__(self):
		"""
		Return the full name of the ``SupplyChainNode`` instance.
		# TODO: write this.

		Returns
		-------
			The node name.

		"""
		return self.__repr__()

