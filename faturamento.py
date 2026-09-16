# ============================================================
# tela_faturamento.py
# TelaFaturamento — relatorio de vendas por data:
#   - produtos vendidos no dia (quantidade e total por produto)
#   - total faturado por forma de pagamento (dinheiro, cartao, pix)
#   - total geral faturado no dia
# ============================================================

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
from bancos import Banco


class TelaFaturamento(tk.Toplevel):
    """
    Janela de relatorio de faturamento.
    Herda de tk.Toplevel -> janela secundaria da principal.
    """

    def __init__(self, janela_pai):
        super().__init__(janela_pai)
        self.title("Faturamento / Relatório de Vendas")
        self.geometry("660x620")
        self.configure(bg="white")
        self.grab_set()

        self.banco = Banco()

        # ---- FILTRO POR DATA ----
        topo = tk.Frame(self, bg="white")
        topo.pack(pady=12)

        tk.Label(topo, text="Data (AAAA-MM-DD):", bg="white").pack(side="left", padx=5)
        self.campo_data = tk.Entry(topo, width=14)
        self.campo_data.pack(side="left", padx=5)
        # ja preenche com a data de hoje
        self.campo_data.insert(0, date.today().isoformat())

        tk.Button(topo, text="🔍 Consultar", bg="#2E86C1", fg="white",
                  command=self.consultar).pack(side="left", padx=8)

        # ---- TITULO: PRODUTOS VENDIDOS ----
        tk.Label(self, text="Produtos vendidos no dia",
                 font=("Arial", 13, "bold"), bg="white", fg="#B22222").pack(pady=(10, 0))

        # ---- LISTA DE PRODUTOS VENDIDOS ----
        colunas = ("produto", "qtd_total", "valor_total")
        self.lista = ttk.Treeview(self, columns=colunas, show="headings", height=10)
        self.lista.pack(padx=10, pady=10, fill="x")

        self.lista.heading("produto",     text="Produto")
        self.lista.heading("qtd_total",   text="Qtd Vendida")
        self.lista.heading("valor_total", text="Total (R$)")

        self.lista.column("produto",     width=320, anchor="w")
        self.lista.column("qtd_total",   width=120, anchor="center")
        self.lista.column("valor_total", width=140, anchor="e")

        # ---- FATURAMENTO POR FORMA DE PAGAMENTO ----
        tk.Label(self, text="Faturamento por forma de pagamento",
                 font=("Arial", 13, "bold"), bg="white", fg="#B22222").pack(pady=(10, 0))

        frame_formas = tk.Frame(self, bg="white")
        frame_formas.pack(pady=8)

        # labels para cada forma
        tk.Label(frame_formas, text="💵 Dinheiro:", bg="white",
                 font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=8, pady=3)
        self.label_dinheiro = tk.Label(frame_formas, text="R$ 0,00", bg="white",
                                       font=("Arial", 12, "bold"), fg="#2E86C1")
        self.label_dinheiro.grid(row=0, column=1, sticky="w", padx=8, pady=3)

        tk.Label(frame_formas, text="💳 Cartão:", bg="white",
                 font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=8, pady=3)
        self.label_cartao = tk.Label(frame_formas, text="R$ 0,00", bg="white",
                                     font=("Arial", 12, "bold"), fg="#2E86C1")
        self.label_cartao.grid(row=1, column=1, sticky="w", padx=8, pady=3)

        tk.Label(frame_formas, text="📱 PIX:", bg="white",
                 font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=8, pady=3)
        self.label_pix = tk.Label(frame_formas, text="R$ 0,00", bg="white",
                                  font=("Arial", 12, "bold"), fg="#2E86C1")
        self.label_pix.grid(row=2, column=1, sticky="w", padx=8, pady=3)

        # ---- TOTAL GERAL FATURADO NO DIA ----
        self.label_total = tk.Label(self, text="TOTAL FATURADO NO DIA: R$ 0,00",
                                    font=("Arial", 16, "bold"), bg="white", fg="#28B463")
        self.label_total.pack(pady=15)

        # ao abrir, ja consulta o dia de hoje
        self.consultar()

    # =====================  METODOS DE BANCO  =====================

    def consultar(self):
        """
        Le a data digitada e monta o relatorio do dia.
        """
        data_texto = self.campo_data.get().strip()
        if not data_texto:
            messagebox.showwarning("Atenção", "Digite uma data (formato AAAA-MM-DD).")
            return

        # limpa a lista antes de recarregar
        for item in self.lista.get_children():
            self.lista.delete(item)

        self._carregar_produtos_vendidos(data_texto)
        self._carregar_total_por_forma(data_texto)
        self._carregar_total_geral(data_texto)

    def _carregar_produtos_vendidos(self, data_texto):
        """
        SELECT — agrupa os itens de comandas PAGAS naquela data.
        Mostra cada produto, a quantidade total vendida e o valor total.
        """
        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "SELECT p.nome, "
                "       SUM(i.quantidade) AS qtd_total, "
                "       SUM(i.quantidade * i.valor_unit_na_venda) AS valor_total "
                "FROM itens_comanda i "
                "JOIN produtos p    ON p.id = i.produto_id "
                "JOIN comandas c    ON c.id = i.comanda_id "
                "JOIN pagamentos pg ON pg.comanda_id = c.id "
                "WHERE DATE(pg.data_pagamento) = %s "
                "  AND c.status = 'paga' "
                "GROUP BY p.id, p.nome "
                "ORDER BY valor_total DESC",
                (data_texto,)
            )
            linhas = cursor.fetchall()
            cursor.close()
            con.close()

            for linha in linhas:
                nome, qtd, valor = linha
                self.lista.insert("", "end", values=(
                    nome,
                    f"{qtd:.3f}",
                    f"{valor:.2f}"
                ))

            if not linhas:
                self.lista.insert("", "end", values=(
                    "Nenhuma venda nesta data", "", ""
                ))

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao carregar produtos vendidos:\n{erro}")

    def _carregar_total_por_forma(self, data_texto):
        """
        SELECT — soma os pagamentos por forma (dinheiro, cartao, pix) no dia.
        Atualiza os 3 labels individuais.
        """
        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "SELECT forma, SUM(valor_pago) "
                "FROM pagamentos "
                "WHERE DATE(data_pagamento) = %s "
                "GROUP BY forma",
                (data_texto,)
            )
            linhas = cursor.fetchall()
            cursor.close()
            con.close()

            # zera tudo antes de preencher
            totais = {"dinheiro": 0.0, "cartao": 0.0, "pix": 0.0}

            for forma, soma in linhas:
                if forma in totais:
                    totais[forma] = float(soma)

            self.label_dinheiro.config(text=f"R$ {totais['dinheiro']:.2f}")
            self.label_cartao.config(text=f"R$ {totais['cartao']:.2f}")
            self.label_pix.config(text=f"R$ {totais['pix']:.2f}")

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao carregar totais por forma:\n{erro}")

    def _carregar_total_geral(self, data_texto):
        """
        SELECT SUM(valor_pago) — total geral faturado no dia.
        """
        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "SELECT SUM(valor_pago) "
                "FROM pagamentos "
                "WHERE DATE(data_pagamento) = %s",
                (data_texto,)
            )
            resultado = cursor.fetchone()[0]
            total = float(resultado) if resultado else 0.0
            cursor.close()
            con.close()

            self.label_total.config(text=f"TOTAL FATURADO NO DIA: R$ {total:.2f}")

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao carregar total geral:\n{erro}")
