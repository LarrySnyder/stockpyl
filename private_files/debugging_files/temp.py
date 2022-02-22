import os
import sys

sys.path.append(os.getcwd())

from stockpyl.gsm_tree import *
from stockpyl.instances import load_instance

tree = load_instance("example_6_5")
tree = preprocess_tree(tree)
cst = {1: 0, 3: 0, 2: 0, 4: 1}
#solution_cost_from_cst(tree, cst)
#bsl = {1: 2.45, 2: 1.00, 3: 1.41, 4: 0.00}
#print(solution_cost_from_base_stock_levels(tree, bsl))
print(cst_to_base_stock_levels(tree, tree.node_indices, cst))