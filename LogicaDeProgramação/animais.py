
perguntas = [
    ['Seu animal gosta de bananas', 'macaco']
]
while True:
    print('Pense em um animal....')
    acertou = False
    for pergunta in perguntas:
        resposta = input(f'{pergunta[0]} (s/n): ')
        if resposta.lower() == 's':
            print(f'Você pensou em {pergunta[1]}!')
            acertou = True
            break
    
    if not acertou: 
        animal = input('Desisto! Qual animal você pensou? ')
        novaPergunta = input('Qual pergunta voce faria para diferenciar esse animal? ')
        perguntas.append([novaPergunta, animal])

    newresposta = input('Quer jogar novamente? (s/n): ')
    if newresposta.lower() != 's':
        print('Até a próxima!')
        break
