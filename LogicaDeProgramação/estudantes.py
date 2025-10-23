estudantes = {
    1: {'nome': 'Joana', 'idade': 45, 'curso': 'Computação'},
    2: {'nome': 'Maria', 'idade': 70, 'curso': 'Matemática'},
    3: {'nome': 'Pedro', 'idade': 12, 'curso': 'Computação'}
}

cursos = {'Computação', 'Matemática', 'Física'}

estudantes_cursos = {
    'Computação': {1,3},
    'Matematica': { 2 }
}

def adicionarEstudante(matricula, nome, idade, curso):
    pessoal = {
        'nome': nome,
        'idade': idade,
        'curso': curso
    }
    estudantes[matricula] = pessoal
    if curso not in cursos:
        estudantes_cursos[curso] = set()
    estudantes_cursos[curso].add(matricula)

print(estudantes_cursos)
adicionarEstudante(4, 'Ana', 20, 'Computação')
print(estudantes_cursos)
adicionarEstudante(5, 'Paulo', 30, 'Matematica')
print(estudantes_cursos)


