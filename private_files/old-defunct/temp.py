from scipy.stats import *
import numpy as np

def is_discrete(dist):
	try:
		_ = dist.pmf(0)
		return True
	except AttributeError:
		return False
	# if type(dist) == rv_discrete:
	# 	return True
	# else:
	# 	return False

dist_norm = norm(10, 2)
dist_poisson = poisson(10)

class continuous_gen(rv_continuous):
	def _pdf(self, x, *args):
		if x >= 0 and x <= 1:
			return 1
		else:
			return 0
dist_contin = continuous_gen()

xk = np.arange(7)
pk = (0.1, 0.2, 0.3, 0.1, 0.1, 0.0, 0.2)
dist_discrete = rv_discrete(values=(xk, pk))

print(type(dist_norm))		# --> return False
print(type(dist_poisson))	# --> return True
print(type(dist_contin))		# --> return False
print(type(dist_discrete))	# --> return True

print(is_discrete(dist_norm))		# --> return False
print(is_discrete(dist_poisson))	# --> return True
print(is_discrete(dist_contin))		# --> return False
print(is_discrete(dist_discrete))	# --> return True
