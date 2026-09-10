# -FATEC_2SEM26_ED-RESTAURANTE_EMILIA

🍽️ Sistema de Restaurante

Projeto desenvolvido para as disciplinas Estrutura de Dados e Linguagem de Programação 2 da Fatec Rio Claro (Centro Paula Souza).

O objetivo é simular a operação de um restaurante — abertura de comandas, controle de estoque perecível, fechamento e pagamento — implementando estruturas de dados próprias (sem uso de estruturas built-in do Python como estrutura do problema), com orientação a objetos e separação de responsabilidades em classes.

📋 Escopo do projeto

O sistema cobre quatro domínios principais:

1. Controle de Comandas
Cada cliente, ao entrar, recebe uma comanda.
A comanda armazena: número, nome do cliente, data/hora de abertura, uma ou mais refeições e uma ou mais bebidas (Coca-Cola, Suco ou Água).
Itens podem ser adicionados ou removidos ao longo do atendimento, antes do fechamento.
2. Controle de Estoque
Armazena, por produto: nome, preço de compra, preço de venda, data da compra, data de vencimento e quantidade em estoque.
Produtos são perecíveis: a prioridade de uso/venda é sempre do lote mais antigo (política FIFO por vencimento).
Permite editar a quantidade em estoque.
3. Controle de Pagamento
O pagamento ocorre no fechamento da comanda, via PIX, cartão ou dinheiro.
Cada pagamento registra: nome de quem pagou, número da comanda, forma de pagamento, valor total pago e data/hora.
4. Controle do que consumiu (fechamento)

No fechamento da comanda, o sistema deve:

Baixar o estoque dos produtos usados nas refeições e bebidas consumidas.
Registrar o pagamento.
Controlar quem consumiu o quê, com base no valor da comanda e na baixa de estoque.

O sistema simula um atendimento completo: abertura → inclusão de refeições e bebidas → fechamento → pagamento.

🧱 Estruturas de dados (regra do projeto)

⚠️ Requisito obrigatório: as estruturas de dados do problema (lista, pilha, fila) devem ser implementadas manualmente em classes próprias, com encapsulamento. Não é permitido usar list, dict, collections, etc. como estrutura do problema. Elas podem ser usadas internamente, encapsuladas dentro das classes que você criar.

Estruturas previstas (a consolidar durante o desenvolvimento):

Estrutura própria	Uso no domínio	Justificativa
Lista encadeada	Comandas abertas; itens de uma comanda	Inserção/remoção dinâmica de itens antes do fechamento
Fila (FIFO)	Lotes de cada produto no estoque	Consumir sempre o lote mais antigo (perecível)
(a definir)	Registros de pagamento / histórico	Consulta para relatórios de vendas
🛠️ Tecnologias
Python 3
Programação Orientada a Objetos
Faker — geração de dados aleatórios para popular o sistema
pickle — persistência não volátil (salvar/carregar estado)
📊 Relatórios
Relatório de vendas
Relatório de consumo
📁 Estrutura de pastas (proposta)
restaurante/
├── src/
│   ├── estruturas/        # Estruturas de dados próprias (lista, fila, etc.)
│   ├── modelos/           # Comanda, Produto, Pagamento, Item...
│   ├── servicos/          # Regras de negócio (fechamento, baixa de estoque)
│   ├── dados/             # Geração (Faker) e persistência (pickle)
│   └── relatorios/        # Relatórios de vendas e consumo
├── main.py                # Simulação de atendimento completo
├── requirements.txt
└── README.md
▶️ Como executar
bash
# criar ambiente virtual (opcional, recomendado)
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# instalar dependências
pip install -r requirements.txt

# executar a simulação
python main.py
🗓️ Prazos e entregas
Link do repositório: entregue nas primeiras 24 horas (issue do repositório da disciplina).
Desenvolvimento: entregas incrementais ao longo da semana.
Prazo final de código: início da aula de 17/09/2026.
Apresentação: a partir das 07h50.

As entregas incrementais (vários commits ao longo da semana) fazem parte da avaliação — evitar um único commit final.

👤 Autor

Fernando Manesco — Fatec Rio Claro
