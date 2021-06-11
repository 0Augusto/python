# -*- coding: utf-8 -*-

a, b, c = map(int, input().split())
  
MaiorAB = ((a + b + abs(a - b))/2)

maiorAB = (MaiorAB + c + abs(MaiorAB - c))/2

print("%d eh o maior" %maiorAB)
