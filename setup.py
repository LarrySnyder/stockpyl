from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
	name='stockpyl',
	version='0.1.0a0',
	description='Python package for inventory optimization',
	long_description=open("README.md").read(),
	url='https://github.com/LarrySnyder/stockpyl',
	author='Larry Snyder',
	author_email='larry.snyder@lehigh.edu',
	license='GPLv3',
	packages=['stockpyl'],
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
	zip_safe=False,
	test_suite='nose.collector',
	test_require=['nose']
	# TODO: add long_descriptions, classifier, 
)