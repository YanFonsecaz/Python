quantidade=[]
for i in range(3):
    valores=float(input(f'Qual valor do {i+1} carro\n'))
    quantidade.append(valores)
    
maiorValor= max(quantidade)
menorValor = min(quantidade)

print(f'O maior valor é {maiorValor:.2f}\n')
print(f'O menor valor é {menorValor:.2f}\n')