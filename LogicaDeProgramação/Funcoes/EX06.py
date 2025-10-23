print("Calculadora")

print("1. Soma")
print("2. Subtração")
print("3. Multiplicação")
print("4. Divisão")

match int(input("Escolha uma operação: ")):
    case 1:
        print("Soma")
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        print(f"{num1} + {num2} = {num1 + num2}")
    case 2:
        print("Subtração")
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        print(f"{num1} - {num2} = {num1 - num2}")
    case 3:
        print("Multiplicação")
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        print(f"{num1} * {num2} = {num1 * num2}")
    case 4:
        print("Divisão")
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        if num2 != 0:
            print(f"{num1} / {num2} = {num1 / num2}")
        else:
            print("Erro: Divisão por zero")
    case _:
        print("Operação inválida")