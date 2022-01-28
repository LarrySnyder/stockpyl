from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
	name='pyinv',
	version='0.1',
	description='Python package for inventory optimization',
	url='https://github.com/LarrySnyder/pyinv',
	author='Larry Snyder',
	author_email='larry.snyder@lehigh.edu',
	license='MIT',
	packages=['pyinv'],
	install_requires=[
		'networkx',
		'numpy',
		'scipy',
		'warnings',
		'tabulate',
		'math',
		'pandas',
		'time',
		'matplotlib',
		'types',
		'numbers',
		'itertools',
		'tqdm',
		'csv'
	],
	zip_safe=False
	# TODO: add long_descriptions, classifier, 
)