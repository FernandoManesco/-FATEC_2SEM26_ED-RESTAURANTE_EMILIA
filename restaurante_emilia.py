# restaurante_emilia.py
# Passo 1: tela de login conectada ao banco EMILIA.

import tkinter as tk                 # biblioteca padrao de janelas do Python
from tkinter import messagebox       # caixinhas de aviso ou erro
import mysql.connector               # driver do MySQL


def verificar_login():
    usuario = campo_usuario.get()    # get() le o que foi digitado no Entry
    senha = campo_senha.get()

    if senha == "":
        messagebox.showwarning("Atenção", "Preencha a senha.")
        return                        # sai da funcao sem continuar

    if usuario == "":
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
            "SELECT id FROM usuarios WHERE usuario = %s AND senha = %s",
            (usuario, senha)
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


def abrir_tela_principal():
    # apaga tudo que esta na janela (some com o login)
    for widget in janela.winfo_children():
        widget.destroy()

    janela.configure(bg="white")
    tk.Label(janela, text="Restaurante Emília",
             font=("Arial", 24, "bold"), bg="white", fg="#B22222").pack(pady=40)
    tk.Label(janela, text="(tela principal — em branco por enquanto)",
             font=("Arial", 12), bg="white", fg="gray").pack()


# ---- Montagem da janela ----
janela = tk.Tk()                         # cria a janela (como um TForm)
janela.title("Restaurante Emília")
janela.geometry("400x400")               # largura x altura
janela.configure(bg="white")

# logotipo simples desenhado num Canvas: um "prato" com a letra E
logo = tk.Canvas(janela, width=120, height=120, bg="white", highlightthickness=0)
logo.pack(pady=20)
logo.create_oval(20, 20, 100, 100, outline="#B22222", width=4)
logo.create_text(60, 60, text="E", font=("Arial", 40, "bold"), fill="#B22222")

tk.Label(janela, text="Restaurante Emília",
         font=("Arial", 18, "bold"), bg="white", fg="#B22222").pack()

tk.Label(janela, text="Usuário:", bg="white").pack(pady=(20, 0))
campo_usuario = tk.Entry(janela, width=30)
campo_usuario.pack()

tk.Label(janela, text="Senha:", bg="white").pack(pady=(10, 0))
campo_senha = tk.Entry(janela, width=30, show="*")   # show="*" mascara a senha
campo_senha.pack()

tk.Button(janela, text="Entrar", width=15, bg="#B22222", fg="white",
          command=verificar_login).pack(pady=20)

janela.mainloop()                        # inicia o loop de eventos (Application.Run)
