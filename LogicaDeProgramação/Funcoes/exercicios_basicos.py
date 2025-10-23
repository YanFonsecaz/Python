"""
EXERCÍCIOS BÁSICOS DE FUNÇÕES EM PYTHON
=======================================

Instruções:
1. Leia cada exercício com atenção
2. Implemente a função solicitada
3. Teste sua função com os exemplos fornecidos
4. Execute o arquivo para verificar se está funcionando

Dicas:
- Use nomes descritivos para suas funções
- Adicione comentários explicando a lógica
- Teste com diferentes valores
"""

# =============================================================================
# EXERCÍCIO 1: SAUDAÇÃO PERSONALIZADA
# =============================================================================
def saudar(nome):
    """
    Crie uma função que receba um nome e retorne uma saudação personalizada.
    
    Exemplo:
    saudar("Ana") → "Olá, Ana! Bem-vinda!"
    """
    # TODO: Implemente aqui
    pass

# Teste do exercício 1
print("=== EXERCÍCIO 1: SAUDAÇÃO ===")
# print(saudar("Ana"))
# print(saudar("João"))


# =============================================================================
# EXERCÍCIO 2: CALCULADORA BÁSICA
# =============================================================================
def somar(a, b):
    """
    Crie uma função que some dois números.
    
    Exemplo:
    somar(5, 3) → 8
    """
    # TODO: Implemente aqui
    pass

def subtrair(a, b):
    """
    Crie uma função que subtraia dois números.
    
    Exemplo:
    subtrair(10, 4) → 6
    """
    # TODO: Implemente aqui
    pass

def multiplicar(a, b):
    """
    Crie uma função que multiplique dois números.
    
    Exemplo:
    multiplicar(6, 7) → 42
    """
    # TODO: Implemente aqui
    pass

def dividir(a, b):
    """
    Crie uma função que divida dois números.
    Cuidado com divisão por zero!
    
    Exemplo:
    dividir(15, 3) → 5.0
    dividir(10, 0) → "Erro: Divisão por zero!"
    """
    # TODO: Implemente aqui
    pass

# Teste do exercício 2
print("\n=== EXERCÍCIO 2: CALCULADORA ===")
# print(f"5 + 3 = {somar(5, 3)}")
# print(f"10 - 4 = {subtrair(10, 4)}")
# print(f"6 × 7 = {multiplicar(6, 7)}")
# print(f"15 ÷ 3 = {dividir(15, 3)}")
# print(f"10 ÷ 0 = {dividir(10, 0)}")


# =============================================================================
# EXERCÍCIO 3: CONVERSÕES
# =============================================================================
def celsius_para_fahrenheit(celsius):
    """
    Converte temperatura de Celsius para Fahrenheit.
    Fórmula: F = (C × 9/5) + 32
    
    Exemplo:
    celsius_para_fahrenheit(0) → 32.0
    celsius_para_fahrenheit(100) → 212.0
    """
    # TODO: Implemente aqui
    pass

def metros_para_centimetros(metros):
    """
    Converte metros para centímetros.
    
    Exemplo:
    metros_para_centimetros(1.5) → 150.0
    """
    # TODO: Implemente aqui
    pass

def segundos_para_minutos(segundos):
    """
    Converte segundos para minutos (com decimais).
    
    Exemplo:
    segundos_para_minutos(120) → 2.0
    segundos_para_minutos(90) → 1.5
    """
    # TODO: Implemente aqui
    pass

# Teste do exercício 3
print("\n=== EXERCÍCIO 3: CONVERSÕES ===")
# print(f"0°C = {celsius_para_fahrenheit(0)}°F")
# print(f"100°C = {celsius_para_fahrenheit(100)}°F")
# print(f"1.5m = {metros_para_centimetros(1.5)}cm")
# print(f"120s = {segundos_para_minutos(120)}min")


