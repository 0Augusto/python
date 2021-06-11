# -*- coding: utf-8 -*-

import math

x1, y1 = map(float, input().split())

x2, y2 = map(float, input().split())

dist = pow(pow(x2 - x1, 2) + pow(y2 - y1, 2), 0.5)

print("%0.4f" %dist)
