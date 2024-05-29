import unittest

from stockpyl.supply_chain_network import *
from stockpyl.supply_chain_product import *
from stockpyl.demand_source import DemandSource
from stockpyl.policy import Policy
from stockpyl.instances import *
from stockpyl.sim import *
from tests.settings import RUN_ALL_TESTS
#RUN_ALL_TESTS = False

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_supply_chain_product   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestSupplyChainProductInit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainProductInit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainProductInit', 'tear_down_class()')

	def test_kwargs(self):
		"""Test that SupplyChainProduct.__init__() produces identical products
		if parameters are passed as arguments vs. set later.
		"""
		print_status('TestSupplyChainProductInit', 'test_kwargs()')

		product1 = SupplyChainProduct(index=1, name='foo', local_holding_cost=5, order_lead_time=2)
		product2 = SupplyChainProduct(index=1)
		product2.name = 'foo'
		product2.local_holding_cost = 5
		product2.order_lead_time = 2
		self.assertTrue(product1.deep_equal_to(product2))

		product1 = SupplyChainProduct(index=3, name='bar', local_holding_cost=2,
			demand_source=DemandSource(type='N', mean=20, standard_deviation=4), 
			inventory_policy=Policy(type='BS', base_stock_level=30)
		)
		product2 = SupplyChainProduct(index=3)
		product2.name = 'bar'
		product2.local_holding_cost = 2
		product2.demand_source = DemandSource()
		product2.demand_source.type = 'N'
		product2.demand_source.mean = 20
		product2.demand_source.standard_deviation = 4
		product2.inventory_policy = Policy()
		product2.inventory_policy.type = 'BS'
		product2.inventory_policy.base_stock_level = 30
		self.assertTrue(product1.deep_equal_to(product2))

	def test_bad_params(self):
		"""Test that SupplyChainProduct.__init__() correctly raises errors on
		invalid parameters.
		"""
		print_status('TestSupplyChainProductInit', 'test_bad_params()')

		with self.assertRaises(AttributeError):
			_ = SupplyChainProduct(index=4, foo=7)


class TestIndex(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIndex', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIndex', 'tear_down_class()')

	def test_bad_index(self):
		"""Test that index property correctly raises error when appropriate.
		"""
		print_status('TestIndex', 'test_bad_index()')

		with self.assertRaises(ValueError):
			_ = SupplyChainProduct(index=5.5)
			_ = SupplyChainProduct(index=-10)

		# Make sure no error raised here.
		_ = SupplyChainProduct(index=-10, is_dummy=True)	
		
		
class TestSetGetBillOfMaterials(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSetGetBillOfMaterials', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSetGetBillOfMaterials', 'tear_down_class()')

	def test_basic(self):
		"""Test that set_ and get_bill_of_materials() work correctly.
		"""
		print_status('TestSetGetBillOfMaterials', 'test_basic()')

		prod = {i: SupplyChainProduct(index=i) for i in range(7)}

		prod[0].set_bill_of_materials(2, 2.5)
		prod[0].set_bill_of_materials(3, 7)
		prod[1].set_bill_of_materials(3, 10)
		prod[1].set_bill_of_materials(4, 3.8)
		prod[2].set_bill_of_materials(5, 0.2)
		prod[3].set_bill_of_materials(5, 2)
		prod[4].set_bill_of_materials(6, 50)
		
		self.assertEqual(prod[0].get_bill_of_materials(2), 2.5)
		self.assertEqual(prod[0].get_bill_of_materials(3), 7)
		self.assertEqual(prod[1].get_bill_of_materials(3), 10)
		self.assertEqual(prod[1].get_bill_of_materials(4), 3.8)
		self.assertEqual(prod[2].get_bill_of_materials(5), 0.2)
		self.assertEqual(prod[3].get_bill_of_materials(5), 2)
		self.assertEqual(prod[4].get_bill_of_materials(6), 50)

		self.assertEqual(prod[0].get_bill_of_materials(5), 0)
		self.assertEqual(prod[4].get_bill_of_materials(655), 0)


class TestBillOfMaterialsDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestBillOfMaterialsDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestBillOfMaterialsDict', 'tear_down_class()')

	def test_basic(self):
		"""Basic test of bill_of_materials_dict.
		"""
		print_status('TestBillOfMaterialsDict', 'test_basic()')

		prod = {i: SupplyChainProduct(index=i) for i in range(7)}

		prod[0].set_bill_of_materials(2, 2.5)
		prod[0].set_bill_of_materials(3, 7)
		prod[1].set_bill_of_materials(3, 10)
		prod[1].set_bill_of_materials(4, 3.8)
		prod[2].set_bill_of_materials(5, 0.2)
		prod[3].set_bill_of_materials(5, 2)
		prod[4].set_bill_of_materials(6, 50)


		self.assertDictEqual(prod[0].bill_of_materials_dict, {2: 2.5, 3: 7})
		self.assertDictEqual(prod[1].bill_of_materials_dict, {3: 10, 4: 3.8})
		self.assertDictEqual(prod[2].bill_of_materials_dict, {5: 0.2})
		self.assertDictEqual(prod[3].bill_of_materials_dict, {5: 2})
		self.assertDictEqual(prod[4].bill_of_materials_dict, {6: 50})
		self.assertDictEqual(prod[5].bill_of_materials_dict, {})
		self.assertDictEqual(prod[6].bill_of_materials_dict, {})

class TestHandlingNodes(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRawMaterials', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRawMaterials', 'tear_down_class()')

	def test_basic(self):
		"""Basic test of raw_materials and raw_material_indices.
		"""
		print_status('TestRawMaterials', 'test_basic()')

		prod = {i: SupplyChainProduct(index=i) for i in range(7)}

		prod[0].set_bill_of_materials(2, 2.5)
		prod[0].set_bill_of_materials(3, 7)
		prod[1].set_bill_of_materials(3, 10)
		prod[1].set_bill_of_materials(4, 3.8)
		prod[2].set_bill_of_materials(5, 0.2)
		prod[3].set_bill_of_materials(5, 2)
		prod[4].set_bill_of_materials(6, 50)

		network = SupplyChainNetwork()
		for i in range(7):
			network.add_product(prod[i])
		
		self.assertListEqual(prod[0].raw_materials, [prod[2], prod[3]])
		self.assertListEqual(prod[1].raw_materials, [prod[3], prod[4]])
		self.assertListEqual(prod[2].raw_materials, [prod[5]])
		self.assertListEqual(prod[3].raw_materials, [prod[5]])
		self.assertListEqual(prod[4].raw_materials, [prod[6]])
		self.assertListEqual(prod[5].raw_materials, [])
		self.assertListEqual(prod[6].raw_materials, [])

		self.assertListEqual(prod[0].raw_material_indices, [2, 3])
		self.assertListEqual(prod[1].raw_material_indices, [3, 4])
		self.assertListEqual(prod[2].raw_material_indices, [5])
		self.assertListEqual(prod[3].raw_material_indices, [5])
		self.assertListEqual(prod[4].raw_material_indices, [6])
		self.assertListEqual(prod[5].raw_material_indices, [])
		self.assertListEqual(prod[6].raw_material_indices, [])


class TestRawMaterials(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRawMaterials', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRawMaterials', 'tear_down_class()')

	def test_basic(self):
		"""Basic test of raw_materials and raw_material_indices.
		"""
		print_status('TestRawMaterials', 'test_basic()')

		prod = {i: SupplyChainProduct(index=i) for i in range(7)}

		prod[0].set_bill_of_materials(2, 2.5)
		prod[0].set_bill_of_materials(3, 7)
		prod[1].set_bill_of_materials(3, 10)
		prod[1].set_bill_of_materials(4, 3.8)
		prod[2].set_bill_of_materials(5, 0.2)
		prod[3].set_bill_of_materials(5, 2)
		prod[4].set_bill_of_materials(6, 50)

		network = SupplyChainNetwork()
		for i in range(7):
			network.add_product(prod[i])
		
		self.assertListEqual(prod[0].raw_materials, [prod[2], prod[3]])
		self.assertListEqual(prod[1].raw_materials, [prod[3], prod[4]])
		self.assertListEqual(prod[2].raw_materials, [prod[5]])
		self.assertListEqual(prod[3].raw_materials, [prod[5]])
		self.assertListEqual(prod[4].raw_materials, [prod[6]])
		self.assertListEqual(prod[5].raw_materials, [])
		self.assertListEqual(prod[6].raw_materials, [])

		self.assertListEqual(prod[0].raw_material_indices, [2, 3])
		self.assertListEqual(prod[1].raw_material_indices, [3, 4])
		self.assertListEqual(prod[2].raw_material_indices, [5])
		self.assertListEqual(prod[3].raw_material_indices, [5])
		self.assertListEqual(prod[4].raw_material_indices, [6])
		self.assertListEqual(prod[5].raw_material_indices, [])
		self.assertListEqual(prod[6].raw_material_indices, [])


