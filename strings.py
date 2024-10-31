s1 = 'Alura'
s2 = "Alura"
print(type(s1),type(s2))

texto = ' Geovana Alessandra dias Sanyos '
number = 6

print(texto.upper())
print(texto.lower())
print(texto.strip())
print(texto.replace('y','t'))
texto = texto.strip().replace('y','t').upper()
print(texto)