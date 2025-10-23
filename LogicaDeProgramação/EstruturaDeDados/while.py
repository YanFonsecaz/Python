n = 1
soma = 0

while n <= 10:
    soma = soma + n
    n = n + 1
    print(soma)

for index in range(1,11):
    soma = soma + index
    print(soma)

for index in range(1,11):
    soma += index
    print(soma)

soma = sum([i for i in range(1,11)])
print(soma)