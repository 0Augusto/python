# -*- coding: utf-8 -*-

X, Y = map(int, input().split())

if   (X == 1):
    Total = (float) (4.00 * Y)
elif (X == 2):
    Total = (float) (4.50 * Y)
elif (X == 3):
    Total = (float) (5.00 * Y)
elif (X == 4):
    Total = (float) (2.00 * Y)
elif (X == 5):
    Total = (float) (1.50 * Y)
print("Total: R$ %0.2f" %Total)
