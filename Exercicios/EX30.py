n1 = int(input('Escreva o primeiro valor\n'))
n2 = int(input('Escreva o segundo valor\n'))
n3 = int(input('Escreva o terceiro valor\n'))

if n1 >= n2 and n2>=n3 :
    print(f'{n1}')
    print(f'{n2}')
    print(f'{n3}')
elif n2 >= n1 and n1>=n3 :
    print(f'{n2}')
    print(f'{n1}')
    print(f'{n3}')
elif n3 >= n1 and n2>=n1:
    print(f'{n3}')
    print(f'{n2}')
    print(f'{n1}')