# This is necessary in order to make the import statements work.
#import sys

#sys.path.append('../src/')

from stockpyl.helpers import build_node_data_dict

attribute_names=['local_holding_cost', 'stockout_cost', 'demand_mean', 'lead_time', 'processing_time']
attribute_values = {}
attribute_values['local_holding_cost'] = 1
attribute_values['stockout_cost'] = [10, 8, 0]
attribute_values['demand_mean'] = {1: 0, 3: 50}
attribute_values['lead_time'] = None
attribute_values['processing_time'] = None
node_indices = [3, 2, 1]
default_values = {'lead_time': 0, 'demand_mean': 99}

data_dict = build_node_data_dict(attribute_names, attribute_values, node_indices, default_values)

print(data_dict[1])
print(data_dict[2])
print(data_dict[3])