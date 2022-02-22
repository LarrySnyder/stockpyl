# Short script to save instance information to CSV for inclusion in
# documentation page.

import sys

sys.path.append('/Users/larry/Documents/GitHub/stockpyl')

from stockpyl.instances import *

save_summary_to_csv('docs/aux_files/temp.csv')