#Fazer aqui a resolução do problema e gerar o grafico

#1 Definição de região (SE)
#2 Teste de região (SE)
#3 Teste de Lucro (L1|L2)

#4 FO MAX/MIN = x1 = NN , x2 = NN (talvez aplicar alguma biblioteca)

#5 Validação - Com os valores acima aplicar o SE e dizer que é verdadeiro ou falso
#6 resolver a função com os valores
#7 gerar a linha dizendo Fo MAX/MIN(z) = R$XX(resultado do passo 6), sendo x1 = NN e x2 = NN


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import pulp

class SolucionadorGraficoPL:
    def __init__(self, tipo, variaveis, restricoes,constante):
        """
        tipo: str "Max" ou "Min"
        variaveis: dict {'x1': coeficiente, 'x2': coeficiente}
        restricoes: list [{'expr': {'x1': a1, 'x2': a2}, 'operador': '<=', 'valor': b}, ...]
        """
        self.tipo = tipo.lower()
        self.variaveis = variaveis
        self.restricoes = restricoes
        self.vertices = [0,0]
        self.limites = {'x1': (0, None), 'x2': (0, None)}  # Limites padrão (podem ser ajustados)
        self.constante = constante
        
    def resolver(self):
        self._passo1_definir_regiao()
        self._passo2_testar_regiao()
        self._passo3_testar_lucro()
        self._passo4_validar()
    
    def macete_pulp(self,tipo, variaveis, restricoes):
        print('pulp',tipo, variaveis, restricoes)
        """
        Resolve um problema de PL com estrutura compatível com sua interface
        
        Args:
            tipo (str): "Max" ou "Min"
            variaveis (dict): {'x1': coeficiente, 'x2': coeficiente}
            restricoes (list): [{'expr': {'x1': a1, 'x2': a2}, 'operador': '<=', 'valor': b}, ...]
        
        Returns:
            dict: {'valor_otimo': float, 'x1': float, 'x2': float} ou None se inviável
        """
        # 1. Criação do problema
        prob = pulp.LpProblem("Problema_PL", 
                            pulp.LpMaximize if tipo.lower() == "max" else pulp.LpMinimize)
        
        # 2. Criação das variáveis de decisão (sem limites fixos)
        x1 = pulp.LpVariable('x1', lowBound=0)  # x1 ≥ 0
        x2 = pulp.LpVariable('x2', lowBound=0)  # x2 ≥ 0
        
        # 3. Função objetivo
        prob += variaveis['x1'] * x1 + variaveis['x2'] * x2, "Z"
        
        # 4. Adicionar restrições
        for i, rest in enumerate(restricoes, 1):
            expr = 0
            for var, coef in rest['expr'].items():
                if var == 'x1':
                    expr += coef * x1
                elif var == 'x2':
                    expr += coef * x2
            
            if rest['operador'] == '<=':
                prob += expr <= rest['valor'], f"Restricao_{i}"
            elif rest['operador'] == '>=':
                prob += expr >= rest['valor'], f"Restricao_{i}"
            elif rest['operador'] == '==':
                prob += expr == rest['valor'], f"Restricao_{i}"
        
        # 5. Resolver o problema
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        
        # 6. Verificar e retornar solução
        if pulp.LpStatus[prob.status] == 'Optimal':
            return {
                'valor_otimo': pulp.value(prob.objective),
                'x1': x1.value(),
                'x2': x2.value()
            }
        else:
            return {
                'valor_otimo': 0,
                'x1': 0,
                'x2': 0}
        
    def _ajustar_variaveis(self, rest):

        if len(rest) == 2:
            a1 = rest['x1']
            a2 = rest['x2']
        else:
            if 'x1' in rest:
                a1 = rest['x1']
                a2 = 0
            else:
                a2 = rest['x2']
                a1 = 0
        return a1,a2
    
    def _passo1_definir_regiao(self):
        print("=== PASSO 1: Definir Região Viável ===")
        
        # Listar todas as restrições enumeradas
        for i, rest in enumerate(self.restricoes, 1):

            expr = rest['expr']
            b = rest['valor']
            
            a1,a2 = self._ajustar_variaveis(expr)
            
            if a1 == 0 or a2 == 0:
                print(f"\nRestrição {i}: {(f'{a2}x2' if a2 != 0 else f'{a1}x1')} {rest['operador']} {b}")
            else:
                print(f"\nRestrição {i}: {a1}x1 {"+" if a2 >= 0 else ""} {a2}x2 {rest['operador']} {b}")
            
            # Caso com apenas 1 variável (ex: x1 <= 40)
            if a1 == 0 or a2 == 0:
                var = 'x1' if a2 == 0 else 'x2'
                valor = b / (a1 if a1 != 0 else a2)
                print(f"  → {var} = {valor:.2f}")
                print(f"  → {('x2' if a2 == 0 else 'x1')} = (∞)")

                if valor >= self.vertices[0]:
                    self.vertices[0] = valor
                    self.vertices[1] = valor

            else:
                # Para 2 variáveis, calcular pontos como no exemplo
                print(f"  Se x1 = 0 → x2 = {b / a2:.2f}")
                print(f"  Se x2 = 0 → x1 = {b / a1:.2f}")

                if (b/a2) >= (b/a1):
                    if (b/a2) >= self.vertices[0]:
                        self.vertices[0] = (b/a2)
                        self.vertices[1] = (b/a2)
                else:
                    if (b/a1) >= self.vertices[0]:
                        self.vertices[0] = (b/a1)
                        self.vertices[1] = (b/a1)

