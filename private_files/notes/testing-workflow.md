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