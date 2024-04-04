import unittest
import csv
import os

import stockpyl.sim_io as sim_io
from stockpyl.sim import *
from stockpyl.instances import *
from stockpyl.disruption_process import DisruptionProcess


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_rq   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestWriteResults(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestWriteResults', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestWriteResults', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1.
		"""
		print_status('TestWriteResults', 'test_example_6_1()')

		# Build network.
		network = load_instance("example_6_1")

		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_example_6_1'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
		sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=cols_to_print, 
			write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

		row0_txt  = 't    | i=0    DISR      IO:EXT  IOPL:EXT        OQ:1      OO:1      IS:1  ISPL:1                  RM:1    OS:EXT     DMFS        FR          IL     BO:EXT    ODI:EXT        HC         SC    ITHC    REV         TC  | i=1    DISR        IO:0  IOPL:0        OQ:2      OO:2      IS:2  ISPL:2                  RM:2      OS:0     DMFS        FR          IL       BO:0    ODI:0        HC    SC      ITHC    REV        TC  | i=2    DISR        IO:1  IOPL:1      OQ:EXT    OO:EXT    IS:EXT  ISPL:EXT                                   RM:EXT      OS:1     DMFS        FR          IL          BO:1    ODI:1       HC    SC      ITHC    REV        TC'
		row1_txt  = '---  -------  ------  --------  ----------  --------  --------  --------  --------------------  ------  --------  -------  --------  ----------  ---------  ---------  --------  ---------  ------  -----  ---------  -------  ------  --------  --------  --------  --------  --------  --------------------  ------  --------  -------  --------  ----------  ---------  -------  --------  ----  --------  -----  --------  -------  ------  --------  --------  --------  --------  --------  ---------------------------------------  --------  --------  -------  --------  ----------  ------------  -------  -------  ----  --------  -----  --------'
		row6_txt  = '4    |        False    6.03719  []           6.03719   6.6525   26.0655   [5.066098888673643]        0  26.0655   5.87469  0.223985   -0.162502   0.162502          0   0          6.03207       0      0    6.03207  |        False    6.03719  []         6.03719   7.1164    5.0661   [5.623901111326357]        0   5.0661   4.45079  0.305055   -1.5864     1.5864          0  0            0   20.2644      0   20.2644  |        False    6.03719  []         6.03719  12.1825    5.6239   [6.145311289572089, 6.037190468227889]          0   5.6239   4.54469  0.398313   -1.4925     1.4925             0  0           0  11.2478       0  11.2478'
		row11_txt = '98   |        False    4.7752   []           4.7752    4.7752    5.85597  [4.775201280806585]        0   4.7752   4.7752   0.927447    1.7148     0                 0  12.0036     0             0      0   12.0036   |        False    4.7752   []         4.7752    4.7752    5.38237  [4.775201280806586]        0   4.7752   4.7752   0.874603    0.754799   0               0  3.01919      0   19.1008      0   22.12    |        False    4.7752   []         4.7752    9.1568    5.56004  [4.381602699335919, 4.775201280806584]          0   4.7752   4.7752   0.888642    1.5332     0                  0  3.06639     0   9.5504       0  12.6168'

		row0 = 't,i=0,DISR,IO:EXT,IOPL:EXT,OQ:1,OO:1,IS:1,ISPL:1,RM:1,OS:EXT,DMFS,FR,IL,BO:EXT,ODI:EXT,HC,SC,ITHC,REV,TC,i=1,DISR,IO:0,IOPL:0,OQ:2,OO:2,IS:2,ISPL:2,RM:2,OS:0,DMFS,FR,IL,BO:0,ODI:0,HC,SC,ITHC,REV,TC,i=2,DISR,IO:1,IOPL:1,OQ:EXT,OO:EXT,IS:EXT,ISPL:EXT,RM:EXT,OS:1,DMFS,FR,IL,BO:1,ODI:1,HC,SC,ITHC,REV,TC'
		row5 = '4,,False,6.037190468227883,[],6.037190468227885,6.652501757799978,26.06553892254117,[5.066098888673643],0.0,26.06553892254117,5.8746887104279075,0.22398503883788762,-0.16250175779997544,0.16250175779997544,0,0.0,6.032065249535088,0.0,0.0,6.032065249535088,,False,6.037190468227885,[],6.037190468227887,7.116402869126333,5.066098888673643,[5.623901111326357],0.0,5.066098888673643,4.450787599101552,0.3050545629127044,-1.5864028691263323,1.5864028691263323,0.0,0.0,0.0,20.264395554694573,0.0,20.264395554694573,,False,6.037190468227887,[],6.037190468227889,12.18250175779998,5.623901111326357,[6.145311289572089, 6.037190468227889],0.0,5.623901111326357,4.544688710427908,0.39831291850351647,-1.4925017577999782,1.492501757799979,0.0,0.0,0.0,11.247802222652714,0.0,11.247802222652714'
		row10 = '98,,False,4.775201280806586,[],4.775201280806585,4.775201280806586,5.855972018122079,[4.775201280806585],0.0,4.775201280806586,4.775201280806586,0.9274469545198983,1.7147987191934133,0.0,0,12.003591034353892,0.0,0.0,0.0,12.003591034353892,,False,4.775201280806585,[],4.775201280806586,4.77520128080658,5.3823688379681025,[4.775201280806586],0.0,4.775201280806585,4.775201280806585,0.8746030168684653,0.7547987191934205,0.0,0.0,3.019194876773682,0,19.10080512322634,0.0,22.120000000000022,,False,4.775201280806586,[],4.775201280806584,9.156803980142493,5.560039692192106,[4.381602699335919, 4.775201280806584],0.0,4.775201280806586,4.775201280806586,0.888642036779627,1.5331960198575052,0.0,0.0,3.0663920397150104,0,9.550402561613172,0.0,12.616794601328182'
		
		# Load TXT results and check them.
		with open(txt_filename) as txtfile:
			lines = txtfile.read().splitlines()

			self.assertEqual(lines[0], row0_txt)
			self.assertEqual(lines[1], row1_txt)
			self.assertEqual(lines[6], row6_txt)
			self.assertEqual(lines[11], row11_txt)

			os.remove(txt_filename)

		# Load CSV results and check them.
		with open(csv_filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[5]), row5)
			self.assertEqual(','.join(rows[10]), row10)

			# Delete file.
			os.remove(csv_filename)

	def test_periods_to_print(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when periods_to_print is specified as a list.
		"""
		print_status('TestWriteResults', 'test_periods_to_print()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_periods_to_print'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
		sim_io.write_results(network=network, num_periods=100, periods_to_print=[2, 7, 43], columns_to_print=cols_to_print, 
			write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

		row0_txt = '  t  | i=0    DISR      IO:EXT  IOPL:EXT       OQ:1      OO:1     IS:1  ISPL:1                  RM:1    OS:EXT     DMFS        FR         IL    BO:EXT    ODI:EXT       HC      SC    ITHC    REV         TC  | i=1    DISR       IO:0  IOPL:0       OQ:2      OO:2     IS:2  ISPL:2                 RM:2     OS:0     DMFS        FR          IL       BO:0    ODI:0    HC    SC     ITHC    REV       TC  | i=2    DISR       IO:1  IOPL:1      OQ:EXT    OO:EXT    IS:EXT  ISPL:EXT                                  RM:EXT      OS:1     DMFS        FR       IL         BO:1    ODI:1       HC    SC     ITHC    REV       TC'
		row1_txt = '---  -------  ------  --------  ----------  -------  --------  -------  --------------------  ------  --------  -------  --------  ---------  --------  ---------  -------  ------  ------  -----  ---------  -------  ------  -------  --------  -------  --------  -------  -------------------  ------  -------  -------  --------  ----------  ---------  -------  ----  ----  -------  -----  -------  -------  ------  -------  --------  --------  --------  --------  --------------------------------------  --------  --------  -------  --------  -------  -----------  -------  -------  ----  -------  -----  -------'
		row2_txt = '  2  |        False    5.6239   []          5.6239   20.5355   0        [0.0]                      0   0        0        0         -14.0455    14.0455          0  0        521.37       0      0  521.37     |        False   5.6239   []        5.6239   26.0655   0        [26.06553892254117]       0  0        0        0         -20.5355    20.5355          0     0     0   0           0   0       |        False   5.6239   []         5.6239    8.76927  27.9863   [3.145371921193491, 5.623901111326357]         0  26.0655   5.6239   0.21576   1.92073  8.88178e-16        0  3.84145     0  52.1311      0  55.9725'
		row3_txt = '  7  |        False    4.6379   []          4.6379    6.23003  6.14531  [6.037190468227889]        0   5.88534  4.6379   0.44692     0.25997    0               0  1.81979    0          0      0    1.81979  |        False   4.6379   []        4.6379    5.72284  6.03719  [5.722839301253794]       0  6.03719  4.44506  0.442889   -0.192839   0.192839        0     0     0  24.1488      0  24.1488  |        False   4.6379   []         4.6379    9.5262    6.88664  [4.888301709871235, 4.63789866160095]          0   5.72284  4.6379   0.518264  1.1638   0                  0  2.3276      0  11.4457      0  13.7733'
		row4_txt = ' 43  |        False    4.30582  []          4.30582   5.40229  6.84541  [3.8445867051753195]       0   5.75771  4.30582  0.869486    1.08771    0               0  7.61395    0          0      0    7.61395  |        False   4.30582  []        4.30582   7.08771  3.84459  [7.087705709707265]       0  3.84459  2.74812  0.819185   -1.55771    1.55771         0     0     0  15.3783      0  15.3783  |        False   4.30582  []         4.30582   9.43255   8.34516  [5.126727211245548, 4.305821103558779]         0   7.08771  4.30582  0.834206  1.25745  0                  0  2.5149      0  14.1754      0  16.6903'

		row0 = 't,i=0,DISR,IO:EXT,IOPL:EXT,OQ:1,OO:1,IS:1,ISPL:1,RM:1,OS:EXT,DMFS,FR,IL,BO:EXT,ODI:EXT,HC,SC,ITHC,REV,TC,i=1,DISR,IO:0,IOPL:0,OQ:2,OO:2,IS:2,ISPL:2,RM:2,OS:0,DMFS,FR,IL,BO:0,ODI:0,HC,SC,ITHC,REV,TC,i=2,DISR,IO:1,IOPL:1,OQ:EXT,OO:EXT,IS:EXT,ISPL:EXT,RM:EXT,OS:1,DMFS,FR,IL,BO:1,ODI:1,HC,SC,ITHC,REV,TC'
		row1 = '2,,False,5.623901111326356,[],5.623901111326356,20.53553892254117,0.0,[0.0],0.0,0.0,0.0,0.0,-14.04553892254117,14.04553892254117,0,0.0,521.3704048047282,0.0,0.0,521.3704048047282,,False,5.623901111326356,[],5.623901111326355,26.06553892254117,0.0,[26.06553892254117],0.0,0.0,0.0,0.0,-20.53553892254117,20.53553892254117,0.0,0.0,0.0,0.0,0.0,0.0,,False,5.623901111326355,[],5.623901111326357,8.769273032519848,27.986265890021322,[3.145371921193491, 5.623901111326357],0.0,26.06553892254117,5.623901111326354,0.21576001662727454,1.9207269674801521,8.881784197001252e-16,0.0,3.8414539349603043,0,52.13107784508234,0.0,55.972531780042644'
		row2 = '7,,False,4.637898661600952,[],4.637898661600951,6.230029769481679,6.145311289572089,[6.037190468227889],0.0,5.8853410590537685,4.637898661600952,0.44691957163047596,0.2599702305183209,0.0,0,1.8197916136282464,0.0,0.0,0.0,1.8197916136282464,,False,4.637898661600951,[],4.637898661600952,5.722839301253787,6.037190468227889,[5.722839301253794],0.0,6.037190468227889,4.445059360347163,0.4428887862743481,-0.19283930125378745,0.19283930125378745,0.0,0.0,0.0,24.148761872911557,0.0,24.148761872911557,,False,4.637898661600952,[],4.63789866160095,9.526200371472186,6.886638929781603,[4.888301709871235, 4.63789866160095],0.0,5.722839301253794,4.637898661600952,0.5182638476284692,1.1637996285278103,0.0,0.0,2.3275992570556205,0,11.445678602507588,0.0,13.773277859563208'
		row3 = '43,,False,4.305821103558777,[],4.3058211035587775,5.402292414882573,6.845413294824685,[3.8445867051753195],0.0,5.757705709707258,4.305821103558777,0.8694855956154881,1.0877075851174274,0.0,0,7.613953095821992,0.0,0.0,0.0,7.613953095821992,,False,4.3058211035587775,[],4.3058211035587775,7.087705709707255,3.8445867051753195,[7.087705709707265],0.0,3.8445867051753195,2.7481153938515215,0.8191846453959901,-1.557705709707256,1.557705709707256,0.0,0.0,0.0,15.378346820701278,0.0,15.378346820701278,,False,4.3058211035587775,[],4.305821103558779,9.43254831480432,8.345157394902943,[5.126727211245548, 4.305821103558779],0.0,7.087705709707265,4.3058211035587775,0.834206268959877,1.2574516851956776,0.0,0.0,2.5149033703913553,0,14.17541141941453,0.0,16.690314789805885'		
		
		# Load TXT results and check them.
		with open(txt_filename) as txtfile:
			lines = txtfile.read().splitlines()

			self.assertEqual(lines[0], row0_txt)
			self.assertEqual(lines[1], row1_txt)
			self.assertEqual(lines[2], row2_txt)
			self.assertEqual(lines[3], row3_txt)
			self.assertEqual(lines[4], row4_txt)

			os.remove(txt_filename)

		# Load CSV results and check them.
		with open(csv_filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[1]), row1)
			self.assertEqual(','.join(rows[2]), row2)
			self.assertEqual(','.join(rows[3]), row3)

			# Delete file.
			os.remove(csv_filename)

	def test_columns_to_print_none(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is None.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_none()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_none'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=None, 
			write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

		row0_txt  = 't    | i=0    DISR      IO:EXT  IOPL:EXT        OQ:1      OO:1      IS:1  ISPL:1                  IDI:1    RM:1    OS:EXT     DMFS        FR          IL     BO:EXT    ODI:EXT        HC         SC    ITHC    REV         TC  | i=1    DISR        IO:0  IOPL:0        OQ:2      OO:2      IS:2  ISPL:2                  IDI:2    RM:2      OS:0     DMFS        FR          IL       BO:0    ODI:0        HC    SC      ITHC    REV        TC  | i=2    DISR        IO:1  IOPL:1      OQ:EXT    OO:EXT    IS:EXT  ISPL:EXT                                   IDI:EXT    RM:EXT      OS:1     DMFS        FR          IL          BO:1    ODI:1       HC    SC      ITHC    REV        TC'
		row1_txt  = '---  -------  ------  --------  ----------  --------  --------  --------  --------------------  -------  ------  --------  -------  --------  ----------  ---------  ---------  --------  ---------  ------  -----  ---------  -------  ------  --------  --------  --------  --------  --------  --------------------  -------  ------  --------  -------  --------  ----------  ---------  -------  --------  ----  --------  -----  --------  -------  ------  --------  --------  --------  --------  --------  ---------------------------------------  ---------  --------  --------  -------  --------  ----------  ------------  -------  -------  ----  --------  -----  --------'
		row6_txt  = '4    |        False    6.03719  []           6.03719   6.6525   26.0655   [5.066098888673643]         0       0  26.0655   5.87469  0.223985   -0.162502   0.162502          0   0          6.03207       0      0    6.03207  |        False    6.03719  []         6.03719   7.1164    5.0661   [5.623901111326357]         0       0   5.0661   4.45079  0.305055   -1.5864     1.5864          0  0            0   20.2644      0   20.2644  |        False    6.03719  []         6.03719  12.1825    5.6239   [6.145311289572089, 6.037190468227889]           0         0   5.6239   4.54469  0.398313   -1.4925     1.4925             0  0           0  11.2478       0  11.2478'
		row11_txt = '98   |        False    4.7752   []           4.7752    4.7752    5.85597  [4.775201280806585]         0       0   4.7752   4.7752   0.927447    1.7148     0                 0  12.0036     0             0      0   12.0036   |        False    4.7752   []         4.7752    4.7752    5.38237  [4.775201280806586]         0       0   4.7752   4.7752   0.874603    0.754799   0               0  3.01919      0   19.1008      0   22.12    |        False    4.7752   []         4.7752    9.1568    5.56004  [4.381602699335919, 4.775201280806584]           0         0   4.7752   4.7752   0.888642    1.5332     0                  0  3.06639     0   9.5504       0  12.6168'

		row0 = 't,i=0,DISR,IO:EXT,IOPL:EXT,OQ:1,OO:1,IS:1,ISPL:1,IDI:1,RM:1,OS:EXT,DMFS,FR,IL,BO:EXT,ODI:EXT,HC,SC,ITHC,REV,TC,i=1,DISR,IO:0,IOPL:0,OQ:2,OO:2,IS:2,ISPL:2,IDI:2,RM:2,OS:0,DMFS,FR,IL,BO:0,ODI:0,HC,SC,ITHC,REV,TC,i=2,DISR,IO:1,IOPL:1,OQ:EXT,OO:EXT,IS:EXT,ISPL:EXT,IDI:EXT,RM:EXT,OS:1,DMFS,FR,IL,BO:1,ODI:1,HC,SC,ITHC,REV,TC'
		row5 = '4,,False,6.037190468227883,[],6.037190468227885,6.652501757799978,26.06553892254117,[5.066098888673643],0,0.0,26.06553892254117,5.8746887104279075,0.22398503883788762,-0.16250175779997544,0.16250175779997544,0,0.0,6.032065249535088,0.0,0.0,6.032065249535088,,False,6.037190468227885,[],6.037190468227887,7.116402869126333,5.066098888673643,[5.623901111326357],0,0.0,5.066098888673643,4.450787599101552,0.3050545629127044,-1.5864028691263323,1.5864028691263323,0.0,0.0,0.0,20.264395554694573,0.0,20.264395554694573,,False,6.037190468227887,[],6.037190468227889,12.18250175779998,5.623901111326357,[6.145311289572089, 6.037190468227889],0,0.0,5.623901111326357,4.544688710427908,0.39831291850351647,-1.4925017577999782,1.492501757799979,0.0,0.0,0.0,11.247802222652714,0.0,11.247802222652714'
		row10 = '98,,False,4.775201280806586,[],4.775201280806585,4.775201280806586,5.855972018122079,[4.775201280806585],0,0.0,4.775201280806586,4.775201280806586,0.9274469545198983,1.7147987191934133,0.0,0,12.003591034353892,0.0,0.0,0.0,12.003591034353892,,False,4.775201280806585,[],4.775201280806586,4.77520128080658,5.3823688379681025,[4.775201280806586],0,0.0,4.775201280806585,4.775201280806585,0.8746030168684653,0.7547987191934205,0.0,0.0,3.019194876773682,0,19.10080512322634,0.0,22.120000000000022,,False,4.775201280806586,[],4.775201280806584,9.156803980142493,5.560039692192106,[4.381602699335919, 4.775201280806584],0,0.0,4.775201280806586,4.775201280806586,0.888642036779627,1.5331960198575052,0.0,0.0,3.0663920397150104,0,9.550402561613172,0.0,12.616794601328182'
		
		# Load TXT results and check them.
		with open(txt_filename) as txtfile:
			lines = txtfile.read().splitlines()

			self.assertEqual(lines[0], row0_txt)
			self.assertEqual(lines[1], row1_txt)
			self.assertEqual(lines[6], row6_txt)
			self.assertEqual(lines[11], row11_txt)

			os.remove(txt_filename)

		# Load CSV results and check them.
		with open(csv_filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[5]), row5)
			self.assertEqual(','.join(rows[10]), row10)

			# Delete file.
			os.remove(csv_filename)

	def test_columns_to_print_list(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a list.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_list()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_list'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=['IO', 'OQ', 'IL', 'TC'], 
			write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

		row0_txt  = 't    | i=0      IO:EXT      OQ:1          IL         TC  | i=1        IO:0      OQ:2          IL        TC  | i=2        IO:1    OQ:EXT          IL        TC'
		row1_txt  = '---  -------  --------  --------  ----------  ---------  -------  --------  --------  ----------  --------  -------  --------  --------  ----------  --------'
		row6_txt  = '4    |         6.03719   6.03719   -0.162502    6.03207  |         6.03719   6.03719   -1.5864     20.2644  |         6.03719   6.03719   -1.4925    11.2478'
		row11_txt = '98   |         4.7752    4.7752     1.7148     12.0036   |         4.7752    4.7752     0.754799   22.12    |         4.7752    4.7752     1.5332    12.6168'

		row0 = 't,i=0,IO:EXT,OQ:1,IL,TC,i=1,IO:0,OQ:2,IL,TC,i=2,IO:1,OQ:EXT,IL,TC'
		row5 = '4,,6.037190468227883,6.037190468227885,-0.16250175779997544,6.032065249535088,,6.037190468227885,6.037190468227887,-1.5864028691263323,20.264395554694573,,6.037190468227887,6.037190468227889,-1.4925017577999782,11.247802222652714'
		row10 = '98,,4.775201280806586,4.775201280806585,1.7147987191934133,12.003591034353892,,4.775201280806585,4.775201280806586,0.7547987191934205,22.120000000000022,,4.775201280806586,4.775201280806584,1.5331960198575052,12.616794601328182'
		
		# Load TXT results and check them.
		with open(txt_filename) as txtfile:
			lines = txtfile.read().splitlines()

			self.assertEqual(lines[0], row0_txt)
			self.assertEqual(lines[1], row1_txt)
			self.assertEqual(lines[6], row6_txt)
			self.assertEqual(lines[11], row11_txt)

			os.remove(txt_filename)

		# Load CSV results and check them.
		with open(csv_filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[5]), row5)
			self.assertEqual(','.join(rows[10]), row10)

			# Delete file.
			os.remove(csv_filename)

	def test_columns_to_print_string(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a string.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_string()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_string'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print='basic', 
			write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

		row0_txt  = 't    | i=0      IO:EXT      OQ:1      IS:1    OS:EXT          IL  | i=1        IO:0      OQ:2      IS:2      OS:0          IL  | i=2        IO:1    OQ:EXT    IS:EXT      OS:1          IL'
		row1_txt  = '---  -------  --------  --------  --------  --------  ----------  -------  --------  --------  --------  --------  ----------  -------  --------  --------  --------  --------  ----------'
		row6_txt  = '4    |         6.03719   6.03719  26.0655   26.0655    -0.162502  |         6.03719   6.03719   5.0661    5.0661    -1.5864    |         6.03719   6.03719   5.6239    5.6239    -1.4925'
		row11_txt = '98   |         4.7752    4.7752    5.85597   4.7752     1.7148    |         4.7752    4.7752    5.38237   4.7752     0.754799  |         4.7752    4.7752    5.56004   4.7752     1.5332'

		row0 = 't,i=0,IO:EXT,OQ:1,IS:1,OS:EXT,IL,i=1,IO:0,OQ:2,IS:2,OS:0,IL,i=2,IO:1,OQ:EXT,IS:EXT,OS:1,IL'
		row5 = '4,,6.037190468227883,6.037190468227885,26.06553892254117,26.06553892254117,-0.16250175779997544,,6.037190468227885,6.037190468227887,5.066098888673643,5.066098888673643,-1.5864028691263323,,6.037190468227887,6.037190468227889,5.623901111326357,5.623901111326357,-1.4925017577999782'
		row10 = '98,,4.775201280806586,4.775201280806585,5.855972018122079,4.775201280806586,1.7147987191934133,,4.775201280806585,4.775201280806586,5.3823688379681025,4.775201280806585,0.7547987191934205,,4.775201280806586,4.775201280806584,5.560039692192106,4.775201280806586,1.5331960198575052'
		
		# Load TXT results and check them.
		with open(txt_filename) as txtfile:
			lines = txtfile.read().splitlines()

			self.assertEqual(lines[0], row0_txt)
			self.assertEqual(lines[1], row1_txt)
			self.assertEqual(lines[6], row6_txt)
			self.assertEqual(lines[11], row11_txt)

#			os.remove(txt_filename)

		# Load CSV results and check them.
		with open(csv_filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[5]), row5)
			self.assertEqual(','.join(rows[10]), row10)

			# Delete file.
			os.remove(csv_filename)

	def test_columns_to_print_list_of_strings(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a list of strings.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_list_of_strings()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_list_of_strings'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=['basic', 'costs'], 
			write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

		row0_txt  = 't    | i=0      IO:EXT      OQ:1      IS:1    OS:EXT          IL        HC         SC         TC  | i=1        IO:0      OQ:2      IS:2      OS:0          IL        HC    SC        TC  | i=2        IO:1    OQ:EXT    IS:EXT      OS:1          IL       HC    SC        TC'
		row1_txt  = '---  -------  --------  --------  --------  --------  ----------  --------  ---------  ---------  -------  --------  --------  --------  --------  ----------  --------  ----  --------  -------  --------  --------  --------  --------  ----------  -------  ----  --------'
		row6_txt  = '4    |         6.03719   6.03719  26.0655   26.0655    -0.162502   0          6.03207    6.03207  |         6.03719   6.03719   5.0661    5.0661    -1.5864    0            0   20.2644  |         6.03719   6.03719   5.6239    5.6239    -1.4925    0           0  11.2478'
		row11_txt = '98   |         4.7752    4.7752    5.85597   4.7752     1.7148    12.0036     0         12.0036   |         4.7752    4.7752    5.38237   4.7752     0.754799  3.01919      0   22.12    |         4.7752    4.7752    5.56004   4.7752     1.5332    3.06639     0  12.6168'

		row0 = 't,i=0,IO:EXT,OQ:1,IS:1,OS:EXT,IL,HC,SC,TC,i=1,IO:0,OQ:2,IS:2,OS:0,IL,HC,SC,TC,i=2,IO:1,OQ:EXT,IS:EXT,OS:1,IL,HC,SC,TC'
		row5 = '4,,6.037190468227883,6.037190468227885,26.06553892254117,26.06553892254117,-0.16250175779997544,0.0,6.032065249535088,6.032065249535088,,6.037190468227885,6.037190468227887,5.066098888673643,5.066098888673643,-1.5864028691263323,0.0,0.0,20.264395554694573,,6.037190468227887,6.037190468227889,5.623901111326357,5.623901111326357,-1.4925017577999782,0.0,0.0,11.247802222652714'
		row10 = '98,,4.775201280806586,4.775201280806585,5.855972018122079,4.775201280806586,1.7147987191934133,12.003591034353892,0.0,12.003591034353892,,4.775201280806585,4.775201280806586,5.3823688379681025,4.775201280806585,0.7547987191934205,3.019194876773682,0,22.120000000000022,,4.775201280806586,4.775201280806584,5.560039692192106,4.775201280806586,1.5331960198575052,3.0663920397150104,0,12.616794601328182'
		
		# Load TXT results and check them.
		with open(txt_filename) as txtfile:
			lines = txtfile.read().splitlines()

			self.assertEqual(lines[0], row0_txt)
			self.assertEqual(lines[1], row1_txt)
			self.assertEqual(lines[6], row6_txt)
			self.assertEqual(lines[11], row11_txt)

			os.remove(txt_filename)

		# Load CSV results and check them.
		with open(csv_filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[5]), row5)
			self.assertEqual(','.join(rows[10]), row10)

			# Delete file.
			os.remove(csv_filename)

	def test_columns_to_print_mixed(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a list that contains
		some column names and some built-in strings.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_mixed()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_mixed'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=['SC', 'basic', 'IDI'], 
			write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

		row0_txt  = 't    | i=0      IO:EXT      OQ:1      IS:1    IDI:1    OS:EXT          IL         SC  | i=1        IO:0      OQ:2      IS:2    IDI:2      OS:0          IL    SC  | i=2        IO:1    OQ:EXT    IS:EXT    IDI:EXT      OS:1          IL    SC'
		row1_txt  = '---  -------  --------  --------  --------  -------  --------  ----------  ---------  -------  --------  --------  --------  -------  --------  ----------  ----  -------  --------  --------  --------  ---------  --------  ----------  ----'
		row6_txt  = '4    |         6.03719   6.03719  26.0655         0  26.0655    -0.162502    6.03207  |         6.03719   6.03719   5.0661         0   5.0661    -1.5864       0  |         6.03719   6.03719   5.6239           0   5.6239    -1.4925       0'
		row11_txt = '98   |         4.7752    4.7752    5.85597        0   4.7752     1.7148      0        |         4.7752    4.7752    5.38237        0   4.7752     0.754799     0  |         4.7752    4.7752    5.56004          0   4.7752     1.5332       0'

		row0 = 't,i=0,IO:EXT,OQ:1,IS:1,IDI:1,OS:EXT,IL,SC,i=1,IO:0,OQ:2,IS:2,IDI:2,OS:0,IL,SC,i=2,IO:1,OQ:EXT,IS:EXT,IDI:EXT,OS:1,IL,SC'
		row5 = '4,,6.037190468227883,6.037190468227885,26.06553892254117,0,26.06553892254117,-0.16250175779997544,6.032065249535088,,6.037190468227885,6.037190468227887,5.066098888673643,0,5.066098888673643,-1.5864028691263323,0.0,,6.037190468227887,6.037190468227889,5.623901111326357,0,5.623901111326357,-1.4925017577999782,0.0'
		row10 = '98,,4.775201280806586,4.775201280806585,5.855972018122079,0,4.775201280806586,1.7147987191934133,0.0,,4.775201280806585,4.775201280806586,5.3823688379681025,0,4.775201280806585,0.7547987191934205,0,,4.775201280806586,4.775201280806584,5.560039692192106,0,4.775201280806586,1.5331960198575052,0'
		
		# Load TXT results and check them.
		with open(txt_filename) as txtfile:
			lines = txtfile.read().splitlines()

			self.assertEqual(lines[0], row0_txt)
			self.assertEqual(lines[1], row1_txt)
			self.assertEqual(lines[6], row6_txt)
			self.assertEqual(lines[11], row11_txt)

			os.remove(txt_filename)

		# Load CSV results and check them.
		with open(csv_filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[5]), row5)
			self.assertEqual(','.join(rows[10]), row10)

			# Delete file.
			os.remove(csv_filename)


class TestWriteInstanceAndStates(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestWriteInstanceAndStates', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestWriteInstanceAndStates', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Example 6.1.
		"""
		print_status('TestWriteInstanceAndStates', 'test_example_6_1()')

		T = 100

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_example_6_1.json'
		sim_io.write_instance_and_states(network, filename, 'temp')

		# Correct node 0 demands.
		node0 = network.get_node_from_index(0)
		demand_list = [node0.state_vars[t].inbound_order[None] for t in range(T)]

		# Load instance and check it.
		new_network = load_instance('temp', filename, ignore_state_vars=True)
		self.assertListEqual(new_network.get_node_from_index(0).demand_source.demand_list[0:T], demand_list[0:T])
		# Remove state variables and demand sources and make sure networks are equal otherwise.
		for node in network.nodes:
			node.demand_source = None
			node.state_vars = None
		for node in new_network.nodes:
			node.demand_source = None
			node.state_vars = None
		self.assertTrue(network.deep_equal_to(new_network))

		# Delete file.
		os.remove(filename)

	def test_example_6_1_with_disruptions(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Example 6.1 with disruptions.
		"""
		print_status('TestWriteInstanceAndStates', 'test_example_6_1_with_disruptions()')

		T = 100

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})
		# Add disruptions.
		network.get_node_from_index(1).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='OP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_example_6_1_with_disruptions.json'
		sim_io.write_instance_and_states(network, filename, 'temp')

		# Correct node 0 demands and node 1 disruptions.
		node0 = network.get_node_from_index(0)
		demand_list = [node0.state_vars[t].inbound_order[None] for t in range(T)]
		node1 = network.get_node_from_index(1)
		disruption_list = [node1.state_vars[t].disrupted for t in range(T)]

		# Load instance and check it.
		new_network = load_instance('temp', filename, ignore_state_vars=True)
		self.assertListEqual(new_network.get_node_from_index(0).demand_source.demand_list[0:T], demand_list[0:T])
		self.assertListEqual(new_network.get_node_from_index(1).disruption_process.disruption_state_list[0:T], disruption_list[0:T])
		# Remove state variables, demand sources, and disruption processes and make sure networks are equal otherwise.
		for node in network.nodes:
			node.demand_source = None
			node.state_vars = None
			node.disruption_process = None
		for node in new_network.nodes:
			node.demand_source = None
			node.state_vars = None
			node.disruption_process = None
		self.assertTrue(network.deep_equal_to(new_network))

		# Delete file.
		os.remove(filename)

	def test_rong_atan_snyder_figure_1a(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Rong, Atan, and Snyder Figure 1.
		"""
		print_status('TestWriteInstanceAndStates', 'test_rong_atan_snyder_figure_1a()')

		T = 100

		# Build network.
		network = load_instance("rong_atan_snyder_figure_1a")

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_rong_atan_snyder_figure_1a.json'
		sim_io.write_instance_and_states(network, filename, 'temp')

		# Correct demands.
		demand_list = {}
		for node in network.nodes:
			if node in network.sink_nodes:
				demand_list[node.index] = [node.state_vars[t].inbound_order[None] for t in range(T)]

		# Load instance and check it.
		new_network = load_instance('temp', filename, ignore_state_vars=True)
		for node in new_network.nodes:
			if node in new_network.sink_nodes:
				self.assertListEqual(node.demand_source.demand_list[0:T], demand_list[node.index][0:T])
		# Remove state variables and demand sources and make sure networks are equal otherwise.
		for node in network.nodes:
			node.demand_source = None
			node.state_vars = None
		for node in new_network.nodes:
			node.demand_source = None
			node.state_vars = None
		self.assertTrue(network.deep_equal_to(new_network))

		# Delete file.
		os.remove(filename)

	def test_rong_atan_snyder_figure_1a_with_disruptions(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Rong, Atan, and Snyder Figure 1, with disruptions.
		"""
		print_status('TestWriteInstanceAndStates', 'test_rong_atan_snyder_figure_1a_with_disruptions()')

		T = 100

		# Build network.
		network = load_instance("rong_atan_snyder_figure_1a")
		# Add disruptions.
		network.get_node_from_index(1).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='OP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)
		network.get_node_from_index(3).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='SP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_rong_atan_snyder_figure_1a_with_disruptions.json'
		sim_io.write_instance_and_states(network, filename, 'temp')

		# Correct demands and disruption states.
		demand_list = {}
		disruption_state_list = {}
		for node in network.nodes:
			if node in network.sink_nodes:
				demand_list[node.index] = [node.state_vars[t].inbound_order[None] for t in range(T)]
			if node.disruption_process is not None and node.disruption_process.random_process_type is not None:
				disruption_state_list[node.index] = [node.state_vars[t].disrupted for t in range(T)]

		# Load instance and check it.
		new_network = load_instance('temp', filename, ignore_state_vars=True)
		for node in new_network.nodes:
			if node in new_network.sink_nodes:
				self.assertListEqual(node.demand_source.demand_list[0:T], demand_list[node.index][0:T])
			if node.disruption_process is not None and node.disruption_process.random_process_type is not None:
				self.assertListEqual(node.disruption_process.disruption_state_list[0:T], disruption_state_list[node.index][0:T])
		# Remove state variables, demand sources, and disruption processes and make sure networks are equal otherwise.
		for node in network.nodes:
			node.demand_source = None
			node.state_vars = None
			node.disruption_process = None
		for node in new_network.nodes:
			node.demand_source = None
			node.state_vars = None
			node.disruption_process = None
		self.assertTrue(network.deep_equal_to(new_network))

		# Delete file.
		os.remove(filename)
class TestDictToHeaderList(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDictToHeaderList', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDictToHeaderList', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that dict_to_header_list() function works correctly for
		simulation of Example 6.1. 
		"""
		print_status('TestDictToHeaderList', 'test_example_6_1()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)

		# Node 1 IO.
		header_list = sim_io._dict_to_header_list(network.get_node_from_index(1).state_vars[0].inbound_order, "IO")
		self.assertListEqual(header_list, ['IO:0'])

		# Node 2 IS.
		header_list = sim_io._dict_to_header_list(network.get_node_from_index(2).state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:EXT'])

	def test_mwor(self):
		"""Test that dict_to_header_list() function works correctly for an MWOR system.
		"""
		print_status('TestDictToHeaderList', 'test_mwor()')

		# Build network.
		network = mwor_system(3, node_order_in_lists=[0, 1, 2, 3],
								local_holding_cost=[5, 1, 1, 2],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)

		# Node 0 IS.
		header_list = sim_io._dict_to_header_list(network.get_node_from_index(0).state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:1', 'IS:2', 'IS:3'])

		# Node 2 IS.
		header_list = sim_io._dict_to_header_list(network.get_node_from_index(2).state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:EXT'])

		# Node 0 ISPL.
		header_list = sim_io._dict_to_header_list(network.get_node_from_index(0).state_vars[0].inbound_shipment_pipeline, "ISPL")
		self.assertListEqual(header_list, ['ISPL:1', 'ISPL:2', 'ISPL:3'])

