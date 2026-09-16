# ============================================================
# tela_caixa.py
# TelaCaixa — le a comanda, mostra o consumo, recebe o pagamento
# ============================================================

import tkinter as tk
from tkinter import messagebox, ttk
from bancos import Banco


class TelaCaixa(tk.Toplevel):
    """
    Janela de caixa.
    Pode abrir sozinha (digitando o numero) OU ja vir de uma comanda fechada
    (parametro comanda_id preenchido).
    """

    def __init__(self, janela_pai, comanda_id=None):
        super().__init__(janela_pai)
        self.title("Caixa")
        self.geometry("600x550")
        self.configure(bg="white")
        self.grab_set()

        self.comanda_id = comanda_id     # se veio da comanda, ja chega preenchido
        self.total = 0.0                 # total da comanda carregada

        # instancia a classe Banco
        self.banco = Banco()

        # ---------- BUSCA POR NUMERO ----------
        topo = tk.Frame(self, bg="white")
        topo.pack(pady=10)
        tk.Label(topo, text="Nº da Comanda:", bg="white").pack(side="left", padx=5)
        self.campo_numero = tk.Entry(topo, width=10)
        self.campo_numero.pack(side="left", padx=5)
        tk.Button(topo, text="Buscar", bg="#2E86C1", fg="white",
                  command=self.buscar_comanda).pack(side="left", padx=5)

        # ---------- INFO DA COMANDA ----------
        self.label_info = tk.Label(self, text="", font=("Arial", 11),
                                   bg="white", fg="#555555")
        self.label_info.pack(pady=5)

        # ---------- CONSUMO ----------
        colunas = ("produto", "qtd", "valor_unit", "subtotal")
        self.lista = ttk.Treeview(self, columns=colunas, show="headings", height=10)
        self.lista.pack(padx=10, pady=10, fill="x")

        self.lista.heading("produto",    text="Produto")
        self.lista.heading("qtd",        text="Qtd")
        self.lista.heading("valor_unit", text="Vlr Unit")
        self.lista.heading("subtotal",   text="Subtotal")

        self.lista.column("produto",    width=260, anchor="w")
        self.lista.column("qtd",        width=70,  anchor="center")
        self.lista.column("valor_unit", width=100, anchor="e")
        self.lista.column("subtotal",   width=110, anchor="e")

        # ---------- TOTAL ----------
        self.label_total = tk.Label(self, text="TOTAL: R$ 0,00",
                                    font=("Arial", 18, "bold"), bg="white", fg="#B22222")
        self.label_total.pack(pady=10)

        # ---------- FORMA DE PAGAMENTO + RECEBER ----------
        pagamento = tk.Frame(self, bg="white")
        pagamento.pack(pady=15)

        tk.Label(pagamento, text="Forma:", bg="white").pack(side="left", padx=5)
        self.combo_forma = ttk.Combobox(pagamento, width=15, state="readonly",
                                        values=["dinheiro", "cartao", "pix"])
        self.combo_forma.pack(side="left", padx=5)

        tk.Button(pagamento, text="RECEBER", font=("Arial", 12, "bold"),
                  bg="#28B463", fg="white", command=self.receber).pack(side="left", padx=15)

        # se ja veio uma comanda (fechamento), carrega direto
        if self.comanda_id is not None:
            self.carregar_consumo()

    # =====================  METODOS DE BANCO  =====================

    def buscar_comanda(self):
        """
        SELECT — acha a comanda pelo numero digitado.
        Aceita comandas com status 'fechada' (prontas para pagamento).
        """
        numero_texto = self.campo_numero.get().strip()
        if not numero_texto:
            messagebox.showwarning("Atenção", "Digite o número da comanda.")
            return

        try:
            numero_int = int(numero_texto)
        except ValueError:
            messagebox.showwarning("Atenção", "Número inválido.")
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()
            cursor.execute(
                "SELECT id, nome_cliente, status FROM comandas WHERE numero = %s",
                (numero_int,)
            )
            resultado = cursor.fetchone()
            cursor.close()
            con.close()

            if resultado is None:
                messagebox.showwarning("Atenção", f"Comanda #{numero_int} não encontrada.")
                return

            comanda_id, cliente, status = resultado

            if status == "paga":
                messagebox.showinfo("Aviso", f"Comanda #{numero_int} já foi paga.")
                return

            if status == "aberta":
                messagebox.showwarning("Atenção",
                    f"Comanda #{numero_int} ainda está aberta.\n"
                    "Feche a comanda primeiro na tela de Vendas.")
                return

            # status == 'fechada' -> pronta para pagamento
            self.comanda_id = comanda_id
            self.label_info.config(text=f"Comanda #{numero_int}  —  Cliente: {cliente}")
            self.carregar_consumo()

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao buscar comanda:\n{erro}")

    def carregar_consumo(self):
        """
        SELECT — lista os itens da comanda (JOIN com produtos) e calcula o total.
        """
        for item in self.lista.get_children():
            self.lista.delete(item)

        if self.comanda_id is None:
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()

            # busca info da comanda para exibir no label (caso veio pelo fechar_comanda)
            cursor.execute(
                "SELECT numero, nome_cliente FROM comandas WHERE id = %s",
                (self.comanda_id,)
            )
            info = cursor.fetchone()
            if info:
                self.label_info.config(text=f"Comanda #{info[0]}  —  Cliente: {info[1]}")
                self.campo_numero.delete(0, tk.END)
                self.campo_numero.insert(0, str(info[0]))

            # busca os itens
            cursor.execute(
                "SELECT p.nome, i.quantidade, i.valor_unit_na_venda "
                "FROM itens_comanda i "
                "JOIN produtos p ON p.id = i.produto_id "
                "WHERE i.comanda_id = %s "
                "ORDER BY i.id",
                (self.comanda_id,)
            )
            linhas = cursor.fetchall()

            self.total = 0.0
            for linha in linhas:
                nome, qtd, vunit = linha
                subtotal = float(qtd) * float(vunit)
                self.total += subtotal
                self.lista.insert("", "end", values=(
                    nome,
                    f"{qtd:.3f}",
                    f"{vunit:.2f}",
                    f"{subtotal:.2f}"
                ))

            cursor.close()
            con.close()

            self.label_total.config(text=f"TOTAL: R$ {self.total:.2f}")

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao carregar consumo:\n{erro}")

    def receber(self):
        """
        INSERT INTO pagamentos + UPDATE comandas SET status='paga'.
        Registra o pagamento e finaliza a comanda.
        """
        if self.comanda_id is None:
            messagebox.showwarning("Atenção", "Busque uma comanda primeiro.")
            return

        forma = self.combo_forma.get()
        if not forma:
            messagebox.showwarning("Atenção", "Escolha a forma de pagamento.")
            return

        confirma = messagebox.askyesno("Confirmar",
            f"Receber R$ {self.total:.2f} em {forma}?")
        if not confirma:
            return

        try:
            con = self.banco.conectar()
            cursor = con.cursor()

            # INSERT — registra o pagamento
            cursor.execute(
                "INSERT INTO pagamentos (comanda_id, forma, valor_pago) "
                "VALUES (%s, %s, %s)",
                (self.comanda_id, forma, self.total)
            )

            # UPDATE — marca a comanda como paga
            cursor.execute(
                "UPDATE comandas SET status = 'paga' WHERE id = %s",
                (self.comanda_id,)
            )

            con.commit()
            cursor.close()
            con.close()

            messagebox.showinfo("Sucesso",
                f"Pagamento de R$ {self.total:.2f} em {forma} registrado!\n"
                "Comanda encerrada.")
            self.destroy()

        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao registrar pagamento:\n{erro}")
