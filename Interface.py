import tkinter as tk
from tkinter import messagebox
import funcoes
import simplexPadrao
import simplexEspecial
import io
import sys

# Variáveis globais para armazenar o último modelo
modelo_funcao = ""
modelo_restricoes = ""
modelo_tipo = ""
variaveis = ""
restricoes = ""

def verificar_modelo():

    global modelo_funcao, modelo_restricoes, modelo_tipo, variaveis, restricoes
    funcao = entrada_funcao.get().strip()
    restricoes = entrada_restricoes.get("1.0", tk.END).strip()

    if not funcao:
        messagebox.showerror("Erro", "A função objetivo não pode estar vazia.")
        desabilitar_botoes()
        limpar_labels()
        return

    if not restricoes:
        messagebox.showerror("Erro", "As restrições não podem estar vazias.")
        desabilitar_botoes()
        limpar_labels()
        return

    
    sucesso_inicio, funcao, variaveis, constante = funcoes.definir_funcao(entrada_funcao.get())

    if sucesso_inicio:
        #restricoes.append(resultado)
        #print(sucesso_inicio, funcao, variaveis, constante)
        sucesso_restricao, restricoes = funcoes.coletar_restricoes(entrada_restricoes.get("1.0", "end-1c").split('\n'),variaveis)
        
    else:
        limpar_labels()
        messagebox.showerror("Erro", funcao)
        desabilitar_botoes()
        return

    

    if sucesso_restricao:
        modelo_funcao = entrada_funcao.get()
        modelo_restricoes = entrada_restricoes.get("1.0", "end-1c")
        modelo_tipo = tipo_var.get()
        print(sucesso_restricao, restricoes)
        atualizar_modelo(funcao, variaveis, restricoes)
        habilitar_botoes(funcoes.classificar_problema(variaveis,restricoes))
        limpar_entrada()
        btn_editar_modelo.config(state="normal")

    else:
        limpar_labels()
        messagebox.showerror("Erro", restricoes)
        desabilitar_botoes()
        return
    # Exibir no frame Modelo
    

    # Ativar os botões de resolução
    #


def atualizar_modelo(funcao, variaveis, restricoes):
    label_fmaxmin.config(text=f"\nFO {tipo_var.get()} (Z): {funcao}")
    label_variaveis.config(text=f"Variáveis: {', '.join(variaveis)}")
    texto_restricoes = formatar_restricoes(restricoes)
    label_restricoes.config(text=f"{texto_restricoes}")
    label_nao_neg.config(text=f"\nNão Negatividade: {' >= 0, '.join(variaveis)} >= 0")


def habilitar_botoes(possibilidades):
    desabilitar_botoes()
    if "gráfico" in possibilidades:
        btn_grafico.config(state="normal")
    if "padrao" in possibilidades and tipo_var.get() == "Max":
        btn_simplex.config(state="normal")
    if "especial" in possibilidades:
        btn_simplex_esp.config(state="normal")
    if "noroeste" in possibilidades:
        btn_canto_noroeste.config(state="normal")

def editar_modelo():
    global modelo_funcao, modelo_restricoes, modelo_tipo
    limpar_labels()
    desabilitar_botoes()
    entrada_funcao.delete(0, tk.END)
    entrada_funcao.insert(0, modelo_funcao)
    entrada_restricoes.delete("1.0", tk.END)
    entrada_restricoes.insert("1.0", modelo_restricoes)
    btn_editar_modelo.config(state="disabled")
    tipo_var.set(modelo_tipo)

def desabilitar_botoes():
    btn_grafico.config(state="disabled")
    btn_simplex.config(state="disabled")
    btn_simplex_esp.config(state="disabled")
    btn_canto_noroeste.config(state="disabled")

def limpar_labels():
    label_fmaxmin.config(text=f"\nFO (Z):")
    label_variaveis.config(text=f"Variáveis: ")
    label_restricoes.config(text=f"")
    label_nao_neg.config(text=f"\nNão Negatividade: ")

def limpar_entrada():
    entrada_funcao.delete(0, 'end')
    entrada_restricoes.delete('1.0', 'end')

def formatar_restricoes(restricoes):
    linhas = []
    for restricao in restricoes:
        termos = []
        for var, coef in restricao["expr"].items():
            if coef == 1:
                termos.append(f"{var}")
            elif coef == -1:
                termos.append(f"-{var}")
            else:
                termos.append(f"{coef}{var}")
        
        lado_esquerdo = " + ".join(termos).replace("+ -", "- ")
        linha = f"{lado_esquerdo} {restricao['operador']} {restricao['valor']}"
        linhas.append(linha)
    return "\n".join(linhas)

