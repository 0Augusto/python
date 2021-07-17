# -*- coding: utf-8 -*-

age = int(input())

year = age//365

age = age - year * 365

month = age//30

age = age - month * 30

day = age

print('{} ano(s)'.format(year))
print('{} mes(es)'.format(month))
print('{} dia(s)'.format(day))
