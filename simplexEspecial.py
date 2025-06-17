import pandas as pd
import sys


class SolucionadorSimplexBigM:
    def __init__(self, tipo, funcao_obj, restricoes):
        self.tipo = tipo.upper() 
        self.funcao_obj = funcao_obj
        self.restricoes = restricoes
        self.tabela = None
        self.variaveis_basicas = []
        self.variaveis_nao_basicas = []
        self.variaveis_artificiais = []
        self.variaveis_originais = sorted(funcao_obj.keys())
        self.M = 10**6  # Valor do Big M
        self.iteracao = 0

    def resolver(self):
        """Orquestra todo o processo de solução com nova ordem de exibição"""
        print("=== PREPARAÇÃO INICIAL ===")
        
        # 1. Primeiro mostra as restrições
        restricoes_padrao, variaveis_folga, variaveis_artificiais, b = self._processar_restricoes()
        
        # 2. Depois mostra a função objetivo
        self._mostrar_funcao_objetivo(variaveis_artificiais)
        
        # 3. Cria a tabela simplex
        self.tabela = self._criar_tabela_simplex(restricoes_padrao, variaveis_folga, variaveis_artificiais, b)
        #self._identificar_variaveis()
        
        # Continuação do algoritmo...
        contador = 0
        while True and contador < 100:
            self.iteracao += 1
            print(f"\n\n=== ALGORITMO {self.iteracao} ===\n")
            self._mostrar_tabela()
            
            solucao = self._obter_solucao_atual()
            if solucao['otima']:
                break
                
            self._processar_iteracao()
            contador += 1
            sys.stderr.write(f"Iteração: {contador}\n")


    def _mostrar_funcao_objetivo(self, vars_artificiais):
        """Mostra a função objetivo após as restrições"""
        print("\n2. Transformando a função objetivo:")
        
        # Parte 1: Original
        termos_orig = [f"{coef:.2f}{var}" for var, coef in self.funcao_obj.items()]
        #tipo = "Maximizar" if self.tipo == 'max' else "Minimizar"
        print(f"FO {self.tipo} (Z) = {' + '.join(termos_orig)}")
        
        # Parte 2: Com Big M (se aplicável)
        if vars_artificiais:
            termos_M = [f"-M{var[1:]}{var}" for var in vars_artificiais]
            print(f"FO {self.tipo} (Z) = {' + '.join(termos_orig)} {' '.join(termos_M)}")
        
        # Parte 3: Forma padrão
        termos_padrao = [f"{-coef:.2f}{var}" for var, coef in self.funcao_obj.items()]
        if vars_artificiais:
            termos_padrao += [f"+M{var[1:]}{var}" for var in vars_artificiais]
        
        fo_zero = []
        for item in termos_padrao:
            if "-" not in item:
                item = "+"+item
            fo_zero.append(item)
        eq_padrao = ' '.join(fo_zero).replace('++', '+')
        print(f"FO {self.tipo} (Z) {eq_padrao} = 0")


    def _processar_restricoes(self):
        """Processa as restrições e exibe no formato especificado"""
        print("\n1. Verificando restrições:")
        
        restricoes_padrao = []
        variaveis_folga = []
        variaveis_artificiais = []
        b = []
        
        for i, restricao in enumerate(self.restricoes, 1):
            # Coeficientes das variáveis originais
            coefs = [restricao['expr'].get(var, 0.0) for var in self.variaveis_originais]
            folga = f"XF{i}"
            artificial = f"A{i}"
            
            # Formatação da parte esquerda da restrição
            lado_esquerdo = " + ".join([f"{c:.2f}{v}" for c, v in zip(coefs, self.variaveis_originais) if c != 0])
            
            # Transformação conforme o operador
            if restricao['operador'] == "<=":
                transformacao = f"{lado_esquerdo} + {folga}"
                variaveis_folga.append(folga)
                
            elif restricao['operador'] == ">=":
                transformacao = f"{lado_esquerdo} - {folga} + {artificial}"
                variaveis_folga.append(folga)
                variaveis_artificiais.append(artificial)
                
            elif restricao['operador'] == "==":
                transformacao = f"{lado_esquerdo} + {artificial}"
                variaveis_artificiais.append(artificial)
            
            # Exibição no formato solicitado
            print(f"Restrição {i}: {lado_esquerdo} {restricao['operador']} {restricao['valor']:.2f} → {transformacao} = {restricao['valor']:.2f}")
            
            restricoes_padrao.append(coefs)
            b.append(restricao['valor'])
        
        return restricoes_padrao, variaveis_folga, variaveis_artificiais, b

    # --- MÉTODOS A SEREM IMPLEMENTADOS ---
    def _mostrar_tabela(self):
        """Exibe a tabela simplex com Big M formatado, mantendo tipos consistentes"""
        # Cria cópia da tabela convertendo tudo para string
        tabela_formatada = self.tabela.copy().astype(str)
        
        # Formata os valores -M como strings
        for col in tabela_formatada.columns:
            if col.startswith('A'):
                idx = col[1:]
                for i in range(len(tabela_formatada)):
                    val = self.tabela.at[i, col]
                    if abs(val + self.M) < 1e-6:
                        tabela_formatada.at[i, col] = f"M{idx}"
                    elif abs(val - self.M) < 1e-6:
                        tabela_formatada.at[i, col] = f"M{idx}"
                    else:
                        tabela_formatada.at[i, col] = f"{val:.2f}"
        
        # Formata os demais valores numéricos
        for col in tabela_formatada.columns:
            if not col.startswith('A'):
                for i in range(len(tabela_formatada)):
                    if isinstance(self.tabela.at[i, col], (int, float)):
                        tabela_formatada.at[i, col] = f"{self.tabela.at[i, col]:.2f}"
        
        # Configura índices
        tabela_formatada.index = ['Z'] + [f"R{i}" for i in range(1, len(tabela_formatada))]
        
        print(tabela_formatada.to_string(index=False))

    def _obter_solucao_atual(self):
        """Retorna e exibe a solução atual corretamente"""
        # Garante que temos variáveis básicas
        if not hasattr(self, 'variaveis_basicas') or not self.variaveis_basicas:
            self._identificar_variaveis_basicas_iniciais()
        
        solucao = {
            'Variaveis_Basicas': {},
            'Variaveis_Nao_Basicas': [],
            'Valor_Z': self.tabela.at[0, 'b'],
            'otima': True,
            'tem_artificiais': False
        }
        
        # Preenche variáveis básicas
        for i, var in enumerate(self.variaveis_basicas, 1):
            if i < len(self.tabela):
                solucao['Variaveis_Basicas'][var] = self.tabela.at[i, 'b']
                if var.startswith('A'):
                    solucao['tem_artificiais'] = True
        
        # Identifica variáveis não-básicas
        todas_variaveis = [col for col in self.tabela.columns 
                        if col not in ['Z', 'b']]
        solucao['Variaveis_Nao_Basicas'] = [var for var in todas_variaveis 
                                        if var not in self.variaveis_basicas]
        
        # 4. CORREÇÃO: Verificar otimalidade APENAS com variáveis não artificiais
        # Identifica APENAS variáveis originais e de folga (NÃO artificiais)
        variaveis_nao_artificiais = []
        for col in self.tabela.columns:
            if col not in ['Z', 'b'] and not col.startswith('A'):
                variaveis_nao_artificiais.append(col)
        
        # Pega os coeficientes da linha Z apenas para variáveis não artificiais
        coeficientes_nao_artificiais = []
        for var in variaveis_nao_artificiais:
            coef = self.tabela.at[0, var]
            coeficientes_nao_artificiais.append(coef)
        
        # Verifica otimalidade baseada no tipo do problema
        if self.tipo.upper() == 'MAX':
            # Maximização: ótimo quando todos coeficientes não artificiais ≤ 0
            solucao['otima'] = all(coef >= 0 for coef in coeficientes_nao_artificiais)
        else:
            # Minimização: ótimo quando todos coeficientes não artificiais ≥ 0
            solucao['otima'] = all(coef >= -1e-6 for coef in coeficientes_nao_artificiais)
        
        # CORREÇÃO ADICIONAL: Verificar se há variáveis artificiais na base
        if solucao['tem_artificiais']:
            # Se ainda há artificiais na base com valor > 0, o problema pode ser inviável
            for var, valor in solucao['Variaveis_Basicas'].items():
                if var.startswith('A') and valor > 1e-6:
                    print(f"\n⚠️  AVISO: Ainda existe variável artificial na tabela!")
                    solucao['otima'] = False  # Força continuação para tentar remover artificiais
        
        # 5. Exibir a solução
        print(f"\n=== SOLUÇÃO {self.iteracao} ===")

        # Variáveis básicas
        if solucao['Variaveis_Basicas']:
            print("\nVariáveis Básicas:")
            for var, valor in solucao['Variaveis_Basicas'].items():
                print(f"{var} = {valor:.2f}")
        else:
            print("\nERRO: Nenhuma variável básica identificada!")
            print("Variáveis básicas esperadas:", self.variaveis_basicas)
        
        # Variáveis não-básicas
        if solucao['Variaveis_Nao_Basicas']:
            print("\nVariáveis Não Básicas:")
            print(", ".join(solucao['Variaveis_Nao_Basicas']) + " = 0.0000")
        
        # Valor de Z
        print(f"\nValor de Z = {solucao['Valor_Z']:.2f}")
        
        # Aviso sobre variáveis artificiais
        if solucao['tem_artificiais']:
            print("\nHá variáveis artificiais na tabela")
        
        # Status
        if solucao['otima']:
            print("\n✅ Solução ótima encontrada!")
        else:
            print("\nContinuando algoritmo...")
        
        return solucao
    
    def _criar_tabela_simplex(self, restricoes, variaveis_folga, variaveis_artificiais, b):
        """Versão final corrigida para alocação de variáveis artificiais"""
        # 1. Configuração das colunas
        colunas = ['Z'] + self.variaveis_originais + variaveis_folga + variaveis_artificiais + ['b']
        
        # 2. Linha Z com Big M negativo
        linha_Z = [1.0] + [-self.funcao_obj.get(var, 0.0) for var in self.variaveis_originais]
        linha_Z += [0.0] * len(variaveis_folga)
        linha_Z += [-self.M] * len(variaveis_artificiais) + [0.0]
        
        # 3. Linhas das restrições
        linhas = [linha_Z]
        artificial_assigned = 0  # Controle de alocação de variáveis artificiais
        
        for i, (restricao, valor_b) in enumerate(zip(restricoes, b)):
            linha = [0.0] + restricao
            
            # Variáveis de folga
            for j, folga in enumerate(variaveis_folga):
                if j == i and self.restricoes[i]['operador'] != "==":
                    sinal = 1.0 if self.restricoes[i]['operador'] == "<=" else -1.0
                    linha.append(sinal)
                else:
                    linha.append(0.0)
            
            # Variáveis artificiais - LÓGICA CORRIGIDA
            if self.restricoes[i]['operador'] in (">=", "==") and artificial_assigned < len(variaveis_artificiais):
                # Preenche zeros até a posição da artificial correta
                linha += [0.0] * artificial_assigned
                # Insere o 1.0 para a artificial atual
                linha.append(1.0)
                # Preenche zeros para as artificiais restantes
                linha += [0.0] * (len(variaveis_artificiais) - artificial_assigned - 1)
                artificial_assigned += 1
            else:
                linha += [0.0] * len(variaveis_artificiais)
            
            linha.append(valor_b)
            linhas.append(linha)
        
        return pd.DataFrame(linhas, columns=colunas)
    
    def _processar_iteracao(self):
        """Executa uma iteração completa do simplex ignorando variáveis artificiais"""
        try:
            # 1. Identificar variável que entra (IN) - IGNORANDO ARTIFICIAIS
            print("\nIDENTIFICANDO VARIÁVEL QUE ENTRA (IN):")
            
            # Filtra APENAS variáveis não artificiais
            colunas_nao_artificiais = [col for col in self.tabela.columns 
                                    if col not in ['Z', 'b'] and not col.startswith('A')]
            
            if not colunas_nao_artificiais:
                print("Não há variáveis não artificiais para analisar!")
                return False
            
            # Pega coeficientes da linha Z apenas para variáveis não artificiais
            linha_Z = self.tabela.iloc[0]
            coeficientes_nao_artificiais = {col: linha_Z[col] for col in colunas_nao_artificiais}
            
            print("Coeficientes das variáveis não artificiais na linha Z:")
            for var, coef in coeficientes_nao_artificiais.items():
                print(f"  {var}: {coef:.2f}")
            
            # Escolhe a variável com menor coeficiente (mais negativo para MAX)
            if self.tipo.upper() == 'MAX':
                # Para maximização, entra a variável com coeficiente mais negativo
                negativos = {var: coef for var, coef in coeficientes_nao_artificiais.items() if coef < -1e-6}
                if not negativos:
                    print("✅ Todos coeficientes não negativos - solução ótima!")
                    return False
                var_entra = min(negativos.items(), key=lambda x: x[1])[0]
            else:
                # Para minimização, entra a variável com coeficiente mais negativo
                negativos = {var: coef for var, coef in coeficientes_nao_artificiais.items() if coef < -1e-6}
                if not negativos:
                    print("✅ Todos coeficientes não negativos - solução ótima!")
                    return False
                var_entra = min(negativos.items(), key=lambda x: x[1])[0]
            
            coef_entra = coeficientes_nao_artificiais[var_entra]
            print(f"\nColuna pivô (IN): {var_entra} (coeficiente: {coef_entra:.2f})")
            
            # 2. Identificar variável que sai (OUT)
            print("\n\nIDENTIFICANDO VARIÁVEL QUE SAI (OUT):")
            coluna_pivo = self.tabela[var_entra][1:]  # Exclui linha Z
            b = self.tabela['b'][1:]
            
            # Calcula razões (b/coluna_pivo) apenas para valores positivos
            razoes = b / coluna_pivo
            razoes_positivas = razoes[coluna_pivo > 0]
            
            if razoes_positivas.empty:
                raise ValueError("Problema ilimitado - não há razões positivas")
            
            var_sai_idx = razoes_positivas.idxmin()
            var_sai = self.variaveis_basicas[var_sai_idx - 1]  # -1 porque linha 0 é Z
            elemento_pivo = self.tabela.at[var_sai_idx, var_entra]
            
            # Exibe cálculo das razões
            print("\nCálculo das razões (b/coluna pivô):")
            for i, (valor_b, valor_col) in enumerate(zip(b, coluna_pivo)):
                if valor_col > 0:
                    print(f"Linha {i+1}: {valor_b:.2f}/{valor_col:.2f} = {valor_b/valor_col:.2f}")
            
            print(f"\nLinha que sai (OUT): {var_sai_idx+1} (menor razão positiva)")
            print(f"Elemento pivô: {elemento_pivo:.2f}")
            
            # 3. Pivotamento
            print("\n=== PIVOTAMENTO ===")

            # 1. Normalização da linha pivô
            print(f"\n1. Normalizando linha pivô (linha {var_sai_idx+1}):")
            linha_pivo_original = self.tabela.iloc[var_sai_idx].copy()
            linha_pivo_norm = linha_pivo_original / elemento_pivo

            # Mostra tabela comparando linha original e normalizada
            dados_pivo = [
                ["Linha OUT"] + linha_pivo_original.to_list(),
                [f"NLP /({elemento_pivo})"] + linha_pivo_norm.to_list()
            ]
            print(pd.DataFrame(dados_pivo, 
                            columns=["Tipo"] + list(self.tabela.columns))
                            .to_string(float_format="%.2f", index=False))

            # Aplica a normalização na tabela
            self.tabela.iloc[var_sai_idx] = linha_pivo_norm

            # 2. Atualização das outras linhas
            print("\n2. Atualizando outras linhas:\n")
            for idx in range(len(self.tabela)):
                if idx == 0:  # Tratamento especial para linha Z (Big M)
                    self._atualizar_linha_z(var_entra, var_sai_idx, elemento_pivo)
                    continue
                if idx == var_sai_idx:
                    continue
                    
                coef_pivo = self.tabela.at[idx, var_entra]
                linha_original = self.tabela.iloc[idx].copy()
                
                # Inverte o sinal do coeficiente para operação correta
                coef_pivo_invertido = -coef_pivo
                elemento_mult = coef_pivo_invertido * linha_pivo_norm
                nova_linha = linha_original + elemento_mult
                
                # Mostra detalhes da operação para cada linha
                dados_linha = [
                    ["NLP"] + linha_pivo_norm.to_list(),
                    [f"*({coef_pivo_invertido:.2f})"] + elemento_mult.to_list(),
                    ["VL "+str(idx+1)] + linha_original.to_list(),
                    ["NL "+str(idx+1)] + nova_linha.to_list()
                ]
                
                print(pd.DataFrame(dados_linha,
                                columns=[f"Linha {idx+1}:"] + list(self.tabela.columns))
                                .to_string(float_format="%.2f", index=False))
                
                print("\n")
                # Aplica a atualização
                self.tabela.iloc[idx] = nova_linha

            # 3. Atualização das variáveis básicas/não-básicas
            #print("\n3. Atualizando variáveis básicas e não-básicas:")
            self._atualizar_variaveis(var_entra, var_sai, var_sai_idx)

            return True
            
        except Exception as e:
            print(f"\n⛔ ERRO durante a iteração: {str(e)}")
            print("Estado atual da tabela:")
            self._mostrar_tabela()
            return False
        

    
    def _atualizar_linha_z(self, var_entra, var_sai_idx, elemento_pivo):
        """Atualização especial da linha Z para lidar com Big M com print detalhado"""
        coef = self.tabela.at[0, var_entra]
        linha_pivo = self.tabela.iloc[var_sai_idx].copy()
        linha_z_original = self.tabela.iloc[0].copy()
        
        # Calcula os componentes
        coef_invertido = -coef
        linha_mult = coef_invertido * linha_pivo
        nova_linha_z = linha_z_original + linha_mult

        
        
        # Prepara os dados para exibição
        dados = [
            ["NLP"] + linha_pivo.round(2).to_list(),
            [f"*({coef_invertido:.2f})"] + linha_mult.round(2).to_list(),
            ["VL1"] + linha_z_original.round(2).to_list(),
            ["NL1"] + nova_linha_z.round(2).to_list()
        ]
        
        # Formata a exibição
        df = pd.DataFrame(
            dados,
            columns=["Linha 1"] + list(self.tabela.columns)
        )
        
        #print("\nAtualização da Linha Z:")
        print(df.to_string(float_format="%.2f", index=False),"\n\n")
        
        # Aplica a atualização
        self.tabela.iloc[0] = nova_linha_z
        
        # Ajusta variáveis artificiais (Big M)
        for col in self.tabela.columns:
            if col.startswith('A') and col in self.variaveis_nao_basicas:
                self.tabela.at[0, col] = -self.M
        
        # Mostra o ajuste das artificiais se houve mudança
        #if any(col.startswith('A') for col in self.tabela.columns):
        #    print("\nAjuste das variáveis artificiais para -M:")
        #    print(self.tabela.iloc[0][[col for col in self.tabela.columns if col.startswith('A')]])

        # Função para formatar direto substituindo A por M
            
    def _atualizar_variaveis(self, var_entra, var_sai, var_sai_idx):
        #"""Atualiza as listas de variáveis de forma segura"""
        try:
            # Atualiza variáveis básicas
            self.variaveis_basicas[var_sai_idx - 1] = var_entra
            
            # Atualiza variáveis não-básicas
            if var_sai in self.variaveis_nao_basicas:
                self.variaveis_nao_basicas.remove(var_sai)
            self.variaveis_nao_basicas.append(var_sai)
            
            # Remove artificiais se saírem da base (com verificação)
            if var_sai.startswith('A') and var_sai in self.variaveis_artificiais:
                self.variaveis_artificiais.remove(var_sai)
                
        except Exception as e:
            print(f"\n⛔ ERRO ao atualizar variáveis: {str(e)}")
            print(f"Tentando atualizar com: var_entra={var_entra}, var_sai={var_sai}")
            print("Variáveis básicas atuais:", self.variaveis_basicas)
            print("Variáveis não-básicas atuais:", self.variaveis_nao_basicas)
            print("Variáveis artificiais atuais:", self.variaveis_artificiais)
            raise

        
    def _identificar_variaveis_basicas_iniciais(self):
        """Identifica corretamente as variáveis básicas iniciais"""
        self.variaveis_basicas = []
        
        # Para cada linha de restrição (ignorando a linha Z)
        for i in range(1, len(self.tabela)):
            # Verifica colunas de folga e artificiais
            for col in self.tabela.columns:
                if col in ['Z', 'b']:
                    continue
                    
                # Verifica se é a coluna pivô (1 na linha atual e 0 nas outras)
                if (abs(self.tabela.at[i, col] - 1.0) < 1e-6 and
                    all(abs(self.tabela.at[j, col]) < 1e-6 
                    for j in range(len(self.tabela)) if j != i and j != 0)):
                    
                    self.variaveis_basicas.append(col)
                    break
        
        # Se não encontrou, usa fallback para identificação padrão
        if not self.variaveis_basicas:
            self.variaveis_basicas = [f'XF{i+1}' if f'XF{i+1}' in self.tabela.columns 
                                    else f'A{i+1}' 
                                    for i in range(len(self.restricoes))]
            
            print(f"AVISO: Usando fallback para variáveis básicas: {self.variaveis_basicas}")