from .. stockpyl.eoq import *

import numpy as np

# h = np.array([1, 1, 1])
# K = np.array([10, 10, 10])
# d = np.array([1, 1, 1])

# h = (1, 2, 3)
# K = (10, 10, 10)
# d = (1, 1, 1)

h = 2
K = 10
d = 1

print(economic_order_quantity(K, h, d))