# Changelog

All significant changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Features to run simulation period-by-period instead of all at once (useful for 
using in a reinforcement learning (RL) context)
- ``newsvendor.newsvendor_poisson_explicit()`` function added, for explicit-form newsvendor problem with Poisson demands
- Various unit tests
- More robust attribute handling for various objects

### Changed
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