# %%
import pandas as pd

notas = {
    'nota': [7,8,5,9,10,6,8,7,9]
}

# %%
df_notas = pd.DataFrame.from_dict(notas)


# %%
df_notas
# %%
df_notas['nota'].mean()

# %%
df_notas['nota'].median()
# %%
df_notas['nota'].mode()
# %%
df_notas.nota.max() - df_notas.nota.min()
# %%
df_notas['nota'].var()
# %%
df_notas['nota'].std()

# %%
## Temperatura
# %%
temperatura = {
    'temperatura': [22,24,19,23,25,21,20]
}
# %%
df_temperatura = pd.DataFrame.from_dict(temperatura)
# %%
df_temperatura
# %%
df_temperatura['temperatura'].mean()
# %%
df_temperatura['temperatura'].median()
# %%
amplitude = df_temperatura['temperatura'].max() - df_temperatura['temperatura'].min()
# %%
amplitude

# %%
df_temperatura['temperatura'].std()

# %%
conjuntos = {
    'conjuntoA': [100, 110, 95, 105, 100],
    'conjuntoB': [80, 120, 90, 130, 110]
}
# %%
df_conjuntos = pd.DataFrame.from_dict(conjuntos)
# %%
df_conjuntos
# %%
df_conjuntos['conjuntoA'].mean()
# %%
df_conjuntos['conjuntoB'].mean()

# %%
df_conjuntos['conjuntoA'].median()
# %%
df_conjuntos['conjuntoB'].median()
# %%
df_conjuntos['conjuntoA'].var()
# %%
df_conjuntos['conjuntoB'].var()

# %%
df_conjuntos['conjuntoA'].std()
# %%
df_conjuntos['conjuntoB'].std()
# %%
if df_conjuntos['conjuntoA'].std() > df_conjuntos['conjuntoB'].std():
    print('O conjunto A possui uma dispersão maior')
else:
    print('O conjunto B possui uma dispersão maior')
# %%