# =============================================================================
# EXERCÍCIO 4: ÁREA DE FORMAS GEOMÉTRICAS
# =============================================================================
def area_retangulo(largura, altura):
    """
    Calcula a área de um retângulo.
    Fórmula: área = largura × altura
    
    Exemplo:
    area_retangulo(5, 3) → 15
    """
    # TODO: Implemente aqui
    pass

def area_circulo(raio):
    """
    Calcula a área de um círculo.
    Fórmula: área = π × raio²
    Use 3.14159 para π
    
    Exemplo:
    area_circulo(2) → 12.56636
    """
    # TODO: Implemente aqui
    pass

def area_triangulo(base, altura):
    """
    Calcula a área de um triângulo.
    Fórmula: área = (base × altura) / 2
    
    Exemplo:
    area_triangulo(6, 4) → 12.0
    """
    # TODO: Implemente aqui
    pass

# Teste do exercício 4
print("\n=== EXERCÍCIO 4: ÁREAS ===")
# print(f"Retângulo 5×3 = {area_retangulo(5, 3)}")
# print(f"Círculo raio 2 = {area_circulo(2)}")
# print(f"Triângulo base 6, altura 4 = {area_triangulo(6, 4)}")


# =============================================================================
# EXERCÍCIO 5: FUNÇÕES COM CONDICIONAIS
# =============================================================================
def eh_par(numero):
    """
    Verifica se um número é par.
    
    Exemplo:
    eh_par(4) → True
    eh_par(7) → False
    """
    # TODO: Implemente aqui
    pass

def maior_de_dois(a, b):
    """
    Retorna o maior entre dois números.
    
    Exemplo:
    maior_de_dois(10, 5) → 10
    maior_de_dois(3, 8) → 8
    """
    # TODO: Implemente aqui
    pass

def classificar_idade(idade):
    """
    Classifica uma pessoa pela idade:
    - 0-12: "Criança"
    - 13-17: "Adolescente"  
    - 18-59: "Adulto"
    - 60+: "Idoso"
    
    Exemplo:
    classificar_idade(10) → "Criança"
    classificar_idade(25) → "Adulto"
    """
    # TODO: Implemente aqui
    pass

# Teste do exercício 5
print("\n=== EXERCÍCIO 5: CONDICIONAIS ===")
# print(f"4 é par? {eh_par(4)}")
# print(f"7 é par? {eh_par(7)}")
# print(f"Maior entre 10 e 5: {maior_de_dois(10, 5)}")
# print(f"Idade 10: {classificar_idade(10)}")
# print(f"Idade 25: {classificar_idade(25)}")


# =============================================================================
# DESAFIO EXTRA: CALCULADORA COMPLETA
# =============================================================================
def calculadora(operacao, a, b):
    """
    DESAFIO: Crie uma calculadora que aceite uma operação como string.
    
    Operações suportadas: "+", "-", "*", "/"
    
    Exemplo:
    calculadora("+", 5, 3) → 8
    calculadora("*", 4, 6) → 24
    calculadora("/", 10, 0) → "Erro: Divisão por zero!"
    calculadora("%", 5, 3) → "Operação inválida!"
    """
    # TODO: Implemente aqui (use as funções que você criou acima!)
    pass

# Teste do desafio
print("\n=== DESAFIO: CALCULADORA COMPLETA ===")
# print(f"5 + 3 = {calculadora('+', 5, 3)}")
# print(f"4 × 6 = {calculadora('*', 4, 6)}")
# print(f"10 ÷ 0 = {calculadora('/', 10, 0)}")
# print(f"5 % 3 = {calculadora('%', 5, 3)}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("EXERCÍCIOS BÁSICOS DE FUNÇÕES")
    print("="*50)
    print("📝 Implemente as funções marcadas com TODO")
    print("🧪 Descomente os testes para verificar suas soluções")
    print("🚀 Execute: python3 exercicios_basicos.py")
    print("="*50)