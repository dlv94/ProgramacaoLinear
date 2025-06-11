#1 Igualar a função para 0 (inverter os sinais)
#2 para cada restrição alterar o operador para == e adicionar uma variavel de folga
#3 Montar a tabela Algoritmo I
    # para achar a coluna b fazer o mesmo esquema de achar o operador, mas antes validar qual lado não contem x para identificar o valor
#4 Montar tabela resultado VB, VNB, Z 
#5 Identificar coluna IN (maior menor negativo)
#6 identificar a coluna OUT, menor valor positivo da divisão da celula IN com celula b da mesma lina
#7 Fazer a LP
    #Fazer uma nova tabela com linha OUT
    #Linha abaixo será a o resultado do elemento divido pela celula de cima e essa será a NLP
#
# fazer a sequencia conforme:
#    NLP
#    x(+/- Elemento)
#    VLx
#    NLx
#           SOMAR linha Elemento com VLX
#
#Não é necessário fazer isso para a linha OUT, fazer algo para identificar e pular a linha pivo
#
#Montar tabelas novamente
#Verificar se os valores da linha 1 são todos positivos
#Se sim = finalizar e informa ZMAX = R$ {Z}, sendo retornar a mesma qtd de variais sem contar as de folga, mas podendo ter os seus valores.
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#


import pandas as pd

