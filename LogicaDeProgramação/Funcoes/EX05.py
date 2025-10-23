def eh_par(numero):
    if numero % 2 == 0:
        return "Valor é par"
    else:
        return "Valor é ímpar"
print(eh_par(4))
print(eh_par(7))

def maio_de_dois(a,b):
    if a > b:
        return a
    else:
        return b
print(maio_de_dois(10, 5))
print(maio_de_dois(3, 8))

def classificar_idade(idade):
    if idade <= 12:
        return "Criança"
    elif idade <= 17:
        return "Adolescente"
    elif idade <= 59:
        return "Adulto"
    else:
        return "Idoso"
print(classificar_idade(10))
print(classificar_idade(25))
print(classificar_idade(65))
