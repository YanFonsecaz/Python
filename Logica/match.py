print('Ola eu sou sua assistente, virtual')

comando = input('Digite um comando: ')

match comando:
    case 'oi':
        print('Como vai você?')
    case 'clima':
        print('Quente')
    case _:
        print('Valor invalido')