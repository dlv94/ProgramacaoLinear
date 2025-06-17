import re
from pulp import LpMaximize, LpProblem, LpVariable, value


def parse_coefs(expr):
    termos = re.findall(r'([+-]?\s*\d*\.?\d*)\s*\*?\s*(x\d+)', expr)
    coefs = {}
    for coef_str, var in termos:
        coef_str = coef_str.replace(' ', '')
        if coef_str in ['', '+']:
            coef = 1.0
        elif coef_str == '-':
            coef = -1.0
        else:
            coef = float(coef_str.replace(',', '.'))
        coefs[var] = coef
    return coefs

def coletar_modelo():
    modelo = {}
    modelo['tipo'] = input("Tipo de problema (max ou min): ").strip().lower()
    
    while modelo['tipo'] not in ['max', 'min']:
        modelo['tipo'] = input("Tipo inválido. Digite 'max' ou 'min': ").strip().lower()

    fo_input = input("Função objetivo (ex: 3x1 + 5x2): ").replace(',', '.')
    
    # Separar o termo independente, se existir
    constante = 0.0
    termo_constante = re.findall(r'^[\d.]+(?=\+)', fo_input.strip())
    if termo_constante:
        constante = float(termo_constante[0])
        fo_input = fo_input[len(termo_constante[0])+1:]

    modelo['funcao_objetivo'] = parse_coefs(fo_input)
    if constante != 0:
        modelo['constante_objetivo'] = constante

    restricoes = []
    variaveis = set(modelo['funcao_objetivo'].keys())

    while True:
        r = input("Digite uma restrição (ou pressione Enter para terminar): ").strip()
        if not r:
            break
        try:
            parts = re.split(r'(<=|>=|=)', r.replace(',', '.')).strip()
            if len(parts) == 3:
                lhs, tipo, valor = parts
                expr = parse_coefs(lhs)
                restricoes.append({
                    'expr': expr,
                    'tipo': tipo,
                    'valor': float(valor)
                })
                variaveis.update(expr.keys())
            else:
                print("Formato inválido. Exemplo esperado: 2x1 + 3x2 <= 100")
        except Exception as e:
            print(f"Erro ao processar restrição: {e}")

    modelo['restricoes'] = restricoes
    modelo['variaveis'] = sorted(list(variaveis))
    modelo['nao_negatividade'] = modelo['variaveis']

    return modelo

modelo = coletar_modelo()

print("\nModelo estruturado:")
import pprint
pprint.pprint(modelo)
