import re
import funcoes
import pandas as pd
import simplexPadrao




# --- Teste ---

#tipo = funcoes.escolher_tipo("")
#funcao, variaveis, constante = funcoes.definir_funcao()
#print('resultado', funcao, variaveis, constante)
#restricoes = funcoes.coletar_restricoes(variaveis)

#print('Funcao: ',funcao,"\nvariaveis: ",variaveis)
#print(restricoes)




# Dados de exemplo (conforme seu formato)
#funcao_str = "5x1+23x2+3x3"
tipo = "Max"
variaveis = {'x1': 100.0, 'x2': 150.0}
restricoes = [
    {'expr': {'x1': 1.0}, 'operador': '<=', 'valor': 40.0},
    {'expr': {'x2': 1.0}, 'operador': '<=', 'valor': 30.0},
    {'expr': {'x1': 2.0, 'x2': 3.0}, 'operador': '<=', 'valor': 120.0}]

#Chama o simplexPadra

solucionador = simplexPadrao.SolucionadorSimplexDetalhado(tipo, variaveis, restricoes)
solucionador.resolver()


# Apresentando os resultados
#print("\nSolução Ótima Encontrada:")
#print(f"Valor de Z: {solucao['Valor_Z']:.2f}")
#
#print("\nVariáveis Básicas (valores diferentes de zero):")
#for var, valor in solucao['Variaveis_Basicas'].items():
#    print(f"{var}: {valor:.2f}")
#
#print("\nVariáveis Não Básicas (valores zero):")
#print(", ".join(solucao['Variaveis_Nao_Basicas'].keys()))
#
#print("\nTabela Final:")
#print(solucao['Tabela_Final'].to_string(index=False, float_format="%.2f"))