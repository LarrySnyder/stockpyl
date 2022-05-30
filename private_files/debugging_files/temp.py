import os
import sys

sys.path.append(os.getcwd())

from stockpyl.gsm_tree import *
from stockpyl.instances import load_instance

net1 = load_instance("example_6_1")
net2 = load_instance("temp")
net2.reindex_nodes({1: 0, 2: 1, 3: 2})
print(net1.deep_equal_to(net2))