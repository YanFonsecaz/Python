print('Ola, eu sou assistente virtual!')

comando = input('Qual é o seu comando? ')

match comando:
    case 'oi' | 'olá' | 'oi assistente':
        print('Olá! Como posso ajudar?')
    case 'tchau' | 'tchau assistente':
        print('Até a próxima!')
    case _:
        print('Comando inválido!')
