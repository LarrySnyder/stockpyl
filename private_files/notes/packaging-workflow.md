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
``twine upload dist/*``


Packaging the Docs
==================
