# ============================================================
# tela_comanda.py
# TelaComanda — abertura de comanda, lancamento de itens, fechamento
# ============================================================

import tkinter as tk
from tkinter import messagebox, ttk
from bancos import Banco


class TelaComanda(tk.Toplevel):
    """
    Janela de comanda/vendas.
    Fluxo: abrir comanda -> adicionar produtos (com quantidade) -> fechar.
    Mexe em 3 tabelas: comandas, itens_comanda, produtos (para o preco).
    """

    def __init__(self, janela_pai):
        super().__init__(janela_pai)
        self.title("Comanda / Vendas")
        self.geometry("700x600")
        self.configure(bg="white")
        self.grab_set()

        # id da comanda aberta no momento (None = nenhuma aberta ainda)
        self.comanda_id = None

        # instancia a classe Banco
        self.banco = Banco()

        # dicionario de produtos: {nome: (id, preco)}
        self.produtos = {}

        # ---------- ABERTURA DA COMANDA ----------
        topo = tk.Frame(self, bg="white")
        topo.pack(pady=10, fill="x")

        tk.Label(topo, text="Nº Comanda:", bg="white").grid(row=0, column=0, padx=5, sticky="e")
        self.campo_numero = tk.Entry(topo, width=10)
        self.campo_numero.grid(row=0, column=1, padx=5)

        tk.Label(topo, text="Cliente:", bg="white").grid(row=0, column=2, padx=5, sticky="e")
        self.campo_cliente = tk.Entry(topo, width=25)
        self.campo_cliente.grid(row=0, column=3, padx=5)

        tk.Button(topo, text="Abrir Comanda", bg="#28B463", fg="white",
                  command=self.abrir_comanda).grid(row=0, column=4, padx=10)

        # ---------- LANCAMENTO DE ITENS ----------
        meio = tk.Frame(self, bg="white")
        meio.pack(pady=10, fill="x")

        tk.Label(meio, text="Produto:", bg="white").grid(row=0, column=0, padx=5, sticky="e")
        self.combo_produto = ttk.Combobox(meio, width=30, state="readonly")
        self.combo_produto.grid(row=0, column=1, padx=5)

        tk.Label(meio, text="Qtd:", bg="white").grid(row=0, column=2, padx=5, sticky="e")
        self.campo_qtd = tk.Entry(meio, width=8)
        self.campo_qtd.grid(row=0, column=3, padx=5)

        tk.Button(meio, text="Adicionar item", bg="#2E86C1", fg="white",
                  command=self.adicionar_item).grid(row=0, column=4, padx=10)
        tk.Button(meio, text="Remover item", bg="#C0392B", fg="white",
                  command=self.remover_item).grid(row=0, column=5, padx=5)

        # ---------- LISTA DO CONSUMO ----------
        colunas = ("item_id", "produto", "qtd", "valor_unit", "subtotal")
        self.lista = ttk.Treeview(self, columns=colunas, show="headings", height=10)
        self.lista.pack(padx=10, pady=10, fill="x")

        self.lista.heading("item_id",    text="ID")
        self.lista.heading("produto",    text="Produto")
        self.lista.heading("qtd",        text="Qtd")
        self.lista.heading("valor_unit", text="Vlr Unit")
        self.lista.heading("subtotal",   text="Subtotal")

        self.lista.column("item_id",    width=40,  anchor="center")
        self.lista.column("produto",    width=280, anchor="w")
        self.lista.column("qtd",        width=60,  anchor="center")
        self.lista.column("valor_unit", width=90,  anchor="e")
        self.lista.column("subtotal",   width=100, anchor="e")

        # ---------- RODAPE: TOTAL + FECHAR ----------
        rodape = tk.Frame(self, bg="white")
        rodape.pack(pady=10, fill="x")

        self.label_total = tk.Label(rodape, text="TOTAL: R$ 0,00",
                                    font=("Arial", 16, "bold"), bg="white", fg="#B22222")
        self.label_total.pack(side="left", padx=20)

        tk.Button(rodape, text="FECHAR COMANDA", font=("Arial", 12, "bold"),
                  bg="#E67E22", fg="white", command=self.fechar_comanda).pack(side="right", padx=20)

        # ao abrir, carrega a lista de produtos no combobox
        self.carregar_produtos()

    # =====================  METODOS DE BANCO  =====================

    def carregar_produtos(self):
        """
        SELECT — le todos os produtos do banco e preenche o Combobox.
        Guarda num dicionario {nome: (id, preco)} para consulta rapida.
        """
        self.produtos = {}
        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute("SELECT id, nome, valor_unitario FROM produtos ORDER BY nome")
            linhas = cursor.fetchall()
            cursor.close()
            con.close()

            nomes = []
            for linha in linhas:
                prod_id, nome, preco = linha
                self.produtos[nome] = (prod_id, float(preco))
                nomes.append(nome)

            self.combo_produto["values"] = nomes

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{erro}")

    def abrir_comanda(self):
        """
        INSERT INTO comandas — cria uma comanda nova no banco.
        Guarda o id gerado em self.comanda_id (cursor.lastrowid).
        """
        if self.comanda_id is not None:
            messagebox.showwarning("Atenção", "Já existe uma comanda aberta nesta tela.")
            return

        numero  = self.campo_numero.get().strip()
        cliente = self.campo_cliente.get().strip()

        if not numero:
            messagebox.showwarning("Atenção", "Preencha o número da comanda.")
            return
        if not cliente:
            messagebox.showwarning("Atenção", "Preencha o nome do cliente.")
            return

        try:
            numero_int = int(numero)
        except ValueError:
            messagebox.showwarning("Atenção", "Número da comanda deve ser inteiro.")
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO comandas (numero, nome_cliente, status, valor_total) "
                "VALUES (%s, %s, 'aberta', 0.00)",
                (numero_int, cliente)
            )
            con.commit()
            self.comanda_id = cursor.lastrowid      # guarda o id gerado
            cursor.close()
            con.close()

            # bloqueia os campos para nao alterar depois de aberta
            self.campo_numero.config(state="disabled")
            self.campo_cliente.config(state="disabled")

            messagebox.showinfo("Sucesso",
                                f"Comanda #{numero_int} aberta para {cliente}.")

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao abrir comanda:\n{erro}")

    def adicionar_item(self):
        """
        INSERT INTO itens_comanda — adiciona um produto a comanda aberta.
        """
        if self.comanda_id is None:
            messagebox.showwarning("Atenção", "Abra uma comanda primeiro.")
            return

        nome_produto = self.combo_produto.get()
        qtd_texto    = self.campo_qtd.get().strip()

        if not nome_produto or nome_produto not in self.produtos:
            messagebox.showwarning("Atenção", "Selecione um produto válido.")
            return
        if not qtd_texto:
            messagebox.showwarning("Atenção", "Preencha a quantidade.")
            return

        try:
            quantidade = float(qtd_texto.replace(",", "."))
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atenção", "Quantidade inválida.")
            return

        prod_id, preco = self.produtos[nome_produto]

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO itens_comanda (comanda_id, produto_id, quantidade, valor_unit_na_venda) "
                "VALUES (%s, %s, %s, %s)",
                (self.comanda_id, prod_id, quantidade, preco)
            )
            con.commit()
            cursor.close()
            con.close()

            # limpa os campos de lancamento
            self.combo_produto.set("")
            self.campo_qtd.delete(0, tk.END)

            self.listar_itens()
            self.atualizar_total()

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao adicionar item:\n{erro}")

    def remover_item(self):
        """
        DELETE FROM itens_comanda — remove o item selecionado na lista.
        """
        selecionado = self.lista.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um item na lista para remover.")
            return

        item_id = self.lista.item(selecionado[0], "values")[0]

        confirma = messagebox.askyesno("Confirmar", "Remover este item da comanda?")
        if not confirma:
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute("DELETE FROM itens_comanda WHERE id = %s", (item_id,))
            con.commit()
            cursor.close()
            con.close()

            self.listar_itens()
            self.atualizar_total()

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao remover item:\n{erro}")

    def listar_itens(self):
        """
        SELECT — lista os itens desta comanda (JOIN com produtos para o nome).
        """
        for item in self.lista.get_children():
            self.lista.delete(item)

        if self.comanda_id is None:
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "SELECT i.id, p.nome, i.quantidade, i.valor_unit_na_venda "
                "FROM itens_comanda i "
                "JOIN produtos p ON p.id = i.produto_id "
                "WHERE i.comanda_id = %s "
                "ORDER BY i.id",
                (self.comanda_id,)
            )
            linhas = cursor.fetchall()
            cursor.close()
            con.close()

            for linha in linhas:
                item_id, nome, qtd, vunit = linha
                subtotal = float(qtd) * float(vunit)
                self.lista.insert("", "end", values=(
                    item_id, nome,
                    f"{qtd:.3f}",
                    f"{vunit:.2f}",
                    f"{subtotal:.2f}"
                ))

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao listar itens:\n{erro}")

    def atualizar_total(self):
        """
        SELECT SUM — calcula o total da comanda e atualiza o label + banco.
        """
        if self.comanda_id is None:
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "SELECT SUM(quantidade * valor_unit_na_venda) "
                "FROM itens_comanda WHERE comanda_id = %s",
                (self.comanda_id,)
            )
            resultado = cursor.fetchone()[0]
            total = float(resultado) if resultado else 0.0

            # grava o total na tabela comandas
            cursor.execute(
                "UPDATE comandas SET valor_total = %s WHERE id = %s",
                (total, self.comanda_id)
            )
            con.commit()
            cursor.close()
            con.close()

            self.label_total.config(text=f"TOTAL: R$ {total:.2f}")

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao atualizar total:\n{erro}")

    def fechar_comanda(self):
        """
        UPDATE comandas SET status='fechada' — fecha a comanda e abre o Caixa.
        """
        if self.comanda_id is None:
            messagebox.showwarning("Atenção", "Nenhuma comanda aberta.")
            return

        # verifica se tem pelo menos 1 item
        if not self.lista.get_children():
            messagebox.showwarning("Atenção", "Adicione pelo menos um item antes de fechar.")
            return

        confirma = messagebox.askyesno("Confirmar", "Fechar esta comanda e ir para o Caixa?")
        if not confirma:
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "UPDATE comandas SET status = 'fechada' WHERE id = %s",
                (self.comanda_id,)
            )
            con.commit()
            cursor.close()
            con.close()

            # importa aqui para evitar importacao circular
            from caixa import TelaCaixa

            janela_pai = self.master       # guarda referencia antes de destruir
            comanda_id = self.comanda_id   # guarda o id
            self.destroy()                 # fecha a tela de comanda
            TelaCaixa(janela_pai, comanda_id=comanda_id)   # abre o caixa

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao fechar comanda:\n{erro}")
