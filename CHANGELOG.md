# Changelog

All significant changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Option to suppress dummy-product indices in simulation output.
- ``SupplyChainNetwork.nodes_by_index`` dict, which returns a ``SupplyChainNode`` object for a given index.
Use this in place of ``SupplyChainNetwork.get_node_from_index()``, which will be deprecated.

### Changed
- Various speedups.
- ``DemandSource.lead_time_demand_distribution()`` now returns an ``rv_discrete`` object with a single
	value (0) and a single probability (1) if the lead time is 0. (In that case, the lead time demand always = 0.)
- Updated dependency for ``setuptools`` package to require v70.0 or later, to avoid [security vulnerability](https://github.com/LarrySnyder/stockpyl/security/dependabot/11).

### Fixed
- Bug that caused ``mwor_system()`` to crash when ``demand_source`` is provided as argument 
[#146](https://github.com/LarrySnyder/stockpyl/issues/146).
- Bugs that caused improper handling of orders and shipments when multiple suppliers provide
the same raw material. [#171](https://github.com/LarrySnyder/stockpyl/issues/171)
- Bug that caused ``ssm_serial.optimize_base_stock_levels()`` to crash when all lead times are 0.
[[#173](https://github.com/LarrySnyder/stockpyl/issues/173)]

## [1.0.0] -- 2024-05-13

### Introducing: Products
- Stockpyl now supports *products* in simulations. Products are implemented using the ``supply_chain_product``
object. 
- Products are "handled" by nodes. Most attributes (``stockout_cost``, 
``inventory_policy``, etc.) may be specified either at the node level, the product 
level, or the (node, product) level.
- Products are related to each other via a bill of materials (BOM), which specifies
the number of units of an upstream product (*raw material*) that are required to make
one unit of a downstream product (*finished goods*). 
- Only the simulation features of Stockpyl can currently make use of products; MEIO and other features
still assume a single-product model.
- For more information about creating and managing products, and simulating multi-product systems in |sp|, see the [``supply_chain_product``](https://stockpyl.readthedocs.io/en/multiproduct/api/datatypes/supply_chain_product.html) module or 
the [tutorial page for multi-product simulation](tutorial_multiproduct_sim_page).

### Added
- Products.
- ``helpers.nearest_dict_value()`` function, to find key in a dictionary that's nearest to
a given number and return the corresponding value.
- ``loss_functions.standard_normal_loss_dict()`` function, to build a dictionary of loss-function values.
- Support for negative binomial demand distributions in ``DemandSource``.
- Functions to validate and parse nodes and products within a network or node. (Mostly used internally for simulation.)

### Changed
- Requires Python 3.8 or later.
- Default git branch has been [changed to ``main``](https://sfconservancy.org/news/2020/jun/23/gitbranchname/).
If you have a local clone, you can rename it using:

	```
	git branch -m master main
	git fetch origin
	git branch -u origin/main main
	git remote set-head origin -a
	```

- ``NodeStateVars.raw_material_inventory`` is now indexed by product, not by predecessor.
- ``NodeStateVars`` object is now in its own module, ``node_state_vars.py``, rather than in ``supply_chain_node.py``.
- ``NodeStateVars`` attributes should now be accessed using the appropriate methods, rather than using
the attribute directly. For example: use ``node.state_vars[42].get_outbound_shipment(successor, product)`` instead
of ``node.state_vars[42].outbound_shipment[successor][product]``. These methods allow you to omit product info if
it is inferrable. (This is especially useful for models that don't have products explicitly added.)
- More compact text representation of ``SupplyChainNetwork`` and ``SupplyChainNode`` objects via ``__repr__()``.

### Fixed
- ``supply_chain_network.network_from_edges()`` now only creates a ``DemandSource`` for sink nodes or if the
demand source parameters were provided specifically for that node in the input args.
- Bug in ``helpers.ensure_list_for_time_period()`` that caused it to handle numpy arrays improperly.
- Bug in ``demand_source.py`` that sometimes caused infinite recursion when some attributes were ``None``.
- Bug in ``sim_io.py`` that caused incorrect headers for a few state variables.
- Various other bug fixes.

### Known Issues
(See https://github.com/LarrySnyder/stockpyl/issues for all issues.)
- BOM relationships assume the products are infinitely divisible; e.g., if 5 units of product A are
required to make 1 unit of product B, and there are 4 units of product A available, then 0.8 units of
product B are produced. [#155](https://github.com/LarrySnyder/stockpyl/issues/155)
- Lead times are specific to downstream node and finished good product, not upstream node and raw material.
This makes it hard to have different lead times for ordering different raw materials from different upstream nodes. [#149](https://github.com/LarrySnyder/stockpyl/issues/149)
- Echelon base-stock policies are not working reliably yet, at least for systems with multiple products. [#153](https://github.com/LarrySnyder/stockpyl/issues/153)
- Disruptions can only occur at node level, not product level. [#158](https://github.com/LarrySnyder/stockpyl/issues/158)

## [0.0.15] -- 2024-02-10

### Added
- Tutorial, in Jupyter notebook form, to accompany Snyder, L. V., "[Stockpyl: A Python Package for Inventory Optimization and Simulation](https://pubsonline.informs.org/doi/10.1287/educ.2023.0256)," in: Bish, E. K. and H. Balasubramanian, INFORMS TutORials in Operations Research, 156–197, 2023
- Check to make sure that a node's ``inventory_policy`` attribute is set, and that the ``Policy`` object's ``node`` attribute is set to the node
- Set the ``Policy`` object's ``node`` attribute automatically when setting the node's ``inventory_policy`` to it 
- Ability to print simulation output table to text file (in addition to CSV option)
- ``order_capacity`` attribute for ``SupplyChainNode``, which is respected in simulation

### Changed
- Changes to ``optimize_base_stock_levels()`` in ``ssm_serial`` that result in large speedups in some cases (via @DominikKamp)
- Add vertical line between nodes in simulation output to make it easier to separate nodes visually
- Minor edits to documentation and README

### Fixed
- Incorrect handling of custom demand distributions in ``ss.s_s_discrete_exact()``
- Error in unit tests for ``meio_general.truncate_and_discretize()``

## [0.0.14] -- 2022-08-17

### Fixed
- Bug in feature that allows overriding order quantities in simulation

## [0.0.13] -- 2022-08-10

### Added
- Features to run simulation period-by-period instead of all at once (useful for 
using in a reinforcement learning (RL) context)
- ``newsvendor.newsvendor_poisson_explicit()`` function added, for explicit-form newsvendor problem with Poisson demands
- Various unit tests
- More robust attribute handling for various objects

### Changed
- Allow earlier version of numpy (v1.21 insead of v1.22), which in turn allows Python 3.7 instead of 3.8
- New format for storing and loading named instances, and better documentation
- ``newsvendor.newsvendor_explicit()`` parameter renamed to ``revenue`` from ``selling_revenue`` for consistency

### Fixed
- State variables are stored as int and float instead of int64 and float64 so they can be JSON serialized when saving
- Bug that created spurious entries in ``inbound_order_pipeline``
- Bug in which only order LT was respected in simulation if both order and shipment LTs are nonzero
- Bug in default value for ``consistency_checks`` in ``simulation()``

## [0.0.12] -- 2022-07-12

### Changed
- Looser dependencies (previous versions required newer than necessary versions of some packages)

## [0.0.11] -- 2022-07-11 -- YANKED

## [0.0.10] -- 2022-07-11 -- YANKED

## [0.0.9] -- 2022-06-28

### Added
- Methods to convert objects to and from dicts

### Changed
- Removed dependency on pandas

### Fixed
- Bug that prevented named instances from being loaded correctly using ``load_instance()``

## [0.0.8] -- 2022-06-27

### Changed
- Removed cost summary output and ``print_cost_summary`` option from ``sim_io.write_results()``

## [0.0.7] -- 2022-06-27

### Fixed
- Small issue in README file

## [0.0.6] -- 2022-06-27

### Added
- Various new unit tests

### Fixed
- Bug in ``supply_chain_network.echelon_to_local_base_stock_levels()``

## [0.0.5] -- 2022-06-25

### Added
- Named instances from Shang and Song (2003)
- More flexible options for node indexing in ``ssm_serial.optimize_base_stock_levels()`` and ``ssm_serial.newsvendor_heuristic()`` 
- More flexible options for choosing rows and columns in simulation output in ``write_results()``
- Better handling of disrupted items for type-RP disruptions
- Various new unit tests

### Changed
- Smarter initialization of inventory levels in simulation
- ``ssm_serial.optimize_base_stock_levels()`` recognizes if demand distribution is discrete and handles discretization accordingly
- Default disruption type changed to 'OP'

### Fixed
- Bug in order quantity with type-RP disruptions

## [0.0.4] -- 2022-06-14

### Added
- Various new unit tests
- Ability to pass ``kwargs`` to ``SupplyChainNetwork()``
- ``owmr_system()`` function to build OWMR networks

### Changed
- Improved flexibility of inputs in ``network_from_edges()``

### Fixed
- Bug in which ``inbound_order_pipeline`` was initialized incorrectly in simulation

## [0.0.3] -- 2022-06-11
### Added
- Various new unit tests.
- Improved documentation throughout.
- Feature to check for duplicate edges when adding edges to a network.
- Feature to check for directed cycles before running simulation.

### Fixed
- Various bugs in backorder calculations in simulation, especially with disruptions.

## [0.0.2] -- 2022-06-06
### Fixed
- Fix problems with setup that prevented installation via pip.

## [0.0.1] -- 2022-06-02
Initial release.