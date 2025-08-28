import pandas as pd

lista = pd.read_csv('databases/marcas_polos.csv', sep=',')

lista_marca = lista['MARCA'].unique().tolist()
lista_polo = lista['CAMPUS'].unique().tolist()

#printa as listas
print("Lista de Marcas:")
print(lista_marca)
print("\nLista de Polos:")
print(lista_polo)