#        # Plotagem do gráfico (igual ao anterior)
#        plt.figure(figsize=(10, 8))
#        for rest in self.restricoes:
#            a1, a2 = rest['coef']
#            b = rest['valor']
#            x = np.linspace(self.limites['x1'][0], self.limites['x1'][1], 400)
#            y = (b - a1*x) / a2 if a2 != 0 else np.full_like(x, np.inf)
#            plt.plot(x, y, label=f"{a1}x1 + {a2}x2 {rest['operador']} {b}")
#            
#        plt.xlabel('x1')
#        plt.ylabel('x2')
#        plt.title('Passo 1: Região Viável')
#        plt.legend()
#        plt.grid()
#        plt.show()
    
    def _valida_regiao(self, valor, operador, limite):
        """
        Valida se um valor satisfaz a condição especificada pelo operador e limite.
        
        Args:
            valor (float): Valor a ser testado
            operador (str): Operador de comparação ('<=', '>=', '==')
            limite (float): Valor limite para comparação
            
        Returns:
            bool: True se a condição for satisfeita, False caso contrário
        """
        if operador == '<=':
            return valor <= limite + 1e-6  # Tolerância numérica
        elif operador == '>=':
            return valor >= limite - 1e-6  # Tolerância numérica
        elif operador == '==':
            return abs(valor - limite) < 1e-6  # Tolerância numérica
        else:
            raise ValueError(f"Operador '{operador}' não suportado")
    
    def _passo2_testar_regiao(self):
        print(f"\n=== PASSO 2: Testar Região Viável ({(self.vertices[0])},{self.vertices[1]}) ===")
        # Encontrar vértices (implementar lógica completa)

        # Listar todas as restrições enumeradas
        for i, rest in enumerate(self.restricoes, 1):
            #a1, a2 = rest['coef']
            a1, a2 = self._ajustar_variaveis(rest['expr'])
            b = rest['valor']
            operador = rest['operador']
            
            if a1 == 0 or a2 == 0:
                print(f"\nTeste {i}: {(f'{a2}x2' if a2 != 0 else f'{a1}x1')} {rest['operador']} {b}")
            else:
                print(f"\nTeste {i}: {a1}x1 {"+" if a2 >= 0 else ""} {a2}x2 {rest['operador']} {b}")
            
            # Caso com apenas 1 variável (ex: x1 <= 40)
            if a1 == 0 or a2 == 0:
                var = 'x1' if a2 == 0 else 'x2'
                valor = b / (a1 if a1 != 0 else a2)
                print(f"  → {(a1 if a2 == 0 else a2)} * {self.vertices[0]} {operador} {b}")
                print(f"  → {(a1 if a2 == 0 else a2)*self.vertices[0]} {operador} {b}")
                print(f"  → {self._valida_regiao(((a1 if a2 == 0 else a2)*self.vertices[0]),operador,b)}")


            else:
                print(f"      → {a1} * {self.vertices[0]} {"+" if a2 >= 0 else ""} {a2} * {self.vertices[1]} {rest['operador']} {b}")
                print(f"      → {a1*self.vertices[0]} {"+" if a2 >= 0 else ""} {a2*self.vertices[1]} {rest['operador']} {b}")
                print(f"      → {(a1*self.vertices[0])+(a2*self.vertices[1])} {rest['operador']} {b}")
                print(f"      → {self._valida_regiao(((a1*self.vertices[0])+(a2*self.vertices[1])),operador,b)}")
        
