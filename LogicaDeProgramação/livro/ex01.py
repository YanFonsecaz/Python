#Escreva uma função chamada right_justify, que receba uma string chamada s como parametro e exiba a string com espaços sufiencientes a sua frente para que a última letra da string esteja na coluna 70 da tela.
def right_justify(s):
    print(' ' * (70 - len(s)) + s)

right_justify('monty')

def print_spam():
    print('spam')

def do_four(f):
    f()
    f()
    f()
    f()

do_four(print_spam)


def print_grade():
    print('+' + '-' * 4 + '+' + '-' * 4 + '+')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('+' + '-' * 4 + '+' + '-' * 4 + '+')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('|' + ' ' * 4 + '|' + ' ' * 4 + '|')
    print('+' + '-' * 4 + '+' + '-' * 4 + '+')

print_grade()

