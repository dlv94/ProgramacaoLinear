import re

#tipo = ""  # "max" ou "min"
 # Pode ser usado para armazenar a função objetivo de outra forma
#constante = 0  # Termo independente da função objetivo
#variaveis = {}  # {nome_variavel: coeficiente_na_funcao_objetivo}
  # Lista de dicionários representando restrições
nao_negatividade = True  # Todas as variáveis são >= 0 por padrão

def padronizar_expressao(entrada):
    """Remove espaços e converte para minúsculas."""
    return entrada.strip().lower().replace(" ", "").replace(",",".")

def escolher_tipo(tipo):
    while tipo not in ['MAX', 'MIN']:
        tipo = input("Tipo de problema (MAX ou MIN): ").strip().upper()
    return tipo

def definir_funcao(funcao_objetivo):
    """
    Recebe uma função objetivo em formato de string e valida a expressão.
    Retorna:
        (True, funcao_objetivo, variaveis, constante) se estiver correta.
        (False, mensagem_erro) se houver algum erro.
    """
    funcao_objetivo = funcao_objetivo.strip()
    if funcao_objetivo == "":
        return False, "Digite uma função objetivo válida.", None, None

    if not validar_expressao(funcao_objetivo):
        return False, "Expressão inválida. Verifique a sintaxe da função objetivo.", None, None

    funcao = padronizar_expressao(funcao_objetivo).replace("-", "+-")
    variaveis = {}
    constante = 0

    for item_funcao in funcao.split("+"):
        if not item_funcao.strip():
            continue

        if "x" in item_funcao:
            try:
                item_funcao = item_funcao.split("x")
                variavel, coef = _validar_variavel("x" + item_funcao[1], item_funcao[0])
            except:
                return False, f"Erro ao processar a variável na expressão: {item_funcao}", None, None

            if variavel in variaveis:
                return False, f"Erro: Variável {variavel} já foi declarada na função.", None, None

            variaveis[variavel] = variaveis.get(variavel, 0) + float(coef)

        else:
            try:
                constante += float(item_funcao)
            except:
                return False, f"Erro ao processar termo constante: {item_funcao}", None, None

    if not variaveis:
        return False, "A função objetivo não possui variáveis válidas.", None, None

    variaveis = ordenar_variaveis(variaveis)

    return True, funcao_objetivo, variaveis, constante


def ordenar_variaveis(dicionario_variaveis):
    chaves_ordenadas = sorted(
        dicionario_variaveis.keys(),
        key=lambda x: int(x[1:])  # Pega o número após o 'x' (ex: 'x3' → 3)
    )
    
    # Passo 2: Cria um novo dicionário com as chaves ordenadas
    dicionario_ordenado = {chave: dicionario_variaveis[chave] for chave in chaves_ordenadas}
    
    return dicionario_ordenado

def _validar_variavel(variavel, coeficiente_objetivo):
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
        
    #variaveis[variavel] = float(coeficiente_objetivo)
    coeficiente_objetivo = float(coeficiente_objetivo)

    return variavel, coeficiente_objetivo


def validar_expressao(expressao):
    expressao = padronizar_expressao(expressao)
    # Regex para identificar termos como: 3x1, -4.5x2, +7x10 etc.
    padrao = re.compile(r'^[+-]?\s*(\d*\.?\d+)?\s*\*?\s*x\d+$') #bkp nãoaceita termo subtração na expressão r'^[+-]?\s*(\d*\.?\d+)?\s*\*?\s*x\d+$'

    if "x" not in expressao or expressao == "":
        return False

    expressao = expressao.replace("-","+-")
    expressao = expressao.split("+")

    if nao_negatividade and "-" in expressao:
        return False
    for exp in expressao:
        exp = exp.strip()
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

def _encontrar_operador(restricao, operadores_validos):
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