#        # Plotar vértices
#        plt.figure(figsize=(10, 8))
#        for x, y in self.vertices:
#            plt.plot(x, y, 'ro')
#        plt.title('Passo 2: Vértices da Região Viável')
#        plt.grid()
#        plt.show()

    def _arredondar_intervalo(self,valor):
        """
        Retorna o intervalo de valores arredondados para 30% menor e 30% maior, 
        considerando um arredondamento grosseiro baseado na magnitude do número.
        
        Args:
            valor (int): Valor de entrada.
        
        Returns:
            tuple: (valor_arredondado_min, valor_arredondado_max)
        """
        # Calcula os limites inferior e superior
        menor = valor * 0.6
        maior = valor * 1.4
        
        # Define o fator de arredondamento conforme a magnitude do número
        if valor <= 100:
            fator = 10
        elif valor <= 1000:
            fator = 100
        elif valor <= 10000:
            fator = 1000
        else:
            fator = 10000
        
        # Arredondamento grosseiro usando o fator determinado
        menor_arredondado = round(menor / fator) * fator
        maior_arredondado = round(maior / fator) * fator

        return menor_arredondado, maior_arredondado


    
    def _passo3_testar_lucro(self):

        macete = self.macete_pulp(self.tipo,self.variaveis,self.restricoes)
        print(macete['valor_otimo'])
        valor_menor,valor_maior = self._arredondar_intervalo(macete['valor_otimo'])
    
        print(f"\n=== PASSO 3: Testar Lucro | L1: R${valor_menor} e L2: R${valor_maior} ===")

        #print(macete['valor_otimo'])
        #tipo = self.tipo
        #coefs = self.variaveis
        #print(tipo,coefs)
        #c1, c2 = coefs
        c1,c2 = self._ajustar_variaveis(self.variaveis)
        # Calcular Z para cada vértice
        #valores_z = []
        #for x, y in self.vertices:
        #    z = c1*x + c2*y
        #    valores_z.append(z)
        #    print(f"Para ({x}, {y}): Z = {z}")
        
        # Encontrar ótimo
        #if tipo == 'max':
       #     idx_otimo = np.argmax(valores_z)
        #else:
        #    idx_otimo = np.argmin(valores_z)
        #
        #self.solucao = self.vertices[idx_otimo]
        #self.z_otimo = valores_z[idx_otimo]
        
        #print(f"\nSolução ótima: {self.solucao}, Z = {self.z_otimo}")

        a1, a2 = self._ajustar_variaveis(self.variaveis)
        
        for i in range(1, 3):
            if a1 == 0 or a2 == 0:
                print(f"\nL{i}: R${valor_menor if i == 1 else valor_maior}  = {f"{a1}x1" if a2 == 0 else f"{a2}x2"} {f"+ {self.constante}" if self.constante !=0 else ""}")
            else:
                print(f"\nL{i}: R${valor_menor if i == 1 else valor_maior} =  {a1}x1 {f"+ {a2}" if a2 >= 0 else a2}x2 {f"+ {self.constante}" if self.constante !=0 else ""}")

                        # Caso com apenas 1 variável (ex: x1 <= 40)
            if a1 == 0 or a2 == 0:
                var = 'x1' if a2 == 0 else 'x2'
                valor = 1
                print(f"  → {var} = {(valor_menor if i == 1 else valor_maior):.2f}")
                print(f"  → {('x2' if a2 == 0 else 'x1')} = (∞)")

                if valor >= self.vertices[0]:
                    self.vertices[0] = valor
                    self.vertices[1] = valor

            else:
                # Para 2 variáveis, calcular pontos como no exemplo
                print(f"  Se x1 = 0 → x2 = {(valor_menor if i == 1 else valor_maior) / a2:.2f}")
                print(f"  Se x2 = 0 → x1 = {(valor_menor if i == 1 else valor_maior) / a1:.2f}")
