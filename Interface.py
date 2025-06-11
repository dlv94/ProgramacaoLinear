import tkinter as tk

# Janela principal
root = tk.Tk()
root.title("Modelo de Programação Linear")
root.geometry("800x766")
root.resizable(False, True)

# Frame superior esquerdo - Entrada de dados
frame_input = tk.Frame(root, bd=2, relief=tk.SOLID)
frame_input.place(x=10, y=10, width=500, height=300)

tk.Label(frame_input, text="Digite as informações:").pack(anchor='nw', padx=10, pady=5)

# Tipo Max/Min
tipo_var = tk.IntVar()
frame_tipo = tk.Frame(frame_input)
frame_tipo.pack(anchor='nw', padx=10, pady=2)
tk.Label(frame_tipo, text="Tipo:").pack(side='left')
tk.Radiobutton(frame_tipo, variable=tipo_var, text="Max", value=1).pack(side='left')
tk.Radiobutton(frame_tipo, variable=tipo_var, text="Min", value=2).pack(side='left')

# Função
tk.Label(frame_input, text="Função:").pack(anchor='nw', padx=10, pady=(10,0))
entry_funcao = tk.Entry(frame_input, width=50)
entry_funcao.pack(anchor='nw', padx=10)

# Restrições
tk.Label(frame_input, text="Restrições:").pack(anchor='nw', padx=10, pady=(10,0))
text_restricoes = tk.Text(frame_input, height=5, width=50)
text_restricoes.pack(anchor='nw', padx=10)

# Não negatividade
nn_var = tk.IntVar()
nn_var.set(value=1)
frame_nn = tk.Frame(frame_input)
frame_nn.pack(anchor='nw', padx=10, pady=5)
tk.Label(frame_nn, text="Não Negatividade:").pack(side='left')
tk.Radiobutton(frame_nn, variable=nn_var, text="Sim", value=1).pack(side='left')
tk.Radiobutton(frame_nn, variable=nn_var, text="Não", value=2).pack(side='left')

# Botão gerar modelo
tk.Button(frame_input, text="Gerar Modelo").pack(pady=5)

# Frame superior direito - Histórico
frame_historico = tk.Frame(root, bd=0, relief="flat")
frame_historico.place(x=520, y=10, width=270, height=300)

tk.Label(frame_historico, text="HISTÓRICO", font=("Arial", 10, "bold")).pack()

# Área de histórico com scrollbar
text_hist = tk.Text(frame_historico, height=15, width=32)
scroll_hist = tk.Scrollbar(frame_historico, command=text_hist.yview)
text_hist.configure(yscrollcommand=scroll_hist.set)
text_hist.pack(side='left', fill='both', expand=True)
scroll_hist.pack(side='right', fill='y')

# Frame inferior esquerdo - Modelo gerado
frame_modelo = tk.Frame(root, bd=2, relief=tk.SOLID)
frame_modelo.place(x=10, y=320, width=390, height=440)

tk.Label(frame_modelo, text="Modelo:").pack(anchor='nw', padx=10, pady=(10, 0))
tk.Label(frame_modelo, text="FMAX/MIN:").pack(anchor='nw', padx=10, pady=(10, 0))
tk.Label(frame_modelo, text="Variáveis:").pack(anchor='nw', padx=10, pady=(10, 0))
tk.Label(frame_modelo, text="Restrições:").pack(anchor='nw', padx=10, pady=(10, 0))
tk.Label(frame_modelo, text="Não negatividade:").pack(anchor='nw', padx=10, pady=(10, 0))

# Botão gerar gráfico
tk.Button(frame_modelo, text="Gerar Gráfico").pack(pady=20)

# Frame inferior direito - Simplex
frame_simplex = tk.Frame(root, bd=2, relief=tk.SOLID)
frame_simplex.place(x=410, y=320, width=380, height=440)

tk.Button(frame_simplex, text="Simplex Padrão").pack(pady=20)

root.mainloop()
