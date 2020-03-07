from enum import Enum


# -------------------

# ENUM TYPES

class DemandType(Enum):
	NONE = 0					# no external demand
	NORMAL = 1
	UNIFORM_DISCRETE = 2
	UNIFORM_CONTINUOUS = 3
	DETERMINISTIC = 4			# must supply 'demands' parameter
	DISCRETE_EXPLICIT = 5		# must supply 'demands' and 'demand_probs' parameters


class SupplyType(Enum):
	NONE = 0					# no external supply
	UNLIMITED = 1				# unlimited external supply
