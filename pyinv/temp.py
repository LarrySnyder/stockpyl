from pyinv.gsm_tree import *
from pyinv.ssm_serial import *
from tests.instances_ssm_serial import *

# Create DiGraph.
two_stage = nx.DiGraph()
k=5
two_stage.add_node(1, processing_time=1,
                     external_inbound_cst=0,
                     external_outbound_cst=0,
                     holding_cost=2, # local
                     stockout_cost=10, # ignored in GSM optimization
                     demand_bound_constant=k,
                     external_demand_mean=10,
                     external_demand_standard_deviation=2)
two_stage.add_node(2, processing_time=1,
                     external_inbound_cst=0,
                     holding_cost=1, # local
                     demand_bound_constant=k)
two_stage.add_edge(2, 1)

# Preprocess.
two_stage = preprocess_tree(two_stage)

#BSL_vec = np.arange(0, 30, 2)
two_stage_SSM = GSM_to_SSM(two_stage)

local_S = {1: 100, 2: 200}
GSM_cost = solution_cost_from_base_stock_levels(two_stage, local_S)
echelon_S = local_to_echelon_base_stock_levels(two_stage, local_S)
SSM_cost = expected_holding_cost(two_stage_SSM, echelon_S, x_num=1000, d_num=100)

print("GSM_cost = {}, SSM_cost = {}".format(GSM_cost, SSM_cost))

# # Fix BSL_1 = 10, plot cost vs. BSL_2.
# cost_GSM = []
# cost_SSM = []
# for i in range(len(BSL_vec)):
#     local_S = {1: 10, 2: BSL_vec[i]}
#     cost_GSM.append(solution_cost_from_base_stock_levels(two_stage, local_S))
#     echelon_S = local_to_echelon_base_stock_levels(two_stage, local_S)
#     cost_SSM.append(expected_holding_cost(two_stage_SSM, echelon_S, x_num=100, d_num=50))
# ax1 = plt.subplot(1, 2, 1)
# ax1.plot(BSL_vec, cost_GSM, BSL_vec, cost_SSM)
# plt.legend(['GSM cost', 'SSM cost'])
# plt.title('Holding Cost vs. Local BSL_2 (BSL_1=10)')
# plt.xlabel('Local BSL_2');
# plt.ylabel('Expected Holding Cost');
#
# # Fix BSL_2 = 10, plot cost vs. BSL_1.
# cost_GSM = []
# cost_SSM = []
# for i in range(len(BSL_vec)):
#     local_S = {1: BSL_vec[i], 2: 10}
#     cost_GSM.append(solution_cost_from_base_stock_levels(two_stage, local_S))
#     echelon_S = local_to_echelon_base_stock_levels(two_stage, local_S)
#     cost_SSM.append(expected_holding_cost(two_stage_SSM, echelon_S, x_num=100, d_num=50))
# ax2 = plt.subplot(1, 2, 2)
# ax2.plot(BSL_vec, cost_GSM, BSL_vec, cost_SSM)
# plt.legend(['GSM cost', 'SSM cost'])
# plt.title('Holding Cost vs. Local BSL_1 (BSL_2=10)')
# plt.xlabel('Local BSL_1');
# plt.ylabel('Expected Holding Cost');
#
# fig = plt.gcf()
# fig.set_size_inches(12, 6)
# plt.show()

