qtd_seguranca = 5
sal_seguranca = 3000
qtd_docente = 16
sal_docente = 6000
qtd_diretoria = 1
sal_diretoria = 12500
total_empregados = qtd_seguranca + qtd_docente + qtd_diretoria
print(total_empregados)
diferenca = sal_diretoria - sal_seguranca
print(diferenca)
media = (qtd_seguranca*sal_seguranca + qtd_diretoria * sal_diretoria + qtd_docente * sal_docente) / total_empregados  
print(media)