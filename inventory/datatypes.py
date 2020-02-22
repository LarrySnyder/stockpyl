from enum import Enum

# -------------------

# ENUM TYPES


class PlayerType(Enum):
	BASE_STOCK = 0				# aka Rational
	STERMAN = 1					# aka Human-Like
	RANDOM = 2					# aka Random
	DNN = 3						# aka AI
	HUMAN = 4					# aka Human
	OPTIMIZED_BASE_STOCK = 5	# used by simulate_all_player_combinations()


class DemandType(Enum):
	NONE = 0					# no external demand
	NORMAL = 1
	UNIFORM_DISCRETE = 2
	UNIFORM_CONTINUOUS = 3
	DETERMINISTIC = 4			# must supply 'demands' parameter
	DISCRETE_EXPLICIT = 5		# must supply 'demands' and 'demand_probs' parameters

