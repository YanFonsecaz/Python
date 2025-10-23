"""
EXERCÍCIOS INTERMEDIÁRIOS - FUNÇÕES EM PYTHON
==============================================

Estes exercícios focam em funções com lógica mais complexa,
incluindo validações, manipulação de strings e listas.
"""

# ========================================
# EXERCÍCIO 1: VALIDAÇÃO DE DADOS
# ========================================

def validar_email(email):
    """
    Função que valida se um email tem formato básico correto.
    Deve conter @ e pelo menos um ponto após o @
    
    Parâmetros:
        email (str): Email a ser validado
    
    Retorna:
        bool: True se válido, False caso contrário
    
    Exemplo:
        validar_email("user@example.com") -> True
        validar_email("invalid-email") -> False
    """
    # SEU CÓDIGO AQUI
    pass

def validar_cpf_basico(cpf):
    """
    Função que valida formato básico de CPF (apenas dígitos e tamanho).
    CPF deve ter exatamente 11 dígitos numéricos.
    
    Parâmetros:
        cpf (str): CPF a ser validado
    
    Retorna:
        bool: True se formato válido, False caso contrário
    
    Exemplo:
        validar_cpf_basico("12345678901") -> True
        validar_cpf_basico("123.456.789-01") -> False (tem pontos)
    """
    # SEU CÓDIGO AQUI
    pass

def validar_senha_forte(senha):
    """
    Função que valida se uma senha é forte.
    Critérios: pelo menos 8 caracteres, 1 maiúscula, 1 minúscula, 1 número
    
    Parâmetros:
        senha (str): Senha a ser validada
    
    Retorna:
        bool: True se forte, False caso contrário
    
    Exemplo:
        validar_senha_forte("MinhaSenh@123") -> True
        validar_senha_forte("123456") -> False
    """
    # SEU CÓDIGO AQUI
    pass

# ========================================
# EXERCÍCIO 2: MANIPULAÇÃO DE STRINGS
# ========================================

def contar_palavras(texto):
    """
    Função que conta o número de palavras em um texto.
    
    Parâmetros:
        texto (str): Texto a ser analisado
    
    Retorna:
        int: Número de palavras
    
    Exemplo:
        contar_palavras("Python é uma linguagem incrível") -> 5
    """
    # SEU CÓDIGO AQUI
    pass

def inverter_palavras(frase):
    """
    Função que inverte a ordem das palavras em uma frase.
    
    Parâmetros:
        frase (str): Frase original
    
    Retorna:
        str: Frase com palavras invertidas
    
    Exemplo:
        inverter_palavras("Python é incrível") -> "incrível é Python"
    """
    # SEU CÓDIGO AQUI
    pass

def capitalizar_palavras(texto):
    """
    Função que capitaliza a primeira letra de cada palavra.
    
    Parâmetros:
        texto (str): Texto original
    
    Retorna:
        str: Texto com palavras capitalizadas
    
    Exemplo:
        capitalizar_palavras("python é incrível") -> "Python É Incrível"
    """
    # SEU CÓDIGO AQUI
    pass

def remover_espacos_extras(texto):
    """
    Função que remove espaços extras entre palavras.
    
    Parâmetros:
        texto (str): Texto com possíveis espaços extras
    
    Retorna:
        str: Texto com espaços normalizados
    
    Exemplo:
        remover_espacos_extras("Python    é     incrível") -> "Python é incrível"
    """
    # SEU CÓDIGO AQUI
    pass

# ========================================
# EXERCÍCIO 3: MANIPULAÇÃO DE LISTAS
# ========================================

def encontrar_maior_menor(numeros):
    """
    Função que encontra o maior e menor número em uma lista.
    
    Parâmetros:
        numeros (list): Lista de números
    
    Retorna:
        tuple: (maior, menor)
    
    Exemplo:
        encontrar_maior_menor([1, 5, 3, 9, 2]) -> (9, 1)
    """
    # SEU CÓDIGO AQUI
    pass

def remover_duplicatas(lista):
    """
    Função que remove elementos duplicados de uma lista mantendo a ordem.
    
    Parâmetros:
        lista (list): Lista original
    
    Retorna:
        list: Lista sem duplicatas
    
    Exemplo:
        remover_duplicatas([1, 2, 2, 3, 1, 4]) -> [1, 2, 3, 4]
    """
    # SEU CÓDIGO AQUI
    pass

def filtrar_pares(numeros):
    """
    Função que filtra apenas os números pares de uma lista.
    
    Parâmetros:
        numeros (list): Lista de números
    
    Retorna:
        list: Lista apenas com números pares
    
    Exemplo:
        filtrar_pares([1, 2, 3, 4, 5, 6]) -> [2, 4, 6]
    """
    # SEU CÓDIGO AQUI
    pass

def agrupar_por_paridade(numeros):
    """
    Função que agrupa números em pares e ímpares.
    
    Parâmetros:
        numeros (list): Lista de números
    
    Retorna:
        dict: {"pares": [...], "impares": [...]}
    
    Exemplo:
        agrupar_por_paridade([1, 2, 3, 4, 5]) -> {"pares": [2, 4], "impares": [1, 3, 5]}
    """
    # SEU CÓDIGO AQUI
    pass

# ========================================
# EXERCÍCIO 4: FUNÇÕES COM MÚLTIPLOS PARÂMETROS
# ========================================

