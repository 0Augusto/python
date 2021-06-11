# -*- coding: utf-8 -*-

codProduto1,numProduto1,valProduto1 = map(float, input().split())

codProduto2,numProduto2,valProduto2 = map(float, input().split())

valPago = ((numProduto1 * valProduto1) + (numProduto2 * valProduto2))

print("VALOR A PAGAR: R$ %0.2lf" %valPago)
