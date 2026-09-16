# ============================================================
# banco.py
# Classe responsavel por conectar no banco de dados MySQL.
# Centraliza os dados de conexao num lugar so: se mudar a senha
# ou o servidor, muda-se AQUI e todo o sistema acompanha.
# ============================================================

import mysql.connector                 # driver que conversa com o MySQL


class Banco:
    """
    Comandos para a conexão com o banco EMILIA.
    Qualquer modulo do sistema (Produtos, Comanda, Caixa) usa esta classe
    para obter uma conexao, sem precisar saber host, usuario ou senha.
    """

    # ---- dados de conexao (atributos de CLASSE: valem para todos os objetos) ----
    HOST = "localhost"
    PORT = 3306
    USUARIO = "root"
    SENHA = ""                          # XAMPP vem sem senha no root
    BANCO = "EMILIA"

    def conectar(self):
        """
        Abre e devolve uma conexao com o banco.
        Quem chamar fica responsavel por fechar depois (con.close()).
        """
        conexao = mysql.connector.connect(
            host=Banco.HOST,            # usamos Banco.HOST -> o atributo da classe
            port=Banco.PORT,
            user=Banco.USUARIO,
            password=Banco.SENHA,
            database=Banco.BANCO
        )
        return conexao                  # devolve a conexao pronta para uso