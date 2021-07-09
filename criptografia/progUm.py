'''
Programa para calcular menssagem via método digest()
'''
import hashlib

h = hashlib.new('sha256')
h.update(b'Nobody expects the Spanish Inquisition.')
h.digest()#Varia de 0 a 255
h.hexdigest()#Hexadecimal
print(h.digest())
print(h.hexdigest())
