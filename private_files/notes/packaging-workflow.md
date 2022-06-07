Packaging the Code
==================

Conda environment:
``conda activate stockpyl-env``

Install locally (if not already done):
``python -m pip install -e .``

Bump version number: 
``bumpver update --patch`` [or ``--minor`` or ``--major``]
add ``--dry`` to do dry run

Build package:
``python -m build``

Check package:
``twine check dist/*``

Upload to TestPyPI:
``twine upload -r testpypi dist/*``

Upload to PyPI:
``twine upload --skip-existing dist/*``


Packaging the Docs
==================

Change to ``docs`` directory:
``cd docs``

Make docs:
``make html``

Test doctests:
``make doctest``

Commit and push to GitHub

Build on RTD:
Go to https://readthedocs.org/projects/stockpyl/
Click "Build Version"
