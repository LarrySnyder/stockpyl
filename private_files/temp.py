# This is necessary in order to make the import statements work.
import sys

sys.path.append('../src/')

from stockpyl import eoq

print(eoq.economic_order_quantity(50, 1, 100))