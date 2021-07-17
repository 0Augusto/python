# -*- coding: utf-8 -*-
import math

A, B, C = map(float, input().split())

delta = pow(B, 2) - (4 * A * C)

if A == 0.0 or delta < 0: 
    print("Impossivel calcular")
else:
    x1 = (-B + (delta) ** (1.0/2.0))/(2.0 * A)
    x2 = (-B - (delta) ** (1.0/2.0))/(2.0 * A)

    print('R1 = %0.5f' %x1)
    print('R2 = %0.5f' %x2)
