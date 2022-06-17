from stockpyl.loss_functions import negative_binomial_loss

r = 6
p = 0.4

n, bar_n = negative_binomial_loss(10, r, p)
print(f"n = {n} bar_n = {bar_n}")