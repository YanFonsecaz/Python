def validar_email(email):
    if "@" in email:
        return True
    else:
        return False
print(validar_email("test@example.com"))
print(validar_email("invalid-email"))

def validar_cpf_basico(cpf):
    if len(cpf) == 11 and cpf.isdigit():
        return True
    else:
        return False
print(validar_cpf_basico("12345678901"))
print(validar_cpf_basico("123.456.789-01"))

def validar_senha_forte(senha):
    if len(senha) >= 8 and any(c.isupper() for c in senha) and any(c.islower() for c in senha) and any(c.isdigit() for c in senha):
        return True
    else:
        return False
print(validar_senha_forte("MinhaSenh@123"))
print(validar_senha_forte("123456"))

