produtos = []

for i in range(3):
    nome = input(f'Escreva o nome do produto {i + 1}: ')
    valor = float(input(f'Digite o valor do produto {i + 1}: '))
    produtos.append((nome, valor))
produto_mais_barato = min(produtos, key=lambda x: x[1])
print(f'O produto mais barato é {produto_mais_barato[0]}, custando R$ {produto_mais_barato[1]:.2f}')