#        # Plotar FO
#        plt.figure(figsize=(10, 8))
#        x_vals = np.array([v[0] for v in self.vertices])
#        y_vals = np.array([v[1] for v in self.vertices])
#        
#        plt.fill(x_vals, y_vals, 'b', alpha=0.1)
#        
#        # Linha da FO
#        x = np.linspace(min(x_vals), max(x_vals), 100)
#        y_fo = (self.z_otimo - c1*x) / c2
#        plt.plot(x, y_fo, 'r--', label=f"Z = {self.z_otimo}")
#        
#        plt.plot(self.solucao[0], self.solucao[1], 'go', markersize=10, label='Ótimo')
#        plt.title('Passo 3: Solução Ótima')
#        plt.legend()
#        plt.grid()
#        plt.show()
    
    def _passo4_validar(self):
        macete = self.macete_pulp(self.tipo,self.variaveis,self.restricoes)
        print(f"\n=== PASSO 4: Validação ({macete['x1']},{macete['x2']}) ===")

        for i, rest in enumerate(self.restricoes, 1):
            #a1, a2 = rest['coef']
            a1, a2 = self._ajustar_variaveis(rest['expr'])
            b = rest['valor']
            operador = rest['operador']
            
            if a1 == 0 or a2 == 0:
                print(f"\nTeste {i}: {(f'{a2}x2' if a2 != 0 else f'{a1}x1')} {rest['operador']} {b}")
            else:
                print(f"\nTeste {i}: {a1}x1 {"+" if a2 >= 0 else ""} {a2}x2 {rest['operador']} {b}")
            
            # Caso com apenas 1 variável (ex: x1 <= 40)
            if a1 == 0 or a2 == 0:
                var = 'x1' if a2 == 0 else 'x2'
                valor = b / (a1 if a1 != 0 else a2)
                print(f"  → {(a1 if a2 == 0 else a2)} * {macete['x1']} {operador} {b}")
                print(f"  → {(a1 if a2 == 0 else a2)*macete['x1']} {operador} {b}")
                print(f"  → {self._valida_regiao(((a1 if a2 == 0 else a2)*macete['x1']),operador,b)}")


            else:
                print(f"      → {a1} * {macete['x1']} {"+" if a2 >= 0 else ""} {a2} * {macete['x2']} {rest['operador']} {b}")
                print(f"      → {(a1*macete['x1'])+(a2*macete['x2'])} {rest['operador']} {b}")
                print(f"      → {self._valida_regiao(((a1*macete['x1'])+(a2*macete['x2'])),operador,b)}")
            
            ##print(f"{a1}*{x1} + {a2}*{x2} = {valor} {rest['operador']} {b}: {'✔' if valido else '✖'}")
        
        #print(f"\nSolução {'VÁLIDA' if valido else 'INVÁLIDA'}")
        #print(f"Valor ótimo de Z: {self.z_otimo}")
        #print(f"Valor ótimo de X1: {self.solucao[0]} e X2: {self.solucao[1]}")

        print(f"\n======= Resolução FO {self.tipo.upper()} (Z) =======\n")
        a1, a2 = self._ajustar_variaveis(self.variaveis)
        print(f"FO {self.tipo.upper()} (Z) =  {a1}x1 {f"+ {a2}" if a2 >= 0 else a2}x2 {f"+ {self.constante}" if self.constante !=0 else ""}")
        print(f"      → {a1} * {macete['x1']} {"+" if a2 >= 0 else ""} {a2} * {macete['x2']}  {f"+ {self.constante}" if self.constante !=0 else ""}")
        print(f"      → {(a1 * macete['x1'])} {"+" if a2 >= 0 else ""} {(a2 * macete['x2'])}  {f"+ {self.constante}" if self.constante !=0 else ""}")
        print(f"      → {(a1 * macete['x1']) + (a2 * macete['x2']) + (self.constante)}")

        print(f"\nValor de Z: R${(a1 * macete['x1']) + (a2 * macete['x2']) + (self.constante)}")
        print(f"Sendo X1: {macete['x1']} e X2: {macete['x2']}\n")



# Exemplo da Página 4/5 do PDF
if __name__ == "__main__":
    problema = {
        'tipo': 'Max',
        'variaveis': {'x1': 100.0, 'x2': 150.0},
        'restricoes': [
            {'expr': {'x1': 2.0, 'x2': 3.0}, 'operador': '<=', 'valor': 120.0},
            {'expr': {'x1': 5.0}, 'operador': '<=', 'valor': 40.0},
            {'expr': {'x2': 6.0}, 'operador': '<=', 'valor': 30.0}],
        'constante': 100,
    }
    
    solver = SolucionadorGraficoPL(**problema)
    solver.resolver()