class SolucionadorSimplexDetalhado:
    def __init__(self, tipo, funcao_obj, restricoes):
        self.tipo = tipo
        self.funcao_obj = funcao_obj
        self.restricoes = restricoes
        self.tabela = None
        self.variaveis_basicas = []
        self.variaveis_nao_basicas = []
        self.variaveis_originais = sorted(funcao_obj.keys())
        self.iteracao = 0
    
    def resolver(self):
        """Orquestra todo o processo de solução detalhada"""
        print("=== PREPARAÇÃO INICIAL ===")
        print("\n1. Transformando a função objetivo para forma padrão:")
        Z = self._processar_funcao_objetivo()
        print(f"FO {self.tipo} (Z) = {self._formatar_equacao(Z[1:], self.variaveis_originais)} → "
              f"FO {self.tipo} (Z) - {self._formatar_equacao([-x for x in Z[1:]], self.variaveis_originais)} = 0")
        
        print("\n2. Adicionando variáveis de folga às restrições:")
        restricoes_padrao, variaveis_folga, b = self._processar_restricoes()
        
        # Cria tabela mas não mostra ainda
        self.tabela = self._criar_tabela_simplex(Z, restricoes_padrao, variaveis_folga, b)
        self._identificar_variaveis()
        
        while True:
            self.iteracao += 1
            print(f"\n\n=== ALGORITMO {self.iteracao} ===\n")
            self._mostrar_tabela()
            
            print(f"\n=== SOLUÇÃO {self.iteracao} ===")
            solucao = self._obter_solucao_atual()
            if solucao['otima']:
                break
            
            # Processa iteração se não for ótima
            self._processar_iteracao()
    
    def _processar_iteracao(self):
        """Executa e mostra detalhes de uma iteração completa"""
        # Identifica variável que entra
        print("\nIDENTIFICANDO VARIÁVEL QUE ENTRA:")
        linha_Z = self.tabela.iloc[0, :-1]  # Exclui coluna 'b'
        var_entra = linha_Z[1:].idxmin()    # Exclui coluna 'Z'
        coef_entra = linha_Z[var_entra]
        print(f"Coluna pivô (IN): {var_entra} (coeficiente mais negativo na Z: {coef_entra:.2f})")
        
        # Identifica variável que sai
        print("\nIDENTIFICANDO VARIÁVEL QUE SAI:")
        coluna_pivo = self.tabela[var_entra][1:]  # Exclui linha Z
        b = self.tabela['b'][1:]
        razoes = b / coluna_pivo
        razoes_positivas = razoes[coluna_pivo > 0]
        
        if razoes_positivas.empty:
            raise ValueError("Problema ilimitado - não há razões positivas")
        
        var_sai_idx = razoes_positivas.idxmin()
        var_sai = self.variaveis_basicas[var_sai_idx - 1]  # -1 porque a linha 0 é Z
        elemento_pivo = self.tabela.at[var_sai_idx, var_entra]
        
        print("\nCálculo das razões (b/coluna pivô):")
        dados_razoes = []
        for i, (valor_b, valor_col) in enumerate(zip(b, coluna_pivo)):
            if valor_col > 0:
                dados_razoes.append([f"Linha {i+1}", f"{valor_b:.2f}/{valor_col:.2f}", f"{valor_b/valor_col:.2f}"])
        print(pd.DataFrame(dados_razoes, columns=["Linha", "Razão", "Resultado"]).to_string(index=False))
        
        print(f"\nLinha que sai (OUT): Linha {(var_sai).replace("x","").replace("F","").replace("X","")} (menor razão positiva)")
        print(f"Elemento pivô: {elemento_pivo:.2f}")# (interseção de {var_entra} e {var_sai})")
        #bkp
        #print(f"\nVariável que sai (OUT): {var_sai} (menor razão positiva)")
        #print(f"Elemento pivô: {elemento_pivo:.2f} (interseção de {var_entra} e {var_sai})")
        
        # Pivotamento
        print("\nPIVOTAMENTO:")
        print(f"1. Normalizando linha pivô (linha {var_sai_idx}):\n")
        linha_pivo_original = self.tabela.iloc[var_sai_idx].copy()
        linha_pivo_norm = linha_pivo_original / elemento_pivo
            
        # Mostra tabela com linha original e normalizada
        dados_pivo = [
            ["Original"] + linha_pivo_original.to_list(),
            [f"Normalizada /({elemento_pivo})"] + (linha_pivo_original / elemento_pivo).to_list()
        ]
        print(pd.DataFrame(dados_pivo, columns=["Tipo"] + list(self.tabela.columns)).to_string(index=False))
        
        # Normaliza a linha pivô
        linha_pivo_norm = linha_pivo_original / elemento_pivo
        self.tabela.iloc[var_sai_idx] = linha_pivo_norm
        
        print("\n2. Atualizando outras linhas:")
        dados_atualizacao = []
        for idx in range(len(self.tabela)):
            print("\n")
            if idx == var_sai_idx:
                continue
            
            coef_pivo = self.tabela.at[idx, var_entra]
            linha_original = self.tabela.iloc[idx].copy()
            elemento_mult = coef_pivo * linha_pivo_norm
            nova_linha = linha_original - elemento_mult

                    # Monta tabela detalhada para cada linha
            dados_linha = [
                ["Nova Linha Pivo"] + linha_pivo_norm.to_list(),
                [f"Elemento *({coef_pivo:.2f})"] + elemento_mult.to_list(),
                ["Velha Linha "+str(idx)] + linha_original.to_list(),
                ["Nova Linha "+str(idx)] + nova_linha.to_list()]
            
            #print(f"\nAtualizando Linha {idx}:")
            print(pd.DataFrame(
                dados_linha,
                columns=[f"Linha {idx}:"] + list(self.tabela.columns)
            ).to_string(float_format="%.2f", index=False))
            
            #dados_atualizacao.append([
            #    f"Linha {idx}",
            #    f" - ({coef_pivo:.2f} × Linha Pivô)",
            #    linha_original.to_list(),
            #    nova_linha.to_list()
            #])
            
            self.tabela.iloc[idx] = nova_linha
        
        # Mostra tabela com operações
        if dados_atualizacao:
            print(pd.DataFrame(
                dados_atualizacao,
                columns=["Linha", "Operação", "Original", "Resultado"]
            ).to_string(index=False, float_format="%.2f"))
        else:
            pass
        
        # Atualiza variáveis básicas/não-básicas
        self.variaveis_basicas[var_sai_idx - 1] = var_entra
        self.variaveis_nao_basicas.remove(var_entra)
        self.variaveis_nao_basicas.append(var_sai)
    
    def _obter_solucao_atual(self):
        """Retorna a solução atual formatada"""
        solucao = {
            'Variaveis_Basicas': {},
            'Variaveis_Nao_Basicas': [],
            'Valor_Z': self.tabela.at[0, 'b'],
            'otima': True
        }
        
        # Filtra apenas variáveis básicas relevantes (originais ou folgas)
        vars_relevantes = self.variaveis_originais + [f'XF{i+1}' for i in range(len(self.restricoes))]
        vars_basicas_filtradas = [v for v in self.variaveis_basicas if v in vars_relevantes]
        
        # Preenche variáveis básicas
        for i, var in enumerate(self.variaveis_basicas, 1):
            if var in vars_relevantes:
                solucao['Variaveis_Basicas'][var] = self.tabela.at[i, 'b']
        
        # Preenche variáveis não-básicas (todas zero)
        solucao['Variaveis_Nao_Basicas'] = [v for v in self.variaveis_nao_basicas if v in vars_relevantes]
        
        # Verifica se é ótimo
        linha_Z = self.tabela.iloc[0, 1:-1]  # Exclui Z e b
        solucao['otima'] = all(linha_Z >= 0)
        
        # Exibe a solução formatada
        print("\n")
        dados_basicas = [[var, f"=  {valor:.2f}"] for var, valor in solucao['Variaveis_Basicas'].items()]
        print(pd.DataFrame(dados_basicas, columns=["Variáveis", "Básicas:"]).to_string(index=False))
        #BKP
        # print(pd.DataFrame(dados_basicas, columns=["Variável", "Valor"]).to_string(index=False))
        
        print("\nVariáveis Não Básicas:")
        print(", ".join(solucao['Variaveis_Nao_Basicas']) + " = 0.00")
        
        print(f"\nValor de Z: {solucao['Valor_Z']:.2f}")
        
        if solucao['otima']:
            print("\n→ Solução ótima encontrada!")
        else:
            print("\n→ Solução não ótima, continuando iterações...")
        
        return solucao
    
    def _mostrar_tabela(self):
        """Mostra a tabela atual formatada"""
        #print("\nTabela Atual:")
        print(self.tabela.to_string(float_format="%.2f", index=False))
    
    def _processar_funcao_objetivo(self):
        """Transforma a função objetivo para forma padrão"""
        coef_Z = [1.0] + [-self.funcao_obj[var] for var in self.variaveis_originais]
        return coef_Z
    
    def _processar_restricoes(self):
        """Processa as restrições para formato padrão"""
        restricoes_padrao = []
        variaveis_folga = []
        b = []
        
        for i, restricao in enumerate(self.restricoes, 1):
            coef_restricao = [restricao['expr'].get(var, 0.0) for var in self.variaveis_originais]
            folga = f'XF{i}'
            
            print(f"Restrição {i}: {self._formatar_equacao(coef_restricao, self.variaveis_originais)} "
                  f"{restricao['operador']} {restricao['valor']:.2f} → "
                  f"{self._formatar_equacao(coef_restricao, self.variaveis_originais)} + {folga} = {restricao['valor']:.2f}")
            
            restricoes_padrao.append(coef_restricao)
            variaveis_folga.append(folga)
            b.append(restricao['valor'])
        
        return restricoes_padrao, variaveis_folga, b
    
    def _criar_tabela_simplex(self, Z, restricoes_padrao, variaveis_folga, b):
        """Monta a tabela simplex inicial"""
        colunas = ['Z'] + self.variaveis_originais + variaveis_folga + ['b']
        
        # Linha Z
        linha_Z = Z + [0.0] * len(variaveis_folga) + [0.0]
        
        # Linhas de restrições
        linhas = [linha_Z]
        for i, (restricao, valor_b) in enumerate(zip(restricoes_padrao, b)):
            linha = [0.0] + restricao
            linha.extend(1.0 if j == i else 0.0 for j in range(len(variaveis_folga)))
            linha.append(valor_b)
            linhas.append(linha)
        
        return pd.DataFrame(linhas, columns=colunas)
    
    def _identificar_variaveis(self):
        """Identifica variáveis básicas e não básicas iniciais"""
        self.variaveis_basicas = [f'XF{i+1}' for i in range(len(self.restricoes))]
        self.variaveis_nao_basicas = self.variaveis_originais.copy()
    
    def _formatar_equacao(self, coeficientes, variaveis):
        """Formata uma equação para exibição"""
        termos = []
        for coef, var in zip(coeficientes, variaveis):
            if coef != 0:
                termos.append(f"{coef:.2f}{var}")
        return " + ".join(termos)

