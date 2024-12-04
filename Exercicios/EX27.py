vetor = []
vetorNomes = []
for i in range(3):
    nomes = input(f'Escreva o nomes do {i} produto \n')
    vetorNomes.append(nomes)
for i in range(3):
    valores=float(input(f'Escreva o {i}\n'))
    vetor.append(valores)

menorValor = min(vetor)
nomeRef = vetorNomes[vetor.index(min(vetor))]
print(f'{nomeRef} {menorValor:.2f}')
