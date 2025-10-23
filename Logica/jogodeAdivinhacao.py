perguntas = [['Gosta de banana','Macaco']]

print('Pense em um animal')

for pergunta in perguntas:
    resposta = input(f'Seu animal gosta de {pergunta[0]} ? (s/n)')
    if resposta == 's':
        print(f'é um {pergunta[1]}')
    else:
        print('Não consegui adivinha')