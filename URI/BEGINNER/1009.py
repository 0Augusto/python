# -*- coding: utf-8 -*-

nome = input()
salario = float(input())
totalVendido = float(input())
bonus = 0.15

salarioTotal = salario + (totalVendido * bonus)

print("TOTAL = R$ %0.2f" %salarioTotal)
