Running Tests from VSCode
=========================

Easy, just use Testing sidebar tool

Running Tests from Command Line
===============================

(Run from ``stockpyl`` directory)

Run tests:
``python -m unittest``

Measuring Coverage
==================

(Uses ``coverage`` package)

Run tests with coverage:
``coverage run -m unittest``

View report:
``coverage report``

Or view HTML version, with links to missing lines of code:
``coverage html``, then open ``htmlcov/index.html``

*Note*: ``.coveragerc`` file tells ``coverage`` not to check coverage for code in ``tests`` folder

Updating Coverage Badge
=======================

(Run from ``stockpyl`` directory)

Generate coverage-badge and save to SVG file:
``coverage-badge -o coverage_badge.svg -f``

(After committing, README.md will be updated with current badge)