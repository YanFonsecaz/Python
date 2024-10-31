import pandas
v1=v2=v3=v4=i = 0
tabela = pandas.DataFrame({"coluna1":[3],"coluna2":[2,3,6]})
for i in range(6):
    v1=input("Escreva um valor")

tabela = pandas.DataFrame({"coluna1":[v1,4,5],"coluna2":[2,3,6]})
print (tabela)
