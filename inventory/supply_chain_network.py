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

from inventory.supply_chain_node import *


# ===============================================================================
# SupplyChainNetwork Class
# ===============================================================================

class SupplyChainNetwork(object):
	"""The ``SupplyChainNetwork`` class contains one or more nodes, each
	represented by a SupplyChainNode object.

	Attributes
	----------
	nodes : dict
		A dict of all nodes in the network; key=index, value=node object.
		(Read only.)

	"""

	def __init__(self):
		"""SupplyChainNetwork constructor method.

		"""
		# Initialize attributes.
		self._nodes = {}

	@property
	def nodes(self):
		return self._nodes

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

	# Methods to add and remove nodes.

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

		# Check whether node is already in network.
		if successor_node not in self.nodes:
			self.nodes[successor_node.index] = successor_node
