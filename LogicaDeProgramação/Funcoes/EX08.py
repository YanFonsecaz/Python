def contador_palavras(texto):
    
    palavras=texto.split()
    return len(palavras)
print(contador_palavras("Python é uma linguagem incrível"))

def inverter_palavras(frase):
    invertido = " ".join(frase.split()[::-1])
    return invertido
print(inverter_palavras("Python é incrível"))

def filter_pares(numeros):
    pares = [num for num in numeros if num % 2 == 0]
    return pares
print(filter_pares([1, 2, 3, 4, 5, 6]))

def encontrar_maior_menor(numeros):
    maior_menor = (max(numeros), min(numeros))
    return maior_menor
print(encontrar_maior_menor([1,5,3,9,2]))

def remover_duplicatas(lista):
    sem_duplicatas = list(set(lista))
    return sem_duplicatas
print(remover_duplicatas([1, 2, 2, 3, 1, 4,4,5]))

def agrupar_por_paridade(numeros):
    agrupar = {
        "pares":[],
        "impar":[]
    }
    for num in numeros:
        if num % 2 == 0:
            agrupar["pares"].append(num)
        else:
            agrupar["impar"].append(num)
    return agrupar

print(agrupar_por_paridade([1, 2, 3, 4, 5, 6]))

def calcular_estatisticas(numeros):
    retorno = {
        "media": float(sum(numeros)) / len(numeros),
        "mediana": sorted(numeros)[len(numeros) // 2],
        "soma": sum(numeros),
        "count": len(numeros)
    }

def buscar_em_lista(lista,item, retorno_indices=False):

    if retorno_indices:
        return [index for index in range(len(lista)) if lista[index] == item]
    else:
        return item in lista

print(buscar_em_lista([1, 2, 3, 2], 2))
print(buscar_em_lista([1, 2, 3, 2], 2, True))