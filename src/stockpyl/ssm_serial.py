# ===============================================================================
# stockpyl - ssm_serial Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_ssm_serial| module contains code to solve serial systems under the stochastic service
model (SSM), either exactly, using the :func:`~stockpyl.ssm_serial.optimize_base_stock_levels` function
(which implements the algorithm by Chen and Zheng (1994), which in turn is
based on the algorithm by Clark and Scarf (1960)), or approximately, using the :func:`~stockpyl.ssm_serial.newsvendor_heuristic` 
function (which implements the newsvendor heuristic by Shang and Song (2003)).

.. note:: |node_stage|

.. note:: |fosct_notation|


.. seealso::

	For an overview of multi-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for multi-echelon inventory optimization<tutorial_meio_page>`.


References
----------
F. Chen and Y. S. Zheng. Lower bounds for multiechelon stochastic inventory systems. *Management Science*, 40(11):1426–1443, 1994.

A. J. Clark and H. Scarf. Optimal policies for a multiechelon inventory problem. *Management Science*, 6(4):475–490, 1960.

K. H. Shang and J.-S. Song. Newsvendor bounds and heuristic for optimal policies in serial supply chains. *Management Science*, 49(5):618-638, 2003.


API Reference
-------------

"""

import matplotlib.pyplot as plt