class TestSupplyChainProductEq(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainProductEq', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainProductEq', 'tear_down_class()')

	def test_eq(self):
		"""Test SupplyChainProduct.__eq__().
		"""
		print_status('TestSupplyChainProductEq', 'test_eq()')

		product1 = SupplyChainProduct(index=3, name="foo")
		product2 = SupplyChainProduct(index=3, name="bar")
		product3 = SupplyChainProduct(index=5, name=None)
		product4 = SupplyChainProduct(index=5, name="taco")
		product5 = SupplyChainProduct(index=3, name="foo")

		eq11 = product1 == product1
		eq12 = product1 == product2
		eq13 = product1 == product3
		eq14 = product1 == product4
		eq15 = product1 == product5
		eq21 = product2 == product1
		eq22 = product2 == product2
		eq23 = product2 == product3
		eq24 = product2 == product4
		eq25 = product2 == product5
		eq31 = product3 == product1
		eq32 = product3 == product2
		eq34 = product3 == product4
		eq35 = product3 == product5

		self.assertEqual(eq11, True)
		self.assertEqual(eq12, True)
		self.assertEqual(eq13, False)
		self.assertEqual(eq14, False)
		self.assertEqual(eq15, True)
		self.assertEqual(eq21, True)
		self.assertEqual(eq22, True)
		self.assertEqual(eq23, False)
		self.assertEqual(eq24, False)
		self.assertEqual(eq25, True)
		self.assertEqual(eq31, False)
		self.assertEqual(eq32, False)
		self.assertEqual(eq34, True)
		self.assertEqual(eq35, False)

	def test_list_contains(self):
		"""Test that a list can correctly determine whether a SupplyChainProduct is
		contained in it. This depends on SupplyChainProduct.__eq__() working
		properly.
		"""
		print_status('TestSupplyChainProductEq', 'test_list_contains()')

		product1 = SupplyChainProduct(index=3, name="foo")
		product2 = SupplyChainProduct(index=3, name="bar")
		product3 = SupplyChainProduct(index=5, name=None)
		product4 = SupplyChainProduct(index=6, name="taco")
		product5 = SupplyChainProduct(index=3, name="foo")

		mylist = [product1, product2, product3]

		contains1 = product1 in mylist
		contains2 = product2 in mylist
		contains3 = product3 in mylist
		contains4 = product4 in mylist
		contains5 = product5 in mylist

		self.assertEqual(contains1, True)
		self.assertEqual(contains2, True)
		self.assertEqual(contains3, True)
		self.assertEqual(contains4, False)
		self.assertEqual(contains5, True)


## STOPPED 
		
