operacao= input('Digite a operacao que voce quer fazer o calculo "+" "-" "*" "/" \n')
v1=float(input('Digite o primeiro valor\n'))
v2=float(input('Digite o segundo valor\n'))
result = 0.0

match operacao: 
    case '+':
        result = v1+v2
        print(f'O valor da soma é {result}')
    case '-':
        result = v1-v2
        print(f'O valor da subtração {result}')
    case '*':
        result = v1*v2
        print(f'O valor da Multiplicação é {result}')
    case '/':
        if v2 == 0:
            print('O denominador não pode ser 0')
        else:
            result = v1/v2
            print(f'O valor da Divisão é {result:.2f}')
    case _:
        print('Essa operação não é valida')