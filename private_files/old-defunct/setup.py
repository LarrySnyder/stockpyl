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
	include_package_data=True,
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
	classifiers=[
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Natural Language :: English',
		'Programming Language :: Python :: 3',
		'Topic :: Education',
		'Topic :: Office/Business',
		'Topic :: Scientific/Engineering'
	],
	zip_safe=False,
	test_suite='nose.collector',
	test_require=['nose']
	# TODO: add long_descriptions, classifier, 
)