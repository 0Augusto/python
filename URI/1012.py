# -*- coding: utf-8 -*-

A, B, C = map(float, input().split())

pi = 3.14159

at = (A * C)/2 
print("TRIANGULO: %0.3f" %at)

rc = pi * (C * C)
print("CIRCULO: %0.3f" %rc)

aTrape = C * (A+B)/2
print("TRAPEZIO: %0.3f" %aTrape)

aQuad = B * B
print("QUADRADO: %0.3f" %aQuad)

aRet = A * B
print("RETANGULO: %0.3f" %aRet)