class TestDeepEqualTo(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDeepEqualTo', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDeepEqualTo', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test deep_equal_to() for nodes in in Example 6.1, but treating the nodes as though
		they were products.
		"""
		print_status('TestDeepEqualTo', 'test_example_6_1()')

		network = load_instance("example_6_1")

		# Convert nodes in network to products.
		products = {n: SupplyChainProduct.from_node(network.nodes_by_index[n]) for n in network.node_indices}

		# Equal products.
		product1copy = copy.deepcopy(products[1])
		self.assertTrue(product1copy.deep_equal_to(products[1]))
		self.assertTrue(products[1].deep_equal_to(product1copy))
		product2copy = copy.deepcopy(products[2])
		self.assertTrue(product2copy.deep_equal_to(products[2]))
		self.assertTrue(products[2].deep_equal_to(product2copy))
		product3copy = copy.deepcopy(products[3])
		self.assertTrue(product3copy.deep_equal_to(products[3]))
		self.assertTrue(products[3].deep_equal_to(product3copy))

		# Unequal nodes due to parameters.
		product1copy.local_holding_cost = 99
		self.assertFalse(product1copy.deep_equal_to(products[1]))
		self.assertFalse(products[1].deep_equal_to(product1copy))
		product2copy.demand_source.standard_deviation = 99
		self.assertFalse(product2copy.deep_equal_to(products[2]))
		self.assertFalse(products[2].deep_equal_to(product2copy))

		# Unequal networks due to missing policy.
		product3copy.inventory_policy = None
		self.assertFalse(product3copy.deep_equal_to(products[3]))
		self.assertFalse(products[3].deep_equal_to(product3copy))


class TestProductToFromDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestProductToFromDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestProductToFromDict', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainProduct objects to and from dicts,
		for products converted from nodes in Example 6.1.
		"""
		print_status('TestProductToFromDict', 'test_example_6_1()')

		network = load_instance("example_6_1")

		# Convert nodes in network to products.
		products = [SupplyChainProduct.from_node(network.nodes_by_index[n]) for n in network.node_indices]

		# Convert products to dicts.
		product_dicts = [prod.to_dict() for prod in products]

		# Convert dicts back to products.
		dict_products = [SupplyChainProduct.from_dict(d) for d in product_dicts]

		# Compare.
		for i in range(len(products)):
			self.assertTrue(products[i].deep_equal_to(dict_products[i]))

	def test_assembly_3_stage(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainProduct objects to and from dicts,
		for products converted from nodes in 3-stage assembly system.
		"""
		print_status('TestProductToFromDict', 'test_assembly_3_stage()')

		network = load_instance("example_6_1")

		# Convert nodes in network to products.
		products = [SupplyChainProduct.from_node(network.nodes_by_index[n]) for n in network.node_indices]

		# Convert products to dicts.
		product_dicts = [prod.to_dict() for prod in products]

		# Convert dicts back to products.
		dict_products = [SupplyChainProduct.from_dict(d) for d in product_dicts]

		# Compare.
		for i in range(len(products)):
			self.assertTrue(products[i].deep_equal_to(dict_products[i]))

			
class TestProductFromNode(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestProductFromNode', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestProductFromNode', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that from_node() correctly converts SupplyChainNode object to product
		in Example 6.1.
		"""
		print_status('TestProductFromNode', 'test_example_6_1()')

		network = load_instance("example_6_1")

		# Convert nodes in network to products.
		products = {n: SupplyChainProduct.from_node(network.nodes_by_index[n]) for n in network.node_indices}

		# Build products from scratch.
		scratch_products = {
			1: SupplyChainProduct(1, 
						 echelon_holding_cost=2, 
						 local_holding_cost=2, 
						 shipment_lead_time=2, 
						 stockout_cost=0,
						 demand_source=DemandSource(type='N', mean=5, standard_deviation=1),
						 inventory_policy=Policy(type='BS', base_stock_level=6.49)
						 ),
			2: SupplyChainProduct(2, 
						 echelon_holding_cost=2, 
						 local_holding_cost=4, 
						 shipment_lead_time=1, 
						 stockout_cost=0,
						 demand_source=None,
						 inventory_policy=Policy(type='BS', base_stock_level=5.53)
						 ),
			3: SupplyChainProduct(3, 
						 echelon_holding_cost=3, 
						 local_holding_cost=7, 
						 shipment_lead_time=1, 
						 stockout_cost=0,
						 demand_source=None,
						 inventory_policy=Policy(type='BS', base_stock_level=10.69)
						 ),
		}

		# Compare.
		for i in network.node_indices:
			self.assertTrue(products[i], scratch_products[i])


	def test_assembly_3_stage(self):
		"""Test that from_node() correctly converts SupplyChainNode object to product
		in 3-stage assembly system.
		"""
		print_status('TestProductFromNode', 'test_assembly_3_stage()')

		network = load_instance("assembly_3_stage")

		# Convert nodes in network to products.
		products = {n: SupplyChainProduct.from_node(network.nodes_by_index[n]) for n in range(3)}

		# Build products from scratch.
		scratch_products = {
			0: SupplyChainProduct(0, 
						 local_holding_cost=2, 
						 stockout_cost=20,
						 shipment_lead_time=1, 
						 demand_source=DemandSource(type='N', mean=5, standard_deviation=1),
						 inventory_policy=Policy(type='BS', base_stock_level=7),
						 initial_inventory_level=7
						 ),
			1: SupplyChainProduct(1, 
						 local_holding_cost=1, 
						 stockout_cost=0,
						 shipment_lead_time=2, 
						 demand_source=None,
						 inventory_policy=Policy(type='BS', base_stock_level=13),
						 initial_inventory_level=13
						 ),
			2: SupplyChainProduct(2, 
						 local_holding_cost=1, 
						 stockout_cost=0,
						 shipment_lead_time=2, 
						 demand_source=None,
						 inventory_policy=Policy(type='BS', base_stock_level=11),
						 initial_inventory_level=11
						 )
		}

		# Compare.
		for i in range(3):
			self.assertTrue(products[i], scratch_products[i])


class TestInitialize(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestInitialize', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestInitialize', 'tear_down_class()')

	def test_initialize(self):
		"""Test that initialize() correctly initializes.
		"""
		print_status('TestInitialize', 'test_copy()')

		prod1 = SupplyChainProduct(index=0)
		prod2 = SupplyChainProduct(index=0)
		prod1.initialize()
		self.assertTrue(prod1.deep_equal_to(prod2))

		prod1 = SupplyChainProduct(index=0, local_holding_cost=2, stockout_cost=50, shipment_lead_time=3)
		prod2 = SupplyChainProduct(index=0)
		prod1.initialize()
		self.assertTrue(prod1.deep_equal_to(prod2))

