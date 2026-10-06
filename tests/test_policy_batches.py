"""MOQ/IOQ regression and end-to-end simulation tests for finished-good policies."""
import math
import unittest
from stockpyl.policy import Policy
from stockpyl.supply_chain_network import single_stage_system, serial_system
from stockpyl.supply_chain_product import SupplyChainProduct
from stockpyl.sim import simulation


class TestPolicyBatches(unittest.TestCase):
    def test_minimum_increment_capacity_examples(self):
        policy = Policy(type='BS', base_stock_level=10,
                        minimum_order_quantity=7, order_quantity_increment=5)
        self.assertEqual(policy.get_order_quantity(inventory_position=8), 10)
        self.assertEqual(policy.get_order_quantity(inventory_position=10), 0)
        self.assertEqual(policy.get_order_quantity(inventory_position=11), 0)
        self.assertEqual(policy.get_order_quantity(inventory_position=8, order_capacity=8), 0)
        self.assertEqual(policy.get_order_quantity(inventory_position=-2, order_capacity=12), 10)
        self.assertEqual(policy.get_order_quantity(inventory_position=-2, order_capacity=0), 0)
        self.assertEqual(policy.get_order_quantity(inventory_position=-2, order_capacity=math.inf), 15)

    def test_minimum_only_and_increment_only(self):
        minimum = Policy(type='BS', base_stock_level=10, minimum_order_quantity=7)
        self.assertEqual(minimum.get_order_quantity(inventory_position=8), 7)
        self.assertEqual(minimum.get_order_quantity(inventory_position=-2, order_capacity=8), 8)
        self.assertEqual(minimum.get_order_quantity(inventory_position=8, order_capacity=6), 0)
        batch = Policy(type='FQ', order_quantity=2.1, order_quantity_increment=.5)
        self.assertEqual(batch.get_order_quantity(), 2.5)
        self.assertEqual(batch.get_order_quantity(order_capacity=2.2), 2)
        self.assertEqual(batch.get_order_quantity(order_capacity=.2), 0)

    def test_legacy_defaults_and_serialization(self):
        policy = Policy(type='BS', base_stock_level=60)
        self.assertEqual(policy.get_order_quantity(inventory_position=52.5), 7.5)
        self.assertEqual(policy.get_order_quantity(inventory_position=52.5, order_capacity=3.2), 3.2)
        self.assertEqual(repr(policy), 'Policy(BS: base_stock_level=60.00)')
        old_dict = {'type': 'BS', 'base_stock_level': 60}
        self.assertEqual(Policy.from_dict(old_dict), policy)
        policy.minimum_order_quantity = 7
        policy.order_quantity_increment = 5
        restored = Policy.from_dict(policy.to_dict())
        self.assertEqual(restored, policy)
        restored.order_quantity_increment = 10
        self.assertNotEqual(restored, policy)
        self.assertIn('minimum_order_quantity=7.00', repr(policy))

    def test_other_policy_types(self):
        examples = [
            Policy(type='sS', reorder_point=9, order_up_to_level=10),
            Policy(type='rQ', reorder_point=9, order_quantity=2),
            Policy(type='FQ', order_quantity=2),
            Policy(type='EBS', base_stock_level=10),
            Policy(type='BEBS', base_stock_level=10),
        ]
        for policy in examples:
            with self.subTest(type=policy.type):
                policy.minimum_order_quantity = 7
                policy.order_quantity_increment = 5
                self.assertEqual(policy.get_order_quantity(inventory_position=8,
                                 echelon_inventory_position_adjusted=math.inf), 10)

    def test_integer_orders_match_enumerated_feasible_set(self):
        # Independent oracle enumerates the admissible quantities instead of rounding.
        for minimum in [0, 1, 7, 10]:
            for increment in [1, 3, 5]:
                for capacity in [0, 2, 8, 12, 30]:
                    admissible = [q for q in range(1, capacity + 1)
                                  if q >= minimum and q % increment == 0]
                    for request in [0, 1, 2, 7, 12, 25, 40]:
                        reaching = [q for q in admissible if q >= request]
                        expected = 0 if request == 0 else (min(reaching) if reaching else max(admissible, default=0))
                        policy = Policy(type='FQ', order_quantity=request,
                                        minimum_order_quantity=minimum,
                                        order_quantity_increment=increment)
                        self.assertEqual(policy.get_order_quantity(order_capacity=capacity), expected)

    def test_invalid_configuration_rejected(self):
        for name, values in [('minimum_order_quantity', [-1, math.nan, math.inf, '7']),
                             ('order_quantity_increment', [0, -1, math.nan, math.inf, '5'])]:
            for value in values:
                policy = Policy(type='BS', base_stock_level=10, **{name: value})
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    policy.get_order_quantity(inventory_position=8)
                with self.assertRaises(ValueError):
                    policy.validate_parameters()
        for capacity in [-1, math.nan, '8']:
            policy = Policy(type='BS', base_stock_level=10, order_quantity_increment=5)
            with self.assertRaises(ValueError):
                policy.get_order_quantity(inventory_position=8, order_capacity=capacity)

    def test_factory_and_simulation_with_capacity(self):
        demand = [4, 2, 1, 0, 8, 0, 1, 0]
        network = single_stage_system(index=0, demand_type='D', demand_list=demand,
                    policy_type='BS', base_stock_level=5, minimum_order_quantity=7,
                    order_quantity_increment=5, order_capacity=12, shipment_lead_time=2,
                    initial_inventory_level=0, local_holding_cost=1, stockout_cost=2)
        node = network.nodes[0]
        # Main's unreleased fixed-cost calculation currently has no node default.
        # Declare zero explicitly; release 1.0.2 does not use this attribute.
        node.fixed_cost = 0
        self.assertEqual(node.inventory_policy.minimum_order_quantity, 7)
        self.assertEqual(node.inventory_policy.order_quantity_increment, 5)
        simulation(network, len(demand), rand_seed=42, progress_bar=False, consistency_checks='E')
        product = node.product_indices[0]
        orders, net = [], 0
        for t, d in enumerate(demand):
            if t >= 2:
                net += orders[t - 2]
            net -= d
            outstanding = sum(orders[max(0, t - 1):])
            request = max(0, 5 - (net + outstanding))
            expected = 10 if request > 0 else 0
            actual = node.state_vars[t].order_quantity_fg[product]
            self.assertEqual(actual, expected)
            orders.append(actual)
            self.assertEqual(node.state_vars[t].inventory_level[product], net)

    def test_finished_good_batches_are_scaled_before_bom_allocation(self):
        network = serial_system(num_nodes=2, node_order_in_system=[2, 1],
                node_order_in_lists=[1, 2], demand_type='D', demand_list=[2, 0, 4, 1],
                shipment_lead_time=[1, 1], initial_inventory_level=0,
                local_holding_cost=1, stockout_cost=1)
        nodes = network.nodes_by_index
        products = {i: SupplyChainProduct(index=i) for i in [10, 20, 30]}
        products[10].set_bill_of_materials(raw_material=20, num_needed=2.5)
        products[10].set_bill_of_materials(raw_material=30, num_needed=3)
        nodes[1].add_product(products[10])
        nodes[2].add_products([products[20], products[30]])
        products[10].inventory_policy = Policy(type='BS', base_stock_level=5,
                minimum_order_quantity=7, order_quantity_increment=5,
                node=nodes[1], product=products[10])
        nodes[1].order_capacity = 12
        nodes[2].inventory_policy = {i: Policy(type='BS', base_stock_level=100,
                                    node=nodes[2], product=products[i]) for i in [20, 30]}
        for node in network.nodes:
            node.fixed_cost = 0
        simulation(network, 4, rand_seed=42, progress_bar=False, consistency_checks='E')
        for state in nodes[1].state_vars[:4]:
            fg = state.order_quantity_fg[10]
            self.assertIn(fg, [0, 10])
            self.assertEqual(state.order_quantity[2][20], fg * 2.5)
            self.assertEqual(state.order_quantity[2][30], fg * 3)


if __name__ == '__main__':
    unittest.main()
