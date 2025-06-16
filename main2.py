import re
import funcoes
import pandas as pd
import simplexPadrao
import simplexEspecial




# --- Teste ---

tipo = funcoes.escolher_tipo("")
sucesso_inicio, funcao, variaveis, constante = funcoes.definir_funcao()
print('resultado', funcao, variaveis, constante)
sucesso_restricao, restricoes = funcoes.coletar_restricoes(variaveis)
print('Funcao: ',funcao,"\nvariaveis: ",variaveis)
print(restricoes)
print("tipos:", funcoes.classificar_problema(variaveis,restricoes))


# Dados de exemplo (conforme seu formato)
#funcao_str = "5x1+23x2+3x3"
#tipo = "Max"
#variaveis = {'x1': 15.0,'x2':10,'x3':8}
#restricoes = [
#    {'expr': {'x1': 1.0,'x2':2,'x3':-1.0}, 'operador': '<=', 'valor': 200.0},
#    {'expr': {'x1': 2.0,'x2':2,'x3':1.0}, 'operador': '>=', 'valor': 400.0},
#    {'expr': {'x1': 1.0, 'x2': 3.0,'x3':2}, 'operador': '==', 'valor': 840.0}]
###Chama o simplexPadra
#print("tipos:", funcoes.classificar_problema(variaveis,restricoes))
#solucionador = simplexEspecial.SolucionadorSimplexBigM(tipo, variaveis, restricoes)
#solucionador.resolver()


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