def calcular_estatisticas(numeros):
    """
    Função que calcula estatísticas básicas de uma lista.
    
    Parâmetros:
        numeros (list): Lista de números
    
    Retorna:
        dict: {"media": float, "mediana": float, "soma": int, "count": int}
    
    Exemplo:
        calcular_estatisticas([1, 2, 3, 4, 5]) -> 
        {"media": 3.0, "mediana": 3.0, "soma": 15, "count": 5}
    """
    # SEU CÓDIGO AQUI
    pass

def buscar_em_lista(lista, item, retornar_indices=False):
    """
    Função que busca um item em uma lista.
    
    Parâmetros:
        lista (list): Lista onde buscar
        item: Item a ser buscado
        retornar_indices (bool): Se True, retorna índices; se False, retorna bool
    
    Retorna:
        bool ou list: Dependendo do parâmetro retornar_indices
    
    Exemplo:
        buscar_em_lista([1, 2, 3, 2], 2) -> True
        buscar_em_lista([1, 2, 3, 2], 2, True) -> [1, 3]
    """
    # SEU CÓDIGO AQUI
    pass

def formatar_nome_completo(nome, sobrenome, formato="normal"):
    """
    Função que formata nome completo de diferentes maneiras.
    
    Parâmetros:
        nome (str): Primeiro nome
        sobrenome (str): Sobrenome
        formato (str): "normal", "sobrenome_primeiro", "iniciais"
    
    Retorna:
        str: Nome formatado
    
    Exemplo:
        formatar_nome_completo("João", "Silva") -> "João Silva"
        formatar_nome_completo("João", "Silva", "sobrenome_primeiro") -> "Silva, João"
        formatar_nome_completo("João", "Silva", "iniciais") -> "J. S."
    """
    # SEU CÓDIGO AQUI
    pass

# ========================================
# EXERCÍCIO 5: FUNÇÕES COM LÓGICA CONDICIONAL COMPLEXA
# ========================================

def classificar_idade(idade):
    """
    Função que classifica uma pessoa por faixa etária.
    
    Parâmetros:
        idade (int): Idade da pessoa
    
    Retorna:
        str: Classificação ("bebê", "criança", "adolescente", "adulto", "idoso")
    
    Faixas:
        0-2: bebê
        3-12: criança
        13-17: adolescente
        18-59: adulto
        60+: idoso
    
    Exemplo:
        classificar_idade(25) -> "adulto"
    """
    # SEU CÓDIGO AQUI
    pass

def calcular_desconto(valor, tipo_cliente, cupom=None):
    """
    Função que calcula desconto baseado no tipo de cliente e cupom.
    
    Parâmetros:
        valor (float): Valor original
        tipo_cliente (str): "bronze", "prata", "ouro"
        cupom (str): Código do cupom (opcional)
    
    Retorna:
        dict: {"valor_original": float, "desconto": float, "valor_final": float}
    
    Descontos:
        bronze: 5%
        prata: 10%
        ouro: 15%
        cupom "SAVE10": +10%
        cupom "SAVE20": +20%
    
    Exemplo:
        calcular_desconto(100, "prata", "SAVE10") -> 
        {"valor_original": 100, "desconto": 20.0, "valor_final": 80.0}
    """
    # SEU CÓDIGO AQUI
    pass

def verificar_triangulo(a, b, c):
    """
    Função que verifica se três lados podem formar um triângulo e seu tipo.
    
    Parâmetros:
        a, b, c (float): Lados do triângulo
    
    Retorna:
        dict: {"eh_triangulo": bool, "tipo": str}
    
    Tipos: "equilátero", "isósceles", "escaleno"
    
    Exemplo:
        verificar_triangulo(3, 4, 5) -> {"eh_triangulo": True, "tipo": "escaleno"}
    """
    # SEU CÓDIGO AQUI
    pass

# ========================================
# DESAFIO INTERMEDIÁRIO
# ========================================

def analisador_texto_completo(texto):
    """
    DESAFIO: Função que faz análise completa de um texto.
    
    Parâmetros:
        texto (str): Texto a ser analisado
    
    Retorna:
        dict: Análise completa com:
        - total_caracteres
        - total_palavras
        - total_frases (considere . ! ?)
        - palavra_mais_comum
        - palavras_unicas
        - media_caracteres_por_palavra
    
    Exemplo:
        analisador_texto_completo("Python é incrível! Python é poderoso.")
        -> {
            "total_caracteres": 38,
            "total_palavras": 6,
            "total_frases": 2,
            "palavra_mais_comum": "Python",
            "palavras_unicas": ["é", "incrível", "poderoso"],
            "media_caracteres_por_palavra": 6.33
        }
    """
    # SEU CÓDIGO AQUI
    pass

# ========================================
# ÁREA DE TESTES
# ========================================

if __name__ == "__main__":
    print("=== TESTANDO EXERCÍCIOS INTERMEDIÁRIOS ===\n")
    
    # Teste suas funções aqui
    print("1. Testando validação de email:")
    # print(validar_email("test@example.com"))
    
    print("\n2. Testando contagem de palavras:")
    # print(contar_palavras("Python é uma linguagem incrível"))
    
    print("\n3. Testando remoção de duplicatas:")
    # print(remover_duplicatas([1, 2, 2, 3, 1, 4]))
    
    print("\n4. Testando classificação de idade:")
    # print(classificar_idade(25))
    
    print("\n5. Testando analisador de texto:")
    # print(analisador_texto_completo("Python é incrível! Python é poderoso."))
    
    print("\n" + "="*50)
    print("Complete as funções e descomente os testes!")
    print("="*50)