def adicionar_restricao(restricao, variaveis):
    """
    Adiciona uma restrição após tratar a expressão.
    Formato esperado: "2x1 + 3x2 <= 500" ou "x1 >= 10".
    """
    # Passo 1: Identifica o operador (>=, <=, >, <, ==)
    restricoes = {}
    restricao = padronizar_expressao(restricao)
    if "x" not in restricao:
        return False, "Insira uma variável na restrição"
    operador, erro = _encontrar_operador(restricao, [">=", "<=", "=="])
    if erro:
        return False, erro
    
    # Passo 2: Se não encontrou operador composto, verifica operadores simples (>, <, =)
    if operador is None:
        operador, erro = _encontrar_operador(restricao, [">", "<", "="])
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
    lista_var = []
    if validar_expressao(termos):
        termos = termos.replace("-","+-")
        for termo in termos.split("+"):
            termo = termo.split("x")
            print(len(termo))
            if termo == None:
                continue
            elif len(termo)==1:
                #no caso identificou que é constante, logo o index 0 = coef, index 1 precisa informar que é constante pra somar posteriormente
                termo.append("constante") # "constante"
                try:
                    termo = float(termo[0])
                except:
                    continue
            elif f'x{termo[1]}' in lista_var:
                return False,f" Variável x{termo[1]} já existe na restrição: {restricao}"
            elif termo[0] == "":
                termo[0] = 1.0  # Coeficiente implícito (ex: "x1" → 1x1)
            elif termo[0] == "-" and len(termo) == 2:
                termo[0] = -1.0  # Coeficiente implícito (ex: "-x1" → -1x1)
            else:
                pass
            #if nao_negatividade and "-" in restricao:
            #    return False, f'Expressão contém valores negativos'
            #Faz dicionario das expressoes, verifica se já existe tal VAR, se existir ele soma o coef
            #print("coef: ",termo[0],"var: ",termo[1])
            termo[1] = termo[1] if termo[1] == "constante" else f"x{termo[1]}"
            coeficientes[termo[1]] = coeficientes.get(termo[1], 0) + float(termo[0])
            if "x" in termo[1] and termo[1] not in variaveis:
                return False,f" Variável {termo[1]} não existe na função"
            else:
                lista_var.append(termo[1])
            
        # Passo 4: Armazena a restrição tratada
        restricoes = {
            "expr": coeficientes, # ou manda o termos direto e posteriormente faço a tratativa
            "operador": operador if len(operador) == 2 else f'{operador}=',
            "valor": valor
        }
    else:
        return False,print(f"Restrição inválida: {restricao}")
    
    if "expr" in restricoes:  # Verifica se existe a chave 'expr'
        # Ordena as variáveis (x1, x2, x3...) e cria um novo dicionário ordenado
        restricoes["expr"] = dict(
            sorted(
                restricoes["expr"].items(),
                key=lambda item: int(item[0][1:]) if item[0] != "constante" else 0
            )
        )

    #print(restricoes)
    
    return True, restricoes

def coletar_restricoes(lista_entradas, variaveis):
    """
    Recebe uma lista de strings (cada string é uma restrição digitada pelo usuário).
    Valida, processa e retorna uma lista de restrições no formato:
        [{'expr': {...}, 'operador': '<=', 'valor': 50.0}, ...]
    Retorna:
        (True, restricoes) se tudo estiver certo.
        (False, mensagem_erro) se houver algum erro.
    """
    restricoes = []

    if not lista_entradas:
        return False, "Nenhuma restrição foi fornecida."

    for entrada in lista_entradas:
        entrada = entrada.lower().strip()

        if entrada == "":
            continue  # Ignora entradas vazias

        sucesso, resultado = adicionar_restricao(entrada, variaveis)

        if not sucesso:
            return False, f"Erro na restrição '{entrada}': {resultado}"

        # Verifica se já existe essa restrição
        ja_existe = any(
            (r["expr"] == resultado["expr"] and
             r["operador"] == resultado["operador"] and
             r["valor"] == resultado["valor"])
            for r in restricoes
        )

        if ja_existe:
            return False, f"A restrição '{entrada}' já foi adicionada."

        restricoes.append(resultado)

    if not restricoes:
        return False, "Adicione pelo menos uma restrição válida."

    return True, restricoes


#
#
# Necessário testar, função talvez não será usado, e INSERIR CANTO NOROESTE
#
#
def classificar_problema(variaveis,restricoes):
    possibilidades = []

    #Verificar se é possivel gerar gráfico
    if len(variaveis) <=2:
        possibilidades.append("gráfico")

    # Classificação do problema
    problema_simplex = True
    problema_especial = True
    operadores_invalidos = False

    for restricao in restricoes:
        operador = restricao['operador']
        
        if operador not in ['<=', '>=', '==']:
            operadores_invalidos = True
            continue  # Pula para próxima restrição
        
        if operador in ['>=', '==']:
            problema_simplex = False

    # Adiciona classificações baseadas nas restrições
    if operadores_invalidos:
        possibilidades.append("inválido")
    elif problema_simplex:
        possibilidades.append("padrao")
    else:
        possibilidades.append("especial")

    return possibilidades