# Funções para abrir novas janelas
def abrir_janela_grafico():
    janela_grafico = tk.Toplevel(janela)
    janela_grafico.title("Gráfico")
    janela_grafico.geometry("500x400")

    tk.Label(janela_grafico, text="Aqui será exibido o Gráfico").pack(pady=20)
    tk.Button(janela_grafico, text="Fechar", command=janela_grafico.destroy).pack(pady=10)

    janela_grafico.grab_set()  # Trava a janela principal

def abrir_janela_simplex():
    janela_simplex = tk.Toplevel(janela)
    janela_simplex.title("Simplex Padrão")
    janela_simplex.geometry("800x600")
    janela_simplex.resizable(True, True)

    tk.Label(janela_simplex, text="Execução do Simplex Padrão").pack(pady=20)

    solucionador = simplexPadrao.SolucionadorSimplex(modelo_tipo, variaveis, restricoes)

    # Captura a saída do método resolver()
    resultado = capturar_saida(solucionador.resolver)
    
        # Frame para a caixa de texto e scrolls
    frame_texto = tk.Frame(janela_simplex)
    frame_texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Scrollbar vertical
    scrollbar_y = tk.Scrollbar(frame_texto, orient=tk.VERTICAL)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    # Scrollbar horizontal
    scrollbar_x = tk.Scrollbar(frame_texto, orient=tk.HORIZONTAL)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Caixa de texto
    caixa_texto = tk.Text(
        frame_texto, 
        wrap="none",  # Desativa quebra de linha para funcionar scroll horizontal
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    caixa_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Conecta os scrollbars à caixa de texto
    scrollbar_y.config(command=caixa_texto.yview)
    scrollbar_x.config(command=caixa_texto.xview)

    # Insere o resultado na caixa de texto
    caixa_texto.insert(tk.END, resultado)
    caixa_texto.config(state='disabled')

    janela_simplex.grab_set()  # Trava a janela principal
    tk.Button(janela_simplex, text="Fechar", command=janela_simplex.destroy).pack(pady=10)

def abrir_janela_simplex_esp():
    janela_esp = tk.Toplevel(janela)
    janela_esp.title("Simplex Especial")
    janela_esp.geometry("800x600")
    janela_esp.resizable(True, True)

    tk.Label(janela_esp, text="Execução do Simplex Especial").pack(pady=10)

    janela_esp.grab_set()  # Trava a janela principal

    # Cria o objeto do solucionador
    solucionador = simplexEspecial.SolucionadorSimplexBigM(modelo_tipo, variaveis, restricoes)

    # Captura a saída do método resolver()
    resultado = capturar_saida(solucionador.resolver)

    # Frame para a caixa de texto e scrolls
    frame_texto = tk.Frame(janela_esp)
    frame_texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Scrollbar vertical
    scrollbar_y = tk.Scrollbar(frame_texto, orient=tk.VERTICAL)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    # Scrollbar horizontal
    scrollbar_x = tk.Scrollbar(frame_texto, orient=tk.HORIZONTAL)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Caixa de texto
    caixa_texto = tk.Text(
        frame_texto, 
        wrap="none",  # Desativa quebra de linha para funcionar scroll horizontal
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    caixa_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Conecta os scrollbars à caixa de texto
    scrollbar_y.config(command=caixa_texto.yview)
    scrollbar_x.config(command=caixa_texto.xview)

    # Insere o resultado na caixa de texto
    caixa_texto.insert(tk.END, resultado)
    caixa_texto.config(state='disabled')

    # Botão fechar
    tk.Button(janela_esp, text="Fechar", command=janela_esp.destroy).pack(pady=10)



def abrir_janela_canto_noroeste():
    janela_cn = tk.Toplevel(janela)
    janela_cn.title("Canto Noroeste")
    janela_cn.geometry("600x500")

    tk.Label(janela_cn, text="Execução do Método Canto Noroeste").pack(pady=20)
    tk.Button(janela_cn, text="Fechar", command=janela_cn.destroy).pack(pady=10)

    janela_cn.grab_set()  # Trava a janela principal


def capturar_saida(funcao):
    buffer = io.StringIO()
    sys_stdout_original = sys.stdout
    sys.stdout = buffer
    try:
        funcao()
    finally:
        sys.stdout = sys_stdout_original
    return buffer.getvalue()

# ----------------------------------------
# Interface
# ----------------------------------------

janela = tk.Tk()
janela.title("Modelo de Programação Linear")
janela.geometry("800x600")
janela.resizable(False, False)

# Frame principal
frame_topo = tk.Frame(janela)
frame_topo.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

frame_baixo = tk.Frame(janela)
frame_baixo.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Frame Entrada
frame_entrada = tk.LabelFrame(frame_topo, text="Digite as informações:", padx=5, pady=5)
frame_entrada.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

# Tipo
frame_tipo = tk.Frame(frame_entrada)
frame_tipo.pack(anchor="w", pady=2)
tk.Label(frame_tipo, text="Tipo:").pack(side=tk.LEFT)
tipo_var = tk.StringVar(value="Max")
tk.Radiobutton(frame_tipo, text="Max", variable=tipo_var, value="Max").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(frame_tipo, text="Min", variable=tipo_var, value="Min").pack(side=tk.LEFT)

# Função
tk.Label(frame_entrada, text="Função:").pack(anchor="w")
entrada_funcao = tk.Entry(frame_entrada, width=50)
entrada_funcao.pack(fill=tk.X, pady=2)

# Restrições
tk.Label(frame_entrada, text="Restrições:").pack(anchor="w")
entrada_restricoes = tk.Text(frame_entrada, width=45, height=5)
entrada_restricoes.pack(fill=tk.X, pady=2)

# Não negatividade
frame_nao_neg = tk.Frame(frame_entrada)
frame_nao_neg.pack(anchor="w", pady=5)
tk.Label(frame_nao_neg, text="Não Negatividade:").pack(side=tk.LEFT)
nao_neg_var = tk.StringVar(value="Sim")
tk.Radiobutton(frame_nao_neg, text="Sim", variable=nao_neg_var, value="Sim").pack(side=tk.LEFT, padx=5)
#tk.Radiobutton(frame_nao_neg, text="Não", variable=nao_neg_var, value="Não").pack(side=tk.LEFT)

# Botão Verificar Modelo
btn_verificar = tk.Button(frame_entrada, text="Verificar Modelo", command=verificar_modelo)
btn_verificar.pack(pady=10,side=tk.LEFT,padx=140)

btn_editar_modelo = tk.Button(frame_entrada, text="Editar Modelo", state="disabled", command=editar_modelo)
btn_editar_modelo.pack(pady=10, side=tk.LEFT)

# Frame Histórico
frame_historico = tk.LabelFrame(frame_topo, text="Histórico:")
frame_historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Frame Modelo
frame_modelo = tk.LabelFrame(frame_baixo, text="Modelo:")
frame_modelo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

label_fmaxmin = tk.Label(frame_modelo, text="\nFO (Z):")
label_fmaxmin.pack(anchor="w", pady=2)

label_variaveis = tk.Label(frame_modelo, text="Variáveis:")
label_variaveis.pack(anchor="w", pady=2)

label_restricoes_titulo = tk.Label(frame_modelo, text="Restrições:")
label_restricoes_titulo.pack(anchor="w", pady=2)
label_restricoes = tk.Label(frame_modelo, text="")
label_restricoes.pack(anchor="w", pady=2)

label_nao_neg = tk.Label(frame_modelo, text="\nNão negatividade:")
label_nao_neg.pack(anchor="w", pady=2)

# Frame Resolução
frame_resolucao = tk.LabelFrame(frame_baixo, text="Resolução:")
frame_resolucao.pack(side=tk.LEFT, fill=tk.Y)

btn_grafico = tk.Button(frame_resolucao, text="Gerar Gráfico", state="disabled", command=abrir_janela_grafico)
btn_grafico.pack(pady=15, padx=60)

btn_simplex = tk.Button(frame_resolucao, text="Simplex Padrão", state="disabled", command=abrir_janela_simplex)
btn_simplex.pack(pady=15)

btn_simplex_esp = tk.Button(frame_resolucao, text="Simplex Especial", state="disabled", command=abrir_janela_simplex_esp)
btn_simplex_esp.pack(pady=15)

btn_canto_noroeste = tk.Button(frame_resolucao, text="Canto Noroeste", state="disabled", command=abrir_janela_canto_noroeste)
btn_canto_noroeste.pack(pady=15)

janela.mainloop()
