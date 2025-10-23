def somar(a,b):
    return a + b
print(somar(5,3))

def subtrair(a, b):
    return a - b

print(subtrair(10,4))

def multiplicar(a,b):
    return a * b
print(multiplicar(5,3))

def dividir(a,b):
    if b == 0:
        return 'Erro: Divisão por zero!'
    else:
        return a / b

print(dividir(10,2))
print(dividir(10,0))
