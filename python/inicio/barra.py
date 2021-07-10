'''
Programa que mostra uma barra de processamento
'''
from tqdm import tqdm #Biblioteca de progresso que, mostra de forma iterativa uma barra de progresso, com um tempo estimado para a conclusao do processo.

if __name__ == '__main__':
    numeros = range(int(10e7))
    for i in tqdm (numeros, colour='green', desc="processando"):
      pass
