import math

A, B, C = map(float, input().split())
print(A, B, C)

delta = pow(B, 2) - (4 * A * C)

val     = (-B) + pow(delta, 0.5)/(2 * A)
valDois = (-B) - pow(delta, 0.5)/(2 * A)
if delta >= 0 and A <= 0 and A > 0: 
    print('R1 = %f' %val)
    print('R2 = %f' %valDois)
else:
    print("Impossivel calcular")
