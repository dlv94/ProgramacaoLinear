import tkinter as tk
from tkinter import ttk, messagebox
import re

# Sua classe importada ou colada aqui
from main2 import ModeloProgramacaoLinear  # adapte o nome conforme necessário

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modelo de Programação Linear")
        self.geometry("600x500")
        self.model = ModeloProgramacaoLinear()

        self.criar_widgets()

    def criar_widgets(self):
        # Tipo do problema
        frame_tipo = tk.LabelFrame(self, text="Tipo do problema")
        frame_tipo.pack(padx=10, pady=10, fill="x")

        self.tipo_var = tk.StringVar(value="max")
        ttk.Radiobutton(frame_tipo, text="Maximizar", variable=self.tipo_var, value="max").pack(side="left", padx=10)
        ttk.Radiobutton(frame_tipo, text="Minimizar", variable=self.tipo_var, value="min").pack(side="left", padx=10)

        # Função objetivo
        frame_fo = tk.LabelFrame(self, text="Função Objetivo (ex: 2x1 + 3x2 - 5)")
        frame_fo.pack(padx=10, pady=10, fill="x")

        self.entrada_fo = tk.Entry(frame_fo)
        self.entrada_fo.pack(fill="x", padx=10)

        # Restrições
        frame_rest = tk.LabelFrame(self, text="Adicionar restrição (ex: 2x1 + 3x2 <= 10)")
        frame_rest.pack(padx=10, pady=10, fill="x")

        self.entrada_rest = tk.Entry(frame_rest)
        self.entrada_rest.pack(fill="x", padx=10)

        ttk.Button(frame_rest, text="Adicionar restrição", command=self.adicionar_restricao).pack(pady=5)

        # Botões de ação
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(pady=10)

        ttk.Button(frame_botoes, text="Registrar função objetivo", command=self.registrar_fo).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Mostrar modelo", command=self.mostrar_modelo).pack(side="left", padx=10)

        # Saída
        self.txt_saida = tk.Text(self, height=10)
        self.txt_saida.pack(padx=10, pady=10, fill="both", expand=True)

    def registrar_fo(self):
        expressao = self.entrada_fo.get().strip()
        if not expressao:
            messagebox.showerror("Erro", "Digite uma função objetivo.")
            return

        if not self.model.validar_expressao(expressao):
            messagebox.showerror("Erro", "Expressão inválida.")
            return

        self.model.tipo = self.tipo_var.get()
        self.model.funcao = self.model.padronizar_variavel(expressao)

        for termo in self.model.funcao.split("+"):
            if "x" in termo:
                coef, var = termo.split("x")
                self.model.adicionar_variavel("x" + var, coef)
            else:
                try:
                    self.model.adicionar_constante(float(termo))
                except ValueError:
                    pass

        messagebox.showinfo("Sucesso", "Função objetivo registrada!")

    def adicionar_restricao(self):
        restricao = self.entrada_rest.get().strip()
        if not restricao:
            messagebox.showerror("Erro", "Digite uma restrição.")
            return
        try:
            self.model.adicionar_restricao(restricao)
            messagebox.showinfo("Sucesso", "Restrição adicionada.")
            self.entrada_rest.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar restrição: {str(e)}")

    def mostrar_modelo(self):
        self.txt_saida.delete("1.0", tk.END)
        self.txt_saida.insert(tk.END, f"Tipo: {self.model.tipo.upper()}\n")
        self.txt_saida.insert(tk.END, f"Função Objetivo: {self.model.variaveis} + {self.model.constante}\n")
        self.txt_saida.insert(tk.END, "Restrições:\n")
        for r in self.model.restricoes:
            self.txt_saida.insert(tk.END, f"  {r['expr']} {r['tipo']} {r['valor']}\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()
