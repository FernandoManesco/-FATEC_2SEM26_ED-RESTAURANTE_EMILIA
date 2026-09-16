# ============================================================
# telas.py
# Janelas (telas) do sistema Restaurante Emilia.
# Cada tela e uma CLASSE que herda de tk.Toplevel (janela secundaria).
# ============================================================

import tkinter as tk
from tkinter import messagebox, ttk       # ttk tem a Treeview (lista em tabela)
from bancos import Banco                    # nossa classe de conexao


class TelaProdutos(tk.Toplevel):
    """
    Janela de cadastro de produtos.
    Herda de tk.Toplevel -> e uma janela secundaria da principal.
    """

    def __init__(self, janela_pai):
        super().__init__(janela_pai)              # constroi a janela
        self.title("Cadastro de Produtos")
        self.geometry("620x520")
        self.configure(bg="white")
        self.grab_set()                            # modal: trava a principal

        # guarda o id do produto em edicao. None = cadastro novo; numero = editando.
        self.id_em_edicao = None

        # instancia a classe Banco (sera usada em todos os metodos)
        self.banco = Banco()

        # ---------- FORMULARIO ----------
        titulo = tk.Label(self, text="Cadastro de Produtos",
                          font=("Arial", 16, "bold"), bg="white", fg="#B22222")
        titulo.grid(row=0, column=0, columnspan=2, pady=15)

        # Nome
        tk.Label(self, text="Nome:", bg="white").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        self.campo_nome = tk.Entry(self, width=40)
        self.campo_nome.grid(row=1, column=1, padx=8, pady=6, sticky="w")

        # Codigo
        tk.Label(self, text="Código:", bg="white").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        self.campo_codigo = tk.Entry(self, width=20)
        self.campo_codigo.grid(row=2, column=1, padx=8, pady=6, sticky="w")

        # Valor unitario
        tk.Label(self, text="Valor Unitário:", bg="white").grid(row=3, column=0, sticky="e", padx=8, pady=6)
        self.campo_valor = tk.Entry(self, width=15)
        self.campo_valor.grid(row=3, column=1, padx=8, pady=6, sticky="w")

        # Unidade
        tk.Label(self, text="Unidade:", bg="white").grid(row=4, column=0, sticky="e", padx=8, pady=6)
        self.campo_unidade = tk.Entry(self, width=15)
        self.campo_unidade.grid(row=4, column=1, padx=8, pady=6, sticky="w")

        # ---------- BOTOES DE ACAO ----------
        frame_botoes = tk.Frame(self, bg="white")
        frame_botoes.grid(row=5, column=0, columnspan=2, pady=10)

        tk.Button(frame_botoes, text="💾 Salvar",   bg="#28B463", fg="white",
                  width=12, command=self.salvar).pack(side="left", padx=5)

        tk.Button(frame_botoes, text="🧹 Limpar",   bg="#2E86C1", fg="white",
                  width=12, command=self.limpar_campos).pack(side="left", padx=5)

        tk.Button(frame_botoes, text="🗑️ Excluir",  bg="#E74C3C", fg="white",
                  width=12, command=self.excluir).pack(side="left", padx=5)

        # ---------- TREEVIEW (tabela / grid) ----------
        colunas = ("id", "nome", "codigo", "valor", "unidade")
        self.tabela = ttk.Treeview(self, columns=colunas, show="headings", height=10)

        # define cabecalhos e larguras
        self.tabela.heading("id",      text="ID")
        self.tabela.heading("nome",    text="Nome")
        self.tabela.heading("codigo",  text="Código")
        self.tabela.heading("valor",   text="Valor (R$)")
        self.tabela.heading("unidade", text="Unidade")

        self.tabela.column("id",      width=40,  anchor="center")
        self.tabela.column("nome",    width=200, anchor="w")
        self.tabela.column("codigo",  width=100, anchor="center")
        self.tabela.column("valor",   width=100, anchor="e")
        self.tabela.column("unidade", width=80,  anchor="center")

        self.tabela.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # ao clicar numa linha da tabela, preenche o formulario para edicao
        self.tabela.bind("<<TreeviewSelect>>", self.selecionar_produto)

        # carrega os produtos ao abrir a tela
        self.carregar_produtos()

    # =====================  METODOS DE BANCO  =====================

    def carregar_produtos(self):
        """
        SELECT — le todos os produtos do banco e preenche a Treeview.
        """
        # limpa a tabela antes de recarregar
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute("SELECT id, nome, codigo, valor_unitario, unidade FROM produtos ORDER BY nome")
            linhas = cursor.fetchall()
            cursor.close()
            con.close()

            for linha in linhas:
                # formata o valor com 2 casas decimais para exibicao
                dados = (linha[0], linha[1], linha[2], f"{linha[3]:.2f}", linha[4])
                self.tabela.insert("", "end", values=dados)

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{erro}")

    def salvar(self):
        """
        INSERT ou UPDATE — se id_em_edicao for None, insere; senao, atualiza.
        """
        nome    = self.campo_nome.get().strip()
        codigo  = self.campo_codigo.get().strip()
        valor   = self.campo_valor.get().strip()
        unidade = self.campo_unidade.get().strip()

        # ---------- validacoes basicas ----------
        if not nome or not codigo or not valor or not unidade:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        try:
            valor_float = float(valor.replace(",", "."))   # aceita virgula ou ponto
        except ValueError:
            messagebox.showwarning("Atenção", "Valor unitário inválido.")
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()

            if self.id_em_edicao is None:
                # ---------- INSERT ----------
                cursor.execute(
                    "INSERT INTO produtos (nome, codigo, valor_unitario, unidade) "
                    "VALUES (%s, %s, %s, %s)",
                    (nome, codigo, valor_float, unidade)
                )
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            else:
                # ---------- UPDATE ----------
                cursor.execute(
                    "UPDATE produtos SET nome = %s, codigo = %s, valor_unitario = %s, unidade = %s "
                    "WHERE id = %s",
                    (nome, codigo, valor_float, unidade, self.id_em_edicao)
                )
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")

            con.commit()          # confirma a gravacao no banco
            cursor.close()
            con.close()

            self.limpar_campos()
            self.carregar_produtos()   # atualiza a tabela na tela

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao salvar:\n{erro}")

    def excluir(self):
        """
        DELETE — remove o produto selecionado na tabela.
        """
        if self.id_em_edicao is None:
            messagebox.showwarning("Atenção", "Selecione um produto na tabela para excluir.")
            return

        confirma = messagebox.askyesno("Confirmar", "Deseja realmente excluir este produto?")
        if not confirma:
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = %s", (self.id_em_edicao,))
            con.commit()
            cursor.close()
            con.close()

            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            self.limpar_campos()
            self.carregar_produtos()

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao excluir:\n{erro}")

    # ==================  METODOS AUXILIARES  ==================

    def selecionar_produto(self, evento):
        """
        Ao clicar numa linha da Treeview, preenche os campos para edicao.
        """
        selecionado = self.tabela.selection()       # tupla com os iid selecionados
        if not selecionado:
            return

        valores = self.tabela.item(selecionado[0], "values")
        # valores = (id, nome, codigo, valor, unidade)

        self.id_em_edicao = valores[0]              # guarda o id para UPDATE / DELETE

        # preenche os campos
        self.campo_nome.delete(0, tk.END)
        self.campo_nome.insert(0, valores[1])

        self.campo_codigo.delete(0, tk.END)
        self.campo_codigo.insert(0, valores[2])

        self.campo_valor.delete(0, tk.END)
        self.campo_valor.insert(0, valores[3])

        self.campo_unidade.delete(0, tk.END)
        self.campo_unidade.insert(0, valores[4])

    def limpar_campos(self):
        """
        Limpa o formulario e volta ao modo de novo cadastro.
        """
        self.id_em_edicao = None
        self.campo_nome.delete(0, tk.END)
        self.campo_codigo.delete(0, tk.END)
        self.campo_valor.delete(0, tk.END)
        self.campo_unidade.delete(0, tk.END)
        self.tabela.selection_remove(*self.tabela.selection())   # deseleciona na tabela
