import re

########## pendente validar as expreçoes repetidas da função, na restrição express]ao repetidaé somada a já existente
########## pendente iniciar interface
########## possivel pendencia (validar mais a fundo a entrada, se repetiu variaavel ou operador <=)
##########




class ModeloProgramacaoLinear:
    def __init__(self):

        """
        Inicializa o modelo de programação linear.

        """
        self.tipo = ""  # "max" ou "min"
        self.funcao = {}  # Pode ser usado para armazenar a função objetivo de outra forma
        self.constante = 0  # Termo independente da função objetivo
        self.variaveis = {}  # {nome_variavel: coeficiente_na_funcao_objetivo}
        self.restricoes = []  # Lista de dicionários representando restrições
        self.nao_negatividade = True  # Todas as variáveis são >= 0 por padrão

    def padronizar_expressao(self, entrada):
        """Remove espaços e converte para minúsculas."""
        return entrada.strip().lower().replace(" ", "").replace(",",".")
    
    def escolher_tipo(self):
        while tipo not in ['MAX', 'MIN']:
            tipo = input("Tipo de problema (MAX ou MIN): ").strip().upper()
        self.tipo = tipo
    
    def definir_funcao(self):
        funcao_objetivo = ""
        while self.validar_expressao(funcao_objetivo) == False or funcao_objetivo.strip() == "":
            funcao_objetivo = input("Digite uma função objetivo válida: ")

        self.funcao = self.padronizar_expressao(funcao_objetivo)
        self.funcao = self.funcao.replace("-","+-")
        for item_funcao in self.funcao.split("+"):
            if "x" in item_funcao:
                item_funcao = item_funcao.split("x")
                self.adicionar_variavel("x"+item_funcao[1],item_funcao[0])
            else:
                self.adicionar_constante(float(item_funcao) if item_funcao != "" else 0.0)

    def adicionar_variavel(self, variavel, coeficiente_objetivo):
        """Adiciona uma variável de decisão ao modelo."""
        # Se o coeficiente veio como string vazia ou apenas espaços
        # isinstance = Evita erro de execução ao chamar .strip() em valores que não são strings (como inteiros ou floats);
        # isinstance = Permite tratar corretamente entradas como " ", "", "-", "2.5" etc. sem quebrar quando o valor já for um número.
        if isinstance(coeficiente_objetivo, str) and coeficiente_objetivo.strip() == "":
            coeficiente_objetivo = 1
        else:
            if "-" in coeficiente_objetivo and len(coeficiente_objetivo) == 1:
                coeficiente_objetivo = -1
            else:
                coeficiente_objetivo = coeficiente_objetivo
            
        self.variaveis[variavel] = float(coeficiente_objetivo)

    def adicionar_constante(self, valor_constante):
        """Adiciona um termo constante à função objetivo."""
        self.constante += valor_constante

    def validar_expressao(self, expressao):
        expressao = self.padronizar_expressao(expressao)

        # Regex para identificar termos como: 3x1, -4.5x2, +7x10 etc.
        padrao = re.compile(r'^[+-]?\s*(\d*\.?\d+)?\s*\*?\s*x\d+$') #bkp nãoaceita termo subtração na expressão r'^[+-]?\s*(\d*\.?\d+)?\s*\*?\s*x\d+$'
        expressao = expressao.replace("-","+-")
        expressao = expressao.split("+")
        #print(expressao)
        for exp in expressao:
            exp = exp.strip()
            #print("exp", exp)
            try:
                float(exp)
                continue
            except:
                pass
            if not exp:
                continue  # ignora termos vazios
            if not padrao.match(exp):
                #print("no", exp)
                return False
        return True
    
    def _encontrar_operador(self, restricao, operadores_validos):
        """
        Verifica se a restrição contém um operador válido.
        Retorna o operador encontrado ou None se não existir.
        Levanta erro se houver mais de um operador.
        """
        operador_encontrado = None
        for op in operadores_validos:
            if op in restricao:
                if operador_encontrado is not None:
                    return None, f'Mais de um operador encontrado: "{operador_encontrado}" e "{op}" na restrição "{restricao}"'
                operador_encontrado = op
        return operador_encontrado, None  # (operador, mensagem_de_erro)
    

    def adicionar_restricao(self, restricao):
        """
        Adiciona uma restrição após tratar a expressão.
        Formato esperado: "2x1 + 3x2 <= 500" ou "x1 >= 10".
        """
        # Passo 1: Identifica o operador (>=, <=, >, <, ==)
        restricao = self.padronizar_expressao(restricao)

        operador, erro = self._encontrar_operador(restricao, [">=", "<=", "=="])
        if erro:
            return False, erro
        
        # Passo 2: Se não encontrou operador composto, verifica operadores simples (>, <, =)
        if operador is None:
            operador, erro = self._encontrar_operador(restricao, [">", "<", "="])
            if erro:
                return False, erro
        
        # Passo 3: Se nenhum operador foi encontrado, retorna erro
        if operador is None:
            return False, f"Operador inválido na restrição: {restricao}"
            # Passo 2: Separa a expressão em partes (termos e valor)

        try:
            termos, valor = restricao.split(operador)
            valor = float(valor.strip())
        except:
            return False, f"Restrição inválida: {restricao}"


        # Passo 3: Extrai os coeficientes das variáveis (ex: "2x1" → {"x1": 2})
        coeficientes = {}

        if self.validar_expressao(termos):
            for termo in termos.split("+"):
                
                termo = termo.split("x")

                if termo[0] == "":
                    coef = 1.0  # Coeficiente implícito (ex: "x1" → 1x1)
                    var = termo[1]
                elif termo[0] == "-" and len(termo) == 2:
                    coef = 1.0  # Coeficiente implícito (ex: "-x1" → -1x1)
                    var = termo[1]
                elif len(termo)==1:
                    coef = int(termo[0])
                    var = "constante"
                else:
                    coef = float(termo[0])
                    var = termo[1]

                #Faz dicionario das expressoes, verifica se já existe tal VAR, se existir ele soma o coef
                print("coef: ",coef,"var: ",var)
                coeficientes[f"x{var}"] = coeficientes.get(f"x{var}", 0) + coef
                

            # Passo 4: Armazena a restrição tratada
            self.restricoes.append({
                "expr": coeficientes, # ou manda o termos direto e posteriormente faço a tratativa
                "tipo": operador,
                "valor": valor
            })
        else:
            return False,print(f"Restrição inválida: {restricao}")
        
        return True, self.restricoes


# --- Teste ---
print("inicio")
teste1 = ModeloProgramacaoLinear()  # Note os parênteses para instanciar!
print("RESTRIÇÂO")
ok, msg = teste1.adicionar_restricao("--6,6x 1+ 99+222X 2 + 3x2+-1x3=400,00")
print('restrições',teste1.restricoes)

#print(ok,msg)
teste1.definir_funcao()
print('variaveis',teste1.variaveis)
print('constante',teste1.constante)
print('funcaoo',teste1.funcao)  # Saída esperada: 0 (valor inicial)
print('restriçoes',teste1.restricoes)  # Saída esperada: 0 (valor inicial)