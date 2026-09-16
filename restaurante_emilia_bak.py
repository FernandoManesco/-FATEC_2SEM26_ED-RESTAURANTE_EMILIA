# restaurante_emilia.py
# Passo 1: tela de login conectada ao banco EMILIA.

import tkinter as tk                 # biblioteca padrao de janelas do Python
from tkinter import messagebox       # caixinhas de aviso ou erro
import mysql.connector               # driver do MySQL
from bancos import Banco            # nosso arquivo de conexao com o banco
from componentes import Logo, BotaoMenu    # importa as duas classes
from telas import produtos, comanda, caixa


def verificar_login():
    nome = campo_nome.get()    # get() le o que foi digitado no Entry , um editbox
    senha = campo_senha.get()

    if senha == "":
        messagebox.showwarning("Atenção", "Preencha a senha.")
        return                        # sai da funcao sem continuar

    if nome == "":
        messagebox.showwarning("Atenção", "Preencha o usuário.")
        return                        # sai da funcao sem continuar

    try:
        conexao = mysql.connector.connect(
            host="localhost", port=3306,
            user="root", password="",
            database="EMILIA"          # agora ja abrimos direto no banco EMILIA
        )
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT codigo FROM usuarios WHERE nome = %s AND senha = %s",
            (nome, senha)
        )
        resultado = cursor.fetchone()  # traz a 1a linha achada, ou None
        cursor.close()
        conexao.close()

        if resultado is not None:
            abrir_tela_principal()     # login OK
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    except mysql.connector.Error as erro:   # cai aqui se o XAMPP estiver parado, etc.
        messagebox.showerror("Erro de conexão", f"Não consegui conectar:\n{erro}")

def abrir_produtos():
    produtos(janela)

def abrir_comanda():
    comanda(janela)

def abrir_caixa():
    caixa(janela)
def abrir_tela_principal():
    # limpa a tela de login (remove todos os widgets da janela)
    for widget in janela.winfo_children():
        widget.destroy()

    # deixa a janela maior para caber os 3 botoes com folga
    janela.geometry("500x550")
    janela.configure(bg="white")

    # logo reaproveitado no topo
    logo = Logo(janela, tamanho=100)
    logo.pack(pady=15)

    # titulo
    tk.Label(janela, text="Restaurante Emília",
             font=("Arial", 20, "bold"), bg="white", fg="#B22222").pack(pady=(0, 20))

    # ---- os 3 botoes grandes ----
    # cada botao: emoji grande + texto, cor de fundo propria, e um comando.
    # por enquanto os comandos so mostram um aviso; depois abrirao as telas.

    # ...dentro da abrir_tela_principal, no lugar dos 3 blocos tk.Button: 
    BotaoMenu(janela, "📦  Cadastro de Produtos", "#2E86C1", abrir_produtos).pack(pady=10)
    BotaoMenu(janela, "🍽️  Comanda / Vendas",     "#28B463", abrir_comanda).pack(pady=10)
    BotaoMenu(janela, "💰  Caixa",                 "#E67E22", abrir_caixa).pack(pady=10)


# ---- Montagem da janela ----
janela = tk.Tk()                         # cria a janela (como um TForm)
janela.title("Restaurante Emília")
janela.geometry("400x400")               # largura x altura
janela.configure(bg="white")

logo = Logo(janela, tamanho=120)
logo.pack(pady=20)

tk.Label(janela, text="Restaurante Emília",
         font=("Arial", 18, "bold"), bg="white", fg="#B22222").pack()

tk.Label(janela, text="Usuário:", bg="white").pack(pady=(20, 0))
campo_nome = tk.Entry(janela, width=30)
campo_nome.pack()

tk.Label(janela, text="Senha:", bg="white").pack(pady=(10, 0))
campo_senha = tk.Entry(janela, width=30, show="*")   # show="*" mascara a senha
campo_senha.pack()

tk.Button(janela, text="Entrar", width=15, bg="#B22222", fg="white",
          command=verificar_login).pack(pady=20)

janela.mainloop()                        # inicia o loop de eventos (Application.Run)
