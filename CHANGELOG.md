# Changelog

All significant changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.4] -- 2022-06-14
### Added
- Various new unit tests.
- Ability to pass ``kwargs`` to ``SupplyChainNetwork()``
- ``owmr_system()`` function to build OWMR networks

### Changed
- Improved flexibility of inputs in ``network_from_edges()``
- Smart initialization of inventory levels in simulation

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