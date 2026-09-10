# ============================================================
# componentes.py
# Componentes visuais reutilizaveis do sistema Restaurante Emilia.
# Para não ter que ficar carregando o logotipo , por exemplo
# toda a vez que for usar o logotipo
# Cada componente e uma classe que herda de um widget do Tkinter.
# ============================================================

import os                              # para montar caminhos de arquivo
import tkinter as tk                   # biblioteca de janelas
from PIL import Image, ImageTk         # Pillow: abrir e redimensionar imagens
                                       # usa PIL para manter a compatibilidade com
                                       #  as versões anteriores


class Logo(tk.Label):
    """
    Componente de logotipo reutilizavel.
    Herda de tk.Label -> um objeto Logo E um Label, ja com a imagem carregada.
    Uso:
        logo = Logo(janela, tamanho=120)
        logo.pack()
    """

    def __init__(self, janela_pai, tamanho=150):
        # __init__ e o construtor: roda automaticamente ao criar o objeto
        # equivale ao Create do Delphi
      
        # 1) monta o caminho do PNG a partir da pasta ONDE ESTE .py esta.
        #    assim funciona em qualquer maquina, sem depender de C:\...
        pasta = os.path.dirname(os.path.abspath(__file__)) # le a pasta onde esta rodando o sistema
        caminho = os.path.join(pasta, "logotipo", "logotipo_emilia.png") # copia o caminho completo com o nome do logo em caminho

        # 2) abre a imagem e redimensiona para o tamanho pedido.
        #    Image.LANCZOS = algoritmo que preserva qualidade ao encolher.
        imagem = Image.open(caminho).resize((tamanho, tamanho), Image.LANCZOS)

        # Constante	Qualidade ao encolher	Velocidade (Aprendi essa)
        # Image.NEAREST	baixa (fica "serrilhado")	mais rápido
        # Image.BILINEAR	média	rápido
        # Image.BICUBIC	boa	médio
        # Image.LANCZOS	melhor (mais nítida)	mais lento

        # 3) converte para o formato que o Tkinter entende.
        #    guardamos em self. (atributo do objeto) para a imagem NAO sumir:
        #    enquanto o objeto Logo viver, a imagem vive junto.
        self.logo_img = ImageTk.PhotoImage(imagem)

        # 4) chama o construtor do Label (a classe pai), ja passando a imagem.
        #    super() = a superclasse (tk.Label). Equivale ao inherited do Delphi.
        super().__init__(janela_pai, image=self.logo_img, bg="white")

  
