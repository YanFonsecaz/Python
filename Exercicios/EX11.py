print('Vamos descobrir o resto da divisão de dois valores\n')

v1= int(input('Digite o 1 valor\n'))
v2= int(input('Digite o 2 valor\n'))
if v2==0:
    print('O denominador deve ser maior que 0')
else:
    div = v1%v2
    print(f'A subtração dos valores é {div:.2f}')